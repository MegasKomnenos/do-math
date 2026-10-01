"""Fake clock port: wall and monotonic time move only when a test moves them.

``sleep`` advances both clocks, so code that waits finishes at once while its
elapsed time still counts. ``set_wall`` moves the wall clock alone (backwards
too); ``advance`` moves both. Identifiers are deterministic: time part from the
fake wall clock, entropy from a counter; random seeds are a hash of the same counter.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import math

from do_math.ids import ENTROPY_BYTES, ulid

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class FakeClock:
    def __init__(self, wall=datetime(2026, 1, 1, tzinfo=timezone.utc), monotonic=1000.0, counter=0,
                 wall_resolution=0.0, monotonic_resolution=0.0):
        self._wall, self._monotonic, self._counter = wall, float(monotonic), counter
        self._resolutions = float(wall_resolution), float(monotonic_resolution)
        if any(not math.isfinite(value) or value < 0 for value in self._resolutions):
            raise ValueError('clock resolutions must be finite and nonnegative')

    def state(self):
        """Time, entropy counter and both resolutions; ``FakeClock(*state)`` restores all five."""
        return self._wall, self._monotonic, self._counter, *self._resolutions

    def now(self) -> str:
        return self.wall().isoformat()

    def wall(self) -> datetime:
        return self._wall

    def wall_ns(self) -> int:
        return (self._wall - EPOCH) // timedelta(microseconds=1) * 1000

    def monotonic(self) -> float:
        return self._monotonic

    def resolutions(self) -> tuple[float, float]:
        """Zero is an exact virtual clock, independent of host clock ticks."""
        return self._resolutions

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)

    def new_id(self, prefix: str) -> str:
        self._counter += 1
        return ulid(prefix, self.wall_ns() // 1_000_000, self._counter.to_bytes(ENTROPY_BYTES, 'big'))

    def random_hex(self, nbytes: int) -> str:
        self._counter += 1
        return hashlib.shake_256(b'random_hex' + self._counter.to_bytes(8, 'big')).hexdigest(nbytes)

    def advance(self, seconds):
        if seconds < 0:
            raise ValueError("normal clock advance must be nonnegative; use set_wall for wall-clock regression")
        self._wall += timedelta(seconds=seconds)
        self._monotonic += seconds

    def set_wall(self, wall):
        self._wall = wall


def make_fake():
    return FakeClock()
