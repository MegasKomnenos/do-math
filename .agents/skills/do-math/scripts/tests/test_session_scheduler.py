from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import os
import uuid
import inspect
import json
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, initialize, control, DEFAULT_CONFIG
from do_math.model_policy import LIMITS, MODELS, assessment_tier, selection, validate_policy
from do_math.planning import contract_hash
from do_math.input_basis import capture_decision_basis
from do_math.repository import new_id
from do_math.session_slots import SessionSlots
from test_engine import ScriptedRunner, common, context_from


class ConcurrentRunner:
    def __init__(self, expected=3, release=None):
        self.expected = expected
        self.release = release or threading.Event()
        self.lock = threading.Lock()
        self.active = 0
        self.peak = 0
        self.models = []
        self.workspaces = []

    def run(self, *, prompt, workspace, model, on_started, should_stop, **kwargs):
        ctx = context_from(prompt)
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            self.models.append(model)
            self.workspaces.append(workspace)
            if self.active == self.expected:
                self.release.set()
        try:
            on_started({"pid": 1})
            deadline = time.monotonic() + 8
            while not self.release.wait(.01):
                if should_stop():
                    return {"status": "stopped", "output": None, "usage": {}, "error": "stopped"}
                if time.monotonic() > deadline:
                    raise AssertionError("independent model calls did not overlap")
            (workspace / "same-name.txt").write_text(ctx["action"]["target"], encoding="utf-8")
            out = common("research_work")
            out.update(outcome="submitted", report="Completed the assigned bounded task.", checkpoint="done")
            return {"status": "completed", "output": out, "usage": {}, "error": None}
        finally:
            with self.lock:
                self.active -= 1


class SessionPolicyTests(unittest.TestCase):
    def test_defaults_and_max_of_difficulty_and_importance(self):
        self.assertEqual(MODELS, {"high": "gpt-6-astra", "medium": "gpt-5.6-sol", "low": "gpt-5.6-terra"})
        per_model = {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3}
        self.assertEqual(LIMITS, {"work": per_model, "operations": per_model})
        self.assertEqual((DEFAULT_CONFIG["tier_models"], DEFAULT_CONFIG["session_limits"]), (MODELS, LIMITS))
        self.assertEqual(assessment_tier({"difficulty": "low", "importance": "high", "reason": "goal-wide impact"}), "high")
        config = deepcopy(DEFAULT_CONFIG)
        config["session_limits"]["work"][MODELS["high"]] = 0
        selected = selection(config, {"role": "research_work", "model_assessment": {
            "difficulty": "high", "importance": "medium", "reason": "new proof approach"}}, {}, {})
        self.assertEqual(selected["model"], MODELS["high"])

    def test_model_names_extend_without_closed_catalogue(self):
        config = deepcopy(DEFAULT_CONFIG)
        config["tier_models"]["high"] = "configured-future-model"
        for pool in config["session_limits"].values():
            pool["configured-future-model"] = 2
        validate_policy(config)

    def test_bad_capacity_and_missing_tier_model_are_rejected(self):
        for value in (-1, True, None, 1.5):
            config = deepcopy(DEFAULT_CONFIG)
            config["session_limits"]["work"][MODELS["high"]] = value
            with self.assertRaises(ValueError): validate_policy(config)

    def test_role_floor_raises_low_assessment_and_unassessed_work_uses_high(self):
        config = deepcopy(DEFAULT_CONFIG)
        low = {"difficulty": "low", "importance": "low", "reason": "bounded local comparison"}
        review = selection(config, {"role": "task_contract_review", "model_assessment": low}, {}, {})
        self.assertEqual((review["tier"], review["model"]), ("medium", MODELS["medium"]))
        unassessed = selection(config, {"role": "research_work"}, {}, {})
        self.assertEqual((unassessed["tier"], unassessed["model"]), ("high", MODELS["high"]))


