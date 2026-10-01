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

This module: the identity review's objection and answer, and the public policy and input decisions.
"""
from copy import deepcopy
import unittest

from do_math.knowledge_records import usable_links
from support.purpose_answers import NEW_GOAL
from support.state_builders import charter_change, policy_change
from support.engine_lifecycle import applied
from support.engine_purpose import PurposeResponder, drive, purpose_sim


class PurposeFlowTests(unittest.TestCase):
    def start(self, scenario='direct', **config):
        sim = purpose_sim(**config)
        responder = sim.model.responder = PurposeResponder(scenario)
        return sim, responder

    def test_objection_judgment_answer_and_final_approval_use_real_engine(self):
        """About 70 s, over the 60 s flow budget: eleven identity review calls over two rounds run with every other role to the goal."""
        # The round cap is 3, so a cycle that closes in round 2 was closed by the
        # confirmed withdrawal, not by the cap.
        sim, responder = self.start('dispute', review_rounds=3)
        # Runs to the goal: the goal audit answer checks that, after the withdrawn
        # objection, it receives only the final matching assessment.
        drive(self, sim)
        reviews = [call for call in responder.calls if call['role'] == 'identity_review']
        self.assertEqual([call['action']['stage'] for call in reviews],
                         ['scope', 'initial', 'initial', 'organize', 'judge', 'judge', 'judge', 'answer',
                          'judge', 'judge', 'judge'])
        self.assertEqual(reviews[7]['action']['slot'], 'initial-0')
        self.assertEqual(set(reviews[2]['context']['role_review']['completed_results']), {'scope:1:scope'})
        self.assertFalse(any(entry['action']['stage'] == 'judge'
                             for entry in reviews[5]['context']['role_review']['completed_results'].values()))
        item = next(row for row in sim.instance['knowledge'].values() if row['title'] == 'Natural zero identity')
        links = usable_links(sim.instance, item['id'])
        self.assertTrue(links)
        final = sim.instance['identity_assessments'][links[0]['assessment_id']]
        self.assertEqual(final['decision'], 'match')
        self.assertEqual(len(final['execution_ids']), 3)
        cycle = sim.runtime['review_cycles'][item['review_cycle_id']]
        self.assertEqual((cycle['decision'], cycle['round']), ('match', 2))

    def test_policy_control_invalidates_old_contract_approval_before_work(self):
        sim, responder = self.start()
        engine = sim.engine
        drive(self, sim, predicate=lambda s: any(task.get('reviews') for task in s.runtime['tasks'].values()))
        task = next(row for row in engine.runtime['tasks'].values() if row.get('reviews'))
        previous_policy = engine._governance()['policy_revision']
        self.assertEqual(task['reviews'][0]['policy_revision'], previous_policy)
        applied(sim, 'decision', config={'change': policy_change(
            engine, 'Every report must name the natural-number domain explicitly.')})
        current_policy = engine._governance()['policy_revision']
        self.assertNotEqual(current_policy, previous_policy)
        self.assertEqual(engine._task_readiness[task['id']]['state'], 'not_ready')

        def new_edition_work(call):
            return call['role'] == 'research_work' and call['context']['governance']['policy_revision'] == current_policy
        # Research work reads the policy edition from its governance input.
        drive(self, sim, predicate=lambda s: any(new_edition_work(call) for call in responder.calls))
        task = sim.runtime['tasks'][task['id']]
        self.assertTrue(any(review['policy_revision'] == current_policy and review['decision'] == 'approved'
                            for review in task['reviews']))
        work = next(call for call in responder.calls if new_edition_work(call))
        self.assertEqual(work['context']['governance']['policy_revision'], current_policy)
        self.assertTrue(any(row['role'] == 'research_work' and row.get('outcome') == 'output_accepted'
                            for row in sim.runtime['executions'].values()))

    def test_user_input_is_independently_checked_without_becoming_goal_authority(self):
        sim, responder = self.start()
        engine = sim.engine
        before = deepcopy(engine._governance()['charter'])
        sim.control('input', text=NEW_GOAL)
        drive(self, sim, predicate=lambda s: any(bundle['source']['text'] == NEW_GOAL and bundle.get('check')
                                                 for bundle in s.runtime.get('intent_imports', {}).values()))
        bundle = next(row for row in sim.runtime['intent_imports'].values() if row['source']['text'] == NEW_GOAL)
        self.assertNotEqual(bundle['execution_id'], bundle['check']['execution_id'])
        self.assertEqual(bundle['check']['decision'], 'approved')
        self.assertEqual(engine._governance()['charter'], before)
        self.assertTrue(any(row['kind'] == 'import_application_authority' for row in sim.runtime['waiting_actions'].values()))
        # An exact public decision, separate from the model's semantic check,
        # authorizes the new goal and preserves the previous charter.
        applied(sim, 'decision', config={'change': charter_change(engine, goal=NEW_GOAL, success_criteria=[NEW_GOAL],
                                                                    included_scope=[NEW_GOAL])})
        self.assertEqual(engine._governance()['goal'], NEW_GOAL)
        self.assertEqual(sim.instance['governance'][before['id']]['status'], 'superseded')


if __name__ == '__main__':
    unittest.main()
