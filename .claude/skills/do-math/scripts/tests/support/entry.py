"""Host values and fake ports for direct domain callers outside a Sim.

Real boundary tests explicitly assemble real_ports at their own call sites.
The host values are sampled by this test entry, never constructed by domain code.
Independent inputs use disjoint deterministic ID ranges, so combining records
from two direct fixture builders cannot accidentally reuse an ID.
"""
import os
import platform
from itertools import count
from pathlib import Path
from types import SimpleNamespace

from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.storage_records import fake_ports

_IDENTITIES = count(1)


def entry():
    environment = dict(os.environ)
    clock = FakeClock(counter=next(_IDENTITIES) << 32)
    return SimpleNamespace(ports=fake_ports(clock, InProcessGit()),
                           environment=environment, host_id=platform.node(),
                           codex_home=Path(environment.get('CODEX_HOME') or Path.home() / '.codex'))
