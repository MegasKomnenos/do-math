"""Deterministic calls port: no threads; the owner decides when each call runs.

``DeterministicCalls`` is the product ``ModelCalls`` with its two thread steps
replaced, so stop judgment, observation queues and collection are the
product's own code. A started call waits in ``pending``; each ``wait`` runs one
pending call to completion on the owner thread (the one ``choose`` picks, by
default the earliest), and with nothing pending advances the clock by the
timeout. A start callback therefore runs at once on the owner thread.
"""
from do_math.parallel import ModelCalls


class DeterministicCalls(ModelCalls):
    def __init__(self, *, clock=None, choose=None, **callbacks):
        super().__init__(**callbacks)
        self.pending, self.clock = [], clock
        self.choose = choose or (lambda pending: 0)

    def _spawn(self, run):
        self.pending.append(run)

    def _owner_call(self, function, args):
        if self.stopping:
            raise RuntimeError("executor is shutting down")
        return function(*args)

    def wait(self, timeout):
        if self.pending:
            self.pending.pop(self.choose(self.pending))()
        elif self.clock is not None:
            self.clock.sleep(timeout)
        self.wake.clear()

    def close(self):
        self.pending.clear()
        super().close()


class DeterministicCallsPort:
    def __init__(self, clock=None):
        self.clock = clock

    def new(self, *, on_returned=None, on_observation_error=None):
        return DeterministicCalls(clock=self.clock, on_returned=on_returned, on_observation_error=on_observation_error)


def make_fake(clock=None):
    return DeterministicCallsPort(clock)
