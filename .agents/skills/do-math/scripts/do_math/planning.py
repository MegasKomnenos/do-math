"""Pure task-readiness and event scheduling for the CLI research workflow."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

from .repository import canonical_json


def _hash(value: Any) -> str: return hashlib.sha256(canonical_json(value)).hexdigest()
CONTRACT_FIELDS = ("id", "revision", "title", "question", "scope", "excluded_scope", "expected_result",
                   "completion_criteria", "inputs", "reuse", "dependencies", "occurrence_condition",
                   "work_class", "profile_refs", "authority_refs", "expected_research_change",
                   "academic_requirement_id", "requirements_sha256", "solution_basis", "required_external_effects",
                   "initial_observation_rules", "model_assessment")

def contract_hash(task: dict) -> str:
    """Hash only fields whose revision approval is intended to cover."""
    return _hash({key: task[key] for key in CONTRACT_FIELDS if key in task})


def ready_task_ids(runtime: dict) -> list[str]:
    """The current selection population, shared by producer input and receiver."""
    return sorted(tid for tid, task in runtime.get("tasks", {}).items() if task.get("status") == "ready")


def validate_plan_submission(output: dict, tasks: dict, ready_ids: list[str]) -> None:
    """Validate the supplied planning population, before applying any decision."""
    import json
    supplied = output["selections"] + [row["task_id"] for row in output["deferred"]]
    eligible = set(ready_ids)
    if len(supplied) != len(set(supplied)) or set(supplied) != eligible:
        details = {"ready_task_ids": sorted(eligible), "missing": sorted(eligible - set(supplied)),
                   "unexpected": sorted(set(supplied) - eligible),
                   "duplicate": sorted({tid for tid in supplied if supplied.count(tid) > 1})}
        raise ValueError("plan must select or defer every ready task exactly once: " + json.dumps(details, ensure_ascii=False, sort_keys=True))
    assessments = output["task_assessments"]
    ids = [row["task_id"] for row in assessments]
    required = {tid for tid, task in tasks.items() if task.get("status") == "assessing"}
    if len(ids) != len(set(ids)) or not required <= set(ids):
        raise ValueError("plan must assess every returned task exactly once")
    for row in assessments:
        task = tasks.get(row["task_id"])
        if not task or task.get("status") not in {"assessing", "waiting"} or not task.get("results"):
            raise ValueError("assessment requires a task with returned work")
        checks = row["criteria_results"]
        if sorted(c["criterion"] for c in checks) != sorted(task["completion_criteria"]):
            raise ValueError("task assessment must cover the exact completion criteria")
        if row["decision"] == "completed" and not all(c["satisfied"] and c["evidence"].strip() for c in checks):
            raise ValueError("completed task requires evidence for every completion criterion")
        if row["decision"] == "closed" and task.get("scope_disposition", {}).get("kind") not in {"withdraw", "transfer", "superseded_requirements"}:
            raise ValueError("closing unfinished obligations requires an explicit scope transfer or withdrawal; use incomplete to return unfinished research")


def validate_condition(condition: dict) -> None:
    """Check the expression's grammar even when its referenced record is absent."""
    fields = {"always": set(), "all": {"args"}, "any": {"args"}, "not": {"arg"},
              "record_exists": {"record_id", "family"}, "record_lifecycle_is": {"record_id", "value"},
              "record_field_equals": {"record_id", "pointer", "value"},
              "relation_exists": {"subkind", "from_id", "to_id"}, "task_disposition_is": {"task_id", "value"}}
    if not isinstance(condition, dict) or condition.get("op") not in fields:
        raise ValueError("unsupported condition op")
    op = condition["op"]
    if set(condition) != {"op", *fields[op]}:
        raise ValueError("condition fields do not match " + op)
    if op in {"all", "any"}:
        if not isinstance(condition["args"], list) or not condition["args"]:
            raise ValueError(op + " requires nonempty args")
        for child in condition["args"]:
            validate_condition(child)
    elif op == "not":
        validate_condition(condition["arg"])
    else:
        for name in fields[op] - {"value"}:
            if not isinstance(condition[name], str) or not condition[name].strip():
                raise ValueError("condition " + name + " must be nonempty text")
        if op == "task_disposition_is" and condition["value"] not in {"completed", "closed"}:
            raise ValueError("task disposition must be completed or closed")
        if op == "record_field_equals" and (not condition["pointer"].startswith("/") or isinstance(condition["value"], (dict, list))):
            raise ValueError("record comparison needs a pointer and scalar value")


