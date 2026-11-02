"""A stand-in for `lean` with a controllable memory and time profile; no Lean is involved.

The last argument is the source file. Its `import` lines cost 8 MiB each plus 8 MiB
(the "baseline"), held for the whole run. A line `-- fake: key=value ...` adds:
alloc_mb (private memory taken after the baseline), sleep (seconds), exit (code),
marker (text printed to stdout), stderr (text printed to stderr). `--threads=N` is
echoed, as are the FAKE_ENV environment variable and the process's niceness;
`--version` prints a version line; an import of a `Missing.*` module fails the way a
nonexistent module would; and `sorry` in the source prints Lean's warning shape so
that an exit code of 0 can still carry a warning.
"""

import os
import sys
import time


def touch(buffer):
    for offset in range(0, len(buffer), 4096):
        buffer[offset] = 1
    return buffer


def main(argv):
    if "--version" in argv:
        print("Lean (version 4.0.0-fake, x86_64-fake, commit 0000000, Release)")
        return 0
    threads = next((arg.split("=", 1)[1] for arg in argv if arg.startswith("--threads=")), None)
    source = argv[-1]
    with open(source, encoding="utf-8") as stream:
        lines = stream.read().splitlines()
    imports = [line for line in lines if line.startswith("import ")]
    missing = [line for line in imports if line.startswith("import Missing.")]
    if missing:
        print(f"{source}:1:0: error: unknown module prefix 'Missing'")
        return 1
    options = {}
    for line in lines:
        if line.startswith("-- fake:"):
            for pair in line[len("-- fake:"):].split():
                key, _, value = pair.partition("=")
                options[key] = value
    held = [touch(bytearray((8 + 8 * len(imports)) * 1024 * 1024))]
    time.sleep(float(options.get("import_sleep", 0.3)))
    if "alloc_mb" in options:
        held.append(touch(bytearray(int(options["alloc_mb"]) * 1024 * 1024)))
    time.sleep(float(options.get("sleep", 0)))
    nice = os.nice(0) if hasattr(os, "nice") else "n/a"
    print(f"compiled {source} imports={len(imports)} threads={threads} FAKE_ENV={os.environ.get('FAKE_ENV')} nice={nice}")
    if "marker" in options:
        print(options["marker"])
    if "stderr" in options:
        print(options["stderr"], file=sys.stderr)
    if any("sorry" in line for line in lines):
        print(f"{source}:1:0: warning: declaration uses 'sorry'")
    sys.stdout.flush()
    del held
    return int(options.get("exit", 0))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
