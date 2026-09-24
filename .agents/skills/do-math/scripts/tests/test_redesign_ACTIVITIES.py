"""Feature-5 activity, execution, control, and provider-wait contracts."""
from pathlib import Path
from copy import deepcopy
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.activities import (assign_execution, finish_activity, open_activity,
                                validate_activities, wait_for)
from do_math.control_transport import ControlTransport
from do_math.execution_lifecycle import (create_execution, record_submission_intent,
                                         recover_execution, transition_execution)
from do_math.parallel import ModelCalls
from do_math.provider_engine import ProviderEngineMixin
from do_math.provider_wait import provider_wait_disposition
from do_math.execution_profiles import TIERS, build_profiles


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
        transition_execution(execution, "stopping", at=TIME, stop_phase="terminating")
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

    def test_pause_and_queued_recovery_preserve_obligation_without_inventing_context(self):
        from do_math import activities
        action = {"id": "AC-local", "role": "research_work"}
        self.runtime["queue"] = [action]
        working = deepcopy(action)
        activities.bind_action(self.runtime, working, "AY-1")
        self.assertEqual(action["owner_activity_id"], "AY-1")
        execution = self.execution("EX-1")
        execution["action"] = working
        assign_execution(self.runtime, "AY-1", execution)
        recovered = activities.requeue_recovered_execution(self.runtime, "EX-1", at=TIME)
        self.assertEqual((execution["status"], execution["outcome"]), ("ended", "cancelled"))
        self.assertEqual(recovered["continuation_of"], "EX-1")
        activities.continue_activity(self.runtime, "EX-1", at=TIME, reason="user_pause",
                                     condition={"kind": "user_resume"}, next_owner="user")
        self.assertEqual(len(self.runtime["queue"]), 1)
        self.assertEqual(self.runtime["activities"]["AY-1"]["waiting"]["next_owner"], "user")
        self.assertEqual(recovered["context_origin"], [])
        self.assertEqual(validate_activities(self.runtime), [])

    def test_queued_recovery_does_not_discard_a_held_reservation(self):
        from do_math.activities import requeue_recovered_execution
        execution = self.execution("EX-1")
        execution["action"] = {"id": "AC-1", "role": "research_work"}
        assign_execution(self.runtime, "AY-1", execution)
        self.runtime["reservations"] = {"RS-1": {"owner_id": "EX-1", "state": "held"}}
        before = deepcopy(self.runtime)
        with self.assertRaisesRegex(ValueError, "reconciliation"):
            requeue_recovered_execution(self.runtime, "EX-1", at=TIME)
        self.assertEqual(self.runtime, before)

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
        from v5_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as workspace:
            intent, _ = sealed_maintenance_submission(workspace, execution['id'])
        record_submission_intent(execution, intent, receipt, at=TIME)
        transition_execution(execution, "stopping", at=TIME, stop_phase="terminating")
        transition_execution(execution, "ended", at=TIME, outcome="output_accepted",
                             disposition="receiver_validation_pending")
        self.assertEqual(execution["outcome"], "output_accepted")

    def test_control_rejects_an_unconfirmed_boundary_and_request_id_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            capability = transport.issue("EX-1", "GR-1")
            request = {**capability, "request_id": "CT-1", "kind": "safety_boundary",
                       "payload": {"inflight_calls": True}}
            self.assertEqual(transport.receive(request)["state"], "rejected")
            self.assertEqual(transport.receive(request)["state"], "rejected")
            with self.assertRaisesRegex(ValueError, "different content"):
                transport.receive({**request, "payload": {"inflight_calls": False}})
            self.assertNotIn("capability", transport.records()[0])

    def test_recovery_changes_only_the_observed_execution(self):
        lost, independent = self.running(), self.running()
        independent["id"] = "EX-2"
        recover_execution(lost, {"fact": "previous_engine_lost"}, at=TIME)
        self.assertEqual((lost["status"], lost["recovery_disposition"]),
                         ("stopping", "reconcile_local_and_remote"))
        self.assertEqual(independent["status"], "running")
        recover_execution(lost, {"fact": "termination_barrier_confirmed"}, at=TIME)
        self.assertEqual((lost["status"], lost["outcome"]), ("ended", "execution_incomplete"))

    def test_submission_transition_replay_and_invalid_receipt_are_atomic(self):
        execution = self.running()
        from v5_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as workspace:
            intent, _ = sealed_maintenance_submission(workspace, execution['id'])
        receipt = {"id": "CT-submit", "kind": "submit_intent", "state": "accepted",
                   "execution_id": "EX-1", "received_at": TIME}
        before = deepcopy(execution)
        with self.assertRaises(ValueError):
            record_submission_intent(execution, intent, {**receipt, "execution_id": "EX-other"})
        self.assertEqual(execution, before)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual((execution["status"], execution["stop_phase"]), ("stopping", "terminating"))
        once = deepcopy(execution)
        record_submission_intent(execution, intent, receipt)
        self.assertEqual(execution, once)
        with self.assertRaises(ValueError):
            record_submission_intent(execution, {"manifest": []}, receipt)
        self.assertEqual(execution, once)

    def test_received_but_unpublished_request_is_published_on_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            binding = transport.issue("EX-receive", "GR-receive")
            ControlTransport.worker_submit(binding, request_id="request-receive", kind="submit_intent",
                                           payload={"manifest": []})
            self.assertEqual(transport.pump()[0]["state"], "received")
            recovered = ControlTransport(root)
            calls = []
            def publish(request):
                calls.append(request)
                return {"state": "accepted", "published": True, "snapshot": "verified-CAS"}
            self.assertEqual(recovered.pump(publish)[0]["state"], "accepted")
            self.assertEqual(len(calls), 1)

    def test_preparation_failure_and_pause_have_distinct_terminal_outcomes(self):
        from do_math.execution_lifecycle import begin_preparation, end_preparation
        for cancelled, expected in ((False, "start_failed"), (True, "cancelled")):
            with self.subTest(cancelled=cancelled):
                execution = create_execution(execution_id="EX-1", owner_activity_id="AY-1", actor_kind="ai",
                    input_manifest=[], profile_ref="PF-1", created_at=TIME)
                begin_preparation(execution, at=TIME)
                self.assertEqual(execution["status"], "queued")
                end_preparation(execution, at=TIME, stage="role_input", reason="test interruption", cancelled=cancelled)
                self.assertEqual(execution["outcome"], expected)
                self.assertEqual(execution["input_preparation"]["stage"], "role_input")
                self.assertEqual(execution["input_manifest"], [])

    def test_failed_preparation_cannot_drop_an_existing_process(self):
        from do_math.execution_lifecycle import end_preparation
        execution = create_execution(execution_id="EX-1", owner_activity_id="AY-1", actor_kind="ai",
            input_manifest=[], profile_ref="PF-1", created_at=TIME)
        execution["process"] = {"job_name": "existing-job"}
        before = deepcopy(execution)
        with self.assertRaisesRegex(ValueError, "reconcile"):
            end_preparation(execution, at=TIME, stage="role_input", reason="input error", cancelled=False)
        self.assertEqual(execution, before)


