"""정상 목표 감사와 TASKS 생산 기록의 단일 필드 변조를 검사한다."""
from copy import deepcopy
import unittest

from do_math import academic
from support.academic_scenes import consumer_sim, theorem_sim, MANUSCRIPT, decide_requirements
from support.academic_assessment_cases import assessed_case


class AcademicAssuranceValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = consumer_sim().engine

    def test_current_solution_requires_usable_dependencies(self):
        engine = self.engine
        self.assertIsNotNone(engine._solution_basis())
        instance = deepcopy(engine.instance)
        for judgment in instance['goal_judgments']:
            if judgment['basis'] == instance['goal_assessment_basis']:
                judgment['dependencies'] = []
        before = deepcopy(instance)
        self.assertIsNone(academic.current_solution_basis(instance, engine.runtime))
        self.assertEqual(instance, before)

    def test_current_solution_requires_nonempty_current_judgment_group(self):
        for field, value in (('goal_judgments', []), ('goal_assessment_basis', 'absent')):
            instance = deepcopy(self.engine.instance)
            instance[field] = value
            self.assertIsNone(academic.current_solution_basis(instance, self.engine.runtime))
        instance = deepcopy(self.engine.instance)
        instance['goal_judgments'][0]['current'] = False
        self.assertIsNone(academic.current_solution_basis(instance, self.engine.runtime))

    def test_solved_goal_without_readable_basis_is_incomplete(self):
        before = deepcopy(self.engine.runtime)
        self.assertEqual(academic.academic_status(self.engine.instance, self.engine.runtime, None),
                         {'status': 'incomplete', 'reason': 'solution basis unreadable'})
        self.assertEqual(self.engine.runtime, before)

    def test_goal_assurance_requires_current_formal_judgments(self):
        engine = self.engine
        basis = engine.instance['goal_assessment_basis']
        judgments = [deepcopy(j) for j in engine.instance['goal_judgments'] if j['basis'] == basis]
        for field, value in (('decision', 'unresolved'), ('current', False), ('formal_result_refs', [])):
            with self.subTest(field=field):
                changed = deepcopy(judgments)
                changed[0][field] = value
                before = deepcopy(engine.instance)
                with self.assertRaisesRegex(ValueError, '^mathematical assurance needs current formal-result judgments$'):
                    academic.apply_goal_assurance(engine.instance, decision='mathematically_solved', basis=basis,
                                                  judgments=changed, runtime=engine.runtime)
                self.assertEqual(engine.instance, before)

    def test_goal_assurance_rejects_a_different_recorded_group(self):
        engine = self.engine
        basis = engine.instance['goal_assessment_basis']
        judgments = [deepcopy(j) for j in engine.instance['goal_judgments'] if j['basis'] == basis]
        judgments[0]['scope_complete'] = False
        before = deepcopy(engine.instance)
        with self.assertRaisesRegex(ValueError, '^final status must consume the complete recorded judgment group$'):
            academic.apply_goal_assurance(engine.instance, decision='mathematically_solved', basis=basis,
                                          judgments=judgments, runtime=engine.runtime)
        self.assertEqual(engine.instance, before)

    def test_goal_assurance_rejects_wrong_required_count(self):
        instance = deepcopy(self.engine.instance)
        basis = instance['goal_assessment_basis']
        judgments = [j for j in instance['goal_judgments'] if j['basis'] == basis]
        judgments[0]['required'] = len(judgments) + 1
        before = deepcopy(instance)
        with self.assertRaisesRegex(ValueError, '^final status lacks the required independent judgment slots$'):
            academic.apply_goal_assurance(instance, decision='mathematically_solved', basis=basis,
                                          judgments=judgments, runtime=self.engine.runtime)
        self.assertEqual(instance, before)

    def test_goal_assurance_rejects_missing_formal_evidence(self):
        instance = deepcopy(self.engine.instance)
        basis = instance['goal_assessment_basis']
        judgments = [j for j in instance['goal_judgments'] if j['basis'] == basis]
        instance['formal_results'].pop(judgments[0]['formal_result_refs'][0])
        before = deepcopy(instance)
        with self.assertRaisesRegex(ValueError, '^final goal cites unavailable formal evidence$'):
            academic.apply_goal_assurance(instance, decision='mathematically_solved', basis=basis,
                                          judgments=judgments, runtime=self.engine.runtime)
        self.assertEqual(instance, before)

    def test_goal_assurance_rejects_duplicate_independent_slots(self):
        instance = deepcopy(self.engine.instance)
        basis = instance['goal_assessment_basis']
        judgments = [j for j in instance['goal_judgments'] if j['basis'] == basis]
        self.assertGreaterEqual(len(judgments), 2)
        judgments[1]['slot'] = judgments[0]['slot']
        before = deepcopy(instance)
        with self.assertRaisesRegex(ValueError, '^final status lacks the required independent judgment slots$'):
            academic.apply_goal_assurance(instance, decision='mathematically_solved', basis=basis,
                                          judgments=judgments, runtime=self.engine.runtime)
        self.assertEqual(instance, before)

    def test_goal_assurance_returns_independent_state_for_valid_group(self):
        engine = self.engine
        basis = engine.instance['goal_assessment_basis']
        judgments = [j for j in engine.instance['goal_judgments'] if j['basis'] == basis]
        before = deepcopy(engine.instance)
        result = academic.apply_goal_assurance(engine.instance, decision='mathematically_solved', basis=basis,
                                              judgments=judgments, runtime=engine.runtime)
        self.assertEqual(result, before)
        result['goal_judgments'].clear()
        self.assertEqual(engine.instance, before)

    def test_binding_cannot_be_changed_after_any_transmission_evidence(self):
        from do_math.external import prepare_operation
        operation = prepare_operation({'method': 'POST', 'url': 'https://academic.example.test/submit'}, 'G', 'user')
        for field, value in (('status', 'confirmed'), ('transmitted', True), ('attempts', [{'request_sha256': operation['request_sha256']}])):
            with self.subTest(field=field):
                changed = {**operation, field: value}
                before = deepcopy(changed)
                with self.assertRaisesRegex(ValueError, '^cannot change academic premise after transmission$'):
                    academic.bind_external_prerequisite(self.engine.instance, self.engine.runtime,
                                                        self.engine._solution_basis(), changed)
                self.assertEqual(changed, before)

    def test_binding_copies_solution_and_preserves_original_operation(self):
        from do_math.external import prepare_operation
        operation = prepare_operation({'method': 'POST', 'url': 'https://academic.example.test/submit'}, 'G', 'user')
        before = deepcopy(operation)
        basis = self.engine._solution_basis()
        result = academic.bind_external_prerequisite(self.engine.instance, self.engine.runtime, basis, operation)
        self.assertEqual(result, {**operation, 'academic_basis': {'solution_basis': basis,
            'requirements_sha256': academic.current_requirements(self.engine.instance)['sha256']}})
        result['academic_basis']['solution_basis']['records'].clear()
        self.assertEqual(operation, before)
        self.assertEqual(basis, self.engine._solution_basis())


