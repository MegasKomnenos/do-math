"""Assigned academic preparations and contract reviews that run through a model call on the real engine, moved
from ``test_academic_preparation`` and ``test_model_assessment_flow``.

Each test restores an academic start state of ``support.academic_scenes`` and
lets the owner start the queued preparation or review: the Jobs fake runs the
product's Codex worker in process, the model double answers from the actual
role input by the test's responder, and the worker submits the draft with the
workspace submission tool, whose receipt the owner writes. The legacy tests ran
the same calls through scripted runners inside a real Windows Job; the owner's
receiving path is the same. One call with its submission and receipt takes
about two to three seconds, and some start states are themselves built by a
call, so these tests live in the flow folder.

The legacy tests reused two scenarios of one class from another (the deferral
wait and the late assessment, run again on a rejected contract); here both are
functions of this module that each pair of tests calls.
"""
from copy import deepcopy
import json
import unittest

from do_math import submission
from do_math.activities import wait_for
from do_math.canonical import canonical_json
from do_math.planning import contract_hash
from support.role_answers import candidate, contract_review, seal_response
from support.observation_inputs import prepared_rule_conditions
from support.default_responder import common, rating
from support.academic_scenes import (ACADEMIC_TASKS, assessment_sim, no_repair_sim, rejected_sim, rule_prepared,
                                     solved_sim, warm_assessment)
from support.engine_purpose import PurposeResponder
from support.purpose_answers import SOLVED_REQUIREMENT_CRITERIA

setUpModule = warm_assessment


def extensions(workspace, value):
    (workspace / 'activity-extensions.json').write_bytes(canonical_json(value))


class AssessingResponder:
    """Rates every assessment target and checks the sealed draft with the installed producer check.

    The legacy runner ran the installed ``check_submission.py --output`` in a child
    process; its process boundary is ``boundary.test_submission_installed_tool``.
    Here the same check (``submission.producer_check``) runs in process on the
    same sealed draft, and its verdict is kept in ``verdicts``.
    """

    def __init__(self, clock):
        self.clock, self.contexts, self.verdicts = clock, [], []

    def respond(self, role, context, workspace):
        self.contexts.append(context)
        output = {**common(role), 'candidates': []}
        extensions(workspace, {'model_assessments': [rating(task_id=tid)
                                                     for tid in context['action'].get('assessment_targets', {})]})
        sealed = deepcopy(output)
        seal_response(sealed, context, workspace)
        draft = workspace / '.scratch' / 'submission.json'
        draft.parent.mkdir(exist_ok=True)
        draft.write_bytes(canonical_json(sealed))
        self.verdicts.append(submission.producer_check(workspace, draft, clock=self.clock)['passed'])
        return output


class DeferringResponder:
    """Defers every assessment target and every observation-rule target to the user's input."""

    def __init__(self):
        self.roles = []

    def respond(self, role, context, workspace):
        self.roles.append(role)
        action = context['action']
        value = {'model_assessment_deferrals': [{'task_id': tid, 'reason': 'Need the missing source text.'}
                                                for tid in action['assessment_targets']]}
        if action.get('observation_rule_targets'):
            value['observation_rule_deferrals'] = [{'task_id': tid, 'reason': 'Need source text',
                                                    'missing_inputs': ['user_input'], 'next_owner': 'user'}
                                                   for tid in action['observation_rule_targets']]
        extensions(workspace, value)
        return {**common(role), 'candidates': []}


class RevisingResponder:
    """Rates its targets, and before it answers the user's revision of the first target's contract is published.

    The legacy runner asked the owner thread to publish the revision at its next
    pass (a replaced ``_check_installation``) and waited for it. On the Sim the
    call and the owner take turns, so while the call runs the owner is at its
    wait; the revision is published here, on the engine's state, before the call
    returns, which is the same order of events.
    """

    def __init__(self, sim):
        self.sim, self.revised = sim, []

    def respond(self, role, context, workspace):
        action = context['action']
        targets = action['assessment_targets']
        value = {'model_assessments': [rating(task_id=tid) for tid in targets]}
        if action.get('observation_rule_targets'):
            value['task_conditions'] = prepared_rule_conditions(action['observation_rule_targets'])
        extensions(workspace, value)
        engine = self.sim.engine
        tid = next(iter(targets))
        task = engine.runtime['tasks'][tid]
        task['revision'] += 1
        task['scope'] = {'included': ['A revised user requirement'], 'excluded': []}
        engine._save()
        self.revised.append(tid)
        return {**common(role), 'candidates': []}


