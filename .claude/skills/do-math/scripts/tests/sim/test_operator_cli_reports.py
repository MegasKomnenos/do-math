"""What the CLI prints for operator results and scheduling failures (``cli._emit``, ``cli._schedule_failure``, layer 3).

Both functions are called directly; neither opens a repository. The windowless
case sets the interpreter path the product reads (``sys.executable``), which is
interpreter state, not a product name.
"""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from do_math import cli


INSTANCE = 'RI-00000000000000000000000000'


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


class EmitTests(unittest.TestCase):
    def test_cli_emits_byte_bearing_operator_receipt_as_json(self):
        output = io.StringIO()
        with redirect_stdout(output):
            cli._emit({'raw': b'preserved bytes'}, command='operator check', request_id='QR-receipt')
        self.assertEqual(json.loads(output.getvalue())['result']['raw']['base64'], 'cHJlc2VydmVkIGJ5dGVz')


class ScheduleFailureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_schedule_reconcile_preserves_entrypoint_paths_and_disable_direction(self):
        repository = self.root / "research owner's repository"
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                result, code = cli._schedule_failure(
                    {'config': {'operator_enabled': enabled}}, RuntimeError('failed'), repository, INSTANCE)
                command = result['operator_schedule']['reconcile']
                self.assertTrue(command.startswith('& ' + quote(sys.executable) + ' '))
                self.assertIn(quote(Path(cli.__file__).resolve().parents[1] / 'do_math.py'), command)
                self.assertIn(' operator ' + ('install' if enabled else 'uninstall') + ' ', command)
                self.assertIn('--repository ' + quote(repository.resolve()), command)
                self.assertTrue(command.endswith('--instance ' + quote(INSTANCE)))
                self.assertEqual(code, 5)

    def test_schedule_reconcile_uses_the_console_interpreter_when_run_windowless(self):
        interpreters = self.root / 'Python'
        interpreters.mkdir()
        for name in ('python.exe', 'pythonw.exe'):
            (interpreters / name).write_bytes(b'')
        repository = self.root / 'repository'
        repository.mkdir()
        with patch.object(sys, 'executable', str(interpreters / 'pythonw.exe')):
            result, _ = cli._schedule_failure({'config': {'operator_enabled': True}}, RuntimeError('failed'),
                                              repository, INSTANCE)
        self.assertTrue(result['operator_schedule']['reconcile'].startswith(
            "& '" + str(interpreters / 'python.exe') + "' "))
        (interpreters / 'python.exe').unlink()
        with patch.object(sys, 'executable', str(interpreters / 'pythonw.exe')):
            result, code = cli._schedule_failure({'config': {'operator_enabled': True}}, RuntimeError('failed'),
                                                repository, INSTANCE)
        self.assertEqual(code, 5)
        self.assertEqual(result['operator_schedule']['error'], 'failed')
        self.assertIsNone(result['operator_schedule']['reconcile'])
        self.assertIn(repr(str(interpreters / 'python.exe')), result['operator_schedule']['reconcile_error'])


if __name__ == '__main__':
    unittest.main()