class AcademicAssessmentValidationTests(unittest.TestCase):
    def test_stored_assessment_requires_its_actual_task_and_execution_references(self):
        from do_math.state_contract import default_state_contract

        sim, task_id, assessment, execution_id = assessed_case()
        engine = sim.engine
        engine._record_academic_assessment(engine.runtime['tasks'][task_id], assessment, execution_id)
        record, = deepcopy(engine.runtime['academic_assessments'])
        self.assertTrue(academic.assessment_current(engine.instance, engine.runtime, record))
        self.assertEqual((record['task_id'], record['execution_id']), (task_id, execution_id))
        engine._save()
        published = deepcopy(engine.store.load())
        head, instance, runtime = published
        self.assertEqual(runtime['academic_assessments'], [record])
        family = default_state_contract().family('runtime', 'academic_assessments')
        self.assertEqual(list(family.references(runtime['academic_assessments'])),
                         [(task_id, 'tasks'), (execution_id, 'executions')])

        cases = (('task_id', 'TK-missing-academic', 'unknown record'),
                 ('execution_id', 'EX-missing-academic', 'unknown record'),
                 ('task_id', execution_id, 'reference has wrong family'),
                 ('execution_id', task_id, 'reference has wrong family'))
        for field, target, failure in cases:
            with self.subTest(field=field, target=target):
                broken = deepcopy(runtime)
                broken['academic_assessments'][0][field] = target
                family.checker.validate(broken['academic_assessments'])
                before = deepcopy((instance, broken))
                reason = ('academic_assessments references unknown record: ' + target
                          if failure == 'unknown record'
                          else 'academic_assessments reference has wrong family: ' + target)
                with self.assertRaises(ValueError) as caught:
                    engine.store.save_with_state(head, instance, broken)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((instance, broken), before)
                self.assertEqual(engine.store.load(), published)

    def test_goal_settlement_preserves_each_cancelled_dispatch_obligation(self):
        engine = consumer_sim().engine
        pending = {row['id']: deepcopy(row) for row in engine.runtime['queue']}
        self.assertTrue(pending)
        history_count = len(engine.runtime['history'])
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(engine.runtime['waiting_actions'], {})
        self.assertEqual(engine.runtime['history'][history_count:], [
            {'kind': 'goal_completion_superseded_action', 'action': action,
             'reason': 'goal_completed_before_dispatch', 'next_owner': 'user'} for action in pending.values()])
        settled = deepcopy(engine.runtime)
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime, settled)
        engine._save()
        self.assertEqual(engine.store.load()[2]['queue'], [])

    def test_record_rejects_changed_requirement_edition_without_ledger_change(self):
        sim, tid, value, eid = assessed_case()
        task = deepcopy(sim.runtime['tasks'][tid])
        task['requirements_sha256'] = '0' * 64
        before = deepcopy(sim.runtime)
        with self.assertRaisesRegex(ValueError, '^academic assessment basis changed$'):
            sim.engine._record_academic_assessment(task, value, eid)
        self.assertEqual(sim.runtime, before)

    def test_nonacademic_task_does_not_append_academic_assessment(self):
        sim, tid, value, eid = assessed_case()
        task = deepcopy(sim.runtime['tasks'][tid])
        task.pop('academic_requirement_id')
        before = deepcopy(sim.runtime)
        sim.engine._record_academic_assessment(task, value, eid)
        self.assertEqual(sim.runtime, before)

    def test_applied_task_assessment_cannot_change_approved_criterion(self):
        sim, tid, value, eid = assessed_case(criterion='승인받지 않은 기준')
        before = deepcopy(sim.runtime)
        with self.assertRaisesRegex(ValueError, '^academic criteria differ from the approved requirement obligations$'):
            sim.engine._record_academic_assessment(sim.runtime['tasks'][tid], value, eid)
        self.assertEqual(sim.runtime, before)

    def test_unresolved_task_assessment_keeps_academic_requirement_open(self):
        sim, tid, value, eid = assessed_case(unresolved=True)
        sim.engine._record_academic_assessment(sim.runtime['tasks'][tid], value, eid)
        record, = sim.runtime['academic_assessments']
        self.assertEqual(record['decision'], 'unresolved')
        self.assertEqual(record['evidence'][0]['satisfied'], False)
        self.assertEqual(sim.engine._academic_status(), {'status': 'active', 'reason': 'requirements remain'})
        sim.engine._save()
        self.assertEqual(sim.engine.store.load()[2]['academic_assessments'], [record])

    def test_current_assessment_receipt_is_sealed_and_deduplicated(self):
        sim, tid, value, eid = assessed_case()
        engine = sim.engine
        task = engine.runtime['tasks'][tid]
        engine._record_academic_assessment(task, value, eid)
        record, = deepcopy(engine.runtime['academic_assessments'])
        self.assertTrue(academic.assessment_current(engine.instance, engine.runtime, record))
        self.assertEqual(record['decision'], 'satisfied')
        self.assertEqual(record['external_effect_receipts'], [])
        engine._record_academic_assessment(task, value, eid)
        self.assertEqual(engine.runtime['academic_assessments'], [record])
        engine._save()
        self.assertEqual(engine.store.load()[2]['academic_assessments'], [record])

    def test_completed_stale_task_is_invalidated_only_once(self):
        sim, tid, value, eid = assessed_case()
        engine = sim.engine
        engine._record_academic_assessment(engine.runtime['tasks'][tid], value, eid)
        decide_requirements(engine, [{**MANUSCRIPT, 'criteria': ['새 기준']}])
        engine._ensure_academic_followup()
        old = deepcopy(engine.runtime['tasks'][tid])
        self.assertEqual(old['status'], 'completed')
        self.assertIs(old['assessment']['current'], False)
        tasks = deepcopy(engine.runtime['tasks'])
        engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['tasks'], tasks)
        engine._save()
        self.assertEqual(engine.store.load()[2]['tasks'][tid], old)

    def test_closed_superseded_task_is_preserved_on_repeated_followup(self):
        engine = consumer_sim().engine
        tid, = engine.runtime['tasks']
        decide_requirements(engine, [{**MANUSCRIPT, 'criteria': ['새 기준']}])
        engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['tasks'][tid]['status'], 'closed')
        tasks = deepcopy(engine.runtime['tasks'])
        engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['tasks'], tasks)
        engine._save()
        self.assertEqual(engine.store.load()[2]['tasks'], tasks)

    def test_wrong_role_work_profile_is_rejected_before_task_creation(self):
        engine = consumer_sim().engine
        # 기존 KD-1200과 분리된 하위 규칙의 일시 상태다. 과제를 지워 조작하지 않는다.
        decide_requirements(engine, [])
        engine._ensure_academic_followup()
        engine._save()
        decide_requirements(engine, [{**MANUSCRIPT, 'id': 'NEXT'}])
        engine.instance['role_profile_refs']['research_work'] = deepcopy(engine.instance['role_profile_refs']['research_plan'])
        before = deepcopy(engine.runtime)
        with self.assertRaisesRegex(ValueError, '^academic work profile has a different role$'):
            engine._ensure_academic_followup()
        self.assertEqual(engine.runtime, before)

    def test_unsolved_goal_rejects_external_rejection(self):
        engine = theorem_sim().engine
        before = deepcopy(engine.runtime)
        with self.assertRaisesRegex(ValueError, '^external rejection requires a current solved mathematical goal$'):
            engine._academic_control({'action': 'decision', 'config': {'change': {
                'kind': 'academic_rejection', 'actor': '합성 심사자', 'text': '반려'}}})
        self.assertEqual(engine.runtime, before)
