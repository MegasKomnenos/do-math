"""Clock and identifier port: wall time, monotonic time, waiting, new registry IDs and random seeds."""
from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> str:
        """The current UTC time as an ISO string, the form ``file_io.parse_utc`` reads."""

    def wall(self) -> datetime:
        """The current UTC time as an aware datetime."""

    def wall_ns(self) -> int:
        """The current Unix time in nanoseconds."""

    def monotonic(self) -> float:
        """Seconds on a clock that never goes backwards."""

    def resolutions(self) -> tuple[float, float]:
        """Current (wall_seconds, monotonic_seconds), finite and nonnegative; zero means exact."""

    def sleep(self, seconds: float) -> None:
        """Wait ``seconds`` on the monotonic clock."""

    def new_id(self, prefix: str) -> str:
        """A new ``PREFIX-ULID`` whose time part is the current wall time."""

    def random_hex(self, nbytes: int) -> str:
        """``nbytes`` fresh random bytes as lowercase hexadecimal, for seeds that are not identifiers."""
