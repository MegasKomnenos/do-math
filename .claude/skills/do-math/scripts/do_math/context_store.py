"""Lossless input catalogs, bounded prompt contexts, and workspace collection."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from .repository import canonical_json
from .git_store import PhysicalBoundary


_REPARSE_POINT = 0x400


class _ChangedDuringRead(OSError):
    pass


class _PhysicalBoundaryError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative(name: str) -> PurePosixPath:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("path must be a nonempty relative POSIX path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe relative path: {name}")
    return path


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE_POINT)


def _safe_path(root: Path, name: str, *, require_input: bool = False) -> Path:
    relative = _relative(name)
    if require_input and (not relative.parts or relative.parts[0] != "input"):
        raise ValueError("source reference must stay below input/")
    root = _physical_root(root)
    candidate = root.joinpath(*relative.parts)
    cursor = root
    if _is_reparse(cursor):
        raise ValueError(f"root is a reparse point: {root}")
    for part in relative.parts:
        cursor /= part
        if cursor.exists() and _is_reparse(cursor):
            raise ValueError(f"path crosses a reparse point: {cursor}")
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError(f"path leaves workspace: {name}")
    return candidate


def _physical_root(root: Path) -> Path:
    root = Path(os.path.abspath(root))
    for ancestor in [*reversed(root.parents), root]:
        if _is_reparse(ancestor):
            raise ValueError("workspace crosses a reparse point: " + str(ancestor))
    return root


def _read_stable(path: Path, *, boundary: PhysicalBoundary | None = None) -> bytes:
    # Keep the approved lexical root: resolving a raced junction would approve
    # its destination. Read and inspect the same descriptor, not a second open.
    path = Path(os.path.abspath(path))
    try:
        boundary = boundary or PhysicalBoundary(path.parent)
        with boundary.open(path, "rb") as stream:
            before = os.fstat(stream.fileno())
            data = stream.read()
            after = os.fstat(stream.fileno())
            boundary.verify_descriptor(stream.fileno(), path)
    except ValueError as error:
        raise _PhysicalBoundaryError(f"physical boundary rejected read: {error}") from error
    signature = lambda value: (value.st_size, value.st_mtime_ns, getattr(value, "st_ino", None))
    if signature(before) != signature(after) or len(data) != after.st_size:
        raise _ChangedDuringRead(f"file changed while being read: {path}")
    return data


def materialize_inputs(workspace: Path, documents: dict[str, bytes]) -> dict:
    if not isinstance(documents, dict):
        raise TypeError("documents must be a path-to-bytes object")
    workspace = _physical_root(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if _is_reparse(workspace):
        raise ValueError("workspace must not be a reparse point")
    planned: list[tuple[str, Path, bytes]] = []
    for name, data in documents.items():
        relative = _relative(name)
        if not isinstance(data, bytes):
            raise TypeError(f"document must be bytes: {name}")
        logical = PurePosixPath("input") / relative
        target = _safe_path(workspace, logical.as_posix(), require_input=True)
        if target.exists():
            raise FileExistsError(f"input path already exists: {logical.as_posix()}")
        planned.append((logical.as_posix(), target, data))
    manifest = []
    for logical, target, data in sorted(planned):
        target.parent.mkdir(parents=True, exist_ok=True)
        _safe_path(workspace, logical, require_input=True)
        with target.open("xb") as stream:
            stream.write(data)
        manifest.append({"path": logical, "sha256": _sha256(data), "bytes": len(data)})
    return {"input_root": "input", "manifest": manifest}


def _excluded(relative: PurePosixPath) -> bool:
    return bool(relative.parts and (relative.parts[0] in {"input", ".git", ".scratch", ".control", "checks"}
                                    or "__pycache__" in relative.parts))


def collect_outputs(workspace: Path, *, required_paths: list[str] = [],
                    max_bytes: int = 268435456, captured_files: dict[str, bytes] | None = None) -> dict:
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
        raise ValueError("max_bytes must be a nonnegative integer")
    if not isinstance(required_paths, list):
        raise TypeError("required_paths must be a list")
    required = {_relative(name).as_posix() for name in required_paths}
    workspace = _physical_root(workspace)
    files: dict[str, bytes] = {}
    manifest: list[dict] = []
    omitted: list[dict] = []
    seen: set[str] = set()
    total_bytes = 0
    if not workspace.is_dir():
        return {"files": files, "manifest": manifest,
                "omitted": [{"path": name, "reason": "workspace_missing"} for name in sorted(required)],
                "complete": False}
    captured_files = captured_files or {}
    if not isinstance(captured_files, dict):
        raise TypeError("captured_files must be a path-to-bytes object")
    for name, data in sorted(captured_files.items()):
        relative = _relative(name)
        if _excluded(relative):
            raise ValueError("captured research file is excluded: " + name)
        if not isinstance(data, bytes):
            raise TypeError("captured research file must be bytes: " + name)
        _safe_path(workspace, name)
        if total_bytes + len(data) > max_bytes:
            omitted.append({"path": name, "reason": "max_bytes_exceeded", "bytes": len(data),
                            "required": name in required})
            continue
        files[name] = data
        manifest.append({"path": name, "sha256": _sha256(data), "bytes": len(data)})
        total_bytes += len(data)
        seen.add(name)
    boundary = PhysicalBoundary(workspace)
    for directory, dirnames, filenames in os.walk(workspace, topdown=True, followlinks=False):
        base = Path(directory)
        kept = []
        for dirname in sorted(dirnames):
            path = base / dirname
            relative = PurePosixPath(path.relative_to(workspace).as_posix())
            if _excluded(relative):
                continue
            if _is_reparse(path):
                reason = "outside_symlink" if not path.resolve(strict=False).is_relative_to(workspace) else "reparse_directory"
                omitted.append({"path": relative.as_posix(), "reason": reason})
                continue
            kept.append(dirname)
        dirnames[:] = kept
        for filename in sorted(filenames):
            path = base / filename
            relative = PurePosixPath(path.relative_to(workspace).as_posix())
            name = relative.as_posix()
            if _excluded(relative):
                continue
            if name in captured_files:
                continue
            seen.add(name)
            if _is_reparse(path):
                reason = "outside_symlink" if not path.resolve(strict=False).is_relative_to(workspace) else "reparse_file"
                omitted.append({"path": name, "reason": reason, "required": name in required})
                continue
            try:
                data = _read_stable(path, boundary=boundary)
            except _PhysicalBoundaryError as error:
                omitted.append({"path": name, "reason": "physical_boundary", "error": str(error),
                                "error_type": type(error).__name__, "required": name in required})
                continue
            except FileNotFoundError:
                omitted.append({"path": name, "reason": "disappeared", "required": name in required})
                continue
            except _ChangedDuringRead as error:
                omitted.append({"path": name, "reason": "changed_during_read", "error": str(error), "required": name in required})
                continue
            except OSError as error:
                omitted.append({"path": name, "reason": "read_error", "error_type": type(error).__name__,
                                "error": str(error), "required": name in required})
                continue
            if total_bytes + len(data) > max_bytes:
                omitted.append({"path": name, "reason": "max_bytes_exceeded", "bytes": len(data), "required": name in required})
                continue
            files[name] = data
            manifest.append({"path": name, "sha256": _sha256(data), "bytes": len(data)})
            total_bytes += len(data)
    for name in sorted(required - set(files)):
        if not any(row["path"] == name for row in omitted):
            omitted.append({"path": name, "reason": "required_missing" if name not in seen else "required_not_collected", "required": True})
    complete = not omitted and required <= set(files)
    return {"files": files, "manifest": sorted(manifest, key=lambda row: row["path"]),
            "omitted": sorted(omitted, key=lambda row: (row["path"], row["reason"])), "complete": complete}


def _catalog_name(key: str) -> str:
    if not isinstance(key, str) or not key or any(not (character.isalnum() or character in "_-") for character in key):
        raise ValueError(f"context key cannot be a catalog filename: {key}")
    return key + ".json"


def write_source_catalog(context: dict, workspace: Path) -> dict:
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    workspace = _physical_root(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if _is_reparse(workspace):
        raise ValueError("workspace must not be a reparse point")
    entries: dict[str, dict] = {}
    manifest: list[dict] = []
    for key in sorted(context):
        if key not in context:
            continue
        logical = "input/catalog/" + _catalog_name(key)
        target = _safe_path(workspace, logical, require_input=True)
        data = canonical_json(context[key])
        if target.exists():
            observed = _read_stable(target)
            if observed != data:
                raise FileExistsError(f"catalog path contains different bytes: {logical}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
            observed = _read_stable(target)
        ref = {"path": logical, "sha256": _sha256(observed), "bytes": len(observed),
               "format": "canonical-json"}
        entries[key] = ref
        manifest.append({"key": key, **ref})
    return {"entries": entries, "manifest": manifest, "total": len(manifest)}


def build_role_manifest(context: dict, *, workspace: Path, role: str,
                        direct_keys: list[str], reference_keys: list[str]) -> dict:
    """Declare direct role inputs separately from exact source references."""
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    if not isinstance(role, str) or not role:
        raise ValueError("role must be a non-empty string")
    for label, keys in (("direct_keys", direct_keys), ("reference_keys", reference_keys)):
        if not isinstance(keys, list) or any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
            raise ValueError(label + " must contain distinct string keys")
    overlap = set(direct_keys).intersection(reference_keys)
    if overlap:
        raise ValueError("a role input cannot be both direct and referenced: " + ", ".join(sorted(overlap)))
    missing = [key for key in [*direct_keys, *reference_keys] if key not in context]
    if missing:
        raise ValueError("role manifest keys are missing: " + ", ".join(missing))
    catalog = write_source_catalog(context, workspace)
    direct = []
    for key in direct_keys:
        data = canonical_json(context[key])
        direct.append({"key": key, "sha256": _sha256(data), "bytes": len(data)})
    references = []
    for key in reference_keys:
        source_ref = catalog["entries"].get(key)
        if source_ref is None:
            raise ValueError("reference key has no exact catalog entry: " + key)
        references.append({"key": key, "source_ref": source_ref})
    return {"role": role, "direct": direct, "references": references,
            "catalog": catalog["manifest"]}


def _encoded_size(value: dict) -> int:
    return len(canonical_json(value))


def restore_continuation(runtime, action, workspace, *, snapshot, read_artifact, checkpoint=None):
    """Restore explicit ancestry, retaining the latest preserved copy per file.

    read_artifact(path) is bound to snapshot. This is provenance restoration,
    not a certification that retained work is mathematically complete.
    """
    def parent(value):
        return (value.get('continuation_of') or value.get('repair', {}).get('execution_id')
                or value.get('refresh', {}).get('execution_id') or value.get('recovery', {}).get('execution_id'))
    identifier = parent(action)
    chain, seen = [], set()
    activity_id = None
    while identifier:
        if identifier in seen:
            raise ValueError('cycle in resume execution lineage')
        seen.add(identifier)
        execution = runtime.get('executions', {}).get(identifier)
        if (not execution or execution.get('status') != 'ended' or execution.get('role') != action.get('role')
                or any(execution.get('action', {}).get(key) != action.get(key)
                       for key in ('target', 'review_cycle_id', 'stage', 'slot', 'round'))):
            raise ValueError('resume lineage does not identify this action\'s ended execution')
        if not execution.get('owner_activity_id'):
            raise ValueError('resume lineage requires an owner activity')
        activity_id = activity_id or execution['owner_activity_id']
        if execution['owner_activity_id'] != activity_id:
            raise ValueError('resume lineage crosses an owner activity')
        chain.append(execution)
        identifier = execution.get('continuation_of') or parent(execution.get('action', {}))
    if not chain:
        return {}
    latest, history, documents = {}, [], {}
    for execution in reversed(chain):
        if checkpoint:
            checkpoint()
        for entry in execution.get('output_files', []):
            logical = _relative(entry['path']).as_posix()
            latest[logical] = {**deepcopy(entry), 'execution_id': execution['id'], 'snapshot': snapshot}
        stage = {'execution_id': execution['id'], 'outcome': execution.get('outcome'),
                 'error': execution.get('error'),
                 'checkpoint': deepcopy(runtime.get('checkpoints', {}).get(execution['id']))}
        result_ref = execution.get('result_ref')
        if not result_ref and execution.get('artifact_bundle'):
            filename = 'checkpoint-recovery.json' if execution.get('error') == 'previous executor disappeared' else 'result.json'
            result_ref = 'runtime/artifacts/' + execution['artifact_bundle'] + '/' + filename
        if result_ref:
            raw = read_artifact(result_ref)
            logical = 'resume-history/' + _sha256(execution['id'].encode()) + '/result.json'
            documents[logical] = raw
            stage['result_source'] = {'artifact_ref': result_ref, 'snapshot': snapshot,
                'local_path': 'input/' + logical, 'sha256': _sha256(raw), 'bytes': len(raw)}
        history.append(stage)
    repair = action.get('repair', {})
    raw_ref = repair.get('raw_output_ref')
    if raw_ref:
        raw = read_artifact(raw_ref)
        if _sha256(raw) != repair.get('raw_output_sha256'):
            raise ValueError('rejected response bytes differ from central capture')
        documents['resume-history/rejected-response.txt'] = raw
        history[-1]['rejected_response'] = {'artifact_ref': raw_ref, 'snapshot': snapshot,
            'local_path': 'input/resume-history/rejected-response.txt', 'sha256': _sha256(raw), 'bytes': len(raw)}
    restored = []
    for logical, entry in sorted(latest.items()):
        if checkpoint:
            checkpoint()
        raw = read_artifact(entry['artifact_ref'])
        if _sha256(raw) != entry['sha256'] or len(raw) != entry['bytes']:
            raise ValueError('resume artifact differs from its preserved reference')
        path = 'previous-output/' + logical
        documents[path] = raw
        restored.append({**entry, 'local_path': 'input/' + path})
    materialize_inputs(workspace, documents)
    previous = chain[0]
    return {'previous_output_files': restored, 'continuation_history': history,
        'resume_checkpoint': deepcopy(runtime.get('checkpoints', {}).get(previous['id'])),
        'previous_execution': {'id': previous['id'], 'role': previous['role'],
            'action': deepcopy(previous.get('action', {})), 'outcome': previous.get('outcome'),
            'error': previous.get('error'), 'result_source': history[-1].get('result_source'),
            'instruction': 'Read continuation history, preserved results/checkpoints and latest previous_output_files. Preserved files are evidence, not automatically applied output. Reuse only within current inputs and authority; for output repair resubmit applicable corrected activity extensions.'}}


_ROLE_DIRECT = {
    'research_preparation': ('profile_selection', 'tasks', 'ongoing_work', 'knowledge_catalog', 'resources', 'blocked_actions', 'pending_revisions'),
    'research_plan': ('profile_selection', 'tasks', 'ongoing_work', 'ready_task_ids', 'returned_task_ids', 'knowledge_catalog', 'resources', 'ongoing_preparation', 'input_overflow_requests', 'review_followups'),
    'research_work': ('task',), 'supplemental_research': ('task',),
    'task_contract_review': ('task',), 'identity_review': ('role_review',),
    'goal_audit': ('eligible_knowledge',),
    'operational_review': ('execution_to_review', 'observation'),
    'intent_interpretation': ('user_request', 'interpretation_to_check'),
    'maintenance': (),
}


def role_direct_keys(role, context):
    """The comparison population, current request and resume evidence are direct."""
    role_keys = _ROLE_DIRECT.get(role, ())
    if role == 'supplemental_research' and context.get('action', {}).get('review_cycle_id'):
        role_keys = ('review_research', 'proposal')
    return list(dict.fromkeys([
        'snapshot', 'goal', 'policies', 'action', 'implementation_documents',
        'governance', 'execution_profile', *role_keys,
        *(['import_consumers', 'original_source'] if context.get('import_consumers') is not None else []),
        *(['impact_review_input'] if context.get('action', {}).get('stage') == 'impact_review' else []),
        *[key for key in ('proposal', 'role_review', 'previous_execution', 'resume_checkpoint',
                         'recovery_materials', 'previous_output_files', 'review_transcript',
                         'continuity_broken', 'continuation_history', 'candidate_order') if key in context]]))


def prepare_role_input(context, *, instance, runtime, role, profile, snapshot,
                       workspace, activity_id, output_schema=None, documents=None, artifact_prefix=None,
                       install_submission_tools=False, max_artifact_bytes=None, candidate_order=None):
    """Build and measure the actual role prompt from the current domain records.

    The caller must supply only the review seat's authorized private inputs.
    This function never fetches another seat's private records.
    """
    from . import contracts, governance, task_contracts
    from .execution_profiles import validate_profile, profile_ref, prepare_prompt
    validate_profile(profile)
    if profile['role'] != role or role not in _ROLE_DIRECT:
        raise ValueError('selected profile does not match the input role')
    if not isinstance(snapshot, str) or len(snapshot) not in (40, 64) or any(c not in '0123456789abcdef' for c in snapshot):
        raise ValueError('input snapshot must be a fixed Git commit')
    value = deepcopy(context)
    detail_sources, detail_bytes = [], {}
    def preserve_detail(name, record):
        raw = canonical_json(record)
        logical = 'details/' + name + '.json'
        materialize_inputs(workspace, {logical: raw})
        ref = {'path': 'input/' + logical, 'snapshot': snapshot, 'sha256': _sha256(raw), 'bytes': len(raw)}
        if artifact_prefix is not None:
            ref['artifact_ref'] = _relative(artifact_prefix).as_posix() + '/' + ref['path']
            detail_bytes[ref['artifact_ref']] = raw
        detail_sources.append(ref)
        return deepcopy(ref)
    if 'config' in value or role in {'research_preparation', 'research_plan'}:
        value.pop('config', None)
        value['configuration_source'] = preserve_detail('configuration', instance['config'])
    if instance.get('governance'):
        governance_input = governance.governance_view(instance)
    elif role in {'intent_interpretation', 'maintenance'} and instance.get('lifecycle', {}).get('state') == 'initializing':
        governance_input = {'status': 'not_yet_adopted',
                            'immutable_input': deepcopy(instance['lifecycle']['immutable_input']),
                            'adoption': deepcopy(instance['lifecycle'].get('adoption', {}))}
    else:
        raise ValueError('role requires adopted governance')
    value.update(snapshot=snapshot, governance=governance_input, execution_profile=deepcopy(profile))
    private_scope = None
    action = value.get('action', {})
    if role == 'identity_review' and action.get('review_cycle_id'):
        from .review_cycle import context_for, review_action
        cycle = runtime.get('review_cycles', {}).get(action['review_cycle_id'])
        if cycle is None:
            raise ValueError('review input has no current cycle')
        expected = context_for(cycle, review_action(action))
        supplied = value.get('role_review')
        if not isinstance(supplied, dict):
            raise ValueError('review requires seat-scoped role_review input')
        if set(supplied) - (set(expected) | {'output_schema', 'review_cycle_id', 'snapshot', 'source_instructions', 'research_request_contract'}):
            raise ValueError('review input contains material outside the seat-scoped contract')
        def without_local(obj):
            if isinstance(obj, dict):
                return {k: without_local(v) for k, v in obj.items() if k != 'local_path'}
            if isinstance(obj, list):
                return [without_local(v) for v in obj]
            return obj
        for key in ('proposal', 'self_messages', 'completed_results', 'identity_basis', 'policy_ref'):
            if without_local(supplied.get(key)) != without_local(expected.get(key)):
                raise ValueError('review direct input differs from authorized seat view: ' + key)
        for ref in supplied.get('source_refs', []):
            if ref.get('slot') != action.get('slot'):
                raise ValueError('another review seat transcript is private')
            resolved = read_source(workspace, {**ref, 'path': ref.get('local_path')}, limit=max(1, ref['bytes']))
            if resolved['status'] != 'ok' or resolved['truncated']:
                raise ValueError('review transcript source bytes could not be verified')
        private_scope = {'review_cycle_id': action['review_cycle_id'], 'slot': action.get('slot'),
                         'stage': action.get('stage'), 'source_refs': deepcopy(supplied.get('source_refs', [])),
                         'view_sha256': _sha256(canonical_json(supplied))}
    if role in {'research_preparation', 'research_plan'}:
        tasks = runtime.get('tasks', {})
        reader_tasks = {task['id']: task for task in value.get('tasks', [])}
        if set(reader_tasks) != set(tasks):
            raise ValueError('planning input must preserve every current task before selection')
        value['task_catalog'] = [
            {'id': identifier, 'title': task.get('title'), 'revision': task.get('revision'),
             'status': task.get('status'), 'result_count': len(task.get('results', [])),
             'result_execution_ids': [row['execution_id'] for row in task.get('results', []) if row.get('execution_id')],
             'source_ref': preserve_detail('tasks/' + _sha256(identifier.encode()), task)}
            for identifier, task in sorted(reader_tasks.items())]
        task_refs = {row['id']: row['source_ref'] for row in value['task_catalog']}
        value['ongoing_work'] = [
            {'execution_id': execution['id'], 'role': execution.get('role'), 'status': execution['status'],
             'target': execution.get('action', {}).get('target'),
             'stage': execution.get('action', {}).get('stage'),
             'reason': execution.get('action', {}).get('reason'),
             'input_snapshot': execution.get('input_snapshot'),
             'continuation_of': execution.get('continuation_of') or execution.get('action', {}).get('continuation_of'),
             'event_refs': deepcopy(execution.get('action', {}).get('event_refs', [])),
             'task_source_ref': deepcopy(task_refs.get(execution.get('action', {}).get('target')))}
            for execution in runtime.get('executions', {}).values() if execution.get('status') != 'ended'
        ] + [
            {'action_id': identifier, 'role': entry.get('action', {}).get('role'),
             'target': entry.get('action', {}).get('target'), 'stage': entry.get('action', {}).get('stage'),
             'reason': entry.get('reason'), 'kind': entry.get('kind'),
             'execution_id': entry.get('execution_id'),
             'event_refs': deepcopy(entry.get('action', {}).get('event_refs', [])),
             'task_source_ref': deepcopy(task_refs.get(entry.get('action', {}).get('target')))}
            for identifier, entry in sorted(runtime.get('waiting_actions', {}).items())
        ]
        def reader_task(identifier):
            if identifier not in reader_tasks:
                raise ValueError('required reader task is absent: ' + identifier)
            return deepcopy(reader_tasks[identifier])
        if role == 'research_plan':
            from .input_recovery import overflow_requests
            value['input_overflow_requests'] = overflow_requests(instance, runtime)
            value['review_followups'] = [
                {'id': cycle['id'], 'knowledge_id': cycle['knowledge_id'], 'status': cycle['status'],
                 'decision': cycle['decision'], 'proposal_digest': cycle['proposal_digest'],
                 'followup': deepcopy(cycle['followup']),
                 'source_ref': preserve_detail('review-followups/' + _sha256(cycle['id'].encode()), cycle)}
                for cycle in value.get('review_followups', [])]
            ready = value.get('ready_task_ids')
            if (not isinstance(ready, list) or any(not isinstance(tid, str) or tid not in tasks for tid in ready)
                    or len(ready) != len(set(ready))):
                raise ValueError('planning input requires its fixed ready_task_ids')
            returned = task_contracts.returned_task_ids(tasks)
            value['returned_task_ids'] = returned
            value['tasks'] = [reader_task(identifier) for identifier in sorted(set(ready) | set(returned))]
            value.setdefault('ongoing_preparation', [])
        else:
            from .planning import pending_revisions
            revisions = pending_revisions(runtime)
            targets = {identifier for row in revisions for identifier in row['action'].get('revision_targets', {})}
            targets.update(action.get('target') for action in runtime.get('queue', []) if action.get('continuation_of'))
            targets.update(action.get('assessment_targets', {}))
            targets.update(action.get('observation_rule_targets', {}))
            if action.get('target') in tasks:
                targets.add(action['target'])
            value['tasks'] = [reader_task(identifier) for identifier, task in sorted(tasks.items())
                              if task.get('status') == 'planned' or identifier in targets and task.get('status') not in {'completed', 'closed'}]
            value.setdefault('blocked_actions', deepcopy(runtime.get('waiting_actions', {})))
            value['pending_revisions'] = deepcopy(revisions)
        from .planning import CONTRACT_FIELDS
        comparison_fields = set(CONTRACT_FIELDS) | {'id', 'title', 'question', 'revision', 'status',
            'scope', 'expected', 'completion_obligations', 'progress_criteria', 'profile_refs',
            'authority_refs', 'basis_refs', 'model_assessment', 'importance', 'difficulty',
            'assessment', 'contract_review', 'selection', 'unresolved'}
        compared = []
        for task in value['tasks']:
            row = {key: deepcopy(task[key]) for key in comparison_fields if key in task}
            row['source_ref'] = deepcopy(task_refs[task['id']])
            row['result_count'] = len(task.get('results', []))
            row['result_execution_ids'] = [item.get('execution_id') for item in task.get('results', [])]
            compared.append(row)
        value['profile_selection'] = {
            'default_policy': {key: deepcopy(instance['config'][key]) for key in
                ('role_tiers', 'tier_models', 'role_models', 'model', 'effort') if key in instance['config']},
            'allowed_profiles': [deepcopy(p) for _, p in sorted(instance.get('execution_profiles', {}).items())],
            'capacity_constraints': deepcopy(instance.get('capacity_constraints', {})),
            'task_profile_constraints': {row['id']: deepcopy(row.get('profile_refs', [])) for row in compared}}
        population = value['ready_task_ids'] if role == 'research_plan' else [row['id'] for row in compared]
        order = _candidate_order(population, snapshot, role, action.get('id'), candidate_order)
        indexed = {row['id']: row for row in compared}
        task_order = [*order['ids'], *[identifier for identifier in sorted(indexed) if identifier not in order['ids']]]
        value['tasks'] = [indexed[identifier] for identifier in task_order]
        value['candidate_order'] = order
        if role == 'research_plan':
            value['ready_task_ids'] = list(order['ids'])
    required = role_direct_keys(role, value)
    # goal/policies are legacy display projections; the full governance view is authoritative.
    required = [key for key in required if key not in {'goal', 'policies', 'implementation_documents'}]
    missing = set(required) - value.keys()
    if missing:
        raise ValueError('required role input is absent: ' + ', '.join(sorted(missing)))
    documents = documents if documents is not None else contracts.prompt_documents(role)
    schema = output_schema if output_schema is not None else contracts.schema_for(role)
    validation_context = deepcopy(value)
    if role in {'research_preparation', 'research_plan'}:
        # Resolve catalog references independently of the comparison population.
        validation_context['tasks'] = [deepcopy(runtime['tasks'][identifier])
                                       for identifier in sorted(runtime['tasks'])]
    if role in {'research_work', 'supplemental_research'}:
        # A fixed public domain view for the shared relation checker, not a
        # second store or a worker-authored validity assertion.
        relation_state = {key: deepcopy(instance.get(key, {})) for key in (
            'knowledge', 'formal_results', 'expositions', 'identity_assessments',
            'assessment_uses', 'kind_definitions', 'trust_environments')}
        relation_state.update(active_trust_environment=instance.get('active_trust_environment'),
                              sources=deepcopy(instance.get('sources', [])))
        raw = canonical_json(relation_state)
        materialize_inputs(workspace, {'submission/relation-state.json': raw})
        ref = {'path': 'input/submission/relation-state.json', 'snapshot': snapshot,
               'sha256': _sha256(raw), 'bytes': len(raw)}
        value['relation_validation_source'] = deepcopy(ref)
        validation_context['relation_validation_source'] = ref
    if install_submission_tools:
        from .submission import install_tools
        install_tools(workspace, validation_context, schema, max_artifact_bytes)
        for key in ('submission_contract', 'reference_catalog', 'formal_verifier'):
            if key in validation_context:
                value[key] = deepcopy(validation_context[key])
        required = list(dict.fromkeys([*required, 'submission_contract',
            *(['formal_verifier'] if 'formal_verifier' in value else [])]))
    limit = profile['input']['max_input_bytes']
    def render(body):
        return prepare_prompt(contracts.render_prompt(role, body, output_schema=schema, documents=documents), profile)
    overhead = len(render({}).encode('utf-8'))
    fitted = fit_context(value, max_bytes=max(1, limit - overhead), workspace=workspace,
                         mandatory_keys=required, role=role, profile_id=profile['id'], activity_id=activity_id)
    prompt = render(fitted['context'])
    original_prompt = render(value)
    actual = len(prompt.encode('utf-8'))
    if actual > limit:
        overflow = fitted['overflow'] or _input_overflow('rendered_prompt_exceeds_limit',
            actual_bytes=len(original_prompt.encode('utf-8')), mandatory_bytes=0, max_bytes=limit,
            mandatory_keys=required, role=role, profile_id=profile['id'], activity_id=activity_id)
        overflow.update(original_bytes=len(original_prompt.encode('utf-8')), actual_bytes=len(original_prompt.encode('utf-8')),
                        packed_bytes=actual, limit_bytes=limit, unit='utf8_bytes',
                        prompt_metrics=contracts.prompt_metrics(prompt, fitted['context'], schema, documents))
        overflow.setdefault('resolution_question', {'kind': 'input_capacity', 'activity_id': activity_id,
            'question': 'Which authorized profile or scope change should resolve this input overflow?',
            'next_owner': 'research_plan' if role == 'research_work' else 'user'})
        base_bytes = len(render({'governance': value['governance']}).encode('utf-8'))
        overflow['cause'] = 'common_documents_or_governance' if base_bytes > limit else 'required_role_input'
        if role == 'identity_review' and base_bytes <= limit and isinstance(value.get('role_review'), dict):
            without_dialogue = deepcopy(value)
            without_dialogue['role_review']['self_messages'] = []
            current_bytes = len(render(without_dialogue).encode('utf-8'))
            overflow['cause'] = 'current_proposal_or_required_sources' if current_bytes > limit else 'restored_dialogue'
            overflow['without_restored_dialogue_bytes'] = current_bytes
        alternatives = []
        if role == 'research_work' and base_bytes <= limit:
            from .execution_profiles import resolve_profile
            from .model_policy import selection
            for reference in value.get('task', {}).get('profile_refs', []):
                try:
                    candidate = resolve_profile(instance['execution_profiles'], reference)
                    selection(instance['config'], {**action, 'profile_ref': profile_ref(candidate)},
                        runtime['tasks'], instance.get('knowledge', {}), profiles=instance['execution_profiles'])
                except ValueError:
                    continue
                if candidate['id'] == profile['id']:
                    continue
                validate_profile(candidate)
                if candidate['role'] == role and candidate.get('input', {}).get('unit') == 'utf8_bytes' and candidate['input']['max_input_bytes'] >= actual:
                    alternatives.append(candidate['id'])
        overflow['allowed_profile_candidates'] = alternatives
        overflow['resolution_question']['next_owner'] = 'research_plan' if alternatives else 'user'
        overflow['suggested_disposition'] = ('unresolved_to_review_plan' if overflow['cause'] == 'current_proposal_or_required_sources'
                                             else 'plan_allowed_profile' if alternatives else 'request_user_decision')
        fitted['overflow'] = overflow
    else:
        # Packing used conservative canonical component sizes. The actual
        # rendered profile input is the final admission measurement.
        fitted['overflow'] = None
    manifest = build_role_manifest(value, workspace=workspace, role=role,
        direct_keys=required, reference_keys=[k for k in value if k not in required])
    # A reduced field's source is the original catalog, not a new JSON wrapper.
    manifest['references'] = [{'key': row['key'], 'source_ref': {k: v for k, v in row.items() if k != 'key'}}
                              for row in fitted['manifest'] if row['key'] not in required]
    manifest.update(feature_version=5, snapshot=snapshot, execution_profile_ref=profile_ref(profile),
        output_contract={'id': schema.get('x-contract-id'), 'sha256': _sha256(canonical_json(schema))},
        documents=[{'path': doc['path'], 'sha256': _sha256(doc['content'].encode('utf-8')),
                    'bytes': len(doc['content'].encode('utf-8'))} for doc in documents],
        prompt={'sha256': _sha256(prompt.encode('utf-8')), 'bytes': actual}, required_direct_keys=required,
        private_scope=private_scope)
    manifest['detail_sources'] = detail_sources
    if 'candidate_order' in value:
        manifest['candidate_order'] = deepcopy(value['candidate_order'])
    artifacts = dict(detail_bytes)
    if artifact_prefix is not None:
        prefix = _relative(artifact_prefix).as_posix()
        if not prefix.startswith('runtime/artifacts/'):
            raise ValueError('role input archive must stay in runtime/artifacts')
        for row in manifest['direct']:
            row['artifact_ref'] = prefix + '/input/catalog/' + _catalog_name(row['key'])
            artifacts[row['artifact_ref']] = canonical_json(value[row['key']])
        for row in manifest['references']:
            ref = row['source_ref']
            ref['artifact_ref'] = prefix + '/' + ref['path']
            artifacts[ref['artifact_ref']] = canonical_json(value[row['key']])
        for index, (row, doc) in enumerate(zip(manifest['documents'], documents)):
            row['artifact_ref'] = prefix + '/input/documents/' + str(index) + '.txt'
            artifacts[row['artifact_ref']] = doc['content'].encode('utf-8')
        manifest['prompt']['artifact_ref'] = prefix + '/input/prompt.txt'
        artifacts[manifest['prompt']['artifact_ref']] = prompt.encode('utf-8')
    validate_role_manifest(manifest)
    fitted.update(manifest=manifest, prompt=prompt, actual_bytes=actual,
                  original_bytes=len(original_prompt.encode('utf-8')), artifacts=artifacts,
                  validation_context=validation_context)
    return fitted


def _candidate_order(ids, snapshot, role, action_id, replay=None):
    algorithm = 'sha256-seed-id-v1'
    basis = {'snapshot': snapshot, 'role': role, 'action_id': action_id}
    seed = replay.get('seed') if isinstance(replay, dict) else os.urandom(32).hex()
    if not isinstance(seed, str) or len(seed) != 64 or any(c not in '0123456789abcdef' for c in seed):
        raise ValueError('candidate order requires a 256-bit seed')
    ordered = sorted(ids, key=lambda identifier: (_sha256(bytes.fromhex(seed) + b'\0' + identifier.encode()), identifier))
    result = {'algorithm': algorithm, 'seed': seed, 'basis': basis, 'ids': ordered}
    if replay is not None and replay != result:
        raise ValueError('candidate order replay differs from population or input basis')
    return result


def validate_role_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get('feature_version') != 5 or manifest.get('role') not in _ROLE_DIRECT:
        raise ValueError('invalid role input manifest version or role')
    snapshot = manifest.get('snapshot', '')
    if not isinstance(snapshot, str) or len(snapshot) not in (40, 64) or any(c not in '0123456789abcdef' for c in snapshot):
        raise ValueError('input manifest requires fixed snapshot')
    direct = manifest.get('direct', [])
    keys = [row['key'] for row in direct]
    role_keys = _ROLE_DIRECT[manifest['role']]
    if manifest['role'] == 'supplemental_research' and 'review_research' in manifest.get('required_direct_keys', []):
        role_keys = ('review_research', 'proposal')
    required = {'snapshot', 'governance', 'execution_profile', 'action', *role_keys}
    if len(keys) != len(set(keys)) or not (required | set(manifest.get('required_direct_keys', []))) <= set(keys):
        raise ValueError('required direct input is missing or duplicated')
    if manifest.get('output_contract', {}).get('id') != 'do-math-cli/5':
        raise ValueError('input does not bind the current response contract')
    paths = [doc['path'] for doc in manifest.get('documents', [])]
    if any(paths.count(path) != 1 for path in ('SKILL.md', 'GLOSSARY.md')):
        raise ValueError('common documents must each occur exactly once')
    rows = [*direct, *manifest['documents'], manifest.get('prompt', {}), *manifest.get('detail_sources', [])]
    rows += [row['source_ref'] for row in manifest.get('references', [])]
    for row in rows:
        digest = row.get('sha256', '')
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('input component requires exact byte hash')
        if type(row.get('bytes')) is not int or row['bytes'] < 0:
            raise ValueError('input component requires measured byte length')
    for ref in manifest.get('references', []):
        _relative(ref['source_ref']['path'])
    order = manifest.get('candidate_order')
    if manifest['role'] in {'research_preparation', 'research_plan'}:
        if not isinstance(order, dict) or len(order.get('ids', [])) != len(set(order.get('ids', []))):
            raise ValueError('candidate input requires a sealed population order')
        _candidate_order(order['ids'], snapshot, manifest['role'], order.get('basis', {}).get('action_id'), order)
    return True


def prefetch_artifacts(paths, read_artifact, read_artifacts=None):
    """Read one fixed snapshot in bulk, retaining per-file failure handling.

    The returned reader belongs only to this inspection. A failed batch is read
    individually by the caller's existing path, so error order and scope stay local.
    """
    if read_artifacts is None or not paths:
        return read_artifact
    from .git_store import GitStateStoreError
    try:
        files = read_artifacts(list(dict.fromkeys(paths)))
    except (GitStateStoreError, OSError, ValueError, TypeError, KeyError):
        return read_artifact

    def read(path):
        return files[path] if path in files else read_artifact(path)
    return read


def verify_manifest_artifacts(manifest, read_artifact, *, read_artifacts=None):
    """Verify published component bytes; return the exact unavailable bindings."""
    validate_role_manifest(manifest)
    missing = []
    rows = [('prompt', manifest['prompt'])]
    rows += [(row['key'], row) for row in manifest['direct']]
    rows += [(row['path'], row) for row in manifest['documents']]
    rows += [(row['key'], row['source_ref']) for row in manifest['references']]
    rows += [(row['path'], row) for row in manifest.get('detail_sources', [])]
    batch = (read_artifacts([row['artifact_ref'] for _, row in rows if row.get('artifact_ref')])
             if read_artifacts is not None else None)
    for name, row in rows:
        path = row.get('artifact_ref')
        if not path or (read_artifact is None and batch is None):
            missing.append(name)
            continue
        raw = batch[path] if batch is not None else read_artifact(path)
        if len(raw) != row['bytes'] or _sha256(raw) != row['sha256']:
            raise ValueError('input artifact bytes differ: ' + name)
    return missing


def defer_input_overflow(runtime, overflow, *, at, question_ref):
    """Let ACTIVITIES own waiting, retaining the question during live termination."""
    from .activities import wait_for
    identifier = overflow['activity_id']
    activity = runtime['activities'][identifier]
    next_owner = overflow.get('resolution_question', {}).get('next_owner', 'user')
    condition = {'kind': 'profile_selection' if next_owner == 'research_plan' else 'user_decision',
                 'question_ref': question_ref, 'input_overflow': deepcopy(overflow)}
    if any(runtime['executions'][eid]['status'] != 'ended' for eid in activity['assigned_execution_ids']):
        if condition not in activity['unresolved']:
            activity['unresolved'].append(condition)
        return {'status': 'working', 'condition': condition}
    wait_for(runtime, identifier, reason='input_overflow', condition=condition,
             next_owner=next_owner, at=at)
    return {'status': 'waiting', 'condition': condition}




def _input_overflow(reason: str, *, actual_bytes: int, mandatory_bytes: int, max_bytes: int,
                    mandatory_keys: list[str], role: str | None, profile_id: str | None,
                    activity_id: str | None) -> dict:
    """Describe a refused input without silently removing required material."""
    return {"kind": "input_overflow", "reason": reason, "actual_bytes": actual_bytes,
            "mandatory_bytes": mandatory_bytes, "limit_bytes": max_bytes,
            "required_direct_keys": list(mandatory_keys), "role": role,
            "profile_id": profile_id, "activity_id": activity_id,
            "next_owner": "activities", "disposition": "await_activity_decision"}


def fit_context(context: dict, *, max_bytes: int, workspace: Path,
                mandatory_keys: list[str], role: str | None = None,
                profile_id: str | None = None, activity_id: str | None = None) -> dict:
    """Pack optional source references without changing mandatory direct bytes."""
    if not isinstance(context, dict):
        raise TypeError("context must be an object")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("max_bytes must be a positive integer")
    if not isinstance(mandatory_keys, list) or any(not isinstance(k, str) for k in mandatory_keys) or len(mandatory_keys) != len(set(mandatory_keys)):
        raise ValueError("mandatory_keys must contain distinct string keys")
    mandatory_keys = list(dict.fromkeys([*mandatory_keys, *[key for key in role_direct_keys(role, context)
                                                   if key in context and key not in {'goal', 'policies', 'implementation_documents'}]]))
    missing = set(mandatory_keys) - context.keys()
    if missing:
        raise ValueError("mandatory context keys are missing: " + ", ".join(sorted(missing)))
    catalog = write_source_catalog(context, workspace)
    fitted = deepcopy(context)
    original_bytes = _encoded_size(context)
    mandatory_bytes = _encoded_size({key: context[key] for key in mandatory_keys})
    reductions = []
    # Catalogs that define a comparison universe are never shortened. Their
    # inclusion as required direct input is enforced by prepare_role_input.
    candidates = sorted((key for key in catalog["entries"] if key not in mandatory_keys),
                        key=lambda key: len(canonical_json(context[key])), reverse=True)
    for key in candidates:
        if _encoded_size(fitted) <= max_bytes or mandatory_bytes > max_bytes:
            break
        ref = catalog["entries"][key]
        projected = {"source_ref": ref, "total": len(context[key]) if isinstance(context[key], (dict, list)) else None}
        if _encoded_size(projected) < _encoded_size(fitted[key]):
            fitted[key] = projected
            reductions.append({"key": key, "kind": "source_reference", "source_ref": ref})
    actual = _encoded_size(fitted)
    overflow = None
    if actual > max_bytes:
        overflow = _input_overflow(
            "mandatory_context_exceeds_limit" if mandatory_bytes > max_bytes else "reference_index_exceeds_limit",
            actual_bytes=original_bytes, mandatory_bytes=mandatory_bytes, max_bytes=max_bytes,
            mandatory_keys=mandatory_keys, role=role, profile_id=profile_id, activity_id=activity_id)
        overflow.update(packed_bytes=actual, original_bytes=original_bytes,
                        component_bytes={key: len(canonical_json(value)) for key, value in context.items()},
                        unit="utf8_bytes", reductions=deepcopy(reductions),
                        resolution_question={"kind": "input_capacity", "activity_id": activity_id,
                            "role": role, "required_direct_keys": list(mandatory_keys),
                            "question": "Which authorized profile or scope change should resolve this input overflow?",
                            "next_owner": "research_plan" if role == "research_work" else "user"})
    return {"context": fitted, "manifest": catalog["manifest"], "actual_bytes": actual,
            "original_bytes": original_bytes, "reductions": reductions, "overflow": overflow}


def read_source(workspace: Path, ref: dict, offset: int = 0,
                limit: int = 1048576) -> dict:
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a nonnegative integer")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    try:
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
            raise ValueError("source ref must contain a path")
        path = _safe_path(workspace, ref["path"], require_input=True)
        if not path.exists():
            return {"status": "missing", "path": ref["path"], "bytes": b"",
                    "sha256": None, "range": {"start": offset, "end": offset, "total": 0},
                    "truncated": False, "reason": "source_missing"}
        data = _read_stable(path, boundary=PhysicalBoundary(_physical_root(workspace)))
        digest = _sha256(data)
        if "sha256" in ref and ref["sha256"] != digest:
            raise ValueError("source hash differs from reference")
        if "bytes" in ref and ref["bytes"] != len(data):
            raise ValueError("source size differs from reference")
        start = min(offset, len(data)); end = min(start + limit, len(data))
        return {"status": "ok", "path": ref["path"], "bytes": data[start:end],
                "sha256": digest, "range": {"start": start, "end": end, "total": len(data)},
                "truncated": end < len(data)}
    except (OSError, ValueError) as error:
        return {"status": "error", "path": ref.get("path") if isinstance(ref, dict) else None,
                "bytes": b"", "sha256": None, "range": None, "truncated": False,
                "reason": str(error), "error_type": type(error).__name__}
