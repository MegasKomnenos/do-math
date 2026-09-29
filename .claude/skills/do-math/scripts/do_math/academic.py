"""Versioned postsolution academic requirements, separate from proof status."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib

from .canonical import exact_content_hash
from .values import distinct_texts


@lru_cache(maxsize=None)
def _requirement_checker():
    """The checker of the stored requirement shape, built once; the schema is a constant."""
    from jsonschema import Draft202012Validator
    from .record_schemas.schemas import ACADEMIC_REQUIREMENT
    return Draft202012Validator(ACADEMIC_REQUIREMENT)


def _requirement(value: dict) -> dict:
    """The stored shape (record_schemas), then distinct effect IDs and the defaults."""
    from .state_contract import validate_record
    validate_record(_requirement_checker(), value, "academic requirement")
    effects = [{"id": effect["id"], "scope": effect["scope"], "grant_id": effect.get("grant_id")}
               for effect in value.get("external_effects", [])]
    if len({effect["id"] for effect in effects}) != len(effects):
        raise ValueError("academic external effects need distinct IDs")
    return {"id": value["id"], "scope": value["scope"], "criteria": list(value["criteria"]),
            "assessor": "research_plan", "required_inputs": list(value.get("required_inputs", [])),
            "external_effects": effects}


def requirement_record(requirements: list[dict]) -> dict:
    """Validate the requirements of one approved charter edition."""
    if not isinstance(requirements, list) or any(not isinstance(item, dict) for item in requirements):
        raise ValueError("requirements must be objects")
    items = [_requirement(item) for item in requirements]
    if len({item["id"] for item in items}) != len(items):
        raise ValueError("requirements need distinct IDs")
    record = {"items": items}
    return {**record, "sha256": exact_content_hash(record)}


def solution_basis(goal_ref: str, records: list[dict]) -> dict:
    if not isinstance(goal_ref, str) or not goal_ref or not records:
        raise ValueError("solution basis needs goal and records")
    return {"goal_ref": goal_ref, "records": [{"id": record["id"], "sha256": exact_content_hash(record)} for record in records]}


def current_solution_basis(instance, runtime):
    """The current goal judgments' solution basis, or None when the goal is not currently solved.

    A pure function of state: the engine, the status report and the state checks share it.
    governance and the knowledge modules import this module, so they are read on first use."""
    if instance.get("goal_status") != "mathematically_solved":
        return None
    group = instance.get("goal_assessment_basis")
    judgments = [j for j in instance.get("goal_judgments", []) if j.get("basis") == group]
    if not judgments or any(not j.get("current", True) for j in judgments):
        return None
    from . import knowledge
    if any(not knowledge.validate_basis(j.get("record_basis", []), instance, runtime)["valid"] for j in judgments):
        return None
    ids = sorted({ref for j in judgments for ref in j.get("dependencies", []) if ref in instance["knowledge"]})
    from .knowledge_records import usable_links, all_records
    if not ids or any(not usable_links(instance, kid) for kid in ids):
        return None
    support = all_records(instance)
    pending, visited, support_ids = list(ids), set(), set()
    while pending:
        kid = pending.pop()
        if kid in visited:
            continue
        visited.add(kid)
        record = instance["knowledge"][kid]
        support_ids.add(record["kind_definition_id"])
        pending.extend(record.get("dependencies", []))
        for link in usable_links(instance, kid):
            support_ids.update(link.values())
    for ref in list(support_ids):
        env = support.get(ref, {}).get("trust_environment_id")
        if env:
            support_ids.add(env)
    records = [support[ref] for ref in sorted(visited | support_ids)]
    records += [{"id": j["execution_id"], **j} for j in judgments]
    from .governance import governance_view
    charter = governance_view(instance).get("charter")
    goal_ref = (exact_content_hash({"content": {key: value for key, value in charter["content"].items()
                                              if key != "academic_requirements"}, "document": charter.get("document")})
                if charter else str(instance.get("goal_revision", 1)))
    # Academic requirements have their own edition binding; changing them
    # alone cannot retroactively change the mathematical solution evidence.
    return solution_basis(goal_ref + ":" + str(group), records)


def criterion_obligations(task_id, requirement):
    """Stable item IDs in the ordinary TASKS contract, not another lifecycle."""
    return [{"id": task_id + ":criterion:" + str(index), "claim": claim,
             "judges": [requirement["assessor"]], "evidence_required": []}
            for index, claim in enumerate(requirement["criteria"], 1)]


def assessment_current(instance, runtime, record):
    task = runtime.get("tasks", {}).get(record.get("task_id"), {})
    from .task_scope import assessment_current as task_assessment_current
    applied = task.get("assessment", {})
    return (record.get("task_assessment_sha256") == exact_content_hash(applied)
            and applied.get("execution_id") == record.get("execution_id")
            and task_assessment_current(task, instance, runtime))


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


def academic_status(instance: dict, runtime: dict, current_basis: dict | None, *, resolve_evidence=None) -> dict:
    if instance.get("goal_status") != "mathematically_solved":
        return {"status": "not_applicable", "reason": "goal not mathematically solved"}
    if current_basis is None:
        return {"status": "incomplete", "reason": "solution basis unreadable"}
    requirements = current_requirements(instance)
    if unresolved_rejections(instance, runtime, current_basis, resolve_evidence=resolve_evidence):
        return {"status": "externally_rejected", "reason": "unresolved external rejection"}
    if not requirements.get("items"): return {"status":"not_applicable", "reason":"no academic requirements"}
    assessments = runtime.get("academic_assessments", [])
    for requirement in requirements["items"]:
        matching = [assessment for assessment in assessments if assessment.get("requirement_id") == requirement["id"]
                    and assessment.get("solution_basis") == current_basis
                    and assessment.get("requirements_sha256") == requirements["sha256"]
                    and assessment_current(instance, runtime, assessment)
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
    started = any(task.get("selected_by") or task.get("results") for task in tasks)
    return {"status": "active" if started else "pending", "reason": "requirements remain"}


def current_requirements(instance):
    from .governance import governance_view
    return governance_view(instance)["academic_requirements"]


EVIDENCE_FAMILIES = ("knowledge", "formal-result", "exposition", "external-operation", "execution")


def evidence_record(instance, runtime, identifier, resolve_evidence=None):
    """Resolve academic evidence in EVIDENCE_FAMILIES of planning.RECORD_FAMILIES, else by resolve_evidence."""
    from .planning import RECORD_FAMILIES
    found = []
    for family in EVIDENCE_FAMILIES:
        space, key = RECORD_FAMILIES[family]
        container = (instance if space == "research" else runtime).get(key)
        if isinstance(container, dict) and identifier in container:
            found.append(container[identifier])
    if not found and resolve_evidence:
        value = resolve_evidence(identifier)
        if value is not None: return value
    if len(found) != 1: raise ValueError("academic evidence must resolve uniquely: " + str(identifier))
    return found[0]


def stored_evidence(store, head, ref):
    """Academic evidence stored at ``ref`` in the snapshot ``head``, or None when that snapshot lacks it.

    evidence_record takes None as unresolvable evidence, so an absent path makes a
    resolution unresolved instead of failing the read. The engine and the status
    report read stored evidence through this one function."""
    return store.read_many([ref], head, missing="omit").get(ref)


def _evidence_hash(value):
    return hashlib.sha256(value).hexdigest() if isinstance(value, bytes) else exact_content_hash(value)


def record_resolution(instance, runtime, basis, resolution, *, execution_id, resolve_evidence=None):
    """Seal an actual planner assessment and its currently resolvable evidence."""
    rejection = next((r for r in runtime.get("external_rejections", []) if r.get("id") == resolution.get("id")), None)
    execution = runtime.get("executions", {}).get(execution_id, {})
    if basis is None or rejection is None or rejection.get("solution_basis") != basis: raise ValueError("rejection basis is not current")
    if execution.get("role") != "research_plan" or execution.get("input_solution_basis") != basis: raise ValueError("planner execution lacks current solution input")
    if resolution.get("decision") not in {"resolved", "unresolved"} or not isinstance(resolution.get("evidence"), str) or not resolution["evidence"].strip():
        raise ValueError("resolution requires verdict and actual assessment")
    refs = distinct_texts(resolution.get("evidence_refs"), "resolution evidence refs")
    if not refs: raise ValueError("resolution needs resolvable evidence")
    record = {"rejection_id": rejection["id"], "rejection_sha256": exact_content_hash(rejection), "solution_basis": deepcopy(basis),
              "requirements_sha256": current_requirements(instance).get("sha256"), "execution_id": execution_id,
              "decision": resolution["decision"], "evidence": resolution["evidence"],
              "evidence_refs": refs, "evidence_hashes": {ref:_evidence_hash(evidence_record(instance, runtime, ref, resolve_evidence)) for ref in refs}}
    record["id"] = "AR-" + exact_content_hash(record)[:24]
    record["sha256"] = exact_content_hash(record)
    records = runtime.setdefault("academic_resolution_records", [])
    if not any(r.get("id") == record["id"] for r in records): records.append(record)
    return deepcopy(record)


def unresolved_rejections(instance, runtime, basis, *, resolve_evidence=None):
    unresolved = []
    for rejection in runtime.get("external_rejections", []):
        if rejection.get("solution_basis") != basis: continue
        matches = [r for r in runtime.get("academic_resolution_records", []) if r.get("rejection_id") == rejection.get("id")]
        record = matches[-1] if matches else {}
        try:
            valid = (bool(record) and record.get("decision") == "resolved" and record.get("solution_basis") == basis
                     and record.get("rejection_sha256") == exact_content_hash(rejection)
                     and record.get("requirements_sha256") == current_requirements(instance).get("sha256")
                     and record.get("sha256") == exact_content_hash({k:v for k,v in record.items() if k != "sha256"})
                     and runtime.get("executions", {}).get(record.get("execution_id"), {}).get("input_solution_basis") == basis
                     and bool(record.get("evidence_refs"))
                     and all(_evidence_hash(evidence_record(instance, runtime, ref, resolve_evidence)) == record["evidence_hashes"][ref] for ref in record["evidence_refs"]))
        except (ValueError, KeyError): valid = False
        if not valid: unresolved.append(deepcopy(rejection))
    return unresolved


def external_prerequisite(instance, runtime, basis, operation, grant, *, resolve_evidence=None):
    """Generic requests with academic restrictions are checked too, not only bound ones."""
    if not (grant.get("academic_only") or grant.get("requires_academic") or operation.get("academic_binding") or operation.get("academic_basis")): return True
    if instance.get("goal_status") != "mathematically_solved" or basis is None or unresolved_rejections(instance, runtime, basis, resolve_evidence=resolve_evidence): return False
    binding = operation.get("academic_binding")
    if binding:
        requirements = current_requirements(instance)
        requirement = next((r for r in requirements.get("items", []) if r["id"] == binding.get("requirement_id")), None)
        return bool(requirement and binding.get("solution_basis") == basis and binding.get("requirements_sha256") == requirements.get("sha256")
                    and any(e["id"] == binding.get("effect_id") and e.get("grant_id") in {None, grant.get("id")} for e in requirement["external_effects"]))
    expected = {"solution_basis":basis,"requirements_sha256":current_requirements(instance).get("sha256")}
    return operation.get("academic_basis") == expected and academic_status(instance, runtime, basis, resolve_evidence=resolve_evidence)["status"] in {"completed", "not_applicable"}


def bind_external_prerequisite(instance, runtime, basis, operation, *, resolve_evidence=None):
    if basis is None or instance.get("goal_status") != "mathematically_solved" or unresolved_rejections(instance,runtime,basis,resolve_evidence=resolve_evidence):
        raise ValueError("no current solution for this request")
    if operation.get("status") != "prepared" or operation.get("transmitted") or operation.get("attempts"):
        raise ValueError("cannot change academic premise after transmission")
    result=deepcopy(operation)
    result["academic_basis"]={"solution_basis":deepcopy(basis),"requirements_sha256":current_requirements(instance).get("sha256")}
    return result


def apply_goal_assurance(instance, *, decision, basis, judgments, runtime=None):
    """Only mathematical proof judgments can establish the v5 final goal fact."""
    if decision not in {"unsolved", "mathematically_solved"}: raise ValueError("nonformal final goal assurance is not supported")
    if decision == "mathematically_solved" and (not basis or not judgments or any(j.get("decision") != "satisfied" or j.get("current") is not True or not j.get("formal_result_refs") for j in judgments)):
        raise ValueError("mathematical assurance needs current formal-result judgments")
    if decision == "mathematically_solved":
        from .knowledge_records import formal_usable
        from .governance import validate_goal_additional_audits
        validate_goal_additional_audits(instance, judgments, runtime=runtime)
        current = [j for j in instance.get("goal_judgments",[]) if j.get("basis") == basis]
        if current != judgments or any(not j.get("scope_complete") for j in judgments):
            raise ValueError("final status must consume the complete recorded judgment group")
        required = {j.get("required") for j in judgments}
        if required != {len(judgments)} or len({j.get("execution_id") for j in judgments}) != len(judgments) or len({j.get("slot") for j in judgments}) != len(judgments):
            raise ValueError("final status lacks the required independent judgment slots")
        for ref in {ref for judgment in judgments for ref in judgment["formal_result_refs"]}:
            formal = instance.get("formal_results",{}).get(ref)
            if not formal or not formal_usable(instance,formal): raise ValueError("final goal cites unavailable formal evidence")
    result = deepcopy(instance)
    result.update(goal_status=decision, goal_assessment_basis=deepcopy(basis))
    return result
