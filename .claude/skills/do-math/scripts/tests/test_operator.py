"""Generic scheduled-operator boundary checks without a Windows registration."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math import scheduled_operator as operator  # noqa: E402
from do_math import cli  # noqa: E402


class OperatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.workspace = self.root / "workspace"
        self.repository.mkdir()
        self.workspace.mkdir()
        self.instance = "RI-00000000000000000000000000"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_task_names_are_repository_scoped_and_stable(self) -> None:
        first = operator.task_names(self.repository, self.instance)
        second = operator.task_names(self.repository, self.instance)
        other = operator.task_names(self.root / "other-repository", self.instance)
        self.assertEqual(first, second)
        self.assertNotEqual(first["operator"], other["operator"])
        self.assertIn("Operator", first["operator"])
        self.assertIn("Engine", first["engine"])

    def test_schedule_request_passes_only_generic_instance_coordinates(self) -> None:
        observed: list[list[str]] = []

        def runner(argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            observed.append(argv)
            return subprocess.CompletedProcess(argv, 0, '{"operator":"ready"}', "")

        result = operator.schedule("install", repository=self.repository, instance=self.instance,
                                   workspace=self.workspace, interval_seconds=7200, runner=runner)
        self.assertEqual(result["operator"], "ready")
        self.assertEqual(len(observed), 1)
        command = observed[0]
        self.assertIn("install", command)
        self.assertIn(str(self.repository.resolve()), command)
        self.assertIn(str(self.workspace.resolve()), command)
        self.assertIn(self.instance, command)
        self.assertNotIn("parking-unimodality", " ".join(command))

    def test_hold_and_release_do_not_resume_or_edit_research_state(self) -> None:
        hold = operator.hold(self.workspace, reason="user requested stop")
        self.assertTrue((self.workspace / "operator" / "HOLD.json").exists())
        released = operator.release(self.workspace)
        self.assertEqual(released["released"]["id"], hold["id"])
        self.assertFalse((self.workspace / "operator" / "HOLD.json").exists())
        self.assertTrue((self.workspace / "operator" / "release.json").exists())

    def test_engine_does_not_start_for_hold_or_any_pause(self) -> None:
        commands: list[list[str]] = []
        status = {"status": "ready", "user_pause": False}
        def run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            commands.append(command)
            return subprocess.CompletedProcess(command, 0, '{"status":"ready"}', "")
        with patch.object(operator, "read_status", side_effect=[status, {"status": "waiting", "user_pause": False}]), \
             patch.object(operator.subprocess, "run", side_effect=run):
            result = operator.run_engine(self.repository, self.instance, self.workspace)
            self.assertEqual(result["outcome"], "completed")
            self.assertEqual(result["before"], status)
            self.assertEqual(result["after"]["status"], "waiting")
        operator.hold(self.workspace, reason="hold")
        with patch.object(operator, "read_status", return_value=status), \
             patch.object(operator.subprocess, "run") as run_cli:
            self.assertEqual(operator.run_engine(self.repository, self.instance, self.workspace)["outcome"], "held")
            run_cli.assert_not_called()
        (self.workspace / "operator" / "HOLD.json").unlink()
        with patch.object(operator, "read_status", return_value={"status": "paused", "user_pause": True}), \
             patch.object(operator.subprocess, "run") as run_cli:
            self.assertEqual(operator.run_engine(self.repository, self.instance, self.workspace)["outcome"], "paused")
            run_cli.assert_not_called()
        self.assertIn("run", commands[0])

    def test_context_records_status_and_previous_report_without_state_write(self) -> None:
        report = self.workspace / "operator" / "latest-report.json"
        report.parent.mkdir()
        report.write_text(json.dumps({"outcome": "prior"}), encoding="utf-8")
        context = operator.invocation_context(self.repository, self.instance, self.workspace,
                                              {"status": "ready", "snapshot": "abc"}, self.root)
        self.assertEqual(context["repository"], str(self.repository.resolve()))
        self.assertEqual(context["workspace"], str(self.workspace.resolve()))
        self.assertEqual(context["status"]["snapshot"], "abc")
        self.assertEqual(context["previous_report"], str(report))
        self.assertEqual(context["control_policy"]["user_pause"], "never resume")

    def test_probe_observes_without_starting_a_model_or_engine(self) -> None:
        status = {"status": "ready", "user_pause": None}
        with patch.object(operator, "read_status", return_value=status), \
             patch.object(operator, "ResearchRepository") as repository, \
             patch.object(operator, "ModelRunner") as runner, \
             patch.object(operator, "schedule") as schedule, \
             patch.object(operator, "recovery") as recovery:
            repository.return_value.load.return_value = ("head", {"config": {}}, {})
            result = operator.check(self.repository, self.instance, self.workspace, probe=True)
        self.assertEqual(result, {"outcome": "observed", "status": status, "model_called": False,
            "engine_start": {"outcome": "startable", "before": status}})
        runner.assert_not_called()
        schedule.assert_not_called()
        recovery.assert_not_called()

    def test_automatic_and_user_pause_do_not_trigger_external_recovery(self) -> None:
        for pause in (None, {"reason": "user stop"}):
            with self.subTest(pause=pause), \
                 patch.object(operator, "read_status", return_value={"status": "paused", "user_pause": pause}), \
                 patch.object(operator, "ResearchRepository") as repository, \
                 patch.object(operator, "ModelRunner") as runner, \
                 patch.object(operator, "schedule") as schedule, \
                 patch.object(operator, "recovery") as recovery:
                repository.return_value.load.return_value = ("head", {"config": {}}, {})
                result = operator.check(self.repository, self.instance, self.workspace)
                self.assertEqual(result["outcome"], "paused")
                runner.assert_not_called()
                schedule.assert_not_called()
                recovery.assert_not_called()

    def test_engine_import_failure_is_preserved_before_recovery(self) -> None:
        with patch.object(operator, "read_status", side_effect=SyntaxError("engine broken")), \
             patch.object(operator, "recovery", return_value={"outcome": "fixture-recovered"}) as recover:
            result = operator.check(self.repository, self.instance, self.workspace)
        self.assertEqual(result["outcome"], "fixture-recovered")
        failure = recover.call_args.kwargs["failure"]
        self.assertEqual(failure["error_type"], "SyntaxError")
        self.assertEqual(failure["kind"], "engine_unavailable")
        self.assertEqual(json.loads((self.workspace / "operator" / "engine-failure.json").read_text(encoding="utf-8")), failure)
        with patch.object(operator, "read_status", side_effect=SyntaxError("engine broken")), \
             patch.object(operator, "recovery") as recover:
            result = operator.check(self.repository, self.instance, self.workspace, probe=True)
            self.assertEqual(result["outcome"], "recovery_required")
            recover.assert_not_called()

    def test_engine_child_targets_live_installation_from_frozen_supervisor(self) -> None:
        live = self.root / "live-installation"
        status = {"status": "ready", "user_pause": False}
        with patch.object(operator, "LIVE_INSTALLATION_ROOT", live, create=True), \
             patch.object(operator, "read_status", return_value=status), \
             patch.object(operator.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "{}", "")) as run:
            result = operator.run_engine(self.repository, self.instance, self.workspace)
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(Path(run.call_args.args[0][1]), live / "scripts/do_math.py")

    def test_real_probe_persists_failure_when_engine_has_syntax_error(self) -> None:
        import shutil
        isolated = self.root / "isolated-skill"
        shutil.copytree(SCRIPTS.parent, isolated, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".lake"))
        (isolated / "scripts/do_math/engine.py").write_text("broken engine syntax !!!\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(isolated / "scripts/operator_bootstrap.py"), "check",
            "--repository", str(self.repository), "--instance", self.instance,
            "--workspace", str(self.workspace), "--probe"], capture_output=True, text=True, encoding="utf-8", timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.assertEqual(result.returncode, 0, result.stderr)
        failure = json.loads(result.stdout)
        self.assertEqual(failure["error_type"], "SyntaxError")
        self.assertEqual(failure["outcome"], "recovery_required")
        self.assertEqual(json.loads((self.workspace / "operator/engine-failure.json").read_text(encoding="utf-8")), failure)

    def test_init_keeps_created_instance_when_schedule_registration_fails(self) -> None:
        subprocess.run(["git", "-C", str(self.repository), "init", "-q"], check=True)
        arguments = cli.build_parser().parse_args((
            "init", "--repository", str(self.repository), "--workspace", str(self.workspace),
            "--goal", "preserve created instance after scheduler failure", "--config-file", str(self._config({"scholarly_enabled": False})),
        ))
        with patch.object(cli.scheduled_operator, "schedule", side_effect=RuntimeError("scheduler unavailable")):
            result, code = cli.execute(arguments)
        self.assertEqual(code, 5)
        self.assertTrue(result["instance_id"])
        self.assertEqual(result["operator_schedule"]["status"], "failed")
        self.assertIn("operator install", result["operator_schedule"]["reconcile"])

    def test_new_instance_installs_the_operator_every_two_hours_by_default(self) -> None:
        subprocess.run(["git", "-C", str(self.repository), "init", "-q"], check=True)
        arguments = cli.build_parser().parse_args((
            "init", "--repository", str(self.repository), "--workspace", str(self.workspace),
            "--goal", "use the default independent operator schedule", "--config-file", str(self._config({"scholarly_enabled": False})),
        ))
        with patch.object(cli.scheduled_operator, "schedule", return_value={"operator": "ready"}) as schedule:
            result, code = cli.execute(arguments)
        self.assertEqual(code, 0)
        self.assertEqual(schedule.call_args.args, ("install",))
        self.assertEqual(schedule.call_args.kwargs["interval_seconds"], 7200)
        self.assertEqual(result["operator_schedule"], {"operator": "ready"})

    def test_cli_emits_byte_bearing_operator_receipt_as_json(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            cli._emit({"raw": b"preserved bytes"}, command="operator check", request_id="QR-receipt")
        self.assertEqual(json.loads(output.getvalue())["result"]["raw"]["base64"], "cHJlc2VydmVkIGJ5dGVz")

    def test_release_submits_a_conditional_resume_even_before_hold_pause_is_applied(self) -> None:
        args = cli.build_parser().parse_args(['operator', 'release', '--repository', str(self.repository),
                                             '--instance', self.instance])
        with patch.object(cli, '_operator_workspace', return_value=self.workspace), \
             patch.object(operator, 'release', return_value={'released': {'id': 'pending-hold'}}), \
             patch.object(operator, 'read_status', return_value={'user_pause': None}), \
             patch.object(cli, '_control', return_value={'effect': 'pending engine processing'}) as submit:
            result, code = cli.execute(args)
        submit.assert_called_once()
        self.assertEqual(submit.call_args.kwargs['config'], {
            'expected_user_pause_reason': 'User requested scheduled operator HOLD pending-hold'})
        self.assertEqual((code, result['resume']['effect']), (0, 'pending engine processing'))

    def test_completed_instance_is_observed_without_starting_an_operator_model(self) -> None:
        completed = {"status": "completed", "user_pause": None, "snapshot": "finished"}
        with patch.object(operator, "read_status", return_value=completed), \
             patch.object(operator, "ModelRunner") as runner, \
             patch.object(operator, "ResearchRepository") as repository:
            repository.return_value.load.return_value = ("head", {"config": {}}, {})
            result = operator.check(self.repository, self.instance, self.workspace)
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["status"], completed)
        runner.assert_not_called()

    def _config(self, value: dict) -> Path:
        path = self.root / "config.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main(verbosity=2)
