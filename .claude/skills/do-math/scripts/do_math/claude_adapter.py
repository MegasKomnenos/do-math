"""Interpret native Claude events without treating exit zero as completion."""
from __future__ import annotations

import json
import subprocess

from . import claude_worker
from .codex_adapter import LocalCLIAdapter, _sha256
from .repository import canonical_json, _reject_constant


from .claude_stream import parse_stream as parse_jsonl


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
        return {"scope": "cli_command_surface_only", "identity": self.capability_identity(), "provider": "claude", "cli_path": self.cli_path,
                "version_bytes": version.stdout, "version_sha256": _sha256(version.stdout),
                "exec_help_bytes": help_result.stdout, "exec_help_sha256": _sha256(help_result.stdout),
                "verified": verified, "supported": {"jsonl": verified, "model": verified,
                "structured_output": verified, "local_job_stop": True},
                "reported_evidence": ["segment_usage", "cumulative_model_usage", "stop_reason_when_present"],
                "unknown": ["remote_termination", "per_execution_read_isolation", "provider_operation_ids",
                            "automatic_compaction_control", "provider_operation_count", "provider_maximum_output"]}

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        return parse_jsonl(raw, require_structured_output="output_schema_path" in request)

    def validate_final(self, parsed: dict, final: bytes | None) -> list[str]:
        if "final_text" in parsed:
            return [] if final == parsed["final_text"].encode("utf-8") else ["final_text_mismatch"]
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
