"""Postsolution academic requirements as pure rules (``academic``, layer 1), moved from ``test_academic``.

Requirement editions, criterion assessments, external rejections and their
sealed resolutions, external-effect receipts, the academic prerequisite of an
external request and the currentness of the solution basis. The records are
plain dictionaries; the engine's use of these rules is
``sim.test_academic_consumers``.
"""
from copy import deepcopy
import unittest

from do_math import academic
from do_math.academic import (academic_status, assess, current_requirements, effect_receipts, record_resolution,
                              requirement_record, solution_basis)
from do_math.external import prepare_operation
from do_math.knowledge import capture_basis
from record_fixtures import domain_governance


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
        # No task or applied TASKS assessment stands behind the record, so it is not current.
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'pending')
        with self.assertRaisesRegex(ValueError, '^assessment must cover each exact criterion once$'):
            assess('paper', self.basis, requirements, 'satisfied', [
                {'criterion': 'publish', 'satisfied': True, 'evidence': 'report'}])

    def test_rejection_needs_a_structured_current_resolution(self):
        self.runtime['external_rejections'] = [{'id': 'RJ', 'solution_basis': self.basis,
            'resolved': True, 'resolution_evidence': ['unbound prose'], 'source_ref': 'planner-evidence'}]
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'externally_rejected')
        # A hand-written resolution row without the sealed rejection and evidence hashes resolves nothing.
        unsealed = {**self.runtime, 'academic_resolution_records': [{'rejection_id': 'RJ', 'solution_basis': self.basis,
            'decision': 'resolved', 'execution_id': 'E', 'evidence_refs': ['artifact:response'], 'current': True}]}
        self.assertEqual(academic_status(self.instance, unsealed, self.basis)['status'], 'externally_rejected')
        self.runtime['executions'] = {'E': {'role': 'research_plan', 'input_solution_basis': self.basis},
            'EX-evidence': {'id': 'EX-evidence', 'role': 'research_work', 'report': 'Planner evidence'}}
        record_resolution(self.instance, self.runtime, self.basis,
            {'id': 'RJ', 'decision': 'resolved', 'evidence': 'Addresses objection', 'evidence_refs': ['EX-evidence']},
            execution_id='E')
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis)['status'], 'pending')

    def test_invalid_requirement_shapes_are_rejected(self):
        cases = (({'id': 'x'}, "^academic requirement/: 'scope' is a required property$"),
                 ({**self.requirement, 'criteria': [], 'assessor': 'other'},
                  "^academic requirement/assessor: 'other' is not one of \\['research_plan'\\]$"),
                 ({**self.requirement, 'required_inputs': ['x', 'x']},
                  "^academic requirement/required_inputs: \\['x', 'x'\\] has non-unique elements$"),
                 ({**self.requirement, 'external_effects': [{'id': 'e', 'scope': 'x'}, {'id': 'e', 'scope': 'y'}]},
                  '^academic external effects need distinct IDs$'))
        for value, reason in cases:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, reason):
                requirement_record([value])

    def test_unsolved_not_applicable(self):
        self.instance['goal_status'] = 'unsolved'
        self.assertEqual(academic_status(self.instance, self.runtime, self.basis),
                         {'status': 'not_applicable', 'reason': 'goal not mathematically solved'})

    def test_effect_receipts_require_the_exact_successful_operation(self):
        requirements = requirement_record([{**self.requirement, 'required_inputs': ['context:goal'],
            'external_effects': [{'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'G'}]}])
        requirement = requirements['items'][0]
        arguments = dict(task_id='T', requirements_sha256=requirements['sha256'], solution_basis_value=self.basis,
                         runtime=self.runtime)
        self.assertFalse(effect_receipts(requirement, **arguments)[0])
        self.runtime['external_operations'] = {'OP': {'id': 'OP', 'status': 'confirmed', 'succeeded': True,
            'grant_id': 'G', 'request_sha256': 'r', 'academic_binding': {
                'task_id': 'T', 'requirement_id': 'paper', 'requirements_sha256': requirements['sha256'],
                'solution_basis': self.basis, 'effect_id': 'submit'}}}
        self.assertEqual(effect_receipts(requirement, **arguments),
                         (True, [{'effect_id': 'submit', 'operation_id': 'OP', 'grant_id': 'G', 'request_sha256': 'r'}]))
        self.runtime['external_operations']['OP']['succeeded'] = False
        self.assertFalse(effect_receipts(requirement, **arguments)[0])


class AcademicGovernanceTests(unittest.TestCase):
    def test_resolution_is_current_only_while_its_real_evidence_is_unchanged(self):
        i = domain_governance()
        i["goal_status"] = "mathematically_solved"
        basis = solution_basis("CH1", [{"id": "K"}])
        rt = {"external_rejections": [{"id": "RJ", "solution_basis": basis, "text": "Missing argument"}],
              "executions": {"E": {"role": "research_plan", "input_solution_basis": basis}}}
        # Artifact evidence is not a state record family; the engine resolves it
        # from stored bytes (academic_engine._academic_evidence).
        ref = "runtime/artifacts/BA-response/response.md"
        stored = {ref: b"Full response"}
        resolution = {"id": "RJ", "decision": "resolved", "evidence": "Response addresses objection", "evidence_refs": [ref]}
        with self.assertRaisesRegex(ValueError, "^academic evidence must resolve uniquely: " + ref + "$"):
            academic.record_resolution(i, rt, basis, resolution, execution_id="E")
        academic.record_resolution(i, rt, basis, resolution, execution_id="E", resolve_evidence=stored.get)
        self.assertEqual(academic.unresolved_rejections(i, rt, basis, resolve_evidence=stored.get), [])
        stored[ref] = b"changed"
        self.assertEqual(academic.unresolved_rejections(i, rt, basis, resolve_evidence=stored.get),
                         [{"id": "RJ", "solution_basis": basis, "text": "Missing argument"}])

    def test_generic_academic_request_must_bind_the_solution_it_relied_on(self):
        i = domain_governance()
        i["goal_status"] = "mathematically_solved"
        basis = solution_basis("CH1", [{"id": "K"}])
        rt = {}
        grant = {"id": "G", "academic_only": True}
        operation = prepare_operation({"method": "POST", "url": "https://example.test/p"}, "G", "S")
        self.assertFalse(academic.external_prerequisite(i, rt, basis, operation, grant))
        operation = academic.bind_external_prerequisite(i, rt, basis, operation)
        self.assertTrue(academic.external_prerequisite(i, rt, basis, operation, grant))
        self.assertFalse(academic.external_prerequisite(i, rt, solution_basis("CH2", [{"id": "K"}]), operation, grant))

    def test_academic_basis_rejects_a_stale_judgment_dependency(self):
        """The engine's ``_solution_basis`` is this function of its state (``academic_engine``)."""
        instance = {"goal_status": "mathematically_solved", "goal_revision": 1, "knowledge": {"K": {"id": "K", "text": "new"}},
                    "goal_assessment_basis": "B"}
        instance["goal_judgments"] = [{"execution_id": "E", "basis": "B", "current": True, "dependencies": ["K"],
                                       "record_basis": capture_basis({"knowledge": {"K": {"id": "K", "text": "old"}}}, {}, ["K"])}]
        self.assertIsNone(academic.current_solution_basis(instance, {}))


if __name__ == '__main__':
    unittest.main()
