"""The ports through which layers 2 and 3 reach outside resources (docs/do-math/시험-재편-2026-09-29/설계.md 2.2).

``Ports`` has one field per port; its field list is the port registry. This
package holds only protocols and the bundle; the real implementations are
chosen by ``do_math.wiring.real_ports`` (layer 3) and tests pass fakes.
"""
from dataclasses import dataclass

from .calls import Calls
from .clock import Clock
from .git_backend import GitBackend
from .jobs import Jobs


@dataclass(frozen=True)
class Ports:
    clock: Clock
    git_backend: GitBackend
    calls: Calls
    jobs: Jobs
