"""Knowledge currentness and Lean trust-environment transitions.

This module records and propagates semantic state.  It does not run formal
tools, enforce OS isolation, or infer mathematical equivalence.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Iterable

from .repository import new_id
from .input_basis import capture_sources, sources_current


def _hash(record: Any) -> str:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty")


def _records(instance: dict, runtime: dict) -> Iterable[tuple[str, dict]]:
    for key in ("knowledge",):
        for record_id, record in instance.get(key, {}).items():
            yield record_id, record
    for record in instance.get("relations", []):
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            yield record["id"], record
    for record in instance.get("goal_judgments", []):
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            yield record["id"], record
    for key in ("tasks", "activities", "executions"):
        for record_id, record in runtime.get(key, {}).items():
            yield record_id, record


def _find(instance: dict, runtime: dict, record_id: str) -> dict | None:
    return next((record for candidate, record in _records(instance, runtime)
                 if candidate == record_id), None)


def _status(record: dict) -> str:
    for key in ("status", "lifecycle", "decision"):
        if isinstance(record.get(key), str):
            return record[key]
    return "present"


def capture_basis(instance: dict, runtime: dict, record_ids: list[str]) -> list[dict]:
    if not isinstance(record_ids, list) or len(record_ids) != len(set(record_ids)):
        raise ValueError("record_ids must be a list of distinct IDs")
    basis = []
    for record_id in record_ids:
        _require_text(record_id, "record ID")
        record = _find(instance, runtime, record_id)
        if record is None:
            raise ValueError(f"unknown record ID: {record_id}")
        basis.append({"id": record_id, "sha256": _hash(record), "status": _status(record)})
    return basis


def validate_basis(basis: list[dict], instance: dict, runtime: dict) -> dict:
    reasons: list[str] = []
    if not isinstance(basis, list):
        return {"valid": False, "reasons": ["basis_not_a_list"]}
    seen: set[str] = set()
    for row in basis:
        if not isinstance(row, dict) or set(row) != {"id", "sha256", "status"}:
            reasons.append("invalid_basis_row")
            continue
        record_id = row["id"]
        if not isinstance(record_id, str) or record_id in seen:
            reasons.append(f"duplicate_or_invalid_id:{record_id}")
            continue
        seen.add(record_id)
        record = _find(instance, runtime, record_id)
        if record is None:
            reasons.append(f"missing:{record_id}")
            continue
        if _hash(record) != row["sha256"]:
            reasons.append(f"hash_changed:{record_id}")
        if _status(record) != row["status"]:
            reasons.append(f"status_changed:{record_id}")
    return {"valid": not reasons, "reasons": reasons}


_STRICT_REFERENCE_KEYS = frozenset({"dependencies"})
_REFERENCE_KEYS = frozenset({
    "used_sources", "exact_refs", "record_refs", "knowledge_refs",
    "evidence_refs", "source_refs", "formal_result_refs", "assessment_refs",
    "inputs", "reuse",
})
# Preserved earlier versions are history, not current dependencies of the record.
_HISTORY_KEYS = frozenset({"history", "use_history", "review_history", "revision_history", "assessment_history", "governance_history"})
_KNOWLEDGE_ID = re.compile(r"^KN-[A-Z0-9][A-Z0-9-]*$")
_ID_KEYS = frozenset({"id", "ref", "record_id", "knowledge_id"})
# Earlier revisions and superseded review rounds are preserved history, not current dependencies.
_HISTORY_KEYS = frozenset({"history", "previous_initial_reviews"})


def _field_refs(value: Any, *, strict: bool, known_ids: set[str]) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, str):
        if strict or value in known_ids or _KNOWLEDGE_ID.fullmatch(value):
            refs.add(value)
    elif isinstance(value, list):
        for item in value:
            refs.update(_field_refs(item, strict=strict, known_ids=known_ids))
    if isinstance(value, dict):
        identifiers = [item for key, item in value.items()
                       if key in _ID_KEYS and isinstance(item, str)]
        for item in identifiers:
            if strict or item in known_ids or _KNOWLEDGE_ID.fullmatch(item):
                refs.add(item)
        # A source-ref object is a locator.  Its path/hash/range strings are
        # validated by context_store, not interpreted as knowledge IDs here.
        if not identifiers and strict:
            for item in value.values():
                refs.update(_field_refs(item, strict=True, known_ids=known_ids))
    return refs


def _explicit_refs(value: Any, known_ids: set[str]) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if key in _HISTORY_KEYS:
                continue
            if key in _STRICT_REFERENCE_KEYS:
                refs.update(_field_refs(item, strict=True, known_ids=known_ids))
            elif key in _REFERENCE_KEYS:
                refs.update(_field_refs(item, strict=False, known_ids=known_ids))
            elif key == "basis" and isinstance(item, list):
                refs.update(_field_refs(item, strict=False, known_ids=known_ids))
            elif key in _HISTORY_KEYS:
                continue
            else:
                refs.update(_explicit_refs(item, known_ids))
    elif isinstance(value, list):
        for item in value:
            refs.update(_explicit_refs(item, known_ids))
    return refs


def assess_use(record: dict, instance: dict) -> dict:
    if not isinstance(record, dict):
        raise TypeError("record must be an object")
    reasons: list[str] = []
    if _status(record) not in {"verified", "active", "accepted"}:
        reasons.append(f"record_not_usable:{_status(record)}")
    if record.get("use_suspended"):
        reasons.append("record_use_suspended")
    if not sources_current(record.get("source_basis", []), instance):
        reasons.append("required_source_changed")
    if record.get("relation_claim") and (not record.get("relation_endpoint_basis") or not validate_basis(record["relation_endpoint_basis"], instance, {})["valid"]):
        reasons.append("relation_endpoint_basis_changed_or_missing")
    knowledge = instance.get("knowledge", {})
    refs = sorted(_explicit_refs(record, set(knowledge)))
    for record_id in refs:
        dependency = knowledge.get(record_id)
        if dependency is None:
            reasons.append(f"missing_dependency:{record_id}")
        elif dependency.get("status") != "verified" or dependency.get("use_suspended"):
            reasons.append(f"dependency_not_usable:{record_id}")
    formal = record.get("formal") if isinstance(record.get("formal"), dict) else {}
    environment_id = formal.get("trust_environment_id")
    if environment_id is not None:
        environment = instance.get("trust_environments", {}).get(environment_id)
        if environment is None:
            reasons.append(f"unknown_trust_environment:{environment_id}")
        elif environment.get("status") == "invalid":
            reasons.append(f"invalid_trust_environment:{environment_id}")
        elif instance.get("active_trust_environment") != environment_id:
            reasons.append(f"inactive_trust_environment:{environment_id}")
    basis = [{"id": item, "sha256": _hash(knowledge[item]), "status": _status(knowledge[item])}
             for item in refs if item in knowledge]
    return {"valid": not reasons, "reasons": reasons, "basis": basis}


def _history(record: dict, action: str, reason: str, actor_ref: str) -> list[dict]:
    previous = {key: deepcopy(value) for key, value in record.items() if key != "history"}
    return [*deepcopy(record.get("history", [])), {"action": action, "reason": reason,
            "actor_ref": actor_ref, "previous_sha256": _hash(record), "previous": previous}]


def _suspend(record: dict, suspension: dict) -> None:
    record["use_suspended"] = True
    suspensions = record.setdefault("use_suspensions", [])
    if suspension not in suspensions:
        suspensions.append(deepcopy(suspension))
    reason = suspension.get("reason")
    if isinstance(reason, str) and reason not in record.setdefault("use_suspension_reasons", []):
        record["use_suspension_reasons"].append(reason)


def _propagate(instance: dict, runtime: dict, roots: set[str], reason: str) -> None:
    affected = set(roots)
    known_ids = set(instance.get("knowledge", {}))
    changed = True
    while changed:
        changed = False
        for record_id, record in instance.get("knowledge", {}).items():
            causes = _explicit_refs(record, known_ids) & affected
            claim = record.get("relation_claim")
            if isinstance(claim, dict): causes |= {claim.get("source"), claim.get("target")} & affected
            if record_id not in affected and causes:
                affected.add(record_id)
                changed = True
                if record.get("status") == "verified":
                    _suspend(record, {"kind": "dependency", "root_ids": sorted(causes),
                                      "reason": reason})
    tasks_changed: list[str] = []
    for task_id, task in runtime.get("tasks", {}).items():
        if _explicit_refs({key: task.get(key) for key in ("dependencies", "inputs", "reuse", "results", "assessment")}, known_ids) & affected:
            # completed and closed are absorbing: keep the sealed disposition and only stop the current use of its assessment.
            if task.get("status") not in {"completed", "closed"}:
                task.setdefault("status_before_reassessment", task.get("status"))
                task["status"] = "waiting"
            if isinstance(task.get("assessment"), dict):
                task["assessment"]["current"] = False
                task["assessment"]["invalidated_reason"] = reason
            tasks_changed.append(task_id)
    judgments_changed: list[str] = []
    for index, judgment in enumerate(instance.get("goal_judgments", [])):
        if _explicit_refs(judgment, known_ids) & affected:
            judgment["current"] = False
            judgment["invalidated_reason"] = reason
            judgments_changed.append(judgment.get("id", f"goal_judgment:{index}"))
    event = {"kind": "knowledge_reassessment_required", "affected_knowledge": sorted(affected),
             "tasks": tasks_changed, "goal_judgments": judgments_changed, "reason": reason}
    runtime.setdefault("history", []).append(event)
    action = {"role": "research_plan", "reason": "knowledge currentness changed",
              "affected_knowledge": sorted(affected)}
    if (tasks_changed or judgments_changed) and action not in runtime.setdefault("queue", []):
        runtime["queue"].append(action)


def revise_knowledge(instance: dict, runtime: dict, knowledge_id: str, changes: dict,
                     *, reason: str, actor_ref: str) -> tuple[dict, dict]:
    _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    if not isinstance(changes, dict) or not changes:
        raise ValueError("changes must be a nonempty object")
    forbidden = {"id", "revision", "history", "status", "formal", "reviews", "verified_at", "use_suspended",
                 "use_suspensions", "identity_assessment", "review_cycle_id", "previous_review_cycle_id",
                 "producer_execution", "producer_execution_ids", "relation_endpoint_basis", "source_basis"}
    if forbidden & set(changes):
        raise ValueError("changes contain engine-owned fields")
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    record = new_instance.get("knowledge", {}).get(knowledge_id)
    if record is None: raise ValueError(f"unknown knowledge ID: {knowledge_id}")
    history = _history(record, "revise", reason, actor_ref)
    record.update(deepcopy(changes)); record["history"] = history
    record["revision"] = int(record.get("revision", 1)) + 1
    record["status"] = "candidate"; record["formal"] = {}; record["reviews"] = []
    record.pop("verified_at", None); record.pop("use_suspension_reasons", None)
    record.pop("use_suspensions", None)
    record["use_suspended"] = False
    if "source_basis" in record or "source_refs" in record:
        source_refs = [row["name"] for row in record.get("source_basis", [])]
        source_refs.extend(record.get("source_refs", []))
        record["source_basis"] = capture_sources(new_instance, source_refs)
    claim = record.get("relation_claim")
    if claim:
        if not isinstance(claim, dict) or any(key not in claim for key in ("source", "target")):
            raise ValueError("relation claim requires exact endpoint IDs")
        record["relation_endpoint_basis"] = capture_basis(new_instance, new_runtime, list(dict.fromkeys([claim["source"], claim["target"]])))
    _propagate(new_instance, new_runtime, {knowledge_id}, reason)
    return new_instance, new_runtime


def invalidate_knowledge(instance: dict, runtime: dict, knowledge_id: str, *,
                         reason: str, actor_ref: str) -> tuple[dict, dict]:
    _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    record = new_instance.get("knowledge", {}).get(knowledge_id)
    if record is None: raise ValueError(f"unknown knowledge ID: {knowledge_id}")
    record["history"] = _history(record, "invalidate", reason, actor_ref)
    record["status"] = "withdrawn"
    _suspend(record, {"kind": "semantic", "root_ids": [knowledge_id], "reason": reason})
    _propagate(new_instance, new_runtime, {knowledge_id}, reason)
    return new_instance, new_runtime

def suspend_for_source_change(instance: dict, runtime: dict, knowledge_id: str, *, source_name: str,
                              reason: str, actor_ref: str) -> tuple[dict, dict]:
    """Stop current use after a required source changed; the record itself is not withdrawn."""
    _require_text(source_name, "source_name"); _require_text(reason, "reason"); _require_text(actor_ref, "actor_ref")
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    record = new_instance.get("knowledge", {}).get(knowledge_id)
    if record is None: raise ValueError(f"unknown knowledge ID: {knowledge_id}")
    suspension = {"kind": "dependency", "source_name": source_name, "reason": reason}
    if suspension in record.get("use_suspensions", []):
        return new_instance, new_runtime
    record.setdefault("use_history", []).append({"action": "required_source_changed", "source_name": source_name,
                                                 "reason": reason, "actor_ref": actor_ref})
    _suspend(record, suspension)
    _propagate(new_instance, new_runtime, {knowledge_id}, reason)
    return new_instance, new_runtime


def register_environment(instance: dict, toolchain: dict,
                         allowed_axioms: list[str]) -> tuple[dict, str]:
    if not isinstance(toolchain, dict) or not toolchain:
        raise ValueError("toolchain must be a nonempty object")
    if (not isinstance(allowed_axioms, list) or len(allowed_axioms) != len(set(allowed_axioms))
            or any(not isinstance(item, str) or not item for item in allowed_axioms)):
        raise ValueError("allowed_axioms must contain distinct nonempty strings")
    output = deepcopy(instance); environment_id = new_id("TE")
    output.setdefault("trust_environments", {})[environment_id] = {
        "id": environment_id, "toolchain": deepcopy(toolchain),
        "allowed_axioms": list(allowed_axioms), "status": "registered"}
    return output, environment_id


def begin_transition(instance: dict, new_env_id: str) -> dict:
    environments = instance.get("trust_environments", {})
    if new_env_id not in environments: raise ValueError(f"unknown trust environment: {new_env_id}")
    if environments[new_env_id].get("status") == "invalid":
        raise ValueError("invalid trust environment cannot be a transition target")
    old_env_id = instance.get("active_trust_environment")
    if old_env_id is not None and old_env_id not in environments:
        raise ValueError("active trust environment is unknown")
    if old_env_id == new_env_id: raise ValueError("new trust environment is already active")
    targets = []
    for record_id, record in sorted(instance.get("knowledge", {}).items()):
        formal = record.get("formal") if isinstance(record.get("formal"), dict) else {}
        normal_target = old_env_id is not None and record.get("status") == "verified" and not record.get("use_suspended")
        recovery_target = (old_env_id is None and record.get("status") == "verified"
                           and record.get("use_suspended") and isinstance(formal.get("trust_environment_id"), str))
        if normal_target or recovery_target:
            previous_ids = list(dict.fromkeys([*formal.get("previous_environment_ids", []),
                                               *([formal["trust_environment_id"]]
                                                 if isinstance(formal.get("trust_environment_id"), str) else [])]))
            targets.append({"id": record_id, "source_sha256": hashlib.sha256(
                record.get("lean_code", "").encode("utf-8")).hexdigest(),
                "basis": {"id": record_id, "sha256": _hash(record), "status": _status(record)},
                "previous_environment_ids": previous_ids})
    return {"id": new_id("TR"), "from_environment": old_env_id,
            "to_environment": new_env_id, "targets": targets, "results": {}, "status": "checking"}


def record_transition_result(instance: dict, transition: dict, result_for_id: dict) -> dict:
    environment_id = transition.get("to_environment")
    if environment_id not in instance.get("trust_environments", {}):
        raise ValueError(f"unknown trust environment: {environment_id}")
    targets = {target["id"] for target in transition.get("targets", [])}
    result = deepcopy(result_for_id)
    record_id = result.get("id", result.get("knowledge_id"))
    if record_id is None and len(result) == 1:
        candidate_id, candidate_result = next(iter(result.items()))
        if candidate_id in targets and isinstance(candidate_result, dict):
            record_id, result = candidate_id, {"id": candidate_id, **candidate_result}
    if record_id not in targets: raise ValueError(f"result is not for a transition target: {record_id}")
    if result.get("status") not in {"verified", "failed", "rejected", "unavailable"}:
        raise ValueError("transition result has an unsupported status")
    output = deepcopy(transition); output.setdefault("results", {})[record_id] = result
    output["status"] = "ready" if set(output["results"]) == targets else "checking"
    return output


def activate_transition(instance: dict, transition: dict) -> dict:
    output = deepcopy(instance); environments = output.get("trust_environments", {})
    new_id_value = transition.get("to_environment")
    if new_id_value not in environments: raise ValueError(f"unknown trust environment: {new_id_value}")
    if output.get("active_trust_environment") != transition.get("from_environment"):
        raise ValueError("active trust environment changed during transition")
    targets = {target["id"]: target for target in transition.get("targets", [])}
    results = transition.get("results", {})
    if set(results) != set(targets) or any(result.get("status") != "verified" for result in results.values()):
        raise ValueError("all transition targets must be verified")
    for record_id, target in targets.items():
        record = output.get("knowledge", {}).get(record_id)
        if record is None or _hash(record) != target["basis"]["sha256"]:
            raise ValueError(f"transition basis changed: {record_id}")
        if record.get("status") != "verified":
            raise ValueError(f"transition target is no longer verified: {record_id}")
        source_hash = hashlib.sha256(record.get("lean_code", "").encode("utf-8")).hexdigest()
        if source_hash != target["source_sha256"] or results[record_id].get("source_sha256") != source_hash:
            raise ValueError(f"transition source changed: {record_id}")
    old_id = output["active_trust_environment"]
    if old_id is not None and environments[old_id].get("status") != "invalid":
        environments[old_id]["status"] = "superseded"
    environments[new_id_value]["status"] = "active"
    output["active_trust_environment"] = new_id_value
    for record_id, result in results.items():
        record = output["knowledge"][record_id]
        target = targets[record_id]
        reasons = deepcopy(record.get("use_suspension_reasons", []))
        typed = record.get("use_suspensions")
        resolved_environments = set(target["previous_environment_ids"])
        if isinstance(typed, list):
            resolved = [item for item in typed if isinstance(item, dict)
                        and item.get("kind") == "environment"
                        and item.get("environment_id") in resolved_environments]
            remaining = [deepcopy(item) for item in typed if item not in resolved]
        else:
            # A legacy boolean/string-only suspension has no safe typed cause.
            resolved, remaining = [], None
        record.setdefault("use_history", []).append({"action": "trust_environment_revalidated",
            "transition_id": transition.get("id"), "reasons": reasons,
            "resolved_suspensions": deepcopy(resolved),
            "previous_environment_ids": deepcopy(target["previous_environment_ids"])})
        record["formal"] = {**deepcopy(result), "trust_environment_id": new_id_value, "trust_environment_status": "active",
                            "previous_environment_ids": deepcopy(target["previous_environment_ids"])}
        if remaining is None:
            record["use_suspended"] = bool(record.get("use_suspended"))
        else:
            record["use_suspensions"] = remaining
            record["use_suspended"] = bool(remaining)
    return output


def invalidate_environment(instance: dict, runtime: dict, env_id: str, reason: str
                           ) -> tuple[dict, dict]:
    _require_text(reason, "reason")
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    environment = new_instance.get("trust_environments", {}).get(env_id)
    if environment is None: raise ValueError(f"unknown trust environment: {env_id}")
    environment["status"] = "invalid"; environment["invalidated_reason"] = reason
    if new_instance.get("active_trust_environment") == env_id:
        new_instance["active_trust_environment"] = None
    affected = set()
    for record_id, record in new_instance.get("knowledge", {}).items():
        formal = record.get("formal") if isinstance(record.get("formal"), dict) else {}
        if formal.get("trust_environment_id") == env_id:
            _suspend(record, {"kind": "environment", "environment_id": env_id,
                              "reason": reason})
            affected.add(record_id)
    if affected: _propagate(new_instance, new_runtime, affected, reason)
    return new_instance, new_runtime
