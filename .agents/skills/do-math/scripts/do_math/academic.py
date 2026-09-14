"""Versioned postsolution academic requirements, separate from proof status."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value) or len(value) != len(set(value)):
        raise ValueError(f"{label} must contain distinct nonempty references")
    return list(value)


def _requirement(value: dict) -> dict:
    if set(value) - {"id", "scope", "assessor", "criteria", "required_inputs", "external_effects"}:
        raise ValueError("unsupported academic requirement fields")
    if not all(isinstance(value.get(key), str) and value[key].strip() for key in ("id", "scope")):
        raise ValueError("invalid academic requirement")
    if value.get("assessor") != "research_plan":
        raise ValueError("academic requirement assessor must be research_plan")
    criteria = _strings(value.get("criteria"), "academic criteria")
    if not criteria: raise ValueError("academic criteria must not be empty")
    effects = value.get("external_effects", [])
    if not isinstance(effects, list):
        raise ValueError("academic external_effects must be a list")
    normalized_effects = []
    for effect in effects:
        if isinstance(effect, dict) and set(effect) - {"id", "scope", "grant_id"}:
            raise ValueError("unsupported academic external effect fields")
        if not isinstance(effect, dict) or not all(isinstance(effect.get(key), str) and effect[key].strip() for key in ("id", "scope")):
            raise ValueError("invalid academic external effect")
        grant_id = effect.get("grant_id")
        if grant_id is not None and (not isinstance(grant_id, str) or not grant_id.strip()):
            raise ValueError("academic external effect grant_id must be a nonempty string or null")
        normalized_effects.append({"id": effect["id"], "scope": effect["scope"], "grant_id": grant_id})
    if len({effect["id"] for effect in normalized_effects}) != len(normalized_effects):
        raise ValueError("academic external effects need distinct IDs")
    return {"id": value["id"], "scope": value["scope"], "criteria": criteria,
            "assessor": "research_plan", "required_inputs": _strings(value.get("required_inputs", []), "academic required_inputs"),
            "external_effects": normalized_effects}


def set_requirements(instance: dict, requirements: list[dict]) -> dict:
    if not isinstance(requirements, list) or any(not isinstance(item, dict) for item in requirements):
        raise ValueError("requirements must be objects")
    items = [_requirement(item) for item in requirements]
    if len({item["id"] for item in items}) != len(items):
        raise ValueError("requirements need distinct IDs")
    result = deepcopy(instance)
    old = result.get("academic_requirements")
    if old:
        result.setdefault("academic_requirements_history", []).append(deepcopy(old))
    record = {"revision": result.get("academic_requirements", {}).get("revision", 0) + 1, "items": items}
    record["sha256"] = _hash(record)
    result["academic_requirements"] = record
    return result


def solution_basis(goal_ref: str, records: list[dict]) -> dict:
    if not isinstance(goal_ref, str) or not goal_ref or not records:
        raise ValueError("solution basis needs goal and records")
    return {"goal_ref": goal_ref, "records": [{"id": record["id"], "sha256": _hash(record)} for record in records]}


def effect_receipts(requirement: dict, *, task_id: str | None, requirements_sha256: str,
                    solution_basis_value: dict, runtime: dict) -> tuple[bool, list[dict]]:
    """Find current, successful ledger receipts for every required external effect."""
    effects = requirement.get("external_effects", [])
    if not effects:
        return True, []
    operations = runtime.get("external_operations", {})
    receipts: list[dict] = []
    for effect in effects:
        receipt = next((operation for operation in operations.values() if isinstance(operation, dict)
                        and operation.get("status") == "confirmed" and operation.get("succeeded") is True
                        and operation.get("academic_binding", {}).get("task_id") == task_id
                        and operation.get("academic_binding", {}).get("requirement_id") == requirement["id"]
                        and operation.get("academic_binding", {}).get("requirements_sha256") == requirements_sha256
                        and operation.get("academic_binding", {}).get("solution_basis") == solution_basis_value
                        and operation.get("academic_binding", {}).get("effect_id") == effect["id"]
                        and (effect.get("grant_id") is None or operation.get("grant_id") == effect["grant_id"])), None)
        if receipt is None:
            return False, receipts
        receipts.append({"effect_id": effect["id"], "operation_id": receipt.get("id"),
                         "grant_id": receipt.get("grant_id"), "request_sha256": receipt.get("request_sha256")})
    return True, receipts


def assess(requirement_id: str, basis: dict, requirements: dict, decision: str, evidence: list[dict]) -> dict:
    if decision not in {"satisfied", "not_satisfied", "unresolved"} or not isinstance(evidence, list) or not evidence:
        raise ValueError("assessment needs decision and evidence")
    requirement = next((item for item in requirements.get("items", []) if item["id"] == requirement_id), None)
    if requirement is None:
        raise ValueError("unknown requirement")
    if any(not isinstance(item, dict) or not isinstance(item.get("criterion"), str) or not isinstance(item.get("satisfied"), bool) or not isinstance(item.get("evidence"), str) for item in evidence):
        raise ValueError("invalid criteria evidence")
    criteria = {item["criterion"]: item for item in evidence}
    if len(criteria) != len(evidence) or set(criteria) != set(requirement["criteria"]):
        raise ValueError("assessment must cover each exact criterion once")
    if decision == "satisfied" and any(not item["satisfied"] or not item["evidence"].strip() for item in evidence):
        raise ValueError("satisfied assessment lacks exact criteria evidence")
    return {"requirement_id": requirement_id, "solution_basis": deepcopy(basis),
            "requirements_sha256": requirements["sha256"], "decision": decision,
            "evidence": deepcopy(evidence), "assessor": "research_plan"}


def academic_status(instance: dict, runtime: dict, current_basis: dict | None) -> dict:
    if instance.get("goal_status") != "mathematically_solved" or not instance.get("academic_requirements", {}).get("items"):
        return {"status": "not_applicable", "reason": "unsolved or no requirements"}
    if current_basis is None:
        return {"status": "incomplete", "reason": "solution basis unreadable"}
    requirements = instance["academic_requirements"]
    rejections = runtime.get("external_rejections", [])
    if any(item.get("solution_basis") == current_basis and (not item.get("resolved") or not item.get("resolution_evidence")) for item in rejections):
        return {"status": "externally_rejected", "reason": "unresolved external rejection"}
    assessments = runtime.get("academic_assessments", [])
    for requirement in requirements["items"]:
        matching = [assessment for assessment in assessments if assessment.get("requirement_id") == requirement["id"]
                    and assessment.get("solution_basis") == current_basis
                    and assessment.get("requirements_sha256") == requirements["sha256"]
                    and runtime.get("tasks", {}).get(assessment.get("task_id"), {}).get("assessment", {}).get("current") is not False
                    and assessment.get("assessor") == "research_plan" and assessment.get("decision") == "satisfied"]
        if not matching:
            break
        if not any(effect_receipts(requirement, task_id=assessment.get("task_id"), requirements_sha256=requirements["sha256"],
                                   solution_basis_value=current_basis, runtime=runtime)[0] for assessment in matching):
            break
    else:
        return {"status": "completed", "reason": "all current requirements satisfied"}
    tasks = [task for task in runtime.get("tasks", {}).values() if task.get("academic_requirement_id") in {item["id"] for item in requirements["items"]}
             and task.get("solution_basis") == current_basis and task.get("requirements_sha256") == requirements["sha256"]]
    return {"status": "active" if tasks else "pending", "reason": "requirements remain"}


def requirements_changed(old: dict, new: dict) -> bool:
    return old.get("academic_requirements") != new.get("academic_requirements")
