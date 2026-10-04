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
from support.role_input_requirements import observe_judgment_inputs


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
        with observe_judgment_inputs(self) as prepared:
            drive(self, sim)
        from do_math.role_input_requirements import REVIEW_STAGE_INPUTS
        self.assertEqual({row['action']['stage'] for row in prepared if row['role'] == 'identity_review'},
                         set(REVIEW_STAGE_INPUTS))
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
        with observe_judgment_inputs(self) as prepared:
            drive(self, sim, predicate=lambda s: any(bundle['source']['text'] == NEW_GOAL and bundle.get('check')
                                                     for bundle in s.runtime.get('intent_imports', {}).values()))
        self.assertEqual([row['interpretation_stage'] for row in prepared if row['role'] == 'intent_interpretation'],
                         ['interpret', 'check'])
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


class PublicGovernancePlanningTests(unittest.TestCase):
    def test_public_decisions_deliver_one_plan_and_replays_deliver_none(self):
        from do_math import planning
        from support.academic_scenes import MANUSCRIPT
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.model import Answer
        from support.planning_contract_inputs import prepared_sim, only_task, produce_task
        from support.sim import Sim
        for variant in ('academic', 'grant', 'waive', 'transfer'):
            with self.subTest(variant=variant):
                sim = prepared_sim() if variant in ('waive', 'transfer') else Sim.activated()
                if variant == 'academic':
                    change = charter_change(sim.engine, academic_requirements=[MANUSCRIPT])
                    field = 'decision_id'
                elif variant == 'grant':
                    change = {'kind': 'grant', 'grant': {'id': 'GR-new-maintenance', 'kind': 'local',
                        'roles': ['maintenance'], 'reuse': 'reusable'}}
                    field = 'decision_id'
                else:
                    task = only_task(sim)
                    change = {'kind': 'task_scope', 'task_id': task['id'], 'disposition': variant,
                        'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                        'obligation_ids': [task['completion_obligations'][0]['id']], 'reason': 'Approve the named scope change.'}
                    if variant == 'transfer':
                        change['target_task_id'] = produce_task(sim, 'scope recipient')
                    field = 'scope_decision_id'
                clear_work(sim)
                sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
                def defer(out, context):
                    out['goal_audit'] = False
                    for row in out['dispositions']:
                        row.update(kind='not_selected', next_owner='research_plan',
                            revisit={'at': '2090-01-02T00:00:00+00:00', 'event_refs': []})
                    return out
                sim.model.on('research_plan').reply(Answer(defer))
                request_id = 'UC-governance-plan-' + variant
                options = {'text': 'Authorize this planning trigger.', 'config': {'change': change}, 'request_id': request_id}
                applied(sim, 'decision', **options)
                decision, = [key for key, value in sim.instance['decisions'].items() if value.get('source_ref') == request_id]
                request, = [a for a in sim.runtime['queue'] if a['role'] == 'research_plan' and a.get(field) == decision]
                before = assert_call_records(self, sim)
                sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
                sim.run_until(lambda current: any(c['action']['id'] == request['id'] for c in current.model.calls), max_steps=8)
                execution, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == request['id']]
                self.assertEqual(execution['outcome'], 'output_accepted',
                    {'error': execution.get('error'), 'issues': [r.get('result', {}).get('issues') for r in sim.model.receipts]})
                self.assertEqual(execution['action'][field], decision)
                self.assertEqual(assert_call_records(self, sim)['research_plan'] - before['research_plan'], 1)
                replay = applied(sim, 'decision', **options)
                self.assertTrue(replay['replayed'])
                for _ in range(2):
                    sim.step()
                    assert_call_records(self, sim)
                    self.assertEqual(sum(c['action'].get(field) == decision for c in sim.model.calls), 1)
                self.assertEqual(sum(value.get('source_ref') == request_id for value in sim.instance['decisions'].values()), 1)
                self.assertEqual(assert_call_records(self, sim)['operational_review'], before['operational_review'])

    def test_initialization_grant_does_not_open_a_research_plan(self):
        import tempfile
        from pathlib import Path
        from support.cross_contracts import assert_call_records
        from support.sim import Sim
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(Path(directory))
            applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
                'id': 'GR-before-adoption', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable'}}})
            self.assertIn('GR-before-adoption', sim.instance['grants'])
            self.assertFalse(any(a['role'] == 'research_plan' for a in sim.runtime['queue']))
            for _ in range(2):
                sim.step()
                self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)


if __name__ == '__main__':
    unittest.main()