def _records(instance: dict, runtime: dict) -> dict[str, tuple[str, dict]]:
    found: dict[str, tuple[str, dict]] = {}
    for family, container in (("knowledge", instance.get("knowledge", {})), ("governance", instance.get("governance", {})),
                              ("grant", instance.get("grants", {})), ("task", runtime.get("tasks", {})),
                              ("activity", runtime.get("activities", {})), ("execution", runtime.get("executions", {})),
                              ("decision", instance.get("decisions", {})), ("external-operation", runtime.get("external_operations", {})),
                              ("source", instance.get("sources", [])), ("trust-environment", instance.get("trust_environments", {})),
                              ("review-cycle", runtime.get("review_cycles", {}))):
        values = container.values() if isinstance(container, dict) else container if isinstance(container, list) else []
        for record in values:
            if isinstance(record, dict) and isinstance(record.get("id"), str): found[record["id"]] = (family, record)
    if instance.get("id"): found[instance["id"]] = ("instance", instance)
    return found


def _basis(record: dict) -> dict: return {"id": record["id"], "sha256": _hash(record), "status": record.get("status", record.get("lifecycle"))}


def _pointer(record: dict, family: str, pointer: str) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/"): raise ValueError("JSON Pointer must start with /")
    allowed={"knowledge":{"/status","/lifecycle","/kind","/value","/use_suspended"},"task":{"/status","/revision"},"activity":{"/status","/role"},"execution":{"/status","/role","/outcome","/http_status","/succeeded"},"governance":{"/status","/lifecycle"},"grant":{"/status","/lifecycle"},"decision":{"/kind"},"external-operation":{"/status","/http_status","/succeeded"}}
    allowed.update({"source": {"/status", "/revision", "/sha256"}, "trust-environment": {"/status"},
                    "review-cycle": {"/status", "/decision", "/phase"}, "instance": {"/goal_status", "/goal_revision", "/policy_revision"}})
    if pointer not in allowed.get(family,set()): raise ValueError("pointer is not an exposed machine field")
    value: Any = record
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value: raise KeyError(pointer)
        value = value[token]
    if isinstance(value, (dict, list)): raise ValueError("pointer must name a scalar machine field")
    if isinstance(value,bool): return value
    if not isinstance(value,(str,int,float)) or isinstance(value,float) and not value.is_integer(): raise ValueError("pointer must name a scalar machine field")
    return value


