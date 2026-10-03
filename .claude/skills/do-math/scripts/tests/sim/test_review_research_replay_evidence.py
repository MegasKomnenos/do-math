"""정본 정상 조사 완료·예산 종료의 봉인 증거를 한 필드씩 변조한다.

각 입력의 첫 시험이 공개 경로의 cold 빌드 비용을 치른다(공유 부하에서
세 빌드 약 86초). 미리 복원하고 버리지 않아 실제 소비자만 같은 root를
복원한다. 시험별 cold 비용과 모듈 전체 비용을 구별해 비교한다.
"""
from copy import deepcopy
import unittest

from do_math import review_cycle as rc
from support.review_replay_inputs import replay_sim


class ResearchReplayEvidenceTests(unittest.TestCase):
    def prepared(self, *, closure=False):
        sim = replay_sim(closure=closure)
        return sim, deepcopy(next(iter(sim.runtime['review_cycles'].values())))

    def replay(self, sim, cycle, *, instance=True):
        return rc.validate_sealed_review(cycle, sim.runtime, instance=sim.instance if instance else None,
            read_artifact=sim.engine.store.read, git_dir=sim.engine.store.git_dir,
            clock=sim.clock, at=sim.clock.now())

    def assert_rejected(self, sim, cycle, reason, *, instance=True):
        before = deepcopy((cycle, sim.instance, sim.runtime))
        head = sim.engine.head
        with self.assertRaisesRegex(ValueError, reason):
            self.replay(sim, cycle, instance=instance)
        self.assertEqual((cycle, sim.instance, sim.runtime), before)
        self.assertEqual(sim.engine.head, head)

    def test_real_research_replay_preserves_exact_request_and_result(self):
        sim, cycle = self.prepared()
        before = deepcopy(cycle)
        result = self.replay(sim, cycle)
        self.assertEqual(result['research'], cycle['research'])
        self.assertEqual(result['decision'], 'match')
        self.assertEqual(cycle, before)
        request = next(iter(cycle['research'].values()))
        self.assertEqual(request['status'], 'answered')
        self.assertEqual(request['result']['execution_status'], 'completed')
        self.assertNotEqual(request['requested_by'], request['result']['execution_id'])

    def test_same_slot_context_origin_is_allowed_without_importing_peer_results(self):
        sim, cycle = self.prepared()
        request = next(iter(cycle['research'].values()))
        final = cycle['results'][rc.slot_key(request['action'])]
        runtime = deepcopy(sim.runtime)
        runtime['executions'][final['execution_id']]['context_origin'] = [request['requested_by']]
        before = deepcopy(runtime)
        self.assertIsNone(rc.validate_review_independence(cycle, runtime, final['execution_id'], final['action']))
        self.assertEqual(runtime, before)
        self.assertEqual(runtime['executions'][request['requested_by']]['action']['slot'], final['action']['slot'])

    def test_replay_rejects_missing_provisional_response(self):
        sim, cycle = self.prepared()
        request = next(iter(cycle['research'].values()))
        messages = cycle['turns'][request['action']['slot']]
        index = next(i for i, m in enumerate(messages) if m.get('message_id') == request['requested_by'] + ':assistant')
        messages[index]['content'] = {}
        self.assert_rejected(sim, cycle, 'supplemental request has no preserved provisional response')

    def test_replay_rejects_each_changed_fixed_request_coordinate(self):
        sim, original = self.prepared()
        rid = next(iter(original['research']))
        for field, value in [('question', '다른 질문'), ('proposal_digest', '0' * 64), ('source_refs', ['proposal:other'])]:
            cycle = deepcopy(original)
            cycle['research'][rid][field] = value
            with self.subTest(field=field):
                self.assert_rejected(sim, cycle, 'fixed supplemental request changed')

    def test_replay_rejects_changed_request_digest(self):
        sim, cycle = self.prepared()
        next(iter(cycle['research'].values()))['request_digest'] = '0' * 64
        self.assert_rejected(sim, cycle, 'supplemental request digest changed')

    def test_replay_rejects_missing_research_result(self):
        sim, cycle = self.prepared()
        next(iter(cycle['research'].values()))['result'] = None
        self.assert_rejected(sim, cycle, 'supplemental investigation is incomplete')

    def test_normal_defer_history_consumes_the_fixed_request_once(self):
        sim, cycle = self.prepared()
        events = [row for row in cycle['history'] if row.get('event') == 'review_deferred_for_research']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['request_ids'], list(cycle['research']))
        result = self.replay(sim, cycle)
        self.assertEqual(result['research'], cycle['research'])
        self.assertEqual(len(result['research']), 1)
        self.assertEqual(len([h for h in result['history'] if h.get('event') == 'review_deferred_for_research']), 1)

    def test_artifact_sources_replay_from_actual_preserved_bytes(self):
        sim, cycle = self.prepared()
        request = next(iter(cycle['research'].values()))
        artifacts = [row for row in request['source_records'] if 'artifact_ref' in row]
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(sim.engine.store.read(artifacts[0]['artifact_ref'], artifacts[0]['snapshot']),
                         '공급된 정확 원천: 자연수의 덧셈 항등식.'.encode('utf-8'))
        result = self.replay(sim, cycle)
        self.assertEqual(result['research'][request['id']]['source_records'], request['source_records'])
        # 원천 바이트는 위에서 실제 저장소로 대조했다. 순수 재생 호출도 같은 기록을 재구성한다.
        pure = rc.validate_sealed_review(cycle, sim.runtime, instance=sim.instance,
            clock=sim.clock, at=sim.clock.now())
        self.assertEqual(pure['research'], result['research'])

    def test_closure_replay_requires_actual_accounting_and_governing_configuration(self):
        sim, original = self.prepared(closure=True)
        closure = next(h for h in original['history'] if h.get('event') == 'investigation_limit_closed')
        self.assertFalse(closure['budget_available'])
        self.assertEqual(self.replay(sim, original)['decision'], 'unresolved')
        cycle = deepcopy(original)
        cycle['execution_accounting']['executions_used'].remove(closure['execution_id'])
        self.assert_rejected(sim, cycle, 'review budget closure has no actual execution accounting')
        self.assert_rejected(sim, original, 'review closure replay requires its governing configuration', instance=False)

    def test_closure_rejects_duplicate_closure_evidence(self):
        sim, cycle = self.prepared(closure=True)
        closure = next(h for h in cycle['history'] if h.get('event') == 'investigation_limit_closed')
        cycle['history'].append(deepcopy(closure))
        self.assert_rejected(sim, cycle, 'review has conflicting closure evidence')

    def test_closure_rejects_missing_actual_provisional_response(self):
        sim, cycle = self.prepared(closure=True)
        closure = next(h for h in cycle['history'] if h.get('event') == 'investigation_limit_closed')
        message = next(m for m in cycle['turns'][closure['action']['slot']] if m.get('message_id') == closure['execution_id'] + ':assistant')
        message['content'] = {}
        self.assert_rejected(sim, cycle, 'review closure lacks its actual provisional response')

    def test_closure_rejects_falsely_claimed_exhaustion(self):
        sim, cycle = self.prepared(closure=True)
        cycle['activity_execution_limit'] += 100
        self.assert_rejected(sim, cycle, 'review budget closure is not exhausted')

    def test_budget_only_closure_cannot_claim_resources_were_available(self):
        sim = replay_sim(closure=True, budget_only=True)
        cycle = deepcopy(next(iter(sim.runtime['review_cycles'].values())))
        closure = next(h for h in cycle['history'] if h.get('event') == 'investigation_limit_closed')
        self.assertEqual(closure['limit'], 3)
        self.assertFalse(closure['budget_available'])
        self.assertEqual(len(cycle['research']), 1)
        self.assertEqual(self.replay(sim, cycle)['decision'], 'unresolved')
        closure['budget_available'] = True
        self.assert_rejected(sim, cycle, 'review closure is not justified by its limits')
