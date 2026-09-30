"""A parallel T3 judges the gate as a one-process T3 does and credits every line it would (설계 5.1, 5.3).

Each run is the real runner in a child process; the parallel one measures in
Windows Job workers and combines their coverage data. The selection index must
stay safe: a line a one-process run credits to a test is credited to that test
in the parallel run too (a worker may credit more, where process caches differ).
About 40 s per run: each measuring worker imports every test module first.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = ['unit.test_ids', 'unit.test_storage_json_digests']


def t3(output, *jobs):
    subprocess.run([sys.executable, '-B', 'run_tests.py', '--tier', 'T3', *jobs, *TESTS, '--output', str(output)],
                   cwd=SCRIPTS, capture_output=True, text=True, timeout=600)
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    files = json.loads((output / 'coverage.json').read_text(encoding='utf-8'))['files']
    credited = {(path, line, context) for path, value in files.items()
                for line, contexts in value.get('contexts', {}).items() for context in contexts
                if context and not context.startswith('fixture:')}
    return report, credited


class ParallelT3Tests(unittest.TestCase):
    def test_parallel_measurement_matches_the_one_process_gate_and_credits(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        serial, serial_credits = t3(root / 'serial')
        parallel, parallel_credits = t3(root / 'parallel', '--jobs', '2')
        self.assertEqual(serial['counts'], parallel['counts'])
        self.assertEqual(serial['branch_gate'], parallel['branch_gate'])
        self.assertGreater(len(serial_credits), 0)
        self.assertEqual(serial_credits - parallel_credits, set())


if __name__ == '__main__':
    unittest.main()
