#!/usr/bin/env python3
"""Normalize B001's heterogeneous exports without discarding source records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence, TextIO


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASELINE_ROOT = SCRIPT_PATH.parents[1]
DEFAULT_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B001.json"
DEFAULT_B002_CANDIDATES = DEFAULT_BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
DEFAULT_CANDIDATES = DEFAULT_BASELINE_ROOT / "catalog" / "B001-candidates.jsonl"
DEFAULT_RELATIONS = DEFAULT_BASELINE_ROOT / "catalog" / "B001-relations.jsonl"
DEFAULT_DIRECT_QUEUE = DEFAULT_BASELINE_ROOT / "catalog" / "B001-direct-title-queue.jsonl"
DEFAULT_DIRECT_AXIS_QUEUE = (
    DEFAULT_BASELINE_ROOT / "catalog" / "B001-direct-axis-queue.jsonl"
)
DEFAULT_BARRIER_TITLE_QUEUE = (
    DEFAULT_BASELINE_ROOT / "catalog" / "B001-barrier-title-queue.jsonl"
)
DEFAULT_OUTPUT_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B001-normalized.json"


def _load_b002_helpers():
    path = SCRIPT_PATH.with_name("build_b002_catalog.py")
    spec = importlib.util.spec_from_file_location("b001_normalization_helpers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B002 normalization helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_helpers = _load_b002_helpers()


class B001CatalogError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _strip_bib_value(segment: str) -> str:
    value = segment.strip()
    if not value:
        return ""
    opening = value[0]
    if opening in {'{', '"'}:
        value = value[1:]
        value = value.rstrip()
        if value.endswith(","):
            value = value[:-1].rstrip()
        closing = "}" if opening == "{" else '"'
        if value.endswith(closing):
            value = value[:-1]
        return value.strip()
    value = value.rstrip()
    if value.endswith(","):
        value = value[:-1]
    value = re.sub(r"[})]\s*$", "", value)
    return value.strip()


_ENTRY_START = re.compile(r"(?i)@(?P<type>[A-Za-z]+)\s*(?P<open>[{(])")
_FIELD_START = re.compile(
    r"(?mi)^[ \t]*(?P<name>[A-Za-z][A-Za-z0-9_-]*)[ \t]*=[ \t]*"
)


def parse_bibtex_tolerant(text: str, *, source_name: str) -> list[dict[str, object]]:
    """Parse export BibTeX by record and field boundaries, ignoring brace damage in abstracts."""
    starts = list(_ENTRY_START.finditer(text))
    if not starts and text.strip():
        raise B001CatalogError(f"{source_name}: no BibTeX entries")
    records: list[dict[str, object]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        raw_text = text[start.start() : end].strip()
        header_end = raw_text.find(",", start.end() - start.start())
        if header_end < 0:
            raise B001CatalogError(f"{source_name}: entry {index + 1} has no key delimiter")
        key = raw_text[start.end() - start.start() : header_end].strip()
        if not key:
            raise B001CatalogError(f"{source_name}: entry {index + 1} has an empty key")
        body = raw_text[header_end + 1 :]
        field_starts = list(_FIELD_START.finditer(body))
        fields: dict[str, list[str]] = defaultdict(list)
        for field_index, field_start in enumerate(field_starts):
            field_end = (
                field_starts[field_index + 1].start()
                if field_index + 1 < len(field_starts)
                else len(body)
            )
            segment = body[field_start.end() : field_end]
            if field_index + 1 == len(field_starts):
                # Remove the entry delimiter after the final field wrapper.
                segment = re.sub(r"\s*[})]\s*$", "", segment)
            value = _strip_bib_value(segment)
            fields[field_start.group("name").casefold()].append(value)
        records.append(
            {
                "entry_type": start.group("type").casefold(),
                "key": key,
                "fields": dict(fields),
                "raw_text": raw_text,
                "parsed_record_sha256": _sha256_bytes(raw_text.encode("utf-8")),
            }
        )
    return records


_RIS_TAG = re.compile(r"^(?P<tag>[A-Z0-9]{2})  - ?(?P<value>.*)$")


def parse_ris(text: str, *, source_name: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    lines: list[str] = []
    fields: dict[str, list[str]] = defaultdict(list)
    last_tag: str | None = None

    def finish() -> None:
        nonlocal lines, fields, last_tag
        if not fields and not any(line.strip() for line in lines):
            lines = []
            last_tag = None
            return
        raw_text = "\n".join(lines).strip()
        records.append(
            {
                "fields": dict(fields),
                "raw_text": raw_text,
                "parsed_record_sha256": _sha256_bytes(raw_text.encode("utf-8")),
            }
        )
        lines = []
        fields = defaultdict(list)
        last_tag = None

    for line_number, raw_line in enumerate(text.lstrip("\ufeff").splitlines(), start=1):
        line = raw_line.rstrip("\r")
        lines.append(line)
        match = _RIS_TAG.match(line)
        if match:
            tag = match.group("tag").casefold()
            value = match.group("value")
            if tag == "er":
                finish()
                continue
            fields[tag].append(value)
            last_tag = tag
        elif line.strip():
            if last_tag is None or not fields[last_tag]:
                raise B001CatalogError(
                    f"{source_name}:{line_number}: continuation without a field"
                )
            fields[last_tag][-1] += "\n" + line
    if fields or any(line.strip() for line in lines):
        raise B001CatalogError(f"{source_name}: final RIS record lacks ER terminator")
    return records


def extract_dois(value: str) -> list[str]:
    value = value.replace(r"\_", "_")
    matches = re.findall(r"(?i)10\.[0-9]{1,9}/[^\s,\]\[{}]+", value)
    dois: list[str] = []
    for match in matches:
        normalized = match.rstrip(".,:;").casefold()
        if normalized and normalized not in dois:
            dois.append(normalized)
    return dois


_SIGNAL_PHRASES = {
    "computational_complexity": ("computational complexity",),
    "circuit_complexity": ("circuit complexity",),
    "proof_complexity": ("proof complexity",),
    "natural_proofs": ("natural proof",),
    "algebrization": ("algebrization", "algebrizing"),
    "relativization": ("relativization", "relativized complexity"),
    "geometric_complexity_theory": ("geometric complexity theory",),
    "descriptive_complexity": ("descriptive complexity",),
    "derandomization": ("derandomization", "derandomized"),
    "parameterized_complexity": ("parameterized complexity",),
    "communication_complexity": ("communication complexity",),
    "meta_complexity": ("meta complexity", "metacomplexity"),
    "fine_grained_complexity": ("fine grained complexity",),
    "query_complexity": ("query complexity",),
    "average_case_complexity": ("average case complexity",),
    "np_hardness": ("np hard", "np hardness", "np complete", "np completeness"),
    "polynomial_time": ("polynomial time",),
    "complexity_classes": ("complexity class",),
    "boolean_circuits": ("boolean circuit",),
    "satisfiability": ("satisfiability", " sat "),
    "lower_bounds": ("lower bound",),
}
_DIRECT_RAW = re.compile(
    r"(?i)(?<![A-Za-z0-9])P\s*(?:=|\?=|!=|≠|vs\.?|versus)\s*NP(?![A-Za-z0-9])"
)
_DIRECT_NORMALIZED = (
    "p vs np",
    "p versus np",
    "p ne np",
    "p np problem",
    "p np question",
)
_LOCATION_ORDER = {"title": 0, "abstract": 1, "keywords": 2}


def detect_search_signals(
    *, title: str, abstract: str = "", keywords: Sequence[str] = ()
) -> dict[str, list[str]]:
    locations = {
        "title": title,
        "abstract": abstract,
        "keywords": " ; ".join(keywords),
    }
    signals: dict[str, list[str]] = defaultdict(list)
    for location, raw_value in locations.items():
        normalized = _helpers.normalize_text(raw_value)[0]
        padded = f" {normalized} "
        if _DIRECT_RAW.search(raw_value) or any(
            phrase in normalized for phrase in _DIRECT_NORMALIZED
        ):
            signals["direct_p_vs_np"].append(location)
        for name, phrases in _SIGNAL_PHRASES.items():
            if any(phrase in padded for phrase in phrases):
                signals[name].append(location)
    return {
        name: sorted(set(found), key=lambda value: _LOCATION_ORDER[value])
        for name, found in sorted(signals.items())
    }


_NAMED_AXIS_SIGNALS = {
    "circuit_complexity",
    "proof_complexity",
    "natural_proofs",
    "algebrization",
    "relativization",
    "geometric_complexity_theory",
    "descriptive_complexity",
    "derandomization",
    "parameterized_complexity",
    "communication_complexity",
    "meta_complexity",
    "fine_grained_complexity",
    "query_complexity",
    "average_case_complexity",
}
_PRIORITY_BARRIER_TITLE_SIGNALS = {
    "natural_proofs",
    "algebrization",
    "proof_complexity",
    "geometric_complexity_theory",
    "meta_complexity",
}


def _review_routing(
    signals: dict[str, list[str]], provenance: Sequence[dict[str, object]]
) -> str:
    if "direct_p_vs_np" in signals:
        return "direct_p_vs_np_signal"
    if any(name in signals for name in _NAMED_AXIS_SIGNALS):
        return "named_complexity_axis_signal"
    if "computational_complexity" in signals:
        return "computational_complexity_signal"
    query_ids = {str(item.get("query_id")) for item in provenance}
    if query_ids & {"M04", "M05"}:
        return "msc_control_seed"
    if signals:
        return "general_complexity_context_signal"
    return "no_explicit_export_signal"


def _first(fields: dict[str, list[str]], *names: str) -> str:
    for name in names:
        for value in fields.get(name.casefold(), []):
            if value.strip():
                return value.strip()
    return ""


def _all(fields: dict[str, list[str]], *names: str) -> list[str]:
    values: list[str] = []
    for name in names:
        for value in fields.get(name.casefold(), []):
            if value.strip():
                values.append(value.strip())
    return values


def _split_people_values(values: Sequence[str], *, separator: str | None = None) -> list[str]:
    people: list[str] = []
    for value in values:
        pieces = value.split(separator) if separator else _helpers._split_people(value)
        for piece in pieces:
            piece = piece.strip()
            if piece and piece not in people:
                people.append(piece)
    return people


def _bibliographic_from_bib(record: dict[str, object]) -> dict[str, object]:
    fields = record["fields"]
    assert isinstance(fields, dict)
    dois: list[str] = []
    for value in _all(fields, "doi"):
        for doi in extract_dois(value):
            if doi not in dois:
                dois.append(doi)
    key = str(record["key"])
    if re.match(r"(?i)^10\.[0-9]{1,9}/", key):
        for doi in extract_dois(key):
            if doi not in dois:
                dois.append(doi)
    return {
        "title": _first(fields, "title"),
        "authors": _split_people_values(_all(fields, "author")),
        "editors": _split_people_values(_all(fields, "editor")),
        "year": _first(fields, "year"),
        "doi": dois,
        "venue": _first(fields, "journal", "booktitle"),
        "volume": _first(fields, "volume"),
        "issue": _first(fields, "number", "issue"),
        "pages": _first(fields, "pages"),
        "publisher": _first(fields, "publisher"),
        "isbn": _all(fields, "isbn"),
        "issn": _all(fields, "issn"),
        "mrnumber": _first(fields, "mrnumber"),
    }


def _bib_occurrence(record: dict[str, object], source_id: str) -> dict[str, object]:
    fields = record["fields"]
    assert isinstance(fields, dict)
    key = str(record["key"])
    if source_id == "mathscinet":
        number = _first(fields, "mrnumber")
        source_record_id = "MR" + number if number else key
        if not re.fullmatch(r"MR[1-9][0-9]*", source_record_id):
            raise B001CatalogError(f"invalid MathSciNet identifier: {source_record_id!r}")
    else:
        source_record_id = key
    bibliography = _bibliographic_from_bib(record)
    return {
        "source_id": source_id,
        "source_record_id": source_record_id,
        "entry_type": str(record["entry_type"]),
        "bibliographic": bibliography,
        "abstract_present": bool(_first(fields, "abstract")),
        "references_present": bool(_first(fields, "references", "reference")),
        "search_signals": detect_search_signals(
            title=str(bibliography["title"]),
            abstract="\n".join(_all(fields, "abstract")),
            keywords=_all(fields, "keywords", "keyword"),
        ),
        "parsed_record_sha256": record["parsed_record_sha256"],
    }


_RIS_TYPES = {
    "JOUR": "article",
    "CONF": "inproceedings",
    "CPAPER": "inproceedings",
    "THES": "thesis",
    "BOOK": "book",
    "CHAP": "incollection",
    "RPRT": "report",
}


def _ris_occurrence(record: dict[str, object], source_id: str) -> dict[str, object]:
    fields = record["fields"]
    assert isinstance(fields, dict)
    if source_id == "wos":
        source_record_id = _first(fields, "ut", "an")
    else:
        source_record_id = _first(fields, "an", "m1")
    if not source_record_id:
        source_record_id = "record:" + str(record["parsed_record_sha256"])
    dois: list[str] = []
    for value in _all(fields, "do"):
        for doi in extract_dois(value):
            if doi not in dois:
                dois.append(doi)
    publication_type = _first(fields, "ty").upper()
    standard_numbers = _all(fields, "sn")
    isbns = [
        value
        for value in standard_numbers
        if len(re.sub(r"[^0-9Xx]", "", value)) in {10, 13}
    ]
    issns = [
        value
        for value in standard_numbers
        if len(re.sub(r"[^0-9Xx]", "", value)) == 8
    ]
    title = _first(fields, "ti", "t1")
    return {
        "source_id": source_id,
        "source_record_id": source_record_id,
        "entry_type": _RIS_TYPES.get(publication_type, publication_type.casefold()),
        "bibliographic": {
            "title": title,
            "authors": _all(fields, "au", "a1"),
            "editors": _all(fields, "ed", "a2"),
            "year": _first(fields, "py", "y1", "da"),
            "doi": dois,
            "venue": _first(fields, "t2", "jf", "jo"),
            "volume": _first(fields, "vl"),
            "issue": _first(fields, "is"),
            "pages": "-".join(
                value for value in (_first(fields, "sp"), _first(fields, "ep")) if value
            ),
            "publisher": _first(fields, "pb"),
            "isbn": isbns,
            "issn": issns,
            "mrnumber": "",
        },
        "abstract_present": bool(_first(fields, "ab")),
        "references_present": bool(_first(fields, "cr")),
        "search_signals": detect_search_signals(
            title=title,
            abstract="\n".join(_all(fields, "ab")),
            keywords=_all(fields, "kw"),
        ),
        "parsed_record_sha256": record["parsed_record_sha256"],
    }


def parse_scopus_csv(stream: TextIO, *, source_name: str) -> Iterable[dict[str, object]]:
    csv.field_size_limit(64 * 1024 * 1024)
    reader = csv.DictReader(stream)
    if not reader.fieldnames or "EID" not in reader.fieldnames or "Title" not in reader.fieldnames:
        raise B001CatalogError(f"{source_name}: invalid Scopus header")
    for ordinal, row in enumerate(reader, start=1):
        if None in row:
            raise B001CatalogError(f"{source_name}:{ordinal}: CSV row width mismatch")
        source_record_id = (row.get("EID") or "").strip()
        row_hash = _sha256_bytes(_canonical_json(row))
        if not source_record_id:
            source_record_id = "record:" + row_hash
        dois = extract_dois(row.get("DOI") or "")
        authors_value = row.get("Author full names") or row.get("Authors") or ""
        authors = _split_people_values([authors_value], separator=";")
        authors = [re.sub(r"\s*\([0-9-]+\)\s*$", "", author).strip() for author in authors]
        title = (row.get("Title") or "").strip()
        yield {
            "source_id": "scopus",
            "source_record_id": source_record_id,
            "entry_type": (row.get("Document Type") or "unknown").strip().casefold(),
            "bibliographic": {
                "title": title,
                "authors": authors,
                "editors": _split_people_values(
                    [row.get("Editors") or ""], separator=";"
                ),
                "year": (row.get("Year") or "").strip(),
                "doi": dois,
                "venue": (row.get("Source title") or "").strip(),
                "volume": (row.get("Volume") or "").strip(),
                "issue": (row.get("Issue") or "").strip(),
                "pages": "-".join(
                    value
                    for value in (
                        (row.get("Page start") or "").strip(),
                        (row.get("Page end") or "").strip(),
                    )
                    if value
                ),
                "publisher": (row.get("Publisher") or "").strip(),
                "isbn": [value for value in [(row.get("ISBN") or "").strip()] if value],
                "issn": [value for value in [(row.get("ISSN") or "").strip()] if value],
                "mrnumber": "",
            },
            "abstract_present": bool((row.get("Abstract") or "").strip()),
            "references_present": bool((row.get("References") or "").strip()),
            "search_signals": detect_search_signals(
                title=title,
                abstract=row.get("Abstract") or "",
                keywords=[
                    row.get("Author Keywords") or "",
                    row.get("Index Keywords") or "",
                ],
            ),
            "parsed_record_sha256": row_hash,
        }


def _safe_artifact_path(root: Path, relative: str) -> Path:
    if not relative or "\\" in relative or Path(relative).is_absolute():
        raise B001CatalogError(f"unsafe artifact path: {relative!r}")
    parts = Path(relative.replace("/", os.sep)).parts
    if ".." in parts:
        raise B001CatalogError(f"unsafe artifact path: {relative!r}")
    path = (root / Path(*parts)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise B001CatalogError(f"artifact escapes baseline root: {relative!r}") from error
    return path


def load_corpus(root: Path, manifest_path: Path) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise B001CatalogError("B001 manifest lacks artifacts")
    occurrences: list[dict[str, object]] = []
    source_counts: Counter[str] = Counter()
    checked_artifacts: list[dict[str, object]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise B001CatalogError("invalid artifact entry")
        relative = str(artifact.get("path", ""))
        path = _safe_artifact_path(root, relative)
        actual_size = path.stat().st_size
        actual_hash = _sha256_file(path)
        if actual_size != artifact.get("bytes") or actual_hash != artifact.get("sha256"):
            raise B001CatalogError(f"artifact hash/size mismatch: {relative}")
        source_id = str(artifact.get("source_id"))
        query_id = str(artifact.get("query_id"))
        media_type = str(artifact.get("media_type"))
        if media_type == "application/x-bibtex":
            parsed = parse_bibtex_tolerant(
                path.read_text(encoding="utf-8-sig"), source_name=relative
            )
            loaded = [_bib_occurrence(record, source_id) for record in parsed]
        elif media_type == "application/x-research-info-systems":
            parsed = parse_ris(path.read_text(encoding="utf-8-sig"), source_name=relative)
            loaded = [_ris_occurrence(record, source_id) for record in parsed]
        elif media_type == "text/csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                loaded = list(parse_scopus_csv(handle, source_name=relative))
        else:
            raise B001CatalogError(f"unsupported media type: {media_type}")
        expected_count = artifact.get("record_count")
        if len(loaded) != expected_count:
            raise B001CatalogError(
                f"record count mismatch for {relative}: {len(loaded)} != {expected_count}"
            )
        for rank, occurrence in enumerate(loaded, start=1):
            occurrence["provenance"] = {
                "batch_id": "B001",
                "source_id": source_id,
                "query_id": query_id,
                "rank": rank,
                "path": relative,
                "artifact_sha256": actual_hash,
            }
            occurrences.append(occurrence)
        source_counts[source_id] += len(loaded)
        checked_artifacts.append(
            {
                "source_id": source_id,
                "query_id": query_id,
                "path": relative,
                "bytes": actual_size,
                "sha256": actual_hash,
                "record_count": len(loaded),
            }
        )
    return {
        "occurrences": occurrences,
        "source_counts": dict(sorted(source_counts.items())),
        "artifacts": checked_artifacts,
        "artifact_mismatches": 0,
        "source_manifest_sha256": _sha256_file(manifest_path),
    }


def load_review_material(
    root: Path, candidate_record: dict[str, object]
) -> dict[str, object]:
    provenance = candidate_record.get("provenance")
    if not isinstance(provenance, list) or not provenance:
        raise B001CatalogError("candidate has no provenance")
    locator = provenance[0]
    if not isinstance(locator, dict):
        raise B001CatalogError("candidate provenance is invalid")
    relative = locator.get("path")
    rank = locator.get("rank")
    if not isinstance(relative, str) or not isinstance(rank, int) or rank < 1:
        raise B001CatalogError("candidate provenance lacks path/rank")
    path = _safe_artifact_path(root, relative)
    source_id = str(candidate_record.get("source_id", ""))
    if source_id == "scopus":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            csv.field_size_limit(64 * 1024 * 1024)
            reader = csv.DictReader(handle)
            selected = None
            for index, row in enumerate(reader, start=1):
                if index == rank:
                    selected = row
                    break
        if selected is None:
            raise B001CatalogError(f"review rank is outside CSV: {relative}#{rank}")
        source_record_id = (selected.get("EID") or "").strip()
        title = (selected.get("Title") or "").strip()
        abstract = (selected.get("Abstract") or "").strip()
        keywords = [
            value.strip()
            for value in (
                selected.get("Author Keywords") or "",
                selected.get("Index Keywords") or "",
            )
            if value.strip()
        ]
    elif source_id in {"wos", "pqdt"}:
        parsed = parse_ris(path.read_text(encoding="utf-8-sig"), source_name=relative)
        if rank > len(parsed):
            raise B001CatalogError(f"review rank is outside RIS: {relative}#{rank}")
        source = parsed[rank - 1]
        fields = source["fields"]
        assert isinstance(fields, dict)
        occurrence = _ris_occurrence(source, source_id)
        source_record_id = str(occurrence["source_record_id"])
        title = _first(fields, "ti", "t1")
        abstract = "\n".join(_all(fields, "ab"))
        keywords = _all(fields, "kw")
    else:
        parsed = parse_bibtex_tolerant(
            path.read_text(encoding="utf-8-sig"), source_name=relative
        )
        if rank > len(parsed):
            raise B001CatalogError(f"review rank is outside BibTeX: {relative}#{rank}")
        source = parsed[rank - 1]
        fields = source["fields"]
        assert isinstance(fields, dict)
        occurrence = _bib_occurrence(source, source_id)
        source_record_id = str(occurrence["source_record_id"])
        title = _first(fields, "title")
        abstract = "\n".join(_all(fields, "abstract"))
        keywords = _all(fields, "keywords", "keyword")
    expected_id = str(candidate_record.get("source_record_id", ""))
    if source_record_id.casefold() != expected_id.casefold():
        raise B001CatalogError(
            f"review locator ID mismatch: {source_record_id!r} != {expected_id!r}"
        )
    return {
        "candidate_id": candidate_record.get("candidate_id"),
        "source_id": source_id,
        "source_record_id": source_record_id,
        "path": relative,
        "rank": rank,
        "query_id": locator.get("query_id"),
        "title": title,
        "abstract": abstract,
        "keywords": keywords,
    }


def _normalize_year(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"(?<![0-9])([12][0-9]{3})(?![0-9])", value)
    return int(match.group(1)) if match else None


def _normalize_isbns(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    output: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        for item in re.split(r"[;,]", value):
            normalized = re.sub(r"[^0-9Xx]", "", item).upper()
            if len(normalized) in {10, 13} and normalized not in output:
                output.append(normalized)
    return output


def _normalize_people(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    output: list[str] = []
    for value in values:
        if isinstance(value, str):
            normalized = _helpers.normalize_text(value)[0]
            if normalized and normalized not in output:
                output.append(normalized)
    return output


def normalize_bibliographic(
    bibliographic: dict[str, object], entry_type: str
) -> dict[str, object]:
    title_value = bibliographic.get("title")
    title = _helpers.normalize_text(title_value)[0] if isinstance(title_value, str) else ""
    authors = _normalize_people(bibliographic.get("authors"))
    editors = _normalize_people(bibliographic.get("editors"))
    creator_role = "author" if authors else "editor" if editors else None
    creators = authors if authors else editors
    dois: list[str] = []
    doi_values = bibliographic.get("doi")
    if isinstance(doi_values, list):
        for value in doi_values:
            if isinstance(value, str):
                for doi in extract_dois(value):
                    if doi not in dois:
                        dois.append(doi)
    publication: dict[str, object] = {"entry_type": entry_type}
    for key in ("venue", "volume", "issue", "pages", "publisher"):
        value = bibliographic.get(key)
        if isinstance(value, str) and value.strip():
            publication[key] = _helpers.normalize_text(value)[0]
    return {
        "title": title,
        "creator_role": creator_role,
        "creators": creators,
        "year": _normalize_year(bibliographic.get("year")),
        "dois": dois,
        "isbns": _normalize_isbns(bibliographic.get("isbn")),
        "publication": publication,
    }


def _candidate_id(source_id: str, source_record_id: str) -> str:
    if source_id == "mathscinet" and re.fullmatch(r"MR[1-9][0-9]*", source_record_id):
        return source_record_id
    digest = _sha256_bytes(f"{source_id}\0{source_record_id}".encode("utf-8"))[:20]
    prefix = {
        "acm-dl": "ACM",
        "ieee-xplore": "IEEE",
        "pqdt": "PQDT",
        "scopus": "SCOPUS",
        "wos": "WOS",
    }.get(source_id, re.sub(r"[^A-Za-z0-9]", "", source_id).upper() or "SOURCE")
    return f"B001-{prefix}-{digest}"


def aggregate_candidates(
    occurrences: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for occurrence in occurrences:
        source_id = str(occurrence["source_id"])
        source_record_id = str(occurrence["source_record_id"])
        grouped[(source_id, source_record_id.casefold())].append(occurrence)
    candidates: list[dict[str, object]] = []
    for (source_id, _), members in grouped.items():
        source_record_id = str(members[0]["source_record_id"])
        primary = members[0]
        bibliographic = primary["bibliographic"]
        assert isinstance(bibliographic, dict)
        variant_hashes: list[str] = []
        for member in members:
            fingerprint = _sha256_bytes(_canonical_json(member["bibliographic"]))
            if fingerprint not in variant_hashes:
                variant_hashes.append(fingerprint)
        provenance = [dict(member["provenance"]) for member in members]
        provenance.sort(key=lambda item: (str(item.get("query_id")), int(item.get("rank", 0))))
        parsed_hashes = sorted({str(member["parsed_record_sha256"]) for member in members})
        search_signals: dict[str, list[str]] = defaultdict(list)
        for member in members:
            for name, locations in member.get("search_signals", {}).items():
                search_signals[name].extend(locations)
        merged_signals = {
            name: sorted(set(locations), key=lambda value: _LOCATION_ORDER[value])
            for name, locations in sorted(search_signals.items())
        }
        candidate = {
            "schema_version": "pvsnp-b001-candidate/1",
            "candidate_id": _candidate_id(source_id, source_record_id),
            "source_id": source_id,
            "source_record_id": source_record_id,
            "entry_type": str(primary["entry_type"]),
            "bibliographic": bibliographic,
            "normalized": normalize_bibliographic(
                bibliographic, str(primary["entry_type"])
            ),
            "content_flags": {
                "abstract_present": any(bool(member["abstract_present"]) for member in members),
                "references_present": any(
                    bool(member["references_present"]) for member in members
                ),
            },
            "search_signals": merged_signals,
            "review_routing": _review_routing(merged_signals, provenance),
            "occurrence_count": len(members),
            "metadata_variant_count": len(variant_hashes),
            "bibliographic_variant_sha256s": variant_hashes,
            "parsed_record_sha256s": parsed_hashes,
            "provenance": provenance,
        }
        candidates.append(candidate)
    candidates.sort(key=lambda item: (str(item["source_id"]), str(item["candidate_id"])))
    return candidates


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise B001CatalogError(f"invalid JSONL at {path}:{line_number}") from error
            if not isinstance(record, dict):
                raise B001CatalogError(f"non-object JSONL at {path}:{line_number}")
            records.append(record)
    return records


def _relation_id(relation_type: str, signal: object) -> str:
    digest = _sha256_bytes(_canonical_json({"type": relation_type, "signal": signal}))[:20]
    return f"B001-REL-{digest}"


def build_relation_groups(
    b001_candidates: Sequence[dict[str, object]],
    b002_candidates: Sequence[dict[str, object]],
) -> tuple[list[dict[str, object]], int]:
    b002_by_id = {str(record["candidate_id"]): record for record in b002_candidates}
    mr_overlap = sum(
        1
        for record in b001_candidates
        if str(record["candidate_id"]).startswith("MR")
        and str(record["candidate_id"]) in b002_by_id
    )
    members: list[dict[str, object]] = []
    for record in b001_candidates:
        candidate_id = str(record["candidate_id"])
        if candidate_id in b002_by_id:
            continue
        members.append(
            {
                "catalog": "B001",
                "candidate_id": candidate_id,
                "source_id": record.get("source_id"),
                "normalized": record.get("normalized", {}),
            }
        )
    for record in b002_candidates:
        members.append(
            {
                "catalog": "B002",
                "candidate_id": record["candidate_id"],
                "source_id": "mathscinet",
                "normalized": record.get("normalized", {}),
            }
        )
    doi_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    fingerprint_groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for member in members:
        normalized = member.get("normalized")
        if not isinstance(normalized, dict):
            continue
        for doi in normalized.get("dois", []):
            if isinstance(doi, str) and doi:
                doi_groups[doi].append(member)
        title = normalized.get("title")
        year = normalized.get("year")
        creators = normalized.get("creators")
        if title and year and isinstance(creators, list) and creators:
            fingerprint_groups[(title, year, tuple(creators))].append(member)

    relations: list[dict[str, object]] = []

    def unique_group(group: Sequence[dict[str, object]]) -> list[dict[str, object]]:
        unique: dict[tuple[str, str], dict[str, object]] = {}
        for member in group:
            key = (str(member["catalog"]), str(member["candidate_id"]))
            unique[key] = member
        return [unique[key] for key in sorted(unique)]

    for doi, group in sorted(doi_groups.items()):
        unique = unique_group(group)
        if len(unique) < 2 or not any(member["catalog"] == "B001" for member in unique):
            continue
        signal = {"doi": doi}
        relations.append(
            {
                "schema_version": "pvsnp-b001-relation-candidate/1",
                "relation_id": _relation_id("same_doi_candidate", signal),
                "relation_type": "same_doi_candidate",
                "status": "unverified_candidate",
                "signal": signal,
                "members": [
                    {
                        "catalog": member["catalog"],
                        "candidate_id": member["candidate_id"],
                        "source_id": member["source_id"],
                    }
                    for member in unique
                ],
            }
        )
    for fingerprint, group in sorted(fingerprint_groups.items(), key=lambda item: str(item[0])):
        unique = unique_group(group)
        catalogs = {str(member["catalog"]) for member in unique}
        source_ids = {str(member["source_id"]) for member in unique}
        if (
            len(unique) < 2
            or not any(member["catalog"] == "B001" for member in unique)
            or (len(catalogs) == 1 and len(source_ids) == 1)
        ):
            continue
        title, year, creators = fingerprint
        signal = {"title": title, "year": year, "creators": list(creators)}
        relations.append(
            {
                "schema_version": "pvsnp-b001-relation-candidate/1",
                "relation_id": _relation_id(
                    "same_bibliographic_fingerprint_candidate", signal
                ),
                "relation_type": "same_bibliographic_fingerprint_candidate",
                "status": "unverified_candidate",
                "signal": signal,
                "members": [
                    {
                        "catalog": member["catalog"],
                        "candidate_id": member["candidate_id"],
                        "source_id": member["source_id"],
                    }
                    for member in unique
                ],
            }
        )
    relations.sort(key=lambda item: str(item["relation_id"]))
    return relations, mr_overlap


def build_direct_title_queue(
    candidates: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[bytes, tuple[dict[str, object], list[dict[str, object]]]] = {}
    for candidate in candidates:
        signals = candidate.get("search_signals")
        if not isinstance(signals, dict) or "title" not in signals.get(
            "direct_p_vs_np", []
        ):
            continue
        normalized = candidate.get("normalized")
        if not isinstance(normalized, dict):
            continue
        dois = normalized.get("dois")
        if isinstance(dois, list) and dois:
            signal: dict[str, object] = {"doi": dois[0]}
        else:
            signal = {
                "title": normalized.get("title"),
                "year": normalized.get("year"),
                "creators": normalized.get("creators", []),
            }
        key = _canonical_json(signal)
        if key not in grouped:
            grouped[key] = (signal, [])
        grouped[key][1].append(candidate)
    queue: list[dict[str, object]] = []
    for key in sorted(grouped):
        signal, members = grouped[key]
        members = sorted(members, key=lambda item: str(item["candidate_id"]))
        compact_members = [
            {
                "candidate_id": member["candidate_id"],
                "source_id": member["source_id"],
                "source_record_id": member["source_record_id"],
                "entry_type": member["entry_type"],
                "title": member["bibliographic"].get("title"),
                "year": member["normalized"].get("year"),
                "venue": member["bibliographic"].get("venue"),
                "query_ids": sorted(
                    {str(item.get("query_id")) for item in member.get("provenance", [])}
                ),
                "search_signals": member.get("search_signals", {}),
            }
            for member in members
        ]
        queue.append(
            {
                "schema_version": "pvsnp-b001-direct-title-queue/1",
                "cluster_id": "B001-DIRECT-"
                + _sha256_bytes(_canonical_json(signal))[:20],
                "signal": signal,
                "member_count": len(compact_members),
                "members": compact_members,
                "status": "unreviewed",
            }
        )
    queue.sort(key=lambda item: str(item["cluster_id"]))
    return queue


def build_direct_axis_queue(
    candidates: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[bytes, tuple[dict[str, object], list[dict[str, object]]]] = {}
    for candidate in candidates:
        signals = candidate.get("search_signals")
        if not isinstance(signals, dict):
            continue
        direct_locations = signals.get("direct_p_vs_np", [])
        named_axes = sorted(_NAMED_AXIS_SIGNALS & set(signals))
        if not direct_locations or "title" in direct_locations or not named_axes:
            continue
        normalized = candidate.get("normalized")
        if not isinstance(normalized, dict):
            continue
        dois = normalized.get("dois")
        if isinstance(dois, list) and dois:
            signal: dict[str, object] = {"doi": dois[0]}
        else:
            signal = {
                "title": normalized.get("title"),
                "year": normalized.get("year"),
                "creators": normalized.get("creators", []),
            }
        key = _canonical_json(signal)
        if key not in grouped:
            grouped[key] = (signal, [])
        grouped[key][1].append(candidate)
    queue: list[dict[str, object]] = []
    for key in sorted(grouped):
        signal, members = grouped[key]
        members = sorted(members, key=lambda item: str(item["candidate_id"]))
        compact_members = []
        for member in members:
            signals = member.get("search_signals", {})
            compact_members.append(
                {
                    "candidate_id": member["candidate_id"],
                    "source_id": member["source_id"],
                    "source_record_id": member["source_record_id"],
                    "entry_type": member["entry_type"],
                    "title": member["bibliographic"].get("title"),
                    "year": member["normalized"].get("year"),
                    "venue": member["bibliographic"].get("venue"),
                    "query_ids": sorted(
                        {
                            str(item.get("query_id"))
                            for item in member.get("provenance", [])
                        }
                    ),
                    "named_axes": sorted(_NAMED_AXIS_SIGNALS & set(signals)),
                    "search_signals": signals,
                }
            )
        queue.append(
            {
                "schema_version": "pvsnp-b001-direct-axis-queue/1",
                "cluster_id": "B001-AXIS-"
                + _sha256_bytes(_canonical_json(signal))[:20],
                "signal": signal,
                "member_count": len(compact_members),
                "members": compact_members,
                "status": "unreviewed",
            }
        )
    queue.sort(key=lambda item: str(item["cluster_id"]))
    return queue


def build_barrier_title_queue(
    candidates: Sequence[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[bytes, tuple[dict[str, object], list[dict[str, object]]]] = {}
    for candidate in candidates:
        if candidate.get("review_routing") != "named_complexity_axis_signal":
            continue
        signals = candidate.get("search_signals")
        if not isinstance(signals, dict):
            continue
        title_axes = sorted(
            name
            for name in _PRIORITY_BARRIER_TITLE_SIGNALS
            if name in signals and "title" in signals[name]
        )
        if not title_axes:
            continue
        normalized = candidate.get("normalized")
        if not isinstance(normalized, dict):
            continue
        dois = normalized.get("dois")
        if isinstance(dois, list) and dois:
            signal: dict[str, object] = {"doi": dois[0]}
        else:
            signal = {
                "title": normalized.get("title"),
                "year": normalized.get("year"),
                "creators": normalized.get("creators", []),
            }
        key = _canonical_json(signal)
        if key not in grouped:
            grouped[key] = (signal, [])
        grouped[key][1].append(candidate)
    queue: list[dict[str, object]] = []
    for key in sorted(grouped):
        signal, members = grouped[key]
        members = sorted(members, key=lambda item: str(item["candidate_id"]))
        compact_members = []
        for member in members:
            signals = member.get("search_signals", {})
            compact_members.append(
                {
                    "candidate_id": member["candidate_id"],
                    "source_id": member["source_id"],
                    "source_record_id": member["source_record_id"],
                    "entry_type": member["entry_type"],
                    "title": member["bibliographic"].get("title"),
                    "year": member["normalized"].get("year"),
                    "venue": member["bibliographic"].get("venue"),
                    "query_ids": sorted(
                        {
                            str(item.get("query_id"))
                            for item in member.get("provenance", [])
                        }
                    ),
                    "title_axes": sorted(
                        name
                        for name in _PRIORITY_BARRIER_TITLE_SIGNALS
                        if name in signals and "title" in signals[name]
                    ),
                    "search_signals": signals,
                }
            )
        queue.append(
            {
                "schema_version": "pvsnp-b001-barrier-title-queue/1",
                "cluster_id": "B001-BARRIER-"
                + _sha256_bytes(_canonical_json(signal))[:20],
                "signal": signal,
                "member_count": len(compact_members),
                "members": compact_members,
                "status": "unreviewed",
            }
        )
    queue.sort(key=lambda item: str(item["cluster_id"]))
    return queue


def _jsonl_bytes(records: Sequence[dict[str, object]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def build_outputs(
    root: Path,
    manifest_path: Path,
    b002_candidates_path: Path,
    candidates_path: Path,
    relations_path: Path,
    direct_queue_path: Path,
    direct_axis_queue_path: Path,
    barrier_title_queue_path: Path,
    output_manifest_path: Path,
) -> dict[str, object]:
    corpus = load_corpus(root, manifest_path)
    occurrences = corpus["occurrences"]
    assert isinstance(occurrences, list)
    candidates = aggregate_candidates(occurrences)
    b002_candidates = _load_jsonl(b002_candidates_path)
    relations, mr_overlap = build_relation_groups(candidates, b002_candidates)
    direct_queue = build_direct_title_queue(candidates)
    direct_axis_queue = build_direct_axis_queue(candidates)
    barrier_title_queue = build_barrier_title_queue(candidates)
    candidate_bytes = _jsonl_bytes(candidates)
    relation_bytes = _jsonl_bytes(relations)
    direct_queue_bytes = _jsonl_bytes(direct_queue)
    direct_axis_queue_bytes = _jsonl_bytes(direct_axis_queue)
    barrier_title_queue_bytes = _jsonl_bytes(barrier_title_queue)
    _atomic_write(candidates_path, candidate_bytes)
    _atomic_write(relations_path, relation_bytes)
    _atomic_write(direct_queue_path, direct_queue_bytes)
    _atomic_write(direct_axis_queue_path, direct_axis_queue_bytes)
    _atomic_write(barrier_title_queue_path, barrier_title_queue_bytes)
    source_candidate_counts = Counter(str(record["source_id"]) for record in candidates)
    entry_types = Counter(str(record["entry_type"]) for record in candidates)
    relation_types = Counter(str(record["relation_type"]) for record in relations)
    review_routing = Counter(str(record["review_routing"]) for record in candidates)
    manifest = {
        "schema_version": "pvsnp-b001-normalized/1",
        "batch_id": "B001",
        "source_manifest": _relative(manifest_path, root),
        "source_manifest_sha256": _sha256_file(manifest_path),
        "normalizer": _relative(SCRIPT_PATH, root),
        "normalizer_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": corpus["artifacts"],
        "counts": {
            "occurrences": len(occurrences),
            "candidates": len(candidates),
            "duplicate_occurrences": len(occurrences) - len(candidates),
            "source_occurrences": corpus["source_counts"],
            "source_candidates": dict(sorted(source_candidate_counts.items())),
            "entry_types": dict(sorted(entry_types.items())),
            "candidates_with_doi": sum(
                1 for record in candidates if record["normalized"]["dois"]
            ),
            "candidates_with_abstract": sum(
                1 for record in candidates if record["content_flags"]["abstract_present"]
            ),
            "candidates_with_references": sum(
                1 for record in candidates if record["content_flags"]["references_present"]
            ),
            "metadata_variant_candidates": sum(
                1 for record in candidates if record["metadata_variant_count"] > 1
            ),
            "b002_mr_overlap": mr_overlap,
            "relations": dict(sorted(relation_types.items())),
            "review_routing": dict(sorted(review_routing.items())),
            "direct_title_review_clusters": len(direct_queue),
            "direct_title_candidate_records": sum(
                int(record["member_count"]) for record in direct_queue
            ),
            "direct_axis_review_clusters": len(direct_axis_queue),
            "direct_axis_candidate_records": sum(
                int(record["member_count"]) for record in direct_axis_queue
            ),
            "barrier_title_review_clusters": len(barrier_title_queue),
            "barrier_title_candidate_records": sum(
                int(record["member_count"]) for record in barrier_title_queue
            ),
        },
        "exceptions": {
            "artifact_mismatches": corpus["artifact_mismatches"],
            "missing_title": sum(
                1 for record in candidates if not record["normalized"]["title"]
            ),
            "missing_creator": sum(
                1 for record in candidates if not record["normalized"]["creators"]
            ),
            "missing_year": sum(
                1 for record in candidates if record["normalized"]["year"] is None
            ),
        },
        "outputs": [
            {
                "path": _relative(candidates_path, root),
                "bytes": len(candidate_bytes),
                "sha256": _sha256_bytes(candidate_bytes),
                "record_count": len(candidates),
            },
            {
                "path": _relative(relations_path, root),
                "bytes": len(relation_bytes),
                "sha256": _sha256_bytes(relation_bytes),
                "record_count": len(relations),
            },
            {
                "path": _relative(direct_queue_path, root),
                "bytes": len(direct_queue_bytes),
                "sha256": _sha256_bytes(direct_queue_bytes),
                "record_count": len(direct_queue),
            },
            {
                "path": _relative(direct_axis_queue_path, root),
                "bytes": len(direct_axis_queue_bytes),
                "sha256": _sha256_bytes(direct_axis_queue_bytes),
                "record_count": len(direct_axis_queue),
            },
            {
                "path": _relative(barrier_title_queue_path, root),
                "bytes": len(barrier_title_queue_bytes),
                "sha256": _sha256_bytes(barrier_title_queue_bytes),
                "record_count": len(barrier_title_queue),
            },
        ],
    }
    _atomic_write(
        output_manifest_path,
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        ),
    )
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build B001 candidate and relation indexes.")
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--b002-candidates", type=Path)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--relations", type=Path)
    parser.add_argument("--direct-queue", type=Path)
    parser.add_argument("--direct-axis-queue", type=Path)
    parser.add_argument("--barrier-title-queue", type=Path)
    parser.add_argument("--output-manifest", type=Path)
    parser.add_argument("--show-review-candidate", action="append")
    parser.add_argument("--review-max-chars", type=int, default=6000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    manifest_path = (args.manifest or root / "manifests/B001.json").resolve()
    b002_candidates_path = (
        args.b002_candidates or root / "catalog/B002-candidates.jsonl"
    ).resolve()
    candidates_path = (
        args.candidates or root / "catalog/B001-candidates.jsonl"
    ).resolve()
    relations_path = (args.relations or root / "catalog/B001-relations.jsonl").resolve()
    direct_queue_path = (
        args.direct_queue or root / "catalog/B001-direct-title-queue.jsonl"
    ).resolve()
    direct_axis_queue_path = (
        args.direct_axis_queue or root / "catalog/B001-direct-axis-queue.jsonl"
    ).resolve()
    barrier_title_queue_path = (
        args.barrier_title_queue or root / "catalog/B001-barrier-title-queue.jsonl"
    ).resolve()
    output_manifest_path = (
        args.output_manifest or root / "manifests/B001-normalized.json"
    ).resolve()
    if args.show_review_candidate:
        candidates = {
            str(record["candidate_id"]): record
            for record in _load_jsonl(candidates_path)
        }
        for candidate_id in args.show_review_candidate:
            if candidate_id not in candidates:
                raise B001CatalogError(f"unknown B001 candidate: {candidate_id}")
            material = load_review_material(root, candidates[candidate_id])
            abstract = str(material.pop("abstract"))
            material["abstract_length"] = len(abstract)
            material["abstract_sha256"] = _sha256_bytes(abstract.encode("utf-8"))
            material["abstract_excerpt"] = abstract[: args.review_max_chars]
            print(json.dumps(material, ensure_ascii=False, sort_keys=True))
        return 0
    result = build_outputs(
        root,
        manifest_path,
        b002_candidates_path,
        candidates_path,
        relations_path,
        direct_queue_path,
        direct_axis_queue_path,
        barrier_title_queue_path,
        output_manifest_path,
    )
    print(
        f"built occurrences={result['counts']['occurrences']} "
        f"candidates={result['counts']['candidates']} "
        f"relations={sum(result['counts']['relations'].values())}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except B001CatalogError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
