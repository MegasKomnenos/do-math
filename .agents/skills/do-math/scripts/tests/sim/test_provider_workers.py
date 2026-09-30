"""The provider workers (``codex_worker``, ``claude_worker``, layer 3): request checks, CLI commands and environment.

A worker is the direct root of its Job: it loads and checks its request,
builds its CLI's command without a shell, keeps only the login state of the
environment, and starts the CLI at its ``spawn`` seam, where these tests put
the scripted CLI (``support.provider_runs``).
"""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft7Validator

from do_math import claude_worker, codex_worker
from do_math.cli import CliInputError, build_parser
from do_math.contracts import ROLES, schema_for
from support.provider_runs import ScriptedCLI


class CodexWorkerTests(unittest.TestCase):
    def test_build_argv_is_direct_cli_with_isolating_probe_flags(self):
        request = {"codex_path": "C:/Codex/codex.exe", "prompt_path": "p", "cwd": "C:/work", "model": "gpt-x",
                   "effort": "high", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 1,
                   "stdout_path": "o", "stderr_path": "e", "final_path": "f", "status_path": "s",
                   "windows_sandbox": "unelevated"}
        argv = codex_worker.build_argv(request)
        self.assertEqual(argv[:4], ["C:/Codex/codex.exe", "--ask-for-approval", "never", "exec"])
        for flag in ("--json", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
                     "project_doc_max_bytes=0", 'windows.sandbox="unelevated"'):
            self.assertIn(flag, argv)
        self.assertEqual(argv[-1], "-")
        self.assertNotIn("shell", " ".join(argv).lower())

    def test_worker_does_not_accept_fake_argument_prefixes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prompt = root / "prompt"
            prompt.write_bytes(b"hello")
            request = {"codex_path": sys.executable, "prompt_path": str(prompt), "cwd": str(root), "model": "gpt-x",
                       "effort": "low", "sandbox": "read-only", "approval_policy": "never", "max_runtime_seconds": 5,
                       "stdout_path": str(root / "out"), "stderr_path": str(root / "err"),
                       "final_path": str(root / "final"), "status_path": str(root / "status")}
            request_path = root / "request.json"
            request_path.write_text(json.dumps({**request, "codex_argv": [sys.executable, str(root / "fake.py")]}),
                                    encoding="utf-8")
            cli = ScriptedCLI()
            with self.assertRaisesRegex(ValueError, "unknown worker request fields: codex_argv"):
                codex_worker.run(request_path, spawn=cli.spawn)
            self.assertEqual(cli.calls, [])
            request_path.write_text(json.dumps(request), encoding="utf-8")
            with patch.dict(os.environ, {"OPENAI_API_KEY": "must-not-pass"}):
                self.assertEqual(codex_worker.run(request_path, spawn=cli.spawn), 0)
            call, = cli.calls
            self.assertEqual(call["command"], codex_worker.build_argv(request))
            self.assertNotIn("OPENAI_API_KEY", call["env"])
            self.assertFalse(call["shell"])
            self.assertEqual(call["stdin"], b"hello")
            self.assertEqual(json.loads((root / "status").read_text(encoding="utf-8"))["cli_exit_code"], 0)

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
            with self.assertRaisesRegex(ValueError, "max_runtime_seconds must be positive and finite or null"):
                codex_worker.load_request(path)
            request["max_runtime_seconds"] = 1
            request["windows_sandbox"] = "none"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "windows_sandbox must be elevated or unelevated"):
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

    def test_unknown_worker_request_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = {"codex_path": sys.executable, "prompt_path": str(root / "prompt"), "cwd": str(root / "work"),
                       "model": "m", "effort": "low", "sandbox": "read-only", "approval_policy": "never",
                       "max_runtime_seconds": 1, "stdout_path": "o", "stderr_path": "e", "final_path": "f",
                       "status_path": "s", "file_system": {}}
            path = root / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown worker request fields: file_system"):
                codex_worker.load_request(path)

    def test_workers_validate_execution_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = {"codex_path": "codex", "prompt_path": "input.txt", "cwd": str(root),
                       "model": "model", "effort": "medium", "approval_policy": "never", "sandbox": "danger-full-access",
                       "max_runtime_seconds": 60, "stdout_path": "out", "stderr_path": "err", "final_path": "final",
                       "status_path": "status", "execution_id": "EX-bound",
                       "profile_ref": {"id": "EP-x", "revision": 1, "sha256": "a" * 64}}
            path = root / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            try:
                loaded = codex_worker.load_request(path)
            except ValueError as error:
                self.fail("worker rejects execution/profile binding: " + str(error))
            self.assertEqual(loaded["execution_id"], "EX-bound")
            for invalid in ({"execution_id": None}, {"profile_ref": {**request["profile_ref"], "id": "   "}}):
                with self.subTest(invalid=invalid):
                    bound = {key: value for key, value in {**request, **invalid}.items() if value is not None}
                    path.write_text(json.dumps(bound), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError,
                                                "worker execution binding requires exact execution_id and profile_ref"):
                        codex_worker.load_request(path)


