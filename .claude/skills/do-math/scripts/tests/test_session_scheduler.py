"""Scheduling: session slots and provider admission, when plans open or wait, call timeouts, and machine reservations."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import control, initialize, ResearchEngine
from do_math.execution_profiles import WORK_ROLES
from do_math.model_policy import assessment_tier, LIMITS, MODELS, selection, validate_policy
from do_math.planning import seal_contract_review
from do_math.system_clock import new_id
from do_math.session_slots import SessionSlots
from engine_fixtures import initialized_instance, reassessment_engine, routing_engine
from purpose_fixtures import ActivatedPurposeHarness
from research_fixtures import (candidate, clock_ports, contract_review, current_state, git_init, install_adapter_fixture,
                               local_job_runner, observation_batch, producer_result, restore_template)
from runner_fixtures import common, context_from, ScriptedRunner
from state_fixtures import start_active_copy


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
        from do_math.configuration import validate_config
        # The configuration schema owns the capacity range; the policy owns cross-field rules.
        for value in (-1, True, None, 1.5):
            config = deepcopy(DEFAULT_CONFIG)
            config["session_limits"]["work"][MODELS["high"]] = value
            with self.assertRaisesRegex(ValueError, "config/session_limits/work"): validate_config(config)
        config = deepcopy(DEFAULT_CONFIG)
        config["session_limits"]["work"][" "] = 1
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


class OwnerRescanTests(unittest.TestCase):
    def test_owner_rejudges_after_a_state_change_or_its_time_bound_but_not_after_an_observation(self):
        import state_fixtures
        from do_math.scheduler import OWNER_RESCAN_SECONDS
        root, instance_id = restore_template(state_fixtures.active_instance, config={})
        engine = ResearchEngine(root / "repository", instance_id)
        instant = [100.0]
        engine.ports = clock_ports(monotonic=lambda: instant[0])
        self.assertTrue(engine._scan_due())
        self.assertFalse(engine._scan_due(), "an unchanged state was judged again")
        engine.runtime["history"].append({"kind": "fixture_observation"})
        engine._publish_observation()
        self.assertFalse(engine._scan_due(), "an observation publication made the owner judge again")
        engine.runtime["history"].append({"kind": "fixture_change"})
        self.assertTrue(engine._scan_due())
        self.assertFalse(engine._scan_due())
        instant[0] = 100.0 + OWNER_RESCAN_SECONDS
        self.assertTrue(engine._scan_due())


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
        from do_math.system_clock import now
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
            'from do_math.repository import ResearchRepository',
            'try:',
            ' with ResearchRepository(Path(sys.argv[2]),sys.argv[3]).writer_lock(): print("acquired")',
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
        from do_math.system_clock import now
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
        # Every persisted-state area is clean, so the check passes; live trust
        # files are outside the snapshot the inspection reads.
        self.assertEqual(checked["inspection"]["not_checked"], [], checked)
        self.assertEqual(checked["inspection"]["findings"], [], checked)
        self.assertTrue(checked["passed"], checked)

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

    def test_planner_queue_order_cancels_only_unstarted_requests_and_preserves_obligations(self):
        engine = self.engine(ConcurrentRunner(), count=3)
        engine._refresh_readiness()
        first, second, third = deepcopy(engine.runtime["queue"])
        eid = "EX-plan"
        engine.runtime["executions"][eid] = {"input_snapshot": engine.head, "status": "ended", "extensions": {
            "queued_requests": [{"request_id": third["id"], "decision": "keep", "reason": "opens the next proof question"},
                                {"request_id": first["id"], "decision": "keep", "reason": "follow after third"},
                                {"request_id": second["id"], "decision": "cancel", "reason": "defer this approach"}]}}
        engine._apply_queue_plan(eid)
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
        self.assertEqual(inspection["inspection"]["not_checked"], [])
        self.assertEqual(inspection["inspection"]["status"], "healthy")

    def test_selected_task_without_a_plan_assessment_runs_at_its_reviewed_assessment(self):
        """About 14 s after the shared template: receipt, plan application and dispatch each decide the unrated selection."""
        assessment = {"difficulty": "low", "importance": "low", "reason": "a local bounded comparison with an explicit method"}
        # The plan rates no selected task, so the receiver accepts it and dispatch reads the task record.
        engine = self.engine(ScriptedRunner(model_rating=assessment, plan_assessments=False), count=0, public=True)
        for _ in range(12):
            engine.run(max_steps=1)
            if any(e["role"] == "research_work" for e in engine.runtime["executions"].values()):
                break
        plans = [e for e in engine.runtime["executions"].values() if e["role"] == "research_plan"]
        self.assertTrue(plans)
        self.assertEqual(plans[0].get("model_decisions"), {})
        work = [e for e in engine.runtime["executions"].values() if e["role"] == "research_work"]
        self.assertTrue(work, [e.get("reason") for e in engine.runtime.get("waiting_actions", {}).values()])
        self.assertEqual(work[0]["model"], MODELS["low"])
        self.assertEqual(work[0]["model_selection"]["assessment"], assessment)

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


class ResearchAdmissionTests(unittest.TestCase):
    def test_public_task_flow_keeps_observation_and_state_contracts_consistent(self):
        from runner_fixtures import ScriptedRunner
        start_active_copy(self)
        engine = ResearchEngine(self.repo, self.identifier, runner=ScriptedRunner())
        # This is a scheduler/storage integration test with scripted answers,
        # not a test of the AI's reading of role prose (checked separately).
        engine._documents = {role: [dict(document, content='Synthetic fixture: ' + document['path'],
            sha256=hashlib.sha256(('Synthetic fixture: ' + document['path']).encode()).hexdigest())
            for document in documents] for role, documents in engine._documents.items()}
        engine.instance, engine.runtime = engine._configure_candidate(engine.instance, engine.runtime,
            {'origin':'user', 'config':{'tool_review_window_seconds':60,
                'self_check_response_window_seconds':5, 'plan_settle_seconds':1}})
        from research_fixtures import FixtureAdapter
        for profile in engine.instance['execution_profiles'].values():
            if profile['actor_kind'] == 'ai':
                evidence = execution_profiles.capability_evidence(profile, FixtureAdapter().describe(),
                    observed_at=engine._lifecycle_now().isoformat())
                engine.instance.setdefault('capability_evidence', {})[evidence['id']] = evidence
        engine._enqueue('research_preparation', reason='Exercise task admission after the approved initial fixture')
        engine._save()
        admit = engine._provider_admit
        def checked_admission(*args, **kwargs):
            accepted = admit(*args, **kwargs)
            self.assertTrue(accepted, {'reason':(args[0].get('dispatch_wait') or {}).get('kind'),
                'resources':engine._session_slots().snapshot(), 'reservations':engine.runtime.get('reservations'),
                'profile':kwargs['profile']})
            return accepted
        engine._provider_admit = create_autospec(engine._provider_admit, side_effect=checked_admission)
        # Readiness events may open an extra plan; a step counts an action,
        # not one of the four conceptual research phases.
        engine.run(max_steps=8)
        work = [e for e in engine.runtime['executions'].values() if e['role']=='research_work']
        self.assertTrue(work, {'tasks':engine.runtime['tasks'], 'queue':engine.runtime['queue'],
                              'waits':engine.runtime.get('waiting_actions'), 'history':engine.runtime['history'][-5:]})
        self.assertTrue(work[0]['observation_rules'])
        report = engine.check()
        self.assertEqual(report['errors'], [])
        # This fixture supplies synthetic initial interpretations without input manifests.
        self.assertEqual(report['inspection']['status'], 'incomplete', report)
        self.assertEqual({row['message'] for row in report['inspection']['findings']}, {
            'EX-check: role input manifest not examined', 'EX-interpret: role input manifest not examined'})


class PlanAfterPreparationTests(ActivatedPurposeHarness):
    def prepare(self, candidates, *, ready_candidate=False):
        # The validated active state has no queued action and no pending event,
        # so nothing but the tested preparation can open a plan. (Public activation
        # leaves reconsideration events that a plan would first have to consume.)
        engine, _ = self.make_active(**self.fixture_config(
            scholarly_enabled=False, operator_enabled=False))
        self.assertEqual(engine.runtime["queue"], [])
        self.assertFalse(engine.runtime.get("pending_events"))
        if ready_candidate:
            engine.runner = ScriptedRunner(preparation_candidates=[candidate("deferred")])
            engine._enqueue("research_preparation", reason="Prepare a task that will await a decision")
            engine._save()
            engine.run(max_steps=2)
            self.assertTrue(any(row["state"] == "ready" for row in engine._task_readiness.values()))
        # Isolate the preparation trigger from previously queued plans. The task
        # and its approval remain actual receiver-created records.
        engine.runtime["queue"] = []
        engine._enqueue("research_preparation", reason="Explicit regression preparation")
        engine.runner = ScriptedRunner(preparation_candidates=candidates)
        engine._save()
        engine.run(max_steps=1)
        return engine

    def plans(self, engine):
        return [a for a in engine.runtime["queue"] if a["role"] == "research_plan"]

    def test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide(self):
        engine = self.prepare([candidate("one")])
        self.assertTrue(any(a["role"] == "task_contract_review" for a in engine.runtime["queue"]))
        self.assertEqual(self.plans(engine), [])

    def test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision(self):
        engine = self.prepare([candidate("one")], ready_candidate=True)
        self.assertEqual(len(self.plans(engine)), 1)

    def test_preparation_without_any_pending_review_still_opens_a_plan(self):
        engine = self.prepare([])
        self.assertEqual(len(self.plans(engine)), 1, self.plans(engine))


class DuplicateContractReviewTests(ActivatedPurposeHarness):
    def test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move(self):
        engine, _ = self.make_active(**self.fixture_config(
            scholarly_enabled=False, operator_enabled=False))
        engine.runner = ScriptedRunner(preparation_candidates=[candidate("window")])
        engine._enqueue("research_preparation", reason="Prepare the contract under review")
        engine._save()
        engine.run(max_steps=1)
        running = next(a for a in engine.runtime["queue"] if a["role"] == "task_contract_review")
        from do_math.system_clock import new_id
        from do_math.system_clock import now
        execution = engine._register_execution(running, {"id": new_id("EX"),
            "role": "task_contract_review", "status": "running", "created_at": now(), "input_snapshot": engine.head})
        before_id = running["id"]
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime["queue"] if a["role"] == "task_contract_review"]
        self.assertEqual([a["id"] for a in reviews], [before_id],
                         "the finished review's own currentness check decides whether another review is needed")


class PlanSettleTests(ActivatedPurposeHarness):
    def setUp(self):
        super().setUp()
        self.engine, _ = self.make_active(scholarly_enabled=False, operator_enabled=False)
        self.engine.runtime["queue"] = []

    def queue(self, plan, review=True):
        self.engine.runtime["queue"] = [plan, *([{"id": "AC-review", "role": "task_contract_review", "target": "TK-x"}] if review else [])]
        return plan

    def test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan"})
        self.assertFalse(self.engine._dispatchable(plan))
        self.assertEqual(plan["dispatch_wait"]["kind"], "plan_settle")
        self.queue(plan, review=False)
        self.assertTrue(self.engine._dispatchable(plan))

    def test_the_settle_wait_ends_at_its_configured_limit(self):
        from datetime import datetime, timedelta, timezone
        self.assertEqual(self.engine.instance["config"]["plan_settle_seconds"], 300)
        started = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "settle_started_at": started})
        self.assertTrue(self.engine._dispatchable(plan), "a slow review must not hold the first ready task for long")

    def test_an_explicitly_requested_plan_does_not_settle(self):
        plan = self.queue({"id": "AC-plan", "role": "research_plan", "requested_by": "UC-user"})
        self.assertTrue(self.engine._dispatchable(plan))


class RunWithoutDeadlineTests(ActivatedPurposeHarness):
    def test_elapsed_time_does_not_block_the_next_execution_and_work_calls_have_no_timeout(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import time
        import do_math.engine as engine_module
        import do_math.scheduler as scheduler
        engine, _ = self.make_active(scholarly_enabled=False, operator_enabled=False)
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', reason='Prepare a contract for the deadline regression')
        engine._save()
        scripted = ScriptedRunner(preparation_candidates=[candidate('deadline regression')])
        clock = [0.0]
        calls = []
        class Runner:
            def run(self, **arguments):
                calls.append(arguments)
                result = scripted.run(**arguments)
                clock[0] += 10000
                return result
        engine.runner = Runner()
        engine.ports = clock_ports(monotonic=lambda: time.monotonic() + clock[0])
        engine.run(max_steps=2)
        self.assertEqual(len(calls), 2)
        self.assertEqual({call['profile']['role'] in WORK_ROLES for call in calls}, {True, False})
        for call in calls:
            if call['profile']['role'] in WORK_ROLES:
                self.assertIsNone(call['timeout_seconds'])
            else:
                self.assertGreater(call['timeout_seconds'], 0)
                self.assertLessEqual(call['timeout_seconds'], call['profile']['window']['call_timeout_seconds'])
        self.assertNotEqual(engine.runtime['status'], 'paused')


class SchedulingResponsibilityTests(unittest.TestCase):
    def test_terminal_stale_assessment_gets_one_followup_without_reopening(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = reassessment_engine(directory)
            task = engine.runtime['tasks']['TK-1']
            task['status'] = 'closed'
            task['assessment'].update(current=False, invalidated_reason='source corrected')
            engine._refresh_readiness(); engine._refresh_readiness()
            self.assertEqual(task['status'], 'closed')
            events = [e for e in engine.runtime['events'] if e['kind'] == 'task_assessment_invalidated']
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['target'], 'TK-1')
            self.assertTrue(any(events[0]['id'] in a.get('event_refs', []) for a in engine.runtime['queue']))

    def test_initial_preparation_owns_initial_events_until_accepted(self):
        from engine_fixtures import FakeEngine
        from research_fixtures import FixtureAdapter
        with tempfile.TemporaryDirectory() as directory, patch('do_math.local_host.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(directory); engine.activate()
            engine.instance['lifecycle']['state'] = 'initializing'
            engine.runtime['status'] = 'initializing'
            engine._lifecycle_event('trust_environment_activated')
            engine._activate_initialization()
            first = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
            self.assertEqual(set(first.get('event_refs', [])), set(engine.runtime['pending_events']))
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            self.assertTrue(engine.runtime['pending_events'], 'Assignment is not consumption')

    def test_normal_dispatch_occupancy_does_not_request_a_new_plan(self):
        from engine_fixtures import FakeEngine
        from research_fixtures import FixtureAdapter
        with tempfile.TemporaryDirectory() as directory, patch('do_math.local_host.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(directory); engine.activate(); task = engine.task()
            engine._refresh_readiness()
            engine.runtime['queue'] = [{'id': 'AC-work', 'role': 'research_work', 'target': task['id']}]
            engine.runtime['pending_events'] = []
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            self.assertTrue(engine._task_readiness[task['id']].get('dispatch_occupied'))
            engine.instance['grants']['GR-research']['status'] = 'revoked'
            engine._refresh_readiness()
            self.assertTrue(any(a['role'] == 'research_plan' for a in engine.runtime['queue']),
                            'Actual authority loss during occupancy still needs planning')


class MachineAdmissionConnections(unittest.TestCase):
    def fixture(self):
        from provider_fixtures import host_capacity_fixture
        instance, selected, _ = host_capacity_fixture()
        engine = routing_engine(); engine.instance.update(instance)
        engine._execution_profile = create_autospec(engine._execution_profile, return_value=selected["formal_check"])
        engine._admit_review_execution = create_autospec(engine._admit_review_execution, return_value={"disposition": "not_applicable"})
        engine._save = create_autospec(engine._save)
        return engine

    def test_common_machine_admission_reserves_before_start_and_refuses_without_execution(self):
        engine = self.fixture()
        for index in range(3):
            action = {"id": f"AC-machine-{index}", "role": "formal_check", "target": "KN-one"}
            execution = engine._register_execution(action, {"id": f"EX-machine-{index}", "status": "running", "role": "formal_check"})
            self.assertEqual(execution["status"], "starting")
            self.assertEqual(len(execution["capacity"]["reservation_ids"]), 3)
            self.assertIsNone(execution["capacity"]["provider"])
        action = {"id": "AC-refused", "role": "formal_check", "target": "KN-one"}
        engine.runtime["queue"].append(action)
        self.assertIsNone(engine._register_execution(action, {"id": "EX-refused", "status": "running", "role": "formal_check"}))
        self.assertNotIn("EX-refused", engine.runtime["executions"])
        self.assertEqual(engine.runtime["activities"][action["owner_activity_id"]]["status"], "waiting")
        self.assertEqual(len(engine.runtime["reservations"]), 9)
        engine._local_call_returned("EX-machine-0", {"launch_not_created":True})
        self.assertTrue(engine._session_slots().release("EX-machine-0", reason="explicit local start failure"))
        retry = engine._register_execution(action, {"id": "EX-retry", "status": "running", "role": "formal_check"})
        self.assertEqual(retry["status"], "starting")

    def test_machine_callback_seals_process_before_resume_and_keeps_uncertain_capacity(self):
        engine = self.fixture()
        execution = engine._register_execution({"id": "AC-one", "role": "formal_check"},
            {"id": "EX-one", "status": "running", "role": "formal_check"})
        identity = {"job_name": execution["launch_ticket"]["job_name"], "pid": 17, "creation_filetime": "12345"}
        def published():
            self.assertEqual(execution["capacity"]["process"], identity)
            self.assertEqual(execution["status"], "running")
        engine._save.side_effect = published
        engine._machine_started("EX-one", identity)
        engine._save.assert_called_once()
        from do_math.execution_lifecycle import release_or_hold
        with patch("do_math.windows_job.named_job_empty", return_value=False):
            self.assertFalse(release_or_hold(execution, engine._session_slots(), at="2026-09-20T00:00:01+00:00"))
        self.assertEqual(execution["status"], "stopping")
        self.assertEqual(execution["error"],
                         "Local Job termination is unconfirmed; capacity and output remain held for recovery.")
        self.assertTrue(all(row["state"] != "settled" for row in engine.runtime["reservations"].values()))

    def test_actual_git_snapshot_binds_machine_reservations_and_start_identity(self):
        from do_math.repository import ResearchRepository
        from do_math.system_clock import new_id
        from provider_fixtures import host_capacity_fixture
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_init(root / "repo")
            instance, profiles, _ = host_capacity_fixture()
            engine = routing_engine()
            engine.instance, engine.runtime = current_state(
                {**instance, "id": new_id("RI"), "workspace": str(root / "work")},
                {"executions": {}, "activities": {}, "tasks": {}, "queue": [], "history": []})
            engine.instance["role_profile_refs"]["formal_check"] = [execution_profiles.profile_ref(profiles["formal_check"])]
            engine.store = ResearchRepository(root / "repo", engine.instance["id"])
            engine.head = engine.store.initialize(engine.instance, engine.runtime)
            with engine.store.writer_lock():
                engine._register_execution({"id": "AC-machine", "role": "formal_check"},
                    {"id": "EX-machine", "role": "formal_check", "status": "running"})
                engine._save()
                admitted = engine.head
                _, _, staged = engine.store.load(admitted)
                self.assertEqual(staged["executions"]["EX-machine"]["status"], "starting")
                self.assertEqual(len(staged["reservations"]), 3)
                # The Job identity is a double; both pre-resume publications and
                # the host reservation records use actual schema and Git CAS.
                identity = {"job_name": engine.runtime["executions"]["EX-machine"]["launch_ticket"]["job_name"], "pid": 29, "creation_filetime": "123456789012345678"}
                engine._machine_started("EX-machine", identity)
                _, _, started = engine.store.load(engine.head)
                self.assertNotEqual(engine.head, admitted)
                self.assertEqual(started["executions"]["EX-machine"]["capacity"]["process"], identity)
                self.assertEqual(started["executions"]["EX-machine"]["status"], "running")


class MaintenanceFenceRunTests(unittest.TestCase):
    def test_run_that_starts_under_a_maintenance_fence_returns_without_an_execution(self):
        # The owner loop meets the fence in its first pass, before the loop's stopping check.
        start_active_copy(self)
        control(self.repo, self.identifier, 'quiesce', text='fixture installation maintenance')
        engine = ResearchEngine(self.repo, self.identifier)
        engine.process_controls()
        self.assertEqual(engine.runtime['maintenance_fence']['state'], 'quiescent')
        executions = deepcopy(engine.runtime['executions'])
        engine.run(max_steps=1)
        self.assertEqual(engine.runtime['maintenance_fence']['state'], 'quiescent')
        self.assertEqual(engine.runtime['executions'], executions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
