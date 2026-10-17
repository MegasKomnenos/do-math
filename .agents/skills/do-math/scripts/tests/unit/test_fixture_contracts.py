"""Scripted inputs preserve the real consumer's clock and receipt contract."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from do_math.observations import ObservationTracker
from support.fakes.clock import FakeClock
from support.observation_inputs import observation_rule, observe


class ObservationFixtureTests(unittest.TestCase):
    def test_utc_rules_and_reviews_fire_only_when_the_injected_receipt_clock_reaches_them(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for year in (2000, 2040):
            for mode in ('event_driven', 'periodic'):
                with self.subTest(year=year, mode=mode):
                    workspace = root / f'{year}-{mode}'
                    workspace.mkdir()
                    clock = FakeClock(wall=datetime(year, 1, 1, tzinfo=timezone.utc))
                    due_at = (clock.wall() + timedelta(seconds=2)).isoformat()
                    tracker = ObservationTracker('EX-fixture', workspace, {
                        'observation_mode': mode, 'research_self_checks': True,
                        'observation_rules': [observation_rule('wall_time_reached', 'clock', 'UTC', due_at)],
                        'observation_interval_seconds': 300,
                        'self_check_response_window_seconds': 5}, time_port=clock)
                    tracker.schedule_review('RECHECK', at=due_at, reason='inspect recovery', basis_ref='DISP-1')
                    self.assertEqual(observe(tracker, {'type': 'tick'}), [])
                    self.assertEqual(tracker.observation_source, {
                        'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 1,
                        'received_at': clock.now(), 'received_monotonic': 1000.0})
                    self.assertFalse(tracker.explicit_reviews['RECHECK']['fired'])
                    clock.advance(2)
                    rows = observe(tracker, {'type': 'tick'})
                    self.assertEqual([row['kind'] for row in rows], ['self_check_due', 'explicit_review_due'])
                    self.assertEqual(tracker.observation_source, {
                        'stream': 'stdout.jsonl', 'start_offset': 1, 'end_offset': 2,
                        'received_at': due_at, 'received_monotonic': 1002.0})
                    self.assertEqual(rows[0]['snapshot']['observed_at'], due_at)
                    self.assertEqual((rows[0]['opened_offset_ms'], rows[0]['deadline_offset_ms']), (2000, 7000))
                    self.assertEqual([row['observed_at'] for row in rows], [due_at, due_at])
                    self.assertEqual(rows[1]['review_id'], 'RECHECK')


if __name__ == '__main__':
    unittest.main()
