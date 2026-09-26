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
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_lifecycle as lifecycle
from do_math.engine import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.git_store import GitStateStoreLockError
from do_math.repository import ResearchRepository, new_id
from do_math.session_slots import SessionSlots
from do_math.provider_wait import epoch_seconds

MODEL = "claude-opus-5"
FAILURE = {"kind": "provider_limit", "provider": "claude", "retry_at": None,
           "evidence_ref": "synthetic-provider-limit.json", "limit_windows": []}


def instant(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()


def admit(slots, instance, runtime, identifier, role="research_work", current=100):
    """Admit a work role (a model slot) or an operational role such as maintenance (no slot)."""
    reference = instance["role_profile_refs"][role][-1]
    profile = instance["execution_profiles"][reference["id"]]
    aid = "AY-" + identifier
    execution = lifecycle.create_execution(execution_id=identifier, owner_activity_id=aid,
        actor_kind="ai", input_manifest=[], profile_ref=profile_ref(profile), created_at=instant(current))
    execution["role"] = role
    if not slots.acquire(identifier, profile=profile, execution=execution, current_time=current):
        return False
    activities.open_activity(runtime, activity_id=aid, activity_kind=role,
        owner_ref=instance["id"], input_refs=[], opened_at=instant(current))
    activities.assign_execution(runtime, aid, execution)
    return True


def report(slots, instance, identifier, current, failure=None, **config):
    """Apply a synthetic runner result: a provider_limit failure, or a completed call."""
    result = ({"status": "failed", "error_kind": "provider_limit", "failure": failure}
              if failure is not None else {"status": "completed"})
    return slots.provider_result_from_run(identifier, result, {**instance["config"], **config},
                                          current_time=current)


def finish(slots, runtime, identifier, current, *, close_activity=True):
    if not slots.release(identifier):
        raise AssertionError("test execution without an acknowledged process did not settle")
    execution = runtime["executions"][identifier]
    lifecycle.transition_execution(execution, "stopping", at=instant(current), stop_phase="terminating")
    lifecycle.transition_execution(execution, "ended", at=instant(current), outcome="start_failed",
        disposition={"kind": "synthetic_provider_observation"})
    if not close_activity:
        return
    activities.finish_activity(runtime, execution["owner_activity_id"], result_refs=[],
        unresolved=[{"reason": "No model process was started in this allocator fixture"}],
        followups=[], at=instant(current))


def transact(repository, operation):
    with repository.writer_lock():
        head, instance, runtime = repository.load()
        slots = SessionSlots(runtime, instance)
        result = operation(slots, instance, runtime)
        repository.save_with_state(head, instance, runtime)[0]
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

    def make_repository(self):
        iid = new_id("RI")
        config = {**deepcopy(DEFAULT_CONFIG), "scholarly_enabled": False,
            "tier_models": {tier: MODEL for tier in ("low", "medium", "high")},
            "session_limits": {"work": {MODEL: 3}},
             }
        from research_fixtures import current_state
        instance, runtime = current_state(
            {"id": iid, "workspace": str(self.root), "config": config, **build_profiles(config)},
            {"status": "ready", "executions": {}, "activities": {}, "reservations": {}, "provider_waits": {}})
        repository = ResearchRepository(self.root, iid)
        repository.initialize(instance, runtime)
        return repository

    def change(self, operation, *, repository=None):
        return transact(repository or self.repository, operation)

    def reject(self, identifier="EX-original", current=100):
        def operation(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, identifier, current=current))
            result = report(slots, instance, identifier, current, FAILURE)
            finish(slots, runtime, identifier, current)
            return result
        return self.change(operation)

    def test_provider_limited_request_waits_in_queue_through_real_git_storage(self):
        from research_fixtures import bare_engine
        def rejected(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, "EX-original", current=100))
            gate = report(slots, instance, "EX-original", 100, FAILURE)
            finish(slots, runtime, "EX-original", 100, close_activity=False)
            return gate
        gate = self.change(rejected)
        head, instance, runtime = self.repository.load()
        engine = bare_engine(instance, runtime)
        reference = instance["role_profile_refs"]["research_work"][-1]
        action = {"id": "AC-original", "role": "research_work", "target": "TK-fixture",
                  "profile_ref": deepcopy(reference),
                  "model_selection": {"tier": "high", "model": MODEL, "assessment": None,
                                      "reason": "Provider-limit fixture assignment"}}
        runtime["queue"] = [action]
        with patch("do_math.session_slots.time.time", return_value=399):
            engine._requeue_provider_action(action, "EX-original", gate)
        self.assertNotIn(action["id"], runtime.get("waiting_actions", {}))
        queued, = [item for item in runtime["queue"] if item["id"] == action["id"]]
        self.assertEqual(queued["recovery"], {"execution_id": "EX-original", "reason": "provider admission retry",
                                              "provider_generation": gate["generation"]})
        wait = queued["dispatch_wait"]
        self.assertEqual((wait["kind"], wait["provider"], wait["next_owner"]),
                         ("provider_limit", "claude", "scheduler"))
        self.assertEqual(epoch_seconds(wait["retry_at"]), epoch_seconds(gate["retry_at"]))
        activity = runtime["activities"]["AY-EX-original"]
        self.assertEqual((activity["status"], activity["waiting"]["condition"]), ("waiting", wait))
        self.repository.save_with_state(head, instance, runtime)[0]
        loaded = self.repository.load()[2]
        self.assertEqual([item for item in loaded["queue"] if item["id"] == action["id"]], [queued])
        self.assertEqual(loaded["activities"]["AY-EX-original"], activity)

    def test_restriction_blocks_work_and_operational_roles_and_survives_another_owner(self):
        self.reject()
        iid = self.repository.load()[1]["id"]
        other = ResearchRepository(self.root, iid)
        def blocked(slots, instance, runtime):
            for role in ("research_work", "maintenance"):
                self.assertFalse(admit(slots, instance, runtime, "EX-" + role, role, 399))
                self.assertEqual(slots.admission_reason, "provider_limit")
            self.assertEqual(slots.snapshot()[MODEL]["used"], 0)
        self.change(blocked, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", "maintenance", 400), repository=other))
        self.assertFalse(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "research_work", 401)))
        def observed(slots, instance, runtime):
            report(slots, instance, "EX-probe", 402)
            finish(slots, runtime, "EX-probe", 402)
        self.change(observed, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "research_work", 403)))

    def test_late_success_does_not_release_a_newer_rejection(self):
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-old", current=1)))
        first = self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        second = self.change(lambda s, i, r: report(s, i, "EX-old", 401, FAILURE))
        self.change(lambda s, i, r: report(s, i, "EX-probe", 402))
        _, instance, runtime = self.repository.load()
        current = SessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=403)["providers"]["claude"]
        self.assertEqual(current["generation"], first["generation"] + 1)
        self.assertEqual(current["generation"], second["generation"])
        self.assertEqual(current["state"], "waiting")


    def test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time(self):
        first = self.reject()
        self.assertEqual(epoch_seconds(first["retry_at"]), 400)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        def reject_again(slots, instance, runtime):
            waiting = report(slots, instance, "EX-probe", 400, FAILURE, provider_retry_max_seconds=500)
            finish(slots, runtime, "EX-probe", 400)
            return waiting
        waiting = self.change(reject_again)
        self.assertEqual(epoch_seconds(waiting["retry_at"]), 900)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-known", current=900)))
        known = {**FAILURE, "retry_at": instant(1500)}
        waiting = self.change(lambda s, i, r: report(s, i, "EX-known", 900, known))
        self.assertEqual(epoch_seconds(waiting["retry_at"]), 1500)

    def test_probe_is_reconciled_only_after_confirmed_local_termination(self):
        self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-vanished", current=400)))
        head, instance, runtime = self.repository.load()
        observer = SessionSlots(runtime, instance, observer=True)
        self.assertEqual(self.repository.load()[0], head)
        self.assertEqual(observer.provider_snapshot(current_time=500)["providers"]["claude"]["state"], "checking")
        self.change(lambda s, i, r: finish(s, r, "EX-vanished", 500))
        _, instance, runtime = self.repository.load()
        gate = SessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=500)["providers"]["claude"]
        self.assertEqual(gate["state"], "waiting")
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-replacement", "maintenance", 500)))

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
            gate = SessionSlots(runtime, instance, observer=True).provider_snapshot(current_time=500)["providers"]["claude"]
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
