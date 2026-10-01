"""What the installed producer check rejects and passes (``submission_tool.main`` in check mode, layer 3).

The legacy tests ran the installed command in a child interpreter for every
check. The launcher only puts the shipped archive on the path and calls
``submission_tool.main``, so these tests call ``main`` in this process with the
workspace as the working directory (``support.submission_protocol.check_output``);
the launcher's own process and its engine-free archive are boundary tests
(``boundary.test_submission_mcp_server.InstalledToolTests``).
"""
import json
import tempfile
import unittest

from support.purpose_answers import common
from support.role_answers import candidate, disposition
from support.submission_protocol import check_output, producer_workspace


class ProducerToolTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = temporary.name

    def prepare(self, role='research_preparation', **options):
        return producer_workspace(self.root, role, **options)

    def test_producer_checks_main_shape_and_preserves_precise_failure_coordinates(self):
        """The name says precise coordinates; like the legacy test, this checks the missing field's name in the issues."""
        workspace, context = self.prepare()
        valid = {**common("A bounded preparation."), "candidates": []}
        self.assertTrue(check_output(self, workspace, context, valid)["passed"])
        invalid = {key: value for key, value in valid.items() if key != "candidates"}
        result = check_output(self, workspace, context, invalid)
        self.assertFalse(result["passed"])
        self.assertIn("candidates", json.dumps(result["issues"]))
        self.assertEqual([(row["rule_id"], row["path"]) for row in result["issues"]],
                         [("schema.required", "output/candidates")])

    def test_producer_checks_used_sources(self):
        workspace, context = self.prepare()
        output = {**common("A bounded preparation."), "candidates": [], "used_sources": ["KN-missing"]}
        result = check_output(self, workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertEqual([(row["rule_id"], row["path"]) for row in result["issues"]],
                         [("submission.output.used_sources.*", "output/used_sources/0")])
        self.assertTrue(result["issues"][0]["message"].startswith(
            "reference must identify supplied input, a record of the input snapshot or a preserved workspace file: KN-missing"))

    def test_reference_support_includes_visible_execution_history_and_supplied_catalogs(self):
        from do_math.context_store import fit_context
        previous = "EX-earlier"
        workspace, context = self.prepare(context_values={
            "preparation_history": [{"execution_id": previous, "report": "Earlier preparation result"}],
            "goal": "g", "large_optional_evidence": {"text": "x" * 30000}})
        fitted = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
        catalog = next(row["path"] for row in fitted["manifest"] if row["key"] == "kind_definitions")
        for reference in (previous, catalog):
            with self.subTest(reference=reference):
                output = {**common("Read the supplied evidence."), "candidates": [], "used_sources": [reference]}
                self.assertTrue(check_output(self, workspace, context, output)["passed"])

    def test_producer_checks_checkpoint_evidence_paths(self):
        from do_math.canonical import canonical_json
        workspace, context = self.prepare()
        output = {**common("A bounded preparation."), "candidates": []}
        (workspace / "checkpoint.json").write_bytes(canonical_json({
            "current_claim": "A bounded result", "evidence_paths": ["missing-proof.txt"],
            "attempts": [], "remaining_work": [], "next_step": "submit", "progress_state": "ready_to_submit"}))
        result = check_output(self, workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("missing-proof.txt", json.dumps(result["issues"]))

    def test_producer_checks_sidecar_kinds_references_and_self_repair(self):
        workspace, context = self.prepare()
        output = {**common("A bounded preparation."), "candidates": []}
        insight = {"kind": "unregistered_kind", "title": "Question", "statement": "What remains?",
                   "summary": "An open question.", "evidence_ids": ["KN-missing"]}
        result = check_output(self, workspace, context, output, {"research_insights": [insight]})
        self.assertFalse(result["passed"])
        self.assertIn("research_insights", json.dumps(result["issues"]))
        insight.update(kind="question", evidence_ids=[])
        self.assertTrue(check_output(self, workspace, context, output, {"research_insights": [insight]})["passed"])

    def test_empty_known_extension_family_remains_a_semantic_noop(self):
        workspace, context = self.prepare("maintenance")
        output = {**common("No changes requested."), "report": "Observed only.", "remaining_work": []}
        self.assertTrue(check_output(self, workspace, context, output, {"knowledge_changes": []})["passed"])

    def test_producer_receives_artifact_and_checkpoint_limits_and_excludes_disposable_scratch(self):
        from do_math.observations import CHECKPOINT_MAX_BYTES
        workspace, context = self.prepare(max_artifact_bytes=100)
        limits = context["submission_contract"]["limits"]
        self.assertEqual(limits["max_artifact_bytes"], 100)
        self.assertEqual(limits["checkpoint_bytes"], 4 * 1024 * 1024)
        self.assertEqual(limits["checkpoint_bytes"], CHECKPOINT_MAX_BYTES)
        self.assertNotIn("observation_rules_bytes", limits)
        output = {**common("No proposal."), "candidates": []}
        (workspace / ".scratch").mkdir()
        (workspace / ".scratch/disposable.bin").write_bytes(b"x" * 101)
        self.assertTrue(check_output(self, workspace, context, output)["passed"])
        (workspace / "evidence.bin").write_bytes(b"x" * 101)
        result = check_output(self, workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("evidence.bin", json.dumps(result["issues"]))

    def test_producer_checks_live_checkpoint_but_not_a_rules_file(self):
        workspace, context = self.prepare()
        output = {**common("No proposal."), "candidates": []}
        (workspace / "checkpoint.json").write_text('{"current_claim":"unfinished schema"}', encoding="utf-8")
        # Rules change only through a self-check response; a leftover rules file is ordinary output.
        (workspace / "observation-rules.json").write_text('[{"id":"bad","op":"counter_gte","threshold":true}]',
                                                          encoding="utf-8")
        result = check_output(self, workspace, context, output)
        self.assertFalse(result["passed"])
        issues = json.dumps(result["issues"])
        self.assertIn("checkpoint.json", issues)
        self.assertNotIn("observation-rules.json", issues)

    def test_producer_checks_planning_population_and_exact_completion_criteria(self):
        tid = "TK-ready"
        # A stored task record has no revises_task_id (the task schema rejects it); the legacy record carried the
        # candidate's field, and the last check below was rejected for that field instead of its completion criteria.
        task = {**{k: v for k, v in candidate().items() if k != "revises_task_id"},
                "id": tid, "revision": 1, "status": "planned", "results": []}
        workspace, context = self.prepare("research_plan", context_values={"tasks": [task], "ready_task_ids": [tid]})
        self.assertIn("submission_contract", context)
        output = {**common("Current population."), "dispositions": [],
                  "preparation_requests": [], "goal_audit": False, "task_assessments": []}
        result = check_output(self, workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("every derived-ready task", json.dumps(result["issues"]))
        output["dispositions"] = [{**disposition(tid), "uncertainty": ""}]
        extension = {"model_assessments": [{"task_id": tid, "difficulty": "low", "importance": "low", "reason": "Bounded task"}]}
        self.assertTrue(check_output(self, workspace, context, output, extension)["passed"])
        task.update(status="waiting", results=[{"execution_id": "EX-work", "report": "Partial argument"}])
        workspace, context = self.prepare("research_plan", context_values={"tasks": [task], "ready_task_ids": []})
        output["dispositions"] = []
        output["task_assessments"] = [{"task_id": tid, "decision": "completed", "reason": "Claimed complete",
                                       "item_dispositions": [], "unresolved": []}]
        result = check_output(self, workspace, context, output, {})
        self.assertFalse(result["passed"])
        self.assertEqual([(row["rule_id"], row["message"]) for row in result["issues"]],
                         [("submission.output", "every obligation requires a disposition or unresolved inspection")])


if __name__ == "__main__":
    unittest.main()
