from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from do_math.contracts import schema_for  # noqa: E402
from do_math.engine import ResearchEngine, control, initialize  # noqa: E402
from do_math.repository import ResearchRepository  # noqa: E402


def context_from(prompt: str) -> dict:
    marker = "--- CANONICAL INPUT CONTEXT ---\n"
    return json.loads(prompt.split(marker, 1)[1].split("\n--- OUTPUT JSON SCHEMA ---", 1)[0])


def common(role: str) -> dict:
    schema = schema_for(role)
    value = {"summary": role, "used_sources": [], "questions": []}
    for key, shape in schema["properties"].items():
        if key in value:
            continue
        if shape.get("type") == "array": value[key] = []
        elif shape.get("type") == "boolean": value[key] = False
        elif "enum" in shape: value[key] = shape["enum"][0]
        else: value[key] = ""
    return value


class ScriptedRunner:
    def __init__(self, *, formal: bool = False, invalid_plan: str | None = None, fail_role: str | None = None):
        self.formal, self.invalid_plan, self.fail_role = formal, invalid_plan, fail_role
        self.prompts: list[tuple[str, str]] = []

    def run(self, *, prompt, output_schema, workspace, evidence_dir, model, effort, timeout_seconds, should_stop, on_started):
        role = next(name for name in ("research_preparation", "task_contract_review", "research_plan", "research_work", "identity_review", "goal_audit", "operational_review") if f"role: {name}." in prompt)
        self.prompts.append((role, prompt)); on_started({"pid": 1})
        if role == self.fail_role:
            return {"status": "failed", "output": None, "usage": {}, "error": "interrupted"}
        ctx, out = context_from(prompt), common(role)
        if role == "research_preparation":
            out["candidates"] = [{"revises_task_id": None, "title": "task", "question": "q", "scope": "s", "expected_result": "r",
                                  "completion_criteria": ["criterion"], "inputs": [], "work_class": "formal" if self.formal else "nonformal", "reuse": []}]
        elif role == "task_contract_review":
            out.update(decision="approved", findings=[])
        elif role == "research_plan":
            ready = [task["id"] for task in ctx["tasks"] if task["status"] == "ready"]
            assess = [task for task in ctx["tasks"] if task["status"] in {"assessing", "waiting"}]
            if self.invalid_plan == "missing": ready = []
            out.update(selections=ready, deferred=[], preparation_requests=[], goal_audit=bool(ctx["knowledge_catalog"]),
                       task_assessments=[{"task_id": task["id"], "decision": "completed", "reason": "done",
                                          "criteria_results": ([] if self.invalid_plan == "criterion" else [{"criterion": "criterion", "satisfied": True, "evidence": "e"}])} for task in assess])
        elif role == "research_work":
            out.update(outcome="submitted", report="work", remaining_work=[], checkpoint="cp", relations=[], knowledge=[{
                "kind": "theorem", "title": "T", "statement": "s", "explanation": "e", "summary": "sum",
                "lean_code": "theorem t : True := by trivial" if self.formal else "", "declaration_names": ["t"] if self.formal else [], "dependencies": []}])
        elif role == "identity_review":
            review = ctx["role_review"]
            stage = review["action"]["stage"]
            out = {"proposal_digest": review["proposal_digest"], "summary": "complete semantic match",
                   "used_sources": ["proposal"], "questions": []}
            if stage == "initial":
                out.update(decision="match", findings=[], scope_complete=True)
            elif stage == "organize":
                out["issues"] = []
            elif stage == "answer":
                out.update(answers=[], new_findings=[])
            elif stage == "judge":
                out.update(decision="match", scope_complete=True, issue_verdicts=[], new_findings=[])
        elif role == "goal_audit":
            out.update(decision="satisfied", reason="basis", scope_complete=True)
        elif role == "operational_review":
            out.update(decision="stop", reason="diagnostic stop")
        jsonschema.validate(out, output_schema)
        return {"status": "completed", "output": out, "usage": {"calls": 1}, "error": None}


def formal_ok(*, source, declarations, workspace, lean_command, timeout_seconds,
              allowed_axioms=(), should_stop=None):
    return {"status": "verified", "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "declarations": declarations, "axioms": {name: [] for name in declarations},
            "declaration_signatures": {name: f"{name} : True" for name in declarations},
            "signature_hash": hashlib.sha256("\n".join(declarations).encode()).hexdigest(),
            "allowed_axioms": list(allowed_axioms),
            "toolchain": {"executable": "test-lean", "sha256": "f" * 64,
                          "version": "Lean test 4.32.0", "version_exit": 0}}


