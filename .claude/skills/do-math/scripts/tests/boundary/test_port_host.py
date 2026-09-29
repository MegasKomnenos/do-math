"""Real side of the host observation port contract: this machine's Lean and provider CLI observations."""
import unittest

from contracts.test_port_host import HostContract
from do_math.wiring import real_ports


class LocalHostContract(HostContract, unittest.TestCase):
    def make(self):
        return real_ports().host


if __name__ == '__main__':
    unittest.main()
