import socket
import sys
from urllib.parse import quote

import fs
import fs.ftpfs
import fs.smbfs
from fs.sshfs import SSHFS
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
    fs_conn = SSHFS(
        host=conn_details.server,
        user=conn_details.user,
        passwd=conn_details.password,
        port=int(conn_details.port),
        keepalive=10,
        timeout=30,
    )
    # Use OS-level TCP keepalive to detect dead SSH connections.
    # Without this, a silently dropped connection hangs the process forever
    # because paramiko cannot detect the failure on its own.
    # Probes start after 30s idle, retry every 10s, give up after 3 failures (~60s total).
    transport = fs_conn._client.get_transport()
    if transport and transport.sock:
        transport.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
        transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
        transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
    if conn_details.dir:
        fs_conn = fs_conn.opendir(conn_details.dir)
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
    with from_fs.open(filename, "rb", prefetch=False) as src_file:
        to_fs.writefile(target_filename, src_file)


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

    try:
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
        total_count = len(total_files)
        logger.debug(f"Found {total_count} file(s) to process")

        # Pre-fetch destination file list to avoid per-file network round-trips
        # this should speed up execution on large filesets
        to_walker = Walker(ignore_errors=True, max_depth=1)
        existing_dest_files = set(to_walker.files(to_fs))

        for index, path in enumerate(total_files, start=1):
            logger.debug(f"[{index}/{total_count}] File to move: {path}")

            if to_delete.upper() == "YES" and path in existing_dest_files:
                logger.debug(f"[{index}/{total_count}] delete (to): {path}")
                try:
                    to_fs.remove(path)
                    existing_dest_files.discard(path)
                except fs.errors.ResourceNotFound:
                    logger.warning(
                        f"[{index}/{total_count}] (To) file ResourceNotFound: {path}"
                    )
            else:
                logger.debug(f"[{index}/{total_count}] No delete (to): {path}")

            # No overwrite feature
            # Check the environment variable status and if the file exists
            if (file_overwrite or "YES").upper() == "NO" and path in existing_dest_files:
                logger.debug(
                    f"[{index}/{total_count}] File overwrite is disabled. File {path} not transferred"
                )
            else:
                # Confirm if single file mode condition is satisfied
                if len(total_files) == 1 and new_filename:
                    should_rename = True
                else:
                    should_rename = False

                transfer_file(
                    from_fs, to_fs, path, should_rename, new_filename=new_filename
                )
                logger.debug(f"[{index}/{total_count}] Transferred: {path}")
                existing_dest_files.add(path)

                if from_delete.upper() == "YES":
                    logger.debug(f"[{index}/{total_count}] delete (from): {path}")
                    try:
                        from_fs.remove(path)
                    except fs.errors.ResourceNotFound:
                        logger.warning(
                            f"[{index}/{total_count}] ResourceNotFound: {path}"
                        )
                else:
                    logger.debug(f"[{index}/{total_count}] No delete (from): {path}")

        logger.debug(f"Completed processing {total_count} file(s)")
    finally:
        from_fs.close()
        to_fs.close()
