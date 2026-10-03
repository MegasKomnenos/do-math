"""실제 owner/Repository에서 mode별 반려와 후속 정상 행의 소비를 검산한다.

파생 시작 상태를 복원하며, 전체 시나리오 비용은 슬롯 수신 후 측정한다.
source는 runner 소유 좌표이고 사건 JSON의 source와 구분한다.
"""
from copy import deepcopy
import json
import unittest

from do_math.execution_profiles import OBSERVATION_MODES
from do_math.observations import ObservationTracker
from support.provider_live import batch, running_execution
from support.sim import Sim, warm_template

setUpModule = warm_template


class ObservationOwnerContractTests(unittest.TestCase):
    def test_every_mode_stores_rejection_then_good_row_and_idle_pass_is_unchanged(self):
        for mode in OBSERVATION_MODES:
            with self.subTest(mode=mode):
                sim = Sim.activated()
                execution_id = 'EX-provider-close'
                workspace = running_execution(sim, execution_id, 'research_work')
                tracker = ObservationTracker(execution_id, workspace, {'observation_mode': mode,
                    'research_self_checks': False, 'observation_interval_seconds': 300}, time_port=sim.clock)
                stream = workspace.parent / 'evidence/stdout.jsonl'
                stream.parent.mkdir(exist_ok=True)
                events = [{'type': 'turn.started', 'execution_id': 'EX-other'},
                          {'type': 'turn.started', 'execution_id': execution_id}]
                incoming = batch(sim, events, stream, terminated=True)
                stream.write_bytes(b''.join(incoming.rows))
                before = set(sim.runtime.get('observation_facts', {}))
                queue = deepcopy(sim.runtime['queue'])
                sim.engine._observe_running(execution_id, tracker, incoming)
                added = [value for key, value in sim.runtime['observation_facts'].items() if key not in before]
                self.assertEqual(len(added), 3)
                payloads = [json.loads(row['event_json']) for row in added]
                rejected = [value for value in payloads if value.get('kind') == 'observation_input_rejected']
                expected = {'kind': 'observation_input_rejected', 'execution_id': execution_id,
                    'reason': 'observation belongs to a different execution', 'next_owner': 'adapter',
                    'observed_at': sim.clock.now()}
                if mode != 'deadline_only':
                    expected['followup'] = {'kind': 'operational_review_due', 'trigger': 'observation_error',
                                           'next_owner': 'operational_review'}
                self.assertEqual(rejected, [expected])
                self.assertEqual([value for value in payloads if 'type' in value], events)
                native = [row for row in added if 'type' in json.loads(row['event_json'])]
                self.assertEqual([row['source'] for row in native], [
                    {'stream': 'stdout.jsonl', 'start_offset': start, 'end_offset': end,
                     'received_at': incoming.received_at, 'received_offset_ms': 0}
                    for start, end in incoming.offsets])
                self.assertEqual(sim.runtime['queue'], queue)
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
                state, head = deepcopy(sim.runtime), sim.engine.head
                sim.advance(1)
                sim.engine._observe_running(execution_id, tracker, batch(sim, [], stream,
                    start=incoming.end_offset, first_row=2, terminated=True))
                self.assertEqual(sim.runtime, state)
                self.assertEqual(sim.engine.head, head)
                self.assertEqual(sim.engine.store.load(head)[2], state)
