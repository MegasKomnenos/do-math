"""Observation of executions: rules and trackers, self-check obligations and their control-bound responses, and the profile signal contract."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import observations
from research_fixtures import acknowledge, Clock, git_init, observation_batch, observation_rule, observe, self_check_response, write_checkpoint
from do_math.execution_profiles import BOUNDARY, build_profiles, profile_ref, seal_profile
from do_math.observations import ObservationTracker, evaluate_rules, observation_rule_contract, self_check_feedback, tracker_config, validate_rules
from do_math.operational_dispositions import validate_disposition, worker_feedback
from provider_fixtures import PROFILE_CONFIG


def profile(bindings):
    return seal_profile({"role": "research_work", "actor_kind": "ai", "boundary": BOUNDARY,
        "ai": {"model": "test", "capacity_refs": ["CP-test"]}, "observation": {"mode": "event_driven", "settings": {
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            "observation_interval_seconds": 300}, "rule_bindings": bindings}})


def counter_rule(*, source="checkpoint"):
    return observation_rule(id="SC-attempts", basis={"source": source, "unit": "count"},
                            required_evidence=["checkpoint.json"])


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws, self.clock = Path(self.temp.name), Clock()
        self.config = {"observation_rules": [observation_rule(repeat_interval=2)], "self_check_response_window_seconds": 5,
                       "tool_review_window_seconds": 60, "observation_interval_seconds": 300}
        self.t = observations.ObservationTracker("E", self.ws, self.config, clock=self.clock)

    def tearDown(self): self.temp.cleanup()

    def assert_persisted_notice(self, record):
        import jsonschema
        from do_math.state_contract import default_state_contract
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

    def test_repeated_checkpoint_reads_reuse_schema_but_recheck_value_and_evidence(self):
        import jsonschema
        self.write()
        validator = jsonschema.validators.validator_for(observations.CHECKPOINT_SCHEMA)
        with patch.object(validator, "check_schema", wraps=validator.check_schema) as checks:
            for _ in range(20):
                self.assertEqual(observations.read_checkpoint(self.ws)["status"], "valid")
            self.write(progress_state="invented")
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
            self.write(evidence_paths=["proof.txt"])
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
            proof = self.ws / "proof.txt"
            proof.write_bytes(b"current evidence")
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "valid")
            proof.unlink()
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
        self.assertLessEqual(checks.call_count, 1)

    def test_live_polling_rereads_the_checkpoint_only_after_a_change(self):
        import os
        from do_math import file_io
        checkpoint = self.ws / "checkpoint.json"
        self.write(evidence_paths=["proof.txt"])
        # Fresh files cannot age their birth time; treat any past fingerprint as settled.
        with patch.object(file_io, "RACY_NS", 0), \
                patch.object(observations, "read_checkpoint", wraps=observations.read_checkpoint) as reads:
            self.assertEqual(self.t._changed_checkpoint()["status"], "invalid")
            # An invalid read is not remembered: its named evidence may appear later.
            (self.ws / "proof.txt").write_bytes(b"evidence")
            self.assertEqual(self.t._changed_checkpoint()["status"], "valid")
            self.assertEqual(self.t._changed_checkpoint()["status"], "unchanged")
            self.assertEqual(reads.call_count, 2)
            self.write(evidence_paths=["proof.txt"], next_step="later")
            later = checkpoint.stat().st_mtime_ns + 10 ** 9
            os.utime(checkpoint, ns=(later, later))
            self.assertEqual(self.t._changed_checkpoint()["status"], "valid")
            self.assertEqual(reads.call_count, 3)

    def test_duplicate_checkpoint_keys_are_invalid_live_and_at_final_capture(self):
        from do_math.submission import _captured_checkpoint
        self.write(current_claim="last valid", counters={"attempts": 1})
        prior, _ = observations.preserve_checkpoint(self.ws,
            artifact_prefix="runtime/artifacts/prior", max_bytes=100000)
        raw = (self.ws / "checkpoint.json").read_bytes()
        variants = [raw.replace(b'"current_claim": "last valid"',
                                b'"current_claim": "first", "current_claim": "last valid"'),
                    raw.replace(b'"attempts": 1', b'"attempts": 0, "attempts": 1')]
        for malformed in variants:
            (self.ws / "checkpoint.json").write_bytes(malformed)
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
            self.assertEqual(_captured_checkpoint({"checkpoint.json": malformed})["status"], "invalid")
            preserved, artifacts = observations.preserve_checkpoint(self.ws, previous=prior,
                artifact_prefix="runtime/artifacts/final", max_bytes=100000)
            self.assertEqual(preserved["sha256"], prior["sha256"])
            self.assertEqual(preserved["final_observation"]["checkpoint_status"], "invalid")
            self.assertEqual(artifacts, {})

    def test_checkpoint_rejects_numbers_outside_the_storage_value_domain(self):
        for changes in ({"iteration": 1.0}, {"counters": {"attempts": 2.0}},
                        {"iteration": 2 ** 53}):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
        self.write(iteration=1, counters={"attempts": 2})
        checkpoint = observations.read_checkpoint(self.ws)
        self.assertEqual(checkpoint["status"], "valid")
        stored = observations.persistent_record(checkpoint,
            artifact_ref="runtime/artifacts/fixture/checkpoint.json")
        self.assertEqual(stored["value"]["iteration"], 1)
        self.assertEqual(stored["value"]["counters"], {"attempts": 2})

    def test_checkpoint_requires_available_preserved_evidence_paths(self):
        self.write(evidence_paths=["proof.txt"])
        self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
        (self.ws / "proof.txt").write_text("actual evidence", encoding="utf-8")
        self.assertEqual(observations.read_checkpoint(self.ws)["status"], "valid")
        (self.ws / ".scratch").mkdir()
        (self.ws / ".scratch/proof.txt").write_text("disposable", encoding="utf-8")
        self.write(evidence_paths=[".scratch/proof.txt"])
        self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")

    def test_checkpoint_is_refused_through_a_workspace_reparse_point(self):
        # The checkpoint obeys the workspace path rule (context_store.safe_path) like every other
        # workspace file: a junction on the path is refused even when it resolves back inside.
        import os
        import subprocess
        real, link = self.ws / "real", self.ws / "link"
        real.mkdir()
        (real / "checkpoint.json").write_text(json.dumps({"current_claim": "c", "evidence_paths": [],
            "attempts": [], "remaining_work": [], "next_step": "n", "progress_state": "working"}), encoding="utf-8")
        if os.name == "nt":
            created = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(real)], capture_output=True)
            self.assertEqual(created.returncode, 0, created.stderr)
        else:
            link.symlink_to(real, target_is_directory=True)
        try:
            self.assertEqual(observations.read_checkpoint(real)["status"], "valid")
            refused = observations.read_checkpoint(link)
            self.assertEqual(refused["status"], "invalid")
            self.assertRegex(refused["error"], "reparse|symlink")
        finally:
            os.rmdir(link) if os.name == "nt" else link.unlink()  # Only the link, not its target.

    def test_invalid_partial_missing_checkpoint_and_stop_request(self):
        self.assertEqual(observations.read_checkpoint(self.ws)["status"], "missing")
        for raw in (b'\xff', b'{"current_claim":"partial"}'):
            (self.ws / "checkpoint.json").write_bytes(raw)
            self.assertEqual(observations.read_checkpoint(self.ws)["status"], "invalid")
        request = observations.request_checkpoint(self.ws, "stop", immediate=True, deadline="2026-01-01T00:00:00Z")
        self.assertIn("Do not start new research", request["instruction"])
        self.assertTrue((self.ws / ".control/stop-request.json").is_file())

    def test_transport_ping_and_idle_do_not_create_math_failure_or_review(self):
        self.clock.value = 200
        for event in ({"type": "tick"}, {"type": "ping"}, {"type": "transport_bytes_received", "bytes": 100}):
            rows = observe(self.t, event)
            self.assertFalse(any("review" in r["kind"] or r["kind"] == "self_check_due" for r in rows))

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
        tracker = observations.ObservationTracker("P", self.ws, {"observation_mode": "periodic", "observation_interval_seconds": 3}, clock=self.clock)
        tracker.schedule_review("RECHECK", at="2026-09-20T10:00:00Z", reason="inspect recovery", basis_ref="DISP-1")
        self.clock.value = 3
        with patch.object(tracker.time_port, "now", return_value="2026-09-20T10:00:00+00:00"):
            rows = observe(tracker, {"type": "tick"})
            self.assertEqual({r["kind"] for r in rows}, {"periodic_review_due", "explicit_review_due"})
            for row in rows:
                self.assert_persisted_notice(row)
            self.assertEqual(observe(tracker, {"type": "tick"}), [])

    def test_deadline_only_never_opens_recursive_review(self):
        tracker = observations.ObservationTracker("D", self.ws, {"observation_mode": "deadline_only", "observation_interval_seconds": 1,
            "tool_review_window_seconds": 1}, clock=self.clock)
        observe(tracker, {"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.clock.value = 100
        self.assertEqual(observe(tracker, {"type": "tick"}), [])
        with self.assertRaises(ValueError): tracker.schedule_review("R", at="2026-01-01T00:00:00Z", reason="x", basis_ref="X")

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
        for change in ({"execution_id": "OTHER"}, {"rule_revision": 99}, {"rule_results": []}, {"obligation_id": []}):
            response = {**self_check_response(obligation), **change}
            self.assertEqual(self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})["kind"], "self_check_rejected")
        response = self_check_response(obligation)
        self.assertIn("evidence_not_current", self.t.record_self_check_response(response, available_evidence_refs=set())["errors"])
        self.assertEqual(self.t.obligations[obligation["id"]]["status"], "open")

    def test_normal_defect_indeterminate_followups(self):
        self.write(counters={"attempts": 2})
        for status, expected in (("normal", "continue"), ("defect", "operational_review_due"), ("indeterminate", "operational_review_due")):
            with self.subTest(status=status):
                tracker = observations.ObservationTracker(status, self.ws, self.config, clock=self.clock)
                obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
                response = self_check_response(obligation, status, [] if status == "indeterminate" else None)
                result = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
                self.assertEqual(result["kind"], "self_check_received")
                self.assertEqual(result["followup"]["kind"], expected)

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
        from do_math.context_store import collect_outputs
        from do_math.submission import _workspace_checks
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
                issues, _ = _workspace_checks(context, self.ws, candidate=captured)
                self.assertEqual(issues, [], issues)
        self.assertEqual(self.t.rule_revision, 1)

    def test_tracker_records_leave_through_the_storage_check(self):
        """The tracker runs the storage gate's own checker on what ENGINE saves (이음새-정본.md §6)."""
        from do_math.state_contract import default_state_contract, validate_record
        obligation = self.due()
        response = {**self_check_response(obligation), "rule_proposal": {"current_revision": 0,
            "reason": "rename", "rules": [observation_rule(id="renamed", repeat_interval=2)]}}
        record = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        validate_record(default_state_contract().family("runtime", "self_check_responses").checker, record, "response")
        self.assertEqual(self.t.stored_obligations(), self.t.obligations)
        self.t.obligations[obligation["id"]]["bookkeeping"] = []
        with self.assertRaisesRegex(ValueError, "bookkeeping"):
            self.t.stored_obligations()

    def test_malformed_rule_proposal_does_not_reject_valid_self_check(self):
        obligation = self.due()
        response = {**self_check_response(obligation), "rule_proposal": {"current_revision": 0, "reason": "bad", "rules": [observation_rule(threshold=1.5)]}}
        result = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received")
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_rejected")

    def test_invalid_checkpoint_counters_do_not_partially_advance(self):
        self.write(counters={"attempts": 1, "branches": 5})
        observe(self.t, {"type": "tick"})
        self.write(counters={"attempts": 2, "branches": 4})
        rows = observe(self.t, {"type": "tick"})
        self.assertTrue(any(r["kind"] == "checkpoint_observation_rejected" for r in rows))
        self.assertEqual(self.t.counters, {"attempts": 1, "branches": 5})
        self.assertEqual(self.t.obligations, {})

    def test_provider_event_counters_are_not_observation_signals(self):
        rows = observe(self.t, {"type": "tick", "counters": {"attempts": 9}, "iterations": {"E": 9},
                               "active_duration_ms": 9000, "id": "provider-event"})
        self.assertEqual(self.t.counters, {})
        self.assertEqual(self.t.iterations, {})
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))

    def test_no_progress_limit_keeps_count_across_rule_replacement(self):
        tracker = observations.ObservationTracker("E", self.ws, {**self.config, "no_progress_limit": 2}, clock=self.clock)
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
        obligation = self.due()
        self.t.obligations[obligation['id']]['status'] = 'answered'
        observe(self.t, {"type": "item.completed", "item": {"type": "mcp_tool_call", "id": "SC-CALL",
            "server": "execution_control", "tool": "control_self_check",
            "arguments": {"self_check_id": obligation['id']}}}, evaluate=False)
        self.assertNotIn("SC-CALL", self.t.completed_call_ids)
        counted = self.t.checkpoint_count
        self.write(counters={"attempts": 2}, current_claim="self-check lineage")
        checkpoint = observations.read_checkpoint(self.ws)
        self.t.register_self_check_checkpoint(checkpoint["sha256"])
        observe(self.t, {"type": "tick"})
        self.assertEqual(self.t.checkpoint_count, counted)

    def test_reminder_is_once_and_does_not_replace_existing_feedback(self):
        self.assertTrue(observations.write_checkpoint_reminder(self.ws))
        self.assertFalse(observations.write_checkpoint_reminder(self.ws))
        value = json.loads((self.ws / ".control/observation-feedback.json").read_text(encoding="utf-8"))
        self.assertIn("current_claim", value["reason"])

    def test_missing_checkpoint_reminder_only_for_checkpointing_roles(self):
        tracker = observations.ObservationTracker("W", self.ws, {**self.config, "checkpoint_expected": True}, clock=self.clock)
        self.clock.value = 300
        self.assertTrue(any(r["kind"] == "checkpoint_reminder_due" for r in observe(tracker, {"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in observe(tracker, {"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in observe(self.t, {"type": "tick"})))

    def test_engine_answers_reminder_without_opening_model_review(self):
        from unittest.mock import create_autospec
        from research_fixtures import bare_engine
        workspace = self.ws / "runs" / "E" / "workspace"
        workspace.mkdir(parents=True)
        queued = []
        engine = bare_engine({"workspace": str(self.ws)}, {"status": "running", "executions": {"E": {}}})
        for name, value in (("_controls", None), ("_check_conversations", False), ("_save", None),
                            ("_unchanged", False), ("_publish_observation", None), ("_review_observation_source", None)):
            setattr(engine, name, create_autospec(getattr(engine, name), return_value=value))
        engine._enqueue = create_autospec(engine._enqueue, side_effect=lambda *a, **kw: queued.append((a, kw)))
        tracker = observations.ObservationTracker("E", workspace, {"observation_mode": "periodic", "observation_interval_seconds": 300,
                                                  "checkpoint_expected": True}, clock=self.clock)
        # This check targets ENGINE's mechanical reminder dispatch, not tracker
        # timing (covered separately above).
        tracker.observe = lambda event, **options: [{"kind": "checkpoint_reminder_due", "execution_id": "E"}]
        engine._observe_running("E", tracker, observation_batch(
            received_monotonic=self.clock(), stream_path=workspace / "stdout.jsonl"))
        self.assertTrue((workspace / ".control/observation-feedback.json").exists())
        self.assertEqual(queued, [])

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

    def test_feedback_producers_share_the_public_field_set(self):
        with self.assertRaisesRegex(ValueError, "private or unknown"):
            observations.worker_feedback({"kind": "x", "diagnostic": "private"})
        obligation = self.due()
        self.assertLessEqual(set(observations.self_check_feedback(obligation)), observations.WORKER_FEEDBACK_FIELDS)
        request = self.t.issue_self_check(obligation["id"])
        self.assertEqual(request, observations.self_check_request(self.t.obligations[obligation["id"]]))
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            self.t.record_delivery(obligation["id"], source_offset=-1)

    def test_explicit_null_repeat_is_not_a_positive_repeat_interval(self):
        with self.assertRaises(ValueError): observations.validate_rules([observation_rule(repeat_interval=None)])

    def test_documented_operator_table_is_the_operator_table(self):
        """「공통 실행」's operator table is the rule authors' copy of observations.OPERATORS."""
        text = (Path(__file__).resolve().parents[2] / 'references' / '공통-실행.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| `(\w+)` \| `(\w+)` \| `(\w+)`, `(\w+)` \|$', text, re.M)
        documented = {operator: {'subject_kind': kind, 'unit': unit, 'source': source}
                      for operator, kind, source, unit in rows}
        self.assertEqual(documented, observations.OPERATORS)


class SelfCheckControlBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws = Path(self.temp.name)
        self.clock = Clock()
    def tearDown(self): self.temp.cleanup()

    def tracker(self):
        return ObservationTracker("EX-1", self.ws, {"observation_rules": [observation_rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=self.clock)

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
        self.assertEqual(tracker.record_self_check_response(response, available_evidence_refs={"EV-1"}, receipt_id="CT-1")["kind"], "self_check_received")

    def test_unbound_or_different_control_request_cannot_acknowledge_response(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        observe(tracker, event)
        rejected = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertIn("control_request_unconfirmed", rejected["errors"])
        altered = deepcopy(request)
        altered["payload"]["response"]["next_method"] = "different"
        with self.assertRaises(ValueError): tracker.bind_control_request(altered, receipt_id="CT-2")

    def test_other_control_submit_and_wrong_server_remain_research_actions(self):
        for change in ("kind", "server"):
            tracker = self.tracker()
            _, _, event = self.submission(tracker)
            if change == "server": event["item"]["server"] = "untrusted"
            else:
                event["item"].update(tool="control_submit", arguments={"request_id": "P", "kind": "submission_preview", "payload": {}})
            self.assertTrue(any(r["kind"] == "self_check_missed" for r in observe(tracker, event)))

    def test_missing_profile_observability_contract_is_not_support(self):
        with self.assertRaises(ValueError): tracker_config(profile([]), initial_self_check_rules=[observation_rule()])

    def test_checkpoint_counter_rule_ignores_counters_from_another_source(self):
        import json
        rule = observation_rule(basis={"source": "checkpoint", "unit": "count"})
        binding = {"operator": rule["operator"], "subject_kind": rule["subject"]["kind"], **rule["basis"]}
        tracker = ObservationTracker("EX-1", self.ws, tracker_config(profile([binding]), initial_self_check_rules=[rule]), clock=self.clock)
        rows = observe(tracker, {"type": "tick", "counters": {"attempts": 2}})
        self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))
        (self.ws / "checkpoint.json").write_text(json.dumps({"current_claim": "c", "evidence_paths": [], "attempts": [],
            "remaining_work": [], "next_step": "n", "progress_state": "working", "counters": {"attempts": 2}}), encoding="utf-8")
        self.assertTrue(any(r["kind"] == "self_check_due" for r in observe(tracker, {"type": "tick"})))




    def test_receipt_cannot_be_reused_for_a_different_response_body(self):
        tracker = self.tracker()
        response, request, event = self.submission(tracker)
        observe(tracker, event)
        tracker.bind_control_request(request, receipt_id="CT-1")
        changed = {**response, "next_method": "not the submitted method"}
        self.assertIn("control_response_mismatch", tracker.record_self_check_response(changed,
                      available_evidence_refs={"EV-1"}, receipt_id="CT-1")["errors"])


class ExecutionObservationProfileTests(unittest.TestCase):
    def research_profile(self):
        profiles = build_profiles({**deepcopy(PROFILE_CONFIG), "tool_review_window_seconds": 60,
            "self_check_response_window_seconds": 5})["execution_profiles"].values()
        return next(profile for profile in profiles if profile["role"] == "research_work")

    def test_checkpoint_counter_name_is_bound_by_the_execution_not_the_profile(self):
        profile = self.research_profile()
        config = tracker_config(profile, initial_self_check_rules=[counter_rule()])
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "checkpoint.json").write_text(json.dumps({
                "current_claim": "working", "evidence_paths": [], "attempts": [],
                "remaining_work": [], "next_step": "continue", "progress_state": "working",
                "counters": {"attempts": 2},
            }), encoding="utf-8")
            emitted = observe(ObservationTracker("EX-local", workspace, config), {"type": "tick"})
        self.assertTrue(any(row["kind"] == "self_check_due" for row in emitted))

    def test_new_execution_gets_its_observation_interval_before_missing_signal_review(self):
        config = tracker_config(self.research_profile(), initial_self_check_rules=[counter_rule()])
        elapsed = [0.0]
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker("EX-local", Path(directory), config, clock=lambda: elapsed[0])
            for value in (0, config["observation_interval_seconds"] - .1):
                elapsed[0] = value
                emitted = observe(tracker, {"type": "tick"})
                self.assertFalse(any(row["kind"] == "observation_unavailable" for row in emitted))
                self.assertNotIn("attempts", tracker.counters)
            elapsed[0] = config["observation_interval_seconds"]
            emitted = observe(tracker, {"type": "tick"})
            unavailable = next(row for row in emitted if row["kind"] == "observation_unavailable")
            self.assertEqual(unavailable["rule_ids"], ["SC-attempts"])
            self.assertEqual(unavailable["followup"]["kind"], "operational_review_due")
            self.assertNotIn("attempts", tracker.counters)

    def test_shared_contract_rejects_forged_source_and_other_execution_subject(self):
        profile = self.research_profile()
        with self.assertRaisesRegex(ValueError, "basis"):
            tracker_config(profile, initial_self_check_rules=[counter_rule(source="invented")])
        other_execution = {"id": "SC-other", "operator": "checkpoint_count_gte",
            "subject": {"kind": "checkpoint", "id": "EX-other"},
            "basis": {"source": "checkpoint", "unit": "count"}, "threshold": 1,
            "required_evidence": ["checkpoint.json"]}
        config = tracker_config(profile, initial_self_check_rules=[other_execution])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "different execution"):
                ObservationTracker("EX-local", Path(directory), config)
            # A later rule replacement meets the same contract and keeps the admitted rules.
            admitted = counter_rule()
            tracker = ObservationTracker("EX-local", Path(directory), tracker_config(profile, initial_self_check_rules=[admitted]))
        self.assertEqual(tracker.rules, [admitted])
        replaced = tracker._replace_rules({"current_revision": 0, "reason": "change", "rules": [other_execution]})
        self.assertEqual(replaced["kind"], "observation_rules_rejected")
        self.assertEqual(tracker.rules, [admitted])

    def test_git_reload_preserves_the_sealed_shared_contract_before_tracker_admission(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.repository import ResearchRepository
        from record_fixtures import domain_governance, governance_import
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git_init(root)
            store = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
            saved_config = {**deepcopy(DEFAULT_CONFIG), "tool_review_window_seconds": 60,
                            "self_check_response_window_seconds": 5}
            from research_fixtures import current_state
            instance, runtime = current_state(
                {**domain_governance(), "config": saved_config, **build_profiles(saved_config)},
                {"status": "ready", "tasks": {}, "executions": {}, "queue": [], "history": []})
            head = store.initialize(instance, runtime)
            _, restored, _ = store.load(head)
            profile = next(item for item in restored["execution_profiles"].values() if item["role"] == "research_work")
            self.assertEqual(profile["observation"]["rule_bindings"], observation_rule_contract())
            self.assertEqual(profile_ref(profile)["id"], profile["id"])
            config = tracker_config(profile, initial_self_check_rules=[counter_rule()])
            workspace = root / "workspace"; workspace.mkdir()
            (workspace / "checkpoint.json").write_text(json.dumps({
                "current_claim": "working", "evidence_paths": [], "attempts": [],
                "remaining_work": [], "next_step": "continue", "progress_state": "working",
                "counters": {"attempts": 2},
            }), encoding="utf-8")
            self.assertTrue(any(row["kind"] == "self_check_due"
                                for row in observe(ObservationTracker("EX-local", workspace, config), {"type": "tick"})))


class ObservationRuleTests(unittest.TestCase):
    def test_rules_bind_operator_subject_unit_and_evidence(self):
        accepted = observation_rule(repeat_interval=2)
        self.assertEqual(validate_rules([accepted]), [accepted])
        for basis in ({"source": "x"}, {"source": "checkpoint", "unit": "milliseconds"}):
            with self.subTest(basis=basis), self.assertRaisesRegex(ValueError, "basis"):
                validate_rules([{**accepted, "basis": basis}])
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_rules([{**accepted, "operator": "tool_results_gte"}])
        with self.assertRaisesRegex(ValueError, "one-time"):
            validate_rules([observation_rule("tool_call_completed", "tool_call", "CALL-1", 2)])
        with self.assertRaisesRegex(ValueError, "nonempty"):
            validate_rules([])

    def test_rule_evaluation_preserves_multiple_boundaries_and_unknowns(self):
        rules = [observation_rule("counter_gte", "counter", "attempts", 2, repeat_interval=2),
                 observation_rule("tool_call_completed", "tool_call", "CALL-1", 1, id="R-2")]
        due = evaluate_rules(rules, {"counters": {"attempts": 5}, "completed_call_ids": ["CALL-1"]})
        self.assertEqual([("R-1", 4), ("R-2", 1)], [(row["rule_id"], row["boundary"]) for row in due])
        # Duplicate rule IDs are invalid; use an independent unknown rule to
        # prove that absence is not converted into a zero counter.
        unknown = observation_rule(subject_id="missing")
        self.assertEqual([], evaluate_rules([unknown], {"counters": {}}))

    def test_tracker_creates_self_check_and_call_specific_review_facts(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker("EX-1", Path(directory), {
                "self_check_revision": 3,
                "observation_rules": [observation_rule()], "self_check_response_window_seconds": 5,
                "tool_review_window_seconds": 60,
            }, clock=clock)
            write_checkpoint(directory, counters={"attempts": 2})
            due = observe(tracker, {"type": "tick"})
            obligation = next(row for row in due if row["kind"] == "self_check_due")
            self.assertEqual(3, obligation["rule_revision"])
            received = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual("self_check_received", received["kind"])
            feedback = self_check_feedback(obligation)
            self.assertEqual(obligation["id"], feedback["obligation_id"])
            self.assertNotIn("basis", feedback["due"][0])
            observe(tracker, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "CALL-1", "name": "Bash",
                "input": {"observation_review_window_seconds": 3}}]}})
            clock.value = 3
            self.assertFalse(any(row["kind"] == "tool_review_due" for row in observe(tracker, {"type": "tick"})))
            clock.value = 60
            review = observe(tracker, {"type": "tick"})
            self.assertEqual("CALL-1", next(row for row in review if row["kind"] == "tool_review_due")["call_id"])

    def tracker(self, workspace, clock, **extra):
        return ObservationTracker("EX-1", workspace, {"observation_rules": [observation_rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            **extra}, clock=clock)

    def test_three_reported_counterexamples(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            rejected = tracker.record_self_check_response(self_check_response(obligation, evidence=["unrelated"]), available_evidence_refs={"unrelated"})
            self.assertEqual(rejected["kind"], "self_check_rejected")
            observe(tracker, {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "C", "name": "Bash", "input": {"timeout": 1, "observation_review_window_seconds": 1}}]}})
            clock.value = 2
            self.assertFalse(any(r["kind"] == "tool_review_due" for r in observe(tracker, {"type": "tick"})))
        utc = observation_rule("wall_time_reached", "clock", "UTC", "2026-09-20T10:00:00Z", basis={"source": "clock", "unit": "UTC"})
        self.assertEqual(len(evaluate_rules(validate_rules([utc]), {"observed_at": "2026-09-20T10:00:00+00:00"})), 1)

    def test_response_deadline_is_current_and_rejection_reaches_worker(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            clock.value = 6
            rejected = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(rejected["kind"], "self_check_rejected")
            self.assertIn("response_deadline_passed", rejected["errors"])
            self.assertEqual(rejected["followup"]["kind"], "operational_review_due")

    def test_call_reported_at_a_safe_boundary_stops_holding_the_deadline(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            observe(tracker, {"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            self.assertEqual((obligation["deadline_offset_ms"], obligation["deadline_held_offset_ms"]), (5000, 0))
            clock.value = 9
            tracker.record_safe_boundary("CT-1", call_ids=["C"])
            self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 14000)
            clock.value = 14
            accepted = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(accepted["kind"], "self_check_received")

    def test_deadline_held_by_a_call_running_at_opening_passes_after_the_call_ends(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            observe(tracker, {"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            self.assertEqual(obligation["deadline_held_offset_ms"], 0)
            clock.value = 9
            observe(tracker, {"type": "item.completed", "item": {"id": "C", "type": "command_execution"}})
            self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 14000)
            clock.value = 15
            rejected = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(rejected["kind"], "self_check_rejected")
            self.assertIn("response_deadline_passed", rejected["errors"])

    def test_research_calls_before_the_response_hold_its_deadline_until_all_of_them_end(self):
        clock = Clock()
        start = lambda cid: observe(tracker, {"type": "item.started", "item": {"id": cid, "type": "command_execution"}})
        end = lambda cid: observe(tracker, {"type": "item.completed", "item": {"id": cid, "type": "command_execution"}})
        missed = lambda rows: any(r["kind"] == "self_check_missed" for r in rows)
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            held = tracker.obligations[obligation["id"]]
            self.assertEqual(held["deadline_offset_ms"], 5000)
            clock.value = 1
            start("A")
            clock.value = 3
            start("B")
            clock.value = 20
            self.assertFalse(missed(end("A")), "a nested call still running holds the deadline")
            clock.value = 30
            self.assertFalse(missed(end("B")))
            self.assertEqual(held["deadline_offset_ms"], 34000)
            self.assertNotIn("deadline_held_offset_ms", held)
            clock.value = 31
            start("C")
            clock.value = 40
            self.assertFalse(missed(end("C")))
            self.assertEqual(held["deadline_offset_ms"], 43000)
            clock.value = 43
            accepted = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(accepted["kind"], "self_check_received")

    def test_research_call_after_the_deadline_does_not_hold_it(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            write_checkpoint(directory, counters={"attempts": 2})
            next(r for r in observe(tracker, {"type": "tick"}) if r["kind"] == "self_check_due")
            clock.value = 6
            rows = observe(tracker, {"type": "item.started", "item": {"id": "late", "type": "command_execution"}})
            self.assertTrue(any(r.get("reason") == "response_deadline_passed" for r in rows))

    def test_integer_persistence_keeps_raw_adapter_payload_as_text(self):
        from do_math.canonical import canonical_json
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            clock.value = 0.125
            facts = observe(tracker, {"type": "result", "duration": 0.25})
            fact = next(r for r in facts if r["kind"] == "observation_fact")
            canonical_json(fact)
            self.assertEqual(fact["monotonic_offset_ms"], 125)
            self.assertEqual(json.loads(fact["event_json"])["duration"], .25)

    def test_rule_identity_change_does_not_reconsume_boundary(self):
        rules = [observation_rule()]
        first = evaluate_rules(rules, {"counters": {"attempts": 2}})
        self.assertIn("boundary_key", first[0])
        consumed = {first[0]["boundary_key"]: first[0]["boundary"]}
        self.assertEqual(evaluate_rules([observation_rule(id="RENAMED")], {"counters": {"attempts": 2}}, consumed_boundaries=consumed), [])

    def test_missing_checkpoint_counter_is_reported_not_zero_or_wall_time(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            clock.value = 100
            rows = observe(tracker, {"type": "tick"})
            unavailable = next(r for r in rows if r["kind"] == "observation_unavailable")
            self.assertEqual(unavailable["rule_ids"], ["R-1"])
            self.assertEqual(unavailable["followup"]["kind"], "operational_review_due")
            self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))

    def test_profile_admission_requires_frozen_windows(self):
        from do_math.observations import observation_rule_contract, tracker_config
        from do_math.execution_profiles import seal_profile, BOUNDARY
        body = {"role": "research_work", "actor_kind": "ai", "boundary": BOUNDARY,
                "ai": {"model": "test", "capacity_refs": ["CP-test"]}, "observation": {"mode": "event_driven", "settings": {},
                "rule_bindings": observation_rule_contract()}}
        with self.assertRaisesRegex(ValueError, "window|interval"):
            tracker_config(seal_profile(body), initial_self_check_rules=[observation_rule()])
        body["observation"]["settings"] = {"tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
                                            "observation_interval_seconds": 300}
        body["observation"]["rule_bindings"] = observation_rule_contract()
        frozen = tracker_config(seal_profile(body), initial_self_check_rules=[observation_rule()])
        self.assertEqual(frozen["tool_review_window_seconds"], 60)
        self.assertEqual(frozen["observation_profile_ref"]["revision"], 1)

    def test_indeterminate_operator_input_is_not_silently_skipped(self):
        with self.assertRaisesRegex(ValueError, "observation"):
            evaluate_rules([observation_rule()], {"counters": {"attempts": 2.5}})

    def test_checkpoint_record_requires_preserved_original_artifact(self):
        from do_math import observations
        from do_math.canonical import canonical_json
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "checkpoint.json").write_text(json.dumps({"current_claim": "c", "evidence_paths": [], "attempts": [],
                "remaining_work": [], "next_step": "n", "progress_state": "working"}), encoding="utf-8")
            checkpoint = {"kind": "checkpoint", **observations.read_checkpoint(workspace)}
            with self.assertRaisesRegex(ValueError, "artifact"):
                observations.persistent_record(checkpoint)
            preserved = observations.persistent_record(checkpoint, artifact_ref="ART-1")
            self.assertNotIn("raw", preserved)
            self.assertEqual(preserved["artifact_ref"], "ART-1")
            canonical_json(preserved)

    def test_maximum_interval_keeps_distinct_ids_for_every_due_rule(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker("EX-1", Path(directory), {
                "observation_rules": [observation_rule(id="@maximum_interval"), observation_rule(id="@maximum_interval:1")],
                "observation_interval_seconds": 10, "tool_review_window_seconds": 60,
                "self_check_response_window_seconds": 5}, clock=clock)
            clock.value = 10
            write_checkpoint(directory, counters={"attempts": 2})
            obligation = next(row for row in observe(tracker, {"type": "tick"})
                              if row["kind"] == "self_check_due")
            ids = [row["rule_id"] for row in obligation["due"]]
            self.assertEqual(len(ids), 3)
            self.assertEqual(len(set(ids)), 3)
            self.assertTrue({"@maximum_interval", "@maximum_interval:1"}.issubset(ids))
            received = tracker.record_self_check_response(self_check_response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(received["kind"], "self_check_received")

    def test_dispositions_are_validated_before_engine_application(self):
        disposition = {"kind": "resume", "basis_refs": ["OF-1", "SC-1"], "next_owner": "engine",
                       "reason": "checkpoint is complete", "checkpoint_ref": "CK-1", "scope": "remaining proof"}
        self.assertEqual(disposition, validate_disposition(disposition))
        self.assertEqual({"kind": "resume", "reason": "checkpoint is complete", "next_owner": "engine"}, worker_feedback(disposition))
        with self.assertRaisesRegex(ValueError, "Additional properties are not allowed"):
            validate_disposition({**disposition, "private_diagnostic": "do not leak"})


if __name__ == "__main__": unittest.main(verbosity=2)
