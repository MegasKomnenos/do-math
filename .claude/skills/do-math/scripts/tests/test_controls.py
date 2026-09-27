"""User and operator controls: transitions, receipts and their identities, queueing, and the maintenance fence."""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import maintenance_gate, submission
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import control, ResearchEngine
from do_math.repository import canonical_json, ResearchRepository
from engine_fixtures import initialized, initialized_instance, routing_engine
from research_fixtures import (install_adapter_fixture, new_instance, observe, restore_template, run_cli,
                               write_checkpoint)
from runner_fixtures import ScriptedRunner
from state_fixtures import active_instance

CONFIG = {"scholarly_enabled": False, "operator_enabled": False, "lean_command": ["test-lean"],
          "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}


class ControlTransitionTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)

    def start(self, build, **parameters):
        """Copy a template state; ``self.repo``, ``self.iid`` and ``self.store`` name it."""
        self.root, self.iid = restore_template(build, config=CONFIG, **parameters)
        self.repo = self.root / "repository"
        self.store = ResearchRepository(self.repo, self.iid)

    def initializing(self):
        self.start(initialized_instance, goal="control transition fixture")

    def active_with_preparation(self):
        """Active state whose queue holds one AI action: a research preparation."""
        self.start(active_instance)
        engine = ResearchEngine(self.repo, self.iid, runner=ScriptedRunner())
        engine._enqueue("research_preparation", reason="Prepare the control transition fixture")
        engine._save()
        return engine

    def update(self, change):
        head, instance, runtime = self.store.load()
        change(instance, runtime)
        self.store.save_with_state(head, instance, runtime)[0]

    def test_pause_and_resume_cannot_reopen_a_publicly_closed_instance(self):
        self.initializing()
        control(self.repo, self.iid, "close")
        engine = ResearchEngine(self.repo, self.iid)
        engine.process_controls()
        self.assertEqual(engine.status()["status"], "closed")
        control(self.repo, self.iid, "pause")
        engine.process_controls()
        self.assertEqual(engine.status()["status"], "closed")
        rejected = control(self.repo, self.iid, "resume")
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status["status"], "closed")
        self.assertEqual(status["pending_controls"], 0)
        _, _, runtime = self.store.load()
        self.assertEqual(runtime["history"][-1]["kind"], "rejected_user_control")
        self.assertEqual(runtime["history"][-1]["request"]["id"], rejected["request_id"])
        response = run_cli("resume", "--repository", str(self.repo), "--instance", self.iid)
        self.assertEqual(response.returncode, 0, response.stdout + response.stderr)
        self.assertEqual(json.loads(response.stdout)["result"]["effect"], "rejected")

    def test_stale_request_is_consumed_and_does_not_poison_later_controls(self):
        engine = self.active_with_preparation()
        from do_math.planning import task_ready
        for _ in range(8):
            engine.run(max_steps=1)
            ready = [task['id'] for task in engine.runtime['tasks'].values()
                     if task_ready(task, engine.instance, engine.runtime,
                                   evaluation_context=engine._evaluation_context())['state'] == 'ready']
            if ready:
                break
        self.assertTrue(ready, engine.runtime['history'][-3:])
        task_id = ready[0]
        request = control(self.repo, self.iid, "request", config={"role": "supplemental_research", "target": task_id})
        self.update(lambda i, r: r["tasks"][task_id].update(status="active"))
        control(self.repo, self.iid, "pause")
        engine = ResearchEngine(self.repo, self.iid)
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status["status"], "paused")
        self.assertEqual(status["pending_controls"], 0)
        _, _, runtime = self.store.load()
        self.assertIn(request["request_id"], runtime["processed_controls"])
        self.assertEqual(runtime["tasks"][task_id]["status"], "active")
        self.assertTrue(any(h.get("kind") == "rejected_user_control"
                            and h["request"]["id"] == request["request_id"] for h in runtime["history"]))

    def test_request_accepted_before_public_close_does_not_reopen_it(self):
        self.initializing()
        control(self.repo, self.iid, "request", config={"role": "maintenance"})
        control(self.repo, self.iid, "close")
        engine = ResearchEngine(self.repo, self.iid)
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status["status"], "closed")
        self.assertEqual(status["pending_actions"], 0)
        self.assertEqual(status["pending_controls"], 0)

    def test_crash_marks_owning_activity_unresolved(self):
        engine = self.active_with_preparation()
        action = engine.runtime['queue'][0]
        execution = engine._register_execution(action, {'id': 'EX-crashed', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': []})
        engine._save()
        ResearchEngine(self.repo, self.iid, runner=ScriptedRunner()).run(max_steps=1)
        _, _, runtime = self.store.load()
        recovered = runtime['executions']['EX-crashed']
        self.assertEqual(recovered['status'], 'stopping')
        self.assertEqual(recovered['stop_phase'], 'terminating')
        self.assertNotIn('outcome', recovered)
        self.assertEqual(recovered['recovery_disposition'], 'reconcile_local_and_remote')
        owner = runtime['activities'][recovered['owner_activity_id']]
        self.assertIn('EX-crashed', owner['assigned_execution_ids'])
        self.assertTrue(runtime['recoveries'])
        disposition = next(row for recovery in runtime['recoveries'].values()
                           for row in recovery['dispositions'] if row['execution_id'] == 'EX-crashed')
        self.assertFalse(disposition['local_termination_confirmed'])
        self.assertEqual(disposition['remote_termination'], 'unknown')
        self.assertEqual(disposition['next_owner'], 'operator')


class SourceControlReceiptTests(unittest.TestCase):
    def test_unchanged_source_control_publishes_one_replayable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            source = root / 'source.txt'
            source.write_text('fixed source\n', encoding='utf-8')
            instance_id = new_instance(repo, goal='Check source receipts', workspace=root / 'work', sources=[source])
            engine = ResearchEngine(repo, instance_id)
            before = deepcopy(engine.instance['sources'][0])
            sent = control(repo, instance_id, 'source', config={'path': str(source)},
                           request_id='UC-unchanged-source')
            self.assertEqual(sent['effect'], 'pending engine processing')
            engine._controls(pump=False)
            receipt = engine.control_result('UC-unchanged-source')
            self.assertEqual(receipt['effect'], 'applied')
            self.assertEqual(receipt['reason'], 'source content unchanged')
            self.assertEqual(engine.instance['sources'][0], before)
            replay = control(repo, instance_id, 'source', config={'path': str(source)},
                             request_id='UC-unchanged-source')
            self.assertEqual(replay['snapshot'], receipt['snapshot'])
            self.assertEqual(len([row for row in engine.runtime['history']
                if row.get('request', {}).get('id') == 'UC-unchanged-source']), 1)
            source.write_text('updated source\n', encoding='utf-8')
            control(repo, instance_id, 'source', config={'path': str(source)},
                    request_id='UC-changed-source')
            engine._controls(pump=False)
            self.assertEqual(engine.instance['sources'][0]['revision'], 2)
            self.assertEqual(engine.store.read(engine.instance['sources'][0]['path'], engine.head),
                             source.read_bytes())


class ControlReceipts(unittest.TestCase):
    def make_engine(self):
        engine = routing_engine()
        engine.head = "parent"
        engine.runtime.update(events=[], pending_events=[])
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        engine.instance["workspace"] = temporary.name
        engine.instance["config"]["max_artifact_bytes"] = 1024 * 1024
        (Path(temporary.name) / "runs/EX-work/workspace/.control").mkdir(parents=True)
        engine.store = create_autospec(ResearchRepository, instance=True)
        engine.store.read.side_effect = [canonical_json({}), canonical_json({})]
        engine.instance["grants"] = {"GR-one": {"id": "GR-one", "kind": "local", "status": "active",
            "roles": ["research_work"], "task_ids": [], "expires_at": None}}
        engine.runtime["executions"]["EX-work"] = {"id": "EX-work", "role": "research_work", "status": "running",
            "grant_id": "GR-one", "action": {"id": "AC-work", "role": "research_work"}, "input_bundle": "BA-input"}
        engine._clock_guard = create_autospec(engine._clock_guard, return_value={"usable": True, "observed_utc": "2026-09-22T00:00:00Z"})
        engine._save = create_autospec(engine._save, side_effect=lambda *a: setattr(engine, "head", "published"))
        request = {"request_id": "request-one", "transport_id": "local", "capability": "delivery-only",
            "execution_id": "EX-work", "grant_id": "GR-one", "kind": "submit_intent",
            "payload": {"draft_path": "draft.json"}}
        return engine, request

    @staticmethod
    def sealed():
        return {"passed": True, "capture_eligible": True, "check": {"issues": []}, "manifest": [],
            "intent": {"candidate_id": "CS-one", "draft_path": "draft.json",
                       "output_sha256": "a" * 64, "extensions_sha256": "b" * 64,
                       "schema_ref": {}, "manifest": []},
            "artifacts": {"output.json": b"{}", "extensions.json": b"{}",
                          "check.json": b"{}", "manifest.json": b"[]"}}

    def test_receipt_requires_successful_cas_and_replay_does_not_reapply(self):
        engine, request = self.make_engine()
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            receipt = engine._publish_control_request(request)
        self.assertEqual(receipt["snapshot"], "published")
        self.assertEqual(receipt["state"], "accepted")
        self.assertEqual(engine.runtime["executions"]["EX-work"]["status"], "stopping")
        self.assertEqual(engine.runtime["executions"]["EX-work"]["stop_phase"], "terminating")
        self.assertNotIn("outcome", engine.runtime["executions"]["EX-work"])
        stored = next(iter(engine.runtime["control_receipts"].values()))
        self.assertNotIn("capability", stored["request"])
        engine.store.read.side_effect = [canonical_json({}), canonical_json({})]
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            engine._publish_control_request(request)
        self.assertEqual(engine._save.call_count, 1)

    def test_preview_control_is_nonpublishing_and_returns_sanitized_result(self):
        engine, request = self.make_engine()
        request["kind"] = "submission_preview"
        result = {"contract_id": submission.PREVIEW_CONTRACT_ID, "passed": True, "authoritative": False}
        engine._preview_submission = create_autospec(engine._preview_submission, return_value=result)
        before = deepcopy((engine.instance, engine.runtime))
        receipt = engine._publish_control_request(request)
        self.assertEqual(receipt, {"state": "previewed", "result": result})
        engine._save.assert_not_called()
        self.assertEqual((engine.instance, engine.runtime), before)

    def test_safety_boundary_updates_obligation_only_after_publication(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule
        engine, request = self.make_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            (Path(temporary)/"runs/EX-work/workspace/.control").mkdir(parents=True)
            clock = Clock()
            tracker = ObservationTracker("EX-work", Path(temporary), {"observation_rules": [observation_rule()],
                "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=clock)
            observe(tracker, {"type": "item.started", "item": {"id": "C", "type": "command_execution"}})
            write_checkpoint(temporary, counters={"attempts": 2})
            obligation = next(row for row in observe(tracker, {"type": "tick"})
                              if row["kind"] == "self_check_due")
            engine._trackers = {"EX-work": tracker}
            engine._transport = Mock(); engine._transport_bindings = {"EX-work": {}}
            request.update(kind="safety_boundary", payload={"inflight_calls": False, "call_ids": ["C"]})
            observe(tracker, {'type': 'item.started', 'item': {'id': 'BOUNDARY', 'type': 'mcp_tool_call',
                'server': 'execution_control', 'tool': 'control_submit', 'arguments': {
                    'request_id': request['request_id'], 'kind': 'safety_boundary', 'payload': request['payload']}}})
            self.assertIn('BOUNDARY', tracker.boundary_call_ids)
            self.assertNotIn('BOUNDARY', tracker.self_check_call_ids)
            uncovered = {**deepcopy(request), "request_id": "uncovered", "payload": {"inflight_calls": False, "call_ids": []}}
            self.assertEqual(engine._publish_control_request(uncovered)["state"], "rejected")
            engine._save.side_effect = ValueError("CAS failed")
            self.assertEqual(engine._publish_control_request(request)["state"], "rejected")
            self.assertIsNone(tracker.obligations[obligation["id"]]["deadline_offset_ms"])
            engine._save.side_effect = lambda *a: setattr(engine, "head", "published")
            self.assertEqual(engine._publish_control_request(request)["state"], "accepted")
            self.assertEqual(tracker.obligations[obligation["id"]]["deadline_offset_ms"], 5000)
            self.assertEqual(engine.runtime["self_check_obligations"][obligation["id"]]["deadline_offset_ms"], 5000)

    def test_rejected_self_check_is_preserved_but_not_acknowledged_as_accepted(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule, self_check_response
        engine, request = self.make_engine()
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            (Path(temporary)/"runs/EX-work/workspace/.control").mkdir(parents=True)
            tracker = ObservationTracker("EX-work", Path(temporary), {"observation_rules": [observation_rule()],
                "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            write_checkpoint(temporary, counters={"attempts": 2})
            obligation = next(row for row in observe(tracker, {"type": "tick"})
                              if row["kind"] == "self_check_due")
            engine._trackers = {"EX-work": tracker}
            engine._control_evidence_refs = create_autospec(engine._control_evidence_refs, return_value=set())
            response = self_check_response(obligation)
            request.update(kind="self_check_response", payload={"self_check_id": obligation["id"], "response": response})
            receipt = engine._publish_control_request(request)
            self.assertEqual(receipt["state"], "rejected")
            self.assertTrue(engine.runtime["self_check_responses"])
            self.assertEqual(len(engine.runtime["queue"]), 1)
            self.assertTrue((Path(temporary)/"runs/EX-work/workspace/.control/observation-feedback.json").is_file())

    def test_self_check_transport_and_native_call_bind_in_both_arrival_orders(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule, self_check_response
        for first in ("native", "receipt"):
            with self.subTest(first=first):
                engine, request = self.make_engine()
                workspace = Path(engine.instance["workspace"]) / "runs/EX-work/workspace"
                tracker = ObservationTracker("EX-work", workspace, {
                    "observation_rules": [observation_rule()], "tool_review_window_seconds": 60,
                    "self_check_response_window_seconds": 5}, clock=Clock())
                write_checkpoint(workspace, counters={"attempts": 2})
                obligation = next(row for row in observe(tracker, {"type": "tick"})
                                  if row["kind"] == "self_check_due")
                response = self_check_response(obligation)
                request.update(request_id="self-check-" + obligation["id"], kind="self_check_response",
                    payload={"self_check_id": obligation["id"], "response": response})
                event = {"type": "item.started", "item": {"id": "CALL-SC", "type": "mcp_tool_call",
                    "server": "execution_control", "tool": "control_self_check", "arguments": request["payload"]}}
                engine._trackers = {"EX-work": tracker}
                engine._control_evidence_refs = create_autospec(engine._control_evidence_refs, return_value={"EV-1"})
                if first == "native":
                    observe(tracker, event)
                receipt = engine._publish_control_request(request)
                self.assertEqual(receipt["state"], "accepted", receipt)
                if first == "receipt":
                    observe(tracker, event)
                self.assertEqual(tracker.obligations[obligation["id"]]["status"], "answered")
                self.assertEqual(tracker.control_calls["CALL-SC"]["payload_sha256"],
                                 tracker.control_requests[request["request_id"]]["payload_sha256"])
                self.assertEqual(tracker.control_requests[request["request_id"]]["receipt_id"],
                                 receipt["publication_id"])
                self.assertEqual(engine.runtime["queue"], [])
                engine._publish_control_request(request)
                self.assertEqual(engine._save.call_count, 1)

    def test_self_check_failed_publication_does_not_publish_tracker_binding(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule, self_check_response
        engine, request = self.make_engine()
        tracker = ObservationTracker("EX-work", Path(engine.instance["workspace"]), {
            "observation_rules": [observation_rule()], "tool_review_window_seconds": 60,
            "self_check_response_window_seconds": 5}, clock=Clock())
        write_checkpoint(engine.instance["workspace"], counters={"attempts": 2})
        obligation = next(row for row in observe(tracker, {"type": "tick"})
                          if row["kind"] == "self_check_due")
        request.update(request_id="self-check-" + obligation["id"], kind="self_check_response",
            payload={"self_check_id": obligation["id"], "response": self_check_response(obligation)})
        engine._trackers = {"EX-work": tracker}
        engine._control_evidence_refs = create_autospec(engine._control_evidence_refs, return_value={"EV-1"})
        engine._save.side_effect = OSError("publication failed")
        engine.store.load.side_effect = OSError("no committed receipt")
        self.assertEqual(engine._publish_control_request(request)["state"], "rejected")
        self.assertEqual(tracker.control_requests, {})
        self.assertEqual(tracker.obligations[obligation["id"]]["status"], "open")

    def test_failed_cas_does_not_acknowledge_submission(self):
        engine, request = self.make_engine()
        engine._save.side_effect = ValueError("CAS failed")
        with patch("do_math.engine.submission.seal_submission", return_value=self.sealed()):
            receipt = engine._publish_control_request(request)
        self.assertEqual(receipt["state"], "rejected")
        self.assertNotIn("submission_receipt", engine.runtime["executions"]["EX-work"])


class UserControlIdentity(unittest.TestCase):
    def test_same_request_replays_before_changed_state_admission(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine = routing_engine()
            engine.instance["workspace"] = str(root / "work")
            store = create_autospec(ResearchRepository, instance=True)
            store.load.return_value = ("snapshot", engine.instance, engine.runtime)
            with patch("do_math.engine.ResearchRepository", return_value=store):
                first = control(root, "RI-test", "request", config={"role": "maintenance"}, request_id="UC-explicit")
                engine.runtime["status"] = "closed"
                replay = control(root, "RI-test", "request", config={"role": "maintenance"}, request_id="UC-explicit")
                self.assertEqual(first["request_id"], replay["request_id"])
                self.assertTrue(replay["replayed"])
                self.assertEqual(len(list((root / "work/control/RI-test").glob("*.json"))), 1)
                with self.assertRaisesRegex(ValueError, "different"):
                    control(root, "RI-test", "request", config={"role": "maintenance"}, text="changed", request_id="UC-explicit")


    def test_git_replay_keeps_original_outcome_and_snapshot_after_close(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            identifier = initialized(root / "repo", goal="Control replay", workspace=root / "work")
            first = control(root / "repo", identifier, "pause", text="pause once")
            engine = ResearchEngine(root / "repo", identifier)
            engine.process_controls()
            original = engine.control_result(first["request_id"])
            self.assertEqual(original["status"], "paused")
            control(root / "repo", identifier, "close")
            engine.process_controls()
            self.assertEqual(engine.runtime["status"], "closed")
            replay = control(root / "repo", identifier, "pause", text="pause once")
            self.assertTrue(replay["replayed"])
            self.assertEqual({key: replay[key] for key in original}, original)
            self.assertNotEqual(engine.head, original["snapshot"])
            from do_math.control_contracts import control_request_id
            self.assertEqual(first["request_id"], control_request_id(identifier, "pause", text="pause once"))

    def test_normalized_source_has_one_identity_and_rejects_wrong_bytes(self):
        from do_math.control_contracts import control_request_id
        import base64
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            engine = routing_engine(); engine.instance["workspace"] = str(root / "work")
            store = create_autospec(ResearchRepository, instance=True); store.load.return_value = ("snapshot", engine.instance, engine.runtime)
            spec = {"name": "source.txt", "body_base64": base64.b64encode(b"original").decode(),
                    "sha256": hashlib.sha256(b"original").hexdigest(), "bytes": 8}
            with patch("do_math.engine.ResearchRepository", return_value=store):
                result = control(root, "RI-test", "source", config=spec, idempotency_key="source-once")
                self.assertEqual(result["request_id"], control_request_id("RI-test", "source", config=spec, idempotency_key="source-once"))
                with self.assertRaisesRegex(ValueError, "hash or size"):
                    control(root, "RI-test", "source", config={**spec, "bytes": 7})


class ControlQueueConnections(unittest.TestCase):
    def engine(self, request):
        engine = routing_engine(); engine.head = "parent"
        engine.instance.update(config={**deepcopy(DEFAULT_CONFIG), }, lifecycle={"state": "active"})
        engine.runtime["processed_controls"] = []
        engine._inbox = create_autospec(engine._inbox, return_value=[request]); engine._save = create_autospec(engine._save)
        for name in ("_review_recovery_control", "_knowledge_io_control", "_academic_control", "_apply_extended_control"):
            setattr(engine, name, create_autospec(getattr(engine, name), return_value=False))
        for name in ("_schedule_operational_reviews", "_retry_submission_publications", "_retry_impact_reviews", "_run_pending_operational_repairs"):
            setattr(engine, name, create_autospec(getattr(engine, name)))
        return engine

    def test_every_queued_user_control_has_a_stable_queue_identity(self):
        # resume only restores the lifecycle (lifecycle_engine._resume_lifecycle); it queues no activity.
        for action, config in (("input", {}), ("request", {"role": "maintenance"})):
            with self.subTest(action=action):
                engine = self.engine({"id": "UC-one", "action": action, "config": config, "text": "Explicit request"})
                engine._controls()
                self.assertEqual(len(engine.runtime["queue"]), 1)
                queued = engine.runtime["queue"][0]
                self.assertTrue(queued.get("id", "").startswith("AC-"), queued)
                self.assertEqual(queued["id"], queued["lineage_id"])

    def test_distinct_approved_cleanup_scopes_are_not_merged(self):
        engine = routing_engine()
        engine._enqueue("maintenance", requested_by="UC-one", cleanup_execution_ids=["EX-one"])
        engine._enqueue("maintenance", requested_by="UC-two", cleanup_execution_ids=["EX-two"])
        self.assertEqual(len(engine.runtime["queue"]), 2)
        self.assertEqual([row["cleanup_execution_ids"] for row in engine.runtime["queue"]], [["EX-one"], ["EX-two"]])


class MaintenanceFenceTests(unittest.TestCase):
    def test_quiescence_does_not_release_unknown_execution_or_user_pause(self):
        runtime={'executions':{'EX-one':{'id':'EX-one','status':'starting'}},
                 'reservations':{},'user_pause':{'request_id':'UC-user'},'status':'paused'}
        request={'action':'quiesce','id':'UC-maint','origin':'operator','text':'install','created_at':'2026-09-25T00:00:00Z'}
        self.assertTrue(maintenance_gate.apply_control(runtime,request))
        maintenance_gate.settle(runtime)
        self.assertEqual(runtime['maintenance_fence']['state'],'blocked')
        release={**request,'action':'release_quiesce','id':'UC-release','config':{'fence_id':'UC-maint'}}
        with self.assertRaises(ValueError): maintenance_gate.apply_control(runtime,release)
        runtime['executions']['EX-one']['status']='ended'
        maintenance_gate.settle(runtime)
        maintenance_gate.apply_control(runtime,release)
        self.assertEqual(runtime['user_pause'],{'request_id':'UC-user'})
        self.assertEqual(runtime['status'],'paused')


class PublicMaintenanceFenceTests(unittest.TestCase):
    def test_public_maintenance_fence_survives_restart_and_preserves_user_pause(self):
        from do_math.engine import ResearchEngine
        from do_math.scheduled_operator import engine_start_guard
        from research_fixtures import cli_result
        from state_fixtures import start_active_copy
        start_active_copy(self)
        args = ('--repository', str(self.repo), '--instance', self.identifier)
        request = cli_result(self.root, 'quiesce', *args, '--origin', 'operator', '--reason', 'fixture installation maintenance')
        engine = ResearchEngine(self.repo, self.identifier)
        fence = engine.runtime['maintenance_fence']
        self.assertEqual(fence['state'], 'quiescent')
        self.assertEqual(fence['request_id'], request['request_id'])
        self.assertNotEqual(engine_start_guard(self.repo, self.identifier,
            Path(engine.instance['workspace']), status=engine.status())['outcome'], 'startable')
        cli_result(self.root, 'pause', *args, '--origin', 'user', '--reason', 'separate user pause')
        cli_result(self.root, 'release-quiesce', *args, '--origin', 'operator', '--fence', fence['request_id'], '--reason', 'fixture complete')
        restored = ResearchEngine(self.repo, self.identifier)
        self.assertNotIn('maintenance_fence', restored.runtime)
        self.assertEqual(restored.runtime['status'], 'paused')
        self.assertEqual(restored.runtime['user_pause']['reason'], 'separate user pause')


if __name__ == "__main__":
    unittest.main(verbosity=2)
