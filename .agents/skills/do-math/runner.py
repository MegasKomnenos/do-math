"""Run a do-math instance. User commands and recovery contract: RUNTIME.md."""

import argparse
from contextlib import AbstractContextManager
import ctypes
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import uuid

from check import check_session
from cli_adapter import build_command, detect_usage_limit, provider_for_model
from knowledge_index import render_index


SKILL = Path(__file__).resolve().parent
SCRIPT = Path(__file__).resolve()
# Consecutive failed plans before dispatch halts; limit-detected failures wait instead.
# Raise it if transient CLI failures halt healthy instances; restart resets the count.
PLAN_FAILURE_LIMIT = 3


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    """Replace one state file atomically; readers see either complete version."""
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_text(path, content):
    """Publish a complete UTF-8 file with the same Windows sharing retry."""
    path = Path(path)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    # Windows readers may briefly hold the destination without delete sharing.
    # Retry only that replacement; keep the old complete state until it succeeds.
    deadline = time.monotonic() + 1.0
    while True:
        try:
            os.replace(temp, path)
            break
        except OSError as exc:
            if (os.name != "nt" or getattr(exc, "winerror", None) not in (5, 32, 33)
                    or time.monotonic() >= deadline):
                raise
            time.sleep(0.05)


class InstanceLock(AbstractContextManager):
    """OS lock, released by process death; the lock file itself stays in place."""
    def __init__(self, path):
        self.path = Path(path)
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
            raise RuntimeError("This instance already has a running runner") from exc
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
    return bool(identity) and process_identity(identity["pid"]) == identity


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


def popen_options(detached=False):
    if os.name == "nt":
        flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                 if detached else subprocess.CREATE_NO_WINDOW)
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


def load_settings(instance):
    settings = read_json(instance / "settings.json")
    if type(settings.get("max_sessions")) is not int or settings["max_sessions"] < 1:
        raise ValueError("max_sessions must be a positive integer")
    seconds = settings.get("limit_wait_seconds")
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("limit_wait_seconds must be positive and finite")
    for category in ("plan", "research", "explore", "review"):
        default = settings["defaults"][category]
        provider = provider_for_model(default["model"])
        build_command(settings["cli"][provider], default["model"], default["effort"], instance)
    lean = settings["lean"]
    for key in ("command", "version_command"):
        if not isinstance(lean[key], list) or not lean[key] or not all(
                isinstance(v, str) and v.strip() for v in lean[key]):
            raise ValueError(f"lean.{key} must be a nonempty string array")
    if lean["cwd"] is not None and not Path(lean["cwd"]).is_absolute():
        raise ValueError("lean.cwd must be absolute or null")
    if not isinstance(lean["env"], dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in lean["env"].items()):
        raise ValueError("lean.env must be a string mapping")
    return settings


def initialize(instance, goal, settings):
    """Create a fresh instance, own Git, and the one initial planning event."""
    goal_bytes, settings_bytes = Path(goal).read_bytes(), Path(settings).read_bytes()
    if not goal_bytes.decode("utf-8-sig").strip():
        raise ValueError("goal must be nonempty UTF-8 text")
    instance.mkdir(parents=True, exist_ok=False)
    for name in ("knowledge", "sessions", "runner", "control/inputs"):
        (instance / name).mkdir(parents=True)
    (instance / "goal.md").write_bytes(goal_bytes)
    (instance / "settings.json").write_bytes(settings_bytes)
    load_settings(instance)
    write_text(instance / "knowledge/index.md", render_index([]))
    (instance / ".gitignore").write_bytes(b"/sessions/\n/runner/\n/control/\n")
    git(instance, "init")
    git(instance, "add", "--", "goal.md", "settings.json", ".gitignore", "knowledge/index.md")
    git(instance, "commit", "-m", "Initialize research goal and settings")
    write_json(instance / "runner/state.json", {
        "events": [{"kind": "start"}], "requests": {}, "sessions": {},
        "seen_inputs": [], "input_errors": {}, "wait": None,
        "limit_until": 0, "complete": None,
        "last_plan": None, "plan_failures": 0, "halted": None,
    })


