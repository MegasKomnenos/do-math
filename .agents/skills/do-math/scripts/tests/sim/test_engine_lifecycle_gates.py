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
from copy import deepcopy
import unittest

from support.engine_gates import gate_engine, initialized_sim
from support.sim import Sim, warm_template

setUpModule = warm_template
CLOCK_REFUSAL = '^clock prevents new authority: '


class ActivationGateTests(unittest.TestCase):
    def test_initial_dispatch_rechecks_transition_grant_and_adopted_profile(self):
        sim = Sim.activated()
        engine = sim.engine
        engine.instance['lifecycle']['state'] = 'initializing'
        engine.runtime['status'] = 'initializing'
        engine.store.contract.validate(engine.instance, engine.runtime)
        cases = [({'role': 'trust_check', 'transition_id': 'TR-absent'},
                  'trust preparation requires explicit transition authority'),
                 ({'role': 'intent_interpretation', 'grant_id': 'GR-research-sim'},
                  'narrow initial operating grant required')]
        from do_math.execution_profiles import profile_ref
        adopted = engine.instance['lifecycle']['adoption']['initial_profile_ref']
        alternate = next(profile_ref(p) for p in engine.instance['execution_profiles'].values()
                         if p['role'] == 'intent_interpretation' and p['id'] != adopted['id'])
        # A later adopted role/model selection does not silently replace the
        # separately adopted exact initial profile.
        engine.instance['lifecycle']['adoption']['initial_profile_ref'] = alternate
        cases.append(({'role': 'intent_interpretation', 'grant_id': 'GR-initial-sim'},
                      'initial interpretation must use its adopted exact profile'))
        before = deepcopy((engine.instance, engine.runtime))
        import re
        for action, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                engine._action_lifecycle_gate(action)
            self.assertEqual((engine.instance, engine.runtime), before)

    def test_active_external_dispatch_requires_the_adopted_explicit_grant_policy(self):
        engine = Sim.activated().engine
        engine.instance['lifecycle']['adoption']['external_policy'] = 'disabled'
        before = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^the adopted policy does not permit external effects$'):
            engine._action_lifecycle_gate({'role': 'external_action'})
        self.assertEqual((engine.instance, engine.runtime), before)

    def test_closed_activation_and_resume_without_a_retained_phase_are_rejected(self):
        engine = initialized_sim().engine
        engine._apply_extended_control({'id': 'UC-close', 'action': 'close', 'config': {}})
        closed = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^closed/completed instance cannot activate$'):
            engine._activate_initialization()
        self.assertEqual((engine.instance, engine.runtime), closed)
        engine = initialized_sim().engine
        # A paused record may load without resume_lifecycle; it must not guess a phase.
        engine.instance['lifecycle']['state'] = 'paused'
        engine.runtime['status'] = 'paused'
        engine.store.contract.validate(engine.instance, engine.runtime)
        before = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^resume lifecycle is missing$'):
            engine._resume_lifecycle({'origin': 'user', 'config': {}})
        self.assertEqual((engine.instance, engine.runtime), before)

    def test_lifecycle_controls_require_their_preserved_request_identity(self):
        engine = initialized_sim().engine
        before = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^extended control requires its preserved user request ID$'):
            engine._apply_extended_control({'action': 'pause', 'config': {}})
        self.assertEqual((engine.instance, engine.runtime), before)

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
        sim = initialized_sim()
        clock = gate_engine(sim, resolutions=(.015625, .015625))
        engine = sim.engine
        self.assertTrue(engine._clock_guard()['usable'])
        clock.move_monotonic(.015625)
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
