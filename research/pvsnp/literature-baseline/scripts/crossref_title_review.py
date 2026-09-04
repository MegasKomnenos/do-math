#!/usr/bin/env python3
"""Triage Crossref and B002 title agreement without changing source records."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASELINE_ROOT = SCRIPT_PATH.parents[1]
DEFAULT_CANDIDATES = DEFAULT_BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
DEFAULT_CROSSREF = DEFAULT_BASELINE_ROOT / "catalog" / "B002-crossref.jsonl"
DEFAULT_CROSSREF_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B002-crossref.json"
DEFAULT_OUTPUT = DEFAULT_BASELINE_ROOT / "catalog" / "B002-crossref-title-review.jsonl"
DEFAULT_MANIFEST = (
    DEFAULT_BASELINE_ROOT / "manifests" / "B002-crossref-title-review.json"
)


def _load_normalizer():
    path = SCRIPT_PATH.with_name("build_b002_catalog.py")
    spec = importlib.util.spec_from_file_location("b002_title_normalizer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the B002 title normalizer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalize_text


_normalize_text = _load_normalizer()


class TitleReviewError(RuntimeError):
    pass


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def plain_crossref_text(value: str) -> str:
    parser = _VisibleText()
    try:
        parser.feed(value)
        parser.close()
    except Exception:
        return value
    return "".join(parser.parts)


def _normalized(value: str) -> str:
    return _normalize_text(plain_crossref_text(value))[0]


def _mr_sort_key(value: str) -> int:
    match = re.fullmatch(r"MR([1-9][0-9]*)", value)
    if not match:
        raise TitleReviewError(f"invalid MR candidate ID: {value!r}")
    return int(match.group(1))


def compare_titles(
    crossref_titles: Sequence[str],
    candidates: Sequence[dict[str, str]],
) -> dict[str, object]:
    if not candidates:
        raise TitleReviewError("title comparison has no B002 candidates")
    raw_crossref_title = " ".join(
        plain_crossref_text(str(value)) for value in crossref_titles
    ).strip()
    crossref_title = _normalized(raw_crossref_title) if raw_crossref_title else ""
    candidate_values: list[dict[str, object]] = []
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        _mr_sort_key(candidate_id)
        title = str(candidate["title"])
        score = (
            difflib.SequenceMatcher(None, crossref_title, title).ratio()
            if crossref_title and title
            else 0.0
        )
        candidate_values.append(
            {
                "candidate_id": candidate_id,
                "title": title,
                "similarity": round(score, 6),
            }
        )
    candidate_values.sort(
        key=lambda item: (-float(item["similarity"]), _mr_sort_key(str(item["candidate_id"])))
    )
    best = candidate_values[0]
    best_title = str(best["title"])
    if not crossref_title:
        classification = "missing_crossref_title"
    elif crossref_title == best_title:
        classification = "exact_title"
    elif crossref_title in best_title or best_title in crossref_title:
        classification = "title_containment"
    elif float(best["similarity"]) >= 0.75:
        classification = "similar_title"
    else:
        classification = "title_mismatch_review"
    return {
        "classification": classification,
        "crossref_title": crossref_title,
        "crossref_title_raw": raw_crossref_title,
        "best_candidate_id": best["candidate_id"],
        "best_similarity": best["similarity"],
        "candidate_titles": sorted(
            candidate_values, key=lambda item: _mr_sort_key(str(item["candidate_id"]))
        ),
    }


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as error:
        raise TitleReviewError(f"cannot read JSONL: {path}") from error
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                raise TitleReviewError(f"blank JSONL line at {path}:{line_number}")
            try:
                record = json.loads(line)
            except ValueError as error:
                raise TitleReviewError(
                    f"invalid JSONL record at {path}:{line_number}"
                ) from error
            if not isinstance(record, dict):
                raise TitleReviewError(f"non-object JSONL record at {path}:{line_number}")
            records.append(record)
    return records


def build_review_records(
    candidates_path: Path, crossref_path: Path
) -> list[dict[str, object]]:
    candidates: dict[str, dict[str, object]] = {}
    for candidate in _read_jsonl(candidates_path):
        try:
            candidate_id = str(candidate["candidate_id"])
            title = str(candidate["normalized"]["title"])
        except (KeyError, TypeError) as error:
            raise TitleReviewError("candidate record lacks normalized title") from error
        _mr_sort_key(candidate_id)
        if candidate_id in candidates:
            raise TitleReviewError(f"duplicate candidate ID: {candidate_id}")
        candidates[candidate_id] = {
            "candidate_id": candidate_id,
            "title": title,
        }

    reviews: list[dict[str, object]] = []
    seen_dois: set[str] = set()
    for record in _read_jsonl(crossref_path):
        try:
            doi = str(record["doi"])
            candidate_ids = [str(value) for value in record["candidate_ids"]]
            state = str(record["state"])
        except (KeyError, TypeError) as error:
            raise TitleReviewError("Crossref record lacks DOI or candidates") from error
        if doi in seen_dois:
            raise TitleReviewError(f"duplicate Crossref DOI: {doi}")
        seen_dois.add(doi)
        try:
            candidate_titles = [candidates[value] for value in candidate_ids]
        except KeyError as error:
            raise TitleReviewError(f"Crossref record has unknown candidate: {error}") from error
        if state == "crossref_not_found":
            comparison: dict[str, object] = {
                "classification": "crossref_not_found",
                "crossref_title": "",
                "crossref_title_raw": "",
                "best_candidate_id": None,
                "best_similarity": None,
                "candidate_titles": sorted(
                    candidate_titles,
                    key=lambda item: _mr_sort_key(str(item["candidate_id"])),
                ),
            }
            returned_doi = None
            crossref_type = None
        else:
            crossref = record.get("crossref")
            if not isinstance(crossref, dict):
                raise TitleReviewError(f"found Crossref record has no metadata: {doi}")
            title_values = crossref.get("title", [])
            if not isinstance(title_values, list):
                raise TitleReviewError(f"Crossref title is not a list: {doi}")
            comparison = compare_titles(
                [str(value) for value in title_values], candidate_titles
            )
            returned_doi = crossref.get("doi")
            crossref_type = crossref.get("type")
        reviews.append(
            {
                "schema_version": "pvsnp-crossref-title-review/1",
                "doi": doi,
                "returned_doi": returned_doi,
                "crossref_state": state,
                "crossref_type": crossref_type,
                "candidate_ids": sorted(set(candidate_ids), key=_mr_sort_key),
                **comparison,
            }
        )
    return sorted(reviews, key=lambda item: str(item["doi"]))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _jsonl_bytes(records: Sequence[dict[str, object]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _validate_crossref_manifest(
    root: Path,
    candidates_path: Path,
    crossref_path: Path,
    manifest_path: Path,
) -> None:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise TitleReviewError(f"cannot read Crossref manifest: {manifest_path}") from error
    if manifest.get("schema_version") != "pvsnp-crossref-manifest/1":
        raise TitleReviewError("unexpected Crossref manifest schema")
    if manifest.get("inputs", {}).get("candidate_index_sha256") != _sha256_file(
        candidates_path
    ):
        raise TitleReviewError("candidate index hash differs from Crossref manifest")
    output = manifest.get("output", {})
    if output.get("path") != _relative(crossref_path, root):
        raise TitleReviewError("Crossref index path differs from manifest")
    if output.get("sha256") != _sha256_file(crossref_path):
        raise TitleReviewError("Crossref index hash differs from manifest")


def write_review(
    root: Path,
    candidates_path: Path,
    crossref_path: Path,
    crossref_manifest_path: Path,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    root = root.resolve()
    _validate_crossref_manifest(
        root, candidates_path, crossref_path, crossref_manifest_path
    )
    records = build_review_records(candidates_path, crossref_path)
    output_bytes = _jsonl_bytes(records)
    _atomic_write(output_path, output_bytes)
    classes = Counter(str(record["classification"]) for record in records)
    crossref_states = Counter(str(record["crossref_state"]) for record in records)
    manifest: dict[str, object] = {
        "schema_version": "pvsnp-crossref-title-review-manifest/1",
        "batch_id": "B002",
        "analyzer": _relative(SCRIPT_PATH, root),
        "analyzer_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": [
            {
                "path": _relative(candidates_path, root),
                "bytes": candidates_path.stat().st_size,
                "sha256": _sha256_file(candidates_path),
            },
            {
                "path": _relative(crossref_path, root),
                "bytes": crossref_path.stat().st_size,
                "sha256": _sha256_file(crossref_path),
            },
            {
                "path": _relative(crossref_manifest_path, root),
                "bytes": crossref_manifest_path.stat().st_size,
                "sha256": _sha256_file(crossref_manifest_path),
            },
        ],
        "counts": {
            "records": len(records),
            "candidate_doi_links": sum(len(record["candidate_ids"]) for record in records),
            "classifications": dict(sorted(classes.items())),
            "crossref_states": dict(sorted(crossref_states.items())),
        },
        "output": {
            "path": _relative(output_path, root),
            "bytes": len(output_bytes),
            "sha256": hashlib.sha256(output_bytes).hexdigest(),
            "record_count": len(records),
        },
    }
    _atomic_write(
        manifest_path,
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify Crossref/B002 title agreement for manual review."
    )
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--crossref", type=Path)
    parser.add_argument("--crossref-manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    candidates = (args.candidates or root / "catalog" / "B002-candidates.jsonl").resolve()
    crossref = (args.crossref or root / "catalog" / "B002-crossref.jsonl").resolve()
    crossref_manifest = (
        args.crossref_manifest or root / "manifests" / "B002-crossref.json"
    ).resolve()
    output = (
        args.output or root / "catalog" / "B002-crossref-title-review.jsonl"
    ).resolve()
    manifest = (
        args.manifest or root / "manifests" / "B002-crossref-title-review.json"
    ).resolve()
    result = write_review(
        root,
        candidates,
        crossref,
        crossref_manifest,
        output,
        manifest,
    )
    print(
        f"built records={result['counts']['records']} "
        f"classifications={result['counts']['classifications']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TitleReviewError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
