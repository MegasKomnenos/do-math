"""Read-only inspection of the exact specification bundle to be implemented.

Fresh bytes are necessary, but do not prove semantic synchronization or grant
execution authority. This module never installs a bundle or runs an AI role.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)


def _contained(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("expected a relative slash-separated path")
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise ValueError(f"unsafe reference: {name}")
    if Path(name).is_absolute() or ":" in name:
        raise ValueError(f"absolute reference: {name}")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"reference leaves its root: {name}")
    return path


def _source_rows(source: str, prefix: str) -> dict[str, dict]:
    rows = {}
    for number, line in enumerate(source.splitlines(), 1):
        match = re.match(r"\| (" + prefix + r"\d+) \|", line)
        if match:
            key = match[1]
            if key in rows:
                raise ValueError(f"duplicate source row: {key}")
            rows[key] = {"source_line": number, "source_row_sha256": sha256(line.encode("utf-8"))}
    return rows


def inspect_bundle(repository: Path) -> dict:
    """Report observed drift and unreadable evidence without mutating any input."""
    docs = repository.resolve() / "docs"
    bundle = docs / "do-math" / "통합-설계-명세-v9"
    source_path = docs / "do-math" / "통합-설계.md"
    observations = []

    def observe(name, operation):
        try:
            details = operation()
        except (OSError, ValueError, TypeError, KeyError) as exc:
            observations.append({"check": name, "status": "incomplete", "reason": str(exc)})
        else:
            observations.append({"check": name, **details})

    def source_map():
        source_bytes = source_path.read_bytes()
        source = source_bytes.decode("utf-8")
        mapping = _load(bundle / "source-vector-map.json")
        expected_source = _contained(bundle.parent, mapping["source"])
        if expected_source != source_path.resolve():
            raise ValueError("source-vector-map refers to a different design document")
        differences = []
        actual_hash = sha256(source_bytes)
        if mapping["source_sha256"] != actual_hash:
            differences.append({"kind": "source_hash", "recorded": mapping["source_sha256"], "actual": actual_hash})
        counts = {}
        for field, prefix in (("vectors", "V"), ("quality_contracts", "Q")):
            actual = _source_rows(source, prefix)
            records = mapping[field]
            indexed = {row["id"]: row for row in records}
            if len(indexed) != len(records):
                raise ValueError(f"duplicate {field} identifier")
            if not actual:
                raise ValueError(f"no {field} rows found in the design")
            counts[field] = {"source": len(actual), "mapped": len(indexed)}
            missing, extra = sorted(actual.keys() - indexed.keys()), sorted(indexed.keys() - actual.keys())
            changed = [key for key in sorted(actual.keys() & indexed.keys())
                       if any(indexed[key].get(k) != v for k, v in actual[key].items())]
            if missing or extra or changed:
                differences.append({"kind": field, "missing": missing, "extra": extra, "changed": changed})
        return {"status": "blocked" if differences else "verified", "source_sha256": actual_hash,
                "counts": counts, "differences": differences}

    def schema_hashes():
        registry = _load(bundle / "schema-registry.json")
        families = registry["families"]
        if not families:
            raise ValueError("empty schema registry")
        seen, schema_ids, contract_ids = set(), set(), set()
        differences = []
        for row in families:
            if row["family"] in seen:
                raise ValueError(f"duplicate schema family: {row['family']}")
            seen.add(row["family"])
            path = _contained(bundle, row["path"])
            schema = _load(path)
            if not isinstance(schema, dict):
                raise ValueError(f"schema is not an object: {row['path']}")
            if (row["schema_id"] in schema_ids or row["contract_id"] in contract_ids):
                raise ValueError("duplicate schema or contract identifier")
            schema_ids.add(row["schema_id"])
            contract_ids.add(row["contract_id"])
            expected_schema_id = "https://do-math.invalid/schemas/draft/9/" + row["family"]
            expected_contract_id = "do-math-draft/" + row["family"] + "/9"
            if (row["path"] != "schemas/" + row["family"] + ".schema.json"
                    or schema.get("$id") != row["schema_id"] or row["schema_id"] != expected_schema_id
                    or row["contract_id"] != expected_contract_id
                    or (row["family"] != "common" and
                        schema.get("properties", {}).get("schema_version", {}).get("const") != row["contract_id"])):
                differences.append(row["path"] + ": family/identifier binding mismatch")
            if sha256(path.read_bytes()) != row["sha256"]:
                differences.append(row["path"])
        actual = {p.name.removesuffix(".schema.json") for p in (bundle / "schemas").glob("*.schema.json")}
        return {"status": "blocked" if differences or seen != actual else "verified",
                "families": len(seen), "changed": differences,
                "unregistered": sorted(actual - seen), "missing": sorted(seen - actual)}

    def validation_basis():
        report = _load(bundle / "validation-report.json")
        records = report["input_basis"]
        if not records:
            raise ValueError("empty validation input basis")
        paths = set()
        changed = []
        for record in records:
            name = record["path"]
            if name in paths:
                raise ValueError(f"duplicate validation input: {name}")
            paths.add(name)
            if sha256(_contained(docs, name).read_bytes()) != record["sha256"]:
                changed.append(name)
        required = {"do-math/통합-설계.md", "형식과-절차.md"}
        required.update("do-math/통합-설계-명세-v9/" + name for name in (
            "build_spec.py", "spec_checks.py", "verify_spec.py", "schema-registry.json",
            "command-contracts.json", "role-contracts.json", "semantic-rules.json",
            "transitions.json", "source-vector-map.json", "relation-templates.json", "toolchain-lock.json"))
        for directory in (bundle / "schemas", bundle / "fixtures"):
            required.update(p.relative_to(docs).as_posix() for p in directory.rglob("*.json"))
        missing = sorted(required - paths)
        successful = (report.get("passed") is True and type(report.get("tests_run")) is int
                      and report["tests_run"] > 0 and report.get("failures") == 0
                      and report.get("errors") == 0 and not report.get("failed_cases"))
        return {"status": "verified" if not changed and not missing and successful else "blocked",
                "changed": changed, "unreported": missing, "recorded_success": successful,
                "scope": report["scope"], "tests_run": report["tests_run"],
                "not_verified": report["not_verified"]}

    observe("source_vector_correspondence", source_map)
    observe("schema_bytes", schema_hashes)
    observe("validation_input_basis", validation_basis)
    statuses = {row["status"] for row in observations}
    return {"scope": "specification_freshness_only",
            "status": "incomplete" if "incomplete" in statuses else "blocked" if "blocked" in statuses else "verified",
            "checks": observations,
            "not_verified": ["D08_semantic_synchronization", "D10_contract_identifier", "actual_adapter",
                             "runtime_execution", "research_roles", "Lean", "research_efficacy"]}
