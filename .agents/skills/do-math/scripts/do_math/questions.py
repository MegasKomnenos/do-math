"""Source-linked questions and explicitly scoped user decision requirements."""
from copy import deepcopy

from .migration_defaults import clock_or_system

# Who answers a question: the user, the research roles or the operational roles.
QUESTION_OWNERS = frozenset({"user", "research", "operations"})
# The roles that own operations questions.
OPERATIONS_ROLES = frozenset({"operational_review", "maintenance"})


def open_links(runtime, owner=None):
    return [row for row in runtime.get("question_links", []) if row["status"] == "open" and (owner is None or row["owner"] == owner)]


def open_targets(row):
    """The question targets that no applied resolution has covered yet."""
    return row["unresolved_target_ids"]


def user_waits(action, instance, runtime, *, records=None):
    """records may carry planning.record_index() of this same state."""
    if action.get("role") in {"intent_interpretation", "operational_review", "maintenance"}:
        return []
    from .planning import action_read_ids
    reads = set() if action.get("role") == "research_plan" else action_read_ids(action, instance, runtime, records=records)
    targets = reads | {action.get("target"), action.get("id"), instance.get("id")}
    retry = action.get("input_overflow_retry", {})
    retry_question = retry.get("question_id") if retry.get("state", "pending") == "pending" else None
    return [{"kind": "user_decision", "question_id": row["id"], "target_ids": open_targets(row), "next_owner": "user"}
            for row in open_links(runtime, "user") if row["id"] != retry_question and row.get("blocks", False)
            and targets & set(open_targets(row))]


def link(runtime, *, execution_id, field, owner, targets, source_ref=None, reason=None, blocks=False, checked_by=None, clock=None):
    clock = clock_or_system(clock)
    if owner not in QUESTION_OWNERS or type(blocks) is not bool:
        raise ValueError("question owner and blocking decision required")
    if not isinstance(targets, list) or any(not isinstance(t, str) or not t for t in targets) or (blocks and not targets):
        raise ValueError("blocking questions require explicit affected targets")
    rows = runtime.setdefault("question_links", [])
    existing = next((row for row in rows if row["origin_execution_id"] == execution_id and row["origin_field"] == field), None)
    if existing:
        if (existing["owner"], existing["target_ids"], existing.get("blocks", False)) != (owner, list(dict.fromkeys(targets)), blocks):
            raise ValueError("question source cannot be rerouted silently")
        return existing
    row = {"id": clock.new_id("QU"), "origin_execution_id": execution_id, "origin_field": field,
           "owner": owner, "target_ids": list(dict.fromkeys(targets)), "unresolved_target_ids": list(dict.fromkeys(targets)),
           "blocks": blocks, "status": "open", "resolution_ref": None, "checked_by": checked_by}
    if source_ref:
        row["source_ref"] = source_ref
    if reason:
        row["routing_reason"] = reason
    rows.append(row)
    return row


def close(row, *, kind, resolution_ref, affected_ids, status="resolved", evidence=None):
    """The only resolving transition: resolve affected targets, closing the question with its last one.

    Every closing path appends the same history entry shape."""
    remaining = set(open_targets(row)) - set(affected_ids)
    row["unresolved_target_ids"] = [target for target in row["target_ids"] if target in remaining]
    entry = {"kind": kind, "resolution_ref": resolution_ref,
             "affected_ids": sorted(set(affected_ids) & set(row["target_ids"]))}
    if evidence is not None:
        entry["evidence"] = deepcopy(evidence)
    row.setdefault("resolution_history", []).append(entry)
    if not remaining:
        row.update(status=status, resolution_ref=resolution_ref)


def resolution_error(row, role):
    """Why an AI extension cannot resolve this question row now; None when it can.

    Submission checks call this on the fixed input, and application calls it again
    because another execution may have closed the question in between."""
    if not row or row["status"] != "open" or row["owner"] not in QUESTION_OWNERS - {"user"}:
        return "only distinct open research or operations questions can be resolved by an AI extension"
    if row["owner"] == "operations" and role not in OPERATIONS_ROLES:
        return "an operations question requires an operational role"
    return None


def resolve_user(runtime, identifiers, *, resolution_ref, affected_ids):
    questions = {row["id"]: row for row in runtime.get("question_links", [])}
    if not isinstance(identifiers, list) or len(identifiers) != len(set(identifiers)):
        raise ValueError("resolves_questions must be distinct question IDs")
    for identifier in identifiers:
        row = questions.get(identifier)
        if not row or row["owner"] != "user" or row["status"] != "open":
            raise ValueError("user decision must name an open user question: " + str(identifier))
        if not set(open_targets(row)) & set(affected_ids):
            raise ValueError("the applied decision does not affect the question target: " + identifier)
    for identifier in identifiers:
        close(questions[identifier], kind="user_decision", resolution_ref=resolution_ref, affected_ids=affected_ids)


def validate_extensions(output, extensions, context):
    # A route target is an ID the role may use (공통-실행.md 「시작할 때 입력을 확인한다」):
    # a supplied input reference, a record the input shows, or a record of its record_index.
    # The citation check reads the same population through the same two functions.
    from .submission import record_index_ids, supplied_reference_ids
    errors = []
    known = supplied_reference_ids(context) | record_index_ids(context) | set(context.get("available_input_refs", []))
    indices = set()
    for route in extensions.get("question_routes", []):
        index = route["question_index"]
        if index in indices or not 0 <= index < len(output.get("questions", [])):
            errors.append({"path": "question_routes", "message": "route each supplied question index at most once"})
        indices.add(index)
        if set(route["target_ids"]) - known or (route["owner"] == "user" and not route["target_ids"]):
            errors.append({"path": "question_routes", "message": "route targets must be IDs this input supplies or "
                           "lists in its record_index, and a user question needs at least one"})
    questions = {row["id"]: row for row in context.get("question_links", [])}
    role = context["action"]["role"]
    seen = set()
    for resolution in extensions.get("question_resolutions", []):
        identifier = resolution["question_id"]
        # A repeated ID is rejected like an unknown one.
        error = resolution_error(None if identifier in seen else questions.get(identifier), role)
        if error:
            errors.append({"path": "question_resolutions", "message": error})
        seen.add(identifier)
    return errors

