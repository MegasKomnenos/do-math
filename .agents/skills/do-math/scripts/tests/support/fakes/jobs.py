"""Fake Jobs port: a Job's program runs in process when the Job is resumed.

``programs`` is a list of ``(matches(argv), run(argv, cwd, env) -> exit code)``;
the first match runs. An argv no entry matches is an error rather than a silent
success, so a fake never hides a program the product started. Inspection after
the program returns shows the termination barrier the product waits for. The
launching owner is one fixed identity; a named Job is empty unless a launched,
unfinished Job carries that name.

By default a resumed program runs to its end inside ``resume``, so the runner's
poll loop first looks at a finished Job. With ``live`` set (이음매 장부 18) the
program runs on its own thread beside the runner, and the two take turns as the
calls fake's calculations and owner do: ``resume`` runs the program to its first
``job_turn()``, and each barrier probe (``inspect``) first gives the owner one
pass, when the runner is a call's calculation, then runs the program to its
next turn. So the runner's observations of a running program are live, and a
stop the owner requests reaches the program: ``terminate`` ends it at its turn,
where ``job_turn`` raises ``JobTerminated`` (a killed process does not run on).
``job_turn()`` outside a live program does nothing, so a program may call it
at every point a real process could be observed.
"""
import threading

from do_math.windows_job import JobInspection
from do_math.worker_request import validate_resource_limits
from support.fakes import calls

_ZERO_USAGE = {"limits": {"memory_bytes": None, "cpu_rate_basis_points": None},
               "peak_job_memory_bytes": 0, "cpu_time_100ns": 0,
               "scope": "local_job_commit_memory_and_cpu_cap_not_rss_or_remote_usage"}
_program = threading.local()


class JobTerminated(BaseException):
    """Raised at a live program's turn once its Job is terminated; a ``BaseException`` so no worker handler resumes it."""


def job_turn():
    """A live program hands its runner the turn until the runner's next barrier probe; nothing outside one."""
    job = getattr(_program, 'job', None)
    if job is not None:
        job._hand_back()


class FakeJob:
    def __init__(self, program, argv, cwd, env, name, resource_limits, pid, live=False):
        self.program, self.argv, self.cwd, self.env, self.name = program, list(argv), cwd, env, name
        self.resource_limits = validate_resource_limits(resource_limits)
        self.pid, self.creation_filetime = pid, 133_000_000_000_000_000 + pid
        self.resumed = self.done = self.closed = False
        self.exit_code = None
        self.live, self._thread, self._stopping = live, None, False

    def resume(self):
        if self.resumed:
            raise RuntimeError("root thread has already been resumed")
        self.resumed = True
        if self.done:
            return
        if not self.live:
            self.exit_code = self.program(self.argv, self.cwd, self.env)
            self.done = True
            return
        self._to_program, self._to_runner = threading.Semaphore(0), threading.Semaphore(0)
        # The program waits for its control receipt with ``owner_turn`` as the calculation it runs in would.
        turn = getattr(calls._current, 'turn', None)
        self._thread = threading.Thread(target=self._body, args=(turn,), name="do-math-fake-job", daemon=True)
        self._thread.start()
        self._step()

    def _body(self, turn):
        _program.job = self
        if turn is not None:
            calls._current.turn = turn
        self._to_program.acquire()
        try:
            code = self.program(self.argv, self.cwd, self.env)
            if not self._stopping:
                self.exit_code = code
        except JobTerminated:
            pass
        finally:
            self.done = True
            self._to_runner.release()

    def _step(self):
        """Runner: let the program run to its next turn or its end."""
        self._to_program.release()
        self._to_runner.acquire()

    def _hand_back(self):
        """Program: give the runner the turn; on return, end if the Job was terminated meanwhile."""
        self._to_runner.release()
        self._to_program.acquire()
        if self._stopping:
            raise JobTerminated()

    def _running(self):
        return self._thread is not None and not self.done

    def wait(self, timeout=None):
        return self.done

    def terminate(self, exit_code=1):
        if self.done:
            return
        self.exit_code = exit_code
        if self._running():
            self._stopping = True
            self._step()
        self.done = True

    def inspect(self):
        if self._running():
            if getattr(calls._current, 'turn', None) is not None:
                calls.owner_turn()
            if not self.done:
                self._step()
        return JobInspection(active_processes=0 if self.done else 1,
                             process_ids=() if self.done else (self.pid,), root_signaled=self.done)

    def resource_usage(self):
        usage = {**_ZERO_USAGE, "limits": dict(_ZERO_USAGE["limits"])}
        if self.resource_limits:
            usage["limits"] = {"memory_bytes": self.resource_limits.get("memory_bytes"),
                               "cpu_rate_basis_points": self.resource_limits.get("cpu_rate_basis_points")}
        return usage

    def close(self):
        if self._running():
            self.terminate()
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class FakeJobs:
    def __init__(self, programs=(), *, live=False):
        self.programs = list(programs)
        self.launched = []
        self.live = live
        self._next_pid = 40000  # per fake, so equal scenarios see equal process identities
        self.owner = {'pid': 4242, 'creation_filetime': '133000000000000000', 'host': 'fake-host', 'session': 1}

    def owner_identity(self):
        return dict(self.owner)

    def owner_ended(self, identity):
        if identity.get('host') != self.owner['host'] or identity.get('session') != self.owner['session']:
            return None
        if identity.get('pid') == self.owner['pid']:
            return identity.get('creation_filetime') != self.owner['creation_filetime']
        return None  # another live process of this fake host is not modelled

    def named_job_empty(self, name):
        jobs = [job for job in self.launched if job.name == name]
        return all(job.done for job in jobs)

    def launch(self, argv, *, cwd=None, env=None, name=None, resource_limits=None):
        program = next((run for matches, run in self.programs if matches(list(argv))), None)
        if program is None:
            raise LookupError("no fake program for argv: " + repr(list(argv)[:3]))
        self._next_pid += 4
        job = FakeJob(program, argv, cwd, env, name, resource_limits, self._next_pid, live=self.live)
        self.launched.append(job)
        return job


def make_fake(programs=()):
    return FakeJobs(programs)
