"""Regression coverage for autonomous withdrawal of AI-prepared tasks."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_purpose_engine import PurposeHarness
from do_math.planning import contract_hash
from do_math.task_scope import apply_task_dispositions


class EngineIntegrationTest(PurposeHarness):
    def test_engine_applies_task_disposition_extension(self):
        """A planning extension closes the eligible task through task_scope."""
        engine, _ = self.make()
        task = {
            "id": "TK-AI", "title": "AI proposal", "revision": 1,
            "status": "planned", "producer_execution": "EX-prep",
            "completion_criteria": ["investigate"], "results": [], "reviews": [],
        }
        engine.runtime["tasks"][task["id"]] = deepcopy(task)
        engine.runtime["executions"]["EX-prep"] = {
            "id": "EX-prep", "role": "research_preparation", "status": "ended",
            "action": {"role": "research_preparation"},
        }
        engine._save()
        engine.runtime["executions"]["EX-plan"] = {
            "id": "EX-plan", "role": "research_plan", "status": "ended",
            "input_snapshot": engine.head,
            "extensions": {"task_dispositions": [{
                "task_id": task["id"], "disposition": "withdraw", "reason": "A better task subsumes it.",
            }]},
        }

        engine._apply_extensions({"role": "research_plan"}, "EX-plan")

        self.assertEqual(engine.runtime["tasks"][task["id"]]["status"], "closed")


class TaskScopeTests(unittest.TestCase):
    def fixture(self):
        task = {"id": "TK-AI", "title": "AI proposal", "revision": 3, "status": "planned",
                "producer_execution": "EX-prep", "completion_criteria": ["investigate"],
                "results": [], "reviews": [{"decision": "approved"}], "dependencies": []}
        runtime = {"tasks": {task["id"]: deepcopy(task), "TK-dependent": {
            "id": "TK-dependent", "status": "waiting", "dependencies": [task["id"]]}},
            "executions": {"EX-prep": {"id": "EX-prep", "role": "research_preparation", "status": "ended",
                                           "action": {"role": "research_preparation"}}},
            "queue": [{"id": "AC-review", "role": "task_contract_review", "target": task["id"]},
                      {"id": "AC-other", "role": "research_plan"}],
            "waiting_actions": {"AC-work": {"action": {"id": "AC-work", "role": "research_work", "target": task["id"]}}},
            "task_readiness": {task["id"]: {"state": "ready"}}}
        return {}, runtime, {task["id"]: deepcopy(task)}

    def withdraw(self, runtime, snapshot):
        return apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "withdraw",
            "reason": "The prepared task is superseded by a narrower current direction."}],
            execution_id="EX-plan", input_tasks=snapshot)

    def test_withdrawal_preserves_contract_and_cancels_only_prestart_actions(self):
        instance, runtime, snapshot = self.fixture()
        _, changed = self.withdraw(runtime, snapshot)
        task = changed["tasks"]["TK-AI"]
        self.assertEqual(task["status"], "closed")
        self.assertEqual(task["completion_criteria"], ["investigate"])
        self.assertEqual(task["reviews"], [{"decision": "approved"}])
        self.assertNotIn("assessment", task)
        record = task["scope_disposition"]
        self.assertEqual(record["actor_execution"], "EX-plan")
        self.assertEqual(record["previous_revision"], 3)
        self.assertEqual(record["previous_contract_sha256"], contract_hash(snapshot["TK-AI"]))
        self.assertTrue(record["cancelled_queue_actions"])
        self.assertTrue(record["cancelled_waiting_actions"])
        self.assertNotIn("TK-AI", changed["task_readiness"])
        self.assertEqual(changed["tasks"]["TK-dependent"]["status"], "waiting")
        self.assertEqual(runtime["tasks"]["TK-AI"]["status"], "planned")

    def test_rejects_changed_snapshot_user_or_academic_task_and_live_or_terminal_task(self):
        for mutation in (
            lambda runtime, snap: snap["TK-AI"].update(question="new"),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(producer_execution="EX-user"),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(academic_requirement_id="writeup"),
            lambda runtime, snap: runtime["executions"].update(EX={"id": "EX", "role": "research_work", "status": "running", "action": {"target": "TK-AI"}}),
            lambda runtime, snap: runtime["tasks"]["TK-AI"].update(status="completed"),
        ):
            with self.subTest(mutation=mutation):
                instance, runtime, snapshot = self.fixture()
                mutation(runtime, snapshot)
                with self.assertRaises(ValueError):
                    self.withdraw(runtime, snapshot)

    def test_rejects_nonwithdraw_and_duplicate_requests_atomically(self):
        _, runtime, snapshot = self.fixture()
        with self.assertRaises(ValueError):
            apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "revise", "reason": "x"}],
                execution_id="EX-plan", input_tasks=snapshot)
        with self.assertRaises(ValueError):
            apply_task_dispositions({}, runtime, [{"task_id": "TK-AI", "disposition": "withdraw", "reason": "x"},
                {"task_id": "TK-AI", "disposition": "withdraw", "reason": "x"}], execution_id="EX-plan", input_tasks=snapshot)
        self.assertEqual(runtime["tasks"]["TK-AI"]["status"], "planned")

    def test_withdrawal_keeps_ended_partial_work_and_results(self):
        _, runtime, snapshot = self.fixture()
        runtime["tasks"]["TK-AI"].update(status="needs_revision", results=[{"id": "R-partial", "outcome": "partial"}])
        runtime["executions"]["EX-work"] = {"id": "EX-work", "role": "research_work", "status": "ended",
            "action": {"target": "TK-AI"}, "outcome": "output_accepted"}
        snapshot["TK-AI"].update(status="needs_revision")

        _, changed = self.withdraw(runtime, snapshot)

        task = changed["tasks"]["TK-AI"]
        self.assertEqual(task["status"], "closed")
        self.assertEqual(task["results"], [{"id": "R-partial", "outcome": "partial"}])
        self.assertEqual(changed["executions"]["EX-work"]["outcome"], "output_accepted")


class SourceCorrectionRegressionTest(PurposeHarness):
    def test_same_source_bytes_can_revise_a_misread_claim_and_suspend_dependents(self):
        """A corrected reading changes knowledge, not the immutable source bytes."""
        engine, _ = self.make()
        engine.instance["sources"] = [{"id": "SO-paper", "name": "paper.pdf", "path": "source.pdf",
                                       "sha256": "a" * 64, "status": "active"}]
        engine.instance["knowledge"] = {
            "KN-reading": {"id": "KN-reading", "revision": 1, "status": "verified", "statement": "The paper prints m/n.",
                           "explanation": "Earlier reading.", "summary": "Misread fraction.", "lean_code": "",
                           "declaration_names": [], "dependencies": [], "reviews": [],
                           "source_basis": [{"name": "paper.pdf", "path": "source.pdf", "sha256": "a" * 64}]},
            "KN-dependent": {"id": "KN-dependent", "revision": 1, "status": "verified", "statement": "Derived claim.",
                             "explanation": "Depends on the reading.", "summary": "Dependent.", "lean_code": "",
                             "declaration_names": [], "dependencies": ["KN-reading"], "reviews": []},
        }
        engine.runtime["executions"]["EX-correction"] = {"id": "EX-correction", "role": "research_preparation",
            "status": "ended", "extensions": {"knowledge_changes": [{"id": "KN-reading", "reason": "PDF layout audit reads n/m.",
                "changes": {"statement": "The paper prints n/m.", "explanation": "The original PDF is unchanged; the prior transcription was reversed."}}]}}

        engine._apply_extensions({"role": "research_preparation"}, "EX-correction")

        self.assertEqual(engine.instance["sources"][0]["sha256"], "a" * 64)
        self.assertEqual(engine.instance["knowledge"]["KN-reading"]["status"], "candidate")
        self.assertEqual(engine.instance["knowledge"]["KN-reading"]["history"][-1]["previous"]["statement"], "The paper prints m/n.")
        self.assertTrue(engine.instance["knowledge"]["KN-dependent"]["use_suspended"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
