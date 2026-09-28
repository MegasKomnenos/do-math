"""Conservative cleanup of explicitly approved, archived execution spaces.

The caller holds the instance writer lock and supplies current state again at
deletion time. This is not a security boundary against hostile same-user writes.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil

from .context_store import read_stable
from .file_io import check_path_segment, file_fingerprint, fingerprint_settled, no_reparse
from .git_store import ARTIFACT_ROOT, PhysicalBoundary, oid_shape
from .relation_refs import relation_references
from .repository import canonical_json, sealed_bytes
from .task_contracts import CONTEXT_INPUT_REFS, TOOL_INPUT_REFS


# The record fields whose values name records, artifacts or paths that a
# cleanup must keep. This one vocabulary decides every reference a record holds.
PROTECTED_REFERENCE_KEYS = frozenset({
    "references", "dependencies", "source_refs", "origin_refs", "input_refs", "inputs", "reuse",
    "artifact_ref", "path", "checkpoint_ref", "source_ref", "formal_result_id", "exposition_id",
    "assessment_id", "evidence_refs", "authority_refs", "basis_refs", "record_refs", "result_ref",
    "formal_result_refs", "assessment_refs"})
# The fields of a referring object that name its target.
_TARGET_FIELDS = ("id", "ref", "artifact_ref", "path")
# Issued semantic references that name no materialized run file.
_SEMANTIC_ALIASES = CONTEXT_INPUT_REFS | TOOL_INPUT_REFS


def _physical(path):
    path = Path(os.path.abspath(path))
    no_reparse(path)
    return path


def _run_path(workspace, execution_id):
    # The state path segment rule: Windows would store "EX-1." as the folder of "EX-1".
    check_path_segment(execution_id)
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


def _protected_paths(workspace, references):
    """The physical paths of protected references, resolved once per cleanup check.

    An alias can refer into a run even when its lexical spelling does not.
    Uncertain/reparse reference paths are refused instead of being followed
    and treating an external target as a new trusted root.
    """
    paths = []
    for reference in _strings(references):
        candidate = Path(reference.replace('\\\\', '/'))
        candidate = candidate if candidate.is_absolute() else Path(workspace) / candidate
        paths.append(_physical(candidate))
    return paths


def record_references(value):
    """The reference strings held under PROTECTED_REFERENCE_KEYS anywhere in ``value``.

    Under such a key a string is a reference, a list contributes its strings
    and the target fields of its objects, and an object contributes its target
    fields. Nested values are searched the same way. Task ``reuse`` lists record
    IDs; grant ``reuse`` is a policy word and names nothing.
    """
    result = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PROTECTED_REFERENCE_KEYS and not (key == "reuse" and isinstance(child, str)):
                if isinstance(child, str):
                    result.append(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, str):
                            result.append(item)
                        elif isinstance(item, dict):
                            result.extend(item[name] for name in _TARGET_FIELDS if isinstance(item.get(name), str))
                elif isinstance(child, dict):
                    result.extend(child[name] for name in _TARGET_FIELDS if isinstance(child.get(name), str))
            if isinstance(child, (dict, list)):
                result.extend(record_references(child))
    elif isinstance(value, list):
        for child in value:
            result.extend(record_references(child))
    return result


def retention_inputs(instance, runtime, rows):
    """The reference records and protected roots of one loaded snapshot.

    ``rows`` are the snapshot's persisted record rows (``load_records``). Each
    record maps to the references it holds; relations add their authored edges
    (``relation_refs``). Research records, tasks, question links and review
    cycles are protected roots, with every reference a waiting action holds.
    """
    records = {}
    for row in rows:
        if row.get("id"):
            references = set(record_references(row["record"]))
            if row["family"] == "relations":
                references |= relation_references(row["record"])
            records[row["id"]] = {"references": sorted(references)}
    for source in instance.get("sources", []):
        if source.get("id") in records:
            for alias in (source.get("name"), "source:" + source.get("name", "")):
                if alias:
                    records.setdefault(alias, {"references": [source["id"]]})
    for alias in _SEMANTIC_ALIASES:
        records.setdefault(alias, {"references": []})
    protected = [row["id"] for row in rows if row.get("id") and
                 (row["root"] == "research" or row["family"] in {"tasks", "question_links", "review_cycles"})]
    protected.extend(record_references(runtime.get("waiting_actions", {})))
    return records, protected


def reference_closure(references, records):
    """Resolve record IDs to their explicit source/reference edges, cycle-safely.

    Unknown identifiers are returned, never treated as an empty dependency set.
    Paths are leaves; each record lists its edges under ``references``
    (``retention_inputs``).
    """
    pending = list(_strings(references)); seen, paths, unresolved = set(), set(), set()
    while pending:
        reference = pending.pop()
        if reference in seen:
            continue
        seen.add(reference)
        if reference in records:
            pending.extend(_strings(records[reference].get('references', [])))
        elif '/' in reference or '\\' in reference or ':' in reference:
            paths.add(reference)
        else:
            unresolved.add(reference)
    return paths, unresolved


def _inventory(path, marks=None, contents=None):
    """Hash every local file once per cleanup.

    ``marks`` maps a file to (settled fingerprint, proof) from an earlier read in
    this cleanup; an unchanged fingerprint reuses the proof without reading.
    ``contents`` receives the bytes that were read.
    """
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
            relative = file.relative_to(path).as_posix()
            mark = file_fingerprint(file)
            known = marks.get(file) if marks is not None else None
            if known is not None and known[0] == mark:
                result[relative] = dict(known[1])
                continue
            data = read_stable(file, boundary=boundary)
            result[relative] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
            if contents is not None:
                contents[relative] = data
            if marks is not None and fingerprint_settled(mark) and file_fingerprint(file) == mark:
                marks[file] = (mark, dict(result[relative]))
    return result


def archive_run(workspace, identifier, execution, prefix, marks=None):
    """The archive of one locally terminated run below ``prefix``.

    Returns the artifact bytes to publish, the retention manifest rows and the
    termination evidence row. The archive holds exactly the bytes the inventory
    hashed, so the caller may record every row as matched once it is published.
    """
    contents = {}
    inventory = _inventory(_run_path(workspace, identifier), marks, contents)
    artifacts, manifest = {}, []
    for relative, proof in inventory.items():
        ref = prefix + '/files/' + relative
        artifacts[ref] = contents[relative]
        manifest.append({'path': relative, 'artifact_ref': ref, **proof})
    receipt = canonical_json({'execution_id': identifier, 'local_terminated': True,
        'basis': deepcopy(execution['capacity']), 'remote_termination': 'not_established'})
    ref = prefix + '/termination.json'
    artifacts[ref] = receipt
    return artifacts, manifest, {'local_terminated': True, 'evidence_ref': ref,
        'sha256': hashlib.sha256(receipt).hexdigest(), 'bytes': len(receipt)}


def _archive_reference(path, snapshot):
    # Reading the artifact validates the path with the Git state path rules.
    oid_shape(snapshot)
    if not isinstance(path, str) or not path.startswith(ARTIFACT_ROOT):
        raise ValueError('invalid immutable archive reference')


def cleanup_candidates(workspace, executions, *, protected_references,
                       approved_execution_ids=None, read_artifact=None, runtime=None, reference_records=None,
                       git_dir=None, marks=None):
    """Verify every file against collection.retention_manifest rows.

    Each row: path (relative to run), artifact_ref, snapshot, sha256, bytes.
    read_artifact(path, snapshot) reads the archive, never the local run copy.
    An archive row already matched in this process (repository.VERIFIED_ARTIFACTS
    of ``git_dir``) is not read again; ``marks`` is passed to ``_inventory``.
    """
    candidates = []
    references, unresolved = reference_closure(protected_references, reference_records or {})
    # One unresolvable protected path makes every run ineligible.
    try:
        protected_paths, protected_error = _protected_paths(workspace, references), None
    except (ValueError, OSError) as error:
        protected_paths, protected_error = [], str(error)
    for identifier, execution in sorted(executions.items()):
        reasons, inventory = ['unresolved_reference: ' + ref for ref in sorted(unresolved)], {}
        try:
            path = _run_path(workspace, identifier)
            if protected_error is not None:
                raise ValueError(protected_error)
            if any(candidate == path or candidate.is_relative_to(path) or path.is_relative_to(candidate)
                   for candidate in protected_paths):
                reasons.append('protected_reference')
            inventory = _inventory(path, marks)
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
                receipt = sealed_bytes(git_dir, termination['evidence_ref'], termination['sha256'], termination['bytes'],
                                       lambda: read_artifact(termination['evidence_ref'], termination['snapshot']))
                fact = json.loads(receipt)
                if not isinstance(fact, dict) or fact.get('execution_id') != identifier or fact.get('local_terminated') is not True:
                    raise ValueError('termination receipt does not confirm this execution')
            except (TypeError, ValueError, KeyError, OSError, RuntimeError) as error:
                reasons.append('termination_unverified: ' + str(error))
        # A recovery disposition lives only until the execution ends (execution_lifecycle.transition_execution),
        # so an ended execution holds no recovery marker; pending recovery is read from the runtime below.
        if runtime is None:
            reasons.append('current_recovery_and_reservations_unexamined')
        else:
            for reservation in runtime.get('reservations', {}).values():
                if reservation.get('owner_id') == identifier and reservation.get('state') != 'settled':
                    reasons.append('unsettled_reservation')
            for waiting in runtime.get('waiting_actions', {}).values():
                if identifier in set(_strings(waiting)):
                    reasons.append('recovery_pending')
            for recovery in runtime.get('recoveries', {}).values():
                if identifier in recovery.get('execution_ids', []) and not recovery.get('finished_at'):
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
                    proof = {'sha256': row['sha256'], 'bytes': row['bytes']}
                    sealed_bytes(git_dir, archive, proof['sha256'], proof['bytes'],
                                 lambda: read_artifact(archive, snapshot), needed=False)
                    archived[local] = proof
                except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
                    reasons.append('archive_unverified: ' + str(error))
            if inventory != archived:
                reasons.append('archive_does_not_cover_current_files')
        candidates.append({'execution_id': identifier, 'path': f'runs/{identifier}',
                           'eligible': not reasons, 'reasons': sorted(set(reasons)), 'inventory': inventory})
    return candidates


def cleanup(workspace, candidates, *, current_state=None, read_artifact=None, git_dir=None, marks=None):
    """Re-read eligibility immediately before removal; never mutate research state.

    current_state() supplies executions, protected_references,
    approved_execution_ids, runtime under the caller's writer lock. With the
    candidates' ``marks``, local files are re-examined by fingerprint.
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
                read_artifact=read_artifact, runtime=state['runtime'], reference_records=state.get('reference_records'),
                git_dir=git_dir, marks=marks)[0]
            if not refreshed['eligible'] or refreshed['inventory'] != candidate['inventory']:
                raise ValueError('cleanup prerequisites changed: ' + ', '.join(refreshed['reasons']))
            shutil.rmtree(_run_path(workspace, identifier))
            deleted.append(f'runs/{identifier}')
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
            failures.append({'path': candidate.get('path'), 'error': str(error),
                             'status': 'degraded', 'next_owner': 'maintenance'})
    return {'deleted': deleted, 'failures': failures, 'status': 'degraded' if failures else 'healthy'}


def record_cleanup_interruption(runtime, execution_ids, execution_id, reason, *, history_start):
    """Name unfinished paths without undoing deletions recorded in this attempt."""
    completed = {path for event in runtime['history'][history_start:]
                 if event.get('kind') == 'maintenance_cleanup' and event.get('execution_id') == execution_id
                 for path in event.get('result', {}).get('deleted', [])}
    runtime['history'].append({'kind': 'maintenance_cleanup_failed', 'execution_id': execution_id,
        'paths': ['runs/' + identifier for identifier in execution_ids if 'runs/' + identifier not in completed],
        'completed_paths': sorted(completed), 'reason': reason, 'next_owner': 'maintenance'})


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
            for path in event['paths']:
                pending[path] = {'path': path, 'error': event.get('reason'), 'status': 'degraded',
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
