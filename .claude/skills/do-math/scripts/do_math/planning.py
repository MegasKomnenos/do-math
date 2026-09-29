"""Derived task readiness and explicit reconsideration scheduling for feature five."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any

from .activities import ACTIVITY_STATUSES
from .execution_lifecycle import EXECUTION_STATUSES
from .execution_profiles import RESEARCH_PRODUCER_ROLES
from .external import OPERATION_STATUSES
from .values import check_path_segment, is_sha256, parse_utc
from .state_contract import ARTIFACT_ROOT
from .governance import GOVERNANCE_STATUSES, GRANT_STATUSES
from .input_basis import SOURCE_STATUSES
from .repository import VERIFIED_ARTIFACTS, artifact_key, sealed_bytes
from .canonical import exact_content_hash
from .review_cycle import CYCLE_STATUSES
from .task_contracts import LIFECYCLE_STATES, TERMINAL_TASK_STATUSES
from .trust_validation import ENVIRONMENT_STATUSES
from .migration_defaults import clock_or_system


CONTRACT_FIELDS = ("id", "revision", "title", "question", "scope", "expected", "description",
                   "completion_obligations", "progress_criteria", "basis_refs", "inputs", "reuse", "dependencies", "occurrence_condition",
                   "work_class", "profile_refs", "authority_refs", "trust_environment_id",
                   "academic_requirement_id", "requirements_sha256", "solution_basis", "required_external_effects",
                   "initial_observation_rules", "model_assessment", "knowledge_revision_targets")

def contract_hash(task: dict) -> str:
    """Hash only fields whose revision approval is intended to cover."""
    return exact_content_hash({key: task[key] for key in CONTRACT_FIELDS if key in task})


# (format validator, artifact path, sha256) -> its verdict. The verdict is a function
# of the validator, the name and the bytes only; whether a repository holds those
# bytes is repository.VERIFIED_ARTIFACTS' fact. Pure, so no repository clears it.
_VALID_ARTIFACTS: dict[tuple, bool] = {}


def revision_requested(task: dict) -> bool:
    """A contract revision was requested for the task's current revision.

    The request names the revision it asked to replace, so a later revision has answered it.
    """
    requested = task.get("revision_requested")
    return isinstance(requested, dict) and requested.get("revision") == task.get("revision")


def revision_required(task: dict) -> bool:
    """A contract revision was requested, or a review of the current revision did not approve it."""
    return revision_requested(task) or any(
        review.get("revision") == task.get("revision") and review.get("decision") != "approved"
        for review in task.get("reviews", []))


def task_reference_basis(task: dict) -> dict:
    """What a result that only cites a task relied on: its contract, the results it could read and whether it was open.

    Lifecycle bookkeeping (reviews, selection, readiness, open status moves) is excluded; the receiver
    re-checks every task that a result actually selects, assesses or revises."""
    results = task.get("results", [])
    return {"id": task["id"], "contract_sha256": contract_hash(task), "result_count": len(results),
            "results_sha256": exact_content_hash(results), "terminal": task.get("status") in TERMINAL_TASK_STATUSES}


def condition_refs(condition) -> set[str]:
    if not isinstance(condition, dict):
        return set()
    refs = {condition[key] for key in ("record_id", "task_id", "from_id", "to_id", "decision_id") if isinstance(condition.get(key), str)}
    for child in condition.get("args", []):
        refs.update(condition_refs(child))
    refs.update(condition_refs(condition.get("arg")))
    return refs


# Fields through which one record reads others. Task read closures
# (action_read_ids), knowledge impact closures (knowledge._impact_refs) and
# completion assessment bases (task_scope.assessment_basis) share this table.
# A list field holds IDs or {"id": ID} references and an ID
# field holds one ID. A strict list field names records only, so an impact
# closure reports its unknown values; a lenient one may also name non-record
# inputs or locators, so an impact closure counts only its known record IDs.
READ_REFERENCE_FIELDS = {"dependencies": "strict", "inputs": "lenient", "reuse": "lenient",
                         "basis_refs": "lenient", "authority_refs": "lenient", "profile_refs": "lenient"}
READ_REFERENCE_ID_FIELDS = ("formal_result_id", "exposition_id", "trust_environment_id",
                            "kind_definition_id", "assessment_id")


def listed_reference_ids(record: dict) -> set[str]:
    """The IDs that the READ_REFERENCE_FIELDS lists of ``record`` name.

    A list entry is an ID or an {"id": ID} reference; an entry of any other shape
    names no record. Task read closures and completion assessment bases read the
    list fields through this one function."""
    return {ref if isinstance(ref, str) else ref['id'] for key in READ_REFERENCE_FIELDS
            if isinstance(record.get(key), list) for ref in record[key]
            if isinstance(ref, str) or isinstance(ref, dict) and isinstance(ref.get('id'), str)}


def action_read_ids(action: dict, instance: dict, runtime: dict, *, records=None) -> set[str]:
    """records may carry record_index() of this same state, shared by one evaluation."""
    from .relation_refs import relation_references
    records = record_index(instance, runtime) if records is None else records
    seeds = {action.get("target"), *action_write_ids(action)} - {None}
    if action.get("role") == "operational_review":
        parent = runtime.get("executions", {}).get(action.get("target"), {})
        seeds.update(row["id"] for row in parent.get("decision_basis", {}).get("records", []))
        parent_target = parent.get("action", {}).get("target")
        if parent_target is not None and not parent.get("action", {}).get("review_cycle_id"):
            seeds.add(parent_target)
    if action.get("role") == "research_plan":
        seeds.update(records)
    visited = set()
    while seeds:
        identifier = seeds.pop()
        if identifier in visited:
            continue
        visited.add(identifier)
        if identifier not in records:
            continue
        family, record = records[identifier]
        seeds.update(listed_reference_ids(record))
        # A reader also follows the provenance source that a record names.
        seeds.update(record[key] for key in (*READ_REFERENCE_ID_FIELDS, 'source_ref') if isinstance(record.get(key), str))
        if record.get('formal_result_id'):
            seeds.update(r['id'] for r in instance.get('identity_assessments',{}).values()
                         if r.get('formal_result_id')==record['formal_result_id'] and r.get('exposition_id')==record.get('exposition_id'))
        seeds.update(r['id'] for r in instance.get('assessment_uses',{}).values() if r.get('assessment_id')==identifier)
        seeds.update(condition_refs(record.get("occurrence_condition")))
        for review in record.get("reviews", []):
            seeds.update(row["id"] for row in review.get("decision_basis", {}).get("records", []))
        seeds.update(relation_references(record.get('relation_claim') or {}))
        if family == 'relation':
            seeds.update(relation_references(record))
    return visited


def action_write_ids(action: dict) -> set[str]:
    return {identifier for key in ('revision_targets', 'assessment_targets', 'observation_rule_targets')
            for identifier in action.get(key, {})}


def pending_revisions(runtime: dict) -> list[dict]:
    rows = {}
    for action in runtime.get("queue", []):
        if action_write_ids(action):
            rows[action.get("id")] = {"action": action, "state": "queued"}
    for identifier, entry in runtime.get("waiting_actions", {}).items():
        action = entry['action']
        if action_write_ids(action) and identifier not in rows:
            rows[identifier] = {"action": action, "state": "waiting",
                                "delegated_targets": entry.get("delegated_targets", {})}
    for execution in runtime.get("executions", {}).values():
        action = execution.get("action", {})
        if execution.get("status") != "ended" and action_write_ids(action):
            rows[action.get("id")] = {"action": action, "state": "running", "execution_id": execution["id"]}
    return list(rows.values())


def revision_waits(action: dict, instance: dict, runtime: dict, *, records=None) -> list[dict]:
    """Declared writers wait for existing readers and older writers; new dependent readers wait."""
    records = record_index(instance, runtime) if records is None else records
    reads = action_read_ids(action, instance, runtime, records=records)
    writes = action_write_ids(action)
    role = action.get("role")
    if role in {"operational_review", "intent_interpretation", "maintenance"}:
        return []
    own_request = runtime.get("tasks", {}).get(action.get("target"), {}).get("revision_request_action_id")
    owners = {own_request, *action.get("revision_parent_ids", [])} - {None}
    owned_targets = writes | set(runtime.get("tasks", {}).get(action.get("target"), {}).get("knowledge_revision_targets", []))
    live = [e for e in runtime.get("executions", {}).values() if e.get("status") != "ended"
            and e.get("action", {}).get("id") != action.get("id")]
    reasons = []
    for execution in live:
        overlap = writes & action_read_ids(execution.get("action", {}), instance, runtime, records=records)
        if overlap:
            reasons.append({"kind": "contract_revision", "execution_id": execution["id"],
                            "record_ids": sorted(overlap), "reason": "existing reader must finish before revision"})
    for pending in pending_revisions(runtime):
        other = pending["action"]
        if other.get("id") == action.get("id"):
            continue
        # Diagnosis and planning can resolve a failed revision. Only live writers
        # block a new global plan; their actual readers already drained above.
        if role == "research_plan" and pending["state"] != "running":
            continue
        # Unstarted writers drain oldest first. A declared writer waits only for
        # older ones, so writers reading each other's targets cannot deadlock.
        if writes and pending["state"] != "running" and other.get("id", "") > action.get("id", ""):
            continue
        overlap = reads & action_write_ids(other)
        if other.get("id") in owners:
            overlap -= owned_targets
        if overlap:
            reasons.append({"kind": "contract_revision", "action_id": other.get("id"),
                            "record_ids": sorted(overlap), "reason": "required record has an unresolved revision"})
    return reasons


def revision_cycles(instance: dict, runtime: dict) -> list[list[str]]:
    from .revisions import dependency_cycles
    rows = pending_revisions(runtime)
    records = record_index(instance, runtime)
    graph = {}
    for row in rows:
        action = row["action"]
        # A started writer waits for nothing, so only unstarted requests can close a wait cycle.
        if not action.get("id") or row["state"] == "running":
            continue
        graph[action["id"]] = {"dependencies": [wait["action_id"] for wait in revision_waits(action, instance, runtime, records=records) if wait.get("action_id")]}
    return dependency_cycles(graph)


def governance_revisions(instance: dict) -> dict:
    """Read the authoritative charter/policy editions, never caller projections."""
    from .governance import governance_view
    view = governance_view(instance)
    return {key: view[key] for key in ('goal_revision', 'policy_revision')}


def instance_record(instance: dict) -> dict:
    """The instance family's one record: its ID, goal status and governance editions.

    Conditions and task bases see this projection whether a caller holds the stored
    instance or a governance working view, so both give one readiness and one seal.
    Before a unique approved charter the editions do not exist and are absent."""
    record = {key: instance[key] for key in ("id", "goal_status") if key in instance}
    try:
        record.update(governance_revisions(instance))
    except ValueError:  # no unique approved charter yet
        pass
    return record


def contract_review_current(review: dict, task: dict, instance: dict, runtime: dict, *, task_basis=None) -> dict:
    """task_basis may carry capture_task_basis() of this task and state, shared across its reviews."""
    from .input_basis import decision_basis_changes, sources_current
    expected = {"revision": task.get("revision"), "contract_sha256": contract_hash(task),
                **governance_revisions(instance)}
    reasons = [{"field": key, "before": review.get(key), "after": value}
               for key, value in expected.items() if review.get(key) != value]
    from .contracts import contract_review_decision
    try:
        if contract_review_decision({'item_reviews':review.get('item_reviews',[])}) != review.get('decision'):
            reasons.append({'field':'item_reviews','after':'summary_does_not_match'})
    except ValueError:
        reasons.append({'field':'item_reviews','after':'incomplete_review'})
    reasons.extend(decision_basis_changes(review.get("decision_basis"), instance, runtime))
    if review.get("inputs_current") is False:
        reasons.append({"field": "inputs_current", "after": False})
    if not sources_current(review.get("source_basis", []), instance):
        reasons.append({"field": "source_basis", "after": "changed"})
    captured = review.get("task_basis")
    current = task_basis if task_basis is not None else capture_task_basis(task, instance, runtime)
    if not isinstance(captured, dict) or captured.get("common") != current["common"]:
        reasons.append({"field": "task_basis", "after": "missing_or_changed"})
    return {"valid": not reasons, "changes": reasons}


def capture_task_basis(task, instance, runtime, *, records=None):
    """Seal exact non-profile premises; profiles have independent applicability.

    records may carry record_index() of this same state, shared by one evaluation."""
    records = record_index(instance, runtime) if records is None else records
    refs = action_read_ids({"role": "task_contract_review", "target": task["id"]}, instance, runtime, records=records)
    profile_ids = [ref['id'] for ref in task.get('profile_refs', [])]
    refs -= {task["id"], *profile_ids}
    if task.get("trust_environment_id"):
        refs.add(task["trust_environment_id"])
    common = {}
    sources = record_index(instance, {}, families=(), source_aliases=True)
    from .task_contracts import available_input_refs
    # Configured availability only: host Lean discovery is a readiness fact, not a contract premise.
    configured = set(available_input_refs(instance, runtime, lean_available=False))
    for ref in sorted(refs):
        found = records.get(ref) or sources.get(ref)
        if found:
            family, record = found
            value = task_reference_basis(record) if family == "task" else record
            # Review append/selection bookkeeping never changes a dependency's contract.
            common[ref] = {"family": family, "sha256": exact_content_hash(value)}
        else:
            common[ref] = {"available": ref in configured}
    return {"common": common, "profiles": {ref: exact_content_hash(records[ref][1]) if ref in records else None for ref in profile_ids}}


def seal_contract_review(task, output, instance, runtime, *, execution_id):
    from .contracts import contract_review_decision
    from .input_basis import capture_decision_basis, capture_sources
    if execution_id == task.get("producer_execution") or execution_id in task.get("author_execution_ids", []):
        raise ValueError("contract author cannot independently review its contract")
    records = record_index(instance, runtime)
    refs = action_read_ids({"role": "task_contract_review", "target": task["id"]}, instance, runtime, records=records)
    return {"id": execution_id, "execution_id": execution_id, "revision": task["revision"],
            "decision": contract_review_decision(output), "item_reviews": deepcopy(output["item_reviews"]),
            "contract_sha256": contract_hash(task), **governance_revisions(instance), "inputs_current": True,
            "decision_basis": capture_decision_basis(instance, runtime, refs), "source_basis": capture_sources(instance, list(refs)),
            "task_basis": capture_task_basis(task, instance, runtime, records=records)}


def review_basis_key(task: dict, instance: dict, runtime: dict, *, task_basis=None) -> str:
    from .input_basis import capture_decision_basis
    records = record_index(instance, runtime)
    refs = action_read_ids({"role": "task_contract_review", "target": task["id"]}, instance, runtime, records=records)
    return exact_content_hash({"contract": contract_hash(task), **governance_revisions(instance),
                  "decision_basis": capture_decision_basis(instance, runtime, refs),
                  "task_basis": task_basis if task_basis is not None else capture_task_basis(task, instance, runtime, records=records)})


def ready_task_ids(runtime: dict, instance: dict, *, evaluation_context=None) -> list[str]:
    """The current selection population, derived for v5 rather than cached."""
    records = _shared_index(instance, runtime)
    return sorted(tid for tid, task in runtime.get("tasks", {}).items() if task_ready(task, instance, runtime,evaluation_context=evaluation_context, records=records)["state"] == "ready")


def validate_plan_submission(output: dict, tasks: dict, ready_ids: list[str]) -> None:
    """Validate the supplied planning population, before applying any decision."""
    from .task_contracts import returned_task_ids, validate_plan_dispositions
    comparison_ids = set(ready_ids) | set(returned_task_ids(tasks))
    comparison_tasks = {identifier: task for identifier, task in tasks.items()
                        if identifier in comparison_ids}
    validate_plan_dispositions(output, comparison_tasks, ready_ids)


CONDITION_FIELDS = {"always": set(), "all": {"args"}, "any": {"args"}, "not": {"arg"},
    "record_exists": {"space", "record_id", "family"}, "record_lifecycle_is": {"space", "family", "record_id", "value"},
    "record_field_equals": {"space", "family", "record_id", "pointer", "value"},
    "relation_exists": {"subkind", "from_id", "to_id"}, "task_disposition_is": {"task_id", "value"},
    "decision_value_is": {"decision_id", "value"}, "artifact_valid": {"artifact_ref"}}


def validate_condition(condition: dict) -> None:
    """Check the expression's grammar even when its referenced record is absent."""
    fields = CONDITION_FIELDS
    if not isinstance(condition, dict) or condition.get("op") not in fields:
        raise ValueError("unsupported condition op")
    op = condition["op"]
    allowed = {"op", *fields[op]}
    if set(condition) != allowed:
        raise ValueError("condition fields do not match " + op)
    if op in {"all", "any"}:
        if not isinstance(condition["args"], list) or not condition["args"]:
            raise ValueError(op + " requires nonempty args")
        for child in condition["args"]:
            validate_condition(child)
    elif op == "not":
        validate_condition(condition["arg"])
    elif op == "artifact_valid":
        ref = condition["artifact_ref"]
        if not isinstance(ref, dict) or set(ref) != {"snapshot", "path", "sha256"}:
            raise ValueError("artifact_ref requires snapshot, path, sha256")
        if not all(isinstance(value, str) and value for value in ref.values()):
            raise ValueError("artifact reference values must be text")
        if not is_sha256(ref["sha256"]):
            raise ValueError("artifact hash must be lowercase SHA256")
        # The reader accepts only archived artifacts; each segment follows the state path rule.
        if not ref["path"].startswith(ARTIFACT_ROOT):
            raise ValueError("artifact path must name an archived artifact under " + ARTIFACT_ROOT)
        for part in ref["path"].split("/"):
            check_path_segment(part)
    else:
        for name in fields[op] - {"value"}:
            if not isinstance(condition[name], str) or not condition[name].strip():
                raise ValueError("condition " + name + " must be nonempty text")
        if op == "task_disposition_is" and condition["value"] not in TERMINAL_TASK_STATUSES:
            raise ValueError("task disposition must be completed or closed")
        if op == "record_field_equals" and (not condition["pointer"].startswith("/") or isinstance(condition["value"], (dict, list))):
            raise ValueError("record comparison needs a pointer and scalar value")
        if "space" in condition and condition["space"] not in {"research", "runtime"}:
            raise ValueError("unknown condition space")
        if "family" in condition and condition["family"] not in RECORD_FAMILIES:
            raise ValueError("unknown condition family")
        if "family" in condition and RECORD_FAMILIES[condition["family"]][0] != condition["space"]:
            raise ValueError("condition family is outside the requested space")
        if op == "record_lifecycle_is":
            values = lifecycle_values().get(condition['family'],set())
            if condition["value"] not in values:
                raise ValueError("value is not a lifecycle value of this family")
        if op=='record_field_equals':
            family,pointer=condition['family'],condition['pointer']
            if pointer not in EXPOSED_FIELDS.get(family,set()):
                raise ValueError('pointer is not an exposed machine field')
            if pointer == '/usable_as_k' and type(condition['value']) is not bool:
                raise ValueError('usable_as_k comparison requires a boolean')
            if pointer in {'/status','/lifecycle'} and condition['value'] not in lifecycle_values().get(family,set()):
                raise ValueError('value is not a lifecycle value of this family')


