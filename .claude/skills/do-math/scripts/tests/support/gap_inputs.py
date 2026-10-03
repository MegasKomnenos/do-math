"""Owned input observations and a subprocess effect fault; no product replacement.

GitProcess's read_objects -> _checked -> _run lets process-launch OSError
escape. Nonzero Git exit instead becomes GitBackendError. The fault below
asks Windows to launch an invalid executable owned by this test, only for
one exact cat-file --batch input. It models a broken Git executable, not a
missing object, permission change, or synthetic store.read exception.
"""
import json
import subprocess

from support.planning_paths import ExecutedLines


def observation(name, **values):
    """Write evidence to runner stdout without making an undecided result an oracle."""
    print('GAP_INPUT ' + json.dumps({'case': name, **values}, ensure_ascii=False, default=str))


class ReadObjectLaunchFault:
    def __init__(self, executable):
        self.executable = executable
        self.spec = None
        self.errors = []
        self.calls = []

    def __call__(self, argv, **options):
        if argv[-2:] == ['cat-file', '--batch']:
            self.calls.append(options.get('input'))
            if self.spec is not None and options.get('input') == (self.spec + '\n').encode():
                try:
                    return subprocess.run(argv, executable=str(self.executable), **options)
                except OSError as error:
                    self.errors.append(error)
                    raise
        return subprocess.run(argv, **options)
