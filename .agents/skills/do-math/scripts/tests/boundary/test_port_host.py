"""Real side of the host observation port contract: this machine's Lean and provider CLI observations."""
import unittest

from support.port_contracts.host import HostContract
from do_math.wiring import real_ports
from test_categories import test_group


@test_group('resource')
class LocalHostContract(HostContract, unittest.TestCase):
    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).host


if __name__ == '__main__':
    unittest.main()
