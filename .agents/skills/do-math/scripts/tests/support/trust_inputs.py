"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
from do_math.file_io import sha256_file
from do_math.lean_evidence import AXIOMS


def validation_fixture(toolchain, source):
    """Explicit compiler double; never present this record as native validation."""
    from do_math.trust_inventory import validation_program
    text,scope=validation_program(toolchain)
    return {'status':'verified','scope':scope,'source':str(source.resolve()),'source_text':text,
        'source_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'command':[*toolchain['configured_command'],str(source.resolve())],
        'exit_code':0,'stdout':'synthetic external compiler result','stderr':'',
        'started_at':'2026-09-20T00:00:00Z','finished_at':'2026-09-20T00:00:01Z'}


SYNTHETIC_TOOLCHAIN_FILES = ('bin/lean.exe', 'bin/lake.exe', 'bin/libleanshared.dll', 'lib/lean/Init/Prelude.olean')


def trust_fixture(root, command, *, directory=None):
    """A synthetic installation, its shared toolchain record and the registration request.

    The checker identity is the real formal.py, so publication gates recompute a
    consistent identity. Each call owns a new directory and record; ``directory``
    names it (a new empty directory) where a run must be reproducible.
    """
    from support.entry import entry
    _entry = entry()
    import tempfile
    from do_math import formal, trust_inventory as records
    Path(root).mkdir(parents=True, exist_ok=True)
    if directory is None:
        directory = tempfile.mkdtemp(prefix='synthetic-trust-', dir=root)
    else:
        Path(directory).mkdir(parents=True)
    directory = Path(directory).resolve()
    for relative in SYNTHETIC_TOOLCHAIN_FILES:
        path = directory / 'toolchain' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("CORE_TESTS synthetic " + relative + " for " + " ".join(command)).encode())
    lean, lake = directory / 'toolchain/bin/lean.exe', directory / 'toolchain/bin/lake.exe'
    checker = Path(formal.__file__).resolve()
    toolchain = {"executable": str(lean), "sha256": sha256_file(lean), "version": "Lean test 4.32.0",
                 "version_exit": 0, "configured_command": list(command),
                 "verifier_sha256": sha256_file(checker), "verifier_path": str(checker),
                 "executables": {str(lean): sha256_file(lean), str(lake): sha256_file(lake)}, "project": None}
    fingerprint = records.observe_fingerprint(toolchain)
    content = records.content_hashes(toolchain, fingerprint['files'])
    record = records.new_record(toolchain, records.new_baseline(
        fingerprint, content, validation_fixture(toolchain, directory / 'smoke.lean'), clock=_entry.ports.clock))
    path = directory / 'records' / (record['id'] + '.json')
    records.write_record(path, record)
    return {"operation": "register", "toolchain": toolchain, "allowed_axioms": sorted(AXIOMS),
            "toolchain_record": {"path": str(path), "id": record['id']}, "binding": records.binding(record)}


def trust_environment(request, *, environment_id='TE-fixture', status='active', source_ref='fixture:trust'):
    """The instance record and runtime binding that registering this request produces.

    Store the record in instance['trust_environments'] and the binding in
    runtime['trust_bindings'] under the same ID.
    """
    environment = {'id': environment_id, 'status': status, 'toolchain': deepcopy(request['toolchain']),
                   'allowed_axioms': list(request['allowed_axioms']), 'source_ref': source_ref,
                   'toolchain_record': deepcopy(request['toolchain_record'])}
    return environment, deepcopy(request['binding'])


def setup_recording(root, *, kind='core', search_path_count=0):
    """Small real setup writer/worker, with only the external compiler and Lake environment doubled.

    No identity, validation or record is filled in after setup returns. The clock
    is ahead of these fresh files so the metadata settling check can finish.
    """
    from datetime import datetime, timedelta, timezone
    import json
    import sys
    from support.entry import entry
    from support.fakes.clock import FakeClock
    from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs
    from support.lean import LeanDouble
    from do_math import trust_inventory as records
    values = entry()
    root = Path(root).resolve()
    for relative in SYNTHETIC_TOOLCHAIN_FILES:
        path = root / 'toolchain' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(('setup external double ' + relative).encode())
    lean_path, lake_path = root / 'toolchain/bin/lean.exe', root / 'toolchain/bin/lake.exe'
    command, paths = [str(lean_path)], []
    if kind == 'project':
        project = root / 'project'
        project.mkdir()
        (project / 'lean-toolchain').write_text('leanprover/lean4:v4.32.0\n', encoding='utf-8')
        (project / 'lakefile.toml').write_text('name = "setup_fixture"\n', encoding='utf-8')
        for index in range(search_path_count):
            directory = project / '.lake' / ('library-' + str(index))
            directory.mkdir(parents=True)
            (directory / 'Fixture.olean').write_bytes(b'synthetic project judgment file')
            paths.append(str(directory))
        command = [str(lake_path), '--dir', str(project), 'env', str(lean_path)]
    elif kind != 'core' or search_path_count:
        raise ValueError('core has no project search paths')
    lean = LeanDouble()
    source = records.SMOKE if kind == 'project' else records.CORE_SMOKE
    # As in InstallationCosts: an explicitly registered representative program,
    # not an inferred proof and not a prebuilt validation record.
    lean.inputs[source.encode('utf-8')] = {}
    environment_compiler = OutputCompiler(json.dumps({'cwd': str(root), 'paths': paths}))

    def spawn(argv, **options):
        if sys.executable in argv and '-c' in argv:
            return environment_compiler(argv, **options)
        return lean.spawn(argv, **options)

    return {'command': command, 'lean': lean, 'search_paths': paths,
            'environment_compiler': environment_compiler, 'records_dir': root / 'records',
            'evidence_root': root / 'evidence', 'jobs': worker_jobs(spawn),
            'clock': FakeClock(wall=datetime.now(timezone.utc) + timedelta(seconds=2)),
            'environment': values.environment, 'git_backend': values.ports.git_backend}


def setup_request_runs(root):
    """Actual new/reused/rerecorded setup requests; core and project paths 0/1/many."""
    import json
    import os
    import setup_lean
    from do_math import trust_inventory as records
    for kind, count in (('core', 0), ('project', 0), ('project', 1), ('project', 2)):
        directory = Path(root) / (kind + '-' + str(count))
        fixture = setup_recording(directory, kind=kind, search_path_count=count)
        options = {key: fixture[key] for key in ('jobs', 'clock', 'environment', 'git_backend')}
        for operation in ('new', 'reused', 'rerecorded'):
            if operation == 'rerecorded':
                path = directory / 'toolchain/lib/lean/Init/Prelude.olean'
                stat = path.stat()
                os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns - 2_000_000_000))
                result = setup_lean.rerecord(fixture['command'], fixture['records_dir'], fixture['evidence_root'],
                    None, **options)
            else:
                result = setup_lean.record_installation(fixture['command'], fixture['records_dir'],
                    fixture['evidence_root'], **options)
            destination = directory / (operation + '-request.json')
            published = setup_lean.write_trust_request(result, destination)
            yield f'{kind}, paths={count}, {operation}', {
                'fixture': fixture, 'operation': operation, 'result': result, 'published': published,
                'request_path': destination, 'request': json.loads(destination.read_bytes()),
                'record': records.read_record(result['record_path']),
                'compile_count': len(fixture['lean'].checks)}
