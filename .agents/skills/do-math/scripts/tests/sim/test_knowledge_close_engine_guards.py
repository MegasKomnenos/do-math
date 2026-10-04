"""실제 엔진의 신뢰 제어와 대기 재개. 입력·출력·저장 상태를 함께 비교한다."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.formal_engine import _toolchain_matches
from support.knowledge_formal_engine import parked, scene
from support.sim import Sim


class EngineGuards(unittest.TestCase):
    def test_toolchain_matching_requires_nonempty_exact_fingerprint(self):
        expected = {'sha256': 'a' * 64, 'version': 'fixed'}
        self.assertTrue(_toolchain_matches(expected, deepcopy(expected)))
        for actual in (None, {}, {**expected, 'version': 'changed'}):
            self.assertFalse(_toolchain_matches(expected, actual))

    def test_trust_control_rejects_unknown_operations_and_environment(self):
        sim = Sim.activated()
        before = deepcopy((sim.instance, sim.runtime))
        for config, reason in (({'operation': 'unknown'}, 'trust operation must be register, transition or invalidate'),
                ({'operation': 'transition', 'env_id': 'missing'}, 'transition target must be a noninvalid registered environment'),
                ({'operation': 'register'}, '^trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding$')):
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, reason):
                sim.engine._trust_control(config, sim.instance['lifecycle']['input_id'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.jobs.launched, [])

    def test_knowledge_control_rejects_unknown_operation_and_item(self):
        sim = Sim.activated()
        before = deepcopy((sim.instance, sim.runtime))
        for config, reason in (({'operation': 'unknown'}, 'knowledge operation must be revise or invalidate'),
                ({'operation': 'invalidate', 'id': 'missing'}, 'knowledge item does not exist')):
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                sim.engine._knowledge_control(config, sim.instance['lifecycle']['input_id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_rebind_without_receipt_or_stale_previous_binding_is_noop(self):
        sim = Sim.activated()
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._apply_trust_rebind({})
        env = sim.instance['active_trust_environment']
        sim.engine._apply_trust_rebind({'environment_id': env, 'rebind': {'previous': {}, 'current': {}}})
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_parked_check_without_environment_remains_unchanged(self):
        sim, action, _, _, _ = parked()
        before = deepcopy((sim.instance, sim.runtime))
        sim.engine._resume_formal_waits()
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.jobs.launched, [])
        self.assertEqual(sim.runtime['waiting_actions'][action['id']]['kind'], 'formal_authority')

    def test_resumption_does_not_duplicate_already_queued_action(self):
        sim, action, environment, binding, _ = parked()
        sim.instance['trust_environments'][environment['id']] = environment
        sim.runtime['trust_bindings'][environment['id']] = binding
        sim.instance['active_trust_environment'] = environment['id']
        waiting = deepcopy(sim.runtime['waiting_actions'][action['id']])
        sim.runtime['queue'].append(deepcopy(waiting['action']))
        queue = deepcopy(sim.runtime['queue'])
        history = deepcopy(sim.runtime['history'])
        sim.engine._resume_formal_waits()
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertEqual(sim.runtime['waiting_actions'], {})
        self.assertEqual(sim.runtime['history'], [*history, {'kind': 'formal_authority_wait_resumed',
            'action_id': action['id'], 'previous': {}}])
        sim.engine._save()
        self.assertEqual(sim.engine.store.load()[2]['queue'], queue)

    def test_machine_continuation_updates_only_same_action(self):
        sim, action = scene()
        before = deepcopy(sim.runtime['queue'])
        execution_id = next(iter(sim.runtime['executions']))
        sim.engine._record_machine_continuation(action, execution_id)
        expected = [{**row, 'continuation_of': execution_id} if row['id'] == action['id'] else row for row in before]
        self.assertEqual(sim.runtime['queue'], expected)
        self.assertEqual(action['continuation_of'], execution_id)

    def test_unavailable_registration_record_has_no_domain_effect(self):
        from support.trust_inputs import trust_fixture
        sim = Sim.activated()
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        request = trust_fixture(root, ['synthetic-lean'])
        Path(request['toolchain_record']['path']).unlink()
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^toolchain record unavailable: '):
            sim.engine._trust_control(request, sim.instance['lifecycle']['input_id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_transition_without_fingerprint_and_duplicate_transition_are_rejected(self):
        from support.engine_lifecycle import next_environment, transition
        sim = Sim.activated()
        eid = next_environment(sim, 'knowledge-close-guard')
        identity = sim.instance['trust_environments'][eid]['toolchain']
        digest = identity.pop('sha256')
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^transition needs an exact executable fingerprint$'):
            sim.engine._trust_control({'operation': 'transition', 'env_id': eid}, sim.instance['lifecycle']['input_id'])
        self.assertEqual((sim.instance, sim.runtime), before)
        identity['sha256'] = digest
        tid = transition(sim, eid)
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^a trust transition is already in progress$'):
            sim.engine._trust_control({'operation': 'transition', 'env_id': eid}, sim.instance['lifecycle']['input_id'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.runtime['trust_transitions'][tid]['status'], 'checking')

    def test_terminal_trust_generators_do_not_register_executions(self):
        from support.engine_lifecycle import next_environment, transition
        sim = Sim.activated()
        eid = next_environment(sim, 'knowledge-close-terminal')
        tid = transition(sim, eid)
        sim.runtime['trust_transitions'][tid]['status'] = 'failed'
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(list(sim.engine._trust_activation_steps({'transition_id': tid})), [])
        self.assertEqual(list(sim.engine._trust_check_steps({'transition_id': tid, 'target': 'missing'})), [])
        sim.engine._finish_trust_transition(tid, {})
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_trust_check_requires_an_assigned_target(self):
        from support.engine_lifecycle import next_environment, transition
        sim = Sim.activated()
        eid = next_environment(sim, 'knowledge-close-target')
        tid = transition(sim, eid)
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^trust check is not an assigned transition target$'):
            list(sim.engine._trust_check_steps({'transition_id': tid, 'target': 'missing'}))
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_environment_wait_requires_actual_environment_change(self):
        from do_math.trust_validation import wait_detail
        sim, action = scene()
        waiting = {'action': deepcopy(action), 'kind': 'formal_environment', 'reason': '재관찰',
            'next_owner': 'trust_governance', 'detail': wait_detail(sim.instance)}
        sim.runtime.setdefault('waiting_actions', {})[action['id']] = waiting
        before = deepcopy(sim.runtime)
        sim.engine._resume_formal_waits()
        self.assertEqual(sim.runtime, before)
        sim.instance['active_trust_environment'] = None
        sim.engine._resume_formal_waits()
        self.assertEqual(sim.runtime['waiting_actions'], {})
        self.assertEqual(sim.runtime['queue'], before['queue'])
        self.assertEqual(sim.runtime['history'][-1], {'kind': 'formal_environment_wait_resumed',
            'action_id': action['id'], 'previous': waiting['detail']})
