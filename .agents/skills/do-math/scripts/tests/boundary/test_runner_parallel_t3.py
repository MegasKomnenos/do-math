"""A parallel T3 judges the gate as a one-process T3 does and credits every function it would (설계 5.1, 5.3).

Each run is the real runner in a child process; the parallel one measures in
Windows Job workers and combines their coverage data and entered functions.
The selection index must stay safe: a function a one-process run credits to a
test is credited to that test in the parallel run too (a worker may credit
more, where process caches differ).
About 40 s per run: each measuring worker imports every test module first.
"""
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = ['unit.test_ids', 'unit.test_storage_json_digests']


def t3(output, *jobs):
    # Each run measures in full with its own store (A29): nothing is reused and the tree's store is untouched.
    subprocess.run([sys.executable, '-B', 'run_tests.py', '--tier', 'T3', '--full', *jobs, *TESTS,
                    '--t3-store', str(output.parent / (output.name + '-store')), '--output', str(output)],
                   cwd=SCRIPTS, capture_output=True, text=True, timeout=600)
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    entered = json.loads((output / 'entered.json').read_text(encoding='utf-8'))
    credited = {(path, key, label) for label, keys in entered.items() for path, key in keys
                if label and not label.startswith('fixture:')}
    return report, credited


def body_lines(module, function):
    """The body lines of a top-level ``function`` of ``module`` (a path under ``scripts/``)."""
    tree = ast.parse((SCRIPTS / module).read_text(encoding='utf-8'))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function)
    return set(range(node.body[0].lineno, node.end_lineno + 1))


def executed(output, module):
    files = json.loads((output / 'coverage.json').read_text(encoding='utf-8'))['files']
    return set(next(value['executed_lines'] for path, value in files.items() if path.endswith(module)))


class ParallelT3Tests(unittest.TestCase):
    def test_parallel_measurement_matches_the_one_process_gate_and_credits(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        serial, serial_credits = t3(root / 'serial')
        parallel, parallel_credits = t3(root / 'parallel', '--jobs', '2')
        self.assertEqual(serial['counts'], parallel['counts'])
        self.assertEqual(serial['branch_gate'], parallel['branch_gate'])
        self.assertGreater(len(serial_credits), 0)
        self.assertEqual(serial_credits - parallel_credits, set())
        # The runner's own result files go through do_math.file_io; the selected tests never call it, so no
        # line of those functions is a test's reach (결함 D5: the gate would pass a path no test ran).
        runner_io = body_lines('do_math/file_io.py', 'write_bytes_atomic') | body_lines('do_math/file_io.py', 'read_bytes_shared')
        for output in (root / 'serial', root / 'parallel'):
            with self.subTest(output=output.name):
                self.assertEqual(executed(output, 'do_math/file_io.py') & runner_io, set())


if __name__ == '__main__':
    unittest.main()
