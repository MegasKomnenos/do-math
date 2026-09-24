from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import observations
import test_redesign_OBSERVATION as helpers
Clock, rule = helpers.Clock, helpers.rule
response_for = helpers.ObservationRedesignTests.response


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws, self.clock = Path(self.temp.name), Clock()
        self.config = {"observation_rules": [rule(repeat_interval=2)], "self_check_response_window_seconds": 5,
                       "tool_review_window_seconds": 60, "observation_interval_seconds": 300}
        self.t = observations.ObservationTracker("E", self.ws, self.config, clock=self.clock)

    def tearDown(self): self.temp.cleanup()

    def assert_persisted_notice(self, record):
        import jsonschema
        from do_math.state_contract import StateContract
        schema = StateContract.default().family('runtime', 'observations').schema
        jsonschema.validate({record['execution_id']: observations.persistent_record(record)}, schema)

    def write(self, **changes):
        value = {"current_claim": "c", "evidence_paths": [], "attempts": [], "remaining_work": [],
                 "next_step": "n", "progress_state": "working", **changes}
        (self.ws / "checkpoint.json").write_text(json.dumps(value), encoding="utf-8")

    def due(self, **event):
        return next(r for r in self.t.observe({"type": "tick", "counters": {"attempts": 2}, **event}) if r["kind"] == "self_check_due")

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
            rows = self.t.observe(event)
            self.assertFalse(any("review" in r["kind"] or r["kind"] == "self_check_due" for r in rows))

    def test_frozen_window_ignores_worker_timeout_and_mutated_input_config(self):
        self.config.update(tool_review_window_seconds=1, observation_mode="periodic")
        self.t.observe({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "C", "name": "Bash",
            "input": {"timeout": 1, "observation_review_window_seconds": 1}}]}})
        self.clock.value = 2
        self.assertEqual(self.t.observe({"type": "tick"}), [])
        self.clock.value = 60
        reviews = [r for r in self.t.observe({"type": "tick"}) if r["kind"] == "tool_review_due"]
        self.assertEqual([r["window_ms"] for r in reviews], [60000])
        self.assert_persisted_notice(reviews[0])
        self.assertEqual(self.t.observe({"type": "tick"}), [])

    def test_adapter_completion_matches_exact_call_and_duplicate_start_cannot_delay(self):
        self.t.observe({"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.clock.value = 50
        self.t.observe({"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.t.observe({"type": "item.completed", "item": {"type": "command_execution", "id": "OTHER"}})
        self.clock.value = 60
        self.assertEqual([r["call_id"] for r in self.t.observe({"type": "tick"}) if r["kind"] == "tool_review_due"], ["C"])
        self.t.observe({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "C", "content": "done"}]}})
        self.assertEqual(self.t.completed_call_ids, {"C", "OTHER"})
        self.assertEqual(self.t.pending_tools, {})

    def test_periodic_and_explicit_reviews_have_independent_bases(self):
        tracker = observations.ObservationTracker("P", self.ws, {"observation_mode": "periodic", "observation_interval_seconds": 3}, clock=self.clock)
        tracker.schedule_review("RECHECK", at="2026-09-20T10:00:00Z", reason="inspect recovery", basis_ref="DISP-1")
        self.clock.value = 3
        with patch.object(observations, "utc_now", return_value="2026-09-20T10:00:00+00:00"):
            rows = tracker.observe({"type": "tick"})
            self.assertEqual({r["kind"] for r in rows}, {"periodic_review_due", "explicit_review_due"})
            for row in rows:
                self.assert_persisted_notice(row)
            self.assertEqual(tracker.observe({"type": "tick"}), [])

    def test_deadline_only_never_opens_recursive_review(self):
        tracker = observations.ObservationTracker("D", self.ws, {"observation_mode": "deadline_only", "observation_interval_seconds": 1,
            "tool_review_window_seconds": 1}, clock=self.clock)
        tracker.observe({"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        self.clock.value = 100
        self.assertEqual(tracker.observe({"type": "tick"}), [])
        with self.assertRaises(ValueError): tracker.schedule_review("R", at="2026-01-01T00:00:00Z", reason="x", basis_ref="X")

    def test_maximum_interval_opens_self_check_and_valid_response_reanchors(self):
        self.clock.value = 300
        rows = self.t.observe({"type": "tick"})
        for row in rows:
            if row['kind'] == 'observation_unavailable':
                self.assert_persisted_notice(row)
        obligation = next(r for r in rows if r["kind"] == "self_check_due")
        self.assertEqual(obligation["due"][0]["rule_id"], "@maximum_interval")
        self.assertEqual(self.t.observe({"type": "tick"}), [])
        self.clock.value = 301
        result = self.t.record_self_check_response(response_for(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(result["next_self_check_offset_ms"], 601000)
        repeated = self.t.record_self_check_response(response_for(obligation), available_evidence_refs={"EV-1"})
        self.assertEqual(repeated["kind"], "self_check_rejected")
        self.assertEqual(self.t.next_self_check_offset_ms, 601000)

    def test_missed_self_check_notification_matches_persisted_contract(self):
        obligation = self.due()
        self.clock.value = 6
        notice = next(row for row in self.t.observe({'type': 'tick'}) if row['kind'] == 'self_check_missed')
        self.assertEqual(notice['obligation_id'], obligation['id'])
        self.assert_persisted_notice(notice)

    def test_response_coverage_identity_revision_and_current_evidence(self):
        obligation = self.due()
        for change in ({"execution_id": "OTHER"}, {"rule_revision": 99}, {"rule_results": []}, {"obligation_id": []}):
            response = {**response_for(obligation), **change}
            self.assertEqual(self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})["kind"], "self_check_rejected")
        response = response_for(obligation)
        self.assertIn("evidence_not_current", self.t.record_self_check_response(response, available_evidence_refs=set())["errors"])
        self.assertEqual(self.t.obligations[obligation["id"]]["status"], "open")

    def test_normal_defect_indeterminate_followups(self):
        for status, expected in (("normal", "continue"), ("defect", "operational_review_due"), ("indeterminate", "operational_review_due")):
            with self.subTest(status=status):
                tracker = observations.ObservationTracker(status, self.ws, self.config, clock=self.clock)
                obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": 2}}) if r["kind"] == "self_check_due")
                response = response_for(obligation, status, [] if status == "indeterminate" else None)
                result = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
                self.assertEqual(result["kind"], "self_check_received")
                self.assertEqual(result["followup"]["kind"], expected)

    def test_rule_only_file_cannot_reanchor_or_replace_and_feedback_is_delivered(self):
        proposal = {"current_revision": 0, "reason": "rename", "rules": [rule(id="R-new")]}
        (self.ws / "observation-rules.json").write_text(json.dumps(proposal), encoding="utf-8")
        rejected = next(r for r in self.t.observe({"type": "tick"}) if r["kind"] == "observation_rules_rejected")
        self.assertEqual(self.t.rule_revision, 0)
        self.assertEqual(self.t.next_self_check_offset_ms, 300000)
        observations.publish_worker_feedback(self.ws, rejected["worker_feedback"])
        self.assertTrue(json.loads((self.ws / ".control/observation-feedback.json").read_text(encoding="utf-8"))["previous_rules_preserved"])

    def test_valid_response_accepts_rules_but_bad_proposal_keeps_previous(self):
        obligation = self.due()
        response = response_for(obligation)
        response["rule_proposal"] = {"current_revision": 99, "reason": "stale", "rules": [rule(id="renamed")]}
        result = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received")
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_rejected")
        self.assertEqual(self.t.rule_revision, 0)

    def test_malformed_rule_proposal_does_not_reject_valid_self_check(self):
        obligation = self.due()
        response = {**response_for(obligation), "rule_proposal": {"current_revision": 0, "reason": "bad", "rules": [rule(threshold=1.5)]}}
        result = self.t.record_self_check_response(response, available_evidence_refs={"EV-1"})
        self.assertEqual(result["kind"], "self_check_received")
        self.assertEqual(result["rule_update"]["kind"], "observation_rules_rejected")

    def test_invalid_observation_does_not_partially_advance_counters(self):
        self.t.observe({"type": "tick", "counters": {"attempts": 2}, "iterations": {"E": -1}})
        self.assertNotIn("attempts", self.t.counters)
        self.assertEqual(self.t.obligations, {})

    def test_no_progress_limit_keeps_count_across_rule_replacement(self):
        tracker = observations.ObservationTracker("E", self.ws, {**self.config, "no_progress_limit": 2}, clock=self.clock)
        for count in (2, 4):
            obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": count}}) if r["kind"] == "self_check_due")
            response = {**response_for(obligation), "progress": "no_progress"}
            if count == 2:
                response["rule_proposal"] = {"current_revision": 0, "reason": "rename", "rules": [rule(id="R-new", repeat_interval=2)]}
            result = tracker.record_self_check_response(response, available_evidence_refs={"EV-1"})
            self.assertEqual(result["no_progress_count"], count // 2)
        self.assertEqual(result["followup"]["trigger"], "repeated_no_progress")
        tracker.acknowledge_review(observation_refs=[result["id"]])
        self.assertEqual(tracker.no_progress_count, 0)

    def test_actual_checkpoint_counters_and_iterations_repeat_without_recounting_bytes(self):
        self.write(counters={"attempts": 2}, iteration=3)
        self.assertTrue(any(r["kind"] == "self_check_due" for r in self.t.observe({"type": "tick"})))
        self.assertEqual(self.t.iterations, {"E": 3})
        self.assertEqual(self.t.observe({"type": "tick"}), [])
        self.write(counters={"attempts": 4}, iteration=4)
        self.assertTrue(any(r["kind"] == "self_check_due" for r in self.t.observe({"type": "tick"})))
        self.write(counters={"attempts": 2}, iteration=3)
        self.t.observe({"type": "tick"})
        self.assertEqual(self.t.checkpoint_count, 2)

    def test_active_duration_counts_only_observed_progress_intervals(self):
        self.assertIsNone(self.t._snapshot(0)["active_duration_ms"])
        self.t.observe({"type": "research_activity_started"})
        self.clock.value = 2.5
        self.t.observe({"type": "research_activity_finished"})
        self.clock.value = 20
        self.assertEqual(self.t._snapshot(20)["active_duration_ms"], 2500)
        self.t.observe({"type": "research_activity_started"})
        self.clock.value = 21
        self.t.set_execution_status("stopping")
        self.assertEqual(self.t._snapshot(21)["active_duration_ms"], 3500)
        self.assertEqual(self.t.observe({"type": "tick"}), [])

    def test_self_check_calls_and_checkpoints_do_not_trigger_themselves(self):
        self.t.register_self_check_calls(["SC-CALL"])
        self.t.observe({"type": "item.completed", "item": {"type": "command_execution", "id": "SC-CALL"}})
        self.assertNotIn("SC-CALL", self.t.completed_call_ids)
        self.write()
        checkpoint = observations.read_checkpoint(self.ws)
        self.t.register_self_check_checkpoint(checkpoint["sha256"])
        self.t.observe({"type": "tick"})
        self.assertEqual(self.t.checkpoint_count, 0)

    def test_reminder_is_once_and_does_not_replace_existing_feedback(self):
        self.assertTrue(observations.write_checkpoint_reminder(self.ws))
        self.assertFalse(observations.write_checkpoint_reminder(self.ws))
        value = json.loads((self.ws / ".control/observation-feedback.json").read_text(encoding="utf-8"))
        self.assertIn("current_claim", value["reason"])

    def test_missing_checkpoint_reminder_only_for_checkpointing_roles(self):
        tracker = observations.ObservationTracker("W", self.ws, {**self.config, "checkpoint_expected": True}, clock=self.clock)
        self.clock.value = 300
        self.assertTrue(any(r["kind"] == "checkpoint_reminder_due" for r in tracker.observe({"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in tracker.observe({"type": "tick"})))
        self.assertFalse(any(r["kind"] == "checkpoint_reminder_due" for r in self.t.observe({"type": "tick"})))

    def test_engine_answers_reminder_without_opening_model_review(self):
        from types import SimpleNamespace
        from do_math.engine import ResearchEngine
        workspace = self.ws / "runs" / "E" / "workspace"
        workspace.mkdir(parents=True)
        queued = []
        fake = SimpleNamespace(_controls=lambda: None, _check_conversations=lambda: False, _save=lambda *a: None,
            _inline_reviewing=False, instance={"workspace": str(self.ws)}, runtime={"status": "running"}, _trackers={},
            _review_observation_source=lambda execution_id, event: None,
            _run_inline_review=lambda *a: queued.append(a))
        tracker = observations.ObservationTracker("E", workspace, {"observation_mode": "periodic", "observation_interval_seconds": 300,
                                                  "checkpoint_expected": True}, clock=self.clock)
        # This check targets ENGINE's mechanical reminder dispatch, not tracker
        # timing (covered separately above).
        tracker.observe = lambda event: [{"kind": "checkpoint_reminder_due", "execution_id": "E"}]
        ResearchEngine._observe_running(fake, "E", tracker, {"type": "tick"})
        self.assertTrue((workspace / ".control/observation-feedback.json").exists())
        self.assertEqual(queued, [])

    def test_response_without_confirmed_safe_boundary_is_not_accepted(self):
        self.t.observe({"type": "item.started", "item": {"type": "command_execution", "id": "C"}})
        obligation = self.due()
        result = self.t.record_self_check_response(response_for(obligation), available_evidence_refs={"EV-1"})
        self.assertIn("response_boundary_unconfirmed", result["errors"])

    def test_explicit_null_repeat_is_not_a_positive_repeat_interval(self):
        with self.assertRaises(ValueError): observations.validate_rules([rule(repeat_interval=None)])


if __name__ == "__main__": unittest.main(verbosity=2)