RECORD_FAMILIES = {"knowledge": ("research", "knowledge"), "governance": ("research", "governance"),
    "goal-judgment": ("research", "goal_judgments"),
    "grant": ("research", "grants"), "decision": ("research", "decisions"), "source": ("research", "sources"),
    "trust-environment": ("research", "trust_environments"), "execution-profile": ("research", "execution_profiles"),
    "formal-result": ("research", "formal_results"), "exposition": ("research", "expositions"),
    "identity-assessment": ("research", "identity_assessments"), "assessment-use": ("research", "assessment_uses"),
    "governance-source": ("research", "governance_sources"), "kind-definition": ("research", "kind_definitions"),
    "relation": ("research", "relations"),
    "task": ("runtime", "tasks"), "activity": ("runtime", "activities"), "execution": ("runtime", "executions"),
    "external-operation": ("runtime", "external_operations"), "review-cycle": ("runtime", "review_cycles"),
    "instance": ("research", None)}


def lifecycle_values():
    """The condition grammar's state values per family: the owners' constants,
    which the storage schema also uses. The knowledge-family owners import this
    module, so their constants are read on first use."""
    from .knowledge_io import KIND_STATUSES
    from .knowledge_records import ASSESSMENT_USE_STATUSES, RECORD_LIFECYCLES
    return {
        'task': LIFECYCLE_STATES,
        'knowledge': RECORD_LIFECYCLES, 'exposition': RECORD_LIFECYCLES,
        'governance': GOVERNANCE_STATUSES, 'grant': GRANT_STATUSES,
        'source': SOURCE_STATUSES, 'trust-environment': ENVIRONMENT_STATUSES,
        'activity': ACTIVITY_STATUSES,
        'execution': EXECUTION_STATUSES,
        'assessment-use': ASSESSMENT_USE_STATUSES,
        'kind-definition': KIND_STATUSES,
        'external-operation': OPERATION_STATUSES,
        'review-cycle': CYCLE_STATUSES,
    }


