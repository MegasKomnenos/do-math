"""Structured candidate import and explicit knowledge/relation ontology."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import re
from typing import Any

from .formal import is_lean_identifier
from .git_store import is_new_id
from .planning import record_index
from .repository import canonical_json, new_id
from .knowledge import assess_use, _propagate, capture_basis
from . import knowledge_records


_TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")
_KNOWLEDGE_FIELDS = {
    "id", "kind", "title", "statement", "explanation", "summary", "lean_code",
    "declaration_names", "dependencies", "origin_refs", "source_refs", "confirmed_scope",
    "epistemic_status", "selection_relevance", "uncertainty_assessment",
    "relation_claim", "definitions", "assumptions", "formal_result_ref",
}
_RELATION_FIELDS = {
    "id", "kind", "source", "target", "evidence", "evidence_refs",
    "formal_result_refs", "assessment_refs", "confirmed_scope",
}


def _definition(family: str, token: str, meaning: str, *, mathematical=False,
                evidence=True) -> dict:
    return {"family": family, "token": token, "meaning": meaning, "status": "active",
            "builtin": True, "constraints": {"mathematical_claim": mathematical,
            "requires_evidence": evidence, "requires_formal_results": mathematical,
            "requires_assessments": mathematical}}


_BUILTINS = [
    *[_definition("knowledge", token, meaning, evidence=False) for token, meaning in (
        ("definition", "A stated mathematical or research definition."),
        ("theorem", "A proposition proposed for formal and semantic verification."),
        ("conjecture", "An unverified mathematical proposition."),
        ("question", "An open research question."),
        ("observation", "A bounded observation with stated evidence and scope."),
        ("obstacle", "A recorded obstruction or failed approach."),
        ("definition_candidate", "A proposed definition not yet adopted."),
        ("proof_candidate", "A proposed proof or proof direction."),
        ("research_direction", "A direction for future investigation."),
        ("partial_result", "A result whose verified scope is smaller than the target."),
    )],
    *[_definition("relation", token, meaning) for token, meaning in (
        ("supports", "Research evidence supports consideration; it does not imply the target."),
        ("challenges", "Research evidence challenges a claim without itself refuting it."),
        ("generated_from", "The target was generated from the source."),
        ("supersedes", "The target is a newer meaning-preserving or explicitly revised record."),
        ("derived_from", "The target was derived using the source as research input."),
        ("cites", "The source cites the target as evidence or background."),
        ("refines", "The target refines the source as a research judgment, not a formal implication."),
        ("splits_from", "The target is one part split from the source."),
        ("analogous_to", "The records are analogous in the stated respects; no implication is asserted."),
    )],
    *[_definition("relation", token, meaning, mathematical=True) for token, meaning in (
        ("solves", "The source establishes the target problem in the stated scope."),
        ("refutes", "The source formally refutes the target claim."),
        ("partially_addresses", "The source formally addresses an explicit part of the target."),
        ("narrows_scope", "The source formally justifies a narrower target scope."),
        ("formally_implies", "The source proposition formally implies the target proposition."),
        ("formally_equivalent", "The source and target are formally equivalent in both directions."),
        ("formally_reduces_to", "The source problem formally reduces to the target problem."),
        ("formally_encodes", "The source is formally encoded by the target with stated preservation."),
        ("formally_simulates", "The target formally simulates the stated source behavior."),
    )],
]


def _key(family: str, token: str) -> str:
    return family + ":" + token


def _lookup_definition(instance, family, token):
    matches = [row for row in instance.get("kind_definitions", {}).values()
               if row.get("family") == family and row.get("token") == token]
    current = [row for row in matches if row.get("status") != "withdrawn"]
    if len(current) > 1:
        raise ValueError("multiple current definitions of one kind")
    return current[0] if current else next((row for row in reversed(matches)), None)


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def ensure_ontology(instance: dict) -> dict:
    output = deepcopy(instance)
    registry = output.setdefault("kind_definitions", {})
    for index, definition in enumerate(_BUILTINS):
        if definition["family"] == "knowledge":
            value = deepcopy(definition)
            value["id"] = "KD-" + str(index + 1).zfill(26)
            registry.setdefault(value["id"], value)
    return output


def relation_templates():
    return [{key: deepcopy(value) for key, value in row.items() if key not in {"status", "builtin"}}
            for row in _BUILTINS if row["family"] == "relation"]


def catalog_definitions(instance: dict) -> dict:
    current = ensure_ontology({"kind_definitions": instance.get("kind_definitions", {})})["kind_definitions"]
    return {"knowledge": [deepcopy(value) for key, value in sorted(current.items())
                          if value.get("family") == "knowledge" and value.get("status") == "active"],
            "relations": [deepcopy(value) for key, value in sorted(current.items())
                          if value.get("family") == "relation" and value.get("status") == "active"]}


def register_kind_definition(instance: dict, definition: dict, *, source_ref: str,
                             actor_ref: str) -> tuple[dict, str]:
    _text(source_ref, "source_ref"); _text(actor_ref, "actor_ref")
    if not isinstance(definition, dict) or set(definition) != {"family", "token", "meaning", "constraints"}:
        raise ValueError("kind definition requires family, token, meaning and constraints")
    family, token = definition["family"], definition["token"]
    if family not in {"knowledge", "relation"} or not isinstance(token, str) or not _TOKEN.fullmatch(token):
        raise ValueError("kind definition has an invalid family or token")
    _text(definition["meaning"], "meaning")
    constraints = definition["constraints"]
    if not isinstance(constraints, dict) or set(constraints) - {
            "mathematical_claim", "requires_evidence", "requires_formal_results", "requires_assessments",
            "allowed_epistemic_statuses", "required_fields"}:
        raise ValueError("kind definition has unsupported constraints")
    for key, value in constraints.items():
        if key in {"allowed_epistemic_statuses", "required_fields"}:
            if not isinstance(value, list) or not value or any(not isinstance(v, str) or not v for v in value) or len(value) != len(set(value)):
                raise ValueError("kind list constraints require distinct nonempty strings")
            if key == "required_fields" and set(value) - _KNOWLEDGE_FIELDS:
                raise ValueError("required fields may not grant authority or add unknown fields")
        elif not isinstance(value, bool):
            raise ValueError("kind boolean constraint expected")
    if constraints.get("mathematical_claim"):
        definition = deepcopy(definition)
        definition["constraints"].update(requires_formal_results=True, requires_assessments=True)
    output = ensure_ontology(instance)
    previous = _lookup_definition(output, family, token)
    if previous and previous["status"] != "withdrawn":
        raise ValueError("kind token is already defined")
    identifier = new_id("KD")
    output["kind_definitions"][identifier] = {**deepcopy(definition), "id": identifier, "status": "candidate", "builtin": False,
        "source_ref": source_ref, "actor_ref": actor_ref,
        "created_at": datetime.now(timezone.utc).isoformat()}
    if previous:
        output["kind_definitions"][identifier]["supersedes"] = previous["id"]
    return output, token


def check_kind_definition(instance, family, token, *, check_ref, actor_ref):
    _text(check_ref, "check_ref"); _text(actor_ref, "actor_ref")
    output = deepcopy(instance)
    record = _lookup_definition(output, family, token)
    if record is None:
        raise ValueError("unknown kind definition")
    if record["status"] not in {"candidate", "checked"}:
        raise ValueError("only candidate definitions can be checked")
    record.update(status="checked", check_ref=check_ref, checked_by=actor_ref)
    return output


def activate_kind_definition(instance, family, token, *, approval_ref, actor_ref):
    _text(approval_ref, "approval_ref"); _text(actor_ref, "actor_ref")
    output = deepcopy(instance)
    record = _lookup_definition(output, family, token)
    if record is None:
        raise ValueError("unknown kind definition")
    if record["status"] != "checked" or not record.get("check_ref"):
        raise ValueError("kind definition must be checked before activation")
    record.update(status="active", approval_ref=approval_ref, activated_by=actor_ref)
    return output


def withdraw_kind_definition(instance, runtime, family, token, *, reason, actor_ref):
    _text(reason, "reason"); _text(actor_ref, "actor_ref")
    output, new_runtime = deepcopy(instance), deepcopy(runtime)
    definition = _lookup_definition(output, family, token)
    if definition is None:
        raise ValueError("unknown kind definition")
    definition.update(status="withdrawn", withdrawn_reason=reason, withdrawn_by=actor_ref)
    roots = set()
    for row in output.get("knowledge", {}).values() if family == "knowledge" else output.get("relations", []):
        if row.get("kind_definition_id") == definition["id"]:
            roots.add(row["id"])
            if family == "relation":
                row["status"] = "suspended"
            else:
                row["kind_use_suspended"] = True
    if roots:
        _propagate(output, new_runtime, roots, reason)
    return output, new_runtime


def _definition_for(instance: dict, family: str, token: str) -> dict:
    definition = _lookup_definition(ensure_ontology({"kind_definitions": instance.get("kind_definitions", {})}),
                                     family, token)
    if not definition or definition.get("status") != "active":
        raise ValueError(f"unknown {family} kind: {token}")
    return definition


def candidate_shape_errors(candidate: dict) -> list[str]:
    """Shape rules of one knowledge candidate: the producer's submission check and import share them.

    How dependencies are named (new titles in a submission, IDs on import) and
    whether they exist stay with each caller."""
    errors = []
    for field in ("kind", "title", "statement", "explanation", "summary", "lean_code"):
        if not isinstance(candidate.get(field), str) or (field != "lean_code" and not candidate[field].strip()):
            errors.append(f"candidate {field} is invalid")
    declarations, dependencies = candidate.get("declaration_names", []), candidate.get("dependencies", [])
    if (not isinstance(declarations, list) or any(not isinstance(value, str) or not value for value in declarations)
            or len(declarations) != len(set(declarations))):
        errors.append("declaration_names must contain distinct strings")
    elif not all(is_lean_identifier(value) for value in declarations):
        errors.append("declaration_names must be Lean identifiers")
    if (not isinstance(dependencies, list) or any(not isinstance(value, str) or not value for value in dependencies)
            or len(dependencies) != len(set(dependencies))):
        errors.append("dependencies must contain distinct references")
    if isinstance(candidate.get("lean_code"), str) and candidate["lean_code"] and not declarations:
        errors.append("a formal candidate requires exported declaration names")
    return errors


def validate_insight(instance: dict, runtime: dict, insight: dict) -> None:
    """An incidental candidate needs a registered kind and real evidence refs."""
    for field in ("kind", "title", "statement", "summary"):
        _text(insight.get(field), "insight " + field)
    _definition_for(instance, "knowledge", insight["kind"])
    refs = insight.get("evidence_ids", [])
    if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref for ref in refs) or len(refs) != len(set(refs)):
        raise ValueError("insight evidence must contain distinct references")
    known = set(record_index(instance, runtime, source_aliases=True))
    for key in ("inputs", "events", "external_rejections"):
        known.update(row["id"] for row in runtime.get(key, []) if row.get("id"))
    unknown = set(refs) - known
    if unknown:
        raise ValueError("unknown insight evidence: " + ", ".join(sorted(unknown)))


def import_candidate(instance: dict, runtime: dict, candidate: dict, *, source_ref: str,
                     actor_ref: str, reserved_dependency_ids=(), plan_nonformal=True) -> tuple[dict, dict, str]:
    _text(source_ref, "source_ref"); _text(actor_ref, "actor_ref")
    if not isinstance(candidate, dict) or set(candidate) - _KNOWLEDGE_FIELDS:
        raise ValueError("candidate has unsupported fields")
    if "uncertainty_assessment" in candidate and not isinstance(candidate["uncertainty_assessment"], (str, dict)):
        raise ValueError("uncertainty_assessment must be text or an object")
    output, new_runtime = ensure_ontology(instance), deepcopy(runtime)
    candidate = deepcopy(candidate)
    reuse_formal = candidate.get("formal_result_ref")
    if reuse_formal:
        formal = output.get("formal_results", {}).get(reuse_formal)
        if not formal or not knowledge_records.formal_usable(output, formal):
            raise ValueError("reused formal result must be current and accepted")
        if candidate.get("lean_code") and candidate["lean_code"] != formal["lean_code"]:
            raise ValueError("reused formal source differs")
        if candidate.get("declaration_names") and candidate["declaration_names"] != formal["declaration_names"]:
            raise ValueError("reused formal declarations differ")
        candidate.update(lean_code=formal["lean_code"], declaration_names=deepcopy(formal["declaration_names"]))
    # A reused formal result has filled its verified source fields before the shared shape check.
    errors = candidate_shape_errors(candidate)
    if errors:
        raise ValueError(errors[0])
    definition = _definition_for(output, "knowledge", candidate["kind"])
    dependencies = candidate.get("dependencies", [])
    record_id = candidate.get("id") or new_id("KN")
    if not isinstance(record_id, str) or not is_new_id("KN", record_id):
        raise ValueError("knowledge ID must be a canonical KN-prefixed ULID")
    if record_id in dependencies:
        raise ValueError("candidate cannot depend on itself")
    reserved = set(reserved_dependency_ids)
    missing = [value for value in dependencies
               if value not in output.get("knowledge", {}) and value not in reserved]
    if missing:
        raise ValueError("candidate dependencies do not exist: " + ", ".join(missing))
    if record_id in knowledge_records.all_records(output):
        raise ValueError("record ID already exists; revisions require a new ID")
    constraints = definition.get("constraints", {})
    allowed = constraints.get("allowed_epistemic_statuses")
    if allowed is not None and candidate.get("epistemic_status") not in allowed:
        raise ValueError("epistemic_status is not allowed by the kind definition")
    if any(not candidate.get(field) for field in constraints.get("required_fields", [])):
        raise ValueError("candidate is missing kind-required fields")
    claim = candidate.get("relation_claim")
    if claim is not None:
        if not isinstance(claim, dict) or set(claim) != {"kind", "source", "target", "confirmed_scope"}:
            raise ValueError("relation_claim needs kind, source, target and confirmed_scope")
        _definition_for(output, "relation", claim["kind"])
        if any(claim[key] not in output.get("knowledge", {}) for key in ("source", "target")):
            raise ValueError("relation claim requires exact existing endpoints")
        _text(claim["confirmed_scope"], "confirmed_scope")
    from .input_basis import capture_sources
    source_refs = candidate.get("source_refs", [])
    if not isinstance(source_refs, list) or any(not isinstance(ref, str) for ref in source_refs):
        raise ValueError("source_refs must be a list of source references")
    if set(source_refs) - set(record_index(output, {}, families=(), source_aliases=True)):
        raise ValueError("required source does not exist")
    output, record_id = knowledge_records.create_candidate(output, {**candidate, "id": record_id},
        source_ref=source_ref, actor_ref=actor_ref)
    record = output["knowledge"][record_id]
    if actor_ref not in new_runtime.get('executions', {}):
        # User/import provenance is not an execution identity. Review author
        # exclusion links must resolve to real executions in this instance.
        authored = [record, output['expositions'][record['exposition_id']]]
        if record['formal_result_id'] and not reuse_formal:
            authored.append(output['formal_results'][record['formal_result_id']])
        for authored_record in authored:
            authored_record.pop('producer_execution', None)
            authored_record['origin_refs'] = list(dict.fromkeys([*authored_record.get('origin_refs', []), actor_ref]))
    record["kind_definition_id"] = definition["id"]
    record["source_basis"] = capture_sources(output, source_refs)
    if claim:
        record["relation_endpoint_basis"] = capture_basis(output, new_runtime, list(dict.fromkeys([claim["source"], claim["target"]])))
    new_runtime.setdefault("history", []).append({"kind": "knowledge_candidate_imported",
        "knowledge_id": record_id, "source_ref": source_ref})
    next_role = "identity_review" if reuse_formal else "formal_check" if record["formal_result_id"] else "research_plan"
    if next_role != 'research_plan' or plan_nonformal:
        action_id = new_id("AC")
        new_runtime.setdefault("queue", []).append({"id": action_id, "lineage_id": action_id, "role": next_role,
            "target": record_id, "reason": "imported candidate requires verification", "source_ref": source_ref})
    return output, new_runtime, record_id


def validate_relation(instance: dict, relation: dict) -> dict:
    reasons: list[str] = []
    if not isinstance(relation, dict) or set(relation) - _RELATION_FIELDS:
        return {"valid": False, "reasons": ["unsupported_relation_fields"], "definition": None}
    kind = relation.get("kind")
    try:
        definition = _definition_for(instance, "relation", kind)
    except ValueError as error:
        return {"valid": False, "reasons": [str(error)], "definition": None}
    knowledge = instance.get("knowledge", {})
    for endpoint in ("source", "target"):
        value = relation.get(endpoint)
        if value not in knowledge:
            reasons.append(f"missing_{endpoint}:{value}")
    constraints = definition.get("constraints", {})
    evidence = relation.get("evidence_refs", [])
    if relation.get("evidence"):
        evidence = [relation["evidence"], *evidence] if isinstance(evidence, list) else [relation["evidence"]]
    if constraints.get("requires_evidence") and not evidence:
        reasons.append("evidence_required")
    establishing = {}
    if constraints.get("requires_formal_results") or constraints.get("requires_assessments"):
        # Effective matching judgments of the named formal results that claim exactly this relation.
        formal_refs = relation.get("formal_result_refs", [])
        for assessment_id, assessment in instance.get("identity_assessments", {}).items():
            claim = assessment.get("relation_claim", {})
            if (assessment.get("formal_result_id") in formal_refs and assessment.get("decision") == "match"
                    and isinstance(claim, dict)
                    and all(claim.get(key) == relation.get(key) for key in ("kind", "source", "target", "confirmed_scope"))
                    and assess_use(assessment, instance)["valid"]):
                establishing[assessment_id] = assessment["formal_result_id"]
    if constraints.get("requires_formal_results"):
        refs = relation.get("formal_result_refs", [])
        if not isinstance(refs, list) or not refs:
            reasons.append("formal_result_refs_required")
        else:
            for ref in refs:
                record = instance.get("formal_results", {}).get(ref)
                if not record or not knowledge_records.formal_usable(instance, record):
                    reasons.append(f"formal_result_not_usable:{ref}")
                if ref not in establishing.values():
                    reasons.append(f"formal_result_does_not_establish_this_relation:{ref}")
    if constraints.get("requires_assessments"):
        assessment_refs = relation.get("assessment_refs", [])
        if not isinstance(assessment_refs, list) or not assessment_refs:
            reasons.append("assessment_refs_required")
        else:
            for ref in assessment_refs:
                if ref not in establishing:
                    reasons.append(f"assessment_not_effective:{ref}")
    return {"valid": not reasons, "reasons": reasons, "definition": deepcopy(definition)}


def import_relation(instance: dict, relation: dict, *, source_ref: str,
                    actor_ref: str) -> tuple[dict, str]:
    _text(source_ref, "source_ref"); _text(actor_ref, "actor_ref")
    result = validate_relation(instance, relation)
    if not result["valid"]:
        raise ValueError("invalid relation: " + ", ".join(result["reasons"]))
    output = ensure_ontology(instance)
    relation_id = relation.get("id") or new_id("RL")
    if not isinstance(relation_id, str) or not is_new_id("RL", relation_id):
        raise ValueError("relation ID must be a canonical RL-prefixed ULID")
    old = next((value for value in output.setdefault("relations", []) if value.get("id") == relation_id), None)
    record = {key: deepcopy(value) for key, value in relation.items() if key != "id"}
    mathematical = result["definition"]["constraints"].get("mathematical_claim", False)
    record.update(id=relation_id, revision=int(old.get("revision", 0)) + 1 if old else 1,
                  status="active", source_ref=source_ref, imported_by=actor_ref,
                  kind_definition_id=result["definition"]["id"],
                  authority="mathematical_connection" if mathematical else "research_connection",
                  imported_at=datetime.now(timezone.utc).isoformat())
    if old:
        record["history"] = [*deepcopy(old.get("history", [])),
                             {key: deepcopy(value) for key, value in old.items() if key != "history"}]
        output["relations"].remove(old)
    output["relations"].append(record)
    # Ensure the stored structure itself is deterministic JSON data.
    canonical_json(record)
    return output, relation_id
