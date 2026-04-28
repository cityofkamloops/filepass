from .base import CHUNK_SIZE, Transport
from .local import LocalTransport
from .sftp import SFTPTransport
from .smb import SMBTransport

__all__ = [
    "Transport",
    "CHUNK_SIZE",
    "LocalTransport",
    "SFTPTransport",
    "SMBTransport",
    "make_transport",
]


def make_transport(conn, logger):
    """Factory: build a Transport from a ConnectionDetails."""
    from ..filepass_config import FilepassMethod

    if conn.method == FilepassMethod.LOCAL:
        return LocalTransport(logger, conn.dir)
    if conn.method == FilepassMethod.SFTP:
        return SFTPTransport(
            logger,
            host=conn.server,
            port=int(conn.port),
            user=conn.user,
            password=conn.password,
            directory=conn.dir,
        )
    if conn.method == FilepassMethod.SMB:
        return SMBTransport(
            logger,
            server=conn.server,
            port=int(conn.port),
            user=conn.user,
            password=conn.password,
            share=conn.share,
            directory=conn.dir,
        )
    raise ValueError(f"Unsupported method: {conn.method}")
