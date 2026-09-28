from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.input_basis import capture_decision_basis, decision_basis_changes
from do_math import integration, planning, revisions
from research_fixtures import approved_governance, bare_engine, candidate, contract_review, charter_record
from do_math.knowledge_records import create_candidate


class BasisTests(unittest.TestCase):
    def test_current_resolution_commits_only_with_its_complete_bundle(self):
        owner = bare_engine()
        action = {'id': 'AC-current', 'role': 'research_plan', 'target': 'A'}
        output = {'summary': 'Resolve the prior failure', 'used_sources': [], 'questions': [],
                  'dispositions': [], 'task_assessments': [], 'preparation_requests': [], 'goal_audit': False}
        context = {'action': action, 'execution_id': 'EX-current', 'snapshot': 'a' * 40}
        claim = {'action_id': 'AC-failed', 'evidence_execution_id': 'current',
                 'reason': 'The current accepted judgment covers the failed request'}
        runtime = {'history': [], 'integrations': {}, 'waiting_actions': {'AC-failed': {
            'kind': 'execution_failure', 'execution_id': 'EX-failed',
            'action': {'role': 'research_plan', 'target': 'A'}}},
            'executions': {'EX-current': {'action': action, 'extensions': {'action_resolutions': [claim]}}}}
        def apply(instance, candidate, bundle):
            owner.runtime = candidate
            owner.instance = instance
            owner._apply_action_resolutions('EX-current', accepting_current=True)
        def run(state, validate, publish=lambda *_: None):
            return integration.apply_bundles({}, state, output, {}, context, execution_id='EX-current',
                apply_bundle=apply, validate_current=lambda *_: None,
                validate_candidate=validate, publish=publish)
        before = deepcopy(runtime)
        failed = run(runtime, lambda *_: (_ for _ in ()).throw(ValueError('later candidate failure')))
        self.assertEqual(failed['status'], 'returned')
        self.assertEqual(runtime, before)
        unpublished = run(runtime, lambda *_: None,
            publish=lambda *_: (_ for _ in ()).throw(OSError('Git publication failed')))
        self.assertEqual(unpublished['status'], 'returned')
        self.assertEqual(runtime, before)
        accepted = run(runtime, lambda *_: None)
        self.assertEqual(accepted['status'], 'accepted')
        self.assertEqual(accepted['runtime']['waiting_actions'], {})
        self.assertEqual(len(accepted['runtime']['history']), 1)
        replay = run(accepted['runtime'], lambda *_: None)
        self.assertEqual(replay['runtime']['history'], accepted['runtime']['history'])

    def test_current_resolution_requires_its_validated_bundle_and_same_scope(self):
        for accepting, evidence_id, target, allowed in (
            (False, 'current', 'A', False),
            (True, 'current', 'A', True),
            (True, 'current', 'B', False),
            (True, 'EX-other', 'A', False),
        ):
            with self.subTest(accepting=accepting, evidence=evidence_id, target=target):
                owner = bare_engine({})
                claim = {'action_id': 'AC-failed', 'evidence_execution_id': evidence_id,
                         'reason': 'The validated current judgment discharges the same obligation'}
                owner.runtime = {'history': [], 'waiting_actions': {'AC-failed': {
                    'kind': 'execution_failure', 'execution_id': 'EX-failed',
                    'action': {'role': 'research_plan', 'target': 'A'}}}, 'executions': {
                    'EX-current': {'action': {'role': 'research_plan', 'target': target},
                                   'extensions': {'action_resolutions': [claim]}},
                    'EX-other': {'action': {'role': 'research_plan', 'target': 'A'}}}}
                if allowed:
                    owner._apply_action_resolutions('EX-current', accepting_current=accepting)
                    self.assertEqual(owner.runtime['waiting_actions'], {})
                    self.assertEqual(owner.runtime['history'][0]['resolved_by'], 'EX-current')
                else:
                    before = deepcopy(owner.runtime)
                    # Unaccepted evidence and a different target both fail the same-scope rule.
                    with self.assertRaisesRegex(ValueError, 'same judgment scope'):
                        owner._apply_action_resolutions('EX-current', accepting_current=accepting)
                    self.assertEqual(owner.runtime, before)

    def setUp(self):
        # Explicit synthetic approval is an input to this domain-level test.
        # No engine lifecycle or activation evidence is injected.
        text = "Preserve approved task premises"
        self.instance = approved_governance({"knowledge": {}, "sources": []}, [charter_record(text)],
                                            source=("UI-basis-fixture", text), approval_id="DC-basis-fixture")
        self.runtime = {"tasks": {"A": {**candidate("A"), "id": "A", "revision": 1, "question": "original", "status": "planned", "results": [{"report": "first"}], "inputs": []}}, "queue": [], "executions": {}, "waiting_actions": {}}

    def test_task_bookkeeping_and_appended_results_are_not_content_changes(self):
        basis = capture_decision_basis(self.instance, self.runtime, ["A"])
        task = self.runtime["tasks"]["A"]
        task.update(status="active", reviews=[{"decision": "approved"}], deferred_reason="later")
        task["results"].append({"report": "second"})
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        task["status"] = "completed"
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        task["results"][0]["report"] = "changed"
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime)[0]["field"], "results_sha256")

    def test_task_contract_change_and_result_removal_are_detected(self):
        basis = capture_decision_basis(self.instance, self.runtime, ["A"])
        self.runtime["tasks"]["A"].update(question="different", results=[])
        self.assertEqual({row["field"] for row in decision_basis_changes(basis, self.instance, self.runtime)}, {"contract_sha256", "results_sha256"})

    def test_split_knowledge_bookkeeping_is_stable_but_authored_reference_change_is_detected(self):
        self.instance, kid = create_candidate(self.instance, {
            "id": "K", "kind": "observation", "title": "P", "statement": "P", "explanation": "P",
            "summary": "P", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref="explicit-fixture", actor_ref="fixture-producer")
        record = self.instance['knowledge'][kid]
        basis = capture_decision_basis(self.instance, self.runtime, [kid])
        record.update(review_cycle_id="RC-new", history=[{"reason": "administrative review scheduling"}])
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        record['exposition_id'] = 'XP-replaced'
        self.assertIn('content_sha256', {row['field'] for row in decision_basis_changes(basis, self.instance, self.runtime)})

    def test_a_previous_approval_is_invalid_after_its_external_premise_changes(self):
        task = {**candidate("B"), "id": "B", "revision": 1, "question": "use A", "inputs": ["A"], "results": []}
        self.runtime["tasks"]["B"] = task
        review = planning.seal_contract_review(task, contract_review({"task": task}),
            self.instance, self.runtime, execution_id="EX-independent-review")
        self.assertTrue(planning.contract_review_current(review, task, self.instance, self.runtime)["valid"])
        self.runtime["tasks"]["A"]["deferred_reason"] = "bookkeeping"
        self.assertTrue(planning.contract_review_current(review, task, self.instance, self.runtime)["valid"])
        self.runtime["tasks"]["A"]["question"] = "new premise"
        self.assertFalse(planning.contract_review_current(review, task, self.instance, self.runtime)["valid"])

    def test_pending_revision_blocks_dependents_but_not_independent_or_delegated_work(self):
        self.runtime["tasks"]["B"] = {"id": "B", "inputs": ["A"]}
        self.runtime["tasks"]["C"] = {"id": "C", "inputs": []}
        writer = {"id": "write", "role": "research_preparation", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        self.runtime["queue"] = [writer]
        self.assertTrue(planning.revision_waits({"id": "B-work", "role": "research_work", "target": "B"}, self.instance, self.runtime))
        self.assertFalse(planning.revision_waits({"id": "C-work", "role": "research_work", "target": "C"}, self.instance, self.runtime))
        self.instance["knowledge"]["K"] = {"id": "K", "statement": "P", "status": "candidate"}
        self.runtime["tasks"]["D"] = {"id": "D", "inputs": ["K"], "knowledge_revision_targets": ["K"], "revision_request_action_id": "write-K"}
        self.runtime["queue"].append({"id": "write-K", "role": "research_preparation", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["K"])})
        self.assertFalse(planning.revision_waits({"id": "D-review", "role": "task_contract_review", "target": "D"}, self.instance, self.runtime))

    def test_unstarted_writers_reading_each_others_targets_drain_oldest_first(self):
        self.runtime["tasks"]["B"] = {"id": "B", "revision": 1, "inputs": ["A"]}
        self.runtime["tasks"]["A"]["inputs"] = ["B"]
        first = {"id": "AC-1", "role": "research_preparation", "target": "A", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        second = {"id": "AC-2", "role": "research_preparation", "target": "B", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["B"])}
        both = {"id": "AC-3", "role": "research_preparation", "target": "A", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A", "B"])}
        self.runtime["queue"] = [second, both, first]
        self.assertEqual(planning.revision_waits(first, self.instance, self.runtime), [])
        self.assertEqual([w["action_id"] for w in planning.revision_waits(second, self.instance, self.runtime)], ["AC-1"])
        self.assertEqual(sorted(w["action_id"] for w in planning.revision_waits(both, self.instance, self.runtime)), ["AC-1", "AC-2"])
        self.assertEqual(planning.revision_cycles(self.instance, self.runtime), [])
        self.assertTrue(planning.revision_waits({"id": "A-work", "role": "research_work", "target": "A"}, self.instance, self.runtime))
        self.runtime["executions"]["E"] = {"id": "E", "status": "running", "action": second}
        waits = planning.revision_waits(first, self.instance, self.runtime)
        self.assertEqual([w["action_id"] for w in waits if "action_id" in w], ["AC-2"])
        self.assertEqual([w["execution_id"] for w in waits if "execution_id" in w], ["E"])
        # The running writer waits for nothing: the two writers' mutual reads form no wait cycle.
        self.assertEqual(planning.revision_cycles(self.instance, self.runtime), [])

    def test_writer_drains_a_running_plan_but_failed_writer_does_not_block_diagnosis(self):
        writer = {"id": "write", "role": "research_preparation", "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        self.runtime["executions"]["E"] = {"id": "E", "status": "running", "action": {"id": "plan", "role": "research_plan"}}
        self.assertTrue(planning.revision_waits(writer, self.instance, self.runtime))
        self.runtime["executions"]["E"]["status"] = "ended"
        self.runtime["waiting_actions"]["write"] = {"action": writer, "kind": "execution_failure"}
        self.assertFalse(planning.revision_waits({"id": "next-plan", "role": "research_plan"}, self.instance, self.runtime))

    def test_declared_revision_requires_an_explicit_resolution(self):
        context = {"action": {"role": "research_preparation", "revision_targets": {"A": {"revision": 1, "required": True}}}, "tasks": [self.runtime["tasks"]["A"]]}
        self.assertTrue(revisions.submission_errors({"candidates": []}, {}, context))
        extension = {"revision_resolutions": [{"record_id": "A", "disposition": "unchanged", "reason": "not needed"}]}
        self.assertTrue(revisions.submission_errors({"candidates": []}, extension, context))
        extension["revision_resolutions"][0]["disposition"] = "deferred"
        self.assertEqual(revisions.submission_errors({"candidates": []}, extension, context), [])

    def test_dependency_cycles_are_reported_with_the_actual_edges(self):
        self.assertEqual(revisions.dependency_cycles({"A": {"dependencies": ["B"]}, "B": {"dependencies": ["A"]}}), [["A", "B", "A"]])

    def test_revision_response_rejects_distinct_titles_for_the_same_existing_task(self):
        context = {"action": {"role": "research_preparation", "revision_targets": {"A": {}}},
                   "tasks": [self.runtime["tasks"]["A"]]}
        extension = {"revision_resolutions": [
            {"record_id": "A", "disposition": "revised", "reason": "Replace the contract"}]}
        output = {"candidates": [{"title": "First", "revises_task_id": "A"},
                                 {"title": "Second", "revises_task_id": "A"}]}
        errors = revisions.submission_errors(output, extension, context)
        self.assertTrue(any("one replacement candidate" in row["message"] for row in errors), errors)
        output["candidates"][1]["revises_task_id"] = None
        self.assertEqual(revisions.submission_errors(output, extension, context), [])

    def test_premise_refresh_of_an_output_repair_continues_the_refreshed_execution(self):
        # EX-second, the output repair of EX-first, had its response bundle accepted before another
        # bundle returned on changed premises. The refresh continues EX-second: it inherits what
        # EX-second had accepted and none of the earlier submission issues.
        repair = {'execution_id': 'EX-first', 'previous_output': {}, 'retry_bundle_ids': ['IN-one'],
                  'bundle_results': [], 'issues': [{'issue_id': 'IS-old', 'rule_id': 'schema.required'}]}
        action = {'id': 'AC-repair', 'role': 'supplemental_research', 'continuation_of': 'EX-first',
                  'repair_attempt': 1, 'repair': repair}
        receipt = {'id': 'IN-report', 'execution_id': 'EX-second', 'response_sha256': 'a' * 64}
        owner = bare_engine({'id': 'RI-test'}, {'queue': [deepcopy(action)], 'tasks': {},
            'executions': {'EX-second': {'id': 'EX-second', 'role': 'supplemental_research', 'action': action}},
            'integrations': {receipt['id']: receipt}})
        owner._refresh_changed_decision(action, 'EX-second', [{'field': 'integration_currentness'}])
        refreshed = owner.runtime['queue'][0]
        self.assertEqual((refreshed['refresh']['execution_id'], refreshed['continuation_of']),
                         ('EX-second', 'EX-second'))
        self.assertNotIn('repair', refreshed)
        context = {}
        owner._submission_repair_context(context, refreshed)
        self.assertEqual(context['submission_failures'], [])
        self.assertEqual(context['accepted_integration_ids'], ['IN-report'])
        self.assertEqual(context['accepted_response'], {'integration_id': 'IN-report', 'response_sha256': 'a' * 64})


if __name__ == "__main__":
    unittest.main()
