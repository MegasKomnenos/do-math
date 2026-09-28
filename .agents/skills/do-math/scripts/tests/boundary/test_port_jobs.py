"""Real side of the Jobs port contract: Windows Jobs."""
import unittest

from contracts.test_port_jobs import JobsContract
from do_math.wiring import real_ports


class WindowsJobsContract(JobsContract, unittest.TestCase):
    def make(self):
        return real_ports().jobs


if __name__ == '__main__':
    unittest.main()
