"""An incremental T3 reuses the stored measurement of unchanged modules and is no closing run (설계 A29).

Each run is the real runner in a child process on two small unit modules with
its own store, so the working tree's store is untouched. About 30 s per run.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[2]
TESTS = ['unit.test_ids', 'unit.test_storage_json_digests']


def t3(store, output, *extra):
    subprocess.run([sys.executable, '-B', 'run_tests.py', '--tier', 'T3', *extra, *TESTS, '--t3-store', str(store),
                    '--output', str(output)], cwd=SCRIPTS, capture_output=True, text=True, timeout=600)
    return json.loads((output / 'report.json').read_text(encoding='utf-8'))


class IncrementalT3Tests(unittest.TestCase):
    def test_a_second_run_reuses_the_unchanged_modules_with_the_same_gate_and_a_full_run_measures_again(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        first = t3(root / 'store', root / 'first')
        second = t3(root / 'store', root / 'second')
        forced = t3(root / 'store', root / 'forced', '--full')
        self.assertEqual((first['t3_store']['mode'], first['t3_store']['measured_modules']), ('full', sorted(TESTS)))
        self.assertEqual((second['t3_store']['mode'], second['t3_store']['measured_modules'],
                          second['t3_store']['reused_modules']), ('incremental', [], sorted(TESTS)))
        self.assertEqual(second['counts'], {})
        self.assertEqual(second['branch_gate'], first['branch_gate'])
        self.assertEqual((first['closing_eligible'], second['closing_eligible']), (False, False))
        self.assertEqual((forced['t3_store']['mode'], forced['t3_store']['measured_modules']), ('full', sorted(TESTS)))
        self.assertEqual(forced['branch_gate'], first['branch_gate'])
        # The runner's own reading of the defect ledger is bookkeeping, not an input read at import (결함 D5):
        # recorded, every ledger change would measure everything again.
        stored = json.loads((root / 'store' / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual([path for path in stored['import_inputs'] if path.endswith('known_defects.json')], [])

    def test_a_parallel_run_with_nothing_to_measure_still_measures_import_time_and_keeps_the_gate(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        first = t3(root / 'store', root / 'first', '--jobs', '2')
        second = t3(root / 'store', root / 'second', '--jobs', '2')
        self.assertEqual((second['t3_store']['reused_modules'], second['counts']), (sorted(TESTS), {}))
        self.assertEqual(second['branch_gate'], first['branch_gate'])


if __name__ == '__main__':
    unittest.main()
