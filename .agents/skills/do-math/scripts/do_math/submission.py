"""Shared, read-only submission checks over the producer's fixed visible input.

These checks do not apply state, run Lean, contact a service, or certify meaning.
The receiving engine separately rechecks current authority and dependencies.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

import jsonschema
from .file_io import atomic_replace, console_python
from .values import json_copy

from . import knowledge_io, planning, review_cycle
from .context_store import collect_outputs, materialize_inputs, read_source, safe_path, is_excluded, read_stable, relative_path
from .state_contract import ARTIFACT_ROOT
from .ids import ULID_PATTERN
from .execution_profiles import PLANNING_ROLES, RESEARCH_PRODUCER_ROLES, review_research, task_research
from .external import prepare_operation, validate_operation
from .model_policy import ASSESSMENT_SCHEMA, assessment_key, validate_assessments, preparation_only
from .observations import read_checkpoint, checkpoint_value, CHECKPOINT_MAX_BYTES
from .values import reject_constant, unique_pairs
from .canonical import canonical_json, exact_content_hash
from .contracts import REFS, TEXT, closed_object
from .questions import QUESTION_OWNERS
from .task_contracts import CONTEXT_INPUT_REFS, TERMINAL_TASK_STATUSES
from . import integration


class SealedSubmissionError(ValueError):
    """A centrally accepted submission cannot be recovered from its receipt."""


def read_sealed_submission(execution: dict, snapshot: str, read_artifact, *, git_dir=None):
    """Read the exact bytes accepted by the central submission receipt.

    With the repository's ``git_dir``, a sealed row this process already matched
    (이음새-정본.md §3) is not hashed again.
    """
    from .repository import sealed_bytes
    from .git_store import GitStateStoreError
    identifier = execution.get("id", "<unknown>")
    intent = execution.get("submission_intent") or {}
    receipt = execution.get("submission_receipt") or {}
    if receipt.get("state") != "accepted" or receipt.get("execution_id") != identifier:
        raise SealedSubmissionError(f"execution {identifier}: accepted submission receipt is missing")
    recorded = {row.get("path"): row for row in
                receipt.get("payload", {}).get("submission_check", {}).get("artifacts", [])
                if isinstance(row, dict)}
    result = {}
    for field, name in (("output_ref", "output"), ("extensions_ref", "extensions"),
                        ("check_ref", "check")):
        path = intent.get(field)
        if not isinstance(path, str) or not path:
            raise SealedSubmissionError(f"execution {identifier}: missing sealed {field} at {path!r}")
        try:
            raw = read_artifact(path, snapshot)
        except (OSError, ValueError, KeyError, GitStateStoreError) as error:
            raise SealedSubmissionError(f"execution {identifier}: cannot read {field} at {path}: {error}") from error
        if not isinstance(raw, bytes):
            raise SealedSubmissionError(f"execution {identifier}: {field} at {path} is not bytes")
        expected = intent.get(name + "_sha256") if name != "check" else None
        entry = recorded.get(path)
        if not expected and entry:
            expected = entry.get("sha256")
        mismatch = SealedSubmissionError(f"execution {identifier}: sealed {field} hash differs at {path}")
        if not isinstance(expected, str):
            raise mismatch
        try:
            sealed_bytes(git_dir, path, expected, None, None, raw=raw, needed=False)
        except ValueError as error:
            raise mismatch from error
        if not entry or entry.get("sha256") != expected:
            raise SealedSubmissionError(f"execution {identifier}: {field} receipt differs at {path}")
        if entry and entry.get("bytes") != len(raw):
            raise SealedSubmissionError(f"execution {identifier}: sealed {field} size differs at {path}")
        try:
            result[name] = load_extensions(raw) if name == "extensions" else load_json(raw)
        except (ValueError, TypeError) as error:
            raise SealedSubmissionError(f"execution {identifier}: invalid sealed {field} JSON at {path}: {error}") from error
    check = result['check']
    _validated_check(canonical_json(check), check.get('id'))
    hashes = check.get('input_hashes', {})
    if (not isinstance(hashes, dict) or check.get('mode') != 'receiver' or check.get('execution_id') != identifier
            or check.get('schema_ref') != intent.get('schema_ref')
            or hashes.get('output') != exact_content_hash(result['output'])
            or hashes.get('extensions') != exact_content_hash(result['extensions'])):
        raise SealedSubmissionError(f"execution {identifier}: sealed check does not bind this candidate")
    if not captured_check(check):
        raise SealedSubmissionError(f"execution {identifier}: sealed check_ref at {intent['check_ref']} is not capture eligible")
    if not check['passed']:
        try:
            context, schema = issued_input(execution, snapshot, read_artifact)
            if (check['input_hashes'] != _check_hashes(result['output'], schema, context, result['extensions'])
                    or not capture_eligible(result['output'], result['extensions'], context, check['issues'])):
                raise ValueError('partial candidate differs from its fixed input or independent bundle structure')
        except (KeyError, TypeError, ValueError, OSError) as error:
            raise SealedSubmissionError(f'execution {identifier}: {error}') from error
    result["output_ref"] = intent["output_ref"]
    return result


# Parsed issued input files keyed by the SHA-256 of their bytes: the key names
# the exact content, so it holds for any repository or path (이음새-정본.md §3).
_ISSUED_INPUTS: dict = {}
_ISSUED_INPUT_LIMIT = 32


def issued_input(execution: dict, snapshot: str, read_artifact, *,
                 with_schema: bool = True) -> tuple[dict, dict | None]:
    """The fixed validation context and output schema this execution received.

    The engine writes both into the immutable input bundle (engine._input_artifacts);
    this is the one reader. The bytes are read on every call (the repository
    keeps recent artifact bytes); a file parsed before in this process is not
    parsed again, and callers get copies.
    """
    def issued(relative):
        raw = read_artifact(ARTIFACT_ROOT + execution["input_bundle"] + "/" + relative, snapshot)
        key = hashlib.sha256(raw).digest()
        value = _ISSUED_INPUTS.get(key)
        if value is None:
            value = load_json(raw)
            if len(_ISSUED_INPUTS) >= _ISSUED_INPUT_LIMIT:
                _ISSUED_INPUTS.pop(next(iter(_ISSUED_INPUTS)))
            _ISSUED_INPUTS[key] = value
        return deepcopy(value)
    return issued("input/submission/context.json"), issued("schema.json") if with_schema else None


# The contract of the nonauthoritative candidate preview response (preview_submission).
PREVIEW_CONTRACT_ID = "do-math-candidate-preview/5"

EXTENSION_ROLES = {
    "revision_requests": {*RESEARCH_PRODUCER_ROLES, *PLANNING_ROLES, "operational_review"}, "revision_resolutions": {*RESEARCH_PRODUCER_ROLES, "research_preparation"},
    "action_resolutions": {*PLANNING_ROLES, "operational_review"},
    "input_overflow_resolutions": {"research_plan"},
    "task_conditions": {"research_preparation"}, "contract_checks": {"research_preparation"}, "task_dispositions": PLANNING_ROLES,
    "research_insights": {"research_preparation", "research_plan", "research_work",
        "supplemental_research", "identity_review", "task_contract_review", "goal_audit",
        "operational_review", "intent_interpretation", "maintenance"},
    "external_requests": RESEARCH_PRODUCER_ROLES, "knowledge_changes": {*RESEARCH_PRODUCER_ROLES, "research_preparation"},
    "kind_definitions": {*RESEARCH_PRODUCER_ROLES, "research_preparation"},
    "knowledge_metadata": RESEARCH_PRODUCER_ROLES, "relations": RESEARCH_PRODUCER_ROLES, "observation_rules": RESEARCH_PRODUCER_ROLES,
    "research_requests": {"identity_review"}, "academic_resolutions": {"research_plan"},
    "model_assessments": PLANNING_ROLES, "model_assessment_deferrals": {"research_preparation"}, "queued_requests": {"research_plan"},
    "observation_rule_deferrals": {"research_preparation"},
}
for _family in ("question_routes", "question_resolutions"):
    EXTENSION_ROLES[_family] = set(EXTENSION_ROLES["research_insights"])


def extension_schema(action: dict) -> dict:
    """The installed schema describes only families available to this role."""
    from .contracts import PROFILE_REF
    kind = TEXT
    claim = closed_object({"kind": TEXT, "source": TEXT, "target": TEXT, "confirmed_scope": TEXT})
    relation = closed_object({"id": TEXT, "kind": TEXT, "source": TEXT, "target": TEXT, "evidence": TEXT,
        "evidence_refs": REFS, "formal_result_refs": REFS, "assessment_refs": REFS,
        "confirmed_scope": TEXT}, ["kind", "source", "target"])
    shapes = {
        "input_overflow_resolutions": closed_object({"action_id": TEXT, "profile_ref": PROFILE_REF, "reason": TEXT}),
        "task_conditions": closed_object({"task_id": TEXT, "task_title": TEXT, "dependencies": REFS,
            "knowledge_revision_targets": REFS,
            "occurrence_condition": {"type": "object"}, "observation_rules": {"type": "array"}}, []),
        "contract_checks": closed_object({"task_title": TEXT,
            "sibling_boundaries": {"type": "array", "items": closed_object({"task_id": TEXT, "revision": {"type": "integer", "minimum": 1},
                "boundary": TEXT, "independent_of_next_revision": {"type": "boolean"}})}}),
        "task_dispositions": closed_object({"task_id": TEXT, "disposition": {"const": "withdraw"}, "reason": TEXT}),
        "research_insights": closed_object({"kind": kind, "title": TEXT, "statement": TEXT, "summary": TEXT,
            "explanation": TEXT, "evidence_ids": REFS},
            ["kind", "title", "statement", "summary"]),
        "external_requests": closed_object({"id": TEXT, "request": {"type": "object"}, "grant_id": {"type": ["string", "null"]},
            "purpose": TEXT, "academic_effect_id": TEXT}, ["request", "purpose"]),
        "knowledge_changes": closed_object({"id": TEXT,
            "replacement_id": {"type": "string", "pattern": "^KN-" + ULID_PATTERN + "$"},
            "changes": {"type": "object", "minProperties": 1},
            "reason": TEXT, "impact_set": REFS}, ["id", "changes", "reason", "impact_set"]),
        "kind_definitions": closed_object({"family": {"enum": ["knowledge", "relation"]}, "token": TEXT,
            "meaning": TEXT, "constraints": closed_object({
                "mathematical_claim": {"type": "boolean"}, "requires_evidence": {"type": "boolean"},
                "requires_formal_results": {"type": "boolean"}, "requires_assessments": {"type": "boolean"},
                "allowed_epistemic_statuses": {**REFS, "minItems": 1},
                "required_fields": {**REFS, "minItems": 1}}, [])}),
        "knowledge_metadata": closed_object({"title": TEXT, "relation_claim": claim, "confirmed_scope": TEXT,
            "epistemic_status": TEXT, "selection_relevance": TEXT,
            "uncertainty_assessment": {"type": ["string", "object"]}}, ["title"]),
        "relations": relation,
        "observation_rules": {"type": "object"},
        "research_requests": review_cycle.research_request_schema(),
        "academic_resolutions": closed_object({"id": TEXT, "decision": {"enum": ["resolved", "unresolved"]},
            "evidence": TEXT, "evidence_refs": {**REFS, "minItems": 1, "uniqueItems": True}}),
        "model_assessments": closed_object({assessment_key(action): TEXT,
            **ASSESSMENT_SCHEMA["properties"]}),
        "model_assessment_deferrals": closed_object({"task_id": TEXT, "reason": TEXT}),
        "observation_rule_deferrals": closed_object({'task_id': TEXT, 'reason': TEXT,
            'missing_inputs': {**REFS, 'minItems': 1},
            'next_owner': {'enum': ['user', 'research_preparation', 'research_plan', 'maintenance']}}),
        "queued_requests": closed_object({"request_id": TEXT, "decision": {"enum": ["keep", "cancel"]}, "reason": TEXT}),
        "revision_requests": closed_object({"record_ids": {**REFS, "minItems": 1}, "reason": TEXT}),
        "revision_resolutions": closed_object({"record_id": TEXT, "disposition": {"enum": ["revised", "unchanged", "deferred", "delegated"]},
            "reason": TEXT, "task_title": TEXT}, ["record_id", "disposition", "reason"]),
        "question_routes": closed_object({"question_index": {"type": "integer", "minimum": 0},
            "owner": {"enum": sorted(QUESTION_OWNERS)}, "target_ids": REFS, "reason": TEXT,
            "blocks": {"type": "boolean"}}, ["question_index", "owner", "target_ids", "reason"]),
        "question_resolutions": closed_object({"question_id": TEXT, "disposition": {"enum": ["resolved", "superseded"]},
            "evidence_refs": {**REFS, "minItems": 1}, "reason": TEXT}),
        "action_resolutions": closed_object({"action_id": TEXT, "evidence_execution_id": TEXT, "reason": TEXT}),
    }
    allowed = {name for name, roles in EXTENSION_ROLES.items() if action["role"] in roles}
    if preparation_only(action):
        allowed &= {"model_assessments", "model_assessment_deferrals", 'task_conditions', 'observation_rule_deferrals'}
        if 'observation_rule_targets' in action:
            shapes['task_conditions'] = closed_object({'task_id': TEXT, 'observation_rules': {'type': 'array', 'minItems': 1}})
        else:
            allowed -= {'task_conditions', 'observation_rule_deferrals'}
    else:
        allowed.discard("model_assessment_deferrals")
        allowed.discard('observation_rule_deferrals')
    if review_research(action):
        allowed.clear()
    if not action.get("review_cycle_id"):
        allowed.discard("research_requests")
    return json_copy(closed_object({name: {"type": "array", "items": shapes[name]} for name in sorted(allowed)}, []))


def load_json(raw: bytes):
    value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    canonical_json(value)
    return value


def load_extensions(raw: bytes):
    value = load_json(raw)
    if isinstance(value, dict):
        return {key: items for key, items in value.items() if items != [] or key not in EXTENSION_ROLES}
    return value


def read_extensions(workspace: Path) -> dict:
    path = safe_path(workspace, "activity-extensions.json")
    return load_extensions(path.read_bytes()) if path.exists() else {}


def reported_references(output: dict, extensions: dict, context: dict | None = None) -> list[str]:
    """Read explicit dependency fields, never historical records or free prose."""
    from .relation_refs import relation_references
    refs = list(output.get("used_sources", []))
    for item in output.get("knowledge", []):
        refs.extend(item.get("dependencies", []))
    for candidate in output.get("candidates", []):
        refs.extend([candidate.get("revises_task_id"), *candidate.get("inputs", []), *candidate.get("reuse", [])])
    for row in [*output.get("dispositions", []), *output.get("task_assessments", []), *extensions.get("task_dispositions", [])]:
        refs.append(row.get("task_id"))
    for row in output.get("candidates", []):
        refs.extend([*row.get("dependencies", []), *row.get("authority_refs", []), *row.get("basis_refs", [])])
    refs.extend(integration.reference_ids(output.get("task_assessments", [])))
    refs.extend(integration.reference_ids(output.get("item_reviews", [])))
    refs.extend(output.get("disposition", {}).get("basis_refs", []))
    for row in extensions.get("task_conditions", []):
        refs.extend(row.get("dependencies", []))
        refs.extend(row.get("knowledge_revision_targets", []))
        refs.extend(planning.condition_refs(row.get("occurrence_condition")))
    for row in extensions.get("revision_requests", []):
        refs.extend(row.get("record_ids", []))
    for row in extensions.get("revision_resolutions", []):
        refs.append(row.get("record_id"))
    if context:
        refs.extend(context.get("action", {}).get("revision_targets", {}))
    for relation in [*output.get("relations", []), *extensions.get("relations", [])]:
        refs.extend(sorted(relation_references(relation)))
    for entry in extensions.get("research_insights", []):
        refs.extend(entry.get("evidence_ids", []))
    for entry in extensions.get("knowledge_changes", []):
        refs.append(entry.get("id"))
        refs.extend(entry.get("changes", {}).get("dependencies", []))
        refs.extend(entry.get("changes", {}).get("source_refs", []))
        refs.extend(entry.get("impact_set", []))
    for entry in extensions.get("knowledge_metadata", []):
        refs.extend(sorted(relation_references(entry.get('relation_claim') or {})))
    for entry in extensions.get("research_requests", []):
        refs.extend(entry.get("source_refs", []))
    aliases = reference_aliases(context or {})
    return list(dict.fromkeys(normalize_reference(ref, aliases) for ref in refs if isinstance(ref, str)))


def reference_aliases(context: dict) -> dict:
    aliases = {row["path"]: row["id"] for row in context.get("knowledge_catalog", []) if row.get("path")}
    for row in context.get("sources", []):
        for value in (row.get("id"), row.get("path"), row.get("local_path"), row["name"], "source:" + row["name"]):
            if value:
                aliases[value] = row["name"]
    return aliases


def normalize_reference(reference: str, aliases: dict) -> str:
    # Historical artifact paths are not aliases of the current record.
    return aliases.get(reference.removeprefix("workspace:"), reference)


def supplied_locators(context):
    """The file locators (paths and artifact references) the fixed input shows."""
    locators = set()
    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "reference_catalog":
                    continue  # The projection cannot grant itself authority.
                if key in {"path", "local_path", "artifact_ref", "ref", "source_ref"} and isinstance(child, str):
                    locators.add(child)
                elif isinstance(child, (dict, list)):
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(context)
    return locators


def reference_catalog(context: dict, workspace: Path) -> list[dict]:
    """Project the same reference checker used by producers and receivers.

    The catalog lists the references the input shows; the further records of the input
    snapshot the role may cite are listed once, in its record_index.
    """
    known, locators = _reference_index(context, records=False)
    aliases = reference_aliases(context)
    candidates = known | locators | set(aliases)
    if context.get("proposal") or context.get("role_review", {}).get("proposal"):
        candidates.add("proposal")
    candidates.update("issue:" + key for key in context.get("role_review", {}).get("issues", {}))
    fixed_research = context.get("action", {}).get("role") == "supplemental_research" and context.get("review_research")
    if fixed_research:
        candidates = {row["ref"] for row in context["review_research"].get("sources", [])}
    records = {row["id"] for row in context.get("knowledge_catalog", [])}
    records.update(row["id"] for row in context.get("tasks", []))
    records.update(row["id"] for row in context.get("task_catalog", []))
    if context.get("task"):
        records.add(context["task"]["id"])
    source_names = {row["name"] for row in context.get("sources", [])}
    rows = []
    for ref in sorted(candidates):
        try:
            _validate_reference(ref, context, workspace, known=known, locators=locators)
        except (ValueError, OSError):
            continue
        identity = aliases.get(ref.removeprefix("workspace:"), ref)
        current = identity in records or identity in source_names
        kind = ("source" if identity in source_names else "record" if identity in records else
                "historical_artifact" if ref.startswith(ARTIFACT_ROOT) else "supplied_reference")
        rows.append({"value": ref, "canonical_ref": identity, "kind": kind,
                     "basis": "current_content" if current else "fixed_input_or_historical_evidence"})
    return rows


RECORD_ID = re.compile(r"(?<![0-9A-Za-z])(?:TK|KN)-[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*")


def contract_check_errors(item: dict, entry: dict, dependencies: list[str], tasks: dict, known: set, revising: set) -> list[tuple[str, str]]:
    """The part of contract review that the input state decides, run by the producer before submission.

    A cited record must exist, and a cited sibling's boundary must be read at its
    current revision and must not silently depend on a sibling under revision.
    Symbol meanings and outcome branches stay with the author's self-review and
    the independent contract review; no declaration of them is compared here.
    Each finding is (rule_id, message); the rule identifies the kind of defect,
    so distinct defects of one candidate remain distinct issues.
    """
    text = "\n".join([item["title"], item["question"], *item["scope"]["included"], *item["scope"]["excluded"],
        *item["expected"]["outputs"], item["expected"]["research_change"],
        *(row["claim"] for row in item["completion_obligations"]), *(row["claim"] for row in item["progress_criteria"])])
    errors = []
    cited = set(RECORD_ID.findall(text)) - {item["revises_task_id"]}
    errors += [("contract_check.cited_record", "cited record is neither in the supplied input nor in its record_index: " + ref)
               for ref in sorted(cited - known - set(tasks))]
    declared = {row["task_id"]: row for row in entry["sibling_boundaries"]}
    if len(declared) != len(entry["sibling_boundaries"]):
        errors.append(("contract_check.sibling_boundary", "sibling boundaries must name distinct tasks"))
    siblings = {ref for ref in cited if ref.startswith("TK-")}
    errors += [("contract_check.sibling_boundary", "cited sibling contract has no declared boundary: " + ref)
               for ref in sorted(siblings - set(declared))]
    for ref, row in declared.items():
        sibling = tasks.get(ref)
        if sibling is None:
            errors.append(("contract_check.sibling_boundary", "sibling boundary names a task outside the supplied input: " + ref))
        elif row["revision"] != sibling.get("revision"):
            errors.append(("contract_check.sibling_revision",
                           f"sibling boundary was not read from the current revision {sibling.get('revision')} of {ref}"))
        elif ((planning.revision_requested(sibling) or ref in revising)
              and not row["independent_of_next_revision"] and ref not in dependencies):
            errors.append(("contract_check.sibling_under_revision",
                           "sibling contract is under revision: state a boundary that its next revision cannot move, "
                           "or wait for it through task_conditions dependencies: " + ref))
    return errors


def _issue(path, message, rule_id=None):
    # Array indices identify the affected item; the rule remains stable across
    # examples and retries. No failure identity depends on human error wording.
    rule_id = rule_id or "submission." + re.sub(r"/\d+(?=/|$)", "/*", path).replace("/", ".")
    return integration.issue(rule_id, path, message)


def _schema_issues(value, schema, path):
    issues = {}
    for error in jsonschema.Draft202012Validator(schema).iter_errors(value):
        coordinate = path + "".join("/" + str(part) for part in error.absolute_path)
        if error.validator == "required" and isinstance(error.instance, dict):
            missing = [key for key in error.validator_value if key not in error.instance]
            rows = [_issue(coordinate + "/" + key, "required property is missing", "schema.required") for key in missing]
        else:
            rows = [_issue(coordinate, error.message, "schema." + str(error.validator))]
        for row in rows:
            issues[row["issue_id"]] = row
    return list(issues.values())


def _explicit_reference_fields(value, path="output"):
    keys = {"evidence_refs", "evidence_required", "authority_ref", "authority_refs", "basis_refs", "decision_refs"}
    if isinstance(value, dict):
        for key, child in value.items():
            coordinate = path + "/" + key
            if key in keys:
                for index, ref in enumerate(child if isinstance(child, list) else [child]):
                    if isinstance(ref, str):
                        yield coordinate + ("/" + str(index) if isinstance(child, list) else ""), ref
            elif key not in {"integration_bundles", "repair_responses"}:
                yield from _explicit_reference_fields(child, coordinate)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _explicit_reference_fields(child, path + "/" + str(index))


def _intent_import_issues(output, context, *, clock):
    """Run the receiver's import-unit check and governance record check on the fixed input.

    Coverage, identity, question and payload coordinates use governance.validate_import_units
    over the supplied records; an owner's live-state candidate check stays with the receiver.
    """
    from .governance import GOVERNANCE_KINDS, validate_governance_record, validate_import_units
    instance = {"id": context.get("instance_id"),
                "decisions": {row["id"]: row for row in context.get("decisions", [])},
                "governance": {row["id"]: row for row in context.get("governance_records", [])},
                "grants": {row["id"]: row for row in context.get("grants", [])}}
    runtime = {"tasks": {row["id"]: row for row in context.get("tasks", [])}}
    issues = []
    try:
        validate_import_units(instance, runtime, context.get("original_source"), output,
                              owner_kinds={row["owner_kind"] for row in context.get("import_consumers", [])}, clock=clock)
    except (ValueError, TypeError, KeyError) as error:
        issues.append(_issue("output/import_units", str(error), "intent.import_units"))
    for index, unit in enumerate(output["import_units"]):
        if unit["owner_kind"] in GOVERNANCE_KINDS and unit["payload"]:
            try:
                validate_governance_record(unit["payload"].get("record"))
            except (ValueError, TypeError, KeyError) as error:
                issues.append(_issue(f"output/import_units/{index}/payload/record", str(error), "intent.governance_record"))
    return issues


def supplied_reference_ids(context):
    """The record IDs the fixed input shows in its context values."""
    ids = {row["id"] for row in context.get("knowledge_catalog", [])}
    for row in context.get("knowledge_catalog", []):
        if row.get("formal_result_id"):
            ids.add(row["formal_result_id"])
        ids.update(row.get("identity_assessment_ids", []))
    governance = context.get("governance", {})
    if isinstance(governance.get("charter"), dict) and governance["charter"].get("id"):
        ids.add(governance["charter"]["id"])
    for family in ("policy_records", "research_context", "additional_audits"):
        ids.update(row["id"] for row in governance.get(family, []) if row.get("id"))
    if isinstance(context.get("instance_id"), str):
        ids.add(context["instance_id"])
    ids.update(row["id"] for row in context.get("tasks", []))
    ids.update(row["id"] for row in context.get("task_catalog", []))
    ids.update(row['id'] for row in context.get('review_followups', []))
    ids.update(row["id"] for row in context.get("sources", []) if row.get("id"))
    for source in context.get("sources", []):
        ids.update((source["name"], source["path"], "source:" + source["name"]))
    ids.update(row["id"] for row in context.get("grants", []))
    for key in ("user_inputs", "events", "external_operations", "external_rejections", "question_links", "decisions",
                "governance_records", "delegations", "goal_judgments"):
        ids.update(row["id"] for row in context.get(key, []) if row.get("id"))
    ids.update(row['resolution']['id'] for row in context.get('question_links', []) if isinstance(row.get('resolution'), dict) and row['resolution'].get('id'))
    for key in ("recent_history", "preparation_history"):
        ids.update(row["execution_id"] for row in context.get(key, []) if row.get("execution_id"))
    for task in context.get("tasks", []):
        ids.update(row["execution_id"] for row in task.get("results", []) if row.get("execution_id"))
        ids.update(row["execution_id"] for row in task.get("reviews", []) if row.get("execution_id"))
    for task in context.get("task_catalog", []):
        ids.update(task.get("result_execution_ids", []))
    for key in ("task", "user_request", "original_source", "execution_to_review", "previous_execution"):
        if isinstance(context.get(key), dict) and context[key].get("id"):
            ids.add(context[key]["id"])
    # An operational review's admissible_basis_refs are the evidence its input supplies: its
    # target, the target's observation facts and self-check obligations, successors and
    # preserved results (operational_dispositions). Like every supplied record they are
    # citable and readable.
    ids.update(context.get("admissible_basis_refs", []))
    return ids


def record_index_ids(context):
    """IDs of the input snapshot records the role may read and cite (its record_index)."""
    return {identifier for ids in context.get("record_index", {}).values() for identifier in ids}


def _reference_index(context, *, records=True):
    """Citable IDs and locators of one fixed input; workspace files are still checked per reference.

    A reference is citable when the input shows it (supplied_reference_ids, which also counts an
    operational review's admissible_basis_refs, so the disposition check and this general
    reference check admit the same set) or, with ``records``, when it names a record of the
    input snapshot in the record_index; field rules apply separately.
    """
    known = (supplied_reference_ids(context) | set(context.get("available_input_refs", []))
             | CONTEXT_INPUT_REFS | (record_index_ids(context) if records else set()))
    locators = supplied_locators(context)
    for source in context.get("sources", []):
        locators.update((source["name"], "source:" + source["name"]))
    return known, locators


def validate_reference(reference: str, context: dict, workspace: Path,
                       *, candidate_files: dict[str, bytes] | None = None) -> None:
    """A reference must identify supplied material or an output that is kept."""
    known, locators = _reference_index(context)
    return _validate_reference(reference, context, workspace, known=known, locators=locators,
                               candidate_files=candidate_files)


def _validate_reference(reference, context, workspace, *, known, locators, candidate_files=None):
    # A catalog or one payload check reuses these indexes only within one
    # unchanged input. Public validation always derives authority from the supplied context anew.
    if reference in known:
        return
    proposal = context.get("proposal") or context.get("role_review", {}).get("proposal")
    if (reference == "proposal" or reference.startswith("proposal:")) and proposal is not None:
        review_cycle.proposal_value(proposal, reference)
        return
    if reference.startswith("issue:") and reference.removeprefix("issue:") in context.get("role_review", {}).get("issues", {}):
        return
    # Historical artifact locators identify their original bytes, not the
    # newest knowledge revision with a similar ID.
    if reference in locators:
        return
    name = reference.removeprefix("workspace:")
    path = safe_path(workspace, name)
    relative = Path(name)
    if relative.parts[0] != "input" and is_excluded(relative):
        raise ValueError("reference must identify supplied input, a record of the input snapshot or a preserved workspace file: " + reference +
                         "; use an exact reference_catalog value, a record_index ID or workspace:<preserved-file>")
    exists = ((name in locators and path.is_file()) if relative.parts[0] == "input"
              else path.is_file() if candidate_files is None else name in candidate_files)
    if not exists:
        raise ValueError("reference must identify supplied input, a record of the input snapshot or a preserved workspace file: " + reference +
                         "; use an exact reference_catalog value, a record_index ID or workspace:<preserved-file>")


def supplied_record_ids(context: dict, record_ids) -> list[str]:
    """Records of ``record_ids`` this fixed input shows or lists in its record_index.

    prepare_role_input stores the result as context['supplied_record_ids']; task inputs
    and completion evidence may cite them (common execution contract).
    """
    return sorted((supplied_reference_ids(context) | record_index_ids(context)) & set(record_ids))


# A failed action a later accepted execution may resolve, and the judgment scope it must share.
RESOLVABLE_WAITS = frozenset({"output_validation", "execution_failure"})
_JUDGMENT_SCOPE = ("role", "stage", "slot", "round", "review_cycle_id", "assessment_targets",
                   "observation_rule_targets", "live")


def blocked_action_row(action_id: str, entry: dict) -> dict:
    """One waiting action as roles receive it: its wait and the scope a resolution must share."""
    action = entry.get("action", {})
    return {"action_id": action_id, "target": action.get("target"), "kind": entry.get("kind"),
            "reason": entry.get("reason"), "execution_id": entry.get("execution_id"),
            **{key: deepcopy(action[key]) for key in (*_JUDGMENT_SCOPE, "revision_targets") if key in action}}


def action_resolution_errors(blocked: dict, evidence_action: dict | None) -> list[str]:
    """What the fixed failed action and the evidence's own action decide about a resolution.

    The producer passes its own action for `current` evidence; the receiver passes the
    evidence execution's action and separately checks acceptance and current premises.
    """
    if blocked.get("kind") not in RESOLVABLE_WAITS:
        return ["only an output_validation or execution_failure wait can be resolved; this action waits for "
                + str(blocked.get("kind"))]
    if evidence_action is None:
        return []
    same_target = (blocked.get("target") == evidence_action.get("target")
                   or blocked.get("target") in evidence_action.get("revision_targets", {}))
    if not same_target or any(blocked.get(key) != evidence_action.get(key) for key in _JUDGMENT_SCOPE):
        return ["resolution evidence must be an execution of the same judgment scope as the failed action"]
    return []


def judgment_families(context: dict) -> dict:
    """Record families of the specialist judgments visible in this input's catalogs."""
    families = {row["formal_result_id"]: "formal-result"
                for row in context.get("knowledge_catalog", []) if row.get("formal_result_id")}
    families.update((identifier, "identity-assessment") for row in context.get("knowledge_catalog", [])
                    for identifier in row.get("identity_assessment_ids", []))
    families.update((row["id"], "goal-judgment") for row in context.get("goal_judgments", []) if row.get("id"))
    return families


