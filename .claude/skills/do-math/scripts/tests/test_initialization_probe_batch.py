from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from research_fixtures import FixtureAdapter, bare_engine


class ProbeBatchTests(unittest.TestCase):
    def setUp(self):
        config = deepcopy(DEFAULT_CONFIG)
        self.engine = bare_engine({"lifecycle": {"state": "initializing"}, "config": config, **build_profiles(config)})
        self.profiles = [p for p in self.engine.instance["execution_profiles"].values() if p["actor_kind"] == "ai"][:2]

    def test_activation_batch_reuses_only_the_current_provider_observation(self):
        from do_math.initialization import _capability_batch_requirements, capability_requirements
        from datetime import datetime, timezone
        references = [profile_ref(p) for p in self.profiles]
        identity = {'host':'fixture'}
        adapter = Mock()
        adapter.describe.return_value = {'identity':identity, 'verified':True,
            'scope':'cli_command_surface_only',
            'supported':{'jsonl':True, 'model':True, 'structured_output':True}}
        adapter.capability_identity.return_value = identity
        with patch('do_math.initialization.adapter_for', return_value=adapter):
            self.engine._initialization_control({'operation':'probe','profile_refs':references}, 'source')
            at = datetime.now(timezone.utc).isoformat()
            expected = [capability_requirements(self.engine.instance, ref, current_identity=identity, at=at)
                        for ref in references]
            actual = list(_capability_batch_requirements(self.engine.instance, references, at=at))
            self.assertEqual(actual, expected)
            self.assertEqual(adapter.capability_identity.call_count, 1)
            self.assertTrue(all(row['evidence_refs'] for row in actual))
            adapter.capability_identity.return_value = {'host':'changed'}
            fresh = list(_capability_batch_requirements(self.engine.instance, references, at=at))
            self.assertEqual(adapter.capability_identity.call_count, 2)
            self.assertTrue(all(not row['satisfied'] and not row['evidence_refs'] for row in fresh))
            bad = dict(references[-1], sha256='0'*64)
            self.assertFalse(list(_capability_batch_requirements(self.engine.instance, [bad], at=at))[0]['satisfied'])

    def test_batch_preserves_each_profile_and_observed_capability_scope(self):
        class Adapter(FixtureAdapter):
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
        class Adapter(FixtureAdapter):
            def describe(self):
                return {"identity": {"host": "fixture"}}
        with patch("do_math.initialization.adapter_for", side_effect=[Adapter(), RuntimeError("probe failed")]):
            with self.assertRaisesRegex(RuntimeError, "probe failed"):
                self.engine._initialization_control({"operation": "probe", "profile_refs": [profile_ref(p) for p in self.profiles]}, "source")
        self.assertFalse(self.engine.instance.get("capability_evidence"))

    def test_active_probe_refreshes_observation_without_adopting_contract(self):
        self.engine.instance["lifecycle"] = {"state": "active", "adoption": {"config_sha256": "saved"}}
        before = deepcopy(self.engine.instance)
        class Adapter(FixtureAdapter):
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

    def test_probe_without_named_editions_observes_every_current_ai_role_profile(self):
        from do_math.initialization import observed_profile_refs
        from do_math.canonical import exact_content_hash
        change = {"operation": "probe", "config_sha256": exact_content_hash(self.engine.instance["config"])}
        with patch("do_math.initialization.adapter_for", return_value=FixtureAdapter()):
            self.engine._initialization_control(change, "source")
        observed = {row["execution_profile_ref"]["id"] for row in self.engine.instance["capability_evidence"].values()}
        current = {ref["id"] for ref in observed_profile_refs(self.engine.instance)
                   if self.engine.instance["execution_profiles"][ref["id"]]["actor_kind"] == "ai"}
        self.assertEqual(observed, current)

    def test_probe_without_named_editions_must_name_the_current_configuration(self):
        with patch("do_math.initialization.adapter_for") as adapter:
            for change in ({"operation": "probe"}, {"operation": "probe", "config_sha256": "0" * 64}):
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, "config_sha256"):
                    self.engine._initialization_control(change, "source")
        adapter.assert_not_called()
        self.assertFalse(self.engine.instance.get("capability_evidence"))


class ActiveProbePublicTests(unittest.TestCase):
    def setUp(self):
        from state_fixtures import start_active_copy
        start_active_copy(self)

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
