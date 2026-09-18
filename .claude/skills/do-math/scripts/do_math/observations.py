"""Observable progress and recoverable checkpoints, without inferring mathematics."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from .context_store import _safe_path, _excluded

CHECKPOINT_MAX_BYTES = 4 * 1024 * 1024
RULES_MAX_BYTES = 65536


CHECKPOINT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "current_claim": {"type": "string"},
        "evidence_paths": {"type": "array", "items": {"type": "string"}},
        "attempts": {"type": "array", "items": {"type": "string"}},
        "remaining_work": {"type": "array", "items": {"type": "string"}},
        "next_step": {"type": "string"},
        "progress_state": {"type": "string", "enum": ["working", "blocked", "no_progress", "ready_to_submit"]},
        "iteration": {"type": "integer", "minimum": 0},
        "counters": {"type": "object", "additionalProperties": {"type": "integer", "minimum": 0}},
    },
    "required": ["current_claim", "evidence_paths", "attempts", "remaining_work", "next_step", "progress_state"],
}


def validate_rules(rules: list[dict]) -> list[dict]:
    if not isinstance(rules, list) or len(rules) > 16:
        raise ValueError("observation rules must be a list of at most 16 rules")
    seen = set()
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) - {"id", "op", "threshold", "repeat_interval", "counter", "reason"}:
            raise ValueError("invalid observation rule fields")
        if not isinstance(rule.get("id"), str) or not rule["id"] or rule["id"] in seen:
            raise ValueError("observation rule IDs must be distinct and nonempty")
        seen.add(rule["id"])
        if rule.get("op") not in {"counter_gte", "iteration_gte", "checkpoint_count_gte", "active_duration_gte", "tool_results_gte"}:
            raise ValueError("unsupported observation operator")
        for key in ("threshold", "repeat_interval"):
            if key == "repeat_interval" and key not in rule: continue
            if isinstance(rule.get(key), bool) or not isinstance(rule.get(key), int) or rule[key] < 1:
                raise ValueError(key + " must be a positive integer")
        if rule["op"] == "counter_gte" and (not isinstance(rule.get("counter"), str) or not rule["counter"]):
            raise ValueError("counter_gte needs a counter name")
        if rule["op"] != "counter_gte" and "counter" in rule:
            raise ValueError("only counter_gte has a counter name")
    return rules


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_checkpoint(workspace: Path) -> dict:
    path = workspace / "checkpoint.json"
    if not path.exists():
        return {"status": "missing"}
    try:
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(workspace.resolve()) or path.is_symlink():
            raise ValueError("checkpoint must stay within the execution workspace")
        before = path.stat()
        if before.st_size > CHECKPOINT_MAX_BYTES:
            raise ValueError("checkpoint exceeds the 4 MiB record limit")
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return {"status": "being_written"}
        digest = hashlib.sha256(raw).hexdigest()
        value = json.loads(raw.decode("utf-8-sig"))
        import jsonschema
        jsonschema.validate(value, CHECKPOINT_SCHEMA)
        for reference in value["evidence_paths"]:
            evidence = _safe_path(workspace, reference)
            relative = Path(reference)
            if (relative.parts[0] != "input" and _excluded(relative)) or not evidence.is_file():
                raise ValueError("checkpoint evidence is unavailable or excluded from preservation: " + reference)
        return {"status": "valid", "value": value, "sha256": digest, "raw": raw, "observed_at": utc_now()}
    except Exception as error:
        return {"status": "invalid", "error": f"{type(error).__name__}: {error}"}


class ObservationTracker:
    def __init__(self, execution_id: str, workspace: Path, config: dict, *, clock=time.monotonic):
        self.execution_id, self.workspace, self.config, self.clock = execution_id, workspace, config, clock
        self.started = self.last_activity = self.last_review = clock()
        self.last_checkpoint = None
        self.last_due_key = None
        self.events_seen = 0
        self.tool_results = 0
        self.messages = []
        self.pending_tools = {}
        self.last_transport = None
        self.transport_bytes = 0
        self.review_count = 0
        self.checkpoint_count = 0
        self.rules = validate_rules(config.get("observation_rules", []))
        self.rules_digest = None
        self.consumed_rules = {}

    def observe(self, event: dict) -> list[dict]:
        when = self.clock()
        emitted = []
        rules_file = self.workspace / "observation-rules.json"
        if rules_file.exists():
            try:
                if rules_file.is_symlink() or not rules_file.resolve().is_relative_to(self.workspace.resolve()):
                    raise ValueError("observation rules must stay in workspace")
                raw = rules_file.read_bytes()
                if len(raw) > RULES_MAX_BYTES: raise ValueError("observation rules exceed 64 KiB")
                digest = hashlib.sha256(raw).hexdigest()
                if digest != self.rules_digest:
                    self.rules = validate_rules(json.loads(raw.decode("utf-8-sig")))
                    self.rules_digest = digest
                    emitted.append({"kind": "observation_rules", "execution_id": self.execution_id,
                                    "rules": self.rules, "sha256": digest, "raw": raw, "observed_at": utc_now()})
            except (ValueError, OSError, UnicodeError) as error:
                # A partially written or invalid update leaves the last valid rules active.
                pass
        event_type = event.get("type")
        if event_type == "transport_bytes_received":
            self.last_transport = when
            self.transport_bytes += event.get("bytes", 0)
        if event_type == "system" and event.get("subtype") == "task_started" and event.get("is_backgrounded"):
            self.pending_tools["background:" + str(event.get("task_id"))] = {"started": when, "name": event.get("task_type"), "timeout_seconds": None}
            self.last_activity = when
        if event_type == "system" and event.get("subtype") == "task_notification":
            self.pending_tools.pop("background:" + str(event.get("task_id")), None)
            self.last_activity = when
        if event_type in {"item.started", "item.completed", "assistant", "user", "stream_event"}:
            self.events_seen += 1
            self.last_activity = when
            item = event.get("item", {})
            if event_type == "item.started" and item.get("type") in {"command_execution", "mcp_tool_call"}:
                self.pending_tools[item.get("id", "unknown")] = {"started": when, "name": item.get("type"), "timeout_seconds": None}
            if event_type == "item.completed":
                self.pending_tools.pop(item.get("id", "unknown"), None)
                if item.get("type") in {"command_execution", "mcp_tool_call"}:
                    self.tool_results += 1
                if item.get("type") == "agent_message":
                    self.messages.append({"text": item.get("text", ""), "observed_at": utc_now()})
            if event_type in {"assistant", "user"}:
                message = event.get("message")
                content = message.get("content", []) if isinstance(message, dict) else []
                for block in content if isinstance(content, list) else []:
                    if not isinstance(block, dict):
                        continue
                    if event_type == "assistant" and block.get("type") == "tool_use":
                        timeout = block.get("input", {}).get("timeout") if isinstance(block.get("input"), dict) else None
                        seconds = timeout / 1000 if block.get("name") == "Bash" and type(timeout) in (int, float) and timeout > 0 else None
                        self.pending_tools[block.get("id", "unknown")] = {"started": when, "name": block.get("name"), "timeout_seconds": seconds}
                    elif event_type == "user" and block.get("type") == "tool_result":
                        self.pending_tools.pop(block.get("tool_use_id", "unknown"), None)
                        self.tool_results += 1
                    elif event_type == "assistant" and block.get("type") == "text":
                        self.messages.append({"text": block.get("text", ""), "observed_at": utc_now()})
        checkpoint = read_checkpoint(self.workspace)
        if checkpoint["status"] == "valid" and checkpoint["sha256"] != self.last_checkpoint:
            self.last_checkpoint = checkpoint["sha256"]
            self.checkpoint_count += 1
            self.last_activity = when
            emitted.append({"kind": "checkpoint", "execution_id": self.execution_id, **checkpoint})
        sample = {"elapsed_seconds": when - self.started, "inactive_seconds": when - self.last_activity,
                  "events_seen": self.events_seen, "tool_results": self.tool_results,
                  "pending_tools": sorted(self.pending_tools), "checkpoint_status": checkpoint["status"],
                  "checkpoint": checkpoint.get("value"), "recent_messages": self.messages[-4:]}
        idle = self.config.get("observation_idle_seconds", 120)
        interval = self.config.get("observation_interval_seconds", 300)
        transport_recent = self.last_transport is not None and when - self.last_transport < idle
        state = "tool_wait" if self.pending_tools else "output_streaming" if transport_recent else "active" if when - self.last_activity < idle else "idle"
        sample.update(activity_state=state, transport_bytes=self.transport_bytes,
                      last_transport_seconds=None if self.last_transport is None else self.last_transport - self.started,
                      last_work_event_seconds=self.last_activity - self.started,
                      next_review_seconds=max(0, interval - (when - self.last_review)),
                      tool_details=[{"id": key, "elapsed_seconds": when - value["started"],
                                     "timeout_seconds": value["timeout_seconds"], "name": value["name"]}
                                    for key, value in self.pending_tools.items()])
        reason = None
        rule_basis = None
        if checkpoint.get("value", {}).get("progress_state") in {"blocked", "no_progress"}:
            reason = "worker_reported_obstacle"
        elif state in {"tool_wait", "output_streaming"}:
            overdue = any(value["timeout_seconds"] is not None and when - value["started"] >= value["timeout_seconds"]
                          for value in self.pending_tools.values())
            if when - self.last_review >= interval or overdue:
                reason = "tool_timeout_observed" if overdue else state + "_review"
        elif sample["inactive_seconds"] >= idle:
            reason = "no_visible_activity"
        elif self.config.get("observation_mode", "event_driven") == "periodic" and when - self.last_review >= self.config.get("observation_interval_seconds", 300):
            reason = "periodic_review"
        if reason is None:
            progress = checkpoint.get("value", {})
            for rule in self.rules:
                value = {"iteration_gte": progress.get("iteration", 0), "checkpoint_count_gte": self.checkpoint_count,
                         "active_duration_gte": sample["elapsed_seconds"], "tool_results_gte": self.tool_results,
                         "counter_gte": progress.get("counters", {}).get(rule.get("counter"), 0)}[rule["op"]]
                signature = hashlib.sha256(json.dumps(rule, sort_keys=True).encode()).hexdigest()
                previous = self.consumed_rules.get(signature)
                boundary = rule["threshold"] if previous is None else previous + rule.get("repeat_interval", 0)
                if (previous is None or "repeat_interval" in rule) and value >= boundary:
                    self.consumed_rules[signature] = boundary
                    reason, rule_basis = "worker_observation_condition", {"rule": rule, "value": value, "boundary": boundary}
                    break
        if reason and self.review_count < self.config.get("max_observation_reviews", 3):
            key = (reason, json.dumps(rule_basis, sort_keys=True), self.last_checkpoint, self.tool_results,
                   int((when-self.started) // max(1, self.config.get("observation_interval_seconds", 300))))
            if key != self.last_due_key:
                self.last_due_key = key
                self.last_review = when
                self.review_count += 1
                emitted.append({"kind": "operational_review_due", "execution_id": self.execution_id,
                                "reason": reason, "sample": sample, "observed_at": utc_now()})
                if rule_basis: emitted[-1]["rule_basis"] = rule_basis
        return emitted


def request_checkpoint(workspace: Path, reason: str, *, immediate: bool, deadline: str) -> dict:
    request = {"reason": reason, "immediate": immediate, "deadline": deadline,
               "instruction": "Preserve only already obtained facts in checkpoint.json and finish. Do not start new research or external actions."}
    destination = workspace / "stop-request.json"
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    temporary.replace(destination)
    return request


def recovered_checkpoint(workspace: Path, messages: list[dict] | None = None) -> dict:
    checkpoint = read_checkpoint(workspace)
    if checkpoint["status"] == "valid":
        return {"kind": "worker_checkpoint", "checkpoint": checkpoint["value"], "sha256": checkpoint["sha256"]}
    return {"kind": "observed_partial_state", "checkpoint_status": checkpoint["status"],
            "messages": messages or [], "workspace": str(workspace),
            "limitation": "No complete worker checkpoint was received; infer no unreported result."}
