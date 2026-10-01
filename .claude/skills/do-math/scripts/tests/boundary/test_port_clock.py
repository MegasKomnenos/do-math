"""Real side of the clock port contract."""
import time
import unittest

from support.port_contracts.clock import ClockContract
from do_math.wiring import real_ports


class SystemClockContract(ClockContract, unittest.TestCase):
    def test_resolutions_are_current_os_facts_in_wall_monotonic_order(self):
        clock = self.make()
        for _ in range(2):
            self.assertEqual(clock.resolutions(), (time.get_clock_info('time').resolution,
                                                   time.get_clock_info('monotonic').resolution))

    def make(self):
        from support.entry import entry
        _entry = entry()
        return real_ports(environment=_entry.environment).clock


if __name__ == '__main__':
    unittest.main()
