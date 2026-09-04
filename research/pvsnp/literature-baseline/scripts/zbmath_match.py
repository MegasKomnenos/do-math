#!/usr/bin/env python3
"""Match DOI-less B002 records with the public zbMATH citation matcher."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASELINE_ROOT = SCRIPT_PATH.parents[1]
DEFAULT_CANDIDATES = DEFAULT_BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
DEFAULT_SOURCE_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B002-normalized.json"
DEFAULT_RESPONSE_ROOT = (
    DEFAULT_BASELINE_ROOT / "intake" / "B002-public" / "zbmath-citation-matcher"
)
DEFAULT_INDEX = DEFAULT_BASELINE_ROOT / "catalog" / "B002-zbmath-matches.jsonl"
DEFAULT_OUTPUT_MANIFEST = (
    DEFAULT_BASELINE_ROOT / "manifests" / "B002-zbmath-matches.json"
)
DEFAULT_ENDPOINT = "https://zbmath.org/citationmatching/match"
SCHEMA_VERSION = "pvsnp-zbmath-match-envelope/1"


def _load_normalizer():
    path = SCRIPT_PATH.with_name("build_b002_catalog.py")
    spec = importlib.util.spec_from_file_location("b002_zbmath_normalizer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the B002 title normalizer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalize_text


_normalize_text = _load_normalizer()


class ZbmathMatchError(RuntimeError):
    pass


class ResponseValidationError(ZbmathMatchError):
    pass


class ExistingResponseError(ZbmathMatchError):
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


def _mr_sort_key(value: str) -> int:
    match = re.fullmatch(r"MR([1-9][0-9]*)", value)
    if not match:
        raise ZbmathMatchError(f"invalid MR candidate ID: {value!r}")
    return int(match.group(1))


def _field_value(record: dict[str, object], name: str) -> str:
    fields = record.get("fields")
    if not isinstance(fields, list):
        return ""
    for field in fields:
        if isinstance(field, dict) and field.get("name") == name:
            value = field.get("value")
            return value if isinstance(value, str) else ""
    return ""


def _matcher_query(record: dict[str, object]) -> dict[str, object]:
    normalized = record.get("normalized")
    if not isinstance(normalized, dict):
        raise ZbmathMatchError(f"candidate lacks normalized data: {record!r}")
    title = _field_value(record, "title")
    if not title:
        raise ZbmathMatchError(f"candidate lacks title: {record.get('candidate_id')!r}")
    query: dict[str, object] = {"t": title, "n": 3, "m": 0, "f": "latex"}
    creators = normalized.get("creators")
    if isinstance(creators, list) and all(isinstance(value, str) for value in creators):
        if creators:
            query["a"] = creators
    year = normalized.get("year")
    if isinstance(year, int):
        query["y"] = str(year)
    return query


def load_doi_less_candidates(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                source = json.loads(line)
            except json.JSONDecodeError as error:
                raise ZbmathMatchError(f"invalid JSONL at {path}:{line_number}") from error
            candidate_id = source.get("candidate_id")
            if not isinstance(candidate_id, str):
                raise ZbmathMatchError(f"missing candidate_id at {path}:{line_number}")
            if candidate_id in seen:
                raise ZbmathMatchError(f"duplicate candidate_id: {candidate_id}")
            seen.add(candidate_id)
            normalized = source.get("normalized")
            dois = normalized.get("dois") if isinstance(normalized, dict) else None
            if not isinstance(dois, list):
                raise ZbmathMatchError(f"invalid DOI list for {candidate_id}")
            if dois:
                continue
            compact = dict(source)
            compact["query"] = _matcher_query(source)
            records.append(compact)
    records.sort(key=lambda item: _mr_sort_key(str(item["candidate_id"])))
    return records


def make_batches(
    records: Sequence[dict[str, object]], batch_size: int = 100
) -> Iterable[list[dict[str, object]]]:
    if not 1 <= batch_size <= 100:
        raise ZbmathMatchError("batch size must be between 1 and 100")
    for offset in range(0, len(records), batch_size):
        yield list(records[offset : offset + batch_size])


def response_filename(batch_number: int) -> str:
    if batch_number < 1:
        raise ZbmathMatchError("batch number must be positive")
    return f"batch-{batch_number:04d}.json"


def make_envelope(
    *,
    batch_number: int,
    candidate_ids: Sequence[str],
    queries: Sequence[dict[str, object]],
    endpoint: str,
    status: int,
    headers: dict[str, str],
    body: bytes,
    retrieved_at: str,
) -> dict[str, object]:
    response_text = body.decode("utf-8")
    payload = {"queries": list(queries)}
    return {
        "schema_version": SCHEMA_VERSION,
        "batch_number": batch_number,
        "candidate_ids": list(candidate_ids),
        "endpoint": endpoint,
        "request_payload": payload,
        "request_sha256": _sha256_bytes(_canonical_json(payload)),
        "http_status": status,
        "headers": dict(sorted(headers.items())),
        "response_sha256": _sha256_bytes(body),
        "response_text": response_text,
        "retrieved_at": retrieved_at,
    }


def validate_envelope_data(
    envelope: dict[str, object],
    *,
    expected_batch_number: int,
    expected_candidate_ids: Sequence[str],
    expected_queries: Sequence[dict[str, object]],
) -> dict[str, object]:
    if envelope.get("schema_version") != SCHEMA_VERSION:
        raise ResponseValidationError("wrong envelope schema")
    if envelope.get("batch_number") != expected_batch_number:
        raise ResponseValidationError("wrong batch number")
    if envelope.get("candidate_ids") != list(expected_candidate_ids):
        raise ResponseValidationError("candidate order mismatch")
    payload = {"queries": list(expected_queries)}
    if envelope.get("request_payload") != payload:
        raise ResponseValidationError("request payload mismatch")
    if envelope.get("request_sha256") != _sha256_bytes(_canonical_json(payload)):
        raise ResponseValidationError("request payload hash mismatch")
    if envelope.get("http_status") != 200:
        raise ResponseValidationError("response is not HTTP 200")
    response_text = envelope.get("response_text")
    if not isinstance(response_text, str):
        raise ResponseValidationError("response text is absent")
    response_bytes = response_text.encode("utf-8")
    if envelope.get("response_sha256") != _sha256_bytes(response_bytes):
        raise ResponseValidationError("response body hash mismatch")
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ResponseValidationError("response is not JSON") from error
    results = parsed.get("results") if isinstance(parsed, dict) else None
    if not isinstance(results, list) or len(results) != len(expected_queries):
        raise ResponseValidationError("result array does not align with queries")
    for result_array in results:
        if not isinstance(result_array, list):
            raise ResponseValidationError("each query result must be an array")
        for item in result_array:
            if not isinstance(item, dict):
                raise ResponseValidationError("citation match must be an object")
            if not isinstance(item.get("title"), str):
                raise ResponseValidationError("citation match lacks title")
            if not isinstance(item.get("zbl_id"), str):
                raise ResponseValidationError("citation match lacks zbl_id")
            score = item.get("score")
            if not isinstance(score, (int, float)):
                raise ResponseValidationError("citation match lacks numeric score")
    return parsed


def load_existing_envelope(
    path: Path,
    *,
    batch_number: int,
    candidate_ids: Sequence[str],
    queries: Sequence[dict[str, object]],
) -> tuple[dict[str, object], dict[str, object]]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError("not an object")
        parsed = validate_envelope_data(
            envelope,
            expected_batch_number=batch_number,
            expected_candidate_ids=candidate_ids,
            expected_queries=queries,
        )
    except (OSError, ValueError, json.JSONDecodeError, ResponseValidationError) as error:
        raise ExistingResponseError(
            f"existing zbMATH response is invalid for batch {batch_number}; refusing overwrite"
        ) from error
    return envelope, parsed


def _request_batch(
    endpoint: str,
    payload: dict[str, object],
    timeout_seconds: float,
) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(
        endpoint,
        data=_canonical_json(payload),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "pvsnp-literature-review/1.0 (bibliographic metadata)",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        headers = {
            key.lower(): value
            for key, value in response.headers.items()
            if key.lower() in {"content-type", "date", "retry-after"}
        }
        return response.status, headers, response.read()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def collect_responses(
    batches: Sequence[list[dict[str, object]]],
    response_root: Path,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    delay_seconds: float = 1.0,
    timeout_seconds: float = 90.0,
    max_retries: int = 4,
) -> tuple[int, int, int]:
    response_root.mkdir(parents=True, exist_ok=True)
    existing = 0
    collected = 0
    for batch_number, batch in enumerate(batches, start=1):
        candidate_ids = [str(record["candidate_id"]) for record in batch]
        queries = [dict(record["query"]) for record in batch]
        path = response_root / response_filename(batch_number)
        if path.exists():
            load_existing_envelope(
                path,
                batch_number=batch_number,
                candidate_ids=candidate_ids,
                queries=queries,
            )
            existing += 1
            continue
        payload = {"queries": queries}
        last_error: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                status, headers, body = _request_batch(
                    endpoint, payload, timeout_seconds
                )
                envelope = make_envelope(
                    batch_number=batch_number,
                    candidate_ids=candidate_ids,
                    queries=queries,
                    endpoint=endpoint,
                    status=status,
                    headers=headers,
                    body=body,
                    retrieved_at=_utc_now(),
                )
                validate_envelope_data(
                    envelope,
                    expected_batch_number=batch_number,
                    expected_candidate_ids=candidate_ids,
                    expected_queries=queries,
                )
                _atomic_write(
                    path,
                    (
                        json.dumps(
                            envelope, ensure_ascii=False, indent=2, sort_keys=True
                        )
                        + "\n"
                    ).encode("utf-8"),
                )
                collected += 1
                print(
                    f"zbmath progress batch={batch_number}/{len(batches)} "
                    f"candidates={len(candidate_ids)}"
                )
                break
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code not in {429, 500, 502, 503, 504}:
                    raise ZbmathMatchError(
                        f"zbMATH batch {batch_number} failed with HTTP {error.code}"
                    ) from error
            except (ResponseValidationError, UnicodeDecodeError) as error:
                # The service can return HTTP 200 with a malformed per-query result
                # under load. Treat the entire batch as uncommitted and retry it.
                last_error = error
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                last_error = error
            if attempt == max_retries:
                raise ZbmathMatchError(
                    f"zbMATH batch {batch_number} failed after retries: {last_error}"
                ) from last_error
            time.sleep(min(2 ** (attempt + 1), 30))
        if delay_seconds > 0 and batch_number < len(batches):
            time.sleep(delay_seconds)
    remaining = len(batches) - existing - collected
    return existing, collected, remaining


def _result_year(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\b([12][0-9]{3})\b", value)
        if match:
            return int(match.group(1))
    return None


def triage_results(
    candidate_record: dict[str, object], results: Sequence[dict[str, object]]
) -> dict[str, object]:
    if not results:
        return {
            "classification": "no_results",
            "best_result_index": None,
            "result_signals": [],
        }
    normalized = candidate_record.get("normalized")
    if not isinstance(normalized, dict):
        raise ZbmathMatchError("candidate lacks normalized data")
    candidate_title = normalized.get("title")
    candidate_year = normalized.get("year")
    signals: list[dict[str, object]] = []
    priorities: list[tuple[int, int]] = []
    for index, result in enumerate(results):
        result_title = result.get("title")
        title_normalized = (
            _normalize_text(result_title)[0] if isinstance(result_title, str) else ""
        )
        exact = bool(candidate_title and title_normalized == candidate_title)
        containment = bool(
            candidate_title
            and title_normalized
            and not exact
            and (
                str(candidate_title) in title_normalized
                or title_normalized in str(candidate_title)
            )
        )
        year = _result_year(result.get("year"))
        year_delta = (
            year - candidate_year
            if isinstance(candidate_year, int) and isinstance(year, int)
            else None
        )
        signals.append(
            {
                "normalized_title": title_normalized,
                "exact_title": exact,
                "title_containment": containment,
                "year": year,
                "year_delta": year_delta,
            }
        )
        if exact and year_delta == 0:
            priority = 0
        elif exact and isinstance(year_delta, int) and abs(year_delta) <= 1:
            priority = 1
        elif exact:
            priority = 2
        elif containment:
            priority = 3
        else:
            priority = 4
        priorities.append((priority, index))
    best_priority, best_index = min(priorities)
    classification = {
        0: "exact_title_same_year",
        1: "exact_title_near_year",
        2: "exact_title_other_or_missing_year",
        3: "title_containment",
        4: "fuzzy_candidates_only",
    }[best_priority]
    return {
        "classification": classification,
        "best_result_index": best_index,
        "result_signals": signals,
    }


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _safe_result(result: dict[str, object]) -> dict[str, object]:
    keys = (
        "score",
        "probability",
        "zbl_id",
        "title",
        "authors",
        "source",
        "pagination",
        "year",
    )
    return {key: result.get(key) for key in keys if key in result}


def validate_source_manifest(
    source_manifest: dict[str, object], candidates_path: Path
) -> None:
    outputs = source_manifest.get("outputs")
    if not isinstance(outputs, list):
        raise ZbmathMatchError("normalization manifest outputs must be a list")
    candidate_output = None
    for output in outputs:
        if (
            isinstance(output, dict)
            and output.get("path") == "catalog/B002-candidates.jsonl"
        ):
            candidate_output = output
            break
    if candidate_output is None:
        raise ZbmathMatchError("normalization manifest lacks the candidate output")
    if candidate_output.get("sha256") != _sha256_file(candidates_path):
        raise ZbmathMatchError("candidate index hash does not match normalization manifest")


def build_outputs(
    root: Path,
    candidates_path: Path,
    source_manifest_path: Path,
    response_root: Path,
    index_path: Path,
    manifest_path: Path,
    *,
    batch_size: int = 100,
) -> dict[str, object]:
    candidates = load_doi_less_candidates(candidates_path)
    batches = list(make_batches(candidates, batch_size=batch_size))
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if not isinstance(source_manifest, dict):
        raise ZbmathMatchError("normalization manifest must be an object")
    validate_source_manifest(source_manifest, candidates_path)
    records: list[dict[str, object]] = []
    artifacts: list[dict[str, object]] = []
    classifications: Counter[str] = Counter()
    returned_result_count = 0
    for batch_number, batch in enumerate(batches, start=1):
        candidate_ids = [str(record["candidate_id"]) for record in batch]
        queries = [dict(record["query"]) for record in batch]
        raw_path = response_root / response_filename(batch_number)
        envelope, parsed = load_existing_envelope(
            raw_path,
            batch_number=batch_number,
            candidate_ids=candidate_ids,
            queries=queries,
        )
        raw_hash = _sha256_file(raw_path)
        artifacts.append(
            {
                "path": _relative(raw_path, root),
                "bytes": raw_path.stat().st_size,
                "sha256": raw_hash,
                "batch_number": batch_number,
                "candidate_count": len(batch),
                "retrieved_at": envelope["retrieved_at"],
            }
        )
        for result_index, candidate in enumerate(batch):
            result_array = parsed["results"][result_index]
            triage = triage_results(candidate, result_array)
            classifications[str(triage["classification"])] += 1
            returned_result_count += len(result_array)
            normalized = candidate["normalized"]
            provenance = []
            for item in candidate.get("provenance", []):
                if isinstance(item, dict):
                    provenance.append(
                        {
                            key: item.get(key)
                            for key in ("field_code", "rank", "path")
                            if key in item
                        }
                    )
            records.append(
                {
                    "schema_version": "pvsnp-zbmath-match/1",
                    "candidate_id": candidate["candidate_id"],
                    "candidate": {
                        "title": normalized.get("title"),
                        "year": normalized.get("year"),
                        "creator_role": normalized.get("creator_role"),
                        "creators": normalized.get("creators", []),
                    },
                    "query": candidate["query"],
                    "provenance": provenance,
                    "source": {
                        "raw_path": _relative(raw_path, root),
                        "raw_file_sha256": raw_hash,
                        "batch_number": batch_number,
                        "batch_index": result_index,
                        "retrieved_at": envelope["retrieved_at"],
                    },
                    "results": [_safe_result(item) for item in result_array],
                    **triage,
                }
            )
    index_bytes = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")
    _atomic_write(index_path, index_bytes)
    manifest = {
        "schema_version": "pvsnp-zbmath-match-manifest/1",
        "batch_id": "B002",
        "source_id": "zbmath_citation_matcher",
        "collector": _relative(SCRIPT_PATH, root),
        "collector_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": [
            {
                "path": _relative(candidates_path, root),
                "bytes": candidates_path.stat().st_size,
                "sha256": _sha256_file(candidates_path),
                "record_count": len(candidates),
            },
            {
                "path": _relative(source_manifest_path, root),
                "bytes": source_manifest_path.stat().st_size,
                "sha256": _sha256_file(source_manifest_path),
            },
        ],
        "request_contract": {
            "endpoint": DEFAULT_ENDPOINT,
            "batch_size": batch_size,
            "result_limit_per_query": 3,
            "minimum_score": 0,
            "concurrency": 1,
        },
        "counts": {
            "candidates": len(records),
            "batches": len(batches),
            "returned_results": returned_result_count,
            "classifications": dict(sorted(classifications.items())),
        },
        "response_artifacts": artifacts,
        "output": {
            "path": _relative(index_path, root),
            "bytes": len(index_bytes),
            "sha256": _sha256_bytes(index_bytes),
            "record_count": len(records),
        },
    }
    _atomic_write(
        manifest_path,
        (
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
    )
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Match every DOI-less B002 candidate against zbMATH."
    )
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--response-root", type=Path)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--output-manifest", type=Path)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--limit-batches", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    candidates_path = (args.candidates or root / "catalog/B002-candidates.jsonl").resolve()
    source_manifest_path = (
        args.source_manifest or root / "manifests/B002-normalized.json"
    ).resolve()
    response_root = (
        args.response_root or root / "intake/B002-public/zbmath-citation-matcher"
    ).resolve()
    index_path = (args.index or root / "catalog/B002-zbmath-matches.jsonl").resolve()
    manifest_path = (
        args.output_manifest or root / "manifests/B002-zbmath-matches.json"
    ).resolve()
    candidates = load_doi_less_candidates(candidates_path)
    batches = list(make_batches(candidates, batch_size=args.batch_size))
    if args.limit_batches is not None:
        if args.limit_batches < 0:
            raise ZbmathMatchError("limit-batches must not be negative")
        batches = batches[: args.limit_batches]
    valid_existing = 0
    for batch_number, batch in enumerate(batches, start=1):
        path = response_root / response_filename(batch_number)
        if path.exists():
            load_existing_envelope(
                path,
                batch_number=batch_number,
                candidate_ids=[str(item["candidate_id"]) for item in batch],
                queries=[dict(item["query"]) for item in batch],
            )
            valid_existing += 1
    print(
        f"plan candidates={sum(len(batch) for batch in batches)} "
        f"batches={len(batches)} existing={valid_existing} "
        f"pending={len(batches) - valid_existing}"
    )
    if args.dry_run:
        return 0
    if not args.build_only:
        existing, collected, remaining = collect_responses(
            batches,
            response_root,
            endpoint=args.endpoint,
            delay_seconds=args.delay_seconds,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
        )
        print(
            f"collection existing={existing} collected={collected} remaining={remaining}"
        )
    if len(batches) != len(list(make_batches(candidates, batch_size=args.batch_size))):
        print("partial collection: outputs not built")
        return 0
    manifest = build_outputs(
        root,
        candidates_path,
        source_manifest_path,
        response_root,
        index_path,
        manifest_path,
        batch_size=args.batch_size,
    )
    print(
        f"built records={manifest['counts']['candidates']} "
        f"classifications={manifest['counts']['classifications']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ZbmathMatchError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
