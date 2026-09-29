import sys
import unittest
from pathlib import Path
from unittest.mock import create_autospec

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import integration
from do_math.engine import control
from do_math.question_engine import QuestionEngineMixin
from do_math.canonical import canonical_json
from do_math.repository import ResearchRepository
from engine_fixtures import context_engine
from purpose_fixtures import ActivatedPurposeHarness, parse_context, purpose_copy, PurposeRunner
from research_fixtures import bare_engine, local_job_runner, producer_result
from runner_fixtures import common as role_output


class QuestionFlowTests(ActivatedPurposeHarness):
    def test_answer_closes_only_its_question_and_reaches_the_next_worker(self):
        # From a prepared task: its worker's question route is the subject.
        engine, _ = purpose_copy(self, PurposeRunner(), until='prepared',
                                 config=self.fixture_config(operator_enabled=False, scholarly_enabled=False))
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_work')
        task = engine.runtime['tasks'][action['target']]
        engine.runtime['queue'] = [action]
        class Runner:
            @local_job_runner
            def run(inner, **args):
                args['on_started']({'fixture': True})
                context = parse_context(args['prompt'], args['workspace'])
                output = role_output('research_work')
                output.update(outcome='waiting', report='A user choice is needed.', remaining_work=['Use the chosen option.'],
                    checkpoint='Waiting for the user.', questions=['Choose option one or two?', 'Research the remaining lemma.'])
                (args['workspace'] / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [
                    {'question_index': 0, 'owner': 'user', 'target_ids': [task['id']], 'reason': 'The user owns this choice.'}]}))
                return producer_result({'status': 'completed', 'output': output, 'usage': {}}, args)
        engine.runner = Runner()
        engine._save()
        engine.run(max_steps=1)
        rows = engine._question_view()
        self.assertTrue(any(row['owner'] == 'user' for row in rows),
            [{key: ex.get(key) for key in ('role', 'outcome', 'error')}
             for ex in engine.runtime['executions'].values()])
        user = next(row for row in rows if row['owner'] == 'user')
        research = next(row for row in rows if row['owner'] == 'research')
        self.assertEqual(engine.status()['questions'], ['Choose option one or two?'])
        control(self.repo, engine.instance['id'], 'input', text='Unrelated information.')
        engine.process_controls()
        self.assertEqual(next(row for row in engine.runtime['question_links'] if row['id'] == user['id'])['status'], 'open')
        control(self.repo, engine.instance['id'], 'decision', config={'change': {
            'kind': 'question_answer', 'text': 'Use option one.', 'target_ids': [task['id']],
            'resolves_questions': [user['id']]}})
        engine.process_controls()
        context = engine._context({'id': 'next', 'role': 'research_work', 'target': task['id'], 'revision_targets': {}}, self.root / 'next-reader')
        answered = next(row for row in context['question_links'] if row['id'] == user['id'])
        self.assertEqual(answered['status'], 'resolved')
        self.assertEqual(answered['resolution']['change']['text'], 'Use option one.')
        self.assertEqual(next(row for row in context['question_links'] if row['id'] == research['id'])['status'], 'open')
        self.assertEqual(engine.status()['questions'], [])


class QuestionSourceTests(unittest.TestCase):
    def test_accepted_maintenance_question_reads_its_single_sealed_source(self):
        engine = context_engine()
        action = {'id': 'AC-sealed-question', 'role': 'maintenance'}
        ref = 'runtime/artifacts/BA-sealed/submission/output.json'
        engine.runtime['executions']['EX-sealed-question'] = {
            'id': 'EX-sealed-question', 'role': 'maintenance', 'status': 'ended',
            'action': action, 'submission_intent': {'output_ref': ref}}
        output = {**role_output('maintenance'), 'questions': ['Which result should be used?']}
        engine._record_output_questions(action, output, 'EX-sealed-question')
        engine._record_output_questions(action, output, 'EX-sealed-question')
        self.assertEqual(len(engine.runtime['question_links']), 1)
        self.assertEqual(engine.runtime['question_links'][0]['source_ref'], ref)
        engine.store.read_many.side_effect = lambda paths, snapshot: {ref: canonical_json(output)}
        self.assertEqual(engine._question_view()[0]['text'], 'Which result should be used?')

    def test_running_maintenance_question_preview_uses_captured_candidate_only(self):
        engine = context_engine()
        action = {'id': 'AC-preview-question', 'role': 'maintenance'}
        execution_id = 'EX-preview-question'
        engine.runtime['executions'][execution_id] = {
            'id': execution_id, 'role': 'maintenance', 'status': 'running', 'action': action}
        output = {**role_output('maintenance'), 'questions': ['Which condition needs a decision?']}
        context = {'action': action, 'snapshot': engine.head, 'execution_id': execution_id}
        ref = 'runtime/artifacts/preview/' + execution_id + '/output.json'
        artifacts = {ref: canonical_json(output)}
        before = canonical_json(engine.runtime)
        preview = integration.preview_bundles(engine.instance, engine.runtime, output, {}, context,
            execution_id=execution_id,
            apply_bundle=lambda instance, runtime, bundle: engine._apply_bundle_candidate(
                instance, runtime, bundle, action=action, execution_id=execution_id,
                extensions={}, question_source_ref=ref),
            validate_current=lambda *_: None,
            validate_candidate=lambda instance, runtime, bundle: engine._validate_bundle_candidate(
                instance, runtime, bundle, artifacts=artifacts))
        self.assertEqual(preview['status'], 'accepted', preview['issues'])
        self.assertEqual(canonical_json(engine.runtime), before)
        self.assertEqual(engine.store.validate_candidate.call_count, 1)
        self.assertEqual(preview['runtime']['question_links'][0]['source_ref'], ref)
        self.assertNotIn('artifact_bundle', engine.runtime['executions'][execution_id])

    def test_operational_question_uses_exact_execution_or_sealed_source_coordinate(self):
        engine = bare_engine()
        engine.instance = {'decisions': {}}
        engine.head = 'fixed'
        engine.store = create_autospec(ResearchRepository, instance=True)
        engine.store.read_many.return_value = {'sealed-output.json': canonical_json({
            'disposition': {'question': 'Question from the sealed response'}})}
        engine.runtime = {'executions': {
            'EX-current': {'id': 'EX-current', 'role': 'operational_review',
                           'output': {'disposition': {'question': 'Choose the next action'}}},
            'EX-missing': {'id': 'EX-missing', 'role': 'operational_review', 'output': {}}},
            'question_links': [
                {'id': 'QU-current', 'origin_execution_id': 'EX-current',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-wrong', 'origin_execution_id': 'EX-current',
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-missing', 'origin_execution_id': 'EX-missing',
                 'origin_field': 'output/disposition/question', 'owner': 'user', 'status': 'open'},
                {'id': 'QU-sealed', 'origin_execution_id': 'EX-current', 'source_ref': 'sealed-output.json',
                 'origin_field': 'disposition/question', 'owner': 'user', 'status': 'open'}]}
        view = {row['id']: row for row in QuestionEngineMixin._question_view(engine)}
        self.assertEqual(view['QU-current']['text'], 'Choose the next action')
        self.assertEqual(view['QU-sealed']['text'], 'Question from the sealed response')
        for identifier in ('QU-wrong', 'QU-missing'):
            self.assertIsNone(view[identifier]['text'])
            self.assertEqual(view[identifier]['source_status'], 'unavailable')
        self.assertEqual(QuestionEngineMixin._user_questions(engine),
                         ['Choose the next action', 'Question from the sealed response'])


if __name__ == '__main__':
    import unittest
    unittest.main()
