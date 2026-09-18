"""Provider admission metadata; no model calls and no research decisions."""
from datetime import datetime, timezone
import math


def provider_for(model: str) -> str:
    return "claude" if model.startswith(("claude:", "claude-")) else "codex"


def timestamp(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return float(value)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.timestamp() if parsed.tzinfo is not None else None
        except ValueError:
            return None
    return None


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value is not None else None


def retry_time(failure, attempts, current, initial=300, maximum=7200):
    known = timestamp(failure.get("retry_at"))
    if known is not None and known > current:
        return known
    return current + min(maximum, initial * (2 ** min(max(0, attempts - 1), 20)))
