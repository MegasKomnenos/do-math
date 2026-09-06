"""Test raw-input registration ownership using two disposable hidden windows.

Does not generate, record, suppress, or forward keystrokes and never targets a game.
"""
import ctypes as C
from ctypes import wintypes as W
import json
import subprocess
import sys

u = C.WinDLL("user32", use_last_error=True)


class Device(C.Structure):
    _fields_ = [("page", W.USHORT), ("usage", W.USHORT),
                ("flags", W.DWORD), ("window", W.HWND)]


u.CreateWindowExW.argtypes = [W.DWORD, W.LPCWSTR, W.LPCWSTR, W.DWORD,
                             C.c_int, C.c_int, C.c_int, C.c_int,
                             W.HWND, W.HMENU, W.HINSTANCE, W.LPVOID]
u.CreateWindowExW.restype = W.HWND
u.DestroyWindow.argtypes = [W.HWND]
u.RegisterRawInputDevices.argtypes = [C.POINTER(Device), W.UINT, W.UINT]
u.RegisterRawInputDevices.restype = W.BOOL
u.GetRegisteredRawInputDevices.argtypes = [C.POINTER(Device), C.POINTER(W.UINT), W.UINT]
u.GetRegisteredRawInputDevices.restype = W.UINT


def registrations():
    count = W.UINT()
    result = u.GetRegisteredRawInputDevices(None, C.byref(count), C.sizeof(Device))
    if result == 0xFFFFFFFF:
        raise C.WinError(C.get_last_error())
    if not count.value:
        return []
    devices = (Device * count.value)()
    result = u.GetRegisteredRawInputDevices(devices, C.byref(count), C.sizeof(Device))
    if result == 0xFFFFFFFF:
        raise C.WinError(C.get_last_error())
    return [{"page": d.page, "usage": d.usage, "flags": d.flags,
             "window": d.window} for d in devices[:result]]


def window():
    handle = u.CreateWindowExW(0, "STATIC", "Raw registration ownership probe",
                               0, 0, 0, 0, 0, W.HWND(-3), None, None, None)
    if not handle:
        raise C.WinError(C.get_last_error())
    return handle


def register(handle):
    device = Device(1, 6, 0x100, handle)  # RIDEV_INPUTSINK, no NOLEGACY or hooks.
    C.set_last_error(0)
    success = bool(u.RegisterRawInputDevices(C.byref(device), 1, C.sizeof(Device)))
    return {"success": success, "error": C.get_last_error() if not success else 0}


if "--child" in sys.argv:
    target = window()
    try:
        print(target, flush=True)
        sys.stdin.readline()
        print(json.dumps({"child_registrations": registrations()}), flush=True)
    finally:
        u.DestroyWindow(target)
else:
    own = window()
    child = subprocess.Popen([sys.executable, __file__, "--child"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    try:
        target = int(child.stdout.readline())
        result = {"own_window_control": register(own),
                  "cross_process_window": register(target),
                  "parent_registrations": registrations()}
        output, errors = child.communicate("check\n", timeout=10)
        if child.returncode:
            raise RuntimeError(errors)
        result.update(json.loads(output))
        print(json.dumps(result, indent=2))
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        u.DestroyWindow(own)
