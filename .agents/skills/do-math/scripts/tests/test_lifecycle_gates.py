"""Instance lifecycle gates: activation requirements and capability evidence, lifecycle transitions, the clock guard and the conversation lease."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from do_math.initialization import (  # noqa: E402
    activation_requirements,
    capability_requirements,
    initialize_state,
)
from do_math.record_schemas import validate_lifecycle  # noqa: E402
from research_fixtures import bare_engine  # noqa: E402


def fixture_engine():
    engine = bare_engine(head="snapshot-fixture")
    engine.current_time = datetime(2026, 9, 20, tzinfo=timezone.utc)
    engine.lifecycle_clock = lambda: engine.current_time.isoformat()
    engine.instance, engine.runtime = initialize_state(instance_id='RI-fixture', goal='G', workspace=Path(tempfile.gettempdir()), config={}, source_input='original request',
        created_at=engine.current_time.isoformat())
    engine.lifecycle_monotonic = lambda: 0.0
    return engine


class ActivationGateTests(unittest.TestCase):
    def test_initialization_persists_missing_activation_requirements_without_dispatch(self):
        instance, runtime = initialize_state(
            instance_id="RI-test", goal="Prove a theorem", workspace=Path(tempfile.gettempdir()) / "do-math-lifecycle-test",
            config={"allowed_axioms": ["propext"]}, source_input="original user request",
        )

        self.assertEqual(instance["lifecycle"]["state"], "initializing")
        self.assertEqual(runtime["status"], "initializing")
        self.assertEqual(runtime["queue"], [])
        self.assertIn("governance", activation_requirements(instance, runtime)["missing"])
        self.assertIn("trust_environment", activation_requirements(instance, runtime)["missing"])
        self.assertEqual(runtime["availability"]["state"], "blocked")

    def test_formal_use_cannot_register_or_activate_an_environment(self):
        engine = fixture_engine()

        with self.assertRaisesRegex(ValueError, 'approved'):
            engine._formal_environment()

        self.assertIsNone(engine.instance["active_trust_environment"])
        self.assertEqual(engine.instance['trust_environments'], {})

    def test_clock_regression_blocks_new_lifecycle_action_without_rewriting_time(self):
        engine = fixture_engine()
        engine.runtime["last_observed_utc"] = "2026-09-20T00:01:00+00:00"

        guard = engine._clock_guard()

        self.assertFalse(guard["usable"])
        self.assertEqual(guard["reason"], "persisted_utc_regression")
        self.assertEqual(engine.runtime["last_observed_utc"], "2026-09-20T00:01:00+00:00")

    def test_capability_gate_reports_missing_evidence_instead_of_assuming_support(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, profile_ref
        instance = build_profiles(DEFAULT_CONFIG)
        profile = next(p for p in instance["execution_profiles"].values() if p["actor_kind"] == "ai")

        result = capability_requirements(instance, profile_ref(profile), current_identity={"host": "fixture"})

        self.assertEqual(result["missing"], sorted(profile["required_capabilities"]))
        self.assertFalse(result["satisfied"])

    def test_activation_requires_recorded_evidence_then_opens_the_correct_first_action(self):
        from engine_fixtures import FakeEngine
        from research_fixtures import FixtureAdapter
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for',return_value=FixtureAdapter()):
            engine=FakeEngine(root)
            self.assertFalse(engine._activate_initialization()['activated'])
            engine.activate()
            self.assertEqual(engine.instance['lifecycle']['state'],'active')
            self.assertEqual(engine.runtime['availability'],{'state':'available'})

    def test_lifecycle_rules_reject_a_state_without_its_utc_high_water(self):
        instance, runtime = initialize_state(
            instance_id="RI-check", goal="Prove a theorem", workspace=Path(tempfile.gettempdir()) / "do-math-lifecycle-check", config={}, source_input="input",
        )
        validate_lifecycle(instance, runtime)
        runtime.pop("last_observed_utc")
        with self.assertRaisesRegex(ValueError, "high-water"):
            validate_lifecycle(instance, runtime)


class LifecycleTransitionTests(unittest.TestCase):
    def engine(self):
        engine = fixture_engine()
        engine.instance, engine.runtime = initialize_state(instance_id='RI-test', goal='G',
            workspace=Path(tempfile.gettempdir()), config={},
            source_input='original', created_at=engine.current_time.isoformat())
        engine.lifecycle_monotonic = lambda: 0.0
        return engine

    def test_initialization_does_not_create_implicit_grants(self):
        engine = self.engine()
        self.assertEqual(engine.instance.get('grants'), {})

    def test_pause_resume_returns_to_initialization_and_requires_new_generation(self):
        engine = self.engine()
        engine._apply_extended_control({'id': 'pause-1', 'action': 'pause', 'config': {}})
        self.assertEqual(engine.runtime['resume_lifecycle'], 'initializing')
        engine._apply_extended_control({'id': 'pause-2', 'action': 'pause', 'config': {}})
        engine._apply_extended_control({'id': 'resume-1', 'action': 'resume', 'config': {}})
        self.assertEqual(engine.runtime['status'], 'initializing')
        engine.instance['conversation_loss_policy'] = 'pause'
        engine._conversation_control({'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 60}, 'attach-1')
        engine._lose_conversation(engine.runtime['conversations']['chat'], 'test')
        with self.assertRaisesRegex(ValueError, 'conversation'):
            engine._apply_extended_control({'id': 'resume-2', 'action': 'resume', 'config': {}})
        engine._conversation_control({'operation': 'attach', 'id': 'chat', 'generation': 2, 'lease_seconds': 60}, 'attach-2')
        engine._apply_extended_control({'id': 'resume-3', 'action': 'resume', 'config': {}})
        self.assertEqual(engine.runtime['status'], 'initializing')

    def test_clock_failure_precedes_grant_application(self):
        engine = self.engine()
        engine.runtime['last_observed_utc'] = '2026-09-21T00:00:00+00:00'
        before = dict(engine.instance.get('grants', {}))
        with self.assertRaisesRegex(ValueError, 'clock'):
            engine._apply_extended_control({'id': 'grant-1', 'action': 'decision', 'config': {'change':
                {'kind': 'grant', 'grant': {'kind': 'local', 'roles': ['maintenance']}}}})
        self.assertEqual(engine.instance.get('grants', {}), before)

    def test_profile_boolean_claim_is_not_capability_evidence(self):
        instance = {'execution_profiles': {'P': {'id': 'P', 'status': 'active', 'capabilities': {'model': True}}}}
        self.assertFalse(capability_requirements(instance, 'P')['satisfied'])

    def test_derived_readiness_not_written_to_runtime(self):
        engine = self.engine()
        engine._record_readiness('T', {'state': 'ready', 'basis': [], 'errors': []}, 'now')
        self.assertNotIn('task_readiness', engine.runtime)
        self.assertEqual(engine._task_readiness['T']['state'], 'ready')

    def test_live_monotonic_regression_blocks_before_catching_persisted_high_water(self):
        from datetime import timedelta
        engine=self.engine(); tick=[0.0]
        engine.lifecycle_monotonic=lambda:tick[0]
        self.assertTrue(engine._clock_guard()['usable'])
        tick[0]=2.0; engine.current_time+=timedelta(seconds=1)
        self.assertEqual(engine._clock_guard()['reason'],'live_monotonic_regression')
        with self.assertRaisesRegex(ValueError,'clock'):
            engine._apply_extended_control({'id':'UI-rejected','action':'decision','config':{'change':{'kind':'grant'}}})


class ClockResolutionTests(unittest.TestCase):
    def test_actual_host_samples_do_not_report_quantization_as_regression(self):
        import time
        from datetime import timedelta
        engine = fixture_engine()
        engine.lifecycle_clock = lambda: datetime.now(timezone.utc).isoformat()
        engine.lifecycle_monotonic = time.monotonic
        engine.runtime['last_observed_utc'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        samples = []
        for index in range(200):
            result = engine._clock_guard()
            samples.append(result.get('observed_utc'))
            self.assertTrue(result['usable'], (index, result, samples))
            time.sleep(.002)

    def test_windows_quantization_interval_is_not_a_regression(self):
        from datetime import timedelta
        from unittest.mock import patch
        from types import SimpleNamespace
        engine = fixture_engine()
        ticks = iter([10., 10., 10.015625, 10.015625])
        engine.lifecycle_monotonic = lambda: next(ticks)
        with patch('do_math.lifecycle_engine.time.get_clock_info', return_value=SimpleNamespace(resolution=.015625)):
            self.assertTrue(engine._clock_guard()['usable'])
            engine.current_time += timedelta(milliseconds=3)
            self.assertTrue(engine._clock_guard()['usable'])

    def test_direct_utc_regressions_have_no_quantization_tolerance(self):
        from datetime import timedelta
        for amount in (timedelta(microseconds=1), timedelta(seconds=60)):
            with self.subTest(amount=amount):
                engine = fixture_engine()
                engine.current_time += timedelta(seconds=120)
                self.assertTrue(engine._clock_guard()['usable'])
                engine.current_time -= amount
                result = engine._clock_guard()
                self.assertFalse(result['usable'])
                self.assertEqual(result['reason'], 'live_utc_regression')


class ConversationLeaseTests(unittest.TestCase):
    def test_independent_operation_does_not_require_a_conversation_lease(self):
        engine = bare_engine({'conversation_loss_policy':'continue_authorized'}, {'conversations':{}})
        self.assertTrue(engine._conversation_live())


if __name__ == "__main__":
    unittest.main()
