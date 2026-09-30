"""Clock-port doubles for the scheduling region's Sim tests.

- ``ScriptedClock(times, ids=None, base=None)``: a clock port whose ``now`` returns
  ``times`` in order and whose ``new_id`` returns ``ids`` in order (without ``ids``,
  ``base``'s identifiers). Every other operation is ``base``'s (default: a new
  ``FakeClock``). The legacy tests passed such a clock to the public ``control``;
  here it is the clock port of a copy of the Sim's ``Ports``.
- ``with_clock(sim, clock)``: the Sim's ports with ``clock`` as the clock port.
"""
from dataclasses import replace

from support.fakes.clock import FakeClock


class ScriptedClock:
    def __init__(self, times, ids=None, base=None):
        self._times = iter(times)
        self._ids = iter(ids) if ids is not None else None
        self.base = base or FakeClock()

    def now(self):
        return next(self._times)

    def new_id(self, prefix):
        return next(self._ids) if self._ids is not None else self.base.new_id(prefix)

    def __getattr__(self, name):
        return getattr(self.base, name)


def with_clock(sim, clock):
    return replace(sim.ports, clock=clock)
