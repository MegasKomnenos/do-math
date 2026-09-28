"""Real side of the clock port contract."""
import time
import unittest

from contracts.test_port_clock import ClockContract
from do_math.wiring import real_ports


class SystemClockContract(ClockContract, unittest.TestCase):
    monotonic_resolution = time.get_clock_info('monotonic').resolution

    def make(self):
        return real_ports().clock


if __name__ == '__main__':
    unittest.main()
