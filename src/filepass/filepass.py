import sys
from urllib.parse import quote

import fs
import fs.ftpfs
import fs.smbfs
from fs.walk import Walker

from .filepass_config import ConnectionDetails, FilepassMethod


# File Transfer Types
def sftp_connection(logger, conn_details: ConnectionDetails):
    """
    Establishes an SFTP connection based on provided connection details.
    Parameters:
        logger (Logger): logger object for logging messages.
        conn_details: Object containing connection details: user, password, server, port and directory (required).
                        port defaults to '22', if not explictly defined.
    """
    logger.debug(
        "sftp://{}:{}@{}:{}{}".format(
            conn_details.user,
            "passwordhere",
            conn_details.server,
            conn_details.port,
            conn_details.dir,
        )
    )
    fs_conn = fs.open_fs(
        "sftp://{}:{}@{}:{}{}".format(
            quote(conn_details.user),
            quote(conn_details.password),
            conn_details.server,
            conn_details.port,
            conn_details.dir,
        )
    )
    return fs_conn


def smb_connection(logger, conn_details: ConnectionDetails):
    """
    Establishes an SMB connection based on provided connection details.
    Parameters:
        logger (Logger): logger object for logging messages.
        conn_details: Object containing connection details: user, password, server, port, share, and directory (required).
                        port defaults to '445', if not explictly defined.
    """
    logger.debug(
        "smb://{}:{}@{}:{}/{}".format(
            conn_details.user,
            "passwordhere",
            conn_details.server,
            conn_details.port,
            conn_details.share + conn_details.dir,
        )
    )
    fs_conn = fs.open_fs(
        "smb://{}:{}@{}:{}/{}?direct-tcp=True&name-port=139&timeout=15&domain=".format(
            quote(conn_details.user),
            quote(conn_details.password),
            conn_details.server,
            conn_details.port,
            conn_details.share + conn_details.dir,
        )
    )
    # timeout, name - port, direct - tcp, hostname, and domain.
    return fs_conn


def osfs_connection(logger, conn_details: ConnectionDetails):
    """
    Establishes an LOCAL connection based on provided connection details.
    Parameters:
        logger (Logger): logger object for logging messages.
        conn_details: Object containing connection details: directory (required).
    """
    logger.debug("osfs/local connection to dir: {}".format(conn_details.dir))
    fs_conn = fs.open_fs(conn_details.dir)
    return fs_conn


# Boolean parameter to add ability to rename target file in single file mode
def transfer_file(from_fs, to_fs, filename, should_rename=False, new_filename=None):
    """
    Transfer file using 'fs' and rename file in single file mode (new_filename required)
    """
    target_filename = new_filename if new_filename and should_rename else filename
    to_fs.writefile(target_filename, from_fs.open(filename, "rb"))


def file_pass(
    logger,
    from_conn: ConnectionDetails,
    from_delete,
    from_filter,
    to_conn: ConnectionDetails,
    to_delete,
    file_overwrite,
    new_filename=None,
):
    connection_functions = {
        FilepassMethod.SFTP: sftp_connection,
        FilepassMethod.SMB: smb_connection,
        FilepassMethod.LOCAL: osfs_connection,
    }

    from_fs = connection_functions[from_conn.method](logger, from_conn)
    to_fs = connection_functions[to_conn.method](logger, to_conn)

    logger.debug(
        f"Establishing {from_conn.method} connection from server: {from_conn.server}\n Directory: {from_conn.dir}"
    )
    logger.debug(
        f"Establishing {to_conn.method} connection from server: {to_conn.server}\n Directory: {to_conn.dir}"
    )
    # Do the move
    walker = Walker(filter=[from_filter], ignore_errors=True, max_depth=1)
    # Create a list of files to be transferred based on the filter.
    total_files = list(walker.files(from_fs))
    for path in walker.files(from_fs):
        logger.debug("File to move: {}".format(path))

        if to_delete.upper() == "YES" and to_fs.exists(path):
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

        # No overwrite feature
        # Check the environment variable status and if the file exists
        if file_overwrite.upper() == "NO" and to_fs.exists(path):
            logger.debug(f"File overwrite is disabled. \nFile {path} not transferred")
            pass
        else:
            # Confirm if single file mode condition is satisfied
            if len(total_files) == 1 and new_filename:
                should_rename = True
            else:
                should_rename = False

            transfer_file(
                from_fs, to_fs, path, should_rename, new_filename=new_filename
            )

            if from_delete.upper() == "YES" and from_fs.exists(path):
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
