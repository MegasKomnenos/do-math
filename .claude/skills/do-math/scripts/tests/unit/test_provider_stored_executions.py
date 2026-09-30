"""The stored execution record: every step below round-trips through the real repository (layer 2).

The repository is ``ResearchRepository`` over the in-process Git port fake
(``support.storage_records.record_store``), so each publication passes the
storage contract and each reload reads the published state back. Settling an
admitted execution runs the real engine's provider mixin on the same
repository, with the Jobs port fake answering whether the ticket's Job is empty.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import activities
from do_math import execution_lifecycle as lifecycle
from do_math.activities import assign_execution, open_activity, validate_activities
from do_math.configuration import DEFAULT_CONFIG
from do_math.control_transport import ControlTransport
from do_math.engine import ResearchEngine
from do_math.execution_lifecycle import create_execution, record_submission_intent, transition_execution
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.session_slots import SessionSlots
from research_fixtures import current_state, sealed_maintenance_submission
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_runs import ProviderJobs, fake_ports
from support.storage_records import INSTANCE_ID, record_store

TIME = "2026-09-20T00:00:00+00:00"


def stored_audit_state(workspace):
    """``(instance, runtime, action)``: a maintenance activity ``AY-audit`` with its queued execution ``EX-audit``."""
    # Every stored state passes the current lifecycle gate.
    instance, runtime = current_state({"config": deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG),
                                       "workspace": str(workspace)},
                                      {"executions": {}, "queue": [], "reservations": {}})
    profile = next(p for p in instance["execution_profiles"].values() if p["role"] == "maintenance")
    open_activity(runtime, activity_id="AY-audit", activity_kind="maintenance", owner_ref="AC-audit", input_refs=[],
                  opened_at=TIME)
    execution = create_execution(execution_id="EX-audit", owner_activity_id="AY-audit", actor_kind="ai",
                                 input_manifest=[], profile_ref=profile_ref(profile), created_at=TIME)
    action = {"id": "AC-audit", "role": "maintenance"}
    execution.update(role="maintenance", action=deepcopy(action))
    assign_execution(runtime, "AY-audit", execution)
    runtime["queue"].append(action)
    return instance, runtime, action


class StoredExecutionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()
        self.backend = InProcessGit()
        self.repo = record_store(self.root / "repository", backend=self.backend, clock=self.clock)
        self.instance, self.runtime, self.action = stored_audit_state(self.root / "work")
        self.execution = self.runtime["executions"]["EX-audit"]
        self.head = self.repo.initialize(self.instance, self.runtime)

    def reload(self):
        self.head = self.repo.save_with_state(self.head, self.instance, self.runtime)[0]
        _, self.instance, self.runtime = self.repo.load(self.head)
        self.execution = self.runtime["executions"]["EX-audit"]

    def running(self):
        transition_execution(self.execution, "starting", at=TIME)
        transition_execution(self.execution, "running", at=TIME)

    def test_recovery_record_completion_round_trips_through_git(self):
        self.runtime["recoveries"] = {"RY-audit": {"id": "RY-audit", "started_at": TIME,
            "execution_ids": ["EX-audit"], "dispositions": [{"execution_id": "EX-audit",
            "local_termination_confirmed": False, "remote_termination": "unknown",
            "next_owner": "operator"}], "finished_at": TIME}}
        self.reload()
        self.assertEqual(self.runtime["recoveries"]["RY-audit"]["finished_at"], TIME)

    def test_confirmed_local_termination_releases_only_its_reservation(self):
        jobs = ProviderJobs(clock=self.clock)
        # Only work roles reserve a model slot; bind this execution to one so a
        # reservation exists whose return the recovery must confirm.
        profile = next(p for p in self.instance["execution_profiles"].values()
                       if p["role"] == "research_work" and p["actor_kind"] == "ai")
        self.execution.update(role="research_work", execution_profile_ref=profile_ref(profile))
        slots = SessionSlots(self.runtime, self.instance, jobs=jobs, clock=self.clock)
        transition_execution(self.execution, "starting", at=TIME)
        self.assertTrue(slots.acquire("EX-audit", profile=profile, execution=self.execution))
        self.assertTrue(self.execution["capacity"]["reservation_ids"])
        name = self.execution["launch_ticket"]["job_name"]
        slots.started("EX-audit", {"job_name": name}, at=TIME)
        self.reload()
        # The worker still runs in the ticket's named Job.
        job = jobs.launch([sys.executable, "codex_worker.py", "request.json"], name=name)

        def engine():
            return ResearchEngine(self.repo.repository, INSTANCE_ID, ports=fake_ports(self.clock, self.backend, jobs))
        owner = engine()
        self.assertFalse(owner._settle_recovered_execution("EX-audit", at=TIME))
        self.assertEqual(owner.runtime["executions"]["EX-audit"]["status"], "running")
        job.terminate()
        self.assertTrue(owner._settle_recovered_execution("EX-audit", at=TIME))
        owner._save()
        _, self.instance, self.runtime = self.repo.load()
        self.execution = self.runtime["executions"]["EX-audit"]
        self.assertEqual((self.execution["status"], self.execution["outcome"]), ("ended", "execution_incomplete"))
        self.assertEqual(self.execution["capacity"]["local_termination"], "confirmed")
        returned = [row for row in self.runtime["reservations"].values() if row["unit"] == "execution"]
        self.assertTrue(returned)
        for row in returned:
            self.assertEqual(row["returned"], row["reserved"])
        # A loaded ended execution is reconciled idempotently, not silently excluded.
        self.assertTrue(engine()._settle_recovered_execution("EX-audit", at=TIME))

    def test_pause_keeps_original_queue_binding_and_checkpoint_lineage(self):
        working = deepcopy(self.action)
        activities.bind_action(self.runtime, working, "AY-audit")
        self.assertEqual(self.runtime["queue"][0]["owner_activity_id"], "AY-audit")
        self.running()
        transition_execution(self.execution, "stopping", at=TIME, reason="user_pause")
        transition_execution(self.execution, "ended", at=TIME, outcome="cancelled")
        self.runtime["checkpoints"] = {"EX-audit": {"kind": "recovered", "reason": "test evidence"}}
        activities.continue_activity(self.runtime, "EX-audit", at=TIME, reason="user_pause",
                                     condition={"kind": "user_resume"}, next_owner="user")
        self.reload()
        activity = self.runtime["activities"]["AY-audit"]
        self.assertEqual(activity["status"], "waiting")
        self.assertEqual(activity["waiting"]["next_owner"], "user")
        activities.resume_activity(self.runtime, activity["id"], condition={"kind": "user_resume"}, at=TIME)
        action = self.runtime["queue"][0]
        successor = create_execution(execution_id="EX-resumed", owner_activity_id=action["owner_activity_id"],
            actor_kind="ai", input_manifest=[], profile_ref=self.execution["execution_profile_ref"],
            created_at=TIME, continuation_of=action["continuation_of"], context_origin=action["context_origin"])
        successor["role"] = "maintenance"
        assign_execution(self.runtime, "AY-audit", successor)
        self.reload()
        self.assertEqual(self.runtime["executions"]["EX-resumed"]["context_origin"], [])
        self.assertIn(self.runtime["executions"]["EX-resumed"]["continuation_of"], self.runtime["checkpoints"])
        self.assertEqual(validate_activities(self.runtime), [])

    def test_intent_stops_and_revokes_execution_authority_in_same_git_publication(self):
        """About 0.2 s, at the unit budget: two publications through the storage contract, one with artifacts, are the subject."""
        self.running()
        self.reload()
        transport = ControlTransport(self.root / "delivery", clock=self.clock)
        workspace = self.root / "submission-workspace"
        intent, artifacts = sealed_maintenance_submission(workspace, "EX-audit")
        binding = transport.issue("EX-audit", "GR-audit", workspace=workspace)
        request = {**binding, "request_id": "request-audit", "kind": "submit_intent",
                   "payload": {"draft_path": "draft.json"}}

        def publish(value):
            receipt = {"id": "CT-audit", "request_id": value["request_id"], "execution_id": "EX-audit",
                       "kind": "submit_intent", "state": "accepted", "received_at": TIME}
            record_submission_intent(self.execution, intent, receipt)
            self.assertEqual(self.execution["status"], "stopping")
            self.assertEqual(self.execution["authority_revocation"]["scope"], "execution_research")
            self.runtime["control_receipts"] = {receipt["id"]: receipt}
            self.head = self.repo.save_with_state(self.head, self.instance, self.runtime, artifacts=artifacts)[0]
            return {"state": "accepted", "published": True, "snapshot": self.head}
        receipt = transport.receive(request, publish=publish)
        _, _, stored = self.repo.load(receipt["snapshot"])
        self.assertEqual(stored["executions"]["EX-audit"]["authority_revocation"]["receipt_id"], "CT-audit")
        self.assertEqual(stored["executions"]["EX-audit"]["status"], "stopping")
        self.assertEqual(stored["control_receipts"]["CT-audit"]["state"], "accepted")

    def test_preparation_attempt_is_durable_before_input_and_failure(self):
        lifecycle.begin_preparation(self.execution, at=TIME)
        self.reload()
        self.assertEqual(self.execution["status"], "queued")
        self.assertEqual(self.execution["input_manifest"], [])
        lifecycle.end_preparation(self.execution, at=TIME, stage="context", reason="input unavailable",
                                  cancelled=False)
        self.reload()
        self.assertEqual((self.execution["status"], self.execution["outcome"]), ("ended", "start_failed"))
        self.assertEqual(self.execution["input_preparation"]["reason"], "input unavailable")
        self.assertEqual(self.execution["input_preparation"]["stage"], "context")
        # A pause during preparation ends the attempt as cancelled, not as a start failure.
        paused = create_execution(execution_id="EX-paused", owner_activity_id="AY-audit", actor_kind="ai",
                                  input_manifest=[], profile_ref="PF-1", created_at=TIME)
        lifecycle.begin_preparation(paused, at=TIME)
        lifecycle.end_preparation(paused, at=TIME, stage="role_input", reason="test interruption", cancelled=True)
        self.assertEqual((paused["outcome"], paused["input_preparation"]["stage"], paused["input_manifest"]),
                         ("cancelled", "role_input", []))


if __name__ == "__main__":
    unittest.main()
