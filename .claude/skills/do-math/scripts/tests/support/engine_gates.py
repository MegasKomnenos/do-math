"""Start states and clocks for the engine region's lifecycle gate tests on the Sim.

- ``initialized_sim()``: a restored copy of one publicly initialized instance
  (``initialize`` only, no activation) that this process built once.
- ``GateClock``: the Sim's fake clock with one more move: ``move_monotonic``
  moves the monotonic clock alone (``FakeClock.set_wall`` moves the wall alone,
  ``advance`` moves both), so a test sets the two clocks the lifecycle clock
  guard compares independently.
- ``gate_engine(sim)``: the Sim rewired onto a ``GateClock`` that continues from
  its clock, with a new engine (a new process) on the same repository; returns
  the clock. The legacy tests replaced the engine's ``lifecycle_clock`` and
  ``lifecycle_monotonic`` on an engine built without ``__init__``; here both
  come from the clock port, as in the product.
"""
from dataclasses import replace

from do_math.engine import ResearchEngine
from support.fakes.clock import FakeClock
from support.sim import Sim, built


def initialized_sim():
    """A restored copy of one publicly initialized, not yet active instance."""
    return built('engine-initialized', lambda root, shared: Sim(root, shared=shared))


class GateClock(FakeClock):
    def move_monotonic(self, seconds):
        """Move the monotonic clock alone by ``seconds`` (the wall clock stays)."""
        self._monotonic += seconds


def gate_engine(sim):
    """Rewire ``sim`` onto a ``GateClock`` continuing its clock and build a new engine; returns the clock."""
    clock = GateClock(*sim.clock.state())
    sim.clock = clock
    sim.ports = replace(sim.ports, clock=clock)
    sim.engine = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports)
    return clock
