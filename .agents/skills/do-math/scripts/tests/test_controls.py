from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, control, initialize
from do_math.repository import ResearchRepository


class ControlTransitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        value = initialize(self.repo, goal="control transition fixture", workspace=self.root / "work")
        self.iid = value["instance_id"]
        self.store = ResearchRepository(self.repo, self.iid)

    def tearDown(self):
        self.temp.cleanup()

    def update(self, change):
        head, instance, runtime = self.store.load()
        change(instance, runtime)
        self.store.save(head, instance, runtime)

    def test_pause_and_resume_cannot_reopen_a_completed_instance(self):
        self.update(lambda i, r: r.update(status="completed", queue=[]))
        control(self.repo, self.iid, "pause")
        engine = ResearchEngine(self.repo, self.iid)
        self.assertEqual(engine.process_controls()["status"], "completed")
        rejected = control(self.repo, self.iid, "resume")
        status = engine.process_controls()
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["pending_controls"], 0)
        _, _, runtime = self.store.load()
        self.assertEqual(runtime["history"][-1]["kind"], "rejected_user_control")
        self.assertEqual(runtime["history"][-1]["request"]["id"], rejected["request_id"])
        cli = Path(__file__).resolve().parents[1] / "do_math.py"
        response = subprocess.run([sys.executable, str(cli), "resume", "--repository", str(self.repo),
                                   "--instance", self.iid], check=True, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(json.loads(response.stdout)["effect"], "rejected")

    def test_stale_request_is_consumed_and_does_not_poison_later_controls(self):
        self.update(lambda i, r: r["tasks"].update({"TK-ready": {"id": "TK-ready", "title": "fixture", "status": "ready"}}))
        request = control(self.repo, self.iid, "request", config={"role": "supplemental_research", "target": "TK-ready"})
        self.update(lambda i, r: r["tasks"]["TK-ready"].update(status="performing"))
        control(self.repo, self.iid, "pause")
        status = ResearchEngine(self.repo, self.iid).process_controls()
        self.assertEqual(status["status"], "paused")
        self.assertEqual(status["pending_controls"], 0)
        _, _, runtime = self.store.load()
        self.assertIn(request["request_id"], runtime["processed_controls"])
        self.assertEqual(runtime["tasks"]["TK-ready"]["status"], "performing")
        self.assertTrue(any(h["kind"] == "rejected_user_control" for h in runtime["history"]))

    def test_request_accepted_before_completion_does_not_reopen_it(self):
        control(self.repo, self.iid, "request", config={"role": "maintenance"})
        self.update(lambda i, r: r.update(status="completed", queue=[]))
        status = ResearchEngine(self.repo, self.iid).process_controls()
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["pending_actions"], 0)
        self.assertEqual(status["pending_controls"], 0)

    def test_crash_marks_owning_activity_unresolved(self):
        def crashed(instance, runtime):
            runtime["activities"]["AY-crashed"] = {"id": "AY-crashed", "role": "research_preparation", "status": "active", "execution_ids": ["EX-crashed"]}
            runtime["executions"]["EX-crashed"] = {"id": "EX-crashed", "activity_id": "AY-crashed", "role": "research_preparation", "status": "running"}
            runtime["active_execution"] = "EX-crashed"
        self.update(crashed)
        status = ResearchEngine(self.repo, self.iid).run(max_steps=1)
        self.assertEqual(status["status"], "paused")
        _, _, runtime = self.store.load()
        self.assertEqual(runtime["activities"]["AY-crashed"]["status"], "unresolved")
        self.assertEqual(runtime["executions"]["EX-crashed"]["outcome"], "execution_incomplete")


if __name__ == "__main__":
    unittest.main(verbosity=2)
