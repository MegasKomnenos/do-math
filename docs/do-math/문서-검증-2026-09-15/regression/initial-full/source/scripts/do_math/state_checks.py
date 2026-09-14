"""Pure persisted-state invariants for feature-2 do-math records.

The checks establish record binding and currentness only.  They do not decide
whether a theorem, explanation, or academic assessment is substantively true.
Feature-1 snapshots keep their original permissive wire shape.  Unknown later
feature versions are rejected, matching the executor's explicit migration gate.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from .academic import academic_status, solution_basis


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TERMINAL_OPERATION = {"confirmed", "failed", "unknown", "cancelled"}
_OPERATION_STATUS = {"prepared", "running", *_TERMINAL_OPERATION}
_SUSPENSION_KINDS = {"environment", "dependency", "semantic"}


def _is_feature2(instance: dict, runtime: dict) -> bool:
    return instance.get("feature_version", runtime.get("feature_version", 1)) == 2


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256.fullmatch(value))


def _error(errors: list[str], subject: str, detail: str) -> None:
    errors.append(f"{subject}: {detail}")


def _source_errors(instance: dict, errors: list[str]) -> None:
    seen = {"id": set(), "name": set(), "path": set()}
    for index, source in enumerate(instance.get("sources", [])):
        label = f"source[{index}]"
        if not isinstance(source, dict):
            _error(errors, label, "descriptor is not an object")
            continue
        for key in ("name", "path"):
            value = source.get(key)
            if not isinstance(value, str) or not value:
                _error(errors, label, f"missing {key}")
            elif value in seen[key]:
                _error(errors, label, f"duplicate {key}")
            else:
                seen[key].add(value)
        if "id" in source:
            value = source["id"]
            if not isinstance(value, str) or not value:
                _error(errors, label, "invalid id")
            elif value in seen["id"]:
                _error(errors, label, "duplicate id")
            else:
                seen["id"].add(value)
        if not _sha(source.get("sha256")):
            _error(errors, label, "invalid sha256")
        if "bytes" in source and (isinstance(source["bytes"], bool) or not isinstance(source["bytes"], int) or source["bytes"] < 0):
            _error(errors, label, "invalid byte count")


def _knowledge_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    environments = instance.get("trust_environments", {})
    active_environment = instance.get("active_trust_environment")
    executions = runtime.get("executions", {})
    cycles = runtime.get("review_cycles", {})
    for kid, record in instance.get("knowledge", {}).items():
        if not isinstance(record, dict):
            _error(errors, str(kid), "knowledge record is not an object")
            continue
        suspensions = record.get("use_suspensions")
        if feature2 and suspensions is not None:
            if not isinstance(suspensions, list):
                _error(errors, str(kid), "typed use_suspensions is not a list")
            else:
                for cause in suspensions:
                    if not isinstance(cause, dict) or cause.get("kind") not in _SUSPENSION_KINDS or not isinstance(cause.get("reason"), str) or not cause["reason"].strip():
                        _error(errors, str(kid), "invalid typed use suspension")
                        break
                if bool(record.get("use_suspended")) != bool(suspensions):
                    _error(errors, str(kid), "use_suspended disagrees with typed suspensions")
        if record.get("status") != "verified" or record.get("use_suspended"):
            continue
        formal = record.get("formal") if isinstance(record.get("formal"), dict) else {}
        if formal.get("status") != "verified":
            _error(errors, str(kid), "current K lacks verified formal result")
        source = record.get("lean_code")
        if not isinstance(source, str) or formal.get("source_sha256") != hashlib.sha256((source if isinstance(source, str) else "").encode("utf-8")).hexdigest():
            _error(errors, str(kid), "current K formal source is stale")
        if feature2:
            environment_id = formal.get("trust_environment_id")
            environment = environments.get(environment_id) if isinstance(environments, dict) else None
            if not isinstance(environment_id, str) or environment_id != active_environment or not isinstance(environment, dict) or environment.get("status") != "active" or formal.get("trust_environment_status") != "active":
                _error(errors, str(kid), "current K formal environment is not active")
            assessment = record.get("identity_assessment") if isinstance(record.get("identity_assessment"), dict) else {}
            cycle_id = record.get("review_cycle_id")
            cycle = cycles.get(cycle_id) if isinstance(cycles, dict) else None
            if not isinstance(cycle_id, str) or not isinstance(cycle, dict) or cycle.get("knowledge_id") != kid or cycle.get("status") != "completed" or cycle.get("decision") != "match" or not assessment.get("effective"):
                _error(errors, str(kid), "current K lacks an effective final identity cycle")
                continue
            if assessment.get("cycle_id") != cycle_id or assessment.get("proposal_digest") != cycle.get("proposal_digest") or assessment.get("decision") != "match":
                _error(errors, str(kid), "identity assessment is not bound to final cycle")
            execution_ids = assessment.get("execution_ids")
            if not isinstance(execution_ids, list) or not execution_ids or len(execution_ids) != len(set(execution_ids)):
                _error(errors, str(kid), "identity assessment has invalid final execution IDs")
            else:
                for execution_id in execution_ids:
                    execution = executions.get(execution_id)
                    action = execution.get("action", {}) if isinstance(execution, dict) else {}
                    if not isinstance(execution, dict) or execution.get("role") != "identity_review" or execution.get("outcome") != "output_accepted" or action.get("target") != kid or action.get("review_cycle_id") != cycle_id:
                        _error(errors, str(kid), "identity assessment references an unaccepted review execution")
                        break


def _task_errors(runtime: dict, errors: list[str], feature2: bool) -> None:
    executions = runtime.get("executions", {})
    for task_id, task in runtime.get("tasks", {}).items():
        if not isinstance(task, dict) or task.get("status") != "completed":
            continue
        assessment = task.get("assessment") if isinstance(task.get("assessment"), dict) else {}
        criteria = task.get("completion_criteria")
        checks = assessment.get("criteria_results")
        if assessment.get("current") is False and not (
                isinstance(assessment.get("invalidated_reason"), str) and assessment["invalidated_reason"].strip()):
            _error(errors, str(task_id), "suspended completed task assessment lacks an invalidation reason")
        if assessment.get("decision") != "completed" or not isinstance(criteria, list) or not isinstance(checks, list):
            _error(errors, str(task_id), "completed task lacks criteria assessment")
        else:
            names = [entry.get("criterion") for entry in checks if isinstance(entry, dict)]
            if len(names) != len(checks) or sorted(names) != sorted(criteria) or any(not entry.get("satisfied") or not isinstance(entry.get("evidence"), str) or not entry["evidence"].strip() for entry in checks):
                _error(errors, str(task_id), "completed task criteria evidence is incomplete")
        for execution in executions.values():
            action = execution.get("action", {}) if isinstance(execution, dict) else {}
            if isinstance(execution, dict) and execution.get("status") in {"starting", "running"} and execution.get("role") in {"research_work", "supplemental_research"} and action.get("target") == task_id:
                _error(errors, str(task_id), "completed task has a live worker")
                break


def _external_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    if not feature2:
        return
    executions = runtime.get("executions", {})
    for operation_id, operation in runtime.get("external_operations", {}).items():
        if not isinstance(operation, dict) or operation.get("id") != operation_id:
            _error(errors, f"operation[{operation_id}]", "ledger key and id differ")
            continue
        status = operation.get("status")
        if status not in _OPERATION_STATUS:
            _error(errors, f"operation[{operation_id}]", "unknown status")
        execution_id = operation.get("execution_id")
        execution = executions.get(execution_id)
        # Preparation allocates an EX identifier before any execution record is
        # persisted.  It is an auditable queued operation, not a missing record.
        if status == "prepared" and execution is None:
            continue
        if not isinstance(execution_id, str) or not isinstance(execution, dict) or execution.get("role") != "external_action" or execution.get("operation_id") != operation_id:
            _error(errors, f"operation[{operation_id}]", "missing EX execution mapping")
            continue
        for key in ("grant_id", "request_sha256", "source_ref"):
            if execution.get(key) != operation.get(key):
                _error(errors, f"operation[{operation_id}]", f"EX {key} differs from ledger")
        if status in _TERMINAL_OPERATION:
            status_matches = execution.get("status") == "ended" and execution.get("outcome") == status
        elif status == "running":
            status_matches = execution.get("status") in {"starting", "running"} and execution.get("outcome") in {None, "prepared", "running"}
        else:  # Some persisted snapshots capture the prepared transmission barrier.
            status_matches = execution.get("status") in {"prepared", "starting", "running"} and execution.get("outcome") in {None, "prepared", "running"}
        if not status_matches:
            _error(errors, f"operation[{operation_id}]", "EX status differs from ledger")
        http_status = operation.get("http_status")
        has_http_status = isinstance(http_status, int) and not isinstance(http_status, bool)
        expected_success = 200 <= http_status < 300 if has_http_status else None
        if has_http_status and (operation.get("succeeded") != expected_success or execution.get("succeeded") != expected_success):
            _error(errors, f"operation[{operation_id}]", "HTTP success flag differs from HTTP status")
        # User/adapter reconciliation can confirm an unknown operation without a
        # response body or HTTP status.  Its recorded reconciliation is the basis.
        if not has_http_status:
            reconciliation = operation.get("reconciliation", {})
            success = reconciliation.get("succeeded") if status == "confirmed" and reconciliation.get("source") in {"user", "adapter"} and reconciliation.get("evidence") else None
            if operation.get("succeeded") != success or execution.get("succeeded") != success:
                _error(errors, f"operation[{operation_id}]", "success flag lacks explicit reconciliation evidence")


def _supplement_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    if not feature2:
        return
    cycles = runtime.get("review_cycles", {})
    for action in runtime.get("queue", []):
        if not isinstance(action, dict) or action.get("role") != "supplemental_research" or not action.get("review_cycle_id"):
            continue
        cycle = cycles.get(action["review_cycle_id"])
        request = cycle.get("research", {}).get(action.get("research_request_id")) if isinstance(cycle, dict) else None
        if not isinstance(cycle, dict) or cycle.get("status") != "working" or cycle.get("knowledge_id") != action.get("target") or not isinstance(request, dict) or request.get("status") != "pending" or request.get("action", {}).get("slot") != action.get("requesting_slot"):
            _error(errors, "supplemental review", "queued investigation is not linked to a pending review request")


def _solution_basis(instance: dict) -> dict | None:
    group = instance.get("goal_assessment_basis")
    judgments = [item for item in instance.get("goal_judgments", []) if item.get("basis") == group]
    if not isinstance(group, str) or not judgments or any(not item.get("current", True) for item in judgments):
        return None
    ids = sorted({reference for item in judgments for reference in item.get("dependencies", []) if reference in instance.get("knowledge", {})})
    records = [instance["knowledge"][record_id] for record_id in ids]
    records.extend({"id": item.get("execution_id"), **item} for item in judgments if isinstance(item.get("execution_id"), str))
    try:
        return solution_basis(f"{instance.get('goal_revision', 1)}:{group}", records)
    except (KeyError, TypeError, ValueError):
        return None


def _goal_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    if runtime.get("status") != "completed":
        return
    group_id = instance.get("goal_assessment_basis")
    group = [item for item in instance.get("goal_judgments", []) if item.get("basis") == group_id]
    if not isinstance(group_id, str) or not group:
        _error(errors, "goal", "completed runtime lacks current audit group")
        return
    required = group[0].get("required", instance.get("config", {}).get("goal_auditors"))
    slots = [item.get("slot") for item in group]
    if not isinstance(required, int) or isinstance(required, bool) or len(group) != required or len(slots) != len(set(slots)) or any(item.get("decision") != "satisfied" or not item.get("scope_complete") or not item.get("current", True) for item in group):
        _error(errors, "goal", "completed runtime lacks complete current agreeing audits")
    if feature2 and instance.get("academic_requirements", {}).get("items"):
        basis = _solution_basis(instance)
        if academic_status(instance, runtime, basis).get("status") != "completed":
            _error(errors, "goal", "completed runtime has incomplete academic requirements")


def state_errors(instance: dict, runtime: dict) -> list[str]:
    """Return persisted cross-record consistency errors without mutating inputs."""
    if not isinstance(instance, dict) or not isinstance(runtime, dict):
        return ["state: instance and runtime must be objects"]
    errors: list[str] = []
    versions = (instance.get("feature_version", 1), runtime.get("feature_version", 1))
    if any(value not in {1, 2} for value in versions):
        errors.append("state: unsupported feature version")
    feature2 = _is_feature2(instance, runtime)
    _source_errors(instance, errors)
    _knowledge_errors(instance, runtime, errors, feature2)
    _task_errors(runtime, errors, feature2)
    _external_errors(instance, runtime, errors, feature2)
    _supplement_errors(instance, runtime, errors, feature2)
    _goal_errors(instance, runtime, errors, feature2)
    return errors
