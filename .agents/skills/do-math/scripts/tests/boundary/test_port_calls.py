"""Thread side of the calls port contract."""
import unittest

from contracts.test_port_calls import CallsContract
from do_math.wiring import real_ports


class ThreadCallsContract(CallsContract, unittest.TestCase):
    def make(self):
        return real_ports().calls


if __name__ == '__main__':
    unittest.main()