def session_host(session):
    """Keep a CLI handle across runner death; never restart a CLI.

    The runner durably records this host's identity BEFORE enabling its gate.
    An unrecorded host cannot start a CLI, even if its parent dies mid-spawn.
    """
    job = read_json(session / "launch.json")
    while not (session / "GO").exists():
        if (session / "CANCEL").exists() or not alive(job["runner"]):
            return 1
        time.sleep(0.1)
    command = job["command"]
    result = {"exit_code": None}
    with (session / "prompt.txt").open("rb") as inp, \
            (session / "cli.stdout.jsonl").open("wb") as out, \
            (session / "cli.stderr.log").open("wb") as err:
        child = None
        try:
            started = time.time()
            child = subprocess.Popen(command["argv"], cwd=command["cwd"],
                                     stdin=inp, stdout=out, stderr=err, shell=False,
                                     **popen_options())
            identity = process_identity(child.pid)
            write_json(session / "process.json", {"process": identity,
                       "pid": child.pid, "started_at": started})
        except OSError as exc:
            result["launch_error"] = str(exc)
        finally:
            if child is not None:
                result["exit_code"] = child.wait()
    write_json(session / "exit.json", result)
    return 0


class Runner:
    def __init__(self, instance, skill=SKILL):
        self.instance = Path(instance).resolve()
        self.skill = Path(skill).resolve()
        if not (self.instance / ".git").is_dir():
            raise ValueError("Instance must have its own .git directory; use init")
        self.settings = load_settings(self.instance)
        self.state_path = self.instance / "runner/state.json"
        self.state = read_json(self.state_path)
        self.identity = process_identity(os.getpid())
        self.hosts = {}

    def save(self):
        write_json(self.state_path, self.state)

    def session_dir(self, sid):
        return self.instance / "sessions" / sid

    def refresh_index(self, commit=True):
        paths = {p.parent.name: p for p in (self.instance / 'knowledge').glob('*/output.json')}
        # Publication commits preserve order across rebuilds, copies and restarts.
        history = git(self.instance, 'log', '--reverse', '--format=%s', '--', 'knowledge')
        ordered = dict.fromkeys(line[8:] for line in history.splitlines()
                                if line.startswith('Publish ') and line[8:] in paths)
        if commit:
            for rid in paths.keys() - ordered.keys():
                if not git(self.instance, 'log', '-1', '--format=%H', '--', 'knowledge/' + rid):
                    raise RuntimeError('Uncommitted publication; start the runner to recover before rebuilding the index')
        # A newly copied record has not been committed yet; append it once.
        for rid in sorted(paths, key=lambda r: (paths[r].parent.stat().st_mtime_ns, r)):
            ordered.setdefault(rid, None)
        records = [(rid, read_json(paths[rid])) for rid in ordered]
        plans = [rid for rid, data in records if data['category'] == 'plan']
        # Only the latest plan's files are current; an older copy would mislead.
        latest = paths[plans[-1]].parent if plans else None
        status, glossary = (plans[-1] if latest and (latest / name).is_file() else None
                            for name in ('research-status.md', 'glossary.md'))
        content = render_index(records, status, glossary)
        path = self.instance / 'knowledge/index.md'
        if not path.exists() or path.read_bytes() != content.encode('utf-8'):
            write_text(path, content)
        if commit:
            git(self.instance, 'add', '--', 'knowledge/index.md')
            if git(self.instance, 'diff', '--cached', '--name-only', '--', 'knowledge/index.md'):
                git(self.instance, 'commit', '--only', '-m', 'Refresh knowledge index', '--', 'knowledge/index.md')
        return path

    def active(self):
        return [(sid, s) for sid, s in self.state["sessions"].items()
                if s["status"] in ("starting", "running", "publishing")]

    def enqueue(self, key, category, task, origin, selection=None):
        self.state["requests"].setdefault(key, {
            "category": category, "task": task, "origin": origin,
            "selection": selection or {}, "status": "pending", "session": None})

    def ingest_inputs(self):
        # File names are random; submission order is the content write time.
        paths = [p for p in (self.instance / "control/inputs").iterdir()
                 if not p.name.startswith(".") and p.name not in self.state["seen_inputs"]]
        # Report only the current scan's input failures.
        self.state["input_errors"] = {}
        for path in sorted(paths, key=lambda p: (p.stat().st_mtime_ns, p.name)):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
                if not text.strip():
                    raise ValueError("input must contain nonempty UTF-8 text")
            except (OSError, UnicodeError, ValueError) as exc:
                self.state["input_errors"][path.name] = str(exc)
                continue
            self.state["seen_inputs"].append(path.name)
            self.state["events"].append({"kind": "user_input", "text": text})
            self.state["wait"] = None

    def dispatch(self, category, task, request=None):
        sid = "s" + uuid.uuid4().hex
        session = self.session_dir(sid)
        session.mkdir()
        (session / "output").mkdir()
        common = [self.skill / "common.md", self.skill / "protocol.md", self.instance / "goal.md"]
        data = {"instance": str(self.instance), "category": category,
                "context": {"common": [str(p) for p in common],
                            "category": str(self.skill / (category + ".md"))}, "task": task}
        write_json(session / "input.json", data)
        prompt = (f"당신은 do-math의 {category} 세션이다. 자기 세션 폴더: {session}\n"
                  f"{session / 'input.json'}의 context.common, context.category, task를 모두 읽고 수행하라.\n"
                  f"축적 지식의 진입점은 {self.instance / 'knowledge/index.md'}다. "
                  f"필요한 원문과 검토는 {self.instance / 'knowledge'}에서 읽는다. "
                  f"Lean 등 설정은 {self.instance / 'settings.json'}에서 읽는다.\n"
                  "새 파일과 수정 파일은 자기 세션 폴더 안에만 둔다. "
                  "공개할 산출 전체는 output/에 작성하라.\n"
                  f"산출을 정리한 뒤 다음 argv의 공식 검사 명령을 실행하고 오류를 고친 뒤 끝내라:\n"
                  f"{json.dumps([sys.executable, str(self.skill / 'check.py'), str(session)], ensure_ascii=False)}\n")
        if category == "plan":
            prompt += (f"이미 게시된 미완료 요청과 대체 의도는 {self.state_path}의 requests에서 읽는다. "
                       f"읽는 법과 상태 의미는 {self.skill / 'RUNTIME.md'}를 따른다.\n")
        (session / "prompt.txt").write_bytes(prompt.encode("utf-8"))
        selected = dict(self.settings["defaults"][category])
        if request:
            selected.update(self.state["requests"][request]["selection"])
        s = {"category": category, "request": request, "status": "starting",
             "model": selected["model"], "effort": selected["effort"],
             "started_at": time.time(), "host": None, "record": None}
        self.state["sessions"][sid] = s
        if request:
            self.state["requests"][request].update(status="assigned", session=sid)
        else:
            self.state["events"] = []
        # Intent, consumed events and assignment are one durable transaction.
        self.save()
        try:
            provider = provider_for_model(selected["model"])
            s["provider"] = provider
            if provider not in self.settings["cli"]:
                raise ValueError(f"settings.cli has no {provider} executable")
            command = build_command(self.settings["cli"][provider], selected["model"], selected["effort"], session)
            write_json(session / "launch.json", {"runner": self.identity,
                       "command": {"argv": command.argv, "cwd": str(command.cwd)}})
            with (session / "host.log").open("wb") as log:
                host = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "_session", str(session)],
                                        stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                        cwd=session, **popen_options(detached=True))
            self.hosts[sid] = host
            s["host"] = process_identity(host.pid)
            s["status"] = "running"
            self.save()
            # No CLI may run until its durable host identity exists in state.
            (session / "GO").write_bytes(b"go\n")
        except (OSError, ValueError) as exc:
            s["launch_error"] = str(exc)
            self.save()

    def finish(self, sid, s):
        session = self.session_dir(sid)
        if s["status"] != "publishing":
            if not s.get("logs_checked"):
                try:
                    if s.get("provider"):
                        limit = detect_usage_limit(
                            s["provider"], session / "cli.stdout.jsonl", session / "cli.stderr.log",
                            now=time.time(), fallback_seconds=self.settings["limit_wait_seconds"],
                            session_started_at=s.get("cli_started_at", s["started_at"]))
                        if limit:
                            s["limit"] = {"retry_at": limit.retry_at, "source": limit.source,
                                          "provider": limit.provider}
                            self.state["limit_until"] = max(self.state["limit_until"], limit.retry_at)
                except OSError as exc:
                    s["log_error"] = str(exc)
                s["logs_checked"] = True
                self.save()
            errors = check_session(session)
            if errors:
                reason = "; ".join(errors)
                if s.get("launch_error"):
                    reason = s["launch_error"] + "; " + reason
                s.update(status="failed", reason=reason)
                request = self.state["requests"].get(s["request"]) or {}
                if request:
                    request["status"] = "failed"
                # The event carries the original task, so a failed plan's consumed events survive.
                self.state["events"].append({
                    "kind": "session_failed", "session": sid, "reason": reason,
                    "category": s["category"], "request": s["request"],
                    "task": request.get("task") or read_json(session / "input.json")["task"],
                    "origin": request.get("origin"), "limit": s.get("limit"),
                    "exit_code": s.get("exit_code"), "launch_error": s.get("launch_error")})
                if s["category"] == "plan" and not s.get("limit"):
                    self.state["plan_failures"] += 1
                    if self.state["plan_failures"] >= PLAN_FAILURE_LIMIT:
                        self.state["halted"] = {"reason": f"{PLAN_FAILURE_LIMIT} consecutive plan failures; last: {reason}",
                                                "at": time.time()}
                self.save()
                return
            s.update(status="publishing", record="k" + uuid.uuid4().hex)
            self.save()
        record = s["record"]
        destination = self.instance / "knowledge" / record
        if destination.resolve().parent != (self.instance / "knowledge").resolve():
            raise ValueError("Publication destination escapes knowledge directory")
        if not destination.exists():
            # A partial copy is private; only a full directory rename publishes it.
            staging = self.instance / "runner" / ("stage-" + record)
            if staging.exists():
                if staging.resolve().parent != (self.instance / "runner").resolve():
                    raise ValueError("Publication staging path escapes runner directory")
                shutil.rmtree(staging)
            shutil.copytree(session / "output", staging)
            staging.rename(destination)
        relative = "knowledge/" + record
        self.refresh_index(commit=False)
        if not git(self.instance, "log", "-1", "--format=%H", "--", relative):
            git(self.instance, "add", "-f", "--", relative, "knowledge/index.md")
            git(self.instance, "commit", "--only", "-m", "Publish " + record, "--", relative, "knowledge/index.md")
        else:
            self.refresh_index()
        output = read_json(destination / "output.json")
        # Effects and the processed marker share one atomic state replacement.
        self.apply_output(s, record, output)
        s["status"] = "integrated"
        if s["request"]:
            self.state["requests"][s["request"]].update(status="finished", record=record)
        self.save()

    def apply_output(self, session, record, output):
        if output["category"] == "plan":
            for group, category, extra in (("research", "research", ("supersedes",)),
                                           ("explorations", "explore", ()), ("reviews", "review", ("target",))):
                for index, item in enumerate(output[group]):
                    keys = ("instructions", "references", *extra)
                    task = {key: item[key] for key in keys}
                    selection = {key: item[key] for key in ("model", "effort") if key in item}
                    self.enqueue(f"{record}:{group}:{index}", category, task, record, selection)
            item = output["goal_review"]
            if item is not None:
                self.enqueue(record + ":goal_review", "review",
                             {"instructions": item["instructions"], "references": item["references"],
                              "target": {"kind": "goal"}}, record,
                             {key: item[key] for key in ("model", "effort") if key in item})
            self.state.update(last_plan=record, plan_failures=0)
            # Inputs arriving while this plan ran have not been answered by it.
            self.state["wait"] = (None if any(e["kind"] == "user_input" for e in self.state["events"])
                                  else output["wait"])
        elif output["category"] == "research":
            self.enqueue(record + ":automatic_review", "review", {
                "instructions": "공개된 연구 산출 전체를 독립 검토하고 각 결과와 확인 범위를 판정하라.",
                "references": [], "target": {"kind": "research", "record": record}}, record)
        elif output["category"] == "explore":
            # Explorations are deliberately unreviewed; the next plan must still hear of them.
            self.state["events"].append({"kind": "exploration_finished", "record": record})
        else:
            self.state["events"].append({"kind": "review_finished", "record": record})
            if output["target"]["kind"] == "goal" and output["goal"]["verdict"] == "achieved":
                self.state["complete"] = record

    def collect(self):
        for sid, s in list(self.active()):
            session = self.session_dir(sid)
            host = self.hosts.get(sid)
            if host is not None and host.poll() is not None:
                # Reap children and release their OS handles during long runs.
                self.hosts.pop(sid, None)
            if s["status"] == "publishing":
                self.finish(sid, s)
                continue
            if not (session / "GO").exists():
                # Recovery of an interrupted launch: an unenabled host must
                # exit, even if an in-process caller reuses the runner object.
                (session / "CANCEL").touch()
            process_file = session / "process.json"
            if process_file.exists():
                data = read_json(process_file)
                s["cli"] = data["process"]
                s["pid"] = data["pid"]
                s["cli_started_at"] = data["started_at"]
            if alive(s.get("host")) or alive(s.get("cli")):
                continue
            if (session / "exit.json").exists():
                s.update(read_json(session / "exit.json"))
            self.finish(sid, s)

    def blocked(self):
        return dispatch_blocks(self.instance, self.state)

    def tick(self):
        self.collect()
        self.ingest_inputs()
        self.save()
        if self.blocked():
            return
        active = self.active()
        slots = self.settings["max_sessions"] - len(active)
        if slots > 0 and self.state["events"] and not any(s["category"] == "plan" for _, s in active):
            self.dispatch("plan", {"instructions": "사건과 축적 지식을 읽고 다음 연구·검토를 계획하라.",
                                   "references": [], "events": list(self.state["events"]),
                                   "previous_plan": self.state["last_plan"]})
            slots -= 1
        for key, request in self.state["requests"].items():
            if slots <= 0 or self.blocked():
                break
            if request["status"] == "pending":
                self.dispatch(request["category"], request["task"], key)
                slots -= 1

    def run(self, token=None):
        with InstanceLock(self.instance / "runner/lock"):
            # Load only after acquiring the lock, so a competing runner cannot
            # resume from an earlier state after the previous runner exits.
            self.state = read_json(self.state_path)
            # A restart is the human's signal that the halt's cause was addressed.
            self.state.update(halted=None, plan_failures=0)
            self.state.setdefault("last_plan", None)  # States written before these fields
            for name in ("common.md", "protocol.md", "plan.md", "research.md", "explore.md", "review.md", "RUNTIME.md", "check.py"):
                if not (self.skill / name).is_file():
                    raise ValueError(f"Missing session context/tool: {self.skill / name}")
            self.collect()
            self.refresh_index()
            write_json(self.instance / "runner/process.json", {
                "process": self.identity, "started_at": time.time(), "token": token})
            print(json.dumps({"started": self.identity, "instance": str(self.instance), "token": token}), flush=True)
            while True:
                self.tick()
                if (self.state["complete"] or self.state["halted"]) and not self.active():
                    return
                time.sleep(0.25)