class ProviderAndParallelTests(unittest.TestCase):
    def test_provider_wait_is_a_wait_record_not_a_capacity_claim(self):
        disposition = provider_wait_disposition(model="gpt-5.6-terra", attempts=2, current=100,
                                                initial=20, maximum=60)
        self.assertEqual((disposition["kind"], disposition["state"], disposition["provider"]),
                         ("provider_admission", "waiting", "codex"))
        self.assertEqual(disposition["retry_at_timestamp"], 140)

    def test_provider_mixin_records_structured_waits_on_admission_and_failure(self):
        class Slots:
            admission_reason = "provider_limit"
            admission_wait = {"kind": "provider_limit", "provider": "codex", "next_owner": "scheduler"}
            def acquire(self, *args, **kwargs):
                return False
        class Harness(ProviderEngineMixin):
            def __init__(self):
                self._slots = Slots()
                self.runtime = {"queue": [], "status": "ready"}
                self.instance = {"config": {"model": "gpt-5.6-terra", "provider_retry_initial_seconds": 20,
                                            "provider_retry_max_seconds": 60}}
            def _session_mode(self):
                return True
            def _remove_action(self, action):
                self.runtime["queue"] = [item for item in self.runtime["queue"] if item is not action]
        engine = Harness()
        action = {"id": "AC-1", "model_selection": "gpt-5.6-terra"}
        profile, execution = {"id": "EP-1"}, {"id": "EX-1"}
        self.assertFalse(engine._provider_admit(action, "EX-1", "work", "gpt-5.6-terra", profile=profile, execution=execution))
        self.assertEqual(action["dispatch_wait"]["activity_wait"]["kind"], "provider_admission")
        engine.runtime["queue"] = [action]
        engine._hold_provider_action(action, "EX-1", {"provider": "codex", "generation": 1, "retry_at": None}, "quota")
        held = engine.runtime["waiting_actions"]["AC-1"]
        self.assertEqual(held["activity_wait"]["state"], "waiting")
        self.assertEqual(engine.runtime["status"], "waiting")

    def test_provider_mixin_uses_git_runtime_reservation_not_sqlite(self):
        config = {
            "observation_mode": "event_driven",
            "max_input_bytes": 16_384,
            "effort": "medium",
            "operator_effort": "medium",
            "operator_timeout_seconds": 60,
            "tier_models": {tier: "gpt-5.6-terra" for tier in TIERS},
            "session_limits": {
                "work": {"gpt-5.6-terra": 1},
                "operations": {"gpt-5.6-terra": 1},
            },
        }
        authored = build_profiles(config)
        profile = next(value for value in authored["execution_profiles"].values()
                       if value["role"] == "research_preparation" and value["actor_kind"] == "ai")
        class Harness(ProviderEngineMixin):
            def __init__(self):
                self._slots = None
                self.runtime = {"executions": {}, "reservations": {}, "provider_waits": {}, "queue": [], "status": "ready"}
                self.instance = {"workspace": tempfile.gettempdir(), "id": "RI-test", "config": config, **authored}
        engine = Harness()
        execution = {"id": "EX-git", "role": profile["role"], "status": "starting"}
        action = {"id": "AC-git"}
        model = profile["ai"]["model"]
        self.assertTrue(engine._provider_admit(action, "EX-git", profile["budget_kind"], model,
                                               profile=profile, execution=execution))
        self.assertIn("EX-git", engine.runtime["executions"])
        self.assertTrue(engine.runtime["reservations"])
        self.assertEqual(engine._provider_status()["source"], "git_runtime")
        from unittest.mock import patch
        other_profile = next(value for value in authored["execution_profiles"].values()
                             if value["role"] == "research_work")
        other = {"id": "EX-independent", "role": "research_work", "status": "starting"}
        self.assertTrue(engine._provider_admit({"id": "AC-independent"}, other["id"],
            other_profile["budget_kind"], model, profile=other_profile, execution=other))
        slots = engine._provider_slots()
        slots.started("EX-git", {"job_name": "local-test-job"})
        transition_execution(execution, "running", at=TIME)
        with patch("do_math.windows_job.named_job_empty", return_value=False):
            self.assertFalse(engine._settle_recovered_execution("EX-git", at=TIME, outcome="cancelled"))
        self.assertEqual(execution["status"], "running")
        with patch("do_math.windows_job.named_job_empty", return_value=True):
            self.assertTrue(engine._settle_recovered_execution("EX-git", at=TIME, outcome="cancelled"))
        self.assertEqual((execution["status"], execution["outcome"]), ("ended", "cancelled"))
        self.assertEqual(execution["capacity"]["local_termination"], "confirmed")
        self.assertEqual(other["status"], "starting")
        self.assertTrue(all(row["state"] == "held" for row in engine.runtime["reservations"].values()
                            if row["owner_id"] == other["id"]))
        self.assertTrue(slots.release("EX-git"))

    def test_child_process_round_trips_submit_receipt_self_check_and_close(self):
        package_root = str(Path(__file__).resolve().parents[1])
        def child(statement, binding):
            environment = {**os.environ, "PYTHONPATH": package_root + os.pathsep + os.environ.get("PYTHONPATH", "")}
            result = subprocess.run([sys.executable, "-c", statement, json.dumps(binding)], capture_output=True,
                                    text=True, check=True, env=environment)
            return json.loads(result.stdout)
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            binding = transport.issue("EX-1", "GR-1")
            submit = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.worker_submit(b, request_id='CT-1', kind='submit_intent', payload={'manifest':['result.json']})))"
            self.assertEqual(child(submit, binding)["state"], "submitted")
            published = []
            receipts = transport.pump(lambda request: (published.append(request) or {"state": "accepted", "published": True, "snapshot": "SN-1", "publication_id": "PR-1"}))
            self.assertEqual(receipts[0]["state"], "accepted")
            query = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.wait_receipt(b, 'CT-1', 0)))"
            self.assertEqual(child(query, binding)["snapshot"], "SN-1")
            recovered = ControlTransport(root)
            self.assertEqual(recovered.pump(lambda _: self.fail("published request must not republish"))[0]["publication_id"], "PR-1")
            transport.request_self_check(binding, self_check_id="SC-1", payload={"obligation": "report scope"})
            poll = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1')))"
            self.assertEqual(child(poll, binding)["payload"]["obligation"], "report scope")
            reply = "import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1', response={'status':'complete'})))"
            self.assertEqual(child(reply, binding)["state"], "submitted")
            self.assertEqual(transport.pump(lambda _: {"state": "accepted", "published": True, "snapshot": "SN-2"})[-1]["kind"], "self_check_response")
            transport.close(binding, reason="execution ended")
            self.assertEqual(ControlTransport.worker_submit(binding, request_id="CT-2", kind="submit_intent", payload={"manifest": []})["state"], "closed")

    def test_stdio_mcp_server_submits_and_reads_a_published_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            transport = ControlTransport(root)
            binding = transport.issue("EX-1", "GR-1")
            config = ControlTransport.mcp_server_config(binding)
            process = subprocess.Popen([config["command"], *config["args"]], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            def request(request_id, method, params):
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}) + "\n")
                process.stdin.flush()
                return json.loads(process.stdout.readline())
            try:
                initialized = request(1, "initialize", {"protocolVersion": "2024-11-05"})
                self.assertEqual(initialized["result"]["serverInfo"]["name"], "do-math-control-transport")
                submitted = request(2, "tools/call", {"name": "control_submit", "arguments": {
                    "request_id": "CT-mcp", "kind": "submit_intent", "payload": {"manifest": ["result.json"]}}})
                self.assertIn("submitted", submitted["result"]["content"][0]["text"])
                transport.pump(lambda _: {"state": "accepted", "published": True, "snapshot": "SN-mcp"})
                receipt = request(3, "tools/call", {"name": "control_receipt", "arguments": {"request_id": "CT-mcp", "wait_seconds": 0}})
                self.assertIn("SN-mcp", receipt["result"]["content"][0]["text"])
            finally:
                process.stdin.close()
                process.wait(timeout=10)
                process.stdout.close()
                process.stderr.close()

    def test_parallel_call_carries_a_distinct_execution_id(self):
        events = []
        class Runner:
            def run(self, **arguments):
                arguments["on_started"]({"pid": 7})
                return {"status": "completed"}
        def operation():
            result = yield {"on_started": lambda observed: events.append(observed)}
            events.append(result)
        generator = operation(); arguments = next(generator)
        calls = ModelCalls()
        try:
            calls.start(generator, Runner(), arguments, execution_id="EX-1")
            deadline = time.monotonic() + 10
            while not calls.collect():
                self.assertLess(time.monotonic(), deadline,
                    "EX-1 did not complete; pending callbacks=" + str(calls.events.qsize()))
                time.sleep(.01)
        finally:
            calls.close()
        self.assertEqual(events, [{"pid": 7}, {"status": "completed"}])


