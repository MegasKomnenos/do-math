"""실제 검토가 게시한 평가의 재검토 전제와 보고 전용 처분."""
from copy import deepcopy

from do_math.canonical import exact_content_hash
from do_math import review_cycle as rc, knowledge
from support.review_inputs import review_stage_output
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm


def setUpModule():
    warm()


class ReassessmentEvidenceTests(ReviewOwnerCase):
    def completed(self):
        cid = self.engine._start_identity_review('K1')
        for _ in range(3):
            self.scene.execute()
        original = self.engine.runtime['review_cycles'][cid]
        assessment = self.scene.assessment()
        self.assertEqual(original['decision'], 'match')
        return original, assessment

    def defect(self, original):
        eid = original['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][eid]['context_origin'] = ['author']
        return {'kind': 'author_context', 'execution_id': eid}

    def test_unknown_original_execution_and_missing_ancestor_are_report_only(self):
        original, assessment = self.completed()
        before = deepcopy(self.engine.instance)
        self.assertIsNone(self.engine._qualified_assessment_defect(assessment, original, {'kind': 'author_context', 'execution_id': 'absent'}))
        eid = original['results']['initial:1:initial-0']['execution_id']
        self.engine.runtime['executions'][eid]['context_origin'] = ['missing-ancestor']
        self.assertIsNone(self.engine._qualified_assessment_defect(assessment, original, {'kind': 'author_context', 'execution_id': eid}))
        result = self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), {'kind': 'author_context', 'execution_id': eid})
        self.assertEqual(result, {'disposition': 'report_only', 'assessment_id': assessment['id'], 'next_owner': 'independent_review'})
        self.assertEqual(self.engine.instance, before)
        self.assertEqual(self.engine.runtime['history'][-1]['disposition'], 'report_only')

    def test_independent_objection_requires_distinct_preserved_cycle(self):
        original, assessment = self.completed()
        before = deepcopy((self.engine.instance, self.engine.runtime))
        for cid in ('absent', original['id']):
            with self.subTest(cid=cid):
                self.assertIsNone(self.engine._qualified_assessment_defect(assessment, original,
                    {'kind': 'independent_objection', 'review_cycle_id': cid}))
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_original_provenance_must_be_completed_and_exact(self):
        original, assessment = self.completed()
        original['status'] = 'working'
        self.assert_engine_rejected('original assessment has no completed review provenance',
            lambda: self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), {}))

    def test_withdrawn_use_cannot_be_reopened(self):
        original, assessment = self.completed()
        evidence = self.defect(original)
        use = next(row for row in self.engine.instance['assessment_uses'].values() if row['assessment_id'] == assessment['id'])
        use['status'] = 'withdrawn'
        self.assert_engine_rejected('a withdrawn assessment cannot be reopened as active',
            lambda: self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), evidence))

    def test_current_reassessment_rejects_changed_exact_original_binding(self):
        original, assessment = self.completed()
        result = self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), self.defect(original))
        action = next(a for a in self.engine.runtime['queue'] if a.get('review_cycle_id') == result['review_cycle_id'])
        self.engine.runtime['review_cycles'][result['review_cycle_id']]['proposal']['assessment_reassessment']['assessment_sha256'] = '0' * 64
        self.assert_engine_rejected('reassessment exact original judgment changed', lambda: self.engine._review_cycle(action))

    def test_independent_objection_missing_result_or_finding_does_not_qualify(self):
        original, assessment = self.completed()
        opened = self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), self.defect(original))
        for _ in range(3):
            self.scene.execute()
        source = self.engine.runtime['review_cycles'][opened['review_cycle_id']]
        self.assertEqual(source['decision'], 'match')
        before = deepcopy((self.engine.instance, self.engine.runtime))
        for key, finding in [('missing', 'missing'), ('initial:1:initial-0', 'missing')]:
            with self.subTest(key=key):
                self.assertIsNone(self.engine._qualified_assessment_defect(assessment, original,
                    {'kind': 'independent_objection', 'review_cycle_id': source['id'], 'result_key': key, 'finding_id': finding}))
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_reassessment_replay_requires_actual_scope_result(self):
        original, assessment = self.completed()
        opened = self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), self.defect(original))
        for _ in range(3):
            self.scene.execute()
        cycle = deepcopy(self.engine.runtime['review_cycles'][opened['review_cycle_id']])
        del cycle['results']['scope:1:scope']
        with self.assertRaisesRegex(ValueError, 'reassessment requires an actual independent scope execution'):
            rc.validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance,
                clock=self.engine.ports.clock, at=self.engine.ports.clock.now())

    def test_reassessment_owner_waits_until_its_last_execution_has_ended(self):
        original, assessment = self.completed()
        opened = self.engine._start_assessment_reassessment(assessment['id'], exact_content_hash(assessment), self.defect(original))
        for _ in range(3):
            _, _, eid = self.scene.execute()
        self.engine.runtime['executions'][eid]['status'] = 'running'
        before = deepcopy(self.engine.runtime['activities'][opened['owner_activity_id']])
        self.assertEqual(self.engine._settle_assessment_reassessments(), [])
        self.assertEqual(self.engine.runtime['activities'][opened['owner_activity_id']], before)
        self.engine.runtime['executions'][eid]['status'] = 'ended'
        self.assertEqual(self.engine._settle_assessment_reassessments(), [opened['review_cycle_id']])
        self.assertEqual(self.engine.runtime['activities'][opened['owner_activity_id']]['status'], 'finished')

    def test_replay_cannot_reuse_ordinary_review_as_a_different_judgment_purpose(self):
        original, assessment = self.completed()
        proposal = knowledge.assessment_reassessment_proposal(self.engine.instance, assessment['id'], runtime=self.engine.runtime)
        proposal['revision'] = original['revision'] + 1
        cycle = rc.start_review(proposal, original['reviewer_slots'], previous=original,
            policy=original['review_policy'], scope_assessment=original['scope_assessment'])
        cycle['id'] = 'RC-other-purpose'
        for index in range(len(cycle['reviewer_slots'])):
            action = rc.next_actions(cycle)[0]
            cycle = rc.accept_result(cycle, action, review_stage_output(cycle, 'initial'), 'other-purpose-' + str(index))
        before = deepcopy((cycle, self.engine.runtime))
        with self.assertRaisesRegex(ValueError, 'previous review has a different judgment purpose'):
            rc.validate_sealed_review(cycle, self.engine.runtime, clock=self.engine.ports.clock, at=self.engine.ports.clock.now())
        self.assertEqual((cycle, self.engine.runtime), before)
