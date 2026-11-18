"""Durable files and process supervision shared by the fresh-instance runtime."""

import ctypes, gc, hashlib, json, os, shutil, signal, stat, subprocess, tarfile, time, uuid
from contextlib import AbstractContextManager
from pathlib import Path

WRITE_BUFFER = bytearray(64 * 1024)
WRITE_VIEW = memoryview(WRITE_BUFFER)
JSON_ENCODER = json.JSONEncoder(ensure_ascii=False, indent=2)
ARCHIVE_PRESET = 6
LEAN_DEFAULTS = {"memory_budget_mb": None, "confidence": 1.3, "min_free_memory_mb": 2048, "cpu_threads_budget": None, "threads": 2, "priority": "below_normal", "max_passes": 3, "calibration_expect_mb": 2048, "default_spread": 0.5}

def memory_status():
    """(total physical, headroom) in bytes: commit headroom on Windows, MemAvailable on Linux.

    Both headroom figures count private memory only; file-backed mappings such as
    Lean's .olean files are page cache and never reduce them (reference/lean.md)."""
    if os.name != "nt":
        fields = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        return (int(fields["MemTotal"].split()[0]) * 1024,
                int(fields["MemAvailable"].split()[0]) * 1024)
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
            (name, ctypes.c_ulonglong) for name in
            ("total_phys", "avail_phys", "total_page", "avail_page", "total_virtual", "avail_virtual", "extended")]
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not WIN.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise ctypes.WinError(ctypes.get_last_error())
    return status.total_phys, status.avail_page



def available_memory():
    """Commit headroom on Windows; available physical memory on Linux."""
    return memory_status()[1]



class EmergencyMemory:
    """Committed headroom for the runner, released before a failed save retry."""
    def __init__(self, size=64 * 1024 * 1024):
        self.size = size
        self.buffer = bytearray(size)

    def release(self):
        if self.buffer is None:
            return False
        self.buffer = None
        gc.collect()
        os.write(2, b"Runner memory reserve released; dispatch will wait for recovery.\n")
        return True

    def restore(self):
        if self.buffer is None:
            self.buffer = bytearray(self.size)



def read_json(path):
    deadline = time.monotonic() + 2.0
    while True:
        try:
            return json.loads(Path(path).read_text(encoding='utf-8-sig'))
        except PermissionError as exc:
            if os.name != 'nt' or getattr(exc, 'winerror', None) not in (None, 5, 32, 33) or time.monotonic() >= deadline:
                raise
            time.sleep(.02)


def file_stamp(path):
    stat = Path(path).stat()
    # Atomic replacement can share an NTFS timestamp with the preceding version.
    return stat.st_mtime_ns, stat.st_size, stat.st_ino



def write_json(path, value):
    """Replace one state file atomically; readers see either complete version."""
    def chunks():
        yield from JSON_ENCODER.iterencode(value)
        yield "\n"
    _write_chunks(path, chunks())



def write_text(path, content):
    """Publish a complete UTF-8 file with the same Windows sharing retry."""
    _write_chunks(path, (content,))



def _write_chunks(path, chunks):
    """No whole-document JSON/UTF-8 copy. Single-threaded runner buffer."""
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("wb", buffering=0) as stream:
            used = 0
            def flush_buffer(length):
                offset = 0
                while offset < length:
                    written = stream.write(WRITE_VIEW[offset:length])
                    if not written:
                        raise OSError("State write made no progress")
                    offset += written
            for chunk in chunks:
                # UTF-8 takes at most four bytes per Unicode code point.
                for start in range(0, len(chunk), 16384):
                    data = chunk[start:start + 16384].encode("utf-8")
                    if used + len(data) > len(WRITE_BUFFER):
                        flush_buffer(used)
                        used = 0
                    WRITE_VIEW[used:used + len(data)] = data
                    used += len(data)
            flush_buffer(used)
            os.fsync(stream.fileno())
        _replace_file(temp, path)
    finally:
        temp.unlink(missing_ok=True)



