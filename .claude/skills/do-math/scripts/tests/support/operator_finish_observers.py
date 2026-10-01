"""Current call paths, observed without replacing constructors or return values."""
import sys

from do_math import scheduled_operator as operator
from do_math.engine import ResearchEngine


def construction(arguments):
    """Called at PY_START; compare code identities, retain names, never live frames.

    Only the exact Engine.__init__ <- read_status path is a status-owned
    constructor. Merely having read_status somewhere in an ancestry is not
    enough. Other operator ancestry includes calls routed through helpers.
    """
    frame = sys._getframe(2).f_back  # capture <- monitoring callback <- callee
    path = []
    modules = []
    while frame is not None:
        path.append(frame.f_code)
        modules.append(frame.f_globals.get('__name__'))
        frame = frame.f_back
    return {'arguments': dict(arguments),
            'status_engine': path[:2] == [ResearchEngine.__init__.__code__, operator.read_status.__code__],
            'status_reload': path[:3] == [ResearchEngine._reload.__code__,
                ResearchEngine.status.__code__, operator.read_status.__code__],
            'operator_scope': operator.__name__ in modules,
            'path': tuple(code.co_qualname for code in path)}


def outside_status(calls, name):
    return [call for call in calls.captured(name)
            if call['operator_scope'] and not call['status_engine']]
