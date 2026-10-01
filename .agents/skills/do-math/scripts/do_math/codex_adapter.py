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
import uuid
import platform
import shutil
from typing import Any, Mapping

from do_math.values import compact_json_bytes, strict_json_loads
from do_math.windows_job import WindowsJob, process_identity
from do_math.codex_stream import artifact as _artifact, parse_response as _parse_codex, provider_observation as _provider_observation
from do_math.provider_final import EXECUTABLE_KEYS, final_bytes as _final_bytes, final_mismatch
from do_math.cli_execution import (checked_start_paths, collection_reasons, decode_status, surface_report,
                                   termination_confirmed)
from do_math import codex_worker


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

    def __init__(self, cli_path: str, *, jobs, clock) -> None:
        self.cli_path = cli_path
        # The Jobs port owns worker creation.
        self.jobs = jobs
        # The clock port for stop receipts and the termination wait.
        self.clock = clock

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
        return surface_report(version, helps, identity=self.capability_identity(), provider=self.provider,
                              cli_path=self.cli_path, surface=self.surface_capabilities,
                              unknown=self.unknown_capabilities)

    def start(self, request_path: Path, *, cwd: Path, env: Mapping[str, str], job_name=None) -> CLIExecution:
        request = self.worker_module.load_request(request_path)
        prompt_path, stdout_path, stderr_path, status_path, final_path, workspace = checked_start_paths(
            request, request_path, cli_path=self.cli_path, executable_key=self.executable_key)
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
        job = self.jobs.launch(
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
                   "observed_at": self.clock.now(),
                   **process_identity(execution.job)}
        execution.stop_receipts.append(receipt)
        return receipt

    def wait_for_termination(self, execution: CLIExecution, timeout: float | None) -> bool:
        """Observe the Job barrier; a signaled root alone is insufficient."""
        deadline = None if timeout is None else self.clock.monotonic() + timeout
        while True:
            if termination_confirmed(execution.job.inspect()):
                return True
            if deadline is not None and self.clock.monotonic() >= deadline:
                return False
            self.clock.sleep(0.02)

    def collect(self, execution: CLIExecution) -> dict[str, Any]:
        # The private request and prompt snapshots are the bytes ``start`` wrote and hashed.
        request_raw, prompt_raw = execution.request_raw, execution.prompt_raw
        request = json.loads(request_raw)
        job_state = execution.job.inspect()
        barrier = termination_confirmed(job_state)
        if not barrier:
            return {"result": "incomplete", "reasons": ["termination_barrier_unconfirmed"],
                    "termination_barrier": {"active_processes": job_state.active_processes,
                    "process_ids": job_state.process_ids, "root_signaled": job_state.root_signaled, "confirmed": False},
                    "artifacts_read": False, "provider_operation_ids": "unknown", "remote_termination": "unknown",
                    "provider_observation": _provider_observation(request, {}, None)}
        stdout, stderr, final_file, status_raw = (_read(path) for path in (execution.stdout_path,
                                                  execution.stderr_path, execution.final_path, execution.status_path))
        status = decode_status(status_raw)
        parsed = self.parse_response(stdout, request)
        final = self.final_bytes(parsed) if self.final_from_stream else final_file
        reasons = collection_reasons(status, parsed, final, request, prompt_sha256=execution.prompt_sha256,
                                     request_sha256=execution.request_sha256, schema_sha256=execution.schema_sha256,
                                     final_check=self.validate_final)
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
        return _final_bytes(parsed)

    def validate_final(self, parsed: dict, final: bytes) -> list[str]:
        """The final response must be the stream's own selected completion."""
        return final_mismatch(parsed, final)

    def provider_failure(self, parsed: dict) -> dict | None:
        """A native admission rejection the provider reported; none by default."""
        return None


class CodexExecAdapter(LocalCLIAdapter):
    """Codex events and command surface with the shared local Job lifecycle."""

    provider = "codex"
    worker_module = codex_worker
    executable_key = EXECUTABLE_KEYS["codex"]
    help_commands = ((("--help",), (b"--ask-for-approval",)),
                     (("exec", "--help"), (b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                                           b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check",
                                           b"--output-schema", b"--config", b"--strict-config", b"--color", b"--cd")))
    surface_capabilities = ("jsonl", "model", "structured_output", "effort_via_config", "sandbox")
    unknown_capabilities = ("actual_input_bytes", "provider_operation_ids", "remote_termination", "per_call_usage",
                            "provider_stop_reason", "automatic_compaction_control",
                            "per_execution_read_isolation", "cross_profile_noninterference")
    identity_modules = ("cli_worker", "codex_worker", "control_transport", "control_protocol", "file_io", "values",
                        "windows_job", "scholarly", "codex_adapter", "codex_stream", "provider_final", "control_server", "worker_request",
                        "cli_execution")

    def worker_options(self, evidence_dir: Path) -> dict[str, Any]:
        # The adopted local permission mode: existing user permissions, approval never.
        # Codex writes its own final message file; the collector compares it with the stream.
        return {**super().worker_options(evidence_dir), "sandbox": "danger-full-access",
                "approval_policy": "never", "windows_sandbox": "unelevated",
                "final_path": str(evidence_dir / "final.txt")}

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        return _parse_codex(raw, request)


