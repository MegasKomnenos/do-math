"""Public grants release the same unstarted action once, preserving its activity."""
from copy import deepcopy
from datetime import timedelta
import unittest
from support.engine_lifecycle import applied, clear_work
from support.sim import Sim, warm_template
from support.wait_reporting import assert_wait_report

setUpModule = warm_template

class ActionAuthorityWaitTests(unittest.TestCase):
    def test_public_grant_releases_the_same_unstarted_maintenance_wait_once(self):
        sim = Sim.activated()
        gid = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': gid}})
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='권한 복원 출구')
        action = deepcopy(sim.runtime['queue'][0])
        before = deepcopy(sim.runtime['executions'])
        self.assertIs(sim.engine._prepare_call(action), False)
        wait = deepcopy(sim.runtime['waiting_actions'][action['id']])
        self.assertEqual(wait['action']['id'], action['id'])
        self.assertEqual((wait['kind'], wait['next_owner']), ('action_authority', 'user'))
        activity_id = wait['action']['owner_activity_id']
        self.assertEqual(sim.runtime['activities'][activity_id]['status'], 'waiting')
        assert_wait_report(self, sim.engine, action['id'])
        sim.restart()
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], wait)
        assert_wait_report(self, sim.engine, action['id'])
        held = deepcopy((sim.instance, sim.runtime))
        for _ in range(2):
            sim.engine._resume_action_authority_waits()
            self.assertEqual((sim.instance, sim.runtime), held)
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-unrelated-role', 'kind': 'local', 'roles': ['research_plan'],
            'reuse': 'reusable', 'expires_at': (sim.ports.clock.wall() + timedelta(days=1)).isoformat()}}})
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], wait)
        self.assertEqual(sim.runtime['activities'][activity_id], held[1]['activities'][activity_id])
        self.assertEqual(sim.runtime['executions'], before)
        applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-maintenance-restored', 'kind': 'local', 'roles': ['maintenance'],
            'reuse': 'reusable', 'expires_at': (sim.ports.clock.wall() + timedelta(days=1)).isoformat()}}})
        self.assertNotIn(action['id'], sim.runtime.get('waiting_actions', {}))
        resumed = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
        self.assertEqual(len(resumed), 1)
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.model.calls, [])
        self.assertEqual(sim.runtime['activities'][activity_id]['status'], 'ready')
        resolutions = [row for row in sim.runtime['history']
                       if row.get('kind') == 'action_authority_resolved' and row['action_id'] == action['id']]
        self.assertEqual(len(resolutions), 1)
        self.assertEqual(resolutions[0]['previous'], wait)
        released = deepcopy((sim.instance, sim.runtime))
        sim.engine._resume_action_authority_waits()
        self.assertEqual((sim.instance, sim.runtime), released)
        self.assertEqual(sim.engine.store.load()[2]['queue'], sim.runtime['queue'])
        report = sim.engine.status()
        self.assertNotIn(action['id'], report['waiting_actions'])
        self.assertNotIn(activity_id, report['waiting_activities'])