def validate_research_reference(reference: str, context: dict) -> None:
    """Producer view of review_cycle.classify_research_source over the seat's fixed input."""
    role_review = context.get("role_review", {})
    review_cycle.classify_research_source(reference,
        proposal=context.get("proposal") or role_review.get("proposal"),
        issues=role_review.get("issues", {}),
        own_source_refs={row["ref"] for row in role_review.get("source_refs", [])},
        sources=context.get("sources", []),
        knowledge_ids={row["id"] for row in context.get("knowledge_catalog", [])})


def fixed_research_reference_path(reference, source_refs):
    """Return a collectable workspace coordinate, or None for a fixed source."""
    if reference in source_refs:
        return None
    if not isinstance(reference, str) or not reference.startswith('workspace:'):
        raise ValueError('investigation evidence is outside its fixed source set')
    name = reference.removeprefix('workspace:')
    relative = relative_path(name)
    if is_excluded(relative):
        raise ValueError('evidence must be a collectable workspace file: ' + name)
    return name


def _payload_issues(output: dict, schema: dict, context: dict, extensions: dict, workspace: Path,
                    *, owns_response=True, candidate_files: dict[str, bytes] | None = None, clock) -> list[dict]:
    """Check producer-visible conditions; application-time state stays separate."""
    issues = _schema_issues(output, schema, "output")
    action = context["action"]
    extension_errors = _schema_issues(extensions, extension_schema(action), "activity-extensions.json")
    if issues or extension_errors:
        return issues + extension_errors
    from .revisions import submission_errors, dependency_cycles
    issues.extend(submission_errors(output, extensions, context))
    from .questions import validate_extensions
    issues.extend(validate_extensions(output, extensions, context))

    def check(path, operation, rule_id=None):
        try:
            operation()
        except (ValueError, TypeError, KeyError, OSError) as error:
            issues.append(_issue(path, str(error), rule_id))

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    # The time is consumed only when an accepted output preserved no contract,
    # which a preparation proposing candidates never is (revisions.record_execution_outcome).
    if (action['role'] == 'research_preparation' and 'regenerate_after' in schema.get('properties', {})
            and not output['candidates']):
        from .revisions import regeneration_time_valid
        check('output/regenerate_after', lambda: require(
            output['regenerate_after'] is not None
            and regeneration_time_valid(output['regenerate_after'], context['observed_at']),
            'an output without candidates needs regenerate_after after the machine observed_at'),
            'submission.regeneration_time')

    if action["role"] == "maintenance" and action.get("stage") == "impact_review":
        check("output/impact_review", lambda: integration.validate_impact_review_response(action["input_basis"]["impact_review"], output),
              "submission.impact_review")
        check("activity-extensions.json", lambda: require(not any(extensions.values()),
              "a designated impact judgment cannot also author research mutations"), "submission.impact_review")

    # One fixed input: build its reference index once, not once per reference.
    reference_known, reference_locators = _reference_index(context)

    def supplied(reference):
        _validate_reference(reference, context, workspace, known=reference_known,
                            locators=reference_locators, candidate_files=candidate_files)

    for coordinate, reference in _explicit_reference_fields(output):
        check(coordinate, lambda reference=reference: supplied(reference), "submission.explicit_reference")
    from .task_scope import require_evidence_refs, result_ids
    records = set(context.get("supplied_record_ids", []))
    context_tasks = {row["id"]: row for row in context.get("tasks", [])}
    returned = set().union(*(result_ids(task) for task in context_tasks.values()))
    for index, item in enumerate(output.get("candidates", [])):
        for family in ("progress_criteria", "completion_obligations"):
            for number, row in enumerate(item[family]):
                check(f"output/candidates/{index}/{family}/{number}/evidence_required",
                      lambda row=row: require_evidence_refs(row["evidence_required"], records | returned),
                      "submission.assessment_reference")
    for index, assessment in enumerate(output.get("task_assessments", [])):
        task = context_tasks.get(assessment["task_id"]) or (
            context["task"] if (context.get("task") or {}).get("id") == assessment["task_id"] else None)
        admissible = records | (result_ids(task) if task else set())
        for number, row in enumerate(assessment["item_dispositions"]):
            check(f"output/task_assessments/{index}/item_dispositions/{number}/evidence_refs",
                  lambda row=row, admissible=admissible: require_evidence_refs(row["evidence_refs"], admissible),
                  "submission.assessment_reference")
        if task is not None:
            from .task_contracts import judge_coverage_errors
            families = judgment_families(context)
            for message in judge_coverage_errors(action["role"], context.get("execution_id"), task, assessment, families):
                issues.append(_issue(f"output/task_assessments/{index}/item_dispositions", message,
                                     "submission.judge_coverage"))
            from .academic import criteria_evidence_errors
            for message in criteria_evidence_errors(task, assessment):
                issues.append(_issue(f"output/task_assessments/{index}/item_dispositions", message,
                                     "submission.academic_criteria_evidence"))
    from .academic import EVIDENCE_FAMILIES, resolve_evidence_reference
    evidence_records = {family: {identifier: identifier for identifier in
        context.get("record_index", {}).get("/".join(planning.RECORD_FAMILIES[family]), [])}
        for family in EVIDENCE_FAMILIES}

    def academic_evidence(reference):
        supplied(reference)
        resolve_evidence_reference(reference, evidence_records,
            lambda ref: True if ref.startswith(ARTIFACT_ROOT) and ref in reference_locators else None)

    for index, row in enumerate(extensions.get("academic_resolutions", [])):
        for number, reference in enumerate(row["evidence_refs"]):
            check(f"activity-extensions.json/academic_resolutions/{index}/evidence_refs/{number}",
                  lambda reference=reference: academic_evidence(reference), "submission.academic_evidence")
    if action["role"] == "intent_interpretation" and action.get("stage", "interpret") == "interpret":
        issues.extend(_intent_import_issues(output, context, clock=clock))

    known = supplied_reference_ids(context) | record_index_ids(context)
    blocked = {row["action_id"]: row for row in context.get("blocked_actions", [])}
    resolutions = extensions.get("action_resolutions", [])
    check("activity-extensions.json/action_resolutions", lambda: require(
        len({row["action_id"] for row in resolutions}) == len(resolutions), "failed action claims must be distinct"))
    for index, row in enumerate(resolutions):
        def resolution(row=row):
            current = row["evidence_execution_id"] == "current"
            require(row["action_id"] in blocked and (current or row["evidence_execution_id"] in known),
                    "action resolution requires a supplied failed action and current or supplied execution evidence")
            errors = action_resolution_errors(blocked[row["action_id"]], action if current else None)
            require(not errors, "; ".join(errors))
        check(f"activity-extensions.json/action_resolutions/{index}", resolution)
    for index, row in enumerate(extensions.get("question_resolutions", [])):
        for ref in row["evidence_refs"]:
            check(f"activity-extensions.json/question_resolutions/{index}/evidence_refs", lambda ref=ref: supplied(ref))
    knowledge_ids = {row["id"] for row in context.get("knowledge_catalog", [])}
    tasks = {row["id"]: row for row in context.get("tasks", [])}
    if isinstance(context.get("task"), dict):
        tasks[context["task"]["id"]] = context["task"]
    new_knowledge = {item["title"] for item in output.get("knowledge", [])}
    new_tasks = {item["title"] for item in output.get("candidates", [])}
    if not review_research(action):
        for index, ref in enumerate(output.get("used_sources", [])):
            check(f"output/used_sources/{index}", lambda ref=ref: supplied(ref))
    for label, rows in (("knowledge", output.get("knowledge", [])), ("candidates", output.get("candidates", []))):
        check("output/" + label, lambda rows=rows: require(len({x["title"] for x in rows}) == len(rows), "titles must be unique within one output"))

    if action["role"] == "research_preparation":
        for index, item in enumerate(output["candidates"]):
            def candidate(item=item):
                from .contracts import task_candidate_record
                prior = tasks.get(item.get("revises_task_id"))
                # A preview-only identifier; ENGINE allocates the durable ID.
                task_candidate_record(item, task_id=item.get("revises_task_id") or "TK-00000000000000000000000000",
                                      previous=prior)
                require(item['title'] not in tasks, 'candidate title cannot collide with an existing task ID')
                if 'execution_profiles' in context:
                    from .execution_profiles import match_profile_ref
                    from .observations import observation_settings_errors
                    registry = {p['id']: p for p in context['execution_profiles']}
                    for reference in item['profile_refs']:
                        errors = observation_settings_errors(match_profile_ref(registry, reference))
                        require(not errors, 'candidate requires prepared observation profiles: ' + json.dumps(errors))
                from .task_contracts import preparation_input_refs, unsupplied_task_inputs
                missing = unsupplied_task_inputs([*item["inputs"], *item["reuse"]], preparation_input_refs(context, new_tasks),
                    admit_named_sources=True)
                require(not missing, "task inputs must name available_input_refs, supplied records or titles "
                                     "prepared in this output; unknown: " + ", ".join(missing))
                if item["revises_task_id"]:
                    old = tasks.get(item["revises_task_id"])
                    require(bool(old) and old.get("status") not in TERMINAL_TASK_STATUSES | {"active"}, "revision requires an existing unfinished task")
                    require(not old.get("academic_requirement_id"), "user academic requirements have a separate decision path")
            check(f"output/candidates/{index}", candidate)
            from .observations import validate_task_rules
            condition = next((row for row in extensions.get('task_conditions', [])
                if row.get('task_title') == item['title'] or
                   item.get('revises_task_id') and row.get('task_id') == item['revises_task_id']), {})
            prior = tasks.get(item.get('revises_task_id'), {})
            rules = condition.get('observation_rules', prior.get('initial_observation_rules', []))
            check(f'output/candidates/{index}/initial_observation_rules', lambda rules=rules: validate_task_rules(rules))
        if not preparation_only(action):
            entries = extensions.get("contract_checks", [])
            titles = [entry["task_title"] for entry in entries]
            expected = [item["title"] for item in output["candidates"]]
            check("activity-extensions.json/contract_checks", lambda: require(
                len(titles) == len(set(titles)) and set(titles) == set(expected),
                "contract self-check coverage: every candidate needs exactly one entry; missing " +
                json.dumps(sorted(set(expected) - set(titles)), ensure_ascii=False)), "contract_check.coverage")
            revising = {target for row in context.get("pending_revisions", []) if row["action"].get("id") != action.get("id")
                        for target in planning.action_write_ids(row['action'])}
            # The checker context holds every current task, siblings outside the comparison
            # population included (context_store.prepare_role_input), so boundaries are read there.
            for index, entry in enumerate(entries):
                item = next((x for x in output["candidates"] if x["title"] == entry["task_title"]), None)
                if item is None:
                    continue
                from .task_contracts import prepared_dependencies
                condition = next((row for row in extensions.get('task_conditions', [])
                    if row.get('task_title') == item['title'] or
                       item.get('revises_task_id') and row.get('task_id') == item['revises_task_id']), {})
                dependencies = prepared_dependencies(item, condition)
                for rule_id, message in contract_check_errors(item, entry, dependencies, tasks, known, revising):
                    issues.append(_issue(f"activity-extensions.json/contract_checks/{index}", message, rule_id))
    if action["role"] == "research_plan":
        check("output", lambda: planning.validate_plan_submission(output, tasks, context.get("ready_task_ids", [])))
    if action["role"] == "task_contract_review":
        from .contracts import contract_review_decision
        check("output/item_reviews", lambda: contract_review_decision(output))
    if action["role"] == "operational_review":
        from .operational_dispositions import validate_disposition, require_basis_refs
        check("output/disposition", lambda: validate_disposition(output["disposition"]))
        check("output/disposition/basis_refs", lambda: require_basis_refs(
            output['disposition'], context['admissible_basis_refs']))
    definitions = deepcopy(context.get("kind_definitions", {}))
    kind_instance = {"kind_definitions": {row["family"] + ":" + row["token"]: deepcopy(row)
                     for rows in definitions.values() for row in rows if "family" in row}}
    for index, definition in enumerate(extensions.get("kind_definitions", [])):
        def check_kind(definition=definition):
            nonlocal kind_instance
            kind_instance, _ = knowledge_io.register_kind_definition(kind_instance, definition,
                source_ref="submission-preview", actor_ref="producer", clock=clock)
            family = "knowledge" if definition["family"] == "knowledge" else "relations"
            require(definition["token"] not in {row["token"] for row in definitions.get(family, [])}, "kind token already exists")
            definitions.setdefault(family, []).append(definition)
        check(f"activity-extensions.json/kind_definitions/{index}", check_kind)
    if task_research(action):
        if owns_response:
            check("output/report", lambda: require(bool(output["report"].strip()), "report must state the actual scope and outcome"))
        for index, item in enumerate(output["knowledge"]):
            def candidate(item=item):
                require(item["kind"] in {row["token"] for row in definitions.get("knowledge", [])}, "knowledge kind must be active or proposed in this bundle")
                errors = knowledge_io.candidate_shape_errors(item)
                require(not errors, "; ".join(errors))
                require(item["title"] not in knowledge_ids, "a new title cannot collide with an existing knowledge ID")
                refs = item["dependencies"]
                require(not set(refs) - knowledge_ids - new_knowledge, "knowledge dependencies must name provided knowledge or unique new titles")
                require(item["title"] not in refs, "knowledge cannot depend on itself")
            check(f"output/knowledge/{index}", candidate)

    for index, insight in enumerate(extensions.get("research_insights", [])):
        check(f"activity-extensions.json/research_insights/{index}/kind", lambda insight=insight:
              require(insight["kind"] in {row["token"] for row in definitions.get("knowledge", [])}, "insight kind must be active or proposed"))
        check(f"activity-extensions.json/research_insights/{index}/evidence_ids", lambda insight=insight:
              require(not set(insight.get("evidence_ids", [])) - known, "insight evidence must name existing input records"))
    metadata = extensions.get("knowledge_metadata", [])
    check("activity-extensions.json/knowledge_metadata", lambda: require(
        len({x["title"] for x in metadata}) == len(metadata) and not {x["title"] for x in metadata} - new_knowledge,
        "metadata titles must be distinct and name new knowledge in this output"))
    for index, entry in enumerate(metadata):
        if "relation_claim" in entry:
            claim = entry["relation_claim"]
            check(f"activity-extensions.json/knowledge_metadata/{index}/relation_claim", lambda claim=claim: require(
                {claim["source"], claim["target"]} <= knowledge_ids and claim["kind"] in {d["token"] for d in context["kind_definitions"]["relations"]},
                "relation claim requires a registered relation kind and existing knowledge endpoints"))
    knowledge_changes = extensions.get("knowledge_changes", [])
    replacement_ids = [entry["replacement_id"] for entry in knowledge_changes if entry.get("replacement_id")]
    check("activity-extensions.json/knowledge_changes", lambda: require(
        len(replacement_ids) == len(set(replacement_ids)) and not set(replacement_ids) & known,
        "replacement IDs must be distinct and must not reuse existing record IDs"))
    sibling_ids = set(replacement_ids)
    for index, entry in enumerate(knowledge_changes):
        check(f"activity-extensions.json/knowledge_changes/{index}", lambda entry=entry: require(
            entry["id"] in knowledge_ids, "knowledge revision requires an existing input record"))
        from .knowledge import validate_changes
        check(f"activity-extensions.json/knowledge_changes/{index}/changes", lambda entry=entry: validate_changes(entry["changes"]))
        for ref in entry["impact_set"]:
            check(f"activity-extensions.json/knowledge_changes/{index}/impact_set", lambda ref=ref: supplied(ref))
        if "dependencies" in entry["changes"]:
            check(f"activity-extensions.json/knowledge_changes/{index}/changes/dependencies", lambda entry=entry: require(
                isinstance(entry["changes"]["dependencies"], list) and
                set(entry["changes"]["dependencies"]) <= (knowledge_ids - {entry["id"]}) | sibling_ids and
                entry.get("replacement_id") not in set(entry["changes"]["dependencies"]),
                "revision dependencies must name other provided knowledge or explicit sibling replacements"))
        if "kind" in entry["changes"]:
            check(f"activity-extensions.json/knowledge_changes/{index}/changes/kind", lambda entry=entry: require(
                entry["changes"]["kind"] in {d["token"] for d in context["kind_definitions"]["knowledge"]}, "revision kind must be registered"))
    if "observation_rules" in extensions:
        from .observations import task_rules_from_execution
        check("activity-extensions.json/observation_rules", lambda: task_rules_from_execution(extensions["observation_rules"], context.get('execution_id')))
        check("activity-extensions.json/observation_rules", lambda: require(action.get("target") in tasks, "persisted rules require the assigned task"))
    conditions = extensions.get("task_conditions", [])
    targeted = []
    for index, entry in enumerate(conditions):
        key = entry.get("task_title", entry.get("task_id"))
        targeted.append(key)
        targets = (set(action['observation_rule_targets']) if 'observation_rule_targets' in action else
                   new_tasks | {x["revises_task_id"] for x in output.get("candidates", []) if x["revises_task_id"]})
        # A title and the ID it revises identify the same prepared target.
        targeted[-1] = next((x['title'] for x in output.get('candidates', [])
                            if x.get('revises_task_id') == key), key)
        check(f"activity-extensions.json/task_conditions/{index}", lambda entry=entry, key=key: require(
            ("task_id" in entry) != ("task_title" in entry) and key in targets, "task condition must name exactly one prepared target"))
        check(f"activity-extensions.json/task_conditions/{index}/dependencies", lambda entry=entry: require(
            set(entry.get("dependencies", [])) <= known | new_tasks, "task dependencies must name provided records or prepared titles"))
        if "observation_rules" in entry:
            from .observations import validate_task_rules
            check(f"activity-extensions.json/task_conditions/{index}/observation_rules", lambda entry=entry: validate_task_rules(entry["observation_rules"]))
        if "occurrence_condition" in entry:
            check(f"activity-extensions.json/task_conditions/{index}/occurrence_condition", lambda entry=entry: planning.validate_condition(entry["occurrence_condition"]))
    check("activity-extensions.json/task_conditions", lambda: require(len(targeted) == len(set(targeted)), "task conditions must not repeat a target"))
    if conditions or output.get('candidates'):
        from .task_contracts import prepared_dependencies
        graph = deepcopy(tasks)
        titles = {row["title"]: row.get("revises_task_id") or row["title"] for row in output.get("candidates", [])}
        for row in output.get("candidates", []):
            graph[titles[row["title"]]] = {"dependencies": prepared_dependencies(row, {}, titles)}
        for row in conditions:
            target = row.get("task_id") or titles.get(row.get("task_title"))
            if target in graph:
                graph[target]["dependencies"] = prepared_dependencies(graph[target], row, titles)
        cycles = [cycle for cycle in dependency_cycles(graph) if set(cycle) & set(titles.values())]
        check("activity-extensions.json/task_conditions/dependencies", lambda: require(not cycles, "explicit task dependency cycle: " + str(cycles)))
    for family, key in (("task_dispositions", "task_id"), ("queued_requests", "request_id"),
                        ("academic_resolutions", "id")):
        rows = extensions.get(family, [])
        check("activity-extensions.json/" + family, lambda rows=rows, key=key: require(
            len({row[key] for row in rows}) == len(rows), "entries must identify distinct targets"))
    if action["role"] in PLANNING_ROLES:
        check("activity-extensions.json/model_assessments", lambda: validate_assessments(
            action, output, extensions, tasks))
    if 'observation_rule_targets' in action:
        from .observations import validate_rule_preparation
        check('activity-extensions.json/task_conditions', lambda: validate_rule_preparation(action, extensions, tasks))
    for entry in extensions.get("queued_requests", []):
        check("activity-extensions.json/queued_requests", lambda entry=entry: require(
            entry["request_id"] in {a["id"] for a in context.get("queued_work", [])}, "request was not available for planning"))
    if extensions.get('input_overflow_resolutions'):
        from .input_recovery import validate_resolutions
        check('activity-extensions.json/input_overflow_resolutions', lambda: validate_resolutions(
            extensions['input_overflow_resolutions'], context.get('input_overflow_requests', [])))
    for entry in extensions.get("task_dispositions", []):
        def disposition(entry=entry):
            task = tasks.get(entry["task_id"], {})
            from .task_scope import validate_withdrawal_scope
            proposed = next((a for a in output.get('task_assessments', []) if a['task_id'] == entry['task_id']), None)
            validate_withdrawal_scope(task, task, proposed_assessment=proposed)
            live = [row for row in context.get('ongoing_work', [])
                    if row.get('target') == entry['task_id']
                    and row.get('status') in {'queued', 'starting', 'running', 'stopping'}
                    and row.get('execution_id') != context.get('execution_id')]
            require(not live, 'task has another live execution')
            require(entry["task_id"] not in {row["task_id"] for row in output.get("dispositions", []) if row["kind"] == "selected"} and entry["task_id"] not in {c["revises_task_id"] for c in output.get("candidates", [])}, "cannot withdraw and select or revise the same task")
        check("activity-extensions.json/task_dispositions", disposition)
    for entry in extensions.get("academic_resolutions", []):
        check("activity-extensions.json/academic_resolutions", lambda entry=entry: require(
            entry["id"] in {r["id"] for r in context.get("external_rejections", [])}, "resolution must identify an external rejection"))

    for index, entry in enumerate(extensions.get("external_requests", [])):
        def external(entry=entry):
            operation = prepare_operation(entry["request"], entry.get("grant_id") or "ungranted", "submission-preview")
            if entry.get("grant_id"):
                grant = next((g for g in context.get("grants", []) if g["id"] == entry["grant_id"]), None)
                require(grant is not None and grant.get("kind") == "http", "external request needs a provided HTTP grant")
                basis_time = context.get("submission_contract", {}).get("basis_time")
                if basis_time is None and (grant.get("expires_at") or grant.get("valid_from")):
                    raise ValueError("time-bounded grant preview requires a fixed input basis_time")
                validate_operation(operation, grant, basis_time or "1970-01-01T00:00:00+00:00")
            if entry.get("academic_effect_id"):
                effect = next((e for e in (context.get("task") or {}).get("required_external_effects", []) if e["id"] == entry["academic_effect_id"]), None)
                require(effect is not None, "academic effect must belong to the assigned task")
                require(not effect.get("grant_id") or effect["grant_id"] == entry.get("grant_id"), "academic effect requires its specified grant")
        check(f"activity-extensions.json/external_requests/{index}", external)

    relations = [*output.get("relations", []), *extensions.get("relations", [])]
    if relations:
        def relational():
            ref = context.get("relation_validation_source")
            require(isinstance(ref, dict) and ref.get("snapshot") == context.get("snapshot"),
                    "relation validation input is missing or belongs to another snapshot")
            source = read_source(workspace, ref, limit=max(1, ref["bytes"]))
            require(source["status"] == "ok" and not source["truncated"],
                    "relation validation input is missing or corrupt")
            instance = load_json(source["bytes"])
            instance["knowledge"].update({x["title"]: {**x, "id": x["title"], "status": "candidate"}
                                          for x in output.get("knowledge", [])})
            for relation in relations:
                result = knowledge_io.validate_relation(instance, relation)
                require(result["valid"], "; ".join(result["reasons"]))
        check("relations", relational)
    if extensions.get("research_requests"):
        check("activity-extensions.json/research_requests",
              lambda: review_cycle.validate_research_requests(extensions["research_requests"]))
        for index, entry in enumerate(extensions["research_requests"]):
            for number, ref in enumerate(entry["source_refs"]):
                check(f"activity-extensions.json/research_requests/{index}/source_refs/{number}",
                      lambda ref=ref: validate_research_reference(ref, context), "submission.research_source")
    if action["role"] == "identity_review" and action.get("review_cycle_id"):
        domain_output = {key: value for key, value in output.items() if key not in {"integration_bundles", "repair_responses"}}
        check("output", lambda: review_cycle.validate_visible_output(context["role_review"], action, domain_output,
                    requesting_research=bool(extensions.get("research_requests"))))
    if review_research(action):
        research = context["review_research"]
        check("output", lambda: review_cycle.validate_research_answer(output))
        for field in ('used_sources', 'evidence_refs'):
            for index, ref in enumerate(output[field]):
                def source(ref=ref):
                    name = fixed_research_reference_path(ref, {s['ref'] for s in research['sources']})
                    if name is not None:
                        path = safe_path(workspace, name)
                        present = path.is_file() if candidate_files is None else name in candidate_files
                        require(present, 'evidence must be a collectable workspace file: ' + name)
                check(f'output/{field}/{index}', source)
    return issues


