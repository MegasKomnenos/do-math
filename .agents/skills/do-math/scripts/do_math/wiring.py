"""Layer 3 assembly of the real ports; product entry points pass this bundle down."""
from .ports import Ports
from .git_process import GitProcess
from .parallel import ThreadCalls
from .system_clock import SystemClock


def real_ports() -> Ports:
    return Ports(clock=SystemClock(), git_backend=GitProcess(), calls=ThreadCalls())


def default_clock():
    """The real clock for callers not yet handed a Ports bundle (stage 1b migration only)."""
    return real_ports().clock
