"""An actual worker's native exit code overrides its successful result file.

The specimen registers exit 7 at interpreter shutdown, after the real runner
writes its complete successful JSON report. No runner or Windows Job function
is replaced. The import path is an input to the child interpreter.
"""
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_tests


class NativeExitTests(unittest.TestCase):
    def test_native_worker_failure_cannot_be_hidden_by_a_successful_json_report(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        identifier = 'runner_exit_specimen.Case.test_one'
        (root / 'runner_exit_specimen.py').write_text(
            'import atexit, os, unittest\n'
            'class Case(unittest.TestCase):\n'
            '    def test_one(self):\n'
            '        self.assertTrue(True)\n'
            '        atexit.register(os._exit, 7)\n', encoding='utf-8')
        destination = root / 'worker'
        python_path = os.pathsep.join(filter(None, [str(root), os.environ.get('PYTHONPATH')]))
        with patch.dict(os.environ, {'PYTHONPATH': python_path}):
            report = run_tests._isolated([SimpleNamespace(id=lambda: identifier)], destination, 30)
        original = json.loads((destination / 'result.json').read_text(encoding='utf-8'))
        self.assertTrue(original['complete'])
        self.assertTrue(original['successful'])
        self.assertEqual(original['rows'][0]['id'], identifier)
        self.assertEqual(original['rows'][0]['outcome'], 'passed')
        self.assertFalse(report['successful'])
        self.assertEqual(report['returncode'], 7)


if __name__ == '__main__':
    unittest.main()
