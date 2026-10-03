"""2-A 관찰 mode 전건의 반려·시계·상태와 중첩 입력 표를 검사한다."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from do_math.execution_profiles import OBSERVATION_MODES
from do_math.observations import ObservationTracker
from support.fakes.clock import FakeClock
from support.provider_native_inputs import NATIVE_ROWS, nested_native_rows
from support.provider_close_inputs import ingress_contracts


class ObservationContractTests(unittest.TestCase):
    def tracker(self, mode):
        workspace = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clock = FakeClock()
        return ObservationTracker('EX-own', workspace, {'observation_mode': mode,
            'research_self_checks': False, 'observation_interval_seconds': 300}, time_port=clock), clock

    def source(self, clock, offset=0):
        return {'stream': 'stdout.jsonl', 'start_offset': offset, 'end_offset': offset + 1,
                'received_at': clock.now(), 'received_monotonic': clock.monotonic()}

    def test_each_mode_rejects_foreign_execution_then_consumes_valid_event(self):
        for mode in OBSERVATION_MODES:
            with self.subTest(mode=mode):
                tracker, clock = self.tracker(mode)
                bad = {'type': 'turn.started', 'execution_id': 'EX-other'}
                rows = tracker.observe(bad, source=self.source(clock), evaluate=False)
                expected = {'kind': 'observation_input_rejected', 'execution_id': 'EX-own',
                    'reason': 'observation belongs to a different execution', 'next_owner': 'adapter',
                    'observed_at': clock.now()}
                if mode != 'deadline_only':
                    expected['followup'] = {'kind': 'operational_review_due', 'trigger': 'observation_error',
                                           'next_owner': 'operational_review'}
                self.assertEqual(rows[0], expected)
                self.assertEqual(len(rows), 2)
                self.assertEqual(json.loads(rows[1]['event_json']), bad)
                clock.advance(1)
                good = {'type': 'turn.started', 'execution_id': 'EX-own'}
                accepted = tracker.observe(good, source=self.source(clock, 1), evaluate=False)
                self.assertEqual(len(accepted), 1)
                self.assertEqual(json.loads(accepted[0]['event_json']), good)
                self.assertEqual(accepted[0]['source'], {'stream': 'stdout.jsonl', 'start_offset': 1,
                    'end_offset': 2, 'received_at': clock.now(), 'received_offset_ms': 1000})

    def test_status_and_live_matrix_preserves_terminated_facts_without_new_obligations(self):
        for mode in OBSERVATION_MODES:
            for status in ('running', 'stopping', 'ended'):
                for live in (False, True):
                    with self.subTest(mode=mode, status=status, live=live):
                        tracker, clock = self.tracker(mode)
                        tracker.set_execution_status(status)
                        event = {'type': 'turn.started'}
                        rows = tracker.observe(event, source=self.source(clock), live=live, evaluate=False)
                        if status != 'running' and live:
                            self.assertEqual(rows, [])
                        else:
                            self.assertEqual(len(rows), 1)
                            self.assertEqual(json.loads(rows[0]['event_json']), event)
                        self.assertEqual(tracker.obligations, {})
                        self.assertEqual(tracker.execution_status, status)

    def test_regressed_clock_has_exact_owner_and_does_not_consume_the_event(self):
        for mode in OBSERVATION_MODES:
            tracker, clock = self.tracker(mode)
            source = self.source(clock)
            source['received_monotonic'] -= 1
            before = deepcopy(tracker.observation_source)
            self.assertEqual(tracker.observe({'type': 'turn.started'}, source=source), [{
                'kind': 'observation_clock_error', 'execution_id': 'EX-own',
                'reason': 'monotonic clock regressed', 'next_owner': 'engine'}])
            self.assertEqual(tracker.observation_source, before)

    def test_ended_clock_cannot_restart_or_accept_unknown_status(self):
        tracker, _ = self.tracker('deadline_only')
        with self.assertRaisesRegex(ValueError, '^unsupported live execution status$'):
            tracker.set_execution_status('outside')
        tracker.set_execution_status('ended')
        for status in ('running', 'stopping'):
            with self.assertRaisesRegex(ValueError, '^ended execution cannot restart its observation clock$'):
                tracker.set_execution_status(status)
            self.assertEqual(tracker.execution_status, 'ended')

    def test_nested_malformed_table_preserves_the_outer_discriminator(self):
        seeds = {name: (seed, field) for name, seed, field, _ in NATIVE_ROWS}
        rows = list(nested_native_rows())
        self.assertEqual(len(rows), 5 * len(NATIVE_ROWS))
        for label, event, field, handler in rows:
            seed, expected_field = seeds[label.split(':', 1)[0]]
            self.assertEqual(field, expected_field)
            self.assertEqual({key: value for key, value in event.items() if key != field},
                             {key: value for key, value in seed.items() if key != field})
            self.assertTrue(handler.startswith('review_engine._record_review_observation:'))
        contracts = ingress_contracts()
        self.assertEqual({row['name'] for row in contracts},
                         set(seeds) | {'observation:' + mode for mode in OBSERVATION_MODES})
        for row in contracts:
            self.assertEqual(set(row), {'name', 'format', 'handler', 'prerequisite', 'coordinate',
                                       'rejection', 'reason', 'consumption', 'limitation'})
