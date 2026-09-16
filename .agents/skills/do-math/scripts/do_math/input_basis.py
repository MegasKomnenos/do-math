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
