"""Scheduler port contract (설계 2.2, 8): the PowerShell task adapter and the fake answer alike.

The shared contract uses ``status`` only, which reads and never changes the OS.
Registering and cancelling are checked on the fake here and on the real
adapter only in the smoke tier (T5), because they change the OS task list.
"""

import os

import unittest


def _arguments(suffix):
    names = {'OperatorTask': 'DoMath-contract-operator-' + suffix, 'EngineTask': 'DoMath-contract-engine-' + suffix,
             'WakeTask': 'DoMath-contract-wake-' + suffix}
    return {'Repository': os.getcwd(), 'Instance': 'RI-01M3HM0X0000000000000000AB', 'Workspace': os.getcwd(),
            'Python': 'python', **names}

@unittest.skipUnless(os.name == 'nt', 'Windows port contract')
class SchedulerContract:
    def make(self):
        raise NotImplementedError

    def test_status_of_tasks_that_do_not_exist_reports_all_three_absent(self):
        value = self.make().run('status', _arguments(os.urandom(8).hex()))
        self.assertEqual(value, {'operator': None, 'engine': None, 'wake': None})
