"""The observation tracker (``observations.ObservationTracker``, layer 2): reviews, self-check obligations and their deadlines.

A tracker observes one execution's provider events (Codex JSONL items, Claude
messages) and the worker's checkpoint, and emits observation rows: reviews,
self-check obligations, misses and facts. Its monotonic clock is a settable
``Clock``; its wall clock is the fake clock port where a test fixes wall time.
Events arrive as the runner delivers them, one stream row at a time
(``research_fixtures.observe``). The engine that applies the rows is
``flows.test_observation_application``.
"""
from support.observation_clock import scripted_clock
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math import observations

from do_math.canonical import canonical_json
from do_math.context_store import collect_outputs
from do_math.execution_profiles import BOUNDARY, seal_profile
from do_math.observations import ObservationTracker, self_check_feedback, tracker_config
from do_math.state_contract import default_state_contract, validate_record
from do_math.submission import _workspace_checks
from support.observation_inputs import Clock, acknowledge, observation_rule, observe, self_check_response, write_checkpoint
from support.fakes.clock import FakeClock


class PublicationCandidateTests(unittest.TestCase):
    def test_candidate_isolates_state_but_keeps_both_clocks_connected(self):
        from support.fakes.clock import FakeClock
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = observations.ObservationTracker('EX-clock', Path(directory),
                {'observation_mode': 'event_driven', 'research_self_checks': False}, time_port=clock)
            tracker.schedule_review('review', at=clock.now(), reason='Check progress', basis_ref='DISP-one')
            candidate = tracker.publication_candidate()
            candidate.explicit_reviews['review']['fired'] = True
            self.assertFalse(tracker.explicit_reviews['review']['fired'])
            self.assertIs(candidate.time_port, clock)
            clock.advance(3)
            self.assertEqual(candidate.time_port.now(), clock.now())
            self.assertEqual(candidate.clock(), clock.monotonic())


def profile(bindings):
    return seal_profile({"role": "research_work", "actor_kind": "ai", "boundary": BOUNDARY,
        "ai": {"model": "test", "capacity_refs": ["CP-test"]}, "observation": {"mode": "event_driven", "settings": {
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            "observation_interval_seconds": 300}, "rule_bindings": bindings}})


def kinds(rows):
    return [row["kind"] for row in rows]


class TrackerCase(unittest.TestCase):
    """A tracker ``E`` of repeating rule ``R-1`` (``attempts`` from the checkpoint, every 2), windows 5 s and 60 s, interval 300 s."""

    def setUp(self):
        from support.entry import entry
        _entry = entry()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.ws, self.clock = Path(temporary.name), Clock()
        self.config = {"observation_rules": [observation_rule(repeat_interval=2)], "self_check_response_window_seconds": 5,
                       "tool_review_window_seconds": 60, "observation_interval_seconds": 300}
        self.t = ObservationTracker("E", self.ws, self.config,  time_port=scripted_clock(self.clock))

    def assert_persisted_notice(self, record):
        schema = default_state_contract().family('runtime', 'observations').schema
        jsonschema.validate({record['execution_id']: observations.persistent_record(record)}, schema)

    def write(self, **changes):
        value = {"current_claim": "c", "evidence_paths": [], "attempts": [], "remaining_work": [],
                 "next_step": "n", "progress_state": "working", **changes}
        (self.ws / "checkpoint.json").write_text(json.dumps(value), encoding="utf-8")

    def due(self):
        # Counters reach the tracker only through the worker's checkpoint.
        self.write(counters={"attempts": 2})
        return next(r for r in observe(self.t, {"type": "tick"}) if r["kind"] == "self_check_due")


