"""Purpose-level flows of the real engine with explicitly scripted semantics, on a Sim.

The model double answers every role as the legacy ``support.purpose_answers.PurposeAnswers``
did (``support.engine_purpose.PurposeResponder``); the worker submits each answer
with the workspace tool, the Lean double answers the formal checks the product's
``verify_lean`` runs, and every other external resource is a port fake. Each
test starts from a restored public activation with the purpose configuration
and drives the owner until its fixture outcome, failing at once when the flow
stops first (``support.engine_purpose.drive``). Neither category establishes
actual-model or actual-Lean accuracy. A flow runs every role of one or more
research rounds, from about 10 s to about a minute, so these tests live in the
flow folder.

This module: knowledge currentness lost and recovered, and a trust environment revalidated.
"""
from copy import deepcopy
import unittest

from do_math import knowledge
from do_math.knowledge_records import usable_links
from support.purpose_answers import EXPLANATION
from support.trust_inputs import trust_fixture
from support.engine_lifecycle import applied
from support.engine_purpose import PurposeResponder, drive, purpose_sim
from support.role_input_requirements import observe_judgment_inputs


class PurposeFlowTests(unittest.TestCase):
    def start(self, scenario='direct', **config):
        sim = purpose_sim(**config)
        responder = sim.model.responder = PurposeResponder(scenario)
        return sim, responder

    def test_knowledge_currentness_loss_and_revision_recover_through_fresh_review(self):
        """About 90 s, over the 60 s flow budget: every role runs to the goal twice, before the invalidation and after the revision."""
        sim, responder = self.start('currentness')
        engine = sim.engine
        drive(self, sim, predicate=lambda s: any(task['title'] == 'Dependent' and task['status'] == 'completed'
                                                 for task in s.runtime['tasks'].values()))
        completed_downstream = {task['id']: deepcopy(task['results']) for task in engine.runtime['tasks'].values()
                                if task['title'] == 'Dependent' and task['status'] == 'completed'}
        self.assertTrue(completed_downstream)
        downstream_work_before_revision = responder.work_order.count('Dependent')
        item = next(row for row in engine.instance['knowledge'].values() if row['title'] == 'Natural zero identity')
        kid, previous_cycle = item['id'], item['review_cycle_id']
        previous_assessments = deepcopy(engine.instance['identity_assessments'])
        downstream = next(task for task in engine.runtime['tasks'].values() if task['title'] == 'Dependent')
        invalidation = applied(sim, 'knowledge', config={'operation': 'invalidate', 'id': kid,
            'reason': 'The previous explanation is disputed and its use is withdrawn',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, [kid], [])['computed_impact']})
        self.assertEqual(engine.instance['goal_status'], 'unsolved')
        suspended = engine.runtime['tasks'][downstream['id']]
        self.assertEqual(suspended['status'], 'completed')
        self.assertFalse(suspended['assessment']['current'])
        self.assertTrue(any('disputed' in row['reason'] for row in suspended['use_history']))
        self.assertFalse(any(judgment.get('current') for judgment in engine.instance.get('goal_judgments', [])))
        changes = {'explanation': EXPLANATION + ' This revision explicitly resolves the disputed domain description.'}
        roots = knowledge.revision_roots(engine.instance, kid)
        revision = applied(sim, 'knowledge', config={'operation': 'revise', 'id': kid, 'changes': changes,
            'reason': 'The replacement explanation fixes the domain explicitly',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact']})
        replacement_id = next(row['id'] for row in engine.instance['knowledge'].values() if row.get('supersedes') == kid)
        sources = {invalidation['request_id'], revision['request_id']}
        requested = [a for a in sim.runtime['queue'] if a['role'] == 'research_plan'
                     and a.get('knowledge_id') == kid and a.get('source_ref') in sources]
        self.assertEqual(len(requested), 2)
        self.assertEqual({a['source_ref'] for a in requested}, sources)
        with observe_judgment_inputs(self) as prepared:
            drive(self, sim, limit=55)
        self.assertTrue(any(row['role'] == 'identity_review' for row in prepared))
        self.assertTrue(any(row['role'] == 'goal_audit' for row in prepared))
        item = sim.instance['knowledge'][replacement_id]
        self.assertTrue(usable_links(sim.instance, replacement_id))
        self.assertNotEqual(item['review_cycle_id'], previous_cycle)
        self.assertIn(previous_cycle, sim.runtime['review_cycles'])
        self.assertEqual(sim.instance['knowledge'][kid]['lifecycle'], 'superseded')
        for identifier, record in previous_assessments.items():
            self.assertEqual(sim.instance['identity_assessments'][identifier], record)
        preserved = sim.runtime['tasks'][downstream['id']]
        self.assertEqual(preserved['status'], 'completed')
        self.assertFalse(preserved['assessment']['current'])
        self.assertEqual(responder.work_order.count('Dependent'), downstream_work_before_revision)
        for task_id, results in completed_downstream.items():
            task = sim.runtime['tasks'][task_id]
            self.assertEqual((task['status'], task['results']), ('completed', results))
            self.assertFalse(task['assessment']['current'])
        self.assertTrue(sim.instance['goal_judgments'][-1].get('current', True))
        from support.cross_contracts import assert_call_records
        counts = assert_call_records(self, sim)
        for request in requested:
            calls = [c for c in sim.model.calls if c['action']['id'] == request['id']]
            self.assertEqual(len(calls), 1)
            executed, = [row for row in sim.runtime['executions'].values() if row['action']['id'] == request['id']]
            self.assertEqual(executed['outcome'], 'output_accepted', executed.get('error'))
            self.assertEqual((executed['action']['knowledge_id'], executed['action']['source_ref']),
                             (kid, request['source_ref']))
        for _ in range(2):
            sim.step()
            self.assertEqual(assert_call_records(self, sim), counts)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_environment_revalidation_does_not_clear_independent_meaning_dispute(self):
        sim, responder = self.start()
        engine = sim.engine
        drive(self, sim, predicate=lambda s: any(usable_links(s.instance, kid) for kid in s.instance['knowledge']))
        kid = next(iter(engine.instance['knowledge']))
        old_environment = engine.instance['active_trust_environment']
        applied(sim, 'trust', config={'operation': 'invalidate', 'env_id': old_environment,
                                      'reason': 'Compiler environment needs revalidation'})
        applied(sim, 'knowledge', config={'operation': 'invalidate', 'id': kid, 'reason': 'Meaning dispute remains open',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, [kid], [])['computed_impact']})
        before_assessments = deepcopy(engine.instance['identity_assessments'])
        self.assertEqual(usable_links(engine.instance, kid), [])
        applied(sim, 'trust', config=trust_fixture(sim.root / 'replacement-environment',
                                                   engine.instance['config']['lean_command']))
        new_environment = next(env for env in engine.instance['trust_environments'] if env != old_environment)
        applied(sim, 'trust', config={'operation': 'transition', 'env_id': new_environment})
        drive(self, sim, predicate=lambda s: s.instance['active_trust_environment'] == new_environment)
        self.assertEqual(sim.instance['identity_assessments'], before_assessments)
        self.assertEqual(usable_links(sim.instance, kid), [])
        self.assertEqual(sim.instance['goal_status'], 'unsolved')


if __name__ == '__main__':
    unittest.main()
