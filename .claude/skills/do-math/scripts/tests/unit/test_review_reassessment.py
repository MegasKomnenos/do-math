"""Reassessing a published identity judgment through the central recovery control (``core_engine``, ``review_engine``, layer 2).

A user's report on a published assessment reopens the judgment only when its
evidence qualifies (here: a reviewer's execution inherited its proposal
author's context); an ordinary report is recorded without suspending the
assessment's use. Every test completes a review of ``K1`` on the product's
``ResearchEngine`` over the stored review state of ``support.review_scene`` and
sends the request to the central control as the owner does for a queued
request (``_review_recovery_control``). The public admission of such a request
and the owner-run review are ``sim.test_review_owner_path`` and
``flows.test_review_reassessment``.
"""
import tempfile
import unittest

from do_math.activities import assign_execution
from do_math.canonical import exact_content_hash
from support.review_scene import ReviewScene, warm


def setUpModule():
    warm()


class ReassessmentCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.scene = ReviewScene(temporary.name)
        self.engine = self.scene.engine
        self.original = self.engine._start_identity_review('K1')
        self.complete()
        self.assessment = self.scene.assessment()
        self.engine.runtime['status'] = 'ready'

    def request(self, evidence, request_id='UC-reassessment'):
        return {'id': request_id, 'action': 'request', 'config': {'role': 'identity_review', 'assessment_reassessment': {
            'assessment_id': self.assessment['id'], 'assessment_sha256': exact_content_hash(self.assessment),
            'evidence': evidence}}}

    def defect(self):
        """One initial reviewer of the original review inherited the author's context; returns that evidence."""
        cycle = self.engine.runtime['review_cycles'][self.original]
        execution_id = cycle['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][execution_id]['context_origin'] = ['author']
        self.engine.runtime['executions']['author'] = {'id': 'author', 'status': 'ended'}
        return {'kind': 'author_context', 'execution_id': execution_id}

    def use(self):
        return next(row for row in self.engine.instance['assessment_uses'].values()
                    if row['assessment_id'] == self.assessment['id'])

    def complete(self, decision='match'):
        """Answer every queued review action toward ``decision`` (``unresolved``: initial slots cannot finish the scope)."""
        while any(a['role'] == 'identity_review' for a in self.engine.runtime['queue']):
            action = self.scene.pending()
            changes = {'decision': 'unresolved', 'scope_complete': False} \
                if action['stage'] == 'initial' and decision == 'unresolved' else {}
            self.scene.execute(changes)


class QualifiedReassessmentTests(ReassessmentCase):
    def test_central_control_consumes_qualified_evidence_and_retains_bounded_followup(self):
        """About 0.22 s, at the 0.2 s unit budget: the original review and the reassessment each run their slots."""
        engine = self.engine
        self.assertTrue(engine._review_recovery_control(self.request(self.defect())))
        opened = engine.runtime['history'][-1]['result']
        self.assertEqual(opened['disposition'], 'reassessment_opened')
        self.assertEqual(self.use()['status'], 'suspended')
        self.complete('unresolved')
        activity = engine.runtime['activities'][opened['owner_activity_id']]
        # The scene's reviewer records its executions directly; attach them through the
        # product's activity API before the central terminal hook, as the owner's registration does.
        for execution in list(engine.runtime['executions'].values()):
            if execution.get('owner_activity_id') == activity['id']:
                assign_execution(engine.runtime, activity['id'], execution)
        engine._settle_activity(activity['assigned_execution_ids'][-1])
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][0]['next_owner'], 'research_plan')
        self.assertTrue(activity['followups'][0]['revisit_conditions'])
        self.assertEqual(list(engine.instance['identity_assessments']), [self.assessment['id']])

    def test_the_same_qualified_report_replayed_names_the_open_reassessment(self):
        """The engine side of the CLI report replay: a second identical report points at the open reassessment."""
        engine = self.engine
        evidence = self.defect()
        self.assertTrue(engine._review_recovery_control(self.request(evidence, 'UC-first')))
        first = engine.runtime['history'][-1]['result']
        self.assertTrue(engine._review_recovery_control(self.request(evidence, 'UC-replay')))
        second = engine.runtime['history'][-1]['result']
        self.assertEqual((first['disposition'], second['disposition']), ('reassessment_opened', 'already_open'))
        self.assertEqual(first['review_cycle_id'], second['review_cycle_id'])
        self.assertEqual(self.use()['status'], 'suspended')
        self.assertEqual(len([cycle for cycle in engine.runtime['review_cycles'].values()
                              if cycle['proposal'].get('assessment_reassessment')]), 1)


class OrdinaryReportTests(ReassessmentCase):
    def test_ordinary_report_cannot_suspend_and_closed_control_cannot_open_review(self):
        engine = self.engine
        request = self.request({'kind': 'report', 'text': 'Maybe wrong'}, 'UC-report')
        self.assertTrue(engine._review_recovery_control(request))
        self.assertEqual(engine.runtime['history'][-1]['result']['disposition'], 'report_only')
        self.assertEqual(self.use()['status'], 'active')
        engine.runtime['status'] = 'closed'
        with self.assertRaisesRegex(ValueError, 'closed/completed instance cannot start an assessment reassessment'):
            engine._review_recovery_control(request)


if __name__ == '__main__':
    unittest.main()
