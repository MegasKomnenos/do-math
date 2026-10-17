"""Model assessments of academic tasks on the real engine without a model call: the batched assessment-only
preparation, its schema, its deferral wait and its failure hold (``planning_engine``, ``lifecycle_engine``,
``dispatch_engine``; layer 2), moved from ``test_model_assessment_flow``'s ``AssessmentFlowTests``.

The start is ``support.academic_scenes.assessment_sim``: the legacy
``assessment_preparation_instance`` on the public activation with the purpose
configuration, whose published readiness replaced the two academic tasks'
contract reviews with one assessment-only preparation. The tests that run a
preparation call are ``flows.test_academic_preparation_calls``.
"""
import json
import unittest

from do_math.canonical import canonical_json
from do_math.model_policy import MODELS
from support.academic_scenes import ACADEMIC_TASKS, assessment_sim


def assessment_action(engine):
    return next(a for a in engine.runtime['queue'] if a.get('assessment_targets'))


class AssessmentFlowTests(unittest.TestCase):
    def test_missing_academic_assessments_are_batched_before_any_contract_review(self):
        engine = assessment_sim().engine
        engine._refresh_readiness()
        queue = engine.runtime['queue']
        self.assertFalse(any(a['role'] == 'task_contract_review' for a in queue))
        preparations = [a for a in queue if a.get('assessment_targets')]
        self.assertEqual(len(preparations), 1)
        action = preparations[0]
        self.assertEqual(action['role'], 'research_preparation')
        self.assertEqual(set(action['assessment_targets']), set(engine.runtime['tasks']))
        self.assertEqual(set(engine.runtime['tasks']), set(ACADEMIC_TASKS))
        self.assertEqual(engine._select_model(action)['model'], MODELS['high'])
        engine._refresh_readiness()
        self.assertEqual(len([a for a in engine.runtime['queue'] if a.get('assessment_targets')]), 1)

    def test_assessment_request_does_not_absorb_an_ordinary_preparation(self):
        engine = assessment_sim().engine
        engine._refresh_readiness()
        engine._enqueue('research_preparation', reason='Explore a separate research direction')
        requests = [a for a in engine.runtime['queue'] if a['role'] == 'research_preparation']
        self.assertEqual(len(requests), 2)
        self.assertEqual(len([a for a in requests if a.get('assessment_targets')]), 1)

    def test_assessment_only_schema_makes_contract_creation_impossible(self):
        engine = assessment_sim().engine
        engine._refresh_readiness()
        schema = engine._response_schema(assessment_action(engine))
        self.assertEqual(schema['properties']['candidates'].get('maxItems'), 0)

    def test_saved_deferral_with_sources_does_not_retry_without_input_change(self):
        engine = assessment_sim().engine
        engine.instance['sources'] = [{'name': 'paper.txt', 'path': 'sources/paper.txt', 'sha256': 'a' * 64}]
        engine._refresh_readiness()
        action = assessment_action(engine)
        engine.runtime['queue'] = []
        engine.runtime['waiting_actions'] = {action['id']: json.loads(canonical_json({
            'action': action, 'kind': 'model_assessment_input', 'input_version': engine._assessment_input_version()}))}
        engine._ensure_model_assessments()
        self.assertIn(action['id'], engine.runtime['waiting_actions'])
        self.assertFalse(any(a.get('assessment_targets') for a in engine.runtime['queue']))
        engine.instance['sources'][0]['sha256'] = 'b' * 64
        engine._ensure_model_assessments()
        self.assertNotIn(action['id'], engine.runtime['waiting_actions'])
        self.assertTrue(any(a.get('assessment_targets') for a in engine.runtime['queue']))

    def test_completed_normal_preparation_does_not_resolve_a_failed_assessment_request(self):
        engine = assessment_sim().engine
        engine._refresh_readiness()
        action = assessment_action(engine)
        held = {'action': action, 'kind': 'output_validation'}
        engine.runtime['waiting_actions'] = {action['id']: held}
        engine._resolve_failed_actions({'role': 'research_preparation'}, 'EX-normal')
        self.assertEqual(engine.runtime['waiting_actions'], {action['id']: held})


if __name__ == '__main__':
    unittest.main()
