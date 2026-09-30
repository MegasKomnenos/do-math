"""Scheduling: parallel calls stopped by a pause, live operational reviews beside running work, and regular supervision.

The module's other tests moved to the new system (tests/migration/dispositions/scheduling.1.json).
These stay until the Sim can run them: a pause stopping running calls and a live review
fed by a running call's observation ticks need a Jobs fake whose worker keeps running while
the runner polls, and regular supervision needs scheduled_operator.check to take the Ports."""
from __future__ import annotations

import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control, ResearchEngine
from do_math.model_policy import MODELS
from do_math.planning import seal_contract_review
from do_math.system_clock import new_id
from engine_fixtures import initialized_instance
from research_fixtures import (candidate, contract_review, install_adapter_fixture, local_job_runner, observation_batch,
                               producer_result, restore_template)
from runner_fixtures import common, context_from, ScriptedRunner


def ready_work(root, shared, *, count, public, config):
    """``restore_template`` build: ``count`` ready tasks whose work a real plan selected and queued.

    By default: validated active state, a real preparation and sealed contract
    approvals, since public activation and contract review have their own tests.
    public=True keeps public activation and real reviews for tests whose outcome
    depends on that state: check() of synthetic initialization executions
    reports an unexamined role input, and activation leaves queue events.
    The plan consumes the readiness events; work queued without it would leave
    them pending, and the engine would schedule another plan for them. With
    count=0 the queue is left as activation left it. Returns the instance ID.
    """
    from research_fixtures import FixtureAdapter, activated_instance
    from state_fixtures import ACTIVE_LEAN_COMMAND, active_instance
    base = {"operator_enabled": False, "scholarly_enabled": False}
    if public:
        instance_id = activated_instance(root, shared, goal="bounded research",
                                         config={**base, "lean_command": ["test-lean"], **config})
    else:
        instance_id = active_instance(root, shared, config={**base, "lean_command": list(ACTIVE_LEAN_COMMAND), **config})
    if not count:
        return instance_id
    engine = ResearchEngine(root / "repository", instance_id, runner=ScriptedRunner(
        preparation_candidates=[candidate(str(i)) for i in range(count)],
        model_rating={"difficulty": "high", "importance": "medium", "reason": "Independent novel fixture approaches"}))
    with patch("do_math.local_host.adapter_for", return_value=FixtureAdapter()):
        engine.run(max_steps=1)
        if public:
            engine.run(max_steps=count)
        else:
            # Seal the approval the review role returns; the engine judges readiness.
            for task in engine.runtime["tasks"].values():
                task["reviews"].append(seal_contract_review(task, contract_review({"task": task}),
                    engine.instance, engine.runtime, execution_id=new_id("EX")))
            engine._refresh_readiness()
        if len(engine.runtime["tasks"]) != count:
            raise AssertionError(engine.runtime["tasks"])
        if not all(row["state"] == "ready" for row in engine._task_readiness.values()):
            raise AssertionError(engine._task_readiness)
        # The sealed approvals answer the queued reviews; the plan then selects every ready task.
        engine.runtime["queue"] = [a for a in engine.runtime["queue"] if a["role"] != "task_contract_review"]
        engine._save()
        engine.run(max_steps=1)
    queued = sorted((a["role"], a["target"]) for a in engine.runtime["queue"])
    if queued != sorted(("research_work", tid) for tid in engine.runtime["tasks"]):
        raise AssertionError(queued)
    if engine.runtime["pending_events"] != []:
        raise AssertionError(engine.runtime["pending_events"])
    return instance_id


