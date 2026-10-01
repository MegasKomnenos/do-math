"""Case-scoped reuse of user authority, with blind independent judgments."""
from copy import deepcopy
from datetime import datetime, timezone

from .values import parse_utc
from .canonical import exact_content_hash


def case_basis_reference_ids(case):
    """Return IDs from the closed string-or-``{"id": ID}`` case-reference form."""
    refs = case.get("basis_refs", [])
    if not isinstance(refs, list):
        raise ValueError("case basis refs must be a list")
    identifiers = []
    for reference in refs:
        if isinstance(reference, str):
            identifier = reference
        elif isinstance(reference, dict) and set(reference) == {"id"}:
            identifier = reference["id"]
        else:
            raise ValueError("case basis reference must be a record ID or an exact {'id': ID} object")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("case basis refs must name distinct record IDs")
        identifiers.append(identifier)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("case basis refs must name distinct record IDs")
    return identifiers


def validate_delegation(delegation, *, now_iso):
    if not isinstance(delegation, dict): raise ValueError("delegation record required")
    for key in ("id", "decision_kind", "original_decision_id", "source_ref", "decision_id"):
        if not isinstance(delegation.get(key), str) or not delegation[key].strip(): raise ValueError("missing delegation " + key)
    if delegation.get("status") != "active": raise ValueError("delegation inactive")
    # The design prohibits these decisions; its other examples are not a closed kind list.
    if delegation["decision_kind"] in {"proposal_adoption", "contract_limit_continuation"}:
        raise ValueError("this decision requires a new explicit user decision")
    for key in ("included_targets", "excluded_targets", "external_effects"):
        value = delegation.get(key)
        if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value) or len(value) != len(set(value)):
            raise ValueError("invalid delegation " + key)
    if not delegation["included_targets"]: raise ValueError("delegation needs explicit included scope")
    if not isinstance(delegation.get("resource_limits", {}), dict): raise ValueError("resource limits must be mapped")
    if any(type(v) is not int or v < 0 for v in delegation.get("resource_limits", {}).values()):
        raise ValueError("invalid delegation resource limit")
    if delegation.get("expires_at") and parse_utc(delegation["expires_at"]) <= parse_utc(now_iso): raise ValueError("delegation expired")
    return deepcopy(delegation)


def _basis(instance, runtime, delegation_id, case, now_iso):
    delegation = validate_delegation(instance.get("delegations", {}).get(delegation_id), now_iso=now_iso)
    original = instance.get("decisions", {}).get(delegation["original_decision_id"], {})
    approval = instance.get("decisions", {}).get(delegation["decision_id"], {})
    if original.get("actor") != "user" or original.get("kind") != delegation["decision_kind"]:
        raise ValueError("original decision is absent or incompatible")
    if approval.get("actor") != "user":
        raise ValueError("delegation has no current user approval")
    approved = approval.get("change", {}).get("delegation")
    declared = {k:v for k,v in delegation.items() if k not in {"source_ref", "decision_id", "created_at"}}
    if approval.get("kind") != "delegation" or approved != declared or approval.get("source_ref") != delegation["source_ref"]:
        raise ValueError("approval does not bind the exact delegated scope")
    source = instance.get("governance_sources", {}).get(delegation["source_ref"])
    from .governance import validate_source
    validate_source(source or {})
    original_source = instance.get("governance_sources", {}).get(original.get("source_ref"))
    validate_source(original_source or {})
    target = case.get("target_id")
    if case.get("decision_kind") != delegation["decision_kind"] or target not in delegation["included_targets"] or target in delegation["excluded_targets"]:
        raise ValueError("case outside delegation scope")
    effects, resources = case.get("external_effects"), case.get("resources")
    if not isinstance(effects, list) or any(x not in delegation["external_effects"] for x in effects): raise ValueError("external effect outside delegation")
    limits = delegation.get("resource_limits", {})
    if not isinstance(resources, dict) or any(k not in limits or type(v) is not int or v < 0 or v > limits[k] for k, v in resources.items()):
        raise ValueError("resource request outside delegation")
    if not isinstance(case.get("effect"), dict) or not case.get("id"): raise ValueError("case must preserve exact proposed effect")
    # Use the same globally unique record population as task/currentness checks.
    from .planning import record_index
    records = record_index(instance, runtime)
    target_record = records.get(target, (None, None))[1]
    if target == instance.get("id"): target_record = {"id": target, "governance": instance.get("governance")}
    if target_record is None: raise ValueError("case target does not resolve")
    refs = case_basis_reference_ids(case)
    if any(ref not in records for ref in refs): raise ValueError("case basis reference does not resolve")
    return {"delegation": delegation, "original_decision": deepcopy(original), "approval": deepcopy(approval),
            "source": deepcopy(source), "original_source":deepcopy(original_source), "case": deepcopy(case),
            "target": deepcopy(target_record), "references": {ref: deepcopy(records[ref][1]) for ref in refs}}


def prepare_application(instance, runtime, delegation_id, case, *, now_iso):
    basis = _basis(instance, runtime, delegation_id, case, now_iso)
    input_sha = exact_content_hash(basis)
    identifier = "DA-" + input_sha[:24]
    record = {"id": identifier, "delegation_id": delegation_id, "basis": basis, "input_sha256": input_sha, "judgments": {}}
    existing = runtime.setdefault("delegation_applications", {}).get(identifier)
    if existing is not None: return deepcopy(existing)
    runtime["delegation_applications"][identifier] = record
    return deepcopy(record)


