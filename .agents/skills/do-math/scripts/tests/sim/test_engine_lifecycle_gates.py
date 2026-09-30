"""Instance lifecycle gates on the Sim's real engine: activation, transitions, the clock guard and the conversation lease.

``lifecycle_engine`` and ``formal_engine`` are layer-2 engine mixins; their
gates are called on the engine of a Sim, a publicly initialized instance
(``support.engine_gates.initialized_sim``) or the restored public activation.
The legacy tests built an engine without ``__init__`` from ``initialize_state``
and replaced its ``lifecycle_clock`` and ``lifecycle_monotonic``; here the
instance is the product's public initialization and both clocks are the clock
port (``support.engine_gates.gate_engine``), which a test moves. Nothing
replaces an engine method or the store.
"""
from datetime import timedelta
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from support.engine_gates import gate_engine, initialized_sim
from support.sim import Sim, warm_template

setUpModule = warm_template
CLOCK_REFUSAL = '^clock prevents new authority: '


class ActivationGateTests(unittest.TestCase):
    def test_formal_use_cannot_register_or_activate_an_environment(self):
        engine = initialized_sim().engine
        with self.assertRaisesRegex(ValueError, '^approved fixed trust environment required: trust environment absent$'):
            engine._formal_environment()
        self.assertIsNone(engine.instance['active_trust_environment'])
        self.assertEqual(engine.instance['trust_environments'], {})

    def test_clock_regression_blocks_new_lifecycle_action_without_rewriting_time(self):
        sim = initialized_sim()
        clock = gate_engine(sim)
        engine = sim.engine
        persisted = engine.runtime['last_observed_utc']
        clock.set_wall(clock.wall() - timedelta(minutes=1))  # the current UTC is a minute before the high-water
        guard = engine._clock_guard()
        self.assertFalse(guard['usable'])
        self.assertEqual(guard['reason'], 'persisted_utc_regression')
        self.assertEqual(engine.runtime['last_observed_utc'], persisted)

    def test_activation_requires_recorded_evidence_then_opens_the_correct_first_action(self):
        before = initialized_sim().engine._activate_initialization()
        self.assertFalse(before['activated'])
        # The public activation (controls for the evidence, then owner passes) on the same initialization.
        active = Sim.activated()
        self.assertEqual(active.instance['lifecycle']['state'], 'active')
        self.assertEqual(active.runtime['availability'], {'state': 'available'})


class LifecycleTransitionTests(unittest.TestCase):
    def test_initialization_does_not_create_implicit_grants(self):
        self.assertEqual(initialized_sim().instance.get('grants'), {})

    def test_pause_resume_returns_to_initialization_and_requires_new_generation(self):
        engine = initialized_sim().engine
        engine._apply_extended_control({'id': 'pause-1', 'action': 'pause', 'config': {}})
        self.assertEqual(engine.runtime['resume_lifecycle'], 'initializing')
        engine._apply_extended_control({'id': 'pause-2', 'action': 'pause', 'config': {}})
        engine._apply_extended_control({'id': 'resume-1', 'action': 'resume', 'config': {}})
        self.assertEqual(engine.runtime['status'], 'initializing')
        engine.instance['conversation_loss_policy'] = 'pause'
        engine._conversation_control({'operation': 'attach', 'id': 'chat', 'generation': 1, 'lease_seconds': 60}, 'attach-1')
        engine._lose_conversation(engine.runtime['conversations']['chat'], 'test')
        with self.assertRaisesRegex(ValueError, '^conversation pause requires a live new connection generation$'):
            engine._apply_extended_control({'id': 'resume-2', 'action': 'resume', 'config': {}})
        engine._conversation_control({'operation': 'attach', 'id': 'chat', 'generation': 2, 'lease_seconds': 60}, 'attach-2')
        engine._apply_extended_control({'id': 'resume-3', 'action': 'resume', 'config': {}})
        self.assertEqual(engine.runtime['status'], 'initializing')

    def test_clock_failure_precedes_grant_application(self):
        sim = initialized_sim()
        clock = gate_engine(sim)
        engine = sim.engine
        clock.set_wall(clock.wall() - timedelta(days=1))  # the high-water is a day after the current UTC
        before = dict(engine.instance.get('grants', {}))
        with self.assertRaisesRegex(ValueError, CLOCK_REFUSAL + 'persisted_utc_regression$'):
            engine._apply_extended_control({'id': 'grant-1', 'action': 'decision', 'config': {'change':
                {'kind': 'grant', 'grant': {'kind': 'local', 'roles': ['maintenance']}}}})
        self.assertEqual(engine.instance.get('grants', {}), before)

    def test_derived_readiness_not_written_to_runtime(self):
        engine = initialized_sim().engine
        engine._record_readiness('T', {'state': 'ready', 'basis': [], 'errors': []}, 'now')
        self.assertNotIn('task_readiness', engine.runtime)
        self.assertEqual(engine._task_readiness['T']['state'], 'ready')
        engine._save()
        self.assertNotIn('task_readiness', engine.store.load()[2])

    def test_live_monotonic_regression_blocks_before_catching_persisted_high_water(self):
        sim = initialized_sim()
        clock = gate_engine(sim)
        engine = sim.engine
        self.assertTrue(engine._clock_guard()['usable'])
        clock.move_monotonic(2.0)
        clock.set_wall(clock.wall() + timedelta(seconds=1))  # UTC moved less than the monotonic interval
        self.assertEqual(engine._clock_guard()['reason'], 'live_monotonic_regression')
        with self.assertRaisesRegex(ValueError, CLOCK_REFUSAL + 'live_monotonic_regression$'):
            engine._apply_extended_control({'id': 'UI-rejected', 'action': 'decision', 'config': {'change': {'kind': 'grant'}}})


class ClockResolutionTests(unittest.TestCase):
    def test_windows_quantization_interval_is_not_a_regression(self):
        """The host reports Windows' 15.625 ms tick (``time.get_clock_info``, the OS's report, not a do-math name)."""
        sim = initialized_sim()
        clock = gate_engine(sim)
        engine = sim.engine
        with patch('time.get_clock_info', return_value=SimpleNamespace(resolution=.015625)):
            self.assertTrue(engine._clock_guard()['usable'])
            clock.move_monotonic(.015625)  # one tick on the monotonic clock
            clock.set_wall(clock.wall() + timedelta(milliseconds=3))
            self.assertTrue(engine._clock_guard()['usable'])

    def test_direct_utc_regressions_have_no_quantization_tolerance(self):
        sim = initialized_sim()
        base = sim.clock.wall()
        for amount in (timedelta(microseconds=1), timedelta(seconds=60)):
            with self.subTest(amount=amount):
                sim.restart()  # a new process: no anchor and no retained failure
                sim.clock.set_wall(base + timedelta(seconds=120))
                self.assertTrue(sim.engine._clock_guard()['usable'])
                sim.clock.set_wall(base + timedelta(seconds=120) - amount)
                result = sim.engine._clock_guard()
                self.assertFalse(result['usable'])
                self.assertEqual(result['reason'], 'live_utc_regression')


class ConversationLeaseTests(unittest.TestCase):
    def test_independent_operation_does_not_require_a_conversation_lease(self):
        engine = Sim.activated().engine
        self.assertEqual(engine.instance['conversation_loss_policy'], 'continue_authorized')
        self.assertEqual(engine.runtime.get('conversations', {}), {})
        self.assertTrue(engine._conversation_live())


if __name__ == '__main__':
    unittest.main()
