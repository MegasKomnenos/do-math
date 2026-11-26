"""Durable files and process supervision shared by the fresh-instance runtime."""

import copy, ctypes, gc, hashlib, json, os, shutil, signal, stat, subprocess, tarfile, time, uuid
from contextlib import AbstractContextManager
from pathlib import Path

WRITE_BUFFER_BYTES = 64 * 1024  # the size of the buffer through which one write of a file goes
JSON_ENCODER = json.JSONEncoder(ensure_ascii=False, indent=2)
COMPACT_ENCODER = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
ARCHIVE_PRESET = 6
LEAN_DEFAULTS = {"memory_budget_mb": None, "confidence": 1.3, "min_free_memory_mb": 2048, "cpu_threads_budget": None, "threads": 2, "priority": "below_normal", "max_passes": 3, "calibration_expect_mb": 2048, "default_spread": 0.5}

def memory_status():
    """(total physical, headroom) in bytes: commit headroom on Windows, MemAvailable on Linux.

    The Windows figure is what the system can still commit. A Lean process is charged there for
    the whole size of the .olean files it maps, although it touches a part of them, so imports
    reduce it (reference/lean-broker.md). MemAvailable on Linux does not count such mappings."""
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



def _read(read, path, seconds):
    """What `read` returns for the file; on Windows a refused read is made again for up to `seconds`.

    A read is refused while another process holds the file without read sharing or is replacing it.
    Python's open reports that as errno 13 with no Windows error code, so winerror is None here. The
    operations of _retried call Windows directly and receive the code itself, which is why the two
    lists of codes differ."""
    deadline = time.monotonic() + seconds
    while True:
        try:
            return read(Path(path))
        except PermissionError as exc:
            if os.name != 'nt' or getattr(exc, 'winerror', None) not in (None, 5, 32, 33) or time.monotonic() >= deadline:
                raise
            time.sleep(.02)


def read_json(path):
    """The parsed content of a JSON file; on Windows a refused read is made again for up to two seconds (_read)."""
    return json.loads(_read(lambda file: file.read_text(encoding='utf-8-sig'), path, 2.0))


def _stamp(info):
    # Atomic replacement can share an NTFS timestamp with the preceding version.
    return info.st_mtime_ns, info.st_size, info.st_ino


def file_stamp(path):
    return _stamp(Path(path).stat())


_JSON_SEEN = {}


def read_json_cached(path):
    """The content of a JSON file that one process reads again and again, or None when it is no file.

    One file-system lookup says whether the file has changed since it was last read, by the same stamp
    as file_stamp; only then is it opened and parsed again. The runner asks for every session's
    declaration, end check and process receipt on each pass, and most of them have not changed since
    the pass before. Each call returns a copy of its own, so a caller may keep or change what it gets."""
    path = Path(path)
    key = str(path)
    try:
        info = path.stat()
    except (FileNotFoundError, NotADirectoryError):
        info = None
    if info is None or not stat.S_ISREG(info.st_mode):
        _JSON_SEEN.pop(key, None)
        return None
    stamp = _stamp(info)
    seen = _JSON_SEEN.get(key)
    if seen is None or seen[0] != stamp:
        seen = _JSON_SEEN[key] = (stamp, read_json(path))
    return copy.deepcopy(seen[1])



def write_json(path, value):
    """Replace one state file atomically; readers see either complete version."""
    def chunks():
        yield from JSON_ENCODER.iterencode(value)
        yield "\n"
    _write_chunks(path, chunks())


def write_json_compact(path, value):
    """Replace one state file atomically, as write_json does, without indentation.

    For a file that is large and rewritten often, such as the Lean broker's state. The indented form
    is produced token by token by the encoder written in Python, and for a state of a few megabytes
    that took about 200 ms a write, ten times what this takes. Here the whole document is encoded in
    one call, by the C encoder where Python has it. Readers parse the file, so its layout is free; the
    replacement is the same as write_json's, and a reader still sees one complete version or the other."""
    _write_chunks(path, (COMPACT_ENCODER.encode(value), "\n"))



def write_text(path, content):
    """Publish a complete UTF-8 file with the same Windows sharing retry."""
    _write_chunks(path, (content,))



