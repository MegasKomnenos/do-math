"""Activities and their executions: attempts, waits, transitions, recovery and the provider gate.

An activity (``activities``, layer 1) owns one piece of work and its attempts;
an execution (``execution_lifecycle``, layer 2) is one attempt that moves only
``queued -> starting -> running -> stopping -> ended``. An accepted output
needs the control receipt of a centrally sealed submission. The provider gate
(``provider_wait``, layer 1) is a wait record with a retry time, not a claim on
capacity.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math.activities import assign_execution, finish_activity, open_activity, validate_activities, wait_for
from do_math.control_transport import ControlTransport
from do_math.execution_lifecycle import (create_execution, end_preparation, end_recovered, record_submission_intent,
                                         recover_execution, transition_execution)
from do_math.provider_wait import gate_open, retry_time
from support.execution_inputs import sealed_maintenance_submission
from support.fakes.clock import FakeClock

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
        with self.assertRaisesRegex(ValueError, "an activity may wait only after its assigned executions ended"):
            wait_for(self.runtime, "AY-1", reason="input", condition={"kind": "input"},
                     next_owner={"kind": "user"}, at=TIME)
        second = self.execution("EX-2", continuation_of="EX-1")
        assign_execution(self.runtime, "AY-1", second)
        self.assertIn("EX-2: continuation is not an ended execution in the same activity",
                      validate_activities(self.runtime))

    def test_assignment_cannot_erase_an_unresolved_pause_wait(self):
        first = self.execution("EX-1")
        assign_execution(self.runtime, "AY-1", first)
        self.end_cancelled(first)
        wait_for(self.runtime, "AY-1", reason="user_pause", condition={"kind": "user_resume"},
                 next_owner="user", at=TIME)
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, "resolve the recorded activity wait before assigning an execution"):
            assign_execution(self.runtime, "AY-1", self.execution("EX-2", continuation_of="EX-1"))
        self.assertEqual(self.runtime, before)


class ExecutionLifecycleTests(unittest.TestCase):
    def running(self, execution_id="EX-1"):
        execution = create_execution(execution_id=execution_id, owner_activity_id="AY-1", actor_kind="ai",
                                     input_manifest={"source": "fixed"}, profile_ref="PF-1", created_at=TIME)
        transition_execution(execution, "starting", at=TIME)
        transition_execution(execution, "running", at=TIME)
        return execution

    def sealed_intent(self, execution_id):
        with tempfile.TemporaryDirectory() as workspace:
            return sealed_maintenance_submission(workspace, execution_id)[0]

    def test_accepted_output_requires_a_real_transport_receipt(self):
        execution = self.running()
        # Without a receipt, an execution cannot end with an accepted output.
        unreceipted = self.running("EX-unreceipted")
        transition_execution(unreceipted, "stopping", at=TIME)
        with self.assertRaisesRegex(ValueError, "accepted output lacks submission receipt"):
            transition_execution(deepcopy(unreceipted), "ended", at=TIME, outcome="output_accepted",
                                 disposition="receiver_validation_pending")
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root, clock=FakeClock())
            capability = transport.issue("EX-1", "GR-1")
            request = {**capability, "request_id": "CT-1", "kind": "submit_intent",
                       "payload": {"manifest": ["result.json"]}}
            receipt = transport.receive(request, publish=lambda _: {"state": "accepted", "published": True,
                                                                    "snapshot": "SN-1"})
        self.assertEqual((receipt["state"], receipt["execution_id"]), ("accepted", "EX-1"))
        record_submission_intent(execution, self.sealed_intent(execution["id"]), receipt, at=TIME)
        transition_execution(execution, "stopping", at=TIME)
        transition_execution(execution, "ended", at=TIME, outcome="output_accepted",
                             disposition="receiver_validation_pending")
        self.assertEqual(execution["outcome"], "output_accepted")

    def test_recovery_changes_only_the_recovered_execution_and_its_end_clears_the_disposition(self):
        lost, independent = self.running(), self.running("EX-2")
        recover_execution(lost, at=TIME)
        self.assertEqual((lost["status"], lost["recovery_disposition"]),
                         ("stopping", "reconcile_local_and_remote"))
        self.assertEqual(independent["status"], "running")
        end_recovered(lost, at=TIME, outcome="execution_incomplete", disposition="preserved_for_followup")
        self.assertEqual((lost["status"], lost["outcome"]), ("ended", "execution_incomplete"))
        # An ended execution is no longer protected from cleanup by its recovery disposition.
        self.assertNotIn("recovery_disposition", lost)
        with self.assertRaisesRegex(ValueError, "a ended execution has no recovery disposition"):
            recover_execution(lost, at=TIME)

    def test_submission_transition_replay_and_invalid_receipt_are_atomic(self):
        execution = self.running()
        intent = self.sealed_intent(execution["id"])
        receipt = {"id": "CT-submit", "kind": "submit_intent", "state": "accepted",
                   "execution_id": "EX-1", "received_at": TIME}
        before = deepcopy(execution)
        with self.assertRaisesRegex(ValueError, "submission receipt belongs to another execution"):
            record_submission_intent(execution, intent, {**receipt, "execution_id": "EX-other"})
        self.assertEqual(execution, before)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual(execution["status"], "stopping")
        once = deepcopy(execution)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual(execution, once)
        with self.assertRaisesRegex(ValueError, "submission intent requires a centrally sealed candidate"):
            record_submission_intent(execution, {"manifest": []}, receipt)
        self.assertEqual(execution, once)
        # A well-formed but different intent cannot replace the recorded one either.
        with self.assertRaisesRegex(ValueError, "a different submission intent or receipt was already recorded"):
            record_submission_intent(execution, {**intent, "candidate_id": "IN-another"}, receipt)
        self.assertEqual(execution, once)

    def test_failed_preparation_cannot_drop_an_existing_process(self):
        execution = create_execution(execution_id="EX-1", owner_activity_id="AY-1", actor_kind="ai",
                                     input_manifest=[], profile_ref="PF-1", created_at=TIME)
        execution["capacity"] = {"reservation_ids": [], "provider": None,
                                 "process": {"job_name": "existing-job"}, "local_termination": "unknown"}
        before = deepcopy(execution)
        with self.assertRaisesRegex(ValueError, "admitted preparation must reconcile reservations and process"):
            end_preparation(execution, at=TIME, stage="role_input", reason="input error", cancelled=False)
        self.assertEqual(execution, before)


class ProviderWaitTests(unittest.TestCase):
    def test_provider_wait_is_a_wait_record_not_a_capacity_claim(self):
        self.assertEqual(retry_time({}, 2, 100, 20, 60), 140)
        self.assertEqual(retry_time({}, 9, 100, 20, 60), 160)
        waiting = {"state": "waiting", "retry_at": 140}
        self.assertFalse(gate_open(waiting, 139))
        self.assertTrue(gate_open(waiting, 140))
        self.assertTrue(gate_open({"state": "available", "retry_at": None}, 0))
        self.assertFalse(gate_open({"state": "checking", "retry_at": 0}, 140))


if __name__ == "__main__":
    unittest.main()
