"""Assessment completeness and the real preparation-to-review state transitions.

Model responses are explicit fixtures; the engine, submission checker, snapshots
and installed producer command are exercised, not model judgment quality.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.contracts import schema_for
from do_math.model_policy import LIMITS, MODELS
from do_math.planning import contract_hash
from do_math.repository import canonical_json
from do_math.submission import payload_issues
from test_engine import common, context_from
from test_purpose_engine import PurposeHarness


def candidate(title="one"):
    return {"title": title, "question": "Check the given identity", "scope": "Given inputs only",
            "expected_result": "A checked report", "completion_criteria": ["Report the check"],
            "inputs": [], "reuse": [], "work_class": "nonformal", "revises_task_id": ""}


def rating(**identity):
    return {**identity, "difficulty": "low", "importance": "medium", "reason": "A bounded check of one supplied identity."}


class AssessmentSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.context = {"action": {"role": "research_preparation"}, "budget_unit": "concurrent_sessions",
                        "tasks": [], "knowledge_catalog": [], "kind_definitions": {}, "sources": []}
        self.output = {**common("research_preparation"), "candidates": [candidate("one"), candidate("two")]}

    def issues(self, extensions):
        return payload_issues(self.output, schema_for("research_preparation"), self.context, extensions, self.workspace)

    def test_missing_candidate_assessments_are_rejected_with_missing_titles(self):
        issues = self.issues({"model_assessments": [rating(task_title="one")]})
        self.assertTrue(issues, "a candidate without an assessment must not pass")
        self.assertIn("two", json.dumps(issues))

    def test_missing_family_cannot_bypass_the_completeness_check(self):
        self.assertTrue(self.issues({}))

    def test_exact_coverage_is_accepted_and_duplicates_and_foreign_targets_are_rejected(self):
        from test_engine import contract_checks
        self.assertEqual(self.issues({"model_assessments": [rating(task_title="one"), rating(task_title="two")],
                                      "contract_checks": contract_checks(self.output["candidates"])}), [])
        for titles in (("one", "one"), ("one", "foreign")):
            with self.subTest(titles=titles):
                self.assertTrue(self.issues({"model_assessments": [rating(task_title=x) for x in titles]}))

    def test_revised_candidate_also_needs_a_new_assessment(self):
        old = {**candidate(), "id": "TK-old", "revision": 1, "status": "needs_revision", "model_assessment": rating()}
        self.context["tasks"] = [old]
        self.output["candidates"] = [{**candidate(), "revises_task_id": "TK-old"}]
        self.assertTrue(self.issues({}), "the old edition's assessment must not fill the new candidate implicitly")

    def test_empty_preparation_and_legacy_call_budget_contract_remain_accepted(self):
        self.output["candidates"] = []
        self.assertEqual(self.issues({}), [])
        self.output["candidates"] = [candidate()]
        self.context["budget_unit"] = "execution_attempts"
        self.assertEqual(self.issues({}), [])

    def test_assessment_only_payload_cannot_edit_contracts_or_use_other_extensions(self):
        self.context["action"]["assessment_targets"] = {"TK-one": {"revision": 1, "contract_sha256": "frozen"}}
        self.output["candidates"] = []
        good = {"model_assessments": [rating(task_id="TK-one")]}
        self.assertEqual(self.issues(good), [])
        self.output["candidates"] = [candidate()]
        self.assertTrue(self.issues(good))
        self.output["candidates"] = []
        self.assertTrue(self.issues({**good, "task_dispositions": [{"task_id": "TK-one", "disposition": "withdraw", "reason": "change user scope"}]}))
        self.assertTrue(self.issues({"model_assessments": [rating(task_id="TK-other")]}))

    def test_assessment_only_deferrals_must_cover_targets_without_overlap(self):
        self.context["action"]["assessment_targets"] = {"TK-one": {}, "TK-two": {}}
        self.output["candidates"] = []
        valid = {"model_assessments": [rating(task_id="TK-one")],
                 "model_assessment_deferrals": [{"task_id": "TK-two", "reason": "Need the required source."}]}
        self.assertEqual(self.issues(valid), [])
        self.assertTrue(self.issues({"model_assessments": [rating(task_id="TK-one")]}))
        self.assertTrue(self.issues({**valid, "model_assessments": [rating(task_id="TK-one"), rating(task_id="TK-two")]}))


class AssessmentFlowTests(PurposeHarness):
    def prepare_engine(self):
        engine, _ = self.make(scholarly_enabled=False, operator_enabled=False, session_limits=deepcopy(LIMITS))
        engine.runtime["queue"] = []
        engine.instance["academic_requirements"] = {"sha256": "preserve-user-requirement", "items": []}
        for number in (1, 2):
            tid = f"TK-academic-{number}"
            engine.runtime["tasks"][tid] = {**candidate(str(number)), "id": tid, "revision": 1, "feature_version": 2,
                "status": "planned", "producer_execution": "user-requirement:r", "academic_requirement_id": "r",
                "requirements_sha256": "preserve-user-requirement", "results": [], "reviews": [], "dependencies": [],
                "occurrence_condition": {"op": "always"}, "initial_observation_rules": []}
            engine._enqueue("task_contract_review", tid)
        engine._save()
        return engine

    def test_missing_academic_assessments_are_batched_before_any_contract_review(self):
        engine = self.prepare_engine()
        engine._refresh_readiness()
        queue = engine.runtime["queue"]
        self.assertFalse(any(a["role"] == "task_contract_review" for a in queue))
        preparations = [a for a in queue if a.get("assessment_targets")]
        self.assertEqual(len(preparations), 1)
        action = preparations[0]
        self.assertEqual(action["role"], "research_preparation")
        self.assertEqual(set(action["assessment_targets"]), set(engine.runtime["tasks"]))
        self.assertEqual(engine._select_model(action)["model"], MODELS["high"])
        engine._refresh_readiness()
        self.assertEqual(len([a for a in engine.runtime["queue"] if a.get("assessment_targets")]), 1)

    def test_assessment_only_run_preserves_user_contract_and_unblocks_independent_review(self):
        engine = self.prepare_engine()
        before = deepcopy(engine.runtime["tasks"])
        seen = []
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                context = context_from(args["prompt"])
                seen.append(context)
                targets = context["action"].get("assessment_targets", {})
                output = {**common("research_preparation"), "candidates": []}
                extensions = {"model_assessments": [rating(task_id=tid) for tid in targets]}
                (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json(extensions))
                draft = args["workspace"] / ".scratch/submission.json"
                draft.parent.mkdir(exist_ok=True); draft.write_bytes(canonical_json(output))
                checked = subprocess.run([*context["submission_contract"]["command"], "--output", str(draft)],
                    cwd=args["workspace"], capture_output=True, timeout=30)
                if checked.returncode:
                    raise AssertionError(checked.stdout.decode("utf-8", "replace"))
                return {"status": "completed", "output": output, "usage": {}}
        engine.runner = Runner()
        engine.run(max_steps=1)
        self.assertEqual(len(seen), 1)
        self.assertTrue(seen[0]["action"].get("assessment_targets"))
        for tid, task in engine.runtime["tasks"].items():
            self.assertEqual(task["model_assessment"], rating())
            self.assertEqual({k: v for k, v in task.items() if k != "model_assessment"}, before[tid])
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime["queue"] if a["role"] == "task_contract_review"]
        self.assertEqual({a["target"] for a in reviews}, set(before))
        self.assertTrue(all(engine._select_model(a)["tier"] == "medium" for a in reviews))
        self.assertEqual(engine.runtime["cycles"], 0, "assessment completion is not a new research preparation cycle")

    def test_assessment_request_does_not_absorb_an_ordinary_preparation(self):
        engine = self.prepare_engine()
        engine._refresh_readiness()
        engine._enqueue("research_preparation", reason="Explore a separate research direction")
        requests = [a for a in engine.runtime["queue"] if a["role"] == "research_preparation"]
        self.assertEqual(len(requests), 2)

    def test_assessment_only_schema_makes_contract_creation_impossible(self):
        engine = self.prepare_engine()
        engine._refresh_readiness()
        action = next(a for a in engine.runtime["queue"] if a.get("assessment_targets"))
        schema = engine._response_schema(action)
        self.assertEqual(schema["properties"]["candidates"].get("maxItems"), 0)

    def test_saved_deferral_with_sources_does_not_retry_without_input_change(self):
        engine = self.prepare_engine()
        engine.instance["sources"] = [{"name": "paper.txt", "path": "sources/paper.txt", "sha256": "a" * 64}]
        engine._refresh_readiness()
        action = next(a for a in engine.runtime["queue"] if a.get("assessment_targets"))
        engine.runtime["queue"] = []
        engine.runtime["waiting_actions"] = {action["id"]: json.loads(canonical_json({
            "action": action, "kind": "model_assessment_input", "input_version": engine._assessment_input_version()}))}
        engine._ensure_model_assessments()
        self.assertIn(action["id"], engine.runtime["waiting_actions"])
        self.assertFalse(any(a.get("assessment_targets") for a in engine.runtime["queue"]))
        engine.instance["sources"][0]["sha256"] = "b" * 64
        engine._ensure_model_assessments()
        self.assertNotIn(action["id"], engine.runtime["waiting_actions"])
        self.assertTrue(any(a.get("assessment_targets") for a in engine.runtime["queue"]))

    def test_completed_normal_preparation_does_not_resolve_a_failed_assessment_request(self):
        engine = self.prepare_engine()
        engine._refresh_readiness()
        action = next(a for a in engine.runtime["queue"] if a.get("assessment_targets"))
        engine.runtime["waiting_actions"] = {action["id"]: {"action": action, "kind": "output_validation"}}
        engine._resolve_failed_actions({"role": "research_preparation"}, "EX-normal")
        self.assertIn(action["id"], engine.runtime["waiting_actions"])

    def test_deferred_assessment_waits_for_input_and_can_resume_without_stale_question(self):
        from do_math.engine import control
        engine = self.prepare_engine()
        class DeferringRunner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                context = context_from(args["prompt"])
                targets = context["action"]["assessment_targets"]
                (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({
                    "model_assessment_deferrals": [{"task_id": tid, "reason": "Need the missing source text."} for tid in targets]}))
                return {"status": "completed", "output": {**common("research_preparation"), "candidates": []}, "usage": {}}
        engine.runner = DeferringRunner()
        engine.run(max_steps=1)
        self.assertEqual(len(engine.runtime["waiting_actions"]), 1)
        held = next(iter(engine.runtime["waiting_actions"].values()))
        question = held["question"]
        self.assertIn(question, engine.runtime["questions"])
        for _ in range(3):
            engine._refresh_readiness()
            self.assertFalse(any(a.get("assessment_targets") for a in engine.runtime["queue"]))
        control(self.repo, engine.instance["id"], "resume", text="The requested source is now available.")
        engine.process_controls()
        self.assertNotIn(question, engine.runtime["questions"])
        self.assertTrue(any(a.get("assessment_targets") for a in engine.runtime["queue"]))

    def test_late_assessment_cannot_change_a_revised_user_contract(self):
        engine = self.prepare_engine()
        class RevisingRunner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                context = context_from(args["prompt"])
                targets = context["action"]["assessment_targets"]
                (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({
                    "model_assessments": [rating(task_id=tid) for tid in targets]}))
                task = engine.runtime["tasks"][next(iter(targets))]
                task["revision"] += 1
                task["scope"] = "A revised user requirement"
                engine._save()
                return {"status": "completed", "output": {**common("research_preparation"), "candidates": []}, "usage": {}}
        engine.runner = RevisingRunner()
        engine.run(max_steps=1)
        execution = next(e for e in engine.runtime["executions"].values() if e["action"].get("assessment_targets"))
        self.assertEqual(execution["outcome"], "output_preserved_after_target_change")
        self.assertTrue(all("model_assessment" not in t for t in engine.runtime["tasks"].values()))
        self.assertTrue(any(a.get("assessment_targets") for a in engine.runtime["queue"]))

    def test_receiver_parks_incomplete_new_candidate_assessments_without_creating_tasks(self):
        engine, _ = self.make(scholarly_enabled=False, operator_enabled=False,
                              session_limits=deepcopy(LIMITS), max_output_repairs=0)
        class MissingRunner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "completed", "output": {**common("research_preparation"), "candidates": [candidate()]}, "usage": {}}
        engine.runner = MissingRunner()
        engine.run(max_steps=1)
        self.assertEqual(engine.runtime["tasks"], {})
        self.assertTrue(any("model assessment coverage" in e.get("reason", "") for e in engine.runtime["waiting_actions"].values()))

    def test_real_academic_generation_enters_assessment_preparation_on_session_conversion(self):
        from do_math.engine import control
        from test_academic_engine import requirement
        engine, _ = self.make(scholarly_enabled=False)
        control(self.repo, engine.instance["id"], "decision", config={"change": {
            "kind": "academic_requirements", "decision_id": "AR-validation", "requirements": [requirement(["Explain the result"])]}})
        engine.process_controls()
        self.drive(engine, predicate=lambda e: e.instance["goal_status"] == "mathematically_solved")
        academic = {tid: t for tid, t in engine.runtime["tasks"].items() if t.get("academic_requirement_id")}
        self.assertTrue(academic)
        control(self.repo, engine.instance["id"], "configure", config={"session_limits": deepcopy(LIMITS)})
        engine.process_controls()
        engine._refresh_readiness()
        covered = {tid for a in engine.runtime["queue"] for tid in a.get("assessment_targets", {})}
        self.assertTrue(set(academic) <= covered)
        self.assertFalse(any(a["role"] == "task_contract_review" and a.get("target") in academic for a in engine.runtime["queue"]))


class ActualGitAssessmentTests(PurposeHarness):
    memory = False
    prepare_engine = AssessmentFlowTests.prepare_engine

    def test_installed_producer_command_and_assessment_handoff_with_actual_git(self):
        AssessmentFlowTests.test_assessment_only_run_preserves_user_contract_and_unblocks_independent_review(self)


class RejectedAcademicAssessmentTests(PurposeHarness):
    prepare_engine = AssessmentFlowTests.prepare_engine

    def rejected_engine(self, decision="revision_required"):
        engine = self.prepare_engine()
        tid = "TK-academic-1"
        engine.runtime["tasks"].pop("TK-academic-2")
        task = engine.runtime["tasks"][tid]
        task["model_assessment"] = rating()
        engine.runtime["queue"] = []
        original = deepcopy(task)
        from do_math.input_basis import capture_decision_basis
        engine._save()
        engine.runtime['executions']['EX-rejected'] = {'id': 'EX-rejected', 'role': 'task_contract_review',
            'status': 'ended', 'input_snapshot': engine.head, 'action': {'role': 'task_contract_review', 'target': tid},
            'decision_basis': capture_decision_basis(engine.instance, engine.runtime, [tid])}
        engine._apply({"role": "task_contract_review", "target": tid}, {
            **common("task_contract_review"), "decision": decision,
            "findings": ["model_assessment.reason: explain the impact on later verification."],
            "questions": []}, "EX-rejected")
        engine._refresh_readiness()
        engine._save()
        return engine, tid, original

    def test_rejected_rating_is_preserved_and_replaced_by_assessment_only_request(self):
        engine, tid, original = self.rejected_engine()
        task = engine.runtime["tasks"][tid]
        self.assertNotIn("model_assessment", task)
        self.assertEqual(task["model_assessment_history"][0]["assessment"], original["model_assessment"])
        self.assertEqual(task["model_assessment_history"][0]["contract_review_execution"], "EX-rejected")
        requests = [a for a in engine.runtime["queue"] if a["role"] == "research_preparation"]
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["assessment_targets"][tid]["contract_sha256"], contract_hash(task))
        for key, value in original.items():
            if key not in {"model_assessment", "reviews", "status"}:
                self.assertEqual(task[key], value)
        for _ in range(3):
            engine._refresh_readiness()
        self.assertEqual(len(task["model_assessment_history"]), 1)
        self.assertFalse(any(a["role"] == "task_contract_review" for a in engine.runtime["queue"]))

    def test_repaired_and_unchanged_ratings_both_receive_fresh_independent_review(self):
        for unchanged in (False, True):
            with self.subTest(unchanged=unchanged):
                engine, tid, original = self.rejected_engine("unresolved" if unchanged else "revision_required")
                chosen = rating() if unchanged else {**rating(), "importance": "high", "reason": "Later verification depends on this report."}
                seen = []
                class Runner:
                    def run(inner, **args):
                        args["on_started"]({"pid": 1})
                        context = context_from(args["prompt"])
                        seen.append(context)
                        role = context["action"]["role"]
                        if role == "research_preparation":
                            self.assertIn(tid, context["action"]["assessment_targets"])
                            supplied = next(t for t in context["tasks"] if t["id"] == tid)
                            self.assertEqual(supplied["reviews"][-1]["execution_id"], "EX-rejected")
                            self.assertEqual(supplied["model_assessment_history"][0]["assessment"], rating())
                            (args["workspace"] / "activity-extensions.json").write_bytes(canonical_json({
                                "model_assessments": [{"task_id": tid, **chosen}]}))
                            output = {**common(role), "candidates": []}
                        else:
                            self.assertEqual(role, "task_contract_review")
                            output = {**common(role), "decision": "approved", "findings": ["The supplied grounds support the rating."]}
                        return {"status": "completed", "output": output, "usage": {}}
                engine.runner = Runner()
                engine.run(max_steps=1)
                self.assertEqual(engine.runtime["tasks"][tid]["model_assessment"], chosen)
                review = next(a for a in engine.runtime["queue"] if a["role"] == "task_contract_review")
                self.assertEqual(engine._select_model(review)["tier"], "medium" if unchanged else "high")
                engine.run(max_steps=1)
                self.assertEqual([c["action"]["role"] for c in seen], ["research_preparation", "task_contract_review"])
                task = engine.runtime["tasks"][tid]
                self.assertEqual(task["status"], "ready")
                self.assertEqual(len(task["reviews"]), 2)
                self.assertEqual(task["reviews"][-1]["decision"], "approved")
                self.assertEqual(engine.runtime["cycles"], 0)
                for key, value in original.items():
                    if key not in {"model_assessment", "reviews", "status"}:
                        self.assertEqual(task[key], value)

    def test_preexisting_rejection_enters_repair_on_refresh(self):
        engine = self.prepare_engine()
        task = engine.runtime["tasks"]["TK-academic-1"]
        task.update(status="needs_revision", model_assessment=rating())
        task["reviews"] = [{"execution_id": "EX-old", "decision": "revision_required",
                            "revision": task["revision"], "contract_sha256": contract_hash(task)}]
        engine.runtime["queue"] = []
        engine._enqueue("research_preparation", task["id"], contract_review_execution="EX-old")
        engine._refresh_readiness()
        self.assertNotIn("model_assessment", task)
        self.assertFalse(any(a.get("contract_review_execution") == "EX-old" for a in engine.runtime["queue"]))
        self.assertTrue(any(task["id"] in a.get("assessment_targets", {}) for a in engine.runtime["queue"]))

    def test_repair_deferral_preserves_obligation_until_resume(self):
        from unittest.mock import patch
        engine, _, _ = self.rejected_engine()
        with patch.object(self, "prepare_engine", return_value=engine):
            AssessmentFlowTests.test_deferred_assessment_waits_for_input_and_can_resume_without_stale_question(self)

    def test_late_repair_cannot_overwrite_a_changed_user_contract(self):
        from unittest.mock import patch
        engine, _, _ = self.rejected_engine()
        with patch.object(self, "prepare_engine", return_value=engine):
            AssessmentFlowTests.test_late_assessment_cannot_change_a_revised_user_contract(self)


if __name__ == "__main__":
    unittest.main()
