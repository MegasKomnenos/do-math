"""사용자 허가·철회의 정확한 효과와 원 승인 검증."""
from copy import deepcopy
import unittest

from do_math import governance as gov
from support.governance_cases import delegated_sim, records_sim, proposed_record
from support.known_defects import known_defect


class GovernanceAuthorityEffectTests(unittest.TestCase):
    def test_nonuser_decision_cannot_change_authority(self):
        sim = delegated_sim()
        change = deepcopy(sim.instance['decisions']['DC-close-original']['change'])
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^a preserved user decision is required$'):
            gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close-delegation', actor='ai', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_grant_source_requires_actual_user_actor(self):
        sim = delegated_sim()
        sim.instance['decisions']['DC-close-original']['actor'] = 'ai'
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(ValueError, '^grant lacks current source-bound user approval$'):
            gov.validate_grant_source(sim.instance, sim.instance['grants']['GR-close'])
        self.assertEqual(sim.instance, before)

    def test_requested_grant_outside_task_scope_does_not_fall_through(self):
        sim = delegated_sim()
        sim.instance['grants']['GR-close']['task_ids'] = ['other']
        action = {'id': 'AC-close', 'role': 'maintenance', 'target': sim.instance['id'], 'grant_id': 'GR-close'}
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(gov.authorize(sim.instance, action, sim.clock.now(), runtime=sim.runtime),
            {'allowed': False, 'grant_id': None, 'reason': 'no current grant permits this action', 'rejected': []})
        self.assertEqual((sim.instance, sim.runtime), before)


    def test_same_domain_decision_returns_original_without_requeueing(self):
        sim = records_sim()
        record = sim.instance['governance']['PO-close']
        event = sim.instance['decisions'][record['approval_ref']]
        # 결정 ID를 명시한 새 승인으로 재시도 좌표를 고정한다.
        proposal = proposed_record(sim.instance, 'PO-close')
        proposal['id'] = 'PO-next'
        proposal['supersedes'] = ['PO-close']
        change = {'kind': 'policy', 'record': proposal, 'decision_id': 'DC-close-policy'}
        i, r, first = gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close', clock=sim.clock)
        before = deepcopy((i, r, record))
        again_i, again_r, again = gov.apply_decision(i, r, change, source_ref='GS-close', clock=sim.clock)
        self.assertEqual((again_i, again_r, record), before)
        self.assertEqual(again, first)
        self.assertEqual(r['queue'][:-1], sim.runtime['queue'])
        self.assertEqual(r['queue'][-1]['role'], 'research_preparation')

    def test_domain_decision_id_cannot_change_approved_record(self):
        sim = records_sim()
        record = proposed_record(sim.instance, 'PO-close')
        record['id'] = 'PO-next'
        record['supersedes'] = ['PO-close']
        change = {'kind': 'policy', 'record': record, 'decision_id': 'DC-close-policy'}
        i, r, _ = gov.apply_decision(sim.instance, sim.runtime, change, source_ref='GS-close', clock=sim.clock)
        change['record']['content']['text'] = '승인하지 않은 규칙'
        before = deepcopy((i, r, record))
        with self.assertRaisesRegex(ValueError, '^decision ID reused$'):
            gov.apply_decision(i, r, change, source_ref='GS-close', clock=sim.clock)
        self.assertEqual((i, r, record), before)

    def test_charter_authority_cannot_become_model(self):
        sim = records_sim()
        record = deepcopy(gov.governance_view(sim.instance)['charter'])
        record['content']['decision_authority'] = 'ai'
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(ValueError, '^charter authority cannot create a new decision owner$'):
            gov.validate_governance_record(record)
        self.assertEqual(sim.instance, before)

    def test_second_active_charter_is_rejected(self):
        sim = records_sim()
        record = deepcopy(gov.governance_view(sim.instance)['charter'])
        record['id'] = 'CH-unapproved'
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(ValueError, '^one active charter must own the goal$'):
            gov._install_record(sim.instance, record, 'unused', 'GS-close')
        self.assertEqual(sim.instance, before)
