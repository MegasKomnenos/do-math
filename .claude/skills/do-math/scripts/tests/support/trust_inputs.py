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
