"""부모 사건과 소비 대기열의 무결성: 최초 T3의 events.py 미도달 거부 경로."""
from copy import deepcopy
import unittest

from do_math.events import EventPublisher, check_sequence


class EventGuardTests(unittest.TestCase):
    def test_invalid_or_duplicate_event_ids_are_rejected_before_numbering(self):
        cases = [[{'id': value}] for value in (None, 0, '', [], {})]
        cases.append([{'id': 'EV-one'}, {'id': 'EV-one'}])
        for events in cases:
            with self.subTest(events=events):
                runtime = {'events': deepcopy(events), 'pending_events': []}
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^event IDs must be distinct$'):
                    EventPublisher.assign_sequences_in_place(runtime)
                self.assertEqual(runtime, before)

    def test_cursor_must_equal_the_complete_published_population(self):
        with self.assertRaisesRegex(ValueError, '^event cursor differs from published events$'):
            check_sequence([{'id': 'EV-one', 'event_seq': 1}], cursor=0)

    def test_pending_queue_requires_distinct_string_references(self):
        cases = [({}, 'pending_events must be a list'),
                 ([0], 'pending_events requires distinct event references'),
                 (['EV-one', 'EV-one'], 'pending_events requires distinct event references')]
        for pending, reason in cases:
            with self.subTest(pending=pending):
                runtime = {'events': [{'id': 'EV-one'}], 'pending_events': pending}
                before = deepcopy(runtime)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    EventPublisher.assign_sequences_in_place(runtime)
                self.assertEqual(runtime, before)

    def test_parent_event_cannot_disappear_even_when_pending_queue_is_empty(self):
        runtime = {'events': [], 'pending_events': []}
        with self.assertRaisesRegex(ValueError, '^published events cannot be removed$'):
            EventPublisher.assign_sequences_in_place(runtime,
                published_events={'EV-parent': {'id': 'EV-parent', 'event_seq': 1}})
        self.assertEqual(runtime, {'events': [], 'pending_events': []})
