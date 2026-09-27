"""Authoritative activity facts for feature-5 execution orchestration.

An activity is the durable work unit.  An execution is one attempt owned by
exactly one activity; this module never derives that relation from a target,
task, or legacy lineage label.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .file_io import require_text


ACTIVITY_STATUSES = frozenset({"ready", "working", "waiting", "finished"})


def _references(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return deepcopy(value)


def _activities(runtime: dict) -> dict:
    activities = runtime.setdefault("activities", {})
    if not isinstance(activities, dict):
        raise ValueError("runtime.activities must be a dictionary")
    return activities


def _executions(runtime: dict) -> dict:
    executions = runtime.setdefault("executions", {})
    if not isinstance(executions, dict):
        raise ValueError("runtime.executions must be a dictionary")
    return executions


def open_activity(runtime: dict, *, activity_id: str, activity_kind: str, owner_ref: Any,
                  input_refs: list[Any], opened_at: str, stage: str | None = None,
                  execution_limit: int | None = None) -> dict:
    """Create an activity, or return its exact idempotent prior declaration."""
    require_text(activity_id, "activity_id")
    require_text(activity_kind, "activity_kind")
    require_text(opened_at, "opened_at")
    if owner_ref is None:
        raise ValueError("owner_ref is required")
    if stage is not None:
        require_text(stage, "stage")
    if execution_limit is not None and (isinstance(execution_limit, bool) or not isinstance(execution_limit, int) or execution_limit < 1):
        raise ValueError("execution_limit must be a positive integer or null")
    record = {
        "id": activity_id,
        "activity_kind": activity_kind,
        "owner_ref": deepcopy(owner_ref),
        "opened_at": opened_at,
        "input_refs": _references(input_refs, "input_refs"),
        "status": "ready",
        "stage": stage,
        "execution_limit": execution_limit,
        "assigned_execution_ids": [],
        "result_refs": [],
        "unresolved": [],
        "followups": [],
    }
    activities = _activities(runtime)
    existing = activities.get(activity_id)
    if existing is not None:
        declaration = ("id", "activity_kind", "owner_ref", "opened_at", "input_refs", "stage", "execution_limit")
        if {key: existing.get(key) for key in declaration} != {key: record[key] for key in declaration}:
            raise ValueError(f"activity {activity_id} was already opened with different facts")
        return existing
    activities[activity_id] = record
    return record


def assign_execution(runtime: dict, activity_id: str, execution: dict, *, stage: str | None = None) -> dict:
    """Attach one execution attempt to a non-finished activity atomically."""
    activity = _activities(runtime).get(activity_id)
    if activity is None:
        raise ValueError(f"unknown activity {activity_id}")
    if activity["status"] == "finished":
        raise ValueError("a finished activity cannot receive another execution")
    if activity["status"] == "waiting":
        raise ValueError("resolve the recorded activity wait before assigning an execution")
    execution_id = require_text(execution.get("id"), "execution.id")
    if execution.get("owner_activity_id") != activity_id:
        raise ValueError("execution owner_activity_id differs from activity")
    if stage is not None and activity.get("stage") not in {None, stage}:
        raise ValueError("execution stage differs from activity stage")
    assigned = activity["assigned_execution_ids"]
    if execution_id not in assigned:
        limit = activity.get("execution_limit")
        if limit is not None and len(assigned) >= limit:
            raise ValueError("activity execution limit is exhausted")
        assigned.append(execution_id)
    if stage is not None:
        activity["stage"] = stage
    _executions(runtime)[execution_id] = execution
    if activity["status"] == "ready":
        activity["status"] = "working"
    activity.pop("waiting", None)
    return activity


def bind_action(runtime: dict, action: dict, activity_id: str) -> dict:
    """Bind the working copy and its same-ID queued request before preparation."""
    activity = _activities(runtime).get(activity_id)
    if activity is None or activity["status"] == "finished":
        raise ValueError("action requires an existing unfinished activity")
    action_id = require_text(action.get("id"), "action.id")
    queued = [row for row in runtime.get("queue", []) if row.get("id") == action_id]
    if len(queued) > 1:
        raise ValueError("action has duplicate queued requests")
    for row in [action, *queued]:
        if row.get("owner_activity_id", activity_id) != activity_id:
            raise ValueError("action is already bound to another activity")
    action["owner_activity_id"] = activity_id
    for row in queued:
        row["owner_activity_id"] = activity_id
    return activity


def successor_state(runtime: dict, execution_id: str) -> dict | None:
    """Read explicit continuation edges; unrelated success never resolves a failure."""
    executions = runtime.get('executions', {})
    target = executions[execution_id]
    owner = target.get('owner_activity_id')
    descendants, pending = set(), {execution_id}
    while pending:
        parent = pending.pop()
        for eid, execution in executions.items():
            previous = execution.get('continuation_of') or execution.get('action', {}).get('continuation_of')
            if (eid != execution_id and eid not in descendants and previous == parent
                    and execution.get('owner_activity_id') == owner):
                descendants.add(eid)
                pending.add(eid)
    queued = [row['id'] for row in runtime.get('queue', [])
              if row.get('continuation_of') in {execution_id, *descendants}
              and row.get('owner_activity_id', owner) == owner]
    if not descendants and not queued:
        return None
    live = sorted(eid for eid in descendants if executions[eid]['status'] != 'ended')
    return {'state': 'in_progress' if live or queued else 'continued',
            'execution_ids': sorted(descendants), 'live_execution_ids': live,
            'action_ids': sorted(set(queued))}


def continue_activity(runtime: dict, execution_id: str, *, at: str, reason: str,
                      condition: Any = None, next_owner: str = "engine") -> dict:
    """Preserve the exact ended attempt's obligation and request its successor.

    A pause condition is an activity wait, even though the pending action stays
    queued. The central lifecycle gate must resolve it before dispatch. An old
    checkpoint remains keyed by continuation_of; it is not evidence that a new
    conversation has inherited the old context.
    """
    require_text(at, "at")
    require_text(reason, "reason")
    require_text(next_owner, "next_owner")
    execution = _executions(runtime)[execution_id]
    if execution["status"] != "ended":
        raise ValueError("only an ended execution can request continuation")
    activity = _activities(runtime)[execution["owner_activity_id"]]
    action = deepcopy(execution.get("action", {}))
    action_id = require_text(action.get("id"), "execution.action.id")
    live = [eid for eid in activity["assigned_execution_ids"] if _executions(runtime)[eid]["status"] != "ended"]
    if live:
        raise ValueError("continuation requires the activity's current attempts to end")
    bind_action(runtime, action, activity["id"])
    queued = next((row for row in runtime.get("queue", []) if row.get("id") == action_id), None)
    if queued is not None:
        # Keep current task/authority inputs; only the execution relation changes.
        action = deepcopy(queued)
    action.update(owner_activity_id=activity["id"], continuation_of=execution_id)
    action.setdefault("context_origin", [])
    if queued is None:
        runtime.setdefault("queue", []).append(action)
    else:
        queued.update(action)
        action = queued
    obligation = {"action_id": action_id, "execution_id": execution_id, "reason": reason}
    activity["unresolved"] = [row for row in activity["unresolved"]
                              if not isinstance(row, dict) or row.get("action_id") != action_id] + [obligation]
    followup = {**obligation, "next_owner": next_owner}
    activity["followups"] = [row for row in activity["followups"]
                             if not isinstance(row, dict) or row.get("action_id") != action_id] + [followup]
    if condition is not None:
        wait_for(runtime, activity["id"], reason=reason, condition=condition, next_owner=next_owner, at=at)
    elif activity["status"] != "waiting":
        activity["status"] = "ready"
    return action


def wait_for(runtime: dict, activity_id: str, *, reason: str, condition: Any,
             next_owner: Any, at: str) -> dict:
    """Record a durable wait after every currently assigned attempt ended."""
    activity = _activities(runtime).get(activity_id)
    if activity is None:
        raise ValueError(f"unknown activity {activity_id}")
    if activity["status"] == "finished":
        raise ValueError("a finished activity cannot wait")
    require_text(reason, "reason")
    require_text(at, "at")
    if condition is None or next_owner is None:
        raise ValueError("condition and next_owner are required")
    executions = _executions(runtime)
    live = [eid for eid in activity["assigned_execution_ids"]
            if executions.get(eid, {}).get("status") != "ended"]
    if live:
        raise ValueError("an activity may wait only after its assigned executions ended")
    activity["status"] = "waiting"
    activity["waiting"] = {"reason": reason, "condition": deepcopy(condition),
                           "next_owner": deepcopy(next_owner), "at": at}
    return activity


def resume_activity(runtime: dict, activity_id: str, *, condition: Any, at: str) -> dict:
    """Move a waiting activity back to ready only for its recorded condition."""
    activity = _activities(runtime).get(activity_id)
    if activity is None:
        raise ValueError(f"unknown activity {activity_id}")
    if activity["status"] != "waiting":
        raise ValueError("only a waiting activity can resume")
    if activity["waiting"].get("condition") != condition:
        raise ValueError("the resolved condition differs from the recorded wait")
    require_text(at, "at")
    activity["status"] = "ready"
    activity["resumed_at"] = at
    activity.pop("waiting", None)
    return activity


def finish_activity(runtime: dict, activity_id: str, *, result_refs: list[Any], unresolved: list[Any],
                    followups: list[Any], at: str) -> dict:
    """Seal a work unit without equating it to task or mathematical completion."""
    activity = _activities(runtime).get(activity_id)
    if activity is None:
        raise ValueError(f"unknown activity {activity_id}")
    require_text(at, "at")
    executions = _executions(runtime)
    live = [eid for eid in activity["assigned_execution_ids"]
            if executions.get(eid, {}).get("status") != "ended"]
    if live:
        raise ValueError("an activity with a live execution cannot finish")
    sealed = {"result_refs": _references(result_refs, "result_refs"),
              "unresolved": _references(unresolved, "unresolved"),
              "followups": _references(followups, "followups"), "finished_at": at}
    if activity["status"] == "finished":
        if {key: activity.get(key) for key in sealed} != sealed:
            raise ValueError("a finished activity is immutable")
        return activity
    activity.update(sealed, status="finished")
    activity.pop("waiting", None)
    return activity


def validate_activities(runtime: dict) -> list[str]:
    """Return structural errors; callers choose the persistent validation policy."""
    errors: list[str] = []
    activities = runtime.get("activities", {})
    executions = runtime.get("executions", {})
    if not isinstance(activities, dict) or not isinstance(executions, dict):
        return ["activities and executions must be dictionaries"]
    assigned_by_execution: dict[str, str] = {}
    for activity_id, activity in activities.items():
        if not isinstance(activity, dict) or activity.get("id") != activity_id:
            errors.append(f"{activity_id}: invalid activity record")
            continue
        for execution_id in activity["assigned_execution_ids"]:
            execution = executions.get(execution_id)
            if execution is None or execution.get("owner_activity_id") != activity_id:
                errors.append(f"{activity_id}: execution binding is invalid for {execution_id}")
            elif execution_id in assigned_by_execution:
                errors.append(f"{execution_id}: assigned to multiple activities")
            else:
                assigned_by_execution[execution_id] = activity_id
        if activity.get("status") == "waiting" and not isinstance(activity.get("waiting"), dict):
            errors.append(f"{activity_id}: waiting state lacks its condition")
        if activity.get("status") == "finished" and "finished_at" not in activity:
            errors.append(f"{activity_id}: finished state lacks finished_at")
    for execution_id, execution in executions.items():
        owner = execution.get("owner_activity_id") if isinstance(execution, dict) else None
        if owner not in activities or assigned_by_execution.get(execution_id) != owner:
            errors.append(f"{execution_id}: execution has no matching activity")
            continue
        predecessor = execution.get("continuation_of")
        if predecessor is not None:
            previous = executions.get(predecessor)
            if previous is None or previous.get("owner_activity_id") != owner or previous.get("status") != "ended":
                errors.append(f"{execution_id}: continuation is not an ended execution in the same activity")
    return errors
