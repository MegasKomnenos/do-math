"""단순 거부보다 앞선 계약이 많은 복합 입력을 실제 생산 상태에서 분리한다."""
from copy import deepcopy
import unittest

from do_math import governance as gov, input_basis, planning
from support.governance_cases import auditor_sim, audit_output, transfer_sim, transfer_output, planned_sim, records_sim


class GovernanceCompositeInputTests(unittest.TestCase):
    def test_initial_approval_without_charter_is_rejected_by_actual_producer(self):
        from support.governance_cases import initial_approval_scene
        sim, i, r, source, approval, approval_source, records = initial_approval_scene()
        i['governance_sources'][approval_source['id']] = approval_source
        sim.engine.instance, sim.engine.runtime = i, r
        context = {'id': 'CX-close-initial', 'kind': 'research_context', 'revision': 1, 'supersedes': [],
            'content': {'terms': [{'term': 'P', 'definition': '연구 명제', 'boundary': '자연수',
                                 'avoid_synonyms': [], 'record_refs': []}]}}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^initialization needs exactly one approved charter$'):
            sim.engine._initialization_control({'kind': 'initialization', 'operation': 'governance',
                                               'records': [context]}, approval_source['id'])
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_domain_decision_closes_only_its_affected_question(self):
        from support.governance_cases import question_sim, question_bundle
        sim = question_sim()
        bundle = question_bundle(sim)
        row = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        charter = gov.governance_view(sim.instance)['charter']['id']
        record = {'id': 'PO-close-answer', 'kind': 'policy', 'revision': 1, 'supersedes': [],
            'content': {'rule_id': 'domain', 'text': '자연수 범위로 연구한다.', 'scope': ['P'],
                        'reason_refs': [charter], 'audit_refs': []}}
        before = deepcopy((sim.instance, sim.runtime))
        i, r, event = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'policy', 'record': record, 'resolves_questions': [row['id']]},
            source_ref=bundle['source']['id'], clock=sim.clock)
        resolved = next(q for q in r['question_links'] if q['id'] == row['id'])
        self.assertEqual(resolved['status'], 'resolved')
        self.assertEqual(resolved['resolution_ref'], event['id'])
        self.assertEqual(resolved['unresolved_target_ids'], [])
        self.assertEqual((sim.instance, sim.runtime), before)
        sim.engine.instance, sim.engine.runtime = i, r
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['question_links'], r['question_links'])

    def test_plan_model_requirement_cannot_exceed_approved_profile_allowlist(self):
        from do_math.execution_profiles import profile_ref
        from support.engine_lifecycle import approve
        from support.governance_sim import returned
        from support.planning_owner import owner_sim, work_profile
        from support.role_answers import disposition
        sim = owner_sim()
        task = sim.runtime['tasks']['TK-1']
        task['profile_refs'] = [profile_ref(work_profile(sim.instance, 'low'))]
        approve(sim.engine, task)
        execution = returned(sim.engine, {'id': 'AC-close-model-plan', 'role': 'research_plan'}, 'EX-close-model-plan')
        sim.engine._save()
        execution = sim.runtime['executions'][execution['id']]
        execution['model_decisions'] = {'TK-1': {'difficulty': 'high', 'importance': 'low', 'reason': '더 강한 모델이 필요한 판단'}}
        output = {'dispositions': [disposition('TK-1')], 'task_assessments': [], 'preparation_requests': []}
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^Selected task TK-1 cannot meet the plan model requirement with its allowed profiles; defer or revise its contract: '):
            sim.engine._apply_task_plan(output, execution['id'], deepcopy(sim.runtime['tasks']), ['TK-1'], evaluation_context=sim.engine._evaluation_context())
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_transfer_cannot_select_recipient_with_new_unreviewed_contract(self):
        sim = transfer_sim()
        output = transfer_output(sim)
        before = deepcopy((sim.instance, sim.runtime))
        with self.assertRaisesRegex(ValueError, '^assessment changed a selected recipient contract; replan after review$'):
            sim.engine._apply_task_plan(output, 'EX-close-transfer-plan',
                                       deepcopy(sim.runtime['tasks']), ['TK-close-target'], evaluation_context=sim.engine._evaluation_context())
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_assessment_requires_the_complete_original_result_set(self):
        sim = transfer_sim()
        output = transfer_output(sim)
        execution = sim.runtime['executions']['EX-close-transfer-plan']
        context = sim.engine._context(execution['action'], sim.root / 'context', execution_id=execution['id'])
        sim.runtime['tasks']['TK-close-source']['results'] = []
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'assessment requires the current complete results') as caught:
            sim.engine._validate_decision_acceptance(execution['action'], output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'id': 'TK-close-source', 'field': 'assessment_result_set',
                       'reason': 'assessment requires the current complete results'}, caught.exception.changes)
        self.assertEqual(sim.instance, before)

    def test_goal_acceptance_rejects_different_complete_basis(self):
        sim = auditor_sim()
        execution = sim.runtime['executions']['EX-close-auditor']
        action = deepcopy(execution['action'])
        execution.update(input_snapshot=sim.engine.head, **planning.governance_revisions(sim.instance))
        context = sim.engine._context(action, sim.root / 'context', execution_id=execution['id'])
        output = audit_output(sim)
        action['basis'] = '0' * 64
        before = deepcopy(sim.instance)
        with self.assertRaisesRegex(input_basis.CurrentnessChanged, 'the complete goal judgment basis changed') as caught:
            sim.engine._validate_decision_acceptance(action, output, execution, context, evaluation_context=sim.engine._evaluation_context())
        self.assertIn({'field': 'goal_audit_basis', 'reason': 'the complete goal judgment basis changed'}, caught.exception.changes)
        self.assertEqual(sim.instance, before)

    def test_academic_only_charter_does_not_revise_nonacademic_task(self):
        sim = planned_sim()
        old = gov.governance_view(sim.instance)['charter']
        record = {key: deepcopy(old[key]) for key in ('id', 'kind', 'revision', 'supersedes', 'content')}
        record.update(id='CH-close-academic', revision=old['revision'] + 1, supersedes=[old['id']])
        # 동일한 계약의 빈 학술 의무도 새 헌장 판본을 승인할 수 있다.
        source = old['source_ref']
        tasks = deepcopy(sim.runtime['tasks'])
        i, r, event = gov.apply_decision(sim.instance, sim.runtime,
            {'kind': 'charter', 'record': record}, source_ref=source, clock=sim.clock)
        self.assertEqual(r['tasks'], tasks)
        self.assertEqual(event['affected'], [])
        self.assertEqual(r['queue'][-1]['role'], 'research_plan')
        self.assertEqual(gov.governance_view(i)['charter']['id'], 'CH-close-academic')
        sim.engine.instance, sim.engine.runtime = i, r
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['tasks'], tasks)

    def test_absent_instance_id_has_explicit_direct_basis_contract(self):
        sim = records_sim()
        i = deepcopy(sim.instance)
        del i['id']
        before = deepcopy((i, sim.runtime))
        # 기록 참조 없는 직접 판정은 인스턴스 전체를 근거로 암묵 추가하지 않는다.
        first = gov._import_basis(i, sim.runtime, {'import_units': []})
        second = gov._import_basis(sim.instance, sim.runtime, {'import_units': []})
        self.assertEqual(first, second)
        self.assertEqual((i, sim.runtime), before)
