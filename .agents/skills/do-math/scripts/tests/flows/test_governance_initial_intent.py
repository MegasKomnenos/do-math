"""The initial input's checked interpretation waits for the user during public activation (``governance_engine``,
``initialization_engine``).

Each scene is a public activation on a Sim whose initial interpretation, answered
by the model double through the worker, needs the user: a blocking question, or
a change that needs the user's exact approval. The independent check is the
default responder's. The activation stops where the instance waits; the test
then acts as the user does, by public control. Each scene is longer than one
Sim test's budget.
"""
import tempfile
import unittest

from do_math.initialization import grant_current
from support.governance_sim import initial_sim


class InitialBlockingQuestionTests(unittest.TestCase):
    def test_initial_blocking_question_waits_and_answer_reopens_original_once(self):
        """About 5 s: the public activation with the initial interpretation and its check as two model calls."""
        with tempfile.TemporaryDirectory() as directory:
            sim = initial_sim(directory, question='Which domain?')
            engine = sim.engine
            lifecycle = engine.instance['lifecycle']
            input_id = lifecycle['input_id']
            (wait,) = engine.runtime['waiting_actions'].values()
            self.assertEqual(wait['kind'], 'import_user_decision')
            bundle = engine.runtime['intent_imports'][wait['import_id']]
            self.assertEqual((bundle['input_ref'], bundle['application']['status']), (input_id, 'awaiting_decision'))
            # Nothing but the waiting import keeps the initial interpretation from the queue:
            # the adopted profile's capability and an initial grant for interpretation are current.
            adoption = lifecycle['adoption']
            self.assertTrue(engine._capability_requirements(adoption['initial_profile_ref'])['satisfied'])
            self.assertTrue(any(grant_current(engine.instance, gid, engine._lifecycle_now(), initial=True)
                                and 'intent_interpretation' in engine.instance['grants'][gid]['roles']
                                for gid in adoption['initial_grant_ids']))
            queue = list(engine.runtime['queue'])
            for _ in range(3):
                engine._queue_initial_intent()
            self.assertEqual(engine.runtime['queue'], queue)
            question = next(row for row in engine.runtime['question_links']
                            if row.get('source_kind') == 'intent_import' and row.get('source_id') == bundle['id'])
            sim.control('decision', text='Natural numbers', config={'change': {
                'kind': 'question_answer', 'text': 'Natural numbers', 'target_ids': [engine.instance['id']],
                'resolves_questions': [question['id']]}})
            engine.process_controls()
            engine._resume_import_question_waits()
            engine._resume_import_question_waits()
            after = engine.runtime['queue']
            self.assertEqual([row for row in after if row in queue], queue)
            (reopened,) = [row for row in after if row not in queue]
            self.assertEqual(reopened['role'], 'intent_interpretation')
            self.assertEqual(reopened['previous_import_id'], bundle['id'])
            self.assertEqual(reopened['target'], input_id)
            self.assertEqual(engine.runtime['waiting_actions'], {})


if __name__ == '__main__':
    unittest.main()
