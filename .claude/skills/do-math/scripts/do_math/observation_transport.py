"""Trusted local stream batches; provider JSON cannot supply their provenance."""
from dataclasses import dataclass
from collections.abc import Callable
from pathlib import Path


@dataclass(frozen=True)
class ObservationBatch:
    events: list[dict]
    offsets: list[tuple[int, int]]
    received_at: str
    received_monotonic: float
    bytes_received: int
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
