"""Clock input for observation rule units with a scripted monotonic source."""
from support.fakes.clock import FakeClock


def scripted_clock(monotonic):
    clock = FakeClock()
    clock.monotonic = monotonic
    return clock