def payload_issues(output: dict, schema: dict, context: dict, extensions: dict, workspace: Path,
                   *, candidate_files: dict[str, bytes] | None = None, clock) -> list[dict]:
    """Shared producer/receiver entry point, including bundle and retry coverage."""
    original_output = output

    def original_schema_issues():
        return _schema_issues(original_output, schema, "output") + _schema_issues(extensions,
            extension_schema(context["action"]), "activity-extensions.json")

    if not isinstance(output, dict) or not isinstance(extensions, dict):
        return original_schema_issues()
    envelope = "integration_bundles" in schema.get("properties", {})
    derived = None
    if envelope:
        try:
            derived = integration.derived_bundles(output, extensions, context)
        except (TypeError, ValueError):
            pass  # inspect_bundles reports the malformed response as a global issue.
    issues = integration.inspect_bundles(output, extensions, context, derived=derived) if envelope else []
    if any(not row.get("integration_id") for row in issues):
        return original_schema_issues() + issues
    if envelope:
        output = derived[0]
    if envelope and integration.split_research(context):
        schema_issues = original_schema_issues()
        for bundle in integration.split_bundles(output, extensions, context, derived=derived):
            sliced = {**bundle["output"], "integration_bundles": output["integration_bundles"]}
            if "repair_responses" in output:
                sliced["repair_responses"] = output["repair_responses"]
            rows = _payload_issues(sliced, schema, context, bundle["extensions"], workspace,
                                   owns_response=bundle["owns_response"], candidate_files=candidate_files, clock=clock)
            # Slicing retains values but changes array indices. Restore exact
            # coordinates in the producer's sealed output before assigning IDs.
            families = {}
            for original in bundle["members"]:
                if "/" in original:
                    prefix = original.rsplit("/", 1)[0]
                    families.setdefault(prefix, []).append(original)
            for row in rows:
                path = row["path"]
                for prefix, originals in families.items():
                    if path.startswith(prefix + "/"):
                        index, _, suffix = path[len(prefix) + 1:].partition("/")
                        # Schema/domain array issues use indices in this sliced family.
                        path = originals[int(index)] + ("/" + suffix if suffix else "")
                        break
                issues.append(integration.issue(row.get("rule_id", "submission." + path.replace("/", ".")),
                    path, row["message"], bundle["integration_id"]))
        # Top-level malformed fields cannot be hidden by the slice projection.
        for row in schema_issues:
            if not any(row["path"].startswith(prefix) for prefix in ("output/knowledge/", "output/relations/", "activity-extensions.json/")):
                issues.append(row)
    else:
        issues.extend(_payload_issues(output, schema, context, extensions, workspace,
                                      candidate_files=candidate_files, clock=clock))
    schema_failed = any(row.get("rule_id", "").startswith("schema.") for row in issues)
    if schema_failed:
        return issues
    failures = context.get("submission_failures", [])
    replies = output.get("repair_responses", [])
    expected = {row["issue_id"] for row in failures}
    actual = [row["issue_id"] for row in replies]
    if set(actual) != expected or len(set(actual)) != len(actual):
        issues.append(_issue("output/repair_responses", "address every previous issue exactly once; unknown replies are forbidden",
                             "repair.coverage"))
    owners = {path: bundle["integration_id"] for bundle in output.get("integration_bundles", [])
              for path in bundle.get("members", [])}
    normalized = []
    for row in issues:
        row = dict(row)
        path = row.get("path", "output")
        matches = [coordinate for coordinate in owners if path == coordinate or path.startswith(coordinate + "/")]
        if not row.get("integration_id") and matches and not row.get("rule_id", "").startswith("integration."):
            row["integration_id"] = owners[max(matches, key=len)]
        normalized.append(integration.issue(row.get("rule_id", "submission." + path.replace("/", ".")),
            path, row["message"], row.get("integration_id")))
    return normalized


