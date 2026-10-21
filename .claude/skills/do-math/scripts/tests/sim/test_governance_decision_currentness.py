"""계획 생산자가 저장한 입력과 현재 상태를 실제 엔진에서 대조한다."""
from copy import deepcopy
import json
import unittest

from do_math import input_basis, planning
from support.governance_cases import planned_sim
from support.governance_sim import returned


def plan_input(sim):
    execution = next(e for e in reversed(list(sim.runtime['executions'].values()))
                     if e['role'] == 'research_plan' and e.get('outcome') == 'output_accepted')
    output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
    context = json.loads(sim.engine.store.read(
        'runtime/artifacts/' + execution['input_bundle'] + '/input/submission/context.json', sim.engine.head))
    return execution, deepcopy(output), context


class GovernanceDecisionCurrentnessTests(unittest.TestCase):
    def test_changed_task_question_reports_contract_drift_without_misclassifying_review_inputs(self):
        sim = planned_sim()
        execution = next(e for e in sim.runtime['executions'].values()
                         if e['role'] == 'task_contract_review' and e.get('outcome') == 'output_accepted')
        output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
        context = json.loads(sim.engine.store.read(
            'runtime/artifacts/' + execution['input_bundle'] + '/input/submission/context.json', sim.engine.head))
        tid = execution['action']['target']
        original = sim.engine.store.load(execution['input_snapshot'])[2]['tasks'][tid]
        sim.runtime['tasks'][tid]['question'] += ' 바뀐 명제'
        queue = deepcopy(sim.runtime['queue'])
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'action contract changed') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context,
                evaluation_context=sim.engine._evaluation_context())
        self.assertEqual(caught.exception.changes, [
            {'id': tid, 'field': 'contract_sha256', 'before': planning.contract_hash(original),
             'after': planning.contract_hash(sim.runtime['tasks'][tid]), 'next': 'refresh_decision'},
            {'id': tid, 'field': 'contract_sha256', 'reason': 'action contract changed'}])
        self.assertEqual(sim.runtime['queue'], queue)

    def test_execution_contract_hash_must_match_current_task(self):
        sim = planned_sim()
        execution = next(e for e in sim.runtime['executions'].values()
                         if e['role'] == 'task_contract_review' and e.get('outcome') == 'output_accepted')
        output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
        context = json.loads(sim.engine.store.read(
            'runtime/artifacts/' + execution['input_bundle'] + '/input/submission/context.json', sim.engine.head))
        execution['contract_sha256'] = '0' * 64
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'action contract changed') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': execution['action']['target'], 'field': 'contract_sha256',
                       'reason': 'action contract changed'}, caught.exception.changes)
        self.assertEqual(sim.instance, before)

    def test_review_task_basis_must_match_original_snapshot(self):
        sim = planned_sim()
        execution = next(e for e in sim.runtime['executions'].values()
                         if e['role'] == 'task_contract_review' and e.get('outcome') == 'output_accepted')
        output = json.loads(sim.engine.store.read(execution['submission_intent']['output_ref'], sim.engine.head))
        context = json.loads(sim.engine.store.read(
            'runtime/artifacts/' + execution['input_bundle'] + '/input/submission/context.json', sim.engine.head))
        tid = execution['action']['target']
        from do_math.execution_profiles import profile_ref, seal_profile
        profile_id = sim.runtime['tasks'][tid]['profile_refs'][0]['id']
        body = deepcopy(sim.instance['execution_profiles'][profile_id])
        body['ai']['effort'] = 'high' if body['ai']['effort'] != 'high' else 'medium'
        profile = seal_profile(body)
        sim.instance['execution_profiles'][profile['id']] = profile
        sim.runtime['tasks'][tid]['profile_refs'][0] = profile_ref(profile)
        queue = deepcopy(sim.runtime['queue'])
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'review source, decision, knowledge, trust or profile premise changed') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': tid, 'field': 'task_basis',
            'reason': 'review source, decision, knowledge, trust or profile premise changed'}, caught.exception.changes)
        self.assertEqual(sim.runtime['queue'], queue)

    def test_old_resolution_evidence_requires_current_premises(self):
        sim = planned_sim()
        evidence, _, _ = plan_input(sim)
        failed_action = {'id': 'AC-close-failed-plan', 'role': 'research_plan'}
        failed_action['refresh'] = {'attempt': 1}
        failed = returned(sim.engine, failed_action, 'EX-close-failed-plan')
        sim.engine._refresh_changed_decision(failed_action, failed['id'], [{'field': 'decision_basis'}])
        resolver = returned(sim.engine, {'id': 'AC-close-resolver', 'role': 'operational_review',
                                        'target': failed['id']}, 'EX-close-resolver')
        resolver['extensions'] = {'action_resolutions': [{'action_id': failed_action['id'],
            'evidence_execution_id': evidence['id'], 'reason': '현재 계획 판단으로 해소한다.'}]}
        evidence['decision_basis'] = {}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^resolution evidence no longer has current premises$'):
            sim.engine._apply_action_resolutions(resolver['id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_failed_revision_requires_accepted_revision_resolution(self):
        sim = planned_sim()
        evidence, _, _ = plan_input(sim)
        failed_action = {'id': 'AC-close-failed-plan', 'role': 'research_plan'}
        failed_action['refresh'] = {'attempt': 1}
        failed = returned(sim.engine, failed_action, 'EX-close-failed-plan')
        sim.engine._refresh_changed_decision(failed_action, failed['id'], [{'field': 'decision_basis'}])
        wait = sim.runtime['waiting_actions'][failed_action['id']]
        tid = next(a['target'] for a in sim.runtime['queue'] if a['role'] == 'research_work')
        from do_math.revisions import capture_targets
        wait['action']['revision_targets'] = capture_targets(sim.instance, sim.runtime, [tid], required=True)
        evidence.setdefault('extensions', {})['action_resolutions'] = [{'action_id': failed_action['id'],
            'evidence_execution_id': 'current', 'reason': '현재 판단으로 해소한다.'}]
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^failed revision obligations require accepted target dispositions$'):
            sim.engine._apply_action_resolutions(evidence['id'], accepting_current=True)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_deleted_planning_target_is_rejected_without_applying(self):
        sim = planned_sim()
        execution, output, context = plan_input(sim)
        tid = output['dispositions'][0]['task_id']
        del sim.runtime['tasks'][tid]
        before = deepcopy(sim.instance)
        queue = deepcopy(sim.runtime['queue'])
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'planning target ended or missing') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': tid, 'field': 'target_applicability', 'reason': 'planning target ended or missing'}, caught.exception.changes)
        self.assertEqual(sim.instance, before)
        self.assertEqual(sim.runtime['queue'], queue)

    def test_finished_planning_target_is_rejected(self):
        sim = planned_sim()
        execution, output, context = plan_input(sim)
        tid = output['dispositions'][0]['task_id']
        sim.runtime['tasks'][tid]['status'] = 'completed'
        queue = deepcopy(sim.runtime['queue'])
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'planning target ended or missing') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': tid, 'field': 'target_applicability', 'reason': 'planning target ended or missing'}, caught.exception.changes)
        self.assertEqual(sim.runtime['queue'], queue)

    def test_confirmed_question_must_still_be_open(self):
        sim = planned_sim()
        execution, output, context = plan_input(sim)
        output['confirmed_question_ids'] = ['QU-missing']
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'the user question is no longer open') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': 'QU-missing', 'field': 'question_applicability',
                       'reason': 'the user question is no longer open'}, caught.exception.changes)
        self.assertEqual(sim.instance, before)

    def test_plan_cannot_apply_after_candidate_contract_changes(self):
        sim = planned_sim()
        execution, output, _ = plan_input(sim)
        _, original_i, original_r = sim.engine.store.load(execution['input_snapshot'])
        tid = output['dispositions'][0]['task_id']
        sim.runtime['tasks'][tid]['question'] += ' 다른 명제'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^candidate contract changed before plan application$'):
            sim.engine._apply_task_plan(output, execution['id'], original_r['tasks'], [tid])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_plan_cannot_apply_when_selection_is_no_longer_ready(self):
        sim = planned_sim()
        execution, output, _ = plan_input(sim)
        _, original_i, original_r = sim.engine.store.load(execution['input_snapshot'])
        tid = output['dispositions'][0]['task_id']
        sim.runtime['tasks'][tid]['status'] = 'completed'
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^selected task is no longer ready$'):
            sim.engine._apply_task_plan(output, execution['id'], original_r['tasks'], [tid])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_missing_research_task_has_no_requirement_refresh(self):
        sim = planned_sim()
        action = deepcopy(next(a for a in sim.runtime['queue'] if a['role'] == 'research_work'))
        action['target'] = 'missing'
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(sim.engine._execution_requirement_changes(action), [])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_ended_research_task_has_no_requirement_refresh(self):
        sim = planned_sim()
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'research_work')
        sim.runtime['tasks'][action['target']]['status'] = 'completed'
        before = deepcopy((sim.instance, sim.runtime))
        self.assertEqual(sim.engine._execution_requirement_changes(action), [])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_missing_failed_action_resolution_is_atomic(self):
        sim = planned_sim()
        execution, _, _ = plan_input(sim)
        execution.setdefault('extensions', {})['action_resolutions'] = [
            {'action_id': 'missing', 'evidence_execution_id': 'current', 'reason': '범위 재검토'}]
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^action resolution requires a current failed action$'):
            sim.engine._apply_action_resolutions(execution['id'], accepting_current=True)
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_second_refresh_parks_research_and_queues_operations(self):
        sim = planned_sim()
        action = deepcopy(next(a for a in sim.runtime['queue'] if a['role'] == 'research_work'))
        action['refresh'] = {'attempt': 1}
        execution = returned(sim.engine, action, 'EX-close-refresh')
        others = [deepcopy(a) for a in sim.runtime['queue'] if a['id'] != action['id']]
        changes = [{'field': 'contract_sha256', 'reason': '계약 변경'}]
        sim.engine._refresh_changed_decision(action, execution['id'], changes)
        waiting = sim.runtime['waiting_actions'][action['id']]
        self.assertEqual(waiting, {'action': action, 'kind': 'execution_failure', 'failure_kind': 'currentness_changed',
            'changes': changes, 'reason': 'decision premises changed again after one refresh', 'execution_id': execution['id'],
            'next_owner': 'operational_review'})
        queued = sim.runtime['queue']
        self.assertEqual(queued[:-1], others)
        self.assertEqual((queued[-1]['role'], queued[-1]['target'], queued[-1]['reason']),
                         ('operational_review', execution['id'], 'Resolve repeated decision premise conflicts'))
        self.assertEqual(execution['error_kind'], 'currentness_changed')

    def test_second_operational_refresh_does_not_queue_itself(self):
        sim = planned_sim()
        action = {'id': 'AC-close-operation', 'role': 'operational_review', 'target': sim.instance['id'],
                  'refresh': {'attempt': 1}}
        execution = returned(sim.engine, action, 'EX-close-operation')
        queue = deepcopy(sim.runtime['queue'])
        changes = [{'field': 'goal_or_policy_revision', 'reason': '승인 변경'}]
        sim.engine._refresh_changed_decision(action, execution['id'], changes)
        self.assertEqual(sim.runtime['queue'], queue)
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], {
            'action': action, 'kind': 'execution_failure', 'failure_kind': 'currentness_changed', 'changes': changes,
            'reason': 'decision premises changed again after one refresh', 'execution_id': execution['id'],
            'next_owner': 'operations', 'release_condition': 'new consistent decision input', 'owner': 'ai'})

    def test_contract_review_refresh_captures_new_exact_basis(self):
        sim = planned_sim()
        tid = next(a['target'] for a in sim.runtime['queue'] if a['role'] == 'research_work')
        action = {'id': 'AC-close-review', 'role': 'task_contract_review', 'target': tid}
        execution = returned(sim.engine, action, 'EX-close-review')
        task = sim.runtime['tasks'][tid]
        expected = {'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                    **planning.governance_revisions(sim.instance)}
        queue = deepcopy(sim.runtime['queue'])
        changes = [{'field': 'task_basis', 'reason': '재검토'}]
        sim.engine._refresh_changed_decision(action, execution['id'], changes)
        refreshed = sim.runtime['queue'][0]
        self.assertEqual(refreshed['contract_basis'], expected)
        self.assertEqual(refreshed['review_basis_key'], planning.review_basis_key(task, sim.instance, sim.runtime))
        self.assertEqual(refreshed['continuation_of'], execution['id'])
        self.assertEqual(sim.runtime['queue'][1:], queue)
