"""Installed worker commands select the console sibling of a windowless interpreter."""
from pathlib import Path
from copy import deepcopy
import sys
import tempfile
import unittest

from do_math.submission import install_tools
from do_math.contracts import schema_for
from do_math.context_store import record_map


class LeanPreviewTests(unittest.TestCase):
    def test_worker_tools_reject_a_windowless_interpreter_without_its_console_sibling(self):
        from support.entry import entry
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            windowless = root / 'pythonw.exe'
            windowless.write_bytes(b'')
            workspace = root / 'workspace'
            workspace.mkdir()
            context = {'action': {'role': 'research_work'}, 'snapshot': 'fixed',
                'formal_verifier': {'command': ['definitely-missing-lean'], 'allowed_axioms': []}}
            context['record_map'] = record_map({}, context['action']['role'], context['snapshot'])
            original = deepcopy(context)
            with patch.object(sys, 'executable', str(windowless)):
                with self.assertRaises(FileNotFoundError) as failure:
                    install_tools(workspace, context, schema_for('research_work'), 1000000, clock=entry().ports.clock)
            self.assertEqual(failure.exception.filename, str(root / 'python.exe'))
            self.assertEqual(context, original)
            self.assertEqual(list(workspace.iterdir()), [])

    def test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless(self):
        """Cold run: 0.28 s; real archive installation checks all three commands from a pythonw engine."""
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
            # The read command is issued only when the input includes a record map.
            context['record_map'] = record_map({}, context['action']['role'], context['snapshot'])
            with patch.object(sys, 'executable', str(interpreters / 'pythonw.exe')):
                contract = install_tools(workspace, context, schema_for('research_work'), 1000000, clock=_entry.ports.clock)
            self.assertEqual(contract['command'][0], str(interpreters / 'python.exe'))
            self.assertEqual(context['formal_verifier']['preview']['command'][0], str(interpreters / 'python.exe'))
            self.assertEqual(context['record_map']['read_tool']['command'][0], str(interpreters / 'python.exe'))
