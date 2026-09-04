#!/usr/bin/env python3
"""Fetch and index Crossref metadata for the DOI-bearing B002 candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_BASELINE_ROOT = SCRIPT_PATH.parents[1]
DEFAULT_CANDIDATES = DEFAULT_BASELINE_ROOT / "catalog" / "B002-candidates.jsonl"
DEFAULT_SOURCE_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B002-normalized.json"
DEFAULT_RESPONSE_ROOT = (
    DEFAULT_BASELINE_ROOT / "intake" / "B002-public" / "crossref"
)
DEFAULT_INDEX = DEFAULT_BASELINE_ROOT / "catalog" / "B002-crossref.jsonl"
DEFAULT_OUTPUT_MANIFEST = DEFAULT_BASELINE_ROOT / "manifests" / "B002-crossref.json"
API_ROOT = "https://api.crossref.org/works/"
USER_AGENT = "pvsnp-literature-baseline/1 (noncommercial metadata verification)"
ENVELOPE_SCHEMA = "pvsnp-crossref-response/1"
INDEX_SCHEMA = "pvsnp-crossref-index/1"
MANIFEST_SCHEMA = "pvsnp-crossref-manifest/1"
TERMINAL_HTTP_STATUSES = {200, 404}
RETRY_HTTP_STATUSES = {429, 500, 502, 503, 504}


class CrossrefError(RuntimeError):
    pass


class ResponseValidationError(CrossrefError):
    pass


class ExistingResponseError(CrossrefError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _mr_sort_key(value: str) -> int:
    match = re.fullmatch(r"MR([1-9][0-9]*)", value)
    if not match:
        raise CrossrefError(f"invalid candidate ID: {value!r}")
    return int(match.group(1))


def load_doi_candidates(path: Path) -> dict[str, list[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    try:
        stream = path.open("r", encoding="utf-8")
    except OSError as error:
        raise CrossrefError(f"cannot read candidate index: {path}") from error
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                raise CrossrefError(f"blank candidate line at {path}:{line_number}")
            try:
                candidate = json.loads(line)
                candidate_id = str(candidate["candidate_id"])
                dois = candidate["normalized"]["dois"]
            except (KeyError, TypeError, ValueError) as error:
                raise CrossrefError(
                    f"invalid candidate record at {path}:{line_number}"
                ) from error
            _mr_sort_key(candidate_id)
            if not isinstance(dois, list):
                raise CrossrefError(f"candidate DOI list is invalid for {candidate_id}")
            for doi_value in dois:
                doi = str(doi_value)
                if (
                    not doi.startswith("10.")
                    or doi != doi.casefold()
                    or doi.strip() != doi
                    or any(character.isspace() for character in doi)
                ):
                    raise CrossrefError(f"non-normalized DOI for {candidate_id}: {doi!r}")
                grouped[doi].add(candidate_id)
    return {
        doi: sorted(candidate_ids, key=_mr_sort_key)
        for doi, candidate_ids in sorted(grouped.items())
    }


def response_filename(doi: str) -> str:
    return _sha256_bytes(doi.encode("utf-8")) + ".json"


def endpoint_for_doi(doi: str) -> str:
    return API_ROOT + urllib.parse.quote(doi, safe="")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_envelope(
    *,
    doi: str,
    endpoint: str,
    status: int,
    headers: Mapping[str, str],
    body: bytes,
    retrieved_at: str,
    resolved_endpoint: str | None = None,
) -> dict[str, object]:
    try:
        response_text = body.decode("utf-8")
    except UnicodeError as error:
        raise ResponseValidationError(f"Crossref response is not UTF-8 for {doi}") from error
    selected_headers: dict[str, str] = {}
    lower_headers = {str(name).lower(): str(value) for name, value in headers.items()}
    for name in ("content-type", "etag", "last-modified"):
        if name in lower_headers:
            selected_headers[name] = lower_headers[name]
    return {
        "schema_version": ENVELOPE_SCHEMA,
        "doi": doi,
        "endpoint": endpoint,
        "resolved_endpoint": resolved_endpoint or endpoint,
        "retrieved_at": retrieved_at,
        "http_status": status,
        "headers": selected_headers,
        "response_sha256": _sha256_bytes(body),
        "response_text": response_text,
    }


def validate_envelope_data(
    envelope: dict[str, object], *, expected_doi: str
) -> dict[str, object]:
    if envelope.get("schema_version") != ENVELOPE_SCHEMA:
        raise ResponseValidationError("unexpected Crossref envelope schema")
    if envelope.get("doi") != expected_doi:
        raise ResponseValidationError(f"Crossref envelope DOI mismatch for {expected_doi}")
    if envelope.get("endpoint") != endpoint_for_doi(expected_doi):
        raise ResponseValidationError(f"Crossref endpoint mismatch for {expected_doi}")
    resolved_endpoint = envelope.get("resolved_endpoint", envelope.get("endpoint"))
    if not isinstance(resolved_endpoint, str):
        raise ResponseValidationError(f"invalid resolved endpoint for {expected_doi}")
    retrieved_at = envelope.get("retrieved_at")
    if not isinstance(retrieved_at, str) or not retrieved_at.endswith("Z"):
        raise ResponseValidationError(f"invalid retrieval time for {expected_doi}")
    status = envelope.get("http_status")
    if status not in TERMINAL_HTTP_STATUSES:
        raise ResponseValidationError(f"nonterminal HTTP status for {expected_doi}: {status}")
    response_text = envelope.get("response_text")
    if not isinstance(response_text, str):
        raise ResponseValidationError(f"missing response text for {expected_doi}")
    response_bytes = response_text.encode("utf-8")
    if envelope.get("response_sha256") != _sha256_bytes(response_bytes):
        raise ResponseValidationError(f"response SHA-256 mismatch for {expected_doi}")
    if status == 404:
        return {"state": "crossref_not_found", "message": None}
    try:
        response = json.loads(response_text)
        message = response["message"]
        returned_doi = message["DOI"]
    except (KeyError, TypeError, ValueError) as error:
        raise ResponseValidationError(f"invalid Crossref JSON for {expected_doi}") from error
    returned_doi = str(returned_doi).casefold()
    state = "found"
    if returned_doi != expected_doi:
        parsed = urllib.parse.urlsplit(resolved_endpoint)
        api_path = urllib.parse.urlsplit(API_ROOT).path
        if (
            parsed.scheme != "https"
            or parsed.netloc != urllib.parse.urlsplit(API_ROOT).netloc
            or not parsed.path.startswith(api_path)
        ):
            raise ResponseValidationError(
                f"returned DOI mismatch without a Crossref redirect for {expected_doi}"
            )
        resolved_doi = urllib.parse.unquote(parsed.path[len(api_path) :]).casefold()
        if resolved_doi != returned_doi or resolved_endpoint == envelope.get("endpoint"):
            raise ResponseValidationError(
                f"returned DOI mismatch without a matching redirect for {expected_doi}"
            )
        state = "found_alias"
    return {"state": state, "message": message, "returned_doi": returned_doi}


def load_existing_envelope(path: Path, doi: str) -> dict[str, object]:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError("envelope is not an object")
        validate_envelope_data(envelope, expected_doi=doi)
    except (OSError, UnicodeError, ValueError, ResponseValidationError) as error:
        raise ExistingResponseError(
            f"existing Crossref response is invalid for {doi}; refusing overwrite"
        ) from error
    return envelope


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _serialize_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _retry_delay(headers: Mapping[str, str], attempt: int) -> float:
    lower = {str(name).lower(): str(value) for name, value in headers.items()}
    retry_after = lower.get("retry-after")
    if retry_after:
        try:
            return max(0.0, min(float(retry_after), 60.0))
        except ValueError:
            pass
    return min(2.0 ** attempt, 60.0)


def fetch_response(
    doi: str, timeout_seconds: float
) -> tuple[int, dict[str, str], bytes, str]:
    request = urllib.request.Request(
        endpoint_for_doi(doi),
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return (
                response.status,
                dict(response.headers.items()),
                response.read(),
                response.geturl(),
            )
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers.items()), error.read(), error.geturl()


def collect_responses(
    doi_mapping: Mapping[str, Sequence[str]],
    response_root: Path,
    *,
    delay_seconds: float,
    timeout_seconds: float,
    max_retries: int,
    limit: int | None = None,
    fetcher: Callable[
        [str, float], tuple[int, dict[str, str], bytes, str]
    ] = fetch_response,
) -> tuple[int, int, int]:
    existing = 0
    pending: list[str] = []
    for doi in doi_mapping:
        path = response_root / response_filename(doi)
        if path.exists():
            load_existing_envelope(path, doi)
            existing += 1
        else:
            pending.append(doi)
    if limit is not None:
        pending = pending[:limit]

    collected = 0
    last_request_started = 0.0
    for doi in pending:
        for attempt in range(max_retries + 1):
            elapsed = time.monotonic() - last_request_started
            if elapsed < delay_seconds:
                time.sleep(delay_seconds - elapsed)
            last_request_started = time.monotonic()
            try:
                status, headers, body, resolved_endpoint = fetcher(
                    doi, timeout_seconds
                )
            except (OSError, TimeoutError, urllib.error.URLError) as error:
                if attempt == max_retries:
                    raise CrossrefError(
                        f"Crossref request failed after retries; completed={collected}"
                    ) from error
                time.sleep(min(2.0 ** attempt, 60.0))
                continue
            if status in RETRY_HTTP_STATUSES:
                if attempt == max_retries:
                    raise CrossrefError(
                        f"Crossref returned HTTP {status} after retries; completed={collected}"
                    )
                time.sleep(_retry_delay(headers, attempt))
                continue
            if status not in TERMINAL_HTTP_STATUSES:
                raise CrossrefError(
                    f"unexpected Crossref HTTP {status}; completed={collected}"
                )
            envelope = make_envelope(
                doi=doi,
                endpoint=endpoint_for_doi(doi),
                status=status,
                headers=headers,
                body=body,
                retrieved_at=_utc_now(),
                resolved_endpoint=resolved_endpoint,
            )
            validate_envelope_data(envelope, expected_doi=doi)
            _atomic_write(
                response_root / response_filename(doi), _serialize_json(envelope)
            )
            collected += 1
            if collected == 1 or collected % 100 == 0:
                print(f"crossref progress collected={collected} existing={existing}")
            break

    remaining = len(doi_mapping) - existing - collected
    return existing, collected, remaining


def _copy_list(message: Mapping[str, object], key: str) -> list[object]:
    value = message.get(key, [])
    return list(value) if isinstance(value, list) else []


def _authors(message: Mapping[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for value in _copy_list(message, "author"):
        if not isinstance(value, dict):
            continue
        result.append(
            {
                key: value[key]
                for key in ("given", "family", "ORCID", "sequence")
                if key in value
            }
        )
    return result


def index_record(
    envelope: dict[str, object],
    candidate_ids: Sequence[str],
    raw_path: str,
) -> dict[str, object]:
    doi = str(envelope["doi"])
    validated = validate_envelope_data(envelope, expected_doi=doi)
    base: dict[str, object] = {
        "schema_version": INDEX_SCHEMA,
        "doi": doi,
        "candidate_ids": sorted(set(candidate_ids), key=_mr_sort_key),
        "state": validated["state"],
        "source": {
            "endpoint": envelope["endpoint"],
            "resolved_endpoint": envelope.get(
                "resolved_endpoint", envelope["endpoint"]
            ),
            "retrieved_at": envelope["retrieved_at"],
            "http_status": envelope["http_status"],
            "raw_path": raw_path,
            "raw_file_sha256": None,
            "response_sha256": envelope["response_sha256"],
        },
        "crossref": None,
    }
    message = validated["message"]
    if not isinstance(message, dict):
        return base
    base["crossref"] = {
        "doi": str(message.get("DOI", "")).casefold(),
        "type": message.get("type"),
        "subtype": message.get("subtype"),
        "title": _copy_list(message, "title"),
        "subtitle": _copy_list(message, "subtitle"),
        "author": _authors(message),
        "publisher": message.get("publisher"),
        "container_title": _copy_list(message, "container-title"),
        "published": message.get("published"),
        "published_print": message.get("published-print"),
        "published_online": message.get("published-online"),
        "isbn": _copy_list(message, "ISBN"),
        "issn": _copy_list(message, "ISSN"),
        "url": message.get("URL"),
        "relation": message.get("relation", {}),
        "update_to": _copy_list(message, "update-to"),
        "assertion": _copy_list(message, "assertion"),
        "abstract_present": bool(message.get("abstract")),
    }
    return base


def _relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _validate_input_manifest(
    baseline_root: Path, candidates_path: Path, manifest_path: Path
) -> dict[str, object]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise CrossrefError(f"cannot read normalization manifest: {manifest_path}") from error
    if manifest.get("schema_version") != "pvsnp-b002-normalized/1":
        raise CrossrefError("unexpected normalization manifest schema")
    candidate_relative = _relative_posix(candidates_path, baseline_root)
    output = next(
        (
            item
            for item in manifest.get("outputs", [])
            if item.get("path") == candidate_relative
        ),
        None,
    )
    if output is None:
        raise CrossrefError("candidate index is absent from normalization manifest")
    if output.get("sha256") != _sha256_file(candidates_path):
        raise CrossrefError("candidate index SHA-256 differs from normalization manifest")
    if output.get("bytes") != candidates_path.stat().st_size:
        raise CrossrefError("candidate index byte count differs from normalization manifest")
    return manifest


def _jsonl_bytes(records: Sequence[dict[str, object]]) -> bytes:
    return (
        "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for record in records
        )
    ).encode("utf-8")


def build_index(
    baseline_root: Path,
    candidates_path: Path,
    source_manifest_path: Path,
    response_root: Path,
    index_path: Path,
    output_manifest_path: Path,
) -> dict[str, object]:
    baseline_root = baseline_root.resolve()
    candidates_path = candidates_path.resolve()
    source_manifest_path = source_manifest_path.resolve()
    response_root = response_root.resolve()
    source_manifest = _validate_input_manifest(
        baseline_root, candidates_path, source_manifest_path
    )
    mapping = load_doi_candidates(candidates_path)
    records: list[dict[str, object]] = []
    statuses = Counter()
    field_counts = Counter()
    response_artifacts: list[dict[str, object]] = []
    for doi, candidate_ids in mapping.items():
        path = response_root / response_filename(doi)
        if not path.exists():
            raise CrossrefError(f"missing Crossref response; remaining DOI includes {doi}")
        envelope = load_existing_envelope(path, doi)
        relative = _relative_posix(path, baseline_root)
        record = index_record(envelope, candidate_ids, relative)
        raw_hash = _sha256_file(path)
        record["source"]["raw_file_sha256"] = raw_hash
        records.append(record)
        statuses[str(record["state"])] += 1
        crossref = record["crossref"]
        if isinstance(crossref, dict):
            for key, value in crossref.items():
                if value not in (None, "", [], {}, False):
                    field_counts[key] += 1
        response_artifacts.append(
            {
                "doi": doi,
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": raw_hash,
                "http_status": envelope["http_status"],
            }
        )

    index_bytes = _jsonl_bytes(records)
    _atomic_write(index_path, index_bytes)
    candidate_count = sum(
        1 for line in candidates_path.open("r", encoding="utf-8") if line.strip()
    )
    linked_candidates = {candidate_id for ids in mapping.values() for candidate_id in ids}
    manifest: dict[str, object] = {
        "schema_version": MANIFEST_SCHEMA,
        "batch_id": "B002",
        "source_id": "crossref",
        "collector": _relative_posix(SCRIPT_PATH, baseline_root),
        "collector_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": {
            "candidate_index": _relative_posix(candidates_path, baseline_root),
            "candidate_index_sha256": _sha256_file(candidates_path),
            "normalization_manifest": _relative_posix(
                source_manifest_path, baseline_root
            ),
            "normalization_manifest_sha256": _sha256_file(source_manifest_path),
            "candidate_count": candidate_count,
            "doi_candidate_count": len(linked_candidates),
            "candidate_doi_link_count": sum(len(ids) for ids in mapping.values()),
            "unique_doi_count": len(mapping),
        },
        "response_artifacts": response_artifacts,
        "counts": {
            "states": dict(sorted(statuses.items())),
            "crossref_field_presence": dict(sorted(field_counts.items())),
        },
        "output": {
            "path": _relative_posix(index_path, baseline_root),
            "bytes": len(index_bytes),
            "sha256": _sha256_bytes(index_bytes),
            "record_count": len(records),
        },
        "source_normalization_schema": source_manifest.get("schema_version"),
    }
    _atomic_write(output_manifest_path, _serialize_json(manifest))
    return manifest


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Crossref records for every DOI-bearing B002 candidate."
    )
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_BASELINE_ROOT)
    parser.add_argument("--candidates", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--response-root", type=Path)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--output-manifest", type=Path)
    parser.add_argument("--delay-seconds", type=float, default=0.30)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    if args.delay_seconds < 0.25:
        raise CrossrefError("--delay-seconds must be at least 0.25 for the public pool")
    if args.timeout_seconds <= 0 or args.max_retries < 0:
        raise CrossrefError("timeout must be positive and retries nonnegative")
    if args.limit is not None and args.limit <= 0:
        raise CrossrefError("--limit must be positive")

    root = args.baseline_root.resolve()
    candidates = (args.candidates or root / "catalog" / "B002-candidates.jsonl").resolve()
    source_manifest = (
        args.source_manifest or root / "manifests" / "B002-normalized.json"
    ).resolve()
    response_root = (
        args.response_root or root / "intake" / "B002-public" / "crossref"
    ).resolve()
    index = (args.index or root / "catalog" / "B002-crossref.jsonl").resolve()
    output_manifest = (
        args.output_manifest or root / "manifests" / "B002-crossref.json"
    ).resolve()
    _validate_input_manifest(root, candidates, source_manifest)
    mapping = load_doi_candidates(candidates)
    valid_existing = 0
    for doi in mapping:
        path = response_root / response_filename(doi)
        if path.exists():
            load_existing_envelope(path, doi)
            valid_existing += 1
    pending = len(mapping) - valid_existing
    print(
        f"plan unique_dois={len(mapping)} existing={valid_existing} pending={pending}"
    )
    if args.dry_run:
        return 0
    if not args.build_only and pending:
        existing, collected, remaining = collect_responses(
            mapping,
            response_root,
            delay_seconds=args.delay_seconds,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            limit=args.limit,
        )
        print(
            f"collection existing={existing} collected={collected} remaining={remaining}"
        )
        if remaining:
            return 0
    manifest = build_index(
        root,
        candidates,
        source_manifest,
        response_root,
        index,
        output_manifest,
    )
    print(
        f"built records={manifest['output']['record_count']} "
        f"states={manifest['counts']['states']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CrossrefError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