def _captured_checkpoint(files: dict[str, bytes]) -> dict:
    raw = files.get("checkpoint.json")
    if raw is None:
        return {"status": "missing"}
    try:
        if len(raw) > CHECKPOINT_MAX_BYTES:
            raise ValueError("checkpoint exceeds the 4 MiB record limit")
        value = checkpoint_value(raw)
        return {"status": "valid", "value": value, "sha256": hashlib.sha256(raw).hexdigest(), "raw": raw}
    except Exception as error:
        return {"status": "invalid", "error": f"{type(error).__name__}: {error}"}


def _workspace_checks(context, workspace, candidate=None, *, clock):
    issues = []
    limits = context.get("submission_contract", {}).get("limits", {})
    files = (candidate if candidate is not None else
             collect_outputs(workspace, max_bytes=limits["max_artifact_bytes"])
             if limits.get("max_artifact_bytes") is not None else {"files": {}, "manifest": [], "omitted": []})
    issues.extend(_issue(row["path"], row["reason"], "artifact.preservation") for row in files["omitted"])
    checkpoint = _captured_checkpoint(files["files"]) if candidate is not None else read_checkpoint(workspace, clock=clock)
    if checkpoint["status"] not in {"missing", "valid"}:
        issues.append(_issue("checkpoint.json", checkpoint.get("error", checkpoint["status"]), "checkpoint.schema"))
    elif checkpoint["status"] == "valid":
        for reference in checkpoint["value"]["evidence_paths"]:
            try:
                validate_reference(reference, context, workspace,
                                   candidate_files=files["files"] if candidate is not None else None)
            except (ValueError, TypeError, OSError) as error:
                issues.append(_issue("checkpoint.json/evidence_paths", str(error), "checkpoint.reference"))
    return issues, files["manifest"]


