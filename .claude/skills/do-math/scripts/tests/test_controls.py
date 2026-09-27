from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, control, _repository
from test_engine import ScriptedRunner
from test_lifecycle_engine import initialized_instance
from research_fixtures import install_adapter_fixture, restore_template, run_cli
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
        self.store = _repository(self.repo, self.iid)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
