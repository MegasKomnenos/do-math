"""Observable local lifetime adapter for ``codex exec``.

Codex CLI has no documented provider-response identifier, remote cancellation,
or per-call usage surface.  This module records those facts as unknown instead
of inferring them from a killed local process.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid
import platform
import shutil
from typing import Any, Mapping

from do_math.windows_job import WindowsJob, process_identity
from do_math.codex_worker import sanitized_environment
from do_math import codex_worker


@dataclass
class CodexExecution:
    request_path: Path
    prompt_path: Path
    request_sha256: str
    prompt_sha256: str
    worker_argv: tuple[str, ...]
    stdout_path: Path
    stderr_path: Path
    final_path: Path
    status_path: Path
    job: WindowsJob
    snapshot_dir: Path
    schema_sha256: str | None
    stop_requested: bool = False
    stop_receipts: list[dict[str, Any]] = field(default_factory=list)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _paths(request: Mapping[str, Any]) -> tuple[Path, Path, Path, Path, Path]:
    return tuple(Path(request[name]) for name in ("prompt_path", "stdout_path", "stderr_path", "final_path", "status_path"))  # type: ignore[return-value]


def _parse_jsonl(raw: bytes | None) -> dict[str, Any]:
    if raw is None:
        return {"parsed_bytes": 0, "unparsed_tail_bytes": 0, "events": [], "thread_id": None,
                "turn_completed": False, "turn_failed": False, "usage": [], "unknown_events": ["stdout_missing"],
                "parse_complete": False}
    from .repository import _reject_constant
    events, usage, unknown = [], [], []
    offset = 0
    thread_id = None
    completed = failed = False
    for line in raw.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        if not body:
            offset += len(line)
            continue
        try:
            event = json.loads(body, object_pairs_hook=codex_worker._pairs,
                               parse_constant=_reject_constant)
            # JSON exponents may overflow to infinity even without a named constant.
            json.dumps(event, allow_nan=False)
        except (UnicodeError, ValueError):
            unknown.append({"kind": "invalid_jsonl", "offset": offset})
            return {"parsed_bytes": offset, "unparsed_tail_bytes": len(raw) - offset, "events": events,
                    "thread_id": thread_id, "turn_completed": completed, "turn_failed": failed,
                    "usage": usage, "unknown_events": unknown, "parse_complete": False}
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            unknown.append({"kind": "unknown_jsonl_event", "offset": offset})
        else:
            event_type = event["type"]
            events.append(event_type)
            if not (event_type in {"thread.started", "turn.started", "turn.completed", "turn.failed", "error"}
                    or event_type.startswith("item.")):
                unknown.append({"kind": "unknown_event_type", "offset": offset, "length": len(line), "type": event_type})
            if event_type == "thread.started" and isinstance(event.get("thread_id"), str):
                thread_id = event["thread_id"]
            completed |= event_type == "turn.completed"
            failed |= event_type == "turn.failed"
            if "usage" in event:
                usage.append(event["usage"])
        offset += len(line)
    terminals = [index for index, item in enumerate(events) if item in {"turn.completed", "turn.failed"}]
    if not thread_id or len(events) < 3 or events[0] != "thread.started" or events[1] != "turn.started":
        unknown.append({"kind": "invalid_lifecycle_order"})
    if len(terminals) != 1 or terminals and terminals[0] != len(events) - 1:
        unknown.append({"kind": "invalid_terminal_count_or_position"})
    if any(not item.startswith("item.") for item in events[2:-1]):
        unknown.append({"kind": "invalid_event_between_turn_start_and_terminal"})
    return {"parsed_bytes": len(raw), "unparsed_tail_bytes": 0, "events": events, "thread_id": thread_id,
            "turn_completed": completed, "turn_failed": failed, "usage": usage, "unknown_events": unknown,
            "parse_complete": not unknown}


class LocalCLIAdapter:
    """Shared snapshots, receipts and Windows Job lifetime for CLI workers."""

    worker_module = codex_worker
    executable_key = "codex_path"
    parse_output = staticmethod(_parse_jsonl)

    def __init__(self, codex_path: str, *, describe_timeout: float = 10.0) -> None:
        self.codex_path = codex_path
        self.cli_path = codex_path
        self.describe_timeout = describe_timeout

    def capability_identity(self) -> dict:
        """Current local identity, without claiming any behavioral capability."""
        path = Path(shutil.which(self.cli_path) or self.cli_path).resolve()
        worker = Path(self.worker_module.__file__).resolve()
        from . import control_transport, windows_job
        return {"cli_path": str(path), "cli_sha256": _sha256(path.read_bytes()) if path.is_file() else None,
                "worker_sha256": _sha256(worker.read_bytes()),
                "windows_job_sha256": _sha256(Path(windows_job.__file__).read_bytes()),
                "control_transport_sha256": _sha256(Path(control_transport.__file__).read_bytes()),
                "adapter_sha256": _sha256(Path(__file__).read_bytes()),
                "provider_adapter_sha256": _sha256(Path(sys.modules[type(self).__module__].__file__).read_bytes()),
                "host": {"system": platform.system(), "release": platform.release(), "version": platform.version(),
                         "machine": platform.machine(), "node": platform.node(), "python": platform.python_version()}}

    def describe(self) -> dict[str, Any]:
        try:
            version_result = subprocess.run([self.codex_path, "--version"], check=False, shell=False,
                                            capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            global_help_result = subprocess.run([self.codex_path, "--help"], check=False, shell=False,
                                                capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            help_result = subprocess.run([self.codex_path, "exec", "--help"], check=False, shell=False,
                                         capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"cli_path": self.codex_path, "verified": False, "error_type": type(exc).__name__}
        version, help_bytes = version_result.stdout, help_result.stdout
        required = (b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                    b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check", b"--output-schema", b"--config")
        verified = (version_result.returncode == 0 and global_help_result.returncode == 0 and help_result.returncode == 0
                    and b"--ask-for-approval" in global_help_result.stdout and all(flag in help_bytes for flag in required))
        return {"scope": "cli_command_surface_only", "identity": self.capability_identity(),
                "cli_path": self.codex_path, "version_bytes": version, "version_sha256": _sha256(version),
                "exec_help_bytes": help_bytes, "exec_help_sha256": _sha256(help_bytes),
                "verified": verified, "supported": {"jsonl": verified, "model": verified, "structured_output": verified,
                              "effort_via_config": verified, "sandbox": verified, "local_job_stop": True},
                "unknown": ["actual_input_bytes", "provider_operation_ids", "remote_termination", "per_call_usage",
                            "provider_stop_reason", "automatic_compaction_control",
                            "per_execution_read_isolation", "cross_profile_noninterference"]}

    def start(self, request_path: Path, *, cwd: Path, env: Mapping[str, str]) -> CodexExecution:
        request = self.worker_module.load_request(request_path)
        prompt_path, stdout_path, stderr_path, final_path, status_path = _paths(request)
        if Path(request[self.executable_key]).resolve() != Path(self.cli_path).resolve():
            raise ValueError("request CLI executable differs from adapter executable")
        paths = [request_path, prompt_path, stdout_path, stderr_path, final_path, status_path]
        if "output_schema_path" in request:
            paths.append(Path(request["output_schema_path"]))
        if len({path.resolve() for path in paths}) != len(paths):
            raise ValueError("request, prompt, and output paths must be distinct")
        if any(path.exists() for path in (stdout_path, stderr_path, final_path, status_path)):
            raise FileExistsError("output paths must be newly allocated")
        workspace = Path(request["cwd"]).resolve()
        if any(path.resolve().is_relative_to(workspace) for path in (stdout_path, stderr_path, final_path, status_path)):
            raise ValueError("worker outputs and status must be outside the model workspace")
        request_raw, prompt_raw = request_path.read_bytes(), prompt_path.read_bytes()
        stage = Path(tempfile.mkdtemp(prefix="do-math-cli-", dir=workspace.parent))
        snapshot_prompt = stage / "prompt.bin"; snapshot_prompt.write_bytes(prompt_raw)
        snapshot_schema = None
        schema_sha256 = None
        if "output_schema_path" in request:
            snapshot_schema = stage / "schema.json"; schema_bytes = Path(request["output_schema_path"]).read_bytes()
            snapshot_schema.write_bytes(schema_bytes); schema_sha256 = _sha256(schema_bytes)
        worker_request = dict(request); worker_request["prompt_path"] = str(snapshot_prompt)
        if snapshot_schema is not None: worker_request["output_schema_path"] = str(snapshot_schema)
        snapshot_request = stage / "request.json"; snapshot_request.write_text(json.dumps(worker_request, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        worker = Path(self.worker_module.__file__)
        worker_argv = (sys.executable, str(worker), str(snapshot_request))
        job = WindowsJob(worker_argv, cwd=cwd, env=self.worker_module.sanitized_environment(env),
                         name="Local\\DoMath-" + uuid.uuid4().hex, resource_limits=request.get("resource_limits"))
        return CodexExecution(snapshot_request, snapshot_prompt, _sha256(snapshot_request.read_bytes()), _sha256(prompt_raw), worker_argv,
                              stdout_path, stderr_path, final_path, status_path, job, stage, schema_sha256)

    def resume(self, execution: CodexExecution) -> None:
        if _sha256(execution.prompt_path.read_bytes()) != execution.prompt_sha256:
            raise RuntimeError("private prompt snapshot changed before resume")
        schema = execution.snapshot_dir / "schema.json"
        if execution.schema_sha256 is not None and _sha256(schema.read_bytes()) != execution.schema_sha256:
            raise RuntimeError("private schema snapshot changed before resume")
        execution.job.resume()

    def inspect(self, execution: CodexExecution) -> dict[str, Any]:
        job = execution.job.inspect()
        raw = _read(execution.stdout_path)
        return {"job": {**process_identity(execution.job),
                         "active_processes": job.active_processes, "process_ids": job.process_ids,
                         "root_signaled": job.root_signaled}, "jsonl": self.parse_output(raw),
                "worker_status_present": execution.status_path.exists(), "stop_requested": execution.stop_requested}

    def stop(self, execution: CodexExecution) -> dict[str, Any]:
        execution.stop_requested = True
        execution.job.terminate()
        receipt = {"accepted": True, "operation": "TerminateJobObject",
                   "observed_at": datetime.now(timezone.utc).isoformat(),
                   **process_identity(execution.job)}
        execution.stop_receipts.append(receipt)
        return receipt

    def wait_for_termination(self, execution: CodexExecution, timeout: float | None) -> bool:
        """Observe the Job barrier; a signaled root alone is insufficient."""
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            state = execution.job.inspect()
            if state.root_signaled and state.active_processes == 0 and state.process_ids == ():
                return True
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(0.02)

    def collect(self, execution: CodexExecution) -> dict[str, Any]:
        job_state = execution.job.inspect()
        barrier = job_state.root_signaled and job_state.active_processes == 0 and job_state.process_ids == ()
        if not barrier:
            return {"result": "incomplete", "reasons": ["termination_barrier_unconfirmed"],
                    "termination_barrier": {"active_processes": job_state.active_processes,
                    "process_ids": job_state.process_ids, "root_signaled": job_state.root_signaled, "confirmed": False},
                    "artifacts_read": False, "provider_operation_ids": "unknown", "remote_termination": "unknown"}
        request_raw, prompt_raw, stdout, stderr, final, status_raw = (_read(path) for path in
                                             (execution.request_path, execution.prompt_path, execution.stdout_path,
                                              execution.stderr_path, execution.final_path, execution.status_path))
        status = None
        if status_raw is not None:
            try:
                status = json.loads(status_raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                status = {"state": "invalid_status_json"}
        try:
            request = json.loads(request_raw) if request_raw is not None else {}
            if not isinstance(request, dict):
                request = {}
        except (ValueError, UnicodeError):
            request = {}
        parsed = self.parse_response(stdout, request)
        reasons = []
        if request_raw is None or _sha256(request_raw) != execution.request_sha256: reasons.append("source_request_changed")
        if prompt_raw is None or _sha256(prompt_raw) != execution.prompt_sha256: reasons.append("source_prompt_changed")
        if not isinstance(status, dict): reasons.append("worker_status_missing")
        elif status.get("state") == "timeout": reasons.append("max_runtime_elapsed")
        elif status.get("state") != "exited": reasons.append("worker_not_exited")
        elif status.get("cli_exit_code") != 0: reasons.append("cli_nonzero_exit")
        elif status.get("stdin_sha256") != execution.prompt_sha256: reasons.append("worker_stdin_hash_mismatch")
        elif status.get("request_sha256") != execution.request_sha256: reasons.append("worker_request_hash_mismatch")
        elif status.get("schema_sha256") != execution.schema_sha256: reasons.append("worker_schema_hash_mismatch")
        if isinstance(status, dict):
            for key in ("execution_id", "profile_ref"):
                if key in request and status.get(key) != request[key]:
                    reasons.append("worker_" + key + "_mismatch")
        if parsed["turn_failed"]: reasons.append("turn_failed")
        if not parsed["turn_completed"]: reasons.append("turn_completed_missing")
        if not parsed["parse_complete"]: reasons.append("jsonl_parse_incomplete")
        if final is None: reasons.append("final_message_missing")
        reasons.extend(self.validate_final(parsed, final))
        if not barrier: reasons.append("termination_barrier_unconfirmed")
        return {"source_request": _artifact(request_raw), "source_prompt": _artifact(prompt_raw),
                "host_resources": execution.job.resource_usage() if request.get("resource_limits") is not None else None,
                "stdout": _artifact(stdout), "stderr": _artifact(stderr), "final": _artifact(final),
                "worker_status": status, "jsonl": parsed, "worker_argv": execution.worker_argv,
                "process_identity": process_identity(execution.job),
                "stop_receipts": execution.stop_receipts,
                "result": "output_collected" if not reasons else "incomplete",
                "reasons": reasons, "termination_barrier": {"active_processes": job_state.active_processes,
                "process_ids": job_state.process_ids, "root_signaled": job_state.root_signaled, "confirmed": barrier}, "provider_operation_ids": "unknown", "remote_termination": "unknown",
                "provider_stop_reason": parsed.get("stop_reason", "unknown"),
                "execution_id": request.get("execution_id"), "profile_ref": request.get("profile_ref"),
                "provider_observation": {
                    "execution_id": request.get("execution_id"), "operation_ids": "unknown", "operation_count": "unknown",
                    "remote_termination": "unknown", "stop_reason": parsed.get("stop_reason", "unknown"),
                    "usage": parsed.get("usage_total", parsed.get("usage", [])[-1] if parsed.get("usage") else {}),
                    "usage_scope": "reported_execution_counters_not_invoice",
                    "model_usage_reported": parsed.get("model_usage_reported", {}),
                    "model_usage_scope": "last_reported_cumulative_not_added_to_segment_usage",
                    "evidence_sha256": _sha256(stdout) if stdout is not None else None}}

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        return self.parse_output(raw)

    def validate_final(self, parsed: dict, final: bytes | None) -> list[str]:
        return []


class CodexExecAdapter(LocalCLIAdapter):
    """Codex events and command surface with the shared local Job lifecycle."""


def _artifact(raw: bytes | None) -> dict[str, Any]:
    return {"present": raw is not None, "bytes": None if raw is None else len(raw),
            "sha256": None if raw is None else _sha256(raw), "raw": raw}
