"""The T3 report survives measured code whose source file is gone.

A test may run code compiled under a path in the measured tree that has no file
(``unit.test_branch_gate`` does) or write a module and remove it. The measured
data then names a file with no source, and coverage's report used to fail the
whole T3 after every test had run. The real measurement runs in a child process,
since two coverage sessions cannot share one.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TESTS = Path(__file__).resolve().parents[1]

CHILD = r'''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from support.branch_gate import SCRIPTS, Measurement, repository_root
directory = Path(sys.argv[2])
measurement = Measurement(repository_root(), data_file=directory / 'coverage.data')
measurement.start()
exec(compile('def gone():\n    return 1\n\n\ngone()\n', str(SCRIPTS / 'tests' / 'support' / 'removed_probe.py'), 'exec'), {})
report = measurement.finish(directory)
print(sorted(name for name in report['files'] if 'removed_probe' in name))
'''


class MissingSourceTests(unittest.TestCase):
    def test_a_measured_file_without_source_is_left_out_of_the_report_instead_of_failing_it(self):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        child = subprocess.run([sys.executable, '-B', '-c', CHILD, str(TESTS), directory],
                               capture_output=True, text=True, timeout=120)
        self.assertEqual((child.returncode, child.stdout.strip()), (0, '[]'), child.stderr[-2000:])


if __name__ == '__main__':
    unittest.main()
