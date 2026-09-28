"""Activities and their executions: attempts, waits, recovery, provider admission and the stored execution record."""
from pathlib import Path
from copy import deepcopy
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.activities import (assign_execution, finish_activity, open_activity,
                                validate_activities, wait_for)
from do_math.control_transport import ControlTransport
from do_math.execution_lifecycle import (create_execution, end_recovered, record_submission_intent,
                                         recover_execution, transition_execution)
from do_math.provider_wait import gate_open, retry_time
from do_math.execution_profiles import TIERS, build_profiles
from research_fixtures import bare_engine, git_init


TIME = "2026-09-20T00:00:00+00:00"


class ActivityContractTests(unittest.TestCase):
    def setUp(self):
        self.runtime = {"activities": {}, "executions": {}}
        open_activity(self.runtime, activity_id="AY-1", activity_kind="research_work",
                      owner_ref={"kind": "task", "id": "TK-1"}, input_refs=["IN-1"], opened_at=TIME)

    def execution(self, execution_id, continuation_of=None):
        return create_execution(execution_id=execution_id, owner_activity_id="AY-1", actor_kind="ai",
                                input_manifest={"id": "IN-1"}, profile_ref="PF-1", created_at=TIME,
                                continuation_of=continuation_of)

    def end_cancelled(self, execution):
        transition_execution(execution, "starting", at=TIME)
        transition_execution(execution, "stopping", at=TIME)
        transition_execution(execution, "ended", at=TIME, outcome="cancelled")

    def test_one_activity_owns_multiple_attempts_and_waits_after_them(self):
        first = self.execution("EX-1")
        assign_execution(self.runtime, "AY-1", first)
        self.end_cancelled(first)
        second = self.execution("EX-2", continuation_of="EX-1")
        assign_execution(self.runtime, "AY-1", second)
        self.end_cancelled(second)
        activity = wait_for(self.runtime, "AY-1", reason="provider unavailable",
                            condition={"kind": "provider_admission", "provider": "codex"},
                            next_owner={"kind": "engine"}, at=TIME)
        self.assertEqual(activity["status"], "waiting")
        self.assertEqual(activity["assigned_execution_ids"], ["EX-1", "EX-2"])
        self.assertEqual(validate_activities(self.runtime), [])
        finished = finish_activity(self.runtime, "AY-1", result_refs=[], unresolved=["provider availability"],
                                   followups=["retry"], at=TIME)
        self.assertEqual(finished["status"], "finished")

    def test_wait_and_continuation_reject_unjustified_relations(self):
        first = self.execution("EX-1")
        assign_execution(self.runtime, "AY-1", first)
        with self.assertRaisesRegex(ValueError, "ended"):
            wait_for(self.runtime, "AY-1", reason="input", condition={"kind": "input"},
                     next_owner={"kind": "user"}, at=TIME)
        second = self.execution("EX-2", continuation_of="EX-1")
        assign_execution(self.runtime, "AY-1", second)
        self.assertTrue(any("continuation" in error for error in validate_activities(self.runtime)))

    def test_assignment_cannot_erase_an_unresolved_pause_wait(self):
        first = self.execution("EX-1")
        assign_execution(self.runtime, "AY-1", first)
        self.end_cancelled(first)
        wait_for(self.runtime, "AY-1", reason="user_pause", condition={"kind": "user_resume"},
                 next_owner="user", at=TIME)
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, "wait"):
            assign_execution(self.runtime, "AY-1", self.execution("EX-2", continuation_of="EX-1"))
        self.assertEqual(self.runtime, before)


