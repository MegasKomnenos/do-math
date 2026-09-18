"""Installed schema checks and explicit-provider representative local CLI probes."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from do_math.engine import json_safe
from do_math.model_runner import ModelRunner
from do_math.preflight import inspect_bundle
from do_math.observations import read_checkpoint
from do_math.scholarly import resolve_scholarly_server


def run_case(destination, case, *, provider, model, effort, timeout, only_assigned, scholarly=False):
    root = destination / case
    workspace = root / "workspace"
    workspace.mkdir(parents=True)
    nonce = uuid.uuid4().hex
    schema = {"type": "object", "additionalProperties": False,
              "properties": {"status": {"const": "CLI_OK"}, "nonce": {"const": nonce},
                             "phase": {"enum": ["finished", "pending"]}}, "required": ["status", "nonce", "phase"]}
    prompt = f'This is an isolated CLI integration probe. Work only in {workspace}. Return the provided JSON schema with status CLI_OK and nonce {nonce}. '
    if case == "structured":
        prompt += 'Use no tools. Return phase finished.'
    elif case == "files":
        checkpoint = {"current_claim": "The local probe file exists.", "evidence_paths": ["probe-evidence.txt"],
                      "attempts": ["Write and read the probe file."], "remaining_work": [],
                      "next_step": "Return the structured probe result.", "progress_state": "ready_to_submit"}
        prompt += ('Write probe-evidence.txt containing exactly ' + nonce + ', read it back, then write checkpoint.json as ' +
                   json.dumps(checkpoint) + '. Return phase finished after verifying both files. ')
        if scholarly:
            prompt += 'Also call the provided scholarly list_sources tool once. Do not search or fetch literature.'
    elif case == "background":
        prompt += ('Use Bash to start exactly one background command (run_in_background=true) which waits 5 seconds '
                   'and writes completed.txt containing exactly ' + nonce + '. Write a local phase-pending.json checkpoint while it runs. '
                   'Use the actual TaskOutput tool to wait for that background task, then read completed.txt and submit phase finished. '
                   'Keep the CLI invocation active until the job finishes. Do not submit the final JSON while it is still pending; '
                   'print mode may terminate outstanding background work when the final result is returned. Do not start agents or another model.')
    else:
        prompt += 'Start a Bash command that waits 120 seconds. The local runner will deliberately stop this probe while that tool is active. Do not start background agents.'
    stop = False
    native_tool_names = []
    def observe(event):
        nonlocal stop
        content = event.get("message", {}).get("content", []) if isinstance(event.get("message"), dict) else []
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                native_tool_names.append(block.get("name"))
                if case == "stop":
                    stop = True
        if case == "stop" and event.get("type") == "item.started" and event.get("item", {}).get("type") == "command_execution":
            stop = True
    server = resolve_scholarly_server(None, start=Path.cwd()) if scholarly else None
    runner = ModelRunner()
    routed_model = model if provider == "codex" or model.startswith("claude-") else "claude:" + model
    result = runner.run(prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=root / "evidence",
        model=routed_model, effort=effort, timeout_seconds=timeout, claude_only_assigned_model=only_assigned,
        scholarly_server=server, on_observation=observe, should_stop=lambda: stop)
    collected = result.get("execution", {}).get("collect", {})
    parsed = collected.get("jsonl", {})
    checks = {"local_termination": collected.get("termination_barrier", {}).get("confirmed") is True}
    if case == "stop":
        checks["requested_stop"] = stop and result["status"] == "stopped"
    else:
        checks["structured_result"] = result["status"] == "completed" and result["output"] == {"status": "CLI_OK", "nonce": nonce, "phase": "finished"}
    if case == "files":
        checks["preserved_file"] = (workspace / "probe-evidence.txt").is_file() and (workspace / "probe-evidence.txt").read_text(encoding="utf-8").strip() == nonce
        checks["checkpoint"] = read_checkpoint(workspace)["status"] == "valid"
        if scholarly:
            checks["scholarly_actual_tool"] = any(name and "scholarly" in name and "list_sources" in name for name in native_tool_names)
    if case == "background":
        checks["native_background_start"] = any(row["event"].get("subtype") == "task_started" for row in parsed.get("background_events", []))
        checks["actual_wait_tool"] = "TaskOutput" in native_tool_names
        checks["completed_file"] = (workspace / "completed.txt").is_file() and (workspace / "completed.txt").read_text(encoding="utf-8").strip() == nonce
    if provider == "claude" and only_assigned and case != "stop":
        checks["reported_models"] = bool(parsed.get("reported_models")) and parsed["reported_models"] == [model]
    report = {"case": case, "passed": all(checks.values()), "checks": checks, "result": json_safe(result),
              "actual_tool_names": native_tool_names}
    (root / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"case": case, "passed": report["passed"], "checks": checks, "report": str(root / "report.json")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-only", action="store_true")
    parser.add_argument("--provider", choices=("claude", "codex"))
    parser.add_argument("--model")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--only-assigned-model", action="store_true")
    parser.add_argument("--scholarly", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--cases", nargs="+", choices=("structured", "files", "background", "stop"), default=["structured", "files", "stop"])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if args.skill_only:
        result = inspect_bundle()
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["status"] == "verified" else 1
    if not args.provider or not args.model or not args.output_dir or args.timeout_seconds < 1:
        parser.error("live probes require explicit --provider, --model, --output-dir and a positive timeout")
    if args.provider == "claude" and args.only_assigned_model and not args.model.startswith("claude-"):
        parser.error("model locking requires the full Claude model ID")
    if args.provider == "codex" and args.model.startswith(("claude:", "claude-")):
        parser.error("provider and model disagree")
    if len(set(args.cases)) != len(args.cases):
        parser.error("cases must be distinct")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    results = []
    for case in args.cases:
        print("probe " + case, flush=True)
        try:
            results.append(run_case(args.output_dir, case, provider=args.provider, model=args.model, effort=args.effort,
                timeout=args.timeout_seconds, only_assigned=args.only_assigned_model, scholarly=args.scholarly and case == "files"))
        except Exception as error:
            results.append({"case": case, "passed": False, "error": type(error).__name__ + ": " + str(error)})
    root = Path(__file__).parent
    report = {"at": datetime.now(timezone.utc).isoformat(), "provider": args.provider, "model": args.model,
              "passed": all(row["passed"] for row in results), "cases": results,
              "sources": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (root / "do_math").glob("*.py")},
              "scope": "representative local CLI protocol, files, tool and stop boundaries; no research efficacy claim"}
    (args.output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
