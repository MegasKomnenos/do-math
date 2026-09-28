"""Prepare the machine-wide Lean toolchain and record it for the research instances.

Installation is idempotent: finished steps are skipped. A toolchain record is written
only after `import Mathlib` compiles through the exact command the verifier will use,
and the ready marker follows the record, so a half-downloaded cache is never selected.
Record writers (installation, --verify-only, --rerecord, --check-contents) exclude each
other with the lock file of the records directory. Exit codes: 0 success, 1 a refused,
failed or mismatching result, 2 an execution error. Every mode prints one JSON object on stdout;
installation progress and Lake output go to stderr.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
import uuid
import zipfile

from do_math.formal import LEAN_VERSION, READY_MARKER, discover_lean, mathlib_project, portable_bin, toolchain_root, inspect_toolchain
from do_math import trust_inventory as records
from do_math.trust_validation import AXIOMS
from do_math.file_io import RACY_NS, fingerprint_settled, now

LEAN_ZIP = f"https://github.com/leanprover/lean4/releases/download/v{LEAN_VERSION}/lean-{LEAN_VERSION}-windows.zip"
# Mathlib tags follow Lean releases; the tag equal to the toolchain is the one whose cached .olean files load.
PROJECT_FILES = {
    "lean-toolchain": f"leanprover/lean4:v{LEAN_VERSION}\n",
    "lakefile.toml": ('name = "do_math_env"\n\n[[require]]\nname = "mathlib"\n'
                      f'git = "https://github.com/leanprover-community/mathlib4"\nrev = "v{LEAN_VERSION}"\n'),
}


class Refused(Exception):
    """A record operation that must not proceed; exit code 1 with the stated result."""
    def __init__(self, result):
        super().__init__(result.get('reason', result.get('status')))
        self.result = result


def observe_identity(command):
    with tempfile.TemporaryDirectory() as directory:
        identity = inspect_toolchain(command, Path(directory))
    errors = records.identity_errors(identity)
    if errors:
        raise ValueError('; '.join(errors))
    return identity


def verify_environment(command, evidence_root, identity):
    """Compile the representative examples through the exact command; nothing is adopted."""
    directory = evidence_root.resolve() / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex)
    if any(directory.is_relative_to(root.resolve()) for root in records.roots(identity).values()):
        raise ValueError('validation evidence must be outside the recorded toolchain and project roots')
    directory.mkdir(parents=True)
    source = directory / 'smoke.lean'
    source_text, scope = records.validation_program(identity)
    source.write_bytes(source_text.encode('utf-8'))
    validation = {'status': 'failed', 'scope': scope, 'source': str(source), 'source_text': source_text,
                  'source_sha256': hashlib.sha256(source_text.encode('utf-8')).hexdigest(),
                  'command': [*command, str(source)], 'exit_code': None, 'stdout': '', 'stderr': '',
                  'started_at': now()}
    try:
        from do_math.formal import _job_run
        from do_math.operation_trace import tracing, phase
        with tracing(directory / 'operations'), phase('environment_smoke_compile') as metrics:
            code, stdout, stderr, stopped = _job_run([*command, str(source)], directory,
                on_started=lambda process: metrics.update(process=process))
        validation.update(exit_code=code, stdout=stdout, stderr=stderr)
        if not stopped and code == 0:
            validation['status'] = 'verified'
    except Exception as error:
        validation['error'] = f'{type(error).__name__}: {error}'
    validation['finished_at'] = now()
    (directory / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return validation


def _baseline(command, evidence_root, identity, fingerprint, content):
    validation = verify_environment(command, evidence_root, identity)
    if validation['status'] != 'verified':
        raise Refused({'status': 'failed', 'reason': 'the representative compile did not succeed', 'validation': validation})
    if records.observe_fingerprint(identity)['sha256'] != fingerprint['sha256']:
        raise Refused({'status': 'failed', 'reason': 'judgment files changed while the baseline was being recorded'})
    return records.new_baseline(fingerprint, content, validation)


def _summary(path, record, **fields):
    return {'record_path': str(path), 'record_id': record['id'], 'binding': records.binding(record),
            'representative_check_seconds': records.representative_check_seconds(record['baselines'][-1]['validation']),
            **fields}


def _settled_fingerprint(identity, attempts=3):
    """Observe the judgment files once every fingerprint is older than the racy window.

    A baseline is compared by metadata later, so it must not record a time that a
    same-size rewrite could still share.
    """
    for _ in range(attempts):
        observed = records.observe_fingerprint(identity)
        if all(fingerprint_settled((size, int(modified), int(born)))
               for size, modified, born in observed['files'].values()):
            return observed
        time.sleep(RACY_NS / 1e9)
    raise RuntimeError('judgment files are still changing; record the installation once it is idle')


def record_installation(command, records_dir, evidence_root):
    """Create the record of an installed identity or confirm an unchanged one; never append a baseline."""
    identity = observe_identity(command)
    with records.writer_lock(records_dir):
        fingerprint = _settled_fingerprint(identity)
        for path, record in records.records_for(records_dir, identity):
            if record['baselines'][-1]['fingerprint']['sha256'] == fingerprint['sha256'] and not records.usable_errors(record):
                return _summary(path, record, status='recorded', created=False)
        content = records.content_hashes(identity, fingerprint['files'])
        path = records.record_path(records_dir, records.record_id(identity, content['sha256']))
        if path.exists():
            raise Refused({'status': 'rerecord_required', 'record_path': str(path),
                'reason': 'the installed bytes match this record but its metadata or check history changed; '
                          'a user or operator decides whether to run --rerecord'})
        record = records.new_record(identity, _baseline(command, evidence_root, identity, fingerprint, content))
        records.write_record(path, record)
        return _summary(path, record, status='recorded', created=True)


def resolve_record(records_dir, record_id, identity):
    """The named record, or the only record of the identity (a callable observes it on demand)."""
    if record_id is not None:
        path = records.record_path(records_dir, record_id)
        return path, records.read_record(path)
    candidates = records.records_for(records_dir, identity())
    if len(candidates) != 1:
        raise ValueError('name the record with --record; records of the current identity: '
                         + (', '.join(record['id'] for _, record in candidates) or 'none'))
    return candidates[0]


def rerecord(command, records_dir, evidence_root, record_id):
    """Append a baseline after metadata-only changes. Users and operators only (D5)."""
    identity = observe_identity(command)
    with records.writer_lock(records_dir):
        path, record = resolve_record(records_dir, record_id, lambda: identity)
        if record['identity'] != identity:
            raise Refused({'status': 'refused', 'record_path': str(path),
                'reason': 'the installed identity differs from the record; create a new record and register and transition to it'})
        fingerprint = _settled_fingerprint(identity)
        content = records.content_hashes(identity, fingerprint['files'])
        mismatched = records.changed_files(record['baselines'][-1]['content']['files'], content['files'])
        if mismatched:
            raise Refused({'status': 'refused', 'record_path': str(path), 'mismatched': mismatched,
                'reason': 'judgment file contents differ from the current baseline; create a new record and '
                          'register and transition to it'})
        record['baselines'].append(_baseline(command, evidence_root, identity, fingerprint, content))
        records.write_record(path, record)
        return _summary(path, record, status='recorded')


def check_contents(records_dir, record_id, command):
    """Hash every judgment file and append the comparison with the current baseline."""
    with records.writer_lock(records_dir):
        path, record = resolve_record(records_dir, record_id, lambda: observe_identity(command))
        current = len(record['baselines']) - 1
        fingerprint = records.observe_fingerprint(record['identity'])
        content = records.content_hashes(record['identity'], fingerprint['files'])
        mismatched = records.changed_files(record['baselines'][current]['content']['files'], content['files'])
        check = {'checked_at': now(), 'baseline': current,
                 'result': 'mismatch' if mismatched else 'passed', 'mismatched': mismatched}
        record['checks'].append(check)
        records.write_record(path, record)
        return _summary(path, record, status=check['result'], check=check)


def write_trust_request(result, destination):
    """A registration request binding the record's identity and one baseline."""
    record = records.read_record(result['record_path'])
    request = {'operation': 'register', 'toolchain': record['identity'], 'allowed_axioms': sorted(AXIOMS),
               'toolchain_record': {'path': str(Path(result['record_path']).resolve()), 'id': record['id']},
               'binding': result['binding']}
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(request, stream, ensure_ascii=False, indent=2)
    return {'path': str(destination), 'toolchain_record': request['toolchain_record'], 'binding': request['binding']}


