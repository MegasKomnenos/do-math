"""실제 형식 검사와 독립 검토를 거친 신뢰 전환. 시간은 아직 측정하지 않았다."""
from copy import deepcopy
import unittest

from do_math import knowledge as k, knowledge_records as kr
from support.engine_lifecycle import next_environment, transition
from support.knowledge_formal_engine import owner_calls
from support.review_sim import reviewed_sim, theorem_id, THEOREM


def staged_transition():
    """정상 엔진 생산자로 새로운 의존 증거와 단계 검토를 만든다."""
    sim = reviewed_sim()
    kid = theorem_id(sim)
    environment = next_environment(sim, 'knowledge-close-staged')
    sim.lean.allow(THEOREM['lean_code'], ['k1'], signatures={'k1': 'k1 : 1 = 1'},
        dependencies={'k1': {'Nat': {'type': 'Type', 'value': None}}},
        declaration_evidence={'k1': {'type': '1 = 1', 'value': None}}, axioms={'k1': []})
    tid = transition(sim, environment)
    action = next(a for a in sim.runtime['queue'] if a['role'] == 'trust_check')
    with owner_calls(sim):
        sim.engine._run_trust_check(action)
    action = next(a for a in sim.runtime['queue'] if a['role'] == 'trust_activate')
    with owner_calls(sim):
        sim.engine._run_trust_activation(action)
    cycle = next(c for c in sim.runtime['review_cycles'].values() if c.get('transition_id') == tid)
    return sim, kid, tid, cycle['id']