class TimingPhaseTests(unittest.TestCase):
    def test_delayed_stream_rows_use_receipt_time_and_replay_cannot_start_live_timers(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for phase in observations.OBSERVATION_PHASE_RULES:
            for mode in observations.OBSERVATION_MODES:
                with self.subTest(phase=phase, mode=mode):
                    workspace = root / f'{phase}-{mode}'
                    workspace.mkdir()
                    clock = FakeClock()
                    tracker = ObservationTracker('EX-phase', workspace, {
                        'observation_mode': mode, 'research_self_checks': False, 'observation_rules': [],
                        'tool_review_window_seconds': 1, 'observation_interval_seconds': 2,
                        'self_check_response_window_seconds': 5}, time_port=clock)
                    received_at = clock.now()
                    received_monotonic = clock.monotonic()
                    clock.advance(1000)
                    tracker.set_execution_status(phase)
                    live = phase == 'running'
                    source = {'stream': 'stdout.jsonl', 'start_offset': 10, 'end_offset': 20,
                              'received_at': received_at, 'received_monotonic': received_monotonic}
                    rows = tracker.observe({'type': 'item.started', 'item': {
                        'id': 'C', 'type': 'command_execution'}}, source=source, live=live)
                    self.assertEqual(kinds(rows), ['observation_fact'])
                    self.assertEqual(rows[0]['monotonic_offset_ms'], 0)
                    self.assertEqual(rows[0]['source'], {key: value for key, value in source.items()
                                                         if key != 'received_monotonic'} | {'received_offset_ms': 0})
                    rows = tracker.observe({'type': 'tick'}, source={**source,
                        'start_offset': 20, 'end_offset': 20, 'received_monotonic': received_monotonic + 1}, live=live)
                    self.assertEqual(kinds(rows), ['tool_review_due']
                                     if live and mode != 'deadline_only' else [])

    def test_self_check_clock_opens_only_for_live_running_evaluation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for phase in observations.OBSERVATION_PHASE_RULES:
            for live in (False, True):
                for evaluate in (False, True):
                    with self.subTest(phase=phase, live=live, evaluate=evaluate):
                        workspace = root / f'{phase}-{live}-{evaluate}'
                        workspace.mkdir()
                        clock = FakeClock()
                        tracker = ObservationTracker('EX-phase', workspace, {
                            'observation_mode': 'event_driven', 'research_self_checks': True,
                            'observation_rules': [observation_rule(repeat_interval=2)],
                            'tool_review_window_seconds': 60, 'observation_interval_seconds': 300,
                            'self_check_response_window_seconds': 5}, time_port=clock)
                        write_checkpoint(workspace, counters={'attempts': 2})
                        tracker.set_execution_status(phase)
                        source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 0,
                                  'received_at': clock.now(), 'received_monotonic': clock.monotonic()}
                        rows = tracker.observe({'type': 'tick'}, source=source, live=live, evaluate=evaluate)
                        expected = phase == 'running' and live and evaluate
                        due = [row for row in rows if row['kind'] == 'self_check_due']
                        self.assertEqual(len(due), int(expected))
                        self.assertEqual(bool(tracker.obligations), expected)
                        self.assertEqual(tracker.checkpoint_count, int(expected))
                        if expected:
                            self.assertEqual(due[0]['deadline_offset_ms'] - due[0]['opened_offset_ms'], 5000)
                            self.assertEqual(due[0]['status'], 'open')

    def test_live_timer_boundaries_cover_every_observation_mode_and_execution_phase(self):
        phases = observations.OBSERVATION_PHASE_RULES
        self.assertEqual(set(phases), {'running', 'stopping', 'ended'})
        self.assertEqual({phase for phase, rule in phases.items() if rule['live']}, {'running'})
        self.assertEqual({phase for phase, rule in phases.items() if rule['terminal']}, {'ended'})
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for phase in phases:
            for mode in observations.OBSERVATION_MODES:
                for live in (False, True):
                    for evaluate in (False, True):
                        for seconds in (0.999, 1.0, 2.0):
                            with self.subTest(phase=phase, mode=mode, live=live, evaluate=evaluate, at=seconds):
                                workspace = root / f'{phase}-{mode}-{live}-{evaluate}-{seconds}'
                                workspace.mkdir()
                                clock = FakeClock()
                                tracker = ObservationTracker('EX-phase', workspace, {
                                    'observation_mode': mode, 'research_self_checks': False, 'observation_rules': [],
                                    'tool_review_window_seconds': 1, 'observation_interval_seconds': 2,
                                    'self_check_response_window_seconds': 5}, time_port=clock)
                                source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 1,
                                          'received_at': clock.now(), 'received_monotonic': clock.monotonic()}
                                tracker.observe({'type': 'item.started', 'item': {
                                    'id': 'C', 'type': 'command_execution'}}, source=source, evaluate=False)
                                tracker.set_execution_status(phase)
                                clock.advance(seconds)
                                rows = tracker.observe({'type': 'tick'}, source={**source,
                                    'start_offset': 1, 'end_offset': 1, 'received_at': clock.now(),
                                    'received_monotonic': clock.monotonic()}, live=live, evaluate=evaluate)
                                expected = []
                                active = phase == 'running' and live and evaluate
                                if active and mode != 'deadline_only' and seconds >= 1:
                                    expected.append('tool_review_due')
                                if active and mode == 'periodic' and seconds >= 2:
                                    expected.append('periodic_review_due')
                                self.assertEqual(kinds(rows), expected)
                                for row in rows:
                                    jsonschema.validate({row['execution_id']: observations.persistent_record(row)},
                                                        default_state_contract().family('runtime', 'observations').schema)
                                self.assertFalse(tracker.obligations)


