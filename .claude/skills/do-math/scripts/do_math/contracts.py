"""Role prompt and output schemas for the CLI adapters of every provider.

The ``do-math-cli/5`` output schemas describe newly requested CLI responses.
They are distinct from the persisted-record contract (``state_contract.STATE_CONTRACT_ID``).
The engine supplies IDs, hashes, references,
and persistence bindings after receiving a validated semantic response.

Every function that builds a schema, here and in the modules whose schemas a
response carries, returns ``file_io.json_copy`` of its result: no node is shared
with a module global such as ``TEXT`` or within the result, so a caller may
change the returned schema in place (이음새-정본.md §5).
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .execution_profiles import RESEARCH_PRODUCER_ROLES
from .values import SHA256_SCHEMA, json_copy


# The response contract every role output schema carries (``x-contract-id``).
RESPONSE_CONTRACT_ID = "do-math-cli/5"

ROLES = (
    "research_preparation", "research_plan", "research_work", "task_contract_review",
    "identity_review", "goal_audit", "supplemental_research", "operational_review",
    "intent_interpretation", "maintenance",
)


def closed_object(properties: dict[str, dict[str, Any]], required: list[str] | None = None) -> dict[str, Any]:
    """A closed wire object schema; every property is required unless ``required`` names them."""
    return {"type": "object", "additionalProperties": False, "properties": properties,
            "required": list(properties) if required is None else required}


STRING = {"type": "string"}
STRINGS = {"type": "array", "items": STRING}
COMMON = {"summary": STRING, "used_sources": STRINGS, "questions": STRINGS}


def task_candidate_record(candidate: dict, *, task_id: str, previous: dict | None = None,
                          trust_environment_id: str | None = None) -> dict:
    """Validate wire fields before assigning receiver-owned identity and revision.

    The caller allocates task_id and checks live authority/revision eligibility.
    This function returns detached contract fields, not a stored lifecycle record.
    """
    import jsonschema
    from .task_contracts import validate_contract_meaning
    errors = sorted(jsonschema.Draft202012Validator(TASK_CANDIDATE).iter_errors(candidate), key=lambda e: str(e.path))
    if errors:
        raise ValueError("invalid task candidate: " + errors[0].message)
    revised_id = candidate["revises_task_id"]
    if previous is None:
        if revised_id is not None:
            raise ValueError("revised task candidate requires its existing contract")
        revision = 1
    else:
        if previous.get("id") != task_id or revised_id != task_id:
            raise ValueError("task candidate and existing contract identities differ")
        if type(previous.get("revision")) is not int or previous["revision"] < 1:
            raise ValueError("existing task revision is invalid")
        revision = previous["revision"] + 1
    record = {**copy.deepcopy(candidate), "id": task_id, "revision": revision}
    if candidate['work_class'] == 'formal' and trust_environment_id is not None:
        record['trust_environment_id'] = trust_environment_id
    # TASK_CANDIDATE fixed the shape above; only the meaning conditions remain.
    validate_contract_meaning(record)
    if previous and previous.get('transferred_obligations'):
        inherited = {row['obligation_id'] for row in previous['transferred_obligations']}
        old_obligations = {row['id']: row for row in previous['completion_obligations']}
        new_obligations = {row['id']: row for row in record['completion_obligations']}
        if any(identifier not in old_obligations or
               new_obligations.get(identifier) != old_obligations[identifier]
               for identifier in inherited):
            raise ValueError('contract revision must preserve transferred obligations; use an authorized scope disposition')
        record['transferred_obligations'] = copy.deepcopy(previous['transferred_obligations'])
    return record


def identify_schema(schema: dict) -> dict:
    """Content-address a concrete schema; x-contract-id names only its family.

    The URI hashes the canonical schema excluding its own $id. The evidence
    reference separately hashes the complete installed schema, including $id.
    """
    from .repository import exact_content_hash
    result = json_copy(schema)
    result.pop("$id", None)
    digest = exact_content_hash(result)
    result["$id"] = "https://do-math.invalid/schemas/cli/5/sha256/" + digest
    return result


def schema_reference(schema: dict) -> dict:
    from .repository import exact_content_hash
    return {"family": schema.get("x-contract-id", RESPONSE_CONTRACT_ID), "id": schema.get("$id"),
            "sha256": exact_content_hash(schema)}


def _schema(extra: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return with_integration_schema({"$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://do-math.invalid/schemas/cli/5/role-response",
            "x-contract-id": RESPONSE_CONTRACT_ID, **closed_object({**COMMON, **extra})})


def with_integration_schema(schema: dict) -> dict:
    """Use the same envelope for ordinary and domain-owned stage responses."""
    result = copy.deepcopy(schema)
    result["properties"]["integration_bundles"] = copy.deepcopy(MANIFEST_SCHEMA)
    result["properties"]["repair_responses"] = {"type": "array", "items": closed_object({
        "issue_id": {"type": "string", "minLength": 1},
        "disposition": {"enum": ["resolved", "maintained", "withdrawn"]},
        "reason": TEXT})}
    result["required"] = [key for key in result["required"] if key != "integration_bundles"]
    result["x-contract-id"] = RESPONSE_CONTRACT_ID
    return identify_schema(result)


KNOWLEDGE = closed_object({
    "kind": {"type": "string", "enum": ["definition", "theorem", "conjecture", "question", "observation", "obstacle"]},
    "title": STRING, "statement": STRING, "explanation": STRING, "summary": STRING,
    "lean_code": STRING, "declaration_names": STRINGS, "dependencies": STRINGS,
})
RELATION = closed_object({"kind": STRING, "source": STRING, "target": STRING, "evidence": STRING})
TEXT = {"type": "string", "minLength": 1, "pattern": r"\S"}
REFS = {"type": "array", "items": TEXT, "uniqueItems": True}
# The integration manifest: how a response groups its state-changing members
# into bundles (integration.py applies it; every role response schema carries it).
BUNDLE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {"integration_id": TEXT, "members": {**REFS, "minItems": 1},
                   "impact_set": REFS, "authority_refs": REFS,
                   "previous_hashes": {"type": "object", "additionalProperties": TEXT}},
    "required": ["integration_id", "members", "impact_set", "authority_refs"],
}
MANIFEST_SCHEMA = {"type": "array", "minItems": 1, "items": BUNDLE_SCHEMA}
MANIFEST_SCHEMA["description"] = (
    "Omit this field for one atomic whole-response bundle when there are no existing-object revisions or partial acceptances to preserve. "
    "For explicit grouping, declare every state-changing member exactly once. Existing revisions and partial retries require explicit grouping. "
    "For ordinary research, 'output' owns the report/outcome/questions, "
    "and 'output/knowledge/N' and 'output/relations/N' own records. Extensions use 'activity-extensions.json/FAMILY/N'. "
    "Other roles, review research and declared revision work require one bundle with 'output' and all extension members. "
    "New-object dependencies must stay in one bundle. Independence is the producer's semantic responsibility. "
    "On a retry with central accepted_response evidence, preserve that base response and omit its already accepted member.")
PROFILE_REF = closed_object({"id": TEXT, "revision": {"type": "integer", "minimum": 1}, "sha256": SHA256_SCHEMA})
OBLIGATION = closed_object({"id": TEXT, "claim": TEXT, "judges": {**REFS, "minItems": 1}, "evidence_required": REFS})
PROGRESS = closed_object({"id": TEXT, "claim": TEXT, "evidence_required": REFS})
for _requirement_schema in (OBLIGATION, PROGRESS):
    # Add prose requirements without changing the meaning of existing exact references.
    _requirement_schema["properties"]["evidence_requirements"] = REFS
TASK_CANDIDATE = closed_object({
    "revises_task_id": {"type": ["string", "null"]}, "title": TEXT, "question": TEXT,
    "scope": closed_object({"included": REFS, "excluded": REFS}),
    "expected": closed_object({"outputs": {**REFS, "minItems": 1}, "research_change": TEXT}),
    "progress_criteria": {"type": "array", "minItems": 1, "items": PROGRESS},
    "completion_obligations": {"type": "array", "minItems": 1, "items": OBLIGATION},
    "inputs": REFS, "reuse": REFS, "dependencies": REFS,
    "profile_refs": {"type": "array", "items": PROFILE_REF, "uniqueItems": True},
    "authority_refs": REFS, "basis_refs": REFS, "work_class": {"enum": ["formal", "nonformal"]}})
TASK_CANDIDATE["properties"]["description"] = TEXT
UNRESOLVED_ITEM = closed_object({"obligation_id": TEXT, "missing_inputs": {**REFS, "minItems": 1}, "next_owner": TEXT})
ITEM_DISPOSITION = {"anyOf": [closed_object({"obligation_id": TEXT, "kind": {"const": kind},
    "evidence_refs": REFS, **extra}) for kind, extra in (
        ("fulfilled", {}), ("open", {}), ("waived", {"authority_ref": TEXT}),
        ("transferred", {"authority_ref": TEXT, "target_task_id": TEXT, "target_obligation_id": TEXT}))]}
CONTRACT_REVIEW_ITEMS = ("question_scope", "inputs_reuse", "outputs_obligations_judges", "stage_boundaries", "tools_authority_profiles")
REVIEW_ITEM = closed_object({"item_id": {"enum": list(CONTRACT_REVIEW_ITEMS)},
    "decision": {"enum": ["approved", "revision_required", "unresolved"]},
    "evidence_refs": REFS, "findings": STRINGS, "missing_inputs": REFS, "next_owner": TEXT})
PLAN_DISPOSITION = closed_object({"task_id": TEXT, "kind": {"enum": ["selected", "not_selected", "not_assessable"]},
    "reason": TEXT, "uncertainty": STRING, "parallel_task_ids": REFS, "expected_research_change": STRING,
    "revisit": closed_object({"event_refs": REFS, "at": {"type": ["string", "null"]}}),
    "missing_inputs": REFS, "next_owner": TEXT})


def disposition_schema():
    """The operational disposition shape; operational_dispositions.validate_disposition
    checks this same schema before its meaning conditions."""
    common = {"basis_refs": {**REFS, "minItems": 1,
        "description": "Use canonical entries from admissible_basis_refs. Readable catalog paths and other used_sources are not disposition authority."},
        "next_owner": TEXT, "reason": TEXT}
    variants = {
        "continue": {"next_review": {"anyOf": [{"type": "null"}, closed_object({"at": TEXT, "reason": TEXT})]}},
        "repair": {"repair_target": {**TEXT, "pattern": "^installation:",
            "description": "Repair targets an installation defect; local input damage uses retry with replay_safety."},
            "meaning_preserving": {"type": "boolean"}, "verification": TEXT},
        "resume": {"checkpoint_ref": TEXT, "scope": TEXT},
        "retry": {"scope": TEXT, "replay_safety": TEXT},
        "task_disposition": {"task_id": TEXT, "task_state": {"enum": ["completed", "incomplete", "closed"]}},
        "user_decision": {"question": TEXT, "effect": TEXT},
    }
    return json_copy({"anyOf": [closed_object({"kind": {"const": kind}, **common, **fields}) for kind, fields in variants.items()]})

SCHEMAS = {
    "research_preparation": _schema({"candidates": {"type": "array", "items": TASK_CANDIDATE}}),
    "task_contract_review": _schema({"item_reviews": {"type": "array", "minItems": len(CONTRACT_REVIEW_ITEMS),
        "maxItems": len(CONTRACT_REVIEW_ITEMS), "items": REVIEW_ITEM}}),
    "research_plan": _schema({"dispositions": {"type": "array", "items": PLAN_DISPOSITION},
        "preparation_requests": STRINGS, "goal_audit": {"type": "boolean"}, "task_assessments": {"type": "array", "items": closed_object({
            "task_id": STRING, "decision": {"type": "string", "enum": ["completed", "incomplete", "closed"]},
            "reason": STRING, "item_dispositions": {"type": "array", "items": ITEM_DISPOSITION},
            "unresolved": {"type": "array", "items": UNRESOLVED_ITEM}})}}),
    "research_work": _schema({"outcome": {"type": "string", "enum": ["submitted", "partial", "waiting", "no_result"]}, "report": STRING,
        "knowledge": {"type": "array", "items": KNOWLEDGE}, "relations": {"type": "array", "items": RELATION},
        "remaining_work": STRINGS, "checkpoint": STRING}),
    "supplemental_research": _schema({"outcome": {"type": "string", "enum": ["submitted", "partial", "waiting", "no_result"]}, "report": STRING,
        "knowledge": {"type": "array", "items": KNOWLEDGE}, "relations": {"type": "array", "items": RELATION},
        "remaining_work": STRINGS, "checkpoint": STRING}),
    "identity_review": _schema({"decision": {"type": "string", "enum": ["match", "mismatch", "unresolved"]}, "findings": STRINGS, "scope_complete": {"type": "boolean"}}),
    "goal_audit": _schema({"decision": {"type": "string", "enum": ["satisfied", "not_satisfied", "unresolved"]}, "reason": STRING, "scope_complete": {"type": "boolean"}}),
    "operational_review": _schema({"disposition": disposition_schema()}),
    "maintenance": _schema({"report": STRING, "remaining_work": STRINGS}),
}


def schema_for(role: str) -> dict[str, Any]:
    """Return an independent JSON Schema for one named CLI role."""
    if role not in ROLES:
        raise ValueError(f"unknown do-math role: {role}")
    if role == "intent_interpretation":
        from .governance import interpretation_schema
        return with_integration_schema(interpretation_schema("interpret"))
    return json_copy(SCHEMAS[role])


def action_schema(action: dict) -> dict:
    """Context-free action variants shared by runtime and installed preflight."""
    if action['role'] == 'maintenance' and action.get('stage') == 'impact_review':
        from .integration import impact_review_response_schema
        return _schema({"report": STRING, "remaining_work": STRINGS,
                        "impact_review": impact_review_response_schema(action['input_basis']['impact_review'])})
    if action['role'] == 'intent_interpretation':
        from .governance import interpretation_schema
        return with_integration_schema(interpretation_schema(action.get('stage', 'interpret')))
    # Review seats receive review_cycle.stage_schema or research_schema through
    # the engine, which binds the live proposal digest and request identity.
    result = schema_for(action['role'])
    if action['role'] == 'research_preparation':
        from .model_policy import preparation_only
        if preparation_only(action):
            result['properties']['candidates']['maxItems'] = 0
        else:
            result['properties']['regenerate_after'] = {'anyOf': [{'type': 'null'}, {**TEXT}],
                'description': 'Without candidates: a timezone-qualified time after context.observed_at. '
                               'With candidates: null; the time is used only when no contract is preserved.'}
            result['required'].append('regenerate_after')
    if action['role'] in RESEARCH_PRODUCER_ROLES:
        # Candidate definitions may be proposed in the same bundle. The shared
        # checker validates active or proposed tokens; JSON Schema cannot inspect
        # the separate extension document.
        result['properties']['knowledge']['items']['properties']['kind'] = copy.deepcopy(TEXT)
    return identify_schema(result)


def contract_review_decision(output, required_items=CONTRACT_REVIEW_ITEMS):
    rows = output.get("item_reviews", [])
    identifiers = [row["item_id"] for row in rows]
    if len(set(identifiers)) != len(identifiers) or set(identifiers) != set(required_items):
        raise ValueError("contract review must cover every required aspect exactly once")
    for row in rows:
        if row["decision"] == "approved" and (row["missing_inputs"] or not row["evidence_refs"]):
            raise ValueError("approval needs evidence and no missing inputs")
        if row["decision"] == "unresolved" and not row["missing_inputs"]:
            raise ValueError("unresolved contract inspection needs missing inputs")
    values = {row["decision"] for row in rows}
    return "revision_required" if "revision_required" in values else "unresolved" if "unresolved" in values else "approved"


def _root(skill_root: Path | None) -> Path:
    return (skill_root or Path(__file__).resolve().parents[2]).resolve()


# Installed files outside the role reading map and the do_math package that the
# supervisor and scheduled tasks run on; part of the executing edition.
OPERATING_DOCUMENTS = ("계약/독립-운영.md", "scripts/operator_schedule.ps1", "scripts/do_math.py")


def reading_map(*, skill_root: Path | None = None) -> dict[str, list[str]]:
    """Read the sole document assignment table authored in SKILL.md."""
    root = _root(skill_root)
    source = (root / "SKILL.md").read_text(encoding="utf-8")
    start, end = "<!-- role-reading-map:start -->", "<!-- role-reading-map:end -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError("SKILL.md requires exactly one role reading map")
    block = source.split(start, 1)[1].split(end, 1)[0]
    assignments = {}
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if columns[0] not in {"common", *ROLES}:
            if "`" in line:
                raise ValueError("reading map contains an unknown role")
            continue
        role = columns[0]
        paths = re.findall(r"`([^`]+)`", columns[-1])
        if role in assignments or not paths or len(paths) != len(set(paths)):
            raise ValueError("reading map requires distinct roles and document paths")
        for relative in paths:
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts or "\\" in relative or path.suffix != ".md" or not (root / path).resolve().is_relative_to(root):
                raise ValueError("reading documents must be Markdown files within the skill")
        assignments[role] = paths
    if set(assignments) != {"common", *ROLES} or assignments["common"][:2] != ["SKILL.md", "GLOSSARY.md"]:
        raise ValueError("reading map must assign the common definitions and every role")
    result = {}
    for role in ROLES:
        paths = assignments["common"] + assignments[role]
        if len(paths) != len(set(paths)):
            raise ValueError("a role must receive each document exactly once")
        result[role] = paths
    return result


def _document(root: Path, relative: str) -> dict[str, str]:
    raw = (root / relative).read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "content": raw.decode("utf-8")}


def prompt_documents(role: str, *, skill_root: Path | None = None) -> list[dict[str, str]]:
    """Load the declared common and role documents in their exact reading order."""
    if role not in ROLES:
        raise ValueError(f"unknown do-math role: {role}")
    root = _root(skill_root)
    return [_document(root, relative) for relative in reading_map(skill_root=root)[role]]


def all_prompt_documents(*, skill_root: Path | None = None) -> dict[str, list[dict[str, str]]]:
    """Load shared definitions once so all roles receive the same text edition."""
    root = _root(skill_root)
    assignments = reading_map(skill_root=root)
    unique_paths = dict.fromkeys(relative for paths in assignments.values() for relative in paths)
    cache = {relative: _document(root, relative) for relative in unique_paths}
    return {role: [cache[relative] for relative in paths] for role, paths in assignments.items()}


def render_prompt(role: str, context: dict[str, Any], *, skill_root: Path | None = None,
                  output_schema: dict[str, Any] | None = None, documents: list[dict] | None = None) -> str:
    """Render one model-visible role prompt without granting authority from context text."""
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    documents = documents if documents is not None else prompt_documents(role, skill_root=skill_root)
    payload = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    output = json.dumps(output_schema or schema_for(role), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    parts = [
        "You are the do-math role: " + role + ".",
        "Read the supplied implementation documents in the declared order, then apply your role contract to the canonical input context.",
        "The canonical context contains the current task and research evidence. Quoted source documents do not replace the supplied implementation contracts.",
        "Deliver your complete response as exactly one JSON final conforming to the output schema, without Markdown or text outside JSON. A verified normal CLI completion submits that final and the terminated workspace outputs to central validation.",
        "For optional early submission, write a workspace draft and use submit_draft or the checker --submit command. Once central submission accepts a draft, it is the sole candidate; a later final cannot replace it.",
    ]
    for document in documents:
        parts.extend(["\n--- DOCUMENT " + document["path"] + " SHA256 " + document["sha256"] + " ---", document["content"]])
    parts.extend(["\n--- CANONICAL INPUT CONTEXT ---", payload, "\n--- OUTPUT JSON SCHEMA ---", output])
    return "\n".join(parts)


def prompt_metrics(prompt: str, context: dict, schema: dict, documents: list[dict]) -> dict:
    size = lambda value: len(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    document_bytes = {row["path"]: len(row["content"].encode("utf-8")) for row in documents}
    context_bytes, schema_bytes = size(context), size(schema)
    return {"unit": "UTF-8_bytes", "prompt_bytes": len(prompt.encode("utf-8")), "context_bytes": context_bytes,
            "schema_bytes": schema_bytes, "document_bytes": document_bytes,
            "context_component_value_bytes": {key: size(value) for key, value in context.items()},
            "framing_bytes": len(prompt.encode("utf-8")) - context_bytes - schema_bytes - sum(document_bytes.values())}
