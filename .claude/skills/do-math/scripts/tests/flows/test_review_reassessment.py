"""A qualified report reopens a published identity judgment and the owner runs the reassessment (설계 4.1, 5.4 흐름 폴더).

``support.review_sim.produced_sim()`` holds a formal theorem that research work
produced and the owner verified and reviewed to a match. One of its initial
reviewers is recorded as having inherited the research work's context: the
qualified lineage defect the review's admission refuses, so it is written into
the published state as a defect found afterwards. The report enters through
the public control, the owner applies it, runs the reassessment review with the
model double and settles its activity itself.
"""
import json
import unittest

from do_math.canonical import exact_content_hash
from support.model import amend
from support.review_sim import produced_sim, reviewed_theorem, warm_produced


def setUpModule():
    warm_produced()


class OwnerReassessmentTests(unittest.TestCase):
    def test_public_qualified_report_reopens_the_judgment_and_the_owner_settles_a_bounded_followup(self):
        """Real reassessment and its one plan followup; about 84 s under parallel load, preserving the full input chain."""
        sim = produced_sim()
        from support.cross_contracts import assert_call_records
        kid, assessment = reviewed_theorem(sim)
        original = sim.runtime['review_cycles'][assessment['review_cycle_id']]
        reviewer = original['results']['initial:1:initial-0']['execution_id']
        [producer] = original['producer_execution_ids']
        assessments = set(sim.instance['identity_assessments'])
        sim.engine.runtime['executions'][reviewer]['context_origin'] = [producer]
        sim.engine._save()
        report = {'assessment_id': assessment['id'], 'assessment_sha256': exact_content_hash(assessment),
                  'evidence': {'kind': 'author_context', 'execution_id': reviewer}}
        config = {'role': 'identity_review', 'assessment_reassessment': report}
        first = sim.control('request', text=json.dumps(report), config=config)
        sim.engine.process_controls()
        opened = next(row['result'] for row in sim.runtime['history']
                      if row.get('kind') == 'assessment_reassessment_control' and row['request_id'] == first['request_id'])
        self.assertEqual(opened['disposition'], 'reassessment_opened')
        use = next(row for row in sim.instance['assessment_uses'].values() if row['assessment_id'] == assessment['id'])
        self.assertEqual(use['status'], 'suspended')
        # The same report again as a new request (without the key it would replay the first request's receipt).
        again = sim.control('request', text=json.dumps(report), config=config, idempotency_key='second-report')
        self.assertNotEqual(again['request_id'], first['request_id'])
        sim.engine.process_controls()
        replayed = next(row['result'] for row in sim.runtime['history']
                        if row.get('kind') == 'assessment_reassessment_control' and row['request_id'] == again['request_id'])
        self.assertEqual((replayed['disposition'], replayed['review_cycle_id']), ('already_open', opened['review_cycle_id']))
        sim.model.on('identity_review', stage='initial', review_cycle_id=opened['review_cycle_id']).reply(
            amend(decision='unresolved', scope_complete=False))
        sim.run_until(lambda s: s.runtime['activities'][opened['owner_activity_id']]['status'] == 'finished', max_steps=8)
        activity = sim.runtime['activities'][opened['owner_activity_id']]
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')
        self.assertTrue(activity['followups'][0]['revisit_conditions'])
        cycle = sim.runtime['review_cycles'][opened['review_cycle_id']]
        self.assertEqual((cycle['status'], cycle['decision']), ('unresolved', 'unresolved'))
        self.assertEqual(set(sim.instance['identity_assessments']), assessments)
        self.assertEqual(sim.instance['identity_assessments'][assessment['id']]['review_cycle_id'], original['id'])
        self.assertFalse(any(row['action'].get('identity_review', {}).get('review_cycle_id') == cycle['id']
                             for row in sim.runtime['executions'].values()))
        before = assert_call_records(self, sim)
        requests = [a for a in sim.runtime['queue'] if a.get('identity_review', {}).get('review_cycle_id') == cycle['id']]
        self.assertEqual(len(requests), 1, {'followups': activity['followups'],
            'history': cycle['history'][-3:], 'queue': sim.runtime['queue'],
            'plans': [row['action'] for row in sim.runtime['executions'].values() if row['role'] == 'research_plan']})
        request, = requests
        self.assertEqual(request['identity_review']['assessment_id'], assessment['id'])
        sim.model.on('research_plan').reply(amend(goal_audit=False))
        sim.run_until(lambda s: any(c['action']['id'] == request['id'] for c in s.model.calls), max_steps=8)
        after = assert_call_records(self, sim)
        self.assertEqual(after['research_plan'] - before['research_plan'], 1)
        execution, = [row for row in sim.runtime['executions'].values() if row['action']['id'] == request['id']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertEqual(execution['action']['identity_review']['assessment_id'], assessment['id'])
        for _ in range(2):
            sim.step()
            self.assertEqual(sum(c['action']['id'] == request['id'] for c in sim.model.calls), 1)
        self.assertFalse(any(a.get('identity_review', {}).get('review_cycle_id') == cycle['id'] for a in sim.runtime['queue']))
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)


if __name__ == '__main__':
    unittest.main()
