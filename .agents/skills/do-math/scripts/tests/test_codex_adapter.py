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
from do_math import codex_worker
from do_math.codex_adapter import CodexExecAdapter, CodexExecution, _parse_jsonl
from do_math.windows_job import JobInspection


class _FakeJob:
    def __init__(self, state): self.state = state
    def inspect(self): return self.state


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

    def test_worker_does_not_accept_fake_argument_prefixes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prompt = root / "prompt"; prompt.write_bytes(b"hello")
            request = {"codex_path": sys.executable, "prompt_path": str(prompt), "cwd": str(root), "model": "gpt-x",
                       "effort": "low", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 5,
                       "stdout_path": str(root / "out"), "stderr_path": str(root / "err"), "final_path": str(root / "final"), "status_path": str(root / "status")}
            request_path = root / "request.json"
            request_path.write_text(json.dumps({**request, "codex_argv": [sys.executable, str(root / "fake.py")]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "codex_argv is forbidden"):
                codex_worker.run(request_path)
            request_path.write_text(json.dumps(request), encoding="utf-8")
            captured = {}
            class Process:
                returncode = 0
                def __init__(self, command, **options): captured.update(command=command, env=options["env"], shell=options["shell"])
                def communicate(self, input=None, timeout=None): captured["stdin"] = input; return b"", b""
            old = os.environ.get("OPENAI_API_KEY"); os.environ["OPENAI_API_KEY"] = "must-not-pass"
            try:
                with patch.object(codex_worker.subprocess, "Popen", Process):
                    self.assertEqual(codex_worker.run(request_path), 0)
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
            with self.assertRaisesRegex(ValueError, "max_runtime"):
                codex_worker.load_request(path)
            request["max_runtime_seconds"] = 1; request["windows_sandbox"] = "none"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "windows_sandbox"):
                codex_worker.load_request(path)

    def test_closed_filesystem_profile_replaces_legacy_sandbox(self):
        request = {"codex_path": "C:/Codex/codex.exe", "prompt_path": "p", "cwd": "C:/work", "model": "gpt-x",
                   "effort": "low", "approval_policy": "never", "windows_sandbox": "elevated",
                   "max_runtime_seconds": 1, "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s",
                   "filesystem": {"read_roots": ["C:/input"], "write_roots": ["C:/work/out"], "deny_roots": ["C:/private"]}}
        argv = codex_worker.build_argv(request)
        self.assertNotIn("--sandbox", argv)
        self.assertIn('default_permissions="do_math"', argv)
        self.assertIn("permissions.do_math.network.enabled=false", argv)
        self.assertIn('windows.sandbox="elevated"', argv)

    def test_filesystem_write_root_outside_workspace_is_rejected_before_spawn(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); workspace = root / "workspace"; workspace.mkdir(); prompt = root / "prompt"; prompt.write_bytes(b"p")
            request = {"codex_path": sys.executable, "prompt_path": str(prompt), "cwd": str(workspace), "model": "m", "effort": "low",
                       "approval_policy": "never", "windows_sandbox": "elevated", "max_runtime_seconds": 1,
                       "stdout_path": str(root / "out"), "stderr_path": str(root / "err"), "final_path": str(root / "final"), "status_path": str(root / "status"),
                       "filesystem": {"read_roots": [], "write_roots": [str(root)], "deny_roots": []}}
            path = root / "request.json"; path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inside the model workspace"):
                CodexExecAdapter(sys.executable).start(path, cwd=root, env={})

    def test_filesystem_request_rejects_mixed_mode_and_unknown_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = {"codex_path": sys.executable, "prompt_path": str(root / "prompt"), "cwd": str(root / "work"),
                       "model": "m", "effort": "low", "approval_policy": "never", "windows_sandbox": "elevated",
                       "max_runtime_seconds": 1, "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s",
                       "filesystem": {"read_roots": [str(root / "input")], "write_roots": [str(root / "work")], "deny_roots": []}}
            path = root / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            self.assertEqual(codex_worker.load_request(path)["filesystem"], request["filesystem"])
            request["sandbox"] = "read-only"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mutually exclusive"):
                codex_worker.load_request(path)
            del request["sandbox"]
            request["file_system"] = {}
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown worker request fields"):
                codex_worker.load_request(path)

    def test_jsonl_tail_and_missing_terminal_are_not_success(self):
        parsed = _parse_jsonl(b'{"type":"thread.started","thread_id":"t"}\nnot-json')
        self.assertEqual(parsed["thread_id"], "t")
        self.assertFalse(parsed["turn_completed"])
        self.assertGreater(parsed["unparsed_tail_bytes"], 0)

    def test_collect_rejects_malformed_tail_even_with_turn_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, prompt, stdout, stderr, final, status = (root / name for name in ("r", "p", "o", "e", "f", "s"))
            request.write_bytes(b"{}"); prompt.write_bytes(b"p")
            stdout.write_bytes(b'{"type":"turn.completed"}\nbroken')
            stderr.write_bytes(b""); final.write_bytes(b"final")
            status.write_text('{"state":"exited","cli_exit_code":0}', encoding="utf-8")
            execution = CodexExecution(request, prompt, __import__("hashlib").sha256(b"{}").hexdigest(),
                                       __import__("hashlib").sha256(b"p").hexdigest(), ("worker",), stdout, stderr, final, status,
                                       _FakeJob(JobInspection(0, (), True)), root, None)
            result = CodexExecAdapter(sys.executable).collect(execution)
            self.assertEqual(result["result"], "incomplete")
            self.assertIn("jsonl_parse_incomplete", result["reasons"])

    def test_timeout_with_descendant_still_in_job_cannot_collect_stale_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request, prompt, stdout, stderr, final, status = (root / name for name in ("r", "p", "o", "e", "f", "s"))
            for path in (request, prompt, stdout, stderr, final): path.write_bytes(b"old")
            status.write_text('{"state":"timeout","runner_stop_required":true}', encoding="utf-8")
            execution = CodexExecution(request, prompt, "x", "y", ("worker",), stdout, stderr, final, status,
                                       _FakeJob(JobInspection(1, (99,), True)), root, None)
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
