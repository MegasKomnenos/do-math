from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.lifecycle_engine import LifecycleEngineMixin


class ProbeBatchTests(unittest.TestCase):
    def setUp(self):
        class Harness(LifecycleEngineMixin):
            pass
        self.engine = Harness()
        config = deepcopy(DEFAULT_CONFIG)
        self.engine.instance = {"lifecycle": {"state": "initializing"}, **build_profiles(config)}
        self.profiles = [p for p in self.engine.instance["execution_profiles"].values() if p["actor_kind"] == "ai"][:2]

    def test_batch_preserves_each_profile_and_observed_capability_scope(self):
        class Adapter:
            def describe(self):
                return {"identity": {"host": "fixture"}, "verified": True,
                        "scope": "cli_command_surface_only", "supported": {"jsonl": True, "local_job": True}}
        with patch("do_math.initialization.adapter_for", return_value=Adapter()):
            self.engine._initialization_control({"operation": "probe", "profile_refs": [profile_ref(p) for p in self.profiles]}, "source")
        rows = list(self.engine.instance["capability_evidence"].values())
        self.assertEqual({row["execution_profile_ref"]["id"] for row in rows}, {p["id"] for p in self.profiles})
        self.assertTrue(all(row["capabilities"]["jsonl"]["status"] == "supported" for row in rows))
        self.assertTrue(all(row["capabilities"]["local_job"]["status"] == "unknown" for row in rows))

    def test_invalid_reference_is_rejected_before_probing_or_mutating_evidence(self):
        with patch("do_math.initialization.adapter_for") as adapter:
            with self.assertRaises(ValueError):
                self.engine._initialization_control({"operation": "probe", "profile_refs": [profile_ref(self.profiles[0]),
                    {"id": "missing", "revision": 1, "sha256": "a" * 64}]}, "source")
        adapter.assert_not_called()
        self.assertFalse(self.engine.instance.get("capability_evidence"))

    def test_failed_later_observation_does_not_publish_partial_evidence(self):
        class Adapter:
            def describe(self):
                return {"identity": {"host": "fixture"}}
        with patch("do_math.initialization.adapter_for", side_effect=[Adapter(), RuntimeError("probe failed")]):
            with self.assertRaisesRegex(RuntimeError, "probe failed"):
                self.engine._initialization_control({"operation": "probe", "profile_refs": [profile_ref(p) for p in self.profiles]}, "source")
        self.assertFalse(self.engine.instance.get("capability_evidence"))

    def test_active_probe_refreshes_observation_without_adopting_contract(self):
        self.engine.instance["lifecycle"] = {"state": "active", "adoption": {"config_sha256": "saved"}}
        before = deepcopy(self.engine.instance)
        class Adapter:
            def describe(self):
                return {"identity": {"host": "fixture"}, "verified": True,
                        "scope": "cli_command_surface_only", "supported": {"jsonl": True}}
        with patch("do_math.initialization.adapter_for", return_value=Adapter()):
            self.engine._initialization_control({"operation": "probe",
                "profile_ref": profile_ref(self.profiles[0])}, "source")
        self.assertTrue(self.engine.instance["capability_evidence"])
        self.assertEqual({k: v for k, v in self.engine.instance.items() if k != "capability_evidence"}, before)
        for operation in ("adopt", "governance"):
            with self.subTest(operation=operation), self.assertRaisesRegex(ValueError, "active contract"):
                self.engine._initialization_control({"operation": operation}, "source")


class ActiveProbePublicTests(unittest.TestCase):
    def setUp(self):
        from test_input_recovery import InputRecoveryPublicTests
        InputRecoveryPublicTests.setUp(self)

    def test_user_refreshes_exact_active_profile_and_other_authority_is_rejected(self):
        from do_math.engine import ResearchEngine, control
        engine = ResearchEngine(self.repo, self.identifier)
        self.assertEqual(engine.instance["lifecycle"]["state"], "active")
        before = deepcopy(engine.instance["lifecycle"])
        reference = deepcopy(engine.instance["role_profile_refs"]["maintenance"][0])
        config = {"change": {"kind": "initialization", "operation": "probe", "profile_ref": reference}}
        with self.assertRaisesRegex(ValueError, "operator controls are limited"):
            control(self.repo, self.identifier, "decision", config=config, origin="operator")
        request = control(self.repo, self.identifier, "decision", config=config)
        engine.process_controls()
        self.assertEqual(engine.control_result(request["request_id"])["effect"], "applied")
        self.assertEqual(engine.instance["lifecycle"], before)
        rows = list(engine.instance["capability_evidence"].values())
        self.assertTrue(any(row["execution_profile_ref"] == reference for row in rows))
        evidence = deepcopy(engine.instance["capability_evidence"])
        bad = deepcopy(config)
        bad["change"]["profile_ref"]["sha256"] = "0" * 64
        request = control(self.repo, self.identifier, "decision", config=bad)
        engine.process_controls()
        self.assertEqual(engine.control_result(request["request_id"])["effect"], "rejected")
        self.assertEqual(engine.instance["capability_evidence"], evidence)
        self.assertEqual(engine.instance["lifecycle"], before)
        _, stored, _ = engine.store.load()
        self.assertEqual(stored["capability_evidence"], evidence)
