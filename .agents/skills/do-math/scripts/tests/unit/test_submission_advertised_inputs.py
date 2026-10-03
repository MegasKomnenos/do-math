"""3-A: 실제 역할 입력의 참조 광고를 원 자료에서 독립적으로 검산한다.

빈 task 모집단과 보통/복구 입력의 catalog를 확인한다. ready/returned의
비어 있지 않은 조합과 live cycle의 의미 적용을 이 시험의 성적으로 세지 않는다.

역할·복구 전건의 실제 입력 생성을 유지하여 첫 실측 최대 1.968초다. 0.2초를 넘는 전건 순회를 축소하지 않는다.
"""
from pathlib import Path
import re
import tempfile
import unittest

from do_math import contracts, submission
from support.submission_advertised import SOURCE_FORMS, advertised_input


class AdvertisedInputTests(unittest.TestCase):
    def test_all_roles_advertise_every_source_identifier_form_and_accept_it(self):
        with tempfile.TemporaryDirectory() as directory:
            for role in contracts.ROLES:
                for recovery in (False, True):
                    with self.subTest(role=role, recovery=recovery):
                        root = Path(directory) / (role + str(recovery))
                        prepared = advertised_input(root, role, recovery=recovery)
                        fixed = prepared['validation_context']
                        values = [row['value'] for row in fixed['reference_catalog']]
                        self.assertEqual(len(values), len(set(values)))
                        # 기대값을 reference_catalog/aliases 함수에서 다시 계산하지 않는다.
                        self.assertEqual(set(SOURCE_FORMS) - set(values), set())
                        self.assertEqual(prepared['context']['reference_catalog'], fixed['reference_catalog'])
                        for value in values:
                            self.assertIsNone(submission.validate_reference(value, fixed, root))
                        for value in SOURCE_FORMS:
                            self.assertEqual(submission.reported_references({'used_sources': [value]}, {}, fixed), ['논문.txt'])
                        if recovery:
                            historical = 'runtime/artifacts/BA-previous/result.json'
                            self.assertIn(historical, values)
                            self.assertEqual(submission.reported_references({'used_sources': [historical]}, {}, fixed), [historical])

    def test_advertisement_cannot_authorize_an_unknown_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            for role in contracts.ROLES:
                with self.subTest(role=role):
                    root = Path(directory) / role
                    fixed = advertised_input(root, role)['validation_context']
                    unknown = 'unadvertised-evidence.txt'
                    fixed['reference_catalog'].append({'value': unknown, 'canonical_ref': unknown})
                    reason = ('reference must identify supplied input, a record of the input snapshot or a preserved '
                              'workspace file: ' + unknown + '; use an exact reference_catalog value, a record_index ID '
                              'or workspace:<preserved-file>')
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        submission.validate_reference(unknown, fixed, root)

    def test_empty_planning_populations_still_advertise_profiles_and_exact_task_sets(self):
        with tempfile.TemporaryDirectory() as directory:
            for role in ('research_plan', 'research_preparation'):
                with self.subTest(role=role):
                    fixed = advertised_input(Path(directory) / role, role)['validation_context']
                    self.assertEqual(fixed['tasks'], [])
                    self.assertEqual(fixed['task_catalog'], [])
                    self.assertEqual(fixed['profile_selection']['task_profile_constraints'], {})
                    self.assertGreater(len(fixed['profile_selection']['allowed_profiles']), 0)
                    if role == 'research_plan':
                        self.assertEqual(fixed['ready_task_ids'], [])
                        self.assertEqual(fixed['returned_task_ids'], [])
