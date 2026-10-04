"""Operator children and probe use real workers/runners with external programs at spawn."""
from copy import deepcopy
from contextlib import redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tempfile
import sys
import subprocess
import unittest

import probe_cli
from do_math import formal, scheduled_operator as operator
from do_math.model_runner import ModelRunner
from support.operator_finish_scene import Scene, OperatorCLI, diagnose
from support.provider_probes import ObservedCalls
from support.provider_runs import ProviderJobs, fake_ports
from support.fakes.clock import FakeClock
from support.fakes.git_backend import make_fake
from support.sim import warm_template
from support.storage_probes import Returns

setUpModule = warm_template


class EngineChildTests(unittest.TestCase):
    def test_command_start_error_preserves_original_exception(self):
        """Both operator consumers must retain the former subprocess error contract."""
        self.maxDiff = None
        observed, expected = [], []
        for function in (operator.run_engine, operator.recovery):
            scene = Scene()
            scene.answer()
            # Exercise the original subprocess contract on a nonexistent executable.
            with self.assertRaises(FileNotFoundError) as original:
                subprocess.run([str(scene.sim.root / 'absent-operator-child.exe')],
                    capture_output=True, text=True, encoding='utf-8', check=False,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            scene.command_error = original.exception  # only the external spawn boundary
            options = {'failure': {'kind': 'engine_unavailable', 'error': 'start error comparison'}} if function is operator.recovery else {}
            result = scene.call(function, **options)
            self.assertEqual(result['outcome'], 'recovery_failed' if options else 'engine_failed')
            if options:
                execution = scene.load()[2]['executions'][result['execution_id']]
                observed.append(execution['error'])
                expected.append({'type': type(original.exception).__name__, 'message': str(original.exception)})
                self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
            else:
                observed.append(result['error'])
                expected.append(f'{type(original.exception).__name__}: {original.exception}')
            self.assertTrue(all(job.closed and job.done for job in scene.jobs.launched))
        self.assertEqual(observed, expected)

    def test_accepted_child_diagnosis_requests_supervisor_immediately(self):
        scene = Scene()
        scene.on_command = lambda command: diagnose(scene)
        result = scene.call(operator.run_engine)
        self.assertEqual(result['outcome'], 'completed', result)
        self.assertEqual([action for action, _ in scene.ports.scheduler.calls], ['start-operator'])
        self.assertIn('supervisor_request', result)
        self.assertEqual(result['after']['installation_repair']['status'], 'installation_repair_pending')

    def test_live_installation_child_retains_argv_streams_exit_and_after_status(self):
        scene = Scene()
        scene.stdout, scene.stderr = '{"status":"ready"}\n', 'child diagnostic é\n'
        scene.jobs.polls = 3
        started = scene.ports.clock.monotonic()
        scene.on_command = lambda command: (scene.sim.engine._idle_wait_status(), scene.sim.engine._save())
        def after_barrier(args):
            if scene.commands:
                self.assertTrue(all(job.closed and job.done for job in scene.jobs.launched))
                self.assertTrue(all(job.inspections >= 3 for job in scene.jobs.launched))
            return args
        with Returns(operator.child_environment, snapshot=deepcopy) as environments, Returns(
                operator.read_status, snapshot=deepcopy) as statuses, ObservedCalls(
                read=operator.read_status, job=formal._job_run, capture={'read': after_barrier}) as calls:
            result = scene.call(operator.run_engine)
        self.assertEqual(calls.count('read'), 2)
        self.assertGreaterEqual(scene.ports.clock.monotonic() - started, .039)
        self.assertEqual(scene.jobs.launched[0].env, environments.snapshots[0])
        self.assertEqual(result['outcome'], 'completed', result)
        self.assertEqual(result['exit_code'], 0)
        before, after = statuses.snapshots
        self.assertEqual(result['before'], before)
        self.assertEqual(result['after'], after)
        self.assertEqual(result['before']['status'], 'ready')
        self.assertEqual(result['after']['status'], 'waiting')
        command, = scene.commands
        expected_command = [sys.executable, str(scene.installation / 'scripts/do_math.py'),
                            'run', '--repository', str(scene.args[0]), '--instance', scene.args[1], '--watch']
        self.assertEqual(command['command'], expected_command)
        job, = calls.captured('job')
        self.assertEqual(job['command'], expected_command)
        self.assertEqual(job['cwd'], scene.sim.root)
        self.assertEqual(job['env'], environments.snapshots[0])
        self.assertIs(job['jobs'], scene.ports.jobs)
        self.assertIs(job['clock'], scene.ports.clock)
        self.assertEqual(command['cwd'], str(scene.sim.root))
        run = Path(result['run_directory'])
        self.assertEqual(json.loads((run / 'before.json').read_bytes()), before)
        self.assertEqual((run / 'stdout.json').read_text(encoding='utf-8'), scene.stdout)
        self.assertEqual((run / 'stderr.txt').read_text(encoding='utf-8'), scene.stderr)
        self.assertEqual(json.loads((scene.workspace / 'operator/latest-engine.json').read_bytes()), result)
        self.assertTrue(all(job.closed and job.done for job in scene.jobs.launched))
        # Requires main's already-integrated spool/strict preservation change.
        self.assertEqual((job.get('evidence_dir'), job.get('decode_errors')), (run, 'strict'))

    def test_writer_contention_is_busy_and_does_not_open_recovery(self):
        scene = Scene()
        scene.exit_code = 5
        scene.stdout = json.dumps({'exit_code': 5, 'error': {'kind': 'tool_error',
            'message': 'writer lock is busy', 'next_owner': 'operator', 'retryable': True}})
        result = scene.call(operator.run_engine)
        self.assertEqual(result['outcome'], 'engine_busy', result)
        self.assertEqual(json.loads((scene.workspace / 'operator/latest-engine.json').read_bytes())['outcome'], 'engine_busy')
        with ObservedCalls(recovery=operator.recovery) as calls:
            self.assertEqual(scene.call(operator.check)['outcome'], 'engine_requested')
        self.assertEqual(calls.count('recovery'), 0)


class ProbeRunnerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clock = FakeClock()
        self.cli = OperatorCLI()
        self.jobs = ProviderJobs(self.cli, clock=clock)
        self.ports = fake_ports(clock, make_fake(), self.jobs)

    def test_claude_prefix_is_forwarded_once_to_the_actual_runner_and_worker(self):
        from support.entry import entry
        _entry = entry()
        for model, routed in (('opus', 'claude:opus'), ('claude:opus', 'claude:opus'),
                              ('claude-opus-5', 'claude-opus-5')):
            with self.subTest(model=model), ObservedCalls(run=ModelRunner.run) as calls:
                result = probe_cli.run_case(self.root / model.replace(':', '-'), 'structured', ports=self.ports,
                    provider='claude', model=model, effort='low', only_assigned=False, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
            self.assertEqual(calls.captured('run')[0]['model'], routed)
            self.assertTrue(result['passed'], result)
            command = self.cli.calls[-1]['command']
            self.assertEqual(command[command.index('--model') + 1], routed.removeprefix('claude:'))
        self.assertEqual(len(self.cli.calls), 3)
        self.assertTrue(all(job.closed and job.done for job in self.jobs.launched))

    def test_live_report_hashes_every_implementation_module_after_real_collection(self):
        destination = self.root / 'evidence'
        with redirect_stdout(io.StringIO()):
            code = probe_cli.main(['--provider', 'codex', '--model', 'fixture-model', '--cases', 'structured',
                                   '--output-dir', str(destination)], ports=self.ports)
        self.assertEqual(code, 0)
        report = json.loads((destination / 'report.json').read_bytes())
        package = Path(probe_cli.__file__).parent / 'do_math'
        self.assertEqual(report['sources'], {str(path.relative_to(package.parent)):
            hashlib.sha256(path.read_bytes()).hexdigest() for path in package.rglob('*.py')})
        self.assertEqual(report['at'], self.ports.clock.now())
        self.assertEqual(len(self.cli.calls), 1)
        self.assertTrue(all(job.closed and job.done for job in self.jobs.launched))
