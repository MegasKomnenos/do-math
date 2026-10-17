"""Current owner functions for exit premises; the table alone is not execution evidence."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ExitCase:
    name: str
    coordinate: str
    premise: str
    implementation: str


EXIT_CASES = (
    ExitCase('fence', 'scheduler._run_parallel:fence', '시작 전 quiescent fence', 'early'),
    ExitCase('pause', 'dispatch_engine._owner_stopping:pause', '제한 복구 승인 없는 pause', 'early'),
    ExitCase('closed', 'core_engine._prepare_executor_pass/lifecycle_engine._instance_closed', '공개 close 적용, loop 준비 전 반환', 'early'),
    ExitCase('completed', 'core_engine._prepare_executor_pass/lifecycle_engine._instance_closed', '목표 완료 여정 종결, loop 준비 전 반환', 'remaining'),
    ExitCase('installation_repair', 'dispatch_engine._owner_stopping:installation_repair', '미해결 설치 수리 기록', 'repair'),
    ExitCase('recovery', 'dispatch_engine._owner_stopping:recovery', '종료 확인 안 된 복구 실행', 'remaining'),
    ExitCase('initializing', 'scheduler._run_parallel:initializing', '미승인 초기화, 빈 queue', 'early'),
    ExitCase('idle', 'scheduler._run_parallel/dispatch_engine._idle_wait_status', '활성 작업의 CLI 능력 증거 대기', 'remaining'),
    ExitCase('capacity', 'scheduler._run_parallel/dispatch_engine._idle_wait_status', '준비된 업무의 지정 모델 용량 0', 'early'),
    ExitCase('until_active', 'scheduler._run_parallel:until_active', '이미 active, dispatch 이전', 'early'),
    ExitCase('until_active_live', 'scheduler._run_parallel:until_active', 'pause 중 승인된 제한 복구 실행 → 공개 resume → active와 미완료 future', 'remaining'),
    ExitCase('clock_guard', 'core_engine._prepare_executor_pass/lifecycle_engine._clock_guard', '저장 high-water보다 과거 벽시계, loop 준비 전 반환', 'early'),
    ExitCase('watch', 'scheduler._run_parallel:watch', '대기 포트에서 공개 pause 전달', 'watch'),
    ExitCase('draining', 'scheduler._run_parallel:draining', '양수 단계 상한 뒤 실제 완료 적용', 'settlement'),
)


def assert_no_dispatch(test, sim, answer, executions, reservations, probe):
    """시작 전 종료: 공개 봉투, 기존 소유 기록, durable 저장과 owner 정리."""
    test.assertIsInstance(answer, dict)
    test.assertEqual(sim.runtime['executions'], executions)
    test.assertEqual(sim.runtime.get('reservations', {}), reservations)
    test.assertEqual(probe.failures, [])
    test.assertIsNone(sim.engine._calls)
    test.assertFalse(sim.engine._executor_running)
    _, _, stored = sim.engine.store.load(sim.engine.head)
    test.assertEqual(stored['executions'], executions)
    test.assertEqual(stored.get('reservations', {}), reservations)


WAIT_SOURCES = ('model_completion', 'observation_stream', 'control_transport', 'machine_execution')


STOP_PHASES = ('before_start', 'running', 'after_collection')
