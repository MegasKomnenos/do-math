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
    this gives a unit test that same coordinate without a stream file. Both
    receipt clocks come from the tracker's time port, including UTC rules and
    explicit reviews that compare ``received_at``.
    """
    previous = tracker.observation_source
    start = previous["end_offset"] if previous is not None else 0
    source = {"stream": "stdout.jsonl", "start_offset": start, "end_offset": start + 1,
              "received_at": tracker.time_port.now(), "received_monotonic": tracker.clock()}
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


def tracker_record_samples(root):
    """Whole records from tracker exits, separate from the rule_ids fragment pair.

    Include valid empty/one/many relations, delivered/undelivered obligations,
    response/proposal outcomes and each observation mode. No record is padded
    to satisfy a schema. The whole-record pairs check field coverage separately.
    """
    from copy import deepcopy
    from do_math.observations import ObservationTracker, persistent_record
    from support.fakes.clock import FakeClock
    rows = []

    def keep(branch, family, record):
        rows.append((branch, family, deepcopy(record)))

    def obligations(branch, tracker):
        for record in tracker.stored_obligations().values():
            keep(branch, 'self_check_obligations', record)

    for count in (1, 2):
        for proposal_kind in ('absent', 'changed', 'unchanged', 'rejected'):
            branch = f'rules={count}, proposal={proposal_kind}'
            workspace = Path(root) / f'{count}-{proposal_kind}'
            workspace.mkdir(parents=True)
            clock = FakeClock()
            rules = [observation_rule(id=f'R-{i}', **({'repeat_interval': 2} if count == 2 else {}))
                     for i in range(count)]
            config = {'observation_rules': rules, 'research_self_checks': True}
            if count == 2:
                config.update(self_check_response_window_seconds=5, observation_interval_seconds=10,
                              tool_review_window_seconds=1)
            tracker = ObservationTracker('EX-sample', workspace, config, time_port=clock)
            self_fact = tracker.fact('observation_fact', {'type': 'fixture'}, clock.monotonic())
            keep(branch + ', no source', 'observation_facts', persistent_record(self_fact))
            write_checkpoint(workspace, counters={'attempts': 2})
            emitted = observe(tracker, {'type': 'item.started', 'item': {'id': 'C', 'type': 'command_execution'}})
            due = next(row for row in emitted if row['kind'] == 'self_check_due')
            obligations(branch + ', open', tracker)
            for row in emitted:
                if row['kind'] == 'observation_fact':
                    keep(branch + ', source', 'observation_facts', persistent_record(row))
            if count == 2:
                acknowledge(tracker, due['id'])
                obligations(branch + ', acknowledged', tracker)
            tracker.record_safe_boundary('CT-boundary', call_ids=['C'])
            obligations(branch + ', boundary', tracker)
            response = self_check_response(due)
            if proposal_kind != 'absent':
                response['rule_proposal'] = {'current_revision': 99 if proposal_kind == 'rejected' else 0,
                    'reason': 'fixture rule choice', 'rules': rules if proposal_kind == 'unchanged' else
                        [observation_rule(id='renamed', repeat_interval=2)]}
            received = tracker.record_self_check_response(response, available_evidence_refs={'EV-1'},
                                                           receipt_id='CT-response' if count == 2 else None)
            keep(branch + ', accepted', 'self_check_responses', received)
            obligations(branch + ', answered', tracker)
            rejected = tracker.record_self_check_response(response, available_evidence_refs={'EV-1'})
            keep(branch + ', repeated response', 'self_check_responses', rejected)

    for mode in ('deadline_only', 'event_driven', 'periodic'):
        for windows in (False, True):
            branch = f'{mode}, windows={windows}, rules=0'
            workspace = Path(root) / f'{mode}-{windows}'
            workspace.mkdir()
            clock = FakeClock()
            config = {'observation_mode': mode, 'research_self_checks': False, 'observation_rules': [],
                      'checkpoint_expected': True}
            if windows:
                config.update(tool_review_window_seconds=1, observation_interval_seconds=2)
            tracker = ObservationTracker('EX-sample', workspace, config, time_port=clock)
            if mode != 'deadline_only':
                tracker.schedule_review('review', at=clock.now(), reason='fixture review', basis_ref='DISP-one')
            observe(tracker, {'type': 'item.started', 'item': {'id': 'C', 'type': 'command_execution'}}, evaluate=False)
            clock.advance(2)
            for row in observe(tracker, {'type': 'tick'}):
                # core_engine._observe_running requests the checkpoint reminder
                # without storing it. Non-review notices leave as fact envelopes.
                if row['kind'] == 'checkpoint_reminder_due':
                    continue
                if row['kind'] == 'observation_capability_missing':
                    keep(branch, 'observation_facts', persistent_record(
                        tracker.fact('observation_fact', row, clock.monotonic())))
                else:
                    keep(branch, 'observations', persistent_record(row))
            assert tracker.stored_obligations() == {}
            keep(branch + ', unknown obligation', 'self_check_responses',
                 tracker.record_self_check_response({}, available_evidence_refs=set()))

    workspace = Path(root) / 'missed'
    workspace.mkdir()
    clock = FakeClock()
    tracker = ObservationTracker('EX-sample', workspace, {'observation_rules': [observation_rule()],
        'self_check_response_window_seconds': 1, 'observation_interval_seconds': 1}, time_port=clock)
    write_checkpoint(workspace, counters={'attempts': 2})
    due = next(row for row in observe(tracker, {'type': 'tick'}) if row['kind'] == 'self_check_due')
    clock.advance(2)
    for row in observe(tracker, {'type': 'tick'}):
        if row['kind'] == 'self_check_missed':
            keep('missed deadline', 'observations', persistent_record(row))
    obligations('missed deadline', tracker)
    # Separate tracker/empty checkpoint: unavailable rule IDs are real notices.
    tracker = ObservationTracker('EX-sample', workspace, {'observation_rules': [observation_rule()],
        'observation_interval_seconds': 1}, time_port=clock)
    (workspace / 'checkpoint.json').unlink()
    clock.advance(1)
    for row in observe(tracker, {'type': 'tick'}):
        if row['kind'] == 'observation_unavailable':
            keep('unavailable measurement', 'observations', persistent_record(row))
    for row in observe(tracker, {'type': 'fixture', 'execution_id': 'EX-other'}, evaluate=False):
        keep('rejected execution input', 'observations' if row['kind'] == 'observation_input_rejected'
             else 'observation_facts', persistent_record(row))
    return rows


def owner_observation_samples(root):
    """Metadata actually published by the owner, including its observation_refs.

    Use the existing real engine/store fixture; only external ports are doubles.
    The rejected input also exercises the tracker's next_owner/followup notice.
    """
    from copy import deepcopy
    from support.engine_control import running_work
    from support.sim import Sim
    sim = Sim.activated(root)
    with running_work(sim, rules=[observation_rule()]) as call:
        call.observe({'type': 'fixture', 'execution_id': 'EX-other'})
        state = call.engine.store.load()[2]
        observation = state['observations'][call.execution_id]
        fact_id, = observation['observation_refs']
        assert json.loads(state['observation_facts'][fact_id]['event_json']) == {
            key: value for key, value in observation.items() if key != 'observation_refs'}
        return [('owner rejected execution input', deepcopy(state['observations']))]
