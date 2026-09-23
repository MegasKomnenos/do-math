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


def provider_wait_disposition(*, model, failure=None, attempts=1, current=None,
                              initial=300, maximum=7200, provider=None):
    """Describe an admission wait without deciding whether work should resume.

    `retry_at` is a provider observation/backoff boundary.  It is not a claim
    that a provider has capacity, nor a deadline for an activity to finish.
    """
    if not isinstance(model, str) or not model:
        raise ValueError("model is required")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    if current is None or not isinstance(current, (int, float)) or isinstance(current, bool) or not math.isfinite(current):
        raise ValueError("current must be a finite timestamp")
    if (isinstance(initial, bool) or not isinstance(initial, (int, float)) or initial <= 0 or
            isinstance(maximum, bool) or not isinstance(maximum, (int, float)) or maximum < initial):
        raise ValueError("retry bounds are invalid")
    failure = failure or {}
    if not isinstance(failure, dict):
        raise ValueError("failure must be a dictionary")
    resolved_provider = provider or provider_for(model)
    if resolved_provider not in {"codex", "claude"}:
        raise ValueError("provider is unsupported")
    # Persist whole seconds, rounding upward so the wait never ends early.
    due = math.ceil(retry_time(failure, attempts, float(current), initial=initial, maximum=maximum))
    return {"kind": "provider_admission", "provider": resolved_provider, "state": "waiting",
            "retry_at": utc(due), "retry_at_timestamp": due, "attempt": attempts}
