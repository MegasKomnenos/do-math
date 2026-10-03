"""공개 검토 종결·개정 뒤 지연 native 입력이 기존 transcript를 바꾸지 않아야 한다."""
from copy import deepcopy
import json
from pathlib import Path
import unittest


from do_math import knowledge
from do_math.observations import ObservationTracker
from support.engine_lifecycle import applied
from support.provider_live import batch, running_execution
from support.review_sim import reviewed_sim, opened_sim, cycle_of, theorem_id, THEOREM


def setUpModule():
    reviewed_sim()
    opened_sim()


class NativeTargetTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.scenes = []
        # 두 템플릿은 서로 다른 절대 경로다. 정상 준비는 예상 실패 본문 밖에서 한다.
        for kind, sim in (('closed', reviewed_sim()), ('superseded', opened_sim())):
            cycle = cycle_of(sim)
            if kind == 'closed':
                self.assertEqual(cycle['decision'], 'match')
                execution = next(row for row in sim.runtime['executions'].values()
                    if row.get('role') == 'identity_review' and row['action'].get('review_cycle_id') == cycle['id'])
                self.assertEqual(execution['status'], 'ended')
                eid = execution['id']
                workspace = Path(sim.instance['workspace']) / 'runs' / eid / 'workspace'
            else:
                action = next(row for row in sim.runtime['queue'] if row['role'] == 'identity_review')
                eid = 'EX-old-proposal'
                workspace = running_execution(sim, eid, 'identity_review', action=action)
                kid = theorem_id(sim)
                roots = knowledge.revision_roots(sim.instance, kid)
                applied(sim, 'knowledge', config={'operation': 'revise', 'id': kid,
                    'changes': {'explanation': THEOREM['explanation'] + ' 새 설명'},
                    'declared_impact': knowledge.plan_impact(sim.instance, sim.runtime, roots, [])['computed_impact'],
                    'reason': '관찰 입구의 현재성 검산'})
                self.assertIsNotNone(sim.engine._obsolete_review_reason(action))
            tracker = ObservationTracker(eid, workspace,
                {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
            stream = workspace.parent / 'evidence' / 'stdout.jsonl'
            stream.parent.mkdir(exist_ok=True)
            other_ws = running_execution(sim, 'EX-next-' + kind, 'research_work')
            other = ObservationTracker('EX-next-' + kind, other_ws,
                {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
            self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
            self.scenes.append((kind, sim, eid, tracker, stream, cycle['id'], other, other_ws))

    def test_obsolete_review_input_is_rejected_and_another_execution_still_progresses(self):
        failures = []
        for kind, sim, eid, tracker, stream, cid, other, other_ws in self.scenes:
            before = deepcopy(sim.runtime['review_cycles'][cid])
            fact_ids = set(sim.runtime['observation_facts'])
            facts = deepcopy(sim.runtime['observation_facts'])
            event = {'type': 'public_message', 'message': {'role': 'assistant', 'content': '늦은 문장'}}
            prior = stream.read_bytes() if stream.exists() else b''
            first_row = len([row for row in prior.splitlines() if row.strip()])
            incoming = batch(sim, [event], stream, start=len(prior), first_row=first_row, terminated=True)
            stream.write_bytes(prior + b''.join(incoming.rows))
            try:
                sim.engine._observe_running(eid, tracker, incoming)
                self.assertEqual({key: sim.runtime['observation_facts'][key] for key in facts}, facts)
                self.assertTrue(sim.runtime['review_cycles'][cid] == before,
                    '지연 입력이 바꾼 필드: ' + repr([key for key in before if sim.runtime['review_cycles'][cid].get(key) != before[key]]))
                added = [json.loads(row['event_json']) for key, row in sim.runtime['observation_facts'].items() if key not in fact_ids]
                rejected = [row for row in added if row.get('kind') == 'observation_input_rejected']
                self.assertEqual(len(rejected), 1)
                self.assertTrue(rejected[0]['reason'])
                good = {'type': 'turn.started', 'execution_id': other.execution_id}
                sim.engine._observe_running(other.execution_id, other, batch(sim, [good], other_ws / 'stdout.jsonl'))
                self.assertEqual([json.loads(row['event_json']) for row in sim.runtime['observation_facts'].values()
                    if row['execution_id'] == other.execution_id], [good])
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
                state, head = deepcopy(sim.runtime), sim.engine.head
                sim.engine._observe_running(eid, tracker, batch(sim, [], stream,
                    start=incoming.end_offset, first_row=first_row + 1, terminated=True))
                self.assertEqual(sim.runtime, state)
                self.assertEqual(sim.engine.head, head)
                fresh = ObservationTracker(eid, tracker.workspace,
                    {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
                sim.engine._observe_running(eid, fresh, incoming)
                self.assertEqual(sim.runtime, state)
                self.assertEqual(sim.engine.head, head)
            except (AttributeError, TypeError, KeyError, ValueError, AssertionError) as error:
                failures.append((kind, type(error).__name__, str(error)))
        self.assertEqual(failures, [], '종결·개정된 검토 입력은 transcript를 바꾸지 않고 소비되어야 한다')
