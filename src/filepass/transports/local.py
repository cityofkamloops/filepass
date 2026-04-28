import fnmatch
import shutil
from pathlib import Path
from typing import BinaryIO

from .base import CHUNK_SIZE


class LocalTransport:
    def __init__(self, logger, directory: str):
        self._logger = logger
        self._base = Path(directory)
        self._logger.debug(f"local connection to dir: {self._base}")
        if not self._base.is_dir():
            raise FileNotFoundError(f"Local directory does not exist: {self._base}")

    def list(self, pattern: str = "*") -> list[str]:
        return [
            entry.name
            for entry in self._base.iterdir()
            if entry.is_file() and fnmatch.fnmatch(entry.name, pattern)
        ]

    def open_read(self, name: str) -> BinaryIO:
        return (self._base / name).open("rb")

    def write(self, name: str, src: BinaryIO) -> None:
        with (self._base / name).open("wb") as dst:
            shutil.copyfileobj(src, dst, length=CHUNK_SIZE)

    def delete(self, name: str) -> None:
        (self._base / name).unlink()

    def close(self) -> None:
        pass
