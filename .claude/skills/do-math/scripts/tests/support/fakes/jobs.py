"""Fake Jobs port: a Job's program runs in process, synchronously, when the Job is resumed.

``programs`` is a list of ``(matches(argv), run(argv, cwd, env) -> exit code)``;
the first match runs. An argv no entry matches is an error rather than a silent
success, so a fake never hides a program the product started. Inspection after
the program returns shows the termination barrier the product waits for. The
launching owner is one fixed identity; a named Job is empty unless a launched,
unfinished Job carries that name.
"""
from do_math.windows_job import JobInspection
from do_math.worker_request import validate_resource_limits

_ZERO_USAGE = {"limits": {"memory_bytes": None, "cpu_rate_basis_points": None},
               "peak_job_memory_bytes": 0, "cpu_time_100ns": 0,
               "scope": "local_job_commit_memory_and_cpu_cap_not_rss_or_remote_usage"}


class FakeJob:
    _next_pid = 40000

    def __init__(self, program, argv, cwd, env, name, resource_limits):
        self.program, self.argv, self.cwd, self.env, self.name = program, list(argv), cwd, env, name
        self.resource_limits = validate_resource_limits(resource_limits)
        FakeJob._next_pid += 4
        self.pid, self.creation_filetime = FakeJob._next_pid, 133_000_000_000_000_000 + FakeJob._next_pid
        self.resumed = self.done = self.closed = False
        self.exit_code = None

    def resume(self):
        if self.resumed:
            raise RuntimeError("root thread has already been resumed")
        self.resumed = True
        if not self.done:
            self.exit_code = self.program(self.argv, self.cwd, self.env)
            self.done = True

    def wait(self, timeout=None):
        return self.done

    def terminate(self, exit_code=1):
        if not self.done:
            self.done, self.exit_code = True, exit_code

    def inspect(self):
        return JobInspection(active_processes=0 if self.done else 1,
                             process_ids=() if self.done else (self.pid,), root_signaled=self.done)

    def resource_usage(self):
        usage = {**_ZERO_USAGE, "limits": dict(_ZERO_USAGE["limits"])}
        if self.resource_limits:
            usage["limits"] = {"memory_bytes": self.resource_limits.get("memory_bytes"),
                               "cpu_rate_basis_points": self.resource_limits.get("cpu_rate_basis_points")}
        return usage

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class FakeJobs:
    def __init__(self, programs=()):
        self.programs = list(programs)
        self.launched = []
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
        job = FakeJob(program, argv, cwd, env, name, resource_limits)
        self.launched.append(job)
        return job


def make_fake(programs=()):
    return FakeJobs(programs)
