"""Pure manifest contracts and cancellable, bounded full-scope file observation."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import threading
import stat

from .operation_trace import phase

ROLES = {'lean_binary', 'lean_source', 'lake_binary', 'mathlib_source', 'mathlib_build', 'checker'}
AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
_scan_gate = threading.BoundedSemaphore(1)


def _strings(value):
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def manifest_structure_errors(manifest):
    """Small structural envelope; per-file contracts retain their immutable cache."""
    if not isinstance(manifest, dict):
        return ['trust manifest must be an object']
    errors = []
    if set(manifest) != {'command', 'foundation_profile', 'scope', 'files', 'validation'}:
        errors.append('trust manifest fields differ from the current contract')
    if not _strings(manifest.get('command')) or not manifest.get('command'):
        errors.append('trust manifest command must be a nonempty argv')
    if not isinstance(manifest.get('files'), list):
        errors.append('trust manifest files must be a list')
    foundation = manifest.get('foundation_profile')
    if not isinstance(foundation, dict) or any(not _strings(foundation.get(key)) for key in ('allowed_axioms', 'forbidden')):
        errors.append('foundation profile must declare string lists of allowed and forbidden axioms')
    from .trust_inventory import scope_errors
    errors.extend(scope_errors(manifest.get('scope')))
    validation = manifest.get('validation')
    if not isinstance(validation, dict) or set(validation) != {'record', 'sha256'}:
        errors.append('trust validation requires a sealed self-contained record')
    return errors


def manifest_errors(environment):
    from .repository import exact_content_hash
    from .formal import toolchain_errors
    if not isinstance(environment, dict):
        return ['trust environment absent']
    manifest = environment.get('manifest', {})
    errors = toolchain_errors(environment.get('toolchain'))
    if not isinstance(manifest, dict) or environment.get('manifest_sha256') != exact_content_hash(manifest):
        return ['trust manifest missing or changed']
    structural = manifest_structure_errors(manifest)
    if structural:
        return errors + structural
    if not environment.get('source_ref'):
        errors.append('trust environment has no explicit adoption')
    if not _strings(environment.get('allowed_axioms')) or set(environment['allowed_axioms']) != AXIOMS:
        errors.append('foundation axiom profile differs')
    foundation = manifest.get('foundation_profile', {})
    if foundation.get('allowed_axioms') != sorted(AXIOMS) or not {'sorryAx', 'Lean.trustCompiler', 'additional_axioms'}.issubset(foundation.get('forbidden', [])):
        errors.append('foundation profile is incomplete')
    toolchain = environment.get('toolchain')
    command = toolchain.get('configured_command') if isinstance(toolchain, dict) else None
    if not command or manifest.get('command') != command:
        errors.append('manifest command differs from toolchain')
    from .payloads import FrozenDict
    if isinstance(manifest, FrozenDict) and hasattr(manifest, '_files_contract_errors'):
        errors.extend(manifest._files_contract_errors)
    else:
        file_errors = manifest_file_errors(manifest.get('files', []))
        errors.extend(file_errors)
        if isinstance(manifest, FrozenDict):
            manifest._files_contract_errors = tuple(file_errors)
    if not errors:
        from .trust_inventory import binding_errors, validation_errors
        identity = exact_content_hash(toolchain)
        cached = getattr(manifest, '_inventory_contract', None)
        if cached is None or cached[0] != identity:
            inventory_digest=exact_content_hash({'scope':manifest['scope'],'files':manifest['files']})
            checks = binding_errors(environment) + validation_errors(manifest['validation'], toolchain, inventory_digest)
            cached = (identity, tuple(checks))
            if isinstance(manifest, FrozenDict):
                manifest._inventory_contract = cached
        errors.extend(cached[1])
    return errors


def manifest_file_errors(files):
    errors = []
    if not isinstance(files, list) or not files:
        errors.append('manifest needs a nonempty complete file inventory')
    else:
        paths = set()
        for entry in files:
            if not isinstance(entry, dict) or entry.get('role') not in ROLES:
                errors.append('manifest file must declare a role')
                continue
            if not isinstance(entry, dict) or not isinstance(entry.get('path'), str) or not Path(entry['path']).is_absolute():
                errors.append('manifest file must have an absolute path')
                continue
            # Lexical only: status/schema validation must not inspect the host.
            key = os.path.normcase(os.path.normpath(entry['path']))
            if key in paths:
                errors.append('duplicate manifest path')
            paths.add(key)
            if not re.fullmatch('[0-9a-f]{64}', str(entry.get('sha256', ''))):
                errors.append('manifest file needs an exact SHA-256')
    return errors


def _observe_file(entry, cancelled, account_bytes):
    path = Path(entry['path'])
    read = 0
    try:
        resolved = str(path.resolve(strict=True)).casefold()
        before = path.stat()
        if path.is_symlink() or not stat.S_ISREG(before.st_mode):
            return resolved, ['trust file changed: ' + str(path)], read
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            while not cancelled.is_set():
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                read += len(chunk)
                digest.update(chunk)
                account_bytes(len(chunk))
            after_open = os.fstat(stream.fileno())
        if cancelled.is_set():
            return resolved, ['file observation cancelled'], read
        after = path.stat()
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
        # Windows path stat and handle fstat expose different ctime semantics.
        # Compare each observation channel against itself, not against the other.
        stable = (identity(before) == identity(opened) == identity(after_open) == identity(after)
                  and before.st_ctime_ns == after.st_ctime_ns
                  and opened.st_ctime_ns == after_open.st_ctime_ns)
        if not stable or digest.hexdigest() != entry['sha256']:
            return resolved, ['trust file changed: ' + str(path)], read
        return resolved, [], read
    except (OSError, RuntimeError):
        return None, ['trust file unavailable: ' + str(path)], read


def verify_environment_files(environment, *, should_stop=None, on_progress=None, workers=4):
    if not isinstance(environment, dict):
        return {'status':'invalid','errors':['trust environment absent']}
    with phase('environment_scan_wait', manifest_sha256=environment.get('manifest_sha256')):
        while not _scan_gate.acquire(timeout=.1):
            if should_stop and should_stop():
                return {'status':'cancelled','manifest_sha256':environment.get('manifest_sha256'),
                        'errors':['environment observation cancelled before admission'],
                        'completed_files':0,'read_bytes':0,'peak_pending':0}
    try:
        return _verify_environment_files(environment, should_stop=should_stop, on_progress=on_progress, workers=workers)
    finally:
        _scan_gate.release()


def _verify_environment_files(environment, *, should_stop=None, on_progress=None, workers=4):
    """Observe every declared file afresh. A result certifies this observation only."""
    if type(workers) is not int or not 1 <= workers <= 16:
        raise ValueError('environment workers must be in 1..16')
    fixed = deepcopy(environment)
    errors = manifest_errors(fixed)
    started = datetime.now(timezone.utc).isoformat()
    manifest = fixed.get('manifest')
    files = manifest.get('files') if isinstance(manifest, dict) else None
    base = {'manifest_sha256': fixed.get('manifest_sha256'), 'started_at': started,
            'file_count': len(files) if isinstance(files, list) else 0,
            'completed_files': 0, 'read_bytes': 0, 'peak_pending': 0}
    if errors:
        return {**base, 'status': 'invalid', 'errors': errors}
    from .trust_inventory import inventory, _key
    try:
        observed_members = inventory(fixed['manifest']['scope'], should_stop=should_stop)
        declared = {_key(row['path']):{'path':row['path'], 'role':row['role']} for row in files}
        if observed_members != declared:
            missing = sorted(set(observed_members) - set(declared))
            extra = sorted(set(declared) - set(observed_members))
            return {**base, 'status':'invalid', 'errors':['inventory membership differs'],
                    'missing_files':missing, 'extra_files':extra}
    except InterruptedError:
        return {**base,'status':'cancelled','errors':['inventory observation cancelled']}
    except (OSError,ValueError) as error:
        return {**base,'status':'invalid','errors':[str(error)]}
    files = fixed['manifest']['files']
    cancelled = threading.Event()
    read_bytes = 0
    byte_lock = threading.Lock()
    def account_bytes(count):
        nonlocal read_bytes
        with byte_lock:
            read_bytes += count
    results, pending, cursor = {}, {}, 0
    with phase('environment_files', manifest_sha256=base['manifest_sha256'], file_count=len(files)) as metrics:
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix='do-math-environment') as pool:
            try:
                while pending or cursor < len(files):
                    if should_stop and should_stop():
                        cancelled.set()
                    while not cancelled.is_set() and cursor < len(files) and len(pending) < workers * 2:
                        pending[pool.submit(_observe_file, files[cursor], cancelled, account_bytes)] = cursor
                        cursor += 1
                    base['peak_pending'] = max(base['peak_pending'], len(pending))
                    if not pending:
                        break
                    done, _ = wait(pending, timeout=.1, return_when=FIRST_COMPLETED)
                    for future in done:
                        index = pending.pop(future)
                        results[index] = future.result()
                        base['completed_files'] += 1
                    with byte_lock:
                        base['read_bytes'] = read_bytes
                    metrics.update({k:base[k] for k in ('completed_files','read_bytes','peak_pending')})
                    if done and on_progress:
                        on_progress({k: base[k] for k in ('file_count', 'completed_files', 'read_bytes', 'peak_pending')})
            finally:
                cancelled.set() if cursor < len(files) or pending else None
        paths = set()
        for index in sorted(results):
            resolved, findings, _ = results[index]
            if resolved is not None:
                if resolved in paths:
                    errors.append('duplicate manifest path')
                paths.add(resolved)
            errors.extend(findings)
        stopped = cancelled.is_set() or base['completed_files'] != len(files) or any('cancelled' in e for e in errors)
        if not stopped:
            try:
                if inventory(fixed['manifest']['scope'], should_stop=should_stop) != observed_members:
                    errors.append('inventory membership changed during observation')
            except InterruptedError:
                stopped = True
                errors.append('inventory observation cancelled')
            except (OSError,ValueError) as error:
                errors.append(str(error))
        metrics.update({k:base[k] for k in ('completed_files','read_bytes','peak_pending')})
        return {**base, 'finished_at': datetime.now(timezone.utc).isoformat(),
                'status': 'cancelled' if stopped else 'invalid' if errors else 'verified', 'errors': errors}