def _check_hashes(output, schema, context, extensions):
    return {"output": exact_content_hash(output), "extensions": exact_content_hash(extensions),
            "context": exact_content_hash(context), "schema": exact_content_hash(schema)}


def capture_eligible(output, extensions, context, issues):
    """A whole immutable candidate may contain independently returnable members."""
    if not issues:
        return True
    if (not integration.split_research(context) or not isinstance(output, dict)
            or not isinstance(output.get('integration_bundles'), list)
            or len(output['integration_bundles']) < 2):
        return False
    # Ownership, new-object closure and declaration authority must all be sound.
    if integration.inspect_bundles(output, extensions, context):
        return False
    owners = {coordinate: bundle['integration_id'] for bundle in output['integration_bundles']
              for coordinate in bundle['members']}
    failed = set()
    for row in issues:
        path = row['path']
        matches = [coordinate for coordinate in owners if path == coordinate or path.startswith(coordinate + '/')]
        if not matches or row.get('rule_id', '').startswith(('integration.', 'artifact.', 'machine_check.')):
            return False
        owner = owners[max(matches, key=len)]
        if row.get('integration_id') != owner:
            return False
        failed.add(owner)
    return bool({bundle['integration_id'] for bundle in output['integration_bundles']} - failed)


def captured_check(check):
    """Validate the central check and its declared capture eligibility."""
    passed = check.get('passed') is True and not check.get('issues')
    if check.get('passed') is not (not check.get('issues')):
        raise ValueError('machine check pass flag differs from its issues')
    eligible = check['capture_eligible']
    if type(eligible) is not bool or (passed and not eligible):
        raise ValueError('invalid machine capture eligibility')
    if eligible and not passed and (not integration.split_research({'action': check['check_subject']})
            or any(not row.get('integration_id') for row in check['issues'])):
        raise ValueError('partial capture requires exclusively local independent bundle issues')
    return eligible