def run(command, cwd, env):
    # Progress goes to stderr; stdout carries only the one JSON result.
    print("+", " ".join(command), file=sys.stderr, flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True, stdout=sys.stderr)


def install(root):
    project = mathlib_project(root)
    bin_dir = portable_bin(root)
    if not (bin_dir / "lean.exe").is_file():
        archive = bin_dir.parents[1] / f"lean-{LEAN_VERSION}-windows.zip"
        archive.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", LEAN_ZIP, file=sys.stderr, flush=True)
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
    return [lake, "--dir", str(project), "env", str(bin_dir / "lean.exe")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--inspect-only', action='store_true', help='observe an installed command without installing or recording it')
    mode.add_argument('--verify-only', action='store_true',
                      help='record an installed environment without downloading: identity, fingerprints, content hashes and a representative compile')
    mode.add_argument('--rerecord', action='store_true',
                      help='users and operators only: append a baseline when only metadata changed; refused if any content differs')
    mode.add_argument('--check-contents', action='store_true',
                      help='hash every judgment file, compare with the current baseline and append the result to the record')
    parser.add_argument('--command-file', type=Path, help='UTF-8 JSON object with lean_command argv; not for installation')
    parser.add_argument('--record', help='toolchain record ID (TC-...); default: the only record of the current identity')
    parser.add_argument('--records-dir', type=Path, help='toolchain record directory; default: <toolchain root>/records')
    parser.add_argument('--evidence-dir', type=Path, help='parent directory for representative compile evidence')
    parser.add_argument('--trust-file', type=Path, help='write a new registration request for the resulting record baseline')
    args = parser.parse_args()
    installing = not (args.inspect_only or args.verify_only or args.rerecord or args.check_contents)
    if args.command_file and installing:
        parser.error('--command-file requires --inspect-only, --verify-only, --rerecord or --check-contents')
    if args.inspect_only and (args.evidence_dir or args.trust_file or args.record or args.records_dir):
        parser.error('--inspect-only neither records nor validates an environment')
    if args.check_contents and (args.evidence_dir or args.trust_file):
        parser.error('--check-contents runs no compile and writes no registration request')
    if args.record and not (args.rerecord or args.check_contents):
        parser.error('--record names the record for --rerecord or --check-contents')
    root = toolchain_root()
    try:
        if installing:
            if root is None:
                raise ValueError("this installation has no repository root above it; set lean_command explicitly instead")
            (mathlib_project(root) / READY_MARKER).unlink(missing_ok=True)
            command = install(root)
        else:
            from do_math.submission import load_json
            command = load_json(args.command_file.read_bytes())['lean_command'] if args.command_file else discover_lean()
            if not command:
                raise ValueError('Lean was not found; supply --command-file')
        if args.inspect_only:
            with tempfile.TemporaryDirectory() as directory:
                print(json.dumps({'status': 'observed', 'lean_command': command,
                                  'toolchain': inspect_toolchain(command, Path(directory))}))
            return
        if root is None and (args.records_dir is None or args.evidence_dir is None and not args.check_contents):
            raise ValueError('this installation has no toolchain root; supply --records-dir and --evidence-dir')
        records_dir = args.records_dir or root / 'records'
        evidence_root = args.evidence_dir or (root / 'validation' if root else None)
        if args.check_contents:
            result = check_contents(records_dir, args.record, command)
        elif args.rerecord:
            result = rerecord(command, records_dir, evidence_root, args.record)
        else:
            result = record_installation(command, records_dir, evidence_root)
        result['lean_command'] = command
        if args.trust_file:
            result['trust_request'] = write_trust_request(result, args.trust_file)
        if installing:
            (mathlib_project(root) / READY_MARKER).write_text(LEAN_VERSION, encoding="utf-8")
    except Refused as refused:
        print(json.dumps(refused.result, ensure_ascii=False))
        raise SystemExit(1)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({'status': 'error', 'error': f'{type(error).__name__}: {error}'}, ensure_ascii=False))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False))
    if result['status'] == 'mismatch':
        raise SystemExit(1)


if __name__ == "__main__":
    main()