EXPOSED_FIELDS = {
    'goal-judgment': {'/decision', '/current'},
    'knowledge': {'/lifecycle','/kind','/kind_use_suspended','/usable_as_k'}, 'task': {'/status','/revision'},
    'activity': {'/status','/activity_kind'}, 'execution': {'/status','/role','/outcome'},
    'governance': {'/status'}, 'grant': {'/status'}, 'decision': {'/kind'},
    'external-operation': {'/status','/http_status','/succeeded'}, 'source': {'/status','/revision','/sha256'},
    'trust-environment': {'/status'}, 'review-cycle': {'/status','/decision','/phase'},
    'instance': {'/goal_status','/goal_revision','/policy_revision'},
    'formal-result': {'/publication_state','/formal_use'}, 'exposition': {'/lifecycle'},
    'identity-assessment': {'/decision'}, 'assessment-use': {'/status'}, 'kind-definition': {'/status','/token'},
}


def record_index(instance: dict, runtime: dict, *, families=None, source_aliases=False,
                 question_links=False) -> dict[str, tuple[str, dict]]:
    """Map record IDs to (family, record): the one population definition of RECORD_FAMILIES.

    families narrows the index to the named RECORD_FAMILIES keys. A duplicate ID
    raises ValueError. question_links adds question rows as family "question";
    source_aliases then adds each source alias that no entry already claims as
    family "source". Neither extra is a condition family or a read-closure seed.
    """
    found: dict[str, tuple[str, dict]] = {}
    for family, (space, key) in RECORD_FAMILIES.items():
        if families is not None and family not in families:
            continue
        if key is None:
            container = [instance_record(instance)] if instance.get("id") else []
        else:
            container = (instance if space == "research" else runtime).get(key, {})
        values = container.values() if isinstance(container, dict) else container if isinstance(container, list) else []
        for record in values:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                if record["id"] in found:
                    raise ValueError("globally duplicate record ID: " + record["id"])
                found[record["id"]] = (family, record)
    if question_links:
        for row in runtime.get("question_links", []):
            if row["id"] in found:
                raise ValueError("globally duplicate record ID: " + row["id"])
            found[row["id"]] = ("question", row)
    if source_aliases:
        from .input_basis import aliases
        for source in instance.get("sources", []):
            for alias in aliases(source):
                found.setdefault(alias, ("source", source))
    return found


