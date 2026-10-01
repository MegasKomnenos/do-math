"""Scheduler port contract (설계 2.2, 8): the PowerShell task adapter and the fake answer alike.

The shared contract uses ``status`` only, which reads and never changes the OS.
Registering and cancelling are checked on the fake here and on the real
adapter only in the smoke tier (T5), because they change the OS task list.
"""
import unittest

from support.fakes.scheduler import make_fake


from support.port_contracts.scheduler import _arguments, SchedulerContract

class FakeSchedulerContract(SchedulerContract, unittest.TestCase):
    def make(self):
        return make_fake()


class FakeSchedulerRegistrationTests(unittest.TestCase):
    """Fake-only semantics of the registering actions; the real side is checked in T5."""

    def test_a_scheduled_wake_is_reported_with_its_key_and_time_and_cancelled_away(self):
        scheduler = make_fake()
        arguments = _arguments('wake')
        value = scheduler.run('schedule-wake', {**arguments, 'WakeAt': '2030-01-01T00:00:00+00:00', 'WakeKey': 'K1'})
        self.assertEqual((value['wake']['description'], value['wake']['next_run']),
                         ('K1', '2030-01-01T00:00:00.0000000Z'))
        self.assertIsNone(scheduler.run('cancel-wake', arguments)['wake'])
        self.assertEqual([action for action, _ in scheduler.calls], ['schedule-wake', 'cancel-wake'])

    def test_install_registers_operator_and_engine_and_uninstall_removes_every_task(self):
        scheduler = make_fake()
        arguments = _arguments('install')
        value = scheduler.run('install', {**arguments, 'IntervalSeconds': '3600', 'OperatorTimeoutSeconds': '600'})
        self.assertEqual((value['operator']['name'], value['engine']['name'], value['wake']),
                         (arguments['OperatorTask'], arguments['EngineTask'], None))
        self.assertEqual(scheduler.run('uninstall', arguments), {'operator': None, 'engine': None, 'wake': None})


if __name__ == '__main__':
    unittest.main()
