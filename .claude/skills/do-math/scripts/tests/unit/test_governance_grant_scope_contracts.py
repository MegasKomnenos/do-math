"""정상 허가의 단일 범위 필드를 바꾸고 정확한 거부 사유를 확인한다."""
from copy import deepcopy
import unittest
from do_math import governance as gov
from support.governance_cases import delegated_sim

class GovernanceGrantScopeTests(unittest.TestCase):
    def test_inactive(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['status'] = 'revoked'
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'grant is not active')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_expired(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['expires_at'] = sim.clock.now()
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'grant expired')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_not_effective(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['valid_from'] = '2099-01-01T00:00:00Z'
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'grant is not effective yet')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_excluded_target(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['excluded_targets'] = [action['target']]
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'target excluded')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_included_target(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['included_targets'] = ['other']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'target outside grant')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_task_scope(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['task_ids'] = ['other']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'target outside grant')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_subject(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['subjects'] = ['other']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'subject outside grant')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_actor_kind(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['execution_kinds'] = ['machine']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'execution kind outside grant')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_purpose(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['purposes'] = ['other']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'purpose outside grant')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_reuse(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['reuse'] = 'unknown'
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'unknown grant reuse contract')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)

    def test_once_without_action_id(self):
        sim = delegated_sim()
        grant = deepcopy(sim.instance['grants']['GR-close'])
        action = {'id': 'AC-close', 'role': 'maintenance', 'actor_kind': 'ai', 'target': sim.instance['id'], 'purpose': 'bounded_review'}
        grant['reuse'] = 'once'
        del action['id']
        before = deepcopy((sim.instance, sim.runtime, grant, action))
        self.assertEqual(gov.grant_scope_reason(grant, action, sim.runtime, at=sim.clock.now()), 'one-case authority requires action identity and current ledger')
        self.assertEqual((sim.instance, sim.runtime, grant, action), before)