def _shared_index(instance: dict, runtime: dict):
    """One index for a loop of readiness evaluations; None lets each evaluation report the error."""
    try:
        return record_index(instance, runtime)
    except (ValueError, TypeError, KeyError):
        return None


def _record_target(records: dict[str, tuple[str, dict]], identifier: str, family: str) -> tuple[str, dict] | None:
    """The condition target in this evaluation's validated record index, or None when it is absent."""
    found = records.get(identifier)
    if found and found[0] != family:
        raise ValueError('existing record belongs to another family: '+identifier)
    return found


def _basis(record: dict) -> dict: return {"id": record["id"], "sha256": exact_content_hash(record), "status": record.get("status", record.get("lifecycle"))}


def _pointer(record: dict, pointer: str) -> Any:
    """The scalar machine field at pointer; validate_condition admitted the pointer for this record's family."""
    value: Any = record
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value: raise KeyError(pointer)
        value = value[token]
    if isinstance(value, (dict, list)): raise ValueError("pointer must name a scalar machine field")
    if isinstance(value,bool): return value
    if not isinstance(value,(str,int,float)) or isinstance(value,float) and not value.is_integer(): raise ValueError("pointer must name a scalar machine field")
    return value


def evaluate_condition(condition: dict, instance: dict, runtime: dict, *, evaluation_context=None, records=None) -> dict:
    """Evaluate a closed readiness AST without treating malformed evidence as true.

    records may carry record_index() of this same state, shared by one evaluation."""
    basis, errors = [], []
    try:
        records = record_index(instance, runtime) if records is None else records
        validate_condition(condition)
    except (ValueError, TypeError) as error:
        return {"state": "evaluation_error", "basis": [], "errors": [str(error)]}
    def visit(node: dict) -> str:
        # validate_condition has checked every node's op, fields and nonempty args above.
        try:
            op = node["op"]
            if op == "always": return "ready"
            if op in {"all", "any"}:
                results = [visit(x) for x in node["args"]]
                if "evaluation_error" in results: return "evaluation_error"
                return "ready" if (all(x == "ready" for x in results) if op == "all" else any(x == "ready" for x in results)) else "not_ready"
            if op == "not":
                result = visit(node.get("arg"))
                return "evaluation_error" if result == "evaluation_error" else "not_ready" if result == "ready" else "ready"
            if op == "relation_exists":
                from .knowledge_io import validate_stored_relation
                candidates = [r for r in instance.get("relations", []) if isinstance(r, dict) and r.get("kind") == node.get("subkind") and r.get("source") == node.get("from_id") and r.get("target") == node.get("to_id")]
                matches = []
                for relation in candidates:
                    basis.append(_basis(relation))
                    if relation.get("status", "active") in {"suspended", "withdrawn", "invalid"} or relation.get("use_status", "active") in {"suspended", "withdrawn"}:
                        continue
                    result = validate_stored_relation(instance, relation)
                    unavailable = ("formal_result_not_usable:", "assessment_not_effective:")
                    structural = [reason for reason in result["reasons"] if not reason.startswith(unavailable)]
                    if structural:
                        raise ValueError("invalid relation: " + ", ".join(structural))
                    from .relation_refs import relation_references
                    for record_id in sorted(relation_references(relation)):
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
                record = _record_target(records, node.get("task_id"), "task")
                if record is None: basis.append({"absencequery": {"op": op, "task_id": node.get("task_id")}}); return "not_ready"
                basis.append(_basis(record[1])); return "ready" if record[1].get("status") == node.get("value") else "not_ready"
            if op == "decision_value_is":
                record = _record_target(records, node.get("decision_id"), "decision")
                if record is None:
                    basis.append({"absencequery": {"op": op, "decision_id": node.get("decision_id")}})
                    return "not_ready"
                decision = record[1]
                basis.append(_basis(decision))
                from .task_scope import decision_is_current
                effective = decision_is_current(decision, instance, runtime, evaluation_context=evaluation_context)
                scope=decision.get('change',{}).get('task_id')
                if scope and scope!=(evaluation_context or {}).get('task_id'):
                    effective=False
                value = decision.get("change", {}).get("value", decision.get("change"))
                return "ready" if effective and type(value) is type(node["value"]) and value == node["value"] else "not_ready"
            if op == "artifact_valid":
                context, ref = evaluation_context or {}, node["artifact_ref"]
                if not context.get("snapshot") or not callable(context.get("read_artifact")) or not callable(context.get("validate_artifact")):
                    raise ValueError("artifact requires a fixed-snapshot reader and format validator")
                # Sealed bytes never change: this repository matches them once
                # (이음새-정본.md §3) and a known verdict needs no bytes at all.
                git_dir, verdict = context.get("git_dir"), (context["validate_artifact"], ref["path"], ref["sha256"])
                valid = _VALID_ARTIFACTS.get(verdict)
                data = sealed_bytes(git_dir, ref["path"], ref["sha256"], None,
                                    lambda: context["read_artifact"](ref["path"], ref["snapshot"]),
                                    needed=valid is None, error="artifact bytes differ from sealed hash")
                if valid is None:
                    valid = _VALID_ARTIFACTS[verdict] = context["validate_artifact"](ref, data) is True
                if not valid:
                    raise ValueError("artifact format validation failed")
                size = len(data) if data is not None else VERIFIED_ARTIFACTS[artifact_key(git_dir, ref["path"], ref["sha256"])]
                basis.append({"artifact_ref": deepcopy(ref), "bytes": size})
                return "ready"
            record = _record_target(records, node.get("record_id"), node.get("family"))
            if op == "record_exists":
                if record is None: basis.append({"absencequery": {"op": op, "record_id": node.get("record_id"), "family": node.get("family")}}); return "not_ready"
                basis.append(_basis(record[1])); return "ready"
            if record is None: basis.append({"absencequery": {"op": op, "record_id": node.get("record_id")}}); return "not_ready"
            basis.append(_basis(record[1]))
            if op == "record_lifecycle_is": return "ready" if record[1].get("lifecycle", record[1].get("status")) == node.get("value") else "not_ready"
            if op == "record_field_equals":
                if record[0] == 'knowledge' and node['pointer'] == '/usable_as_k':
                    from .knowledge import assess_use
                    actual = assess_use(record[1], instance)['valid']
                else:
                    actual = _pointer(record[1], node["pointer"])
                expected = node.get("value")
                return "ready" if type(actual) is type(expected) and actual==expected else "not_ready"
            raise ValueError(f"unsupported condition op: {op}")
        except (KeyError, TypeError, ValueError, OSError) as error:
            errors.append(str(error)); return "evaluation_error"
    state = visit(condition)
    return {"state": state, "basis": basis, "errors": errors}


