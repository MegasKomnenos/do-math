"""Real provider calls on the Jobs and clock port fakes: runner, adapter, worker and collector code all run.

Legacy provider tests put a scripted collector (``provider_fixtures.Adapter``)
or a ``Mock`` in the runner's adapter table, so the adapter's start, the
worker's request check, the CLI command and the collection never ran. Here the
only doubles are the two things outside the process (설계 2.2 "작업자와 외부
프로그램"): the Jobs port, whose Job runs its worker module in process, and the
provider CLI at the worker's ``spawn`` seam.

- ``ScriptedCLI(stdout=None, final=b'{}', returncode=0, timeout=False)``: the
  provider CLI. Each start is recorded in ``calls`` (``command``, ``env``,
  ``shell``, ``cwd``, ``creationflags`` and the ``stdin`` it was given). It
  writes ``stdout`` (default: a completed stream in the provider's own format
  whose final response is ``final``) and, for Codex, ``final`` to the
  ``--output-last-message`` file. ``timeout`` writes ``stdout`` and then lets
  the worker's wait time out, as a CLI past the request's runtime limit does.
- ``ProviderJobs(cli, ...)``: the Jobs fake whose programs run
  ``codex_worker.run`` and ``claude_worker.run`` with ``cli.spawn``. Each Job
  counts its ``inspections`` and ``terminations``. Options give the Job facts a
  test needs: ``polls`` (after its worker returned, a Job still reports a live
  process until that many inspections; a termination ends it), ``clock`` and
  ``advance`` (each inspection moves the fake clock, as a long call's time
  passes between polls), ``remaining`` (process IDs left in the Job after its
  root was signaled), ``refuse`` (the exception every launch raises, as
  ``WindowsJob`` does for an unsupported host or a taken Job name) and
  ``empty`` (answers of ``named_job_empty`` by Job name; ``None`` is unknown).
- ``model_runner(root, jobs, clock)``: the real ``ModelRunner`` on these fakes;
  its CLIs are ``root/codex.exe`` and ``root/claude.exe`` (never started).
- ``dispatched(execution_id, profile, jobs, clock)``: the dispatched launch
  ticket an owner hands a pinned runner (``launch.ticket`` on the Jobs port).
- ``codex_stream(final, usage)`` and ``claude_result(final, **fields)``: stream
  bytes of a completed call.
- ``fake_ports(clock, git_backend, jobs)``: a Ports bundle of fakes with these Jobs.
"""
import json
from pathlib import Path
import subprocess

from do_math import claude_worker, codex_worker, launch
from do_math.model_runner import ModelRunner
from do_math.windows_job import JobInspection
from support.fakes.jobs import FakeJob, FakeJobs

CLAUDE_INIT = {"type": "system", "subtype": "init", "session_id": "session-one"}


def codex_stream(final, usage=None):
    """A completed ``codex exec --json`` stream whose last agent message is ``final`` (bytes)."""
    events = [{"type": "thread.started", "thread_id": "thread-one"}, {"type": "turn.started"},
              {"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": final.decode("utf-8")}},
              {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1} if usage is None else usage}]
    return b"".join(json.dumps(event).encode("utf-8") + b"\n" for event in events)


def claude_result(final, *, structured=True, **fields):
    """A successful Claude result event whose output is ``final`` (bytes): structured, or result text."""
    output = {"structured_output": json.loads(final)} if structured else {"result": final.decode("utf-8")}
    return {"type": "result", "subtype": "success", "is_error": False, "session_id": CLAUDE_INIT["session_id"],
            "usage": {"input_tokens": 7, "output_tokens": 3}, **output, **fields}


def _rows(*events):
    return b"".join(json.dumps(event).encode("utf-8") + b"\n" for event in events)


def _default_stdout(command, final):
    if "--print" in command:  # a Claude print command; a schema requests the structured final
        return _rows(CLAUDE_INIT, claude_result(final, structured="--json-schema" in command))
    return codex_stream(final)


