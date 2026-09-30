"""A review's execution budget (``review_policy``, ``review_cycle``, ``review_engine``, layer 2).

The scope assessment's execution limit must cover the attempts already used
and every mandatory follow-up stage. When the owner cannot admit a review's
next attempt, only that review's attempts drain and planning receives the
actual evidence; no judgment is fabricated. The engine tests register
attempts through the owner's registration on the product's ``ResearchEngine``
over the stored review state of ``support.review_scene``, whose adopted policy
carries the limit under test.
"""
from copy import deepcopy
import tempfile
import unittest

from do_math import execution_lifecycle, review_cycle, review_policy
from research_fixtures import scope_assessment, start_scoped_review
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ScopeFloorTests(unittest.TestCase):
    def test_floor_counts_scope_and_mandatory_followup(self):
        for rounds, required in [(1, 8), (2, 14), (4, 14)]:
            with self.subTest(rounds=rounds):
                policy = review_policy.build_review_policy(None, reviewer_count=3, max_rounds=rounds)
                scope = scope_assessment(policy, ['one', 'two', 'three'])
                scope['activity_execution_limit'] = required - 1
                with self.assertRaisesRegex(ValueError, 'scope activity execution limit requires at least'):
                    review_policy.validate_scope_assessment(scope, policy, executions_used=1)
                scope['activity_execution_limit'] = required
                self.assertEqual(review_policy.validate_scope_assessment(scope, policy,
                    executions_used=1)['activity_execution_limit'], required)

    def test_scope_context_exposes_actual_attempt_usage(self):
        cycle = review_cycle.start_review({'revision': 1}, 2)
        cycle['execution_accounting']['executions_used'] = ['EX-first', 'EX-retry']
        visible = review_cycle.context_for(cycle, review_cycle.next_actions(cycle)[0])
        self.assertEqual(visible['scope_executions_used'], 2)
        self.assertEqual(visible['minimum_scope_execution_limit'], 13)


class ResourceDispositionTests(unittest.TestCase):
    def scene(self, name):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return ReviewScene(temporary.name + '/' + name)

    def test_exhaustion_drains_only_owned_attempts_before_publishing_followup(self):
        scene = self.scene('exhaustion')
        engine = scene.engine
        policy = engine.instance['review_policy']
        limit = review_policy.minimum_scope_executions(2, policy['round_limit'])
        policy['activity_execution_limit'] = limit
        cid = start_scoped_review(engine, 'K1', scope_assessment(policy, ['one', 'two']))
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        stamp = engine.ports.clock.now()
        for number in range(limit):
            execution = engine._register_execution(action,
                {'id': f'EX-attempt-{number}', 'role': 'identity_review', 'status': 'queued'})
            if number < limit - 1:
                execution_lifecycle.end_preparation(execution, at=stamp, stage='context', reason='fixture interrupted attempt', cancelled=True)
        last = execution['id']
        execution_lifecycle.transition_execution(execution, 'starting', at=stamp)
        execution_lifecycle.transition_execution(execution, 'running', at=stamp)
        unrelated = engine._register_execution({'id': 'AC-unrelated', 'role': 'maintenance'},
            {'id': 'EX-unrelated', 'role': 'maintenance', 'status': 'running'})
        self.assertIsNone(engine._register_execution(action, {'id': 'EX-denied', 'role': 'identity_review', 'status': 'queued'}))
        cycle = engine.runtime['review_cycles'][cid]
        self.assertEqual(review_cycle.resource_disposition(cycle)['state'], 'draining')
        self.assertEqual(engine.runtime['executions'][last]['stop_requested'], 'review_resource_disposition')
        self.assertNotIn('stop_requested', unrelated)
        self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
        execution_lifecycle.transition_execution(execution, 'stopping', at=stamp)
        execution_lifecycle.transition_execution(execution, 'ended', at=stamp, outcome='execution_incomplete', disposition='fixture return')
        engine._settle_activity(last)
        self.assertEqual(cycle['status'], 'unresolved')
        self.assertEqual(engine.runtime['activities'][cycle['owner_activity_id']]['status'], 'finished')
        self.assertEqual(unrelated['status'], 'running')
        self.assertEqual(sum(a['role'] == 'research_plan' for a in engine.runtime['queue']), 1)
        self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')

    def test_unaffordable_scope_returns_to_plan_without_fabricating_a_judgment(self):
        for disposition in ('unresolved', 'defer'):
            with self.subTest(disposition=disposition):
                scene = self.scene(disposition)
                engine = scene.engine
                engine.instance['review_policy'].update(activity_execution_limit=1, overflow_disposition=disposition)
                cid = engine._start_identity_review('K1')
                action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
                before = deepcopy(engine.instance['identity_assessments'])
                result = engine._register_execution(action, {'id': 'EX-unstarted', 'role': 'identity_review', 'status': 'queued'})
                self.assertIsNone(result)
                self.assertNotIn('EX-unstarted', engine.runtime['executions'])
                cycle = engine.runtime['review_cycles'][cid]
                record = review_cycle.validate_resource_disposition(cycle, engine.runtime)
                self.assertEqual(record['state'], 'ended' if disposition == 'unresolved' else 'deferred')
                self.assertEqual(engine.instance['identity_assessments'], before)
                plans = [a for a in engine.runtime['queue'] if a['role'] == 'research_plan']
                self.assertEqual(len(plans), 1)
                self.assertIn(cid, plans[0]['evidence_refs'])
                self.assertEqual(review_cycle.next_actions(cycle), [])
                engine._settle_review_resource_dispositions()
                self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 1)
                if disposition == 'unresolved':
                    self.assertEqual(review_cycle.validate_sealed_review(cycle, engine.runtime)['decision'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