class ExecutionLifecycleTests(unittest.TestCase):
    def running(self):
        execution = create_execution(execution_id="EX-1", owner_activity_id="AY-1", actor_kind="ai",
                                     input_manifest={"source": "fixed"}, profile_ref="PF-1", created_at=TIME)
        transition_execution(execution, "starting", at=TIME)
        transition_execution(execution, "running", at=TIME)
        return execution

    def test_accepted_output_requires_a_real_transport_receipt(self):
        execution = self.running()
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            capability = transport.issue("EX-1", "GR-1")
            request = {**capability, "request_id": "CT-1", "kind": "submit_intent",
                       "payload": {"manifest": ["result.json"]}}
            receipt = transport.receive(request, publish=lambda _: {"state": "accepted", "published": True, "snapshot": "SN-1"})
        from research_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as workspace:
            intent, _ = sealed_maintenance_submission(workspace, execution['id'])
        record_submission_intent(execution, intent, receipt, at=TIME)
        transition_execution(execution, "stopping", at=TIME)
        transition_execution(execution, "ended", at=TIME, outcome="output_accepted",
                             disposition="receiver_validation_pending")
        self.assertEqual(execution["outcome"], "output_accepted")

    def test_recovery_changes_only_the_recovered_execution_and_its_end_clears_the_disposition(self):
        lost, independent = self.running(), self.running()
        independent["id"] = "EX-2"
        recover_execution(lost, at=TIME)
        self.assertEqual((lost["status"], lost["recovery_disposition"]),
                         ("stopping", "reconcile_local_and_remote"))
        self.assertEqual(independent["status"], "running")
        end_recovered(lost, at=TIME, outcome="execution_incomplete", disposition="preserved_for_followup")
        self.assertEqual((lost["status"], lost["outcome"]), ("ended", "execution_incomplete"))
        # An ended execution is no longer protected from cleanup by its recovery disposition.
        self.assertNotIn("recovery_disposition", lost)
        with self.assertRaisesRegex(ValueError, "no recovery disposition"):
            recover_execution(lost, at=TIME)

    def test_submission_transition_replay_and_invalid_receipt_are_atomic(self):
        execution = self.running()
        from research_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as workspace:
            intent, _ = sealed_maintenance_submission(workspace, execution['id'])
        receipt = {"id": "CT-submit", "kind": "submit_intent", "state": "accepted",
                   "execution_id": "EX-1", "received_at": TIME}
        before = deepcopy(execution)
        with self.assertRaises(ValueError):
            record_submission_intent(execution, intent, {**receipt, "execution_id": "EX-other"})
        self.assertEqual(execution, before)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual(execution["status"], "stopping")
        once = deepcopy(execution)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual(execution, once)
        with self.assertRaises(ValueError):
            record_submission_intent(execution, {"manifest": []}, receipt)
        self.assertEqual(execution, once)

    def test_failed_preparation_cannot_drop_an_existing_process(self):
        from do_math.execution_lifecycle import end_preparation
        execution = create_execution(execution_id="EX-1", owner_activity_id="AY-1", actor_kind="ai",
            input_manifest=[], profile_ref="PF-1", created_at=TIME)
        execution["capacity"] = {"reservation_ids": [], "provider": None,
                                 "process": {"job_name": "existing-job"}, "local_termination": "unknown"}
        before = deepcopy(execution)
        with self.assertRaisesRegex(ValueError, "reconcile"):
            end_preparation(execution, at=TIME, stage="role_input", reason="input error", cancelled=False)
        self.assertEqual(execution, before)


