"""Windows Job-backed process lifetime ownership for the initial do-math adapter.

This module owns process lifetime only.  A Job object does not isolate files,
network, IPC, credentials, or process identity; those boundaries need separate
enforcement.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence
from typing import Final


class WindowsJobUnsupportedError(RuntimeError):
    """The host cannot provide atomic Job-list process creation."""


@dataclass(frozen=True, slots=True)
class JobInspection:
    """A point-in-time observation of the Job and its root process."""

    active_processes: int
    process_ids: tuple[int, ...]
    root_signaled: bool


if os.name == "nt":
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    _DWORD = ctypes.c_uint32
    _DWORD_PTR = ctypes.c_size_t
    _HANDLE = ctypes.c_void_p
    _SIZE_T = ctypes.c_size_t
    _BOOL = ctypes.c_int

    _ERROR_INSUFFICIENT_BUFFER: Final = 122
    _ERROR_MORE_DATA: Final = 234
    _ERROR_NOT_SUPPORTED: Final = 50
    _ERROR_CALL_NOT_IMPLEMENTED: Final = 120
    _ERROR_INVALID_PARAMETER: Final = 87
    _ERROR_ACCESS_DENIED: Final = 5
    _HANDLE_FLAG_INHERIT: Final = 0x00000001
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE: Final = 0x00002000
    _JobObjectBasicAccountingInformation: Final = 1
    _JobObjectBasicProcessIdList: Final = 3
    _JobObjectExtendedLimitInformation: Final = 9
    _PROC_THREAD_ATTRIBUTE_JOB_LIST: Final = 0x0002000D
    _PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES: Final = 0x00020009
    _EXTENDED_STARTUPINFO_PRESENT: Final = 0x00080000
    _CREATE_SUSPENDED: Final = 0x00000004
    _CREATE_NO_WINDOW: Final = 0x08000000
    _CREATE_UNICODE_ENVIRONMENT: Final = 0x00000400
    _WAIT_OBJECT_0: Final = 0
    _WAIT_TIMEOUT: Final = 258
    _WAIT_FAILED: Final = 0xFFFFFFFF
    _INFINITE: Final = 0xFFFFFFFF

    class _FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", _DWORD), ("dwHighDateTime", _DWORD)]

    class _STARTUPINFOW(ctypes.Structure):
        _fields_ = [
            ("cb", _DWORD),
            ("lpReserved", ctypes.c_wchar_p),
            ("lpDesktop", ctypes.c_wchar_p),
            ("lpTitle", ctypes.c_wchar_p),
            ("dwX", _DWORD),
            ("dwY", _DWORD),
            ("dwXSize", _DWORD),
            ("dwYSize", _DWORD),
            ("dwXCountChars", _DWORD),
            ("dwYCountChars", _DWORD),
            ("dwFillAttribute", _DWORD),
            ("dwFlags", _DWORD),
            ("wShowWindow", ctypes.c_ushort),
            ("cbReserved2", ctypes.c_ushort),
            ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
            ("hStdInput", _HANDLE),
            ("hStdOutput", _HANDLE),
            ("hStdError", _HANDLE),
        ]

    class _STARTUPINFOEXW(ctypes.Structure):
        _fields_ = [("StartupInfo", _STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]

    class _PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("hProcess", _HANDLE),
            ("hThread", _HANDLE),
            ("dwProcessId", _DWORD),
            ("dwThreadId", _DWORD),
        ]

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
        )]

    class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", _DWORD),
            ("MinimumWorkingSetSize", _SIZE_T),
            ("MaximumWorkingSetSize", _SIZE_T),
            ("ActiveProcessLimit", _DWORD),
            ("Affinity", _DWORD_PTR),
            ("PriorityClass", _DWORD),
            ("SchedulingClass", _DWORD),
        ]

    class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", _SIZE_T),
            ("JobMemoryLimit", _SIZE_T),
            ("PeakProcessMemoryUsed", _SIZE_T),
            ("PeakJobMemoryUsed", _SIZE_T),
        ]

    class _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_int64),
            ("TotalKernelTime", ctypes.c_int64),
            ("ThisPeriodTotalUserTime", ctypes.c_int64),
            ("ThisPeriodTotalKernelTime", ctypes.c_int64),
            ("TotalPageFaultCount", _DWORD),
            ("TotalProcesses", _DWORD),
            ("ActiveProcesses", _DWORD),
            ("TotalTerminatedProcesses", _DWORD),
        ]

    class _SECURITY_CAPABILITIES(ctypes.Structure):
        _fields_ = [
            ("AppContainerSid", ctypes.c_void_p),
            ("Capabilities", ctypes.c_void_p),
            ("CapabilityCount", _DWORD),
            ("Reserved", _DWORD),
        ]

    _kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    _kernel32.CreateJobObjectW.restype = _HANDLE
    _kernel32.SetInformationJobObject.argtypes = [_HANDLE, ctypes.c_int, ctypes.c_void_p, _DWORD]
    _kernel32.SetInformationJobObject.restype = _BOOL
    _kernel32.QueryInformationJobObject.argtypes = [
        _HANDLE, ctypes.c_int, ctypes.c_void_p, _DWORD, ctypes.POINTER(_DWORD),
    ]
    _kernel32.QueryInformationJobObject.restype = _BOOL
    _kernel32.SetHandleInformation.argtypes = [_HANDLE, _DWORD, _DWORD]
    _kernel32.SetHandleInformation.restype = _BOOL
    _kernel32.InitializeProcThreadAttributeList.argtypes = [
        ctypes.c_void_p, _DWORD, _DWORD, ctypes.POINTER(_SIZE_T),
    ]
    _kernel32.InitializeProcThreadAttributeList.restype = _BOOL
    _kernel32.UpdateProcThreadAttribute.argtypes = [
        ctypes.c_void_p, _DWORD, _DWORD_PTR, ctypes.c_void_p, _SIZE_T,
        ctypes.c_void_p, ctypes.c_void_p,
    ]
    _kernel32.UpdateProcThreadAttribute.restype = _BOOL
    _kernel32.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
    _kernel32.DeleteProcThreadAttributeList.restype = None
    _kernel32.CreateProcessW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_void_p,
        _BOOL, _DWORD, ctypes.c_void_p, ctypes.c_wchar_p,
        ctypes.POINTER(_STARTUPINFOW), ctypes.POINTER(_PROCESS_INFORMATION),
    ]
    _kernel32.CreateProcessW.restype = _BOOL
    _kernel32.GetProcessTimes.argtypes = [
        _HANDLE, ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME),
        ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME),
    ]
    _kernel32.GetProcessTimes.restype = _BOOL
    _kernel32.ResumeThread.argtypes = [_HANDLE]
    _kernel32.ResumeThread.restype = _DWORD
    _kernel32.TerminateJobObject.argtypes = [_HANDLE, _DWORD]
    _kernel32.TerminateJobObject.restype = _BOOL
    _kernel32.WaitForSingleObject.argtypes = [_HANDLE, _DWORD]
    _kernel32.WaitForSingleObject.restype = _DWORD
    _kernel32.CloseHandle.argtypes = [_HANDLE]
    _kernel32.CloseHandle.restype = _BOOL


def _raise_last_error(function: str) -> None:
    error = ctypes.get_last_error()
    raise OSError(error, f"{function} failed", None, error)


def _require_windows_10_job_list() -> None:
    if os.name != "nt":
        raise WindowsJobUnsupportedError("Windows Job process creation requires Windows 10 or later")
    version = sys.getwindowsversion()
    if version.major < 10:
        raise WindowsJobUnsupportedError(
            "PROC_THREAD_ATTRIBUTE_JOB_LIST requires Windows 10 / Windows Server 2016 or later"
        )


def _command_line(argv: Sequence[str | os.PathLike[str]]) -> str:
    if isinstance(argv, (str, bytes)) or not argv:
        raise ValueError("argv must be a non-empty sequence of argument strings")
    arguments = [os.fspath(argument) for argument in argv]
    if any(not isinstance(argument, str) or "\x00" in argument for argument in arguments):
        raise ValueError("argv must contain NUL-free strings")
    return subprocess.list2cmdline(arguments)


def _environment_block(env: Mapping[str, str] | None):
    if env is None:
        return None
    entries: list[str] = []
    for key, value in env.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("environment names and values must be strings")
        if not key or "=" in key or "\x00" in key or "\x00" in value:
            raise ValueError("environment names and values must be NUL-free; names cannot contain '='")
        entries.append(f"{key}={value}")
    entries.sort(key=str.upper)
    return ctypes.create_unicode_buffer("\x00".join(entries) + "\x00\x00")


class WindowsJob:
    """A single suspended root atomically placed in a kill-on-close Job.

    The object is the sole holder of its non-inheritable Job handle.  Closing
    it therefore kills remaining roots and descendants.  It intentionally
    does not claim any filesystem, network, IPC, credential, or identity
    isolation.  ``appcontainer_sid`` is an unverified optional creation
    attribute and is not evidence that any such boundary is enforced.
    """

    def __init__(
        self,
        argv: Sequence[str | os.PathLike[str]],
        *,
        cwd: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
        appcontainer_sid: int | None = None,
        name: str | None = None,
    ) -> None:
        _require_windows_10_job_list()
        command_line = _command_line(argv)
        environment = _environment_block(env)
        current_directory = None if cwd is None else os.fspath(cwd)
        if current_directory is not None and "\x00" in current_directory:
            raise ValueError("cwd must be NUL-free")
        if appcontainer_sid is not None and (
            isinstance(appcontainer_sid, bool)
            or not isinstance(appcontainer_sid, int)
            or appcontainer_sid <= 0
        ):
            raise ValueError("appcontainer_sid must be a non-null SID pointer integer")

        self.name = name
        self._job: int | None = None
        self._process: int | None = None
        self._thread: int | None = None
        self._resumed = False
        self._closed = False
        self.pid = 0
        self.creation_filetime = 0

        try:
            self._job = self._create_job()
            self._process, self._thread, self.pid = self._create_suspended_root(
                command_line, current_directory, environment, appcontainer_sid
            )
            self.creation_filetime = self._process_creation_filetime()
        except BaseException:
            self.close()
            raise

    @property
    def job_handle(self) -> int:
        return self._require_open_handle(self._job, "Job")

    @property
    def process_handle(self) -> int:
        return self._require_open_handle(self._process, "process")

    def _require_open_handle(self, handle: int | None, name: str) -> int:
        if self._closed or handle is None:
            raise RuntimeError(f"{name} handle is closed")
        return handle

    def _create_job(self) -> int:
        handle = _kernel32.CreateJobObjectW(None, self.name)
        if not handle:
            _raise_last_error("CreateJobObjectW")
        if not _kernel32.SetHandleInformation(handle, _HANDLE_FLAG_INHERIT, 0):
            error = ctypes.get_last_error()
            _kernel32.CloseHandle(handle)
            raise OSError(error, "SetHandleInformation failed", None, error)
        limits = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not _kernel32.SetInformationJobObject(
            handle,
            _JobObjectExtendedLimitInformation,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            error = ctypes.get_last_error()
            _kernel32.CloseHandle(handle)
            raise OSError(error, "SetInformationJobObject failed", None, error)
        return int(handle)

    def _create_suspended_root(
        self,
        command_line: str,
        cwd: str | None,
        environment,
        appcontainer_sid: int | None,
    ) -> tuple[int, int, int]:
        attribute_count = 1 + (appcontainer_sid is not None)
        attribute_size = _SIZE_T()
        ctypes.set_last_error(0)
        _kernel32.InitializeProcThreadAttributeList(None, attribute_count, 0, ctypes.byref(attribute_size))
        if ctypes.get_last_error() != _ERROR_INSUFFICIENT_BUFFER or not attribute_size.value:
            error = ctypes.get_last_error()
            raise WindowsJobUnsupportedError(
                f"InitializeProcThreadAttributeList is unavailable (Win32 error {error})"
            )

        attributes_buffer = ctypes.create_string_buffer(attribute_size.value)
        attribute_list = ctypes.cast(attributes_buffer, ctypes.c_void_p)
        initialized = False
        try:
            if not _kernel32.InitializeProcThreadAttributeList(
                attribute_list, attribute_count, 0, ctypes.byref(attribute_size)
            ):
                error = ctypes.get_last_error()
                raise WindowsJobUnsupportedError(
                    f"InitializeProcThreadAttributeList failed (Win32 error {error})"
                )
            initialized = True
            job_list = (_HANDLE * 1)(_HANDLE(self.job_handle))
            if not _kernel32.UpdateProcThreadAttribute(
                attribute_list,
                0,
                _PROC_THREAD_ATTRIBUTE_JOB_LIST,
                ctypes.byref(job_list),
                ctypes.sizeof(job_list),
                None,
                None,
            ):
                error = ctypes.get_last_error()
                raise WindowsJobUnsupportedError(
                    f"PROC_THREAD_ATTRIBUTE_JOB_LIST is unavailable (Win32 error {error})"
                )
            security_capabilities = None
            if appcontainer_sid is not None:
                security_capabilities = _SECURITY_CAPABILITIES(
                    ctypes.c_void_p(appcontainer_sid), None, 0, 0
                )
                if not _kernel32.UpdateProcThreadAttribute(
                    attribute_list,
                    0,
                    _PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES,
                    ctypes.byref(security_capabilities),
                    ctypes.sizeof(security_capabilities),
                    None,
                    None,
                ):
                    error = ctypes.get_last_error()
                    if error in (_ERROR_NOT_SUPPORTED, _ERROR_CALL_NOT_IMPLEMENTED):
                        raise WindowsJobUnsupportedError(
                            f"PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES is unavailable (Win32 error {error})"
                        )
                    raise OSError(
                        error,
                        "PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES failed",
                        None,
                        error,
                    )

            startup = _STARTUPINFOEXW()
            startup.StartupInfo.cb = ctypes.sizeof(startup)
            startup.lpAttributeList = attribute_list
            process_info = _PROCESS_INFORMATION()
            mutable_command_line = ctypes.create_unicode_buffer(command_line)
            flags = (
                _EXTENDED_STARTUPINFO_PRESENT
                | _CREATE_SUSPENDED
                | _CREATE_NO_WINDOW
                | _CREATE_UNICODE_ENVIRONMENT
            )
            environment_pointer = None if environment is None else ctypes.cast(environment, ctypes.c_void_p)
            if not _kernel32.CreateProcessW(
                None,
                mutable_command_line,
                None,
                None,
                False,
                flags,
                environment_pointer,
                cwd,
                ctypes.byref(startup.StartupInfo),
                ctypes.byref(process_info),
            ):
                error = ctypes.get_last_error()
                if error in (_ERROR_NOT_SUPPORTED, _ERROR_CALL_NOT_IMPLEMENTED, _ERROR_INVALID_PARAMETER, _ERROR_ACCESS_DENIED):
                    raise WindowsJobUnsupportedError(
                        f"atomic Job-list process creation is unsupported (Win32 error {error})"
                    )
                raise OSError(error, "CreateProcessW failed", None, error)
            return int(process_info.hProcess), int(process_info.hThread), int(process_info.dwProcessId)
        finally:
            if initialized:
                _kernel32.DeleteProcThreadAttributeList(attribute_list)

    def _process_creation_filetime(self) -> int:
        created = _FILETIME()
        exited = _FILETIME()
        kernel = _FILETIME()
        user = _FILETIME()
        if not _kernel32.GetProcessTimes(
            self.process_handle,
            ctypes.byref(created),
            ctypes.byref(exited),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            _raise_last_error("GetProcessTimes")
        return (int(created.dwHighDateTime) << 32) | int(created.dwLowDateTime)

    def resume(self) -> None:
        """Start the initially suspended root exactly once."""
        if self._resumed:
            raise RuntimeError("root thread has already been resumed")
        thread = self._require_open_handle(self._thread, "root thread")
        if _kernel32.ResumeThread(thread) == _WAIT_FAILED:
            _raise_last_error("ResumeThread")
        self._resumed = True
        if not _kernel32.CloseHandle(thread):
            self._thread = None
            _raise_last_error("CloseHandle(root thread)")
        self._thread = None

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for the root; return ``False`` on timeout without dropping ownership."""
        if timeout is None:
            milliseconds = _INFINITE
        else:
            if timeout < 0:
                raise ValueError("timeout must be non-negative")
            milliseconds = min(int(timeout * 1000), _INFINITE - 1)
        result = _kernel32.WaitForSingleObject(self.process_handle, milliseconds)
        if result == _WAIT_OBJECT_0:
            return True
        if result == _WAIT_TIMEOUT:
            return False
        _raise_last_error("WaitForSingleObject")

    def terminate(self, exit_code: int = 1) -> None:
        """Terminate every process in the Job, including descendants."""
        if not 0 <= exit_code <= 0xFFFFFFFF:
            raise ValueError("exit_code must fit in DWORD")
        if not _kernel32.TerminateJobObject(self.job_handle, exit_code):
            _raise_last_error("TerminateJobObject")

    def inspect(self) -> JobInspection:
        """Read active count, live Job PIDs, and the root handle's signal state."""
        accounting = _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        returned = _DWORD()
        if not _kernel32.QueryInformationJobObject(
            self.job_handle,
            _JobObjectBasicAccountingInformation,
            ctypes.byref(accounting),
            ctypes.sizeof(accounting),
            ctypes.byref(returned),
        ):
            _raise_last_error("QueryInformationJobObject(BasicAccounting)")
        process_ids = self._job_process_ids()
        wait = _kernel32.WaitForSingleObject(self.process_handle, 0)
        if wait == _WAIT_FAILED:
            _raise_last_error("WaitForSingleObject")
        return JobInspection(
            active_processes=int(accounting.ActiveProcesses),
            process_ids=process_ids,
            root_signaled=wait == _WAIT_OBJECT_0,
        )

    def _job_process_ids(self) -> tuple[int, ...]:
        capacity = 16
        while True:
            buffer = ctypes.create_string_buffer(8 + ctypes.sizeof(_DWORD_PTR) * capacity)
            returned = _DWORD()
            if _kernel32.QueryInformationJobObject(
                self.job_handle,
                _JobObjectBasicProcessIdList,
                buffer,
                ctypes.sizeof(buffer),
                ctypes.byref(returned),
            ):
                count = ctypes.c_uint32.from_buffer(buffer, 4).value
                values = (_DWORD_PTR * count).from_buffer(buffer, 8)
                return tuple(int(value) for value in values)
            error = ctypes.get_last_error()
            if error != _ERROR_MORE_DATA:
                raise OSError(error, "QueryInformationJobObject(BasicProcessIdList) failed", None, error)
            required_count = ctypes.c_uint32.from_buffer(buffer, 4).value
            capacity = max(capacity * 2, required_count, 1)

    def close(self) -> None:
        """Close owned handles; closing the Job kills remaining descendants."""
        if self._closed:
            return
        self._closed = True
        first_error: OSError | None = None
        for attribute in ("_thread", "_job", "_process"):
            handle = getattr(self, attribute)
            setattr(self, attribute, None)
            if handle is not None and not _kernel32.CloseHandle(handle) and first_error is None:
                error = ctypes.get_last_error()
                first_error = OSError(error, f"CloseHandle({attribute}) failed", None, error)
        if first_error is not None:
            raise first_error

    def __enter__(self) -> "WindowsJob":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def named_job_empty(name: str) -> bool | None:
    """Observe a known local Job after owner loss; access failure is unknown."""
    if os.name != "nt":
        return None
    open_job = _kernel32.OpenJobObjectW
    open_job.argtypes = [_DWORD, _BOOL, ctypes.c_wchar_p]
    open_job.restype = _HANDLE
    handle = open_job(4, False, name)  # JOB_OBJECT_QUERY
    if not handle:
        return True if ctypes.get_last_error() == 2 else None
    try:
        accounting = _JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        returned = _DWORD()
        if not _kernel32.QueryInformationJobObject(handle, _JobObjectBasicAccountingInformation,
                ctypes.byref(accounting), ctypes.sizeof(accounting), ctypes.byref(returned)):
            return None
        return accounting.ActiveProcesses == 0
    finally:
        _kernel32.CloseHandle(handle)
