from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math.scholarly import resolve_scholarly_server, validate_scholarly_server


class ScholarlyServerTests(unittest.TestCase):
    def test_explicit_server_is_closed_when_paths_are_already_absolute(self):
        value = {"command": "C:/tools/python.exe", "args": ["C:/service/server.py", "--credential-root", "credentials"]}
        resolved = resolve_scholarly_server(value, start=Path.cwd())
        self.assertEqual(resolved, value)
        self.assertIsNot(resolved, value)

    def test_rejects_non_scholarly_fields_and_data_directory_override(self):
        for value in (
            {"command": "python", "args": [], "env": {}},
            {"command": "tools/python.exe", "args": ["C:/server.py"]},
            {"command": "python", "args": ["server.py"]},
            {"command": "python", "args": ["server.py", "--data-dir", "outside"]},
            {"command": "python", "args": ["server.py", "--data-dir=outside"]},
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_scholarly_server(value)

    def test_project_config_beats_code_home_and_extracts_only_scholarly(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as home:
            root = Path(directory)
            (root / ".codex").mkdir()
            (root / ".codex" / "python.exe").write_bytes(b"")
            (root / ".codex" / "server.py").write_text("# fixture", encoding="utf-8")
            (root / ".codex" / "config.toml").write_text(
                '[mcp_servers.other]\ncommand = "ignored"\nargs = ["secret"]\n\n'
                '[mcp_servers.scholarly]\ncommand = "python.exe"\nargs = ["server.py"]\nstartup_timeout_sec = 30\ntool_timeout_sec = 1800\n', encoding="utf-8")
            (Path(home) / "config.toml").write_text(
                '[mcp_servers.scholarly]\ncommand = "home-python"\nargs = ["home-server.py"]\n', encoding="utf-8")
            old = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = home
            try:
                self.assertEqual(resolve_scholarly_server(None, start=root), {
                    "command": str((root / ".codex" / "python.exe").resolve()),
                    "args": [str((root / ".codex" / "server.py").resolve())],
                })
            finally:
                if old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old

    def test_code_home_is_used_when_project_has_no_scholarly_entry(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as home:
            root = Path(directory)
            home_config = Path(home) / "config.toml"
            home_config.write_text(
                '[mcp_servers.scholarly]\ncommand = "python"\nargs = ["C:/home-server.py"]\n', encoding="utf-8")
            old = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = home
            try:
                self.assertEqual(resolve_scholarly_server(None, start=root),
                                 {"command": "python", "args": ["C:/home-server.py"]})
            finally:
                if old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = old

    def test_default_home_config_is_used_when_code_home_is_unset(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as home:
            root = Path(directory)
            config_dir = Path(home) / ".codex"
            config_dir.mkdir()
            (config_dir / "config.toml").write_text(
                '[mcp_servers.scholarly]\ncommand = "python"\nargs = ["C:/home-server.py"]\n', encoding="utf-8")
            old = os.environ.pop("CODEX_HOME", None)
            try:
                with patch("do_math.scholarly.Path.home", return_value=Path(home)):
                    self.assertEqual(resolve_scholarly_server(None, start=root),
                                     {"command": "python", "args": ["C:/home-server.py"]})
            finally:
                if old is not None:
                    os.environ["CODEX_HOME"] = old


if __name__ == "__main__":
    unittest.main()
