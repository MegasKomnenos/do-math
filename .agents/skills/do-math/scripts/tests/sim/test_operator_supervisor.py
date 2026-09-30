"""The scheduled operator's own steps, called directly without an engine (``scheduled_operator``, layer 3).

``schedule`` builds the scheduler port's request; its real port (the PowerShell
adapter) takes the process runner as a constructor argument, so the test
receives the exact argv the adapter would start. ``hold`` and ``release`` touch
only the operator's marker files. ``engine_start_guard`` checks the HOLD marker
before it reads any status and then judges the status it is given.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from do_math import planning, scheduled_operator
from support.provider_probes import ObservedCalls


AT = '2026-09-22T00:00:00+00:00'
INSTANCE = 'RI-00000000000000000000000000'


class OperatorFolders(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository = self.root / 'repository'
        self.workspace = self.root / 'workspace'
        self.repository.mkdir()
        self.workspace.mkdir()


class ScheduleRequestTests(OperatorFolders):
    def test_schedule_request_passes_only_generic_instance_coordinates(self):
        observed = []

        def runner(argv, **_):
            observed.append(argv)
            return subprocess.CompletedProcess(argv, 0, '{"operator":"ready"}', '')

        result = scheduled_operator.schedule('install', repository=self.repository, instance=INSTANCE,
                                             workspace=self.workspace, interval_seconds=7200,
                                             operator_timeout_seconds=5400, runner=runner)
        self.assertEqual(result['operator'], 'ready')
        self.assertEqual(len(observed), 1)
        command = observed[0]
        self.assertIn('install', command)
        self.assertIn(str(self.repository.resolve()), command)
        self.assertIn(str(self.workspace.resolve()), command)
        self.assertIn(INSTANCE, command)
        # "Only": after the script path the adapter receives named pairs, and exactly these names.
        pairs = command[command.index('-File') + 2:]
        named = dict(zip(pairs[::2], pairs[1::2]))
        self.assertEqual(set(named), {'-Action', '-Repository', '-Instance', '-Workspace', '-Python', '-OperatorTask',
                                      '-EngineTask', '-WakeTask', '-IntervalSeconds', '-OperatorTimeoutSeconds'})
        names = scheduled_operator.task_names(self.repository, INSTANCE)
        self.assertEqual({key: named['-' + key] for key in ('Action', 'Repository', 'Instance', 'Workspace',
                                                            'OperatorTask', 'EngineTask', 'WakeTask',
                                                            'IntervalSeconds', 'OperatorTimeoutSeconds')},
                         {'Action': 'install', 'Repository': str(self.repository.resolve()), 'Instance': INSTANCE,
                          'Workspace': str(self.workspace.resolve()), 'OperatorTask': names['operator'],
                          'EngineTask': names['engine'], 'WakeTask': names['wake'],
                          'IntervalSeconds': '7200', 'OperatorTimeoutSeconds': '5400'})


class HoldTests(OperatorFolders):
    def test_hold_and_release_do_not_resume_or_edit_research_state(self):
        hold = scheduled_operator.hold(self.workspace, reason='user requested stop')
        self.assertTrue((self.workspace / 'operator' / 'HOLD.json').exists())
        released = scheduled_operator.release(self.workspace)
        self.assertEqual(released['released']['id'], hold['id'])
        self.assertFalse((self.workspace / 'operator' / 'HOLD.json').exists())
        self.assertTrue((self.workspace / 'operator' / 'release.json').exists())
        self.assertEqual(json.loads((self.workspace / 'operator' / 'release.json').read_text(encoding='utf-8')),
                         released)
        self.assertEqual(list(self.repository.iterdir()), [], 'HOLD and release write nothing into the repository')


class StartGuardTests(OperatorFolders):
    def test_guard_reports_each_refusal_under_the_status_it_judged(self):
        """The judgment over one status; the status arrives as the ``status`` argument.

        The legacy test patched ``read_status`` to hand over the same status.
        That read opens the engine with the real ports and takes no Ports, so the
        wiring from ``read_status`` to this guard is not run here (see the
        migration ledger note). The HOLD case passes no status: the marker is
        read first and no status is read at all.
        """
        instance = {'lifecycle': {'state': 'active'}, 'goal_status': 'unresolved'}
        runtime = {'status': 'waiting', 'tasks': {}, 'executions': {},
                   'queue': [{'role': 'research_preparation'}], 'next_research_reconsider_at': AT}
        reasons = planning.research_wake_reasons(instance, runtime, now=AT)
        status = {'status': 'waiting', 'research_wake_reasons': reasons}
        self.assertEqual(scheduled_operator.engine_start_guard(self.repository, 'RI-test', self.workspace,
                                                               status=status),
                         {'outcome': 'startable', 'before': status, 'reason': 'research reconsideration due',
                          'research_wake_reasons': reasons})
        status['model_policy_violation'] = {'execution_id': 'EX-model'}
        # Every refusal reports the status it judged under the same key.
        self.assertEqual(scheduled_operator.engine_start_guard(self.repository, 'RI-test', self.workspace,
                                                               status=deepcopy(status)),
                         {'outcome': 'model_policy_waiting', 'before': status})
        del status['model_policy_violation']
        status['user_pause'] = {'reason': 'user'}
        self.assertEqual(scheduled_operator.engine_start_guard(self.repository, 'RI-test', self.workspace,
                                                               status=status)['outcome'], 'paused')
        scheduled_operator.hold(self.workspace, reason='test')
        with ObservedCalls(read=scheduled_operator.read_status) as observed:
            self.assertEqual(scheduled_operator.engine_start_guard(self.repository, 'RI-test', self.workspace),
                             {'outcome': 'held'})
        self.assertEqual(observed.count('read'), 0)


if __name__ == '__main__':
    unittest.main()
