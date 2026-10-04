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


class PublicJudgmentRequestTests(unittest.TestCase):
    def test_conversation_and_submission_records_do_not_automatically_open_judgments(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
        applied(sim, 'conversation', config={'operation': 'attach', 'id': 'talk-events', 'generation': 1,
            'lease_seconds': 60, 'disconnect_policy': 'continue_authorized'})
        for operation in ('heartbeat', 'detach'):
            applied(sim, 'conversation', config={'operation': operation, 'id': 'talk-events', 'generation': 1})
        events = [e for e in sim.runtime['events'] if e.get('target') == 'talk-events']
        self.assertEqual({e['kind'] for e in events},
                         {'conversation_attach', 'conversation_heartbeat', 'conversation_detach', 'conversation_lost'})
        self.assertTrue(all(e['id'] not in sim.runtime['pending_events'] for e in events))
        for _ in range(2):
            sim.step()
            counts = assert_call_records(self, sim)
            self.assertEqual(counts['research_plan'], 0)
            self.assertEqual(counts['operational_review'], 0)
        checked = [e for e in sim.runtime['events'] if e['kind'] == 'submission_checked']
        self.assertTrue(checked)
        self.assertTrue(all(e['id'] not in sim.runtime['pending_events'] for e in checked))

    def test_new_decision_event_during_a_plan_is_assigned_to_a_later_plan(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.model import amend
        from support.submission_calls import applied_now, submission_model
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        def grant(identifier):
            return {'change': {'kind': 'grant', 'grant': {'id': identifier, 'kind': 'local',
                'roles': ['maintenance'], 'reuse': 'reusable'}}}
        first_control = applied(sim, 'decision', config=grant('GR-event-first'))
        first_id, = [a['id'] for a in sim.runtime['queue'] if a['role'] == 'research_plan']
        first_event, = [e['id'] for e in sim.runtime['events']
                       if e.get('source_ref') == first_control['request_id'] and e['kind'] == 'user_decision_applied']
        model = submission_model(sim, DefaultResponder(preparation_candidates=[], plan_assessments=False))
        model.on('research_plan').reply(amend(goal_audit=False))
        arrived = []
        fixed = []
        def while_planning(context, workspace):
            if context['action']['id'] == first_id:
                fixed.append(deepcopy(context['action']))
                arrived.append(applied_now(sim, 'decision', text='An independent permission arrived.',
                                           config=grant('GR-event-later')))
                self.assertEqual(context['action'], fixed[0])
        model.before('research_plan', while_planning)
        sim.step()
        second_event, = [e['id'] for e in sim.runtime['events']
                        if e.get('source_ref') == arrived[0]['request_id'] and e['kind'] == 'user_decision_applied']
        first, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == first_id]
        self.assertEqual(first['outcome'], 'output_accepted', first.get('error'))
        self.assertIn(first_event, first['action']['event_refs'])
        self.assertNotIn(second_event, first['action']['event_refs'])
        sim.run_until(lambda current: any(second_event in c['action'].get('event_refs', [])
                                         for c in current.model.calls), max_steps=8)
        later, = [e for e in sim.runtime['executions'].values() if second_event in e['action'].get('event_refs', [])]
        self.assertEqual(later['outcome'], 'output_accepted', later.get('error'))
        self.assertNotEqual(first['action']['id'], later['action']['id'])
        self.assertNotIn(first_event, sim.runtime['pending_events'])
        self.assertNotIn(second_event, sim.runtime['pending_events'])
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            for event in (first_event, second_event):
                self.assertEqual(sum(event in c['action'].get('event_refs', []) for c in model.calls), 1)

    def test_explicit_judgment_requests_run_once_and_replay_without_another_call(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.model import amend
        from support.scheduling_recovery import failed_plan_sim, failed_execution
        from support.sim import Sim
        for role in ('research_plan', 'operational_review'):
            with self.subTest(role=role):
                sim = failed_plan_sim() if role == 'operational_review' else Sim.activated()
                clear_work(sim)
                sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
                sim.model.on('research_plan').reply(amend(goal_audit=False))
                config = {'role': role}
                if role == 'operational_review':
                    config['target'] = failed_execution(sim)['id']
                request_id = 'UC-direct-' + role
                options = {'text': 'Judge the preserved current facts.', 'config': config, 'request_id': request_id}
                applied(sim, 'request', **options)
                request, = [a for a in sim.runtime['queue'] if a.get('requested_by') == request_id]
                before = assert_call_records(self, sim)
                sim.run_until(lambda current: any(c['action']['id'] == request['id'] for c in current.model.calls), max_steps=8)
                self.assertEqual(assert_call_records(self, sim)[role] - before[role], 1)
                execution, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == request['id']]
                self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
                self.assertEqual(execution['action'].get('target'), config.get('target'))
                self.assertTrue(applied(sim, 'request', **options)['replayed'])
                for _ in range(2):
                    sim.step()
                    assert_call_records(self, sim)
                    self.assertEqual(sum(c['action'].get('requested_by') == request_id for c in sim.model.calls), 1)

    def test_missing_operational_target_is_rejected_without_a_judgment_call(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.sim import Sim
        sim = Sim.activated()
        clear_work(sim)
        sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
        for target in (None, 'EX-not-present'):
            with self.subTest(target=target):
                config = {'role': 'operational_review'}
                if target is not None:
                    config['target'] = target
                with self.assertRaisesRegex(ValueError, '^operational review requires an existing execution ID$'):
                    sim.control('request', config=config)
        for _ in range(2):
            sim.step()
            counts = assert_call_records(self, sim)
            self.assertEqual(counts['operational_review'], 0)
            self.assertEqual(counts['research_plan'], 0)


if __name__ == '__main__':
    unittest.main()
