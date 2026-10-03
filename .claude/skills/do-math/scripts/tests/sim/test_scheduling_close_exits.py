"""2-C: 시작 전 종료의 공개 run 봉투와 실행 전체 불변. 실행 성적은 별도 대기."""
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from do_math.model_policy import MODELS
from support.engine_lifecycle import applied
from support.scheduling_exit_contracts import EXIT_CASES
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()
    ready_work_sim(1)


class EarlyExitTests(unittest.TestCase):
    def assert_exit(self, sim, *, status=None, **options):
        before = deepcopy(sim.runtime['executions'])
        reservations = deepcopy(sim.runtime.get('reservations', {}))
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1, **options)
        self.assertIsInstance(answer, dict)
        if status is not None:
            self.assertEqual(answer['status'], status)
        self.assertEqual(set(sim.runtime['executions']) - set(before), set())
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime.get('reservations', {}), reservations)
        self.assertEqual(answer['active_executions'], [])
        self.assertFalse(sim.engine._executor_running)
        self.assertIsNone(sim.engine._calls)
        self.assertEqual(probe.failures, [])
        _, _, stored = sim.engine.store.load(sim.engine.head)
        self.assertEqual(stored['executions'], before)
        return answer

    def test_declared_early_exits_use_public_run(self):
        """약 4초: 일곱 공개 종료 전제를 각각 복원하고 저장 불변을 검사한다."""
        for row in EXIT_CASES:
            if row.implementation != 'early':
                continue
            with self.subTest(exit=row.name, coordinate=row.coordinate), TemporaryDirectory() as root:
                if row.name == 'initializing':
                    sim = Sim(Path(root))
                    self.assertEqual(sim.runtime['queue'], [])
                    self.assert_exit(sim, status='initializing')
                    continue
                sim = ready_work_sim(1) if row.name == 'capacity' else Sim.activated()
                if row.name == 'fence':
                    applied(sim, 'quiesce', text='정비 시작 전 종료 검사')
                    self.assertEqual(sim.runtime['maintenance_fence']['state'], 'quiescent')
                    self.assert_exit(sim)
                    self.assertEqual(sim.runtime['maintenance_fence']['state'], 'quiescent')
                elif row.name in {'pause', 'closed'}:
                    applied(sim, 'pause' if row.name == 'pause' else 'close', text='공개 종료 입력')
                    self.assert_exit(sim, status='paused' if row.name == 'pause' else 'closed')
                elif row.name == 'until_active':
                    self.assertEqual(sim.instance['lifecycle']['state'], 'active')
                    self.assert_exit(sim, until_active=True)
                elif row.name == 'clock_guard':
                    persisted = datetime.fromisoformat(sim.runtime['last_observed_utc'])
                    sim.clock.set_wall(persisted - timedelta(seconds=5))
                    answer = self.assert_exit(sim)
                    self.assertEqual(sim.runtime['availability'], {
                        'state': 'blocked', 'reason': 'clock_regression', 'next_owner': 'operator'})
                elif row.name == 'capacity':
                    applied(sim, 'configure', config={'session_limits': {'work': {
                        model: 0 for model in MODELS.values()}}})
                    self.assert_exit(sim, status='capacity_waiting')
                else:
                    self.fail('구현되지 않은 early 표 행: ' + row.name)

    def test_nonpositive_max_steps_is_rejection_not_normal_exit(self):
        sim = Sim.activated()
        before = deepcopy(sim.runtime)
        for limit in (0, -1):
            with self.subTest(limit=limit):
                with self.assertRaisesRegex(ValueError, '^max_steps must be positive$'):
                    sim.engine.run(max_steps=limit)
                self.assertEqual(sim.runtime, before)
                self.assertFalse(sim.engine._executor_running)

    def test_watch_idle_sleep_consumes_pause_without_dispatch(self):
        for initializing in (True, False):
            with self.subTest(initializing=initializing), TemporaryDirectory() as root:
                sim = Sim(Path(root)) if initializing else ready_work_sim(1)
                if not initializing:
                    applied(sim, 'configure', config={'session_limits': {'work': {
                        model: 0 for model in MODELS.values()}}})
                slept = []
                advance = sim.clock.sleep

                def sleep(seconds):
                    slept.append(seconds)
                    if len(slept) > 2:
                        self.fail('watch 대기의 공개 pause가 두 대기 안에 소비되지 않음')
                    sim.control('pause', text='watch 대기를 끝내는 사용자 입력')
                    advance(seconds)

                # 외부 시계 포트의 대기 일정만 바꾼다.
                sim.clock.sleep = sleep
                self.assert_exit(sim, status='paused', watch=True)
                self.assertEqual(slept, [0.25])
