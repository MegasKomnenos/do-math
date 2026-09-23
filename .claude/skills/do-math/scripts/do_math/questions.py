"""Source-linked questions and explicitly scoped user decision requirements."""
from copy import deepcopy

from .repository import new_id


def open_links(runtime, owner=None):
    return [row for row in runtime.get("question_links", []) if row["status"] == "open" and (owner is None or row["owner"] == owner)]


def user_waits(action, instance, runtime):
    if action.get("role") in {"intent_interpretation", "operational_review", "maintenance"}:
        return []
    from .planning import action_read_ids
    reads = set() if action.get("role") == "research_plan" else action_read_ids(action, instance, runtime)
    targets = reads | {action.get("target"), action.get("id"), instance.get("id")}
    retry = action.get("input_overflow_retry", {})
    retry_question = retry.get("question_id") if retry.get("state", "pending") == "pending" else None
    return [{"kind": "user_decision", "question_id": row["id"], "target_ids": row.get("unresolved_target_ids", row["target_ids"]), "next_owner": "user"}
            for row in open_links(runtime, "user") if row["id"] != retry_question and row.get("blocks", False)
            and targets & set(row.get("unresolved_target_ids", row["target_ids"]))]


def link(runtime, *, execution_id, field, owner, targets, source_ref=None, reason=None, blocks=False, checked_by=None):
    if owner not in {"user", "research", "operations"} or type(blocks) is not bool:
        raise ValueError("question owner and blocking decision required")
    if not isinstance(targets, list) or any(not isinstance(t, str) or not t for t in targets) or (blocks and not targets):
        raise ValueError("blocking questions require explicit affected targets")
    rows = runtime.setdefault("question_links", [])
    existing = next((row for row in rows if row["origin_execution_id"] == execution_id and row["origin_field"] == field), None)
    if existing:
        if (existing["owner"], existing["target_ids"], existing.get("blocks", False)) != (owner, list(dict.fromkeys(targets)), blocks):
            raise ValueError("question source cannot be rerouted silently")
        return existing
    row = {"id": new_id("QU"), "origin_execution_id": execution_id, "origin_field": field,
           "owner": owner, "target_ids": list(dict.fromkeys(targets)), "unresolved_target_ids": list(dict.fromkeys(targets)),
           "blocks": blocks, "status": "open", "resolution_ref": None, "checked_by": checked_by}
    if source_ref:
        row["source_ref"] = source_ref
    if reason:
        row["routing_reason"] = reason
    rows.append(row)
    return row


def resolve_user(runtime, identifiers, *, resolution_ref, affected_ids):
    questions = {row["id"]: row for row in runtime.get("question_links", [])}
    if not isinstance(identifiers, list) or len(identifiers) != len(set(identifiers)):
        raise ValueError("resolves_questions must be distinct question IDs")
    for identifier in identifiers:
        row = questions.get(identifier)
        if not row or row["owner"] != "user" or row["status"] != "open":
            raise ValueError("user decision must name an open user question: " + str(identifier))
        if not set(row.get("unresolved_target_ids", row["target_ids"])) & set(affected_ids):
            raise ValueError("the applied decision does not affect the question target: " + identifier)
    for identifier in identifiers:
        row = questions[identifier]
        remaining = set(row.get("unresolved_target_ids", row["target_ids"])) - set(affected_ids)
        row["unresolved_target_ids"] = [target for target in row["target_ids"] if target in remaining]
        row.setdefault("resolution_history", []).append({"resolution_ref": resolution_ref, "affected_ids": sorted(set(affected_ids) & set(row["target_ids"]))})
        if not remaining: row.update(status="resolved", resolution_ref=resolution_ref)


def validate_extensions(output, extensions, context):
    errors = []
    known = {context.get("instance_id"), *context.get("available_input_refs", [])}
    for key in ("tasks", "task_catalog", "knowledge_catalog", "sources", "question_links"):
        known.update(row["id"] for row in context.get(key, []) if isinstance(row, dict) and row.get("id"))
    if context.get("task"):
        known.add(context["task"]["id"])
    indices = set()
    for route in extensions.get("question_routes", []):
        index = route["question_index"]
        if index in indices or not 0 <= index < len(output.get("questions", [])):
            errors.append({"path": "question_routes", "message": "route each supplied question index at most once"})
        indices.add(index)
        if set(route["target_ids"]) - known or (route["owner"] == "user" and not route["target_ids"]):
            errors.append({"path": "question_routes", "message": "user questions require provided affected target IDs"})
        if type(route.get("blocks", False)) is not bool or (route.get("blocks") and not route.get("reason", "").strip()):
            errors.append({"path": "question_routes", "message": "a blocking question needs the necessary decision and its reason"})
    questions = {row["id"]: row for row in context.get("question_links", [])}
    role = context["action"]["role"]
    seen = set()
    for resolution in extensions.get("question_resolutions", []):
        identifier = resolution["question_id"]
        row = questions.get(identifier)
        owner = row.get("owner") if row else None
        if identifier in seen or not row or row["status"] != "open" or owner not in {"research", "operations"}:
            errors.append({"path": "question_resolutions", "message": "only distinct open research or operations questions can be resolved by an AI extension"})
        if owner == "operations" and role not in {"operational_review", "maintenance"}:
            errors.append({"path": "question_resolutions", "message": "an operations question requires an operational role"})
        seen.add(identifier)
    return errors


def sync_activity_wait(runtime, activity_id, question_ids, *, at):
    """Only ACTIVITIES owns the transition; questions supply its exact condition."""
    from .activities import wait_for, resume_activity
    rows = {row["id"]:row for row in runtime.get("question_links", [])}
    if not isinstance(question_ids, list) or any(q not in rows for q in question_ids): raise ValueError("activity question does not resolve")
    activity = runtime.get("activities", {}).get(activity_id)
    if activity is None: raise ValueError("question wait activity is absent")
    pending = [q for q in question_ids if rows[q]["status"] == "open" and rows[q].get("blocks") and rows[q]["owner"] == "user"]
    previous = activity.get("waiting", {})
    if pending:
        condition = {"kind":"user_questions", "question_ids":sorted(pending)}
        if activity["status"] == "waiting" and previous.get("condition", {}).get("kind") != "user_questions":
            raise ValueError("question wait cannot replace another owner's condition")
        return wait_for(runtime,activity_id,reason="Necessary user decisions remain",condition=condition,next_owner="user",at=at)
    if activity["status"] == "waiting" and previous.get("condition", {}).get("kind") == "user_questions":
        waiting_ids = previous["condition"]["question_ids"]
        if any(rows.get(q, {}).get("status", "open") == "open" for q in waiting_ids): return activity
        return resume_activity(runtime,activity_id,condition=previous["condition"],at=at)
    return activity
