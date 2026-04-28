import fnmatch
import socket
import stat
from typing import BinaryIO

import paramiko

from .base import CHUNK_SIZE

CONNECT_TIMEOUT = 30
CHANNEL_TIMEOUT = 60
KEEPALIVE_INTERVAL = 10


class SFTPTransport:
    def __init__(self, logger, host, port, user, password, directory):
        self._logger = logger
        self._directory = directory.rstrip("/") or "/"
        self._logger.debug(f"sftp://{user}:passwordhere@{host}:{port}{self._directory}")

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            timeout=CONNECT_TIMEOUT,
            banner_timeout=CONNECT_TIMEOUT,
            auth_timeout=CONNECT_TIMEOUT,
            allow_agent=False,
            look_for_keys=False,
        )

        transport = self._client.get_transport()
        # App-level SSH keepalive: paramiko sends ignore packets every N seconds.
        transport.set_keepalive(KEEPALIVE_INTERVAL)
        # OS-level TCP keepalive: detect a fully dead peer.
        # Probes start after 30s idle, retry every 10s, give up after 3 failures (~60s total).
        if transport.sock:
            transport.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
            transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
            transport.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)

        self._sftp = self._client.open_sftp()
        # Bound every blocking SFTP read/write/close. Without this, paramiko's
        # internal Event.wait() blocks forever when the server is stuck-but-alive
        # (the failure mode TCP keepalive cannot detect).
        self._sftp.get_channel().settimeout(CHANNEL_TIMEOUT)

    def _remote(self, name: str) -> str:
        if self._directory == "/":
            return f"/{name}"
        return f"{self._directory}/{name}"

    def list(self, pattern: str = "*") -> list[str]:
        result = []
        for entry in self._sftp.listdir_attr(self._directory):
            if entry.st_mode is None or stat.S_ISREG(entry.st_mode):
                if fnmatch.fnmatch(entry.filename, pattern):
                    result.append(entry.filename)
        return result

    def open_read(self, name: str) -> BinaryIO:
        f = self._sftp.open(self._remote(name), "rb")
        # Disable prefetch — same fix as the previous codebase. Prefetch in
        # paramiko spawns a background reader that can hang independently.
        f.set_pipelined(False)
        return f

    def write(self, name: str, src: BinaryIO) -> None:
        with self._sftp.open(self._remote(name), "wb") as dst:
            dst.set_pipelined(True)
            while True:
                chunk = src.read(CHUNK_SIZE)
                if not chunk:
                    break
                dst.write(chunk)

    def delete(self, name: str) -> None:
        try:
            self._sftp.remove(self._remote(name))
        except IOError as e:
            # paramiko raises IOError("No such file") for missing files
            if "No such file" in str(e):
                raise FileNotFoundError(name) from e
            raise

    def close(self) -> None:
        try:
            self._sftp.close()
        except Exception:
            pass
        try:
            self._client.close()
        except Exception:
            pass
