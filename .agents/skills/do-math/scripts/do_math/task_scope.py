"""Narrow, auditable withdrawal of unfinished AI-prepared tasks."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from .planning import contract_hash


_WITHDRAWABLE_STATES = {"planned", "waiting", "needs_revision", "ready"}
def _withdrawal(disposition: dict) -> tuple[str, str]:
    if not isinstance(disposition, dict) or set(disposition) != {"task_id", "disposition", "reason"}:
        raise ValueError("task disposition must contain only task_id, disposition, and reason")
    task_id, kind, reason = disposition["task_id"], disposition["disposition"], disposition["reason"]
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task disposition needs a task ID")
    if kind != "withdraw":
        raise ValueError("AI task disposition supports only withdraw")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("task withdrawal needs a reason")
    return task_id, reason


def _task_execution(execution: dict, task_id: str) -> bool:
    return isinstance(execution, dict) and execution.get("action", {}).get("target") == task_id


def _validate(task: dict, snapshot_task: dict, runtime: dict, task_id: str) -> None:
    if not isinstance(snapshot_task, dict) or contract_hash(task) != contract_hash(snapshot_task):
        raise ValueError("task contract changed since the execution input snapshot: " + task_id)
    if task.get("status") not in _WITHDRAWABLE_STATES:
        raise ValueError("task is not an unfinished, unperformed task: " + task_id)
    if task.get("academic_requirement_id"):
        raise ValueError("academic requirement task cannot be withdrawn autonomously: " + task_id)
    producer_id = task.get("producer_execution")
    producer = runtime.get("executions", {}).get(producer_id)
    if not isinstance(producer_id, str) or not isinstance(producer, dict) or producer.get("role") != "research_preparation":
        raise ValueError("task is not attributable to a research preparation execution: " + task_id)
    for execution in runtime.get("executions", {}).values():
        if not _task_execution(execution, task_id):
            continue
        if execution.get("status") != "ended":
            raise ValueError("task has a live execution: " + task_id)


def apply_task_dispositions(instance: dict, runtime: dict, dispositions: list[dict], *,
                            execution_id: str, input_tasks: dict) -> tuple[dict, dict]:
    """Apply withdrawal requests after snapshot and provenance validation.

    The caller owns role authorization.  This function deliberately cannot alter
    goals, policies, grants, academic requirements, or user task-scope records.
    """
    if not isinstance(execution_id, str) or not execution_id:
        raise ValueError("task dispositions need an execution ID")
    if not isinstance(dispositions, list) or not isinstance(input_tasks, dict):
        raise ValueError("task dispositions and input tasks must be collections")
    requested = [_withdrawal(item) for item in dispositions]
    if len({task_id for task_id, _ in requested}) != len(requested):
        raise ValueError("a task may be withdrawn only once per execution")

    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    tasks = new_runtime.get("tasks", {})
    for task_id, _ in requested:
        task = tasks.get(task_id)
        if not isinstance(task, dict):
            raise ValueError("unknown task: " + task_id)
        _validate(task, input_tasks.get(task_id), new_runtime, task_id)

    for task_id, reason in requested:
        task = tasks[task_id]
        removed_queue = [deepcopy(action) for action in new_runtime.get("queue", [])
                         if isinstance(action, dict) and action.get("target") == task_id]
        new_runtime["queue"] = [action for action in new_runtime.get("queue", [])
                                if not isinstance(action, dict) or action.get("target") != task_id]
        waiting_actions = new_runtime.get("waiting_actions", {})
        removed_waiting = []
        for action_id, entry in list(waiting_actions.items()):
            action = entry.get("action", {}) if isinstance(entry, dict) else {}
            if isinstance(action, dict) and action.get("target") == task_id:
                removed_waiting.append({"id": action_id, "entry": deepcopy(entry)})
                waiting_actions.pop(action_id)
        previous_hash = contract_hash(task)
        task["scope_disposition"] = {
            "kind": "withdraw", "actor_execution": execution_id, "reason": reason,
            "previous_revision": task.get("revision"), "previous_contract_sha256": previous_hash,
            "at": datetime.now(timezone.utc).isoformat(), "cancelled_queue_actions": removed_queue,
            "cancelled_waiting_actions": removed_waiting,
        }
        task["status"] = "closed"
        new_runtime.get("task_readiness", {}).pop(task_id, None)
    return new_instance, new_runtime
