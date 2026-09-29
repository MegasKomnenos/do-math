"""Real file-system arrangements for storage tests, made in process on Windows, and an audit-event recorder.

The file system is not a port (설계 2.2): storage tests run on real temporary
folders. What a test cannot write with ordinary file calls it arranges here
with the Windows API rather than by replacing a product or ``os`` function:

- ``age(path, seconds)``: set a file's creation and modification times back,
  so its fingerprint counts as settled (``file_io.fingerprint_settled``).
- ``unlistable(directory)``: hold the directory open with no sharing, so
  listing it fails with a sharing violation (``PermissionError``) while its
  attributes stay readable.
- ``junction(target, link)``: an NTFS directory junction, a reparse point.
- ``audit_events(*names)``: the audit events (``sys.audit``) raised while a
  block runs, such as ``open`` for files read or ``subprocess.Popen`` for
  processes started. Python cannot remove an audit hook, so one hook is
  installed for the process and records only while a block is active.
"""
from contextlib import contextmanager
import ctypes
import os
import sys
import time

_RECORDERS = []
_HOOK = []


def _hook(event, arguments):
    for record in list(_RECORDERS):
        record(event, arguments)


@contextmanager
def audit_events(*names):
    """``[(event, arguments)]`` of the named audit events raised while the block runs."""
    if not _HOOK:
        sys.addaudithook(_hook)
        _HOOK.append(_hook)
    events = []

    def record(event, arguments):
        if event in names:
            events.append((event, arguments))
    _RECORDERS.append(record)
    try:
        yield events
    finally:
        _RECORDERS.remove(record)


def age(path, seconds):
    """Set ``path``'s creation and last-write times ``seconds`` before now (Windows ``SetFileTime``)."""
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                   wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    # FILE_WRITE_ATTRIBUTES, share read/write/delete, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
    handle = kernel.CreateFileW(str(path), 0x100, 0x7, None, 3, 0x80, None)
    if handle in (None, wintypes.HANDLE(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        ticks = (time.time_ns() - seconds * 1_000_000_000) // 100 + 116444736000000000
        stamp = wintypes.FILETIME(ticks & 0xFFFFFFFF, ticks >> 32)
        if not kernel.SetFileTime(handle, ctypes.byref(stamp), None, ctypes.byref(stamp)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


@contextmanager
def unlistable(directory):
    """``directory`` is held open for listing with no sharing while the block runs; listing it fails."""
    import _winapi
    # FILE_LIST_DIRECTORY, no sharing, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS (needed to open a directory)
    handle = _winapi.CreateFile(str(directory), 0x1, 0, 0, 3, 0x02000000, 0)
    try:
        yield
    finally:
        _winapi.CloseHandle(handle)


def junction(target, link):
    """Make ``link`` an NTFS junction to the directory ``target``; remove it with ``os.rmdir(link)`` only."""
    import _winapi
    _winapi.CreateJunction(str(target), str(link))
    return link


def remove_link(link):
    """Remove a junction itself, never the directory it points to."""
    os.rmdir(link)
