"""Execution-local observation rules use the sealed profile's shared signal contract."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.execution_profiles import build_profiles, profile_ref
from do_math.observations import ObservationTracker, observation_rule_contract, tracker_config
from test_redesign_PROFILES import CONFIG


def counter_rule(*, execution_id="EX-local", source="checkpoint"):
    return {
        "id": "SC-attempts", "operator": "counter_gte",
        "subject": {"kind": "counter", "id": "attempts"},
        "basis": {"source": source, "unit": "count"}, "threshold": 2,
        "required_evidence": ["checkpoint.json"],
    }


class ExecutionObservationProfileTests(unittest.TestCase):
    def research_profile(self):
        profiles = build_profiles({**deepcopy(CONFIG), "tool_review_window_seconds": 60,
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
            emitted = ObservationTracker("EX-local", workspace, config).observe({"type": "tick"})
        self.assertTrue(any(row["kind"] == "self_check_due" for row in emitted))

    def test_new_execution_gets_its_observation_interval_before_missing_signal_review(self):
        config = tracker_config(self.research_profile(), initial_self_check_rules=[counter_rule()])
        elapsed = [0.0]
        with tempfile.TemporaryDirectory() as directory:
            tracker = ObservationTracker("EX-local", Path(directory), config, clock=lambda: elapsed[0])
            for value in (0, config["observation_interval_seconds"] - .1):
                elapsed[0] = value
                emitted = tracker.observe({"type": "tick"})
                self.assertFalse(any(row["kind"] == "observation_unavailable" for row in emitted))
                self.assertNotIn("attempts", tracker.counters)
            elapsed[0] = config["observation_interval_seconds"]
            emitted = tracker.observe({"type": "tick"})
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

    def test_git_reload_preserves_the_sealed_shared_contract_before_tracker_admission(self):
        import subprocess
        from do_math.engine import DEFAULT_CONFIG
        from do_math.repository import ResearchRepository
        from test_redesign_GOVERNANCE import DomainGovernanceTests
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            store = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
            saved_config = {**deepcopy(DEFAULT_CONFIG), "tool_review_window_seconds": 60,
                            "self_check_response_window_seconds": 5}
            from research_fixtures import current_state
            instance, runtime = current_state(
                {**DomainGovernanceTests().initial(), "config": saved_config, **build_profiles(saved_config)},
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
                                for row in ObservationTracker("EX-local", workspace, config).observe({"type": "tick"})))


if __name__ == "__main__":
    unittest.main()
