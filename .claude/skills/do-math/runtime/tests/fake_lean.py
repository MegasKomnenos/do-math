"""A stand-in for `lean` with a controllable memory and time profile; no Lean is involved.

The last argument is the source file. Its `import` lines cost 8 MiB each plus 8 MiB
(the "baseline"), held for the whole run and alone for its first 0.3 seconds, so that
the broker's sampling sees an imports-only peak. A line `-- fake: key=value ...` adds:
alloc_mb (private memory taken after the baseline), sleep (seconds), exit (code),
marker (text printed to stdout), stderr (text printed to stderr). `--threads=N` is
echoed, as are the FAKE_ENV environment variable and the process's niceness;
`--version` prints a version line; and an import of a `Missing.*` module fails the way a
nonexistent module would. Build tests use the artifact profile
observed with Lean 4.32: .olean, .olean.private, .olean.server and .ir are emitted
together and all are required for a local import. This models file transport only.
"""

import os
import re
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
    olean = next((argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == "-o"), None)
    with open(source, encoding="utf-8") as stream:
        lines = stream.read().splitlines()
    imports = [match.group(1) for line in lines
               if (match := re.match(r"^(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?(\S+)", line))]
    if any(name.startswith("Missing.") for name in imports):
        print(f"{source}:1:0: error: unknown module prefix 'Missing'")
        return 1
    search = [p for p in os.environ.get("LEAN_PATH", "").split(os.pathsep) if p]
    suffixes = (".olean", ".olean.private", ".olean.server", ".ir")
    for name in imports:
        if name.split(".")[0] in ("Mathlib", "Init", "Std", "Lean"):
            continue
        if not any(all(os.path.isfile(os.path.join(entry, *name.split(".")) + suffix)
                       for suffix in suffixes) for entry in search):
            print(f"{source}:1:0: error: incomplete compiled module '{name}'")
            return 1
    options = {}
    for line in lines:
        if line.startswith("-- fake:"):
            for pair in line[len("-- fake:"):].split():
                key, _, value = pair.partition("=")
                options[key] = value
    held = [touch(bytearray((8 + 8 * len(imports)) * 1024 * 1024))]
    time.sleep(0.3)  # the baseline alone, long enough for the broker's sampling to see it
    if "alloc_mb" in options:
        held.append(touch(bytearray(int(options["alloc_mb"]) * 1024 * 1024)))
    time.sleep(float(options.get("sleep", 0)))
    nice = os.nice(0) if hasattr(os, "nice") else "n/a"
    print(f"compiled {source} imports={len(imports)} threads={threads} FAKE_ENV={os.environ.get('FAKE_ENV')} nice={nice}")
    if "marker" in options:
        print(options["marker"])
    if "stderr" in options:
        print(options["stderr"], file=sys.stderr)
    sys.stdout.flush()
    del held
    code = int(options.get("exit", 0))
    if olean and code == 0:
        for suffix in (".olean", ".olean.private", ".olean.server", ".ir"):
            with open(os.path.splitext(olean)[0] + suffix, "w", encoding="utf-8") as stream:
                stream.write(f"fake {suffix} of {source}\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
