"""차례를 한 번 보류하는 외부 Calls 포트. collect/pump/판정은 제품 그대로다."""
from dataclasses import replace

from support.fakes.calls import DeterministicCalls
from support.scheduling_parallel import round_robin


class DeferredCalls(DeterministicCalls):
    def __init__(self, *, before_first_turn, **options):
        super().__init__(**options)
        self.before_first_turn = before_first_turn
        self.deferred = False

    def wait(self, timeout):
        if not self.deferred and self.futures:
            self.deferred = True
            self.before_first_turn()
            # 아직 계산을 실행하지 않고 소유자에게 차례를 돌린다.
            return
        return super().wait(timeout)


class DeferredCallsPort:
    def __init__(self, clock, before_first_turn):
        self.clock, self.before_first_turn = clock, before_first_turn
        self.created = []

    def new(self, *, on_returned=None, on_observation_error=None):
        calls = DeferredCalls(clock=self.clock, choose=round_robin(), before_first_turn=self.before_first_turn,
                              on_returned=on_returned, on_observation_error=on_observation_error)
        self.created.append(calls)
        return calls


def defer_first_calculation(sim, callback):
    """run 시작 전에 새 Ports 묶음을 연결한다. 실제 엔진/러너/검증기는 유지한다."""
    port = DeferredCallsPort(sim.clock, callback)
    sim.ports = replace(sim.ports, calls=port)
    sim.engine.ports = sim.ports
    return port
