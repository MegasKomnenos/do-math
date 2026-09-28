"""Local CLI adapters: the lifetime base every provider shares, and ``codex exec``.

``LocalCLIAdapter`` and ``CLIExecution`` serve both providers. Codex CLI has no
documented provider-response identifier, remote cancellation, or per-call usage
surface; its adapter records those facts as unknown instead of inferring them
from a killed local process.
"""
from __future__ import annotations
from .operation_trace import measured


from dataclasses import dataclass, field
import hashlib
import importlib
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

from do_math.file_io import compact_json_bytes, now, strict_json_loads
from do_math.windows_job import WindowsJob, process_identity
from do_math import cli_worker, codex_worker


@dataclass
class CLIExecution:
    """One started worker Job and the request and prompt bytes hashed at its start."""
    request_sha256: str
    prompt_sha256: str
    worker_argv: tuple[str, ...]
    stdout_path: Path
    stderr_path: Path
    final_path: Path | None
    status_path: Path
    job: WindowsJob
    schema_sha256: str | None
    request_raw: bytes
    prompt_raw: bytes
    stop_receipts: list[dict[str, Any]] = field(default_factory=list)


def _read(path: Path | None) -> bytes | None:
    if path is None:
        return None
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _parse_jsonl(raw: bytes | None) -> dict[str, Any]:
    if raw is None:
        return {"parsed_bytes": 0, "unparsed_tail_bytes": 0, "events": [], "thread_id": None,
                "turn_completed": False, "turn_failed": False, "usage": [], "unknown_events": ["stdout_missing"],
                "parse_complete": False}
    events, usage, unknown = [], [], []
    offset = 0
    thread_id = None
    completed = failed = False
    message = None  # (event index, text) of the latest completed agent message
    for line in raw.splitlines(keepends=True):
        body = line.rstrip(b"\r\n")
        if not body:
            offset += len(line)
            continue
        try:
            event = strict_json_loads(body)
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
            item = event.get("item")
            if (event_type == "item.completed" and isinstance(item, dict) and item.get("type") == "agent_message"
                    and isinstance(item.get("text"), str)):
                message = (len(events) - 1, item["text"])
        offset += len(line)
    terminals = [index for index, item in enumerate(events) if item in {"turn.completed", "turn.failed"}]
    if not thread_id or len(events) < 3 or events[0] != "thread.started" or events[1] != "turn.started":
        unknown.append({"kind": "invalid_lifecycle_order"})
    if len(terminals) != 1 or terminals and terminals[0] != len(events) - 1:
        unknown.append({"kind": "invalid_terminal_count_or_position"})
    if any(not item.startswith("item.") for item in events[2:-1]):
        unknown.append({"kind": "invalid_event_between_turn_start_and_terminal"})
    parsed = {"parsed_bytes": len(raw), "unparsed_tail_bytes": 0, "events": events, "thread_id": thread_id,
              "turn_completed": completed, "turn_failed": failed, "usage": usage, "unknown_events": unknown,
              "parse_complete": not unknown}
    # The final response is the agent message immediately before the terminal event.
    if message is not None and message[0] == len(events) - 2:
        parsed["final_text"] = message[1]
    return parsed


