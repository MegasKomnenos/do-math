"""The Windows Job adapter itself (``windows_job.WindowsJob``): real Jobs, real child processes, kernel state read directly.

A ``WindowsJob`` places one command as the suspended root of a new
kill-on-close Job and runs no user code before ``resume``. Its Job handle is
not inheritable and allows no breakaway, so closing the last Job handle (the
owner's exit included) ends every process in it. The tests read the kernel's
own view through ``kernel32``.
"""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from do_math.windows_job import WindowsJob

SCRIPTS = Path(__file__).resolve().parents[2]
WAIT_TIMEOUT = 258  # WaitForSingleObject: the object is not signaled

if os.name == "nt":
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _HANDLE_FLAG_INHERIT = 0x00000001
    _JobObjectExtendedLimitInformation = 9
    _JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
    _JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
        )]

    class _BASIC_LIMITS(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class _EXTENDED_LIMITS(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BASIC_LIMITS),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]


def process_kernel():
    """kernel32 typed for holding and signalling one process handle."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel.WaitForSingleObject.restype = ctypes.c_uint32
    kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel.TerminateProcess.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    return kernel


def release_process(kernel, handle):
    """End a still-live process this test holds a handle to, then close the handle."""
    if not handle:
        return
    try:
        if kernel.WaitForSingleObject(handle, 0) == WAIT_TIMEOUT:
            kernel.TerminateProcess(handle, 1)
            kernel.WaitForSingleObject(handle, 5000)
    finally:
        kernel.CloseHandle(handle)


def reached(predicate, timeout=15.0):
    """Poll ``predicate`` until it holds or ``timeout`` seconds pass; whether it held."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while time.monotonic() < deadline:
        if predicate():
            return True
        pause.wait(0.02)
    return predicate()


