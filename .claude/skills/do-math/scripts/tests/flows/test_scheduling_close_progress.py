"""8-A: 실제 worker 스트림과 소유 루프에서 유한 차례·관찰 상한을 검사한다."""
from concurrent.futures import Future
import json
import unittest

from do_math.execution_profiles import OBSERVATION_MODES
from do_math.parallel import ModelCalls
from support.live_finish_model import execution, install
from support.provider_probes import ObservedCalls
from support.scheduling_return_observer import OwnerProbe, assert_settled
from support.scheduling_parallel import ready_work_sim, round_robin
from support.scheduling_machine import formal_scene, hold_lean
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
    def test_owner_pass_defers_native_rows_arriving_during_observation(self):
        sim = observation_sim('deadline_only')
        sim.clock.sleep = lambda seconds: None
        before = set(sim.runtime['executions'])
        scheduled, exhausted, arrivals, errors = [], [], [], []
        probe = OwnerProbe(sim, passes=128, observations=256)

        def hook(cli, context):
            for index in range(128):
                cli.event({'type': 'item.completed', 'item': {'type': 'agent_message',
                           'id': f'during-observation-{index}', 'text': '진행'}})
            exhausted.append('stream')
            raise AssertionError('128회 관찰 전에 생산자가 정지하지 못함')

        def arrive_during_observation(arguments):
            if not scheduled and any(event.get('item', {}).get('id', '').startswith('during-observation-')
                                     for event in arguments['batch'].events):
                # The existing Calls port lets the real runner read the next
                # native row while the owner is applying its entry backlog.
                calls = sim.engine._calls
                before_rows = sum(len(f.observations) for f in calls.futures)
                for _ in range(64):
                    calls.wait(0)
                    if sum(len(f.observations) for f in calls.futures) > before_rows:
                        break
                else:
                    exhausted.append('arrival')
                after_rows = sum(len(f.observations) for f in calls.futures)
                arrivals.append((before_rows, after_rows))
                scheduled.append((probe.passes, sim.control('pause', text='관찰 적용 중 다음 관찰 도착')))
            return arguments['execution_id']

        install(sim, hook)
        with probe, ObservedCalls(observation=sim.engine._observe_running,
                                  error=sim.engine._observation_failed,
                                  capture={'observation': arrive_during_observation,
                                           'error': lambda arguments: errors.append(str(arguments['error']))}):
            answer = sim.engine.run(max_steps=1)
        assert_settled(self, sim, before, probe)
        self.assertEqual(exhausted, [])
        self.assertEqual(errors, [])
        self.assertGreaterEqual(probe.observations, 2)
        self.assertEqual(len(arrivals), 1)
        self.assertGreater(arrivals[0][1], arrivals[0][0], '새 native 묶음의 실제 도착이 필요함')
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(answer['status'], 'paused')
        requested, envelope = scheduled[0]
        self.assertEqual(sim.engine.control_result(envelope['request_id'])['effect'], 'applied')
        consumed = next(turn for turn, ids in probe.control_passes if envelope['request_id'] in ids)
        self.assertLessEqual(consumed - requested, 1)
        self.assertTrue(probe.pass_batches)
        for turn, entry, applied in probe.pass_batches:
            self.assertLessEqual(applied, entry, (turn, entry, applied))
        entry, applied = next((entry, applied) for turn, entry, applied in probe.pass_batches if turn == requested)
        self.assertEqual((entry, applied), (1, 1))

    def test_machine_completion_precedes_competing_slow_observation_backlog(self):
        # formal/trust use the same _run_machine_steps/ModelCalls collector.
        # Complete the real held Lean worker inside an observation callback,
        # after pump has selected it. Only the calls/Lean ports take turns.
        for size in (1, 64, 1024):
            with self.subTest(size=size):
                sim, action, _ = formal_scene()
                maintenance = next(a for a in sim.runtime['queue'] if a['role'] == 'maintenance')
                sim.runtime['queue'][:] = [action, maintenance]
                sim.engine._save()
                sim.ports.calls.choose = round_robin()
                before = set(sim.runtime['executions'])
                held, released, exhausted, ready, received = [], [], [], {}, []
                probe = OwnerProbe(sim, observations=4096)

                def hold():
                    from support.fakes.calls import owner_turn
                    held.append(True)
                    for _ in range(64):
                        if released:
                            return
                        owner_turn()
                    exhausted.append('lean')
                    raise AssertionError('Lean 완료 일정에 64차례 안에 도달하지 못함')

                def hook(cli, context):
                    from support.fakes.jobs import job_turn
                    for turn in range(64):
                        if any(e['role'] == 'formal_check' and e['status'] == 'ended'
                               for eid, e in sim.runtime['executions'].items() if eid not in before):
                            return
                        rows = [{'type': 'item.completed', 'item': {'type': 'agent_message',
                                 'id': f'competing-{turn}-{i}', 'text': '관찰'}} for i in range(size)]
                        cli.stdout.write(b''.join(json.dumps(row).encode() + b'\n' for row in rows))
                        cli.stdout.flush()
                        job_turn()
                    exhausted.append('stream')
                    raise AssertionError('기계 완료가 64개 스트림 차례 안에 수신되지 않음')

                def release_at_backlog(arguments):
                    calls = arguments['self']
                    if held and not released and arguments['backlog']:
                        released.append((probe.passes, arguments['backlog']))
                        # All other calls remain parked; choose the held machine
                        # at this external scheduling point, then restore fairness.
                        choose = calls.choose
                        calls.choose = lambda waiting: 0
                        try:
                            calls.wait(0)
                        finally:
                            calls.choose = choose
                    return None

                def completed(arguments):
                    future = arguments['self']
                    eid = getattr(future, 'execution_id', None)
                    if eid and sim.runtime['executions'][eid]['role'] == 'formal_check':
                        ready[eid] = (sim.clock.monotonic(), probe.passes, probe.observations)
                    return eid

                def ended(arguments):
                    eid = arguments['execution']['id']
                    if eid in ready:
                        at, turn, count = ready[eid]
                        received.append((eid, sim.clock.monotonic() - at,
                                         probe.passes - turn, probe.observations - count))
                    return eid

                def costly_observation(arguments):
                    release_at_backlog({'self': sim.engine._calls, 'backlog': len(arguments['batch'].events)})
                    sim.advance(len(arguments['batch'].events) * 0.25)
                    return arguments['execution_id']

                hold_lean(sim, hold)
                install(sim, hook)
                with probe, ObservedCalls(pump=ModelCalls.pump, completed=Future.set_result,
                        received=sim.engine._end_machine_execution, observation=sim.engine._observe_running,
                        capture={'pump': lambda arguments: None, 'completed': completed,
                                 'received': ended, 'observation': costly_observation}):
                    sim.engine.run(max_steps=2)
                added = assert_settled(self, sim, before, probe)
                self.assertEqual(exhausted, [])
                self.assertEqual(len(held), 1)
                self.assertEqual(len(released), 1)
                self.assertGreater(released[0][1], 0)
                self.assertEqual(len(ready), 1)
                self.assertEqual(len(received), 1)
                eid, seconds, turns, observations = received[0]
                self.assertIn(eid, added)
                self.assertEqual(sim.runtime['executions'][eid]['outcome'], 'output_accepted')
                self.assertLessEqual(seconds, 1.0, (size, received))
                self.assertLessEqual(turns, 1, (size, received))
                self.assertGreater(probe.observations, 0)

    def test_completed_calls_are_not_delayed_by_unrelated_slow_observation_batches(self):
        # 한 사건의 가상 비용을 0.25초로 고정한다. 허용 지연 1초는 이미
        # 시작한 작은 배치 한 개의 여유이며 N에 비례해서 늘리지 않는다.
        for size in (1, 64, 1024):
            with self.subTest(size=size):
                sim = ready_work_sim(3)
                sim.ports.calls.choose = round_robin()
                before = set(sim.runtime['executions'])
                entered, exhausted, ready, latencies = [], [], {}, []
                # The producer may emit 64 fixed-size waves before its explicit
                # failure. Joining a sole returned call's read preserves every
                # event's cost; allow that finite cleanup, while the completion
                # assertion below remains the original fixed one second.
                probe = OwnerProbe(sim, passes=256, observations=4096, seconds=32768)

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
