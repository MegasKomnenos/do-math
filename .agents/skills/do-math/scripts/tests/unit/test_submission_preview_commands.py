"""Installed worker commands select the console sibling of a windowless interpreter."""
from pathlib import Path
import sys
import tempfile
import unittest

from do_math.submission import install_tools
from do_math.contracts import schema_for


class LeanPreviewTests(unittest.TestCase):
    def test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless(self):
        """Cold run: 0.28 s; real archive installation checks both commands from a pythonw engine."""
        from support.entry import entry
        _entry = entry()
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            interpreters = root / 'Python'
            interpreters.mkdir()
            for name in ('python.exe', 'pythonw.exe'):
                (interpreters / name).write_bytes(b'')
            workspace = root / 'workspace'
            workspace.mkdir()
            context = {"action": {"role": "research_work"}, "snapshot": "fixed",
                "formal_verifier": {"command": ["definitely-missing-lean"], "allowed_axioms": []}}
            with patch.object(sys, 'executable', str(interpreters / 'pythonw.exe')):
                contract = install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            self.assertEqual(contract['command'][0], str(interpreters / 'python.exe'))
            self.assertEqual(context['formal_verifier']['preview']['command'][0], str(interpreters / 'python.exe'))
