"""T4 observes actual adapter execution and reports gaps without a reach gate.

Native runner specimens exceed the unit budget because measuring/merging in a
separate process and an owned worker is the behavior under test.
"""
import ast
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

import run_tests
from test_categories import test_group

SCRIPTS = Path(__file__).resolve().parents[2]


def body_lines(module, name):
    tree = ast.parse((SCRIPTS / module).read_text(encoding='utf-8'))
    nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    return {line for node in nodes for line in range(node.body[0].lineno, node.end_lineno + 1)}


@test_group('resource')
class NativeAdapterTests(unittest.TestCase):
    def test_t4_observes_in_process_and_owned_worker_without_writing_t3_outputs(self):
        # Owned runner scratch retains the child publication for diagnostic evidence.
        root = Path(tempfile.mkdtemp(prefix='adapter-native-'))
        if root:
            command = [sys.executable, '-u', '-B', str(SCRIPTS / 'run_tests.py'),
                       '--tier', 'T4', '--jobs', '1', 'boundary.test_port_clock',
                       'boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once',
                       '--output', str(root / 'run')]
            child = subprocess.run(command, capture_output=True, text=True)
            (root / 'child.stdout').write_text(child.stdout, encoding='utf-8')
            (root / 'child.stderr').write_text(child.stderr, encoding='utf-8')
            report = json.loads((root / 'run/report.json').read_text(encoding='utf-8'))
            self.assertEqual(child.returncode, 0, child.stdout[-3000:] + child.stderr[-3000:]
                             + repr([row for part in report['reports'] for row in part['rows']
                                     if row['outcome'] not in ('passed', 'skipped')]))
            adapter = report['t4_adapter']
            self.assertTrue(adapter['complete'], adapter)
            self.assertEqual(report['counts'], {'passed': 11})
            from do_math.layers import LAYERS
            self.assertEqual(set(adapter['modules']), {p for p, layer in LAYERS.items() if layer == 'adapter'})
            clock = adapter['modules']['do_math/system_clock.py']
            self.assertTrue(set(clock['executed_lines']) & body_lines('do_math/system_clock.py', 'wall'))
            job = adapter['modules']['do_math/windows_job.py']
            self.assertTrue(set(job['executed_lines']) & body_lines('do_math/windows_job.py', 'resume'))
            self.assertFalse(set(adapter['modules']['do_math/http_transport.py']['executed_lines'])
                             & body_lines('do_math/http_transport.py', '_http'))
            self.assertTrue(adapter['modules']['do_math/http_transport.py']['missing_branches'])
            self.assertEqual(len(adapter['workers']), 1)
            self.assertEqual(adapter['workers'][0]['status'], 'merged')
            self.assertNotIn('branch_gate', report)
            self.assertNotIn('selection_index', report)
            self.assertFalse((root / 'run/entered.json').exists())

    def test_parallel_t4_keeps_runner_job_bookkeeping_out_of_adapter_reach(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            child = subprocess.run([sys.executable, '-u', '-B', str(SCRIPTS / 'run_tests.py'),
                '--tier', 'T4', '--jobs', '2', 'boundary.test_port_clock', 'boundary.test_port_calls',
                '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr[-3000:])
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            adapter = report['t4_adapter']
            self.assertTrue(adapter['complete'], adapter['problems'])
            self.assertEqual(len(adapter['workers']), 2)
            self.assertEqual(set(report['group_seconds']), {'boundary'})
            self.assertEqual(report['total_seconds'], report['group_seconds']['boundary'])
            lines = set(adapter['modules']['do_math/windows_job.py']['executed_lines'])
            self.assertFalse(lines & body_lines('do_math/windows_job.py', 'resume'))
            self.assertFalse(lines & body_lines('do_math/windows_job.py', 'inspect'))

    def test_t3_t4_union_keeps_t3_gate_entries_and_store_separate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            observations = []
            for mode in ('t3', 'union'):
                output = root / mode
                command = [sys.executable, '-u', '-B', str(SCRIPTS / 'run_tests.py'), '--tier', 'T3',
                    '--full', '--jobs', '1', 'unit.test_ids', '--t3-store', str(root / (mode + '-store')),
                    '--output', str(output)]
                if mode == 'union':
                    command.insert(command.index('unit.test_ids') + 1, 'boundary.test_port_clock')
                    command += ['--tier', 'T4']
                child = subprocess.run(command, capture_output=True, text=True)
                self.assertTrue((output / 'report.json').exists(), child.stdout + child.stderr)
                report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
                self.assertEqual(child.returncode, 1)  # deliberately partial T3: product gate has gaps
                self.assertTrue(report['successful'], child.stderr[-2000:])
                self.assertIsNone(report['selection_index'])
                entered = json.loads((output / 'entered.json').read_text(encoding='utf-8'))
                self.assertFalse(any(label.startswith(('boundary.', 'fixture:boundary.')) for label in entered))
                store = json.loads((root / (mode + '-store') / 'records.json').read_text(encoding='utf-8'))
                self.assertEqual(set(store['modules']), {'unit.test_ids'})
                self.assertFalse(any(p.endswith('/' + mode + '-store/records.json')
                                     for p in store['import_inputs']))
                observations.append((report['branch_gate'], entered))
                if mode == 'union':
                    self.assertTrue(report['t4_adapter']['complete'])
                    self.assertEqual(report['t4_adapter']['workers'][0]['status'], 'merged')
            self.assertEqual(observations[0], observations[1])

    def test_missing_worker_data_refuses_runner_success_even_when_all_tests_pass(self):
        program = '''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import run_tests
isolated = run_tests._isolated
def lose_data(*args, **kwargs):
    report = isolated(*args, **kwargs)
    if isinstance(kwargs.get('measure'), dict):
        (Path(report['directory']) / 'coverage.data').unlink()
    return report
run_tests._isolated = lose_data  # external file-loss injection after real worker termination
raise SystemExit(run_tests.main(['--tier', 'T4', '--jobs', '2', 'boundary.test_port_clock',
                                '--output', sys.argv[2]]))
'''
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            child = subprocess.run([sys.executable, '-u', '-B', '-c', program, str(SCRIPTS), str(output)],
                                   capture_output=True, text=True)
            self.assertEqual(child.returncode, 1, child.stderr[-2000:])
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertTrue(report['successful'])
            self.assertEqual(report['counts'], {'passed': 10})
            self.assertFalse(report['t4_adapter']['complete'])
            self.assertEqual(report['t4_adapter']['workers'][0]['status'], 'invalid')
            self.assertIn('FileNotFoundError', report['t4_adapter']['problems'][0]['reason'])

    def test_measurement_preserves_failed_skipped_and_unrun_test_outcomes(self):
        program = '''
import json, sys, types, unittest
from pathlib import Path
sys.path[:0] = [sys.argv[1], str(Path(sys.argv[1]) / 'tests')]
import run_tests
from support.adapter_coverage import AdapterMeasurement, source_edition
from support.branch_gate import repository_root
from do_math.system_clock import SystemClock
module = types.ModuleType('boundary.adapter_outcome_specimen')
sys.modules[module.__name__] = module
class Cases(unittest.TestCase):
    def test_fail(self):
        SystemClock().wall()
        self.fail('measured ordinary failure')
    def test_skip(self): self.skipTest('measured skip')
class BrokenFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls): raise RuntimeError('measured fixture error')
    def test_unrun(self): self.fail('must not execute')
Cases.__module__ = BrokenFixture.__module__ = module.__name__
tests = [Cases('test_fail'), Cases('test_skip'), BrokenFixture('test_unrun')]
directory = Path(sys.argv[2]); directory.mkdir()
request = {'kind':'t4', 'run_id':'outcomes', 'source_sha256':source_edition()}
observer = AdapterMeasurement(repository_root(), data_file=directory/'adapter.data', request=request)
observer.start(); observer.begin([test.id() for test in tests])
report = run_tests._run_suite(tests, directory/'suite', measurement=observer)
adapter = observer.finish_report(directory, reports=[], changed=[])
(directory/'outcomes.json').write_text(json.dumps({'tests':report,'adapter':adapter}), encoding='utf-8')
'''
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'run'
            child = subprocess.run([sys.executable, '-u', '-B', '-c', program, str(SCRIPTS), str(output)],
                                   capture_output=True, text=True)
            self.assertEqual(child.returncode, 0, child.stderr[-3000:])
            report = json.loads((output / 'outcomes.json').read_text(encoding='utf-8'))
            self.assertTrue(report['adapter']['complete'])
            self.assertFalse(report['tests']['successful'])
            self.assertEqual([row['outcome'] for row in report['tests']['rows'] if not row.get('fixture')],
                             ['failed', 'skipped', 'not_run'])
            self.assertEqual([row['outcome'] for row in report['tests']['rows'] if row.get('fixture')], ['error'])


@test_group('resource')
class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from support.adapter_coverage import source_edition
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.request = {'kind': 't4', 'run_id': 'native-publication-specimen', 'source_sha256': source_edition()}
        tests = list(run_tests.flatten(unittest.TestLoader().loadTestsFromName(
            'boundary.test_port_clock.SystemClockContract.test_wall_is_an_aware_utc_datetime')))
        cls.worker = run_tests._isolated(tests, cls.root / 'original', measure=cls.request)
        if not cls.worker['successful']:
            raise AssertionError(cls.worker)

    def measure(self, directory, report):
        from support.adapter_coverage import AdapterMeasurement
        from support.branch_gate import repository_root
        measurement = AdapterMeasurement(repository_root(), data_file=directory / 'merged.data', request=self.request)
        return measurement.finish_report(directory, reports=[report], changed=[])

    def test_missing_corrupt_foreign_and_changed_source_publications_are_incomplete(self):
        from support.adapter_coverage import MANIFEST
        from support.branch_gate import DATA
        for kind in ('missing', 'corrupt', 'foreign', 'edition', 'request', 'sqlite'):
            with self.subTest(kind=kind):
                root = self.root / kind
                worker = root / 'worker'
                shutil.copytree(self.root / 'original', worker)
                manifest_path = worker / MANIFEST
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                if kind == 'missing':
                    (worker / DATA).unlink()
                elif kind == 'corrupt':
                    manifest_path.write_text('{broken', encoding='utf-8')
                elif kind == 'foreign':
                    manifest['request']['run_id'] = 'another-run'
                elif kind == 'edition':
                    manifest['source_after']['do_math/system_clock.py'] = 'different-edition'
                elif kind == 'request':
                    manifest['request']['requested'] = ['boundary.some_other.Case.test_x']
                elif kind == 'sqlite':
                    from do_math.file_io import sha256_file
                    (worker / DATA).write_bytes(b'not a database')
                    manifest['artifacts'][DATA] = sha256_file(worker / DATA)
                if kind not in ('missing', 'corrupt'):
                    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
                result = self.measure(root, {**self.worker, 'directory': str(worker)})
                self.assertFalse(result['complete'])
                self.assertEqual(len(result['problems']), 1)
                self.assertEqual(result['workers'][0]['status'], 'invalid')
                self.assertEqual(set(result['modules']), {p for p in self.request['source_sha256']
                    if p in result['modules']})
                self.assertEqual(result['modules']['do_math/system_clock.py']['executed_lines'], [])
                self.assertTrue(result['modules']['do_math/system_clock.py']['missing_lines'])

    def test_an_actual_worker_merges_and_zero_reach_files_keep_the_source_denominator(self):
        root = self.root / 'valid'
        root.mkdir()
        result = self.measure(root, self.worker)
        self.assertTrue(result['complete'], result['problems'])
        self.assertEqual(result['workers'][0]['status'], 'merged')
        clock = result['modules']['do_math/system_clock.py']
        self.assertTrue(set(clock['executed_lines']) & body_lines('do_math/system_clock.py', 'wall'))
        self.assertGreater(result['totals']['num_branches'], 0)


if __name__ == '__main__':
    unittest.main()