def start(instance):
    """Detach, then verify this launch's readiness record and live identity."""
    token = uuid.uuid4().hex
    directory = instance / "runner"
    stdout = directory / ("start-" + token + ".stdout.log")
    stderr = directory / ("start-" + token + ".stderr.log")
    with stdout.open("wb") as out, stderr.open("wb") as err:
        child = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "run", str(instance), "--token", token],
                                 cwd=instance, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                 **popen_options(detached=True))
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        path = directory / "process.json"
        if path.exists():
            info = read_json(path)
            if info.get("token") == token and token in stdout.read_text(encoding="utf-8"):
                if alive(info["process"]) or read_json(directory / "state.json")["complete"]:
                    return {"pid": child.pid, "stdout": str(stdout), "stderr": str(stderr), "instance": str(instance)}
        if child.poll() is not None:
            raise RuntimeError(f"Runner exited before readiness; read {stderr}")
        time.sleep(0.05)
    raise RuntimeError(f"Readiness not yet confirmed (PID {child.pid}); inspect {stdout} and {stderr} before retrying")


def dispatch_blocks(instance, state):
    reasons = []
    if state["complete"]:
        reasons.append("complete")
    if state.get("halted"):
        reasons.append("halted")
    if (instance / "control/STOP").exists():
        reasons.append("STOP")
    if state["wait"]:
        reasons.append("external_input")
    if time.time() < state["limit_until"]:
        reasons.append("usage_limit")
    return reasons


