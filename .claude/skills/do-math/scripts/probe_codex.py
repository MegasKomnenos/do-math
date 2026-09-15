"""Reproducible live checks of the initial codex exec adapter.

This is an implementation probe, not the research-instance run command.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import uuid

from do_math.codex_adapter import CodexExecAdapter
from do_math.codex_worker import sanitized_environment
from do_math.preflight import inspect_bundle


def dump(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def digest(path: Path, base: Path | None = None) -> dict:
    data = path.read_bytes()
    return {"path": path.relative_to(base).as_posix() if base else path.name,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def json_safe(value):
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items() if k != "raw"}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def run_case(adapter: CodexExecAdapter, directory: Path, case: str, *, model: str,
             effort: str, timeout: float, windows_sandbox: str) -> dict:
    directory.mkdir()
    workspace = directory / "workspace"
    workspace.mkdir()
    nonce = uuid.uuid4().hex
    if case == "structured":
        prompt = f'Return only the JSON object with status "CLI_OK" and nonce "{nonce}". Do not use tools.'
    elif case == "cancel":
        prompt = "Return the integers from 1 to 10000, one per line. Do not call tools."
    elif case == "tool":
        prompt = "Run exactly one shell command: Get-Location. Return the location it prints. Do not modify files or request elevation."
    else:
        prompt = f"Reply with exactly CLI_OK_{nonce}. Do not call tools."
    prompt_path = directory / "prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8", newline="\n")
    request = {
        "codex_path": adapter.codex_path, "prompt_path": str(prompt_path),
        "cwd": str(workspace), "model": model, "effort": effort,
        "sandbox": "workspace-write" if case == "tool" else "read-only",
        "windows_sandbox": windows_sandbox, "approval_policy": "never",
        "max_runtime_seconds": timeout,
        **{name + "_path": str(directory / filename) for name, filename in (
            ("stdout", "stdout.jsonl"), ("stderr", "stderr.txt"),
            ("final", "final.txt"), ("status", "worker-status.json"))},
    }
    if case == "structured":
        schema_path = directory / "output-schema.json"
        dump(schema_path, {"type": "object", "additionalProperties": False,
                           "properties": {"status": {"type": "string", "enum": ["CLI_OK"]},
                                          "nonce": {"type": "string", "enum": [nonce]}},
                           "required": ["status", "nonce"]})
        request["output_schema_path"] = str(schema_path)
    request_path = directory / "request.json"
    dump(request_path, request)
    execution = adapter.start(request_path, cwd=directory, env=sanitized_environment())
    initial = adapter.inspect(execution)
    stopped_on_turn = False
    try:
        adapter.resume(execution)
        deadline = time.monotonic() + timeout
        while True:
            observed = adapter.inspect(execution)
            if case == "cancel" and "turn.started" in observed["jsonl"]["events"]:
                adapter.stop(execution)
                stopped_on_turn = True
                break
            if observed["job"]["root_signaled"]:
                break
            if time.monotonic() >= deadline:
                adapter.stop(execution)
                break
            time.sleep(0.05)
        if not adapter.wait_for_termination(execution, 5):
            adapter.stop(execution)
            adapter.wait_for_termination(execution, 5)
        result = adapter.collect(execution)
        final = result["final"].get("raw")
        final_text = final.decode("utf-8", errors="replace").strip() if final is not None else None
        if case == "cancel":
            passed = stopped_on_turn and result["termination_barrier"]["confirmed"]
        elif case == "structured":
            try:
                parsed = json.loads(final_text) if final_text is not None else None
            except ValueError:
                parsed = None
            passed = result["result"] == "output_collected" and parsed == {"status": "CLI_OK", "nonce": nonce}
        elif case == "tool":
            # Check the actual tool event; an agent's report of success is insufficient.
            events = [json.loads(line) for line in execution.stdout_path.read_bytes().splitlines() if line.strip()]
            tool_results = [event.get("item", {}) for event in events
                            if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "command_execution"]
            passed = result["result"] == "output_collected" and any(
                item.get("exit_code") == 0 and str(workspace) in item.get("aggregated_output", "")
                for item in tool_results)
        else:
            passed = result["result"] == "output_collected" and final_text == "CLI_OK_" + nonce
        return {"case": case, "passed": passed, "initial": json_safe(initial),
                "stopped_on_turn": stopped_on_turn, "collected": json_safe(result),
                "artifacts": [digest(path, directory) for path in sorted(directory.rglob("*"))
                              if path.is_file() and not path.is_relative_to(workspace)]}
    finally:
        execution.job.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd(), help="Base directory for live probe evidence")
    parser.add_argument("--skill-only", "--spec-only", dest="skill_only", action="store_true",
                        help="Check installed skill documents and role schemas; make no model request")
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--model", help="Required for a live CLI probe")
    parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max", "ultra"), default="low")
    parser.add_argument("--windows-sandbox", choices=("unelevated", "elevated"), default="elevated")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--cases", nargs="+", choices=("text", "structured", "tool", "cancel"), default=["text", "structured", "cancel"])
    parser.add_argument("--output-dir", type=Path, help="New evidence directory, which must not already exist")
    args = parser.parse_args()
    if args.skill_only:
        report = inspect_bundle()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["status"] == "verified" else 1
    if not args.model or not args.codex:
        parser.error("live probes require --model and an installed codex CLI")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    if len(set(args.cases)) != len(args.cases):
        parser.error("--cases must not contain duplicates")
    destination = (args.output_dir or args.repository / ".skill-workspace" / "do-math-cli-live" /
                   ("probe-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    adapter = CodexExecAdapter(str(Path(args.codex).resolve()))
    description = adapter.describe()
    for key, filename in (("version_bytes", "cli-version.txt"), ("exec_help_bytes", "cli-exec-help.txt")):
        if isinstance(description.get(key), bytes):
            (destination / filename).write_bytes(description[key])
    report = {"schema_version": "do-math-implementation-probe/1", "scope": "codex_exec_live_probe",
              "started_at": datetime.now(timezone.utc).isoformat(), "model": args.model,
              "effort": args.effort, "adapter": json_safe(description), "cases": [],
              "implementation_complete": False,
              "not_verified": ["provider_call_identity", "remote_termination", "per_call_usage",
                               "actual_model_input", "automatic_compaction_control", "all_isolation_boundaries",
                               "research_roles", "Lean", "all_design_vectors"]}
    for case in args.cases if description.get("verified") is True else []:
        print(f"probe {case}", file=sys.stderr, flush=True)
        try:
            result = run_case(adapter, destination / case, case, model=args.model, effort=args.effort,
                              timeout=args.timeout_seconds, windows_sandbox=args.windows_sandbox)
        except Exception as exc:
            result = {"case": case, "passed": False, "error_type": type(exc).__name__, "error": str(exc)}
        report["cases"].append(result)
    report["passed"] = description.get("verified") is True and bool(report["cases"]) and all(
        case["passed"] for case in report["cases"])
    if description.get("verified") is not True:
        report["not_run"] = list(args.cases)
        report["failure"] = "cli_description_unavailable_or_incompatible"
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["implementation_sources"] = [digest(path) for path in sorted((Path(__file__).parent / "do_math").glob("*.py"))]
    dump(destination / "report.json", report)
    print(json.dumps({"passed": report["passed"], "scope": report["scope"],
                      "implementation_complete": False, "report": str(destination / "report.json")}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