def _write_chunks(path, chunks):
    """Write the chunks into a file beside `path` and replace `path` with it.

    A chunk is encoded 16384 characters at a time, so no document is held a second time as bytes. Each
    call writes through a buffer of its own, so several threads of one process may write at once."""
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("wb", buffering=WRITE_BUFFER_BYTES) as stream:
            for chunk in chunks:
                for start in range(0, len(chunk), 16384):
                    stream.write(chunk[start:start + 16384].encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        replace_file(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def remove_unfinished_writes(folder):
    """Remove, anywhere under a folder, the files that writes which did not finish left there.

    _write_chunks removes the file it writes beside a destination, unless its process ends first: a process that
    is ended, or a machine that goes down, inside a write leaves `<name>.<32 hexadecimal digits>.tmp`. The caller
    is the one process that writes under the folder and has no write of its own under way."""
    for path in Path(folder).rglob('*.tmp'):
        mark = path.name[:-len('.tmp')].rpartition('.')[2]
        if len(mark) == 32 and not mark.strip('0123456789abcdef'):
            remove_file(path)



def _retried(operation, *paths):
    """Carry out a file operation, repeating it for up to a minute while Windows refuses it for access or sharing."""
    deadline = time.monotonic() + 60.0
    while True:
        try:
            return operation(*paths)
        except OSError as exc:
            if (os.name != "nt" or getattr(exc, "winerror", None) not in (5, 32, 33)
                    or time.monotonic() >= deadline):
                raise
            time.sleep(0.05)


def replace_file(source, destination):
    """Move a complete file to its destination in one step, replacing a file that is there.

    Windows readers, such as sessions reading the canon, may briefly hold the source or the destination
    without delete sharing. Retry the move for up to a minute; until it succeeds both files stay as they were."""
    _retried(os.replace, source, destination)


def remove_file(path):
    """Remove a file that a Windows reader may briefly hold without delete sharing, with the retry of _retried;
    until the removal succeeds the file stays."""
    _retried(os.unlink, path)


def read_bytes(path):
    """The bytes of a file that a Windows process may briefly hold without read sharing; a refused read is made
    again for up to a minute (_read), as long as a replacement waits (_retried)."""
    return _read(lambda file: file.read_bytes(), path, 60.0)


def rename_directory(source, destination):
    """Retry only Windows access/sharing failures; never replace a destination.

    Keep the same staged tree throughout the retry. The caller may advance its
    workflow only after this returns; persistent or unexpected errors propagate.
    """
    def rename(source, destination):
        if os.path.lexists(destination):
            raise FileExistsError(f'directory destination already exists: {destination}')
        os.rename(source, destination)
    _retried(rename, source, destination)



class InstanceLock(AbstractContextManager):
    """OS lock, released by process death; the lock file itself stays in place.

    `wait` is the number of seconds for which the lock is asked for again while another process holds
    it; with none the lock is refused at once. `refusal` is what the RuntimeError of a refusal says."""
    def __init__(self, path, holder="runner", wait=0.0, refusal=None):
        self.path = Path(path)
        # The refusal names the holder, so a broker log does not blame the runner.
        self.refusal = refusal or f"This instance already has a running {holder}"
        self.wait = wait
        self.stream = None

    def __enter__(self):
        deadline = time.monotonic() + self.wait
        self.stream = self.path.open("a+b")
        if self.path.stat().st_size == 0:
            self.stream.write(b"0")
            self.stream.flush()
        while True:
            self.stream.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError as exc:
                if time.monotonic() >= deadline:
                    self.stream.close()
                    raise RuntimeError(self.refusal) from exc
                time.sleep(0.05)

    def __exit__(self, *args):
        if self.stream:
            if os.name == "nt":
                # Unlocked here and not left to the close: Windows gives no time by which it frees the lock
                # of a file that is closed while it is locked.
                import msvcrt
                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
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
        # As bytes: the name a process gave itself stands in this file and need not be text.
        fields = Path(f"/proc/{pid}/stat").read_bytes().rsplit(b")", 1)[1].split()
        if fields[0] == b"Z":
            return None
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        return {"pid": pid, "birth": boot + ":" + fields[19].decode()}
    except (FileNotFoundError, ProcessLookupError):
        # The process ended before its stat file was opened, or it was reaped between the open and the
        # read, which Linux answers with ESRCH. Either way it is gone.
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
    """Verify creation identity on the same handle used to terminate the process."""
    if os.name == "nt":
        handle = WIN.OpenProcess(0x1000 | 0x100000 | 1, False, identity["pid"])
        if not handle:
            raise RuntimeError("Process no longer exists or cannot be opened")
        try:
            if windows_birth(handle) != identity["birth"]:
                raise RuntimeError("PID now belongs to a different process; not terminated")
            if WIN.WaitForSingleObject(handle, 0) != 0:
                if not WIN.TerminateProcess(handle, 1):
                    error = ctypes.get_last_error()
                    # The handle was opened with the right to terminate, so access denied (5) is the system's
                    # answer for a process that is already ending: another caller terminated it first.
                    # kill-session and the session host both end a cancelled CLI (runner.main, ending.run_turn).
                    if error != 5:
                        raise ctypes.WinError(error)
        finally:
            WIN.CloseHandle(handle)
    else:
        # A pidfd keeps the identity stable between comparison and signal.
        fd = os.pidfd_open(identity["pid"])
        try:
            if not alive(identity):
                raise RuntimeError("Process creation identity changed; not terminated")
            signal.pidfd_send_signal(fd, signal.SIGKILL)
        finally:
            os.close(fd)



def popen_options(detached=False, breakaway=False):
    """breakaway: on Windows, ask to start the process outside the caller's job, for shared
    infrastructure such as the Lean broker that must not end with one session. The request changes
    nothing for a caller outside any job, and a job that forbids leaving, as a session's does
    (contain_session_processes), refuses it with PermissionError."""
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
    # core.fsync=all: left to its default, Git does not send to the disk the loose objects, the index and the
    # reference that a commit writes. The runner saves, through to the disk, that a publication is done once
    # its commit is made, so after a loss of power the repository has to hold that commit whole.
    # commit.gpgsign=false: the commits here are the runtime's own, made under the name given below by a runner
    # that nobody attends, and the person who runs the instance has no key for that name. Where that person's
    # Git configuration signs every commit, Git would start the signing program for these commits as well,
    # which finds no key for that name and refuses the commit, or waits for a passphrase that nobody gives.
    # core.hooksPath: Git looks for its hooks in the folder named here, and nothing makes this one, so Git runs
    # no hook. The Git configuration of the person who runs the instance can name a folder of hooks for every
    # repository, or a template from which `git init` copies hooks into each new one. Such a hook checks that
    # person's own commits, their message or their files. One that refused a commit made here would end init,
    # or the runner at that publication and at every start after it.
    result = subprocess.run(
        ["git", "-C", str(instance), "-c", "user.name=do-math",
         "-c", "user.email=do-math@localhost", "-c", "core.fsync=all", "-c", "commit.gpgsign=false",
         "-c", "core.hooksPath=" + (Path(instance) / ".git" / "hooks-not-used").as_posix(),
         "--literal-pathspecs", *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        encoding="utf-8", errors="replace", **popen_options())
    if result.returncode:
        raise RuntimeError("Git: " + result.stderr.strip())
    return result.stdout.strip()


def first_commit(instance, commit="HEAD"):
    """The commit with which an instance began: the commit without a parent that `commit` descends from.

    runner.initialize makes exactly one such commit, so the history of an instance has one."""
    return git(instance, "rev-list", "--max-parents=0", commit).split()[0]



def lean_config(settings):
    """The broker configuration in force: settings plus the values derived on this host.

    A null memory budget is the physical memory minus the machine gate and a
    512 MiB allowance per AI session; a null thread budget is twice the logical
    core count, since a compile is CPU-bound only during elaboration (reference/lean-broker.md)."""
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
    work a session waits on across turns keeps running. The job grants no breakaway, so nothing
    the session starts can leave it. A job that permits breakaway does not hold a session's
    computations: Git Bash asks to leave on every program it starts whenever its job permits that,
    so the job that once let the Lean broker leave let every computation run from the session's
    shell leave too. The shared broker is therefore never started from inside a session
    (lean_broker.ensure_broker); the runner starts it outside every session's job.
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
    # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE alone: without JOB_OBJECT_LIMIT_BREAKAWAY_OK a request to
    # leave the job is refused, and Git Bash, which asks only where it is permitted, does not ask.
    info.BasicLimitInformation.LimitFlags = 0x2000
    if (not WIN.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info))
            or not WIN.AssignProcessToJobObject(handle, WIN.GetCurrentProcess())):
        error = ctypes.get_last_error()
        WIN.CloseHandle(handle)
        return {"contained": False, "reason": str(ctypes.WinError(error))}
    _SESSION_JOB = handle  # held until the host exits; the system's close then ends the job
    return {"contained": True}


def wait_for_go(folder, starter):
    """Wait at a host's gate: True once the host's folder holds GO, False when the host is not to start.

    The runner starts a session host and the Lean broker a job host (lean_broker.job_host). Each records
    the host's identity durably and only then writes GO into the host's folder, so a host that its starter
    never recorded starts nothing, even if the starter dies while it spawns the host. The host is not to
    start when CANCEL appears first, or when the starter has died without writing GO. The starter can die
    right after it wrote GO, and the host outlives it, so a GO that appeared since the loop's test still
    opens the gate."""
    while not (folder / "GO").exists():
        if (folder / "CANCEL").exists():
            return False
        if not alive(starter):
            return (folder / "GO").exists()
        time.sleep(0.1)
    return True


def session_host(session):
    """Supervise one logical session independently of the runner's lifetime.

    The runner durably records this host's identity BEFORE enabling its gate.
    An unrecorded host cannot start a CLI, even if its parent dies mid-spawn.
    """
    job = read_json(session / "launch.json")
    if not wait_for_go(session, job["runner"]):
        return 1
    write_json(session / "process-job.json", {**contain_session_processes(), "at": time.time()})
    from ending import supervise
    result = supervise(session, job)
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
    """Remove a directory tree that its caller has finished with.

    Windows refuses to remove a read-only file or directory. Git creates its object files read-only,
    and shutil.copytree keeps the flag in its copy. No caller needs the tree it removes: a finished
    work/ whose files are in its verified archive, a staging copy of files that remain where they were
    copied from, a folder that the finalize command made and makes again or has finished with, the
    fixture of a test. The flag protects nothing there, so it is cleared where Windows refuses. Windows refuses
    in the same way a file or directory that another process holds for a moment, and the removal then waits
    for it as the removal of one file does (_retried)."""
    def clear_read_only(function, name, error):
        if os.name != "nt" or function not in (os.unlink, os.rmdir) or not isinstance(error, PermissionError):
            raise error
        os.chmod(name, stat.S_IWRITE)
        _retried(function, name)
    shutil.rmtree(path, onexc=clear_read_only)



def _packed(session, name, entries):
    """Whether the archive `name` of a session holds every entry intact; where there is no archive, it is written first.

    `entries` is what the caller read in the session folder: archive name -> SHA-256 of a file, None for a
    directory. An existing archive is never overwritten. A new one is written beside its place, read back,
    and moved into its place only if it holds exactly the entries, so that no archive stands for files it
    does not hold. The caller removes the originals only when this returns True."""
    archive = session / name
    if archive.exists():
        stored = _archive_entries(archive)
    else:
        part = session / (name + ".part")
        try:
            # dereference: a file that stands under two names among the entries, a hard link, is written under
            # each name as a file with its content. Left to its default, tarfile writes the second name as a
            # link to the first; the read-back below then finds no file under that name, the archive never
            # holds exactly the entries, and the originals would stay unarchived at every pass.
            with tarfile.open(part, "w:xz", preset=ARCHIVE_PRESET, dereference=True) as tar:
                for entry in entries:
                    tar.add(session / entry, arcname=entry, recursive=False)
            stored = _archive_entries(part)
            if stored == entries:
                # On disk before the originals are removed: the check above read the archive back from the system's cache.
                with part.open("rb+") as stream:
                    os.fsync(stream.fileno())
                os.replace(part, archive)
        finally:
            part.unlink(missing_ok=True)
    return all(stored.get(entry, "missing") == value for entry, value in entries.items())


def archive_work(session):
    """Replace a finished session's work/ with work.tar.xz, verified file by file.

    work/ is removed only after every file in it is found intact in the archive.
    An existing archive is never overwritten: work/ left by an interrupted removal
    must already be inside it, otherwise both are kept and the mismatch is raised.
    """
    work = session / "work"
    if not work.is_dir():
        return False
    if work.is_symlink() or work.is_junction() or work.resolve().parent != session.resolve():
        raise ValueError('work archive must remain inside its session directory')
    if not _packed(session, "work.tar.xz", _work_entries(session)):
        raise RuntimeError(f"work/ does not match work.tar.xz; work/ kept: {session}")
    remove_tree(work)
    return True


def archive_raw(session):
    """Replace a finished session's raw conversation with raw.tar.xz, verified as archive_work verifies work/.

    The raw conversation is the CLI stream of each turn, cli.stdout.jsonl in the session folder and in
    each folder under turns/, and each copy of the CLI's own transcript, transcript-<id>.jsonl
    (retention.capture). The archive holds them under the paths they had in the session folder, which are
    the paths retention.json gives. Everything else stays where it is: conversation.md, the readable text
    drawn from them, retention.json, and the folder transcript-<id>/ that conversation.md points into.
    A file is removed only after it is found intact in the archive. An existing archive is never
    overwritten: a raw file left by an interrupted removal must already be inside it, otherwise both are
    kept and the mismatch is raised."""
    files = [path for pattern in ("cli.stdout.jsonl", "turns/*/cli.stdout.jsonl", "transcript-*.jsonl")
             for path in sorted(session.glob(pattern)) if path.is_file()]
    if not files:
        return False
    entries = {}
    for path in files:
        with path.open("rb") as stream:
            entries[path.relative_to(session).as_posix()] = _digest(stream)
    if not _packed(session, "raw.tar.xz", entries):
        raise RuntimeError(f"raw conversation does not match raw.tar.xz; its files kept: {session}")
    for path in files:
        remove_file(path)
    return True