class AuditRecoveryTests(unittest.TestCase):
    """Real family storage; only the OS Job observation is replaced."""

    def setUp(self):
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import profile_ref
        from do_math.repository import ResearchRepository
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        self.repo = ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")
        self.instance = {"feature_version": 5, "config": deepcopy(DEFAULT_CONFIG),
                         **build_profiles(DEFAULT_CONFIG)}
        self.profile = next(p for p in self.instance["execution_profiles"].values()
                            if p["role"] == "maintenance")
        self.runtime = {"feature_version": 5, "executions": {}, "queue": [], "reservations": {}}
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
        self.head = self.repo.save(self.head, self.instance, self.runtime)
        _, self.instance, self.runtime = self.repo.load(self.head)
        self.execution = self.runtime["executions"]["EX-audit"]

    def running(self):
        transition_execution(self.execution, "starting", at=TIME)
        transition_execution(self.execution, "running", at=TIME)

    def test_03_real_recovery_record_completion_round_trip(self):
        self.runtime["recoveries"] = {"RY-audit": {"id": "RY-audit", "started_at": TIME,
            "execution_ids": ["EX-audit"], "dispositions": [{"execution_id": "EX-audit",
            "local_termination_confirmed": False, "remote_termination": "unknown",
            "reservation_reconciled": False, "next_owner": "operator"}], "finished_at": TIME}}
        self.reload()
        self.assertEqual(self.runtime["recoveries"]["RY-audit"]["finished_at"], TIME)

    def test_04_confirmed_local_termination_releases_only_its_reservation(self):
        from unittest.mock import patch
        from do_math.session_slots import GitSessionSlots
        slots = GitSessionSlots(self.runtime, self.instance)
        transition_execution(self.execution, "starting", at=TIME)
        self.assertTrue(slots.acquire("EX-audit", self.profile["budget_kind"], self.profile["ai"]["model"],
                                     profile=self.profile, execution=self.execution))
        slots.started("EX-audit", {"job_name": "audit-job"})
        transition_execution(self.execution, "running", at=TIME)
        self.reload()
        engine = ProviderEngineMixin()
        engine.instance, engine.runtime = self.instance, self.runtime
        engine._slots = GitSessionSlots(self.runtime, self.instance)
        self.assertTrue(hasattr(engine, "_settle_recovered_execution"), "missing recovery/slot settlement API")
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
        engine._slots = GitSessionSlots(self.runtime, self.instance)
        self.assertTrue(engine._settle_recovered_execution("EX-audit", at=TIME))

    def test_05_queued_recovery_is_retired_and_requeued_with_exact_lineage(self):
        from do_math import activities
        self.assertTrue(hasattr(activities, "requeue_recovered_execution"), "queued recovery has no redispatch API")
        activities.requeue_recovered_execution(self.runtime, "EX-audit", at=TIME)
        self.reload()
        self.assertEqual((self.execution["status"], self.execution["outcome"]), ("ended", "cancelled"))
        self.assertEqual(self.runtime["queue"][0]["continuation_of"], "EX-audit")
        self.assertEqual(self.runtime["queue"][0]["owner_activity_id"], "AY-audit")
        self.assertFalse(any(e["status"] != "ended" and e["action"]["id"] == "AC-audit"
                             for e in self.runtime["executions"].values()))
        self.assertEqual(validate_activities(self.runtime), [])

    def test_06_pause_keeps_original_queue_binding_and_checkpoint_lineage(self):
        from do_math import activities
        self.assertTrue(hasattr(activities, "bind_action"), "working action loses durable queue binding")
        working = deepcopy(self.action)
        activities.bind_action(self.runtime, working, "AY-audit")
        self.assertEqual(self.action["owner_activity_id"], "AY-audit")
        self.running()
        transition_execution(self.execution, "stopping", at=TIME, reason="user_pause", stop_phase="terminating")
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

    def test_07_intent_stops_and_revokes_execution_authority_in_same_git_publication(self):
        self.running()
        self.reload()
        transport = ControlTransport(Path(self.temporary.name) / "delivery")
        workspace=Path(self.temporary.name)/'submission-workspace'
        from v5_fixtures import sealed_maintenance_submission
        intent, artifacts = sealed_maintenance_submission(workspace, 'EX-audit')
        binding = transport.issue("EX-audit", "GR-audit", workspace=workspace)
        request = {**binding, "request_id": "request-audit", "kind": "submit_intent", "payload": {"draft_path": "draft.json"}}
        def publish(value):
            receipt = {"id": "CT-audit", "request_id": value["request_id"], "execution_id": "EX-audit",
                       "kind": "submit_intent", "state": "accepted", "received_at": TIME}
            record_submission_intent(self.execution, intent, receipt)
            self.assertEqual(self.execution["status"], "stopping")
            self.assertEqual(self.execution["stop_phase"], "terminating")
            self.assertEqual(self.execution["authority_revocation"]["scope"], "execution_research")
            self.runtime["control_receipts"] = {receipt["id"]: receipt}
            self.head=self.repo.save(self.head,self.instance,self.runtime,artifacts=artifacts)
            return {"state": "accepted", "published": True, "snapshot": self.head}
        receipt = transport.receive(request, publish=publish)
        _, _, stored = self.repo.load(receipt["snapshot"])
        self.assertEqual(stored["executions"]["EX-audit"]["authority_revocation"]["receipt_id"], "CT-audit")
        self.assertEqual(stored["control_receipts"]["CT-audit"]["state"], "accepted")

    def test_11_preparation_attempt_is_durable_before_input_and_failure(self):
        from do_math import execution_lifecycle as lifecycle
        self.assertTrue(hasattr(lifecycle, "begin_preparation"), "preparation has no durable stage API")
        lifecycle.begin_preparation(self.execution, at=TIME)
        self.reload()
        self.assertEqual(self.execution["status"], "queued")
        self.assertEqual(self.execution["input_manifest"], [])
        lifecycle.end_preparation(self.execution, at=TIME, stage="context", reason="input unavailable", cancelled=False)
        self.reload()
        self.assertEqual((self.execution["status"], self.execution["outcome"]), ("ended", "start_failed"))
        self.assertEqual(self.execution["input_preparation"]["reason"], "input unavailable")

    def test_starting_no_substantive_action_has_a_legal_terminal_path(self):
        transition_execution(self.execution, "starting", at=TIME)
        recover_execution(self.execution, {"fact": "no_substantive_action"}, at=TIME)
        self.assertEqual(self.execution["outcome"], "start_failed")
        self.reload()


if __name__ == "__main__":
    unittest.main(verbosity=2)
