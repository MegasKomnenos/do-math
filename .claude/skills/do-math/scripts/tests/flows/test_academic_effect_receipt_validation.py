"""실제 전체 생산 흐름의 성공 영수에서 필드 하나를 바꾸어 학술 완료를 검증한다.

기존 requirement_flows와 같은 다회차 시나리오라 흐름 폴더에 둔다. 이번 작성에서는 시간 미측정.
"""
from copy import deepcopy
import unittest

from do_math import academic
from support.academic_effect_cases import confirmed_effect_sim


def setUpModule():
    confirmed_effect_sim()


class AcademicEffectReceiptValidationTests(unittest.TestCase):
    def setUp(self):
        self.sim = confirmed_effect_sim()
        self.engine = self.sim.engine
        self.requirements = academic.current_requirements(self.engine.instance)
        self.requirement, = self.requirements['items']
        self.operation, = self.engine.runtime['external_operations'].values()
        self.task = self.engine.runtime['tasks'][self.operation['academic_binding']['task_id']]
        self.arguments = {'task_id': self.task['id'], 'requirements_sha256': self.requirements['sha256'],
                          'solution_basis_value': self.engine._solution_basis()}

    def test_real_confirmed_receipt_has_exact_effect_identity(self):
        operation = self.operation
        self.assertEqual(academic.effect_receipts(self.requirement, runtime=self.engine.runtime, **self.arguments),
            (True, [{'effect_id': 'submit', 'operation_id': operation['id'], 'grant_id': 'HTTP',
                     'request_sha256': operation['request_sha256']}]))
        self.assertEqual(self.engine._academic_status(), {'status': 'completed', 'reason': 'all current requirements satisfied'})
        self.assertEqual(self.engine.store.load()[2]['external_operations'][operation['id']], operation)

    def test_each_changed_binding_field_invalidates_receipt_and_completion(self):
        for field, value in (('task_id', 'other'), ('requirement_id', 'other'),
                             ('requirements_sha256', '0' * 64), ('solution_basis', {}), ('effect_id', 'other')):
            with self.subTest(field=field):
                runtime = deepcopy(self.engine.runtime)
                runtime['external_operations'][self.operation['id']]['academic_binding'][field] = value
                before = deepcopy(runtime)
                self.assertEqual(academic.effect_receipts(self.requirement, runtime=runtime, **self.arguments), (False, []))
                self.assertEqual(academic.academic_status(self.engine.instance, runtime, self.engine._solution_basis()),
                                 {'status': 'active', 'reason': 'requirements remain'})
                self.assertEqual(runtime, before)

    def test_changed_success_status_or_grant_invalidates_receipt(self):
        for field, value in (('status', 'unknown'), ('succeeded', False), ('grant_id', 'other')):
            with self.subTest(field=field):
                runtime = deepcopy(self.engine.runtime)
                runtime['external_operations'][self.operation['id']][field] = value
                self.assertEqual(academic.effect_receipts(self.requirement, runtime=runtime, **self.arguments), (False, []))
                self.assertEqual(academic.academic_status(self.engine.instance, runtime, self.engine._solution_basis()),
                                 {'status': 'active', 'reason': 'requirements remain'})

    def test_changed_receipt_blocks_re_recording_a_satisfied_assessment(self):
        self.engine.runtime['external_operations'][self.operation['id']]['succeeded'] = False
        before = deepcopy(self.engine.runtime)
        applied = self.task['assessment']
        with self.assertRaisesRegex(ValueError, '^satisfied academic assessment lacks confirmed successful required external effects$'):
            self.engine._record_academic_assessment(self.task, applied, applied['execution_id'])
        self.assertEqual(self.engine.runtime, before)

    def test_partial_receipts_preserve_satisfied_prefix_only(self):
        requirement = deepcopy(self.requirement)
        requirement['external_effects'].append({'id': 'second', 'scope': '합성 후속 전송', 'grant_id': 'HTTP'})
        operation = self.operation
        self.assertEqual(academic.effect_receipts(requirement, runtime=self.engine.runtime, **self.arguments),
            (False, [{'effect_id': 'submit', 'operation_id': operation['id'], 'grant_id': 'HTTP',
                      'request_sha256': operation['request_sha256']}]))

    def test_external_prerequisite_rejects_changed_requirement_binding(self):
        grant = self.engine.instance['grants']['HTTP']
        basis = self.engine._solution_basis()
        self.assertTrue(academic.external_prerequisite(self.engine.instance, self.engine.runtime, basis, self.operation, grant))
        for field, value in (('requirement_id', 'missing'), ('effect_id', 'missing'),
                             ('requirements_sha256', '0' * 64), ('solution_basis', {})):
            with self.subTest(field=field):
                operation = deepcopy(self.operation)
                operation['academic_binding'][field] = value
                before = deepcopy(operation)
                self.assertFalse(academic.external_prerequisite(self.engine.instance, self.engine.runtime, basis, operation, grant))
                self.assertEqual(operation, before)
