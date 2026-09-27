"""Trusted local stream batches; provider JSON cannot supply their provenance."""
from dataclasses import dataclass
from collections.abc import Callable
import json
from pathlib import Path


def decode_observation_row(raw: bytes) -> dict:
    """Decode one nonblank stdout row; an undecodable row is still an observed event."""
    try:
        return json.loads(raw)
    except (UnicodeError, json.JSONDecodeError):
        return {"type": "unparsed_observation", "bytes": len(raw.rstrip(b"\n"))}


@dataclass(frozen=True)
class ObservationBatch:
    """Rows decoded from one read of the stream.

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

    def source(self, offset, *, start_offset):
        return {'stream': 'stdout.jsonl', 'start_offset': start_offset, 'end_offset': offset, 'received_at': self.received_at,
                'received_monotonic': self.received_monotonic}

    def stream_size(self):
        return self.stream_path.stat().st_size if self.stream_path.exists() else 0

    def caught_up(self):
        return self.end_offset >= self.stream_size()