class SlotTests(unittest.TestCase):
    def test_independent_operator_uses_the_same_instance_operating_slot(self):
        from do_math import scheduled_operator
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            slots = SessionSlots(workspace, "instance")
            slots.configure(deepcopy(LIMITS))
            capacity = LIMITS["operations"][MODELS["high"]]
            for number in range(capacity):
                self.assertTrue(slots.acquire(f"internal-plan-{number}", "operations", MODELS["high"]))
            config = deepcopy(DEFAULT_CONFIG); config["scholarly_enabled"] = False
            class Runner:
                def run(inner, *, model, on_started, **kwargs):
                    self.assertEqual(model, MODELS["high"])
                    self.assertEqual(slots.snapshot()["operations"][model]["used"], capacity)
                    on_started({"pid": 1})
                    return {"status": "completed", "output": {}, "usage": {}}
            try:
                with patch.object(scheduled_operator, "read_status", return_value={"status": "ready", "user_pause": None}), \
                     patch.object(scheduled_operator, "ResearchRepository") as repository, \
                     patch.object(scheduled_operator, "ModelRunner", return_value=Runner()) as runner:
                    repository.return_value.load.return_value = ("snapshot", {"config": config}, {})
                    waiting = scheduled_operator.check(workspace, "instance", workspace)
                    self.assertEqual(waiting["outcome"], "capacity_waiting")
                    runner.assert_not_called()
                    slots.release("internal-plan-0")
                    result = scheduled_operator.check(workspace, "instance", workspace)
                    self.assertEqual(result["outcome"], "completed")
                    self.assertEqual(slots.snapshot()["operations"][MODELS["high"]]["used"], capacity - 1)
            finally:
                slots.close()

    def test_independent_operator_prompt_carries_the_saved_context_compactly(self):
        import json
        from do_math import scheduled_operator
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            slots = SessionSlots(workspace, "instance")
            slots.configure(deepcopy(LIMITS))
            config = deepcopy(DEFAULT_CONFIG); config["scholarly_enabled"] = False
            class Runner:
                def run(inner, *, on_started, **kwargs):
                    on_started({"pid": 1})
                    return {"status": "completed", "output": {}, "usage": {}}
            try:
                with patch.object(scheduled_operator, "read_status", return_value={"status": "ready", "user_pause": None}), \
                     patch.object(scheduled_operator, "ResearchRepository") as repository, \
                     patch.object(scheduled_operator, "ModelRunner", return_value=Runner()):
                    repository.return_value.load.return_value = ("snapshot", {"config": config}, {})
                    scheduled_operator.check(workspace, "instance", workspace)
            finally:
                slots.close()
            prompt, = workspace.rglob("prompt.md")
            carried = prompt.read_text(encoding="utf-8").split("\n\n## Invocation context\n\n", 1)[1]
            saved = json.loads((prompt.parent / "context.json").read_text(encoding="utf-8"))
            self.assertEqual(json.loads(carried), saved)
            self.assertNotIn("\n", carried)

    def test_two_processes_share_the_same_capacity(self):
        with tempfile.TemporaryDirectory() as directory:
            slots = SessionSlots(Path(directory), "one")
            slots.configure({"work": {"model": 1}, "operations": {"model": 1}})
            program = "\n".join([
                "import sys", "from pathlib import Path",
                "sys.path.insert(0, sys.argv[1])",
                "from do_math.session_slots import SessionSlots",
                "s=SessionSlots(Path(sys.argv[2]), 'one')",
                "print(s.acquire('child', 'work', 'model'), flush=True)",
                "sys.stdin.readline()", "s.release('child'); s.close()",
            ])
            child = subprocess.Popen([sys.executable, "-c", program, str(Path(__file__).resolve().parents[1]), directory],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                self.assertEqual(child.stdout.readline().strip(), "True")
                self.assertFalse(slots.acquire("parent", "work", "model"))
                child.communicate("release\n", timeout=10)
                self.assertEqual(child.returncode, 0)
                self.assertTrue(slots.acquire("parent", "work", "model"))
                slots.release("parent")
            finally:
                if child.poll() is None:
                    child.kill(); child.communicate(timeout=10)
                slots.close()

    @unittest.skipUnless(os.name == "nt", "requires a Windows Job")
    def test_slot_waits_for_actual_named_job_termination(self):
        from do_math.windows_job import WindowsJob, named_job_empty
        with tempfile.TemporaryDirectory() as directory:
            slots = SessionSlots(Path(directory), "one")
            slots.configure({"work": {"model": 1}, "operations": {"model": 1}})
            name = "Local\\DoMath-test-" + uuid.uuid4().hex
            try:
                with WindowsJob([sys.executable, "-c", "import time; time.sleep(30)"], name=name) as job:
                    self.assertTrue(slots.acquire("session", "work", "model"))
                    slots.started("session", {"pid": job.pid, "job_name": name})
                    job.resume()
                    self.assertFalse(named_job_empty(name))
                    self.assertFalse(slots.release("session"))
                    self.assertFalse(slots.acquire("next", "work", "model"))
                    job.terminate()
                    self.assertTrue(job.wait(10))
                    deadline = time.monotonic() + 10
                    while not named_job_empty(name) and time.monotonic() < deadline:
                        time.sleep(.01)
                    self.assertTrue(slots.release("session"))
                    self.assertTrue(slots.acquire("next", "work", "model"))
                    slots.release("next")
            finally:
                slots.close()

    def test_shared_capacity_separate_pools_and_instances_and_reusable_slots(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = SessionSlots(Path(directory), "one"), SessionSlots(Path(directory), "one")
            other = SessionSlots(Path(directory), "two")
            try:
                a.configure({"work": {"model": 1}, "operations": {"model": 1}})
                other.configure({"work": {"model": 1}, "operations": {"model": 1}})
                self.assertTrue(a.acquire("work-1", "work", "model"))
                self.assertFalse(b.acquire("work-2", "work", "model"))
                self.assertTrue(b.acquire("op-1", "operations", "model"))
                self.assertTrue(other.acquire("other", "work", "model"))
                a.release("work-1")
                self.assertTrue(b.acquire("work-2", "work", "model"))
                a.configure({"work": {"model": 0}, "operations": {"model": 1}})
                self.assertEqual(a.snapshot()["work"]["model"]["used"], 1)
                self.assertFalse(a.acquire("work-3", "work", "model"))
                b.release("work-2"); b.release("op-1"); other.release("other")
            finally:
                a.close(); b.close(); other.close()

    def test_lost_owner_before_start_is_reconciled_but_unknown_started_lifetime_is_held(self):
        with tempfile.TemporaryDirectory() as directory:
            a = SessionSlots(Path(directory), "one")
            a.configure({"work": {"model": 2}, "operations": {"model": 1}})
            a.acquire("before-start", "work", "model")
            a.acquire("started", "work", "model")
            a.started("started", {"pid": 100})
            a.close()
            b = SessionSlots(Path(directory), "one")
            try:
                self.assertEqual(b.snapshot()["work"]["model"]["execution_ids"], ["started"])
            finally:
                b.close()


class ParallelEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"; self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def engine(self, runner, count=3, **config):
        result = initialize(self.repo, goal="bounded research", goal_kind="research", workspace=self.root / "work",
                            config={"operator_enabled": False, "scholarly_enabled": False, **config})
        engine = ResearchEngine(self.repo, result["instance_id"], runner=runner)
        engine.runtime["queue"] = []
        for i in range(count):
            tid = new_id("TK")
            task = {"id": tid, "revision": 1, "status": "performing", "title": str(i), "question": "q",
                    "scope": "bounded", "expected_result": "report", "completion_criteria": ["report"],
                    "inputs": [], "reuse": [], "dependencies": [], "work_class": "nonformal", "results": [],
                    "model_assessment": {"difficulty": "high", "importance": "medium", "reason": "novel approach"},
                    "occurrence_condition": {"op": "always"}, "initial_observation_rules": [], "feature_version": 2}
            task["reviews"] = [{"id": new_id("CR"), "revision": 1, "decision": "approved", "contract_sha256": contract_hash(task),
                                "goal_revision": engine.instance["goal_revision"], "policy_revision": engine.instance["policy_revision"]}]
            engine.runtime["tasks"][tid] = task
            task["reviews"][0]["decision_basis"] = capture_decision_basis(engine.instance, engine.runtime, [tid])
            engine._enqueue("research_work", tid)
        engine._save()
        return engine

    def test_three_calls_overlap_and_apply_serially_to_distinct_workspaces(self):
        runner = ConcurrentRunner()
        engine = self.engine(runner)
        main = threading.get_ident()
        save = engine._save
        def checked_save(*args, **kwargs):
            self.assertEqual(threading.get_ident(), main)
            return save(*args, **kwargs)
        engine._save = checked_save
        state = engine.run(max_steps=3)
        self.assertEqual(runner.peak, 3)
        self.assertEqual(len(set(runner.workspaces)), 3)
        self.assertEqual(runner.models, [MODELS["high"]] * 3)
        self.assertEqual(len({(p / "same-name.txt").read_text(encoding="utf-8") for p in runner.workspaces}), 3)
        self.assertEqual(len([e for e in engine.runtime["executions"].values() if e["outcome"] == "output_accepted"]), 3)
        self.assertEqual(state["budget"]["work"][MODELS["high"]]["used"], 0)
        self.assertTrue(engine.check()["passed"], engine.check())

    def test_unavailable_assigned_model_waits_without_spending_other_model_slots(self):
        limits = deepcopy(LIMITS); limits["work"][MODELS["high"]] = 0
        runner = ConcurrentRunner(expected=1)
        engine = self.engine(runner, count=1, session_limits=limits)
        state = engine.run(max_steps=1)
        self.assertEqual(state["status"], "capacity_waiting")
        self.assertEqual(runner.models, [])
        self.assertEqual(state["capacity_waiting"][0]["model_selection"]["model"], MODELS["high"])
        limits["work"][MODELS["high"]] = 1
        control(self.repo, engine.instance["id"], "configure", config={"session_limits": limits})
        engine.run(max_steps=1)
        self.assertEqual(runner.models, [MODELS["high"]])

    def test_blocked_high_priority_work_does_not_block_independent_low_model_work(self):
        limits = deepcopy(LIMITS); limits["work"][MODELS["high"]] = 0
        runner = ConcurrentRunner(expected=1)
        engine = self.engine(runner, count=2, session_limits=limits)
        high = engine.runtime["queue"][0]["target"]
        task = engine.runtime["tasks"][engine.runtime["queue"][1]["target"]]
        task["model_assessment"] = {"difficulty": "low", "importance": "low", "reason": "bounded local transcription"}
        task["reviews"][0]["contract_sha256"] = contract_hash(task)
        task["reviews"][0]["decision_basis"] = capture_decision_basis(engine.instance, engine.runtime, [task["id"]])
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual(runner.models, [MODELS["low"]])
        self.assertTrue(any(a.get("target") == high for a in engine.runtime["queue"]))

    def test_legacy_budget_transition_preserves_history_and_changes_units(self):
        runner = ConcurrentRunner(expected=1)
        engine = self.engine(runner, count=0, work_calls=4, operations_calls=3)
        self.assertIsNone(engine.instance["config"]["session_limits"])
        before = deepcopy(engine.runtime["executions"])
        control(self.repo, engine.instance["id"], "configure", config={"session_limits": deepcopy(LIMITS)})
        state = engine.process_controls()
        self.assertEqual(state["budget_unit"], "concurrent_sessions")
        self.assertEqual(engine.runtime["executions"], before)
        self.assertEqual(engine.instance["feature_version"], 4)

    def test_pause_reaches_all_parallel_calls_and_releases_their_slots(self):
        runner = ConcurrentRunner(expected=99)
        engine = self.engine(runner, checkpoint_grace_seconds=1)
        def pause_when_started():
            deadline = time.monotonic() + 15
            while runner.active < 3 and time.monotonic() < deadline:
                time.sleep(.01)
            control(self.repo, engine.instance["id"], "pause", text="pause the whole instance")
        controller = threading.Thread(target=pause_when_started)
        controller.start()
        try:
            state = engine.run(max_steps=3)
        finally:
            controller.join(20)
        self.assertFalse(controller.is_alive())
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["active_executions"], [])
        self.assertEqual(state["budget"]["work"][MODELS["high"]]["used"], 0)
        self.assertEqual(len(engine.runtime["executions"]), 3)

    def test_live_operations_can_run_when_work_is_full_and_step_limit_is_reached(self):
        release = threading.Event()
        class ObservedRunner(ConcurrentRunner):
            def run(inner, *, prompt, workspace, model, on_started, should_stop, on_observation=None, **kwargs):
                context = context_from(prompt)
                if context["action"]["role"] == "operational_review":
                    on_started({"pid": 1})
                    out = common("operational_review")
                    out.update(decision="continue", reason="progress is supported by current evidence")
                    release.set()
                    return {"status": "completed", "output": out, "usage": {}, "error": None}
                with inner.lock:
                    inner.active += 1; inner.peak = max(inner.peak, inner.active)
                try:
                    on_started({"pid": 1})
                    deadline = time.monotonic() + 20
                    while not release.is_set():
                        on_observation({"type": "tick"})
                        if should_stop():
                            return {"status": "stopped", "output": None, "usage": {}, "error": "stopped"}
                        if time.monotonic() > deadline:
                            raise AssertionError("operating slot could not run beside the full work pool")
                        time.sleep(.1)
                    out = common("research_work")
                    out.update(outcome="submitted", report="work completed", checkpoint="done")
                    return {"status": "completed", "output": out, "usage": {}, "error": None}
                finally:
                    with inner.lock: inner.active -= 1
        runner = ObservedRunner(expected=99)
        engine = self.engine(runner, observation_mode="periodic", observation_interval_seconds=1)
        engine.run(max_steps=3)
        operating = [e for e in engine.runtime["executions"].values() if e["role"] == "operational_review"]
        self.assertTrue(operating)
        self.assertEqual(operating[0]["budget_kind"], "operations")
        self.assertEqual(operating[0]["model"], MODELS["high"])
        self.assertIn(operating[0]["outcome"], {"output_accepted", "output_preserved_after_target_change"})
        if operating[0]['outcome'] == 'output_preserved_after_target_change':
            self.assertEqual(engine.runtime['executions'][operating[0]['action']['target']]['status'], 'ended')

    def test_planner_queue_order_cancels_only_unstarted_requests_and_preserves_obligations(self):
        engine = self.engine(ConcurrentRunner(), count=3)
        first, second, third = deepcopy(engine.runtime["queue"])
        eid = "EX-plan"
        engine.runtime["executions"][eid] = {"input_snapshot": engine.head, "status": "ended", "extensions": {
            "queued_requests": [{"request_id": third["id"], "decision": "keep", "reason": "opens the next proof question"},
                                {"request_id": first["id"], "decision": "keep", "reason": "follow after third"},
                                {"request_id": second["id"], "decision": "cancel", "reason": "defer this approach"}]}}
        engine._apply_queue_plan({"role": "research_plan"}, eid)
        self.assertEqual([a["id"] for a in engine.runtime["queue"]], [third["id"], first["id"]])
        task = engine.runtime["tasks"][second["target"]]
        self.assertEqual(task["status"], "ready")
        self.assertEqual(task["completion_criteria"], ["report"])

    def test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution(self):
        assessment = {"difficulty": "low", "importance": "low", "reason": "a local bounded comparison with an explicit method"}
        class AssessedRunner(ScriptedRunner):
            def run(inner, **arguments):
                allowed = inspect.signature(ScriptedRunner.run).parameters
                result = super().run(**{k: v for k, v in arguments.items() if k in allowed})
                context = context_from(arguments["prompt"])
                role = context["action"]["role"]
                entries = []
                if role == "research_preparation":
                    entries = [{"task_title": c["title"], **assessment} for c in result["output"]["candidates"]]
                elif role == "research_plan":
                    entries = [{"task_id": tid, **assessment} for tid in result["output"]["selections"]]
                if entries:
                    from test_engine import contract_checks
                    checks = contract_checks(result["output"]["candidates"]) if role == "research_preparation" else []
                    (arguments["workspace"] / "activity-extensions.json").write_text(
                        json.dumps({"model_assessments": entries, **({"contract_checks": checks} if checks else {})}), encoding="utf-8")
                return result
        result = initialize(self.repo, goal="bounded research", goal_kind="research", workspace=self.root / "work",
                            config={"operator_enabled": False, "scholarly_enabled": False})
        engine = ResearchEngine(self.repo, result["instance_id"], runner=AssessedRunner())
        engine.run(max_steps=12)
        tasks = list(engine.runtime["tasks"].values())
        self.assertEqual(tasks[0]["model_assessment"], assessment)
        work = [e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertTrue(work)
        self.assertEqual(work[0]["model"], MODELS["low"])
        self.assertEqual(work[0]["model_selection"]["assessment"], assessment)
        self.assertTrue(engine.check()["passed"], engine.check())

    def test_failed_work_waits_for_diagnosis_when_its_operating_model_is_full(self):
        class FailingRunner:
            def __init__(inner): inner.calls = 0
            def run(inner, *, on_started, **kwargs):
                inner.calls += 1
                on_started({"pid": 1})
                return {"status": "failed", "output": None, "usage": {}, "error": "preserved tool failure"}
        limits = deepcopy(LIMITS); limits["operations"][MODELS["high"]] = 0
        runner = FailingRunner()
        engine = self.engine(runner, count=1, session_limits=limits)
        state = engine.run(max_steps=3)
        self.assertEqual(runner.calls, 1)
        self.assertEqual(state["status"], "capacity_waiting")
        self.assertEqual(engine.runtime["queue"][0]["role"], "operational_review")
        self.assertTrue(any(row.get("kind") == "execution_failure" for row in engine.runtime["waiting_actions"].values()))

    def test_failed_live_review_stops_its_parent_and_preserves_independent_work(self):
        class Runner:
            def run(inner, *, prompt, on_started, should_stop, on_observation=None, **kwargs):
                ctx = context_from(prompt)
                on_started({"pid": 1})
                if ctx["action"]["role"] == "operational_review":
                    return {"status": "failed", "output": None, "usage": {}, "error": "operating model unavailable"}
                started = time.monotonic()
                while time.monotonic() - started < 20:
                    if ctx["task"]["title"] == "0":
                        on_observation({"type": "tick"})
                    elif time.monotonic() - started > 2:
                        out = common("research_work")
                        out.update(outcome="submitted", report="independent work finished", checkpoint="done")
                        return {"status": "completed", "output": out, "usage": {}, "error": None}
                    if should_stop():
                        return {"status": "stopped", "output": None, "usage": {}, "error": "parent stopped"}
                    time.sleep(.1)
                raise AssertionError("failed live review did not stop its parent")
        engine = self.engine(Runner(), count=2, observation_mode="periodic", observation_interval_seconds=1,
                             checkpoint_grace_seconds=1)
        state = engine.run(max_steps=2)
        work = [e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertEqual(sum(e["outcome"] == "output_accepted" for e in work), 1)
        self.assertNotEqual(state["status"], "paused")

    def test_user_requests_and_intent_join_existing_operating_queue_in_order(self):
        engine = self.engine(ConcurrentRunner(), count=0)
        engine._enqueue("maintenance", reason="older operating request")
        engine._save()
        control(self.repo, engine.instance["id"], "request", config={"role": "research_preparation"}, text="new preparation request")
        control(self.repo, engine.instance["id"], "input", text="new information to interpret")
        engine.process_controls()
        self.assertEqual([a["role"] for a in engine.runtime["queue"]],
                         ["maintenance", "research_preparation", "intent_interpretation"])

    def test_output_repair_keeps_the_original_operating_queue_position(self):
        class InvalidPreparation:
            def __init__(inner):
                inner.roles = []
            def run(inner, *, prompt, on_started, **kwargs):
                inner.roles.append(context_from(prompt)["action"]["role"])
                on_started({"pid": 1})
                out = common("research_preparation")
                out.pop("candidates")
                return {"status": "completed", "output": out, "usage": {}, "error": None}
        limits = deepcopy(LIMITS); limits["operations"][MODELS["medium"]] = 0
        runner = InvalidPreparation()
        engine = self.engine(runner, count=0, session_limits=limits)
        engine.runtime["queue"] = [{"id": "AC-older", "role": "maintenance", "reason": "older operating request"},
                                   {"id": "AC-preparation", "role": "research_preparation", "reason": "newer operating request"}]
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual(runner.roles, ["research_preparation"])
        self.assertEqual([a["id"] for a in engine.runtime["queue"]], ["AC-older", "AC-preparation"])
        self.assertEqual(engine.runtime["queue"][1]["repair_attempt"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