def _replace_file(temp, path):
    # Windows readers may briefly hold the destination without delete sharing.
    # Retry that replacement for up to a minute; keep the old complete state.
    deadline = time.monotonic() + 60.0
    while True:
        try:
            os.replace(temp, path)
            break
        except OSError as exc:
            if (os.name != "nt" or getattr(exc, "winerror", None) not in (5, 32, 33)
                    or time.monotonic() >= deadline):
                raise
            time.sleep(0.05)


def rename_directory(source, destination):
    """Retry only Windows access/sharing failures; never replace a destination.

    Keep the same staged tree throughout the retry. The caller may advance its
    workflow only after this returns; persistent or unexpected errors propagate.
    """
    deadline = time.monotonic() + 60.0
    while True:
        if os.path.lexists(destination):
            raise FileExistsError(f'directory destination already exists: {destination}')
        try:
            os.rename(source, destination)
            return
        except OSError as exc:
            if (os.name != 'nt' or getattr(exc, 'winerror', None) not in (5, 32, 33)
                    or time.monotonic() >= deadline):
                raise
            time.sleep(0.05)



class InstanceLock(AbstractContextManager):
    """OS lock, released by process death; the lock file itself stays in place."""
    def __init__(self, path, holder="runner"):
        self.path = Path(path)
        self.holder = holder  # named in the refusal, so a broker log does not blame the runner
        self.stream = None

    def __enter__(self):
        self.stream = self.path.open("a+b")
        if self.path.stat().st_size == 0:
            self.stream.write(b"0")
            self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.stream.close()
            raise RuntimeError(f"This instance already has a running {self.holder}") from exc
        return self

    def __exit__(self, *args):
        if self.stream:
            self.stream.close()



if os.name == "nt":
    from ctypes import wintypes
    WIN = ctypes.WinDLL("kernel32", use_last_error=True)
    WIN.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    WIN.OpenProcess.restype = wintypes.HANDLE
    WIN.CloseHandle.argtypes = [wintypes.HANDLE]
    WIN.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    WIN.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    WIN.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    WIN.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    WIN.CreateJobObjectW.restype = wintypes.HANDLE
    WIN.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    WIN.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    WIN.GetCurrentProcess.restype = wintypes.HANDLE

    class _BasicLimits(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class _IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                     "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _ExtendedLimits(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BasicLimits), ("IoInfo", _IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]



def windows_birth(handle):
    values = [wintypes.FILETIME() for _ in range(4)]
    if not WIN.GetProcessTimes(handle, *[ctypes.byref(v) for v in values]):
        raise ctypes.WinError(ctypes.get_last_error())
    return str((values[0].dwHighDateTime << 32) | values[0].dwLowDateTime)



def process_identity(pid):
    """PID plus OS creation identity. None means gone, never merely inaccessible."""
    if os.name == "nt":
        handle = WIN.OpenProcess(0x1000 | 0x100000, False, pid)
        if not handle:
            error = ctypes.get_last_error()
            if error == 87:  # ERROR_INVALID_PARAMETER: no such PID
                return None
            raise ctypes.WinError(error)
        try:
            if WIN.WaitForSingleObject(handle, 0) == 0:
                return None
            return {"pid": pid, "birth": windows_birth(handle)}
        finally:
            WIN.CloseHandle(handle)
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        if fields[0] == "Z":
            return None
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        return {"pid": pid, "birth": boot + ":" + fields[19]}
    except FileNotFoundError:
        return None



def alive(identity):
    if not identity:
        return False
    try:
        return process_identity(identity["pid"]) == identity
    except PermissionError:
        # Every recorded process is a descendant that inherited the same privileges, so it can
        # always be opened. A refusal means a process of another account reused the PID. Mixing with
        # elevated runs can break this premise, which is why reference/operations.md asks operators to
        # use shells of one privilege level. If mixing becomes unavoidable, compare creation times from
        # the system process list instead.
        return False



def terminate_process(identity):
    """Verify creation identity on the same handle used to terminate the CLI."""
    if os.name == "nt":
        handle = WIN.OpenProcess(0x1000 | 0x100000 | 1, False, identity["pid"])
        if not handle:
            raise RuntimeError("CLI no longer exists or cannot be opened")
        try:
            if windows_birth(handle) != identity["birth"]:
                raise RuntimeError("PID now belongs to a different process; not terminated")
            if WIN.WaitForSingleObject(handle, 0) != 0:
                if not WIN.TerminateProcess(handle, 1):
                    raise ctypes.WinError(ctypes.get_last_error())
        finally:
            WIN.CloseHandle(handle)
    else:
        # A pidfd keeps the identity stable between comparison and signal.
        fd = os.pidfd_open(identity["pid"])
        try:
            if not alive(identity):
                raise RuntimeError("CLI creation identity changed; not terminated")
            signal.pidfd_send_signal(fd, signal.SIGKILL)
        finally:
            os.close(fd)



def popen_options(detached=False, breakaway=False):
    """breakaway: on Windows, start the process outside the caller's job (contain_session_processes);
    for shared infrastructure such as the Lean broker that must not end with one session."""
    if os.name == "nt":
        flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                 if detached else subprocess.CREATE_NO_WINDOW)
        if breakaway:
            flags |= 0x01000000  # CREATE_BREAKAWAY_FROM_JOB
        return {"creationflags": flags, "close_fds": True}
    return {"start_new_session": True, "close_fds": True}



