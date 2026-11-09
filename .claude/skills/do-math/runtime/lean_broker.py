"""The Lean broker of one do-math instance: every Lean process is a scheduled job. See ../reference/lean.md.

Three roles live in this file.

- The client (`submit`, `run`, `build`, `wait`, `result`, `status`, `cancel`, `version`) is
  what a session runs instead of Lean. It writes a request, waits for the result and
  relays Lean's output and exit code.
- The broker (`serve`) is one detached process per instance, single through
  runner/lean/lock. It measures what compiles cost, keeps the calibration table, and
  starts queued jobs within one memory budget and one thread budget.
- The job host (`_job`) is the parent of each Lean process, so that a job's exit code
  survives the broker's death exactly as a session's survives the runner's.
"""

import argparse
from collections import defaultdict
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time
import uuid

from runtime_support import (InstanceLock, alive, available_memory, file_stamp, lean_config,
                    popen_options, process_identity, read_json, terminate_process, write_json)
from settings import load_settings

SCRIPT = Path(__file__).resolve()
MIB = 1024 * 1024
POLL = 0.25
SAMPLE_SAVE_SECONDS = 1.0  # memory samples alone reach state.json at most this often
ACTIVE = ("queued", "running")
FINISHED = ("finished", "failed", "cancelled")
BROKER_SESSION = "broker"
NICE = {"normal": 0, "below_normal": 10, "idle": 19}
WINDOWS_PRIORITY = {"normal": 0x20, "below_normal": 0x4000, "idle": 0x40}
P90 = 1.2816  # the standard-normal 90th percentile: an estimate is read as a probable peak
HISTORY = 20  # samples kept per import closure
KEEP_FINISHED = 200  # finished job records kept in the broker state; result.json files stay
READY_SECONDS = 20.0
IMPORT = re.compile(r"^(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?(\S+)")
JOB_ID = re.compile(r"^[jc][0-9a-f]{32}$")  # a job folder name; anything else never touches the file system
BUILD_ID = re.compile(r"^b[0-9a-f]{32}$")
MODULE_PART = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")  # one component of a module name, as a file name
# Modules of the toolchain itself; a local module under these names would shadow them for every compile.
TOOLCHAIN_ROOTS = ("Init", "Lean", "Std", "Lake")


# ----------------------------------------------------------------------------- files

class Paths:
    def __init__(self, instance):
        self.instance = Path(instance).resolve()
        self.root = self.instance / "runner/lean"
        self.lock = self.root / "lock"
        self.process = self.root / "process.json"
        self.state = self.root / "state.json"
        self.calibration = self.root / "calibration.json"
        self.queue = self.root / "queue"
        self.jobs = self.root / "jobs"
        self.sources = self.root / "calibration"
        self.builds = self.root / "builds"
        self.cache = self.root / "cache"  # emitted module files and logs; a manifest marks complete entries
        self.log = self.root / "broker.log"

    def ensure(self):
        for directory in (self.root, self.queue, self.jobs, self.sources, self.builds, self.cache):
            directory.mkdir(parents=True, exist_ok=True)

    def job(self, job_id):
        if not JOB_ID.fullmatch(job_id):
            raise ValueError('invalid job ID')
        return self.jobs / job_id

    def build(self, build_id):
        if not BUILD_ID.fullmatch(build_id):
            raise ValueError('invalid build ID')
        return self.builds / build_id


def read_imports(path):
    """Read header imports, preserving code around ordinary and nested comments."""
    imports = set()
    depth = 0
    for line in Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines():
        code = []
        index = 0
        while index < len(line):
            if depth:
                if line.startswith("/-", index):
                    depth += 1
                    index += 2
                elif line.startswith("-/", index):
                    depth -= 1
                    index += 2
                else:
                    index += 1
            elif line.startswith("--", index):
                break
            elif line.startswith("/-", index):
                code.append(" ")
                depth = 1
                index += 2
            else:
                code.append(line[index])
                index += 1
        stripped = "".join(code).strip()
        if not stripped or stripped in ("prelude", "module"):
            continue
        match = IMPORT.match(stripped)
        if not match:
            break
        imports.add(match[1])
    return sorted(imports)


def closure_key(environment, imports, direct=False):
    """One key per (environment identity, import set, launch mode); a new Lean or a changed
    environment_key makes old baselines invisible. `environment` is Broker.environment_identity().

    A compile launched directly, without `lake env` in front of it, costs about a gigabyte
    less on this machine, so its baselines are kept apart from those measured through lake."""
    text = environment + "\n" + "\n".join(imports) + ("\ndirect" if direct else "")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------- module trees

def module_name(root, path):
    """`<root>/Foo/Bar.lean` is the module `Foo.Bar`, exactly as `lean -R <root>` names it."""
    relative = Path(path).resolve().relative_to(Path(root).resolve())
    parts = relative.with_suffix("").parts
    if relative.suffix != ".lean" or not all(MODULE_PART.match(p) for p in parts):
        raise ValueError(f"not a module path under the root: {path}")
    return ".".join(parts)


def module_path(root, name):
    return Path(root).joinpath(*name.split(".")).with_suffix(".lean")


def discover_modules(root, targets):
    """The targets and every local module they import, directly or not, in dependency order.

    An import is local when `<root>/<its path>.lean` exists; anything else is external
    (Mathlib, the toolchain). Returns [(name, {"source", "imports", "local", "external"})]
    with every module after the ones it imports. Rejects an import cycle, an unreadable
    file, and a local module that would shadow the toolchain or an external import."""
    root = Path(root).resolve()
    modules, order, visiting = {}, [], []

    def visit(name):
        if name in modules:
            return
        if name in visiting:
            cycle = visiting[visiting.index(name):] + [name]
            raise ValueError("import cycle: " + " -> ".join(cycle))
        visiting.append(name)
        source = module_path(root, name)
        imports = read_imports(source)  # OSError if the file cannot be read
        local = [i for i in imports if module_path(root, i).is_file()]
        for dep in local:
            visit(dep)
        visiting.pop()
        modules[name] = {"source": str(source), "imports": imports, "local": local,
                         "external": [i for i in imports if i not in local]}
        order.append(name)

    for target in targets:
        visit(module_name(root, target))
    external_roots = {i.split(".")[0] for m in modules.values() for i in m["external"]} | set(TOOLCHAIN_ROOTS)
    for name in order:
        if name.split(".")[0] in external_roots:
            raise ValueError(f"local module {name} would shadow a library module of the same name")
    return [(name, modules[name]) for name in order]


def module_keys(environment, modules):
    """The cache key of each module: environment identity (Broker.environment_identity()), module name, source bytes and the keys of its local imports.

    A change anywhere below a module changes its key, so a stale .olean can never be
    reached; the same bytes built by two sessions get the same key and the same .olean."""
    keys = {}
    for name, module in modules:
        digest = hashlib.sha256()
        source_bytes = Path(module['source']).read_bytes()
        module['source_sha256'] = hashlib.sha256(source_bytes).hexdigest()
        for part in [environment, name, source_bytes] + [keys[d] for d in module["local"]]:
            digest.update(part if isinstance(part, bytes) else part.encode("utf-8"))
            digest.update(b"\n")
        keys[name] = digest.hexdigest()[:32]
    return keys


# ---------------------------------------------------------------------- processes

def process_tree(pid):
    """pid and every descendant, parents before children. `lake env lean` is two processes."""
    children = defaultdict(list)
    if os.name == "nt":
        for child, parent in _windows_processes():
            children[parent].append(child)
        # Windows keeps a dead parent's PID in its children; a process created before its
        # recorded parent cannot be that parent's child, so only younger children are followed.
        births = {}
        def born(candidate):
            if candidate not in births:
                births[candidate] = _windows_birth(candidate)
            return births[candidate]
        order, stack = [], [pid]
        while stack:
            current = stack.pop()
            order.append(current)
            parent_birth = born(current)
            if parent_birth is None:
                continue
            stack.extend(child for child in children.get(current, [])
                         if (child_birth := born(child)) is not None and child_birth >= parent_birth)
        return order
    else:
        for entry in os.scandir("/proc"):
            if not entry.name.isdigit():
                continue
            try:
                stat = Path(entry.path, "stat").read_text()
            except OSError:
                continue
            children[int(stat.rsplit(")", 1)[1].split()[1])].append(int(entry.name))
    order, stack = [], [pid]
    while stack:
        current = stack.pop()
        order.append(current)
        stack.extend(children.get(current, []))
    return order


def private_memory_mb(pids):
    """Private (anonymous / committed) memory of the processes, in MiB; shared mappings excluded."""
    total = 0
    for pid in pids:
        try:
            total += _private_bytes(pid)
        except (OSError, ValueError, KeyError):  # gone, or a zombie without memory fields
            continue
    return total / MIB