# The action fields a machine check is about; its failure key hashes them (_failure_key).
CHECK_SUBJECT_FIELDS = ("id", "role", "target", "stage", "slot", "review_cycle_id", "revision_targets")
# What no machine check decides; the installed submission contract states the same list.
NOT_MACHINE_CHECKED = ("mathematical_meaning", "Lean", "application_time_currentness",
                       "final_authority_and_provenance", "kind_semantic_approval")


def _check_subject(context):
    return {key: deepcopy(context.get("action", {}).get(key)) for key in CHECK_SUBJECT_FIELDS}


def _failed_check(mode, context, raw, error, phase, execution_id):
    """The check record of a candidate that could not be read or parsed."""
    return {"contract_id": "do-math-machine-check/5", "mode": mode, "passed": False,
            "execution_id": execution_id,
            "tool_sha256": context.get("submission_contract", {}).get("tool_sha256"),
            "check_subject": _check_subject(context), "input_snapshot": context.get("snapshot"),
            "input_hashes": {"raw_output": hashlib.sha256(raw).hexdigest()} if raw is not None else {},
            "issues": [_issue("submission", str(error), 'submission.parse'
                if phase == 'parse' and isinstance(error, (ValueError, TypeError)) else 'submission.read')], "repairs": [],
            "check_order": ["read_or_parse"], "comparison": {"status": "no_previous_check"},
            "not_checked": ["schema", "payload_semantics", "integration_structure", "artifact_preservation",
                            *NOT_MACHINE_CHECKED]}


def check_submission(output, schema, context, extensions, workspace, *, mode,
                     execution_id, tool_sha256, previous=None, candidate=None, clock):
    """Record deterministic payload checks; producer records never grant authority."""
    if mode not in {"producer", "receiver", "preview"}:
        raise ValueError("unknown submission check mode")
    candidate_files = candidate["files"] if candidate is not None else None
    issues = payload_issues(output, schema, context, extensions, workspace, candidate_files=candidate_files, clock=clock)
    workspace_issues, files = _workspace_checks(context, workspace, candidate, clock=clock)
    issues.extend(workspace_issues)
    hashes = _check_hashes(output, schema, context, extensions)
    skipped = list(NOT_MACHINE_CHECKED)
    if any(row["rule_id"].startswith("schema.") for row in issues):
        skipped.extend(["payload_semantics", "integration_structure"])
    from .contracts import schema_reference
    result = {"contract_id": "do-math-machine-check/5", "tool_sha256": tool_sha256,
              "check_subject": _check_subject(context),
              "schema_ref": schema_reference(schema),
              "mode": mode, "execution_id": execution_id, "input_snapshot": context.get("snapshot"),
              "input_hashes": hashes, "check_order": ["schema", "payload_semantics", "integration_structure", "repair_coverage"],
              "issues": issues, "passed": not issues, "not_checked": skipped, "files": files,
              "comparison": {"status": "no_previous_check"}, "repairs": []}
    if previous is not None:
        same_tool = previous.get("tool_sha256") == tool_sha256
        same_input = previous.get("input_hashes") == hashes
        if not same_tool:
            status = "tool_changed"
        elif not same_input:
            status = "input_changed"
        else:
            projection = lambda rows: sorted((row["rule_id"], row["path"], row.get("integration_id")) for row in rows)
            status = "matched" if (projection(previous.get("issues", [])) == projection(issues)
                                    and previous.get("not_checked") == skipped) else "tool_defect"
        result["comparison"] = {"status": status, "previous_check_id": previous.get("id")}
        if status == "tool_defect":
            result["passed"] = False
            result["issues"].append(_issue("checks", "producer and receiver disagree for the same tool and input hashes",
                                          "machine_check.tool_defect"))
        result["repairs"] = _repair_links([previous], result)
    result['capture_eligible'] = capture_eligible(output, extensions, context, result['issues'])
    result["id"] = "MC-" + exact_content_hash(result)[:24]
    return result


