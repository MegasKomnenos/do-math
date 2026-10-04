"""Decision basis currentness and revision waits (``input_basis``, ``planning``, ``revisions``), moved from ``test_decision_basis``.

An AI judgment seals the state of the records it relied on and checks before
its application that the basis is still current: task bookkeeping and appended
results are not content changes, a contract change or a result edit is. The
revision rules decide which work waits for a declared revision and what a
revision response must resolve. Every test calls the product functions on the
legacy dictionary state; nothing is replaced.
"""
import unittest
from copy import deepcopy

from do_math import planning, revisions
from do_math.input_basis import capture_decision_basis, decision_basis_changes
from do_math.knowledge_records import create_candidate
from support.state_builders import approved_governance, charter_record
from support.role_answers import candidate, contract_review


class BasisCase(unittest.TestCase):
    """The legacy ``setUp``: an approved charter and task ``A`` with one result."""

    def setUp(self):
        # Explicit synthetic approval is an input to this domain-level test.
        # No engine lifecycle or activation evidence is injected.
        text = "Preserve approved task premises"
        self.instance = approved_governance({"knowledge": {}, "sources": []}, [charter_record(text)],
                                            source=("UI-basis-fixture", text), approval_id="DC-basis-fixture")
        self.runtime = {"tasks": {"A": {**candidate("A"), "id": "A", "revision": 1, "question": "original",
                                        "status": "planned", "results": [{"report": "first"}], "inputs": []}},
                        "queue": [], "executions": {}, "waiting_actions": {}}


