"""CLI initialization, schedule failure and conditional release on real repository state."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from do_math import cli, scheduled_operator as operator
from do_math.engine import initialize
from do_math.repository import ResearchRepository
from support.fakes.git_backend import make_repository
from support.operator_finish_ports import Scheduler
from support.operator_finish_scene import Scene
from support.provider_probes import ObservedCalls
from support.storage_probes import Returns
from support.sim import Sim, warm_template

setUpModule = warm_template


class CliTests(unittest.TestCase):
    def test_new_instance_installs_default_two_hour_operator_and_keeps_saved_failures(self):
        """About 3 s: real initialization receipts cover four scheduler faults, including a missing console sibling."""
        for error, missing_console in ((None, False), (RuntimeError('scheduler unavailable'), False),
                      (OSError('scheduler executable unavailable'), False),
                      (subprocess.SubprocessError('scheduler process failed'), False),
                      (RuntimeError('scheduler unavailable'), True)):
            with self.subTest(error=error, missing_console=missing_console), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sim = Sim.activated()
                repository = make_repository(root / 'repository')
                scheduler = Scheduler(error=error)
                ports = replace(sim.ports, scheduler=scheduler)
                config = root / 'config.json'
                config.write_text(json.dumps({'scholarly_enabled': False}), encoding='utf-8')
                args = cli.build_parser().parse_args(['init', '--repository', str(repository),
                    '--workspace', str(root / 'work'), '--goal', 'Keep the saved instance', '--config-file', str(config)])
                windowless = root / 'pythonw.exe'
                windowless.write_bytes(b'')
                with Returns(initialize, snapshot=deepcopy) as saved, Returns(
                        operator.schedule, snapshot=deepcopy) as scheduled, patch.object(
                        sys, 'executable', str(windowless) if missing_console else sys.executable):
                    result, code = cli.execute(args, ports=ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
                self.assertEqual({key: result[key] for key in saved.snapshots[0]}, saved.snapshots[0])
                repo = ResearchRepository(repository, result['instance_id'], backend=ports.git_backend, clock=ports.clock)
                self.assertEqual(repo.load()[0], result['snapshot'])
                action, actual = scheduler.calls[0]
                self.assertEqual(action, 'install')
                self.assertEqual(actual['IntervalSeconds'], '7200')
                self.assertEqual(len(scheduler.calls), 1)
                if error is None:
                    self.assertEqual(code, 0)
                    receipt, = scheduled.snapshots
                    self.assertEqual(result['operator_schedule'], receipt)
                    self.assertEqual(receipt['operator']['state'], 'Ready')
                else:
                    self.assertEqual(code, 5)
                    failure = result['operator_schedule']
                    self.assertEqual((failure['status'], failure['error']), ('failed', str(error)))
                    if missing_console:
                        self.assertIsNone(failure['reconcile'])
                        self.assertIn(repr(str(root / 'python.exe')), failure['reconcile_error'])
                    else:
                        self.assertIn('operator install', failure['reconcile'])
                        self.assertIn('--repository', failure['reconcile'])
                        self.assertIn(str(repository), failure['reconcile'])

    def test_configure_schedule_process_errors_preserve_the_applied_control(self):
        """About 3.5 s: three real applied controls retain receipts across independent scheduler/console failures."""
        from support.entry import entry
        _entry = entry()
        for error, missing_console in ((OSError('scheduler executable unavailable'), False),
                (subprocess.SubprocessError('scheduler process failed'), False),
                (OSError('scheduler executable unavailable'), True)):
            with self.subTest(error=error, missing_console=missing_console):
                scene = Scene()
                ports = replace(scene.ports, scheduler=Scheduler(error=error))
                config = scene.sim.root / 'configuration.json'
                config.write_text(json.dumps({'operator_interval_seconds': 8000}), encoding='utf-8')
                args = cli.build_parser().parse_args(['configure', '--repository', str(scene.args[0]),
                    '--instance', scene.args[1], '--config-file', str(config)])
                windowless = scene.sim.root / 'pythonw.exe'
                windowless.write_bytes(b'')
                with Returns(cli._control, snapshot=deepcopy) as saved, patch.object(
                        sys, 'executable', str(windowless) if missing_console else sys.executable):
                    result, code = cli.execute(args, ports=ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
                self.assertEqual(code, 5)
                self.assertEqual({key: result[key] for key in saved.snapshots[0]}, saved.snapshots[0])
                self.assertEqual(result['effect'], 'applied')
                self.assertEqual(scene.load()[1]['config']['operator_interval_seconds'], 8000)
                self.assertEqual(result['operator_schedule']['status'], 'failed')
                self.assertEqual(result['operator_schedule']['error'], str(error))
                if missing_console:
                    self.assertIsNone(result['operator_schedule']['reconcile'])
                    self.assertIn(repr(str(windowless.with_name('python.exe'))),
                                  result['operator_schedule']['reconcile_error'])

    def test_release_queues_conditional_resume_even_before_pending_hold_is_applied(self):
        from support.entry import entry
        _entry = entry()
        scene = Scene()
        marker = operator.hold(scene.workspace, reason='pending HOLD', clock=scene.ports.clock)
        pause = scene.sim.control('pause', text=operator.hold_pause_reason(marker['id']))
        self.assertFalse(scene.load()[2].get('user_pause'))
        args = cli.build_parser().parse_args(['operator', 'release', '--repository', str(scene.args[0]),
                                             '--instance', scene.args[1]])
        with ObservedCalls(submit=cli._control) as calls, scene.sim.engine.store.writer_lock():
            result, code = cli.execute(args, ports=scene.ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
        self.assertEqual(calls.count('submit'), 1)
        self.assertEqual(calls.captured('submit')[0]['config'], {
            'expected_user_pause_reason': operator.hold_pause_reason(marker['id'])})
        self.assertEqual((code, result['resume']['effect']), (0, 'pending engine processing'))
        self.assertEqual(result['released']['id'], marker['id'])
        scene.sim.engine.process_controls()
        self.assertEqual(scene.sim.engine.control_result(pause['request_id'])['effect'], 'applied')
        self.assertEqual(scene.sim.engine.control_result(result['resume']['request_id'])['effect'], 'applied')
        self.assertFalse(scene.load()[2].get('user_pause'))


class OperatorCommandTests(unittest.TestCase):
    def setUp(self):
        self.scene = Scene()

    def invoke(self, mode, *arguments, ports=None):
        from contextlib import redirect_stdout
        from io import StringIO
        output = StringIO()
        sim = self.scene.sim
        with redirect_stdout(output):
            code = cli.main(['operator', mode, '--repository', str(sim.repository),
                             '--instance', sim.instance_id, *map(str, arguments)],
                            ports=ports or self.scene.ports, environment=sim.environment,
                            host_id=sim.host_id, codex_home=sim.codex_home)
        return code, json.loads(output.getvalue())

    def test_supplied_workspace_must_match_the_instance_before_scheduler_access(self):
        before = self.scene.load()
        code, envelope = self.invoke('status', '--workspace', self.scene.workspace / '..' / self.scene.workspace.name)
        self.assertEqual(code, 0)
        self.assertIsNotNone(envelope['result']['operator'])
        calls = list(self.scene.ports.scheduler.calls)
        code, envelope = self.invoke('status', '--workspace', self.scene.workspace / 'different')
        self.assertEqual(code, 2)
        self.assertEqual(envelope['error'], {'kind': 'input_error',
            'message': '--workspace must equal the instance workspace', 'next_owner': 'user', 'retryable': False})
        self.assertEqual(self.scene.ports.scheduler.calls, calls)
        self.assertEqual(self.scene.load(), before)

    def test_startable_instance_requests_the_installed_engine_task(self):
        before = self.scene.load()
        code, envelope = self.invoke('start')
        self.assertEqual(code, 0)
        self.assertEqual(envelope['result']['engine']['state'], 'Running')
        self.assertEqual([action for action, _ in self.scene.ports.scheduler.calls], ['start-engine'])
        self.assertEqual(self.scene.load(), before)
        self.assertEqual(self.scene.jobs.launched, [])
        self.assertEqual(self.scene.cli.calls, [])

    def test_release_without_hold_never_requests_resume(self):
        before = self.scene.load()
        code, envelope = self.invoke('release')
        self.assertEqual(code, 0)
        self.assertEqual(envelope['result'], {'released': None,
            'resume': {'effect': 'not_requested', 'reason': 'no HOLD was released'}})
        self.assertEqual(self.scene.load(), before)
        self.assertEqual(self.scene.ports.scheduler.calls, [])

    def test_hold_stops_wake_engine_and_supervisor_at_the_public_boundary(self):
        code, held = self.invoke('hold', '--reason', 'No work while inspecting')
        self.assertEqual(code, 0)
        self.assertEqual(held['result']['pause']['effect'], 'applied')
        before = self.scene.load()
        calls = list(self.scene.ports.scheduler.calls)
        for mode in ('wake', 'engine', 'check', 'probe'):
            with self.subTest(mode=mode):
                code, envelope = self.invoke(mode)
                self.assertEqual(code, 0)
                self.assertEqual(envelope['result'], {'outcome': 'held'})
                self.assertEqual(self.scene.load(), before)
                self.assertEqual(self.scene.ports.scheduler.calls, calls)
                self.assertEqual(self.scene.jobs.launched, [])
                self.assertEqual(self.scene.cli.calls, [])