def formal_fail(**_): return {"status": "failed", "reason": "mock formal failure; not Lean sorry evidence"}


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.repo = self.root / "repo"; self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)

    def tearDown(self): self.temp.cleanup()

    def make(self, runner, verifier=formal_ok, goal_kind="mathematical", **config):
        init = initialize(self.repo, goal="goal", goal_kind=goal_kind, workspace=self.root / "work", config={"reviewers": 2, "goal_auditors": 2, "max_cycles": 8, **config})
        return ResearchEngine(self.repo, init["instance_id"], runner=runner, formal_verifier=verifier), init["instance_id"]

    def test_nonformal_completion_then_goal_audit(self):
        runner = ScriptedRunner(); engine, _ = self.make(runner, goal_kind="research")
        status = engine.run(max_steps=20)
        self.assertEqual(status["goal_status"], "research_goal_satisfied")
        self.assertTrue(engine.check()["passed"])
        self.assertEqual(status["knowledge"]["K"], 0)

    def test_nonformal_mathematical_goal_is_not_solved(self):
        engine, _ = self.make(ScriptedRunner())
        status = engine.run(max_steps=20)
        self.assertNotEqual(status["goal_status"], "mathematically_solved")
        self.assertEqual(status["knowledge"]["K"], 0)

    def test_formal_requires_two_blind_reviews_and_failure_does_not_create_k(self):
        runner = ScriptedRunner(formal=True); engine, _ = self.make(runner)
        solved = engine.run(max_steps=30)
        reviews = [prompt for role, prompt in runner.prompts if role == "identity_review"]
        self.assertEqual(len(reviews), 2)
        self.assertTrue(all('"reviews"' not in prompt for prompt in reviews))
        self.assertEqual(solved["knowledge"]["K"], 1)
        verified = next(iter(engine.instance["knowledge"].values()))
        self.assertEqual(verified["formal"]["trust_environment_status"], "active")
        self.assertEqual(engine.instance["active_trust_environment"], verified["formal"]["trust_environment_id"])
        self.assertEqual(verified["formal"]["toolchain"]["sha256"], "f" * 64)
        failed_runner = ScriptedRunner(formal=True); failed, _ = self.make(failed_runner, formal_fail)
        self.assertEqual(failed.run(max_steps=20)["knowledge"]["K"], 0)

    def test_plan_rejects_missing_candidate_and_criterion(self):
        for invalid in ("missing", "criterion"):
            engine, _ = self.make(ScriptedRunner(invalid_plan=invalid))
            state = engine.run(max_steps=10)
            self.assertEqual(state["status"], "paused")
            self.assertTrue(state["questions"])

    def test_work_budget_pause_resume_preserves_queue(self):
        runner = ScriptedRunner(fail_role="research_work"); engine, instance = self.make(runner, work_calls=2, operations_calls=3)
        paused = engine.run(max_steps=10)
        self.assertEqual(paused["status"], "paused")
        before = ResearchRepository(self.repo, instance).load()[2]["queue"]
        self.assertTrue(before and before[0]["role"] == "research_work")
        control(self.repo, instance, "resume")
        resumed = engine.run(max_steps=1)
        after = ResearchRepository(self.repo, instance).load()[2]["queue"]
        self.assertEqual(before, after)
        self.assertIn(resumed["status"], {"paused", "budget_exhausted"})

    def test_work_budget_exhaustion_does_not_prevent_operations(self):
        runner = ScriptedRunner()
        engine, _ = self.make(runner, work_calls=1, operations_calls=10)
        engine.run(max_steps=3)
        self.assertEqual(engine.runtime["queue"][0]["role"], "research_work")
        blocked = dict(engine.runtime["queue"][0])
        before = engine.status()["budget"]
        self.assertEqual(before["work"]["used"], before["work"]["limit"])
        engine._enqueue("research_plan", reason="Assess next steps with the remaining operating budget")
        engine._save()
        status = engine.run(max_steps=1)
        self.assertEqual(runner.prompts[-1][0], "research_plan")
        self.assertEqual(status["budget"]["operations"]["used"], before["operations"]["used"] + 1)
        self.assertEqual(status["budget"]["work"]["used"], before["work"]["used"])
        self.assertEqual(engine.runtime["queue"][0], blocked)

    def test_crash_recovery_and_artifact_immutability(self):
        engine, instance = self.make(ScriptedRunner())
        action = {"role": "research_work", "target": "TK-crash"}
        engine.runtime["active_execution"] = "EX-crash"
        engine.runtime["activities"]["AY-crash"] = {"id": "AY-crash", "role": "research_work",
            "status": "active", "execution_ids": ["EX-crash"]}
        engine.runtime["executions"]["EX-crash"] = {"id": "EX-crash", "activity_id": "AY-crash",
            "role": "research_work", "status": "running", "action": action,
            "input_snapshot": engine.head, "parent_execution_id": None}
        engine.runtime["queue"].insert(0, action)
        engine._save()
        recovered = ResearchEngine(self.repo, instance, runner=ScriptedRunner()).run(max_steps=1)
        self.assertEqual(recovered["status"], "paused")
        _, _, runtime = ResearchRepository(self.repo, instance).load()
        self.assertEqual(runtime["executions"]["EX-crash"]["outcome"], "execution_incomplete")
        self.assertEqual(runtime["activities"]["AY-crash"]["status"], "unresolved")
        self.assertTrue(any(action.get("recovery", {}).get("execution_id") == "EX-crash"
                            for action in runtime["queue"]))
        engine, _ = self.make(ScriptedRunner())
        engine.run(max_steps=1)
        head, instance_data, runtime_data = ResearchRepository(self.repo, engine.instance["id"]).load()
        bundle = next(iter(runtime_data["executions"].values()))["artifact_bundle"]
        with self.assertRaises(ValueError):
            ResearchRepository(self.repo, engine.instance["id"]).save(head, instance_data, runtime_data, artifacts={f"runtime/artifacts/{bundle}/other.txt": b"mutate"})


if __name__ == "__main__": unittest.main(verbosity=2)
