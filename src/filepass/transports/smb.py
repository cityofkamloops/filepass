import fnmatch
from typing import BinaryIO

import smbclient

from .base import CHUNK_SIZE

CONNECTION_TIMEOUT = 60


class SMBTransport:
    def __init__(self, logger, server, port, user, password, share, directory):
        self._logger = logger
        self._server = server
        self._share = share.strip("/").strip("\\")
        rel = directory.strip("/").replace("/", "\\")
        self._logger.debug(
            f"smb://{user}:passwordhere@{server}:{port}/{self._share}/{rel}"
        )

        self._unc_base = rf"\\{server}\{self._share}"
        self._unc_dir = rf"{self._unc_base}\{rel}" if rel else self._unc_base

        smbclient.register_session(
            server,
            username=user,
            password=password,
            port=int(port),
            connection_timeout=CONNECTION_TIMEOUT,
        )

    def _unc(self, name: str) -> str:
        return rf"{self._unc_dir}\{name}"

    def list(self, pattern: str = "*") -> list[str]:
        result = []
        for entry in smbclient.scandir(self._unc_dir):
            if entry.is_file() and fnmatch.fnmatch(entry.name, pattern):
                result.append(entry.name)
        return result

    def open_read(self, name: str) -> BinaryIO:
        return smbclient.open_file(self._unc(name), mode="rb")

    def write(self, name: str, src: BinaryIO) -> None:
        with smbclient.open_file(self._unc(name), mode="wb") as dst:
            while True:
                chunk = src.read(CHUNK_SIZE)
                if not chunk:
                    break
                dst.write(chunk)

    def delete(self, name: str) -> None:
        smbclient.remove(self._unc(name))

    def close(self) -> None:
        try:
            smbclient.delete_session(self._server)
        except Exception:
            pass
