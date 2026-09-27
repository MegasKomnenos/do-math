"""Shared toolchain records: installation identity, fingerprints and content baselines.

One record file describes one installed Lean/Mathlib identity. setup_lean.py
writes it when a toolchain is installed or replaced, re-recorded or explicitly
content-checked; research instances only read it. The threat model is
accidental change (updates, reinstallation, synchronization, mistakes, disk
damage). A fingerprint row is the scandir metadata of one judgment file, so
bytes changed while size and both times are preserved are found only by an
explicit content check against the recorded full hashes.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator

from .repository import exact_content_hash
from .file_io import fingerprint_json, now, os_lock, sha256_file, stat_fingerprint
from .trust_validation import RECORD_ID_PATTERN

SMOKE = 'import Mathlib\nexample (n : Nat) : n + 0 = n := by rfl\nexample : (2 : ℝ) + 2 = 4 := by norm_num\n'
CORE_SMOKE = 'example (n : Nat) : n + 0 = n := by rfl\nexample : True := True.intro\n'
SCHEMA = 'do-math-toolchain-record/1'
# Imported modules and the runtime libraries that contain the kernel. The thin
# lean.exe/lake.exe launchers and the checker are bound by the identity hashes.
JUDGMENT_SUFFIXES = ('.olean', '.dll', '.so', '.dylib')
VALIDATION_SUMMARY = ('command', 'source_sha256', 'exit_code', 'stdout', 'stderr', 'started_at', 'finished_at')

_TEXT = {'type': 'string'}
_HASH = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
_NANOSECONDS = {'type': 'string', 'pattern': '^[0-9]+$'}
_BASELINE = {'type': 'object', 'additionalProperties': False,
    'required': ['recorded_at', 'fingerprint', 'content', 'validation', 'validation_sha256'],
    'properties': {
        'recorded_at': _TEXT,
        'fingerprint': {'type': 'object', 'additionalProperties': False, 'required': ['files', 'sha256'],
            'properties': {'sha256': _HASH, 'files': {'type': 'object', 'additionalProperties': {
                'type': 'array', 'minItems': 3, 'maxItems': 3,
                'prefixItems': [{'type': 'integer', 'minimum': 0}, _NANOSECONDS, _NANOSECONDS]}}}},
        'content': {'type': 'object', 'additionalProperties': False, 'required': ['files', 'sha256'],
            'properties': {'sha256': _HASH, 'files': {'type': 'object', 'additionalProperties': _HASH}}},
        'validation': {'type': 'object', 'additionalProperties': False,
            'required': ['status', 'scope', 'source', 'source_text', 'source_sha256', 'command',
                         'exit_code', 'stdout', 'stderr', 'started_at', 'finished_at'],
            'properties': {'status': {'enum': ['verified', 'failed']}, 'scope': _TEXT, 'source': _TEXT,
                'source_text': _TEXT, 'source_sha256': _HASH, 'command': {'type': 'array', 'items': _TEXT},
                'exit_code': {'type': ['integer', 'null']}, 'stdout': _TEXT, 'stderr': _TEXT,
                'started_at': _TEXT, 'finished_at': _TEXT, 'error': _TEXT}},
        'validation_sha256': _HASH}}
RECORD_SCHEMA = {'type': 'object', 'additionalProperties': False,
    'required': ['schema', 'id', 'identity', 'identity_sha256', 'baselines', 'checks'],
    'properties': {
        'schema': {'const': SCHEMA},
        'id': {'type': 'string', 'pattern': RECORD_ID_PATTERN},
        'identity': {'type': 'object'},
        'identity_sha256': _HASH,
        'baselines': {'type': 'array', 'minItems': 1, 'items': _BASELINE},
        'checks': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
            'required': ['checked_at', 'baseline', 'result', 'mismatched'],
            'properties': {'checked_at': _TEXT, 'baseline': {'type': 'integer', 'minimum': 0},
                'result': {'enum': ['passed', 'mismatch']}, 'mismatched': {'type': 'array', 'items': _TEXT}}}}}}
_VALIDATOR = Draft202012Validator(RECORD_SCHEMA)


def validation_program(toolchain):
    return ((SMOKE, 'mathlib_import_and_representative_proofs') if toolchain.get('project') is not None
            else (CORE_SMOKE, 'lean_core_representative_proofs'))


def roots(identity):
    """Named fingerprint roots: the Lean installation and the Lake project, if any."""
    executable = Path(identity['executable'])
    result = {'toolchain': executable.parent.parent if executable.parent.name.lower() == 'bin' else executable.parent}
    if identity.get('project') is not None:
        result['project'] = Path(identity['project']['source_identity']['root'])
    return result


def _key(path):
    return os.path.normcase(os.path.normpath(str(path)))


def identity_errors(identity):
    """Lexical scope rules of an identity; no host path is resolved or read."""
    from .formal import toolchain_errors
    errors = toolchain_errors(identity)
    if errors:
        return errors
    named = {name: Path(_key(path)) for name, path in roots(identity).items()}
    if any(a != b and (named[a] == named[b] or named[a].is_relative_to(named[b])) for a in named for b in named):
        errors.append('toolchain and project roots must not overlap')
    for path in (identity['project'] or {}).get('search_paths', []):
        if not any(Path(_key(path)).is_relative_to(root) for root in named.values()):
            errors.append('Lean search path is outside the recorded toolchain and project roots: ' + path)
    return errors


def observe_fingerprint(identity):
    """Rows (size, modification ns, creation ns) of every judgment file under the roots."""
    rows = {}
    for name, base in sorted(roots(identity).items()):
        _scan(base, name, rows)
    return {'files': rows, 'sha256': exact_content_hash(rows)}


def _scan(directory, prefix, rows):
    with os.scandir(directory) as entries:
        for entry in entries:
            relative = prefix + '/' + entry.name
            if entry.is_dir(follow_symlinks=False):
                if entry.name != '.git':
                    _scan(entry.path, relative, rows)
            elif entry.name.lower().endswith(JUDGMENT_SUFFIXES):
                rows[relative] = fingerprint_json(stat_fingerprint(entry.stat(follow_symlinks=False)))


def changed_files(expected, observed):
    return sorted(path for path in set(expected) | set(observed) if expected.get(path) != observed.get(path))


def content_hashes(identity, paths):
    """Full SHA-256 of each named file; used at recording and explicit content checks only."""
    base = roots(identity)
    def one(relative):
        name, _, rest = relative.partition('/')
        return relative, sha256_file(base[name] / rest)
    with ThreadPoolExecutor(max_workers=4) as pool:
        files = dict(pool.map(one, sorted(paths)))
    return {'files': files, 'sha256': exact_content_hash(files)}


def validation_sha256(validation):
    return exact_content_hash({key: validation.get(key) for key in VALIDATION_SUMMARY})


def new_baseline(fingerprint, content, validation):
    return {'recorded_at': now(), 'fingerprint': fingerprint, 'content': content,
            'validation': validation, 'validation_sha256': validation_sha256(validation)}


def record_path(directory, record_id):
    """The file of one toolchain record: <record ID>.json in its records directory."""
    return Path(directory) / (record_id + '.json')


def record_id(identity, content_sha256):
    return 'TC-' + exact_content_hash({'identity_sha256': exact_content_hash(identity), 'content_sha256': content_sha256})


def new_record(identity, baseline):
    return {'schema': SCHEMA, 'id': record_id(identity, baseline['content']['sha256']), 'identity': identity,
            'identity_sha256': exact_content_hash(identity), 'baselines': [baseline], 'checks': []}


def binding(record, index=None):
    """The instance-side reference to one baseline entry of a record."""
    index = len(record['baselines']) - 1 if index is None else index
    entry = record['baselines'][index]
    return {'baseline': index, 'fingerprint_sha256': entry['fingerprint']['sha256'],
            'content_sha256': entry['content']['sha256'], 'validation_sha256': entry['validation_sha256']}


def record_errors(record):
    """Schema and self-consistency of a record; the listed file hashes are not recomputed."""
    error = next(_VALIDATOR.iter_errors(record), None)
    if error is not None:
        return ['toolchain record differs from ' + SCHEMA + ': ' + '/'.join(map(str, error.absolute_path))
                + ': ' + error.message]
    errors = identity_errors(record['identity'])
    if record['identity_sha256'] != exact_content_hash(record['identity']):
        errors.append('toolchain record identity digest differs from its identity')
    elif record['id'] != record_id(record['identity'], record['baselines'][0]['content']['sha256']):
        errors.append('toolchain record ID differs from its identity and first content baseline')
    if any(check['baseline'] >= len(record['baselines']) for check in record['checks']):
        errors.append('toolchain record check names an absent baseline')
    return errors


def usable_errors(record):
    """A current baseline with a successful representative check and no later mismatch."""
    current = len(record['baselines']) - 1
    validation = record['baselines'][current]['validation']
    errors = []
    if validation['status'] != 'verified' or validation['exit_code'] != 0:
        errors.append('current toolchain baseline has no successful representative check')
    if any(check['baseline'] == current and check['result'] == 'mismatch' for check in record['checks']):
        errors.append('a content check found files that differ from the current toolchain baseline')
    return errors


def read_record(path):
    from .file_io import read_bytes_shared
    record = json.loads(read_bytes_shared(path))
    errors = record_errors(record)
    if errors:
        raise ValueError('; '.join(errors))
    return record


def write_record(path, record):
    from .file_io import write_bytes_atomic
    from .repository import canonical_json
    errors = record_errors(record)
    if errors:
        raise ValueError('; '.join(errors))
    write_bytes_atomic(path, canonical_json(record))


@contextmanager
def writer_lock(directory):
    """Exclude other record writers with the OS lock of ``directory/.lock``; ``OSError`` while another holds it.

    The OS releases the lock when its holder ends, so a killed writer leaves nothing to remove.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with os_lock(directory / '.lock', blocking=False):
        yield


def records_for(directory, identity):
    """Record files in a records directory that describe exactly this identity."""
    wanted = exact_content_hash(identity)
    found = []
    for path in sorted(Path(directory).glob(record_path('', 'TC-*').name)):
        record = read_record(path)
        if record['identity_sha256'] == wanted:
            found.append((path, record))
    return found
