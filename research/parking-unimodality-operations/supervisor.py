"""Scheduled entry points; the scheduler owns engine and operator separately."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"
CLI = ROOT / ".agents/skills/do-math/scripts/do_math.py"
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "observed_status": {"type": "string"},
        "actions": {"type": "array", "items": {"type": "string"}},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "user_questions": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"}
    },
    "required": ["summary", "observed_status", "actions", "evidence_paths", "user_questions", "next_step"]
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def cli_argv(config: dict, command: str, *arguments: str) -> list[str]:
    return [config["python"], str(CLI), command, "--repository", config["repository"],
            "--instance", config["instance"], *arguments]


def inspect_status(config: dict) -> dict:
    result = subprocess.run(cli_argv(config, "status", "--json"), capture_output=True,
                            timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace") or result.stdout.decode("utf-8", "replace"))
    return json.loads(result.stdout)


def engine_may_start(status: dict, held: bool) -> bool:
    return not held and status["status"] in {"ready", "running"}


def status_summary(status: dict) -> dict:
    return {key: status.get(key) for key in ("snapshot", "status", "goal_status", "active_execution",
                                           "pending_actions", "budget", "questions")}


def codex_argv(config: dict, run_dir: Path) -> list[str]:
    # Keep the user's authentication and enabled scholarly MCP configuration.
    return [config["codex"], "-a", "never", "exec", "--skip-git-repo-check",
            "--sandbox", "danger-full-access", "--model", config["model"],
            "-c", 'model_reasoning_effort="' + config["effort"] + '"',
            "--json", "--output-schema", str(run_dir / "schema.json"),
            "--output-last-message", str(run_dir / "report.json"), "-C", str(ROOT), "-"]


def codex_child(config: dict, run_dir: Path) -> int:
    env = dict(os.environ)
    for name in ("CODEX_SESSION_ID", "CODEX_THREAD_ID"):
        env.pop(name, None)
    with (run_dir / "prompt.txt").open("rb") as source, \
            (run_dir / "events.jsonl").open("wb") as output, \
            (run_dir / "stderr.txt").open("wb") as errors:
        result = subprocess.run(codex_argv(config, run_dir), stdin=source, stdout=output,
                                stderr=errors, cwd=ROOT, env=env,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    write_json(run_dir / "child-result.json", {"exit_code": result.returncode})
    return result.returncode


def operator(config: dict, run_dir: Path, probe: bool) -> dict:
    logs = Path(config["logs"])
    if (logs / "HOLD").exists():
        return {"outcome": "held", "reason": "HOLD exists"}
    before = inspect_status(config)
    write_json(run_dir / "before.json", before)
    previous = logs / "latest-check.json"
    if previous.exists():
        write_json(run_dir / "previous-check.json", json.loads(previous.read_text(encoding="utf-8")))
    context = {"config_file": str(CONFIG), "run_directory": str(run_dir), "probe": probe,
               "status_file": str(run_dir / "before.json"), "hold_file": str(logs / "HOLD"),
               "previous_check": str(run_dir / "previous-check.json") if previous.exists() else None}
    prompt = (HERE / "OPERATOR.md").read_text(encoding="utf-8")
    prompt += "\n\n## 이번 호출의 입력\n\n" + json.dumps(context, ensure_ascii=False, indent=2)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_json(run_dir / "schema.json", SCHEMA)
    sys.path.insert(0, str(CLI.parent))
    from do_math.windows_job import WindowsJob
    command = [config["pythonw"], str(Path(__file__).resolve()), "codex-child", "--run-dir", str(run_dir)]
    with WindowsJob(command, cwd=ROOT, env=os.environ) as job:
        write_json(run_dir / "process.json", {"pid": job.pid, "creation_filetime": job.creation_filetime})
        job.resume()
        deadline = time.monotonic() + config["operator_timeout_seconds"]
        while not job.wait(0.5):
            if (logs / "HOLD").exists() or time.monotonic() >= deadline:
                job.terminate()
                if not job.wait(30):
                    raise RuntimeError("Operator process tree did not terminate")
                return {"outcome": "held" if (logs / "HOLD").exists() else "timeout"}
    child = json.loads((run_dir / "child-result.json").read_text(encoding="utf-8"))
    if child["exit_code"]:
        return {"outcome": "codex_failed", **child}
    import jsonschema
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    jsonschema.validate(report, SCHEMA)
    return {"outcome": "completed", "report": report, "after": status_summary(inspect_status(config))}


def engine(config: dict, run_dir: Path) -> dict:
    before = inspect_status(config)
    write_json(run_dir / "before.json", before)
    if not engine_may_start(before, (Path(config["logs"]) / "HOLD").exists()):
        return {"outcome": "not_started", "status": before["status"]}
    with (run_dir / "stdout.json").open("wb") as output, (run_dir / "stderr.txt").open("wb") as errors:
        result = subprocess.run(cli_argv(config, "run"), cwd=ROOT, stdout=output, stderr=errors,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return {"outcome": "completed" if result.returncode == 0 else "engine_failed",
            "exit_code": result.returncode, "after": status_summary(inspect_status(config))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["check", "engine", "codex-child", "hold", "release"])
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    logs = Path(config["logs"])
    logs.mkdir(parents=True, exist_ok=True)
    if args.mode == "codex-child":
        return codex_child(config, args.run_dir)
    if args.mode == "hold":
        hold = {"id": uuid.uuid4().hex, "started_at": datetime.now(timezone.utc).isoformat()}
        write_json(logs / "HOLD", hold)
        return subprocess.run(cli_argv(config, "pause", "--reason", "User requested scheduled operator HOLD " + hold["id"]),
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).returncode
    if args.mode == "release":
        hold = logs / "HOLD"
        if hold.exists():
            write_json(logs / "release.json", {"hold": json.loads(hold.read_text(encoding="utf-8")),
                       "released_at": datetime.now(timezone.utc).isoformat()})
            hold.unlink()
        return 0  # The next operator checks the cause before deciding to resume.
    run_dir = logs / args.mode / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True)
    record = {"started_at": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
              "probe": args.probe, "run_directory": str(run_dir), "outcome": "running",
              "pid": os.getpid(), "parent_pid": os.getppid()}
    write_json(run_dir / "result.json", record)
    try:
        record.update(operator(config, run_dir, args.probe) if args.mode == "check" else engine(config, run_dir))
    except Exception as error:
        record.update(outcome="failed", error=f"{type(error).__name__}: {error}")
    record["ended_at"] = datetime.now(timezone.utc).isoformat()
    write_json(run_dir / "result.json", record)
    write_json(logs / ("latest-" + args.mode + ".json"), record)
    return 0 if record["outcome"] in {"completed", "held", "not_started"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
