"""Monotonic execution deadlines with UTC descriptions and a non-revoking notice."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import time


def notice_seconds(config, pool=None):
    values = [config.get("finish_notice_seconds", 60), config["run_timeout_seconds"] / 10]
    if pool == "operations":
        values.append(config["call_timeout_seconds"] / 10)
    return min(values)


def dispatch_reserve_seconds(config):
    """Ordinary executions are not started this close to the run deadline; they could not finish."""
    return min(config.get("dispatch_reserve_seconds", 300), config["run_timeout_seconds"] / 10)


def _write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def publish(workspace: Path, execution_id: str, deadline: float, config: dict, pool: str, *,
            deadline_source: str, clock=time.monotonic, wall_clock=None):
    remaining = max(0, deadline - clock())
    current = wall_clock or datetime.now(timezone.utc)
    finish = current + timedelta(seconds=remaining)
    notice = notice_seconds(config, pool)
    value = {"execution_id": execution_id, "effective_deadline_at": finish.isoformat(),
             "remaining_seconds_at_start": remaining, "deadline_source": deadline_source,
             "finish_notice_at": (finish - timedelta(seconds=notice)).isoformat(),
             "effective_notice_seconds": notice}
    _write(workspace / "execution-window.json", value)
    return value


def request_finish(workspace: Path, deadline: float, config: dict, pool: str, *, clock=time.monotonic):
    path = workspace / "finish-request.json"
    if path.exists() or deadline - clock() > notice_seconds(config, pool):
        return False
    _write(path, {"requested_at": datetime.now(timezone.utc).isoformat(),
                  "kind": "finish_notice", "revokes_authority": False,
                  "instruction": "Submit established results, evidence and remaining obligations before the effective deadline. Partial work is acceptable under the role contract."})
    return True
