import os
import time


class FileLock:
    def __init__(
        self,
        path: str,
        *,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.05,
        stale_after_seconds: float = 60.0,
    ) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds
        self.poll_interval_seconds = poll_interval_seconds
        self.stale_after_seconds = stale_after_seconds
        self._fd: int | None = None

    def __enter__(self):
        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                self._fd = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                os.write(self._fd, str(os.getpid()).encode("ascii", "ignore"))
                return self
            except FileExistsError:
                if self._is_stale():
                    self._force_release()
                    continue
                if time.time() >= deadline:
                    raise TimeoutError(f"Timed out acquiring lock '{self.path}'.")
                time.sleep(self.poll_interval_seconds)

    def __exit__(self, exc_type, exc, tb):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self._force_release()

    def _is_stale(self) -> bool:
        try:
            return (time.time() - os.path.getmtime(self.path)) > self.stale_after_seconds
        except FileNotFoundError:
            return False

    def _force_release(self) -> None:
        try:
            os.remove(self.path)
        except FileNotFoundError:
            return
