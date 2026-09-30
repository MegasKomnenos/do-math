"""The Lean verifier run directly on the Jobs port (``formal.verify_lean``, ``formal._job_run``), for knowledge tests.

``verify_lean(..., jobs=)`` starts the compile through the Jobs port. A Jobs fake
from ``formal_jobs`` recognizes the Lean worker Job root that ``_job_run``
launches (``[python, -B, -c, <import formal._worker>, <scripts>, <request>]``) and
runs ``run(request_path)`` in process in its place; any other argv is an error.
``worker_jobs(spawn)`` runs the product's own worker there with ``spawn`` at the
worker's seam, so the request file, the output files, the status file and their
reading are the product's. ``OutputCompiler`` is a ``spawn`` double for a
compiler that prints a fixed output whatever it is given, as the legacy
synthetic compilers (Python scripts) did; it records every command it was given.

``approved_toolchain(root)`` is a synthetic Lean command and its approved
identity: the trust fixture's toolchain (``research_fixtures.trust_fixture``),
whose checker is the running ``formal.py``, so ``toolchain_identity_errors``
accepts it until one of its recorded files changes. ``inspect_toolchain``
cannot make this identity in process: it starts its ``--version`` Job without
the Jobs port.
"""
from __future__ import annotations

from pathlib import Path

from do_math import formal
from support.fakes.jobs import FakeJobs


def is_formal_worker(argv):
    return argv[1:3] == ['-B', '-c'] and 'do_math.formal import _worker' in argv[3]


def formal_jobs(run):
    """A Jobs fake whose one program is the Lean worker root: ``run(request_path)`` returns its exit code."""
    return FakeJobs([(is_formal_worker, lambda argv, cwd, env: run(Path(argv[5])))])


def worker_jobs(spawn):
    """The Jobs fake running the product's ``formal._worker`` with ``spawn`` at its seam."""
    return formal_jobs(lambda request: formal._worker(request, spawn=spawn))


class OutputCompiler:
    """A ``spawn`` double: the compiler writes ``stdout`` and exits with ``exit_code``.

    ``during()``, when given, runs while the compiler runs (before it exits).
    ``commands`` lists every command the worker started.
    """

    def __init__(self, stdout='', *, exit_code=0, during=None):
        self.stdout, self.exit_code, self.during = stdout, exit_code, during
        self.commands = []

    def __call__(self, command, *, cwd=None, stdout=None, stderr=None, shell=False, creationflags=0):
        self.commands.append(list(command))
        return _Run(self, stdout)


class _Run:
    def __init__(self, compiler, out):
        self.compiler, self.out = compiler, out

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def wait(self, timeout=None):
        if self.compiler.during is not None:
            self.compiler.during()
        self.out.write(self.compiler.stdout.encode('utf-8'))
        return self.compiler.exit_code


def approved_toolchain(root):
    """``(command, toolchain)``: the synthetic Lean executable under ``root/'trust'`` and its approved identity."""
    from research_fixtures import trust_fixture
    lean = Path(root).resolve() / 'trust' / 'toolchain' / 'bin' / 'lean.exe'
    request = trust_fixture(root, [str(lean)], directory=Path(root) / 'trust')
    return [str(lean)], request['toolchain']
