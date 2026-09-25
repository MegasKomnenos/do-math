"""Monotonic execution deadlines with UTC descriptions and a non-revoking notice."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import time

from .observations import duration_ms
from .file_io import write_bytes_atomic


def observation_window(profile_observation, field):
    """Read a selected profile's declared observation window without defaults.

    The caller must have already selected and frozen the execution profile.  A
    missing value is an unavailable capability, not permission to substitute a
    convenient global timeout.
    """
    if not isinstance(profile_observation, dict):
        raise ValueError("selected profile has no observation settings")
    value = profile_observation.get(field)
    if value is None:
        raise ValueError("selected profile lacks a positive " + field)
    duration_ms(value, field, required=True)
    return value


def notice_seconds(config, pool=None):
    if pool != "operations":
        return 0
    return min(config.get("finish_notice_seconds", 60), config["call_timeout_seconds"] / 10)


def _write(path, value):
    write_bytes_atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))


def publish(workspace: Path, execution_id: str, deadline: float | None, config: dict, pool: str, *,
            deadline_source: str, clock=time.monotonic, wall_clock=None):
    if deadline is None:
        value = {"execution_id": execution_id, "effective_deadline_at": None,
                 "remaining_ms_at_start": None, "deadline_source": "none",
                 "finish_notice_at": None, "effective_notice_ms": 0}
        _write(workspace / ".control" / "execution-window.json", value)
        return value
    remaining_ms = max(0, int((Decimal(str(deadline)) - Decimal(str(clock()))) * 1000))
    current = wall_clock or datetime.now(timezone.utc)
    finish = current + timedelta(milliseconds=remaining_ms)
    notice = notice_seconds(config, pool)
    value = {"execution_id": execution_id, "effective_deadline_at": finish.isoformat(),
             "remaining_ms_at_start": remaining_ms, "deadline_source": deadline_source,
             "finish_notice_at": (finish - timedelta(seconds=notice)).isoformat(),
             "effective_notice_ms": int(Decimal(str(notice)) * 1000)}
    _write(workspace / ".control" / "execution-window.json", value)
    return value


def request_finish(workspace: Path, deadline: float | None, config: dict, pool: str, *, clock=time.monotonic):
    if deadline is None:
        return False
    path = workspace / ".control" / "finish-request.json"
    if path.exists() or deadline - clock() > notice_seconds(config, pool):
        return False
    _write(path, {"requested_at": datetime.now(timezone.utc).isoformat(),
                  "kind": "finish_notice", "revokes_authority": False,
                  "instruction": "Submit established results, evidence and remaining obligations before the effective deadline. Partial work is acceptable under the role contract."})
    return True
