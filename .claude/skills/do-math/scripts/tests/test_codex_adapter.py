from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from do_math import claude_worker, cli_worker, codex_worker
from do_math.codex_adapter import CLIExecution, CodexExecAdapter
from do_math.codex_stream import parse_jsonl as _parse_jsonl
from do_math.windows_job import JobInspection
from provider_fixtures import FakeJob


class CodexWorkerTests(unittest.TestCase):
    def test_build_argv_is_direct_cli_with_isolating_probe_flags(self):
        request = {"codex_path": "C:/Codex/codex.exe", "prompt_path": "p", "cwd": "C:/work", "model": "gpt-x",
                   "effort": "high", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 1,
                   "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s", "windows_sandbox": "unelevated"}
        argv = codex_worker.build_argv(request)
        self.assertEqual(argv[:4], ["C:/Codex/codex.exe", "--ask-for-approval", "never", "exec"])
        self.assertIn("--json", argv); self.assertIn("--ephemeral", argv); self.assertIn("--ignore-user-config", argv)
        self.assertIn("--ignore-rules", argv); self.assertIn("--skip-git-repo-check", argv)
        self.assertIn("project_doc_max_bytes=0", argv)
        self.assertIn('windows.sandbox="unelevated"', argv)
        self.assertEqual(argv[-1], "-")
        self.assertNotIn("shell", " ".join(argv).lower())

    def test_surface_requires_the_flags_used_by_the_worker(self):
        import subprocess
        flags = [b"--json", b"--output-last-message", b"--model", b"--sandbox", b"--ephemeral",
                 b"--ignore-user-config", b"--ignore-rules", b"--skip-git-repo-check", b"--output-schema",
                 b"--config", b"--strict-config", b"--color", b"--cd"]
        for missing in (None, b"--strict-config", b"--color", b"--cd"):
            with self.subTest(missing=missing):
                adapter = CodexExecAdapter("fixture-cli")
                results = [subprocess.CompletedProcess([], 0, b"fixture-version"),
                           subprocess.CompletedProcess([], 0, b"--ask-for-approval"),
                           subprocess.CompletedProcess([], 0, b" ".join(flag for flag in flags if flag != missing))]
                with patch("do_math.codex_adapter.subprocess.run", side_effect=results), \
                     patch.object(adapter, "capability_identity", return_value={"fixture": True}):
                    description = adapter.describe()
                self.assertEqual(description["verified"], missing is None)

    def test_worker_does_not_accept_fake_argument_prefixes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prompt = root / "prompt"; prompt.write_bytes(b"hello")
            request = {"codex_path": sys.executable, "prompt_path": str(prompt), "cwd": str(root), "model": "gpt-x",
                       "effort": "low", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 5,
                       "stdout_path": str(root / "out"), "stderr_path": str(root / "err"), "final_path": str(root / "final"), "status_path": str(root / "status")}
            request_path = root / "request.json"
            request_path.write_text(json.dumps({**request, "codex_argv": [sys.executable, str(root / "fake.py")]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown worker request fields: codex_argv"):
                codex_worker.run(request_path)
            request_path.write_text(json.dumps(request), encoding="utf-8")
            captured = {}
            class Process:
                returncode = 0
                def __init__(self, command, **options): captured.update(command=command, env=options["env"], shell=options["shell"])
                def communicate(self, input=None, timeout=None): captured["stdin"] = input; return b"", b""
            old = os.environ.get("OPENAI_API_KEY"); os.environ["OPENAI_API_KEY"] = "must-not-pass"
            try:
                self.assertEqual(codex_worker.run(request_path, spawn=Process), 0)
            finally:
                if old is None: os.environ.pop("OPENAI_API_KEY", None)
                else: os.environ["OPENAI_API_KEY"] = old
            self.assertEqual(captured["command"], codex_worker.build_argv(request))
            self.assertNotIn("OPENAI_API_KEY", captured["env"])
            self.assertFalse(captured["shell"])
            self.assertEqual(captured["stdin"], b"hello")
            self.assertEqual(json.loads((root / "status").read_text())["cli_exit_code"], 0)

    def test_sanitized_environment_removes_every_forced_api_route(self):
        clean = codex_worker.sanitized_environment({"OPENAI_API_KEY": "x", "CODEX_API_KEY": "x",
                                                    "CODEX_ACCESS_TOKEN": "x", "OPENAI_BASE_URL": "x",
                                                    "PATH": "safe"})
        self.assertEqual(clean, {"PATH": "safe"})

    def test_invalid_timeout_duplicate_json_and_windows_sandbox_fail_before_start(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text('{"codex_path":"x","codex_path":"x"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                codex_worker.load_request(path)
            request = {"codex_path": "x", "prompt_path": "p", "cwd": "c", "model": "m", "effort": "low",
                       "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": float("nan"),
                       "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s"}
            path.write_text(json.dumps(request), encoding="utf-8")
            # The request file is parsed strictly: a named non-finite constant never reaches the field checks.
            with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
                codex_worker.load_request(path)
            request["max_runtime_seconds"] = 0
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "max_runtime"):
                codex_worker.load_request(path)
            request["max_runtime_seconds"] = 1; request["windows_sandbox"] = "none"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "windows_sandbox"):
                codex_worker.load_request(path)

    def test_scholarly_is_the_only_explicit_mcp_and_uses_workspace_data_directory(self):
        request = {"codex_path": "C:/Codex/codex.exe", "prompt_path": "p", "cwd": "C:/work", "model": "gpt-x",
                   "effort": "low", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 1,
                   "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s",
                   "scholarly_server": {"command": "python", "args": ["C:/server.py"]}}
        argv = codex_worker.build_argv(request)
        overrides = [argv[index + 1] for index, value in enumerate(argv[:-1]) if value == "--config"]
        self.assertIn('mcp_servers.scholarly.command="python"', overrides)
        args = next(value for value in overrides if value.startswith("mcp_servers.scholarly.args="))
        self.assertIn('"C:/server.py"', args)
        self.assertIn('"--data-dir"', args)
        self.assertIn("scholarly-data", args)
        self.assertFalse(any("mcp_servers." in value and "scholarly" not in value for value in overrides))

    def test_worker_remains_importable_as_its_direct_job_root(self):
        worker = Path(codex_worker.__file__)
        result = __import__("subprocess").run([sys.executable, str(worker)], capture_output=True, timeout=10)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: codex_worker.py REQUEST.json", result.stderr)

    def test_claude_worker_remains_importable_as_its_direct_job_root(self):
        worker = Path(claude_worker.__file__)
        result = __import__("subprocess").run([sys.executable, str(worker)], capture_output=True, timeout=10)
        self.assertNotIn(b"No module named", result.stderr)
        self.assertIn(b"usage: claude_worker.py REQUEST.json", result.stderr)

    def test_unknown_worker_request_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = {"codex_path": sys.executable, "prompt_path": str(root / "prompt"), "cwd": str(root / "work"),
                       "model": "m", "effort": "low", "sandbox": "read-only", "approval_policy": "never",
                       "max_runtime_seconds": 1, "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s",
                       "file_system": {}}
            path = root / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown worker request fields"):
                codex_worker.load_request(path)

    def test_jsonl_tail_and_missing_terminal_are_not_success(self):
        parsed = _parse_jsonl(b'{"type":"thread.started","thread_id":"t"}\nnot-json')
        self.assertEqual(parsed["thread_id"], "t")
        self.assertFalse(parsed["turn_completed"])
        self.assertGreater(parsed["unparsed_tail_bytes"], 0)

    def test_ambiguous_or_nonfinite_native_events_cannot_establish_completion(self):
        prefix = (b'{"type":"thread.started","thread_id":"t"}\n'
                  b'{"type":"turn.started"}\n')
        invalid = [b'{"type":"turn.failed","type":"turn.completed"}\n',
                   b'{"type":"turn.completed","usage":{"tokens":1,"tokens":2}}\n',
                   b'{"type":"turn.completed","usage":{"cost":NaN}}\n',
                   b'{"type":"turn.completed","usage":{"cost":Infinity}}\n',
                   b'{"type":"turn.completed","usage":{"cost":-Infinity}}\n',
                   b'{"type":"turn.completed","usage":{"cost":1e999}}\n']
        for terminal in invalid:
            with self.subTest(terminal=terminal):
                parsed = _parse_jsonl(prefix + terminal)
                self.assertFalse(parsed["parse_complete"])
                self.assertFalse(parsed["turn_completed"])
                self.assertEqual(parsed["parsed_bytes"], len(prefix))
                self.assertEqual(parsed["unparsed_tail_bytes"], len(terminal))
                self.assertEqual(parsed["unknown_events"][0]["kind"], "invalid_jsonl")
        valid = _parse_jsonl(prefix + b'{"type":"turn.completed","usage":{"cost":0.25}}\n')
        self.assertTrue(valid["parse_complete"])
        self.assertTrue(valid["turn_completed"])
        self.assertEqual(valid["usage"], [{"cost": 0.25}])

    def test_collect_rejects_malformed_tail_even_with_turn_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout, stderr, final, status = (root / name for name in ("o", "e", "f", "s"))
            stdout.write_bytes(b'{"type":"turn.completed"}\nbroken')
            stderr.write_bytes(b""); final.write_bytes(b"final")
            status.write_text('{"state":"exited","cli_exit_code":0}', encoding="utf-8")
            execution = CLIExecution(__import__("hashlib").sha256(b"{}").hexdigest(),
                                     __import__("hashlib").sha256(b"p").hexdigest(), ("worker",), stdout, stderr, final, status,
                                     FakeJob(JobInspection(0, (), True)), None, b"{}", b"p")
            result = CodexExecAdapter(sys.executable).collect(execution)
            self.assertEqual(result["result"], "incomplete")
            self.assertIn("jsonl_parse_incomplete", result["reasons"])

    def test_collect_reports_start_snapshot_bytes_without_rereading_them(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout, stderr, final, status = (root / name for name in ("o", "e", "f", "s"))
            stdout.write_bytes(b""); stderr.write_bytes(b""); final.write_bytes(b"final")
            status.write_text('{"state":"exited","cli_exit_code":0}', encoding="utf-8")
            # The private snapshot files are absent: collection uses the bytes hashed at start.
            execution = CLIExecution(hashlib.sha256(b"{}").hexdigest(),
                                     hashlib.sha256(b"p").hexdigest(), ("worker",), stdout, stderr, final, status,
                                     FakeJob(JobInspection(0, (), True)), None, b"{}", b"p")
            result = CodexExecAdapter(sys.executable).collect(execution)
        self.assertEqual(result["source_request"], {"present": True, "bytes": 2,
                         "sha256": execution.request_sha256, "raw": b"{}"})
        self.assertEqual(result["source_prompt"]["sha256"], execution.prompt_sha256)

    def test_timeout_with_descendant_still_in_job_cannot_collect_stale_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout, stderr, final, status = (root / name for name in ("o", "e", "f", "s"))
            for path in (stdout, stderr, final): path.write_bytes(b"old")
            status.write_text('{"state":"timeout","runner_stop_required":true}', encoding="utf-8")
            execution = CLIExecution("x", "y", ("worker",), stdout, stderr, final, status,
                                     FakeJob(JobInspection(1, (99,), True)), None, b"{}", b"old")
            result = CodexExecAdapter(sys.executable).collect(execution)
            self.assertFalse(result["artifacts_read"])
            self.assertIn("termination_barrier_unconfirmed", result["reasons"])

    def test_start_rejects_preexisting_output_before_creating_a_job(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prompt = root / "prompt"; prompt.write_bytes(b"p"); final = root / "final"; final.write_bytes(b"old")
            request = {"codex_path": sys.executable, "prompt_path": str(prompt), "cwd": str(root), "model": "m", "effort": "low",
                       "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 1,
                       "stdout_path": str(root / "out"), "stderr_path": str(root / "err"), "final_path": str(final), "status_path": str(root / "status")}
            request_path = root / "request.json"; request_path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaises(FileExistsError):
                CodexExecAdapter(sys.executable).start(request_path, cwd=root, env={})


if __name__ == "__main__": unittest.main()
