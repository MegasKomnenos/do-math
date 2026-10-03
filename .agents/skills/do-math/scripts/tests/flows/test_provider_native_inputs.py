"""2-A 정상 계약 재현. setUp은 정상 준비를 검증하고 본문은 전체 입력의 실패를 모은다.

표시 없는 실행과 표시된 실행의 최종 소스 지문은 인계 보고서에서 대조한다.
"""
from copy import deepcopy
import json
import unittest

from do_math.observations import ObservationTracker
from do_math.execution_profiles import OBSERVATION_MODES
from support.provider_live import batch, running_execution
from support.provider_native_inputs import native_rejection_cases
from support.review_sim import opened_sim, cycle_of


def setUpModule():
    opened_sim()


class NativeInputContractTests(unittest.TestCase):
    maxDiff = None
    def setUp(self):
        self.sim = opened_sim()
        self.action = deepcopy(next(a for a in self.sim.runtime['queue'] if a['role'] == 'identity_review'))
        workspace = running_execution(self.sim, 'EX-native-defect', 'identity_review', action=self.action)
        self.tracker = ObservationTracker('EX-native-defect', workspace,
            {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=self.sim.clock)
        self.stream = workspace / 'stdout.jsonl'
        self.good = {'type': 'public_message', 'message': {'role': 'assistant', 'content': '정상'}}
        self.first = batch(self.sim, [self.good], self.stream, terminated=True)
        self.stream.write_bytes(b''.join(self.first.rows))
        self.sim.engine._observe_running('EX-native-defect', self.tracker, self.first)
        self.assertEqual([row['content'] for row in cycle_of(self.sim)['turns'][self.action['slot']]], ['정상'])
        self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)

        self.rejection_scenes = []
        if self._testMethodName == 'test_malformed_native_message_is_rejected_once_and_next_message_is_stored':
            for index, (label, event) in enumerate(native_rejection_cases()):
                eid = 'EX-native-case-' + str(index)
                workspace = running_execution(self.sim, eid, 'identity_review', action=self.action)
                tracker = ObservationTracker(eid, workspace,
                    {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=self.sim.clock)
                stream = workspace / 'stdout.jsonl'
                first = batch(self.sim, [self.good], stream, terminated=True)
                first.stream_path.write_bytes(b''.join(first.rows))
                self.sim.engine._observe_running(eid, tracker, first)
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                self.rejection_scenes.append((label, event, eid, tracker, stream, first))

        self.collision_scenes = []
        if self._testMethodName == 'test_successful_native_batch_redelivery_does_not_duplicate_or_fail':
            for index, (left, right) in enumerate((('먼저', '나중'), ('나중', '먼저'))):
                eid = 'EX-native-collision-' + str(index)
                workspace = running_execution(self.sim, eid, 'identity_review', action=self.action)
                tracker = ObservationTracker(eid, workspace,
                    {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=self.sim.clock)
                stream = workspace / 'stdout.jsonl'
                first = batch(self.sim, [{'type': 'public_message', 'message': {'role': 'assistant', 'content': left}}],
                    stream, terminated=True)
                first.stream_path.write_bytes(b''.join(first.rows))
                self.sim.engine._observe_running(eid, tracker, first)
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                self.collision_scenes.append((eid, tracker, stream, first, left, right))

        self.observation_replays = []
        if self._testMethodName == 'test_successful_native_batch_redelivery_does_not_duplicate_or_fail':
            for mode in OBSERVATION_MODES:
                eid = 'EX-replay-' + mode.replace('_', '-')
                workspace = running_execution(self.sim, eid, 'research_work')
                tracker = ObservationTracker(eid, workspace,
                    {'observation_mode': mode, 'research_self_checks': False}, time_port=self.sim.clock)
                first = batch(self.sim, [{'type': 'turn.started'}], workspace / 'stdout.jsonl', terminated=True)
                first.stream_path.write_bytes(b''.join(first.rows))
                self.sim.engine._observe_running(eid, tracker, first)
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                self.observation_replays.append((eid, tracker, first))

        self.reversed_scene = None
        if self._testMethodName == 'test_successful_native_batch_redelivery_does_not_duplicate_or_fail':
            eid = 'EX-native-reversed'
            workspace = running_execution(self.sim, eid, 'identity_review', action=self.action)
            tracker = ObservationTracker(eid, workspace,
                {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=self.sim.clock)
            stream = workspace / 'stdout.jsonl'
            events = [{'type': 'public_message', 'message': {'role': 'assistant', 'content': content}}
                      for content in ('지연된 첫 행', '먼저 받은 둘째 행', '정상 셋째 행')]
            rows = [json.dumps(event).encode('utf-8') + b'\n' for event in events]
            stream.write_bytes(b''.join(rows))
            first = batch(self.sim, [events[1]], stream, rows=[rows[1]], start=len(rows[0]), first_row=1, terminated=True)
            self.sim.engine._observe_running(eid, tracker, first)
            self.assertEqual(cycle_of(self.sim)['turns'][self.action['slot']][-1]['content'], '먼저 받은 둘째 행')
            self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
            self.reversed_scene = (eid, tracker, stream, events, rows)

    def test_malformed_native_message_is_rejected_once_and_next_message_is_stored(self):
        """2-A 정상 반려 계약. 전건 실행 뒤 실패를 합쳐 첫 행이 나머지를 가리지 않는다."""
        failures = []
        for label, bad, eid, tracker, stream, first in self.rejection_scenes:
            incoming = batch(self.sim, [bad, self.good], stream,
                start=first.end_offset, first_row=1, terminated=True)
            stream.write_bytes(b''.join(first.rows + incoming.rows))
            before = set(self.sim.runtime['observation_facts'])
            turns = deepcopy(cycle_of(self.sim)['turns'][self.action['slot']])
            try:
                self.sim.engine._observe_running(eid, tracker, incoming)
                added = [json.loads(value['event_json']) for key, value in self.sim.runtime['observation_facts'].items()
                         if key not in before]
                rejected = [row for row in added if row.get('kind') == 'observation_input_rejected']
                self.assertEqual(len(rejected), 1, label)
                self.assertEqual(rejected[0]['execution_id'], eid)
                self.assertEqual(rejected[0]['next_owner'], 'adapter')
                self.assertIsInstance(rejected[0]['reason'], str)
                self.assertTrue(rejected[0]['reason'])
                if label.startswith('public:'):
                    self.assertEqual(rejected[0]['reason'], 'invalid normalized public message')
                messages = cycle_of(self.sim)['turns'][self.action['slot']]
                self.assertEqual(messages[:-1], turns)
                self.assertEqual(messages[-1]['content'], '정상')
                self.assertEqual(messages[-1]['source']['event_index'], 2)
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                state, head = deepcopy(self.sim.runtime), self.sim.engine.head
                self.sim.advance(1)
                self.sim.engine._observe_running(eid, tracker, batch(self.sim, [], stream,
                    start=incoming.end_offset, first_row=3, terminated=True))
                self.assertEqual(self.sim.runtime, state)
                self.assertEqual(self.sim.engine.head, head)
            except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
                failures.append((label, type(error).__name__, str(error)))
        self.assertEqual(failures, [], '모든 원 외곽에서 반려 1회와 같은 batch 후속 처리가 필요하다')

    def test_successful_native_batch_redelivery_does_not_duplicate_or_fail(self):
        failures = []
        state, head = deepcopy(self.sim.runtime), self.sim.engine.head
        try:
            self.sim.engine._observe_running('EX-native-defect', self.tracker, self.first)
            self.assertEqual(self.sim.runtime, state)
            self.assertEqual(self.sim.engine.head, head)
            self.assertEqual(self.sim.engine.store.load(head)[2], state)
        except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
            failures.append(('redelivery', type(error).__name__, str(error)))
        for eid, tracker, incoming in self.observation_replays:
            state, head = deepcopy(self.sim.runtime), self.sim.engine.head
            try:
                self.sim.engine._observe_running(eid, tracker, incoming)
                self.assertTrue(self.sim.runtime == state, '같은 stream 좌표가 observation fact를 중복 생성했다')
                self.assertEqual(self.sim.engine.head, head)
                self.assertEqual(self.sim.engine.store.load(head)[2], state)
            except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
                failures.append((eid, type(error).__name__, str(error)))
        for eid, tracker, stream, first, left, right in self.collision_scenes:
            bad = {'type': 'public_message', 'message': {'role': 'assistant', 'content': right}}
            incoming = batch(self.sim, [bad, self.good], stream, terminated=True)
            stream.write_bytes(b''.join(incoming.rows))
            before = set(self.sim.runtime['observation_facts'])
            turns = deepcopy(cycle_of(self.sim)['turns'][self.action['slot']])
            try:
                self.sim.engine._observe_running(eid, tracker, incoming)
                added = [json.loads(row['event_json']) for key, row in self.sim.runtime['observation_facts'].items() if key not in before]
                self.assertEqual([row['reason'] for row in added if row.get('kind') == 'observation_input_rejected'],
                                 ['transcript message ID changed content'])
                messages = cycle_of(self.sim)['turns'][self.action['slot']]
                self.assertEqual(messages[:-1], turns)
                self.assertEqual(messages[-1]['content'], '정상')
                self.assertEqual(messages[-1]['source']['event_index'], 1)
                self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
                state, head = deepcopy(self.sim.runtime), self.sim.engine.head
                self.sim.engine._observe_running(eid, tracker, batch(self.sim, [], stream,
                    start=incoming.end_offset, first_row=2, terminated=True))
                self.assertEqual(self.sim.runtime, state)
                self.assertEqual(self.sim.engine.head, head)
            except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
                failures.append((left + '→' + right, type(error).__name__, str(error)))
        eid, tracker, stream, events, rows = self.reversed_scene
        turns = deepcopy(cycle_of(self.sim)['turns'][self.action['slot']])
        before = set(self.sim.runtime['observation_facts'])
        try:
            delayed = batch(self.sim, [events[0]], stream, rows=[rows[0]], first_row=0, terminated=True)
            self.sim.engine._observe_running(eid, tracker, delayed)
            added = [json.loads(row['event_json']) for key, row in self.sim.runtime['observation_facts'].items() if key not in before]
            self.assertEqual([row['reason'] for row in added if row.get('kind') == 'observation_input_rejected'],
                             ['observed public review event arrived out of order'])
            following = batch(self.sim, [events[2]], stream, rows=[rows[2]],
                start=len(rows[0]) + len(rows[1]), first_row=2, terminated=True)
            self.sim.engine._observe_running(eid, tracker, following)
            messages = cycle_of(self.sim)['turns'][self.action['slot']]
            self.assertEqual(messages[:-1], turns)
            self.assertEqual(messages[-1]['content'], '정상 셋째 행')
            self.assertEqual(messages[-1]['source']['event_index'], 2)
            self.assertEqual(self.sim.engine.store.load(self.sim.engine.head)[2], self.sim.runtime)
            state, head = deepcopy(self.sim.runtime), self.sim.engine.head
            self.sim.engine._observe_running(eid, tracker, batch(self.sim, [], stream,
                start=following.end_offset, first_row=3, terminated=True))
            self.assertEqual(self.sim.runtime, state)
            self.assertEqual(self.sim.engine.head, head)
            earlier = batch(self.sim, [events[1]], stream, rows=[rows[1]],
                start=len(rows[0]), first_row=1, terminated=True)
            self.sim.engine._observe_running(eid, tracker, earlier)
            self.assertTrue(self.sim.runtime == state, 'already consumed earlier rows changed the stored stream cursor')
            self.assertEqual(self.sim.engine.head, head)
        except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
            failures.append(('reversed-coordinate', type(error).__name__, str(error)))
        self.assertEqual(failures, [], '재전달 멱등성과 충돌 양 순서의 반려 후 진행')
