"""Native Claude invocation segments, parsed by the collector (``claude_adapter``).

Only the observed same-session task-notification continuation is supported.
The original JSONL remains the authority for event and submission bytes.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import math

from .values import json_digest, strict_json_loads


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def usage_total(segments):
    """Sum reported segment counters only, never cumulative modelUsage/cost."""
    keys = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    return {key: sum(row["usage"][key] for row in segments if _number(row["usage"].get(key)))
            for key in keys if any(_number(row["usage"].get(key)) for row in segments)}


def provider_limit(parsed):
    """Classify the last native admission event, not tool errors or overage flags."""
    events = parsed.get("rate_limits", [])
    if not events or events[-1]["info"].get("status") != "rejected" or parsed.get("turn_completed"):
        return None
    record = events[-1]
    info = record["info"]
    windows = [{"type": info.get("rateLimitType"), "resetsAt": info.get("resetsAt")}]
    windows_info = info.get("unifiedWindows")
    for name, window in (windows_info if isinstance(windows_info, dict) else {}).items():
        if isinstance(window, dict) and (window.get("status") == "rejected" or
                (_number(window.get("utilization")) and window["utilization"] >= 1)):
            windows.append({"type": name, **window})
    times = [w["resetsAt"] for w in windows if _number(w.get("resetsAt"))]
    retry_at = None
    if times:
        try:
            retry_at = datetime.fromtimestamp(max(times), timezone.utc).isoformat()
        except (ValueError, OverflowError, OSError):
            pass
    return {"kind": "provider_limit", "provider": "claude", "retry_at": retry_at,
            "limit_windows": windows, "evidence_line": record["line"], "native_info": info}


def parse_stream(raw: bytes | None, *, require_structured_output: bool = True) -> dict:
    parsed = {"parsed_bytes": 0, "unparsed_tail_bytes": 0, "events": [], "thread_id": None,
              "turn_completed": False, "turn_failed": False, "usage": [], "unknown_events": [],
              "parse_complete": False, "result_segments": [], "usage_segments": [],
              "background_events": [], "post_result_events": [],
              "rate_limits": [], "model_usage_reported": {}, "reported_models": [],
              "usage_scope": {"usage": "sum_of_reported_segment_counters",
                              "model_usage_reported": "last_reported_cumulative_model_usage",
                              "total_cost_usd": "last_reported_estimate_not_invoice"}}
    errors = parsed["unknown_events"]
    if raw is None:
        errors.append("stdout_missing")
        return parsed
    segment = None
    selected = None
    last_result = None
    sessions = []
    models = set()
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        if not line.endswith(b"\n"):
            errors.append("incomplete_jsonl_line")
            parsed["unparsed_tail_bytes"] = len(raw) - parsed["parsed_bytes"]
            break
        if not line.strip():
            parsed["parsed_bytes"] += len(line)
            continue
        try:
            event = strict_json_loads(line)
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                raise ValueError("event requires a type")
        except (ValueError, UnicodeError):
            errors.append("invalid_jsonl")
            parsed["unparsed_tail_bytes"] = len(raw) - parsed["parsed_bytes"]
            break
        parsed["parsed_bytes"] += len(line)
        kind = event["type"]
        parsed["events"].append(kind)
        if "session_id" in event:
            sessions.append(event["session_id"])
        if kind == "rate_limit_event":
            info = event.get("rate_limit_info")
            if isinstance(info, dict):
                parsed["rate_limits"].append({"line": line_number, "info": info})
        is_init = kind == "system" and event.get("subtype") == "init"
        if kind == "system" and event.get("subtype") in {"background_tasks_changed", "task_started", "task_updated", "task_notification"}:
            parsed["background_events"].append({"line": line_number, "event": event})
        if is_init:
            if segment is not None and not segment["terminal"]:
                errors.append("unfinished_segment")
            if parsed["thread_id"] is None:
                parsed["thread_id"] = event.get("session_id")
            segment = {"index": len(parsed["result_segments"]), "start_line": line_number,
                       "terminal": False, "work": False}
            continue
        if segment is None:
            if kind != "rate_limit_event":
                errors.append("work_before_session_start")
            continue
        if segment["terminal"]:
            # Claude 2.1.276 reports termination of outstanding background jobs
            # after its final result. This is cleanup, not another model turn.
            cleanup = kind == "system" and (
                (event.get("subtype") == "background_tasks_changed" and event.get("tasks") == []) or
                (event.get("subtype") == "task_updated" and isinstance(event.get("patch"), dict) and event["patch"].get("status") == "killed") or
                (event.get("subtype") == "task_notification" and event.get("status") == "stopped"))
            if cleanup:
                parsed["post_result_events"].append({"line": line_number, "event": event})
            else:
                errors.append("event_after_terminal_without_init")
            continue
        if kind != "result":
            if kind in {"assistant", "user", "stream_event", "tool_use", "tool_result"}:
                segment["work"] = True
            continue
        segment["terminal"] = True
        last_result = event
        origin = event.get("origin")
        if segment["index"] and (not isinstance(origin, dict) or origin.get("kind") != "task-notification"):
            errors.append("unsupported_continuation")
        if event.get("session_id") != parsed["thread_id"]:
            errors.append("session_mismatch")
        success = event.get("subtype") == "success" and event.get("is_error") is False
        summary = {"segment": segment["index"], "start_line": segment["start_line"],
                   "result_line": line_number, "result_sha256": hashlib.sha256(line.rstrip(b"\r\n")).hexdigest(),
                   "success": success, "origin": event.get("origin"), "num_turns": event.get("num_turns")}
        if "structured_output" in event:
            summary["output_sha256"] = json_digest(event["structured_output"])
        parsed["result_segments"].append(summary)
        if isinstance(event.get("usage"), dict):
            parsed["usage"].append(event["usage"])
            parsed["usage_segments"].append({"segment": segment["index"], "line": line_number, "usage": event["usage"]})
        if isinstance(event.get("modelUsage"), dict):
            parsed["model_usage_reported"] = event["modelUsage"]
            models.update(event["modelUsage"])
        for key in ("subtype", "stop_reason", "modelUsage", "total_cost_usd", "permission_denials"):
            if key in event:
                parsed[key] = event[key]
        if not success:
            selected = None
            parsed["turn_failed"] = True
        elif "structured_output" in event:
            selected = (summary, "structured_output", event["structured_output"])
        elif not require_structured_output and isinstance(event.get("result"), str):
            summary["output_sha256"] = json_digest(event["result"])
            selected = (summary, "final_text", event["result"])
        elif not (segment["index"] and not segment["work"] and event.get("num_turns") == 0
                  and all(value == 0 for value in usage_total(parsed["usage_segments"][-1:]).values())):
            selected = None
            errors.append("segment_submission_missing")
    session = parsed["thread_id"]
    if not isinstance(session, str) or not session:
        errors.append("invalid_session_start")
    if any(value != session for value in sessions):
        errors.append("session_mismatch")
    if segment is None or not segment["terminal"] or last_result is None:
        errors.append("terminal_missing")
    parsed["parse_complete"] = not errors
    parsed["reported_models"] = sorted(models)
    parsed["usage_total"] = usage_total(parsed["usage_segments"])
    if selected is not None and parsed["parse_complete"] and not parsed["turn_failed"]:
        parsed["selected_result"] = selected[0]
        parsed[selected[1]] = selected[2]
        parsed["superseded_results"] = [row for row in parsed["result_segments"]
                                        if "output_sha256" in row and row != selected[0]]
        parsed["turn_completed"] = True
    return parsed
