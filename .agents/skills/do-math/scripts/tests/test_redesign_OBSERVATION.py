from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.execution_window import observation_window
from do_math.observations import ObservationTracker, evaluate_rules, self_check_feedback, validate_rules
from do_math.operational_dispositions import disposition_is_current, validate_disposition, worker_feedback


class Clock:
    def __init__(self): self.value = 0
    def __call__(self): return self.value


def rule(operator="counter_gte", subject_kind="counter", subject_id="attempts", threshold=2, **changes):
    value = {
        "id": "R-1", "operator": operator, "subject": {"kind": subject_kind, "id": subject_id},
        "basis": {"source": "execution_events", "unit": "count"}, "threshold": threshold,
        "required_evidence": ["EV-1"],
    }
    value.update(changes)
    return value


class ObservationRedesignTests(unittest.TestCase):
    def test_rules_bind_operator_subject_unit_and_evidence(self):
        accepted = rule(repeat_interval=2)
        self.assertEqual(validate_rules([accepted]), [accepted])
        with self.assertRaisesRegex(ValueError, "basis"):
            validate_rules([{**accepted, "basis": {"source": "x"}}])
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_rules([{**accepted, "operator": "tool_results_gte"}])
        with self.assertRaisesRegex(ValueError, "one-time"):
            validate_rules([rule("tool_call_completed", "tool_call", "CALL-1", 2)])
        with self.assertRaisesRegex(ValueError, "nonempty"):
            validate_rules([])

    def test_rule_evaluation_preserves_multiple_boundaries_and_unknowns(self):
        rules = [rule("counter_gte", "counter", "attempts", 2, repeat_interval=2),
                 rule("tool_call_completed", "tool_call", "CALL-1", 1, id="R-2")]
        due = evaluate_rules(rules, {"counters": {"attempts": 5}, "completed_call_ids": ["CALL-1"]})
        self.assertEqual([("R-1", 4), ("R-2", 1)], [(row["rule_id"], row["boundary"]) for row in due])
        # Duplicate rule IDs are invalid; use an independent unknown rule to
        # prove that absence is not converted into a zero counter.
        unknown = rule(subject_id="missing")
        self.assertEqual([], evaluate_rules([unknown], {"counters": {}}))

    def test_tracker_creates_self_check_and_call_specific_review_facts(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker("EX-1", Path(directory), {
                "observation_contract_version": 5, "self_check_revision": 3,
                "observation_rules": [rule()], "self_check_response_window_seconds": 5,
                "tool_review_window_seconds": 60,
            }, clock=clock)
            due = tracker.observe({"type": "tick", "counters": {"attempts": 2}})
            obligation = next(row for row in due if row["kind"] == "self_check_due")
            self.assertEqual(3, obligation["rule_revision"])
            received = tracker.record_self_check_response(self.response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual("self_check_received", received["kind"])
            feedback = self_check_feedback(obligation, [{"rule_id": "R-9", "reason": "rejected"}])
            self.assertEqual(obligation["id"], feedback["obligation_id"])
            self.assertNotIn("basis", feedback["due"][0])
            tracker.observe({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "CALL-1", "name": "Bash",
                "input": {"observation_review_window_seconds": 3}}]}})
            clock.value = 3
            self.assertFalse(any(row["kind"] == "tool_review_due" for row in tracker.observe({"type": "tick"})))
            clock.value = 60
            review = tracker.observe({"type": "tick"})
            self.assertEqual("CALL-1", next(row for row in review if row["kind"] == "tool_review_due")["call_id"])

    @staticmethod
    def response(obligation, status="normal", evidence=None):
        return {"obligation_id": obligation["id"], "execution_id": obligation["execution_id"],
                "rule_revision": obligation["rule_revision"], "progress": "progress",
                "attempts": ["checked actual artifact"], "next_method": "continue proof",
                "rule_results": [{"rule_id": row["rule_id"], "status": status,
                    "evidence_refs": evidence if evidence is not None else row["required_evidence"],
                    "missing_evidence_refs": row["required_evidence"] if status == "indeterminate" else [],
                    "reason": "artifact comparison"} for row in obligation["due"]]}

    def tracker(self, workspace, clock, **extra):
        return ObservationTracker("EX-1", workspace, {"observation_rules": [rule()],
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            **extra}, clock=clock)

    def test_three_reported_counterexamples(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": 2}}) if r["kind"] == "self_check_due")
            rejected = tracker.record_self_check_response(self.response(obligation, evidence=["unrelated"]), available_evidence_refs={"unrelated"})
            self.assertEqual(rejected["kind"], "self_check_rejected")
            tracker.observe({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "C", "name": "Bash", "input": {"timeout": 1, "observation_review_window_seconds": 1}}]}})
            clock.value = 2
            self.assertFalse(any(r["kind"] == "tool_review_due" for r in tracker.observe({"type": "tick"})))
        utc = rule("wall_time_reached", "clock", "UTC", "2026-09-20T10:00:00Z", basis={"source": "clock", "unit": "UTC"})
        self.assertEqual(len(evaluate_rules(validate_rules([utc]), {"observed_at": "2026-09-20T10:00:00+00:00"})), 1)

    def test_response_deadline_is_current_and_rejection_reaches_worker(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": 2}}) if r["kind"] == "self_check_due")
            clock.value = 6
            rejected = tracker.record_self_check_response(self.response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(rejected["kind"], "self_check_rejected")
            self.assertIn("response_deadline_passed", rejected["errors"])
            self.assertEqual(rejected["followup"]["kind"], "operational_review_due")

    def test_tool_wait_defers_deadline_until_confirmed_boundary(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            tracker.observe({"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
            obligation = next(r for r in tracker.observe({"type": "tick", "counters": {"attempts": 2}}) if r["kind"] == "self_check_due")
            self.assertIsNone(obligation["deadline_offset_ms"])
            clock.value = 9
            tracker.record_safe_boundary("CT-1", call_ids=["C"])
            self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 14000)
            clock.value = 14
            accepted = tracker.record_self_check_response(self.response(obligation), available_evidence_refs={"EV-1"})
            self.assertEqual(accepted["kind"], "self_check_received")

    def test_invalid_rules_feedback_preserves_previous_revision(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            tracker = self.tracker(workspace, clock)
            (workspace / "observation-rules.json").write_text('{"rules":[]}', encoding="utf-8")
            rows = tracker.observe({"type": "tick"})
            rejected = next(r for r in rows if r["kind"] == "observation_rules_rejected")
            self.assertEqual(tracker.rule_revision, 0)
            self.assertEqual(tracker.rules, [rule()])
            self.assertTrue(rejected["worker_feedback"]["reason"])
            self.assertEqual(rejected["worker_feedback"]["active_revision"], 0)

    def test_integer_persistence_keeps_raw_adapter_payload_as_text(self):
        from do_math.repository import canonical_json
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock)
            clock.value = 0.125
            facts = tracker.observe({"type": "result", "duration": 0.25})
            fact = next(r for r in facts if r["kind"] == "observation_fact")
            canonical_json(fact)
            self.assertEqual(fact["monotonic_offset_ms"], 125)
            self.assertEqual(json.loads(fact["event_json"])["duration"], .25)

    def test_rule_identity_change_does_not_reconsume_boundary(self):
        rules = [rule()]
        first = evaluate_rules(rules, {"counters": {"attempts": 2}})
        self.assertIn("boundary_key", first[0])
        consumed = {first[0]["boundary_key"]: first[0]["boundary"]}
        self.assertEqual(evaluate_rules([rule(id="RENAMED")], {"counters": {"attempts": 2}}, consumed_boundaries=consumed), [])

    def test_missing_active_measurement_is_reported_not_zero_or_wall_time(self):
        clock = Clock()
        with tempfile.TemporaryDirectory() as directory:
            tracker = self.tracker(Path(directory), clock, observation_rules=[rule("active_duration_gte", "execution", "EX-1", 1000,
                basis={"source": "adapter_active_intervals", "unit": "milliseconds"})])
            clock.value = 100
            rows = tracker.observe({"type": "tick"})
            unavailable = next(r for r in rows if r["kind"] == "observation_unavailable")
            self.assertEqual(unavailable["rule_ids"], ["R-1"])
            self.assertEqual(unavailable["followup"]["kind"], "operational_review_due")
            self.assertFalse(any(r["kind"] == "self_check_due" for r in rows))

    def test_profile_admission_requires_frozen_windows(self):
        from do_math.observations import observation_rule_contract, tracker_config
        from do_math.execution_profiles import seal_profile, BOUNDARY
        body = {"role": "research_work", "actor_kind": "ai", "budget_kind": "work", "boundary": BOUNDARY,
                "ai": {"model": "test"}, "observation": {"mode": "event_driven", "settings": {},
                "rule_bindings": observation_rule_contract()}}
        with self.assertRaisesRegex(ValueError, "window|interval"):
            tracker_config(seal_profile(body), initial_self_check_rules=[rule()])
        body["observation"]["settings"] = {"tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
                                            "observation_interval_seconds": 300}
        body["observation"]["rule_bindings"] = observation_rule_contract()
        frozen = tracker_config(seal_profile(body), initial_self_check_rules=[rule()])
        self.assertEqual(frozen["tool_review_window_seconds"], 60)
        self.assertEqual(frozen["observation_profile_ref"]["revision"], 1)

    def test_indeterminate_operator_input_is_not_silently_skipped(self):
        with self.assertRaisesRegex(ValueError, "observation"):
            evaluate_rules([rule()], {"counters": {"attempts": 2.5}})

    def test_checkpoint_record_requires_preserved_original_artifact(self):
        from do_math import observations
        from do_math.repository import canonical_json
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

    def test_dispositions_are_validated_before_engine_application(self):
        disposition = {"kind": "resume", "basis_refs": ["OF-1", "SC-1"], "next_owner": "engine",
                       "reason": "checkpoint is complete", "checkpoint_ref": "CK-1", "scope": "remaining proof"}
        self.assertEqual(disposition, validate_disposition(disposition))
        self.assertTrue(disposition_is_current(disposition, {"OF-1", "SC-1", "other"}))
        self.assertFalse(disposition_is_current(disposition, {"OF-1"}))
        self.assertEqual({"kind": "resume", "reason": "checkpoint is complete", "next_owner": "engine"}, worker_feedback(disposition))
        with self.assertRaisesRegex(ValueError, "fields"):
            validate_disposition({**disposition, "private_diagnostic": "do not leak"})

    def test_profile_window_has_no_global_fallback(self):
        self.assertEqual(15, observation_window({"tool_review_window_seconds": 15}, "tool_review_window_seconds"))
        with self.assertRaisesRegex(ValueError, "lacks"):
            observation_window({}, "tool_review_window_seconds")


if __name__ == "__main__":
    unittest.main(verbosity=2)