class ClaudeWorkerTests(unittest.TestCase):
    def test_role_schemas_reach_claude_without_unsupported_meta_schema(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "schema.json"
            for role in ROLES:
                with self.subTest(role=role):
                    original = schema_for(role)
                    raw = json.dumps(original)
                    path.write_text(raw, encoding="utf-8")
                    args = claude_worker.build_argv({"claude_path": "claude.exe", "model": "claude-opus-5",
                                                     "effort": "high", "cwd": d, "output_schema_path": str(path)})
                    sent = json.loads(args[args.index("--json-schema") + 1])
                    self.assertEqual(sent, {k: v for k, v in original.items() if k not in {"$schema", "x-contract-id"}})
                    Draft7Validator.check_schema(sent)
                    self.assertFalse(Draft7Validator(sent).is_valid({}))
                    self.assertEqual(path.read_text(encoding="utf-8"), raw)

    def test_worker_uses_login_stdin_schema_and_only_configured_mcp(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            request = {"claude_path": "claude.exe", "model": "haiku", "effort": "low",
                       "cwd": str(root), "output_schema_path": str(schema),
                       "scholarly_server": {"command": "python", "args": [str(root / "server.py")]}}
            args = claude_worker.build_argv(request)
            self.assertEqual(args[:2], ["claude.exe", "--print"])
            self.assertIn("stream-json", args)
            self.assertNotIn("--bare", args)
            self.assertIn("--no-session-persistence", args)
            self.assertIn("--strict-mcp-config", args)
            mcp = json.loads(args[args.index("--mcp-config") + 1])
            self.assertEqual(set(mcp["mcpServers"]), {"scholarly"})
            self.assertEqual(mcp["mcpServers"]["scholarly"]["args"][-2:], ["--data-dir", str(root / "scholarly-data")])
            # Running the request: the prompt goes to the CLI's standard input, the command has no shell.
            prompt = root / "prompt.txt"
            prompt.write_bytes("the role prompt\n".encode("utf-8"))
            request_path = root / "request.json"
            request_path.write_text(json.dumps({**request, "prompt_path": str(prompt), "max_runtime_seconds": None,
                **{key: str(root / "outputs" / key) for key in ("stdout_path", "stderr_path", "status_path")}}),
                encoding="utf-8")
            cli = ScriptedCLI()
            self.assertEqual(claude_worker.run(request_path, spawn=cli.spawn), 0)
            call, = cli.calls
            self.assertEqual(call["stdin"], b"the role prompt\n")
            self.assertEqual(call["command"], claude_worker.build_argv(claude_worker.load_request(request_path)))
            self.assertFalse(call["shell"])
        env = claude_worker.sanitized_environment({"PATH": "ok", "USERPROFILE": "login", "CLAUDE_CONFIG_DIR": "config",
              "ANTHROPIC_API_KEY": "secret", "ANTHROPIC_AUTH_TOKEN": "secret", "CLAUDECODE": "1",
              "ANTHROPIC_BASE_URL": "https://elsewhere", "CLAUDE_CODE_USE_BEDROCK": "1"})
        self.assertEqual(env, {"PATH": "ok", "USERPROFILE": "login", "CLAUDE_CONFIG_DIR": "config"})


class ProviderChoiceTests(unittest.TestCase):
    def test_profile_accepts_claude_provider(self):
        try:
            args = build_parser().parse_args(["profile", "--provider", "claude"])
        except CliInputError as error:
            self.fail(str(error))
        self.assertEqual(args.provider, "claude")


if __name__ == "__main__":
    unittest.main()
