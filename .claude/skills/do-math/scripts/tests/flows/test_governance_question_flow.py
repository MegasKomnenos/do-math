"""A worker's user question, its answer and the next worker's input (``question_engine``, ``governance``).

The owner of a restored public activation runs the research roles through
the workers: the model double answers them with the default responder, except
that the research work waits on two questions and routes the first to the user
in its activity extensions (as the legacy local runner wrote them). The user
then acts by public control. The scene runs several role calls, longer than one
Sim test's budget.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from runner_fixtures import ScriptedRunner, common as role_output
from support.model import ModelDouble
from support.sim import Sim, warm_template

setUpModule = warm_template

QUESTIONS = ['Choose option one or two?', 'Research the remaining lemma.']


class RoutingResponder(ScriptedRunner):
    """The default responder, but research work waits on ``QUESTIONS`` and routes the first to the user."""

    def respond(self, role, ctx, workspace):
        if role != 'research_work':
            return super().respond(role, ctx, workspace)
        output = role_output('research_work')
        output.update(outcome='waiting', report='A user choice is needed.', remaining_work=['Use the chosen option.'],
                      checkpoint='Waiting for the user.', questions=list(QUESTIONS))
        (Path(workspace) / 'activity-extensions.json').write_bytes(canonical_json({'question_routes': [
            {'question_index': 0, 'owner': 'user', 'target_ids': [ctx['action']['target']],
             'reason': 'The user owns this choice.'}]}))
        return output


class QuestionFlowTests(unittest.TestCase):
    def test_answer_closes_only_its_question_and_reaches_the_next_worker(self):
        """About 7 s: the preparation, contract review, plan and research work are role calls through the worker."""
        sim = Sim.activated()
        sim.model = ModelDouble(sim.clock, RoutingResponder())

        def worked(s):
            return [row for row in s.runtime['executions'].values()
                    if row.get('role') == 'research_work' and row.get('status') == 'ended']
        sim.run_until(worked, max_steps=30)
        engine = sim.engine
        (work,) = worked(sim)
        task = work['action']['target']
        rows = [row for row in engine._question_view() if row['origin_execution_id'] == work['id']]
        self.assertEqual(sorted((row['owner'], row['text']) for row in rows),
                         [('research', QUESTIONS[1]), ('user', QUESTIONS[0])], work)
        user = next(row for row in rows if row['owner'] == 'user')
        research = next(row for row in rows if row['owner'] == 'research')
        self.assertEqual(engine.status()['questions'], [QUESTIONS[0]])
        sim.control('input', text='Unrelated information.')
        engine.process_controls()
        self.assertEqual(next(row for row in engine.runtime['question_links'] if row['id'] == user['id'])['status'], 'open')
        sim.control('decision', text='Use option one.', config={'change': {
            'kind': 'question_answer', 'text': 'Use option one.', 'target_ids': [task],
            'resolves_questions': [user['id']]}})
        engine.process_controls()
        with tempfile.TemporaryDirectory() as reader:
            context = engine._context({'id': 'next', 'role': 'research_work', 'target': task, 'revision_targets': {}},
                                      Path(reader))
        answered = next(row for row in context['question_links'] if row['id'] == user['id'])
        self.assertEqual(answered['status'], 'resolved')
        self.assertEqual(answered['resolution']['change']['text'], 'Use option one.')
        self.assertEqual(next(row for row in context['question_links'] if row['id'] == research['id'])['status'], 'open')
        self.assertEqual(engine.status()['questions'], [])


if __name__ == '__main__':
    unittest.main()