if os.name == "nt":
    from ctypes import wintypes
    from runtime_support import WIN as KERNEL, windows_birth
    PSAPI = ctypes.WinDLL("psapi", use_last_error=True)

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_char * 260)]

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in
            ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
             "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage",
             "PeakPagefileUsage", "PrivateUsage")]

    KERNEL.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    KERNEL.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    KERNEL.Process32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    KERNEL.Process32First.restype = wintypes.BOOL
    KERNEL.Process32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
    KERNEL.Process32Next.restype = wintypes.BOOL
    PSAPI.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX), wintypes.DWORD]
    PSAPI.GetProcessMemoryInfo.restype = wintypes.BOOL

    def _windows_birth(pid):
        """Creation time as an integer, or None if the process cannot be opened (gone, or not ours)."""
        handle = KERNEL.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return None
        try:
            return int(windows_birth(handle))
        except OSError:
            return None
        finally:
            KERNEL.CloseHandle(handle)

    def _windows_processes():
        snapshot = KERNEL.CreateToolhelp32Snapshot(0x2, 0)
        if snapshot == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            entry = PROCESSENTRY32()
            entry.dwSize = ctypes.sizeof(entry)
            ok = KERNEL.Process32First(snapshot, ctypes.byref(entry))
            while ok:
                yield entry.th32ProcessID, entry.th32ParentProcessID
                ok = KERNEL.Process32Next(snapshot, ctypes.byref(entry))
        finally:
            KERNEL.CloseHandle(snapshot)

    def _private_bytes(pid):
        handle = KERNEL.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            raise OSError(ctypes.get_last_error(), "cannot open process")
        try:
            counters = PROCESS_MEMORY_COUNTERS_EX()
            counters.cb = ctypes.sizeof(counters)
            if not PSAPI.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                raise ctypes.WinError(ctypes.get_last_error())
            return counters.PrivateUsage
        finally:
            KERNEL.CloseHandle(handle)
else:
    def _private_bytes(pid):
        fields = {}
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            key, _, value = line.partition(":")
            fields[key] = value
        if "RssAnon" in fields:
            return int(fields["RssAnon"].split()[0]) * 1024
        return (int(fields["VmRSS"].split()[0]) - int(fields.get("RssFile", "0 kB").split()[0])) * 1024


def terminate_tree(pid):
    """Terminate a process and its descendants, children first; a reused PID is left alone."""
    errors = []
    for victim in reversed(process_tree(pid)):
        try:
            identity = process_identity(victim)
            if identity:
                terminate_process(identity)
        except (OSError, RuntimeError) as exc:
            errors.append(f"{victim}: {exc}")
    return errors


# ---------------------------------------------------------------------- job host

def job_host(job_dir):
    """Parent of one Lean process; records its identity and exit like the session host."""
    job_dir = Path(job_dir)
    launch = read_json(job_dir / "launch.json")
    while not (job_dir / "GO").exists():
        if (job_dir / "CANCEL").exists() or not alive(launch["broker"]):
            return 1
        time.sleep(0.1)
    result = {"exit_code": None}
    with (job_dir / "stdout.log").open("wb") as out, (job_dir / "stderr.log").open("wb") as err:
        child = None
        try:
            options = popen_options()
            if os.name == "nt":
                options["creationflags"] |= WINDOWS_PRIORITY[launch["priority"]]
            elif NICE[launch["priority"]]:
                # Set before exec so that every process Lean's command starts (lake, then lean) inherits it.
                # The host is single-threaded, so preexec_fn is safe here.
                options["preexec_fn"] = lambda: os.nice(NICE[launch["priority"]])
            started = time.time()
            child = subprocess.Popen(launch["argv"], cwd=launch["cwd"], env={**os.environ, **launch["env"]},
                                     stdin=subprocess.DEVNULL, stdout=out, stderr=err, shell=False, **options)
            write_json(job_dir / "process.json", {"process": process_identity(child.pid),
                       "pid": child.pid, "started_at": started})
        except OSError as exc:
            result["launch_error"] = str(exc)
        finally:
            if child is not None:
                result["exit_code"] = child.wait()
    result["finished_at"] = time.time()
    write_json(job_dir / "exit.json", result)
    return 0


# ------------------------------------------------------------------ calibration

class Calibration:
    """What compiles of each import closure have cost in this instance. Only the broker writes it."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = read_json(self.path) if self.path.exists() else {"entries": {}}
        self.dirty = False

    def entry(self, key):
        return self.data["entries"].get(key)

    def baseline(self, key):
        entry = self.entry(key)
        return entry["baseline_mb"] if entry and entry.get("baseline_mb") is not None else None

    def known(self, key):
        """Calibrated, or calibration tried and failed: either way no new calibration job is due."""
        return self.entry(key) is not None

    def record_baseline(self, key, identity, baseline_mb, import_seconds):
        """`identity` is what the key hashes, in readable form: imports, version, environment_key and direct."""
        entry = self.data["entries"].setdefault(key, {**identity, "excess_mb": [], "seconds": []})
        entry.update(baseline_mb=round(baseline_mb, 1), import_seconds=round(import_seconds, 1),
                     calibrated_at=time.time(), failed=None)
        self.dirty = True

    def record_failure(self, key, identity, exit_code, reason):
        """A calibration that did not succeed; compiles of this closure run on their own estimates."""
        entry = self.data["entries"].setdefault(key, {**identity, "excess_mb": [], "seconds": []})
        entry.update(baseline_mb=None, import_seconds=None, calibrated_at=time.time(),
                     failed={"exit_code": exit_code, "reason": reason})
        self.dirty = True

    def record_job(self, key, excess_mb, seconds):
        entry = self.entry(key)
        if entry is None:
            return
        entry["excess_mb"] = (entry["excess_mb"] + [round(excess_mb, 1)])[-HISTORY:]
        entry["seconds"] = (entry["seconds"] + [round(seconds, 1)])[-HISTORY:]
        self.dirty = True

    def spread(self, key):
        """The measured spread of the closure's excess relative to its mean; None until two samples."""
        entry = self.entry(key)
        excess = entry["excess_mb"] if entry else []
        if len(excess) < 2 or not statistics.fmean(excess):
            return None
        return statistics.pstdev(excess) / statistics.fmean(excess)

    def save(self):
        if self.dirty:
            write_json(self.path, self.data)
            self.dirty = False


# ------------------------------------------------------------------- admission

def reservation(expect_mb, baseline_mb, cv, current_mb=None):
    """(certain, mean, sd) in MiB for one job under the statistical-multiplexing rule (reference/lean.md).

    The baseline is certain: every compile of the closure reaches it. The estimate
    is read as the 90th percentile of the job's peak, so the elaboration excess above
    the baseline has mean m and spread cv*m with m + P90*cv*m = estimate - baseline;
    cv is the closure's measured spread or the configured default. A running job's
    measured memory replaces the certain part as it grows, and what the mean already
    predicted of that growth is no longer owed."""
    if baseline_mb is None:
        certain, mean, sd = float(expect_mb), 0.0, 0.25 * expect_mb
    else:
        excess = max(0.0, expect_mb - baseline_mb)
        mean = excess / (1 + P90 * cv)
        sd = cv * mean
        certain = float(baseline_mb)
    if current_mb is not None:
        grown = max(certain, current_mb)
        mean = max(0.0, certain + mean - grown)
        certain = grown
    return certain, mean, sd


def admission(running, candidate, budget_mb, z):
    """Whether the candidate fits beside the running reservations, and the total it would make.

    Floors are reserved in full, expected excesses are summed, and the spreads are
    pooled: z * sqrt(sum of variances), so N uncertain compiles need about sqrt(N)
    times one safety margin rather than N times."""
    rows = list(running) + [candidate]
    total = (sum(r[0] for r in rows) + sum(r[1] for r in rows)
             + z * math.sqrt(sum(r[2] ** 2 for r in rows)))
    return total <= budget_mb, total


# ----------------------------------------------------------------------- broker

