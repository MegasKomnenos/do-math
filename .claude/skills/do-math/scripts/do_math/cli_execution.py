"""What the local CLI collector concludes from what it observed (layer 2).

The provider adapters (``codex_adapter``, ``claude_adapter``) run the CLI's
help commands, launch the worker's Job and read its files. This module judges
those observations: whether a CLI's command surface is verified, whether a
request's paths may be used, whether the Job's termination barrier holds, and
why a collection is incomplete. Only the start path checks read the file system.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from .worker_request import STATUS_BINDING_KEYS
from .file_io import executable_identity


def surface_report(version, helps, *, identity: dict, provider: str, cli_path: str,
                   surface: tuple[str, ...], unknown: tuple[str, ...]) -> dict[str, Any]:
    """The command-surface record: verified when ``--version`` and every help command exit 0 with their flags.

    ``version`` and each result in ``helps`` (``(result, flags)`` pairs) carry
    ``returncode`` and ``stdout`` as ``subprocess.run`` returns them.
    """
    verified = version.returncode == 0 and all(result.returncode == 0 and all(flag in result.stdout for flag in flags)
                                               for result, flags in helps)
    help_bytes = helps[-1][0].stdout
    return {"scope": "cli_command_surface_only", "identity": identity, "provider": provider,
            "cli_path": cli_path, "version_bytes": version.stdout,
            "version_sha256": hashlib.sha256(version.stdout).hexdigest(),
            "exec_help_bytes": help_bytes, "exec_help_sha256": hashlib.sha256(help_bytes).hexdigest(),
            "verified": verified,
            "supported": {**{name: verified for name in surface}, "local_job_stop": True},
            "unknown": list(unknown)}


def checked_start_paths(request: dict, request_path: Path, *, cli_path: str, executable_key: str):
    """The request's prompt, output and status paths, and its workspace, once they may be used.

    The request must name this adapter's CLI; request, prompt, schema and outputs
    must be distinct; outputs must be new and outside the model workspace.
    Returns ``(prompt, stdout, stderr, status, final, workspace)``.
    """
    prompt_path, stdout_path, stderr_path, status_path = (Path(request[name]) for name in
        ("prompt_path", "stdout_path", "stderr_path", "status_path"))
    final_path = Path(request["final_path"]) if "final_path" in request else None
    if executable_identity(request[executable_key]) != executable_identity(cli_path):
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
    return prompt_path, stdout_path, stderr_path, status_path, final_path, workspace


def termination_confirmed(state) -> bool:
    """The Job barrier: the root signaled and no process remains; a signaled root alone is insufficient."""
    return state.root_signaled and state.active_processes == 0 and state.process_ids == ()


def decode_status(raw: bytes | None) -> dict | None:
    """The worker's status file; unreadable JSON is recorded as such, a missing file as None."""
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"state": "invalid_status_json"}


def collection_reasons(status, parsed: dict, final: bytes | None, request: dict, *, prompt_sha256: str,
                       request_sha256: str, schema_sha256: str | None,
                       final_check: Callable[[dict, bytes], list[str]]) -> list[str]:
    """Why a collection behind a confirmed barrier is incomplete; empty when the output was collected."""
    reasons = []
    if not isinstance(status, dict): reasons.append("worker_status_missing")
    elif status.get("state") == "timeout": reasons.append("max_runtime_elapsed")
    elif status.get("state") != "exited": reasons.append("worker_not_exited")
    elif status.get("cli_exit_code") != 0: reasons.append("cli_nonzero_exit")
    elif status.get("stdin_sha256") != prompt_sha256: reasons.append("worker_stdin_hash_mismatch")
    elif status.get("request_sha256") != request_sha256: reasons.append("worker_request_hash_mismatch")
    elif status.get("schema_sha256") != schema_sha256: reasons.append("worker_schema_hash_mismatch")
    if isinstance(status, dict):
        for key in STATUS_BINDING_KEYS:
            if key in request and status.get(key) != request[key]:
                reasons.append("worker_" + key + "_mismatch")
    if parsed["turn_failed"]: reasons.append("turn_failed")
    if not parsed["turn_completed"]: reasons.append("turn_completed_missing")
    if not parsed["parse_complete"]: reasons.append("jsonl_parse_incomplete")
    if final is None: reasons.append("final_message_missing")
    else: reasons.extend(final_check(parsed, final))
    return reasons
