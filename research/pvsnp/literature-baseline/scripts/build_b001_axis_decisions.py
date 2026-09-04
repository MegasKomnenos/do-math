#!/usr/bin/env python3
"""Bind B001 direct+axis abstract review reports to their source queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[1]
ALLOWED_DISPOSITIONS = {
    "core_barrier_or_method_candidate",
    "standard_subaxis_research",
    "conditional_problem_result",
    "application_or_distant_bridge",
    "alternative_model_or_relativized_variant",
    "survey_history_or_commentary",
    "purported_resolution_requires_adversarial_review",
    "non_tcs_false_positive",
    "needs_full_text_review",
}
A_ROW = re.compile(
    r"(?m)^\|\s*(?P<id>[0-9a-f]{20})\s*\|\s*(?P<count>[0-9]+)\s*"
    r"\|\s*(?P<basis>.*?)\s*\|\s*`(?P<disposition>[a-z_]+)`\s*\|\s*$"
)
B_ROW = re.compile(
    r"(?m)^\|\s*[0-9]+\s*\|\s*`B001-AXIS-(?P<id>[0-9a-f]{20})`;\s*"
    r"(?P<count>[0-9]+):.*?\|\s*(?P<basis>.*?)\s*\|\s*"
    r"`(?P<disposition>[a-z_]+)`\s*\|\s*$"
)
C_ROW = re.compile(
    r"(?m)^\|\s*`?B001-AXIS-(?P<id>[0-9a-f]{20})`?\s*\|\s*"
    r"(?P<count>[0-9]+)\s*\|\s*.*?\|\s*`?(?P<disposition>[a-z_]+)`?\s*"
    r"\|\s*(?P<basis>.*?)\s*\|\s*$"
)


class DecisionError(RuntimeError):
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


def _load_queue(path: Path) -> dict[str, dict[str, object]]:
    queue: dict[str, dict[str, object]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            cluster_id = record.get("cluster_id")
            if not isinstance(cluster_id, str) or not re.fullmatch(
                r"B001-AXIS-[0-9a-f]{20}", cluster_id
            ):
                raise DecisionError(f"invalid queue cluster at line {line_number}")
            if cluster_id in queue:
                raise DecisionError(f"duplicate queue cluster: {cluster_id}")
            queue[cluster_id] = record
    return queue


def build_decisions(
    queue_path: Path, report_paths: Sequence[Path]
) -> list[dict[str, object]]:
    queue = _load_queue(queue_path)
    parsed: dict[str, dict[str, object]] = {}
    for report_path in report_paths:
        text = report_path.read_text(encoding="utf-8")
        for pattern in (A_ROW, B_ROW, C_ROW):
            for match in pattern.finditer(text):
                cluster_id = "B001-AXIS-" + match.group("id")
                if cluster_id in parsed:
                    raise DecisionError(f"duplicate decision for {cluster_id}")
                disposition = match.group("disposition")
                if disposition not in ALLOWED_DISPOSITIONS:
                    raise DecisionError(
                        f"invalid disposition for {cluster_id}: {disposition}"
                    )
                parsed[cluster_id] = {
                    "member_count": int(match.group("count")),
                    "disposition": disposition,
                    "basis": match.group("basis").strip(),
                    "review_report": report_path.name,
                }
    missing = sorted(set(queue) - set(parsed))
    extra = sorted(set(parsed) - set(queue))
    if missing or extra:
        raise DecisionError(
            f"decision/queue cluster mismatch: missing={missing}, extra={extra}"
        )
    output: list[dict[str, object]] = []
    for cluster_id in sorted(queue):
        source = queue[cluster_id]
        decision = parsed[cluster_id]
        if source.get("member_count") != decision["member_count"]:
            raise DecisionError(f"member count mismatch for {cluster_id}")
        members = source.get("members")
        if not isinstance(members, list):
            raise DecisionError(f"invalid queue members for {cluster_id}")
        output.append(
            {
                "schema_version": "pvsnp-b001-direct-axis-decision/1",
                "cluster_id": cluster_id,
                "signal": source.get("signal", {}),
                "member_count": source["member_count"],
                "member_ids": sorted(str(member["candidate_id"]) for member in members),
                **decision,
            }
        )
    return output


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def write_outputs(
    root: Path,
    queue_path: Path,
    report_paths: Sequence[Path],
    output_path: Path,
    manifest_path: Path,
) -> dict[str, object]:
    records = build_decisions(queue_path, report_paths)
    output_bytes = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")
    _atomic_write(output_path, output_bytes)
    counts = Counter(str(record["disposition"]) for record in records)
    inputs = [queue_path, *report_paths]
    manifest = {
        "schema_version": "pvsnp-b001-direct-axis-decision-manifest/1",
        "batch_id": "B001",
        "builder": _relative(SCRIPT_PATH, root),
        "builder_sha256": _sha256_file(SCRIPT_PATH),
        "inputs": [
            {
                "path": _relative(path, root),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
            for path in inputs
        ],
        "counts": {
            "clusters": len(records),
            "candidate_records": sum(int(record["member_count"]) for record in records),
            "dispositions": dict(sorted(counts.items())),
        },
        "output": {
            "path": _relative(output_path, root),
            "bytes": len(output_bytes),
            "sha256": _sha256_bytes(output_bytes),
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
    parser = argparse.ArgumentParser(description="Build B001 direct-axis decisions.")
    parser.add_argument("--baseline-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--reports", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    root = args.baseline_root.resolve()
    queue = (args.queue or root / "catalog/B001-direct-axis-queue.jsonl").resolve()
    reports = args.reports or [
        root / "reports/B001-direct-axis-review-A1.md",
        root / "reports/B001-direct-axis-review-A2.md",
        root / "reports/B001-direct-axis-review-A3.md",
        root / "reports/B001-direct-axis-review-B.md",
        root / "reports/B001-direct-axis-review-C1.md",
        root / "reports/B001-direct-axis-review-C2.md",
        root / "reports/B001-direct-axis-review-C3.md",
        root / "reports/B001-direct-axis-review-C4.md",
        root / "reports/B001-direct-axis-review-C5.md",
        root / "reports/B001-direct-axis-review-C6.md",
        root / "reports/B001-direct-axis-review-C7.md",
        root / "reports/B001-direct-axis-review-C8.md",
    ]
    reports = [path.resolve() for path in reports]
    output = (
        args.output or root / "catalog/B001-direct-axis-decisions.jsonl"
    ).resolve()
    manifest = (
        args.manifest or root / "manifests/B001-direct-axis-decisions.json"
    ).resolve()
    result = write_outputs(root, queue, reports, output, manifest)
    print(
        f"built clusters={result['counts']['clusters']} "
        f"candidate_records={result['counts']['candidate_records']} "
        f"dispositions={result['counts']['dispositions']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DecisionError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
