"""Clock port contract (설계 2.2): the same expectations bind the real clock and its fake.

``ClockContract`` is not a TestCase so it does not run by itself. The fake side
runs here; the real side is ``boundary/test_port_clock.py``.
"""
import unittest

from support.fakes.clock import make_fake, FakeClock


from support.port_contracts.clock import ClockContract

class FakeClockContract(ClockContract, unittest.TestCase):
    def make(self):
        return make_fake()

    def test_negative_advance_or_sleep_preserves_both_clocks(self):
        clock = self.make()
        before = clock.state()
        for operation in (clock.advance, clock.sleep):
            with self.assertRaisesRegex(ValueError, 'normal clock advance must be nonnegative'):
                operation(-1)
            self.assertEqual(clock.state(), before)

    def test_wall_regression_is_explicit_and_never_regresses_monotonic(self):
        from datetime import timedelta
        clock = self.make()
        before = clock.monotonic()
        wall = clock.wall()
        clock.set_wall(wall - timedelta(seconds=10))
        self.assertEqual(clock.wall(), wall - timedelta(seconds=10))
        self.assertEqual(clock.monotonic(), before)
        clock.advance(3)
        self.assertEqual(clock.monotonic(), before + 3)


    def test_exact_virtual_clock_and_configured_resolutions_survive_restore(self):
        self.assertEqual(self.make().resolutions(), (0.0, 0.0))
        clock = FakeClock(wall_resolution=.015625, monotonic_resolution=.002)
        clock.sleep(.1)
        clock.new_id('EX')
        restored = FakeClock(*clock.state())
        self.assertEqual(restored.state(), clock.state())
        self.assertEqual(restored.resolutions(), (.015625, .002))
        self.assertEqual(restored.new_id('EX'), clock.new_id('EX'))
        for value in (-1, float('inf'), float('nan')):
            for key in ('wall_resolution', 'monotonic_resolution'):
                with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, "finite and nonnegative"):
                    FakeClock(**{key: value})


if __name__ == '__main__':
    unittest.main()
