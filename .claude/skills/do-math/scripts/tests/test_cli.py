"""Subprocess checks for the do-math command surface without model execution."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
ENTRYPOINT = SCRIPTS / "do_math.py"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        subprocess.run(["git", "-C", str(self.repository), "init", "-q"], check=True)
        self.workspace = self.root / "workspace"
        initialized = self.run_cli(
            "init", "--repository", str(self.repository), "--workspace", str(self.workspace),
            "--goal", "Prove a small theorem", "--title", "Small theorem",
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.initial = json.loads(initialized.stdout)
        self.instance = self.initial["instance_id"]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ENTRYPOINT), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=SCRIPTS.parents[3],
        )

    def instance_args(self) -> tuple[str, ...]:
        return ("--repository", str(self.repository), "--instance", self.instance)

    def test_help_and_input_error_exit_codes_are_structured(self) -> None:
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("init", help_result.stdout)
        self.assertIn("request", help_result.stdout)
        invalid = self.run_cli("init", "--repository", str(self.repository), "--workspace", str(self.workspace))
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(json.loads(invalid.stdout)["kind"], "input_error")

    def test_status_input_pause_and_configure_apply_without_running_model(self) -> None:
        status = self.run_cli("status", *self.instance_args(), "--json")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(json.loads(status.stdout)["status"], "ready")

        incoming = self.run_cli("input", *self.instance_args(), "--text", "Use induction")
        self.assertEqual(incoming.returncode, 0, incoming.stderr)
        self.assertTrue(json.loads(incoming.stdout)["accepted"])
        paused = self.run_cli("pause", *self.instance_args(), "--reason", "review inputs")
        self.assertEqual(paused.returncode, 0, paused.stderr)
        self.assertEqual(json.loads(paused.stdout)["status"], "paused")

        config_path = self.root / "config.json"
        config_path.write_text(json.dumps({"work_calls": 4}), encoding="utf-8")
        configured = self.run_cli("configure", *self.instance_args(), "--config-file", str(config_path))
        self.assertEqual(configured.returncode, 0, configured.stderr)
        self.assertEqual(json.loads(configured.stdout)["config"]["work_calls"], 4)

    def test_request_applies_a_maintenance_queue_entry_without_model_execution(self) -> None:
        requested = self.run_cli("request", *self.instance_args(), "--role", "maintenance", "--reason", "inspect state")
        self.assertEqual(requested.returncode, 0, requested.stderr)
        result = json.loads(requested.stdout)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["effect"], "applied")
        status = self.run_cli("status", *self.instance_args(), "--json")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertGreaterEqual(json.loads(status.stdout)["pending_actions"], 2)
        from do_math.repository import ResearchRepository
        _, _, runtime = ResearchRepository(self.repository, self.instance).load()
        self.assertEqual(runtime["queue"][0]["role"], "maintenance")
        self.assertFalse(runtime["executions"], "request must not start a model execution")

    def test_query_read_export_and_check_use_a_fixed_repository_snapshot(self) -> None:
        records = self.run_cli("query", *self.instance_args(), "--limit", "1")
        self.assertEqual(records.returncode, 0, records.stderr)
        record_page = json.loads(records.stdout)
        self.assertGreaterEqual(record_page["total"], 2)
        self.assertTrue(any(item["record"]["family"] == "grant" for item in record_page["items"]))
        self.assertEqual(record_page["loaded"], 1)
        self.assertEqual(record_page["items"][0]["record"]["family"], "grant")
        self.assertEqual(record_page["items"][0]["record"]["status"], "active")
        self.assertIsNotNone(record_page["next_cursor"])
        queried = self.run_cli("query", *self.instance_args(), "--files", "--prefix", "research/", "--text", "small", "--limit", "1")
        self.assertEqual(queried.returncode, 0, queried.stderr)
        query = json.loads(queried.stdout)
        self.assertEqual(query["total"], 1)
        read = self.run_cli("read", *self.instance_args(), "--path", "research/instance.json")
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(json.loads(read.stdout)["path"], "research/instance.json")
        destination = self.root / "export"
        exported = self.run_cli("export", *self.instance_args(), "--destination", str(destination))
        self.assertEqual(exported.returncode, 0, exported.stderr)
        self.assertTrue((destination / "research" / "instance.json").exists())
        checked = self.run_cli("check", *self.instance_args())
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertTrue(json.loads(checked.stdout)["passed"])

    def test_create_repository_is_explicit_and_only_accepts_empty_directory(self) -> None:
        created = self.root / "created"
        result = self.run_cli(
            "init", "--create-repository", "--repository", str(created), "--workspace", str(self.root / "other-workspace"),
            "--goal", "A research goal",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((created / ".git").exists())
        nonempty = self.root / "nonempty"
        nonempty.mkdir()
        (nonempty / "file.txt").write_text("x", encoding="utf-8")
        refused = self.run_cli(
            "init", "--create-repository", "--repository", str(nonempty), "--workspace", str(self.root / "third-workspace"),
            "--goal", "A research goal",
        )
        self.assertEqual(refused.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
