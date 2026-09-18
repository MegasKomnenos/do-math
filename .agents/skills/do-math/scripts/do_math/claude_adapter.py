"""Interpret native Claude events without treating exit zero as completion."""
from __future__ import annotations

import json
import subprocess

from . import claude_worker
from .codex_adapter import LocalCLIAdapter, _sha256
from .repository import canonical_json, _reject_constant


def parse_jsonl(raw: bytes | None) -> dict:
    parsed = {"parsed_bytes": 0, "unparsed_tail_bytes": 0, "events": [], "thread_id": None,
              "turn_completed": False, "turn_failed": False, "usage": [], "unknown_events": [],
              "parse_complete": False}
    if raw is None:
        parsed["unknown_events"].append("stdout_missing")
        return parsed
    events = []
    for line in raw.splitlines(keepends=True):
        if line.strip():
            try:
                event = json.loads(line, object_pairs_hook=claude_worker._pairs)
                if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                    raise ValueError("event requires a type")
            except (ValueError, UnicodeError):
                parsed["unknown_events"].append("invalid_jsonl")
                parsed["unparsed_tail_bytes"] = len(raw) - parsed["parsed_bytes"]
                return parsed
            events.append(event)
            parsed["events"].append(event["type"])
        parsed["parsed_bytes"] += len(line)
    starts = [i for i, e in enumerate(events) if e["type"] == "system" and e.get("subtype") == "init"]
    terminals = [i for i, e in enumerate(events) if e["type"] == "result"]
    if len(starts) != 1:
        parsed["unknown_events"].append("invalid_session_start")
    else:
        start = starts[0]
        session_id = events[start].get("session_id")
        if not isinstance(session_id, str) or not session_id:
            parsed["unknown_events"].append("invalid_session_id")
        else:
            parsed["thread_id"] = session_id
        if any(e["type"] != "rate_limit_event" for e in events[:start]):
            parsed["unknown_events"].append("work_before_session_start")
        if any("session_id" in e and e["session_id"] != session_id for e in events):
            parsed["unknown_events"].append("session_mismatch")
    if len(terminals) != 1 or terminals[0] != len(events) - 1:
        parsed["unknown_events"].append("invalid_terminal_count_or_position")
    else:
        result = events[-1]
        if result.get("session_id") != parsed["thread_id"]:
            parsed["unknown_events"].append("session_mismatch")
        parsed["turn_completed"] = result.get("subtype") == "success" and result.get("is_error") is False
        parsed["turn_failed"] = not parsed["turn_completed"]
        if "structured_output" in result:
            parsed["structured_output"] = result["structured_output"]
        if isinstance(result.get("usage"), dict):
            parsed["usage"].append(result["usage"])
        for key in ("subtype", "stop_reason", "modelUsage", "total_cost_usd", "permission_denials"):
            if key in result:
                parsed[key] = result[key]
    parsed["parse_complete"] = not parsed["unknown_events"]
    return parsed


class ClaudePrintAdapter(LocalCLIAdapter):
    worker_module = claude_worker
    executable_key = "claude_path"
    parse_output = staticmethod(parse_jsonl)

    def describe(self) -> dict:
        try:
            options = dict(capture_output=True, timeout=self.describe_timeout, shell=False)
            version = subprocess.run([self.cli_path, "--version"], **options,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            help_result = subprocess.run([self.cli_path, "--help"], **options,
                                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"cli_path": self.cli_path, "verified": False, "error_type": type(exc).__name__}
        required = (b"--print", b"--output-format", b"--verbose", b"--model", b"--effort", b"--json-schema",
                    b"--no-session-persistence", b"--setting-sources", b"--settings", b"--strict-mcp-config",
                    b"--mcp-config", b"--disable-slash-commands", b"--disallowedTools", b"--permission-mode")
        verified = version.returncode == help_result.returncode == 0 and all(flag in help_result.stdout for flag in required)
        return {"scope": "cli_command_surface_only", "provider": "claude", "cli_path": self.cli_path,
                "version_bytes": version.stdout, "version_sha256": _sha256(version.stdout),
                "exec_help_bytes": help_result.stdout, "exec_help_sha256": _sha256(help_result.stdout),
                "verified": verified, "supported": {"jsonl": verified, "model": verified,
                "structured_output": verified, "local_job_stop": True},
                "unknown": ["remote_termination", "per_execution_read_isolation", "provider_operation_ids"]}

    def validate_final(self, parsed: dict, final: bytes | None) -> list[str]:
        if "structured_output" not in parsed:
            return ["structured_output_missing"]
        try:
            if final is None:
                return ["structured_output_mismatch"]
            value = json.loads(final, object_pairs_hook=claude_worker._pairs, parse_constant=_reject_constant)
            if canonical_json(value) != canonical_json(parsed["structured_output"]):
                return ["structured_output_mismatch"]
        except (ValueError, UnicodeError):
            return ["structured_output_invalid"]
        return []
