"""Observe the actual owner, calls collector and durable termination settlement."""
import inspect
import sys
from do_math.engine import ResearchEngine
from do_math.parallel import ModelCalls
from support.monitoring_slots import reserve_tool

class SchedulingBoundExceeded(BaseException):
    """제품의 Exception 처리로 삼켜지지 않는 시험 탐지 상한."""



class OwnerProbe:
    """소유 바퀴·pump·완료 회수를 관찰하고 정지한 시계에서도 유한 실패한다.

    256회는 단일/소수 실행 시나리오의 8개 배선 단계에 32회 여유를 준
    탐지 한도다. 4096 관찰과 가상 4096초는 성공 기준이 아닌 안전 한도다.
    collect 진입의 done 전건과 반환 때 제거 전건을 별도로 기록한다.
    """
    def __init__(self, sim, *, passes=256, observations=4096, seconds=4096):
        self.sim = sim
        self.limits = passes, observations, seconds
        self.passes = self.observations = 0
        self.collections, self.pumps, self.failures = [], [], []
        self.pass_batches = []
        self.control_passes = []
        self._pass_entry = None
        self._collect_stack, self._pump_stack = [], []
        self.active = False

    def _check(self):
        elapsed = self.sim.clock.monotonic() - self.started
        if (self.passes > self.limits[0] or self.observations > self.limits[1]
                or elapsed > self.limits[2]):
            detail = (self.passes, self.observations, elapsed)
            self.failures.append(detail)
            self.active = False
            raise SchedulingBoundExceeded('스케줄링 유한 탐지 상한 초과: ' + repr(detail))

    def __enter__(self):
        self.started = self.sim.clock.monotonic()
        self.tool = reserve_tool('scheduling close owner')
        self.codes = {
            inspect.unwrap(ResearchEngine._run_parallel).__code__: 'loop',
            inspect.unwrap(ResearchEngine._settle_stops).__code__: 'pass',
            inspect.unwrap(ResearchEngine._controls).__code__: 'controls',
            inspect.unwrap(ResearchEngine._observe_running).__code__: 'observation',
            ModelCalls.collect.__code__: 'collect',
            ModelCalls.pump.__code__: 'pump',
        }

        def started(code, offset):
            name = self.codes[code]
            arguments = sys._getframe(1).f_locals
            obj = arguments['self']
            if name == 'loop' and obj is self.sim.engine:
                self.active = True
            if not self.active:
                return
            if name == 'pass' and obj is self.sim.engine and arguments['clock'] is False:
                if self._pass_entry is not None:
                    before, queued = self._pass_entry
                    self.pass_batches.append((self.passes, queued, self.observations - before))
                self.passes += 1
                self._pass_entry = (self.observations,
                                    sum(len(f.observations) for f in obj._calls.futures))
            elif name == 'observation' and obj is self.sim.engine:
                self.observations += 1
            elif name == 'collect':
                self._collect_stack.append((obj, tuple(f for f in obj.futures if f.done())))
            elif name == 'pump':
                self._pump_stack.append((self.passes, self.observations,
                                         sum(len(f.observations) for f in obj.futures)))
            self._check()

        def returned(code, offset, value):
            if not self.active:
                return
            name = self.codes[code]
            if name == 'controls':
                self.control_passes.append((self.passes, tuple(self.sim.runtime['processed_controls'])))
            elif name == 'collect' and self._collect_stack:
                calls, done = self._collect_stack.pop()
                self.collections.append((self.passes, tuple(f.execution_id for f in done),
                                         tuple(f.execution_id for f in done if f in calls.futures), value))
            elif name == 'pump' and self._pump_stack:
                turn, before, queued = self._pump_stack.pop()
                self.pumps.append((turn, queued, self.observations - before))
            elif name == 'loop':
                if self._pass_entry is not None:
                    before, queued = self._pass_entry
                    self.pass_batches.append((self.passes, queued, self.observations - before))
                self.active = False

        monitoring = sys.monitoring
        monitoring.register_callback(self.tool, monitoring.events.PY_START, started)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, returned)
        for code in self.codes:
            monitoring.set_local_events(self.tool, code, monitoring.events.PY_START | monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *error):
        monitoring = sys.monitoring
        for code in self.codes:
            monitoring.set_local_events(self.tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_START, None)
        monitoring.register_callback(self.tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(self.tool)
        return False



def assert_settled(test, sim, before, probe):
    """future 수 외에 실제 저장·종료 장벽·예약·완료 증거를 전건 확인한다."""
    test.assertEqual(probe.failures, [])
    test.assertGreater(probe.passes, 0)
    test.assertEqual([pending for _, _, pending, _ in probe.collections if pending], [])
    added = set(sim.runtime['executions']) - before
    test.assertTrue(added)
    _, _, stored = sim.engine.store.load(sim.engine.head)
    test.assertEqual(stored['executions'], sim.runtime['executions'])
    for eid in sorted(added):
        row = stored['executions'][eid]
        test.assertEqual(row['status'], 'ended', eid)
        test.assertEqual(row['capacity']['local_termination'], 'confirmed', eid)
        test.assertTrue(row['owner_activity_id'])
        test.assertEqual(row['launch_ticket']['execution_id'], eid)
        for rid in row['capacity']['reservation_ids']:
            reservation = stored['reservations'][rid]
            test.assertEqual((reservation['state'], reservation['returned'], reservation['confirmed_consumed']),
                             ('settled', reservation['reserved'], 0), rid)
            test.assertTrue(reservation['evidence_refs'], rid)
        # 반환값이 실제 저장 생산물까지 도달했음을 확인한다.
        test.assertTrue(row.get('result_ref') or row.get('raw_result_ref'), eid)
        for key in ('result_ref', 'raw_result_ref'):
            if row.get(key):
                test.assertTrue(sim.engine.store.read(row[key], sim.engine.head), (eid, key))
    test.assertIsNone(sim.engine._calls)
    test.assertFalse(sim.engine._executor_running)
    return added
