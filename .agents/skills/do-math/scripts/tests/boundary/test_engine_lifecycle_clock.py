"""The lifecycle clock guard on this host's real clocks (``lifecycle_engine._clock_guard``; the clock port's real side).

The guard compares the UTC clock with the monotonic clock and allows each its
reported resolution. Whether the real clocks' quantization stays inside that
allowance is a property of the host, so this test runs the engine of a Sim on
the product's real clock port (``system_clock.SystemClock``) and samples it.
The legacy test replaced the engine's two clock functions with
``datetime.now`` and ``time.monotonic`` and spaced the samples with
``time.sleep(.002)``; here the samples are spaced by the monotonic clock itself.
"""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import time
import unittest

from do_math.engine import ResearchEngine
from do_math.system_clock import SystemClock
from support.engine_gates import initialized_sim


class ClockResolutionTests(unittest.TestCase):
    def test_actual_host_samples_do_not_report_quantization_as_regression(self):
        sim = initialized_sim()
        engine = ResearchEngine(sim.repository, sim.instance_id, ports=replace(sim.ports, clock=SystemClock()))
        engine.runtime['last_observed_utc'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        samples = []
        for index in range(200):
            result = engine._clock_guard()
            samples.append(result.get('observed_utc'))
            self.assertTrue(result['usable'], (index, result, samples))
            spaced = time.monotonic() + .002
            while time.monotonic() < spaced:  # two milliseconds between samples, measured, not slept
                pass
        self.assertGreater(len(set(samples)), 1, 'the samples span more than one UTC reading')


if __name__ == '__main__':
    unittest.main()