class Broker:
    def __init__(self, instance, log_path=None):
        self.paths = Paths(instance)
        self.paths.ensure()
        self.log_path = log_path  # None: stderr, which `serve` has redirected to broker.log
        self.identity = process_identity(os.getpid())
        self.settings = None
        self.config = None
        self.config_error = None
        self.direct = None  # {"argv", "env"} to run lean without lake in front of it, once lake's environment is known
        self.settings_stamp = None
        # start() reads the saved state under the lock; this is the state of an instance that has none yet.
        self.state = {"jobs": {}, "builds": {}, "version": None}
        self.calibration = Calibration(self.paths.calibration)
        self.hosts = {}
        self.dirty = False
        self.samples_dirty = False
        self.last_sample_save = 0.0
        self.runner_stamp = None
        self.runner_state = None
        self.last_sessions_check = 0.0

    # --- plumbing

    def log(self, **fields):
        line = json.dumps({"at": time.time(), **fields}, ensure_ascii=True)
        if self.log_path is None:
            print(line, file=sys.stderr, flush=True)
        else:
            with open(self.log_path, "a", encoding="utf-8") as stream:
                stream.write(line + "\n")

    def save(self):
        self.calibration.save()
        if self.samples_dirty and time.monotonic() - self.last_sample_save >= SAMPLE_SAVE_SECONDS:
            self.dirty = True
        if self.dirty:
            write_json(self.paths.state, self.state)
            self.dirty = self.samples_dirty = False
            self.last_sample_save = time.monotonic()

    def reload_settings(self):
        """Apply settings.json whenever it changes; keep the last good configuration on error."""
        path = self.paths.instance / "settings.json"
        try:
            stamp = file_stamp(path)
        except OSError as exc:
            stamp = None
            error = str(exc)
        if stamp == self.settings_stamp and self.config_error is None:
            return
        self.settings_stamp = stamp
        try:
            if stamp is None:
                raise ValueError(error)
            settings = load_settings(self.paths.instance)
            config = lean_config(settings)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # Re-read on every poll while rejected: a file caught mid-write may not change its stamp
            # again. Logged once per distinct error; the last valid configuration stays in force.
            if str(exc) != self.config_error:
                self.config_error = str(exc)
                self.state["config_error"] = self.config_error
                self.dirty = True
                self.log(event="settings_rejected", error=self.config_error)
            return
        self.settings, self.config, self.config_error = settings, config, None
        environment = {key: settings['lean'][key] for key in ('command', 'cwd', 'env', 'cache_epoch')}
        self.state['environment_key'] = hashlib.sha256(json.dumps(environment, sort_keys=True).encode('utf-8')).hexdigest()[:16]
        self.state.update(config=config, config_error=None)
        self.dirty = True
        self.log(event="settings_applied", config=config)
        self.capture_environment()

    def capture_environment(self):
        """With `lake env lean …` configured, ask lake once for the environment it gives lean.

        Every later compile then runs lean directly in that environment, sparing the
        workspace load that lake repeats per compile (reference/lean.md). If this fails, the
        configured command stays in force, so no compile depends on it working."""
        command = list(self.settings["lean"]["command"])
        self.direct = None
        split = command.index("env") if "env" in command[1:] else 0  # lake and its options before, lean after
        if not split or split == len(command) - 1:
            self.state["launcher"] = {"direct": False, "reason": "the command is not of the form lake [options] env lean"}
            return
        # Resolve inside Lake's environment and cwd. On Windows Popen's env PATH
        # does not control the executable search for a bare command name.
        probe = command[:split + 1] + [sys.executable, "-c",
            "import json, os, shutil, sys; p = shutil.which(sys.argv[1]); "
            "print(json.dumps({'env': dict(os.environ), 'executable': os.path.abspath(p) if p else None}))",
            command[split + 1]]
        given = self.lean_env()
        try:
            result = subprocess.run(probe, cwd=self.lean_cwd(None), env=given, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, encoding="utf-8", errors="replace", timeout=300,
                                    **popen_options())
            if result.returncode:
                raise RuntimeError(f"exit code {result.returncode}: {result.stderr.strip()[:500]}")
            payload = json.loads(result.stdout)
            captured = payload['env']
            executable = payload['executable']
            if not executable:
                raise RuntimeError(f"cannot resolve executable in Lake environment: {command[split + 1]}")
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            self.state["launcher"] = {"direct": False, "reason": str(exc)}
            self.log(event="environment_failed", error=str(exc))
            return
        delta = {k: v for k, v in captured.items() if given.get(k) != v}
        argv = [executable, *command[split + 2:]]
        self.direct = {"argv": argv, "env": delta}
        self.state["launcher"] = {"direct": True, "argv": argv, "variables": sorted(delta),
                                  "captured_at": time.time()}
        self.log(event="environment_captured", variables=sorted(delta))

    def read_version(self):
        """The version string every calibration entry is tagged with; None if not obtained."""
        lean = self.settings["lean"]
        try:
            result = subprocess.run(lean["version_command"], cwd=self.lean_cwd(None), env=self.lean_env(),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8",
                                    errors="replace", timeout=300, **popen_options())
            if result.returncode:
                raise RuntimeError(f"exit code {result.returncode}: {result.stdout.strip()}")
            version = result.stdout.strip()
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            self.state.update(version=None, version_error=str(exc))
            self.log(event="version_failed", error=str(exc))
        else:
            self.state.update(version=version, version_error=None)
        self.dirty = True

    def lean_cwd(self, session):
        configured = self.settings["lean"]["cwd"]
        if configured:
            return configured
        if session and session != BROKER_SESSION and (self.paths.instance / "sessions" / session).is_dir():
            return str(self.paths.instance / "sessions" / session)
        return str(self.paths.sources)

    def lean_env(self):
        return {**os.environ, **self.settings["lean"]["env"]}

    def environment_identity(self):
        """The Lean version and environment_key in one string: the environment that calibration closures and module cache keys belong to."""
        return (self.state['version'] or '') + '\n' + self.state['environment_key']

    def runner_sessions(self):
        path = self.paths.instance / "runner/state.json"
        try:
            stamp = file_stamp(path)
            if stamp != self.runner_stamp:
                self.runner_state = read_json(path)
                self.runner_stamp = stamp
        except (OSError, ValueError):
            return None
        return self.runner_state

    # --- queue

    def ingest(self):
        for path in sorted(self.paths.queue.glob("*.json"), key=lambda p: (p.stat().st_mtime_ns, p.name)):
            job_id = path.stem
            try:
                if not JOB_ID.fullmatch(job_id) and not BUILD_ID.fullmatch(job_id):
                    raise ValueError(f"not a job ID: {job_id}")
                folder = self.paths.build(job_id) if BUILD_ID.fullmatch(job_id) else self.paths.job(job_id)
                # Registration or a final outcome can be durable while its queue
                # file remains after a crash. Acknowledge it without registering
                # again, replacing its outcome or redirecting the ID to itself.
                if job_id in self.state["jobs"] or job_id in self.state["builds"] \
                        or (folder / "result.json").exists():
                    path.unlink(missing_ok=True)
                    continue
                request = read_json(path)
                if request.get("id") != job_id:
                    raise ValueError("the request's id does not match its file name")
                expect = request["expect_mb"]
                if type(expect) is not int or expect < 1:
                    raise ValueError("expect_mb must be a positive integer")
                # Fields kept in the broker state must have the shapes the scheduler and the orphan
                # check rely on; a request that fails here is answered, not left to crash a later tick.
                if request.get("session") is not None and not isinstance(request["session"], str):
                    raise ValueError("session must be a session ID")
                if "submitted_at" in request and (type(request["submitted_at"]) not in (int, float)
                                                  or not math.isfinite(request["submitted_at"])):
                    raise ValueError("submitted_at must be a finite number")
                if (folder / "CANCEL").exists():
                    write_json(folder / "result.json", {"id": job_id, "status": "cancelled",
                               "session": request.get("session"), "reason": "cancelled on request",
                               "finished_at": time.time()})
                    path.unlink(missing_ok=True)
                    self.log(event="cancelled", job=job_id, reason="cancelled before registration")
                    continue
                if BUILD_ID.match(job_id):
                    self.ingest_build(job_id, request)
                    path.unlink(missing_ok=True)
                    continue
                source = request["source"]
                if not isinstance(source, str):
                    raise ValueError("source must be a path")
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                self.log(event="request_rejected", file=path.name, error=str(exc))
                folder = self.paths.build(job_id) if BUILD_ID.fullmatch(job_id) else \
                    self.paths.job(job_id) if JOB_ID.fullmatch(job_id) else None
                if folder is not None:
                    folder.mkdir(exist_ok=True)
                    write_json(folder / "result.json",
                               {"id": job_id, "status": "failed", "reason": f"request rejected: {exc}"})
                path.unlink(missing_ok=True)
                continue
            job_dir = self.paths.job(job_id)
            job_dir.mkdir(exist_ok=True)
            try:
                source_hash = request.get("source_sha256") or hashlib.sha256(Path(source).read_bytes()).hexdigest()
            except (OSError, ValueError):  # unreadable, or a path with a character the OS rejects
                source_hash = None
            # A module compile of a build runs with -R, -o and the build's lib on the search path;
            # a single-file submission of the same bytes is a different compile, not its duplicate.
            duplicate = next((jid for jid, j in self.state["jobs"].items()
                              if j["status"] in ACTIVE and j["session"] == request.get("session")
                              and j["source"] == source and j["kind"] == "compile" and not j.get("build")
                              and source_hash is not None and j.get("source_sha256") == source_hash
                              and j["environment_key"] == self.state["environment_key"]), None)
            if duplicate:
                write_json(job_dir / "result.json", {"id": job_id, "status": "duplicate", "duplicate_of": duplicate})
                if (job_dir / "CANCEL").exists():
                    cancel(self.paths, duplicate)
                path.unlink(missing_ok=True)
                continue
            try:
                imports = read_imports(source)
            except (OSError, ValueError) as exc:
                imports = []
                self.log(event="imports_unreadable", job=job_id, error=str(exc))
            job = self.new_job(job_id, request, source, imports, imports, source_sha256=source_hash)
            write_json(job_dir / "job.json", job)
            self.state["jobs"][job_id] = job
            if (job_dir / "CANCEL").exists():
                self.cancel(job, "cancelled on request")
            self.dirty = True
            self.save()
            path.unlink(missing_ok=True)
            self.log(event=job["status"], job=job_id, session=job["session"], expect_mb=expect, imports=len(imports))

    def ingest_build(self, build_id, request):
        """Expand a build request into one job per module that is not already in the cache.

        Modules are discovered from the targets' import headers; cached ones are copied
        into the build's own lib folder, the rest become jobs chained by `deps`. A build
        whose modules are all cached is complete at once. Any error here fails the
        whole build with its reason (an import cycle, a shadowing name, an unreadable
        file), since no module compile could make it right."""
        root, targets, session = request["root"], request["targets"], request.get("session") or "unknown"
        folder = self.paths.build(build_id)
        folder.mkdir(exist_ok=True)
        lib = folder / "lib"
        build = {"id": build_id, "session": session, "root": root, "targets": [], "lib": str(lib),
                 "expect_mb": request["expect_mb"], "submitted_at": request.get("submitted_at", time.time()),
                 "status": "queued", "modules": {}, "finished_at": None, "reason": None}
        jobs = {}
        try:
            build["targets"] = [module_name(root, t) for t in targets]
            modules = discover_modules(root, targets)
            keys = module_keys(self.environment_identity(), modules)
            build.update(module_keys=keys, fresh_targets=bool(request.get("fresh_targets")))
            duplicate = next((b for b in self.state["builds"].values() if b["status"] in ACTIVE
                              and b["session"] == session and b["root"] == root
                              and b["targets"] == build["targets"] and b["module_keys"] == keys
                              and b["fresh_targets"] == build["fresh_targets"]), None)
            if duplicate:
                write_json(folder / "result.json", {"id": build_id, "status": "duplicate", "duplicate_of": duplicate["id"]})
                if (folder / "CANCEL").exists():
                    cancel(self.paths, duplicate["id"])
                return
            for name, module in modules:
                olean = lib.joinpath(*name.split(".")).with_suffix(".olean")
                entry = {"key": keys[name], "source": module["source"], "source_sha256": module['source_sha256'], "job": None, "status": None,
                         "exit_code": None, "olean": str(olean)}
                if not (request.get("fresh_targets") and name in build["targets"]) and self.restore_module(keys[name], olean):
                    entry.update(status="cached", exit_code=0)
                else:
                    job_id = "j" + uuid.uuid4().hex
                    deps = [jobs[d] for d in module["local"] if d in jobs]
                    job = self.new_job(job_id, request, module["source"], module["imports"], module["external"],
                                       build=build_id, module=name, root=root, lib=str(lib), olean=str(olean),
                                        deps=deps, key=keys[name], source_sha256=module['source_sha256'])
                    self.paths.job(job_id).mkdir(exist_ok=True)
                    write_json(self.paths.job(job_id) / "job.json", job)
                    self.state["jobs"][job_id] = job
                    jobs[name] = job_id
                    entry.update(job=job_id, status="queued")
                build["modules"][name] = entry
        except (OSError, ValueError) as exc:
            build.update(status="failed", reason=str(exc), finished_at=time.time())
            for job_id in jobs.values():
                self.cancel(self.state["jobs"][job_id], f"build {build_id} failed: {exc}")
            self.log(event="build_failed", build=build_id, session=session, reason=str(exc))
        self.state["builds"][build_id] = build
        write_json(folder / "build.json", build)
        self.dirty = True
        if build["status"] == "queued":
            if (folder / "CANCEL").exists():
                for job_id in jobs.values():
                    job = self.state["jobs"][job_id]
                    if job["status"] in ACTIVE:
                        self.cancel(job, "build cancelled on request")
            self.log(event="build_queued", build=build_id, session=session, modules=len(build["modules"]),
                     cached=sum(m["status"] == "cached" for m in build["modules"].values()))
            self.settle_build(build)
        else:
            write_json(folder / "result.json", build)
        self.save()

    def settle_build(self, build):
        """Close a build after its modules end, retaining an explicit build cancellation."""
        if build["status"] not in ACTIVE:
            return
        modules = build["modules"]
        if (self.paths.build(build["id"]) / "CANCEL").exists():
            build["cancel_requested"] = True
            build["reason"] = "cancelled on request"
        if any(m["status"] in ACTIVE for m in modules.values()):
            return
        broken = next((n for n, m in modules.items() if m["status"] == "failed"), None) \
            or next((n for n, m in modules.items() if m["status"] == "cancelled"), None)
        if build.get("cancel_requested"):
            build["status"] = "cancelled"
        elif broken is None:
            build["status"] = "finished"
        else:
            build["status"] = modules[broken]["status"]
            build["reason"] = f"module {broken} {modules[broken]['status']}: {modules[broken].get('reason')}"
        build["finished_at"] = time.time()
        write_json(self.paths.build(build["id"]) / "result.json", build)
        self.dirty = True
        self.log(event="build_" + build["status"], build=build["id"], session=build["session"], reason=build["reason"])

    def new_job(self, job_id, request, source, imports, external, source_sha256, **extra):
        """A queued compile job; `external` imports alone key its calibration closure.

        `source_sha256` is the hash the caller has already read, or None when the source
        could not be read; the job does not read the source a second time."""
        session = request.get("session") or "unknown"
        return {"id": job_id, "kind": "compile", "session": session, "source": source,
                "source_sha256": source_sha256,
                'lean_version': self.state['version'], 'environment_key': self.state['environment_key'],
                "cwd": self.lean_cwd(session), "expect_mb": request["expect_mb"], "imports": imports,
                "external": external, "closure": closure_key(self.environment_identity(), external, self.direct is not None),
                "threads": self.config["threads"], "submitted_at": request.get("submitted_at", time.time()),
                "status": "queued", "waiting_for": None, "passed": 0, "started_at": None, "finished_at": None,
                "host": None, "lean": None, "pid": None, "measured": None, "reserve": None,
                "exit_code": None, "launch_error": None, "reason": None, **extra}

    def calibration_job(self, closure, imports):
        """An imports-only compile whose peak is the closure's baseline; real jobs wait for it."""
        job_id = "c" + uuid.uuid4().hex
        source = self.paths.sources / (closure + ".lean")
        source.write_text("".join(f"import {name}\n" for name in imports) or "-- no imports\n", encoding="utf-8")
        job = {"id": job_id, "kind": "calibration", "session": BROKER_SESSION, "source": str(source),
               "environment_key": self.state['environment_key'], "direct": self.direct is not None,
               "cwd": self.lean_cwd(None), "expect_mb": self.config["calibration_expect_mb"], "imports": imports,
               "closure": closure, "threads": 1, "submitted_at": time.time(), "status": "queued",
               "waiting_for": None, "passed": 0, "started_at": None, "finished_at": None, "host": None,
               "lean": None, "pid": None, "measured": None, "reserve": None, "exit_code": None,
               "launch_error": None, "reason": None}
        self.paths.job(job_id).mkdir(exist_ok=True)
        write_json(self.paths.job(job_id) / "job.json", job)
        self.state["jobs"][job_id] = job
        self.dirty = True
        self.log(event="calibration_queued", job=job_id, closure=closure, imports=imports)
        return job

    # --- sampling and collection

    def sample(self, job):
        """Read the private memory of the job's process tree; every poll, so short compiles are caught at their peak."""
        measured = job["measured"]
        if not job.get("pid") or not alive(job.get("lean")):
            return
        current = round(private_memory_mb(process_tree(job["pid"])), 1)
        measured["sampled_at"] = time.time()
        if current != measured["current_mb"]:
            measured["current_mb"] = current
            measured["peak_mb"] = max(measured["peak_mb"], current)
            self.samples_dirty = True

    def collect(self):
        # A host can end just after the poll that finished its job. Every ended host is reaped here,
        # whatever became of its job, so that no Popen keeps a finished job's host process (a zombie
        # on POSIX, an open handle on Windows) for the rest of the broker's life.
        for job_id, host in list(self.hosts.items()):
            if host.poll() is not None:
                del self.hosts[job_id]
        for build in list(self.state["builds"].values()):
            if build["status"] in ACTIVE and (self.paths.build(build["id"]) / "CANCEL").exists():
                build["cancel_requested"] = True
                build["reason"] = "cancelled on request"
                for module in build["modules"].values():
                    job = self.state["jobs"].get(module.get("job"))
                    if job and job["status"] in ACTIVE and not job.get("cancel_requested"):
                        self.cancel(job, "build cancelled on request")
                self.settle_build(build)
        for job_id, job in list(self.state["jobs"].items()):
            if job["status"] in ACTIVE and not job.get("cancel_requested") \
                    and (self.paths.job(job_id) / "CANCEL").exists():
                self.cancel(job, "cancelled on request")
            if job["status"] != "running":
                continue
            job_dir = self.paths.job(job_id)
            receipt = job_dir / "process.json"
            if job.get("lean") is None and receipt.exists():
                try:
                    data = read_json(receipt)
                except (OSError, ValueError):
                    continue  # the host is still writing it (Windows refuses a read mid-replace); next poll
                job.update(lean=data["process"], pid=data["pid"], started_at=data["started_at"])
                self.dirty = True
            if job.get("cancel_requested") and not job.get("terminated") and job.get("pid") and alive(job.get("lean")):
                job["terminated"] = True
                self.dirty = True
                errors = terminate_tree(job["pid"])
                if errors:
                    self.log(event="terminate_errors", job=job_id, errors=errors)
            self.sample(job)
            if (job_dir / "exit.json").exists():
                self.finish(job, read_json(job_dir / "exit.json"))
            elif not alive(job.get("host")) and not alive(job.get("lean")):
                # The host writes exit.json just before it ends, so the exit may have appeared since the
                # check above; only a host that ended without one fails the job.
                if (job_dir / "exit.json").exists():
                    self.finish(job, read_json(job_dir / "exit.json"))
                else:
                    self.finish(job, {"exit_code": None, "launch_error": "the job host ended without recording an exit"})

    def finish(self, job, exit_info):
        now = exit_info.get("finished_at") or time.time()
        job["finished_at"] = now
        job["exit_code"] = exit_info.get("exit_code")
        job["launch_error"] = exit_info.get("launch_error")
        measured = job["measured"] = job["measured"] or {"peak_mb": 0.0, "current_mb": 0.0, "seconds": None}
        measured["seconds"] = round(now - (job["started_at"] or now), 1)
        baseline = self.calibration.baseline(job["closure"])
        if job["kind"] == "calibration":
            # What the closure key hashes, in readable form: a session matching its imports against the
            # table compares `environment_key` and `direct` with what `status` reports as environment_key
            # and launcher.direct, since the key itself is a hash it cannot recompute.
            identity = {"imports": job["imports"], "version": self.state["version"],
                        "environment_key": job["environment_key"], "direct": job["direct"]}
            if job["exit_code"] == 0:
                self.calibration.record_baseline(job["closure"], identity, measured["peak_mb"], measured["seconds"])
            elif job["exit_code"] is not None and 0 < job["exit_code"] < 2 ** 31 and not job.get("cancel_requested"):
                # Lean ran and rejected the imports: a verdict on the closure, kept until the Lean changes.
                self.calibration.record_failure(job["closure"], identity, job["exit_code"],
                                                "the calibration compile failed; see its stdout.log")
            else:
                # A launch error, a cancellation or a crash records nothing, so the next compile calibrates
                # again. A crash is a negative code (a POSIX signal) or a Windows code of 2**31 and above
                # (0xC0000005 and the like): an execution failure, not Lean's verdict on the imports.
                # The compiles that waited for this one go ahead on their own estimates rather than
                # wait for another calibration that might fail the same way.
                for waiting in self.state["jobs"].values():
                    if waiting["status"] == "queued" and waiting.get("waiting_for") == job["id"]:
                        waiting["uncalibrated"] = job["id"]
            measured["baseline_mb"] = measured["peak_mb"]
        elif baseline is not None:
            measured["baseline_mb"] = baseline
            measured["excess_mb"] = round(max(0.0, measured["peak_mb"] - baseline), 1)
            if job["exit_code"] is not None and not job.get("cancel_requested"):
                self.calibration.record_job(job["closure"], measured["excess_mb"], measured["seconds"])
        if job["kind"] == "compile" and job["exit_code"] is not None and measured["peak_mb"] > 0:
            # Reported so that the session sees how its estimate did; the broker does not act on it.
            measured["estimate_ratio"] = round(measured["peak_mb"] / job["expect_mb"], 2)
        if job.get("cancel_requested"):
            job["status"] = "cancelled"
        elif job["exit_code"] is None:
            job["status"] = "failed"
            job["reason"] = job["launch_error"] or "no exit code was recorded"
        else:
            job["status"] = "finished"
        if job.get("build"):
            self.finish_module(job)
        write_json(self.paths.job(job["id"]) / "result.json", job)
        self.dirty = True
        self.log(event=job["status"], job=job["id"], session=job["session"], exit_code=job["exit_code"],
                 measured=measured)
        self.prune()

    def finish_module(self, job):
        """Record a module's outcome in its build, keep a successful .olean in the cache, settle the build."""
        if job["status"] == "finished" and job["exit_code"] == 0:
            if Path(job["olean"]).is_file():
                self.cache_module(job["key"], Path(job["olean"]), self.paths.job(job["id"]))
            else:
                job.update(status="failed", reason="Lean exited with code 0 but wrote no .olean")
        build = self.state["builds"].get(job["build"])
        if build is None:
            return
        build["modules"][job["module"]].update(status=job["status"], exit_code=job["exit_code"],
                                               reason=job.get("reason"), measured=job.get("measured"))
        self.settle_build(build)

    def restore_module(self, key, olean):
        """Restore every emitted file; an entry whose manifest was never published (its caching was cut short) or that lacks a listed file is a miss."""
        try:
            suffixes = read_json(self.paths.cache / (key + ".artifacts.json")).get("artifacts")
        except (OSError, ValueError, AttributeError):
            return False
        if not isinstance(suffixes, list) or ".olean" not in suffixes or not all(
                isinstance(s, str) and len(s) > 1 and s.startswith(".")
                and not any(c in s for c in ('/', '\\', ':', '\0')) for s in suffixes):
            return False
        if not all((self.paths.cache / (key + suffix)).is_file() for suffix in suffixes):
            return False
        olean.parent.mkdir(parents=True, exist_ok=True)
        for suffix in suffixes:
            shutil.copyfile(self.paths.cache / (key + suffix), olean.with_name(olean.stem + suffix))
        return True

    def cache_module(self, key, olean, job_dir):
        """Preserve a module's emitted files and logs; publish its file list last."""
        artifacts = [(p.name[len(olean.stem):], p) for p in sorted(olean.parent.glob(olean.stem + ".*"))
                     if p.is_file()]
        for suffix, source in artifacts + [(".stdout.log", job_dir / "stdout.log"),
                                           (".stderr.log", job_dir / "stderr.log")]:
            target = self.paths.cache / (key + suffix)
            if target.exists() or not source.is_file():
                continue
            temporary = self.paths.cache / f".{key}{suffix}.{uuid.uuid4().hex}"
            try:
                shutil.copyfile(source, temporary)
                os.replace(temporary, target)
            except OSError as exc:
                temporary.unlink(missing_ok=True)
                self.log(event="cache_skipped", key=key, file=target.name, error=str(exc))
                return
        try:
            write_json(self.paths.cache / (key + ".artifacts.json"),
                       {"artifacts": [suffix for suffix, _ in artifacts]})
        except OSError as exc:
            self.log(event="cache_skipped", key=key, error=str(exc))

    def prune(self):
        """Keep the KEEP_FINISHED most recently finished jobs and builds in the state; result.json files stay.

        A finished job that a queued job still imports is kept, whatever its age. A
        pruned build loses its lib folder, which no compile reads once the build is over."""
        needed = {d for j in self.state["jobs"].values() if j["status"] in ACTIVE for d in j.get("deps", [])}
        finished = sorted((j for j in self.state["jobs"].values() if j["status"] in FINISHED and j["id"] not in needed),
                          key=lambda j: j["finished_at"] or 0)
        for job in finished[:-KEEP_FINISHED] if len(finished) > KEEP_FINISHED else []:
            del self.state["jobs"][job["id"]]
        builds = sorted((b for b in self.state["builds"].values() if b["status"] in FINISHED),
                        key=lambda b: b["finished_at"] or 0)
        for build in builds[:-KEEP_FINISHED] if len(builds) > KEEP_FINISHED else []:
            del self.state["builds"][build["id"]]
            target = Path(build['lib']).resolve()
            if not target.is_relative_to(self.paths.builds.resolve()) or target.name != 'lib':
                raise ValueError('build library cleanup escapes the broker build directory')
            shutil.rmtree(target, ignore_errors=True)

    def deps_done(self, job):
        """True when every module this job imports has been compiled with exit code 0."""
        return all(self.state["jobs"].get(d, {}).get("status") == "finished"
                   and self.state["jobs"][d].get("exit_code") == 0 for d in job.get("deps", []))

    def propagate(self):
        """A queued job whose import ended without a usable .olean cannot compile; close it with the reason."""
        for job in list(self.state["jobs"].values()):
            if job["status"] != "queued":
                continue
            for dep_id in job.get("deps", []):
                dep = self.state["jobs"].get(dep_id)
                usable = dep is not None and (dep["status"] not in FINISHED
                                              or (dep["status"] == "finished" and dep["exit_code"] == 0))
                if usable:
                    continue
                why = "is unknown" if dep is None else dep["status"] if dep["status"] != "finished" \
                    else f"ended with exit code {dep['exit_code']}"
                self.finish(job, {"exit_code": None,
                                  "launch_error": f"dependency {dep.get('module', dep_id) if dep else dep_id} {why}"})
                break

    def cancel(self, job, reason):
        job["cancel_requested"] = True
        job["reason"] = reason
        self.dirty = True
        if job["status"] == "queued":
            job["finished_at"] = time.time()
            job["status"] = "cancelled"
            job["measured"] = job["measured"] or {"peak_mb": 0.0, "current_mb": 0.0, "seconds": 0.0}
            if job.get("build"):
                self.finish_module(job)
            write_json(self.paths.job(job["id"]) / "result.json", job)
            self.log(event="cancelled", job=job["id"], reason=reason)
            return
        # collect() terminates the process tree once the Lean identity is known.
        (self.paths.job(job["id"]) / "CANCEL").touch()
        self.log(event="cancelling", job=job["id"], reason=reason)

    def cancel_orphans(self):
        """A job whose session has ended has no reader; its compile only costs memory."""
        now = time.monotonic()
        if now - self.last_sessions_check < 1.0:
            return
        self.last_sessions_check = now
        state = self.runner_sessions()
        if not state:
            return
        sessions = state.get("sessions", {})
        for job in self.state["jobs"].values():
            if job["status"] not in ACTIVE or job["session"] == BROKER_SESSION or job.get("cancel_requested"):
                continue
            session = sessions.get(job["session"])
            if session is None:
                continue
            if session["status"] in ("ended", "integrated", "failed", "publishing"):
                self.cancel(job, f"session {job['session']} ended ({session['status']})")
            elif session["status"] == "running" and session.get("cli") is not None \
                    and not alive(session.get("host")) and not alive(session.get("cli")):
                self.cancel(job, f"session {job['session']} is no longer alive")

    # --- scheduling

    def reserve(self, job):
        baseline = self.calibration.baseline(job["closure"]) if job["kind"] == "compile" else None
        expect = max(job["expect_mb"], baseline or 0)
        cv = (self.calibration.spread(job["closure"]) if baseline is not None else None) \
            or self.config["default_spread"]
        current = (job["measured"] or {}).get("current_mb", 0.0) if job["status"] == "running" else None
        certain, mean, sd = reservation(expect, baseline, cv, current)
        job["reserve"] = {"expected_mb": round(expect, 1), "certain_mb": round(certain, 1),
                          "mean_mb": round(mean, 1), "sd_mb": round(sd, 1)}
        return certain, mean, sd

    def fits(self, job, running, free_mb):
        """The memory rule, the thread budget and the machine gate, all at once.

        A job that exceeds a budget on its own still runs, alone: refusing it
        forever would be a kill policy by another name (reference/lean.md)."""
        config = self.config
        rows = [self.reserve(r) for r in running]
        certain, mean, sd = self.reserve(job)
        ok, total = admission(rows, (certain, mean, sd), config["memory_budget_mb"], config["confidence"])
        job["reserve"]["total_mb"] = round(total, 1)
        if running and not ok:
            return False
        if running and sum(r["threads"] for r in running) + job["threads"] > config["cpu_threads_budget"]:
            return False
        return free_mb - certain >= config["min_free_memory_mb"]

    def schedule(self):
        """First fit in submission order, with aging: a job passed `max_passes` times closes the queue behind it."""
        jobs = self.state["jobs"]
        def order(job):
            return job["kind"] != "calibration", job["submitted_at"]
        queued = sorted((j for j in jobs.values() if j["status"] == "queued"), key=order)
        stale = [j for j in queued if j['environment_key'] != self.state['environment_key']]
        for job in stale:
            self.finish(job, {'exit_code': None, 'launch_error': 'Lean environment changed while queued; resubmit in the current environment'})
        queued = [j for j in queued if j['status'] == 'queued']
        direct = self.direct is not None
        for job in queued:
            # A queued compile starts with the lean.threads in force, as it does with the priority;
            # a running one keeps the threads it started with (reference/lean.md, Settings).
            if job["kind"] == "compile" and job["threads"] != self.config["threads"]:
                job["threads"] = self.config["threads"]
                self.dirty = True
            # A queued job is keyed by the launch mode in force as well. A settings change or a restart
            # asks lake again (capture_environment) and can switch between lake and direct launch without
            # changing environment_key; a baseline or an excess measured in one mode must not be recorded
            # under the other mode's key. A queued calibration follows the compiles waiting for it.
            imports = job["external"] if job["kind"] == "compile" else job["imports"]
            closure = closure_key(self.environment_identity(), imports, direct)
            if job["closure"] != closure:
                job["closure"] = closure
                if job["kind"] == "calibration":
                    job["direct"] = direct
                self.dirty = True
        running = [j for j in jobs.values() if j["status"] == "running"]
        if not queued:
            return
        pending_calibration = {j["closure"]: j["id"] for j in jobs.values()
                               if j["kind"] == "calibration" and j["status"] in ACTIVE}
        created = []
        for job in queued:
            if job["kind"] != "compile" or self.calibration.known(job["closure"]) or job.get("uncalibrated"):
                job["waiting_for"] = None
                continue
            if job["closure"] not in pending_calibration:
                # Only the external imports are calibrated: a local module's .olean exists in no
                # calibration, and its cost is small beside the library's and is measured as excess.
                calibration = self.calibration_job(job["closure"], job["external"])
                pending_calibration[job["closure"]] = calibration["id"]
                created.append(calibration)
            job["waiting_for"] = pending_calibration[job["closure"]]
        # Calibrations created here join the queue in creation order, behind those already waiting,
        # as they will on the next tick.
        queued = sorted(queued + created, key=order)
        eligible = [j for j in queued if not j.get("waiting_for") and self.deps_done(j)]
        if not eligible:
            return
        try:
            free_mb = available_memory() / MIB
        except OSError as exc:
            self.log(event="memory_unreadable", error=str(exc))
            return
        for index, job in enumerate(eligible):
            if self.fits(job, running, free_mb):
                for passed in eligible[:index]:
                    passed["passed"] += 1
                self.launch(job)
                return
            if job["passed"] >= self.config["max_passes"]:
                return  # nothing behind this job starts until it has

    def launch(self, job):
        job_dir = self.paths.job(job["id"])
        if (job_dir / "CANCEL").exists() or (job.get("build") and
                (self.paths.build(job["build"]) / "CANCEL").exists()):
            self.cancel(job, "cancelled on request")
            return
        lean = self.settings["lean"]
        if self.direct:  # lean itself, in the environment lake gave once; see capture_environment
            command, env = self.direct["argv"], {**lean["env"], **self.direct["env"]}
        else:
            command, env = lean["command"], dict(lean["env"])
        argv = list(command) + [f"--threads={job['threads']}"]
        if job.get("olean"):
            # A module of a build: named from its root, written as .olean into the build's lib,
            # which goes on the search path so that the modules built before it are found.
            argv += ["-R", job["root"], "-o", job["olean"]]
            env["LEAN_PATH"] = os.pathsep.join(
                p for p in (job["lib"], env.get("LEAN_PATH") or os.environ.get("LEAN_PATH")) if p)
        argv.append(job["source"])
        job["measured"] = {"peak_mb": 0.0, "current_mb": 0.0, "seconds": None}
        job["status"] = "running"
        job["started_at"] = time.time()
        if job.get("build") in self.state["builds"]:
            build = self.state["builds"][job["build"]]
            build["modules"][job["module"]]["status"] = build["status"] = "running"
        self.dirty = True
        try:
            if not Path(job["source"]).is_file():
                raise OSError(f"source does not exist: {job['source']}")
            if job.get('source_sha256') and hashlib.sha256(Path(job['source']).read_bytes()).hexdigest() != job['source_sha256']:
                raise OSError('source changed after submission; submit the completed source again')
            if job.get("olean"):
                Path(job["olean"]).parent.mkdir(parents=True, exist_ok=True)
            write_json(job_dir / "launch.json", {"argv": argv, "cwd": job["cwd"], "env": env,
                                                 "priority": self.config["priority"], "broker": self.identity})
            with (job_dir / "host.log").open("ab") as log:
                host = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "_job", str(job_dir)],
                                        cwd=job_dir, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                        **popen_options(detached=True))
            self.hosts[job["id"]] = host
            job["host"] = process_identity(host.pid)
            self.save()
            # No Lean may start until its host's identity is durable, as for the session host.
            (job_dir / "GO").write_bytes(b"go\n")
        except OSError as exc:
            (job_dir / "CANCEL").touch()  # a host started before the failure must not wait for GO
            self.finish(job, {"exit_code": None, "launch_error": str(exc)})
            return
        self.log(event="started", job=job["id"], session=job["session"], reserve=job["reserve"],
                 threads=job["threads"], passed=job["passed"])

    # --- lifecycle

    def should_exit(self):
        state = self.runner_sessions()
        if not state or not state.get("finished"):
            return False
        if any(s["status"] in ("starting", "running", "publishing") for s in state.get("sessions", {}).values()):
            return False
        return not any(j["status"] in ACTIVE for j in self.state["jobs"].values())

    def adopt(self):
        """Jobs left by a previous broker.

        A running job is followed by identity and its exit read from the job host,
        never relaunched. A job whose host never received GO has not started Lean:
        its host exits on CANCEL and the job goes back to the queue."""
        # A copy: finishing a job below can prune older finished jobs from the state.
        for job_id, job in list(self.state["jobs"].items()):
            if job["status"] != "running":
                continue
            job_dir = self.paths.job(job_id)
            if not (job_dir / "GO").exists():
                cancelled = (job_dir / "CANCEL").exists()  # a client's request, not ours: honour it
                (job_dir / "CANCEL").touch()
                deadline = time.monotonic() + 2.0
                while alive(job.get("host")) and time.monotonic() < deadline:
                    time.sleep(0.05)
                if alive(job.get("host")):
                    self.finish(job, {"exit_code": None, "launch_error": "an unstarted job host did not exit"})
                    continue
                (job_dir / "launch.json").unlink(missing_ok=True)
                job.update(status="queued", host=None, lean=None, pid=None, started_at=None, measured=None)
                if cancelled:
                    self.cancel(job, "cancelled on request")
                    continue
                (job_dir / "CANCEL").unlink(missing_ok=True)
                self.log(event="requeued", job=job_id, reason="Lean had not started")
                continue
            self.log(event="adopted", job=job_id, host=job.get("host"), lean=job.get("lean"))

    def tick(self):
        self.reload_settings()
        if self.config is None:
            return
        self.collect()
        self.ingest()
        self.cancel_orphans()
        self.propagate()
        self.schedule()
        self.save()

    def start(self):
        """Everything a broker does before serving: settings, version, the jobs a predecessor left."""
        self.state = read_json(self.paths.state) if self.paths.state.exists() else self.state
        # The version a predecessor recorded belongs to the installation it ran. `version` and `status`
        # read this file while this broker is still starting (restart-broker returns once it is alive),
        # so nothing is reported as the version until this broker has run version_command itself.
        self.state.update(version=None, version_error=None)
        self.dirty = True
        self.save()
        self.reload_settings()
        if self.config is None:
            raise ValueError("settings.json rejected: " + str(self.config_error))
        self.read_version()
        self.adopt()
        self.dirty = True
        self.save()

    def serve(self):
        with InstanceLock(self.paths.lock, "Lean broker"):
            # Alive from this moment: clients may queue requests while the broker finishes starting.
            write_json(self.paths.process, {"process": self.identity, "started_at": time.time()})
            self.start()
            print(json.dumps({"started": self.identity, "instance": str(self.paths.instance)}), flush=True)
            while True:
                self.tick()
                if self.should_exit():
                    self.log(event="exit", reason="instance complete and no session active")
                    return 0
                time.sleep(POLL)


