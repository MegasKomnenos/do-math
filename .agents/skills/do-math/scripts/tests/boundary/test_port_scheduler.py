"""Real side of the scheduler port contract: the PowerShell task adapter (status only)."""
import unittest

from support.port_contracts.scheduler import SchedulerContract
from do_math.wiring import real_ports
from test_categories import test_group


@test_group('resource')
class PowerShellSchedulerContract(SchedulerContract, unittest.TestCase):
    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).scheduler


if __name__ == '__main__':
    unittest.main()
