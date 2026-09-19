from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.input_basis import capture_decision_basis, decision_basis_changes
from do_math import planning, revisions


class BasisTests(unittest.TestCase):
    def setUp(self):
        self.instance = {"goal_revision": 1, "policy_revision": 1, "knowledge": {}, "sources": []}
        self.runtime = {"tasks": {"A": {"id": "A", "revision": 1, "question": "original", "status": "ready", "results": [{"report": "first"}], "inputs": []}}, "queue": [], "executions": {}, "waiting_actions": {}}

    def test_task_bookkeeping_and_appended_results_are_not_content_changes(self):
        basis = capture_decision_basis(self.instance, self.runtime, ["A"])
        task = self.runtime["tasks"]["A"]
        task.update(status="performing", reviews=[{"decision": "approved"}], deferred_reason="later")
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

    def test_verified_upgrade_keeps_identical_content_but_not_unknown_author_fields(self):
        record = {"id": "K", "revision": 1, "status": "reviewing", "statement": "P", "dependencies": [], "reviews": []}
        self.instance["knowledge"]["K"] = record
        basis = capture_decision_basis(self.instance, self.runtime, ["K"])
        record.update(status="verified", reviews=[{"match": True}], verified_at="now", identity_assessment={"effective": True})
        self.assertEqual(decision_basis_changes(basis, self.instance, self.runtime), [])
        record["new_authored_condition"] = "H"
        self.assertIn("content_sha256", {row["field"] for row in decision_basis_changes(basis, self.instance, self.runtime)})
        record.pop("new_authored_condition")
        record["use_suspended"] = True
        self.assertIn("use_suspended", {row["field"] for row in decision_basis_changes(basis, self.instance, self.runtime)})

    def test_a_previous_approval_is_invalid_after_its_external_premise_changes(self):
        task = {"id": "B", "revision": 1, "question": "use A", "inputs": ["A"], "results": []}
        self.runtime["tasks"]["B"] = task
        review = {"revision": 1, "contract_sha256": planning.contract_hash(task), "goal_revision": 1, "policy_revision": 1,
                  "decision_basis": capture_decision_basis(self.instance, self.runtime, ["A", "B"])}
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


if __name__ == "__main__":
    unittest.main()
