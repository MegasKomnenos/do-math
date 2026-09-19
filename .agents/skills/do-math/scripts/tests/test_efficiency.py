"""Efficiency changes must preserve obligations, inputs and published state."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, initialize, control
from do_math.governance import apply_decision
from do_math.model_policy import MODELS
from do_math.planning import contract_hash
from do_math.input_basis import capture_decision_basis
from test_engine import ScriptedRunner, context_from


class EfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        result = initialize(repo, goal="bounded research", workspace=self.root / "work",
                            config={"operator_enabled": False, "scholarly_enabled": False})
        self.engine = ResearchEngine(repo, result["instance_id"])
        self.resources = {pool: {model: {"available": 3} for model in MODELS.values()}
                          for pool in ("work", "operations")}

    def startup(self):
        e = self.engine
        e.instance, e.runtime, decision = apply_decision(e.instance, e.runtime,
            {"kind": "academic_requirements", "requirements": [
                {"id": "explain", "scope": "solution", "criteria": ["explain structure"],
                 "assessor": "research_plan"}]}, source_ref="initial-user-decision")
        e._lifecycle_event("user_decision_applied", source_ref="initial-user-decision",
                           decision_id=decision["id"])
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

    def test_initial_registration_waits_but_preserves_its_event(self):
        action = self.startup()
        before = deepcopy(self.engine.runtime["events"])
        self.assertFalse(self.engine._dispatchable(action, self.resources))
        self.assertEqual(self.engine.runtime["events"], before)
        self.assertTrue(self.engine.runtime["pending_events"])

    def test_scheduler_first_plan_receives_an_approved_candidate_and_consumes_registration(self):
        self.startup()
        e = self.engine
        e.runner = ScriptedRunner()
        e._save()
        e.run(max_steps=3)
        plans = [context_from(prompt) for role, prompt in e.runner.prompts if role == 'research_plan']
        self.assertEqual(len(plans), 1)
        self.assertEqual(len(plans[0]['ready_task_ids']), 1)
        self.assertEqual([role for role, _ in e.runner.prompts],
                         ['research_preparation', 'task_contract_review', 'research_plan'])
        event = next(row for row in e.runtime['events'] if row['kind'] == 'user_decision_applied')
        self.assertTrue(event.get('consumed_by'))
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
        e.runtime["tasks"]["first"]["status"] = "ready"
        # The remaining reviews are awaited only up to plan_settle_seconds, never indefinitely.
        self.assertFalse(e._dispatchable(action, self.resources))
        self.assertEqual(action["dispatch_wait"]["kind"], "plan_settle")
        from datetime import datetime, timedelta, timezone
        action["settle_started_at"] = (datetime.now(timezone.utc) - timedelta(seconds=301)).isoformat()
        self.assertTrue(e._dispatchable(action, self.resources))

    def test_pause_received_during_input_preparation_prevents_model_start(self):
        e = self.engine
        original = e._context
        def prepare(action, workspace):
            context = original(action, workspace)
            control(e.store._store.repository, e.instance["id"], "pause", text="stop during materialization")
            return context
        with patch.object(e, '_context', side_effect=prepare):
            generator = e._call_steps(e.runtime["queue"][0], time.monotonic() + 30)
            with self.assertRaises(StopIteration):
                next(generator)
        self.assertEqual(e.runtime["status"], "paused")
        self.assertEqual(e.runtime["executions"], {})
        self.assertEqual(list((self.root / 'work' / 'runs').iterdir()), [])

    def test_pause_before_model_resume_has_no_checkpoint_grace(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0], time.monotonic() + 60)
        arguments = next(steps)
        arguments['on_started']({'pid': 1})
        control(e.store._store.repository, e.instance['id'], 'pause', text='stop before model resume')
        try:
            self.assertTrue(arguments['should_stop'](), 'a suspended model must not resume for checkpoint grace')
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'stopped before resume'})

    def test_running_model_keeps_checkpoint_grace_after_initial_check(self):
        e = self.engine
        steps = e._call_steps(e.runtime['queue'][0], time.monotonic() + 60)
        arguments = next(steps)
        arguments['on_started']({'pid': 1})
        self.assertFalse(arguments['should_stop']())
        control(e.store._store.repository, e.instance['id'], 'pause', text='checkpoint running work')
        try:
            self.assertFalse(arguments['should_stop']())
        finally:
            with self.assertRaises(StopIteration):
                steps.send({'status': 'stopped', 'output': None, 'usage': {}, 'error': 'checkpoint collected'})

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
        e.runtime['tasks']['T'] = {'id': 'T', 'status': 'assessing', 'results': [
            {'execution_id': 'E', 'output_files': entries}]}
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
        e.runtime["questions"].append("real change with same status")
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

    def test_readiness_timestamp_changes_only_with_its_evidence(self):
        e = self.engine
        task = {"id": "T", "revision": 1, "status": "planned", "title": "bounded",
            "question": "q", "scope": "s", "expected_result": "r", "completion_criteria": ["c"],
            "inputs": [], "reuse": [], "dependencies": [], "results": [], "reviews": [],
            "work_class": "nonformal", "model_assessment": {"difficulty": "low", "importance": "low", "reason": "bounded"}}
        e.runtime["tasks"]["T"] = task
        e.lifecycle_clock = lambda: "2026-09-17T00:00:00+00:00"
        e._refresh_readiness()
        before = deepcopy(e.runtime["task_readiness"]["T"])
        e._save()
        head = e.head
        e.lifecycle_clock = lambda: "2026-09-17T00:00:01+00:00"
        e._refresh_readiness()
        self.assertEqual(e.runtime["task_readiness"]["T"], before)
        e._save()
        self.assertEqual(e.head, head)
        task = e.runtime["tasks"]["T"]
        task["reviews"].append({"id": "CR", "decision": "approved", "revision": 1,
            "contract_sha256": contract_hash(task), "goal_revision": 1, "policy_revision": 1,
            "decision_basis": capture_decision_basis(e.instance, e.runtime, [task['id']])})
        e._refresh_readiness()
        self.assertEqual(e.runtime["task_readiness"]["T"]["state"], "ready")
        self.assertNotEqual(e.runtime["task_readiness"]["T"]["evaluated_at"], before["evaluated_at"])


if __name__ == "__main__":
    unittest.main()