def instance_ended(instance: dict, runtime: dict) -> bool:
    """Closed or completed research: no lifecycle control, dispatch or task readiness applies any more."""
    return (runtime.get('status') in {'closed', 'completed'}
            or bool(instance.get('lifecycle', {}).get('permanently_closed')))


# The readiness error of a task whose current revision has no approved contract
# review. task_ready and the readiness refresh (lifecycle_engine) state it;
# status (reporting.task_status) reads it as a contract review wait.
CONTRACT_REVIEW_MISSING = "current revision lacks approved contract review"


def task_ready(task: dict, instance: dict, runtime: dict, *, include_scheduling_waits=True,
               action=None, evaluation_context=None, records=None) -> dict:
    """The same live predicate serves population, receipt, and pre-start checks.

    include_scheduling_waits=False skips occupancy only, never user/revision gates.
    The owning request is excluded explicitly using action.id. records may carry
    record_index() of this same state; one index serves the whole evaluation.
    """
    from .task_contracts import validate_task_contract, returned_task_ids
    try:
        validate_task_contract(task)
        records = record_index(instance, runtime) if records is None else records
    except (ValueError, TypeError, KeyError) as error:
        return {"state": "evaluation_error", "basis": [], "errors": [str(error)]}
    action = action or {"role": "research_work", "target": task["id"]}
    from .questions import user_waits
    waits = user_waits(action, instance, runtime, records=records)
    if waits:
        return {"state": "not_ready", "basis": [], "errors": ["an explicit user decision is required"], "waits": waits}
    if instance.get("goal_status") == "mathematically_solved" and not task.get("academic_requirement_id"):
        return {"state": "not_ready", "basis": [], "errors": ["research production stopped after goal satisfaction"]}
    if task.get("status") not in LIFECYCLE_STATES - TERMINAL_TASK_STATUSES:
        return {"state": "not_ready", "basis": [], "errors": ["task state is not schedulable"]}
    if revision_requested(task):
        return {"state": "not_ready", "basis": [], "errors": ["a contract revision was requested by " + str(task["revision_requested"].get("source")) + "; awaiting a new revision"]}
    revision = task.get("revision")
    reviews = task.get("reviews", [])
    approved = [r for r in reviews if r.get("revision") == revision and r.get("decision") == "approved" and r.get("inputs_current", True)]
    try:
        task_basis = capture_task_basis(task, instance, runtime, records=records) if approved else None
        approved = [r for r in approved if contract_review_current(r, task, instance, runtime, task_basis=task_basis)["valid"]]
    except (ValueError, KeyError, TypeError) as error:
        return {"state": "evaluation_error", "basis": [], "errors": [str(error)]}
    if not approved: return {"state": "not_ready", "basis": [], "errors": [CONTRACT_REVIEW_MISSING]}
    waits = revision_waits(action, instance, runtime, records=records)
    if waits:
        return {"state": "not_ready", "basis": [], "errors": ["required record has an unresolved revision"], "waits": waits}
    from .task_contracts import available_input_refs, unsupplied_task_inputs
    available = available_input_refs(instance, runtime,
        lean_available=(evaluation_context or {}).get("lean_available", False))
    missing = unsupplied_task_inputs([*task.get("inputs", []), *task.get("reuse", [])],
                                     {*available, *records}, admit_named_sources=False)
    if missing: return {"state": "not_ready", "basis": [], "errors": ["missing inputs: " + ",".join(missing)],
        'waits':[{'kind':'external_event','target_refs':missing,'next_owner':'research_preparation'}]}
    blocked = [dep for dep in {*task.get("dependencies", []), *task.get("reuse", [])}
               if dep not in records or records[dep][1].get("use_suspended")
               or records[dep][1].get("status") in {"blocked", "withdrawn", "invalid", "use_suspended"}
               or (records[dep][0] == "task" and dep in task.get("dependencies", []) and
                   (records[dep][1].get("status") != "completed" or
                    records[dep][1].get("assessment", {}).get("current") is False))]
    if blocked: return {"state": "not_ready", "basis": [], "errors": ["blocked dependencies: " + ",".join(blocked)]}
    from .task_scope import assessment_current
    for dep in task.get('dependencies',[]):
        if records[dep][0]=='task' and not assessment_current(records[dep][1],instance,runtime,evaluation_context=evaluation_context,records=records):
            return {'state':'not_ready','basis':[],'errors':['dependency lacks a current completion assessment: '+dep]}
    from .knowledge import assess_research_use
    for ref in task.get("reuse", []):
        if records[ref][0] == "knowledge" and not assess_research_use(records[ref][1], instance).get("valid"):
            return {"state": "not_ready", "basis": [], "errors": ["unusable knowledge: " + ref]}
    from .governance import authorize
    authority_action={**action,'id':action.get('id') or 'readiness:'+task['id']}
    grants = [authorize(instance, {**authority_action, "grant_id": ref}, (evaluation_context or {}).get("now"), runtime=runtime)
              for ref in task.get("authority_refs", []) if ref in instance.get("grants", {})]
    if not any(grant["allowed"] for grant in grants):
        return {"state": "not_ready", "basis": [], "errors": ["no contract authority permits this work"],
            'waits':[{'kind':'permission','target_refs':task.get('authority_refs',[]),'next_owner':'governance'}]}
    from .execution_profiles import profile_ref, match_profile_ref
    profiles = []
    for ref in task.get("profile_refs", []):
        try:
            profile = match_profile_ref(instance.get('execution_profiles', {}), ref)
        except ValueError:
            continue
        if profile.get('role') != action['role']:
            continue
        if any(review.get("task_basis", {}).get("profiles", {}).get(ref['id']) == exact_content_hash(profile) for review in approved):
            profiles.append(ref['id'])
    selected = action.get("profile_ref")
    if not profiles or (selected and (not isinstance(selected,dict) or selected.get("id") not in profiles or
                                     selected != profile_ref(instance['execution_profiles'][selected['id']]))):
        return {"state": "not_ready", "basis": [], "errors": ["no current approved execution profile"]}
    from .model_policy import work_profile_selection
    try:
        selected_work = work_profile_selection(instance['config'], task,
            instance, action=action)
        if selected_work['profile_ref']['id'] not in profiles:
            raise ValueError('required work profile is outside the current contract approval')
    except (ValueError, KeyError) as error:
        return {'state': 'not_ready', 'basis': [],
                'errors': ['work profile requirement: ' + str(error)],
                'waits': [{'kind': 'contract_revision', 'target_refs': [task['id']],
                           'next_owner': 'research_preparation'}]}
    if task.get("work_class") == "formal":
        trust = instance.get("trust_environments", {}).get(task.get("trust_environment_id"))
        if not trust or trust.get("status") != "active" or instance.get('active_trust_environment') != task.get('trust_environment_id'):
            return {"state": "not_ready", "basis": [], "errors": ["formal task lacks its fixed active trust environment"]}
    if include_scheduling_waits:
        if task["id"] in returned_task_ids(runtime.get("tasks", {})):
            return {"state": "not_ready", "basis": [], "errors": ["returned work requires assessment"]}
        occupied = [e for e in runtime.get("executions", {}).values() if e.get("status") != "ended"
                    and e.get("action", {}).get("target") == task["id"] and e.get("action", {}).get("id") != action.get("id")]
        queued = [a for a in runtime.get("queue", []) if a.get("target") == task["id"] and a.get("role") in RESEARCH_PRODUCER_ROLES and a.get("id") != action.get("id")]
        waiting = task.get("waiting")
        continuation=bool(waiting and waiting.get('kind')=='research_followup' and
                          waiting.get('basis_ref')==task.get('assessment',{}).get('execution_id') and
                          assessment_current(task,instance,runtime,evaluation_context=evaluation_context,records=records))
        if occupied or queued or (waiting and not continuation):
            normal = bool(occupied or queued) and (not waiting or continuation)
            normal = normal and all(e.get('role', e.get('action', {}).get('role')) in
                RESEARCH_PRODUCER_ROLES for e in occupied)
            normal = normal and not any(w.get('action', {}).get('target') == task['id']
                                        for w in runtime.get('waiting_actions', {}).values())
            if normal:
                normal = evaluate_condition(task.get('occurrence_condition', {'op': 'always'}), instance, runtime,
                    evaluation_context={**(evaluation_context or {}), 'task_id': task['id']}, records=records)['state'] == 'ready'
            return {"state": "not_ready", "basis": [], "errors": ["task is occupied or has an unresolved wait"],
                    "waits": [waiting] if waiting else [], 'dispatch_occupied': normal}
        if task.get("status") in {"active", "waiting"} and not action.get("id") and not continuation:
            return {"state": "not_ready", "basis": [], "errors": ["subsequent work needs an explicit continuation basis"]}
    result = evaluate_condition(task.get("occurrence_condition", {"op": "always"}), instance, runtime,
                                evaluation_context={**(evaluation_context or {}),'task_id':task['id']}, records=records)
    result["profile_ids"] = profiles
    if result['state']=='not_ready' and not result['errors']:
        result['waits']=[{'kind':'condition','target_refs':sorted(condition_refs(task['occurrence_condition'])),'next_owner':'scheduler'}]
    result["basis"].extend(_basis(x) for x in approved if isinstance(x, dict) and "id" in x)
    return result


