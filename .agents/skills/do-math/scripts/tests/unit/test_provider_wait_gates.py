"""Provider gates across stored transactions (``session_slots.SessionSlots``, ``provider_engine``; layer 2), moved
from ``test_provider_wait``.

A provider's usage-limit rejection closes its gate, raises its generation and
sets a retry time; while it is closed, work and operational roles are refused
with ``provider_limit``, and at the retry time one probe is let through. Every
step here is one transaction of the real ``ResearchRepository`` (writer lock,
load, publication through the storage contract; ``support.provider_state``)
on the Git port's fake, as the legacy tests made them on real Git; the session
slots get the clock and Jobs port fakes. Provider results and times are
synthetic, and each call's time is passed in. The race of two real processes
for one probe is ``boundary.test_provider_wait_probe_race``.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.provider_wait import epoch_seconds
from do_math.session_slots import SessionSlots
from provider_fixtures import PROVIDER_LIMIT_FAILURE, PROVIDER_MODEL, admit, finish, instant, report
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.fakes.jobs import FakeJobs
from support.provider_runs import fake_ports
from support.provider_state import gate_store, transact
from support.storage_records import INSTANCE_ID, record_store


class ProviderTests(unittest.TestCase):
    """No model execution or research activation is asserted by these fixtures."""
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock, self.backend, self.jobs = FakeClock(), InProcessGit(), FakeJobs()
        self.repository = gate_store(self.root, clock=self.clock, backend=self.backend)

    def another_owner(self):
        """A second repository object on the same storage, with its own caches."""
        return record_store(self.root / 'repository', backend=self.backend, clock=self.clock)

    def change(self, operation, *, repository=None):
        return transact(repository or self.repository, operation, clock=self.clock, jobs=self.jobs)

    def observer(self, instance, runtime):
        return SessionSlots(runtime, instance, observer=True, clock=self.clock, jobs=self.jobs)

    def reject(self, identifier="EX-original", current=100):
        def operation(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, identifier, current=current))
            result = report(slots, instance, identifier, current, PROVIDER_LIMIT_FAILURE)
            finish(slots, runtime, identifier, current)
            return result
        return self.change(operation)

    def test_provider_limited_request_waits_in_queue_through_real_git_storage(self):
        def rejected(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, "EX-original", current=100))
            gate = report(slots, instance, "EX-original", 100, PROVIDER_LIMIT_FAILURE)
            finish(slots, runtime, "EX-original", 100, close_activity=False)
            return gate
        gate = self.change(rejected)
        engine = ResearchEngine(self.repository.repository, INSTANCE_ID,
                                ports=fake_ports(self.clock, self.backend, self.jobs))
        head, instance, runtime = engine.head, engine.instance, engine.runtime
        reference = instance["role_profile_refs"]["research_work"][-1]
        action = {"id": "AC-original", "role": "research_work", "target": "TK-fixture",
                  "profile_ref": deepcopy(reference),
                  "model_selection": {"tier": "high", "model": PROVIDER_MODEL, "assessment": None,
                                      "reason": "Provider-limit fixture assignment"}}
        runtime["queue"] = [action]
        # One second before the gate's retry time (the legacy test set the clock port's wall time).
        self.clock.set_wall(datetime.fromtimestamp(399, timezone.utc))
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
        self.repository.save_with_state(head, instance, runtime)
        loaded = self.another_owner().load()[2]
        self.assertEqual([item for item in loaded["queue"] if item["id"] == action["id"]], [queued])
        self.assertEqual(loaded["activities"]["AY-EX-original"], activity)

    def test_restriction_blocks_work_and_operational_roles_and_survives_another_owner(self):
        """About 0.2 s, at the 0.2 s unit budget: six transactions each publish through the storage contract, the persistence under test."""
        self.reject()
        other = self.another_owner()
        def blocked(slots, instance, runtime):
            for role in ("research_work", "maintenance"):
                self.assertFalse(admit(slots, instance, runtime, "EX-" + role, role, 399))
                self.assertEqual(slots.admission_reason, "provider_limit")
            self.assertEqual(slots.snapshot()[PROVIDER_MODEL]["used"], 0)
        self.change(blocked, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", "maintenance", 400), repository=other))
        self.assertFalse(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "research_work", 401)))
        def observed(slots, instance, runtime):
            report(slots, instance, "EX-probe", 402)
            finish(slots, runtime, "EX-probe", 402)
        self.change(observed, repository=other)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-next", "research_work", 403)))

    def test_late_success_does_not_release_a_newer_rejection(self):
        """About 0.25 s, over the 0.2 s unit budget: five transactions each publish through the storage contract, as the reports' order is stored."""
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-old", current=1)))
        first = self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        second = self.change(lambda s, i, r: report(s, i, "EX-old", 401, PROVIDER_LIMIT_FAILURE))
        self.change(lambda s, i, r: report(s, i, "EX-probe", 402))
        _, instance, runtime = self.repository.load()
        current = self.observer(instance, runtime).provider_snapshot(current_time=403)["providers"]["claude"]
        self.assertEqual(current["generation"], first["generation"] + 1)
        self.assertEqual(current["generation"], second["generation"])
        self.assertEqual(current["state"], "waiting")

    def test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time(self):
        first = self.reject()
        self.assertEqual(epoch_seconds(first["retry_at"]), 400)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-probe", current=400)))
        def reject_again(slots, instance, runtime):
            waiting = report(slots, instance, "EX-probe", 400, PROVIDER_LIMIT_FAILURE, provider_retry_max_seconds=500)
            finish(slots, runtime, "EX-probe", 400)
            return waiting
        waiting = self.change(reject_again)
        self.assertEqual(epoch_seconds(waiting["retry_at"]), 900)
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-known", current=900)))
        known = {**PROVIDER_LIMIT_FAILURE, "retry_at": instant(1500)}
        waiting = self.change(lambda s, i, r: report(s, i, "EX-known", 900, known))
        self.assertEqual(epoch_seconds(waiting["retry_at"]), 1500)

    def test_probe_is_reconciled_only_after_confirmed_local_termination(self):
        self.reject()
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-vanished", current=400)))
        head, instance, runtime = self.repository.load()
        observer = self.observer(instance, runtime)
        self.assertEqual(self.repository.load()[0], head)
        self.assertEqual(observer.provider_snapshot(current_time=500)["providers"]["claude"]["state"], "checking")
        self.change(lambda s, i, r: finish(s, r, "EX-vanished", 500))
        _, instance, runtime = self.repository.load()
        gate = self.observer(instance, runtime).provider_snapshot(current_time=500)["providers"]["claude"]
        self.assertEqual(gate["state"], "waiting")
        self.assertTrue(self.change(lambda s, i, r: admit(s, i, r, "EX-replacement", "maintenance", 500)))


if __name__ == "__main__":
    unittest.main()
