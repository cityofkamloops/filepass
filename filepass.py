import sys

import fs
import os
import fs.smbfs
import fs.ftpfs
from fs.walk import Walker
import logging
import graypy


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


def ftps_connection(logger, user, pw, svr, port, tls, dir):
    logger.debug(
        "ftps host: {} user: {} password: {} port: {} tls: {} dir: {}".format(
            svr, user, "passwordhere", port, tls, dir
        )
    )
    # fs_conn = fs.ftpfs.FTPFS(host=svr, user=user, passwd=pw, port=port, tls=tls)
    fs_conn = fs.open_fs("ftps://{}:{}@{}/{}".format(user, pw, svr, dir))
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

    if from_method == "ftps":
        logger.debug("Create from FTPS connection")
        from_fs = ftps_connection(
            logger, from_user, from_pw, from_svr, from_port, True, from_dir
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
    if to_method == "ftps":
        logger.debug("Create to FTPS connection")
        to_fs = ftps_connection(logger, to_user, to_pw, to_svr, to_port, True, to_dir)

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


def main():

    # Load Environmental Variables

    # GREYLOG_SERVER
    # GREYLOG_PORT
    # INTEGRATION_NAME

    from_user = os.environ.get("FROMUSER")
    from_pw = os.environ.get("FROMPW")
    from_svr = os.environ.get("FROMSVR")
    from_port = os.environ.get("FROMPORT")
    from_dir = os.environ.get("FROMDIR")
    from_share = os.environ.get("FROMSMBSHARE")
    from_method = os.environ.get("FROMMETHOD")
    from_delete = os.environ.get("FROMDELETE")
    from_filter = os.environ.get("FROMFILEFILTER")

    to_user = os.environ.get("TOUSER")
    to_pw = os.environ.get("TOPW")
    to_svr = os.environ.get("TOSVR")
    to_port = os.environ.get("TOPORT")
    to_dir = os.environ.get("TODIR")
    to_share = os.environ.get("TOSMBSHARE")
    to_method = os.environ.get("TOMETHOD")
    to_delete = os.environ.get("TODELETE")

    filepass_logger = logging.getLogger("filepass_logger")
    filepass_logger.setLevel(logging.DEBUG)

    handler = graypy.GELFTCPHandler(
        os.environ.get("GREYLOG_SERVER"), int(os.environ.get("GREYLOG_PORT"))
    )
    filepass_logger.addHandler(handler)

    handler_std = logging.StreamHandler(sys.stdout)
    filepass_logger.addHandler(handler_std)

    logger = logging.LoggerAdapter(
        filepass_logger,
        {
            "from_method": from_method,
            "from_user": from_user,
            "from_svr": from_svr,
            "from_port": from_port,
            "from_share": from_share,
            "from_dir": from_dir,
            "from_filter": from_filter,
            "to_method": to_method,
            "to_user": to_user,
            "to_svr": to_svr,
            "to_port": to_port,
            "to_share": to_share,
            "to_dir": to_dir,
            "integration": "filepass",
            "filepass_name": os.environ.get("INTEGRATION_NAME"),
        },
    )
    try:
        file_pass(
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
        )
    except:
        logger.exception("Critical error found", stack_info=True)


if __name__ == "__main__":
    main()
