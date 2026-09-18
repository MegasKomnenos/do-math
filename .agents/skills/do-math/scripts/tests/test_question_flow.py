from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control
from do_math.repository import canonical_json
from test_purpose_engine import PurposeHarness, common, parse_context
from test_engine import common as role_output


class QuestionFlowTests(PurposeHarness):
    def test_answer_closes_only_its_question_and_reaches_the_next_worker(self):
        engine, _ = self.make(operator_enabled=False, scholarly_enabled=False)
        engine.run(max_steps=2)
        task = next(iter(engine.runtime['tasks'].values()))
        task['status'] = 'performing'
        engine.runtime['queue'] = []
        engine._enqueue('research_work', task['id'])
        class Runner:
            def run(inner, **args):
                args['on_started']({'fixture': True})
                context = parse_context(args['prompt'], args['workspace'])
                output = role_output('research_work')
                output.update(outcome='waiting', report='A user choice is needed.', remaining_work=['Use the chosen option.'],
                    checkpoint='Waiting for the user.', questions=['Choose option one or two?', 'Research the remaining lemma.'])
                (args['workspace'] / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [
                    {'question_index': 0, 'owner': 'user', 'target_ids': [task['id']], 'reason': 'The user owns this choice.'}]}))
                return {'status': 'completed', 'output': output, 'usage': {}}
        engine.runner = Runner()
        engine._save()
        engine.run(max_steps=1)
        rows = engine._question_view()
        user = next(row for row in rows if row['owner'] == 'user')
        research = next(row for row in rows if row['owner'] == 'research')
        self.assertEqual(engine.status()['questions'], ['Choose option one or two?'])
        control(self.repo, engine.instance['id'], 'input', text='Unrelated information.')
        engine.process_controls()
        self.assertEqual(next(row for row in engine.runtime['question_links'] if row['id'] == user['id'])['status'], 'open')
        control(self.repo, engine.instance['id'], 'decision', config={'change': {
            'kind': 'question_answer', 'text': 'Use option one.', 'resolves_questions': [user['id']]}})
        engine.process_controls()
        context = engine._context({'id': 'next', 'role': 'research_work', 'target': task['id'], 'revision_targets': {}}, self.root / 'next-reader')
        answered = next(row for row in context['question_links'] if row['id'] == user['id'])
        self.assertEqual(answered['status'], 'resolved')
        self.assertEqual(answered['resolution']['change']['text'], 'Use option one.')
        self.assertEqual(next(row for row in context['question_links'] if row['id'] == research['id'])['status'], 'open')
        self.assertEqual(engine.status()['questions'], [])


if __name__ == '__main__':
    import unittest
    unittest.main()