def preview_submission(output, schema, context, extensions, workspace, *, execution_id,
                       tool_sha256, instance, runtime, apply_bundle, validate_current,
                       validate_candidate, previous=None, check=None, clock):
    """Central-only candidate preview with a closed, producer-visible response.

    ENGINE supplies its actual pure candidate callbacks. No publisher is supplied
    and neither copied projections nor private exception text leave this function.
    A sealed ``check`` that is not capture-eligible is answered from its own
    issues without applying a candidate; ``output`` and ``extensions`` may then be None.
    """
    not_checked = ["mathematical_meaning", "Lean", "future_application_currentness"]
    check = deepcopy(check) if check is not None else check_submission(
        output, schema, context, extensions, workspace, mode="preview",
        execution_id=execution_id, tool_sha256=tool_sha256, previous=previous, clock=clock)
    response = {"contract_id": PREVIEW_CONTRACT_ID, "check_id": check["id"],
                "schema_ref": check["schema_ref"], "input_hashes": check["input_hashes"], "authoritative": False}
    if check.get("capture_eligible") is False:
        return {**response, "passed": False, "issues": deepcopy(check["issues"]), "bundles": [],
                "not_checked": ["candidate_application", *not_checked]}
    candidate = integration.preview_bundles(instance, runtime, output, extensions, context,
        execution_id=execution_id, apply_bundle=apply_bundle, validate_current=validate_current,
        validate_candidate=validate_candidate, submission_issues=check["issues"])
    public_issues = deepcopy(check["issues"])
    known = {row["issue_id"] for row in public_issues}
    for row in candidate["issues"]:
        if row["issue_id"] not in known:
            # Hashing a private error message could itself reveal a small verdict
            # space. Recreate its identity from public stage and bundle only.
            stage = row["rule_id"] if row["rule_id"] in {
                "integration.currentness", "integration.application", "integration.candidate",
                "integration.id_reuse"} else "integration.candidate"
            public_issues.append(integration.issue(stage, "output/integration_bundles",
                "Candidate cannot pass this stage with the current admissible evidence.", row.get("integration_id")))
    return {**response, "passed": not public_issues, "issues": public_issues,
        "bundles": [{"integration_id": row["integration_id"], "status": row["status"]}
                    for row in candidate["bundles"]],
        "not_checked": not_checked}


def _failure_key(record, issue):
    return (record.get("execution_id"), record.get("tool_sha256"), exact_content_hash({
                'subject': record.get('check_subject', {}), 'schema_ref': record.get('schema_ref'),
                'input_snapshot': record.get('input_snapshot')}),
            issue["rule_id"], issue["path"], issue.get("integration_id"))


def _pending_failures(records):
    pending = {}
    for record in records:
        for row in record.get("issues", []):
            pending[_failure_key(record, row)] = {**row, "check_id": record["id"],
                "execution_id": record.get("execution_id"), "tool_sha256": record.get("tool_sha256"),
                "check_subject": deepcopy(record.get("check_subject", {}))}
        for repair in record.get("repairs", []):
            key = _failure_key(record, repair)
            prior = pending.get(key)
            if (repair.get("status") == "resolved" and prior and
                    repair.get("previous_check_id") == prior["check_id"]):
                del pending[key]
    return pending


def _repair_links(records, result):
    current = {_failure_key(result, row) for row in result["issues"]}
    scope = _failure_key(result, {"rule_id": "", "path": ""})[:3]
    if result.get("comparison", {}).get("status") == "tool_defect":
        return []
    links = []
    for key, failure in _pending_failures(records).items():
        if key[:3] != scope or key in current:
            continue
        rule = failure["rule_id"]
        skipped = result.get("not_checked", [])
        checked = ("schema" not in skipped if rule.startswith("schema.") else
                   "read_or_parse" not in result.get("check_order", []) if rule in {
                       'submission.parse', 'submission.read'} else
                   "payload_semantics" not in skipped)
        if checked:
            links.append({key: failure[key] for key in ("issue_id", "rule_id", "path")})
            links[-1].update(integration_id=failure.get("integration_id"), previous_check_id=failure["check_id"],
                             status="resolved", kind="output_retry")
    return links


def summarize_checks(records, *, history_window):
    """Derive rule counts from supplied seal order, retaining older open failures.

    ENGINE/SURFACE supplies checks in public event/seal order, including returned
    and partial executions. Timestamps and lexicographic IDs do not define order.
    """
    if isinstance(history_window, bool) or not isinstance(history_window, int) or history_window < 0:
        raise ValueError("history_window must be a nonnegative integer")
    records = list(records)
    unresolved = _pending_failures(records)
    counts, evidence = {}, {}
    for record in records[-history_window:] if history_window else []:
        for rule in sorted({row["rule_id"] for row in record.get("issues", [])}):
            counts[rule] = counts.get(rule, 0) + 1
            evidence.setdefault(rule, []).append({
                "check_id": record["id"], "execution_id": record.get("execution_id"),
                "mode": record.get("mode"), "producer_role": record.get("check_subject", {}).get("role"),
                "schema_ref": deepcopy(record.get("schema_ref")), "tool_sha256": record.get("tool_sha256"),
                "checker_module": "do_math/submission.py",
                "issues": [{key: row.get(key) for key in ("issue_id", "path", "integration_id")}
                           for row in record.get("issues", []) if row["rule_id"] == rule]})
    return {"history_window": history_window, "window_check_count": min(history_window, len(records)),
            "rule_failure_counts": counts, "rule_evidence": evidence, "unresolved": list(unresolved.values()),
            "authority": "derived_from_sealed_checks"}


def _validated_check(raw, identifier):
    row = load_json(raw)
    if (not isinstance(row, dict) or row.get("id") != identifier or
            identifier != "MC-" + exact_content_hash({k: v for k, v in row.items() if k != "id"})[:24]):
        raise ValueError("machine-check content identity differs")
    return row


def read_producer_checks(workspace, check_id, *, boundary=None):
    """Read the exact predecessor chain named by the intent, never directory order.

    One physical boundary of the workspace serves every read in the chain.
    """
    from .file_io import PhysicalBoundary
    workspace = Path(workspace).resolve()
    rows, seen = [], set()
    while check_id is not None:
        if not isinstance(check_id, str) or not re.fullmatch(r"MC-[0-9a-f]{24}", check_id) or check_id in seen:
            raise ValueError("invalid or cyclic producer check chain")
        seen.add(check_id)
        boundary = boundary or PhysicalBoundary(workspace)
        row = _validated_check(read_stable(safe_path(workspace, "checks/" + check_id + ".json"), boundary=boundary),
                               check_id)
        if row.get("mode") != "producer" or type(row.get("producer_sequence")) is not int:
            raise ValueError("producer check lacks an explicit sequence")
        rows.append(row)
        check_id = row.get("previous_producer_check_id")
    rows.reverse()
    _validate_producer_sequence(rows)
    return rows


def _validate_producer_sequence(rows):
    for number, row in enumerate(rows, 1):
        previous = rows[number - 2]["id"] if number > 1 else None
        if (row.get("mode") != "producer" or type(row.get("producer_sequence")) is not int or
                row["producer_sequence"] != number or row.get("execution_id") != rows[-1].get("execution_id") or
                row.get("previous_producer_check_id") != previous):
            raise ValueError("producer check sequence or execution differs")


def summarize_snapshot_checks(seals, *, snapshot, read_artifact, history_window, git_dir=None):
    """Derive diagnostics from central checks in immutable publication order.

    With the repository's ``git_dir``, check artifacts this process already
    matched (이음새-정본.md §3) are read but not hashed again.
    """
    from .repository import sealed_bytes
    if not isinstance(snapshot, str) or not snapshot or type(history_window) is not int or history_window < 0:
        raise ValueError("snapshot and nonnegative history_window are required")
    records, seen, sequence = [], set(), 0
    for seal in seals:
        if type(seal.get('event_seq')) is not int or seal['event_seq'] <= sequence:
            raise ValueError('central checks must follow explicit public event order')
        sequence = seal['event_seq']
        capture_id = seal.get('capture_id')
        if not capture_id or capture_id in seen:
            raise ValueError('central submission request was published twice')
        seen.add(capture_id)
        evidence = seal['submission_check']
        artifacts = {}
        for entry in evidence['artifacts']:
            if not entry['path'].startswith(ARTIFACT_ROOT) or entry['path'] in artifacts:
                raise ValueError('central check artifact coordinate differs')
            raw = sealed_bytes(git_dir, entry['path'], entry['sha256'], entry['bytes'],
                               lambda: read_artifact(entry['path'], snapshot),
                               error='central check artifact hash or size differs')
            artifacts[entry['path']] = raw
        raw = artifacts[evidence['check_ref']]
        parsed = load_json(raw)
        row = _validated_check(raw, parsed.get('id') if isinstance(parsed, dict) else None)
        if row.get('mode') != 'receiver' or row.get('execution_id') != seal['execution_id']:
            raise ValueError('central check execution or mode differs')
        if (seal['state'] == 'accepted') != captured_check(row):
            raise ValueError('central check result differs from its published receipt')
        # Repair links are a derived projection, never an edit of the sealed check.
        row['repairs'] = _repair_links(records, row)
        records.append(row)
    summary = summarize_checks(records, history_window=history_window)
    summary.update(snapshot=snapshot, seal_count=len(records), window_seal_count=min(history_window,len(records)),
                   coverage='central_submission_checks')
    return summary


@lru_cache(maxsize=2)
def _support_archive(package: Path, sources: tuple[tuple[str, str], ...]) -> bytes:
    """Reuse compression only for exactly the same relative names and digests."""
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as bundle:
        for relative, _ in sources:
            entry = zipfile.ZipInfo("do_math/" + relative, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, (package / relative).read_bytes())
    return archive.getvalue()


