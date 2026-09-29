"""Monotonic execution deadlines with UTC descriptions and a non-revoking notice."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path

from .migration_defaults import clock_or_system
from .file_io import write_bytes_atomic


def notice_seconds(config):
    """Finish notice before a per-call deadline; only operational calls have one."""
    return min(config["finish_notice_seconds"], config["call_timeout_seconds"] / 10)


def _write(path, value):
    write_bytes_atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))


def publish(workspace: Path, execution_id: str, deadline: float | None, config: dict, *,
            clock=None, wall_clock=None):
    """Describe the call's deadline in UTC; only an operational call has one."""
    if deadline is None:
        value = {"execution_id": execution_id, "effective_deadline_at": None,
                 "remaining_ms_at_start": None, "deadline_source": "none",
                 "finish_notice_at": None, "effective_notice_ms": 0}
        _write(workspace / ".control" / "execution-window.json", value)
        return value
    clock = clock or clock_or_system(None).monotonic
    remaining_ms = max(0, int((Decimal(str(deadline)) - Decimal(str(clock()))) * 1000))
    current = wall_clock or clock_or_system(None).wall()
    finish = current + timedelta(milliseconds=remaining_ms)
    notice = notice_seconds(config)
    value = {"execution_id": execution_id, "effective_deadline_at": finish.isoformat(),
             "remaining_ms_at_start": remaining_ms, "deadline_source": "operational_call",
             "finish_notice_at": (finish - timedelta(seconds=notice)).isoformat(),
             "effective_notice_ms": int(Decimal(str(notice)) * 1000)}
    _write(workspace / ".control" / "execution-window.json", value)
    return value


def request_finish(workspace: Path, deadline: float | None, config: dict, *, clock=None, now_iso=None):
    if deadline is None:
        return False
    path = workspace / ".control" / "finish-request.json"
    clock = clock or clock_or_system(None).monotonic
    if path.exists() or deadline - clock() > notice_seconds(config):
        return False
    _write(path, {"requested_at": now_iso or clock_or_system(None).now(),
                  "kind": "finish_notice", "revokes_authority": False,
                  "instruction": "Submit established results, evidence and remaining obligations before the effective deadline. Partial work is acceptable under the role contract."})
    return True
