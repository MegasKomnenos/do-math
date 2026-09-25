"""Validation and disclosure boundaries for operational-review dispositions.

This module records a reviewer's proposed operational action.  It deliberately
does not mutate executions, activities, tasks, or permissions: ENGINE applies
an accepted proposal only after its own currentness and authority checks.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


DISPOSITION_KINDS = frozenset({
    "continue", "repair", "resume", "retry", "task_disposition", "user_decision",
})
_COMMON = {"kind", "basis_refs", "next_owner", "reason"}
_REQUIRED = {
    "continue": _COMMON | {"next_review"},
    "repair": _COMMON | {"repair_target", "meaning_preserving", "verification"},
    "resume": _COMMON | {"checkpoint_ref", "scope"},
    "retry": _COMMON | {"scope", "replay_safety"},
    "task_disposition": _COMMON | {"task_id", "task_state", "authority_ref"},
    "user_decision": _COMMON | {"question", "effect"},
}


def validate_disposition(disposition: dict[str, Any]) -> dict[str, Any]:
    """Return a detached v5 disposition or raise before any state transition."""
    if not isinstance(disposition, dict) or disposition.get("kind") not in DISPOSITION_KINDS:
        raise ValueError("operational disposition kind is unsupported")
    kind = disposition["kind"]
    if set(disposition) != _REQUIRED[kind]:
        raise ValueError("operational disposition fields do not match its kind")
    if (not isinstance(disposition["basis_refs"], list) or not disposition["basis_refs"] or
            any(not isinstance(ref, str) or not ref for ref in disposition["basis_refs"]) or
            len(set(disposition["basis_refs"])) != len(disposition["basis_refs"])):
        raise ValueError("operational disposition needs distinct basis_refs")
    for key in ("next_owner", "reason"):
        if not isinstance(disposition[key], str) or not disposition[key]:
            raise ValueError("operational disposition needs " + key)
    if kind == "continue":
        value = disposition["next_review"]
        if value is not None and (not isinstance(value, dict) or set(value) != {"at", "reason"} or
                                  not all(isinstance(value.get(k), str) and value[k] for k in ("at", "reason"))):
            raise ValueError("continue next_review is null or contains at and reason")
    elif kind == "repair":
        if not isinstance(disposition["repair_target"], str) or not disposition["repair_target"]:
            raise ValueError("repair needs repair_target")
        if not disposition["repair_target"].startswith("installation:"):
            raise ValueError("local input damage requires retry with replay_safety; repair is for installation: targets")
        if not isinstance(disposition["meaning_preserving"], bool) or not isinstance(disposition["verification"], str) or not disposition["verification"]:
            raise ValueError("repair needs preservation status and verification")
    elif kind in {"resume", "retry"}:
        if not isinstance(disposition["scope"], str) or not disposition["scope"]:
            raise ValueError(kind + " needs scope")
        key = "checkpoint_ref" if kind == "resume" else "replay_safety"
        if not isinstance(disposition[key], str) or not disposition[key]:
            raise ValueError(kind + " needs " + key)
    elif kind == "task_disposition":
        if (not isinstance(disposition["task_id"], str) or not disposition["task_id"] or
                disposition["task_state"] not in {"completed", "incomplete", "closed"} or
                not isinstance(disposition["authority_ref"], str) or not disposition["authority_ref"]):
            raise ValueError("task disposition needs task, state and authority")
    else:
        if not isinstance(disposition["question"], str) or not disposition["question"] or not isinstance(disposition["effect"], str) or not disposition["effect"]:
            raise ValueError("user decision needs question and effect")
    return deepcopy(disposition)


def disposition_is_current(disposition: dict[str, Any], current_basis_refs: set[str] | list[str]) -> bool:
    """True only if the exact observation basis still exists at apply time."""
    checked = validate_disposition(disposition)
    return set(checked["basis_refs"]).issubset(set(current_basis_refs))


def admissible_basis_refs(instance, runtime, action):
    """Canonical operational evidence, shared by input production and application."""
    from .revisions import action_repetition_waits
    target = runtime.get('executions', {}).get(action.get('target'))
    if target is None:
        raise ValueError('operational disposition has no execution target')
    refs = {target['id'], *action.get('observation_refs', []), *action.get('obligation_ids', [])}
    refs.update(hold['event_ref'] for hold in action_repetition_waits(instance, runtime, target.get('action', {})))
    refs.update(ref for ref in (target.get('result_ref'),
        runtime.get('checkpoints', {}).get(target['id'], {}).get('artifact_ref')) if ref)
    from .activities import successor_state
    successor=successor_state(runtime,target['id'])
    for identifier in successor['execution_ids'] if successor else []:
        refs.add(identifier)
        result=runtime['executions'][identifier].get('result_ref')
        if result:refs.add(result)
    return sorted(refs)


def require_basis_refs(disposition, allowed):
    """Reject source paths or other visible records that are not disposition evidence."""
    invalid = sorted(set(disposition['basis_refs']) - set(allowed))
    if invalid:
        raise ValueError('operational disposition cites evidence outside its current input; '
                         'invalid_basis_refs=' + repr(invalid) + '; admissible_basis_refs=' + repr(sorted(allowed)))




def worker_feedback(disposition: dict[str, Any]) -> dict[str, Any]:
    """Expose only information a worker needs; diagnostics remain with ENGINE."""
    checked = validate_disposition(disposition)
    return {key: checked[key] for key in ("kind", "reason", "next_owner")}


def reconcile_recovery(runtime: dict, record: dict) -> bool:
    """Settle an obsolete recovery proposal without duplicating its successor."""
    if record.get('status') == 'superseded':
        return True
    if record['disposition']['kind'] not in {'retry', 'resume'}:
        return False
    # A successfully applied retry already owns the successor it created.
    if record.get('result', {}).get('continuation_action_id'):
        return False
    from .activities import successor_state
    successor = successor_state(runtime, record['target_execution_id'])
    if successor is None:
        return False
    record['status'] = 'superseded'
    record.setdefault('result', {})['successor'] = successor
    target = runtime['executions'][record['target_execution_id']]
    if target.get('pending_operational_disposition') == record['id']:
        target.pop('pending_operational_disposition')
    return True