# ----------------------------------------------------------------------- client

def broker_alive(paths):
    try:
        info = read_json(paths.process)
        return info if alive(info["process"]) else None
    except (OSError, ValueError, KeyError):
        return None


def ensure_broker(paths):
    """The live broker's receipt, launching one if none is alive; the lock settles any race."""
    info = broker_alive(paths)
    if info:
        return info
    paths.ensure()
    argv = [sys.executable, "-B", str(SCRIPT), "serve", str(paths.instance)]
    with paths.log.open("ab") as log:
        # A session's client may start the shared broker; it must not join that session's job and
        # end with it. A caller in a job that forbids breakaway starts it as before.
        try:
            subprocess.Popen(argv, cwd=paths.instance, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                             **popen_options(detached=True, breakaway=True))
        except PermissionError:
            subprocess.Popen(argv, cwd=paths.instance, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                             **popen_options(detached=True))
    deadline = time.monotonic() + READY_SECONDS
    while time.monotonic() < deadline:
        info = broker_alive(paths)
        if info:
            return info
        time.sleep(0.1)
    raise RuntimeError(f"No Lean broker became ready; read {paths.log}")


def submit(paths, source, expect_mb, session):
    source = Path(source).resolve()
    if not source.is_file():
        raise ValueError(f"source file does not exist: {source}")
    if type(expect_mb) is not int or expect_mb < 1:
        raise ValueError("--expect-mb must be a positive integer: your probable peak private memory in MiB")
    if not isinstance(session, str) or not session.strip():
        raise ValueError("--session must be your session ID")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    ensure_broker(paths)
    job_id = "j" + uuid.uuid4().hex
    request = {"id": job_id, "source": str(source), "expect_mb": expect_mb, "session": session,
               "source_sha256": source_hash, "submitted_at": time.time()}
    temporary = paths.queue / ("." + job_id)
    write_json(temporary, request)
    temporary.rename(paths.queue / (job_id + ".json"))
    return {"job": job_id, "dir": str(paths.job(job_id)), "session": session, "expect_mb": expect_mb}


