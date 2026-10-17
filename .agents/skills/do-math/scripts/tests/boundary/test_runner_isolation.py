"""Actual runner workers and Windows Jobs; only disposable Python children.

Specimen sources and raw worker publications remain under the official
resource worker's scratch. No compiler, provider or scheduler is invoked.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_tests
from do_math.windows_job import WindowsJob
from support.host_live import reached
from test_categories import test_group


@test_group('resource')
@unittest.skipUnless(os.name == 'nt', 'requires real Windows Jobs')
class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='runner-isolation-')).resolve()
        print('Runner isolation evidence: ' + str(self.root), flush=True)

    def specimen(self, source, methods):
        root = self.root / str(len(list(self.root.iterdir())))
        root.mkdir()
        (root / 'isolation_specimen.py').write_text(source, encoding='utf-8')
        identifiers = ['isolation_specimen.Case.' + method for method in methods]
        python_path = os.pathsep.join(filter(None, [str(root), os.environ.get('PYTHONPATH')]))
        destination = root / 'worker'
        with patch.dict(os.environ, {'PYTHONPATH': python_path}):
            report = run_tests._isolated([SimpleNamespace(id=lambda value=value: value)
                                          for value in identifiers], destination)
        self.assertEqual(report['requested'], identifiers)
        self.assertEqual([row['id'] for row in report['rows'] if not row.get('fixture')], identifiers)
        self.assertEqual(json.loads((destination / 'worker-report.json').read_bytes()), report)
        return report, destination

    def test_worker_retains_scratch_environment_streams_and_immutable_progress(self):
        report, destination = self.specimen(
            'import json, os, sys, tempfile, unittest\nfrom pathlib import Path\n'
            'class Case(unittest.TestCase):\n'
            '    def test_one(self):\n'
            '        print("stdout 한글", flush=True)\n'
            '        print("stderr 한글", file=sys.stderr, flush=True)\n'
            '        Path("environment.json").write_text(json.dumps({\n'
            '            "cwd": os.getcwd(), "tempfile": tempfile.gettempdir(),\n'
            '            **{key: os.environ[key] for key in ("TMP", "TEMP", "TMPDIR")}}))\n'
            '    def test_two(self): self.assertTrue(True)\n', ['test_one', 'test_two'])
        self.assertTrue(report['complete'])
        self.assertTrue(report['successful'])
        self.assertEqual(report['returncode'], 0)
        self.assertEqual([row['outcome'] for row in report['rows']], ['passed', 'passed'])
        environment = json.loads((destination / 'environment.json').read_bytes())
        self.assertEqual(Path(environment.pop('cwd')), destination)
        self.assertEqual({Path(value) for value in environment.values()}, {destination / 'scratch'})
        self.assertIn('stdout 한글', (destination / 'stdout.txt').read_text(encoding='utf-8'))
        self.assertIn('stderr 한글', (destination / 'stderr.txt').read_text(encoding='utf-8'))
        progress = [json.loads(path.read_bytes()) for path in sorted(destination.glob('progress-*.json'))]
        self.assertEqual([row['sequence'] for row in progress], [1, 2, 3, 4])
        self.assertEqual([row['phase'] for row in progress], ['test', 'fixture_or_shutdown'] * 2)
        self.assertEqual([row['test_id'] for row in progress],
                         [report['requested'][0], None, report['requested'][1], None])

    def test_worker_abort_and_interrupt_keep_unfinished_and_last_selection_not_run(self):
        for action, code in [('os._exit(9)', 9), ('raise KeyboardInterrupt("specimen stop")', None)]:
            with self.subTest(action=action):
                report, destination = self.specimen(
                    'import os, unittest\nclass Case(unittest.TestCase):\n'
                    '    def test_first(self): self.assertTrue(True)\n'
                    '    def test_interrupt(self): ' + action + '\n'
                    '    def test_last(self): self.fail("must not run")\n',
                    ['test_first', 'test_interrupt', 'test_last'])
                raw = json.loads((destination / 'result.json').read_bytes())
                self.assertFalse(raw['complete'])
                self.assertFalse(report['complete'])
                self.assertFalse(report['successful'])
                self.assertEqual([row['outcome'] for row in report['rows']], ['passed', 'not_run', 'not_run'])
                self.assertNotEqual(report['returncode'], 0)
                if code is not None:
                    self.assertEqual(report['returncode'], code)
                else:
                    self.assertIn('KeyboardInterrupt: specimen stop',
                                  (destination / 'stderr.txt').read_text(encoding='utf-8'))

    def test_worker_fixture_skip_and_error_have_distinct_complete_reports(self):
        for error, outcome, code in [('unittest.SkipTest', 'skipped', 0), ('RuntimeError', 'error', 1)]:
            with self.subTest(error=error):
                report, _ = self.specimen(
                    'import unittest\nclass Case(unittest.TestCase):\n'
                    '    @classmethod\n'
                    '    def setUpClass(cls): raise ' + error + '("fixture specimen")\n'
                    '    def test_one(self): self.fail("must not run")\n'
                    '    def test_two(self): self.fail("must not run")\n', ['test_one', 'test_two'])
                fixture, *rows = report['rows']
                self.assertTrue(report['complete'])
                self.assertEqual(report['successful'], code == 0)
                self.assertEqual(report['returncode'], code)
                self.assertTrue(fixture['fixture'])
                self.assertEqual(fixture['outcome'], outcome)
                self.assertEqual([row['outcome'] for row in rows],
                                 ['skipped' if code == 0 else 'not_run'] * 2)

    def test_wait_observes_a_live_owned_child_after_the_actual_root_exits(self):
        release = self.root / 'release'
        child_pid = self.root / 'child-pid'
        child_code = ('import threading; from pathlib import Path\n'
                      f'while not Path({str(release)!r}).exists(): threading.Event().wait(.02)\n')
        root_code = ('import subprocess, sys; from pathlib import Path\n'
                     f'child = subprocess.Popen([sys.executable, "-c", {child_code!r}], '
                     'creationflags=subprocess.CREATE_NO_WINDOW)\n'
                     f'Path({str(child_pid)!r}).write_text(str(child.pid))\n')
        with WindowsJob([sys.executable, '-c', root_code]) as job:
            job.resume()
            try:
                self.assertTrue(reached(lambda: job.wait(0) and child_pid.exists()), 'root did not exit')
                pid = int(child_pid.read_text())
                before = job.inspect()
                (self.root / 'ownership.json').write_text(json.dumps({
                    'executable': sys.executable, 'root_pid': job.pid, 'child_pid': pid,
                    'root_signaled': before.root_signaled, 'active_processes': before.active_processes,
                    'process_ids': before.process_ids}), encoding='utf-8')
                self.assertTrue(before.root_signaled)
                # An interpreter command may include a native launcher as well
                # as its interpreter. All live descendants remain owned.
                self.assertGreaterEqual(before.active_processes, 1)
                self.assertIn(pid, before.process_ids)
                observations = []
                def release_after_observation(seconds):
                    state = job.inspect()
                    observations.append(state)
                    self.assertTrue(state.root_signaled)
                    self.assertIn(pid, state.process_ids)
                    release.write_text('release')
                    self.assertTrue(reached(lambda: run_tests._empty(job)), 'owned child did not exit')
                run_tests.wait_for_worker(job, pause=release_after_observation)
                self.assertEqual(len(observations), 1)
                self.assertTrue(run_tests._empty(job))
            finally:
                job.terminate()
                run_tests.wait_for_worker(job)

    def test_parent_interrupt_confirms_owned_tree_termination_and_retains_not_run(self):
        destination = self.root / '0' / 'worker'
        original_wait = run_tests.wait_for_worker
        ended = []
        def interrupt_once(job):
            if not ended:
                self.assertTrue(reached(lambda: bool(list(destination.glob('progress-*.json')))),
                                'worker did not start its test')
                ended.append(None)
                raise KeyboardInterrupt('explicit specimen cancellation')
            original_wait(job)
            ended.append(job.inspect())
        with patch.object(run_tests, 'wait_for_worker', side_effect=interrupt_once):
            report, _ = self.specimen(
                'import threading, unittest\nclass Case(unittest.TestCase):\n'
                '    def test_wait(self): threading.Event().wait()\n'
                '    def test_last(self): self.fail("must not run")\n', ['test_wait', 'test_last'])
        self.assertEqual(len(ended), 2)
        self.assertTrue(ended[1].root_signaled)
        self.assertEqual((ended[1].active_processes, ended[1].process_ids), (0, ()))
        self.assertTrue(report['interrupted'])
        self.assertFalse(report['complete'])
        self.assertFalse(report['successful'])
        self.assertIn('KeyboardInterrupt: explicit specimen cancellation', report['worker_error'])
        self.assertEqual([row['outcome'] for row in report['rows']], ['not_run', 'not_run'])