class ProviderAdmissionTests(unittest.TestCase):
    def test_provider_wait_is_a_wait_record_not_a_capacity_claim(self):
        self.assertEqual(retry_time({}, 2, 100, 20, 60), 140)
        self.assertEqual(retry_time({}, 9, 100, 20, 60), 160)
        waiting = {"state": "waiting", "retry_at": 140}
        self.assertFalse(gate_open(waiting, 139))
        self.assertTrue(gate_open(waiting, 140))
        self.assertTrue(gate_open({"state": "available", "retry_at": None}, 0))
        self.assertFalse(gate_open({"state": "checking", "retry_at": 0}, 140))

    def test_provider_mixin_records_structured_wait_on_refused_admission(self):
        from unittest.mock import create_autospec
        wait = {"kind": "provider_limit", "provider": "codex", "retry_at": "2026-09-20T00:01:00+00:00",
                "next_owner": "scheduler"}
        class Slots:
            admission_wait = wait
            def acquire(self, execution_id, *, profile, execution, current_time=None):
                return False
        engine = bare_engine({"config": {"provider_retry_initial_seconds": 20,
                                         "provider_retry_max_seconds": 60}}, {"queue": [], "status": "ready"})
        engine._session_slots = create_autospec(engine._session_slots, return_value=Slots())
        action = {"id": "AC-1", "model_selection": {"tier": "low", "model": "gpt-5.6-terra",
                  "assessment": None, "reason": "Provider-admission fixture assignment"}}
        profile, execution = {"id": "EP-1"}, {"id": "EX-1"}
        self.assertFalse(engine._provider_admit(action, "EX-1", profile=profile, execution=execution))
        self.assertEqual(action["dispatch_wait"], wait)
        self.assertIsNot(action["dispatch_wait"], wait)

    def test_provider_admission_reserves_runtime_capacity_and_settles_after_the_job_is_empty(self):
        config = {
            "observation_mode": "event_driven",
            "max_input_bytes": 16_384,
            "effort": "medium",
            "operator_effort": "medium",
            "operator_timeout_seconds": 60,
            "scholarly_enabled": True,
            "scholarly_server": None,
            "claude_only_assigned_model": False,
            "tier_models": {tier: "gpt-5.6-terra" for tier in TIERS},
            "session_limits": {
                "work": {"gpt-5.6-terra": 2},
            },
        }
        authored = build_profiles(config)
        profile = next(value for value in authored["execution_profiles"].values()
                       if value["role"] == "research_work" and value["actor_kind"] == "ai")
        engine = bare_engine({"workspace": tempfile.gettempdir(), "id": "RI-test", "config": config, **authored},
            {"executions": {}, "reservations": {}, "provider_waits": {}, "queue": [], "status": "ready"})
        execution = {"id": "EX-git", "role": profile["role"], "status": "starting"}
        action = {"id": "AC-git"}
        self.assertTrue(engine._provider_admit(action, "EX-git", profile=profile, execution=execution))
        self.assertIn("EX-git", engine.runtime["executions"])
        self.assertTrue(engine.runtime["reservations"])
        from unittest.mock import patch
        other_profile = next(value for value in authored["execution_profiles"].values()
                             if value["role"] == "research_work")
        other = {"id": "EX-independent", "role": "research_work", "status": "starting"}
        self.assertTrue(engine._provider_admit({"id": "AC-independent"}, other["id"],
                                               profile=other_profile, execution=other))
        slots = engine._session_slots()
        slots.started("EX-git", {"job_name": execution['launch_ticket']['job_name']}, at=TIME)
        self.assertEqual(execution["status"], "running")
        with patch("do_math.windows_job.named_job_empty", return_value=False):
            self.assertFalse(engine._settle_recovered_execution("EX-git", at=TIME))
        self.assertEqual(execution["status"], "running")
        with patch("do_math.windows_job.named_job_empty", return_value=True):
            self.assertTrue(engine._settle_recovered_execution("EX-git", at=TIME))
        self.assertEqual((execution["status"], execution["outcome"]), ("ended", "execution_incomplete"))
        self.assertEqual(execution["capacity"]["local_termination"], "confirmed")
        self.assertEqual(other["status"], "starting")
        self.assertTrue(all(row["state"] == "held" for row in engine.runtime["reservations"].values()
                            if row["owner_id"] == other["id"]))
        self.assertTrue(slots.release("EX-git"))


