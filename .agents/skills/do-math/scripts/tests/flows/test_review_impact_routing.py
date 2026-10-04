"""A research bundle held for an independent impact review waits for it, then is received or stays blocked (설계 4.1, 5.4 흐름 폴더).

``support.review_sim.impact_sim()`` holds research work whose bundle revises
observations ``A`` and ``C`` and declares ``B`` in their impact: the receiver
returned it for impact review, the work action waits and the one queued action
is the ``maintenance`` review of the exact request. The owner runs that review
through the worker and the model double; the owner's retry reads both sealed
submissions from the repository and receives the preserved producer bundle
(``core_engine._retry_impact_reviews``). Calls are observed as they start
(``ObservedCalls``); nothing is replaced.
"""
from copy import deepcopy
import unittest

from do_math import submission
from support.provider_probes import ObservedCalls
from support.review_sim import held_impact, impact_review_answer, impact_sim, observations, warm_impact
from support.role_input_requirements import observe_judgment_inputs


def setUpModule():
    warm_impact()


def sealed_output(sim, execution):
    engine = sim.engine
    return submission.read_sealed_submission(execution, engine.head, engine.store.read, git_dir=engine.store.git_dir)['output']


def at_receipt(arguments):
    """What a receipt call saw as it started: the execution, the preserved flag and the held entry's review IDs."""
    waiting = arguments['self'].runtime.get('waiting_actions', {}).get(arguments['action']['id'], {})
    return {'execution_id': arguments['execution_id'], 'preserved': arguments['preserved'],
            'review_execution_ids': deepcopy(waiting.get('review_execution_ids'))}


def impact_reviews(sim):
    return [row for row in sim.runtime['executions'].values()
            if row.get('role') == 'maintenance' and row.get('action', {}).get('stage') == 'impact_review']


class ImpactReviewRoutingTests(unittest.TestCase):
    def test_exact_request_waits_for_accepted_review_without_new_producer(self):
        """The review releases the preserved bundle, then its impact receives one actual planning judgment."""
        sim = impact_sim()
        waiting, producer, identifier, request = held_impact(sim)
        reviews = [row for row in sim.runtime['queue'] if row.get('stage') == 'impact_review']
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['input_basis']['impact_review'], request)
        self.assertNotIn('continuation_of', reviews[0])
        sim.engine._hold_impact_reviews(waiting['action'], producer['id'], {'bundles': [
            {'integration_id': identifier, 'next_owner': 'impact_review', 'impact_review_request': request}]})
        self.assertEqual(len([row for row in sim.runtime['queue'] if row.get('stage') == 'impact_review']), 1)
        before = sealed_output(sim, producer)
        with ObservedCalls(capture={'receive': at_receipt}, receive=sim.engine._receive_submission) as observed:
            sim.engine._retry_impact_reviews()
        self.assertEqual(observed.captured('receive'), [], 'no receipt before the requested review ended')
        sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer())
        with observe_judgment_inputs(self) as prepared:
            with ObservedCalls(capture={'receive': at_receipt}, receive=sim.engine._receive_submission) as observed:
                sim.step()
        self.assertEqual(len([row for row in prepared if row['action'].get('stage') == 'impact_review']), 1)
        [review] = impact_reviews(sim)
        self.assertEqual(review['outcome'], 'output_accepted')
        # Every receipt call of the pass, in order: the review's own output, then the preserved producer bundle.
        self.assertEqual(observed.captured('receive'),
                         [{'execution_id': review['id'], 'preserved': False, 'review_execution_ids': None},
                          {'execution_id': producer['id'], 'preserved': True, 'review_execution_ids': {identifier: review['id']}}])
        self.assertEqual([row['id'] for row in sim.runtime['executions'].values() if row.get('role') == 'research_work'],
                         [producer['id']])
        self.assertEqual(sealed_output(sim, sim.runtime['executions'][producer['id']]), before)
        ids = observations(sim)
        self.assertEqual({row['supersedes'] for row in sim.instance['knowledge'].values() if row.get('supersedes')},
                         {ids['A'], ids['C']})
        self.assertNotIn(waiting['action']['id'], sim.runtime['waiting_actions'])
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.model import Answer
        from support.role_answers import assessment_awaiting_required_evidence
        followup, = [a for a in sim.runtime['queue'] if a.get('affected_ids')]
        self.assertIn(ids['B'], followup['affected_ids'])
        sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
        def inspect_remaining(out, context):
            out['goal_audit'] = False
            for result in out['task_assessments']:
                current = next(t for t in context['tasks'] if t['id'] == result['task_id'])
                result.update(assessment_awaiting_required_evidence(current))
            return out
        sim.model.on('research_plan').reply(Answer(inspect_remaining))
        assert_call_records(self, sim)
        sim.run_until(lambda current: any(c['action']['id'] == followup['id'] for c in current.model.calls), max_steps=12)
        execution, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == followup['id']]
        self.assertEqual(execution['outcome'], 'output_accepted',
                         {'error': execution.get('error'), 'issues': [r.get('result', {}).get('issues') for r in sim.model.receipts]})
        self.assertEqual(execution['action']['affected_ids'], followup['affected_ids'])
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            self.assertEqual(sum(c['action']['id'] == followup['id'] for c in sim.model.calls), 1)


    def test_unresolved_review_remains_held_and_has_one_final_rejected_receipt(self):
        """About 3 s: the impact review runs as a model call in one owner pass."""
        sim = impact_sim()
        waiting, producer, identifier, request = held_impact(sim)
        first_scope = next(iter(request['plans']))
        sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer({first_scope: 'unresolved'}))
        engine = sim.engine
        with ObservedCalls(capture={'receive': at_receipt,
                                    'receipt': lambda arguments: (arguments['execution_id'], arguments['accepted'])},
                           receive=engine._receive_submission, receipt=engine._record_task_receipt) as observed:
            sim.step()  # the review runs, is received, and the owner's retry reads it
            sim.engine._retry_impact_reviews()  # the owner's next pass retries again
        [review] = impact_reviews(sim)
        # The only receipt call is the review's own output; the held producer bundle is never received.
        self.assertEqual(observed.captured('receive'),
                         [{'execution_id': review['id'], 'preserved': False, 'review_execution_ids': None}])
        self.assertEqual({execution for execution, _ in observed.captured('receipt')}, {review['id'], producer['id']})
        self.assertEqual([row for row in observed.captured('receipt') if row[0] == producer['id']], [(producer['id'], False)])
        self.assertEqual(sim.runtime['waiting_actions'][waiting['action']['id']]['kind'], 'impact_review_blocked')
        self.assertEqual(len(impact_reviews(sim)), 1)
        self.assertEqual([row for row in sim.runtime['queue'] if row.get('stage') == 'impact_review'], [])
        from support.cross_contracts import assert_call_records
        self.assertFalse(any(a.get('affected_ids') for a in sim.runtime['queue']))
        self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)


if __name__ == '__main__':
    unittest.main()
