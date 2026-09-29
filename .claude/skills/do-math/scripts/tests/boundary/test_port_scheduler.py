"""Real side of the scheduler port contract: the PowerShell task adapter (status only)."""
import unittest

from contracts.test_port_scheduler import SchedulerContract
from do_math.wiring import real_ports


class PowerShellSchedulerContract(SchedulerContract, unittest.TestCase):
    def make(self):
        return real_ports().scheduler


if __name__ == '__main__':
    unittest.main()
