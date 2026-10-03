"""8-A: 실제 worker 스트림과 소유 루프에서 유한 차례·관찰 상한을 검사한다."""
from concurrent.futures import Future
import json
import unittest

from do_math.execution_profiles import OBSERVATION_MODES
from support.live_finish_model import execution, install
from support.provider_probes import ObservedCalls
from support.scheduling_return_observer import OwnerProbe, assert_settled
from support.scheduling_parallel import ready_work_sim, round_robin
from support.sim import warm_template, Sim
from support.engine_lifecycle import clear_work


def observation_sim(mode):
    """정본 producer가 해당 관찰 방식을 배정하는 역할로 실제 입력을 준비한다."""
    if mode == 'deadline_only':
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='정지 가능한 운영 호출')
        sim.engine._save()
        return sim
    return ready_work_sim(1, observation_mode=mode)


def setUpModule():
    warm_template()
    for mode in OBSERVATION_MODES:
        observation_sim(mode)


class OwnerProgressTests(unittest.TestCase):
    def test_completed_calls_are_not_delayed_by_unrelated_slow_observation_batches(self):
        # 한 사건의 가상 비용을 0.25초로 고정한다. 허용 지연 1초는 이미
        # 시작한 작은 배치 한 개의 여유이며 N에 비례해서 늘리지 않는다.
        for size in (1, 64, 1024):
            with self.subTest(size=size):
                sim = ready_work_sim(3)
                sim.ports.calls.choose = round_robin()
                before = set(sim.runtime['executions'])
                entered, exhausted, ready, latencies = [], [], {}, []
                probe = OwnerProbe(sim, passes=256, observations=4096, seconds=4096)

                def completed(arguments):
                    future = arguments['self']
                    eid = getattr(future, 'execution_id', None)
                    if eid is not None:
                        ready[eid] = (sim.clock.monotonic(), probe.observations)
                    return eid

                def received(arguments):
                    eid = arguments['prepared']['execution_id']
                    if eid in ready:
                        at, count = ready[eid]
                        latencies.append((eid, sim.clock.monotonic() - at, probe.observations - count))
                    return eid

                def costly_observation(arguments):
                    # 실제 관찰 수신 코드의 호출 시점에 시계 포트만 움직인다.
                    sim.advance(len(arguments['batch'].events) * 0.25)
                    return arguments['execution_id']

                def hook(cli, context):
                    from support.fakes.jobs import job_turn
                    eid = execution(sim, cli.workspace)['id']
                    entered.append(eid)
                    for turn in range(64):
                        if len(entered) == 3:
                            break
                        job_turn()
                    else:
                        exhausted.append('overlap')
                        raise AssertionError('세 호출이 64차례 안에 시작하지 않음')
                    if eid != entered[0]:
                        return
                    for turn in range(64):
                        if all(sim.runtime['executions'][other]['status'] == 'ended' for other in entered[1:]):
                            return
                        rows = [{'type': 'item.completed', 'item': {'type': 'agent_message',
                                 'id': f'event-{turn}-{index}', 'text': '관찰'}} for index in range(size)]
                        cli.stdout.write(b''.join(json.dumps(row).encode() + b'\n' for row in rows))
                        cli.stdout.flush()
                        job_turn()
                    exhausted.append('collection')
                    raise AssertionError('완료가 64개 스트림 차례 안에 적용되지 않음')

                install(sim, hook)
                with probe, ObservedCalls(completed=Future.set_result, received=sim.engine._receive_call,
                    observation=sim.engine._observe_running, capture={
                        'completed': completed, 'received': received, 'observation': costly_observation}):
                    sim.engine.run(max_steps=3)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(exhausted, [])
                self.assertEqual(added, set(entered))
                self.assertEqual(len(entered), 3)
                self.assertGreater(probe.observations, 0)
                self.assertCountEqual([eid for eid, _, _ in latencies], entered)
                for eid, seconds, count in latencies:
                    if eid != entered[0]:
                        self.assertLessEqual(seconds, 1.0, (size, eid, seconds, count))

    def test_unending_native_stream_yields_to_pause_with_frozen_clock(self):
        # 종료 조건 없는 생산자는 128번째 관찰까지 중단되지 않으면 실패한다.
        # clock을 전진하지 않으므로 시간 경과만으로 빠져나가는 검사는 아니다.
        for mode in OBSERVATION_MODES:
            with self.subTest(mode=mode):
                sim = observation_sim(mode)
                sim.clock.sleep = lambda seconds: None
                started_at = sim.clock.monotonic()
                before = set(sim.runtime['executions'])
                emitted, exhausted, request = [], [], []
                probe = OwnerProbe(sim, passes=128, observations=256)

                def hook(cli, context):
                    eid = execution(sim, cli.workspace)['id']
                    for index in range(128):
                        if index == 2:
                            request.append((probe.passes, sim.control('pause', text='끝없는 관찰 중 정지')))
                        emitted.append((eid, index))
                        cli.event({'type': 'item.completed', 'item': {
                            'type': 'agent_message', 'id': 'progress-' + str(index), 'text': '검사 진행'}})
                    exhausted.append(eid)
                    raise AssertionError('128회 관찰 전에 소유자가 생산자를 중단하지 못함')

                install(sim, hook)
                with probe:
                    answer = sim.engine.run(max_steps=1)
                assert_settled(self, sim, before, probe)
                self.assertEqual(exhausted, [])
                self.assertEqual(len(request), 1)
                self.assertGreaterEqual(len(emitted), 3)
                self.assertGreater(probe.observations, 0)
                self.assertEqual(answer['status'], 'paused')
                self.assertEqual(sim.clock.monotonic(), started_at)
                requested_at, envelope = request[0]
                self.assertEqual(sim.engine.control_result(envelope['request_id'])['effect'], 'applied')
                consumed_at = next(turn for turn, ids in probe.control_passes if envelope['request_id'] in ids)
                self.assertLessEqual(consumed_at - requested_at, 1)
                self.assertTrue(probe.pass_batches)
                for turn, entry, applied in probe.pass_batches:
                    self.assertLessEqual(applied, entry, (mode, turn, entry, applied))

    def test_overlapping_ai_completions_are_applied_exactly_once_in_both_orders(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                sim = ready_work_sim(2)
                choose = round_robin()
                sim.ports.calls.choose = (lambda ready: len(ready) - 1 - choose(list(reversed(ready)))) if reverse else choose
                before = set(sim.runtime['executions'])
                entered, exhausted = [], []

                def hook(cli, context):
                    from support.fakes.jobs import job_turn
                    entered.append(execution(sim, cli.workspace)['id'])
                    for _ in range(64):
                        if len(entered) == 2:
                            return
                        job_turn()
                    exhausted.append(cli.workspace)
                    raise AssertionError('두 모델 호출이 64차례 안에 겹치지 않음')

                install(sim, hook)
                with OwnerProbe(sim) as probe:
                    sim.engine.run(max_steps=2)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(exhausted, [])
                self.assertEqual(len(entered), 2)
                self.assertEqual(added, set(entered))
                collected = [eid for _, done, _, _ in probe.collections for eid in done]
                self.assertCountEqual(collected, entered)
                for eid in entered:
                    self.assertEqual(sim.runtime['executions'][eid]['outcome'], 'output_accepted')
                    receipts = [r for r in sim.runtime['control_receipts'].values()
                                if r['execution_id'] == eid and r['kind'] == 'submit_intent']
                    self.assertEqual(len(receipts), 1)
                    self.assertEqual(receipts[0]['state'], 'accepted')
