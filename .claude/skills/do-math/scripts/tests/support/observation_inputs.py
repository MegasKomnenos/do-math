"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from support.role_answers import candidate


class Clock:
    """A settable clock for an ``ObservationTracker``: each call returns ``value``."""
    def __init__(self): self.value = 0
    def __call__(self): return self.value


def observation_rule(operator="counter_gte", subject_kind="counter", subject_id="attempts", threshold=2, **changes):
    """One observation rule ``R-1`` on ``subject_id``; its basis is ``operator``'s own source and unit.

    The default counts ``attempts`` from the worker checkpoint; ``changes``
    replace fields (``id``, ``required_evidence``, ``basis``) or add
    ``repeat_interval``.
    """
    from do_math.observations import OPERATORS
    value = {
        "id": "R-1", "operator": operator, "subject": {"kind": subject_kind, "id": subject_id},
        "basis": {"source": OPERATORS[operator]["source"], "unit": OPERATORS[operator]["unit"]},
        "threshold": threshold, "required_evidence": ["EV-1"],
    }
    value.update(changes)
    return value


def self_check_response(obligation, status="normal", evidence=None):
    """The worker's answer to a delivered self-check ``obligation``: every due rule gets ``status``.

    ``evidence`` replaces each rule's required evidence references; an
    ``indeterminate`` answer names that evidence as missing.
    """
    return {"obligation_id": obligation["id"], "execution_id": obligation["execution_id"],
            "rule_revision": obligation["rule_revision"], "progress": "progress",
            "attempts": ["checked actual artifact"], "next_method": "continue proof",
            "rule_results": [{"rule_id": row["rule_id"], "status": status,
                "evidence_refs": evidence if evidence is not None else row["required_evidence"],
                "missing_evidence_refs": row["required_evidence"] if status == "indeterminate" else [],
                "reason": "artifact comparison"} for row in obligation["due"]]}


def supply_observation_rules(candidates, extensions):
    """Declare an explicit checkpoint-counter policy for the scripted short task."""
    if not candidates:
        return
    conditions = extensions.setdefault('task_conditions', [])
    for candidate in candidates:
        row = next((item for item in conditions if item.get('task_title') == candidate['title']), None)
        if row is None:
            row = {'task_title': candidate['title']}
            conditions.append(row)
        row.setdefault('observation_rules', [observation_rule(
            threshold=10, id='fixture-attempts', required_evidence=['checkpoint.json'])])


def write_checkpoint(workspace, *, counters=None, iteration=None, claim="fixture progress"):
    """Write a valid worker checkpoint; a tracker reads counters and iterations only from here."""
    value = {"current_claim": claim, "evidence_paths": [], "attempts": [], "remaining_work": [],
             "next_step": "continue", "progress_state": "working"}
    if counters is not None:
        value["counters"] = counters
    if iteration is not None:
        value["iteration"] = iteration
    Path(workspace, "checkpoint.json").write_text(json.dumps(value), encoding="utf-8")


def observe(tracker, event, **options):
    """``tracker.observe`` of ``event`` as the next one-byte stream row, received at the tracker's clock.

    A runner delivers every row with its stream coordinate (``ObservationBatch.source``);
    this gives a unit test that same coordinate without a stream file.
    """
    previous = tracker.observation_source
    start = previous["end_offset"] if previous is not None else 0
    source = {"stream": "stdout.jsonl", "start_offset": start, "end_offset": start + 1,
              "received_at": datetime.now(timezone.utc).isoformat(), "received_monotonic": tracker.clock()}
    return tracker.observe(event, source=source, **options)


def acknowledge(tracker, obligation_id):
    """Deliver an open self-check request and observe the worker's successful poll of it.

    After this, a research action the tracker observes violates the open request.
    """
    from do_math.control_protocol import CONTROL_SERVER, SELF_CHECK_TOOL
    request = tracker.issue_self_check(obligation_id)
    previous = tracker.observation_source
    tracker.record_delivery(obligation_id, source_offset=previous["end_offset"] if previous is not None else 0)
    poll = {"type": "item.completed", "item": {"id": "poll-" + obligation_id, "type": "mcp_tool_call",
            "server": CONTROL_SERVER, "tool": SELF_CHECK_TOOL, "arguments": {"self_check_id": obligation_id},
            "status": "completed", "result": {"content": [{"type": "text", "text": json.dumps(request)}]}}}
    observe(tracker, poll, evaluate=False)
    assert tracker.obligations[obligation_id].get("acknowledged_call_id") == "poll-" + obligation_id


def observation_batch(events=(), *, received_monotonic, stream_path, start=0, terminated=False):
    """The runner's batch of ``events`` as consecutive JSON rows starting at stream offset ``start``."""
    from do_math.observation_transport import ObservationBatch
    rows = [json.dumps(event).encode("utf-8") + b"\n" for event in events]
    offsets, position = [], start
    for row in rows:
        offsets.append((position, position + len(row)))
        position += len(row)
    return ObservationBatch(list(events), offsets, rows, 0, datetime.now(timezone.utc).isoformat(),
                            received_monotonic, position, Path(stream_path), lambda: terminated)


def prepared_rule_conditions(task_ids):
    """Explicit response fixture for assigned existing-task rule preparation."""
    extensions = {}
    supply_observation_rules([{'title': tid} for tid in task_ids], extensions)
    return [{'task_id': row['task_title'], 'observation_rules': row['observation_rules']}
            for row in extensions.get('task_conditions', [])]
