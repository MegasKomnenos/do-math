"""Real clock port: the operating system's clocks and entropy."""
from datetime import datetime, timezone
import secrets
import time

from .ids import ENTROPY_BYTES, ulid


class SystemClock:
    def now(self) -> str:
        return self.wall().isoformat()

    def wall(self) -> datetime:
        return datetime.now(timezone.utc)

    def wall_ns(self) -> int:
        return time.time_ns()

    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def new_id(self, prefix: str) -> str:
        return ulid(prefix, time.time_ns() // 1_000_000, secrets.token_bytes(ENTROPY_BYTES))