def git(instance, *args):
    # A caller's Git environment must not redirect this instance's repository.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["git", "-C", str(instance), "-c", "user.name=do-math",
         "-c", "user.email=do-math@localhost", "--literal-pathspecs", *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        encoding="utf-8", errors="replace", **popen_options())
    if result.returncode:
        raise RuntimeError("Git: " + result.stderr.strip())
    return result.stdout.strip()



def lean_config(settings):
    """The broker configuration in force: settings plus the values derived on this host.

    A null memory budget is the physical memory minus the machine gate and a
    512 MiB allowance per AI session; a null thread budget is twice the logical
    core count, since a compile is CPU-bound only during elaboration (reference/lean.md)."""
    lean = settings["lean"]
    config = {key: lean[key] for key in LEAN_DEFAULTS}
    total_mb = memory_status()[0] // (1024 * 1024)
    if config["memory_budget_mb"] is None:
        config["memory_budget_mb"] = max(
            1024, total_mb - lean["min_free_memory_mb"] - 512 * settings["max_sessions"])
    if config["cpu_threads_budget"] is None:
        config["cpu_threads_budget"] = 2 * (os.cpu_count() or 1)
    config["derived"] = {"total_memory_mb": total_mb, "logical_cores": os.cpu_count() or 1,
                         "max_sessions": settings["max_sessions"]}
    return config



_SESSION_JOB = None


def contain_session_processes():
    """Put this host, and every process it or its descendants start, in one Windows job that the
    system terminates when the host exits.

    A session's computations often outlive the shell that started them (nohup, background jobs),
    and their parent link is then gone, so following the process tree at the end misses them.
    Job membership is inherited regardless, so the whole session ends with its host: after its
    last turn, through kill-session, or when the host itself dies. Turns do not end the host, so
    work a session waits on across turns keeps running. Only a process started with an explicit
    breakaway request leaves the job: the Lean broker a session's client may start
    (popen_options(breakaway=True)), and tools that ask for it, which would otherwise fail to start.
    Returns a short status for the session folder; failure leaves the session uncontained."""
    global _SESSION_JOB
    if os.name != "nt":
        return {"contained": False, "reason": "not windows"}
    if _SESSION_JOB is not None:
        return {"contained": True}  # one job per process; repeated in-process calls reuse it
    handle = WIN.CreateJobObjectW(None, None)
    if not handle:
        return {"contained": False, "reason": str(ctypes.WinError(ctypes.get_last_error()))}
    info = _ExtendedLimits()
    # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_BREAKAWAY_OK (explicit requests only)
    info.BasicLimitInformation.LimitFlags = 0x2000 | 0x800
    if (not WIN.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info))
            or not WIN.AssignProcessToJobObject(handle, WIN.GetCurrentProcess())):
        error = ctypes.get_last_error()
        WIN.CloseHandle(handle)
        return {"contained": False, "reason": str(ctypes.WinError(error))}
    _SESSION_JOB = handle  # held until the host exits; the system's close then ends the job
    return {"contained": True}


