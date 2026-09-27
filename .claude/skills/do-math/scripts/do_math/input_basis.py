"""Exact source dependencies without invalidating unrelated repository changes."""
from __future__ import annotations

from copy import deepcopy

from .repository import exact_content_hash

# The state of a registered source; a replaced source moves into the history of its successor.
SOURCE_STATUSES = frozenset({"active"})


def aliases(source: dict) -> set[str]:
    return {value for value in (source.get("id"), source.get("path"), source.get("local_path"), source.get("name"),
            "source:" + source["name"] if source.get("name") else None) if value}


def capture_sources(instance: dict, refs: list[str] | None = None) -> list[dict]:
    selected = set(refs) if refs is not None else None
    return [{"name": source["name"], "sha256": source["sha256"], "path": source["path"]}
            for source in instance.get("sources", [])
            if selected is None or selected.intersection(aliases(source))]


def sources_current(basis: list[dict], instance: dict) -> bool:
    current = {source["name"]: source for source in instance.get("sources", [])}
    return all(row["name"] in current and row["sha256"] == current[row["name"]]["sha256"] for row in basis)


class CurrentnessChanged(ValueError):
    def __init__(self, changes):
        import json
        self.changes = changes
        super().__init__("decision premises changed: " + json.dumps(changes, ensure_ascii=False, sort_keys=True))


def capture_review_input_basis(cycle: dict) -> dict:
    """Freeze the non-proposal inputs that make a review result interpretable."""
    fields = ("review_policy", "scope_assessment", "owner_activity_id", "activity_execution_limit",
              "identity_basis", "policy_ref", "publication_premises")
    return {"values": {field: deepcopy(cycle.get(field)) for field in fields}}


def review_input_basis_changes(basis: dict, cycle: dict) -> list[dict]:
    """Report precise policy/scope/profile drift; do not infer semantic equivalence.

    The basis is part of the validated stored cycle, so only its presence is checked.
    """
    if not isinstance(basis, dict) or not isinstance(basis.get("values"), dict):
        return [{"field": "review_input_basis", "reason": "missing_basis", "next": "refresh_review"}]
    current = capture_review_input_basis(cycle)["values"]
    changes = []
    for field in current:
        before, after = basis["values"].get(field), current.get(field)
        if before == after:
            continue
        if field == "scope_assessment" and isinstance(before, dict) and isinstance(after, dict) and \
                before.get("selected_profile_ref") != after.get("selected_profile_ref"):
            changes.append({"field": "selected_profile_ref", "before": before.get("selected_profile_ref"),
                            "after": after.get("selected_profile_ref"), "next": "refresh_review"})
        else:
            changes.append({"field": field, "before": before, "after": after, "next": "refresh_review"})
    return changes


def capture_decision_basis(instance: dict, runtime: dict, refs) -> dict:
    from . import knowledge, planning
    refs = list(refs)
    records = []
    for identifier in sorted(set(refs)):
        if identifier in runtime.get("tasks", {}):
            row = planning.task_reference_basis(runtime["tasks"][identifier])
            row.pop("terminal", None)
            records.append({"kind": "task", **row})
        elif identifier in instance.get("knowledge", {}):
            records.append({"kind": "knowledge", **knowledge.decision_reference(instance["knowledge"][identifier], instance)})
    return {"records": records, "sources": capture_sources(instance, list(refs))}


def decision_basis_changes(basis: dict, instance: dict, runtime: dict) -> list[dict]:
    from . import knowledge, planning
    if not isinstance(basis, dict) or not isinstance(basis.get("records"), list):
        return [{"id": None, "field": "decision_basis", "reason": "missing_basis"}]
    changes = []
    def add(identifier, field, before, after):
        changes.append({"id": identifier, "field": field, "before": before, "after": after, "next": "refresh_decision"})
    for row in basis.get("records", []):
        identifier = row["id"]
        record = runtime.get("tasks", {}).get(identifier) if row["kind"] == "task" else instance.get("knowledge", {}).get(identifier)
        if record is None:
            add(identifier, "existence", True, False)
            continue
        if row["kind"] == "task":
            current = planning.task_reference_basis(record)
            if current["contract_sha256"] != row["contract_sha256"]:
                add(identifier, "contract_sha256", row["contract_sha256"], current["contract_sha256"])
            prefix_hash = exact_content_hash(record.get("results", [])[:row["result_count"]])
            if prefix_hash != row["results_sha256"]:
                add(identifier, "results_sha256", row["results_sha256"], prefix_hash)
        else:
            current = knowledge.decision_reference(record, instance)
            for field in ("revision", "content_sha256", "use_suspended", "trust_environment_id", "trust_environment_state", "source_basis"):
                if current.get(field) != row.get(field):
                    add(identifier, field, row.get(field), current.get(field))
            if current["status"] != row["status"] and (row["status"], current["status"]) != ("reviewing", "verified"):
                add(identifier, "status", row["status"], current["status"])
            if row["usable"] and not current["usable"]:
                add(identifier, "usable", True, False)
            if not sources_current(row["source_basis"], instance):
                add(identifier, "source_content", row["source_basis"], "changed")
    if not sources_current(basis.get("sources", []), instance):
        add(None, "sources", basis["sources"], "changed")
    return changes
