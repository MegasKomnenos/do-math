"""실제 외부 작업 준비 생산자의 사례 식별과 허가 소비 경계."""
from copy import deepcopy
import unittest

from do_math import governance as gov
from support.engine_lifecycle import external_sim, http_grant, applied


class GovernanceExternalCaseIdentityTests(unittest.TestCase):
    def test_external_case_rejects_different_pinned_grant(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        sim.engine._save()
        applied(sim, 'external', config=config)
        operation = sim.runtime['external_operations']['OP-audit']
        action = {'id': operation['id'], 'role': 'external_operation', 'grant_id': 'other'}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^external case grant differs$'):
            gov.grant_case_id(action, sim.runtime)
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.ports.http.requests, [])

    def test_ambiguous_external_case_is_rejected_and_scope_returns_same_reason(self):
        sim = external_sim()
        config = http_grant(sim.engine, once=True)
        sim.engine._save()
        applied(sim, 'external', config=config)
        second_config = {**config, 'id': 'OP-close-other'}
        # 두 번째 준비에는 별도 허가를 써서 첫 허가의 once 계약을 보존한다.
        second_config['grant_id'] = 'GR-close-other'
        http_grant(sim.engine, gid='GR-close-other')
        sim.engine._save()
        applied(sim, 'external', config=second_config)
        runtime = deepcopy(sim.runtime)
        first = runtime['external_operations']['OP-audit']
        runtime['external_operations']['OP-close-other']['action_id'] = first['id']
        action = {'id': first['id'], 'role': 'external_operation', 'grant_id': first['grant_id']}
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^ambiguous external case identity$'):
            gov.grant_case_id(action, runtime)
        self.assertEqual(gov.grant_scope_reason(sim.instance['grants'][first['grant_id']], action,
                                               runtime, at=sim.clock.now()), 'ambiguous external case identity')
        self.assertEqual(runtime, before)
        self.assertEqual(sim.ports.http.requests, [])

    def test_revoke_does_not_dispose_other_grant_operation(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        sim.engine._save()
        applied(sim, 'external', config=config)
        http_grant(sim.engine, gid='GR-close-other')
        sim.engine._save()
        applied(sim, 'external', config={**config, 'id': 'OP-close-other', 'grant_id': 'GR-close-other'})
        before = deepcopy((sim.instance, sim.runtime))
        source = sim.instance['grants']['GR-http-audit']['source_ref']
        result, state, event = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'revoke', 'grant_id': 'GR-http-audit'}, source_ref=source, clock=sim.clock)
        self.assertEqual(state['external_operations']['OP-close-other'], before[1]['external_operations']['OP-close-other'])
        self.assertEqual(state['external_operations']['OP-audit']['status'], 'cancelled')
        self.assertEqual(event['affected'], ['OP-audit'])
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.ports.http.requests, [])
        sim.engine.instance, sim.engine.runtime = result, state
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['external_operations'], state['external_operations'])
