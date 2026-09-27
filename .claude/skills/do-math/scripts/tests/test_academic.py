from copy import deepcopy
from pathlib import Path
import sys
import unittest
import json
from unittest.mock import create_autospec
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.academic import (academic_status, assess, current_requirements,
    effect_receipts, record_resolution, requirement_record, solution_basis)
from do_math import governance as gov
from do_math.external import prepare_operation
from record_fixtures import domain_governance
from research_fixtures import approved_governance, bare_engine, charter, disposition, review_items


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
        # A hand-written resolution row without the sealed rejection and evidence hashes resolves nothing.
        unsealed = {**self.runtime, 'academic_resolution_records': [{'rejection_id': 'RJ', 'solution_basis': self.basis,
            'decision': 'resolved', 'execution_id': 'E', 'evidence_refs': ['artifact:response'], 'current': True}]}
        self.assertEqual(academic_status(self.instance, unsealed, self.basis)['status'], 'externally_rejected')
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


class AcademicConsumerTests(unittest.TestCase):
    """Actual academic producer and TASKS consumers; mathematical evidence is synthetic."""

    def host(self):
        from do_math.execution_profiles import seal_profile, profile_ref, BOUNDARY
        from do_math.governance import timestamp
        h = bare_engine()
        h._solution_basis = create_autospec(h._solution_basis, side_effect=lambda: deepcopy(h.basis))
        h._academic_evidence = create_autospec(h._academic_evidence, return_value=None)
        h._lifecycle_now = create_autospec(h._lifecycle_now, return_value=timestamp('2026-09-20T00:00:00Z'))
        h.instance = approved_governance({'id': 'I'}, [charter(academic_requirements=[{'id': 'AR',
            'scope': 'Prepare a manuscript', 'assessor': 'research_plan',
            'criteria': ['Explain the proof', 'Discuss the limitations']}])],
            source=('S', 'Synthetic approval of a manuscript requirement'))
        from do_math.execution_profiles import build_profiles
        from do_math.configuration import DEFAULT_CONFIG
        config = {**deepcopy(DEFAULT_CONFIG),
                  'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}
        # Adopt every research_work tier edition, as initialization does: an
        # unassessed work task requires the high tier (model_policy.selection).
        built = build_profiles(config)
        h.instance.update(goal_status='mathematically_solved', knowledge={}, sources=[], config=config,
            execution_profiles=built['execution_profiles'],
            role_profile_refs={'research_work': built['role_profile_refs']['research_work']},
            grants={'G': {'id': 'G', 'kind': 'local', 'status': 'active', 'roles': ['research_work'],
                          'source_ref': 'S', 'reuse': 'reusable', 'resource_limits': {}}})
        h.runtime = {'status': 'ready', 'tasks': {}, 'executions': {}, 'queue': [], 'inputs': [],
                     'waiting_actions': {}, 'history': [], 'questions': []}
        h.basis = solution_basis('synthetic-current-goal', [h.instance['governance_sources']['S']])
        return h

    def generated(self):
        h = self.host(); h._ensure_academic_followup()
        return h, next(iter(h.runtime['tasks'].values()))

    def reviewed(self):
        from do_math import planning
        h, task = self.generated()
        from research_fixtures import prepared_rule_conditions
        action = next(a for a in h.runtime['queue'] if a.get('observation_rule_targets'))
        h.runtime['executions']['PREP'] = {'id': 'PREP', 'role': 'research_preparation', 'status': 'ended',
            'action': action, 'extensions': {'task_conditions': prepared_rule_conditions([task['id']])}}
        h._finish_assessment_preparation(action, 'PREP')
        h._remove_action(action)
        output = review_items([task['id']], next_owner='research_preparation')
        task['reviews'].append(planning.seal_contract_review(task, output, h.instance, h.runtime, execution_id='REVIEW'))
        return h, task

    def assessed(self, *, kind='fulfilled', decision='completed'):
        from do_math.task_scope import apply_task_assessments
        h, task = self.reviewed()
        tid = task['id']
        task['results'] = [{'execution_id': 'WORK', 'report': 'Synthetic returned manuscript'}]
        h.runtime['executions'].update(WORK={'id': 'WORK', 'role': 'research_work', 'status': 'ended', 'action': {'target': tid}},
            PLAN={'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_solution_basis': deepcopy(h.basis)})
        assessment = {'task_id': tid, 'decision': decision, 'reason': 'Synthetic assessment of the returned manuscript',
            'item_dispositions': [{'obligation_id': o['id'], 'kind': kind, 'evidence_refs': ['WORK']}
                                  for o in task['completion_obligations']], 'unresolved': []}
        h.instance, h.runtime = apply_task_assessments(h.instance, h.runtime, [assessment],
            execution_id='PLAN', input_tasks=deepcopy(h.runtime['tasks']))
        return h, h.runtime['tasks'][tid], assessment

    def test_actual_constructor_review_and_ready_population_use_the_task_contract(self):
        from do_math import planning, task_contracts
        h, task = self.reviewed()
        task_contracts.validate_task_contract(task)
        self.assertEqual([o['claim'] for o in task['completion_obligations']],
                         ['Explain the proof', 'Discuss the limitations'])
        self.assertEqual(task['profile_refs'], h.instance['role_profile_refs']['research_work'])
        self.assertEqual(task['authority_refs'], ['G'])
        self.assertTrue({row['id'] for row in h.basis['records']}.issubset(task['inputs']))
        self.assertNotIn('completion_criteria', task)
        self.assertEqual(planning.task_ready(task, h.instance, h.runtime)['state'], 'ready')
        self.assertEqual(planning.ready_task_ids(h.runtime, h.instance), [task['id']])
        h._ensure_academic_followup()
        self.assertEqual(len(h.runtime['tasks']), 1)

    def test_actual_assessment_consumer_uses_item_dispositions_and_current_evidence(self):
        h, task, assessment = self.assessed()
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(h._academic_status()['status'], 'completed')
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(len(h.runtime['academic_assessments']), 1)
        h.runtime['executions']['WORK']['changed_evidence'] = True
        self.assertNotEqual(h._academic_status()['status'], 'completed')
        with self.assertRaises(ValueError): h._record_academic_assessment(task, assessment, 'PLAN')

    def test_open_disposition_keeps_followup_in_same_task_contract(self):
        h, task, assessment = self.assessed(kind='open', decision='incomplete')
        h._record_academic_assessment(task, assessment, 'PLAN')
        self.assertEqual(task['status'], 'waiting')
        self.assertEqual(h.runtime['academic_assessments'][0]['decision'], 'not_satisfied')
        h._ensure_academic_followup()
        self.assertEqual(len(h.runtime['tasks']), 1)

    def test_engine_plan_dispatch_consumes_generated_contract_and_applied_assessment(self):
        from do_math.engine import ResearchEngine
        from do_math.repository import ResearchRepository
        h, task = self.reviewed()
        tid = task['id']
        h.runtime['executions']['SELECT'] = {'id': 'SELECT', 'role': 'research_plan', 'status': 'ended', 'input_snapshot': 'before-work', 'input_bundle': 'BA-select'}
        first = deepcopy((h.instance, h.runtime))
        h.store = create_autospec(ResearchRepository, instance=True)
        h.store.view.side_effect = lambda snapshot: (snapshot, *deepcopy(first))
        h.store.read.side_effect = lambda path, snapshot: json.dumps({'snapshot': 'before-work', 'tasks': list(first[1]['tasks'].values()), 'ready_task_ids': [tid]}).encode()
        h.head = 'before-work'
        h._evaluation_context = create_autospec(h._evaluation_context, side_effect=lambda snapshot=None: {'snapshot': snapshot})
        ResearchEngine._apply_plan(h, {'dispositions': [{**disposition(tid), 'reason': 'Current academic work',
            'expected_research_change': 'Complete the manuscript'}],
            'task_assessments': [], 'goal_audit': False}, 'SELECT')
        task = h.runtime['tasks'][tid]
        self.assertEqual(task['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == tid for a in h.runtime['queue']))
        task['results'] = [{'execution_id': 'WORK', 'report': 'Synthetic manuscript'}]
        h.runtime['executions'].update(WORK={'id': 'WORK', 'role': 'research_work', 'status': 'ended', 'action': {'target': tid}},
            PLAN={'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_snapshot': 'after-work', 'input_bundle': 'BA-returned', 'input_solution_basis': h.basis})
        returned = deepcopy((h.instance, h.runtime))
        h.store = create_autospec(ResearchRepository, instance=True)
        h.store.view.side_effect = lambda snapshot: (snapshot, *deepcopy(returned))
        h.store.read.side_effect = lambda path, snapshot: json.dumps({'snapshot': 'after-work', 'tasks': list(returned[1]['tasks'].values()), 'ready_task_ids': []}).encode()
        h.head = 'after-work'
        assessment = {'task_id': tid, 'decision': 'completed', 'reason': 'Synthetic assessment of the returned manuscript',
            'item_dispositions': [{'obligation_id': o['id'], 'kind': 'fulfilled', 'evidence_refs': ['WORK']}
                                  for o in task['completion_obligations']], 'unresolved': []}
        ResearchEngine._apply_plan(h, {'dispositions': [], 'task_assessments': [assessment], 'goal_audit': False}, 'PLAN')
        self.assertEqual(h.runtime['tasks'][tid]['status'], 'completed')
        self.assertEqual(h._academic_status()['status'], 'completed')
        self.assertEqual(h.runtime['status'], 'completed')

    def test_unapplied_or_different_assessment_cannot_certify_academic_success(self):
        h, task, assessment = self.assessed()
        forged = deepcopy(assessment); forged['item_dispositions'][0]['evidence_refs'] = ['not-in-input']
        with self.assertRaises(ValueError): h._record_academic_assessment(task, forged, 'PLAN')
        task.pop('assessment')
        with self.assertRaises(ValueError): h._record_academic_assessment(task, assessment, 'PLAN')

    def test_scope_waiver_records_authority_without_applying_a_second_task_lifecycle(self):
        from do_math.planning import contract_hash
        from do_math.task_scope import apply_task_assessments
        h, task = self.generated()
        task['results'] = [{'execution_id': 'WORK', 'report': 'Cannot satisfy the requirement'}]
        change = {'kind': 'task_scope', 'decision_id': 'WAIVER', 'task_id': task['id'],
            'disposition': 'waive', 'revision': task['revision'], 'contract_sha256': contract_hash(task),
            'obligation_ids': [row['id'] for row in task['completion_obligations']], 'reason': 'Synthetic explicit waiver'}
        before = deepcopy(task)
        h.instance, h.runtime, decision = gov.apply_decision(h.instance, h.runtime, change, source_ref='S')
        self.assertEqual(h.runtime['tasks'][task['id']], before)
        h.runtime['executions']['PLAN'] = {'id': 'PLAN', 'role': 'research_plan', 'status': 'ended', 'input_solution_basis': h.basis}
        assessment = {'task_id': task['id'], 'decision': 'closed', 'reason': 'Synthetic waiver of every obligation',
            'item_dispositions': [{'obligation_id': row['id'], 'kind': 'waived', 'authority_ref': decision['id'],
                                   'evidence_refs': ['WORK']} for row in task['completion_obligations']], 'unresolved': []}
        h.instance, h.runtime = apply_task_assessments(h.instance, h.runtime, [assessment],
            execution_id='PLAN', input_tasks=deepcopy(h.runtime['tasks']))
        h._record_academic_assessment(h.runtime['tasks'][task['id']], assessment, 'PLAN')
        self.assertNotEqual(h._academic_status()['status'], 'completed')

    def test_task_scope_transfer_decision_changes_no_task_and_requires_the_current_contract(self):
        from do_math.planning import contract_hash
        h, task = self.generated()
        h.runtime['tasks']['RECIPIENT'] = {**deepcopy(task), 'id': 'RECIPIENT'}
        change = {'kind': 'task_scope', 'task_id': task['id'], 'disposition': 'transfer',
            'target_task_id': 'RECIPIENT', 'revision': task['revision'], 'contract_sha256': contract_hash(task),
            'obligation_ids': [task['completion_obligations'][0]['id']], 'reason': 'Transfer only the first obligation'}
        i, rt, _ = gov.apply_decision(h.instance, h.runtime, change, source_ref='S')
        self.assertEqual(rt['tasks'], h.runtime['tasks'])
        change['contract_sha256'] = 'stale'
        with self.assertRaises(ValueError): gov.apply_decision(h.instance, h.runtime, change, source_ref='S')

    def test_academic_only_charter_change_preserves_math_fact_and_replaces_requirement_task(self):
        h, task = self.generated()
        record = charter('CH2'); record['supersedes'] = ['CH1']
        record['content']['academic_requirements'] = [{'id': 'AR', 'scope': 'Prepare a manuscript',
            'assessor': 'research_plan', 'criteria': ['Revised manuscript']}]
        h.instance, h.runtime, _ = gov.apply_decision(h.instance, h.runtime,
            {'kind': 'charter', 'record': record}, source_ref='S')
        self.assertEqual(h.instance['goal_status'], 'mathematically_solved')
        h._ensure_academic_followup()
        self.assertEqual(h.runtime['tasks'][task['id']]['status'], 'closed')
        current = [t for t in h.runtime['tasks'].values() if t['status'] != 'closed']
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]['completion_obligations'][0]['claim'], 'Revised manuscript')
        changed = charter('CH3', 'Prove Q'); changed['supersedes'] = ['CH2']
        h.instance, h.runtime, _ = gov.apply_decision(h.instance, h.runtime,
            {'kind': 'charter', 'record': changed}, source_ref='S')
        self.assertEqual(h.instance['goal_status'], 'unsolved')


class AcademicGovernanceTests(unittest.TestCase):
    def test_resolution_is_current_only_while_its_real_evidence_is_unchanged(self):
        from do_math import academic
        i = domain_governance(); i["goal_status"] = "mathematically_solved"
        basis = solution_basis("CH1", [{"id": "K"}])
        rt = {"external_rejections": [{"id": "RJ", "solution_basis": basis, "text": "Missing argument"}],
              "executions": {"E": {"role": "research_plan", "input_solution_basis": basis}}}
        # Artifact evidence is not a state record family; the engine resolves it
        # from stored bytes (academic_engine._academic_evidence).
        ref = "runtime/artifacts/BA-response/response.md"
        stored = {ref: b"Full response"}
        with self.assertRaises(ValueError):
            academic.record_resolution(i, rt, basis, {"id": "RJ", "decision": "resolved", "evidence": "Response addresses objection",
                                                      "evidence_refs": [ref]}, execution_id="E")
        academic.record_resolution(i, rt, basis, {"id": "RJ", "decision": "resolved", "evidence": "Response addresses objection", "evidence_refs": [ref]},
                                   execution_id="E", resolve_evidence=stored.get)
        self.assertEqual(academic.unresolved_rejections(i, rt, basis, resolve_evidence=stored.get), [])
        stored[ref] = b"changed"
        self.assertEqual(len(academic.unresolved_rejections(i, rt, basis, resolve_evidence=stored.get)), 1)

    def test_generic_academic_request_must_bind_the_solution_it_relied_on(self):
        from do_math import academic
        i=domain_governance();i["goal_status"]="mathematically_solved"
        basis=solution_basis("CH1",[{"id":"K"}]);rt={}
        grant={"id":"G","academic_only":True}
        operation=prepare_operation({"method":"POST","url":"https://example.test/p"},"G","S")
        self.assertFalse(academic.external_prerequisite(i,rt,basis,operation,grant))
        operation=academic.bind_external_prerequisite(i,rt,basis,operation)
        self.assertTrue(academic.external_prerequisite(i,rt,basis,operation,grant))
        self.assertFalse(academic.external_prerequisite(i,rt,solution_basis("CH2",[{"id":"K"}]),operation,grant))

    def test_academic_basis_rejects_a_stale_judgment_dependency(self):
        from do_math.knowledge import capture_basis
        h=bare_engine();h.instance={"goal_status":"mathematically_solved","goal_revision":1,"knowledge":{"K":{"id":"K","text":"new"}},"goal_assessment_basis":"B"};h.runtime={}
        h.instance["goal_judgments"]=[{"execution_id":"E","basis":"B","current":True,"dependencies":["K"],"record_basis":capture_basis({"knowledge":{"K":{"id":"K","text":"old"}}},{},["K"])}]
        self.assertIsNone(h._solution_basis())


if __name__ == '__main__':
    unittest.main()
