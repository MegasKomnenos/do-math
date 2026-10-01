"""Real installation copies and return-time control delivery; no product definitions are replaced."""
from contextlib import contextmanager
import inspect
from pathlib import Path
import shutil
import sys

from support.provider_probes import settle
from support.monitoring_slots import reserve_tool


def copy_installation(target):
    source = Path(__file__).resolve().parents[3]
    target = Path(target)
    # Only installed source/document files; no test trees, caches or linked toolchains.
    paths = list((source / 'scripts/do_math').rglob('*.py'))
    paths += list(source.glob('*.md'))
    for directory in ('references', '계약'):
        paths += list((source / directory).rglob('*.md'))
    paths += [source / 'scripts/operator_schedule.ps1', source / 'scripts/do_math.py']
    for path in paths:
        destination = target / path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        settle(destination)
    return target


@contextmanager
def at_return(function, action):
    """Run one external action at a successful PY_RETURN, after the original body finished."""
    code = inspect.unwrap(getattr(function, '__func__', function)).__code__
    monitoring = sys.monitoring
    tool = reserve_tool('do-math storage return event')
    values = []

    def returned(actual, offset, value):
        if actual is code:
            monitoring.set_local_events(tool, code, monitoring.events.NO_EVENTS)
            values.append(value)
            action()
    monitoring.register_callback(tool, monitoring.events.PY_RETURN, returned)
    monitoring.set_local_events(tool, code, monitoring.events.PY_RETURN)
    try:
        yield values
    finally:
        monitoring.set_local_events(tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(tool, monitoring.events.PY_RETURN, None)
        monitoring.free_tool_id(tool)
