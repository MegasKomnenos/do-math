"""Efficiency changes must preserve obligations, inputs and published state."""
from copy import deepcopy
from contextlib import contextmanager
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import time
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, control
from v5_fixtures import charter_change, policy_change, send_control, candidate
from state_fixtures import active_engine
from test_lifecycle_engine import AdapterDouble
from do_math.model_policy import MODELS
from do_math.planning import contract_hash
from do_math.input_basis import capture_decision_basis
from test_engine import ScriptedRunner, context_from


class EfficiencyTests(unittest.TestCase):
    @contextmanager
    def model_process(self, arguments, *, resume):
        from do_math.windows_job import WindowsJob, process_identity
        job = WindowsJob([sys.executable, '-c', 'import time; time.sleep(600)'],
                         cwd=arguments['workspace'], name='EFFICIENCY-' + uuid.uuid4().hex)
        try:
            arguments['on_started']({**process_identity(job), 'job_name': job.name})
            if resume:
                job.resume()
            yield
        finally:
            try:
                job.terminate()
                self.assertTrue(job.wait(10))
                self.assertEqual(job.inspect().active_processes, 0)
            finally:
                job.close()

    def setUp(self):
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=AdapterDouble()))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.engine = active_engine(repo, self.root / "work", runner=ScriptedRunner(),
            config={"operator_enabled": False, "scholarly_enabled": False, "lean_command": ["test-lean"],
                    "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5})
        # These tests start after activation. Keep real state publication and
        # the preparation request they exercise, without replaying input approval.
        (self.root / "work" / "runs").mkdir(exist_ok=True)
        self.engine._enqueue("research_preparation", reason="Prepare the bounded efficiency fixture")
        self.engine._save()
        self.resources = {pool: {model: {"available": 3} for model in MODELS.values()}
                          for pool in ("work", "operations")}

    def startup(self):
        e = self.engine
        send_control(e, "decision", config={"change":
            charter_change(e, academic_requirements=[
                {"id": "explain", "scope": "solution", "criteria": ["explain structure"],
                 "assessor": "research_plan"}])})
        e._refresh_readiness()
        return next(a for a in e.runtime["queue"] if a["role"] == "research_plan")

    def test_pending_preparation_keeps_every_reason_without_duplicate_text(self):
        e = self.engine
        e.runtime["queue"] = []
        e._enqueue("research_preparation", reason="Investigate definition A", event_refs=["A"])
        e._enqueue("research_preparation", reason="Check independent obligation B", event_refs=["B"])
        e._enqueue("research_preparation", reason="Check independent obligation B", event_refs=["B"])
        self.assertEqual(len(e.runtime["queue"]), 1)
        action = e.runtime["queue"][0]
        self.assertIn("Investigate definition A", action["reason"])
        self.assertEqual(action["reason"].count("Check independent obligation B"), 1)
        self.assertEqual(action["event_refs"], ["A", "B"])

    def test_stopping_execution_input_is_never_merged(self):
        e = self.engine
        e.runtime["queue"] = [{"id": "A", "role": "research_preparation", "reason": "old"}]
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "stopping", "action": deepcopy(e.runtime["queue"][0])}
        e._enqueue("research_preparation", reason="new", event_refs=["later"])
        self.assertEqual(len(e.runtime["queue"]), 2)
        self.assertEqual(e.runtime["queue"][0]["reason"], "old")
        self.assertNotIn("event_refs", e.runtime["queue"][0])

    def test_active_charter_update_can_plan_and_preserves_its_event(self):
        action = self.startup()
        before = deepcopy(self.engine.runtime["events"])
        self.assertNotIn('initial_preparation_wait', action)
        self.assertTrue(self.engine._dispatchable(action, self.resources))
        self.assertEqual(self.engine.runtime["events"], before)
        self.assertTrue(self.engine.runtime["pending_events"])

    def test_charter_replanning_preserves_ongoing_preparation_and_consumes_its_event(self):
        self.startup()
        e = self.engine
        e.runner = ScriptedRunner()
        e._save()
        e.run(max_steps=3)
        plans = [context_from(prompt) for role, prompt in e.runner.prompts if role == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]['ready_task_ids'], [])
        self.assertCountEqual([role for role, _ in e.runner.prompts],
                         ['research_preparation', 'task_contract_review', 'research_plan'])
        event = next(row for row in reversed(e.runtime['events']) if row['kind'] == 'user_decision_applied')
        self.assertTrue(any(row.get('kind') == 'event_consumption' and event['id'] in row['event_ids']
                            for row in e.runtime['history']))
        self.assertNotIn(event['id'], e.runtime['pending_events'])

    def test_regular_empty_plan_can_still_dispatch(self):
        self.assertTrue(self.engine._dispatchable({"role": "research_plan", "reason": "assess failed approach"}, self.resources))

    def test_initial_plan_waits_for_other_reviews_only_up_to_the_settle_limit(self):
        action = self.startup()
        e = self.engine
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "ended", "outcome": "output_accepted", "action": {"role": "research_preparation"}}
        e.runtime["tasks"] = {"first": {"status": "planned"}, "slow": {"status": "planned"}}
        e.runtime["queue"].extend([{"role": "task_contract_review", "target": tid} for tid in e.runtime["tasks"]])
        self.assertFalse(e._dispatchable(action, self.resources))
        e.runtime["tasks"] = {}
        original_queue = deepcopy(e.runtime["queue"])
        e.runtime["queue"] = []
        e._enqueue("research_preparation", reason="Create a candidate for the settle regression")
        e.runtime["executions"].pop("E")  # The scheduler-only probe above is not a saved execution.
        e.runner = ScriptedRunner()
        e._save()  # Public run reloads the Git head, so publish the actual preparation request.
        for _ in range(8):
            e.run(max_steps=1)
            if any(row["state"] == "ready" for row in e._task_readiness.values()):
                break
        self.assertTrue(any(row["state"] == "ready" for row in e._task_readiness.values()))
        e.runtime["queue"] = original_queue
        # The remaining reviews are awaited only up to plan_settle_seconds, never indefinitely.
        self.assertFalse(e._dispatchable(action, self.resources))
        self.assertEqual(action["dispatch_wait"]["kind"], "plan_settle")
        from datetime import datetime, timedelta, timezone
        action["settle_started_at"] = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        self.assertTrue(e._dispatchable(action, self.resources))

    def test_pause_received_during_input_preparation_prevents_model_start(self):
        e = self.engine
        before_executions = set(e.runtime["executions"])
        before_calls = len(e.runner.prompts)
        before_runs = set((self.root / "work" / "runs").iterdir())
        original = e._context
        def prepare(action, workspace, **kwargs):
            context = original(action, workspace, **kwargs)
            control(e.store._store.repository, e.instance["id"], "pause", text="stop during materialization")
            return context
        with patch.object(e, '_context', side_effect=prepare):
            generator = e._call_steps(e.runtime["queue"][0])
            with self.assertRaises(StopIteration):
                next(generator)
        self.assertEqual(e.runtime["status"], "paused")
        self.assertEqual(len(e.runner.prompts), before_calls)
        added = set(e.runtime['executions']) - before_executions
        self.assertEqual(len(added), 1)
        execution = e.runtime['executions'][added.pop()]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'cancelled'))
        self.assertIsNone(execution.get('started_at'))
        self.assertNotIn('capacity', execution)
        self.assertEqual(set((self.root / "work" / "runs").iterdir()), before_runs)

    def test_pause_before_model_resume_has_no_checkpoint_grace(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        try:
            with self.model_process(arguments, resume=False):
                control(e.store._store.repository, e.instance['id'], 'pause', text='stop before model resume')
                self.assertTrue(arguments['should_stop'](), 'a suspended model must not resume for checkpoint grace')
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'stopped before resume'})

    def test_running_model_stops_immediately_after_public_pause(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0])
        arguments = next(steps)
        try:
            with self.model_process(arguments, resume=True):
                self.assertFalse(arguments['should_stop']())
                control(e.store._store.repository, e.instance['id'], 'pause', text='stop running work')
                self.assertTrue(arguments['should_stop']())
                execution = e.runtime['executions'][e.runtime['active_execution']]
                self.assertEqual(execution['status'], 'stopping')
                self.assertEqual(execution['stop_phase'], 'terminating')
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'local stop requested'})

    def test_installation_polling_is_bounded_and_forced_checks_still_detect_edits(self):
        e = self.engine
        self.assertTrue(callable(getattr(e, '_check_installation', None)), 'bounded installation checks required')
        with patch.object(e, '_installation_manifest', return_value=e._installation) as probe:
            for _ in range(10):
                self.assertTrue(e._check_installation())
            self.assertLessEqual(probe.call_count, 1)
        with patch.object(e, '_installation_manifest', return_value={"sha256": "changed"}):
            self.assertFalse(e._check_installation(force=True))
        self.assertEqual(e.runtime["status"], "paused")

    def test_installation_change_cannot_reopen_a_terminal_instance(self):
        e = self.engine
        for terminal in ('closed', 'completed'):
            with self.subTest(terminal=terminal):
                e.runtime['status'] = terminal
                with patch.object(e, '_installation_manifest', return_value={'sha256': 'changed'}):
                    self.assertFalse(e._check_installation(force=True))
                self.assertEqual(e.runtime['status'], terminal)

    def test_initial_wait_ends_on_new_independent_user_decision(self):
        action = self.startup()
        event = self.engine._lifecycle_event("user_decision_applied", decision_id="new-policy")
        action["event_refs"].append(event["id"])
        self.assertTrue(self.engine._dispatchable(action, self.resources))

    def test_empty_or_failed_initial_preparation_does_not_wait_forever(self):
        action = self.startup()
        for outcome in ("output_accepted", "execution_incomplete"):
            with self.subTest(outcome=outcome):
                self.engine.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
                    "status": "ended", "outcome": outcome, "action": {"role": "research_preparation"}}
                self.assertTrue(self.engine._dispatchable(action, self.resources))

    def test_plan_receives_public_running_preparation_without_private_output(self):
        e = self.engine
        e.runtime["executions"]["E"] = {"id": "E", "role": "research_preparation",
            "status": "running", "input_snapshot": e.head, "goal_revision": 1, "policy_revision": 1,
            "action": {"id": "A", "role": "research_preparation", "reason": "derive last-car recurrence",
                       "repair": {"previous_output": {"secret": "private draft"}}}}
        context = e._context({"role": "research_plan"}, self.root / "plan")
        activities = context.get("ongoing_preparation", [])
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0]["reason"], "derive last-car recurrence")
        self.assertEqual(activities[0]["input_snapshot"], e.head)
        self.assertNotIn("private draft", str(activities))

    def test_task_result_materialization_batches_reads_without_losing_files(self):
        e = self.engine
        files = {f'runtime/artifacts/results/{i}.bin': bytes(range(256)) + bytes([i]) for i in range(12)}
        entries = [{'artifact_ref': path, 'path': Path(path).name,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)} for path, raw in files.items()]
        e.runtime['tasks']['T'] = {**candidate('materialization'), 'id': 'T', 'revision': 1, 'feature_version': 5, 'status': 'active', 'reviews': [], 'results': [
            {'execution_id': 'E', 'output_files': entries}]}
        e.runtime['tasks']['T'].pop('revises_task_id')
        e._save(files)
        with patch.object(e.store._store, '_git', wraps=e.store._store._git) as calls:
            context = e._context({'role': 'research_plan'}, self.root / 'results-plan')
        reads = [c for c in calls.call_args_list if c.args[0] == 'cat-file']
        self.assertEqual(len(reads), 1)
        restored = context['tasks'][0]['results'][0]['output_files']
        self.assertEqual(len(restored), 12)
        for item in restored:
            self.assertEqual((self.root / 'results-plan' / item['local_path']).read_bytes(), files[item['artifact_ref']])

    def test_repeated_idle_save_does_not_publish_but_real_changes_do(self):
        e = self.engine
        e._save()
        first = e.head
        e._save()
        self.assertEqual(e.head, first)
        e.runtime["cycles"] += 1
        e._save()
        self.assertNotEqual(e.head, first)
        second = e.head
        e._save({"runtime/artifacts/idle-test/evidence.bin": b"\x00\xff"})
        self.assertNotEqual(e.head, second)
        self.assertEqual(e.store.read("runtime/artifacts/idle-test/evidence.bin", e.head), b"\x00\xff")

    def test_reopened_idle_engine_does_not_publish_again(self):
        e = self.engine
        e._save()
        head = e.head
        reopened = ResearchEngine(e.store._store.repository, e.instance['id'])
        reopened._save()
        self.assertEqual(reopened.head, head)

    def test_merged_user_requests_keep_all_request_references(self):
        e = self.engine
        e.runtime['queue'] = []
        e._enqueue('research_plan', reason='first instruction', requested_by='UC-first')
        e._enqueue('research_plan', reason='second instruction', requested_by='UC-second')
        self.assertEqual(e.runtime['queue'][0].get('requested_by_refs'), ['UC-first', 'UC-second'])

    def test_readiness_is_derived_and_changes_with_contract_review_evidence(self):
        e = self.engine
        e.runner = ScriptedRunner()
        e.run(max_steps=1)
        tid = next(iter(e.runtime["tasks"]))
        before = deepcopy(e._task_readiness[tid])
        self.assertNotEqual(before["state"], "ready")
        e._save()
        head = e.head
        e._refresh_readiness()
        self.assertEqual(e._task_readiness[tid], before)
        e._save()
        self.assertEqual(e.head, head)
        e.run(max_steps=1)
        self.assertEqual(e.runtime["tasks"][tid]["status"], "planned")
        self.assertEqual(e._task_readiness[tid]["state"], "ready")
        self.assertNotEqual(e._task_readiness[tid], before)
        self.assertNotIn("task_readiness", e.store.load()[2])


if __name__ == "__main__":
    unittest.main()
