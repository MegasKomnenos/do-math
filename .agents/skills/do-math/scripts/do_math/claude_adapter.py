"""Interpret native Claude events without treating exit zero as completion.

This module also owns the provider-to-adapter table: every place that turns a
provider name or a worker request into an adapter uses ``ADAPTERS``.
"""
from __future__ import annotations

import shutil

from . import claude_worker
from .codex_adapter import CodexExecAdapter, LocalCLIAdapter


from .claude_stream import parse_stream as parse_jsonl, provider_limit


class ClaudePrintAdapter(LocalCLIAdapter):
    provider = "claude"
    worker_module = claude_worker
    executable_key = "claude_path"
    help_commands = ((("--help",), (b"--print", b"--output-format", b"--verbose", b"--model", b"--effort",
                                    b"--json-schema", b"--no-session-persistence", b"--setting-sources",
                                    b"--settings", b"--strict-mcp-config", b"--mcp-config",
                                    b"--disable-slash-commands", b"--disallowedTools", b"--permission-mode")),)
    surface_capabilities = ("jsonl", "model", "structured_output")
    unknown_capabilities = ("remote_termination", "per_execution_read_isolation", "provider_operation_ids",
                            "automatic_compaction_control", "provider_operation_count", "provider_maximum_output")
    # The collector imports codex_adapter, which holds the shared base and the ADAPTERS entry for Codex.
    identity_modules = ("claude_worker", "cli_worker", "codex_worker", "control_transport", "file_io", "windows_job",
                        "scholarly", "codex_adapter", "claude_adapter", "claude_stream")
    # The worker writes no final file; the collector selects the final from the stream once.
    final_from_stream = True

    def parse_response(self, raw: bytes | None, request: dict) -> dict:
        return parse_jsonl(raw, require_structured_output="output_schema_path" in request)

    def provider_failure(self, parsed: dict) -> dict | None:
        return provider_limit(parsed)


ADAPTERS = {adapter.provider: adapter for adapter in (CodexExecAdapter, ClaudePrintAdapter)}


def provider_adapter(provider: str, cli_path: str | None = None) -> LocalCLIAdapter:
    """The adapter of a provider; its CLI defaults to the executable named like the provider."""
    if provider not in ADAPTERS:
        raise ValueError("unsupported profile provider")
    return ADAPTERS[provider](cli_path or shutil.which(provider) or provider)


def request_provider(request: dict) -> str:
    """The provider whose worker request carries this executable key."""
    providers = [name for name, adapter in ADAPTERS.items() if adapter.executable_key in request]
    if len(providers) != 1:
        raise ValueError("worker request names no single provider executable")
    return providers[0]
