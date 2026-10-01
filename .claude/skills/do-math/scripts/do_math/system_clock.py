"""Real clock port: the operating system's clocks and entropy."""
from datetime import datetime, timezone
import secrets
import time

from .ids import ENTROPY_BYTES, ulid


def now() -> str:
    """The current UTC time as an ISO string, the form ``values.parse_utc`` reads."""
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    """Create a canonical uppercase ULID with the caller's registry prefix."""
    return ulid(prefix, time.time_ns() // 1_000_000, secrets.token_bytes(ENTROPY_BYTES))


class SystemClock:
    def now(self) -> str:
        return self.wall().isoformat()

    def wall(self) -> datetime:
        return datetime.now(timezone.utc)

    def wall_ns(self) -> int:
        return time.time_ns()

    def monotonic(self) -> float:
        return time.monotonic()

    def resolutions(self) -> tuple[float, float]:
        return time.get_clock_info('time').resolution, time.get_clock_info('monotonic').resolution

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def new_id(self, prefix: str) -> str:
        return ulid(prefix, time.time_ns() // 1_000_000, secrets.token_bytes(ENTROPY_BYTES))

    def random_hex(self, nbytes: int) -> str:
        return secrets.token_hex(nbytes)
