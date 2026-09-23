"""Prepare the machine-wide Lean toolchain and the Mathlib project that discover_lean() prefers.

Idempotent: finished steps are skipped. The ready marker is written only after `import Mathlib`
compiles through the exact command the verifier will use, so a half-downloaded cache is never selected.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import zipfile

from do_math.formal import LEAN_VERSION, READY_MARKER, discover_lean, mathlib_project, portable_bin, toolchain_root, inspect_toolchain

LEAN_ZIP = f"https://github.com/leanprover/lean4/releases/download/v{LEAN_VERSION}/lean-{LEAN_VERSION}-windows.zip"
# Mathlib tags follow Lean releases; the tag equal to the toolchain is the one whose cached .olean files load.
PROJECT_FILES = {
    "lean-toolchain": f"leanprover/lean4:v{LEAN_VERSION}\n",
    "lakefile.toml": ('name = "do_math_env"\n\n[[require]]\nname = "mathlib"\n'
                      f'git = "https://github.com/leanprover-community/mathlib4"\nrev = "v{LEAN_VERSION}"\n'),
}
SMOKE = "import Mathlib\nexample : (2 : ℝ) + 2 = 4 := by norm_num\n"


def run(command, cwd, env):
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspect-only', action='store_true', help='observe an installed command without installing or adopting it')
    parser.add_argument('--command-file', type=Path, help='UTF-8 JSON object with lean_command argv; requires --inspect-only')
    parser.add_argument("--smoke-timeout", type=int, default=None,
                        help="legacy option, ignored; Lean runs to completion")
    args = parser.parse_args()
    if args.command_file and not args.inspect_only:
        parser.error('--command-file requires --inspect-only')
    if args.inspect_only:
        from do_math.submission import load_json
        command = load_json(args.command_file.read_bytes())['lean_command'] if args.command_file else discover_lean()
        if not command:
            parser.error('Lean was not found; supply --command-file')
        with tempfile.TemporaryDirectory() as directory:
            observed = inspect_toolchain(command, Path(directory), args.smoke_timeout)
        print(json.dumps({'status':'observed', 'lean_command':command, 'toolchain':observed}))
        return
    root = toolchain_root()
    if root is None:
        raise SystemExit("this installation has no repository root above it; set lean_command explicitly instead")
    bin_dir = portable_bin(root)
    if not (bin_dir / "lean.exe").is_file():
        archive = bin_dir.parents[1] / f"lean-{LEAN_VERSION}-windows.zip"
        archive.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", LEAN_ZIP, flush=True)
        urllib.request.urlretrieve(LEAN_ZIP, archive)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(archive.parent)
    project = mathlib_project(root)
    project.mkdir(parents=True, exist_ok=True)
    for name, text in PROJECT_FILES.items():
        if not (project / name).is_file() or (project / name).read_text(encoding="utf-8") != text:
            (project / name).write_text(text, encoding="utf-8")
    lake = str(bin_dir / "lake.exe")
    # Mathlib's cache tool calls lean and leantar by name; there is no elan here to resolve them.
    env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", "")}
    if not (project / "lake-manifest.json").is_file():
        run([lake, "update"], project, env)
    run([lake, "exe", "cache", "get"], project, env)
    marker = project / READY_MARKER
    command = [lake, "--dir", str(project), "env", str(bin_dir / "lean.exe")]
    with tempfile.TemporaryDirectory() as directory:
        smoke = Path(directory) / "smoke.lean"
        smoke.write_text(SMOKE, encoding="utf-8")
        print("+", " ".join([*command, str(smoke)]), flush=True)
        ok = subprocess.run([*command, str(smoke)], cwd=directory).returncode == 0
    if not ok:
        marker.unlink(missing_ok=True)
        raise SystemExit("import Mathlib compilation failed; the environment is not selected")
    marker.write_text(LEAN_VERSION, encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        observed = inspect_toolchain(command, Path(directory), args.smoke_timeout)
    print(json.dumps({"status": "ready", "lean_command": command, 'toolchain': observed}))


if __name__ == "__main__":
    main()