def build(paths, root, targets, expect_mb, session, fresh_targets=False):
    """Queue a build of the targets and the local modules they import; the broker reads the headers."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f"module root is not a folder: {root}")
    names = []
    for target in targets:
        target = Path(target)
        target = (target if target.is_absolute() else root / target).resolve()
        if not target.is_file():
            raise ValueError(f"target does not exist: {target}")
        names.append(module_name(root, target))  # also rejects a target outside the root
    if not names:
        raise ValueError("at least one target file is required")
    if type(expect_mb) is not int or expect_mb < 1:
        raise ValueError("--expect-mb must be a positive integer: the probable peak private memory of one module compile in MiB")
    if not isinstance(session, str) or not session.strip():
        raise ValueError("--session must be your session ID")
    ensure_broker(paths)
    build_id = "b" + uuid.uuid4().hex
    request = {"id": build_id, "kind": "build", "root": str(root), "targets": [str(module_path(root, n)) for n in names], "fresh_targets": fresh_targets,
               "expect_mb": expect_mb, "session": session, "submitted_at": time.time()}
    temporary = paths.queue / ("." + build_id)
    write_json(temporary, request)
    temporary.rename(paths.queue / (build_id + ".json"))
    return {"build": build_id, "dir": str(paths.build(build_id)), "session": session, "expect_mb": expect_mb,
            "targets": names}


def job_record(paths, job_id):
    """The job's or build's current record from the result or the broker state, or None if unknown."""
    is_build = BUILD_ID.match(job_id) is not None
    result = (paths.build(job_id) if is_build else paths.job(job_id)) / "result.json"
    if result.exists():
        return read_json(result)
    if paths.state.exists():
        record = read_json(paths.state).get("builds" if is_build else "jobs", {}).get(job_id)
        if record:
            return record
    if (paths.queue / (job_id + ".json")).exists():
        return {"id": job_id, "status": "submitted"}
    return None


def wait(paths, job_id, timeout=None):
    """Relay the finished job's output and exit code; 124 if the timeout passed first."""
    deadline = None if timeout is None else time.monotonic() + timeout
    checked = 0.0
    while True:
        record = job_record(paths, job_id)
        if record is None:
            raise ValueError(f"unknown job: {job_id}")
        if record["status"] == "duplicate":
            job_id = record["duplicate_of"]
            continue
        if record["status"] in FINISHED:
            break
        if time.monotonic() - checked > 2.0:
            ensure_broker(paths)
            checked = time.monotonic()
        if deadline is not None and time.monotonic() >= deadline:
            print(json.dumps({"job": job_id, "status": record["status"], "timeout": True,
                              "hint": f"the job continues; run wait {job_id} again"}), file=sys.stderr, flush=True)
            return 124
        time.sleep(POLL)
    if BUILD_ID.match(job_id):
        return report_build(paths, record)
    job_dir = paths.job(job_id)
    relay(job_dir / "stdout.log", job_dir / "stderr.log")
    summary = {"job": job_id, "status": record["status"], "exit_code": record.get("exit_code"),
               "reason": record.get("reason"), "expect_mb": record.get("expect_mb"),
               "measured": record.get("measured"), "dir": str(job_dir)}
    print("lean-broker: " + json.dumps(summary, ensure_ascii=True), file=sys.stderr, flush=True)
    if record["status"] == "finished":
        return record["exit_code"]
    return 3 if record["status"] == "failed" else 4


