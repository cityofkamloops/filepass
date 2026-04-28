import os
import threading


def _timeout_from_env() -> int:
    raw = os.environ.get("FILEPASS_PER_FILE_TIMEOUT")
    if not raw:
        return 600
    try:
        value = int(raw)
    except ValueError:
        return 600
    return value if value > 0 else 600


PER_FILE_TIMEOUT = _timeout_from_env()


class WatchdogTimeout(TimeoutError):
    """Raised when a guarded operation exceeds its time budget."""


def run_with_timeout(fn, timeout, *args, _label=None, **kwargs):
    """Run ``fn(*args, **kwargs)`` on a daemon thread, bound by ``timeout`` seconds.

    On timeout, raises WatchdogTimeout. The worker thread is left running
    (it cannot be safely killed) and the caller is expected to abort the
    process so the OS can reclaim any blocked sockets.

    ``_label`` is used in the timeout message; pass a human-readable
    description (e.g. the filename being processed) so Graylog ERROR
    records identify the stuck unit of work without cross-referencing
    earlier debug lines.
    """
    result: list = []
    error: list = []

    def runner():
        try:
            result.append(fn(*args, **kwargs))
        except BaseException as e:
            error.append(e)

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        label = _label or getattr(fn, "__name__", "operation")
        raise WatchdogTimeout(f"{label} exceeded {timeout}s")
    if error:
        raise error[0]
    return result[0] if result else None
