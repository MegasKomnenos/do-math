"""Observation probes for provider and observation tests: they watch the product and replace nothing.

- ``ObservedCalls(name=function, ...)``: a context that records every call to
  the named functions while it is open, on any thread, seen through
  ``sys.monitoring`` start events of those functions' code objects alone (other
  code runs unobserved and at full speed). Each call is recorded as ``(caller,
  captured)``: ``caller`` is the ``__name__`` of the module whose code made the
  call, and ``captured`` is ``capture(arguments)`` taken as the call starts,
  before the callee can change its arguments (default: a shallow copy of the
  argument mapping). Legacy tests counted such calls by patching the product
  name with a ``wraps`` double; this counts the same calls on the unchanged product.
- ``settle(path)``: move a file's modification and creation times beyond
  ``file_io.RACY_NS`` into the past, so its fingerprint may stand in for its
  bytes (``fingerprint_settled``). A new file's creation time cannot be set
  with ``os``; on Windows it is set with ``SetFileTime``.
- ``junction(link, target)``: a directory junction (Windows) or a directory
  symbolic link elsewhere, made without a child process.
"""
import ctypes
import inspect
import os
from pathlib import Path
import sys

from do_math.file_io import RACY_NS


def _code(function):
    return inspect.unwrap(getattr(function, '__func__', function)).__code__


class ObservedCalls:
    def __init__(self, *, capture=None, **functions):
        """``capture`` maps a name to its capture function; unnamed functions record a copy of their arguments."""
        self.names = {_code(function): name for name, function in functions.items()}
        self.capture = {name: (capture or {}).get(name, dict) for name in functions}
        self.calls = {name: [] for name in functions}

    def __enter__(self):
        monitoring = sys.monitoring
        # A tool slot no debugger, coverage tool or profiler holds.
        self.tool = next(tool for tool in (3, 4, 0, 2) if monitoring.get_tool(tool) is None)
        monitoring.use_tool_id(self.tool, 'do-math observed calls')

        def started(code, offset):
            frame = sys._getframe(1)  # the frame of the call that just started
            name = self.names[code]
            caller = frame.f_back.f_globals.get('__name__') if frame.f_back is not None else None
            self.calls[name].append((caller, self.capture[name](dict(frame.f_locals))))
        monitoring.register_callback(self.tool, monitoring.events.PY_START, started)
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.PY_START)
        return self

    def __exit__(self, *exception):
        monitoring = sys.monitoring
        for code in self.names:
            monitoring.set_local_events(self.tool, code, monitoring.events.NO_EVENTS)
        monitoring.register_callback(self.tool, monitoring.events.PY_START, None)
        monitoring.free_tool_id(self.tool)
        return False

    def count(self, name, *, caller=None):
        """How many calls to ``name`` were made, only from module ``caller`` when it is given."""
        return sum(1 for made_by, _ in self.calls[name] if caller is None or made_by == caller)

    def captured(self, name, *, caller=None):
        return [value for made_by, value in self.calls[name] if caller is None or made_by == caller]


def _set_creation_time(path, nanoseconds):
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                   wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    handle = kernel.CreateFileW(str(path), 0x100, 0x7, None, 3, 0x80, None)  # FILE_WRITE_ATTRIBUTES, share all
    if handle in (None, wintypes.HANDLE(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ticks = nanoseconds // 100 + 116444736000000000
        created = wintypes.FILETIME(ticks & 0xFFFFFFFF, ticks >> 32)
        if not kernel.SetFileTime(handle, ctypes.byref(created), None, None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


def settle(path):
    """Put ``path``'s modification and creation times twice the racy window in the past."""
    info = os.stat(path)
    past = 2 * RACY_NS
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns - past))
    if os.name == 'nt':
        _set_creation_time(path, getattr(info, 'st_birthtime_ns', info.st_ctime_ns) - past)


def junction(link, target):
    """A directory reparse point at ``link`` resolving to ``target``."""
    link, target = Path(link), Path(target)
    if os.name == 'nt':
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)
