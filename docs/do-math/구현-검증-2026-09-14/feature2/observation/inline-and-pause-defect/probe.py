from __future__ import annotations

import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback


ROOT = Path(__file__).resolve().parent
BASE_FROZEN = Path(r"C:\math\.skill-workspace\do-math-feature2-tests-fg5ma0v3\do-math")
FROZEN = ROOT / "frozen-derived"
SCRIPTS = FROZEN / "scripts"
sys.path.insert(0, str(SCRIPTS))

from do_math.engine import ResearchEngine, control, initialize  # noqa: E402
from do_math.model_runner import CodexModelRunner  # noqa: E402
from do_math.planning import contract_hash  # noqa: E402
from do_math.repository import ResearchRepository  # noqa: E402


INSTANCE_REPOSITORY = ROOT / "repository"
WORKSPACE = ROOT / "workspace"
BUNDLE = ROOT / "state.bundle"
REPORT = ROOT / "report.json"
MANIFEST = ROOT / "source-manifest.json"
EXPECTED_PARTIAL = b"feature2-live-observation-partial-v1\n"
CHECKPOINT_OBJECT = {
    "current_claim": "Synthetic operational-observation fixture has written its partial artifact.",
    "evidence_paths": ["partial.txt"],
    "attempts": ["Wrote the exact requested partial bytes and checkpoint."],
    "remaining_work": ["Wait for the controller's operational decision."],
    "next_step": "Run the bounded benign wait command without changing artifacts.",
    "progress_state": "blocked",
    "iteration": 1,
    "counters": {"artifacts_written": 2},
}
EXPECTED_CHECKPOINT = (json.dumps(CHECKPOINT_OBJECT, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def log(message: str) -> None:
    print(f"[{utc_now()}] {message}", file=sys.stderr, flush=True)


def run_checked(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, check=True, capture_output=True, text=True)


def source_manifest() -> dict:
    files = []
    for path in sorted(FROZEN.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        raw = path.read_bytes()
        files.append({"path": path.relative_to(FROZEN).as_posix(), "bytes": len(raw), "sha256": sha(raw)})
    base_runner = BASE_FROZEN / "scripts" / "do_math" / "model_runner.py"
    derived_runner = FROZEN / "scripts" / "do_math" / "model_runner.py"
    value = {
        "base_frozen_root": str(BASE_FROZEN),
        "derived_frozen_root": str(FROZEN),
        "captured_at": utc_now(),
        "files": files,
        "intentional_difference": {
            "path": "scripts/do_math/model_runner.py",
            "base_sha256": sha(base_runner.read_bytes()),
            "derived_sha256": sha(derived_runner.read_bytes()),
            "reason": "Use the root-verified danger-full-access request while retaining Windows Job containment and explicit execution cwd; the base elevated helper stalled before completing file writes.",
            "request_profile": {"sandbox": "danger-full-access", "windows_sandbox": "unelevated"},
        },
    }
    MANIFEST.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return value


def same_process_alive(identity: dict | None) -> dict:
    if not identity or not identity.get("pid"):
        return {"state": "identity_missing"}
    pid = int(identity["pid"])
    expected_creation = int(identity.get("creation_filetime") or 0)
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        return {"state": "not_openable", "pid": pid, "winerror": error,
                "same_identity_alive": False if error == 87 else None}
    try:
        creation = wintypes.FILETIME()
        exit_time = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not kernel32.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time), ctypes.byref(kernel), ctypes.byref(user)):
            return {"state": "query_failed", "pid": pid, "winerror": ctypes.get_last_error(), "same_identity_alive": None}
        actual_creation = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return {"state": "query_failed", "pid": pid, "winerror": ctypes.get_last_error(), "same_identity_alive": None}
        same = expected_creation == actual_creation
        return {"state": "queried", "pid": pid, "expected_creation_filetime": expected_creation,
                "actual_creation_filetime": actual_creation, "exit_code": int(code.value),
                "same_identity_alive": bool(same and code.value == STILL_ACTIVE)}
    finally:
        kernel32.CloseHandle(handle)


def make_fixture() -> tuple[str, dict]:
    INSTANCE_REPOSITORY.mkdir()
    run_checked(["git", "init", "-q"], INSTANCE_REPOSITORY)
    run_checked(["git", "config", "user.name", "do-math live observation probe"], INSTANCE_REPOSITORY)
    run_checked(["git", "config", "user.email", "probe@example.invalid"], INSTANCE_REPOSITORY)
    init = initialize(
        INSTANCE_REPOSITORY,
        goal="Observe and stop one synthetic reviewed research task while preserving exact partial artifacts.",
        goal_kind="research",
        workspace=WORKSPACE,
        config={
            "model": "gpt-5.6-sol",
            "effort": "medium",
            "work_calls": 1,
            "operations_calls": 2,
            "call_timeout_seconds": 90,
            "run_timeout_seconds": 150,
            "max_cycles": 1,
            "reviewers": 2,
            "goal_auditors": 2,
            "max_input_bytes": 500000,
            "max_output_repairs": 0,
            "observation_mode": "event_driven",
            "observation_idle_seconds": 60,
            "max_observation_reviews": 1,
            "checkpoint_grace_seconds": 3,
        },
        title="Synthetic live observation evidence",
        policies="This is an explicitly synthetic reviewed-task fixture. Do only the requested local artifact writes and bounded benign wait.",
    )
    store = ResearchRepository(INSTANCE_REPOSITORY, init["instance_id"])
    head, instance, runtime = store.load()
    task = {
        "id": "TK-SYNTHETIC-LIVE-OBSERVATION",
        "feature_version": 2,
        "revision": 1,
        "title": "Write exact partial evidence, checkpoint, then remain observable",
        "question": (
            "Execute this fixture exactly using exec_command, never apply_patch. The canonical input context contains "
            "execution_workspace_absolute; pass that exact path as exec_command workdir and set login=false for every command. "
            "First, in one completed PowerShell command, write partial.txt as UTF-8 without BOM with the exact bytes "
            f"{EXPECTED_PARTIAL!r}. Then write checkpoint.json as UTF-8 without BOM containing exactly this JSON object "
            f"(key order and whitespace may differ): {json.dumps(CHECKPOINT_OBJECT, ensure_ascii=False, sort_keys=True)}. "
            "Wait for that first exec_command to complete, ensuring both file handles are closed. Then make a second exec_command "
            "with the same explicit workdir and login=false to run "
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -NoProfile -NonInteractive "
            "-Command Start-Sleep -Seconds 35. Do not replace, delete, or modify either file after starting the wait. "
            "If a stop request arrives, obey it and do not publish knowledge."
        ),
        "scope": "Only partial.txt, checkpoint.json, and one 35-second local sleep command in this execution workspace.",
        "excluded_scope": ["mathematical claims", "knowledge publication", "network access", "repository edits"],
        "expected_result": "A stopped execution whose exact local partial evidence is recoverable after an inline operational review.",
        "completion_criteria": [
            "partial.txt has the exact requested bytes",
            "checkpoint.json is valid and reports blocked after the partial artifact is complete",
            "the 35-second benign tool begins only after both files are closed",
        ],
        "inputs": ["SKILL.md", "GLOSSARY.md", "context:goal", "context:policy"],
        "reuse": [],
        "dependencies": [],
        "occurrence_condition": {"op": "always"},
        "work_class": "nonformal",
        "profile_refs": [],
        "authority_refs": [],
        "expected_research_change": "No research result; operational evidence only.",
        "status": "performing",
        "reviews": [],
        "results": [],
        "fixture_origin": "probe.py synthetic reviewed task; preparation, contract review, and planning intentionally skipped",
    }
    review = {
        "id": "RV-SYNTHETIC-FIXTURE",
        "revision": 1,
        "decision": "approved",
        "inputs_current": True,
        "goal_revision": instance.get("goal_revision"),
        "policy_revision": instance.get("policy_revision"),
    }
    task["reviews"] = [review]
    review["contract_sha256"] = contract_hash(task)
    runtime["tasks"] = {task["id"]: task}
    runtime["queue"] = [{"id": "AC-SYNTHETIC-WORK", "role": "research_work", "target": task["id"],
                         "reason": "explicit synthetic operational-observation fixture"}]
    runtime["status"] = "ready"
    runtime["questions"] = []
    store.save(head, instance, runtime)
    return init["instance_id"], task


def main() -> int:
    started_at = time.monotonic()
    report: dict = {
        "schema": "do-math-feature2-live-observation-probe/1",
        "started_at": utc_now(),
        "frozen_skill": str(FROZEN),
        "fixture_origin": "synthetic reviewed task injected after initialize; preparation/contract/plan deliberately skipped",
        "limits": {"actual_model_calls_max": 3, "overall_seconds_max": 600, "model": "gpt-5.6-sol", "effort": "medium"},
    }
    watcher_state: dict = {"checkpoint_seen": False, "inline_seen": False, "pause_sent": False, "samples": []}
    try:
        log("capturing frozen source manifest")
        manifest = source_manifest()
        report["source_manifest"] = {"path": str(MANIFEST), "file_count": len(manifest["files"]), "sha256": sha(MANIFEST.read_bytes())}
        instance_id, task = make_fixture()
        report["instance_id"] = instance_id
        report["fixture"] = task
        stop_watcher = threading.Event()

        def watcher() -> None:
            store = ResearchRepository(INSTANCE_REPOSITORY, instance_id)
            deadline = time.monotonic() + 120
            while not stop_watcher.is_set() and time.monotonic() < deadline:
                try:
                    _, _, runtime = store.load()
                    parents = [e for e in runtime.get("executions", {}).values() if e.get("role") == "research_work"]
                    inline = [e for e in runtime.get("executions", {}).values() if e.get("role") == "operational_review" and e.get("parent_execution_id")]
                    parent = parents[-1] if parents else None
                    checkpoint_path = WORKSPACE / "runs" / parent["id"] / "workspace" / "checkpoint.json" if parent else None
                    if checkpoint_path and checkpoint_path.exists():
                        watcher_state["checkpoint_seen"] = True
                        watcher_state.setdefault("checkpoint_seen_at", utc_now())
                    if inline:
                        current = inline[-1]
                        watcher_state["inline_seen"] = True
                        watcher_state.setdefault("inline_first_seen_at", utc_now())
                        sample = {"at": utc_now(), "parent_status": parent.get("status") if parent else None,
                                  "inline_status": current.get("status"), "parent_id": parent.get("id") if parent else None,
                                  "inline_id": current.get("id")}
                        if not watcher_state["samples"] or watcher_state["samples"][-1] != sample:
                            watcher_state["samples"].append(sample)
                        if current.get("status") == "ended" and parent and parent.get("status") in {"starting", "running"}:
                            watcher_state["parent_running_when_inline_ended"] = True
                            watcher_state["pause_request"] = control(
                                INSTANCE_REPOSITORY, instance_id, "pause",
                                text="probe pause after completed inline operational review and preserved checkpoint",
                            )
                            watcher_state["pause_sent"] = True
                            watcher_state["pause_sent_at"] = utc_now()
                            return
                    elif parent and parent.get("status") == "ended":
                        watcher_state["parent_ended_before_inline"] = True
                        return
                except Exception as error:
                    watcher_state.setdefault("errors", []).append(f"{type(error).__name__}: {error}")
                time.sleep(0.1)
            watcher_state["timed_out"] = True

        watcher_thread = threading.Thread(target=watcher, name="observation-control-watcher", daemon=True)
        watcher_thread.start()
        class ProbeEngine(ResearchEngine):
            def _context(self, action: dict, workspace: Path) -> dict:
                context = super()._context(action, workspace)
                context["execution_workspace_absolute"] = str(workspace.resolve())
                context["instructions"] += " Use execution_workspace_absolute as the explicit exec_command workdir and set login=false."
                return context

        log("starting real ResearchEngine with CodexModelRunner (danger-full-access, unelevated)")
        engine = ProbeEngine(INSTANCE_REPOSITORY, instance_id,
                             runner=CodexModelRunner(windows_sandbox="unelevated", sandbox="danger-full-access"))
        run_status = engine.run(max_steps=1)
        stop_watcher.set()
        watcher_thread.join(timeout=5)
        report["engine_run_status"] = run_status
        report["watcher"] = watcher_state

        store = ResearchRepository(INSTANCE_REPOSITORY, instance_id)
        head, instance, runtime = store.load()
        report["final_snapshot"] = head
        report["final_runtime_status"] = runtime.get("status")
        executions = list(runtime.get("executions", {}).values())
        actual = [e for e in executions if e.get("role") in {"research_work", "operational_review"}]
        parent = next((e for e in actual if e.get("role") == "research_work"), None)
        inline = next((e for e in actual if e.get("role") == "operational_review" and e.get("parent_execution_id")), None)
        report["actual_model_call_count"] = len(actual)
        report["executions"] = actual
        report["knowledge"] = instance.get("knowledge", {})
        report["knowledge_counts"] = engine.status()["knowledge"]

        result_evidence = {}
        jsonl_files = []
        barriers = []
        process_checks = []
        for execution in actual:
            evidence = WORKSPACE / "runs" / execution["id"] / "evidence" / "stdout.jsonl"
            if evidence.exists():
                jsonl_files.append({"execution_id": execution["id"], "path": str(evidence), "bytes": evidence.stat().st_size,
                                    "sha256": sha(evidence.read_bytes())})
            bundle = execution.get("artifact_bundle")
            if bundle:
                result_path = f"runtime/artifacts/{bundle}/result.json"
                result = json.loads(store.read(result_path, head))
                result_evidence[execution["id"]] = {"path": result_path, "value": result}
                barrier = result.get("execution", {}).get("collect", {}).get("termination_barrier")
                barriers.append({"execution_id": execution["id"], "barrier": barrier})
                identity = result.get("execution", {}).get("started") or execution.get("process")
                process_checks.append({"execution_id": execution["id"], "check": same_process_alive(identity)})
        report["raw_jsonl"] = jsonl_files
        report["result_evidence"] = result_evidence
        report["termination_barriers"] = barriers
        report["post_run_process_checks"] = process_checks

        artifact_checks: dict = {}
        if parent:
            parent_workspace = WORKSPACE / "runs" / parent["id"] / "workspace"
            for relative, expected in (("partial.txt", EXPECTED_PARTIAL), ("checkpoint.json", EXPECTED_CHECKPOINT)):
                local_path = parent_workspace / relative
                local = local_path.read_bytes() if local_path.exists() else None
                entry = next((f for f in parent.get("output_files", []) if f.get("path") == relative), None)
                stored = store.read(entry["artifact_ref"], head) if entry else None
                artifact_checks[relative] = {
                    "local_path": str(local_path), "local_present": local is not None,
                    "local_sha256": sha(local) if local is not None else None,
                    "expected_sha256": sha(expected), "exact_expected_bytes": local == expected,
                    "artifact_ref": entry.get("artifact_ref") if entry else None,
                    "stored_sha256": sha(stored) if stored is not None else None,
                    "stored_equals_local": stored == local if stored is not None and local is not None else False,
                }
            observed = runtime.get("checkpoints", {}).get(parent["id"])
            artifact_checks["observed_checkpoint"] = observed
            if isinstance(observed, dict) and observed.get("artifact_ref"):
                raw = store.read(observed["artifact_ref"], head)
                artifact_checks["observed_checkpoint_artifact"] = {
                    "artifact_ref": observed["artifact_ref"], "sha256": sha(raw),
                    "equals_workspace_checkpoint": raw == (parent_workspace / "checkpoint.json").read_bytes(),
                }
        report["artifact_checks"] = artifact_checks

        live_overlap = bool(
            inline and parent and inline.get("parent_execution_id") == parent.get("id")
            and watcher_state.get("parent_running_when_inline_ended")
        )
        observed_checkpoint = runtime.get("checkpoints", {}).get(parent["id"], {}) if parent else {}
        checkpoint_object = observed_checkpoint.get("checkpoint", observed_checkpoint.get("value"))
        checkpoint_file_check = artifact_checks.get("checkpoint.json", {})
        checkpoint_local = None
        if parent:
            checkpoint_path = WORKSPACE / "runs" / parent["id"] / "workspace" / "checkpoint.json"
            if checkpoint_path.exists():
                try:
                    checkpoint_local = json.loads(checkpoint_path.read_text(encoding="utf-8-sig"))
                except (UnicodeError, json.JSONDecodeError):
                    checkpoint_local = None
        report["assertions"] = {
            "two_actual_model_calls": len(actual) == 2,
            "checkpoint_observed": observed_checkpoint.get("kind") == "worker_checkpoint" and checkpoint_object == CHECKPOINT_OBJECT,
            "inline_operational_review": inline is not None,
            "parent_alive_through_inline_review": live_overlap,
            "real_pause_sent_after_inline": watcher_state.get("pause_sent") is True,
            "parent_execution_ended": bool(parent and parent.get("status") == "ended"),
            "all_jobs_termination_barrier_confirmed": len(barriers) == len(actual) and all(x.get("barrier", {}).get("confirmed") is True for x in barriers),
            "no_same_process_identity_alive": len(process_checks) == len(actual) and all(x["check"].get("same_identity_alive") is False for x in process_checks),
            "partial_exact_and_preserved": artifact_checks.get("partial.txt", {}).get("exact_expected_bytes") is True and artifact_checks.get("partial.txt", {}).get("stored_equals_local") is True,
            "checkpoint_exact_and_preserved": checkpoint_local == CHECKPOINT_OBJECT and checkpoint_file_check.get("stored_equals_local") is True,
            "no_knowledge_published": not instance.get("knowledge") and engine.status()["knowledge"] == {"K": 0, "F": 0, "suspended_K": 0},
            "model_call_limit": len(actual) <= 3,
        }
        report["passed"] = all(report["assertions"].values())
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        report["traceback"] = traceback.format_exc()
        report["passed"] = False
    finally:
        report["ended_at"] = utc_now()
        report["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
        try:
            if INSTANCE_REPOSITORY.exists():
                run_checked(["git", "bundle", "create", str(BUNDLE), "--all"], INSTANCE_REPOSITORY)
                report["git_bundle"] = {"path": str(BUNDLE), "bytes": BUNDLE.stat().st_size, "sha256": sha(BUNDLE.read_bytes())}
        except Exception as error:
            report["git_bundle_error"] = f"{type(error).__name__}: {error}"
            report["passed"] = False
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