def targeted_first(sim):
    """Put the assigned preparation first: a rejected-contract state can also hold a legitimate plan."""
    sim.engine.runtime['queue'].sort(key=lambda a: not bool(a.get('assessment_targets') or a.get('observation_rule_targets')))
    sim.engine._save()


def assert_deferral_waits_for_input(test, sim):
    """A deferring preparation leaves one question and holds; re-judging does not retry; the user's input resumes it."""
    engine = sim.engine
    targeted_first(sim)
    responder = sim.model.responder = DeferringResponder()
    sim.step()
    test.assertEqual(responder.roles, ['research_preparation'])
    test.assertEqual(len(engine.runtime['waiting_actions']), 1)
    held = next(iter(engine.runtime['waiting_actions'].values()))
    question = held['question']
    test.assertIn(question, engine.runtime['questions'])
    for _ in range(3):
        engine._refresh_readiness()
        test.assertFalse(any(a.get('assessment_targets') for a in engine.runtime['queue']))
    sim.control('input', text='The requested source is now available.')
    engine.process_controls()
    engine._refresh_readiness()  # the next scheduler pass reconciles the changed inputs
    test.assertNotIn(question, engine.runtime['questions'])
    test.assertTrue(any(a.get('assessment_targets') for a in engine.runtime['queue']))


def assert_late_assessment_preserved(test, sim):
    """An assessment returned after the user revised its target's contract is preserved, not applied, and asked again."""
    engine = sim.engine
    targeted_first(sim)
    responder = sim.model.responder = RevisingResponder(sim)
    sim.step()
    test.assertEqual(len(responder.revised), 1)
    execution = next(e for e in engine.runtime['executions'].values() if e['action'].get('assessment_targets'))
    test.assertEqual(execution['outcome'], 'execution_incomplete')
    test.assertEqual(execution['result_disposition']['kind'], 'preserved_after_target_change')
    test.assertTrue(all('model_assessment' not in t for t in engine.runtime['tasks'].values()))
    test.assertTrue(any(a.get('assessment_targets') for a in engine.runtime['queue']))


class RulePreparationCallTests(unittest.TestCase):
    def test_combined_preparation_preserves_user_terms_and_publishes_fresh_review(self):
        sim = rule_prepared()
        engine = sim.engine
        before = deepcopy(engine.runtime['tasks'])
        action = next(a for a in engine.runtime['queue'] if a.get('observation_rule_targets'))
        self.assertEqual(set(action['assessment_targets']), set(action['observation_rule_targets']))
        failed_id = 'AC-old-rules'
        failed_action = {'id': failed_id, 'role': 'research_work', 'target': next(iter(before))}
        activity = engine._activity_for_action(failed_action)
        wait_for(engine.runtime, activity['id'], kind='observation_rules', reason='missing rules', condition={'kind': 'observation_rules'},
                 next_owner='research_preparation', at=engine._lifecycle_now().isoformat())
        engine.runtime.setdefault('waiting_actions', {})[failed_id] = {'action': failed_action, 'kind': 'observation_rules',
                                                                       'reason': 'missing rules'}
        engine._save()
        # The legacy PurposeAnswers's answer: a rating for every assessment target, rules for every rule target.
        responder = sim.model.responder = PurposeResponder()
        sim.step()
        self.assertEqual([call['role'] for call in responder.calls], ['research_preparation'])
        runtime = sim.runtime
        self.assertNotIn(failed_id, runtime['waiting_actions'])
        self.assertEqual(runtime['activities'][activity['id']]['status'], 'finished')
        for tid, task in runtime['tasks'].items():
            for key in ('question', 'scope', 'expected', 'completion_obligations', 'academic_requirement_id', 'authority_refs'):
                self.assertEqual(task[key], before[tid][key])
            self.assertEqual(task['revision'], before[tid]['revision'] + 1)
            self.assertEqual(task['initial_observation_rules'], prepared_rule_conditions([tid])[0]['observation_rules'])
            self.assertEqual(task['model_assessment'], {'difficulty': 'low', 'importance': 'medium',
                                                        'reason': 'The fixture supplies a bounded natural-number identity'})
            reviews = [a for a in runtime['queue'] if a['role'] == 'task_contract_review' and a.get('target') == tid]
            self.assertEqual(len(reviews), 1)
            self.assertEqual(reviews[0]['contract_basis']['revision'], task['revision'])
        self.assertEqual(runtime['cycles'], 0)
        resolved = [row for row in runtime['history'] if row.get('kind') == 'observation_rules_resolved']
        self.assertEqual([row['action_id'] for row in resolved], [failed_id])