def exhaustion_state(instance, runtime, *, now=None, evaluation_context=None):
    """Exhaustion concerns unresolved research, never the queue alone."""
    answer={'exhausted':False,'prepare':False,'reasons':[],'next_owner':None}
    if runtime.get('status') != 'active' or instance.get('goal_status') == 'mathematically_solved':
        return answer
    roles={'research_work','supplemental_research','research_preparation','task_contract_review','formal_check','identity_review'}
    requests=[a for a in runtime.get('queue',[]) if a.get('role') in roles]
    requests += [e.get('action',{}) for e in runtime.get('executions',{}).values() if e.get('role') in roles and e.get('status')!='ended']
    requests += [w.get('action',{}) for w in runtime.get('waiting_actions',{}).values() if w.get('action',{}).get('role') in roles]
    if requests:
        answer['reasons'].append('unfinished_research_requests'); return answer
    records=_shared_index(instance,runtime)
    evaluations={tid:task_ready(t,instance,runtime,evaluation_context=evaluation_context,records=records) for tid,t in runtime.get('tasks',{}).items() if t.get('status') not in TERMINAL_TASK_STATUSES}
    if any(r['state']=='ready' for r in evaluations.values()):
        answer['reasons'].append('ready_contracts'); return answer
    if any(r['state']=='evaluation_error' for r in evaluations.values()):
        answer.update(reasons=['readiness_evaluation_error'],next_owner='operational_review'); return answer
    observed_waits=[w for result in evaluations.values() for w in result.get('waits',[]) if w.get('kind') in
                    {'external_event','user_decision','permission','condition'}]
    if observed_waits:
        answer.update(reasons=['external_waits'],next_owner=observed_waits[0].get('next_owner'),waiting_basis=observed_waits);return answer
    from .task_contracts import returned_task_ids
    if returned_task_ids(runtime.get('tasks',{})):
        answer.update(reasons=['returned_work_requires_assessment'],next_owner='research_plan');return answer
    unfinished=[t for t in runtime.get('tasks',{}).values() if t.get('status') not in TERMINAL_TASK_STATUSES]
    external=[t for t in unfinished if t.get('waiting',{}).get('kind') in {'external_event','user_decision','assessment_input','permission','condition'}]
    if external:
        answer.update(reasons=['external_waits'],next_owner=external[0]['waiting'].get('next_owner')); return answer
    receipts=[r for r in runtime.get('history',[]) if r.get('kind')=='task_repetition' and r.get('lineage')=='exhaustion_empty']
    answer['exhausted']=True
    answer['basis']={'tasks':{tid:{'contract_sha256':contract_hash(t),'results_sha256':exact_content_hash(t.get('results',[])),
        'waiting':deepcopy(t.get('waiting'))} for tid,t in runtime.get('tasks',{}).items()},
        'governance':deepcopy(instance.get('governance', {})),
        'source_hashes':{s.get('id',s.get('path')):s.get('sha256') for s in instance.get('sources',[])},
        'last_preparation':deepcopy(receipts[-1]) if receipts else None}
    if receipts and receipts[-1].get('outcome')=='empty':
        receipt=receipts[-1]
        from .revisions import repetition_hold
        hold = repetition_hold(runtime,'exhaustion_empty',receipt['lineage_id'])
        if hold:
            answer.update(reasons=['exhaustion_lineage_hold'],next_owner=hold['next_owner']);return answer
        if not receipt.get('regenerate_after'):
            answer.update(reasons=['regeneration_condition_missing'],next_owner='research_plan');return answer
        instant=parse_utc(now) if now else clock_or_system(None).wall()
        if instant < parse_utc(receipt['regenerate_after']):
            answer.update(reasons=['regeneration_guard'],reobserve_at=receipt['regenerate_after']);return answer
    answer.update(prepare=True,next_owner='research_preparation');return answer