def relay(stdout_log, stderr_log):
    """Lean's bytes, unchanged, on our own streams."""
    for path, stream in ((stdout_log, sys.stdout), (stderr_log, sys.stderr)):
        if path.exists():
            stream.flush()
            data = path.read_bytes()
            if getattr(stream, "buffer", None) is not None:
                stream.buffer.write(data)
            else:
                stream.write(data.decode("utf-8", errors="replace"))
            stream.flush()


def report_build(paths, build):
    """Relay each target's Lean output, cached or fresh, then one summary line for the whole build."""
    modules = build.get("modules", {})
    for name in build.get("targets", []):
        entry = modules.get(name) or {}
        if entry.get("job"):
            relay(paths.job(entry["job"]) / "stdout.log", paths.job(entry["job"]) / "stderr.log")
        elif entry.get("status") == "cached":
            relay(paths.cache / (entry["key"] + ".stdout.log"), paths.cache / (entry["key"] + ".stderr.log"))
    rows = [{"module": name, "status": m.get("status"), "exit_code": m.get("exit_code"),
             "cached": m.get("status") == "cached", "reason": m.get("reason"),
             "measured": {k: (m.get("measured") or {}).get(k) for k in ("peak_mb", "seconds")}}
            for name, m in modules.items()]
    # Successful modules must not mask negative subprocess return codes.
    exit_codes = [m["exit_code"] for m in modules.values() if m.get("exit_code") not in (None, 0)]
    summary = {"build": build["id"], "status": build["status"], "exit_code": max(exit_codes, default=0),
               "reason": build.get("reason"), "targets": build.get("targets", []), "modules": rows,
               "dir": str(paths.build(build["id"]))}
    print("lean-broker: " + json.dumps(summary, ensure_ascii=True), file=sys.stderr, flush=True)
    if build["status"] == "finished":
        return summary["exit_code"]
    return 3 if build["status"] == "failed" else 4


