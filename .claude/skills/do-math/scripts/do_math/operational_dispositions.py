"""Validation and disclosure boundaries for operational-review dispositions.

This module records a reviewer's proposed operational action.  It deliberately
does not mutate executions, activities, tasks, or permissions: ENGINE applies
an accepted proposal only after its own currentness and authority checks.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable
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


def validate_new_disposition(disposition):
    """New repairs change installation files; old input repairs remain readable."""
    checked = validate_disposition(disposition)
    if checked['kind'] == 'repair' and not checked['repair_target'].startswith('installation:'):
        raise ValueError('local input damage requires retry with replay_safety; repair is for installation: targets')
    return checked


def worker_feedback(disposition: dict[str, Any]) -> dict[str, Any]:
    """Expose only information a worker needs; diagnostics remain with ENGINE."""
    checked = validate_disposition(disposition)
    return {key: checked[key] for key in ("kind", "reason", "next_owner")}


def execute_repair(record: dict, *, target_execution: dict, current_basis_refs,
                   repair: Callable, verify: Callable, resume: Callable, publish: Callable) -> dict:
    """Execute an authorized repair, verify its exact effects, then request resume.

    ENGINE owns the callbacks: repair runs the admitted maintenance operation;
    verify reads its resulting artifacts; resume enqueues the continuation.
    publish must CAS this disposition record and its referenced evidence into
    the same authoritative runtime. Callback effect keys are stable per OD ID.
    No successful return from repair alone means that the disposition applied.

    In-flight states require reconciliation, not blind replay after a crash.
    Completed phases can be resumed without repeating their effects. An owner
    must reconcile an interrupted callback using its stable effect key before
    calling again with its recorded result.
    """
    value = deepcopy(record)
    disposition = validate_disposition(value["disposition"])
    if disposition["kind"] != "repair" or not disposition["meaning_preserving"]:
        raise ValueError("execute_repair requires an admitted meaning-preserving repair")
    if not isinstance(value.get("id"), str) or not value["id"]:
        raise ValueError("repair requires an authoritative disposition ID")
    if target_execution.get("id") != value.get("target_execution_id") or target_execution.get("status") != "ended":
        raise ValueError("repair requires its ended predecessor")

    def check_current():
        refs = current_basis_refs() if callable(current_basis_refs) else current_basis_refs
        if not disposition_is_current(disposition, refs):
            raise ValueError("repair disposition basis is no longer current")

    def save(status):
        from .repository import canonical_json
        value["status"] = status
        canonical_json(value)
        publish(deepcopy(value))

    def refs(result, field):
        items = result.get(field)
        if (not isinstance(items, list) or not items or any(not isinstance(x, str) or not x for x in items)
                or len(set(items)) != len(items)):
            raise ValueError("repair result needs distinct " + field)
        return items

    check_current()
    status = value.get("status", "pending")
    if status in {"repair_running", "repair_verifying", "repair_resuming"}:
        raise ValueError("interrupted repair phase requires effect reconciliation before retry")
    if status == "applied":
        if not all(value.get(key) for key in ("repair_effect", "repair_verification", "repair_resume")):
            raise ValueError("applied repair lacks execution, verification or resume evidence")
        return value
    if status not in {"pending", "awaiting_termination", "repair_required", "repair_verification_required", "repair_resume_required"}:
        raise ValueError("repair requires an explicit retry disposition after failure")
    plan = {"disposition_id": value["id"], "target_execution_id": value["target_execution_id"],
            "owner": disposition["next_owner"], "repair_target": disposition["repair_target"],
            "verification": disposition["verification"], "basis_refs": disposition["basis_refs"]}
    if status in {"pending", "awaiting_termination", "repair_required"}:
        save("repair_running")
        # If execution raises, the last published status explicitly requires
        # reconciliation. It does not silently re-run a possibly partial effect.
        effect = repair({**plan, "effect_key": value["id"] + ":repair"})
        if (not isinstance(effect, dict) or not isinstance(effect.get("execution_id"), str)
                or not effect["execution_id"] or effect.get("target") != plan["repair_target"]):
            raise ValueError("repair execution result does not identify the requested target")
        refs(effect, "effect_refs")
        value["repair_effect"] = deepcopy(effect)
        save("repair_verification_required")
    if value["status"] == "repair_verification_required":
        check_current()
        save("repair_verifying")
        verification = verify({**plan, "effect_key": value["id"] + ":verify"}, deepcopy(value["repair_effect"]))
        if (not isinstance(verification, dict) or not isinstance(verification.get("execution_id"), str)
                or not verification["execution_id"] or type(verification.get("passed")) is not bool
                or type(verification.get("meaning_preserved")) is not bool):
            raise ValueError("repair verification requires an execution and explicit verdicts")
        refs(verification, "evidence_refs")
        if set(refs(verification, "effect_refs")) != set(value["repair_effect"]["effect_refs"]):
            raise ValueError("repair verification did not inspect the exact repaired effects")
        value["repair_verification"] = deepcopy(verification)
        if not verification["passed"] or not verification["meaning_preserved"]:
            save("repair_verification_failed")
            return value
        save("repair_resume_required")
    check_current()
    save("repair_resuming")
    resumed = resume({**plan, "effect_key": value["id"] + ":resume"}, deepcopy(value["repair_verification"]))
    if (not isinstance(resumed, dict) or not isinstance(resumed.get("request_id"), str) or not resumed["request_id"]
            or resumed.get("continuation_of") != value["target_execution_id"]):
        raise ValueError("repair resume must identify a continuation of the repaired predecessor")
    value["repair_resume"] = deepcopy(resumed)
    save("applied")
    return value
