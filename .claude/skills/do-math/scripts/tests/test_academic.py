from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.academic import (academic_status, assess, current_requirements,
    effect_receipts, record_resolution, requirement_record, solution_basis)


class Tests(unittest.TestCase):
    def setUp(self):
        self.requirement = {'id': 'paper', 'scope': 'solution', 'criteria': ['draft'], 'assessor': 'research_plan'}
        self.instance = {'goal_status': 'mathematically_solved', 'governance': {'CH': {
            'id': 'CH', 'kind': 'charter', 'revision': 1, 'status': 'active',
            'content': {'goal': 'P', 'academic_requirements': [self.requirement]}}}}
        self.basis = solution_basis('goal', [{'id': 'K', 'value': 1}])
        self.runtime = {'tasks': {}, 'academic_assessments': [], 'external_rejections': []}

    def test_requirements_follow_the_charter_edition(self):
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'pending')
        changed = deepcopy(self.instance)
        changed['governance']['CH']['revision'] = 2
        changed['governance']['CH']['content']['academic_requirements'][0]['criteria'] = ['publish']
        self.assertNotEqual(current_requirements(changed)['sha256'], current_requirements(self.instance)['sha256'])

    def test_assessment_covers_exact_criteria_but_does_not_replace_task_evidence(self):
        requirements = current_requirements(self.instance)
        assessment = assess('paper', self.basis, requirements, 'satisfied', [
            {'criterion': 'draft', 'satisfied': True, 'evidence': 'report'}])
        self.runtime['academic_assessments'] = [assessment]
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'pending')
        with self.assertRaises(ValueError):
            assess('paper', self.basis, requirements, 'satisfied', [
                {'criterion': 'publish', 'satisfied': True, 'evidence': 'report'}])

    def test_rejection_needs_a_structured_current_resolution(self):
        self.runtime['external_rejections'] = [{'id': 'RJ', 'solution_basis': self.basis,
            'resolved': True, 'resolution_evidence': ['unbound prose'], 'source_ref': 'planner-evidence'}]
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'externally_rejected')
        self.runtime['executions'] = {'E': {'role': 'research_plan', 'input_solution_basis': self.basis},
            'EX-evidence': {'id': 'EX-evidence', 'role': 'research_work', 'report': 'Planner evidence'}}
        record_resolution(self.instance, self.runtime, self.basis,
            {'id': 'RJ', 'decision': 'resolved', 'evidence': 'Addresses objection', 'evidence_refs': ['EX-evidence']}, execution_id='E')
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'pending')

    def test_invalid_requirement_shapes_are_rejected(self):
        for value in ({'id': 'x'}, {**self.requirement, 'criteria': [], 'assessor': 'other'},
                      {**self.requirement, 'required_inputs': ['x', 'x']},
                      {**self.requirement, 'external_effects': [{'id': 'e', 'scope': 'x'}, {'id': 'e', 'scope': 'y'}]}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                requirement_record([value])

    def test_unsolved_not_applicable(self):
        self.instance['goal_status'] = 'unsolved'
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'not_applicable')

    def test_effect_receipts_require_the_exact_successful_operation(self):
        requirements = requirement_record([{**self.requirement, 'required_inputs': ['context:goal'],
            'external_effects': [{'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'G'}]}])
        requirement = requirements['items'][0]
        arguments = dict(task_id='T', requirements_sha256=requirements['sha256'], solution_basis_value=self.basis, runtime=self.runtime)
        self.assertFalse(effect_receipts(requirement, **arguments)[0])
        self.runtime['external_operations'] = {'OP': {'id': 'OP', 'status': 'confirmed', 'succeeded': True,
            'grant_id': 'G', 'request_sha256': 'r', 'academic_binding': {
                'task_id': 'T', 'requirement_id': 'paper', 'requirements_sha256': requirements['sha256'],
                'solution_basis': self.basis, 'effect_id': 'submit'}}}
        self.assertTrue(effect_receipts(requirement, **arguments)[0])
        self.runtime['external_operations']['OP']['succeeded'] = False
        self.assertFalse(effect_receipts(requirement, **arguments)[0])


if __name__ == '__main__':
    unittest.main()