def cancel(paths, job_id):
    is_build = BUILD_ID.fullmatch(job_id) is not None
    folder = paths.build(job_id) if is_build else paths.job(job_id)
    key = "build" if is_build else "job"
    record = job_record(paths, job_id)
    if record and record["status"] == "duplicate":
        return cancel(paths, record["duplicate_of"])
    if record and record["status"] in FINISHED:
        return {key: job_id, "status": record["status"], "cancelled": "already completed"}
    if record is None and not folder.is_dir():
        raise ValueError(f"unknown {key}: {job_id}")
    folder.mkdir(exist_ok=True)
    # Ingestion may already hold the request; keep both the request and its cancellation.
    (folder / "CANCEL").touch()
    latest = job_record(paths, job_id)
    if latest and latest["status"] == "duplicate":
        return cancel(paths, latest["duplicate_of"])
    if latest and latest["status"] in FINISHED:
        return {key: job_id, "status": latest["status"], "cancelled": "already completed"}
    return {key: job_id, "cancelled": "requested"}


def broker_status(paths):
    info = broker_alive(paths)
    state = read_json(paths.state) if paths.state.exists() else {}
    jobs = state.get("jobs", {})
    return {"instance": str(paths.instance), "broker": info, "broker_alive": bool(info),
            'environment_key': state.get('environment_key'),
            "config": state.get("config"), "config_error": state.get("config_error"),
            "version": state.get("version"), "version_error": state.get("version_error"),
            "launcher": state.get("launcher"),
            "queued": [{k: j.get(k) for k in ("id", "kind", "session", "expect_mb", "waiting_for", "passed", "reserve")}
                       for j in jobs.values() if j["status"] == "queued"],
            "running": [{k: j.get(k) for k in ("id", "kind", "session", "expect_mb", "started_at", "reserve", "measured")}
                        for j in jobs.values() if j["status"] == "running"],
            "finished": [{k: j.get(k) for k in ("id", "kind", "session", "status", "exit_code", "expect_mb", "measured")}
                         for j in sorted((j for j in jobs.values() if j["status"] in FINISHED),
                                         key=lambda j: j["finished_at"] or 0)][-20:],
            "builds": [{"id": b["id"], "session": b["session"], "status": b["status"], "targets": b["targets"],
                        "modules": {s: sum(m["status"] == s for m in b["modules"].values())
                                    for s in ("cached", "queued", "running", "finished", "failed", "cancelled")}}
                       for b in state.get("builds", {}).values() if b["status"] in ACTIVE
                       or b["finished_at"] and b["finished_at"] > time.time() - 600],
            "calibration": str(paths.calibration), "cache": str(paths.cache)}


