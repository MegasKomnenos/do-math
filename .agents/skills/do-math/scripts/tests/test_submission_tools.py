"""Exercise the actual producer command in its supplied, standalone workspace."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_purpose_engine as purpose
from do_math.repository import canonical_json


class ProducerToolTests(purpose.PurposeHarness):
    def test_revoked_original_grant_preserves_late_output_despite_alternative_grant(self):
        from do_math import governance
        engine, _ = self.make(scholarly_enabled=False)
        engine.runtime["queue"] = [{"id": "AC-revoked", "role": "maintenance"}]
        grant = next(value for value in engine.instance["grants"].values() if "maintenance" in value.get("roles", []))
        alternative = {**deepcopy(grant), "id": "ZZ-alternative"}
        engine.instance["grants"][alternative["id"]] = alternative
        engine._save()
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                execution = next(value for value in engine.runtime["executions"].values() if value["status"] == "running")
                engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
                    {"kind": "revoke", "grant_id": execution["grant_id"]}, source_ref="UC-revoke")
                engine._save()
                self.assertTrue(governance.authorize(engine.instance, execution["action"])["allowed"])
                args["should_stop"]()
                return {"status": "completed", "output": {**purpose.common("Completed before revocation."),
                    "report": "Preserve the completed portion.", "remaining_work": []}, "usage": {}}
        engine.runner = Runner()
        engine.run(max_steps=1)
        execution = next(iter(engine.runtime["executions"].values()))
        self.assertEqual(execution["outcome"], "execution_incomplete")
        self.assertIn("grant_revoked", execution["error"])
        self.assertIn("AC-revoked", engine.runtime["waiting_actions"])

    def test_parsed_invalid_runner_output_uses_the_bounded_output_repair_path(self):
        engine, _ = self.make(scholarly_enabled=False)
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": {}, "usage": {}, "error_kind": "output_validation",
                        "error": "output/candidates: required property is missing"}
        engine.runner = Runner()
        engine.run(max_steps=1)
        self.assertTrue(any(a.get("repair") for a in engine.runtime["queue"]))
        self.assertFalse(any(a["role"] == "operational_review" for a in engine.runtime["queue"]))

    def test_local_call_timeout_parks_only_the_timed_out_request(self):
        import time
        engine, _ = self.make(scholarly_enabled=False, call_timeout_seconds=1)
        engine.runtime["queue"] = [{"id": "AC-timeout", "role": "maintenance"},
                                   {"id": "AC-independent", "role": "research_preparation"}]
        engine._save()
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                time.sleep(1.05)
                self.assertTrue(args["should_stop"]())
                return {"status": "stopped", "output": None, "usage": {}, "error": "local call deadline"}
        engine.runner = Runner()
        engine.run(max_steps=1)
        self.assertNotEqual(engine.runtime["status"], "paused")
        self.assertIn("AC-timeout", engine.runtime["waiting_actions"])
        self.assertTrue(any(a.get("id") == "AC-independent" for a in engine.runtime["queue"]))

    def test_receiver_rejects_unknown_insight_kind_and_missing_evidence(self):
        for changes in ({"kind": "unregistered_kind"}, {"evidence_ids": ["KN-missing"]}):
            with self.subTest(changes=changes):
                engine, _ = self.make(scholarly_enabled=False, max_output_repairs=0)
                output = {**purpose.common("Preserve a candidate."), "candidates": []}
                insight = {"kind": "question", "title": "Question", "statement": "What remains?",
                           "summary": "An open question.", "evidence_ids": [], **changes}
                class Runner:
                    def run(inner, **args):
                        args["on_started"]({"pid": 1})
                        (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({"research_insights": [insight]}))
                        return {"status": "completed", "output": output, "usage": {}}
                engine.runner = Runner()
                engine.run(max_steps=1)
                execution = next(iter(engine.runtime["executions"].values()))
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertEqual(engine.instance["knowledge"], {})
                saved = engine.store.read(f"runtime/artifacts/{execution['artifact_bundle']}/output.json")
                self.assertEqual(json.loads(saved), output)

    def prepare(self, role="research_preparation", **configuration):
        engine, _ = self.make(scholarly_enabled=False, **configuration)
        workspace = self.root / (role + "-producer")
        context = engine._context({"role": role}, workspace)
        self.assertIn("submission_contract", context,
                      "the producer needs an executable check, fixed inputs and limits")
        self.assertTrue(context["submission_contract"]["command"])
        return engine, workspace, context

    def check_output(self, workspace, context, output, extension=None):
        draft = workspace / ".scratch/submission.json"
        draft.parent.mkdir(exist_ok=True)
        draft.write_bytes(canonical_json(output))
        if extension is not None:
            (workspace / "activity-extensions.json").write_bytes(canonical_json(extension))
        command = [*context["submission_contract"]["command"], "--output", str(draft)]
        process = subprocess.run(command, cwd=workspace, capture_output=True, timeout=30)
        self.assertIn(process.returncode, (0, 1), process.stderr.decode("utf-8", "replace"))
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode == 0, result["passed"])
        self.assertEqual(json.loads(draft.read_bytes()), output, "a validator cannot rewrite the author's meaning")
        return result

    def test_producer_checks_main_shape_and_preserves_precise_failure_coordinates(self):
        _, workspace, context = self.prepare()
        valid = {**purpose.common("A bounded preparation."), "candidates": []}
        self.assertTrue(self.check_output(workspace, context, valid)["passed"])
        invalid = {key: value for key, value in valid.items() if key != "candidates"}
        result = self.check_output(workspace, context, invalid)
        self.assertFalse(result["passed"])
        self.assertIn("candidates", json.dumps(result["issues"]))

    def test_producer_checks_used_sources(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": [], "used_sources": ["KN-missing"]}
        self.assertFalse(self.check_output(workspace, context, output)["passed"])

    def test_reference_support_includes_visible_execution_history_and_supplied_catalogs(self):
        from do_math.context_store import fit_context
        engine, _ = self.make(scholarly_enabled=False)
        engine.run(max_steps=1)
        workspace = self.root / "history-reference-producer"
        context = engine._context({"role": "research_preparation"}, workspace)
        previous = context["preparation_history"][0]["execution_id"]
        fitted = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
        catalog = next(row["path"] for row in fitted["manifest"] if row["key"] == "kind_definitions")
        for reference in (previous, catalog):
            with self.subTest(reference=reference):
                output = {**purpose.common("Read the supplied evidence."), "candidates": [], "used_sources": [reference]}
                self.assertTrue(self.check_output(workspace, context, output)["passed"])
    def test_producer_checks_checkpoint_evidence_paths(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": []}
        (workspace / "checkpoint.json").write_bytes(canonical_json({
            "current_claim": "A bounded result", "evidence_paths": ["missing-proof.txt"],
            "attempts": [], "remaining_work": [], "next_step": "submit", "progress_state": "ready_to_submit"}))
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("missing-proof.txt", json.dumps(result["issues"]))

    def test_legacy_live_review_validates_sidecar_before_applying_continue(self):
        engine, runner = self.make(observation="continue", scholarly_enabled=False)
        original = runner.answer
        def answer(role, context, workspace):
            if role == "operational_review":
                (workspace / "activity-extensions.json").write_bytes(canonical_json({"research_insights": [{
                    "kind": "not_registered", "title": "Bad insight", "statement": "x", "summary": "x"}]}))
            return original(role, context, workspace)
        runner.answer = answer
        self.drive(engine, predicate=lambda e: any(x["role"] == "operational_review" and x["status"] == "ended" for x in e.runtime["executions"].values()))
        reviewed = next(x for x in engine.runtime["executions"].values() if x["role"] == "operational_review")
        self.assertEqual(reviewed["outcome"], "execution_incomplete")
        self.assertNotIn("operational_decision", engine.runtime["observations"][reviewed["parent_execution_id"]])

    def test_producer_checks_sidecar_kinds_references_and_self_repair(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("A bounded preparation."), "candidates": []}
        insight = {"kind": "unregistered_kind", "title": "Question", "statement": "What remains?",
                   "summary": "An open question.", "evidence_ids": ["KN-missing"]}
        result = self.check_output(workspace, context, output, {"research_insights": [insight]})
        self.assertFalse(result["passed"])
        self.assertIn("research_insights", json.dumps(result["issues"]))
        insight.update(kind="question", evidence_ids=[])
        self.assertTrue(self.check_output(workspace, context, output, {"research_insights": [insight]})["passed"])

    def test_empty_known_extension_family_remains_a_semantic_noop(self):
        _, workspace, context = self.prepare("maintenance")
        output = {**purpose.common("No changes requested."), "report": "Observed only.", "remaining_work": []}
        self.assertTrue(self.check_output(workspace, context, output, {"knowledge_changes": []})["passed"])

    def test_producer_receives_artifact_and_checkpoint_limits_and_excludes_disposable_scratch(self):
        _, workspace, context = self.prepare(max_artifact_bytes=100)
        limits = context["submission_contract"]["limits"]
        self.assertEqual(limits["max_artifact_bytes"], 100)
        self.assertEqual(limits["checkpoint_bytes"], 4 * 1024 * 1024)
        self.assertEqual(limits["observation_rules_bytes"], 65536)
        output = {**purpose.common("No proposal."), "candidates": []}
        (workspace / ".scratch").mkdir()
        (workspace / ".scratch/disposable.bin").write_bytes(b"x" * 101)
        self.assertTrue(self.check_output(workspace, context, output)["passed"])
        (workspace / "evidence.bin").write_bytes(b"x" * 101)
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn("evidence.bin", json.dumps(result["issues"]))

    def test_producer_checks_live_checkpoint_and_observation_files(self):
        _, workspace, context = self.prepare()
        output = {**purpose.common("No proposal."), "candidates": []}
        (workspace / "checkpoint.json").write_text('{"current_claim":"unfinished schema"}', encoding="utf-8")
        (workspace / "observation-rules.json").write_text('[{"id":"bad","op":"counter_gte","threshold":true}]', encoding="utf-8")
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        issues = json.dumps(result["issues"])
        self.assertIn("checkpoint.json", issues)
        self.assertIn("observation-rules.json", issues)

    def test_producer_checks_planning_population_and_exact_completion_criteria(self):
        engine, _ = self.make(scholarly_enabled=False)
        engine.run(max_steps=2)
        workspace = self.root / "plan-producer"
        context = engine._context({"role": "research_plan"}, workspace)
        self.assertIn("submission_contract", context)
        tid = next(iter(engine.runtime["tasks"]))
        output = {**purpose.common("Current population."), "selections": [], "deferred": [],
                  "preparation_requests": [], "goal_audit": False, "task_assessments": []}
        result = self.check_output(workspace, context, output)
        self.assertFalse(result["passed"])
        self.assertIn(tid, json.dumps(result["issues"]))
        output["selections"] = [tid]
        self.assertTrue(self.check_output(workspace, context, output)["passed"])

    def test_supplied_checker_is_standalone_and_does_not_mutate_fixed_inputs(self):
        _, workspace, context = self.prepare()
        before = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (workspace / "input").rglob("*") if p.is_file()}
        self.assertTrue(self.check_output(workspace, context,
            {**purpose.common("No proposal."), "candidates": []})["passed"])
        after = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in (workspace / "input").rglob("*") if p.is_file()}
        self.assertEqual(after, before)
        for part in context["submission_contract"]["command"][1:]:
            if part.endswith(".py"):
                self.assertTrue((workspace / part).resolve().is_relative_to(workspace.resolve()))


class OperatorProducerTests(unittest.TestCase):
    def test_independent_operator_receives_a_working_submission_check(self):
        import tempfile
        from unittest.mock import patch
        from do_math import scheduled_operator as operator
        observed = []
        class Runner:
            def run(inner, **args):
                context_path = args["workspace"] / "input/submission/context.json"
                self.assertTrue(context_path.is_file(), "independent operator has no supplied producer check")
                context = json.loads(context_path.read_bytes())
                output = {"summary": "Observed current status.", "observed_status": "ready", "actions": [],
                          "evidence_paths": [], "user_questions": [], "next_step": "Return the recorded observation."}
                draft = args["workspace"] / "submission.json"
                draft.write_bytes(canonical_json(output))
                result = subprocess.run([*context["submission_contract"]["command"], "--output", str(draft)],
                                        cwd=args["workspace"], capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout.decode("utf-8", "replace"))
                observed.append(json.loads(result.stdout))
                return {"status": "completed", "output": output, "usage": {}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(operator, "read_status", return_value={"status": "ready", "snapshot": "fixed", "user_pause": None}), \
                 patch.object(operator, "ResearchRepository") as repository, \
                 patch.object(operator, "CodexModelRunner", Runner):
                repository.return_value.load.return_value = ("fixed", {"config": {"scholarly_enabled": False}}, {})
                result = operator.check(root, "instance", root, probe=True)
            self.assertEqual(result["outcome"], "completed", result)
            self.assertEqual(len(observed), 1)


class ReviewFailureTests(purpose.PurposeHarness):
    def test_failed_contract_review_is_not_regenerated_while_waiting_for_diagnosis(self):
        engine, _ = self.make(scholarly_enabled=False)
        engine.run(max_steps=1)
        task_id = next(iter(engine.runtime["tasks"]))
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "reviewer unavailable"}
        engine.runner = Runner()
        engine.run(max_steps=1)
        self.assertTrue(any(e["action"].get("target") == task_id for e in engine.runtime["waiting_actions"].values()))
        self.assertFalse(any(a["role"] == "task_contract_review" and a.get("target") == task_id for a in engine.runtime["queue"]))

    def test_failed_identity_slot_is_not_regenerated_after_its_peer_finishes(self):
        engine, runner = self.make(scholarly_enabled=False)
        self.drive(engine, predicate=lambda e: bool(e.runtime["review_cycles"]))
        original_run, original_answer = runner.run, runner.answer
        def run(**args):
            context = purpose.parse_context(args["prompt"], args["workspace"])
            if context["action"].get("slot") == "initial-0":
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "reviewer unavailable"}
            return original_run(**args)
        def answer(role, context, workspace):
            if role == "operational_review":
                return {**purpose.common("Preserved failure needs repair."), "decision": "wait", "reason": "Repair the execution environment."}
            return original_answer(role, context, workspace)
        runner.run, runner.answer = run, answer
        engine.run(max_steps=3)
        self.assertFalse(any(a["role"] == "identity_review" and a.get("slot") == "initial-0" for a in engine.runtime["queue"]))
        self.assertTrue(any(e["action"].get("slot") == "initial-0" for e in engine.runtime["waiting_actions"].values()))

    def test_explicit_diagnosis_can_open_one_new_attempt_after_an_exhausted_retry(self):
        from do_math.engine import control
        engine, _ = self.make(scholarly_enabled=False)
        engine.runtime["queue"] = [{"id": "AC-failed", "role": "maintenance", "recovery_attempt": 1}]
        engine._save()
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                args["on_started"]({"pid": 1})
                if context["action"]["role"] == "maintenance":
                    return {"status": "failed", "output": None, "usage": {}, "error": "configuration failure"}
                return {"status": "completed", "usage": {}, "output": {
                    **purpose.common("The explicit repair diagnosis is complete."), "decision": "retry",
                    "reason": "The independent operator repaired the execution configuration and requested this diagnosis."}}
        engine.runner = Runner()
        engine.run(max_steps=1)
        failed = next(iter(engine.runtime["executions"]))
        control(self.repo, engine.instance["id"], "request", origin="operator", config={"role": "operational_review", "target": failed},
                text="Inspect the repaired execution configuration before one new attempt.")
        engine.process_controls()
        engine.run(max_steps=1)
        retries = [a for a in engine.runtime["queue"] if a["role"] == "maintenance"]
        self.assertEqual(len(retries), 1)
        self.assertNotEqual(retries[0]["id"], "AC-failed")
        self.assertEqual(retries[0]["recovery_attempt"], 1)

    def test_late_contract_review_cannot_reopen_a_user_closed_task(self):
        from do_math.engine import control
        engine, runner = self.make(scholarly_enabled=False)
        engine.run(max_steps=1)
        original = runner.run
        def run(**args):
            result = original(**args)
            context = purpose.parse_context(args["prompt"], args["workspace"])
            control(self.repo, engine.instance["id"], "decision", config={"change": {
                "kind": "task_scope", "task_id": context["task"]["id"], "disposition": "withdraw", "reason": "Withdraw this task."}})
            args["should_stop"]()
            return result
        runner.run = run
        engine.run(max_steps=1)
        task = next(iter(engine.runtime["tasks"].values()))
        self.assertEqual(task["status"], "closed")
        review = next(e for e in engine.runtime["executions"].values() if e["role"] == "task_contract_review")
        self.assertNotEqual(review["outcome"], "output_accepted")
        self.assertFalse(any(a.get("target") == task["id"] for a in engine.runtime["queue"]))

    def test_late_identity_result_is_preserved_without_retrying_a_superseded_slot(self):
        from do_math.engine import control
        engine, runner = self.make(scholarly_enabled=False)
        self.drive(engine, predicate=lambda e: bool(e.runtime["review_cycles"]))
        cid = next(iter(engine.runtime["review_cycles"]))
        original = runner.run
        def run(**args):
            result = original(**args)
            context = purpose.parse_context(args["prompt"], args["workspace"])
            control(self.repo, engine.instance["id"], "knowledge", config={"operation": "revise", "id": context["action"]["target"],
                "changes": {"explanation": "A replacement explanation of the same domain."}, "reason": "Revise the sealed proposal."})
            args["should_stop"]()
            return result
        runner.run = run
        engine.run(max_steps=1)
        self.assertFalse(any(a.get("review_cycle_id") == cid for a in engine.runtime["queue"]))
        review = next(e for e in engine.runtime["executions"].values() if e["role"] == "identity_review")
        self.assertNotEqual(review["outcome"], "output_accepted")
        self.assertIsNotNone(engine.store.read(f"runtime/artifacts/{review['artifact_bundle']}/output.json"))

    def test_large_own_review_history_does_not_request_mathematical_reconstruction(self):
        from do_math.review_cycle import record_turn
        engine, runner = self.make(scholarly_enabled=False)
        self.drive(engine, predicate=lambda e: bool(e.runtime["review_cycles"]))
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        cid, kid = action["review_cycle_id"], action["target"]
        engine.runtime["review_cycles"][cid] = record_turn(engine.runtime["review_cycles"][cid], action["slot"], [
            {"role": "assistant", "content": "Retained earlier reasoning. " * 30000, "message_id": "retained-history"}])
        engine.instance["config"]["max_input_bytes"] = 500000
        before = deepcopy(engine.instance["knowledge"][kid])
        engine._save()
        count = len(runner.calls)
        engine.run(max_steps=1)
        self.assertEqual(len(runner.calls), count)
        self.assertEqual(engine.instance["knowledge"][kid], before)
        self.assertFalse(any(a.get("reconstruction_target") == kid for a in engine.runtime["queue"]))

    def test_fixed_question_resolver_accepts_the_supplied_source_aliases(self):
        from do_math.engine import control
        engine, _ = self.make(scholarly_enabled=False)
        path = self.root / "paper.txt"
        path.write_text("The exact original source.", encoding="utf-8")
        control(self.repo, engine.instance["id"], "source", config={"path": str(path)})
        engine.process_controls()
        self.drive(engine, predicate=lambda e: bool(e.runtime["review_cycles"]))
        action = next(a for a in engine.runtime["queue"] if a["role"] == "identity_review")
        workspace = self.root / "source-alias-input"
        context = engine._context(action, workspace)
        source = context["sources"][0]
        cycle = engine.runtime["review_cycles"][action["review_cycle_id"]]
        for reference in (source["id"], "source:" + source["name"], source["local_path"], source["path"], source["name"]):
            with self.subTest(reference=reference):
                error = None
                try:
                    resolved = engine._research_source_spec(cycle, action, reference)
                except ValueError as rejected:
                    error = str(rejected)
                self.assertIsNone(error, "a supplied source alias was refused: " + str(error))
                self.assertEqual(resolved["sha256"], source["sha256"])
    def test_private_insight_rechecks_its_own_basis_when_published_after_peer_review(self):
        from do_math.engine import control
        engine, runner = self.make(scholarly_enabled=False)
        control(self.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": {
            "kind": "observation", "title": "Earlier computation", "statement": "The answer is one.",
            "explanation": "A bounded computation.", "summary": "One was computed.", "lean_code": ""}})
        engine.process_controls()
        kid = next(iter(engine.instance["knowledge"]))
        engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] == "research_preparation"]
        engine._save()
        original = runner.run
        def run(**args):
            context = purpose.parse_context(args["prompt"], args["workspace"])
            result = original(**args)
            action = context["action"]
            if action["role"] == "identity_review" and action["stage"] == "initial":
                if action["slot"] == "initial-0":
                    (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({"research_insights": [{
                        "kind": "question", "title": "Private followup", "statement": "What follows from the old computation?",
                        "summary": "A possible followup.", "evidence_ids": [kid]}]}))
                else:
                    control(self.repo, engine.instance["id"], "knowledge", config={"operation": "revise", "id": kid,
                        "changes": {"statement": "The corrected answer is two."}, "reason": "Correct a computation."})
                    args["should_stop"]()
            return result
        runner.run = run
        self.drive(engine, predicate=lambda e: any(k["title"] == "Private followup" for k in e.instance["knowledge"].values()))
        insight = next(k for k in engine.instance["knowledge"].values() if k["title"] == "Private followup")
        self.assertTrue(insight.get("use_suspended", False))
        self.assertEqual(insight["status"], "candidate")
        self.assertEqual(insight["dependencies"], [kid])

    def test_exhausted_investigation_returns_incomplete_to_its_waiting_review_slot(self):
        from test_review_research import InvestigationRunner, signed_formal_fixture
        from do_math.review_cycle import next_actions
        engine, _ = self.make(scholarly_enabled=False)
        class Runner(InvestigationRunner):
            def run(inner, **args):
                if "role: supplemental_research." in args["prompt"]:
                    args["on_started"]({"pid": 1})
                    return {"status": "failed", "output": None, "usage": {}, "error": "diagnosed investigation failed"}
                return super().run(**args)
        engine.runner = Runner()
        engine.formal_verifier = signed_formal_fixture
        self.drive(engine, predicate=lambda e: any(a["role"] == "supplemental_research" for a in e.runtime["queue"]))
        request = next(a for a in engine.runtime["queue"] if a["role"] == "supplemental_research")
        request["recovery_attempt"] = 1
        engine.runtime["queue"] = [request]
        engine._save()
        engine.run(max_steps=1)
        cycle = engine.runtime["review_cycles"][request["review_cycle_id"]]
        investigation = cycle["research"][request["research_request_id"]]
        self.assertEqual(investigation["status"], "unresolved")
        self.assertEqual(investigation["result"]["execution_status"], "incomplete")
        self.assertTrue(any(a["slot"] == request["requesting_slot"] for a in next_actions(cycle)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