class StoredExecutionTests(unittest.TestCase):
    """Real family storage; only the OS Job observation is replaced."""
    def setUp(self):
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import profile_ref
        from do_math.repository import ResearchRepository
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        git_init(root)
        self.repo = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        from research_fixtures import current_state
        # Every stored state passes the current lifecycle gate.
        self.instance, self.runtime = current_state(
            {"config": deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG)},
            {"executions": {}, "queue": [], "reservations": {}})
        self.profile = next(p for p in self.instance["execution_profiles"].values()
                            if p["role"] == "maintenance")
        open_activity(self.runtime, activity_id="AY-audit", activity_kind="maintenance",
                      owner_ref="AC-audit", input_refs=[], opened_at=TIME)
        self.execution = create_execution(execution_id="EX-audit", owner_activity_id="AY-audit",
            actor_kind="ai", input_manifest=[], profile_ref=profile_ref(self.profile), created_at=TIME)
        self.action = {"id": "AC-audit", "role": "maintenance"}
        self.execution.update(role="maintenance", action=deepcopy(self.action))
        assign_execution(self.runtime, "AY-audit", self.execution)
        self.runtime["queue"].append(self.action)
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
        from unittest.mock import patch
        from do_math.execution_profiles import profile_ref
        from do_math.session_slots import SessionSlots
        # Only work roles reserve a model slot; bind this execution to one so a
        # reservation exists whose return the recovery must confirm.
        profile = next(p for p in self.instance["execution_profiles"].values()
                       if p["role"] == "research_work" and p["actor_kind"] == "ai")
        self.execution.update(role="research_work", execution_profile_ref=profile_ref(profile))
        slots = SessionSlots(self.runtime, self.instance)
        transition_execution(self.execution, "starting", at=TIME)
        self.assertTrue(slots.acquire("EX-audit", profile=profile, execution=self.execution))
        self.assertTrue(self.execution["capacity"]["reservation_ids"])
        slots.started("EX-audit", {"job_name": self.execution['launch_ticket']['job_name']}, at=TIME)
        self.reload()
        engine = bare_engine(self.instance, self.runtime)
        with patch("do_math.windows_job.named_job_empty", return_value=False):
            self.assertFalse(engine._settle_recovered_execution("EX-audit", at=TIME))
        self.assertEqual(self.execution["status"], "running")
        with patch("do_math.windows_job.named_job_empty", return_value=True):
            self.assertTrue(engine._settle_recovered_execution("EX-audit", at=TIME))
        self.reload()
        self.assertEqual((self.execution["status"], self.execution["outcome"]), ("ended", "execution_incomplete"))
        self.assertEqual(self.execution["capacity"]["local_termination"], "confirmed")
        for row in self.runtime["reservations"].values():
            if row["unit"] == "execution":
                self.assertEqual(row["returned"], row["reserved"])
        engine.instance, engine.runtime = self.instance, self.runtime
        # A loaded ended execution is reconciled idempotently, not silently excluded.
        self.assertTrue(engine._settle_recovered_execution("EX-audit", at=TIME))

    def test_pause_keeps_original_queue_binding_and_checkpoint_lineage(self):
        from do_math import activities
        working = deepcopy(self.action)
        activities.bind_action(self.runtime, working, "AY-audit")
        self.assertEqual(self.action["owner_activity_id"], "AY-audit")
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
        self.running()
        self.reload()
        transport = ControlTransport(Path(self.temporary.name) / "delivery")
        workspace=Path(self.temporary.name)/'submission-workspace'
        from research_fixtures import sealed_maintenance_submission
        intent, artifacts = sealed_maintenance_submission(workspace, 'EX-audit')
        binding = transport.issue("EX-audit", "GR-audit", workspace=workspace)
        request = {**binding, "request_id": "request-audit", "kind": "submit_intent", "payload": {"draft_path": "draft.json"}}
        def publish(value):
            receipt = {"id": "CT-audit", "request_id": value["request_id"], "execution_id": "EX-audit",
                       "kind": "submit_intent", "state": "accepted", "received_at": TIME}
            record_submission_intent(self.execution, intent, receipt)
            self.assertEqual(self.execution["status"], "stopping")
            self.assertEqual(self.execution["authority_revocation"]["scope"], "execution_research")
            self.runtime["control_receipts"] = {receipt["id"]: receipt}
            self.head=self.repo.save_with_state(self.head,self.instance,self.runtime,artifacts=artifacts)[0]
            return {"state": "accepted", "published": True, "snapshot": self.head}
        receipt = transport.receive(request, publish=publish)
        _, _, stored = self.repo.load(receipt["snapshot"])
        self.assertEqual(stored["executions"]["EX-audit"]["authority_revocation"]["receipt_id"], "CT-audit")
        self.assertEqual(stored["control_receipts"]["CT-audit"]["state"], "accepted")

    def test_preparation_attempt_is_durable_before_input_and_failure(self):
        from do_math import execution_lifecycle as lifecycle
        lifecycle.begin_preparation(self.execution, at=TIME)
        self.reload()
        self.assertEqual(self.execution["status"], "queued")
        self.assertEqual(self.execution["input_manifest"], [])
        lifecycle.end_preparation(self.execution, at=TIME, stage="context", reason="input unavailable", cancelled=False)
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
    unittest.main(verbosity=2)
