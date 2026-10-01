"""CLI initialization, schedule failure and conditional release on real repository state."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

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
        for error in (None, RuntimeError('scheduler unavailable'), OSError('scheduler executable unavailable'),
                      subprocess.SubprocessError('scheduler process failed')):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sim = Sim.activated()
                repository = make_repository(root / 'repository')
                scheduler = Scheduler(error=error)
                ports = replace(sim.ports, scheduler=scheduler)
                config = root / 'config.json'
                config.write_text(json.dumps({'scholarly_enabled': False}), encoding='utf-8')
                args = cli.build_parser().parse_args(['init', '--repository', str(repository),
                    '--workspace', str(root / 'work'), '--goal', 'Keep the saved instance', '--config-file', str(config)])
                with Returns(initialize, snapshot=deepcopy) as saved, Returns(
                        operator.schedule, snapshot=deepcopy) as scheduled:
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
                    self.assertIn('operator install', failure['reconcile'])
                    self.assertIn('--repository', failure['reconcile'])
                    self.assertIn(str(repository), failure['reconcile'])

    def test_configure_schedule_process_errors_preserve_the_applied_control(self):
        from support.entry import entry
        _entry = entry()
        for error in (OSError('scheduler executable unavailable'), subprocess.SubprocessError('scheduler process failed')):
            with self.subTest(error=error):
                scene = Scene()
                ports = replace(scene.ports, scheduler=Scheduler(error=error))
                config = scene.sim.root / 'configuration.json'
                config.write_text(json.dumps({'operator_interval_seconds': 8000}), encoding='utf-8')
                args = cli.build_parser().parse_args(['configure', '--repository', str(scene.args[0]),
                    '--instance', scene.args[1], '--config-file', str(config)])
                with Returns(cli._control, snapshot=deepcopy) as saved:
                    result, code = cli.execute(args, ports=ports, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id)
                self.assertEqual(code, 5)
                self.assertEqual({key: result[key] for key in saved.snapshots[0]}, saved.snapshots[0])
                self.assertEqual(result['effect'], 'applied')
                self.assertEqual(scene.load()[1]['config']['operator_interval_seconds'], 8000)
                self.assertEqual(result['operator_schedule']['status'], 'failed')
                self.assertEqual(result['operator_schedule']['error'], str(error))

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
