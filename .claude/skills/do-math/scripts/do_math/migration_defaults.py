"""Migration defaults for values the layer-3 entry points will pass (설계 A15), removed in stage 1f.

Functions that mint IDs or read the current time take ``clock``, and host checks
take ``host_id``; product callers pass ``self.ports.clock`` and the engine's host.
Until the old tests and entry points pass them too, a missing value falls back to
the operating system here, in one place.
"""


def clock_or_system(clock):
    if clock is not None:
        return clock
    from .system_clock import SystemClock  # layer: 1c migration default until every caller passes the clock port (1f)
    return SystemClock()


def host_or_local(host_id):
    if host_id is not None:
        return host_id
    import platform
    return platform.node()  # layer: 1c migration default until the entry points pass the host (1f)
