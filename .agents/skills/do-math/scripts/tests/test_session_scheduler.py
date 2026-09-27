from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
import os
import uuid
import inspect
import json
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, initialize, control, DEFAULT_CONFIG
from do_math.model_policy import LIMITS, MODELS, assessment_tier, selection, validate_policy
from do_math.planning import contract_hash, seal_contract_review
from do_math.input_basis import capture_decision_basis
from do_math.repository import new_id
from do_math.session_slots import SessionSlots
from test_engine import ScriptedRunner, common, context_from
from research_fixtures import local_job_runner, restore_template
from research_fixtures import install_adapter_fixture, candidate, contract_review, producer_result
from test_lifecycle_engine import initialized_instance


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
    with patch("do_math.initialization.adapter_for", return_value=FixtureAdapter()):
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


class SessionPolicyTests(unittest.TestCase):
    def test_old_profile_cannot_bypass_a_new_zero_capacity_limit(self):
        from do_math.execution_profiles import apply_editions, build_profiles
        from do_math.session_slots import SessionSlots

        config = deepcopy(DEFAULT_CONFIG)
        instance = {"config": config, **build_profiles(config)}
        runtime = {"executions": {}, "reservations": {}, "provider_waits": {}}
        old = next(profile for profile in instance["execution_profiles"].values()
                   if profile["role"] == "research_work" and profile["ai"].get("tier") == "high")
        slots = SessionSlots(runtime, instance)

        lower = deepcopy(config["session_limits"])
        lower["work"][MODELS["high"]] = 0
        config["session_limits"] = lower
        apply_editions(instance, build_profiles(config))
        execution = {"id": "EX-old-profile", "role": "research_work", "status": "queued"}
        self.assertFalse(slots.acquire(execution["id"], profile=old, execution=execution))
        self.assertEqual(slots.admission_wait["kind"], "capacity")
        self.assertEqual(slots.admission_wait["next_owner"], "user")
        self.assertEqual(runtime["reservations"], {})

        raised = deepcopy(lower)
        raised["work"][MODELS["high"]] = 1
        config["session_limits"] = raised
        apply_editions(instance, build_profiles(config))
        self.assertTrue(slots.acquire(execution["id"], profile=old, execution=execution))
        current = next(instance["execution_profiles"][ref["id"]]
                       for ref in instance["role_profile_refs"]["research_work"]
                       if instance["execution_profiles"][ref["id"]]["ai"].get("tier") == "high")
        self.assertEqual(next(iter(runtime["reservations"].values()))["constraint_id"],
                         current["ai"]["capacity_refs"][0])

    def test_defaults_and_max_of_difficulty_and_importance(self):
        self.assertEqual(MODELS, {"high": "gpt-6-astra", "medium": "gpt-5.6-sol", "low": "gpt-5.6-terra"})
        per_model = {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3}
        self.assertEqual(LIMITS, {"work": per_model})
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
        config["session_limits"]["work"]["configured-future-model"] = 2
        validate_policy(config)

    def test_bad_capacity_and_missing_tier_model_are_rejected(self):
        for value in (-1, True, None, 1.5):
            config = deepcopy(DEFAULT_CONFIG)
            config["session_limits"]["work"][MODELS["high"]] = value
            with self.assertRaises(ValueError): validate_policy(config)
        for tier in ("low", "medium", "high"):
            config = deepcopy(DEFAULT_CONFIG)
            del config["tier_models"][tier]
            with self.assertRaises(ValueError): validate_policy(config)

    def test_role_floor_raises_low_assessment_and_unassessed_work_uses_high(self):
        config = deepcopy(DEFAULT_CONFIG)
        low = {"difficulty": "low", "importance": "low", "reason": "bounded local comparison"}
        review = selection(config, {"role": "task_contract_review", "model_assessment": low}, {}, {})
        self.assertEqual((review["tier"], review["model"]), ("medium", MODELS["medium"]))
        unassessed = selection(config, {"role": "research_work"}, {}, {})
        self.assertEqual((unassessed["tier"], unassessed["model"]), ("high", MODELS["high"]))