class LocalCLIAdapter:
    """Snapshots, receipts, Windows Job lifetime and command-surface checks shared by CLI providers.

    A provider sets its worker, executable key, command surface, stream parser
    and the modules whose files identify the implementation it runs.
    """

    provider: str
    worker_module: Any
    executable_key: str
    # (arguments, flags the output must contain); the last one is the reported help.
    help_commands: tuple[tuple[tuple[str, ...], tuple[bytes, ...]], ...]
    surface_capabilities: tuple[str, ...]
    unknown_capabilities: tuple[str, ...]
    # Modules loaded by the worker inside its Job or by this collector.
    identity_modules: tuple[str, ...]
    # True when the collector derives the final response from the stream instead of a CLI file.
    final_from_stream = False

    # Seconds each ``describe`` command may run.
    describe_timeout = 10.0

    def __init__(self, cli_path: str, *, jobs=None) -> None:
        self.cli_path = cli_path
        # The Jobs port; None starts the module's WindowsJob (stage 1b migration).
        self.jobs = jobs

    def worker_options(self, evidence_dir: Path) -> dict[str, Any]:
        """The provider's worker request fields for one call that writes under ``evidence_dir``."""
        return {self.executable_key: self.cli_path}

    def capability_identity(self) -> dict:
        """Current local identity, without claiming any behavioral capability."""
        from . import file_io
        path = Path(shutil.which(self.cli_path) or self.cli_path).resolve()
        # Digests are recomputed only when a file's fingerprint changes (이음새-정본.md §2).
        return {"cli_path": str(path), "cli_sha256": file_io.cached_sha256(path) if path.is_file() else None,
                "module_sha256": {name: file_io.cached_sha256(importlib.import_module("do_math." + name).__file__)
                                  for name in sorted(self.identity_modules)},
                "host": {"system": platform.system(), "release": platform.release(), "version": platform.version(),
                         "machine": platform.machine(), "node": platform.node(), "python": platform.python_version()}}

    def observation_key(self):
        """One batch may share facts only for this exact adapter/tool selection."""
        return (type(self).__module__, type(self).__qualname__,
                str(Path(shutil.which(self.cli_path) or self.cli_path).resolve()),
                str(Path(self.worker_module.__file__).resolve()))

    @measured('capability_surface')
    def describe(self) -> dict[str, Any]:
        def run(arguments):
            return subprocess.run([self.cli_path, *arguments], check=False, shell=False, capture_output=True,
                                  timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            version = run(("--version",))
            helps = [(run(arguments), flags) for arguments, flags in self.help_commands]
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"cli_path": self.cli_path, "verified": False, "error_type": type(exc).__name__}
        verified = version.returncode == 0 and all(result.returncode == 0 and all(flag in result.stdout for flag in flags)
                                                   for result, flags in helps)
        help_bytes = helps[-1][0].stdout
        return {"scope": "cli_command_surface_only", "identity": self.capability_identity(), "provider": self.provider,
                "cli_path": self.cli_path, "version_bytes": version.stdout,
                "version_sha256": hashlib.sha256(version.stdout).hexdigest(),
                "exec_help_bytes": help_bytes, "exec_help_sha256": hashlib.sha256(help_bytes).hexdigest(),
                "verified": verified,
                "supported": {**{name: verified for name in self.surface_capabilities}, "local_job_stop": True},
                "unknown": list(self.unknown_capabilities)}

    def start(self, request_path: Path, *, cwd: Path, env: Mapping[str, str], job_name=None) -> CLIExecution:
        request = self.worker_module.load_request(request_path)
        prompt_path, stdout_path, stderr_path, status_path = (Path(request[name]) for name in
            ("prompt_path", "stdout_path", "stderr_path", "status_path"))
        final_path = Path(request["final_path"]) if "final_path" in request else None
        if Path(request[self.executable_key]).resolve() != Path(self.cli_path).resolve():
            raise ValueError("request CLI executable differs from adapter executable")
        outputs = [path for path in (stdout_path, stderr_path, final_path, status_path) if path is not None]
        paths = [request_path, prompt_path, *outputs]
        if "output_schema_path" in request:
            paths.append(Path(request["output_schema_path"]))
        if len({path.resolve() for path in paths}) != len(paths):
            raise ValueError("request, prompt, and output paths must be distinct")
        if any(path.exists() for path in outputs):
            raise FileExistsError("output paths must be newly allocated")
        workspace = Path(request["cwd"]).resolve()
        if any(path.resolve().is_relative_to(workspace) for path in outputs):
            raise ValueError("worker outputs and status must be outside the model workspace")
        prompt_raw = prompt_path.read_bytes()
        stage = Path(tempfile.mkdtemp(prefix="do-math-cli-", dir=workspace.parent))
        snapshot_prompt = stage / "prompt.bin"; snapshot_prompt.write_bytes(prompt_raw)
        snapshot_schema = None
        schema_sha256 = None
        if "output_schema_path" in request:
            snapshot_schema = stage / "schema.json"; schema_bytes = Path(request["output_schema_path"]).read_bytes()
            snapshot_schema.write_bytes(schema_bytes); schema_sha256 = hashlib.sha256(schema_bytes).hexdigest()
        worker_request = dict(request); worker_request["prompt_path"] = str(snapshot_prompt)
        if snapshot_schema is not None: worker_request["output_schema_path"] = str(snapshot_schema)
        snapshot_raw = compact_json_bytes(worker_request)
        snapshot_request = stage / "request.json"; snapshot_request.write_bytes(snapshot_raw)
        worker = Path(self.worker_module.__file__)
        worker_argv = (sys.executable, str(worker), str(snapshot_request))
        job = (self.jobs.launch if self.jobs is not None else WindowsJob)(
            worker_argv, cwd=cwd, env=self.worker_module.sanitized_environment(env),
                         name=job_name or "Local\\DoMath-" + uuid.uuid4().hex, resource_limits=request.get("resource_limits"))
        return CLIExecution(hashlib.sha256(snapshot_raw).hexdigest(), hashlib.sha256(prompt_raw).hexdigest(), worker_argv,
                            stdout_path, stderr_path, final_path, status_path, job, schema_sha256,
                            snapshot_raw, prompt_raw)

    def resume(self, execution: CLIExecution) -> None:
        execution.job.resume()

    def stop(self, execution: CLIExecution) -> dict[str, Any]:
        execution.job.terminate()
        receipt = {"accepted": True, "operation": "TerminateJobObject",
                   "observed_at": now(),
                   **process_identity(execution.job)}
        execution.stop_receipts.append(receipt)
        return receipt

    def wait_for_termination(self, execution: CLIExecution, timeout: float | None) -> bool:
        """Observe the Job barrier; a signaled root alone is insufficient."""
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            state = execution.job.inspect()
            if state.root_signaled and state.active_processes == 0 and state.process_ids == ():
                return True
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(0.02)

    def collect(self, execution: CLIExecution) -> dict[str, Any]:
        # The private request and prompt snapshots are the bytes ``start`` wrote and hashed.
        request_raw, prompt_raw = execution.request_raw, execution.prompt_raw
        request = json.loads(request_raw)
        job_state = execution.job.inspect()
        barrier = job_state.root_signaled and job_state.active_processes == 0 and job_state.process_ids == ()
        if not barrier:
            return {"result": "incomplete", "reasons": ["termination_barrier_unconfirmed"],
                    "termination_barrier": {"active_processes": job_state.active_processes,
                    "process_ids": job_state.process_ids, "root_signaled": job_state.root_signaled, "confirmed": False},
                    "artifacts_read": False, "provider_operation_ids": "unknown", "remote_termination": "unknown",
                    "provider_observation": _provider_observation(request, {}, None)}
        stdout, stderr, final_file, status_raw = (_read(path) for path in (execution.stdout_path,
                                                  execution.stderr_path, execution.final_path, execution.status_path))
        status = None
        if status_raw is not None:
            try:
                status = json.loads(status_raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                status = {"state": "invalid_status_json"}
        parsed = self.parse_response(stdout, request)
        final = self.final_bytes(parsed) if self.final_from_stream else final_file
        reasons = []
        if not isinstance(status, dict): reasons.append("worker_status_missing")
        elif status.get("state") == "timeout": reasons.append("max_runtime_elapsed")
        elif status.get("state") != "exited": reasons.append("worker_not_exited")
        elif status.get("cli_exit_code") != 0: reasons.append("cli_nonzero_exit")
        elif status.get("stdin_sha256") != execution.prompt_sha256: reasons.append("worker_stdin_hash_mismatch")
        elif status.get("request_sha256") != execution.request_sha256: reasons.append("worker_request_hash_mismatch")
        elif status.get("schema_sha256") != execution.schema_sha256: reasons.append("worker_schema_hash_mismatch")
        if isinstance(status, dict):
            for key in cli_worker.STATUS_BINDING_KEYS:
                if key in request and status.get(key) != request[key]:
                    reasons.append("worker_" + key + "_mismatch")
        if parsed["turn_failed"]: reasons.append("turn_failed")
        if not parsed["turn_completed"]: reasons.append("turn_completed_missing")
        if not parsed["parse_complete"]: reasons.append("jsonl_parse_incomplete")
        if final is None: reasons.append("final_message_missing")
        else: reasons.extend(self.validate_final(parsed, final))
        return {"source_request": _artifact(request_raw, execution.request_sha256),
                "source_prompt": _artifact(prompt_raw, execution.prompt_sha256),
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
                "provider_observation": _provider_observation(request, parsed, stdout)}

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        raise NotImplementedError

    @staticmethod
    def final_bytes(parsed: dict) -> bytes | None:
        """The exact final response bytes the stream selected, if any."""
        if "final_text" in parsed:
            return parsed["final_text"].encode("utf-8")
        if "structured_output" in parsed:
            return json.dumps(parsed["structured_output"], ensure_ascii=False, allow_nan=False).encode("utf-8")
        return None

    def validate_final(self, parsed: dict, final: bytes) -> list[str]:
        """The final response must be the stream's own selected completion."""
        return [] if final == self.final_bytes(parsed) else ["final_response_mismatch"]

    def provider_failure(self, parsed: dict) -> dict | None:
        """A native admission rejection the provider reported; none by default."""
        return None


class CodexExecAdapter(LocalCLIAdapter):
    """Codex events and command surface with the shared local Job lifecycle."""

    provider = "codex"
    worker_module = codex_worker
    executable_key = "codex_path"
    help_commands = ((("--help",), (b"--ask-for-approval",)),
                     (("exec", "--help"), (b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                                           b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check",
                                           b"--output-schema", b"--config", b"--strict-config", b"--color", b"--cd")))
    surface_capabilities = ("jsonl", "model", "structured_output", "effort_via_config", "sandbox")
    unknown_capabilities = ("actual_input_bytes", "provider_operation_ids", "remote_termination", "per_call_usage",
                            "provider_stop_reason", "automatic_compaction_control",
                            "per_execution_read_isolation", "cross_profile_noninterference")
    identity_modules = ("cli_worker", "codex_worker", "control_transport", "file_io", "windows_job", "scholarly",
                        "codex_adapter")

    def worker_options(self, evidence_dir: Path) -> dict[str, Any]:
        # The adopted local permission mode: existing user permissions, approval never.
        # Codex writes its own final message file; the collector compares it with the stream.
        return {**super().worker_options(evidence_dir), "sandbox": "danger-full-access",
                "approval_policy": "never", "windows_sandbox": "unelevated",
                "final_path": str(evidence_dir / "final.txt")}

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        return _parse_jsonl(raw)


def _provider_observation(request: dict, parsed: dict, stdout: bytes | None) -> dict[str, Any]:
    """The provider-reported facts of one collection, including an unconfirmed barrier."""
    return {"execution_id": request.get("execution_id"), "operation_ids": "unknown", "operation_count": "unknown",
            "remote_termination": "unknown", "stop_reason": parsed.get("stop_reason", "unknown"),
            "usage": parsed.get("usage_total", parsed.get("usage", [])[-1] if parsed.get("usage") else {}),
            "usage_scope": "reported_execution_counters_not_invoice",
            "model_usage_reported": parsed.get("model_usage_reported", {}),
            "model_usage_scope": "last_reported_cumulative_not_added_to_segment_usage",
            "evidence_sha256": hashlib.sha256(stdout).hexdigest() if stdout is not None else None}


def _artifact(raw: bytes | None, sha256: str | None = None) -> dict[str, Any]:
    """Describe collected bytes; a caller may supply the digest it already computed."""
    return {"present": raw is not None, "bytes": None if raw is None else len(raw),
            "sha256": None if raw is None else sha256 or hashlib.sha256(raw).hexdigest(), "raw": raw}