class ConcurrentRunner:
    def __init__(self, expected=3, release=None):
        self.expected = expected
        self.release = release or threading.Event()
        self.lock = threading.Lock()
        self.active = 0
        self.peak = 0
        self.models = []
        self.workspaces = []
        self.started = threading.Condition(self.lock)
        self.started_count = 0

    @local_job_runner
    def run(self, *, prompt, workspace, model, on_started, should_stop, **kwargs):
        ctx = context_from(prompt, workspace)
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            self.models.append(model)
            self.workspaces.append(workspace)
            if self.active == self.expected:
                self.release.set()
        try:
            on_started()
            with self.started:
                self.started_count += 1
                self.started.notify_all()
            deadline = time.monotonic() + 120
            while not self.release.wait(.01):
                if should_stop():
                    return {"status": "stopped", "output": None, "usage": {}, "error": "stopped"}
                if time.monotonic() > deadline:
                    raise AssertionError("independent model calls did not overlap")
            (workspace / "same-name.txt").write_text(ctx["action"]["target"], encoding="utf-8")
            out = common("research_work")
            out.update(outcome="submitted", report="Completed the assigned bounded task.", checkpoint="done")
            return producer_result({"status": "completed", "output": out, "usage": {}, "error": None}, {**kwargs, 'prompt': prompt, 'workspace': workspace, 'model': model, 'on_started': on_started, 'should_stop': should_stop})
        finally:
            with self.lock:
                self.active -= 1


class SlotTests(unittest.TestCase):
    """The Git writer owns admission; observers never reconcile reservations."""
    def setUp(self):
        limits = {'work': {model: 1 for model in MODELS.values()}}
        self.root, instance_id = restore_template(initialized_instance, goal='Reservation boundary fixture',
            config={'operator_enabled': True, 'scholarly_enabled': False, 'session_limits': limits})
        self.repo, self.workspace = self.root / 'repository', self.root / 'work-0'
        self.engine = ResearchEngine(self.repo, instance_id, runner=ScriptedRunner())


    def test_regular_supervision_observes_without_creating_an_ai_execution(self):
        from do_math import scheduled_operator
        with patch.object(scheduled_operator, 'ModelRunner', side_effect=AssertionError('unexpected model')):
            outcome = scheduled_operator.check(self.repo, self.engine.instance['id'], self.workspace, probe=True)
        self.assertEqual(outcome['outcome'], 'observed')
        self.assertFalse(outcome['model_called'])
        self.assertEqual(self.engine.store.load()[2]['executions'], {})


class ParallelEngineTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)

    def engine(self, runner, count=3, *, public=False, **config):
        """A copy of ``ready_work``'s state (see there) with ``runner``; ``config`` includes limits."""
        self.root, instance_id = restore_template(ready_work, count=count, public=public, config=config)
        self.repo = self.root / "repository"
        return ResearchEngine(self.repo, instance_id, runner=runner)


    def test_pause_reaches_all_parallel_calls_and_releases_their_slots(self):
        runner = ConcurrentRunner(expected=99)
        engine = self.engine(runner)
        def pause_when_started():
            with runner.started:
                if not runner.started.wait_for(lambda: runner.started_count == 3, timeout=120):
                    return
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
        self.assertEqual(state["budget"][MODELS["high"]]["used"], 0)
        self.assertEqual(len([e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]), 3)

    def test_live_operations_can_run_when_work_is_full_and_step_limit_is_reached(self):
        release = threading.Event()
        class ObservedRunner(ConcurrentRunner):
            @local_job_runner
            def run(inner, *, prompt, workspace, model, on_started, should_stop, on_observation=None, **kwargs):
                context = context_from(prompt, workspace)
                if context["action"]["role"] == "operational_review":
                    on_started()
                    out = common("operational_review")
                    out["disposition"] = {"kind": "continue", "basis_refs": [context["action"]["target"]],
                        "next_owner": "research_work", "reason": "The running target supplied progress evidence", "next_review": None}
                    # Submit while the target still runs, then release it; releasing first lets
                    # the target end and the engine reject the review as obsolete.
                    result = producer_result({"status": "completed", "output": out, "usage": {}, "error": None}, {**kwargs, 'prompt': prompt, 'workspace': workspace, 'model': model, 'on_started': on_started, 'should_stop': should_stop, 'on_observation': on_observation})
                    release.set()
                    return result
                with inner.lock:
                    inner.active += 1; inner.peak = max(inner.peak, inner.active)
                try:
                    on_started()
                    # A hang guard, as ConcurrentRunner's: dispatching the full pool can take tens of seconds under load.
                    deadline = time.monotonic() + 120
                    last_tick = None
                    while not release.is_set():
                        # The real runner's idle cadence (model_runner.observe): one empty batch per second.
                        if last_tick is None or time.monotonic() - last_tick >= 1:
                            on_observation(observation_batch(received_monotonic=time.monotonic(),
                                stream_path=Path(kwargs["evidence_dir"]) / "stdout.jsonl"))
                            last_tick = time.monotonic()
                        if should_stop():
                            return {"status": "stopped", "output": None, "usage": {}, "error": "stopped"}
                        if time.monotonic() > deadline:
                            raise AssertionError("operating slot could not run beside the full work pool")
                        time.sleep(.1)
                    out = common("research_work")
                    out.update(outcome="submitted", report="work completed", checkpoint="done")
                    return producer_result({"status": "completed", "output": out, "usage": {}, "error": None}, {**kwargs, 'prompt': prompt, 'workspace': workspace, 'model': model, 'on_started': on_started, 'should_stop': should_stop, 'on_observation': on_observation})
                finally:
                    with inner.lock: inner.active -= 1
        runner = ObservedRunner(expected=99)
        # Its outcome differs from the active-state start; keep the public state.
        engine = self.engine(runner, public=True, observation_mode="periodic", observation_interval_seconds=1)
        engine.run(max_steps=3)
        operating = [e for e in engine.runtime["executions"].values() if e["role"] == "operational_review"]
        self.assertTrue(operating)
        self.assertFalse([row for row in engine.runtime["reservations"].values()
                          if row["owner_id"] == operating[0]["id"] and row["unit"] == "execution"],
                         "an operational role runs beside full work slots without holding one")
        self.assertEqual(operating[0]["model"], MODELS["high"])
        # A result collected after its target ended is preserved, not applied (engine result_disposition).
        if operating[0].get("result_disposition", {}).get("kind") == "preserved_after_target_change":
            self.assertEqual(engine.runtime['executions'][operating[0]['action']['target']]['status'], 'ended')
        else:
            self.assertEqual(operating[0]["outcome"], "output_accepted")

    def test_failed_live_review_stops_its_parent_and_preserves_independent_work(self):
        review_failed = threading.Event()
        class Runner:
            @local_job_runner
            def run(inner, *, prompt, on_started, should_stop, on_observation=None, **kwargs):
                ctx = context_from(prompt, kwargs['workspace'])
                on_started()
                if ctx["action"]["role"] == "operational_review":
                    review_failed.set()
                    return {"status": "failed", "output": None, "usage": {}, "error": "operating model unavailable"}
                started = time.monotonic()
                while time.monotonic() - started < 20:
                    if ctx["task"]["title"] == "0":
                        # An empty runner batch is the idle tick.
                        on_observation(observation_batch(received_monotonic=time.monotonic(),
                            stream_path=Path(kwargs["evidence_dir"]) / "stdout.jsonl"))
                    elif review_failed.is_set():
                        # The independent work returns after the parent's review failed.
                        out = common("research_work")
                        out.update(outcome="submitted", report="independent work finished", checkpoint="done")
                        return producer_result({"status": "completed", "output": out, "usage": {}, "error": None}, {**kwargs, 'prompt': prompt, 'on_started': on_started, 'should_stop': should_stop, 'on_observation': on_observation, 'workspace': kwargs['workspace']})
                    if should_stop():
                        return {"status": "stopped", "output": None, "usage": {}, "error": "parent stopped"}
                    time.sleep(.1)
                raise AssertionError("failed live review did not stop its parent")
        engine = self.engine(Runner(), count=2, observation_mode="periodic", observation_interval_seconds=1)
        state = engine.run(max_steps=2)
        work = [e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertEqual(sum(e["outcome"] == "output_accepted" for e in work), 1)
        self.assertNotEqual(state["status"], "paused")


if __name__ == "__main__":
    unittest.main(verbosity=2)