def judgment_input(runtime, application_id):
    """Both executions receive this same payload, without either judgment."""
    record = runtime["delegation_applications"][application_id]
    return {"basis": deepcopy(record["basis"]), "input_sha256": record["input_sha256"]}


def _judgment_input_hash(execution):
    # ENGINE seals the complete role context separately from the blind case.
    return execution.get("delegation_input_sha256")


def _check_judgment(runtime, record, execution_id, output, author_ids):
    """What one stage judgment satisfies when it is recorded and again when its application is used."""
    execution = runtime.get("executions", {}).get(execution_id, {})
    if execution.get("role") != "intent_interpretation" or _judgment_input_hash(execution) != record["input_sha256"]:
        raise ValueError("judgment execution must bind blind shared input")
    from .governance import validate_independent_execution
    validate_independent_execution(runtime, execution_id, author_ids)
    if output.get("input_sha256") != record["input_sha256"]:
        raise ValueError("judgment needs current input, verdict, reasons")


def record_judgment(runtime, application_id, output, *, execution_id, stage):
    record = runtime["delegation_applications"][application_id]
    if stage not in {"interpret", "check"} or stage in record["judgments"] or record.get("application"):
        raise ValueError("invalid or sealed judgment stage")
    author_ids = {j["execution_id"] for j in record["judgments"].values()}
    author_ids.update(record["basis"]["original_decision"].get("author_execution_ids", []))
    _check_judgment(runtime, record, execution_id, output, author_ids)
    if output.get("decision") not in {"within_scope", "outside_scope", "unresolved"} or not isinstance(output.get("reason"), str) or not output["reason"].strip():
        raise ValueError("judgment needs current input, verdict, reasons")
    record["judgments"][stage] = {"execution_id": execution_id, "output": deepcopy(output), "sha256": exact_content_hash(output)}
    return deepcopy(record)


def _checked(instance, runtime, application_id, now_iso):
    record = runtime.get("delegation_applications", {}).get(application_id)
    if record is None: raise ValueError("application not found")
    basis = _basis(instance, runtime, record["delegation_id"], record["basis"]["case"], now_iso)
    receipt = record.get("application", {})
    expected = receipt.get("post_basis_sha256",record["input_sha256"])
    if receipt and receipt.get("sha256") != exact_content_hash({k:v for k,v in receipt.items() if k != "sha256"}): raise ValueError("delegation receipt changed")
    if exact_content_hash(basis) != expected or exact_content_hash(record["basis"]) != record["input_sha256"]: raise ValueError("delegation application stale")
    judgments = record["judgments"]
    if set(judgments) != {"interpret", "check"} or len({j["execution_id"] for j in judgments.values()}) != 2: raise ValueError("two independent judgments required")
    from .governance import validate_independent_execution
    validate_independent_execution(runtime,judgments["check"]["execution_id"],[judgments["interpret"]["execution_id"]])
    for judgment in judgments.values():
        _check_judgment(runtime, record, judgment["execution_id"], judgment["output"],
            record["basis"]["original_decision"].get("author_execution_ids", []))
        if judgment["sha256"] != exact_content_hash(judgment["output"]) or judgment["output"]["decision"] != "within_scope":
            raise ValueError("delegation verdict is not current matching judgment")
    return record


def authorize_delegated_case(instance, delegation_id, case, *, runtime=None, now_iso):
    try:
        record = _checked(instance, runtime or {}, case.get("application_id"), now_iso)
        if record["delegation_id"] != delegation_id: raise ValueError("wrong delegation")
        supplied = {key: value for key, value in case.items() if key != "application_id"}
        if supplied and supplied != record["basis"]["case"]: raise ValueError("requested case differs from independently checked effect")
        return {"allowed": True, "delegation_id": delegation_id, "application_id": record["id"], "original_decision_id": record["basis"]["original_decision"]["id"]}
    except ValueError as error:
        return {"allowed": False, "delegation_id": delegation_id, "reason": str(error)}


def apply_application(instance, runtime, application_id, *, apply_effect, now_iso):
    record = _checked(instance, runtime, application_id, now_iso)
    if record.get("application"): return deepcopy(instance), deepcopy(runtime), deepcopy(record["application"])
    result, state = apply_effect(deepcopy(instance), deepcopy(runtime), deepcopy(record["basis"]["case"]["effect"]))
    for family in ("decisions", "grants", "delegations", "governance", "governance_sources"):
        if result.get(family) != instance.get(family): raise ValueError("delegated application cannot alter authority")
    receipt = {"status": "applied", "application_id": application_id, "input_sha256": record["input_sha256"],
               "original_decision_id": record["basis"]["original_decision"]["id"], "effect": deepcopy(record["basis"]["case"]["effect"])}
    receipt["post_basis_sha256"] = exact_content_hash(_basis(result,state,record["delegation_id"],record["basis"]["case"],now_iso))
    receipt["sha256"] = exact_content_hash(receipt)
    state["delegation_applications"][application_id]["application"] = receipt
    return result, state, receipt
