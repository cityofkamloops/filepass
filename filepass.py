import fs
import os
import fs.smbfs
import fs.ftpfs
from fs.walk import Walker
import fplogger


log = fplogger.FPLogger()


def logger(log_level, log_message):
    log.write(log_level, log_message)


# File Transfer Types
def ssh_connection(user, pw, svr, port, dir):
    logger(0, "ssh://{}:{}@{}:{}{}".format(user, "passwordhere", svr, port, dir))
    fs_conn = fs.open_fs("ssh://{}:{}@{}:{}{}".format(user, pw, svr, port, dir))
    return fs_conn


def smb_connection(user, pw, svr, port, smbshare, dir):
    logger(
        0,
        "smb://{}:{}@{}:{}/{}".format(user, "passwordhere", svr, port, smbshare + dir),
    )
    fs_conn = fs.open_fs(
        "smb://{}:{}@{}:{}/{}?direct-tcp=True&name-port=139&timeout=15&domain=".format(
            user, pw, svr, port, smbshare + dir
        )
    )
    # timeout, name - port, direct - tcp, hostname, and domain.
    return fs_conn


def ftps_connection(user, pw, svr, port, tls, dir):
    logger(
        0,
        "ftps host: {} user: {} password: {} port: {} tls: {} dir: {}".format(
            svr, user, "passwordhere", port, tls, dir
        ),
    )
    # fs_conn = fs.ftpfs.FTPFS(host=svr, user=user, passwd=pw, port=port, tls=tls)
    fs_conn = fs.open_fs("ftps://{}:{}@{}/{}".format(user, pw, svr, dir))
    return fs_conn


def transfer_file(from_fs, to_fs, filename):
    to_fs.writefile(filename, from_fs.open(filename, "rb"))


def main():
    # Load Environmental Variables
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

    # From File System
    if from_method == "ssh":
        logger(0, "Create from SSH connection")
        from_fs = ssh_connection(from_user, from_pw, from_svr, from_port, from_dir)

    if from_method == "smb":
        logger(0, "Create from SMB connection")
        from_fs = smb_connection(
            from_user, from_pw, from_svr, from_port, from_share, from_dir
        )

    if from_method == "ftps":
        logger(0, "Create from FTPS connection")
        from_fs = ftps_connection(
            from_user, from_pw, from_svr, from_port, True, from_dir
        )

    # To File System
    if to_method == "ssh":
        logger(0, "Create to SSH connection")
        to_fs = ssh_connection(to_user, to_pw, to_svr, to_port, to_dir)
    if to_method == "smb":
        logger(0, "Create to SMB connection")
        to_fs = smb_connection(to_user, to_pw, to_svr, to_port, to_share, to_dir)
    if to_method == "ftps":
        logger(0, "Create to FTPS connection")
        to_fs = ftps_connection(to_user, to_pw, to_svr, to_port, True, to_dir)

    # Do the move
    walker = Walker(filter=[from_filter], ignore_errors=True, max_depth=1)

    for path in walker.files(from_fs):
        logger(0, "File to move: {}".format(path))

        if to_delete == "yes" and to_fs.exists(path):
            logger(0, "delete (to): {}".format(path))
            if to_fs.exists(path):
                try:
                    to_fs.remove(path)
                except fs.errors.ResourceNotFound:
                    logger(2, "(To) file ResourceNotFound: {}".format(path))
            else:
                logger(1, "file {} not found".format(path))
        else:
            logger(0, "No delete (to): {}".format(path))

        # todo: document, paths with files should be at the lowest level (no sub dirs)
        transfer_file(from_fs, to_fs, path)

        if from_delete == "yes" and from_fs.exists(path):
            logger(0, "delete (from): {}".format(path))
            if from_fs.exists(path):
                try:
                    from_fs.remove(path)
                except fs.errors.ResourceNotFound:
                    logger(2, "ResourceNotFound: {}".format(path))
            else:
                logger(1, "file {} not found".format(path))

        else:
            logger(0, "No delete (from): {}".format(path))

    from_fs.close()
    to_fs.close()


if __name__ == "__main__":
    main()
