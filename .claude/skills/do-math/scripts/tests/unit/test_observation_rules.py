"""Observation rules and the profile signal contract (``observations``, ``execution_profiles``, ``operational_dispositions``; layer 2).

A rule names an operator from the one operator table (``observations.OPERATORS``),
its subject, the operator's own source and unit, and a threshold. A task's
rules name ``$execution`` and are bound to one execution when it starts. A
profile seals the signal kinds (``rule_bindings``) and the observation windows
a tracker admits. The repository test runs the real ``ResearchRepository`` on
the in-process Git fake.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
import unittest

from do_math import observations
from do_math.execution_profiles import BOUNDARY, build_profiles, profile_ref, seal_profile
from do_math.observations import (ObservationTracker, evaluate_rules, observation_rule_contract, tracker_config,
                                  validate_rules)
from do_math.operational_dispositions import validate_disposition, worker_feedback
from provider_fixtures import PROFILE_CONFIG
from research_fixtures import observation_rule, observe
from support.fakes.clock import FakeClock

SKILL = Path(__file__).resolve().parents[3]


def profile(bindings):
    return seal_profile({"role": "research_work", "actor_kind": "ai", "boundary": BOUNDARY,
        "ai": {"model": "test", "capacity_refs": ["CP-test"]}, "observation": {"mode": "event_driven", "settings": {
            "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
            "observation_interval_seconds": 300}, "rule_bindings": bindings}})


def counter_rule(*, source="checkpoint"):
    return observation_rule(id="SC-attempts", basis={"source": source, "unit": "count"},
                            required_evidence=["checkpoint.json"])


def write_counter_checkpoint(workspace):
    (workspace / "checkpoint.json").write_text(json.dumps({
        "current_claim": "working", "evidence_paths": [], "attempts": [],
        "remaining_work": [], "next_step": "continue", "progress_state": "working",
        "counters": {"attempts": 2},
    }), encoding="utf-8")


class RuleTests(unittest.TestCase):
    def test_rules_bind_operator_subject_unit_and_evidence(self):
        accepted = observation_rule(repeat_interval=2)
        self.assertEqual(validate_rules([accepted]), [accepted])
        for basis in ({"source": "x"}, {"source": "checkpoint", "unit": "milliseconds"}):
            with self.subTest(basis=basis), self.assertRaisesRegex(
                    ValueError, "rule basis of counter_gte must be source checkpoint in count"):
                validate_rules([{**accepted, "basis": basis}])
        with self.assertRaisesRegex(ValueError, "unsupported observation operator"):
            validate_rules([{**accepted, "operator": "tool_results_gte"}])
        with self.assertRaisesRegex(ValueError, "tool_call_completed is a one-time recorded event"):
            validate_rules([observation_rule("tool_call_completed", "tool_call", "CALL-1", 2)])
        with self.assertRaisesRegex(ValueError, "observation rules must be a nonempty list"):
            validate_rules([])

    def test_explicit_null_repeat_is_not_a_positive_repeat_interval(self):
        with self.assertRaisesRegex(ValueError, "repeat_interval must be a positive integer"):
            validate_rules([observation_rule(repeat_interval=None)])

    def test_rule_evaluation_preserves_multiple_boundaries_and_unknowns(self):
        rules = [observation_rule("counter_gte", "counter", "attempts", 2, repeat_interval=2),
                 observation_rule("tool_call_completed", "tool_call", "CALL-1", 1, id="R-2")]
        due = evaluate_rules(rules, {"counters": {"attempts": 5}, "completed_call_ids": ["CALL-1"]})
        self.assertEqual([("R-1", 4), ("R-2", 1)], [(row["rule_id"], row["boundary"]) for row in due])
        # Duplicate rule IDs are invalid; use an independent unknown rule to
        # prove that absence is not converted into a zero counter.
        unknown = observation_rule(subject_id="missing")
        self.assertEqual([], evaluate_rules([unknown], {"counters": {}}))

    def test_rule_identity_change_does_not_reconsume_boundary(self):
        rules = [observation_rule()]
        first = evaluate_rules(rules, {"counters": {"attempts": 2}})
        self.assertIn("boundary_key", first[0])
        consumed = {first[0]["boundary_key"]: first[0]["boundary"]}
        self.assertEqual(evaluate_rules([observation_rule(id="RENAMED")], {"counters": {"attempts": 2}},
                                        consumed_boundaries=consumed), [])

    def test_indeterminate_operator_input_is_not_silently_skipped(self):
        with self.assertRaisesRegex(ValueError, "invalid observation value for R-1"):
            evaluate_rules([observation_rule()], {"counters": {"attempts": 2.5}})

    def test_a_wall_time_rule_is_due_at_exactly_its_threshold(self):
        utc = observation_rule("wall_time_reached", "clock", "UTC", "2026-09-20T10:00:00Z",
                               basis={"source": "clock", "unit": "UTC"})
        due = evaluate_rules(validate_rules([utc]), {"observed_at": "2026-09-20T10:00:00+00:00"})
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["rule_id"], "R-1")

    def test_documented_operator_table_is_the_operator_table(self):
        """「공통 실행」's operator table is the rule authors' copy of observations.OPERATORS."""
        text = (SKILL / 'references' / '공통-실행.md').read_text(encoding='utf-8')
        rows = re.findall(r'^\| `(\w+)` \| `(\w+)` \| `(\w+)`, `(\w+)` \|$', text, re.M)
        documented = {operator: {'subject_kind': kind, 'unit': unit, 'source': source}
                      for operator, kind, source, unit in rows}
        self.assertEqual(documented, observations.OPERATORS)


class ProfileContractTests(unittest.TestCase):
    def research_profile(self):
        profiles = build_profiles({**deepcopy(PROFILE_CONFIG), "tool_review_window_seconds": 60,
            "self_check_response_window_seconds": 5})["execution_profiles"].values()
        return next(profile for profile in profiles if profile["role"] == "research_work")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def test_missing_profile_observability_contract_is_not_support(self):
        with self.assertRaisesRegex(ValueError, "profile lacks observation rule bindings"):
            tracker_config(profile([]), initial_self_check_rules=[observation_rule()])

    def test_profile_admission_requires_frozen_windows(self):
        body = {"role": "research_work", "actor_kind": "ai", "boundary": BOUNDARY,
                "ai": {"model": "test", "capacity_refs": ["CP-test"]}, "observation": {"mode": "event_driven", "settings": {},
                "rule_bindings": observation_rule_contract()}}
        with self.assertRaisesRegex(ValueError, "window|interval"):
            tracker_config(seal_profile(body), initial_self_check_rules=[observation_rule()])
        body["observation"]["settings"] = {"tool_review_window_seconds": 60, "self_check_response_window_seconds": 5,
                                           "observation_interval_seconds": 300}
        frozen = tracker_config(seal_profile(body), initial_self_check_rules=[observation_rule()])
        self.assertEqual(frozen["tool_review_window_seconds"], 60)
        self.assertEqual(frozen["observation_profile_ref"]["revision"], 1)

    def test_checkpoint_counter_name_is_bound_by_the_execution_not_the_profile(self):
        config = tracker_config(self.research_profile(), initial_self_check_rules=[counter_rule()])
        write_counter_checkpoint(self.directory)
        emitted = observe(ObservationTracker("EX-local", self.directory, config), {"type": "tick"})
        self.assertTrue(any(row["kind"] == "self_check_due" for row in emitted))

    def test_new_execution_gets_its_observation_interval_before_missing_signal_review(self):
        config = tracker_config(self.research_profile(), initial_self_check_rules=[counter_rule()])
        elapsed = [0.0]
        tracker = ObservationTracker("EX-local", self.directory, config, clock=lambda: elapsed[0])
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
        with self.assertRaisesRegex(ValueError, "different execution"):
            ObservationTracker("EX-local", self.directory, config)
        # A later rule replacement meets the same contract and keeps the admitted rules.
        admitted = counter_rule()
        tracker = ObservationTracker("EX-local", self.directory, tracker_config(profile, initial_self_check_rules=[admitted]))
        self.assertEqual(tracker.rules, [admitted])
        replaced = tracker._replace_rules({"current_revision": 0, "reason": "change", "rules": [other_execution]})
        self.assertEqual(replaced["kind"], "observation_rules_rejected")
        self.assertEqual(tracker.rules, [admitted])

    def test_git_reload_preserves_the_sealed_shared_contract_before_tracker_admission(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.repository import ResearchRepository
        from record_fixtures import domain_governance
        from research_fixtures import current_state
        from support.fakes.git_backend import make_fake, make_repository
        clock = FakeClock()
        store = ResearchRepository(make_repository(self.directory / "repository"), "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV",
                                   backend=make_fake(), clock=clock)
        saved_config = {**deepcopy(DEFAULT_CONFIG), "tool_review_window_seconds": 60,
                        "self_check_response_window_seconds": 5}
        instance, runtime = current_state(
            {**domain_governance(), "config": saved_config, **build_profiles(saved_config)},
            {"status": "ready", "tasks": {}, "executions": {}, "queue": [], "history": []})
        head = store.initialize(instance, runtime)
        _, restored, _ = store.load(head)
        profile = next(item for item in restored["execution_profiles"].values() if item["role"] == "research_work")
        self.assertEqual(profile["observation"]["rule_bindings"], observation_rule_contract())
        self.assertEqual(profile_ref(profile)["id"], profile["id"])
        config = tracker_config(profile, initial_self_check_rules=[counter_rule()])
        workspace = self.directory / "workspace"
        workspace.mkdir()
        write_counter_checkpoint(workspace)
        self.assertTrue(any(row["kind"] == "self_check_due"
                            for row in observe(ObservationTracker("EX-local", workspace, config),
                                               {"type": "tick"})))


class DispositionTests(unittest.TestCase):
    def test_dispositions_are_validated_before_engine_application(self):
        disposition = {"kind": "resume", "basis_refs": ["OF-1", "SC-1"], "next_owner": "engine",
                       "reason": "checkpoint is complete", "checkpoint_ref": "CK-1", "scope": "remaining proof"}
        self.assertEqual(disposition, validate_disposition(disposition))
        self.assertEqual({"kind": "resume", "reason": "checkpoint is complete", "next_owner": "engine"},
                         worker_feedback(disposition))
        with self.assertRaisesRegex(ValueError, "Additional properties are not allowed"):
            validate_disposition({**disposition, "private_diagnostic": "do not leak"})


if __name__ == "__main__":
    unittest.main()