def research_wake_reasons(instance, runtime, *, now, evaluation_context=None):
    """Read-only wake decision over the same snapshot used for status."""
    if (instance.get('lifecycle', {}).get('state') != 'active'
            or runtime.get('status') != 'waiting'
            or runtime.get('user_pause') or instance.get('goal_status') == 'mathematically_solved'):
        return []
    reasons = [{'kind': event['kind'], 'event_id': event['id']}
               for event in collect_due_events(instance, runtime, now)]
    state = exhaustion_state(instance, {**runtime, 'status': 'active'},
                             now=now, evaluation_context=evaluation_context)
    from .questions import user_waits
    if state['prepare'] and not user_waits({'role': 'research_preparation'}, instance, runtime):
        reasons.append({'kind': 'research_regeneration_due'})
    return reasons


def schedule_reconsideration(instance, runtime, *, now, evaluation_context=None, clock=None):
    """Assign preserved due events and exhaustion reasons, coalescing only unstarted preparation.

    Due events are recorded beforehand by record_due_events, their one collection path."""
    clock = clock_or_system(clock)
    state=exhaustion_state(instance,runtime,now=now,evaluation_context=evaluation_context)
    if runtime.get('status')!='active' or instance.get('goal_status')=='mathematically_solved': return state
    exhaustion_event=None
    if state['exhausted']:
        basis_sha256=exact_content_hash(state['basis'])
        exhaustion_event=next((e for e in runtime['events'] if e.get('kind')=='research_exhausted' and e.get('basis_sha256')==basis_sha256),None)
        if not exhaustion_event:
            exhaustion_event={'id':clock.new_id('EV'),'kind':'research_exhausted','observed_at':now,
                'basis_sha256':basis_sha256,'basis':deepcopy(state['basis']),'regenerate_after':state.get('reobserve_at')}
            runtime['events'].append(exhaustion_event)
    held=assigned_event_refs(runtime)
    pending=[e for e in runtime.get('events',[]) if e['id'] in runtime.get('pending_events',[]) and e['id'] not in held]
    periodic=[e['id'] for e in pending if e.get('kind')=='research_reconsider_due']
    selection_events=[e['id'] for e in pending if e.get('kind') in {'task_revisit_due','task_new_input'}]
    if periodic or state['prepare']:
        role='research_preparation'
    else:
        role='research_plan' if selection_events else state.get('next_owner') if state.get('next_owner') in {'research_plan','operational_review'} else None
    if not role: return state
    # A missing regeneration condition needs one decision on this exact basis.
    # Finishing that decision does not itself supply a new research premise.
    # Failed attempts retain their explicit repair/retry owner as well.
    if exhaustion_event and not state['prepare'] and not periodic and not selection_events:
        if any(e.get('action', {}).get('exhaustion_event_ref') == exhaustion_event['id']
               for e in runtime.get('executions', {}).values()):
            return state
    if any(e.get('role')==role and e.get('status')!='ended' for e in runtime.get('executions',{}).values()): return state
    from .model_policy import preparation_only
    queued = next((a for a in runtime.setdefault('queue', []) if a.get('role') == role
                   and (role != 'research_preparation' or not preparation_only(a))), None)
    if not queued:
        queued={'id':clock.new_id('AC'),'role':role,'reason':'research reconsideration','event_refs':[]}
        runtime['queue'].append(queued)
    assigned=periodic if role=='research_preparation' else selection_events
    queued['event_refs']=list(dict.fromkeys([*queued.get('event_refs',[]),*assigned]))
    if exhaustion_event:
        queued['exhaustion_basis']=deepcopy(state)
        queued['exhaustion_event_ref']=exhaustion_event['id']
    if state['prepare']:
        from .revisions import bind_repetition_bases
        bind_repetition_bases(instance,runtime,queued)
    if periodic:
        queued['periodic_reconsideration']=True
        seconds=instance['config']['research_reconsider_seconds']
        runtime['next_research_reconsider_at']=(parse_utc(now)+timedelta(seconds=seconds)).isoformat()
    return state


