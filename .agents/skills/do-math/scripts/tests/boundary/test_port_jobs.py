"""Real side of the Jobs port contract: Windows Jobs."""
import unittest
from test_categories import test_group

from support.port_contracts.jobs import JobsContract
from do_math.wiring import real_ports


@test_group('resource')
class WindowsJobsContract(JobsContract, unittest.TestCase):
    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).jobs


if __name__ == '__main__':
    unittest.main()