def install_tools(workspace: Path, context: dict, schema: dict, max_artifact_bytes: int | None, *, clock) -> dict:
    """Copy one installed code edition, never the central research state.

    The read tool reads that state only at the input snapshot and within the record map.
    """
    interpreter = console_python()
    context["reference_catalog"] = reference_catalog(context, workspace)
    package = Path(__file__).resolve().parent
    # The installed edition is identified by fingerprint-cached digests; code
    # bytes are read only to compress a new edition. Application callbacks
    # remain central; only shared checker code is shipped.
    from .file_io import cached_sha256
    sources = tuple((path.relative_to(package).as_posix(), cached_sha256(path))
                    for path in sorted(package.rglob("*.py"))
                    if path.name != "engine.py" and not path.name.endswith("_engine.py"))
    archive = _support_archive(package, sources)
    files = {"tools/submission-support.zip": archive}
    files["tools/check_submission.py"] = (b"import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
        b"sys.path.insert(0, str(Path(__file__).with_name('submission-support.zip')))\n"
        b"from do_math.submission_tool import main\nraise SystemExit(main())\n")
    files["tools/read_input.py"] = (b"import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
        b"sys.path.insert(0, str(Path(__file__).with_name('submission-support.zip')))\n"
        b"from do_math.input_tool import read_main\nraise SystemExit(read_main())\n")
    if "record_map" in context:
        from .context_store import READ_LOG
        context["record_map"]["read_tool"] = {
            "command": [interpreter, "-B", "input/tools/read_input.py"],
            "arguments": "--list [--family <root/family>] | --id <record ID> (repeatable) | --path <snapshot file path> "
                         "(repeatable) [--output <workspace-relative file> with one --path]",
            "log_path": READ_LOG}
    if "formal_verifier" in context:
        files["tools/check_lean.py"] = (b"import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
            b"sys.path.insert(0, str(Path(__file__).with_name('submission-support.zip')))\n"
            b"from do_math.formal_preview import main\nraise SystemExit(main())\n")
        context["formal_verifier"]["preview"] = {
            "command": [interpreter, "-B", "input/tools/check_lean.py"],
            "arguments": "--source <workspace-relative .lean file> --declaration <name> (repeat for each declaration)",
            "authoritative": False,
            "environment": "Same verifier edition and configured command for the kernel check, signatures and axioms; dependency evidence is not extracted. Shared libraries and Lake caches are not isolated. Central verification is mandatory."}
    from .contracts import schema_reference
    contract = {"command": [interpreter, "-B", "input/tools/check_submission.py"],
        "schema_ref": schema_reference(schema),
        "delivery": "Normal delivery is one complete JSON final. Central validation captures its exact bytes after verified CLI completion and local termination. Draft submission is optional and early; an accepted draft cannot be replaced by a later final.",
        "arguments": "--output <workspace-relative draft>; add --preview or --submit and --wait-seconds <remaining caller budget> for central control; --new-knowledge-id prints a fresh replacement_id without submission or reservation",
        "basis_time": context.get("observed_at") or clock.now(),
        "tool_sha256": hashlib.sha256(archive).hexdigest(), "checks_directory": "checks",
        "workspace": str(workspace.resolve()),
        "schema_path": "input/submission/schema.json", "context_path": "input/submission/context.json",
        "extensions_schema_path": "input/submission/extensions.schema.json",
        "limits": {"max_artifact_bytes": max_artifact_bytes, "checkpoint_bytes": CHECKPOINT_MAX_BYTES},
        "scratch_directory": ".scratch", "not_checked": list(NOT_MACHINE_CHECKED)}
    context["submission_contract"] = contract
    files["submission/context.json"] = canonical_json(context)
    files["submission/schema.json"] = canonical_json(schema)
    files["submission/extensions.schema.json"] = canonical_json(extension_schema(context["action"]))
    materialize_inputs(workspace, files)
    return contract


def producer_check(workspace, draft, *, clock):
    """Serialize local checks; immutable predecessors, not timestamps, own order.

    The OS lock (file_io.os_lock) ends with its holder, so a check killed by a
    shell timeout leaves no owner behind for the next check of this workspace.
    """
    from contextlib import ExitStack
    from .file_io import PhysicalBoundary, os_lock
    workspace = Path(workspace).resolve()
    directory = safe_path(workspace, "checks")
    directory.mkdir(parents=True, exist_ok=True)
    lock = safe_path(workspace, "checks/.producer-lock")
    with ExitStack() as held:
        try:
            held.enter_context(os_lock(lock, blocking=False))
        except OSError as error:
            raise ValueError("another producer check owns this workspace") from error
        boundary = PhysicalBoundary(workspace)  # one root proof for this check's reads
        head = safe_path(workspace, "checks/.producer-head")
        history = (read_producer_checks(workspace, load_json(read_stable(head, boundary=boundary))["check_id"],
                                        boundary=boundary) if head.exists() else [])
        result = _producer_check(workspace, draft, history, clock=clock)
        _validated_check(read_stable(safe_path(workspace, "checks/" + result["id"] + ".json"), boundary=boundary),
                         result["id"])
        pending = safe_path(workspace, "checks/.producer-head.pending")
        pending.write_bytes(canonical_json({"check_id": result["id"]}))
        atomic_replace(pending, head)
        return result


def _producer_check(workspace, draft, history, *, clock):
    """Read exact local bytes and seal a check, including malformed drafts."""
    workspace = Path(workspace).resolve()
    raw = None
    context = {}
    schema = None
    relative = None
    phase = 'read'
    try:
        context = load_json((workspace / "input/submission/context.json").read_bytes())
        schema = load_json((workspace / "input/submission/schema.json").read_bytes())
        draft = (workspace / draft).resolve()
        if not draft.is_relative_to(workspace):
            raise ValueError("submission draft must be inside this workspace")
        relative = draft.relative_to(workspace).as_posix()
        raw = read_stable(safe_path(workspace, relative))
        phase = 'parse'
        output = load_json(raw)
        extensions = read_extensions(workspace)
        phase = 'check'
        contract = context["submission_contract"]
        # Preparation fixed the support archive's digest; each check reuses it.
        tool_hash = contract["tool_sha256"]
        from .contracts import schema_reference
        if schema_reference(schema) != contract["schema_ref"]:
            raise ValueError("installed response schema differs from its exact contract reference")
        result = check_submission(output, schema, context, extensions, workspace, mode="producer",
            execution_id=context.get("execution_id") or context.get("action", {}).get("execution_id"),
            tool_sha256=tool_hash, previous=history[-1] if history else None, clock=clock)
    except (ValueError, TypeError, KeyError, OSError) as error:
        result = _failed_check("producer", context, raw, error, phase, context.get("execution_id"))
    from .contracts import schema_reference
    result["check_subject"] = _check_subject(context)
    result["producer_sequence"] = len(history) + 1
    result["previous_producer_check_id"] = history[-1]["id"] if history else None
    result["repairs"] = _repair_links(history, result)
    result["schema_ref"] = schema_reference(schema) if schema is not None else None
    if raw is not None:
        result.update(output_sha256=hashlib.sha256(raw).hexdigest(), raw_output_path=relative)
    result["id"] = "MC-" + exact_content_hash({key: value for key, value in result.items() if key != "id"})[:24]
    try:
        check_path = safe_path(workspace, "checks/" + result["id"] + ".json")
        check_path.parent.mkdir(parents=True, exist_ok=True)
        check_path.write_bytes(canonical_json(result))
    except (ValueError, OSError) as error:
        result["passed"] = False
        result['capture_eligible'] = False
        result["issues"].append(_issue("checks", str(error), "machine_check.preservation"))
    return result


def seal_submission(workspace, draft=None, *, execution_id, context, schema, max_artifact_bytes, raw_output=None, captured_outputs=None, clock):
    """Capture one research candidate, validate those bytes, and return detached CAS artifacts."""
    workspace = Path(workspace).resolve()
    result = {"passed": False, "capture_eligible": False, "check": None, "intent": None, "manifest": [], "artifacts": {}}
    relative = None
    raw = None
    extension_raw = None
    collected = {"files": {}, "manifest": [], "omitted": []}
    phase = 'capture'
    try:
        if context.get("execution_id") != execution_id:
            raise ValueError("central context belongs to another execution")
        if raw_output is not None:
            if draft is not None or not isinstance(raw_output, bytes):
                raise ValueError("central capture requires exactly one byte source")
            raw = raw_output
            captured = {}
        else:
            draft_path = (workspace / Path(draft)).resolve(strict=False)
            if not draft_path.is_relative_to(workspace):
                raise ValueError("submission draft must be inside this workspace")
            relative = draft_path.relative_to(workspace).as_posix()
            raw = read_stable(safe_path(workspace, relative))
            captured = {} if is_excluded(Path(relative)) else {relative: raw}
        collected = (deepcopy(captured_outputs) if captured_outputs is not None else
                     collect_outputs(workspace, max_bytes=max_artifact_bytes, captured_files=captured))
        extension_raw = collected["files"].get("activity-extensions.json", canonical_json({}))
        phase = 'parse'
        output = load_json(raw)
        extensions = load_extensions(extension_raw)
        phase = 'check'
        check = check_submission(output, schema, context, extensions, workspace, mode="receiver",
            execution_id=execution_id, tool_sha256=context["submission_contract"]["tool_sha256"],
            candidate=collected, clock=clock)
        if check['issues'] and collected.get('complete'):
            check['failure_kind'] = 'output_validation'
    except (ValueError, TypeError, KeyError, OSError) as error:
        check = {**_failed_check("receiver", context, raw, error, phase, execution_id), "files": []}
        from .contracts import schema_reference
        check["schema_ref"] = schema_reference(schema)
        if phase == 'parse' and isinstance(error, (ValueError, TypeError)) and collected.get('complete'):
            check['failure_kind'] = 'output_validation'
    check.setdefault('capture_eligible', False)
    check['id'] = 'MC-' + exact_content_hash({key: value for key, value in check.items() if key != 'id'})[:24]
    artifacts = {"check.json": canonical_json(check), "manifest.json": canonical_json(collected["manifest"])}
    from .context_store import read_log_bytes
    reads = read_log_bytes(workspace)
    if reads is not None:
        # What the producer read of its input snapshot through the read tool, up to this capture.
        artifacts["reads.jsonl"] = reads
    if raw is not None:
        artifacts["output.json"] = raw
    if extension_raw is not None:
        artifacts["extensions.json"] = extension_raw
    artifacts.update({"files/" + path: data for path, data in collected["files"].items()})
    result.update(check=check, manifest=collected["manifest"], artifacts=artifacts)
    if not captured_check(check):
        return result
    identity = {"draft_path": relative, "output_sha256": hashlib.sha256(raw).hexdigest(),
        "extensions_sha256": hashlib.sha256(extension_raw).hexdigest(), "schema_ref": check["schema_ref"],
        "manifest": collected["manifest"]}
    candidate_id = "CS-" + exact_content_hash(identity)[:24]
    result.update(passed=check['passed'], capture_eligible=True, check=check, manifest=collected["manifest"], artifacts=artifacts,
        intent={"candidate_id": candidate_id, **identity})
    return result


def control_request_payload(workspace, draft, *, kind, wait_seconds, binding=None):
    """The binding and payload of one draft-locator control request, once the request may be sent.

    The kind is a submission kind, the wait is a finite nonnegative caller
    budget, the binding belongs to this workspace's execution, and the draft
    lies inside the workspace.
    """
    from .control_protocol import SUBMISSION_KINDS
    if kind not in SUBMISSION_KINDS:
        raise ValueError("unsupported submission control kind")
    if not isinstance(wait_seconds, (int, float)) or isinstance(wait_seconds, bool) or not 0 <= wait_seconds < float("inf"):
        raise ValueError("wait_seconds must be a finite nonnegative caller budget")
    workspace = Path(workspace).resolve()
    context = load_json(read_stable(safe_path(workspace, "input/submission/context.json")))
    binding = binding or context.get("control_binding")
    if not isinstance(binding, dict) or binding.get("execution_id") != context.get("execution_id"):
        raise ValueError("draft has no matching execution control binding")
    draft_path = (workspace / Path(draft)).resolve(strict=False)
    if not draft_path.is_relative_to(workspace):
        raise ValueError("submission draft must be inside this workspace")
    relative = draft_path.relative_to(workspace).as_posix()
    safe_path(workspace, relative)
    return binding, {"draft_path": relative}
