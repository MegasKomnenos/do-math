"""Prepare the machine-wide Lean toolchain and the Mathlib project that discover_lean() prefers.

Idempotent: finished steps are skipped. The ready marker is written only after `import Mathlib`
compiles through the exact command the verifier will use, so a half-downloaded cache is never selected.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import zipfile
import uuid

from do_math.formal import LEAN_VERSION, READY_MARKER, discover_lean, mathlib_project, portable_bin, toolchain_root, inspect_toolchain
from do_math.trust_inventory import SMOKE, validation_program, collect_manifest, collect_inventory
from do_math.trust_validation import AXIOMS

LEAN_ZIP = f"https://github.com/leanprover/lean4/releases/download/v{LEAN_VERSION}/lean-{LEAN_VERSION}-windows.zip"
# Mathlib tags follow Lean releases; the tag equal to the toolchain is the one whose cached .olean files load.
PROJECT_FILES = {
    "lean-toolchain": f"leanprover/lean4:v{LEAN_VERSION}\n",
    "lakefile.toml": ('name = "do_math_env"\n\n[[require]]\nname = "mathlib"\n'
                      f'git = "https://github.com/leanprover-community/mathlib4"\nrev = "v{LEAN_VERSION}"\n'),
}


def verify_environment(command, evidence_root):
    """Preserve a bounded-scope environment check; no trust adoption is implied."""
    directory = evidence_root.resolve() / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex)
    directory.mkdir(parents=True)
    source = directory / 'smoke.lean'
    record = {'status': 'failed',
              'started_at': datetime.now(timezone.utc).isoformat(),
              'command': [*command, str(source)], 'source': str(source)}
    try:
        from do_math.repository import exact_content_hash
        from do_math.operation_trace import tracing, phase
        record['toolchain'] = inspect_toolchain(command, directory)
        source_text, scope = validation_program(record['toolchain'])
        source.write_bytes(source_text.encode('utf-8'))
        record.update(scope=scope, source_text=source_text,
                      source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        with tracing(directory/'operations'), phase('environment_inventory_before'):
            before_inventory=collect_inventory(record['toolchain'])
        if any(directory.is_relative_to(Path(root['path'])) for root in before_inventory['scope']['roots']):
            raise ValueError('validation evidence must be outside the adopted installation roots')
        record['inventory_sha256']=exact_content_hash(before_inventory)
        from do_math.formal import _job_run
        with tracing(directory / 'operations'), phase('environment_smoke_compile') as metrics:
            code, stdout, stderr, stopped = _job_run([*command, str(source)], directory,
                on_started=lambda process: metrics.update(process=process))
        record.update(exit_code=code, stdout=stdout, stderr=stderr)
        record['toolchain_after'] = inspect_toolchain(command, directory)
        with tracing(directory/'operations'), phase('environment_inventory_after'):
            after_inventory=collect_inventory(record['toolchain_after'])
        if (not stopped and code == 0 and record['toolchain_after'] == record['toolchain']
                and after_inventory==before_inventory):
            record['status'] = 'verified'
            (directory/'inventory.json').write_text(json.dumps(before_inventory,ensure_ascii=False),encoding='utf-8')
        elif code == 0:
            record['error'] = 'toolchain identity or complete inventory changed during environment validation'
    except Exception as error:
        record['error'] = f'{type(error).__name__}: {error}'
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    evidence = directory / 'validation.json'
    evidence.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'status': record['status'], 'lean_command': list(command),
            'toolchain': record.get('toolchain'),
            'validation': record, 'evidence_path': str(evidence),
            'inventory_path':str(directory/'inventory.json') if record['status']=='verified' else None}


def write_trust_request(result, destination):
    if result['status'] not in {'verified', 'ready'}:
        raise ValueError('a successful environment validation is required')
    observed=json.loads(Path(result['inventory_path']).read_text(encoding='utf-8'))
    request={'operation':'register','toolchain':result['toolchain'],
             'allowed_axioms':sorted(AXIOMS),
             'manifest':collect_manifest(result['toolchain'],result['validation'],observed_inventory=observed)}
    destination=destination.resolve()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('x',encoding='utf-8') as stream:
        json.dump(request,stream,ensure_ascii=False,indent=2)
    return {'path':str(destination),'file_count':len(request['manifest']['files'])}


def run(command, cwd, env):
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--inspect-only', action='store_true', help='observe an installed command without installing or adopting it')
    mode.add_argument('--verify-only', action='store_true', help='validate an installed environment and preserve evidence without downloading or adopting it')
    parser.add_argument('--command-file', type=Path, help='UTF-8 JSON object with lean_command argv; requires --inspect-only or --verify-only')
    parser.add_argument('--evidence-dir', type=Path, help='parent directory for unique environment validation records')
    parser.add_argument('--trust-file', type=Path, help='write a new complete registration request after successful validation')
    args = parser.parse_args()
    if args.command_file and not (args.inspect_only or args.verify_only):
        parser.error('--command-file requires --inspect-only or --verify-only')
    if args.inspect_only and args.evidence_dir:
        parser.error('--evidence-dir requires an environment validation run')
    if args.inspect_only and args.trust_file:
        parser.error('--trust-file requires an environment validation run')
    if args.inspect_only or args.verify_only:
        from do_math.submission import load_json
        command = load_json(args.command_file.read_bytes())['lean_command'] if args.command_file else discover_lean()
        if not command:
            parser.error('Lean was not found; supply --command-file')
        if args.verify_only:
            root = toolchain_root()
            if args.evidence_dir is None and root is None:
                parser.error('--verify-only requires --evidence-dir for this installation')
            result = verify_environment(command, args.evidence_dir or root / 'validation')
            if result['status']=='verified' and args.trust_file:
                result['trust_request']=write_trust_request(result,args.trust_file)
            print(json.dumps(result))
            if result['status'] != 'verified':
                raise SystemExit(1)
        else:
            with tempfile.TemporaryDirectory() as directory:
                observed = inspect_toolchain(command, Path(directory))
            print(json.dumps({'status':'observed', 'lean_command':command, 'toolchain':observed}))
        return
    root = toolchain_root()
    if root is None:
        raise SystemExit("this installation has no repository root above it; set lean_command explicitly instead")
    project = mathlib_project(root)
    marker = project / READY_MARKER
    marker.unlink(missing_ok=True)
    bin_dir = portable_bin(root)
    if not (bin_dir / "lean.exe").is_file():
        archive = bin_dir.parents[1] / f"lean-{LEAN_VERSION}-windows.zip"
        archive.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", LEAN_ZIP, flush=True)
        urllib.request.urlretrieve(LEAN_ZIP, archive)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(archive.parent)
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
    command = [lake, "--dir", str(project), "env", str(bin_dir / "lean.exe")]
    result = verify_environment(command, args.evidence_dir or root / 'validation')
    if result['status'] != 'verified':
        marker.unlink(missing_ok=True)
        print(json.dumps(result))
        raise SystemExit(1)
    marker.write_text(LEAN_VERSION, encoding="utf-8")
    if args.trust_file:
        result['trust_request']=write_trust_request(result,args.trust_file)
    print(json.dumps({**result, 'status': 'ready'}))


if __name__ == "__main__":
    main()
