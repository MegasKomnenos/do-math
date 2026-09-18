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
    return [{"kind": "user_decision", "question_id": row["id"], "target_ids": row["target_ids"]}
            for row in open_links(runtime, "user") if targets & set(row["target_ids"])]


def link(runtime, *, execution_id, field, owner, targets, source_ref=None, reason=None):
    rows = runtime.setdefault("question_links", [])
    existing = next((row for row in rows if row["origin_execution_id"] == execution_id and row["origin_field"] == field), None)
    if existing:
        return existing
    row = {"id": new_id("QU"), "origin_execution_id": execution_id, "origin_field": field,
           "owner": owner, "target_ids": list(dict.fromkeys(targets)), "status": "open", "resolution_ref": None}
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
        if not set(row["target_ids"]) & set(affected_ids):
            raise ValueError("the applied decision does not affect the question target: " + identifier)
    for identifier in identifiers:
        questions[identifier].update(status="resolved", resolution_ref=resolution_ref)


def validate_extensions(output, extensions, context):
    errors = []
    known = {context.get("instance_id"), *context.get("available_input_refs", [])}
    for key in ("tasks", "knowledge_catalog", "sources", "question_links"):
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
