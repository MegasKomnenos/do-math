"""Structured candidate import and explicit knowledge/relation ontology."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import re
from typing import Any

from .repository import canonical_json, new_id
from .knowledge import assess_use, _propagate, capture_basis


_TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")
_KNOWLEDGE_FIELDS = {
    "id", "kind", "title", "statement", "explanation", "summary", "lean_code",
    "declaration_names", "dependencies", "origin_refs", "source_refs", "confirmed_scope",
    "epistemic_status", "selection_relevance", "uncertainty_assessment",
    "relation_claim",
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


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def ensure_ontology(instance: dict) -> dict:
    output = deepcopy(instance)
    registry = output.setdefault("kind_definitions", {})
    for definition in _BUILTINS:
        registry.setdefault(_key(definition["family"], definition["token"]), deepcopy(definition))
    return output


def catalog_definitions(instance: dict) -> dict:
    current = ensure_ontology(instance)["kind_definitions"]
    return {"knowledge": [deepcopy(value) for key, value in sorted(current.items())
                          if key.startswith("knowledge:") and value.get("status") == "active"],
            "relations": [deepcopy(value) for key, value in sorted(current.items())
                          if key.startswith("relation:") and value.get("status") == "active"]}


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
            "mathematical_claim", "requires_evidence", "requires_formal_results", "requires_assessments"}:
        raise ValueError("kind definition has unsupported constraints")
    if any(not isinstance(value, bool) for value in constraints.values()):
        raise ValueError("kind constraints must be booleans")
    if constraints.get("mathematical_claim"):
        definition = deepcopy(definition)
        definition["constraints"].update(requires_formal_results=True, requires_assessments=True)
    output = ensure_ontology(instance); key = _key(family, token)
    if key in output["kind_definitions"]:
        raise ValueError("kind token is already defined")
    output["kind_definitions"][key] = {**deepcopy(definition), "status": "active", "builtin": False,
        "source_ref": source_ref, "actor_ref": actor_ref,
        "created_at": datetime.now(timezone.utc).isoformat()}
    return output, token


def _definition_for(instance: dict, family: str, token: str) -> dict:
    definition = ensure_ontology(instance)["kind_definitions"].get(_key(family, token))
    if not definition or definition.get("status") != "active":
        raise ValueError(f"unknown {family} kind: {token}")
    return definition


def import_candidate(instance: dict, runtime: dict, candidate: dict, *, source_ref: str,
                     actor_ref: str) -> tuple[dict, dict, str]:
    _text(source_ref, "source_ref"); _text(actor_ref, "actor_ref")
    if not isinstance(candidate, dict) or set(candidate) - _KNOWLEDGE_FIELDS:
        raise ValueError("candidate has unsupported fields")
    for field in ("kind", "title", "statement", "explanation", "summary", "lean_code"):
        if not isinstance(candidate.get(field), str) or (field != "lean_code" and not candidate[field].strip()):
            raise ValueError(f"candidate {field} is invalid")
    output, new_runtime = ensure_ontology(instance), deepcopy(runtime)
    _definition_for(output, "knowledge", candidate["kind"])
    declarations, dependencies = candidate.get("declaration_names", []), candidate.get("dependencies", [])
    if (not isinstance(declarations, list) or any(not isinstance(value, str) or not value for value in declarations)
            or len(declarations) != len(set(declarations))):
        raise ValueError("declaration_names must contain distinct strings")
    if (not isinstance(dependencies, list) or any(not isinstance(value, str) or not value for value in dependencies)
            or len(dependencies) != len(set(dependencies))):
        raise ValueError("dependencies must contain distinct knowledge IDs")
    record_id = candidate.get("id") or new_id("KN")
    if record_id in dependencies:
        raise ValueError("candidate cannot depend on itself")
    missing = [value for value in dependencies if value not in output.get("knowledge", {})]
    if missing:
        raise ValueError("candidate dependencies do not exist: " + ", ".join(missing))
    old = output.setdefault("knowledge", {}).get(record_id)
    if candidate["lean_code"] and not declarations:
        raise ValueError("a formal candidate requires exported declaration names")
    claim = candidate.get("relation_claim")
    if claim is not None:
        if not isinstance(claim, dict) or set(claim) != {"kind", "source", "target", "confirmed_scope"}:
            raise ValueError("relation_claim needs kind, source, target and confirmed_scope")
        _definition_for(output, "relation", claim["kind"])
        if any(claim[key] not in output["knowledge"] for key in ("source", "target")) or not isinstance(claim["confirmed_scope"], str) or not claim["confirmed_scope"].strip():
            raise ValueError("relation claim needs exact existing endpoints and scope")
    engine_fields = {"status", "formal", "reviews", "identity_assessment", "verified_at"}
    if engine_fields & set(candidate):
        raise ValueError("candidate cannot supply engine-owned verification fields")
    origin_refs = list(dict.fromkeys([*deepcopy(candidate.get("origin_refs", [])), source_ref]))
    record = {key: deepcopy(value) for key, value in candidate.items() if key != "id"}
    record.update(id=record_id, revision=int(old.get("revision", 0)) + 1 if old else 1,
                  status="candidate", formal={}, reviews=[], dependencies=list(dependencies),
                  declaration_names=list(declarations), origin_refs=origin_refs,
                  source_ref=source_ref, imported_by=actor_ref,
                  producer_execution=actor_ref,
                  imported_at=datetime.now(timezone.utc).isoformat(),
                  required_reviews=(old or {}).get("required_reviews",
                      output.get("config", {}).get("reviewers", 2)))
    if old:
        record["history"] = [*deepcopy(old.get("history", [])),
                             {key: deepcopy(value) for key, value in old.items() if key != "history"}]
        record["previous_review_cycle_id"] = old.get("review_cycle_id")
        previous = new_runtime.get("review_cycles", {}).get(old.get("review_cycle_id"))
        if previous and previous["status"] == "working": previous.update(status="unresolved", decision="unresolved", phase="ended")
    output["knowledge"][record_id] = record
    if claim is not None:
        record["relation_endpoint_basis"] = capture_basis(output, new_runtime, list(dict.fromkeys([claim["source"], claim["target"]])))
    if old: _propagate(output, new_runtime, {record_id}, "Imported knowledge revision changed its meaning basis")
    new_runtime.setdefault("history", []).append({"kind": "knowledge_candidate_imported",
        "knowledge_id": record_id, "revision": record["revision"], "source_ref": source_ref})
    new_runtime.setdefault("queue", [])[:] = [action for action in new_runtime.get("queue", [])
                                               if action.get("target") != record_id]
    next_action = {"role": "formal_check" if record["lean_code"] else "research_plan",
                   "target": record_id, "reason": "imported candidate requires verification",
                   "source_ref": source_ref}
    new_runtime["queue"].append(next_action)
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
    if constraints.get("requires_formal_results"):
        refs = relation.get("formal_result_refs", [])
        if not isinstance(refs, list) or not refs:
            reasons.append("formal_result_refs_required")
        else:
            for ref in refs:
                record = knowledge.get(ref)
                formal = record.get("formal", {}) if isinstance(record, dict) else {}
                if (not record or not assess_use(record, instance)["valid"] or formal.get("status") != "verified"):
                    reasons.append(f"formal_result_not_usable:{ref}")
                claim = (record or {}).get("relation_claim", {})
                if not isinstance(claim, dict) or any(claim.get(key) != relation.get(key) for key in ("kind", "source", "target", "confirmed_scope")):
                    reasons.append(f"formal_result_does_not_establish_this_relation:{ref}")
    if constraints.get("requires_assessments"):
        assessment_refs = relation.get("assessment_refs", [])
        if not isinstance(assessment_refs, list) or not assessment_refs:
            reasons.append("assessment_refs_required")
        else:
            effective = set()
            for proof_id in relation.get("formal_result_refs", []):
                record = knowledge.get(proof_id, {})
                assessment = record.get("identity_assessment")
                if isinstance(assessment, dict) and assessment.get("effective"):
                    effective.update(value for value in (assessment.get("cycle_id"),
                        assessment.get("id"), record.get("review_cycle_id")) if isinstance(value, str))
            for ref in assessment_refs:
                if ref not in effective:
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
    old = next((value for value in output.setdefault("relations", []) if value.get("id") == relation_id), None)
    record = {key: deepcopy(value) for key, value in relation.items() if key != "id"}
    mathematical = result["definition"]["constraints"].get("mathematical_claim", False)
    record.update(id=relation_id, revision=int(old.get("revision", 0)) + 1 if old else 1,
                  status="active", source_ref=source_ref, imported_by=actor_ref,
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
