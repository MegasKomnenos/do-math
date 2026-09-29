"""Clock port contract (설계 2.2): the same expectations bind the real clock and its fake.

``ClockContract`` is not a TestCase so it does not run by itself. The fake side
runs here; the real side is ``boundary/test_port_clock.py``.
"""
from datetime import timezone
import re
import unittest

from do_math.values import parse_utc
from do_math.ids import ULID_PATTERN
from support.fakes.clock import make_fake


class ClockContract:
    # Tick of the implementation's monotonic clock. On Windows the system clock
    # ticks every 15.625 ms, so a measured sleep may fall short by one tick.
    monotonic_resolution = 0.0

    def make(self):
        raise NotImplementedError

    def test_now_is_an_iso_utc_time_that_the_product_parses(self):
        parsed = parse_utc(self.make().now())
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)

    def test_wall_is_an_aware_utc_datetime(self):
        self.assertIs(self.make().wall().tzinfo, timezone.utc)

    def test_wall_ns_agrees_with_wall(self):
        clock = self.make()
        self.assertLess(abs(clock.wall_ns() / 1e9 - clock.wall().timestamp()), 5)

    def test_monotonic_never_decreases(self):
        clock = self.make()
        first = clock.monotonic()
        self.assertGreaterEqual(clock.monotonic(), first)

    def test_sleep_advances_monotonic_time_by_at_least_the_duration(self):
        clock = self.make()
        first = clock.monotonic()
        clock.sleep(0.02)
        self.assertGreaterEqual(clock.monotonic() - first, 0.02 - self.monotonic_resolution - 1e-6)

    def test_new_ids_have_the_stored_shape_and_differ(self):
        clock = self.make()
        first, second = clock.new_id('EX'), clock.new_id('EX')
        self.assertRegex(first, re.compile(f'EX-{ULID_PATTERN}'))
        self.assertNotEqual(first, second)

    def test_random_hex_has_the_requested_width_and_differs(self):
        clock = self.make()
        first, second = clock.random_hex(32), clock.random_hex(32)
        self.assertRegex(first, re.compile('[0-9a-f]{64}'))
        self.assertEqual(len(first), 64)
        self.assertNotEqual(first, second)

    def test_new_id_rejects_a_non_registry_prefix(self):
        with self.assertRaisesRegex(ValueError, 'canonical uppercase registry prefix'):
            self.make().new_id('ex')


class FakeClockContract(ClockContract, unittest.TestCase):
    def make(self):
        return make_fake()


if __name__ == '__main__':
    unittest.main()
