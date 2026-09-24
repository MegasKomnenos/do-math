"""Feature-5 lifecycle boundaries: initialization, trust, and clock safety."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
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
from do_math.knowledge import register_environment  # noqa: E402
from do_math.lifecycle_engine import LifecycleEngineMixin  # noqa: E402
from do_math.governance_engine import GovernanceEngineMixin
from do_math.preflight import inspect_current_state  # noqa: E402


class FixtureEngine(LifecycleEngineMixin, GovernanceEngineMixin):
    def __init__(self):
        self.current_time = datetime(2026, 9, 20, tzinfo=timezone.utc)
        self.lifecycle_clock = lambda: self.current_time.isoformat()
        self.instance = {
            "id": "RI-fixture", "feature_version": 5,
            "config": {"research_reconsider_seconds": 60, "allowed_axioms": ["propext"]},
            "knowledge": {}, "relations": [], "goal_judgments": [], "sources": [],
            "trust_environments": {}, "active_trust_environment": None,
        }
        self.runtime = {"feature_version": 5, "status": "initializing", "tasks": {},
                        "executions": {}, "activities": {}, "queue": [], "history": [],
                        "questions": [], "last_observed_utc": self.current_time.isoformat()}
        self.head = "snapshot-fixture"
        self.instance, self.runtime = initialize_state(instance_id='RI-fixture', goal='G', workspace=Path(tempfile.gettempdir()), config={}, source_input='original request',
            created_at=self.current_time.isoformat())
        self.lifecycle_monotonic = lambda: 0.0
        self._task_readiness = {}

    def _enqueue(self, role, target=None, **extra):
        self.runtime["queue"].append({"role": role, **({"target": target} if target else {}), **extra})


class LifecycleRedesignTests(unittest.TestCase):
    def test_initialization_persists_missing_activation_requirements_without_dispatch(self):
        instance, runtime = initialize_state(
            instance_id="RI-test", goal="Prove a theorem", workspace=Path(tempfile.gettempdir()) / "do-math-lifecycle-test",
            config={"allowed_axioms": ["propext"]}, source_input="original user request",
        )

        self.assertEqual(instance["feature_version"], 5)
        self.assertEqual(instance["lifecycle"]["state"], "initializing")
        self.assertEqual(runtime["status"], "initializing")
        self.assertEqual(runtime["queue"], [])
        self.assertIn("governance", activation_requirements(instance, runtime)["missing"])
        self.assertIn("trust_environment", activation_requirements(instance, runtime)["missing"])
        self.assertEqual(runtime["availability"]["state"], "blocked")

    def test_formal_discovery_registers_but_cannot_activate_feature_five_environment(self):
        engine = FixtureEngine()
        toolchain = {"executable": "lean", "configured_command": ["lean"],
                     "sha256": hashlib.sha256(b"lean").hexdigest(), "version": "Lean fixture"}

        with self.assertRaisesRegex(ValueError, 'approved'):
            engine._bind_formal_environment({"status": "verified", "toolchain": toolchain,
                                               "allowed_axioms": ["propext"]})

        self.assertIsNone(engine.instance["active_trust_environment"])
        self.assertEqual(engine.instance['trust_environments'], {})

    def test_clock_regression_blocks_new_lifecycle_action_without_rewriting_time(self):
        engine = FixtureEngine()
        engine.runtime["last_observed_utc"] = "2026-09-20T00:01:00+00:00"

        guard = engine._clock_guard()

        self.assertFalse(guard["usable"])
        self.assertEqual(guard["reason"], "persisted_utc_regression")
        self.assertEqual(engine.runtime["last_observed_utc"], "2026-09-20T00:01:00+00:00")

    def test_capability_gate_reports_missing_evidence_instead_of_assuming_support(self):
        instance = {"execution_profiles": {"P1": {"id": "P1", "status": "active", "capabilities": {"tool_results": True}}}}

        result = capability_requirements(instance, "P1", {"tool_results", "remote_cancel"})

        self.assertEqual(result["missing"], ["remote_cancel", "tool_results"])
        self.assertFalse(result["satisfied"])

    def test_activation_requires_recorded_evidence_then_opens_the_correct_first_action(self):
        from test_lifecycle_engine import FakeEngine, AdapterDouble
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for',return_value=AdapterDouble()):
            engine=FakeEngine(root)
            self.assertFalse(engine._activate_initialization()['activated'])
            engine.activate()
            self.assertEqual(engine.instance['lifecycle']['state'],'active')
            self.assertEqual(engine.runtime['availability'],{'state':'available'})

    def test_read_only_preflight_rejects_an_incomplete_feature_five_head(self):
        instance, runtime = initialize_state(
            instance_id="RI-check", goal="Prove a theorem", workspace=Path(tempfile.gettempdir()) / "do-math-lifecycle-check", config={}, source_input="input",
        )
        self.assertTrue(inspect_current_state(instance, runtime)["valid"])
        runtime.pop("last_observed_utc")
        diagnosis = inspect_current_state(instance, runtime)
        self.assertFalse(diagnosis["valid"])
        self.assertEqual(diagnosis["errors"][0]["check"], "clock_high_water")


class FollowupTests(unittest.TestCase):
    def engine(self):
        engine = FixtureEngine()
        engine.instance, engine.runtime = initialize_state(instance_id='RI-test', goal='G',
            workspace=Path(tempfile.gettempdir()), config={},
            source_input='original', created_at=engine.current_time.isoformat())
        engine.lifecycle_monotonic = lambda: 0.0
        engine._task_readiness = {}
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
        self.assertFalse(capability_requirements(instance, 'P', ['model'])['satisfied'])

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
        engine = FixtureEngine()
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
        engine = FixtureEngine()
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
                engine = FixtureEngine()
                engine.current_time += timedelta(seconds=120)
                self.assertTrue(engine._clock_guard()['usable'])
                engine.current_time -= amount
                result = engine._clock_guard()
                self.assertFalse(result['usable'])
                self.assertEqual(result['reason'], 'live_utc_regression')

    def test_elapsed_time_regression_outside_resolution_interval_is_rejected(self):
        from datetime import timedelta
        engine = FixtureEngine()
        tick = [0.]
        engine.lifecycle_monotonic = lambda: tick[0]
        self.assertTrue(engine._clock_guard()['usable'])
        tick[0] = 2.
        engine.current_time += timedelta(seconds=1)
        self.assertEqual(engine._clock_guard()['reason'], 'live_monotonic_regression')


if __name__ == "__main__":
    unittest.main()