def evaluate_condition(condition: dict, instance: dict, runtime: dict) -> dict:
    """Evaluate a closed readiness AST without treating malformed evidence as true."""
    records, basis, errors = _records(instance, runtime), [], []
    try:
        validate_condition(condition)
    except (ValueError, TypeError) as error:
        return {"state": "evaluation_error", "basis": [], "errors": [str(error)]}
    def visit(node: dict) -> str:
        try:
            if not isinstance(node, dict) or not isinstance(node.get("op"), str): raise ValueError("condition op is required")
            op = node["op"]
            if op not in {"always","all","any","not","record_exists","record_lifecycle_is","record_field_equals","relation_exists","task_disposition_is"}: raise ValueError(f"unsupported condition op: {op}")
            if op == "always": return "ready"
            if op in {"all", "any"}:
                args = node.get("args")
                if not isinstance(args, list) or not args: raise ValueError(f"{op} requires nonempty args")
                results = [visit(x) for x in args]
                if "evaluation_error" in results: return "evaluation_error"
                return "ready" if (all(x == "ready" for x in results) if op == "all" else any(x == "ready" for x in results)) else "not_ready"
            if op == "not":
                result = visit(node.get("arg"))
                return "evaluation_error" if result == "evaluation_error" else "not_ready" if result == "ready" else "ready"
            if op == "relation_exists":
                from .knowledge_io import _RELATION_FIELDS, validate_relation
                candidates = [r for r in instance.get("relations", []) if isinstance(r, dict) and r.get("kind") == node.get("subkind") and r.get("source") == node.get("from_id") and r.get("target") == node.get("to_id")]
                matches = []
                for relation in candidates:
                    basis.append(_basis(relation))
                    if relation.get("status", "active") in {"suspended", "withdrawn", "invalid"} or relation.get("use_status", "active") in {"suspended", "withdrawn"}:
                        continue
                    value = {key: value for key, value in relation.items() if key in _RELATION_FIELDS}
                    result = validate_relation(instance, value)
                    unavailable = ("formal_result_not_usable:", "assessment_not_effective:")
                    structural = [reason for reason in result["reasons"] if not reason.startswith(unavailable)]
                    if structural:
                        raise ValueError("invalid relation: " + ", ".join(structural))
                    for record_id in dict.fromkeys([relation.get("source"), relation.get("target"), *relation.get("formal_result_refs", [])]):
                        record = records.get(record_id)
                        if record is not None:
                            basis.append(_basis(record[1]))
                    if result["valid"]:
                        matches.append(relation)
                if matches:
                    return "ready"
                basis.append({"absencequery": {"op": op, "subkind": node.get("subkind"), "from_id": node.get("from_id"), "to_id": node.get("to_id")}})
                return "not_ready"
            if op == "task_disposition_is":
                record = records.get(node.get("task_id"));
                if record is None: basis.append({"absencequery": {"op": op, "task_id": node.get("task_id")}}); return "not_ready"
                if record[0] != "task": raise ValueError("task disposition requires a task")
                basis.append(_basis(record[1])); return "ready" if record[1].get("status") == node.get("value") else "not_ready"
            record = records.get(node.get("record_id"))
            if op == "record_exists":
                if record is None: basis.append({"absencequery": {"op": op, "record_id": node.get("record_id"), "family": node.get("family")}}); return "not_ready"
                basis.append(_basis(record[1])); return "ready" if record[0] == node.get("family") else "not_ready"
            if record is None: basis.append({"absencequery": {"op": op, "record_id": node.get("record_id")}}); return "not_ready"
            basis.append(_basis(record[1]))
            if op == "record_lifecycle_is": return "ready" if record[1].get("lifecycle", record[1].get("status")) == node.get("value") else "not_ready"
            if op == "record_field_equals":
                actual, expected=_pointer(record[1], record[0], node.get("pointer")),node.get("value")
                return "ready" if type(actual) is type(expected) and actual==expected else "not_ready"
            raise ValueError(f"unsupported condition op: {op}")
        except (KeyError, TypeError, ValueError) as error:
            errors.append(str(error)); return "evaluation_error"
    state = visit(condition)
    return {"state": state, "basis": basis, "errors": errors}


