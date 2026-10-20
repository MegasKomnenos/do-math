import json
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

from support import ENGINE, Fixture, run, write_json


class RunTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.close)
        self.f.new_phase(kind="review")
        self.command = (sys.executable, str(ENGINE / "tests" / "fake_codex.py"))

    def test_parallel_barriers_manager_order_and_nonzero_exits(self):
        run.run(self.f.repo, self.f.records, "001", command=self.command)
        events = self.f.records / "events"
        names = {"001-core", "001-cli", "001-manager", "002-followup", "002-manager"}
        self.assertEqual({p.stem for p in events.glob("*.finished")}, names)
        for name in names:
            self.assertTrue((events / f"{name}.started").is_file())
        self.assertGreater((self.f.phase_path() / "logs/task-core.log").stat().st_size, 100000)
        self.assertIn(b"manager stderr", (self.f.phase_path() / "logs/manager.log").read_bytes())
        self.assertFalse(any(self.f.records.glob("phases/*/tasks/*/report.json")))

    def test_missing_manager_result_is_not_success(self):
        with patch.dict("os.environ", {"PHASE_TEST_NO_MANAGER_RESULT": "1"}):
            with self.assertRaises(FileNotFoundError):
                run.run(self.f.repo, self.f.records, "001", command=self.command)
        self.assertFalse((self.f.records / "events/002-followup.started").exists())

    def test_cli_forwards_codex_options_to_every_session(self):
        commands = []

        def child(command, **kwargs):
            commands.append(command)
            if "역할: manager" in kwargs["input"].decode("utf-8"):
                (self.f.phase_path() / "manager.json").write_text(json.dumps({"next": None}), encoding="utf-8")
            return subprocess.CompletedProcess(command, 0)

        argv = [str(ENGINE / "run.py"), str(self.f.repo), str(self.f.records), "001", "--sandbox", "workspace-write"]
        with patch.object(sys, "argv", argv), patch("subprocess.run", side_effect=child):
            runpy.run_path(str(ENGINE / "run.py"), run_name="__main__")
        self.assertEqual(len(commands), 3)
        for command in commands:
            self.assertEqual(command[:4], ["codex", "exec", "--sandbox", "workspace-write"])

    def test_task_selections_and_global_manager_selection(self):
        spec = self.f.spec()
        spec["tasks"][0].update(model="task-model", effort="low")
        self.f.save_spec(spec)
        write_json(self.f.records / "settings.json", {"manager": {"model": "manager-model", "effort": "high"}})
        commands = {}

        def child(command, **kwargs):
            fields = dict(line.split(": ", 1) for line in kwargs["input"].decode("utf-8").splitlines() if ": " in line)
            commands[(fields["phase"], fields["task"])] = command
            if fields["역할"] == "manager":
                directory = self.f.phase_path(fields["phase"])
                write_json(directory / "manager.json", {"next": "002" if fields["phase"] == "001" else None})
            return subprocess.CompletedProcess(command, 0)

        base = ("codex", "exec", "--model", "base-model", "-c", 'model_reasoning_effort="medium"')
        with patch("subprocess.run", side_effect=child):
            run.run(self.f.repo, self.f.records, "001", command=base)
        self.assertIn("task-model", commands[("001", "core")])
        self.assertNotIn("base-model", commands[("001", "core")])
        self.assertIn('model_reasoning_effort="low"', commands[("001", "core")])
        self.assertIn("base-model", commands[("001", "cli")])
        self.assertIn('model_reasoning_effort="medium"', commands[("001", "cli")])
        for phase in ("001", "002"):
            self.assertIn("manager-model", commands[(phase, "-")])
            self.assertEqual(commands[(phase, "-")].count("--model"), 1)
            self.assertIn('model_reasoning_effort="high"', commands[(phase, "-")])

    def test_model_override_handles_codex_flag_spellings(self):
        for flags in (("-m", "base"), ("--model", "base"), ("--model=base",), ("-mbase",)):
            with self.subTest(flags=flags):
                result = run.selected_command(("codex", "exec", *flags, "--ephemeral"), {"model": "chosen"})
                self.assertEqual(result, ["codex", "exec", "--ephemeral", "--model", "chosen"])


if __name__ == "__main__":
    unittest.main()
