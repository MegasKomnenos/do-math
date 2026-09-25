from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, control, initialize, _repository
from test_engine import ScriptedRunner
from research_fixtures import activate, install_adapter_fixture
from do_math.repository import ResearchRepository


class ControlTransitionTests(unittest.TestCase):
    def setUp(self):
        install_adapter_fixture(self)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        value = initialize(self.repo, goal="control transition fixture", workspace=self.root / "work",
                           config={"scholarly_enabled": False, "operator_enabled": False, "lean_command": ["test-lean"]})
        self.iid = value["instance_id"]
        self.store = _repository(self.repo, self.iid)

    def tearDown(self):
        self.temp.cleanup()

    def update(self, change):
        head, instance, runtime = self.store.load()
        change(instance, runtime)
        self.store.save_with_state(head, instance, runtime)[0]

    def test_pause_and_resume_cannot_reopen_a_publicly_closed_instance(self):
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
        cli = Path(__file__).resolve().parents[1] / "do_math.py"
        response = subprocess.run([sys.executable, str(cli), "resume", "--repository", str(self.repo),
                                   "--instance", self.iid], check=True, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(response.stdout)["result"]["effect"], "rejected")

    def test_stale_request_is_consumed_and_does_not_poison_later_controls(self):
        engine = ResearchEngine(self.repo, self.iid, runner=ScriptedRunner())
        activate(engine, self.root, initialization_runner=ScriptedRunner())
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
        control(self.repo, self.iid, "request", config={"role": "maintenance"})
        control(self.repo, self.iid, "close")
        engine = ResearchEngine(self.repo, self.iid)
        engine.process_controls()
        status = engine.status()
        self.assertEqual(status["status"], "closed")
        self.assertEqual(status["pending_actions"], 0)
        self.assertEqual(status["pending_controls"], 0)

    def test_crash_marks_owning_activity_unresolved(self):
        engine = ResearchEngine(self.repo, self.iid, runner=ScriptedRunner())
        activate(engine, self.root, initialization_runner=ScriptedRunner())
        action = engine.runtime['queue'][0]
        execution = engine._register_execution(action, {'id': 'EX-crashed', 'role': action['role'],
            'status': 'running', 'input_snapshot': engine.head, 'input_manifest': []})
        engine.runtime['active_execution'] = execution['id']
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
