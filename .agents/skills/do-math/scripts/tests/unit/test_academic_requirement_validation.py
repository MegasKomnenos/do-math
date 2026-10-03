"""학술 요구·평가 입력의 정확한 거부 사유와 원본 불변을 검사한다."""
from copy import deepcopy
import unittest

from do_math import academic
from do_math.canonical import exact_content_hash
from support.academic_scenes import MANUSCRIPT


class RequirementValidationTests(unittest.TestCase):
    def setUp(self):
        self.requirements = academic.requirement_record([deepcopy(MANUSCRIPT)])
        self.basis = academic.solution_basis('goal', [{'id': 'K', 'text': '합성 증거'}])
        self.evidence = [{'criterion': claim, 'satisfied': True, 'evidence': '합성 보고서'}
                         for claim in MANUSCRIPT['criteria']]

    def test_requirement_container_rejects_non_list_and_non_objects(self):
        for value in ({}, None, [None], ['requirement']):
            with self.subTest(value=value):
                before = deepcopy(value)
                with self.assertRaisesRegex(ValueError, '^requirements must be objects$'):
                    academic.requirement_record(value)
                self.assertEqual(value, before)

    def test_duplicate_requirement_identity_is_rejected(self):
        value = [deepcopy(MANUSCRIPT), deepcopy(MANUSCRIPT)]
        before = deepcopy(value)
        with self.assertRaisesRegex(ValueError, '^requirements need distinct IDs$'):
            academic.requirement_record(value)
        self.assertEqual(value, before)

    def test_requirement_defaults_hash_and_copy_are_exact(self):
        source = deepcopy(MANUSCRIPT)
        record = academic.requirement_record([source])
        expected = {**MANUSCRIPT, 'required_inputs': [], 'external_effects': []}
        self.assertEqual(record, {'items': [expected], 'sha256': exact_content_hash({'items': [expected]})})
        record['items'][0]['criteria'].append('추가')
        self.assertEqual(source, MANUSCRIPT)

    def test_solution_basis_rejects_missing_goal_or_records(self):
        for goal, records in ((None, [{'id': 'K'}]), ('', [{'id': 'K'}]), ('goal', [])):
            with self.subTest(goal=goal, records=records):
                with self.assertRaisesRegex(ValueError, '^solution basis needs goal and records$'):
                    academic.solution_basis(goal, records)
                self.assertEqual(records, [] if goal == 'goal' else [{'id': 'K'}])

    def test_solution_basis_seals_each_actual_record(self):
        records = [{'id': 'K', 'text': '합성 증거'}, {'id': 'EX', 'text': '합성 판정'}]
        self.assertEqual(academic.solution_basis('goal', records), {
            'goal_ref': 'goal', 'records': [{'id': row['id'], 'sha256': exact_content_hash(row)} for row in records]})

    def test_assessment_rejects_unknown_decision_or_empty_evidence(self):
        for decision, evidence in (('approved', self.evidence), ('satisfied', []), ('satisfied', {})):
            with self.subTest(decision=decision, evidence=evidence):
                before = deepcopy(self.requirements)
                with self.assertRaisesRegex(ValueError, '^assessment needs decision and evidence$'):
                    academic.assess('AR', self.basis, self.requirements, decision, evidence)
                self.assertEqual(self.requirements, before)

    def test_assessment_rejects_unknown_requirement(self):
        with self.assertRaisesRegex(ValueError, '^unknown requirement$'):
            academic.assess('missing', self.basis, self.requirements, 'satisfied', self.evidence)
        self.assertEqual(self.requirements['items'][0]['id'], 'AR')

    def test_assessment_rejects_one_malformed_evidence_field(self):
        for key, value in (('criterion', 1), ('satisfied', 1), ('evidence', None)):
            with self.subTest(key=key):
                evidence = deepcopy(self.evidence)
                evidence[0][key] = value
                before = deepcopy(evidence)
                with self.assertRaisesRegex(ValueError, '^invalid criteria evidence$'):
                    academic.assess('AR', self.basis, self.requirements, 'satisfied', evidence)
                self.assertEqual(evidence, before)

    def test_assessment_rejects_non_object_evidence_row(self):
        with self.assertRaisesRegex(ValueError, '^invalid criteria evidence$'):
            academic.assess('AR', self.basis, self.requirements, 'satisfied', [None])

    def test_assessment_rejects_duplicate_missing_and_foreign_criteria(self):
        for evidence in ([self.evidence[0], self.evidence[0]], self.evidence[:1],
                         [{**self.evidence[0], 'criterion': 'foreign'}, self.evidence[1]]):
            with self.subTest(evidence=evidence):
                before = deepcopy(evidence)
                with self.assertRaisesRegex(ValueError, '^assessment must cover each exact criterion once$'):
                    academic.assess('AR', self.basis, self.requirements, 'satisfied', evidence)
                self.assertEqual(evidence, before)

    def test_satisfied_assessment_requires_true_and_substantive_evidence(self):
        for key, value in (('satisfied', False), ('evidence', ' \t')):
            with self.subTest(key=key):
                evidence = deepcopy(self.evidence)
                evidence[0][key] = value
                with self.assertRaisesRegex(ValueError, '^satisfied assessment lacks exact criteria evidence$'):
                    academic.assess('AR', self.basis, self.requirements, 'satisfied', evidence)
                self.assertEqual(evidence[0][key], value)

    def test_assessment_copies_basis_and_evidence_for_each_verdict(self):
        for decision in ('satisfied', 'not_satisfied', 'unresolved'):
            with self.subTest(decision=decision):
                basis, evidence = deepcopy(self.basis), deepcopy(self.evidence)
                result = academic.assess('AR', basis, self.requirements, decision, evidence)
                self.assertEqual(result, {'requirement_id': 'AR', 'solution_basis': basis,
                    'requirements_sha256': self.requirements['sha256'], 'decision': decision,
                    'evidence': evidence, 'assessor': 'research_plan'})
                result['solution_basis']['records'].clear()
                result['evidence'][0]['evidence'] = '변조'
                self.assertEqual(basis, self.basis)
                self.assertEqual(evidence, self.evidence)

    def test_criterion_obligations_preserve_order_and_identity(self):
        self.assertEqual(academic.criterion_obligations('TK', self.requirements['items'][0]), [
            {'id': 'TK:criterion:1', 'claim': MANUSCRIPT['criteria'][0], 'judges': ['research_plan'], 'evidence_required': []},
            {'id': 'TK:criterion:2', 'claim': MANUSCRIPT['criteria'][1], 'judges': ['research_plan'], 'evidence_required': []}])

    def test_unsolved_assurance_copies_state_without_claiming_proof(self):
        instance = {'goal_status': 'mathematically_solved', 'goal_judgments': [{'execution_id': 'EX'}]}
        before = deepcopy(instance)
        result = academic.apply_goal_assurance(instance, decision='unsolved', basis=None, judgments=[])
        self.assertEqual(result, {**before, 'goal_status': 'unsolved', 'goal_assessment_basis': None})
        result['goal_judgments'].clear()
        self.assertEqual(instance, before)

    def test_nonformal_assurance_is_rejected_without_state_change(self):
        instance = {'goal_status': 'unsolved'}
        with self.assertRaisesRegex(ValueError, '^nonformal final goal assurance is not supported$'):
            academic.apply_goal_assurance(instance, decision='completed', basis=self.basis, judgments=[])
        self.assertEqual(instance, {'goal_status': 'unsolved'})
