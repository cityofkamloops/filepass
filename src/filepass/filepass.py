import fs
import fs.ftpfs
import fs.smbfs
from fs.walk import Walker


# File Transfer Types
def sftp_connection(logger, user, pw, svr, port, dir):
    logger.debug("sftp://{}:{}@{}:{}{}".format(user, "passwordhere", svr, port, dir))
    fs_conn = fs.open_fs("sftp://{}:{}@{}:{}{}".format(user, pw, svr, port, dir))
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


def local_connection(logger, dir: str):
    """Establishes a connection to a directory on the local filesystem"""
    logger.debug("local connection to {}".format(dir))
    fs_conn = fs.open_fs("{}".format(dir))
    return fs_conn


def osfs_connection(logger, dir):
    logger.debug("osfs dir: {}".format(dir))
    fs_conn = fs.open_fs(dir)
    return fs_conn


# Boolean parameter to add ability to rename target file in single file mode
def transfer_file(from_fs, to_fs, filename, should_rename=False, new_filename=None):
    target_filename = new_filename if new_filename and should_rename else filename
    to_fs.writefile(target_filename, from_fs.open(filename, "rb"))


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
    new_filename=None,
):
    # From File System
    if from_method == "sftp":
        logger.debug("Create from SFTP connection")
        from_fs = sftp_connection(
            logger, from_user, from_pw, from_svr, from_port, from_dir
        )

    if from_method == "smb":
        logger.debug("Create from SMB connection")
        from_fs = smb_connection(
            logger, from_user, from_pw, from_svr, from_port, from_share, from_dir
        )

    if from_method == "local":
        logger.debug("Create from local/osfs connection")
        from_fs = local_connection(logger, from_dir)

    if from_method == "osfs":
        logger.debug("Create osfs connection")
        from_fs = osfs_connection(logger, from_dir)

    # To File System
    if to_method == "sftp":
        logger.debug("Create to SFTP connection")
        to_fs = sftp_connection(logger, to_user, to_pw, to_svr, to_port, to_dir)

    if to_method == "smb":
        logger.debug("Create to SMB connection")
        to_fs = smb_connection(
            logger, to_user, to_pw, to_svr, to_port, to_share, to_dir
        )

    if to_method == "local":
        logger.debug("Create from local connection")
        to_fs = local_connection(logger, to_dir)

    if to_method == "osfs":
        logger.debug("Create to OSFS connection")
        to_fs = osfs_connection(logger, to_dir)

    # Do the move
    walker = Walker(filter=[from_filter], ignore_errors=True, max_depth=1)
    # Create a list of files to be transferred based on the filter.
    total_files = list(walker.files(from_fs))
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

        # Confirm if single file mode condition is satisfied
        if len(total_files) == 1 and new_filename:
            should_rename = True
        else:
            should_rename = False

        transfer_file(from_fs, to_fs, path, should_rename, new_filename=new_filename)

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