class SlotTests(unittest.TestCase):
    """The Git writer owns admission; observers never reconcile reservations."""
    def setUp(self):
        limits = {'work': {model: 1 for model in MODELS.values()}}
        self.root, instance_id = restore_template(initialized_instance, goal='Reservation boundary fixture',
            config={'operator_enabled': True, 'scholarly_enabled': False, 'session_limits': limits})
        self.repo, self.workspace = self.root / 'repository', self.root / 'work-0'
        self.engine = ResearchEngine(self.repo, instance_id, runner=ScriptedRunner())

    def slots(self, *, observer=False):
        e = self.engine
        return SessionSlots( runtime=e.runtime,
                            instance=e.instance, observer=observer)

    def reserve(self, eid, *, operational=False):
        """Admit a work role, which holds a model slot, or an operational role, which holds none."""
        e = self.engine
        role = 'research_plan' if operational else 'task_contract_review'
        profile = next(p for p in e.instance['execution_profiles'].values()
                       if p['role'] == role and p['ai']['model'] == MODELS['high'])
        from do_math.execution_profiles import profile_ref
        from do_math.execution_lifecycle import create_execution, transition_execution
        from do_math.activities import open_activity, assign_execution
        from do_math.engine import now
        action = {'id': 'AC-' + eid, 'role': role, 'profile_ref': profile_ref(profile)}
        activity = open_activity(e.runtime, activity_id='AY-' + eid, activity_kind=role,
            owner_ref=e.instance['id'], input_refs=[], opened_at=now())
        execution = create_execution(execution_id=eid, owner_activity_id=activity['id'], actor_kind='ai',
            input_manifest=[], profile_ref=profile_ref(profile), created_at=now())
        execution.update(role=role, action=action, input_snapshot=e.head)
        transition_execution(execution, 'starting', at=now())
        assign_execution(e.runtime, activity['id'], execution)
        accepted = self.slots().acquire(eid, profile=profile, execution=execution)
        return accepted, execution

    def test_work_slot_operational_admission_and_reusable_slots_are_published_together(self):
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-work')[0])
            self.assertFalse(self.reserve('EX-blocked')[0])
            self.assertTrue(self.reserve('EX-operation', operational=True)[0])
            self.engine._save()
            head, state, runtime = self.engine.store.load()
            self.assertEqual(head, self.engine.head)
            self.assertTrue(runtime['reservations'])
            self.assertFalse([row for row in runtime['reservations'].values()
                              if row['owner_id'] == 'EX-operation' and row['unit'] == 'execution'])
            self.assertTrue(all(row['owner_id'] in runtime['executions'] for row in runtime['reservations'].values()))
            self.assertTrue(self.slots().release('EX-work'))
            self.assertTrue(self.reserve('EX-next')[0])
            self.engine._save()
        self.assertFalse(list(self.workspace.rglob('*.sqlite*')))

    def test_saved_reservations_survive_reopen_until_explicit_release(self):
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-held')[0])
            self.engine._save()
        saved = deepcopy(self.engine.runtime['reservations'])
        self.engine = ResearchEngine(self.repo, self.engine.instance['id'], runner=ScriptedRunner())
        self.assertEqual(self.engine.runtime['reservations'], saved)
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 1)
        with self.engine.store.writer_lock():
            self.assertTrue(self.slots().release('EX-held'))
            self.engine._save()
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 0)

    def test_distinct_instances_have_distinct_reservation_ledgers(self):
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-first-instance')[0])
            self.engine._save()
        other_workspace = self.root / 'other-work'
        created = initialize(self.repo, goal='Separate reservation ledger', workspace=other_workspace,
            config={'session_limits': deepcopy(self.engine.instance['config']['session_limits']),
                    'operator_enabled': False, 'scholarly_enabled': False})
        other = ResearchEngine(self.repo, created['instance_id'], runner=ScriptedRunner())
        self.assertNotEqual(other.instance['id'], self.engine.instance['id'])
        observer = SessionSlots( runtime=other.runtime,
                                instance=other.instance, observer=True)
        self.assertEqual(observer.snapshot()[MODELS['high']]['used'], 0)
        self.assertEqual(self.slots(observer=True).snapshot()[MODELS['high']]['used'], 1)
        self.assertEqual(other.store.load()[2]['reservations'], {})

    def test_observer_cannot_acquire_or_reconcile_an_unknown_lifetime(self):
        with self.engine.store.writer_lock():
            self.reserve('EX-held')
            self.engine._save()
        before = deepcopy(self.engine.runtime)
        observer = self.slots(observer=True)
        with self.assertRaisesRegex(ValueError, 'read-only'):
            observer.release('EX-held')
        observer.snapshot()
        self.assertEqual(self.engine.runtime, before)

    def test_two_processes_cannot_both_own_the_git_writer(self):
        program = "\n".join([
            'import sys', 'from pathlib import Path',
            'sys.path.insert(0, sys.argv[1])',
            'from do_math.engine import _repository',
            'try:',
            ' with _repository(Path(sys.argv[2]),sys.argv[3]).writer_lock(): print("acquired")',
            'except Exception as error: print(type(error).__name__)'])
        with self.engine.store.writer_lock():
            child = subprocess.run([sys.executable, '-c', program, str(Path(__file__).resolve().parents[1]),
                str(self.repo), self.engine.instance['id']], capture_output=True, text=True, timeout=30)
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertIn('LockError', child.stdout)
        self.assertNotIn('acquired', child.stdout)

    @unittest.skipUnless(os.name == 'nt', 'requires a Windows Job')
    def test_slot_waits_for_actual_named_job_termination(self):
        from do_math.windows_job import WindowsJob, named_job_empty
        from do_math.engine import now
        name = 'Local\\DoMath-test-' + uuid.uuid4().hex
        with self.engine.store.writer_lock():
            self.assertTrue(self.reserve('EX-job')[0])
            name = self.engine.runtime['executions']['EX-job']['launch_ticket']['job_name']
            with WindowsJob([sys.executable, '-c', 'import time; time.sleep(30)'], name=name) as job:
                self.slots().started('EX-job', {'pid': job.pid, 'job_name': name}, at=now())
                self.engine._save()
                job.resume()
                self.assertFalse(self.slots().release('EX-job'))
                job.terminate()
                self.assertTrue(job.wait(10))
                self.assertTrue(named_job_empty(name))
                self.assertTrue(self.slots().release('EX-job'))
            self.engine._save()

    def test_regular_supervision_observes_without_creating_an_ai_execution(self):
        from do_math import scheduled_operator
        with patch.object(scheduled_operator, 'ModelRunner', side_effect=AssertionError('unexpected model')):
            outcome = scheduled_operator.check(self.repo, self.engine.instance['id'], self.workspace, probe=True)
        self.assertEqual(outcome['outcome'], 'observed')
        self.assertFalse(outcome['model_called'])
        self.assertEqual(self.engine.store.load()[2]['executions'], {})

    def test_recovery_requires_actual_failure_evidence(self):
        from do_math import scheduled_operator
        with self.assertRaisesRegex(ValueError, 'failure evidence'):
            scheduled_operator.recovery(self.repo, self.engine.instance['id'], self.workspace, failure={})


class ParallelEngineTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)

    def engine(self, runner, count=3, *, public=False, **config):
        """A copy of ``ready_work``'s state (see there) with ``runner``; ``config`` includes limits."""
        self.root, instance_id = restore_template(ready_work, count=count, public=public, config=config)
        self.repo = self.root / "repository"
        return ResearchEngine(self.repo, instance_id, runner=runner)

    def configure_limits(self, engine, limits):
        from research_fixtures import send_control
        send_control(engine, "configure", config={"session_limits":limits})
        refs = [ref for rows in engine.instance['role_profile_refs'].values() for ref in rows
                if engine.instance['execution_profiles'][ref['id']]['actor_kind']=='ai']
        send_control(engine, 'decision', config={'change':{'kind':'initialization',
            'operation':'probe', 'profile_refs':refs}})

    def test_three_calls_overlap_and_apply_serially_to_distinct_workspaces(self):
        runner = ConcurrentRunner()
        engine = self.engine(runner, public=True)  # judges check(); see engine()
        main = threading.get_ident()
        save = engine._save
        def checked_save(*args, **kwargs):
            self.assertEqual(threading.get_ident(), main)
            return save(*args, **kwargs)
        engine._save = create_autospec(engine._save, side_effect=checked_save)
        state = engine.run(max_steps=3)
        self.assertEqual(runner.peak, 3)
        self.assertEqual(len(set(runner.workspaces)), 3)
        self.assertEqual(runner.models, [MODELS["high"]] * 3)
        self.assertEqual(len({(p / "same-name.txt").read_text(encoding="utf-8") for p in runner.workspaces}), 3)
        self.assertEqual(len([e for e in engine.runtime["executions"].values() if e["role"] == "research_work" and e.get("outcome") == "output_accepted"]), 3)
        self.assertEqual(state["budget"][MODELS["high"]]["used"], 0)
        checked = engine.check()
        self.assertEqual(checked["errors"], [], checked)
        # Snapshot inspection deliberately leaves live trust files unexamined
        # (state_checks governance_trust); every other area is clean.
        self.assertEqual(checked["inspection"]["not_checked"], ["governance_trust"], checked)
        self.assertEqual({(row["area"], row["status"]) for row in checked["inspection"]["findings"]},
                         {("governance_trust", "incomplete")}, checked)

    def test_unavailable_assigned_model_waits_without_spending_other_model_slots(self):
        limits = deepcopy(LIMITS); limits["work"][MODELS["high"]] = 0
        runner = ConcurrentRunner(expected=1)
        engine = self.engine(runner, count=1, session_limits=limits)
        state = engine.run(max_steps=1)
        self.assertEqual(state["status"], "capacity_waiting")
        self.assertEqual(runner.models, [])
        self.assertEqual(state["capacity_waiting"][0]["model_selection"]["model"], MODELS["high"])
        limits["work"][MODELS["high"]] = 1
        self.configure_limits(engine, limits)
        engine.run(max_steps=1)
        self.assertEqual(runner.models, [MODELS["high"]])

    def test_blocked_high_priority_work_does_not_block_independent_low_model_work(self):
        limits = deepcopy(LIMITS); limits["work"][MODELS["high"]] = 0
        runner = ConcurrentRunner(expected=1)
        engine = self.engine(runner, count=2, session_limits=limits)
        high = engine.runtime["queue"][0]["target"]
        task = engine.runtime["tasks"][engine.runtime["queue"][1]["target"]]
        task["model_assessment"] = {"difficulty": "low", "importance": "low", "reason": "bounded local transcription"}
        # Complete another real contract review after the model judgment changes.
        pending = deepcopy(engine.runtime["queue"])
        engine.runtime["queue"] = []
        engine._enqueue("task_contract_review", task["id"])
        engine.runner = ScriptedRunner()
        engine._save()
        engine.run(max_steps=1)
        # The changed contract lost its selection; a real plan selects it again under
        # the new judgment while the high task's selected work waits for its model.
        engine.runtime["queue"] = [a for a in pending if a["target"] == high] + engine.runtime["queue"]
        engine._save()
        engine.run(max_steps=1)
        engine.runner = runner
        engine.run(max_steps=1)
        self.assertEqual(runner.models, [MODELS["low"]])
        self.assertTrue(any(a.get("target") == high for a in engine.runtime["queue"]))


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
                        # The real runner's idle cadence (model_runner.observe): one delivery per second.
                        if last_tick is None or time.monotonic() - last_tick >= 1:
                            on_observation({"type": "tick"}); last_tick = time.monotonic()
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

    def test_planner_queue_order_cancels_only_unstarted_requests_and_preserves_obligations(self):
        engine = self.engine(ConcurrentRunner(), count=3)
        engine._refresh_readiness()
        first, second, third = deepcopy(engine.runtime["queue"])
        eid = "EX-plan"
        engine.runtime["executions"][eid] = {"input_snapshot": engine.head, "status": "ended", "extensions": {
            "queued_requests": [{"request_id": third["id"], "decision": "keep", "reason": "opens the next proof question"},
                                {"request_id": first["id"], "decision": "keep", "reason": "follow after third"},
                                {"request_id": second["id"], "decision": "cancel", "reason": "defer this approach"}]}}
        engine._apply_queue_plan({"role": "research_plan"}, eid)
        self.assertEqual([a["id"] for a in engine.runtime["queue"]], [third["id"], first["id"]])
        task = engine.runtime["tasks"][second["target"]]
        self.assertEqual(task["status"], "planned")
        self.assertEqual([row["id"] for row in task["completion_obligations"]], ["OB-argument"])

    def test_model_assessments_flow_from_preparation_through_review_and_planning_to_execution(self):
        assessment = {"difficulty": "low", "importance": "low", "reason": "a local bounded comparison with an explicit method"}
        # Public activation: check() judges the interpretation executions (see ready_work).
        engine = self.engine(ScriptedRunner(model_rating=assessment), count=0, public=True)
        # Every assertion reads the first work execution and the submissions up to it;
        # the plan, goal audits and repreparation after it assert nothing.
        for _ in range(12):
            engine.run(max_steps=1)
            if any(e["role"] == "research_work" and e["status"] == "ended"
                   for e in engine.runtime["executions"].values()):
                break
        tasks = list(engine.runtime["tasks"].values())
        self.assertEqual(tasks[0]["model_assessment"], assessment)
        work = [e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertTrue(work)
        self.assertEqual(work[0]["model"], MODELS["low"])
        self.assertEqual(work[0]["model_selection"]["assessment"], assessment)
        inspection = engine.check()
        self.assertEqual(inspection["errors"], [])
        self.assertEqual(inspection["submission_checks"]["status"], "verified")
        self.assertEqual(inspection["inspection"]["not_checked"], ["governance_trust"])
        self.assertEqual(inspection["inspection"]["status"], "incomplete")

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
                        on_observation({"type": "tick"})
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
            @local_job_runner
            def run(inner, *, prompt, on_started, **kwargs):
                inner.roles.append(context_from(prompt, kwargs['workspace'])["action"]["role"])
                on_started()
                out = common("research_preparation")
                out.pop("candidates")
                return {"status": "completed", "output": out, "usage": {}, "error": None}
        runner = InvalidPreparation()
        # Activation leaves queue events that this queue-order rule meets.
        engine = self.engine(runner, count=0, public=True)
        # The newer request replaces activation's own preparation and keeps ownership
        # of its events; unowned events would schedule a plan into this queue.
        activation = next(a for a in engine.runtime["queue"] if a["role"] == "research_preparation")
        engine.runtime["queue"] = [{"id": "AC-older", "role": "maintenance", "reason": "older operating request"},
                                   {"id": "AC-preparation", "role": "research_preparation", "reason": "newer operating request",
                                    "event_refs": activation["event_refs"]}]
        engine._save()
        # Operational roles hold no model slot; the older request waits on its dispatch check instead.
        dispatchable = engine._dispatchable
        engine._dispatchable = create_autospec(engine._dispatchable,
            side_effect=lambda action: action["role"] != "maintenance" and dispatchable(action))
        engine.run(max_steps=1)
        self.assertEqual(runner.roles, ["research_preparation"])
        self.assertEqual([a["id"] for a in engine.runtime["queue"]], ["AC-older", "AC-preparation"])
        self.assertEqual(engine.runtime["queue"][1]["repair_attempt"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
