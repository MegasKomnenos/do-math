#!/usr/bin/env python3
"""Build a safe B001+B002 candidate and relation reference index."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[1]


class UnifiedCatalogError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise UnifiedCatalogError(f"invalid JSONL at {path}:{line_number}") from error
            if not isinstance(record, dict):
                raise UnifiedCatalogError(f"non-object JSONL at {path}:{line_number}")
            records.append(record)
    return records


def _catalog_map(
    records: Sequence[dict[str, object]], catalog: str
) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for record in records:
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise UnifiedCatalogError(f"{catalog} candidate lacks an ID")
        if candidate_id in output:
            raise UnifiedCatalogError(f"duplicate {catalog} candidate: {candidate_id}")
        output[candidate_id] = record
    return output


def _agreement(
    left: dict[str, object], right: dict[str, object]
) -> dict[str, bool]:
    left_normalized = left.get("normalized")
    right_normalized = right.get("normalized")
    if not isinstance(left_normalized, dict) or not isinstance(right_normalized, dict):
        raise UnifiedCatalogError("overlap record lacks normalized metadata")
    return {
        key: left_normalized.get(key) == right_normalized.get(key)
        for key in ("title", "creators", "year", "dois", "isbns")
    }


def build_unified_candidates(
    b001_records: Sequence[dict[str, object]],
    b002_records: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    b001 = _catalog_map(b001_records, "B001")
    b002 = _catalog_map(b002_records, "B002")
    all_ids = sorted(set(b001) | set(b002))
    output: list[dict[str, object]] = []
    for candidate_id in all_ids:
        records: list[dict[str, str]] = []
        if candidate_id in b001:
            records.append({"catalog": "B001", "candidate_id": candidate_id})
        if candidate_id in b002:
            records.append({"catalog": "B002", "candidate_id": candidate_id})
        primary_catalog = "B002" if candidate_id in b002 else "B001"
        primary = b002[candidate_id] if primary_catalog == "B002" else b001[candidate_id]
        record = {
            "schema_version": "pvsnp-unified-candidate-reference/1",
            "global_candidate_id": candidate_id,
            "primary_record": {
                "catalog": primary_catalog,
                "candidate_id": candidate_id,
            },
            "records": records,
            "normalized": primary.get("normalized", {}),
        }
        if candidate_id in b001 and candidate_id in b002:
            record["same_primary_identifier"] = {
                "type": "mathscinet_mr",
                "agreement": _agreement(b001[candidate_id], b002[candidate_id]),
            }
        output.append(record)
    return output


def build_unified_relations(
    b001_relations: Sequence[dict[str, object]],
    b002_relations: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    seen: set[str] = set()
    for source_catalog, source_rows in (
        ("B001", b001_relations),
        ("B002", b002_relations),
    ):
        for source in source_rows:
            relation_id = source.get("relation_id")
            if not isinstance(relation_id, str) or not relation_id:
                raise UnifiedCatalogError(f"{source_catalog} relation lacks an ID")
            if relation_id in seen:
                raise UnifiedCatalogError(f"duplicate relation ID: {relation_id}")
            seen.add(relation_id)
            source_members = source.get("members")
            if not isinstance(source_members, list):
                raise UnifiedCatalogError(f"invalid members for {relation_id}")
            members: list[dict[str, str]] = []
            for member in source_members:
                if source_catalog == "B002":
                    if not isinstance(member, str):
                        raise UnifiedCatalogError(f"invalid B002 member in {relation_id}")
                    members.append({"catalog": "B002", "candidate_id": member})
                else:
                    if not isinstance(member, dict):
                        raise UnifiedCatalogError(f"invalid B001 member in {relation_id}")
                    catalog = member.get("catalog")
                    candidate_id = member.get("candidate_id")
                    if catalog not in {"B001", "B002"} or not isinstance(
                        candidate_id, str
                    ):
                        raise UnifiedCatalogError(f"invalid B001 member in {relation_id}")
                    members.append(
                        {"catalog": str(catalog), "candidate_id": candidate_id}
                    )
            output.append(
                {
                    "schema_version": "pvsnp-unified-relation-reference/1",
                    "relation_id": relation_id,
                    "source_catalog": source_catalog,
                    "relation_type": source.get("relation_type"),
                    "status": source.get("status"),
                    "signal": source.get("signal", {}),
                    "members": members,
                }
            )
    output.sort(key=lambda record: str(record["relation_id"]))
    return output


def _jsonl_bytes(records: Sequence[dict[str, object]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def write_outputs(
    root: Path,
    b001_candidates_path: Path,
    b002_candidates_path: Path,
    b001_relations_path: Path,
    b002_relations_path: Path,
    candidate_output_path: Path,
    relation_output_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    b001_candidates = load_jsonl(b001_candidates_path)
    b002_candidates = load_jsonl(b002_candidates_path)
    b001_relations = load_jsonl(b001_relations_path)
    b002_relations = load_jsonl(b002_relations_path)
    candidates = build_unified_candidates(b001_candidates, b002_candidates)
    relations = build_unified_relations(b001_relations, b002_relations)
    candidate_ids = {str(record["global_candidate_id"]) for record in candidates}
    missing_members: list[tuple[str, str]] = []
    for relation in relations:
        for member in relation["members"]:
            if member["candidate_id"] not in candidate_ids:
                missing_members.append(
                    (str(relation["relation_id"]), str(member["candidate_id"]))
                )
    if missing_members:
        raise UnifiedCatalogError(f"relations reference missing candidates: {missing_members}")
    candidate_bytes = _jsonl_bytes(candidates)
    relation_bytes = _jsonl_bytes(relations)
    _atomic_write(candidate_output_path, candidate_bytes)
    _atomic_write(relation_output_path, relation_bytes)
    overlap_records = [record for record in candidates if len(record["records"]) == 2]
    agreement_counts = Counter()
    for record in overlap_records:
        for key, value in record["same_primary_identifier"]["agreement"].items():
            agreement_counts[f"{key}_{'match' if value else 'diff'}"] += 1
    relation_types = Counter(str(record["relation_type"]) for record in relations)
    inputs = [
        b001_candidates_path,
        b002_candidates_path,
        b001_relations_path,
        b002_relations_path,
    ]
    manifest = {
        "schema_version": "pvsnp-unified-catalog-manifest/1",
        "batches": ["B001", "B002"],
        "builder": _relative(SCRIPT_PATH, root),
        "builder_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": [
            {
                "path": _relative(path, root),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
                "record_count": len(load_jsonl(path)),
            }
            for path in inputs
        ],
        "counts": {
            "b001_candidates": len(b001_candidates),
            "b002_candidates": len(b002_candidates),
            "same_mr_overlap": len(overlap_records),
            "safe_candidate_union": len(candidates),
            "relations": len(relations),
            "relation_types": dict(sorted(relation_types.items())),
            "overlap_field_agreement": dict(sorted(agreement_counts.items())),
            "missing_relation_members": 0,
        },
        "outputs": [
            {
                "path": _relative(candidate_output_path, root),
                "bytes": len(candidate_bytes),
                "sha256": _sha256_bytes(candidate_bytes),
                "record_count": len(candidates),
            },
            {
                "path": _relative(relation_output_path, root),
                "bytes": len(relation_bytes),
                "sha256": _sha256_bytes(relation_bytes),
                "record_count": len(relations),
            },
        ],
    }
    _atomic_write(
        manifest_path,
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the B001+B002 safe union.")
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--b001-candidates", type=Path)
    parser.add_argument("--b002-candidates", type=Path)
    parser.add_argument("--b001-relations", type=Path)
    parser.add_argument("--b002-relations", type=Path)
    parser.add_argument("--candidate-output", type=Path)
    parser.add_argument("--relation-output", type=Path)
    parser.add_argument("--manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    paths = {
        "b001_candidates_path": (
            args.b001_candidates or root / "catalog/B001-candidates.jsonl"
        ).resolve(),
        "b002_candidates_path": (
            args.b002_candidates or root / "catalog/B002-candidates.jsonl"
        ).resolve(),
        "b001_relations_path": (
            args.b001_relations or root / "catalog/B001-relations.jsonl"
        ).resolve(),
        "b002_relations_path": (
            args.b002_relations or root / "catalog/B002-relations.jsonl"
        ).resolve(),
        "candidate_output_path": (
            args.candidate_output or root / "catalog/B001-B002-candidates.jsonl"
        ).resolve(),
        "relation_output_path": (
            args.relation_output or root / "catalog/B001-B002-relations.jsonl"
        ).resolve(),
        "manifest_path": (
            args.manifest or root / "manifests/B001-B002-unified.json"
        ).resolve(),
    }
    result = write_outputs(root=root, **paths)
    print(
        f"built candidates={result['counts']['safe_candidate_union']} "
        f"relations={result['counts']['relations']} "
        f"same_mr_overlap={result['counts']['same_mr_overlap']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UnifiedCatalogError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
