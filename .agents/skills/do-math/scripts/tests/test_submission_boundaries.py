"""Regression contracts for evidence acceptance and bounded failure recovery.

The scheduler, Git snapshots and SQLite slots are real. Model replies are
scripted to make the otherwise nondeterministic failure ordering reproducible.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_session_scheduler as scheduling
import test_purpose_engine as purpose
from test_engine import common, formal_ok
from do_math.engine import control
from do_math.knowledge import assess_use, revise_knowledge
from do_math.context_store import fit_context
from do_math.planning import contract_hash


def note(title="Computation", **changes):
    return {"kind": "observation", "title": title, "statement": "The result is one.",
            "summary": "A bounded computation.", "explanation": "Exact finite computation.",
            "lean_code": "", "declaration_names": [], "dependencies": [], **changes}


def returned(role, **changes):
    output = common(role)
    if role == "research_work":
        output.update(outcome="submitted", report="The assigned scope was examined.", checkpoint="Ready.")
    return {"status": "completed", "output": {**output, **changes}, "usage": {}, "error": None}


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = scheduling.ParallelEngineTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)

    def test_newly_reported_knowledge_dependencies_bind_the_read_snapshot(self):
        for declaration in ("used_sources", "dependencies", "both", "knowledge_path"):
            with self.subTest(declaration=declaration):
                class Runner:
                    def run(inner, **args):
                        args["on_started"]({"pid": 1})
                        original = json.loads((args["workspace"] / "input/knowledge" / (kid + ".json")).read_bytes())
                        self.assertEqual(original["statement"], "The result is one.")
                        control(self.fixture.repo, engine.instance["id"], "knowledge", config={
                            "operation": "revise", "id": kid, "changes": {"statement": "The result is two."},
                            "reason": "Correct the computation."})
                        args["should_stop"]()
                        dependencies = [kid] if declaration in {"dependencies", "both"} else []
                        used = [kid] if declaration in {"used_sources", "both"} else []
                        if declaration == "knowledge_path":
                            used = ["input/knowledge/" + kid + ".json"]
                        return returned("research_work", used_sources=used,
                                        knowledge=[note("Derived", dependencies=dependencies)])
                engine = self.fixture.engine(Runner(), count=1, max_output_repairs=0)
                control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": note()})
                engine.process_controls()
                kid = next(iter(engine.instance["knowledge"]))
                engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] == "research_work"]
                engine._save()
                engine.run(max_steps=1)
                execution = next(e for e in engine.runtime["executions"].values() if e["role"] == "research_work")
                self.assertEqual(execution["outcome"], "execution_incomplete")
                self.assertIn("dependency", execution["error"])
                self.assertFalse(any(k["title"] == "Derived" for k in engine.instance["knowledge"].values()))

    def test_identity_review_ignores_unrelated_source_change_but_checks_required_source(self):
        for required in (False, True):
            with self.subTest(required=required):
                source = self.fixture.root / ("required.txt" if required else "unrelated.txt")
                source.write_text("original", encoding="utf-8")
                class Runner:
                    def run(inner, **args):
                        context = purpose.parse_context(args["prompt"], args["workspace"])
                        args["on_started"]({"pid": 1})
                        source.write_text("corrected", encoding="utf-8")
                        control(self.fixture.repo, engine.instance["id"], "source", config={"path": str(source)})
                        args["should_stop"]()
                        return returned("identity_review", proposal_digest=context["role_review"]["proposal_digest"],
                                        used_sources=["proposal:statement"], decision="match", findings=[], scope_complete=True)
                engine = self.fixture.engine(Runner(), count=0, max_output_repairs=0)
                engine.formal_verifier = formal_ok
                control(self.fixture.repo, engine.instance["id"], "source", config={"path": str(source)})
                control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate":
                    note("Formal claim", kind="theorem", lean_code="theorem t : True := by trivial",
                         declaration_names=["t"], source_refs=[source.name] if required else [])})
                engine.process_controls()
                engine.run(max_steps=1)
                engine.run(max_steps=1)
                execution = next(e for e in engine.runtime["executions"].values() if e["role"] == "identity_review")
                self.assertEqual(execution["outcome"], "execution_incomplete" if required else "output_accepted")

    def test_changed_prerequisite_task_assessment_invalidates_its_running_consumer(self):
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "revise", "id": kid,
                    "changes": {"statement": "The result is two."}, "reason": "Correct a prerequisite result."})
                args["should_stop"]()
                return returned("research_work", used_sources=[prerequisite["id"]])
        engine = self.fixture.engine(Runner(), count=1, max_output_repairs=0)
        control(self.fixture.repo, engine.instance["id"], "knowledge", config={"operation": "import", "candidate": note()})
        engine.process_controls()
        kid = next(iter(engine.instance["knowledge"]))
        task = next(iter(engine.runtime["tasks"].values()))
        prerequisite = {**deepcopy(task), "id": "TK-prerequisite", "title": "Prerequisite", "status": "completed",
                        "results": [{"execution_id": "EX-prerequisite", "report": "The result is one.", "used_sources": [kid]}],
                        "assessment": {"current": True, "decision": "completed", "criteria_results": [
                            {"criterion": "report", "satisfied": True, "evidence": "The report."}]}}
        engine.runtime["tasks"][prerequisite["id"]] = prerequisite
        task["dependencies"] = [prerequisite["id"]]
        task["reviews"][0]["contract_sha256"] = contract_hash(task)
        engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] == "research_work"]
        engine._save()
        engine.run(max_steps=1)
        execution = next(e for e in engine.runtime["executions"].values() if e["role"] == "research_work")
        self.assertFalse(engine.runtime["tasks"][prerequisite["id"]]["assessment"]["current"])
        self.assertEqual(execution["outcome"], "execution_incomplete")

    def test_exhausted_retry_does_not_stop_a_running_independent_worker(self):
        peer_started = threading.Event()
        observed = {"stopped": False}
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                args["on_started"]({"pid": 1})
                if context["task"]["title"] == "0":
                    if not peer_started.wait(10):
                        raise AssertionError("peer never started")
                    return {"status": "failed", "output": None, "usage": {}, "error": "diagnosed retry failed"}
                (args["workspace"] / "result.txt").write_text("Independent result.", encoding="utf-8")
                peer_started.set()
                until = time.monotonic() + 2
                while time.monotonic() < until:
                    if args["should_stop"]():
                        observed["stopped"] = True
                        return {"status": "stopped", "output": None, "usage": {}, "error": "unrelated pause"}
                    time.sleep(.02)
                return returned("research_work")
        engine = self.fixture.engine(Runner(), count=2, checkpoint_grace_seconds=1)
        failed_action = engine.runtime["queue"][0]
        failed_action["recovery_attempt"] = 1
        failed_id = failed_action["id"]
        engine._save()
        engine.run(max_steps=2)
        self.assertFalse(observed["stopped"], "one failed request revoked an independent worker")
        self.assertNotEqual(engine.runtime["status"], "paused")
        self.assertIn(failed_id, engine.runtime["waiting_actions"])
        peer = next(e for e in engine.runtime["executions"].values() if e["action"]["id"] != failed_id)
        self.assertEqual(peer["outcome"], "output_accepted")
        self.assertTrue(any(f["path"] == "result.txt" for f in peer["output_files"]))
        control(self.fixture.repo, engine.instance["id"], "resume", origin="operator")
        engine.process_controls()
        self.assertNotIn(failed_id, [a.get("id") for a in engine.runtime["queue"]])

    def test_legacy_failure_is_parked_before_diagnosis(self):
        class Runner:
            def run(inner, **args):
                args["on_started"]({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "local execution failure"}
        engine = self.fixture.engine(Runner(), count=1, session_limits=None)
        failed_id = engine.runtime["queue"][0]["id"]
        engine.run(max_steps=1)
        self.assertNotIn(failed_id, [a.get("id") for a in engine.runtime["queue"]])
        self.assertEqual(engine.runtime["waiting_actions"][failed_id]["kind"], "execution_failure")
        self.assertTrue(any(a["role"] == "operational_review" for a in engine.runtime["queue"]))

    def test_same_oversized_contract_is_not_automatically_requeued(self):
        class Runner:
            def run(inner, **args):
                raise AssertionError("oversized contract must not start a model")
        engine = self.fixture.engine(Runner(), count=1, max_input_bytes=500000)
        task = next(iter(engine.runtime["tasks"].values()))
        task.update(question="q" * 600000, status="planned", reviews=[])
        engine.runtime["queue"] = []
        engine._save()
        engine.run(max_steps=3)
        failures = [row for row in engine.runtime.get("input_overflows", []) if row["action"]["role"] == "task_contract_review"]
        self.assertEqual(len(failures), 1)
        self.assertEqual(engine.runtime["executions"], {})

    def test_large_accepted_report_survives_revision_review_and_resumed_work(self):
        roles, work_calls = [], []
        class Runner:
            def run(inner, **args):
                context = purpose.parse_context(args["prompt"], args["workspace"])
                role = context["action"]["role"]
                roles.append(role)
                args["on_started"]({"pid": 1})
                if role == "research_work":
                    work_calls.append(context["task"]["revision"])
                    if len(work_calls) == 1:
                        (args["workspace"] / "evidence.txt").write_bytes(b"preserved partial evidence")
                        return returned(role, outcome="partial", report="p" * 600000, remaining_work=["Resolve the remaining case."])
                    self.assertEqual(context["task"]["results"][0]["report"], "p" * 600000)
                    previous = next(f for f in context["previous_output_files"] if f["path"] == "evidence.txt")
                    self.assertEqual((args["workspace"] / previous["local_path"]).read_bytes(), b"preserved partial evidence")
                    return returned(role)
                if role == "research_plan":
                    assessments = [{"task_id": task["id"], "decision": "incomplete", "reason": "The remaining case is explicit.",
                        "criteria_results": [{"criterion": criterion, "satisfied": False, "evidence": "The partial report records unfinished work."}
                                             for criterion in task["completion_criteria"]]}
                        for task in context["tasks"] if task["status"] == "assessing"]
                    return returned(role, selections=context["ready_task_ids"], deferred=[], task_assessments=assessments,
                        goal_audit=False, preparation_requests=["Revise the unfinished task."] if assessments else [])
                if role == "research_preparation":
                    task = context["tasks"][0]
                    return returned(role, candidates=[purpose.candidate(task["title"], formal=False, revises=task["id"])])
                if role == "task_contract_review":
                    return returned(role, decision="approved", findings=[])
                raise AssertionError("unexpected role: " + role)
        engine = self.fixture.engine(Runner(), count=1, max_input_bytes=500000)
        for _ in range(12):
            engine.run(max_steps=1)
            if len(work_calls) == 2:
                break
        self.assertEqual(len(work_calls), 2, engine.runtime["questions"])
        self.assertGreater(work_calls[1], work_calls[0])
        self.assertIn("task_contract_review", roles)
        self.assertFalse(engine.runtime.get("input_overflows"))
        worker_results = [e["outcome"] for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertEqual(worker_results, ["output_accepted", "output_accepted"])


class HistoricalInputTests(unittest.TestCase):
    def test_large_checkpoint_and_operational_evidence_use_exact_readable_references(self):
        import tempfile
        checkpoint = {"current_claim": "x" * 600000, "evidence_paths": [], "attempts": [],
                      "remaining_work": [], "next_step": "Continue.", "progress_state": "working"}
        contexts = [
            ({"resume_checkpoint": {"kind": "worker_checkpoint", "value": checkpoint}}, []),
            ({"recovery_materials": {"checkpoint": checkpoint}}, []),
            ({"execution_to_review": {"id": "EX-old", "role": "research_work", "status": "ended", "details": checkpoint},
              "observation": {"execution_id": "EX-old", "reason": "checkpoint", "sample": {"checkpoint": checkpoint}}},
             ["execution_to_review", "observation"]),
        ]
        for additions, required in contexts:
            with self.subTest(fields=list(additions)), tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                original = {"goal": "g", "action": {"role": "operational_review"}, **additions}
                result = fit_context(original, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", *required])
                self.assertIsNone(result["overflow"])
                for key, value in additions.items():
                    ref = result["context"][key]["source_ref"]
                    self.assertEqual(json.loads((workspace / ref["path"]).read_bytes()), value)

    def test_large_repair_action_and_previous_execution_remain_readable_by_reference(self):
        import tempfile
        action = {"id": "AC-repair", "role": "research_preparation", "repair_attempt": 1,
                  "repair": {"execution_id": "EX-old", "error": "bad extension",
                             "previous_output": {"summary": "x" * 600000, "candidates": []}}}
        context = {"goal": "g", "action": action, "previous_execution": {"id": "EX-old", "action": action}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action"])
            self.assertIsNone(result["overflow"])
            current = result["context"]["action"]
            self.assertEqual(current["id"], action["id"])
            self.assertEqual(current["role"], action["role"])
            self.assertEqual(json.loads((workspace / current["source_ref"]["path"]).read_bytes()), action)

    def test_preserved_history_does_not_recreate_current_knowledge_dependencies(self):
        for key in ("history", "use_history", "review_history", "revision_history", "assessment_history", "governance_history", "previous_initial_reviews"):
            with self.subTest(key=key):
                source = {**note(), "id": "KN-A", "status": "verified"}
                target = {**note("Independent"), "id": "KN-B", "status": "verified", key: [{"dependencies": ["KN-A"]}]}
                instance = {"knowledge": {"KN-A": source, "KN-B": target}}
                changed, _ = revise_knowledge(instance, {}, "KN-A", {"statement": "corrected"}, reason="correction", actor_ref="user")
                self.assertFalse(changed["knowledge"]["KN-B"].get("use_suspended", False))
                self.assertTrue(assess_use(changed["knowledge"]["KN-B"], changed)["valid"])

    def test_large_task_history_is_readable_without_inflating_the_current_contract(self):
        import tempfile
        task = {"id": "TK-A", "revision": 2, "title": "Current contract", "question": "q", "scope": "s",
                "completion_criteria": ["c"], "results": [{"report": "x" * 600000}],
                "revision_history": [{"question": "old", "results": [{"report": "x" * 600000}]}]}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = {"goal": "g", "action": {"role": "task_contract_review"}, "task": task}
            result = fit_context(context, max_bytes=20000, workspace=workspace, mandatory_keys=["goal", "action", "task"])
            self.assertIsNone(result["overflow"])
            current = result["context"]["task"]
            self.assertEqual(current["question"], task["question"])
            self.assertEqual(current["completion_criteria"], task["completion_criteria"])
            self.assertEqual(contract_hash(current), contract_hash(task))
            self.assertEqual(json.loads((workspace / current["source_ref"]["path"]).read_bytes()), task)


if __name__ == "__main__":
    unittest.main(verbosity=2)
