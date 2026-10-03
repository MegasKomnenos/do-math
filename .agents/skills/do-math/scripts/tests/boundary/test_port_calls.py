"""Thread side of the calls port contract."""
import unittest

from support.port_contracts.calls import CallsContract
from do_math.wiring import real_ports


class ThreadCallsContract(CallsContract, unittest.TestCase):
    def track_threads(self, calls):
        threads = list(calls.threads)
        return lambda: threads

    def park_callback(self, calls):
        self.assertTrue(calls.wake.wait(5), 'start callback was not queued')
        self.assertEqual(calls.events.qsize(), 1)

    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).calls


if __name__ == '__main__':
    unittest.main()
