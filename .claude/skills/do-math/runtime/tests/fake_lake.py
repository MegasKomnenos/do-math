"""A stand-in for `lake env <command>`: runs the command in the environment a Lake workspace would add.

It sets FAKE_LAKE=1 and puts a marker folder in front of LEAN_PATH, so that a test can
tell whether a compile ran through it or directly in the environment it reported once.
With FAKE_LAKE_FAIL set it exits 7 instead, like a lake whose workspace will not load.
"""

import os
import subprocess
import sys


def main(argv):
    if not argv or argv[0] != "env":
        print("fake lake: only `env <command>` is supported", file=sys.stderr)
        return 2
    if os.environ.get("FAKE_LAKE_FAIL"):
        print("fake lake: the workspace failed to load", file=sys.stderr)
        return 7
    lean_path = os.pathsep.join(p for p in ("fake-lake-lib", os.environ.get("LEAN_PATH", "")) if p)
    return subprocess.call(argv[1:], env=dict(os.environ, FAKE_LAKE="1", LEAN_PATH=lean_path))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
