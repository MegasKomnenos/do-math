"""Provider admission over real Git; provider responses and clocks are synthetic."""
from copy import deepcopy
from datetime import datetime, timezone
import multiprocessing
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_lifecycle as lifecycle
from do_math.engine import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.git_store import GitStateStoreLockError
from do_math.repository import ResearchRepository, new_id
from do_math.session_slots import GitSessionSlots
from do_math.provider_wait import timestamp

MODEL = "claude-opus-5"
FAILURE = {"kind": "provider_limit", "provider": "claude", "retry_at": None,
           "evidence_ref": "synthetic-provider-limit.json", "limit_windows": []}


def instant(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def admit(slots, instance, runtime, identifier, pool="work", current=100):
    role = "research_work" if pool == "work" else "maintenance"
    reference = instance["role_profile_refs"][role][-1]
    profile = instance["execution_profiles"][reference["id"]]
    aid = "AY-" + identifier
    execution = lifecycle.create_execution(execution_id=identifier, owner_activity_id=aid,
        actor_kind="ai", input_manifest=[], profile_ref=profile_ref(profile), created_at=instant(current))
    execution["role"] = role
    lifecycle.transition_execution(execution, "starting", at=instant(current))
    if not slots.acquire(identifier, pool, MODEL, profile=profile, execution=execution,
                         provider="claude", current_time=current):
        return False
    activities.open_activity(runtime, activity_id=aid, activity_kind=role,
        owner_ref=instance["id"], input_refs=[], opened_at=instant(current))
    activities.assign_execution(runtime, aid, execution)
    return True


def finish(slots, runtime, identifier, current):
    if not slots.release(identifier):
        raise AssertionError("test execution without an acknowledged process did not settle")
    execution = runtime["executions"][identifier]
    lifecycle.transition_execution(execution, "stopping", at=instant(current), stop_phase="terminating")
    lifecycle.transition_execution(execution, "ended", at=instant(current), outcome="start_failed",
        disposition={"kind": "synthetic_provider_observation"})
    activities.finish_activity(runtime, execution["owner_activity_id"], result_refs=[],
        unresolved=[{"reason": "No model process was started in this allocator fixture"}],
        followups=[], at=instant(current))


def transact(repository, operation):
    with repository.writer_lock():
        head, instance, runtime = repository.load()
        slots = GitSessionSlots(runtime, instance)
        result = operation(slots, instance, runtime)
        repository.save(head, instance, runtime)
        return result


def compete(root, iid, ready, release, output, name):
    repository = ResearchRepository(Path(root), iid)
    acquired = False
    try:
        if not ready.wait(120):
            raise AssertionError("probe race was not released")
        deadline = time.monotonic() + 120
        while True:
            try:
                acquired = transact(repository, lambda slots, instance, runtime:
                    admit(slots, instance, runtime, name, current=500))
                break
            except GitStateStoreLockError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(.02)
        output.put((name, acquired, None))
        if acquired and not release.wait(120):
            raise AssertionError("probe race cleanup was not released")
    except Exception as error:
        output.put((name, False, type(error).__name__ + ": " + str(error)))
        raise
    finally:
        if acquired:
            transact(repository, lambda slots, instance, runtime: finish(slots, runtime, name, 501))


class ProviderTests(unittest.TestCase):
    """No model execution or research activation is asserted by these fixtures."""
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.repository = self.make_repository()

    def make_repository(self, *, call_mode=False):
        iid = new_id("RI")
        config = {**deepcopy(DEFAULT_CONFIG), "scholarly_enabled": False,
            "model": MODEL, "operator_model": MODEL,
            "tier_models": {tier: MODEL for tier in ("low", "medium", "high")},
            "session_limits": None if call_mode else {"work": {MODEL: 3}, "operations": {MODEL: 1}},
            "work_calls": 10, "operations_calls": 10}
        instance = {"feature_version": 5, "id": iid, "workspace": str(self.root),
                    "config": config, **build_profiles(config)}
        runtime = {"feature_version": 5, "status": "ready", "executions": {},
                   "activities": {}, "reservations": {}, "provider_waits": {}}
        repository = ResearchRepository(self.root, iid)
        repository.initialize(instance, runtime)
        return repository

    def change(self, operation, *, repository=None):
        return transact(repository or self.repository, operation)

    def reject(self, identifier="EX-original", current=100):
        def operation(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, identifier, current=current))
            result = slots.provider_result(identifier, "claude", failure=FAILURE, current_time=current)
            finish(slots, runtime, identifier, current)
            return result
        return self.change(operation)

    def test_engine_provider_wait_disposition_survives_real_git_storage(self):
        from do_math.engine import ResearchEngine
        gate = self.reject()
        head, instance, runtime = self.repository.load()
        engine = ResearchEngine.__new__(ResearchEngine)
        engine.instance, engine.runtime = instance, runtime
        action = {"id": "AC-original", "role": "research_work", "target": "TK-fixture"}
        runtime["queue"] = [action]
        engine._hold_provider_action(action, "EX-original", gate, "Observed provider limit")
        waiting = runtime["waiting_actions"][action["id"]]
        self.repository.save(head, instance, runtime)
        loaded = self.repository.load()[2]["waiting_actions"][action["id"]]
        self.assertEqual(loaded, waiting)
        due = loaded["activity_wait"]["retry_at_timestamp"]
        self.assertIs(type(due), int)
        self.assertGreaterEqual(due, timestamp(loaded["activity_wait"]["retry_at"]))

    def test_restriction_blocks_both_pools_and_survives_another_owner(self):
        self.reject()
        iid = self.repository.load()[1]["id"]
        other = ResearchRepository(self.root, iid)
        def blocked(slots, instance, runtime):
            for pool in ("work", "operations"):
                self.assertFalse(admit(slots, instance, runtime, "EX-" + pool, pool, 399))
            self.assertEqual(slots.admission_reason, "provider_limit")
            self.assertEqual(slots.snapshot()["work"][MODEL]["used"], 0)
        self.change(blocked, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", "operations", 400), repository=other))
        self.assertFalse(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "work", 401)))
        def observed(slots, instance, runtime):
            slots.provider_result("EX-probe", "claude", current_time=402)
            finish(slots, runtime, "EX-probe", 402)
        self.change(observed, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "work", 403)))

    def test_late_success_does_not_release_a_newer_rejection(self):
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-old", current=1)))
        first = self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        second = self.change(lambda s, i, r: s.provider_result("EX-old", "claude", failure=FAILURE, current_time=401))
        self.change(lambda s, i, r: s.provider_result("EX-probe", "claude", current_time=402))
        _, instance, runtime = self.repository.load()
        current = GitSessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=403)["providers"]["claude"]
        self.assertEqual(current["generation"], first["generation"] + 1)
        self.assertEqual(current["generation"], second["generation"])
        self.assertEqual(current["state"], "waiting")

    def test_call_budget_mode_uses_provider_gate_without_model_capacity(self):
        self.repository = self.make_repository(call_mode=True)
        def reject(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, "EX-call", "operations", 1))
            slots.provider_result("EX-call", "claude", failure=FAILURE, current_time=1)
            finish(slots, runtime, "EX-call", 1)
            self.assertFalse(slots.snapshot()["operations"])
        self.change(reject)
        self.assertFalse(self.change(lambda s, i, r: admit(s, i, r, "EX-blocked", "operations", 2)))

    def test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time(self):
        first = self.reject()
        self.assertEqual(timestamp(first["retry_at"]), 400)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        def reject_again(slots, instance, runtime):
            waiting = slots.provider_result("EX-probe", "claude", failure=FAILURE,
                                            current_time=400, maximum_seconds=500)
            finish(slots, runtime, "EX-probe", 400)
            return waiting
        waiting = self.change(reject_again)
        self.assertEqual(timestamp(waiting["retry_at"]), 900)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-known", current=900)))
        known = {**FAILURE, "retry_at": instant(1500)}
        waiting = self.change(lambda s, i, r: s.provider_result("EX-known", "claude", failure=known, current_time=900))
        self.assertEqual(timestamp(waiting["retry_at"]), 1500)

    def test_probe_is_reconciled_only_after_confirmed_local_termination(self):
        self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-vanished", current=400)))
        head, instance, runtime = self.repository.load()
        observer = GitSessionSlots(runtime, instance, observer=True)
        observer.close()
        self.assertEqual(self.repository.load()[0], head)
        self.assertEqual(observer.provider_snapshot(current_time=500)["providers"]["claude"]["state"], "checking")
        self.change(lambda s, i, r: finish(s, r, "EX-vanished", 500))
        _, instance, runtime = self.repository.load()
        gate = GitSessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=500)["providers"]["claude"]
        self.assertEqual(gate["state"], "waiting")
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-replacement", "operations", 500)))

    def test_two_real_processes_admit_one_probe(self):
        self.reject()
        iid = self.repository.load()[1]["id"]
        context = multiprocessing.get_context("spawn")
        ready, release, output = context.Event(), context.Event(), context.Queue()
        children = [context.Process(target=compete,
            args=(str(self.root), iid, ready, release, output, name)) for name in ("EX-one", "EX-two")]
        try:
            for child in children:
                child.start()
            ready.set()
            outcomes = [output.get(timeout=180), output.get(timeout=180)]
            self.assertTrue(all(error is None for _, _, error in outcomes), outcomes)
            self.assertEqual(sum(success for _, success, _ in outcomes), 1, outcomes)
            _, instance, runtime = self.repository.load()
            gate = GitSessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=500)["providers"]["claude"]
            winner = next(name for name, success, _ in outcomes if success)
            self.assertEqual((gate["state"], gate["probe_owner"]), ("checking", winner))
        finally:
            release.set()
            for child in children:
                child.join(180)
                if child.is_alive():
                    child.terminate()
                    child.join(5)
                self.assertEqual(child.exitcode, 0)
            output.close()


if __name__ == "__main__":
    unittest.main()