def version(paths):
    ensure_broker(paths)
    deadline = time.monotonic() + READY_SECONDS
    while time.monotonic() < deadline:
        state = read_json(paths.state) if paths.state.exists() else {}
        if "version" in state and (state["version"] is not None or state.get("version_error")):
            return {"version": state["version"], "error": state.get("version_error")}
        time.sleep(POLL)
    raise RuntimeError("the broker has not reported a version yet")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("submit", "run", "build", "wait", "result", "status", "cancel", "version", "serve", "_job"):
        sub = commands.add_parser(name)
        if name == "_job":
            sub.add_argument("job_dir", type=Path)
            continue
        sub.add_argument("instance", type=Path)
        if name in ("submit", "run"):
            sub.add_argument("source", type=Path)
        if name == "build":
            sub.add_argument("root", type=Path, help="the module root: <root>/Foo/Bar.lean is the module Foo.Bar")
            sub.add_argument("targets", type=Path, nargs="+", help="the files to compile, with everything they import under the root")
            sub.add_argument("--fresh-targets", action="store_true", help="compile targets independently; reuse unchanged dependency modules")
            sub.add_argument("--no-wait", action="store_true", help="print the build ID and return; wait <build> later")
        if name in ("submit", "run", "build"):
            sub.add_argument("--expect-mb", type=int, required=True,
                             help="your probable peak private memory of one compile in MiB (reference/lean.md)")
            sub.add_argument("--session", required=True, help="your session ID, as given in your launch prompt")
        if name in ("wait", "result", "cancel"):
            sub.add_argument("job", help="a job ID or a build ID")
        if name in ("run", "build", "wait"):
            sub.add_argument("--timeout", type=float, help="seconds to wait before returning 124; the work continues")
    args = parser.parse_args(argv)
    try:
        if args.command == "_job":
            return job_host(args.job_dir)
        paths = Paths(args.instance)
        # Checked before serve as well: a broker started for an instance that has since been
        # deleted must not recreate its folders.
        if not (paths.instance / "runner").is_dir():
            raise ValueError(f"not a do-math instance: {paths.instance}")
        if args.command == "serve":
            return Broker(paths.instance).serve()
        if args.command in ("submit", "run"):
            receipt = submit(paths, args.source, args.expect_mb, args.session)
            if args.command == "submit":
                print(json.dumps(receipt, ensure_ascii=True))
                return 0
            print("lean-broker: " + json.dumps(receipt, ensure_ascii=True), file=sys.stderr, flush=True)
            return wait(paths, receipt["job"], args.timeout)
        if args.command == "build":
            receipt = build(paths, args.root, args.targets, args.expect_mb, args.session, args.fresh_targets)
            if args.no_wait:
                print(json.dumps(receipt, ensure_ascii=True))
                return 0
            print("lean-broker: " + json.dumps(receipt, ensure_ascii=True), file=sys.stderr, flush=True)
            return wait(paths, receipt["build"], args.timeout)
        if args.command == "wait":
            return wait(paths, args.job, args.timeout)
        if args.command == "result":
            record = job_record(paths, args.job)
            if record is None:
                raise ValueError(f"unknown job: {args.job}")
            print(json.dumps(record, ensure_ascii=True, indent=2))
            return 0
        if args.command == "status":
            print(json.dumps(broker_status(paths), ensure_ascii=True, indent=2))
            return 0
        if args.command == "cancel":
            print(json.dumps(cancel(paths, args.job), ensure_ascii=True))
            return 0
        if args.command == "version":
            print(json.dumps(version(paths), ensure_ascii=True))
            return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    code = main()
    # Windows gives a process's exit code as an unsigned 32-bit value, so a crashed Lean's
    # NTSTATUS code (0xC0000005 and the like) exceeds the C long that SystemExit accepts and
    # would end this client with an OverflowError instead. The same 32 bits in signed form
    # reach the caller as Lean's own code.
    raise SystemExit(code - 2 ** 32 if os.name == "nt" and code >= 2 ** 31 else code)