class StagedTransitionTests(unittest.TestCase):
    def test_changed_evidence_requires_real_staged_review_before_activation(self):
        sim, kid, tid, cid = staged_transition()
        old = deepcopy(sim.instance['knowledge'][kid])
        assessments = deepcopy(sim.instance['identity_assessments'])
        self.assertEqual(sim.runtime['trust_transitions'][tid]['status'], 'ready')
        self.assertEqual(sim.runtime['review_cycles'][cid]['status'], 'working')
        self.assertNotEqual(sim.instance['active_trust_environment'], sim.runtime['trust_transitions'][tid]['to_environment'])
        sim.run_until(lambda s: s.runtime['trust_transitions'][tid]['status'] in {'active', 'failed'}, max_steps=24)
        self.assertEqual(sim.runtime['trust_transitions'][tid]['status'], 'active',
                         sim.runtime['trust_transitions'][tid])
        self.assertEqual(sim.runtime['review_cycles'][cid]['decision'], 'match')
        current = sim.instance['knowledge'][kid]
        self.assertEqual(current['previous_review_cycle_id'], old['review_cycle_id'])
        self.assertEqual(current['review_cycle_id'], cid)
        self.assertNotEqual(current['formal_result_id'], old['formal_result_id'])
        for aid, assessment in assessments.items():
            self.assertEqual(sim.instance['identity_assessments'][aid], assessment)
        added = [a for aid, a in sim.instance['identity_assessments'].items() if aid not in assessments]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]['transition_id'], tid)
        self.assertEqual(added[0]['review_cycle_id'], cid)
        self.assertEqual(kr.usable_links(sim.instance, kid)[0]['assessment_id'], added[0]['id'])
        _, state, runtime = sim.engine.store.load()
        self.assertEqual(state['knowledge'][kid], current)
        self.assertEqual(runtime['trust_transitions'][tid], sim.runtime['trust_transitions'][tid])

    def test_staged_review_rejects_each_changed_binding_without_live_publication(self):
        sim, kid, tid, cid = staged_transition()
        transition_record = sim.runtime['trust_transitions'][tid]
        before = deepcopy((sim.instance, sim.runtime))
        for field, value, reason in (
                ('knowledge_id', 'missing', 'staged identity review belongs to another transition target'),
                ('identity_basis', {}, 'staged identity review basis changed'),
                ('publication_premises', {}, 'staged identity review publication premises changed')):
            runtime = deepcopy(sim.runtime)
            runtime['review_cycles'][cid][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k._validated_staged_identity_review(sim.instance, transition_record, kid,
                    {'review_cycle_id': cid}, runtime, clock=sim.ports.clock, at=sim.ports.clock.now())
        for field in ('identity_basis', 'active_trust_environment', 'trust_environment',
                      'review_policy', 'governance'):
            runtime = deepcopy(sim.runtime)
            runtime['review_cycles'][cid]['publication_premises'][field] = None
            with self.subTest(premise=field), self.assertRaisesRegex(ValueError,
                    '^staged identity review publication premises changed$'):
                k._validated_staged_identity_review(sim.instance, transition_record, kid,
                    {'review_cycle_id': cid}, runtime, clock=sim.ports.clock, at=sim.ports.clock.now())
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.store.load()[1]['knowledge'][kid], before[0]['knowledge'][kid])

    def test_lost_mathematical_dependency_reopens_the_actual_goal(self):
        from support.engine_lifecycle import solve_goal
        sim = reviewed_sim()
        kid = theorem_id(sim)
        solve_goal(sim.engine, kid)
        self.assertEqual(sim.instance['goal_status'], 'mathematically_solved')
        from support.cross_contracts import assert_call_records
        from support.model import Answer
        sim.engine._invalidate_goal_currentness()
        self.assertFalse(any(e['kind'] == 'goal_basis_invalidated' for e in sim.runtime['events']))
        sim.engine._save()
        before = assert_call_records(self, sim)
        sim.step()
        self.assertEqual(assert_call_records(self, sim), before)
        sim.engine.instance, sim.engine.runtime = k.invalidate_knowledge(sim.instance, sim.runtime, kid,
            reason='수학 증거 철회', actor_ref='user', clock=sim.ports.clock)
        events = deepcopy(sim.runtime['events'])
        queue = deepcopy(sim.runtime['queue'])
        sim.advance(1)
        sim.engine._invalidate_goal_currentness()
        self.assertEqual(sim.instance['goal_status'], 'unsolved')
        self.assertEqual(sim.runtime['status'], 'ready')
        added_events = sim.runtime['events'][len(events):]
        self.assertEqual([row['kind'] for row in added_events], ['goal_basis_invalidated'])
        self.assertEqual(sim.runtime['events'][:len(events)], events)
        plans = [row for row in sim.runtime['queue'] if row['role'] == 'research_plan']
        self.assertEqual(len(plans), 1, '개방된 목표는 중복 없이 계획을 요청해야 함')
        previous_plans = [row for row in queue if row['role'] == 'research_plan']
        if previous_plans:
            self.assertEqual(plans[0]['id'], previous_plans[0]['id'])
        independent = {row['id']: row for row in queue if row['role'] != 'research_plan'}
        self.assertEqual({row['id']: row for row in sim.runtime['queue'] if row['id'] in independent}, independent)
        self.assertTrue(all(j['current'] is False for j in sim.instance['goal_judgments']))
        sim.engine._save()
        _, state, runtime = sim.engine.store.load()
        self.assertEqual(state['goal_status'], 'unsolved')
        self.assertEqual(runtime['status'], 'ready')
        # No ready task remains; decide from the current input without reopening a goal audit.
        sim.model.on('research_plan').reply(Answer(lambda out, ctx: {**out, 'goal_audit': False}))
        request = plans[0]
        event = added_events[0]
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.run_until(lambda s: any(c['action']['id'] == request['id'] for c in s.model.calls), max_steps=8)
        after = assert_call_records(self, sim)
        self.assertEqual(after['research_plan'] - before['research_plan'], 1)
        execution, = [row for row in sim.runtime['executions'].values() if row['action']['id'] == request['id']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertIn(event['id'], execution['action']['event_refs'])
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            self.assertEqual(sum(c['action']['id'] == request['id'] for c in sim.model.calls), 1)
            self.assertEqual(sum(event['id'] in c['action'].get('event_refs', []) for c in sim.model.calls), 1)
        self.assertEqual(sum(e['kind'] == 'goal_basis_invalidated' for e in sim.runtime['events']), 1)


class KnowledgeWithdrawalTests(unittest.TestCase):
    def test_knowledge_withdrawal_cancels_pending_but_preserves_answered_research(self):
        """공개 철회와 실제 조사 실행을 보존한다. 두 시나리오는 긴 소유 흐름이다."""
        from support.review_research import InvestigationResponder, research_sim
        from support.storage_records import apply_control
        for answered in (False, True):
            with self.subTest(answered=answered):
                sim = research_sim()
                sim.model.responder = InvestigationResponder()
                sim.run_until(lambda s: any(a['role'] == 'supplemental_research'
                    for a in s.runtime['queue']), max_steps=12)
                action = next(a for a in sim.runtime['queue'] if a['role'] == 'supplemental_research')
                cid = action['review_cycle_id']
                kid = sim.runtime['review_cycles'][cid]['knowledge_id']
                if answered:
                    sim.run_until(lambda s: any(r['status'] == 'answered'
                        for r in s.runtime['review_cycles'][cid]['research'].values()), max_steps=12)
                before = deepcopy(sim.runtime['review_cycles'][cid]['research'])
                self.assertTrue(before)
                self.assertEqual({r['status'] for r in before.values()},
                                 {'answered'} if answered else {'pending'})
                request = apply_control(sim, 'knowledge', text='지식 철회',
                    config={'operation': 'invalidate', 'id': kid, 'reason': '지식 철회'})
                source = request['request_id']
                cycle = sim.runtime['review_cycles'][cid]
                self.assertEqual((cycle['status'], cycle['decision'], cycle['phase']),
                                 ('unresolved', 'unresolved', 'ended'))
                expected = deepcopy(before)
                for record in expected.values():
                    if record['status'] == 'pending':
                        record.update(status='cancelled', cancellation={
                            'source_ref': source, 'reason': '지식 철회'})
                self.assertEqual(cycle['research'], expected)
                self.assertEqual(cycle['deferred_actions'], {})
                self.assertEqual(sim.instance['knowledge'][kid]['lifecycle'], 'withdrawn')
                self.assertEqual(sim.engine.store.load()[2]['review_cycles'][cid]['research'], expected)
