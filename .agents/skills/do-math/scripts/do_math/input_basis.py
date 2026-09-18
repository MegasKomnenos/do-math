"""Exact source dependencies without invalidating unrelated repository changes."""
from __future__ import annotations


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
    return {"version": 1, "records": records, "sources": capture_sources(instance, list(refs))}


def decision_basis_changes(basis: dict, instance: dict, runtime: dict) -> list[dict]:
    from . import knowledge, planning
    if not isinstance(basis, dict) or basis.get("version") != 1:
        return [{"id": None, "field": "decision_basis", "reason": "missing_or_unsupported_basis"}]
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
            prefix_hash = planning._hash(record.get("results", [])[:row["result_count"]])
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
