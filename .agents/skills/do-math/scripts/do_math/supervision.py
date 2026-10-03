"""Supervision rules shared by the scheduled operator, the engine and the status report (layer 2).

Which persisted facts may stop supervision from starting research or repair, in
which priority, and the shape of an operator report.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from .wait_rules import PROVIDER_WAIT

# Supervision blockers in priority order; the first present one decides.
# ``held`` is the local HOLD file and ``disabled`` the operator setting.
SUPERVISION_BLOCKS = ('held', 'disabled', 'user_pause', 'maintenance', 'model_policy',
                      'paused', 'closed', 'completed', 'conversation_lost', 'installation_repair')

OPERATOR_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"}, "observed_status": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "user_questions": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
    },
    "required": ["summary", "observed_status", "actions", "evidence_paths", "user_questions", "next_step"],
}


def hold_pause_reason(hold_id: str) -> str:
    """The user pause a HOLD requests; its release resumes only this exact pause."""
    return "User requested scheduled operator HOLD " + hold_id


def supervision_facts(instance: dict, runtime: dict) -> dict[str, Any]:
    """The persisted facts that decide whether supervision may start research or repair."""
    from .repair_execution import pending_installation_repair
    return {'status': runtime.get('status'), 'user_pause': deepcopy(runtime.get('user_pause')),
            'maintenance_fence': deepcopy(runtime.get('maintenance_fence')),
            'model_policy_violation': deepcopy(runtime.get('model_policy_violation')),
            'conversation_lost': (runtime.get('stop_requested') == 'conversation_lost'
                                  and instance.get('conversation_loss_policy') == 'pause'),
            'installation_repair': deepcopy(pending_installation_repair(runtime)),
            'operator_enabled': instance.get('config', {}).get('operator_enabled') is True}


def supervision_block(facts: dict[str, Any]) -> str | None:
    """The first supervision blocker present in ``facts``, or None.

    Facts without ``held`` or ``operator_enabled`` never report those blockers;
    a persisted-state view or an explicit engine start omits them.
    """
    present = {'held': facts.get('held'),
               'disabled': 'operator_enabled' in facts and not facts['operator_enabled'],
               'user_pause': facts.get('user_pause'), 'maintenance': facts.get('maintenance_fence'),
               'model_policy': facts.get('model_policy_violation'),
               'conversation_lost': facts.get('conversation_lost'),
               'installation_repair': facts.get('installation_repair'),
               **{state: facts.get('status') == state for state in ('paused', 'closed', 'completed')}}
    return next((code for code in SUPERVISION_BLOCKS if present[code]), None)


# Judgments of the scheduled supervisor (``scheduled_operator``); it reads the status and markers and acts.

def repair_report_schema(*, diagnosed=False):
    """The CLI output schema of a repair run, in OPERATOR_SCHEMA's keywords only.

    No preserved run shows a provider accepting other keywords here. The prompt
    names the allowed values; collect_repair_verification judges them on receipt.
    """
    schema = deepcopy(OPERATOR_SCHEMA)
    if diagnosed:
        schema['properties'].update(repair_outcome={'type':'string'},
            verification_evidence={'type':'array','items':{'type':'string'}})
        schema['required'].extend(['repair_outcome','verification_evidence'])
    return schema


def collect_repair_verification(output, workspace):
    """Preserve actual regression evidence; a completed model call is insufficient."""
    if not output or output.get('repair_outcome') != 'repaired' or not output.get('verification_evidence'):
        raise ValueError('diagnosed repair requires repaired outcome and regression evidence files')
    rows = []
    workspace = Path(workspace).resolve()
    for name in output['verification_evidence']:
        path = (workspace / name).resolve()
        if not path.is_relative_to(workspace) or not path.is_file():
            raise ValueError('repair verification evidence must be a real file in its workspace')
        raw = path.read_bytes()
        if not raw:
            raise ValueError('repair verification evidence is empty')
        rows.append({'path': path.relative_to(workspace).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(),
                     'bytes': len(raw)})
    return rows


def task_names(repository: Path, instance: str) -> dict[str, str]:
    """Return stable task names scoped to the exact repository and instance."""
    digest = hashlib.sha256((str(repository.resolve()) + "\0" + instance).encode("utf-8")).hexdigest()[:12]
    return {"operator": f"DoMath-Operator-{digest}", "engine": f"DoMath-Engine-{digest}", "wake": f"DoMath-Wake-{digest}"}


def retryable_tool_error(stdout: str) -> bool:
    """A busy writer lock or lost CAS is contention, not an installation failure."""
    try:
        envelope = json.loads(stdout)
    except json.JSONDecodeError:
        return False
    error = envelope.get("error") if isinstance(envelope, dict) else None
    return isinstance(error, dict) and error.get("kind") == "tool_error" and error.get("retryable") is True


def start_guard(status: dict) -> dict:
    """What the status snapshot allows before either scheduled task starts an engine (the HOLD marker is checked first).

    An explicit engine start does not depend on automatic supervision being enabled.
    """
    block = supervision_block({key: value for key, value in status.items() if key != 'operator_enabled'})
    if block == 'maintenance':
        return {'outcome':'maintenance_waiting', 'before':status}
    if block == 'model_policy':
        return {"outcome": "model_policy_waiting", "before": status}
    if block in {'user_pause', 'paused'}:
        return {"outcome": "paused", "before": status}
    if block in {'closed', 'completed'}:
        return {"outcome": "not_started", "before": status}
    if block == 'conversation_lost':
        return {'outcome': 'user_paused', 'before': status}
    if block == 'installation_repair':
        return {'outcome': 'installation_repair_waiting', 'before': status}
    providers = status.get("provider_waits", {}).get("providers", {})
    # A queued request waits on a provider whose gate is open again.
    provider_open = any(row['wait'].get('kind') == PROVIDER_WAIT
                        and providers.get(row['wait'].get('provider'), {}).get('open')
                        for row in status.get("dispatch_waits", []))
    if status.get("status") == "waiting" and provider_open:
        return {"outcome": "startable", "before": status, "reason": "provider re-observation due"}
    if status.get("status") == "waiting" and status.get("research_wake_reasons"):
        return {"outcome": "startable", "before": status, "reason": "research reconsideration due",
                "research_wake_reasons": status["research_wake_reasons"]}
    if status.get("status") not in {"ready", "running", "capacity_waiting"}:
        return {"outcome": "not_started", "before": status}
    return {"outcome": "startable", "before": status}


def wake_need(facts: dict, providers: dict, *, held: bool) -> dict:
    """Whether a one-shot wake is wanted for the earliest provider wait.

    ``held`` is the operator's HOLD marker. Returns ``{"status": "held"}`` or
    ``{"status": "not_needed"}`` when none is wanted, else ``{"wanted": {"key", "retry_at"}}``.
    """
    from .provider_wait import epoch_seconds
    block = supervision_block({**facts, 'held': held})
    blocked = block not in {None, 'disabled', 'installation_repair'}
    waits = [row for row in providers.values() if row["state"] == "waiting"]
    if blocked or block == 'disabled' or not waits:
        return {"status": "held" if blocked else "not_needed"}
    row = min(waits, key=lambda value: epoch_seconds(value["retry_at"]))
    key = row["provider"] + ":" + str(row["generation"])
    return {"wanted": {"key": key, "retry_at": row["retry_at"]}}


def wake_is_current(previous, wanted: dict, observed: dict, *, now: float) -> bool:
    """The registered wake is the wanted one and will still fire, or its engine is running.

    ``previous`` is the local registration marker, ``observed`` the task status
    and ``now`` the wall-clock time in epoch seconds.
    """
    from .provider_wait import epoch_seconds
    actual = observed.get("wake")
    future_trigger = actual and (epoch_seconds(actual.get("next_run")) or 0) > now
    running = (observed.get("engine") or {}).get("state") == "Running" or (actual or {}).get("state") == "Running"
    return bool(previous == wanted and actual and actual.get("description") == wanted["key"] and (future_trigger or running))


def blocked_check_outcome(block, status: dict) -> dict | None:
    """The supervision result when a block other than an installation repair stops the check, else None."""
    if block == 'disabled':
        return {"outcome": "disabled"}
    if block in {'user_pause', 'paused', 'closed', 'completed'}:
        return {"outcome": status.get("status", "paused"), "status": status}
    if block == 'maintenance':
        return {"outcome": "maintenance_waiting", "status": status, "model_called": False}
    if block == 'model_policy':
        return {"outcome": "model_policy_waiting", "status": status}
    if block == 'conversation_lost':
        return {"outcome": "user_paused", "status": status}
    return None


def engine_failure_recovery(latest: dict | None, *, evidence_path) -> dict | None:
    """The recovery failure a preserved failed engine run opens, or None."""
    if latest and latest.get("outcome") == "engine_failed":
        return {"kind": "engine_unavailable", "error": latest.get("error") or
                    "engine process failed with exit code " + str(latest.get("exit_code")),
                "evidence_path": str(evidence_path),
                "engine_run_directory": latest.get("run_directory")}
    return None


def engine_run_outcome(returncode: int, stdout: str) -> str:
    """A scheduled engine run completed, lost only to contention (busy), or failed."""
    if returncode == 0:
        return "completed"
    return "engine_busy" if retryable_tool_error(stdout) else "engine_failed"
