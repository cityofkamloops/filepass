import os
from typing import BinaryIO, Protocol, runtime_checkable


def _chunk_size_from_env() -> int:
    raw = os.environ.get("FILEPASS_CHUNK_BYTES")
    if not raw:
        return 1 << 20  # 1 MiB
    try:
        value = int(raw)
    except ValueError:
        return 1 << 20
    return value if value > 0 else 1 << 20


CHUNK_SIZE = _chunk_size_from_env()


@runtime_checkable
class Transport(Protocol):
    """File-transfer interface. All paths are bare filenames (no separators).

    Each transport is bound to a single base directory at construction time;
    list/open/write/delete operate relative to that directory.
    """

    def list(self, pattern: str = "*") -> list[str]:
        """Return filenames in the base directory matching ``pattern`` (fnmatch)."""
        ...

    def open_read(self, name: str) -> BinaryIO:
        """Open ``name`` for binary reading. Caller is responsible for closing."""
        ...

    def write(self, name: str, src: BinaryIO) -> None:
        """Stream ``src`` into ``name``, overwriting if it exists."""
        ...

    def delete(self, name: str) -> None:
        """Remove ``name``. Raises FileNotFoundError if missing."""
        ...

    def close(self) -> None:
        """Release any held resources. Safe to call multiple times."""
        ...
