"""Actual engine status reaches operator guards; all effects cross the supplied ports."""
from copy import deepcopy
import json
import sys
from pathlib import Path
from dataclasses import replace
import unittest

from do_math import scheduled_operator as operator
from do_math.model_runner import ModelRunner
from support.operator_finish_observers import construction, outside_status
from support.storage_probes import Returns
from support.operator_finish_scene import Scene
from support.provider_probes import ObservedCalls
from support.sim import warm_template
from support.operator_finish_ports import UnreadableOnce

setUpModule = warm_template


class SupervisionTests(unittest.TestCase):
    def test_probe_uses_one_real_status_without_model_recovery_or_scheduler(self):
        scene = Scene()
        before = scene.load()[0]
        with ObservedCalls(status=operator.read_status, model=ModelRunner.run,
                           recovery=operator.recovery, runner=ModelRunner.__init__,
                           capture={'runner': construction}) as calls, Returns(
                               operator.read_status, snapshot=deepcopy) as statuses:
            result = scene.call(operator.check, probe=True)
        self.assertEqual(result['outcome'], 'observed')
        status, = statuses.snapshots
        self.assertEqual(result, {'outcome': 'observed', 'status': status, 'model_called': False,
                                  'engine_start': {'outcome': 'startable', 'before': status}})
        self.assertEqual(outside_status(calls, 'runner'), [])
        self.assertEqual(sum(c['status_engine'] for c in calls.captured('runner')), 1)
        self.assertEqual(scene.jobs.launched, [])
        self.assertFalse(result['model_called'])
        self.assertEqual(calls.count('status'), 1)
        self.assertEqual(calls.count('model'), 0)
        self.assertEqual(calls.count('recovery'), 0)
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual(scene.load()[0], before)

    def test_read_status_reaches_guard_and_wake_obeys_pause_and_hold(self):
        scene = Scene()
        scene.sim._apply('configure', config={'operator_enabled': False})
        self.assertFalse(scene.load()[1]['config']['operator_enabled'])
        scheduling = self.enterContext(ObservedCalls(schedule=operator.schedule))
        with ObservedCalls(read=operator.read_status, guard=operator.start_guard) as calls:
            result = scene.call(operator.wake)
        self.assertEqual(result['outcome'], 'engine_requested')
        self.assertEqual(calls.captured('read'), [{'repository': scene.args[0],
            'instance': scene.args[1], 'ports': scene.ports, 'codex_home': scene.sim.codex_home,
            'environment': scene.sim.environment, 'host_id': scene.sim.host_id}])
        self.assertEqual(calls.captured('guard'), [{'status': result['before']}])
        self.assertEqual([action for action, _ in scene.ports.scheduler.calls], ['start-engine'])
        scheduled, = scheduling.captured('schedule')
        self.assertEqual(scheduled, {'action': 'start-engine', 'repository': scene.args[0],
            'instance': scene.args[1], 'workspace': scene.workspace, 'interval_seconds': None,
            'operator_timeout_seconds': None, 'wake_at': None, 'wake_key': None,
            'scheduler': scene.ports.scheduler})
        pythonw = Path(sys.executable).with_name('pythonw.exe')
        names = operator.task_names(scene.args[0], scene.args[1])
        expected = ('start-engine', {'Repository': str(scene.args[0].resolve()),
            'Instance': scene.args[1], 'Workspace': str(scene.workspace.resolve()),
            'Python': str(pythonw) if pythonw.is_file() else sys.executable,
            'OperatorTask': names['operator'], 'EngineTask': names['engine'], 'WakeTask': names['wake']})
        self.assertEqual(scene.ports.scheduler.calls, [expected])
        scene.sim._apply('pause', text='Keep this synthetic instance paused')
        for function, outcome in ((operator.wake, 'paused'), (operator.run_engine, 'paused'),
                                  (operator.check, 'disabled')):
            self.assertEqual(scene.call(function)['outcome'], outcome)
        marker = operator.hold(scene.workspace, reason='hold', clock=scene.ports.clock)
        self.assertEqual(marker['started_at'], scene.ports.clock.now())
        with ObservedCalls(read=operator.read_status) as calls:
            for function in (operator.wake, operator.run_engine, operator.check):
                self.assertEqual(scene.call(function)['outcome'], 'held')
        self.assertEqual(calls.count('read'), 0)
        self.assertEqual(scene.ports.scheduler.calls, [expected])
        self.assertEqual(scene.jobs.launched, [])
        self.assertEqual(scheduling.count('schedule'), 1)
        self.assertEqual(operator.release(scene.workspace, clock=scene.ports.clock)['released'], marker)

    def test_supervisor_requests_once_without_a_model(self):
        scene = Scene()
        with ObservedCalls(model=ModelRunner.run, recovery=operator.recovery,
                           repository=operator.ResearchRepository.__init__, runner=ModelRunner.__init__,
                           capture={'repository': construction, 'runner': construction}) as calls:
            first = scene.call(operator.check)
            second = scene.call(operator.check)
        self.assertEqual((first['outcome'], second['outcome']), ('engine_requested', 'engine_running'))
        self.assertFalse(first['model_called'])
        self.assertEqual(calls.count('model'), 0)
        self.assertEqual(calls.count('recovery'), 0)
        for name in ('repository', 'runner'):
            self.assertEqual(outside_status(calls, name), [])
            self.assertEqual(sum(c['status_engine'] for c in calls.captured(name)), 2)
        self.assertEqual([action for action, _ in scene.ports.scheduler.calls],
                         ['status', 'start-engine', 'status'])

    def test_completed_instance_is_observed_without_a_model(self):
        """First use builds the publicly verified theorem template (about 9 seconds)."""
        from support.governance_sim import theorem_sim
        from support.engine_lifecycle import solve_goal
        scene = Scene(theorem_sim())
        solve_goal(scene.sim.engine, 'k1')
        scene.sim.engine._save()
        with ObservedCalls(model=ModelRunner.run, runner=ModelRunner.__init__,
                           capture={'runner': construction}) as calls, Returns(
                               operator.read_status, snapshot=deepcopy) as statuses:
            result = scene.call(operator.check)
        self.assertEqual(result['outcome'], 'completed')
        status, = statuses.snapshots
        self.assertEqual(status['status'], 'completed')
        self.assertEqual(result['status'], status)
        self.assertEqual(outside_status(calls, 'runner'), [])
        self.assertEqual(sum(c['status_engine'] for c in calls.captured('runner')), 1)
        self.assertEqual(calls.count('model'), 0)
        self.assertEqual(scene.ports.scheduler.calls, [])

    def test_automatic_pause_and_user_pause_never_open_external_recovery(self):
        for user in (False, True):
            with self.subTest(user=user):
                scene = Scene()
                if user:
                    scene.sim._apply('pause', text='user stop')
                else:
                    scene.sim.engine._pause_lifecycle('automatic stop')
                    scene.sim.engine._save()
                with ObservedCalls(model=ModelRunner.run, recovery=operator.recovery,
                                   runner=ModelRunner.__init__, capture={'runner': construction}) as calls:
                    result = scene.call(operator.check)
                self.assertEqual(result['outcome'], 'paused')
                self.assertEqual(bool(result['status'].get('user_pause')), user)
                self.assertEqual(outside_status(calls, 'runner'), [])
                self.assertEqual(sum(c['status_engine'] for c in calls.captured('runner')), 1)
                self.assertEqual(calls.count('model'), 0)
                self.assertEqual(calls.count('recovery'), 0)
                self.assertEqual(scene.ports.scheduler.calls, [])

    def test_unavailable_status_is_preserved_before_locked_recovery_and_probe_stops(self):
        for probe in (False, True):
            with self.subTest(probe=probe):
                scene = Scene()
                scene.ports = replace(scene.ports, git_backend=UnreadableOnce(scene.ports.git_backend.objects))
                scene.answer()
                scene.cli.answer['next_step'] = None
                def before_recovery(arguments):
                    persisted = json.loads((scene.workspace / 'operator/engine-failure.json').read_bytes())
                    self.assertEqual(persisted, arguments['failure'])
                    return arguments
                with ObservedCalls(recovery=operator.recovery,
                                   capture={'recovery': before_recovery}) as calls:
                    result = scene.call(operator.check, probe=probe)
                failure = json.loads((scene.workspace / 'operator/engine-failure.json').read_bytes())
                self.assertEqual((failure['error_type'], failure['kind'], failure['error']),
                                 ('SyntaxError', 'engine_unavailable', 'engine broken'))
                self.assertEqual(failure['observed_at'], scene.ports.clock.now())
                if probe:
                    self.assertEqual(result, failure)
                    self.assertEqual(result['outcome'], 'recovery_required')
                    self.assertEqual(calls.count('recovery'), 0)
                else:
                    self.assertEqual(result['outcome'], 'recovery_failed')
                    self.assertEqual(calls.count('recovery'), 1)
                    self.assertEqual(calls.captured('recovery')[0]['failure'], failure)
                    preserved = scene.load()[2]['executions'][result['execution_id']]['input_manifest']['failure']
                    self.assertEqual(preserved, failure)

    def test_due_research_status_reaches_guard_and_requests_only_once(self):
        from do_math.provider_wait import epoch_seconds
        scene = Scene()
        # The public activation produced this timer. A stopped scheduler owner
        # has published waiting; advance to that exact saved deadline.
        due = scene.sim.runtime['next_research_reconsider_at']
        scene.sim.engine._idle_wait_status()
        scene.sim.engine._save()
        scene.sim.advance(epoch_seconds(due) - scene.ports.clock.wall().timestamp())
        original = scene.load()[0]
        with ObservedCalls(guard=operator.start_guard) as calls:
            probe = scene.call(operator.check, probe=True)
        self.assertEqual(probe['engine_start']['reason'], 'research reconsideration due')
        self.assertEqual(calls.captured('guard')[0]['status'], probe['status'])
        self.assertEqual(scene.ports.scheduler.calls, [])
        self.assertEqual(scene.load()[0], original)
        self.assertEqual(scene.call(operator.check)['outcome'], 'engine_requested')
        self.assertEqual(scene.call(operator.check)['outcome'], 'engine_running')
        self.assertEqual(sum(action == 'start-engine' for action, _ in scene.ports.scheduler.calls), 1)