def task_ready(task: dict, instance: dict, runtime: dict) -> dict:
    if instance.get("goal_status") in {"mathematically_solved", "research_goal_satisfied"} and not task.get("academic_requirement_id"):
        return {"state": "not_ready", "basis": [], "errors": ["research production stopped after goal satisfaction"]}
    if task.get("status") not in {"planned", "waiting", "needs_revision", "ready"}:
        return {"state": "not_ready", "basis": [], "errors": ["task state is not schedulable"]}
    requested = task.get("revision_requested")
    if isinstance(requested, dict) and requested.get("revision") == task.get("revision"):
        return {"state": "not_ready", "basis": [], "errors": ["a contract revision was requested by " + str(requested.get("source")) + "; awaiting a new revision"]}
    revision = task.get("revision")
    reviews = task.get("reviews", [])
    approved = [r for r in reviews if r.get("revision") == revision and r.get("decision") == "approved" and r.get("inputs_current", True)]
    if task.get("feature_version",0)>=2:
        approved=[r for r in approved if r.get("contract_sha256")==contract_hash(task) and r.get("goal_revision")==instance.get("goal_revision") and r.get("policy_revision")==instance.get("policy_revision")]
    if not approved: return {"state": "not_ready", "basis": [], "errors": ["current revision lacks approved contract review"]}
    records = _records(instance, runtime); missing = []
    available=set(instance.get("available_input_refs",[]))
    for source in [*task.get("inputs",[]),*task.get("reuse",[])]:
        special={"SKILL.md","GLOSSARY.md","context:goal","context:policy","tool:lean"}
        if source in special and source not in available: missing.append(source)
        elif source not in special and source not in records and source not in available and not any(source in {s.get("path"), s.get("name")} for s in instance.get("sources", [])): missing.append(source)
    if missing: return {"state": "not_ready", "basis": [], "errors": ["missing inputs: " + ",".join(missing)]}
    blocked = [dep for dep in {*task.get("dependencies", []), *task.get("reuse", [])}
               if dep not in records or records[dep][1].get("use_suspended")
               or records[dep][1].get("status") in {"blocked", "withdrawn", "invalid", "use_suspended"}
               or (records[dep][0] == "knowledge" and records[dep][1].get("lean_code") and records[dep][1].get("status") != "verified")
               or (records[dep][0] == "task" and dep in task.get("dependencies", []) and
                   (records[dep][1].get("status") != "completed" or
                    records[dep][1].get("assessment", {}).get("current") is False))]
    if blocked: return {"state": "not_ready", "basis": [], "errors": ["blocked dependencies: " + ",".join(blocked)]}
    result = evaluate_condition(task.get("occurrence_condition", {"op": "always"}), instance, runtime)
    result["basis"].extend(_basis(x) for x in approved if isinstance(x, dict) and "id" in x)
    return result


def _utc(value: str) -> datetime:
    if not isinstance(value, str): raise ValueError("UTC timestamp required")
    parsed=datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None: raise ValueError("naive timestamp forbidden")
    return parsed.astimezone(timezone.utc)


def _event(kind: str, when: str, target: str | None = None) -> dict:
    seed = f"{kind}|{when}|{target or ''}"; return {"id": hashlib.sha256(seed.encode()).hexdigest()[:24], "kind": kind, "at": when, "target": target}


def collect_due_events(instance: dict, runtime: dict, now_iso: str) -> list[dict]:
    now = _utc(now_iso); events = []
    if instance.get("goal_status") not in {"mathematically_solved", "research_goal_satisfied"}:
        due = runtime.get("next_research_reconsider_at")
        if due and _utc(due) <= now: events.append(_event("research_reconsider_due", due))
    for task in runtime.get("tasks", {}).values():
        if not isinstance(task, dict): continue
        if task.get("wake_at") and _utc(task["wake_at"]) <= now: events.append(_event("task_wake_due", task["wake_at"], task.get("id")))
        for condition in task.get("due_conditions", []):
            outcome = evaluate_condition(condition, instance, runtime)
            key=_hash(condition); previous=runtime.get("condition_states",{}).get(f"{task.get('id')}:{key}")
            if outcome["state"] == "ready" and previous != "ready": events.append(_event("task_condition_due", key, task.get("id")))
        if task.get("newinput"): events.append(_event("task_new_input", now_iso, task.get("id")))
    existing = {event.get("id") for event in runtime.get("events", [])}
    return [event for event in events if event["id"] not in existing]


def apply_event_schedule(instance: dict, runtime: dict, now_iso: str) -> dict:
    """Return a deep-copied runtime with due events preserved once; paused does not consume them."""
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    events = collect_due_events(new_instance, new_runtime, now_iso)
    new_runtime.setdefault("events", []).extend(events)
    new_runtime.setdefault("pending_events", []).extend(event["id"] for event in events if event["id"] not in new_runtime.get("pending_events", []))
    states=new_runtime.setdefault("condition_states",{})
    for task in new_runtime.get("tasks",{}).values():
        for condition in task.get("due_conditions",[]): states[f"{task.get('id')}:{_hash(condition)}"]=evaluate_condition(condition,new_instance,new_runtime)["state"]
    return {"instance": new_instance, "runtime": new_runtime, "events": events}
