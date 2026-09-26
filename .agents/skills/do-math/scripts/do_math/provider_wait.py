"""Provider admission metadata; no model calls and no research decisions."""
from datetime import datetime, timezone
import math

from .file_io import parse_utc


def provider_for(model: str) -> str:
    return "claude" if model.startswith(("claude:", "claude-")) else "codex"


def epoch_seconds(value):
    """Seconds since the epoch of a finite number or a zoned ISO time; otherwise None."""
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return float(value)
    if isinstance(value, str):
        try:
            return parse_utc(value).timestamp()
        except ValueError:
            return None
    return None


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value is not None else None


def retry_time(failure, attempts, current, initial, maximum):
    known = epoch_seconds(failure.get("retry_at"))
    if known is not None and known > current:
        return known
    return current + min(maximum, initial * (2 ** min(max(0, attempts - 1), 20)))


def gate_open(row, now):
    """A provider gate admits new work: available, or waiting with its retry time reached.

    ``row`` is a stored gate (``retry_at`` in epoch seconds); a checking gate
    stays closed until its probe owner reports.
    """
    return row["state"] == "available" or row["state"] == "waiting" and row["retry_at"] <= now
