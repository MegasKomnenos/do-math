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


def transport_or_http(transport):
    if transport is not None:
        return transport
    from . import http_transport  # layer: 1c migration default until every caller passes the HTTP port (1f)
    return http_transport._http


def codex_home_or_default(codex_home):
    if codex_home is not None:
        return codex_home
    import os
    from pathlib import Path
    value = os.environ.get("CODEX_HOME")  # layer: 1c migration default until the entry points pass CODEX_HOME (1f)
    return Path(value) if value else Path.home() / ".codex"


def jobs_or_windows(jobs):
    if jobs is not None:
        return jobs
    from .windows_job import WindowsJobs  # layer: 1c migration default until every caller passes the Jobs port (1f)
    return WindowsJobs()