def _event(kind: str, when: str, target: str | None = None, *, key: str | None = None) -> dict:
    """A due event whose ID is derived from key (default: when), so one cause is one event."""
    seed = f"{kind}|{when if key is None else key}|{target or ''}"
    return {"id": hashlib.sha256(seed.encode()).hexdigest()[:24], "kind": kind, "at": when, "target": target}


def collect_due_events(instance: dict, runtime: dict, now_iso: str) -> list[dict]:
    now = parse_utc(now_iso); events = []
    if instance.get("goal_status") != "mathematically_solved":
        due = runtime.get("next_research_reconsider_at")
        if due and parse_utc(due) <= now: events.append(_event("research_reconsider_due", due))
    for task in runtime.get("tasks", {}).values():
        if not isinstance(task, dict): continue
        disposition=task.get('selection_disposition',{})
        revisit=disposition.get('revisit',{})
        if disposition.get('kind') in {'not_selected','not_assessable'}:
            references={e.get('id') for e in runtime.get('events',[])}
            triggers=sorted(set(revisit.get('event_refs',[])) & references)
            if (revisit.get('at') and parse_utc(revisit['at'])<=now) or triggers:
                event=_event('task_revisit_due',exact_content_hash({'decision':disposition.get('execution_id'),'revisit':revisit,'triggers':triggers}),task.get('id'))
                event.update(observed_at=now_iso,basis=deepcopy(disposition));events.append(event)
        if task.get("newinput"):
            # One input request is one event however often its task is observed.
            event = _event("task_new_input", now_iso, task.get("id"), key=task["newinput"])
            event["request_id"] = task["newinput"]
            events.append(event)
    existing = {event.get("id") for event in runtime.get("events", [])}
    return [event for event in events if event["id"] not in existing]


def record_due_events(instance: dict, runtime: dict, now_iso: str) -> list[dict]:
    """Preserve each due event once in runtime, in place, and return the new ones.

    This is the one collection path; paused research keeps them pending."""
    events = collect_due_events(instance, runtime, now_iso)
    runtime.setdefault("events", []).extend(events)
    pending = runtime.setdefault("pending_events", [])
    pending.extend(event["id"] for event in events if event["id"] not in pending)
    return events


def assigned_event_refs(runtime: dict) -> set[str]:
    """The events that a queued, live or waiting request already names in its event_refs.

    Request event_refs are the one record of assignment; event records carry no
    assignment mark. Assignment is not consumption: the owning engine consumes
    only the event_refs of an accepted execution's input."""
    requests = [*runtime.get('queue', []),
                *(e.get('action', {}) for e in runtime.get('executions', {}).values() if e.get('status') != 'ended'),
                *(w['action'] for w in runtime.get('waiting_actions', {}).values() if 'action' in w)]
    return {ref for action in requests for ref in action.get('event_refs', [])}
