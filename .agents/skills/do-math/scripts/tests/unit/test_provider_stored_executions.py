"""The stored execution record: every step below round-trips through the real repository (layer 2).

The repository is ``ResearchRepository`` over the in-process Git port fake
(``support.storage_records.record_store``), so each publication passes the
storage contract and each reload reads the published state back. Settling an
admitted execution runs the real engine's provider mixin on the same
repository, with the Jobs port fake answering whether the ticket's Job is empty.
"""
from copy import deepcopy
import hashlib
import json
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
from support.state_builders import current_state
from support.execution_inputs import sealed_maintenance_submission
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_runs import ProviderJobs, fake_ports
from support.storage_records import INSTANCE_ID, record_store

TIME = "2026-09-20T00:00:00+00:00"


def stored_audit_state(workspace):
    """``(instance, runtime, action)``: a maintenance activity ``AY-audit`` with its queued execution ``EX-audit``."""
    from support.entry import entry
    _entry = entry()
    # Every stored state passes the current lifecycle gate.
    instance, runtime = current_state({"config": deepcopy(DEFAULT_CONFIG), **build_profiles(DEFAULT_CONFIG, host=_entry.ports.host),
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

    def test_unadmitted_attempt_has_no_capacity_to_hold_or_return(self):
        from support.entry import entry
        slots = SessionSlots(self.runtime, self.instance, jobs=ProviderJobs(clock=self.clock),
                             clock=self.clock, host_id=entry().host_id)
        before = deepcopy((self.instance, self.runtime))
        self.assertIs(lifecycle.release_or_hold(self.execution, slots, at=TIME), True)
        self.assertEqual((self.instance, self.runtime), before)

    def test_unproduced_execution_fields_are_rejected_without_changing_the_head(self):
        """Keep one real queued attempt and reject obsolete top-level slots individually."""
        published = deepcopy(self.repo.load(self.head))
        for field, value in (
                ('pid', 123), ('conversation_id', 'session'), ('finished_at', TIME),
                ('workspace', 'work'), ('parent_execution_id', None),
                ('profile_ref', self.execution['execution_profile_ref']),
                ('submission_check', {}), ('started', TIME), ('currentness', {}), ('integration_id', 'IN-transient')):
            with self.subTest(field=field):
                changed = deepcopy(self.runtime)
                changed['executions']['EX-audit'][field] = value
                before = deepcopy(changed)
                with self.assertRaises(ValueError) as rejected:
                    self.repo.save_with_state(self.head, self.instance, changed)
                self.assertIs(type(rejected.exception), ValueError)
                self.assertEqual(str(rejected.exception),
                    "runtime/executions/EX-audit/: Additional properties are not allowed "
                    f"('{field}' was unexpected)")
                self.assertEqual(changed, before)
                self.assertEqual(self.repo.load(), published)
        self.reload()
        self.assertEqual(self.repo.load(self.head)[2]['executions']['EX-audit'], published[2]['executions']['EX-audit'])

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

    def test_failed_live_review_and_recovery_preserve_the_stop_then_replace_the_disposition(self):
        from support.entry import entry
        inputs = entry()
        self.running()
        self.reload()
        old_head = self.head
        old = deepcopy(self.repo.load(old_head))
        owner = ResearchEngine(self.repo.repository, INSTANCE_ID,
            ports=fake_ports(self.clock, self.backend, ProviderJobs(clock=self.clock)),
            codex_home=inputs.codex_home, environment=inputs.environment, host_id=inputs.host_id)
        reason = 'Exact live-review failure e\u0301\r\n'
        owner._failed_live_review({'target': 'EX-audit', 'live': True}, reason)
        owner._save()
        reader = record_store(self.repo.repository, backend=self.backend, clock=self.clock)
        row = reader.load(owner.head)[2]['executions']['EX-audit']
        self.assertEqual(row['stop_requested'], 'operating_review_unavailable')
        self.assertEqual(row['after_stop'], {'decision': 'wait', 'reason': reason})
        lifecycle.recover_execution(owner.runtime['executions']['EX-audit'], at=TIME)
        owner._save()
        row = reader.load(owner.head)[2]['executions']['EX-audit']
        self.assertEqual(row['recovery_disposition'], 'reconcile_local_and_remote')
        self.assertEqual(row['status'], 'stopping')
        lifecycle.end_recovered(owner.runtime['executions']['EX-audit'], at=TIME,
            outcome='execution_incomplete', disposition='preserved_for_followup')
        owner._save()
        row = reader.load(owner.head)[2]['executions']['EX-audit']
        self.assertNotIn('recovery_disposition', row)
        self.assertEqual((row['ended_at'], row['result_disposition']), (TIME, 'preserved_for_followup'))
        self.assertEqual(row['after_stop'], {'decision': 'wait', 'reason': reason})
        self.assertEqual(reader.load(old_head), old)

    def test_confirmed_local_termination_releases_only_its_reservation(self):
        from support.entry import entry
        _entry = entry()
        jobs = ProviderJobs(clock=self.clock)
        # Only work roles reserve a model slot; bind this execution to one so a
        # reservation exists whose return the recovery must confirm.
        profile = next(p for p in self.instance["execution_profiles"].values()
                       if p["role"] == "research_work" and p["actor_kind"] == "ai")
        self.execution.update(role="research_work", execution_profile_ref=profile_ref(profile))
        slots = SessionSlots(self.runtime, self.instance, jobs=jobs, clock=self.clock, host_id=_entry.host_id)
        transition_execution(self.execution, "starting", at=TIME)
        self.assertTrue(slots.acquire("EX-audit", profile=profile, execution=self.execution))
        self.assertTrue(self.execution["capacity"]["reservation_ids"])
        name = self.execution["launch_ticket"]["job_name"]
        slots.started("EX-audit", {"job_name": name}, at=TIME)
        self.reload()
        # The worker still runs in the ticket's named Job.
        job = jobs.launch([sys.executable, "codex_worker.py", "request.json"], name=name)

        def engine():
            return ResearchEngine(self.repo.repository, INSTANCE_ID, ports=fake_ports(self.clock, self.backend, jobs), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
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
        activities.continue_activity(self.runtime, "EX-audit", wait_kind='user_resume', at=TIME, reason="user_pause",
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

    def test_unconfirmed_job_keeps_the_original_error_and_reservations_until_termination(self):
        from support.entry import entry
        host_id = entry().host_id
        jobs = ProviderJobs(clock=self.clock)
        profile = next(row for row in self.instance['execution_profiles'].values()
                       if row['role'] == 'research_work' and row['actor_kind'] == 'ai')
        self.execution.update(role='research_work', execution_profile_ref=profile_ref(profile))
        slots = SessionSlots(self.runtime, self.instance, jobs=jobs, clock=self.clock, host_id=host_id)
        transition_execution(self.execution, 'starting', at=TIME)
        self.assertTrue(slots.acquire('EX-audit', profile=profile, execution=self.execution))
        self.assertTrue(self.execution['capacity']['reservation_ids'])
        name = self.execution['launch_ticket']['job_name']
        job = self.enterContext(jobs.launch([sys.executable, 'codex_worker.py', 'request.json'], name=name))
        slots.started('EX-audit', {'job_name': name}, at=TIME)
        self.execution['error'] = 'Original worker diagnosis before barrier reconciliation.'
        before_capacity = deepcopy(self.execution['capacity'])
        before_reservations = deepcopy(self.runtime['reservations'])
        self.assertIs(lifecycle.release_or_hold(self.execution, slots, at=TIME), False)
        self.assertEqual(self.execution['status'], 'stopping')
        self.assertEqual(self.execution['error'], 'Original worker diagnosis before barrier reconciliation.')
        self.assertEqual(self.execution['capacity'], before_capacity)
        self.assertEqual(self.runtime['reservations'], before_reservations)
        self.reload()
        self.assertEqual(self.execution['error'], 'Original worker diagnosis before barrier reconciliation.')
        job.terminate()
        restored_slots = SessionSlots(self.runtime, self.instance, jobs=jobs, clock=self.clock, host_id=host_id)
        self.assertIs(lifecycle.release_or_hold(self.execution, restored_slots, at=TIME), True)
        self.assertEqual(self.execution['status'], 'stopping')
        self.assertEqual(self.execution['capacity']['local_termination'], 'confirmed')
        self.assertEqual(self.execution['error'], 'Original worker diagnosis before barrier reconciliation.')
        self.assertEqual(set(self.runtime['reservations']), set(before_reservations))
        for identifier, original in before_reservations.items():
            self.assertEqual(self.runtime['reservations'][identifier]['returned'], original['reserved'])
        self.reload()
        self.assertEqual(self.execution['capacity']['local_termination'], 'confirmed')


class StoredCallEvidenceTests(unittest.TestCase):
    def test_delegated_input_hash_binds_the_frozen_case_after_reload(self):
        from support.storage_execution_pairs import StoredExecutions, assert_stored_delegation_input
        assert_stored_delegation_input(StoredExecutions(self))

    def test_unconfirmed_provider_failure_preserves_exact_decimal_evidence(self):
        from support.storage_execution_pairs import StoredExecutions, assert_stored_provider_failure
        assert_stored_provider_failure(StoredExecutions(self), unconfirmed=True)

    def test_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs(self):
        from support.storage_execution_pairs import assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs
        assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs(self)

    def test_maintenance_archive_writes_termination_and_collection_before_local_cleanup(self):
        from support.storage_execution_pairs import assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup
        assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup(self)

    def test_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload(self):
        from support.storage_execution_pairs import assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload
        assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload(self)


if __name__ == "__main__":
    unittest.main()
