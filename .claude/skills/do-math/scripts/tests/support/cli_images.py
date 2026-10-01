"""Two initialized CLI repository images, copied back to their original absolute path.

Only public CLI initialization is cached here. No active engine, external trust
installation or process state is reconstructed by this boundary helper.
"""
import atexit
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile

from do_math.repository import ResearchRepository
from do_math.session_slots import quiescence
from support.sim import _remove

_IMAGES = {}


def initialized_cli(kind):
    from support.entry import entry
    _entry = entry()
    from do_math.wiring import real_ports
    _entry.ports = real_ports(environment=_entry.environment)
    if kind not in {'existing', 'created'}:
        raise ValueError('unknown initialized CLI image: ' + kind)
    if kind not in _IMAGES:
        _IMAGES[kind] = None  # A failed public initialization is never retried.
        base = Path(tempfile.mkdtemp(prefix='do-math-cli-image-')).resolve()
        atexit.register(_remove, base)
        live, image = base / 'live', base / 'image'
        live.mkdir()
        if kind == 'existing':
            from support.engine_cli import cli_instance
            value = cli_instance(live)
            repository, identifier = live / 'repository', value['instance_id']
        else:
            from support.engine_cli_created import created_instance
            value = created_instance(live)
            repository, identifier = live / 'repo', value
        _, instance, runtime = ResearchRepository(repository, identifier, backend=_entry.ports.git_backend, clock=_entry.ports.clock).load()
        if instance['lifecycle']['state'] != 'initializing' or any(quiescence(runtime).values()):
            raise AssertionError('CLI image must be initialized with no unfinished execution or held reservation')
        shutil.copytree(live, image)
        _IMAGES[kind] = (live, image, value)
    if _IMAGES[kind] is None:
        raise AssertionError('the initialized CLI image failed earlier: ' + kind)
    live, image, value = _IMAGES[kind]
    _remove(live)
    shutil.copytree(image, live)
    return live, deepcopy(value)