@unittest.skipUnless(os.name == "nt", "requires a Windows host")
class WindowsJobTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def wait_for(self, predicate, timeout=15.0):
        if not reached(predicate, timeout):
            self.fail("timed out waiting for Windows process state")

    def test_root_is_suspended_until_explicit_resume(self):
        marker = self.path / "started"
        code = f"from pathlib import Path; Path({str(marker)!r}).write_text('ok')"
        with WindowsJob([sys.executable, "-c", code]) as job:
            self.assertFalse(marker.exists())
            self.assertGreater(job.creation_filetime, 0)
            initial = job.inspect()
            self.assertEqual(initial.active_processes, 1)
            self.assertIn(job.pid, initial.process_ids)
            self.assertFalse(initial.root_signaled)

            job.resume()
            self.wait_for(marker.exists)
            self.assertTrue(job.wait(5.0))
            self.wait_for(lambda: job.inspect().active_processes == 0)
            completed = job.inspect()
            self.assertEqual(completed.active_processes, 0)
            self.assertEqual(completed.process_ids, ())
            self.assertTrue(completed.root_signaled)

    def test_wait_timeout_keeps_job_owned_until_explicit_close(self):
        kernel = process_kernel()
        job = WindowsJob([sys.executable, "-c", "import time; time.sleep(60)"])
        # Retain the process, not the Job: close must release the last Job handle.
        root_handle = kernel.OpenProcess(0x00100001, False, job.pid)
        try:
            self.assertTrue(root_handle, f"OpenProcess failed: {ctypes.get_last_error()}")
            job.resume()
            self.assertFalse(job.wait(0.01))
            inspection = job.inspect()
            self.assertGreaterEqual(inspection.active_processes, 1)
            self.assertIn(job.pid, inspection.process_ids)
            job.close()
            self.assertEqual(kernel.WaitForSingleObject(root_handle, 5000), 0,
                             "a timed-out wait leaked a live root after close")
        finally:
            job.close()
            release_process(kernel, root_handle)

    def test_direct_createprocess_receives_requested_cwd_and_environment(self):
        marker = self.path / "environment"
        code = (
            "import os; "
            f"open({str(marker)!r}, 'w').write(os.getcwd() + '\\n' + os.environ['DO_MATH_JOB_TEST'])"
        )
        environment = {"DO_MATH_JOB_TEST": "present", "SystemRoot": os.environ["SystemRoot"]}
        with WindowsJob([sys.executable, "-c", code], cwd=self.path, env=environment) as job:
            job.resume()
            self.wait_for(marker.exists)
            self.assertTrue(job.wait(5.0))
        observed_cwd, observed_value = marker.read_text().splitlines()
        self.assertEqual(Path(observed_cwd), self.path)
        self.assertEqual(observed_value, "present")

    def test_terminate_ends_descendant_processes_and_job_becomes_empty(self):
        child_pid_file = self.path / "child-pid"
        child_code = "import time; time.sleep(30)"
        parent_code = (
            "import subprocess, sys, time; "
            f"p=subprocess.Popen([sys.executable, '-c', {child_code!r}]); "
            f"open({str(child_pid_file)!r}, 'w').write(str(p.pid)); "
            "time.sleep(30)"
        )
        with WindowsJob([sys.executable, "-c", parent_code]) as job:
            job.resume()
            self.wait_for(lambda: child_pid_file.exists() and bool(child_pid_file.read_text()))
            child_pid = int(child_pid_file.read_text())
            self.assertIn(child_pid, job.inspect().process_ids)

            job.terminate()
            self.assertTrue(job.wait(5.0))
            self.wait_for(lambda: job.inspect().active_processes == 0)
            after = job.inspect()
            self.assertEqual(after.process_ids, ())
            self.assertTrue(after.root_signaled)

    def test_owner_process_loss_closes_job_and_ends_root(self):
        root_pid_file = self.path / "root-pid"
        started_marker = self.path / "root-started"
        root_code = (
            "import time; from pathlib import Path; "
            f"Path({str(started_marker)!r}).write_text('running'); "
            "time.sleep(60)"
        )
        owner_code = (
            "import os, sys; from pathlib import Path; "
            f"sys.path.insert(0, {str(SCRIPTS)!r}); "
            "from do_math.windows_job import WindowsJob; "
            f"job=WindowsJob([sys.executable, '-c', {root_code!r}]); "
            "job.resume(); "
            f"Path({str(root_pid_file)!r}).write_text(str(job.pid)); "
            "sys.stdin.buffer.read(1); os._exit(0)"
        )
        kernel = process_kernel()
        owner = subprocess.Popen([sys.executable, "-c", owner_code], stdin=subprocess.PIPE,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        root_handle = None
        try:
            self.wait_for(lambda: root_pid_file.exists() and bool(root_pid_file.read_text()))
            # Hold only the process handle; retaining a Job handle would prevent
            # the owner-loss condition from closing the last Job handle.
            root_handle = kernel.OpenProcess(0x00100001, False, int(root_pid_file.read_text()))
            self.assertTrue(root_handle, f"OpenProcess failed: {ctypes.get_last_error()}")
            self.wait_for(started_marker.exists)
            self.assertIsNone(owner.poll())
            self.assertEqual(kernel.WaitForSingleObject(root_handle, 0), WAIT_TIMEOUT)
            owner.stdin.write(b"x")
            owner.stdin.flush()
            self.assertEqual(owner.wait(timeout=10), 0)
            self.assertEqual(kernel.WaitForSingleObject(root_handle, 5000), 0,
                             "the running root did not terminate after its Job owner exited")
        finally:
            if owner.poll() is None:
                owner.kill()
                owner.wait(timeout=10)
            owner.stdin.close()
            release_process(kernel, root_handle)

    def test_job_handle_is_not_inheritable_and_breakaway_is_disabled(self):
        with WindowsJob([sys.executable, "-c", "import time; time.sleep(30)"]) as job:
            flags = ctypes.c_uint32()
            self.assertTrue(_kernel32.GetHandleInformation(job.job_handle, ctypes.byref(flags)))
            self.assertEqual(flags.value & _HANDLE_FLAG_INHERIT, 0)

            limits = _EXTENDED_LIMITS()
            returned = ctypes.c_uint32()
            self.assertTrue(_kernel32.QueryInformationJobObject(
                job.job_handle, _JobObjectExtendedLimitInformation, ctypes.byref(limits),
                ctypes.sizeof(limits), ctypes.byref(returned)))
            limit_flags = limits.BasicLimitInformation.LimitFlags
            self.assertTrue(limit_flags & _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
            self.assertFalse(limit_flags & _JOB_OBJECT_LIMIT_BREAKAWAY_OK)
            self.assertFalse(limit_flags & _JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK)

    def test_create_failure_leaves_no_live_job_root(self):
        with self.assertRaisesRegex(OSError, "CreateProcessW failed"):
            WindowsJob([str(self.path / "not-an-executable.exe")])

    def test_root_cannot_signal_an_unrelated_inheritable_parent_handle(self):
        _kernel32.CreateEventW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_wchar_p]
        _kernel32.CreateEventW.restype = ctypes.c_void_p
        _kernel32.SetHandleInformation.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
        _kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        event = _kernel32.CreateEventW(None, True, False, None)
        self.assertTrue(event)
        try:
            self.assertTrue(_kernel32.SetHandleInformation(event, _HANDLE_FLAG_INHERIT, _HANDLE_FLAG_INHERIT))
            marker = self.path / "handle-probe-ran"
            code = (
                "import ctypes; "
                "k=ctypes.WinDLL('kernel32',use_last_error=True); "
                "k.SetEvent.argtypes=[ctypes.c_void_p]; "
                f"k.SetEvent({event}); "
                f"open({str(marker)!r},'w').write('ran')"
            )
            with WindowsJob([sys.executable, "-c", code]) as job:
                job.resume()
                self.assertTrue(job.wait(15))
                self.assertTrue(marker.exists())
                self.assertEqual(_kernel32.WaitForSingleObject(event, 0), WAIT_TIMEOUT,
                                 "root inherited and signaled an unrelated parent Event")
        finally:
            _kernel32.CloseHandle(event)


if __name__ == "__main__":
    unittest.main()
