"""Trusted local stream batches; provider JSON cannot supply their provenance."""
from dataclasses import dataclass
from collections.abc import Callable
from pathlib import Path
from .values import strict_json_loads


def decode_observation_row(raw: bytes) -> dict:
    """Decode one nonblank stdout row; an undecodable row is still an observed event."""
    try:
        event = strict_json_loads(raw)
        if not isinstance(event, dict):
            raise ValueError('provider observation must be an object')
        return event
    except (UnicodeError, ValueError):
        return {"type": "unparsed_observation", "bytes": len(raw.rstrip(b"\n"))}


@dataclass(frozen=True)
class ObservationBatch:
    """Consecutive rows decoded from a bounded part of one stream read.

    ``rows[i]`` holds the exact bytes of ``events[i]`` at ``offsets[i]``; its
    stream row number (nonblank rows, from zero) is ``first_row + i``.
    """
    events: list[dict]
    offsets: list[tuple[int, int]]
    rows: list[bytes]
    first_row: int
    received_at: str
    received_monotonic: float
    end_offset: int
    stream_path: Path
    is_terminated: Callable[[], bool]
    # Direct batches represent a whole read. Runner parts mark its last part,
    # so a collector can join one read without moving its tick boundary.
    ends_read: bool = True

    def source(self, offset, *, start_offset):
        return {'stream': 'stdout.jsonl', 'start_offset': start_offset, 'end_offset': offset, 'received_at': self.received_at,
                'received_monotonic': self.received_monotonic}

    def stream_size(self):
        return self.stream_path.stat().st_size if self.stream_path.exists() else 0

    def caught_up(self):
        return self.ends_read and self.end_offset >= self.stream_size()