def session_host(session):
    """Supervise one logical session independently of the runner's lifetime.

    The runner durably records this host's identity BEFORE enabling its gate.
    An unrecorded host cannot start a CLI, even if its parent dies mid-spawn.
    """
    job = read_json(session / "launch.json")
    while not (session / "GO").exists():
        if (session / "CANCEL").exists():
            return 1
        if not alive(job["runner"]):
            # The runner writes GO once this host's identity is durable and can die right after it. The host
            # outlives the runner, so a GO that appeared since the loop's test still starts the session.
            if (session / "GO").exists():
                break
            return 1
        time.sleep(0.1)
    write_json(session / "process-job.json", {**contain_session_processes(), "at": time.time()})
    from ending import run_turn, supervise
    if job.get('end_check') is not None:
        result = supervise(session, job)
    else:
        result = run_turn(session, session, job["command"])
    write_json(session / "exit.json", result)
    return 0



def _digest(stream):
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()



def _work_entries(session):
    """Archive name -> SHA-256 of each file, None for each directory. Links are refused."""
    def scan_error(error):
        raise error
    entries = {"work": None}
    for top, dirs, files in os.walk(session / "work", onerror=scan_error):
        dirs.sort()
        for name in dirs + sorted(files):
            path = os.path.join(top, name)
            if os.path.islink(path) or os.path.isjunction(path):
                raise ValueError(f"work/ contains a link; left unarchived: {path}")
            arcname = Path(path).relative_to(session).as_posix()
            if name in files:
                with open(path, "rb") as stream:
                    entries[arcname] = _digest(stream)
            else:
                entries[arcname] = None
    return entries



def _archive_entries(archive):
    entries = {}
    with tarfile.open(archive, "r|xz") as tar:
        for member in tar:
            entries[member.name] = (_digest(tar.extractfile(member)) if member.isfile()
                                    else None if member.isdir() else "not a file or directory")
    return entries



def remove_tree(path):
    """Remove a directory tree whose contents the runtime keeps elsewhere.

    Windows refuses to remove a read-only file or directory. Git creates its object files read-only,
    and shutil.copytree keeps the flag in its copy. Every caller removes a tree whose contents remain
    elsewhere: a finished work/ in its verified archive, or a stale staging copy in the files it was
    copied from. The flag protects nothing there, so it is cleared where Windows refuses."""
    def clear_read_only(function, name, error):
        if os.name != "nt" or function not in (os.unlink, os.rmdir) or not isinstance(error, PermissionError):
            raise error
        os.chmod(name, stat.S_IWRITE)
        function(name)
    shutil.rmtree(path, onexc=clear_read_only)



def archive_work(session):
    """Replace a finished session's work/ with work.tar.xz, verified file by file.

    work/ is removed only after every file in it is found intact in the archive.
    An existing archive is never overwritten: work/ left by an interrupted removal
    must already be inside it, otherwise both are kept and the mismatch is raised.
    """
    work, archive = session / "work", session / "work.tar.xz"
    if not work.is_dir():
        return False
    if work.is_symlink() or work.is_junction() or work.resolve().parent != session.resolve():
        raise ValueError('work archive must remain inside its session directory')
    entries = _work_entries(session)
    if archive.exists():
        stored = _archive_entries(archive)
    else:
        part = session / "work.tar.xz.part"
        try:
            with tarfile.open(part, "w:xz", preset=ARCHIVE_PRESET) as tar:
                for name in entries:
                    tar.add(session / name, arcname=name, recursive=False)
            stored = _archive_entries(part)
            if stored == entries:
                os.replace(part, archive)
        finally:
            part.unlink(missing_ok=True)
    if any(stored.get(name, "missing") != value for name, value in entries.items()):
        raise RuntimeError(f"work/ does not match {archive.name}; work/ kept: {session}")
    remove_tree(work)
    return True
