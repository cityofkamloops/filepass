import fs
import fs.ftpfs
import fs.smbfs
from fs.walk import Walker


# File Transfer Types
def ssh_connection(logger, user, pw, svr, port, dir):
    logger.debug("ssh://{}:{}@{}:{}{}".format(user, "passwordhere", svr, port, dir))
    fs_conn = fs.open_fs("ssh://{}:{}@{}:{}{}".format(user, pw, svr, port, dir))
    return fs_conn


def smb_connection(logger, user, pw, svr, port, smbshare, dir):
    logger.debug(
        "smb://{}:{}@{}:{}/{}".format(user, "passwordhere", svr, port, smbshare + dir)
    )
    fs_conn = fs.open_fs(
        "smb://{}:{}@{}:{}/{}?direct-tcp=True&name-port=139&timeout=15&domain=".format(
            user, pw, svr, port, smbshare + dir
        )
    )
    # timeout, name - port, direct - tcp, hostname, and domain.
    return fs_conn


def transfer_file(from_fs, to_fs, filename):
    to_fs.writefile(filename, from_fs.open(filename, "rb"))


def file_pass(
    logger,
    from_user,
    from_pw,
    from_svr,
    from_port,
    from_dir,
    from_share,
    from_method,
    from_delete,
    from_filter,
    to_user,
    to_pw,
    to_svr,
    to_port,
    to_dir,
    to_share,
    to_method,
    to_delete,
):
    # From File System
    if from_method == "ssh":
        logger.debug("Create from SSH connection")
        from_fs = ssh_connection(
            logger, from_user, from_pw, from_svr, from_port, from_dir
        )

    if from_method == "smb":
        logger.debug("Create from SMB connection")
        from_fs = smb_connection(
            logger, from_user, from_pw, from_svr, from_port, from_share, from_dir
        )

    # To File System
    if to_method == "ssh":
        logger.debug("Create to SSH connection")
        to_fs = ssh_connection(logger, to_user, to_pw, to_svr, to_port, to_dir)
    if to_method == "smb":
        logger.debug("Create to SMB connection")
        to_fs = smb_connection(
            logger, to_user, to_pw, to_svr, to_port, to_share, to_dir
        )

    # Do the move
    walker = Walker(filter=[from_filter], ignore_errors=True, max_depth=1)

    for path in walker.files(from_fs):
        logger.debug("File to move: {}".format(path))

        if to_delete == "yes" and to_fs.exists(path):
            logger.debug("delete (to): {}".format(path))
            if to_fs.exists(path):
                try:
                    to_fs.remove(path)
                except fs.errors.ResourceNotFound:
                    logger.warning("(To) file ResourceNotFound: {}".format(path))
            else:
                logger.warning("file {} not found".format(path))
        else:
            logger.debug("No delete (to): {}".format(path))

        # todo: document, paths with files should be at the lowest level (no sub dirs)
        transfer_file(from_fs, to_fs, path)

        if from_delete == "yes" and from_fs.exists(path):
            logger.debug("delete (from): {}".format(path))
            if from_fs.exists(path):
                try:
                    from_fs.remove(path)
                except fs.errors.ResourceNotFound:
                    logger.warning("ResourceNotFound: {}".format(path))
            else:
                logger.warning("file {} not found".format(path))

        else:
            logger.debug("No delete (from): {}".format(path))

    from_fs.close()
    to_fs.close()
