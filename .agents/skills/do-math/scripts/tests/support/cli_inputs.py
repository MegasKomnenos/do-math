"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

import json
import os
from pathlib import Path
from support.fakes.git_backend import make_repository
import sys


def new_instance(repository, *, goal, workspace=None, **options):
    """Create a Git repository and initialize one instance in it through the public ``initialize``.

    ``workspace`` defaults to ``repository / 'work'``; ``options`` pass to ``initialize``.
    Returns the new instance ID.
    """
    from support.entry import entry
    _entry = entry()
    from do_math.wiring import real_ports
    _entry.ports = real_ports(environment=_entry.environment)
    from do_math.engine import initialize
    repository = Path(repository)
    make_repository(repository)
    return initialize(repository, goal=goal, workspace=repository / "work" if workspace is None else workspace,
                      **options, codex_home=_entry.codex_home, host_id=_entry.host_id, ports=_entry.ports)["instance_id"]


def role_reach(prompt, workspace, secret):
    """Where ``secret`` reaches the role given ``prompt`` in its prepared ``workspace``.

    A role reads three things: its rendered prompt, the files of its workspace (the fixed
    input), and through its installed read tool the input snapshot that record_map allows.
    The tool is run as the role runs it, on every record_index ID and on every snapshot
    file that holds ``secret``. Returns ``(reached, held)``: the prompt, workspace files and
    tool requests that yield ``secret``, and the snapshot files that hold it. An empty
    ``held`` means the snapshot never held the secret, so ``reached`` proves nothing.
    """
    from support.entry import entry
    _entry = entry()
    from do_math.wiring import real_ports
    _entry.ports = real_ports(environment=_entry.environment)
    import subprocess
    from do_math.git_store import GitStateStore
    workspace, needle = Path(workspace), secret.encode("utf-8")
    reached = ["prompt"] if secret in prompt else []
    reached += sorted(path.relative_to(workspace).as_posix() for path in workspace.rglob("*")
                      if path.is_file() and needle in path.read_bytes())
    context = json.loads((workspace / "input/submission/context.json").read_bytes())
    store = GitStateStore(Path(context["record_store"]["repository"]), context["record_store"]["instance_id"], backend=_entry.ports.git_backend, clock=_entry.ports.clock)
    paths = sorted(store.tree_paths(context["snapshot"]))
    held = sorted(path for path, raw in store.read_many(context["snapshot"], paths).items() if needle in raw)
    requests = [argument for identifier in sorted({i for ids in context["record_index"].values() for i in ids})
                for argument in ("--id", identifier)] + [argument for path in held for argument in ("--path", path)]
    if requests:
        result = subprocess.run([sys.executable, "-B", "input/tools/read_input.py", *requests], cwd=workspace,
                                capture_output=True, timeout=120)
        output = json.loads(result.stdout)
        reached += ["read_input.py " + row["request"] for row in output["records"]
                    if row["status"] == "ok" and secret in json.dumps(row, ensure_ascii=False)]
    return reached, held


def run_cli(*arguments, cwd=None):
    """Run the CLI's ``main`` in this process, as ``python do_math.py *arguments`` would.

    Returns a ``subprocess.CompletedProcess`` with ``returncode`` and text
    ``stdout``/``stderr``. ``cwd`` is the working directory during the call.
    Nothing about the process is exercised: stream encoding, interpreter
    start-up and process-wide state stay those of the test process.
    """
    import io
    import subprocess
    from contextlib import redirect_stderr, redirect_stdout
    from do_math.cli import main
    arguments = [os.fspath(argument) for argument in arguments]
    stdout, stderr = io.StringIO(), io.StringIO()
    previous = os.getcwd()
    try:
        if cwd is not None:
            os.chdir(cwd)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = main(arguments)
            except SystemExit as exit:
                # As the interpreter does: None is success, other non-integers print and fail.
                code = 0 if exit.code is None else exit.code if isinstance(exit.code, int) else 1
                if not isinstance(exit.code, (int, type(None))):
                    print(exit.code, file=sys.stderr)
    finally:
        os.chdir(previous)
    return subprocess.CompletedProcess(['do_math.py', *arguments], code, stdout.getvalue(), stderr.getvalue())
