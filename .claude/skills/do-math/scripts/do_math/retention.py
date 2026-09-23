"""Conservative cleanup of explicitly approved, archived execution spaces.

The caller holds the instance writer lock and supplies current state again at
deletion time. This is not a security boundary against hostile same-user writes.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

from .context_store import _read_stable
from .git_store import PhysicalBoundary


def _physical(path):
    path = Path(os.path.abspath(path))
    for part in [*reversed(path.parents), path]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('path crosses reparse point: ' + str(part))
    return path


def _run_path(workspace, execution_id):
    if not isinstance(execution_id, str) or not execution_id or any(c in execution_id for c in '/\\\\:') or execution_id in {'.', '..'}:
        raise ValueError('invalid execution path segment')
    root = _physical(workspace)
    path = _physical(root / 'runs' / execution_id)
    if path.parent != root / 'runs':
        raise ValueError('execution path outside workspace/runs')
    return path


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _strings(item)


def _references_run(workspace, path, references):
    for reference in _strings(references):
        candidate = Path(reference.replace('\\\\', '/'))
        candidate = candidate if candidate.is_absolute() else Path(workspace) / candidate
        # An alias can refer into the run even when its lexical spelling does
        # not. Refuse uncertain/reparse reference paths instead of following
        # them and treating an external target as a new trusted root.
        candidate = _physical(candidate)
        if candidate == path or candidate.is_relative_to(path) or path.is_relative_to(candidate):
            return True
    return False


def reference_closure(references, records):
    """Resolve record IDs to their explicit source/reference edges, cycle-safely.

    Unknown identifiers are returned, never treated as an empty dependency set.
    Paths are leaves; records may contain references, dependencies, source_refs,
    input_refs, artifact_ref, path, or checkpoint_ref.
    """
    pending = list(_strings(references)); seen, paths, unresolved = set(), set(), set()
    while pending:
        reference = pending.pop()
        if reference in seen:
            continue
        seen.add(reference)
        if reference in records:
            row = records[reference]
            for key in ('references', 'dependencies', 'source_refs', 'input_refs', 'artifact_ref', 'path', 'checkpoint_ref'):
                pending.extend(_strings(row.get(key, [])))
        elif '/' in reference or '\\' in reference or ':' in reference:
            paths.add(reference)
        else:
            unresolved.add(reference)
    return paths, unresolved


def _inventory(path):
    result = {}
    if not path.is_dir():
        raise ValueError('execution directory missing')
    boundary = PhysicalBoundary(path)
    def unreadable(error):
        raise error
    for base, dirs, files in os.walk(path, followlinks=False, onerror=unreadable):
        for name in dirs + files:
            _physical(Path(base) / name)
        for name in files:
            file = Path(base) / name
            data = _read_stable(file, boundary=boundary)
            result[file.relative_to(path).as_posix()] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return result


def _archive_reference(path, snapshot):
    if (not isinstance(snapshot, str) or len(snapshot) not in (40, 64)
            or any(c not in '0123456789abcdef' for c in snapshot)
            or not isinstance(path, str) or not path.startswith('runtime/artifacts/')
            or any(part in {'', '.', '..'} for part in path.split('/'))
            or '\\' in path or ':' in path):
        raise ValueError('invalid immutable archive reference')


def cleanup_candidates(workspace, executions, *, protected_references,
                       approved_execution_ids=None, read_artifact=None, runtime=None, reference_records=None):
    """Verify every file against collection.retention_manifest rows.

    Each row: path (relative to run), artifact_ref, snapshot, sha256, bytes.
    read_artifact(path, snapshot) reads the archive, never the local run copy.
    """
    candidates = []
    references, unresolved = reference_closure(protected_references, reference_records or {})
    for identifier, execution in sorted(executions.items()):
        reasons, inventory = ['unresolved_reference: ' + ref for ref in sorted(unresolved)], {}
        try:
            path = _run_path(workspace, identifier)
            if _references_run(workspace, path, references):
                reasons.append('protected_reference')
            inventory = _inventory(path)
        except (ValueError, OSError) as error:
            reasons.append(str(error))
        if not isinstance(execution, dict) or execution.get('id') != identifier:
            reasons.append('invalid_execution_record')
            execution = {}
        if execution.get('status') != 'ended':
            reasons.append('execution_not_ended')
        termination = execution.get('termination', {})
        if not isinstance(termination, dict):
            termination = {}
        if termination.get('local_terminated') is not True or not termination.get('evidence_ref'):
            reasons.append('termination_unconfirmed')
        else:
            try:
                _archive_reference(termination['evidence_ref'], termination['snapshot'])
                receipt = read_artifact(termination['evidence_ref'], termination['snapshot'])
                if hashlib.sha256(receipt).hexdigest() != termination['sha256'] or len(receipt) != termination['bytes']:
                    raise ValueError('termination receipt hash/size differs')
                fact = json.loads(receipt)
                if not isinstance(fact, dict) or fact.get('execution_id') != identifier or fact.get('local_terminated') is not True:
                    raise ValueError('termination receipt does not confirm this execution')
            except (TypeError, ValueError, KeyError, OSError, RuntimeError) as error:
                reasons.append('termination_unverified: ' + str(error))
        if execution.get('recovery_pending') or execution.get('checkpoint_required') or execution.get('recovery_disposition') in {'preserve_space_and_reservations', 'reconcile_local_and_remote', 'retain_for_recheck'}:
            reasons.append('recovery_pending')
        if runtime is None:
            reasons.append('current_recovery_and_reservations_unexamined')
        else:
            for reservation in runtime.get('reservations', {}).values():
                if reservation.get('owner_id') == identifier and reservation.get('state') != 'settled':
                    reasons.append('unsettled_reservation')
            for waiting in runtime.get('waiting_actions', {}).values():
                if identifier in set(_strings(waiting)) and not waiting.get('resolved'):
                    reasons.append('recovery_pending')
            for recovery in runtime.get('recoveries', {}).values():
                if identifier == recovery.get('execution_id') or identifier in recovery.get('execution_ids', []):
                    if recovery.get('status') not in {'resolved', 'finished', 'closed', 'completed'}:
                        reasons.append('recovery_pending')
            for activity in runtime.get('activities', {}).values():
                if identifier in activity.get('assigned_execution_ids', []) and (activity.get('status') != 'finished' or activity.get('unresolved')):
                    reasons.append('activity_obligation_pending')
        if approved_execution_ids is None or identifier not in approved_execution_ids:
            reasons.append('outside_approved_scope')
        collection = execution.get('collection')
        manifest = collection.get('retention_manifest') if isinstance(collection, dict) else None
        if not isinstance(manifest, list) or read_artifact is None:
            reasons.append('artifacts_not_verified')
        else:
            archived = {}
            for row in manifest:
                try:
                    local = row['path']; archive = row['artifact_ref']; snapshot = row['snapshot']
                    _archive_reference(archive, snapshot)
                    if local in archived:
                        raise ValueError('invalid archive reference')
                    raw = read_artifact(archive, snapshot)
                    proof = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                    if proof != {k: row[k] for k in proof}:
                        raise ValueError('archive hash/size mismatch')
                    archived[local] = proof
                except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
                    reasons.append('archive_unverified: ' + str(error))
            if inventory != archived:
                reasons.append('archive_does_not_cover_current_files')
        candidates.append({'execution_id': identifier, 'path': f'runs/{identifier}',
                           'eligible': not reasons, 'reasons': sorted(set(reasons)), 'inventory': inventory})
    return candidates


def cleanup(workspace, candidates, *, current_state=None, read_artifact=None):
    """Re-read eligibility immediately before removal; never mutate research state.

    current_state() supplies executions, protected_references,
    approved_execution_ids, runtime under the caller's writer lock.
    """
    deleted, failures = [], []
    for candidate in candidates:
        if not candidate.get('eligible'):
            continue
        try:
            if current_state is None:
                raise ValueError('current cleanup prerequisites are required')
            state = current_state()
            identifier = candidate['execution_id']
            execution = state['executions'].get(identifier)
            if execution is None:
                raise ValueError('execution disappeared from current state')
            refreshed = cleanup_candidates(workspace, {identifier: execution},
                protected_references=state['protected_references'], approved_execution_ids=state['approved_execution_ids'],
                read_artifact=read_artifact, runtime=state['runtime'], reference_records=state.get('reference_records'))[0]
            if not refreshed['eligible'] or refreshed['inventory'] != candidate['inventory']:
                raise ValueError('cleanup prerequisites changed: ' + ', '.join(refreshed['reasons']))
            path = _run_path(workspace, identifier)
            if _inventory(path) != candidate['inventory']:
                raise ValueError('cleanup files changed')
            shutil.rmtree(path)
            deleted.append(f'runs/{identifier}')
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
            failures.append({'path': candidate.get('path'), 'error': str(error),
                             'status': 'degraded', 'next_owner': 'maintenance'})
    return {'deleted': deleted, 'failures': failures, 'status': 'degraded' if failures else 'healthy'}


def pending_cleanup_failures(runtime):
    """Derive unresolved path failures from the actual maintenance history.

    An unrelated healthy attempt does not clear an older failure. Only deletion
    of that exact path establishes cleanup completion; research effect is not
    part of this operational projection.
    """
    pending = {}
    for index, event in enumerate(runtime.get('history', [])):
        if event.get('kind') == 'maintenance_cleanup_failed':
            reference = 'runtime/history/' + str(index)
            pending[reference] = {'path': None, 'error': event.get('reason'), 'status': 'degraded',
                'next_owner': 'maintenance', 'execution_id': event.get('execution_id'), 'evidence_ref': reference}
            continue
        if event.get('kind') != 'maintenance_cleanup':
            continue
        result = event.get('result', {})
        for path in result.get('deleted', []):
            pending.pop(path, None)
        for failure in result.get('failures', []):
            path = failure.get('path')
            pending[path] = {**failure, 'status': 'degraded', 'next_owner': 'maintenance',
                             'execution_id': event.get('execution_id'),
                             'evidence_ref': 'runtime/history/' + str(index)}
    return list(pending.values())