class AssessmentCallTests(unittest.TestCase):
    def test_assessment_only_run_preserves_user_contract_and_unblocks_independent_review(self):
        sim = assessment_sim()
        engine = sim.engine
        before = deepcopy(engine.runtime['tasks'])
        responder = sim.model.responder = AssessingResponder(sim.clock)
        sim.step()
        self.assertEqual(len(responder.contexts), 1)
        self.assertTrue(responder.contexts[0]['action'].get('assessment_targets'))
        self.assertEqual(responder.verdicts, [True])
        for tid, task in engine.runtime['tasks'].items():
            self.assertEqual(task['model_assessment'], rating())
            self.assertEqual({k: v for k, v in task.items() if k != 'model_assessment'}, before[tid])
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review']
        self.assertEqual({a['target'] for a in reviews}, set(before))
        self.assertTrue(all(engine._select_model(a)['tier'] == 'medium' for a in reviews))
        self.assertEqual(engine.runtime['cycles'], 0, 'assessment completion is not a new research preparation cycle')

    def test_deferred_assessment_waits_for_input_and_can_resume_without_stale_question(self):
        assert_deferral_waits_for_input(self, assessment_sim())

    def test_late_assessment_cannot_change_a_revised_user_contract(self):
        assert_late_assessment_preserved(self, assessment_sim())

    def test_receiver_parks_incomplete_new_candidate_assessments_without_creating_tasks(self):
        """The owner's check refuses the draft for the missing assessment; with no repair allowed the action is parked
        and no task is made. The refusal reason is read from the check the owner recorded for the call."""
        sim = no_repair_sim()
        engine = sim.engine
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', reason='Check missing candidate assessments')
        action_id = engine.runtime['queue'][-1]['id']
        engine._save()

        class MissingResponder:
            """A preparation with one candidate and no activity extensions: no assessment, no observation rules."""

            def respond(self, role, context, workspace):
                return {**common(role), 'candidates': [candidate('one')]}
        from support.model import default
        sim.model.responder = MissingResponder()
        sim.model.on('research_preparation').reply(default(expected_receipt='rejected'))
        sim.step()
        self.assertEqual(engine.runtime['tasks'], {})
        held = engine.runtime['waiting_actions'][action_id]
        self.assertEqual((held['kind'], held['reason']), (
            'output_validation', 'Producer repair was rejected again; diagnose the preserved contract and receiver errors'))
        checks = [submission.load_json(engine.store.read(ref, engine.head))
                  for event in engine.runtime['events']
                  if event['kind'] == 'submission_checked' and event.get('target') == held['execution_id']
                  for ref in event['evidence_refs']]
        issues = [(issue['rule_id'], issue['message']) for check in checks for issue in check['issues']]
        self.assertIn(('submission.activity-extensions.json.model_assessments',
                       'model assessment coverage: {"missing": ["one"], "unexpected": []}'), issues)

    def test_real_academic_generation_enters_assessment_preparation_before_contract_review(self):
        # The template approves an academic requirement, then drives the real solution, which generates its task.
        engine = solved_sim(SOLVED_REQUIREMENT_CRITERIA).engine
        academic = {tid: t for tid, t in engine.runtime['tasks'].items() if t.get('academic_requirement_id')}
        self.assertTrue(academic)
        engine.process_controls()
        engine._refresh_readiness()
        covered = {tid for a in engine.runtime['queue'] for tid in a.get('assessment_targets', {})}
        self.assertTrue(set(academic) <= covered)
        self.assertFalse(any(a['role'] == 'task_contract_review' and a.get('target') in academic
                             for a in engine.runtime['queue']))


