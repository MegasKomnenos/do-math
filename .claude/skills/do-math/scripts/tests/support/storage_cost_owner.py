"""비용 측정용 실제 소유자와 외부 시계 포트. 제품 함수는 대체하지 않는다."""
from dataclasses import replace

from do_math.engine import ResearchEngine
from support.fakes.clock import FakeClock
from support.storage_git import ObservedGit


class IdleClock(FakeClock):
    """각 sleep 진입에서 관찰하고 가상 시간을 진행한다. 종료는 공개 제어로 한다."""
    def __init__(self, state):
        super().__init__(*state)
        self.on_sleep = None
        self.sleeps = []

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        if self.on_sleep is not None:
            self.on_sleep()
        super().sleep(seconds)


def observe_idle(sim):
    """같은 실제 저장 상태를 새 실제 엔진에서 열고 외부 두 포트만 계측한다."""
    clock = IdleClock(sim.clock.state())
    backend = ObservedGit(sim.ports.git_backend.objects)
    sim.clock = clock
    sim.ports = replace(sim.ports, clock=clock, git_backend=backend)
    sim.engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports,
        codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
    return clock, backend