def status(instance):
    state = read_json(instance / "runner/state.json")
    path = instance / "runner/process.json"
    runner = read_json(path) if path.exists() else None
    reasons = dispatch_blocks(instance, state)
    return {"instance": str(instance), "knowledge": str(instance / "knowledge"),
            "runner": runner, "runner_alive": bool(runner and alive(runner["process"])),
            "dispatch_blocks": reasons, "state": state}


def submit_input(instance, source):
    content = Path(source).read_bytes()
    if not content.decode("utf-8-sig").strip():
        raise ValueError("input must contain nonempty UTF-8 text")
    directory = instance / "control/inputs"
    name = uuid.uuid4().hex
    temporary = directory / ("." + name)
    temporary.write_bytes(content)
    destination = directory / (name + ".txt")
    temporary.rename(destination)
    return str(destination)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "start", "run", "status", "stop", "resume", "input", "index", "kill-session", "_session"):
        sub = commands.add_parser(name)
        sub.add_argument("instance", type=Path)
        if name == "init":
            sub.add_argument("--goal", required=True, type=Path)
            sub.add_argument("--settings", required=True, type=Path)
        if name == "run":
            sub.add_argument("--token")
        if name == "input":
            sub.add_argument("--file", required=True, type=Path)
        if name == "kill-session":
            sub.add_argument("session")
    args = parser.parse_args(argv)
    instance = args.instance.resolve()
    try:
        result = {"instance": str(instance)}
        if args.command == "_session":
            return session_host(instance)
        if args.command == "init":
            initialize(instance, args.goal, args.settings)
        elif args.command == "start":
            result = start(instance)
        elif args.command == "run":
            Runner(instance).run(args.token)
        elif args.command == "status":
            result = status(instance)
        elif args.command == "stop":
            (instance / "control/STOP").touch()
        elif args.command == "resume":
            (instance / "control/STOP").unlink(missing_ok=True)
        elif args.command == "input":
            result["input"] = submit_input(instance, args.file)
        elif args.command == "index":
            with InstanceLock(instance / "runner/lock"):
                result["index"] = str(Runner(instance).refresh_index())
        elif args.command == "kill-session":
            state = read_json(instance / "runner/state.json")
            if args.session not in state["sessions"]:
                raise ValueError("Unknown session ID")
            receipt = read_json(instance / "sessions" / args.session / "process.json")
            if not receipt["process"]:
                raise ValueError("CLI already exited before its identity was recorded")
            terminate_process(receipt["process"])
            result["terminated"] = args.session
        print(json.dumps(result, ensure_ascii=True))
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
