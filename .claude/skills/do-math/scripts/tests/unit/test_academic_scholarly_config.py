"""The scholarly-MCP server pair for isolated Codex executions: its closed shape (``scholarly``, layer 1)
and its resolution from the nearest Codex configuration file (``scholarly_config``, layer 2); moved from ``test_scholarly``.

The configuration files are real files in temporary folders. The entry point
passes the selected Codex home as a value; resolution performs no environment reads.
"""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.scholarly import validate_scholarly_server
from do_math.scholarly_config import resolve_scholarly_server

HOME_ENTRY = '[mcp_servers.scholarly]\ncommand = "python"\nargs = ["C:/home-server.py"]\n'


class ScholarlyServerShapeTests(unittest.TestCase):
    def test_explicit_server_is_closed_when_paths_are_already_absolute(self):
        from support.entry import entry
        _entry = entry()
        value = {"command": "C:/tools/python.exe", "args": ["C:/service/server.py", "--credential-root", "credentials"]}
        resolved = resolve_scholarly_server(value, start=Path.cwd(), codex_home=_entry.codex_home)
        # Only the first argument is a server file; the later relative literal stays as given.
        self.assertEqual(resolved, value)
        self.assertIsNot(resolved, value)

    def test_rejects_non_scholarly_fields_and_data_directory_override(self):
        """Each shape is refused by its own rule: extra keys, a relative command or server file without a
        configuration-file base, and a data-directory override in either argument form."""
        cases = (
            ({"command": "python", "args": [], "env": {}}, "^scholarly server must contain exactly command and args$"),
            ({"command": "tools/python.exe", "args": ["C:/server.py"]},
             "^relative scholarly command needs a configuration-file base$"),
            ({"command": "python", "args": ["server.py"]},
             "^relative scholarly server file needs a configuration-file base$"),
            ({"command": "python", "args": ["server.py", "--data-dir", "outside"]},
             "^scholarly args must not override the execution data directory$"),
            ({"command": "python", "args": ["server.py", "--data-dir=outside"]},
             "^scholarly args must not override the execution data directory$"),
        )
        for value, reason in cases:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, reason):
                validate_scholarly_server(value)


class ScholarlyConfigurationTests(unittest.TestCase):
    def folders(self):
        """A project root and a home folder, both removed after the test."""
        root, home = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.addCleanup(home.cleanup)
        return Path(root.name), Path(home.name)

    def no_project_start(self, temporary_root):
        # Runner scratch may be under a real project with its own .codex file.
        # The filesystem root has no ancestors; verify the absence this case needs.
        start = Path(temporary_root.anchor)
        self.assertFalse((start / '.codex/config.toml').exists(),
                         'home fallback requires a start without a project configuration')
        return start

    def test_project_config_beats_code_home_and_extracts_only_scholarly(self):
        from support.entry import entry
        _entry = entry()
        root, home = self.folders()
        (root / ".codex").mkdir()
        (root / ".codex" / "python.exe").write_bytes(b"")
        (root / ".codex" / "server.py").write_text("# fixture", encoding="utf-8")
        (root / ".codex" / "config.toml").write_text(
            '[mcp_servers.other]\ncommand = "ignored"\nargs = ["secret"]\n\n'
            '[mcp_servers.scholarly]\ncommand = "python.exe"\nargs = ["server.py"]\nstartup_timeout_sec = 30\n'
            'tool_timeout_sec = 1800\n', encoding="utf-8")
        (home / "config.toml").write_text(
            '[mcp_servers.scholarly]\ncommand = "home-python"\nargs = ["home-server.py"]\n', encoding="utf-8")
        # Exactly the pair: the other server and the client time limits are not inherited;
        # the relative command and server file become the files beside the configuration.
        nested = root / 'nested/project'
        nested.mkdir(parents=True)
        for start in (root, nested):
            with self.subTest(start=start):
                resolved = resolve_scholarly_server(None, start=start, codex_home=home)
                self.assertEqual(resolved, {"command": str((root / ".codex" / "python.exe").resolve()),
                                            "args": [str((root / ".codex" / "server.py").resolve())]})

    def test_code_home_is_used_when_project_has_no_scholarly_entry(self):
        from support.entry import entry
        _entry = entry()
        root, home = self.folders()
        (home / "config.toml").write_text(HOME_ENTRY, encoding="utf-8")
        start = self.no_project_start(root)
        resolved = resolve_scholarly_server(None, start=start, codex_home=home)
        # "python" has no separator or suffix, so it is not a path and stays literal.
        self.assertEqual(resolved, {"command": "python", "args": ["C:/home-server.py"]})
        # The entry point's CODEX_HOME, passed as an argument, is read the same way.
        self.assertEqual(resolve_scholarly_server(None, start=start, codex_home=home),
                         {"command": "python", "args": ["C:/home-server.py"]})

    def test_default_home_config_is_used_when_code_home_is_unset(self):
        from support.entry import entry
        _entry = entry()
        root, home = self.folders()
        (home / ".codex").mkdir()
        (home / ".codex" / "config.toml").write_text(HOME_ENTRY, encoding="utf-8")
        resolved = resolve_scholarly_server(None, start=self.no_project_start(root), codex_home=home / ".codex")
        self.assertEqual(resolved, {"command": "python", "args": ["C:/home-server.py"]})


if __name__ == "__main__":
    unittest.main()