class ReviewTests(TrackerCase):
    def test_transport_ping_and_idle_do_not_create_math_failure_or_review(self):
        self.clock.value = 200
        for event in ({"type": "tick"}, {"type": "ping"}, {"type": "transport_bytes_received", "bytes": 100}):
            with self.subTest(event=event["type"]):
                rows = observe(self.t, event)
                self.assertFalse(any("review" in r["kind"] or r["kind"] == "self_check_due" for r in rows), rows)

    def test_frozen_window_ignores_worker_timeout_and_mutated_input_config(self):
        self.config.update(tool_review_window_seconds=1, observation_mode="periodic")
        observe(self.t, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "C", "name": "Bash",
            "input": {"timeout": 1, "observation_review_window_seconds": 1}}]}})
        self.clock.value = 2
        self.assertEqual(observe(self.t, {"type": "tick"}), [])
        self.clock.value = 60
        reviews = [r for r in observe(self.t, {"type": "tick"}) if r["kind"] == "tool_review_due"]
        self.assertEqual([r["window_ms"] for r in reviews], [60000])
        self.assert_persisted_notice(reviews[0])
        self.assertEqual(observe(self.t, {"type": "tick"}), [])

    def test_adapter_completion_matches_exact_call_and_duplicate_start_cannot_delay(self):
        observe(self.t, {"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.clock.value = 50
        observe(self.t, {"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        observe(self.t, {"type": "item.completed", "item": {"type": "command_execution", "id": "OTHER"}})
        self.clock.value = 60
        self.assertEqual([r["call_id"] for r in observe(self.t, {"type": "tick"}) if r["kind"] == "tool_review_due"], ["C"])
        observe(self.t, {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "C", "content": "done"}]}})
        self.assertEqual(self.t.completed_call_ids, {"C", "OTHER"})
        self.assertEqual(self.t.pending_tools, {})

    def test_periodic_and_explicit_reviews_have_independent_bases(self):
        # The wall clock stands exactly at the scheduled time; the monotonic clock at the periodic interval.
        wall = FakeClock(wall=datetime(2026, 9, 20, 10, 0, tzinfo=timezone.utc))
        wall.monotonic = self.clock
        tracker = ObservationTracker("P", self.ws, {"observation_mode": "periodic", "observation_interval_seconds": 3},
                                      time_port=wall)
        tracker.schedule_review("RECHECK", at="2026-09-20T10:00:00Z", reason="inspect recovery", basis_ref="DISP-1")
        self.clock.value = 3
        rows = observe(tracker, {"type": "tick"})
        self.assertEqual({r["kind"] for r in rows}, {"periodic_review_due", "explicit_review_due"})
        for row in rows:
            self.assert_persisted_notice(row)
        self.assertEqual(observe(tracker, {"type": "tick"}), [])

    def test_deadline_only_never_opens_recursive_review(self):
        from support.entry import entry
        _entry = entry()
        tracker = ObservationTracker("D", self.ws, {"observation_mode": "deadline_only", "observation_interval_seconds": 1,
            "tool_review_window_seconds": 1},  time_port=scripted_clock(self.clock))
        observe(tracker, {"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.clock.value = 100
        self.assertEqual(observe(tracker, {"type": "tick"}), [])
        with self.assertRaisesRegex(ValueError, "deadline_only cannot schedule recursive operational review"):
            tracker.schedule_review("R", at="2026-01-01T00:00:00Z", reason="x", basis_ref="X")


class SelfCheckObligationTests(TrackerCase):
    def test_maximum_interval_opens_self_check_and_valid_response_reanchors(self):
        self.clock.value = 300
        rows = observe(self.t, {"type": "tick"})
        for row in rows:
            if row['kind'] == 'observation_unavailable':
                self.assert_persisted_notice(row)
        obligation = next(r for r in rows if r["kind"] == "self_check_due")
        self.assertEqual(obligation["due"][0]["rule_id"], "@maximum_interval")
        self.assertEqual(observe(self.t, {"type": "tick"}), [])
        self.clock.value = 301
        result = self.t.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(result["next_self_check_offset_ms"], 601000)
        repeated = self.t.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(repeated["kind"], "self_check_rejected")
        self.assertEqual(self.t.next_self_check_offset_ms, 601000)

    def test_missed_self_check_notification_matches_persisted_contract(self):
        obligation = self.due()
        self.clock.value = 6
        notice = next(row for row in observe(self.t, {'type': 'tick'}) if row['kind'] == 'self_check_missed')
        self.assertEqual(notice['obligation_id'], obligation['id'])
        self.assert_persisted_notice(notice)

    def test_response_coverage_identity_revision_and_current_evidence(self):
        obligation = self.due()
        for change, errors in (({"execution_id": "OTHER"}, ["execution_mismatch"]),
                               ({"rule_revision": 99}, ["revision_mismatch"]),
                               ({"rule_results": []}, ["invalid_response_schema"]),
                               ({"obligation_id": []}, ["invalid_response_schema", "unknown_obligation"])):
            with self.subTest(change=change):
                response = {**self_check_response(obligation), **change}
                rejected = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
                self.assertEqual(rejected["kind"], "self_check_rejected")
                self.assertEqual(rejected["errors"], errors)
        response = self_check_response(obligation)
        self.assertIn("evidence_not_current", self.t.record_self_check_response(response, available_evidence_refs=set())["errors"])
        self.assertEqual(self.t.obligations[obligation["id"]]["status"], "open")

    def test_normal_defect_indeterminate_followups(self):
        from support.entry import entry
        _entry = entry()
        self.write(counters={"attempts": 2})
        for status, expected in (("normal", "continue"), ("defect", "operational_review_due"), ("indeterminate", "operational_review_due")):
            with self.subTest(status=status):
                tracker = ObservationTracker(status, self.ws, self.config,  time_port=scripted_clock(self.clock))
                obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
                response = self_check_response(obligation, status, [] if status == "indeterminate" else None)
                result = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
                self.assertEqual(result["kind"], "self_check_received")
                self.assertEqual(result["followup"]["kind"], expected)

    def test_no_progress_limit_keeps_count_across_rule_replacement(self):
        from support.entry import entry
        _entry = entry()
        tracker = ObservationTracker("E", self.ws, {**self.config, "no_progress_limit": 2},  time_port=scripted_clock(self.clock))
        for count in (2, 4):
            self.write(counters={"attempts": count})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            response = {**self_check_response(obligation), "progress": "no_progress"}
            if count == 2:
                response["rule_proposal"] = {"current_revision": 0, "reason": "rename", "rules": [observation_rule(id="R-new", repeat_interval=2)]}
            result = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
            self.assertEqual(result["no_progress_count"], count // 2)
        self.assertEqual(result["followup"]["trigger"], "repeated_no_progress")
        tracker.acknowledge_review(observation_refs=[result["id"]])
        self.assertEqual(tracker.no_progress_count, 0)

    def test_feedback_producers_share_the_public_field_set(self):
        with self.assertRaisesRegex(ValueError, "private or unknown"):
            observations.worker_feedback({"kind": "x", "diagnostic": "private"})
        obligation = self.due()
        self.assertLessEqual(set(observations.self_check_feedback(obligation)), observations.WORKER_FEEDBACK_FIELDS)
        request = self.t.issue_self_check(obligation["id"])
        self.assertEqual(request, observations.self_check_request(self.t.obligations[obligation["id"]]))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            self.t.record_delivery(obligation["id"], source_offset=-1)

    def test_tracker_records_leave_through_the_storage_check(self):
        """The tracker runs the storage gate's own checker on what ENGINE saves (이음새-정본.md §6)."""
        obligation = self.due()
        response = {**self_check_response(obligation), "rule_proposal": {"current_revision": 0,
            "reason": "rename", "rules": [observation_rule(id="renamed", repeat_interval=2)]}}
        record = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        validate_record(default_state_contract().family("runtime", "self_check_responses").checker, record, "response")
        self.assertEqual(self.t.stored_obligations(), self.t.obligations)
        self.t.obligations[obligation["id"]]["bookkeeping"] = []
        with self.assertRaisesRegex(ValueError, "bookkeeping"):
            self.t.stored_obligations()

    def test_unissued_delivery_and_malformed_feedback_do_not_consume_the_obligation(self):
        obligation = self.due()
        before = deepcopy(self.t.stored_obligations())
        consumed = deepcopy(self.t.consumed_rules)
        with self.assertRaises(ValueError) as rejected:
            self.t.record_delivery(obligation['id'], source_offset=0)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception), 'self-check delivery requires an issued request')
        for malformed, reason in (
                ([], 'self-check feedback requires a self_check_due obligation'),
                ({**obligation, 'kind': 'other'}, 'self-check feedback requires a self_check_due obligation'),
                ({**obligation, 'due': []}, 'malformed self-check obligation'),
                ({**obligation, 'rule_revision': '0'}, 'malformed self-check obligation')):
            with self.subTest(obligation=malformed), self.assertRaises(ValueError) as rejected:
                self_check_feedback(malformed)
            self.assertIs(type(rejected.exception), ValueError)
            self.assertEqual(str(rejected.exception), reason)
            self.assertEqual(self.t.stored_obligations(), before)
            self.assertEqual(self.t.consumed_rules, consumed)
        request = self.t.issue_self_check(obligation['id'])
        self.t.record_delivery(obligation['id'], source_offset=0)
        self.assertEqual(request, observations.self_check_request(self.t.obligations[obligation['id']]))
        self.assertIs(type(self.t.obligations[obligation['id']]['delivered_source_offset']), int)
        self.assertEqual(self.t.obligations[obligation['id']]['delivered_source_offset'], 0)


class RuleProposalTests(TrackerCase):
    def test_a_rules_file_in_the_workspace_is_not_a_replacement_path(self):
        # Only a self-check response's rule_proposal replaces rules; a workspace file is ordinary output
        # that neither replaces them nor draws a notice.
        proposal = {"current_revision": 0, "reason": "rename", "rules": [observation_rule(id="R-new")]}
        (self.ws / "observation-rules.json").write_text(json.dumps(proposal), encoding="utf-8")
        rows = observe(self.t, {"type": "tick"})
        self.assertFalse(any(r["kind"] == "observation_rules_rejected" for r in rows), rows)
        self.assertEqual(self.t.rules, self.config["observation_rules"])
        self.assertEqual(self.t.rule_revision, 0)
        self.assertEqual(self.t.next_self_check_offset_ms, 300000)

    def test_valid_response_accepts_rules_but_bad_proposal_keeps_previous(self):
        obligation = self.due()
        response = self_check_response(obligation)
        response["rule_proposal"] = {"current_revision": 99, "reason": "stale", "rules": [observation_rule(id="renamed")]}
        result = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received")
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_rejected")
        self.assertEqual(self.t.rule_revision, 0)

    def test_rule_proposal_travels_in_the_response_and_a_rules_file_is_not_checked(self):
        from support.entry import entry
        _entry = entry()
        proposal = {"current_revision": 0, "reason": "Use a renamed rule",
                    "rules": [observation_rule(id="renamed", repeat_interval=2)]}
        obligation = self.due()
        result = self.t.record_self_check_response({**self_check_response(obligation), "rule_proposal": proposal},
            available_evidence_refs={"EV-1"})
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_accepted")
        context = {"submission_contract": {"limits": {"max_artifact_bytes": 100000}}}
        path = self.ws / "observation-rules.json"
        # A file of any shape carries no rule meaning, so neither a live nor a captured submission checks it.
        for value in (proposal, proposal["rules"], {**proposal, "current_revision": -1}):
            path.write_text(json.dumps(value), encoding="utf-8")
            for captured in (None, collect_outputs(self.ws)):
                issues, _ = _workspace_checks(context, self.ws, candidate=captured, clock=_entry.ports.clock)
                self.assertEqual(issues, [], issues)
        self.assertEqual(self.t.rule_revision, 1)

    def test_malformed_rule_proposal_does_not_reject_valid_self_check(self):
        obligation = self.due()
        response = {**self_check_response(obligation), "rule_proposal": {"current_revision": 0, "reason": "bad",
                                                                           "rules": [observation_rule(threshold=1.5)]}}
        result = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received")
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_rejected")

    def test_identical_rule_proposal_preserves_revision_and_consumed_boundary(self):
        obligation = self.due()
        before = deepcopy(self.t.consumed_rules)
        digest = self.t.rules_digest
        rules = deepcopy(self.t.rules)
        response = self_check_response(obligation)
        response['rule_proposal'] = {'current_revision': self.t.rule_revision,
                                    'reason': 'Keep the current rule', 'rules': rules}
        result = self.t.record_self_check_response(response, available_evidence_refs={'EV-1'})
        self.assertEqual(result['kind'], 'self_check_received')
        update = result['rule_update']
        self.assertEqual(update['kind'], 'observation_rules_unchanged')
        self.assertEqual(update['rules'], rules)
        self.assertEqual((update['previous_rules_sha256'], update['active_rules_sha256']), (digest, digest))
        self.assertIs(type(update['active_revision']), int)
        self.assertEqual(update['active_revision'], obligation['rule_revision'])
        self.assertEqual(self.t.consumed_rules, before)
        self.assertEqual(before, {row['boundary_key']: row['boundary'] for row in obligation['due']})
        rows = observe(self.t, {'type': 'tick'})
        self.assertNotIn('self_check_due', kinds(rows))
        self.write(counters={'attempts': 4})
        next_due = [row for row in observe(self.t, {'type': 'tick'}) if row['kind'] == 'self_check_due']
        self.assertEqual(len(next_due), 1)
        self.assertEqual([(row['first_boundary'], row['boundary']) for row in next_due[0]['due']], [(4, 4)])


class CheckpointSignalTests(TrackerCase):
    def test_invalid_checkpoint_counters_do_not_partially_advance(self):
        self.write(counters={"attempts": 1, "branches": 5})
        observe(self.t, {"type": "tick"})
        self.write(counters={"attempts": 2, "branches": 4})
        rows = observe(self.t, {"type": "tick"})
        rejected = [r for r in rows if r["kind"] == "checkpoint_observation_rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertIn("checkpoint counters cannot decrease", rejected[0]["reason"])
        self.assertEqual(self.t.counters, {"attempts": 1, "branches": 5})
        self.assertEqual(self.t.obligations, {})

    def test_provider_event_counters_are_not_observation_signals(self):
        rows = observe(self.t, {"type": "tick", "counters": {"attempts": 9}, "iterations": {"E": 9},
                               "active_duration_ms": 9000, "id": "provider-event"})
        self.assertEqual(self.t.counters, {})
        self.assertEqual(self.t.iterations, {})
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))

    def test_actual_checkpoint_counters_and_iterations_repeat_without_recounting_bytes(self):
        self.write(counters={"attempts": 2}, iteration=3)
        self.assertTrue(any(r["kind"] == "self_check_due" for r in observe(self.t, {"type": "tick"})))
        self.assertEqual(self.t.iterations, {"E": 3})
        self.assertEqual(observe(self.t, {"type": "tick"}), [])
        self.write(counters={"attempts": 4}, iteration=4)
        self.assertTrue(any(r["kind"] == "self_check_due" for r in observe(self.t, {"type": "tick"})))
        self.write(counters={"attempts": 2}, iteration=3)
        observe(self.t, {"type": "tick"})
        self.assertEqual(self.t.checkpoint_count, 2)

    def test_self_check_calls_and_checkpoints_do_not_trigger_themselves(self):
        from support.entry import entry
        _entry = entry()
        obligation = self.due()
        self.t.obligations[obligation['id']]['status'] = 'answered'
        observe(self.t, {"type": "item.completed", "item": {"type": "mcp_tool_call", "id": "SC-CALL",
            "server": "execution_control", "tool": "control_self_check",
            "arguments": {"self_check_id": obligation['id']}}}, evaluate=False)
        self.assertNotIn("SC-CALL", self.t.completed_call_ids)
        counted = self.t.checkpoint_count
        self.write(counters={"attempts": 2}, current_claim="self-check lineage")
        checkpoint = observations.read_checkpoint(self.ws, clock=_entry.ports.clock)
        self.t.register_self_check_checkpoint(checkpoint["sha256"])
        observe(self.t, {"type": "tick"})
        self.assertEqual(self.t.checkpoint_count, counted)

    def test_missing_checkpoint_reminder_only_for_checkpointing_roles(self):
        from support.entry import entry
        _entry = entry()
        tracker = ObservationTracker("W", self.ws, {**self.config, "checkpoint_expected": True},  time_port=scripted_clock(self.clock))
        self.clock.value = 300
        self.assertTrue(any(r["kind"] == "checkpoint_reminder_due" for r in observe(tracker, {"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in observe(tracker, {"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in observe(self.t, {"type": "tick"})))

    def test_counted_checkpoint_cannot_be_reclassified_as_self_check_evidence(self):
        rules = observations.bind_task_rules([
            observation_rule('checkpoint_count_gte', 'checkpoint', '$execution', 1)], 'E')
        tracker = ObservationTracker('E', self.ws, {**self.config, 'observation_rules': rules},
                                     time_port=scripted_clock(self.clock))
        write_checkpoint(self.ws, counters={'attempts': 1})
        raw = (self.ws / 'checkpoint.json').read_bytes()
        import hashlib
        digest = hashlib.sha256(raw).hexdigest()
        rows = observe(tracker, {'type': 'tick'})
        due = [row for row in rows if row['kind'] == 'self_check_due']
        self.assertEqual(len(due), 1)
        self.assertEqual([(row['operator'], row['value'], row['boundary']) for row in due[0]['due']],
                         [('checkpoint_count_gte', 1, 1)])
        consumed = deepcopy(tracker.consumed_rules)
        before = tracker.stored_obligations()
        with self.assertRaises(ValueError) as rejected:
            tracker.register_self_check_checkpoint(digest)
        self.assertIs(type(rejected.exception), ValueError)
        self.assertEqual(str(rejected.exception),
                         'checkpoint already counted; response lineage must precede file polling')
        self.assertEqual(tracker.self_check_checkpoints, set())
        self.assertEqual(tracker.consumed_rules, consumed)
        self.assertEqual(tracker.stored_obligations(), before)
        self.assertNotIn('self_check_due', kinds(observe(tracker, {'type': 'tick'})))
        self.assertEqual(tracker.checkpoint_count, 1)
        self.assertEqual((self.ws / 'checkpoint.json').read_bytes(), raw)


class DeadlineHoldTests(TrackerCase):
    def test_obligation_opened_during_a_research_call_is_held_until_the_call_ends(self):
        observe(self.t, {"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        obligation = self.due()
        held = self.t.obligations[obligation["id"]]
        self.assertEqual((held["deadline_offset_ms"], held["deadline_held_offset_ms"]), (5000, 0))
        self.clock.value = 30
        self.assertFalse(any(r["kind"] == "self_check_missed" for r in observe(self.t, {"type": "tick"})))
        observe(self.t, {"type": "item.completed", "item": {"type": "command_execution", "id": "C"}})
        self.assertEqual(held["deadline_offset_ms"], 35000)
        self.assertNotIn("deadline_held_offset_ms", held)
        # No safety boundary is needed before the response.
        result = self.t.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received", result.get("errors"))


class ExecutionTrackerTests(unittest.TestCase):
    """A tracker ``EX-1`` of the single rule ``R-1`` without an observation interval."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory, self.clock = Path(temporary.name), Clock()

    def tracker(self, **extra):
        from support.entry import entry
        _entry = entry()
        return ObservationTracker("EX-1", self.directory, {"observation_rules": [observation_rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5, **extra},  time_port=scripted_clock(self.clock))

    def open_obligation(self, tracker):
        write_checkpoint(self.directory, counters={"attempts": 2})
        return next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")

    def test_tracker_creates_self_check_and_call_specific_review_facts(self):
        tracker = self.tracker(self_check_revision=3)
        obligation = self.open_obligation(tracker)
        self.assertEqual(3, obligation["rule_revision"])
        received = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual("self_check_received", received["kind"])
        feedback = self_check_feedback(obligation)
        self.assertEqual(obligation["id"], feedback["obligation_id"])
        self.assertNotIn("basis", feedback["due"][0])
        observe(tracker, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "CALL-1", "name": "Bash",
            "input": {"observation_review_window_seconds": 3}}]}})
        self.clock.value = 3
        self.assertFalse(any(row["kind"] == "tool_review_due" for row in observe(tracker, {"type": "tick"})))
        self.clock.value = 60
        review = observe(tracker, {"type": "tick"})
        self.assertEqual("CALL-1", next(row for row in review if row["kind"] == "tool_review_due")["call_id"])

    def test_a_response_citing_only_evidence_the_rule_does_not_require_is_rejected(self):
        tracker = self.tracker()
        obligation = self.open_obligation(tracker)
        rejected = tracker.record_self_check_response(self_check_response(obligation, evidence=["unrelated"]),
                                                      available_evidence_refs={"unrelated"})
        self.assertEqual(rejected["kind"], "self_check_rejected")
        self.assertEqual(rejected["errors"], ["required_evidence_missing"])

    def test_a_worker_tool_input_cannot_shorten_the_tool_review_window(self):
        """The worker's ``timeout`` and review window in a tool input do not bring the fixed 60 s review forward."""
        tracker = self.tracker()
        self.open_obligation(tracker)
        observe(tracker, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "C", "name": "Bash",
            "input": {"timeout": 1, "observation_review_window_seconds": 1}}]}})
        self.clock.value = 2
        self.assertFalse(any(r["kind"] == "tool_review_due" for r in observe(tracker, {"type": "tick"})))

    def test_response_deadline_is_current_and_rejection_reaches_worker(self):
        tracker = self.tracker()
        obligation = self.open_obligation(tracker)
        self.clock.value = 6
        rejected = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(rejected["kind"], "self_check_rejected")
        self.assertIn("response_deadline_passed", rejected["errors"])
        self.assertEqual(rejected["followup"]["kind"], "operational_review_due")

    def test_call_reported_at_a_safe_boundary_stops_holding_the_deadline(self):
        tracker = self.tracker()
        observe(tracker, {"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
        obligation = self.open_obligation(tracker)
        self.assertEqual((obligation["deadline_offset_ms"], obligation["deadline_held_offset_ms"]), (5000, 0))
        self.clock.value = 9
        tracker.record_safe_boundary("CT-1", call_ids=["C"])
        self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 14000)
        self.clock.value = 14
        accepted = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(accepted["kind"], "self_check_received")

    def test_deadline_held_by_a_call_running_at_opening_passes_after_the_call_ends(self):
        tracker = self.tracker()
        observe(tracker, {"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
        obligation = self.open_obligation(tracker)
        self.assertEqual(obligation["deadline_held_offset_ms"], 0)
        self.clock.value = 9
        observe(tracker, {"type": "item.completed", "item": {"id": "C", "type": "command_execution"}})
        self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 14000)
        self.clock.value = 15
        rejected = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(rejected["kind"], "self_check_rejected")
        self.assertIn("response_deadline_passed", rejected["errors"])

    def test_research_calls_before_the_response_hold_its_deadline_until_all_of_them_end(self):
        tracker = self.tracker()
        start = lambda cid: observe(tracker, {"type": "item.started", "item": {"id": cid, "type": "command_execution"}})
        end = lambda cid: observe(tracker, {"type": "item.completed", "item": {"id": cid, "type": "command_execution"}})
        missed = lambda rows: any(r["kind"] == "self_check_missed" for r in rows)
        obligation = self.open_obligation(tracker)
        held = tracker.obligations[obligation["id"]]
        self.assertEqual(held["deadline_offset_ms"], 5000)
        self.clock.value = 1
        start("A")
        self.clock.value = 3
        start("B")
        self.clock.value = 20
        self.assertFalse(missed(end("A")), "a nested call still running holds the deadline")
        self.clock.value = 30
        self.assertFalse(missed(end("B")))
        self.assertEqual(held["deadline_offset_ms"], 34000)
        self.assertNotIn("deadline_held_offset_ms", held)
        self.clock.value = 31
        start("C")
        self.clock.value = 40
        self.assertFalse(missed(end("C")))
        self.assertEqual(held["deadline_offset_ms"], 43000)
        self.clock.value = 43
        accepted = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(accepted["kind"], "self_check_received")

    def test_research_call_after_the_deadline_does_not_hold_it(self):
        tracker = self.tracker()
        self.open_obligation(tracker)
        self.clock.value = 6
        rows = observe(tracker, {"type": "item.started", "item": {"id": "late", "type": "command_execution"}})
        self.assertTrue(any(r.get("reason") == "response_deadline_passed" for r in rows))

    def test_integer_persistence_keeps_raw_adapter_payload_as_text(self):
        tracker = self.tracker()
        self.clock.value = 0.125
        facts = observe(tracker, {"type": "result", "duration": 0.25})
        fact = next(r for r in facts if r["kind"] == "observation_fact")
        canonical_json(fact)
        self.assertEqual(fact["monotonic_offset_ms"], 125)
        self.assertEqual(json.loads(fact["event_json"])["duration"], .25)

    def test_missing_checkpoint_counter_is_reported_not_zero_or_wall_time(self):
        tracker = self.tracker()
        self.clock.value = 100
        rows = observe(tracker, {"type": "tick"})
        unavailable = next(r for r in rows if r["kind"] == "observation_unavailable")
        self.assertEqual(unavailable["rule_ids"], ["R-1"])
        self.assertEqual(unavailable["followup"]["kind"], "operational_review_due")
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))

    def test_unavailable_text_rule_ids_publish_and_reload_without_record_id_restrictions(self):
        from support.state_builders import current_state
        from support.storage_records import record_store
        ids = ['progress check', '규칙', 'r:1', ' \t']
        tracker = self.tracker(observation_rules=[observation_rule(id=value) for value in ids])
        self.clock.value = 100
        rows = observe(tracker, {'type': 'tick'})
        unavailable = next(row for row in rows if row['kind'] == 'observation_unavailable')
        self.assertEqual(unavailable['rule_ids'], ids)
        repo = record_store(self.directory / 'published')
        head = repo.initialize(*current_state(runtime={'observations': {'EX-1': unavailable}}))
        self.assertEqual(repo.load(head)[2]['observations'], {'EX-1': unavailable})

    def test_maximum_interval_keeps_distinct_ids_for_every_due_rule(self):
        from support.entry import entry
        _entry = entry()
        tracker = ObservationTracker("EX-1", self.directory, {
            "observation_rules": [observation_rule(id="@maximum_interval"), observation_rule(id="@maximum_interval:1")],
            "observation_interval_seconds": 10, "tool_review_window_seconds": 60,
            "self_check_response_window_seconds": 5},  time_port=scripted_clock(self.clock))
        self.clock.value = 10
        obligation = self.open_obligation(tracker)
        ids = [row["rule_id"] for row in obligation["due"]]
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertTrue({"@maximum_interval", "@maximum_interval:1"}.issubset(ids))
        received = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(received["kind"], "self_check_received")


class SelfCheckControlBindingTests(unittest.TestCase):
    """A self-check response counts only through a control request bound to its receipt."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.ws = Path(temporary.name)
        self.clock = Clock()

    def tracker(self):
        from support.entry import entry
        _entry = entry()
        return ObservationTracker("EX-1", self.ws, {"observation_rules": [observation_rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5},  time_port=scripted_clock(self.clock))

    def submission(self, tracker):
        write_checkpoint(self.ws, counters={"attempts": 2})
        obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
        # The worker has polled the delivered request: a research action from here misses it.
        acknowledge(tracker, obligation["id"])
        response = self_check_response(obligation)
        request = {"request_id": "self-check-" + obligation["id"], "execution_id": "EX-1", "kind": "self_check_response",
                   "payload": {"self_check_id": obligation["id"], "response": response}}
        event = {"type": "item.started", "item": {"id": "CALL-SC", "type": "mcp_tool_call", "server": "execution_control",
                 "tool": "control_self_check", "arguments": {"self_check_id": obligation["id"], "response": response}}}
        return response, request, event

    def test_real_control_submission_is_not_research_action(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        rows = observe(tracker, event)
        self.assertFalse(any(r["kind"] == "self_check_missed" for r in rows))
        tracker.bind_control_request(request, receipt_id="CT-1")
        record = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"}, receipt_id="CT-1")
        self.assertEqual(record["kind"], "self_check_received")
        self.assertIn("CALL-SC", tracker.self_check_call_ids)
        self.assertEqual(tracker.control_requests[request["request_id"]]["receipt_id"], "CT-1")

    def test_receipt_before_adapter_event_and_claude_shape(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        tracker.bind_control_request(request, receipt_id="CT-1")
        item = event["item"]
        observe(tracker, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": item["id"],
            "name": "mcp__execution_control__control_self_check", "input": item["arguments"]}]}})
        self.assertEqual(tracker.record_self_check_response(response, available_evidence_refs={"EV-1"},
                                                            receipt_id="CT-1")["kind"], "self_check_received")

    def test_unbound_or_different_control_request_cannot_acknowledge_response(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        observe(tracker, event)
        rejected = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertIn("control_request_unconfirmed", rejected["errors"])
        altered = deepcopy(request)
        altered["payload"]["response"]["next_method"] = "different"
        with self.assertRaisesRegex(ValueError, "received control request differs from observed call"):
            tracker.bind_control_request(altered, receipt_id="CT-2")

    def test_other_control_submit_and_wrong_server_remain_research_actions(self):
        for change in ("kind", "server"):
            with self.subTest(change=change):
                tracker = self.tracker()
                _, _, event = self.submission(tracker)
                if change == "server":
                    event["item"]["server"] = "untrusted"
                else:
                    event["item"].update(tool="control_submit", arguments={"request_id": "P", "kind": "submission_preview",
                                                                          "payload": {}})
                self.assertTrue(any(r["kind"] == "self_check_missed" for r in observe(tracker, event)))

    def test_checkpoint_counter_rule_ignores_counters_from_another_source(self):
        from support.entry import entry
        _entry = entry()
        rule = observation_rule(basis={"source": "checkpoint", "unit": "count"})
        binding = {"operator": rule["operator"], "subject_kind": rule["subject"]["kind"], **rule["basis"]}
        tracker = ObservationTracker("EX-1", self.ws, tracker_config(profile([binding]), initial_self_check_rules=[rule]),
                                      time_port=scripted_clock(self.clock))
        rows = observe(tracker, {"type": "tick", "counters": {"attempts": 2}})
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))
        (self.ws / "checkpoint.json").write_text(json.dumps({"current_claim": "c", "evidence_paths": [], "attempts": [],
            "remaining_work": [], "next_step": "n", "progress_state": "working", "counters": {"attempts": 2}}),
            encoding="utf-8")
        self.assertTrue(any(r["kind"] == "self_check_due" for r in observe(tracker, {"type": "tick"})))

    def test_receipt_cannot_be_reused_for_a_different_response_body(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        observe(tracker, event)
        tracker.bind_control_request(request, receipt_id="CT-1")
        changed = {**response, "next_method": "not the submitted method"}
        self.assertIn("control_response_mismatch", tracker.record_self_check_response(changed,
                      available_evidence_refs={"EV-1"}, receipt_id="CT-1")["errors"])


class SelfCheckAcknowledgementTests(unittest.TestCase):
    """When a delivered self-check request counts as received, and which later research action misses it.

    Rows carry their stream coordinates (``source``) as the runner's batch
    gives them; the request is delivered at stream offset 100.
    """

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory, self.clock = Path(temporary.name), Clock()

    def delivered(self):
        from support.entry import entry
        _entry = entry()
        tracker = ObservationTracker('EX-one', self.directory, {'observation_rules': [observation_rule()],
            'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5},  time_port=scripted_clock(self.clock))
        write_checkpoint(self.directory, counters={'attempts': 2})
        obligation = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
        # The poll returns the exact request object the tracker issued and hashed.
        envelope = deepcopy(tracker.issue_self_check(obligation['id']))
        tracker.record_delivery(obligation['id'], source_offset=100)
        return tracker, obligation, envelope

    def test_native_poll_ack_requires_the_exact_successful_returned_request(self):
        for variant in ('ok', 'started', 'failed', 'wrong_payload', 'error_result', 'claude'):
            with self.subTest(variant=variant):
                tracker, obligation, envelope = self.delivered()
                if variant == 'wrong_payload':
                    envelope['payload']['rule_revision'] += 1
                item = {'id': 'poll', 'type': 'mcp_tool_call', 'server': 'execution_control',
                    'tool': 'control_self_check', 'arguments': {'self_check_id': obligation['id']},
                    'status': 'failed' if variant == 'failed' else 'completed',
                    'result': {'content': [{'type': 'text', 'text': json.dumps(envelope)}],
                               'isError': variant == 'error_result'}}
                source = {'stream': 'stdout.jsonl', 'start_offset': 100, 'end_offset': 150,
                          'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 1}
                if variant == 'claude':
                    tracker.observe({'type': 'assistant', 'message': {'content': [{'type': 'tool_use',
                        'id': 'poll', 'name': 'mcp__execution_control__control_self_check', 'input': item['arguments']}]}},
                        source=source, evaluate=False)
                    event = {'type': 'user', 'message': {'content': [{'type': 'tool_result',
                        'tool_use_id': 'poll', 'content': json.dumps(envelope)}]}}
                else:
                    event = {'type': 'item.started' if variant == 'started' else 'item.completed', 'item': item}
                tracker.observe(event, source=source, evaluate=False)
                acknowledged = variant in {'ok', 'claude'}
                self.assertEqual(tracker.obligations[obligation['id']].get('acknowledged_call_id'),
                                 'poll' if acknowledged else None)
                rows = tracker.observe({'type': 'item.started', 'item': {'id': 'new', 'type': 'command_execution'}},
                    source={**source, 'start_offset': 150, 'end_offset': 200, 'received_monotonic': 2}, evaluate=False)
                self.assertEqual(any(r['kind'] == 'self_check_missed' for r in rows), acknowledged)

    def test_native_command_after_delivery_without_ack_is_only_missing_response_evidence(self):
        tracker, obligation, _ = self.delivered()
        source = {'stream': 'stdout.jsonl', 'start_offset': 200, 'end_offset': 300,
                  'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 1}
        rows = tracker.observe({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'late'}},
                               source=source, evaluate=False)
        self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows),
                         'Publication after delivery does not establish receipt of this self-check')
        # The running command held the deadline from 1s to 2s, so it passes after 6s.
        self.clock.value = 2
        observe(tracker, {'type': 'item.completed', 'item': {'type': 'command_execution', 'id': 'late'}})
        self.clock.value = 7
        rows = observe(tracker, {'type': 'tick'})
        self.assertTrue(any(r.get('reason') == 'response_deadline_passed' for r in rows))

    def test_buffered_command_before_delivery_is_not_a_new_action_violation(self):
        tracker, obligation, envelope = self.delivered()
        source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 80, 'received_at': '2026-09-25T00:00:00Z',
                  'received_monotonic': 1}
        old = {'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'old'}}
        rows = tracker.observe(old, source=source, evaluate=False)
        self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows))
        new = {'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'new'}}
        partial = {**old, 'item': {**old['item'], 'id': 'partial-before-delivery'}}
        rows = tracker.observe(partial, source={**source, 'start_offset': 80, 'end_offset': 160}, evaluate=False)
        self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows),
                         'The beginning of a partially written old event predates delivery')
        poll = {'type': 'item.completed', 'item': {'id': 'poll', 'type': 'mcp_tool_call',
            'server': 'execution_control', 'tool': 'control_self_check',
            'arguments': {'self_check_id': obligation['id']}, 'status': 'completed',
            'result': {'content': [{'type': 'text', 'text': json.dumps(envelope)}]}}}
        tracker.observe(poll, source={**source, 'start_offset': 100, 'end_offset': 160}, evaluate=False)
        rows = tracker.observe(new, source={**source, 'start_offset': 160, 'end_offset': 200, 'received_monotonic': 2},
                               evaluate=False)
        self.assertTrue(any(r['kind'] == 'self_check_missed' for r in rows))


if __name__ == "__main__":
    unittest.main()
