import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("parking_operator", Path(__file__).with_name("supervisor.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OperatorTests(unittest.TestCase):
    def test_engine_never_resumes_a_paused_or_finished_instance(self):
        for state in ("paused", "waiting", "completed", "closed", "budget_exhausted"):
            self.assertFalse(module.engine_may_start({"status": state}, False))
        for state in ("ready", "running"):
            self.assertTrue(module.engine_may_start({"status": state}, False))
            self.assertFalse(module.engine_may_start({"status": state}, True))

    def test_handoff_summary_does_not_repeat_execution_history(self):
        summary = module.status_summary({"snapshot": "abc", "status": "paused", "questions": ["q"],
                                         "checkpoints": {"large": "history"}, "usage": [1, 2]})
        self.assertEqual(summary["snapshot"], "abc")
        self.assertEqual(summary["questions"], ["q"])
        self.assertNotIn("checkpoints", summary)
        self.assertNotIn("usage", summary)

    def test_commands_preserve_target_and_use_configured_mcp(self):
        config = json.loads(module.CONFIG.read_text(encoding="utf-8"))
        run = module.cli_argv(config, "run")
        self.assertEqual(run[run.index("--instance") + 1], config["instance"])
        self.assertEqual(run[run.index("--repository") + 1], config["repository"])
        codex = module.codex_argv(config, Path("C:/test dir"))
        self.assertNotIn("--ignore-user-config", codex)
        self.assertIn("C:/test dir/report.json".replace("/", "\\"), codex)
        self.assertEqual(codex[-1], "-")

    def test_release_records_the_exact_hold_and_does_not_resume_the_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            logs = Path(directory)
            config = logs / "config.json"
            config.write_text(json.dumps({"logs": directory}), encoding="utf-8")
            (logs / "HOLD").write_text(json.dumps({"id": "hold-test-1", "started_at": "2026-09-16T00:00:00+00:00"}), encoding="utf-8")
            with patch.object(module, "CONFIG", config), patch.object(module.sys, "argv", ["supervisor", "release"]), \
                    patch.object(module.subprocess, "run") as runner:
                self.assertEqual(module.main(), 0)
                runner.assert_not_called()
                self.assertFalse((logs / "HOLD").exists())
                release = json.loads((logs / "release.json").read_text(encoding="utf-8"))
                self.assertEqual(release["hold"]["id"], "hold-test-1")
                first = (logs / "release.json").read_bytes()
                self.assertEqual(module.main(), 0)
                self.assertEqual(first, (logs / "release.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
