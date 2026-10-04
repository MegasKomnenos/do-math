"""Monotonic execution deadlines with UTC descriptions and a non-revoking notice."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path

from .file_io import write_bytes_atomic
from .execution_profiles import WORK_ROLES
from .model_policy import ROLE_TIERS


# Every AI role uses its frozen profile window. A work role has no elapsed limit.
AI_CALL_TIME_RULES = {role: None if role in WORK_ROLES else 'call_timeout_seconds' for role in ROLE_TIERS}


def call_deadline(role, config, *, clock):
    field = AI_CALL_TIME_RULES[role]
    return None if field is None else clock() + config[field]


def deadline_passed(deadline, *, clock):
    return deadline is not None and clock() >= deadline


def notice_seconds(config):
    """Finish notice before a per-call deadline; only operational calls have one."""
    return min(config["finish_notice_seconds"], config["call_timeout_seconds"] / 10)


def _write(path, value):
    write_bytes_atomic(path,json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))


def publish(workspace: Path, execution_id: str, deadline: float | None, config: dict, *,
            clock, wall_clock):
    """Describe the call's deadline in UTC; only an operational call has one."""
    if deadline is None:
        value = {"execution_id": execution_id, "effective_deadline_at": None,
                 "remaining_ms_at_start": None, "deadline_source": "none",
                 "finish_notice_at": None, "effective_notice_ms": 0}
        _write(workspace / ".control" / "execution-window.json", value)
        return value
    remaining_ms = max(0, int((Decimal(str(deadline)) - Decimal(str(clock()))) * 1000))
    current = wall_clock
    finish = current + timedelta(milliseconds=remaining_ms)
    notice = notice_seconds(config)
    value = {"execution_id": execution_id, "effective_deadline_at": finish.isoformat(),
             "remaining_ms_at_start": remaining_ms, "deadline_source": "operational_call",
             "finish_notice_at": (finish - timedelta(seconds=notice)).isoformat(),
             "effective_notice_ms": int(Decimal(str(notice)) * 1000)}
    _write(workspace / ".control" / "execution-window.json", value)
    return value


def request_finish(workspace: Path, deadline: float | None, config: dict, *, clock, now_iso):
    if deadline is None:
        return False
    path = workspace / ".control" / "finish-request.json"
    if path.exists() or deadline - clock() > notice_seconds(config):
        return False
    _write(path, {"requested_at": now_iso,
                  "kind": "finish_notice", "revokes_authority": False,
                  "instruction": "Submit established results, evidence and remaining obligations before the effective deadline. Partial work is acceptable under the role contract."})
    return True