class BasisTests(BasisCase):
    def test_every_declared_task_contract_field_is_a_sensitive_citation_premise(self):
        """5-A: JSON projection sensitivity, before higher-level shape/admission checks."""
        original = deepcopy(self.runtime['tasks']['A'])
        basis = capture_decision_basis(self.instance, self.runtime, ['A'])
        for field in planning.CONTRACT_FIELDS:
            changed = deepcopy(original)
            value = changed.get(field)
            if isinstance(value, str): changed[field] = value + ' changed'
            elif type(value) is int: changed[field] = value + 1
            elif isinstance(value, list): changed[field] = [*value, 'changed-member']
            elif isinstance(value, dict): changed[field] = {**value, 'changed_content': True}
            else: changed[field] = 'new-' + field
            self.runtime['tasks']['A'] = changed
            with self.subTest(contract_field=field):
                differences = decision_basis_changes(basis, self.instance, self.runtime)
                self.assertIn('contract_sha256', {row['field'] for row in differences})
        self.runtime['tasks']['A'] = original
        for field, value in (('status', 'active'), ('reviews', [{'decision': 'approved'}]),
                             ('selection', {'execution_id': 'EX-new'}), ('history', [{'kind': 'management'}]),
                             ('review_cycle_id', 'RC-added'), ('receipt', {'state': 'accepted'})):
            self.runtime['tasks']['A'] = {**deepcopy(original), field: value}
            with self.subTest(management_field=field):
                self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        self.runtime['tasks']['A'] = original

    def test_result_prefix_membership_is_stable_for_append_but_sensitive_to_replacement_and_removal(self):
        basis = capture_decision_basis(self.instance, self.runtime, ['A'])
        original = deepcopy(self.runtime['tasks']['A']['results'])
        self.runtime['tasks']['A']['results'].append({'report': 'later result'})
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        for values in ([], [{'report': 'replacement'}], [{'report': 'prefix replaced'}, {'report': 'later result'}]):
            self.runtime['tasks']['A']['results'] = values
            with self.subTest(results=values):
                self.assertEqual([row['field'] for row in decision_basis_changes(basis, self.instance, self.runtime)],
                                 ['results_sha256'])
        self.runtime['tasks']['A']['results'] = original

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
        self.assertEqual({row["field"] for row in decision_basis_changes(basis, self.instance, self.runtime)},
                         {"contract_sha256", "results_sha256"})

    def test_split_knowledge_bookkeeping_is_stable_but_authored_reference_change_is_detected(self):
        from support.entry import entry
        _entry = entry()
        self.instance, kid = create_candidate(self.instance, {
            "id": "K", "kind": "observation", "title": "P", "statement": "P", "explanation": "P",
            "summary": "P", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref="explicit-fixture", actor_ref="fixture-producer", clock=_entry.ports.clock)
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


class RevisionWaitTests(BasisCase):
    def test_pending_revision_blocks_dependents_but_not_independent_or_delegated_work(self):
        self.runtime["tasks"]["B"] = {"id": "B", "inputs": ["A"]}
        self.runtime["tasks"]["C"] = {"id": "C", "inputs": []}
        writer = {"id": "write", "role": "research_preparation",
                  "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        self.runtime["queue"] = [writer]
        self.assertTrue(planning.revision_waits({"id": "B-work", "role": "research_work", "target": "B"},
                                                self.instance, self.runtime))
        self.assertFalse(planning.revision_waits({"id": "C-work", "role": "research_work", "target": "C"},
                                                 self.instance, self.runtime))
        self.instance["knowledge"]["K"] = {"id": "K", "statement": "P", "status": "candidate"}
        self.runtime["tasks"]["D"] = {"id": "D", "inputs": ["K"], "knowledge_revision_targets": ["K"],
                                      "revision_request_action_id": "write-K"}
        self.runtime["queue"].append({"id": "write-K", "role": "research_preparation",
                                      "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["K"])})
        self.assertFalse(planning.revision_waits({"id": "D-review", "role": "task_contract_review", "target": "D"},
                                                 self.instance, self.runtime))

    def test_unstarted_writers_reading_each_others_targets_drain_oldest_first(self):
        self.runtime["tasks"]["B"] = {"id": "B", "revision": 1, "inputs": ["A"]}
        self.runtime["tasks"]["A"]["inputs"] = ["B"]
        first = {"id": "AC-1", "role": "research_preparation", "target": "A",
                 "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        second = {"id": "AC-2", "role": "research_preparation", "target": "B",
                  "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["B"])}
        both = {"id": "AC-3", "role": "research_preparation", "target": "A",
                "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A", "B"])}
        self.runtime["queue"] = [second, both, first]
        self.assertEqual(planning.revision_waits(first, self.instance, self.runtime), [])
        self.assertEqual([w["action_id"] for w in planning.revision_waits(second, self.instance, self.runtime)], ["AC-1"])
        self.assertEqual(sorted(w["action_id"] for w in planning.revision_waits(both, self.instance, self.runtime)),
                         ["AC-1", "AC-2"])
        self.assertEqual(planning.revision_cycles(self.instance, self.runtime), [])
        self.assertTrue(planning.revision_waits({"id": "A-work", "role": "research_work", "target": "A"},
                                                self.instance, self.runtime))
        self.runtime["executions"]["E"] = {"id": "E", "status": "running", "action": second}
        waits = planning.revision_waits(first, self.instance, self.runtime)
        self.assertEqual([w["action_id"] for w in waits if "action_id" in w], ["AC-2"])
        self.assertEqual([w["execution_id"] for w in waits if "execution_id" in w], ["E"])
        # The running writer waits for nothing: the two writers' mutual reads form no wait cycle.
        self.assertEqual(planning.revision_cycles(self.instance, self.runtime), [])

    def test_writer_drains_a_running_plan_but_failed_writer_does_not_block_diagnosis(self):
        writer = {"id": "write", "role": "research_preparation",
                  "revision_targets": revisions.capture_targets(self.instance, self.runtime, ["A"])}
        self.runtime["executions"]["E"] = {"id": "E", "status": "running", "action": {"id": "plan", "role": "research_plan"}}
        self.assertTrue(planning.revision_waits(writer, self.instance, self.runtime))
        self.runtime["executions"]["E"]["status"] = "ended"
        self.runtime["waiting_actions"]["write"] = {"action": writer, "kind": "execution_failure"}
        self.assertFalse(planning.revision_waits({"id": "next-plan", "role": "research_plan"}, self.instance, self.runtime))


class RevisionResponseTests(BasisCase):
    def test_declared_revision_requires_an_explicit_resolution(self):
        context = {"action": {"role": "research_preparation", "revision_targets": {"A": {"revision": 1, "required": True}}},
                   "tasks": [self.runtime["tasks"]["A"]]}
        self.assertEqual(revisions.submission_errors({"candidates": []}, {}, context), [
            {'path': 'activity-extensions.json/revision_resolutions',
             'message': 'resolve each declared target exactly once, using a task withdrawal only for task targets'}])
        extension = {"revision_resolutions": [{"record_id": "A", "disposition": "unchanged", "reason": "not needed"}]}
        self.assertEqual(revisions.submission_errors({"candidates": []}, extension, context), [
            {'path': 'activity-extensions.json/revision_resolutions',
             'message': 'a required revision or rejected contract cannot be cancelled as unchanged'}])
        extension["revision_resolutions"][0]["disposition"] = "deferred"
        self.assertEqual(revisions.submission_errors({"candidates": []}, extension, context), [])

    def test_dependency_cycles_are_reported_with_the_actual_edges(self):
        self.assertEqual(revisions.dependency_cycles({"A": {"dependencies": ["B"]}, "B": {"dependencies": ["A"]}}),
                         [["A", "B", "A"]])

    def test_revision_response_rejects_distinct_titles_for_the_same_existing_task(self):
        context = {"action": {"role": "research_preparation", "revision_targets": {"A": {}}},
                   "tasks": [self.runtime["tasks"]["A"]]}
        extension = {"revision_resolutions": [
            {"record_id": "A", "disposition": "revised", "reason": "Replace the contract"}]}
        output = {"candidates": [{"title": "First", "revises_task_id": "A"},
                                 {"title": "Second", "revises_task_id": "A"}]}
        errors = revisions.submission_errors(output, extension, context)
        self.assertEqual(errors, [{'path': 'activity-extensions.json/revision_targets',
                                   'message': 'each existing task may have only one replacement candidate per response'}])
        output["candidates"][1]["revises_task_id"] = None
        self.assertEqual(revisions.submission_errors(output, extension, context), [])


if __name__ == "__main__":
    unittest.main()