class RejectedAcademicAssessmentTests(unittest.TestCase):
    def test_rejected_rating_is_preserved_and_replaced_by_assessment_only_request(self):
        sim, tid, original = rejected_sim()
        engine = sim.engine
        task = engine.runtime['tasks'][tid]
        rejected_id = task['reviews'][-1]['execution_id']
        self.assertEqual(task['reviews'][-1]['decision'], 'revision_required')
        self.assertNotIn('model_assessment', task)
        self.assertEqual(task['model_assessment_history'][0]['assessment'], original['model_assessment'])
        self.assertEqual(task['model_assessment_history'][0]['contract_review_execution'], rejected_id)
        requests = [a for a in engine.runtime['queue'] if a['role'] == 'research_preparation']
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['assessment_targets'][tid]['contract_sha256'], contract_hash(task))
        for key, value in original.items():
            if key not in {'model_assessment', 'reviews', 'status', 'initial_observation_rules'}:
                self.assertEqual(task[key], value)
        for _ in range(3):
            engine._refresh_readiness()
        self.assertEqual(len(task['model_assessment_history']), 1)
        self.assertFalse(any(a['role'] == 'task_contract_review' for a in engine.runtime['queue']))

    def test_repaired_and_unchanged_ratings_both_receive_fresh_independent_review(self):
        for unchanged in (False, True):
            with self.subTest(unchanged=unchanged):
                sim, tid, original = rejected_sim('unresolved' if unchanged else 'revision_required')
                engine = sim.engine
                rejected_id = engine.runtime['tasks'][tid]['reviews'][-1]['execution_id']
                engine.runtime['queue'] = [a for a in engine.runtime['queue']
                                           if a.get('assessment_targets') or a['role'] == 'task_contract_review']
                engine._save()
                chosen = rating() if unchanged else {**rating(), 'importance': 'high',
                                                     'reason': 'Later verification depends on this report.'}
                seen = []

                class Responder:
                    def respond(self, role, context, workspace):
                        seen.append(deepcopy(context))
                        if role == 'research_preparation':
                            extensions(workspace, {'model_assessments': [{'task_id': tid, **chosen}],
                                                   'task_conditions': prepared_rule_conditions(
                                                       context['action'].get('observation_rule_targets', {}))})
                            return {**common(role), 'candidates': []}
                        return {**common(role), **contract_review(context)}
                sim.model.responder = Responder()
                sim.step()
                self.assertIn('model_assessment', engine.runtime['tasks'][tid], json.dumps({
                    'executions': [{key: row.get(key) for key in ('role', 'outcome', 'error', 'integration_result')}
                                   for row in list(engine.runtime['executions'].values())[-3:]],
                    'waiting': [{key: row.get(key) for key in ('kind', 'reason')}
                                for row in engine.runtime.get('waiting_actions', {}).values()]}, ensure_ascii=False))
                self.assertEqual(engine.runtime['tasks'][tid]['model_assessment'], chosen)
                review = next(a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review')
                self.assertEqual(engine._select_model(review)['tier'], 'medium' if unchanged else 'high')
                sim.step()
                self.assertEqual([c['action']['role'] for c in seen], ['research_preparation', 'task_contract_review'])
                # The preparation read the rejected contract and the preserved rating.
                self.assertIn(tid, seen[0]['action']['assessment_targets'])
                supplied = next(t for t in seen[0]['tasks'] if t['id'] == tid)
                self.assertEqual(supplied['reviews'][-1]['execution_id'], rejected_id)
                self.assertEqual(supplied['model_assessment_history'][0]['assessment'], rating())
                task = engine.runtime['tasks'][tid]
                self.assertEqual(task['status'], 'planned')
                self.assertEqual(engine._task_readiness[tid]['state'], 'ready')
                self.assertEqual(len(task['revision_history'][-1]['reviews']), 1)
                self.assertEqual(len(task['reviews']), 2)
                self.assertEqual(task['reviews'][-1]['decision'], 'approved')
                self.assertEqual(engine.runtime['cycles'], 0)
                for key, value in original.items():
                    if key not in {'model_assessment', 'reviews', 'status', 'revision'}:
                        self.assertEqual(task[key], value)

    def test_preexisting_rejection_enters_repair_on_refresh(self):
        sim, tid, _ = rejected_sim()
        rejected_id = sim.engine.runtime['tasks'][tid]['reviews'][-1]['execution_id']
        sim.restart()
        engine = sim.engine
        engine._refresh_readiness()
        task = engine.runtime['tasks'][tid]
        self.assertNotIn('model_assessment', task)
        self.assertTrue(any(task['id'] in a.get('assessment_targets', {}) for a in engine.runtime['queue']))
        self.assertEqual(task['model_assessment_history'][0]['contract_review_execution'], rejected_id)

    def test_repair_deferral_preserves_obligation_until_resume(self):
        sim, _, _ = rejected_sim()
        self.assertEqual(set(sim.engine.runtime['tasks']), {ACADEMIC_TASKS[0]})
        assert_deferral_waits_for_input(self, sim)

    def test_late_repair_cannot_overwrite_a_changed_user_contract(self):
        sim, _, _ = rejected_sim()
        self.assertEqual(set(sim.engine.runtime['tasks']), {ACADEMIC_TASKS[0]})
        assert_late_assessment_preserved(self, sim)


if __name__ == '__main__':
    unittest.main()