class ScriptedCLI:
    def __init__(self, *, stdout=None, final=b"{}", returncode=0, timeout=False):
        self.stdout, self.final, self.returncode, self.timeout = stdout, final, returncode, timeout
        self.calls = []

    def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
              creationflags=0):
        call = {"command": list(command), "env": dict(env or {}), "shell": shell, "cwd": cwd,
                "creationflags": creationflags}
        self.calls.append(call)
        return _Process(self, call, stdout)


class _Process:
    def __init__(self, cli, call, stdout):
        self.cli, self.call, self.stream = cli, call, stdout
        self.returncode, self.waited = None, False

    def communicate(self, input=None, timeout=None):
        if self.waited:  # the wait after a kill
            return None, None
        self.waited = True
        self.call["stdin"] = input
        command = self.call["command"]
        self.stream.write(self.cli.stdout if self.cli.stdout is not None else _default_stdout(command, self.cli.final))
        if "--output-last-message" in command:
            Path(command[command.index("--output-last-message") + 1]).write_bytes(self.cli.final)
        if self.cli.timeout:
            self.waited = False
            raise subprocess.TimeoutExpired(command, timeout)
        self.returncode = self.cli.returncode
        return None, None

    def kill(self):
        self.returncode, self.waited = 1, True


class ProviderJob(FakeJob):
    def __init__(self, jobs, *arguments):
        super().__init__(*arguments)
        self.jobs, self.inspections, self.terminations = jobs, 0, 0

    def terminate(self, exit_code=1):
        self.terminations += 1
        super().terminate(exit_code)

    def inspect(self):
        self.inspections += 1
        jobs = self.jobs
        if jobs.advance:
            jobs.clock.advance(jobs.advance)
        if self.done and not self.terminations and self.inspections < jobs.polls:
            return JobInspection(active_processes=1, process_ids=(self.pid,), root_signaled=False)
        if self.done and jobs.remaining:
            return JobInspection(active_processes=len(jobs.remaining), process_ids=tuple(jobs.remaining),
                                 root_signaled=True)
        return super().inspect()


def _worker_program(name, module, cli):
    return (lambda argv: Path(argv[1]).name == name,
            lambda argv, cwd, env: module.run(Path(argv[2]), spawn=cli.spawn))


class ProviderJobs(FakeJobs):
    def __init__(self, cli=None, *, clock=None, polls=0, advance=0, remaining=(), refuse=None):
        self.cli = cli or ScriptedCLI()
        super().__init__([_worker_program("codex_worker.py", codex_worker, self.cli),
                          _worker_program("claude_worker.py", claude_worker, self.cli)])
        self.clock, self.polls, self.advance, self.remaining, self.refuse = clock, polls, advance, remaining, refuse
        self.empty = {}

    def named_job_empty(self, name):
        return self.empty[name] if name in self.empty else super().named_job_empty(name)

    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        if self.refuse is not None:
            raise self.refuse
        program = next((run for matches, run in self.programs if matches(list(argv))), None)
        if program is None:
            raise LookupError("no fake program for argv: " + repr(list(argv)[:3]))
        self._next_pid += 4
        job = ProviderJob(self, program, argv, cwd, env, name, resource_limits, self._next_pid)
        self.launched.append(job)
        return job


def model_runner(root, jobs, clock):
    from support.entry import entry
    _entry = entry()
    return ModelRunner(codex_path=str(Path(root) / "codex.exe"), claude_path=str(Path(root) / "claude.exe"),
                       jobs=jobs, clock=clock, environment=_entry.environment, host_id=_entry.host_id)


def dispatched(execution_id, profile, jobs, clock):
    return launch.mark_dispatched(launch.ticket(execution_id, profile, jobs=jobs, clock=clock))


def fake_ports(clock, git_backend, jobs):
    from do_math.ports import Ports
    from support.fakes.calls import make_fake as fake_calls
    from support.fakes.host import make_fake as fake_host
    from support.fakes.http import make_fake as fake_http
    from support.fakes.scheduler import make_fake as fake_scheduler
    return Ports(clock=clock, git_backend=git_backend, calls=fake_calls(clock), jobs=jobs,
                 scheduler=fake_scheduler(), http=fake_http({}), host=fake_host())
