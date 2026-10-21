"""Codex CLI output, parsed by the collector (``codex_adapter``) (layer 1).

``parse_jsonl`` reads one ``codex exec --json`` stream; recorded streams (the
corpus) go through the same function.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from .values import strict_json_loads


def stderr_diagnostics(raw: bytes | None) -> list[dict[str, Any]]:
    """Index recognized CLI logs in the preserved stderr, without judging the call.

    A models-manager refresh timeout reports a catalog request, not a failed
    model turn. Unknown log formats remain available in the raw artifact.
    Offsets and lengths are bytes, including the line's original terminator.
    """
    diagnostics = []
    offset = 0
    for line in (raw or b"").splitlines(keepends=True):
        match = re.fullmatch(
            rb"(\d{4}-\d{2}-\d{2}T[0-9:.]+Z) (ERROR|WARN) codex_models_manager::manager: "
            rb"failed to refresh available models: request timed out", line.rstrip(b"\r\n"))
        if match:
            diagnostics.append({"kind": "model_catalog_refresh_timeout", "scope": "cli_model_catalog",
                                "reported_at": match[1].decode("ascii"), "reported_level": match[2].decode("ascii"),
                                "source": {"artifact": "stderr", "offset": offset, "bytes": len(line)}})
        offset += len(line)
    return diagnostics


def parse_jsonl(raw: bytes | None) -> dict[str, Any]:
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
    # A real rejected Codex request emits error before turn.failed. It is a
    # complete failed protocol, not malformed JSONL and not a successful turn.
    if any(not item.startswith("item.") and not (item == "error" and failed and not completed)
           for item in events[2:-1]):
        unknown.append({"kind": "invalid_event_between_turn_start_and_terminal"})
    parsed = {"parsed_bytes": len(raw), "unparsed_tail_bytes": 0, "events": events, "thread_id": thread_id,
              "turn_completed": completed, "turn_failed": failed, "usage": usage, "unknown_events": unknown,
              "parse_complete": not unknown}
    # The final response is the agent message immediately before the terminal event.
    if message is not None and message[0] == len(events) - 2:
        parsed["final_text"] = message[1]
    return parsed


def parse_response(raw: bytes | None, request: dict) -> dict[str, Any]:
    """The collector's parse of a Codex worker's stream; the request adds nothing for Codex."""
    return parse_jsonl(raw)


def provider_observation(request: dict, parsed: dict, stdout: bytes | None) -> dict[str, Any]:
    """The provider-reported facts of one collection, including an unconfirmed barrier."""
    return {"execution_id": request.get("execution_id"), "operation_ids": "unknown", "operation_count": "unknown",
            "remote_termination": "unknown", "stop_reason": parsed.get("stop_reason", "unknown"),
            "usage": parsed.get("usage_total", parsed.get("usage", [])[-1] if parsed.get("usage") else {}),
            "usage_scope": "reported_execution_counters_not_invoice",
            "model_usage_reported": parsed.get("model_usage_reported", {}),
            "model_usage_scope": "last_reported_cumulative_not_added_to_segment_usage",
            "evidence_sha256": hashlib.sha256(stdout).hexdigest() if stdout is not None else None}


def artifact(raw: bytes | None, sha256: str | None = None) -> dict[str, Any]:
    """Describe collected bytes; a caller may supply the digest it already computed."""
    return {"present": raw is not None, "bytes": None if raw is None else len(raw),
            "sha256": None if raw is None else sha256 or hashlib.sha256(raw).hexdigest(), "raw": raw}
