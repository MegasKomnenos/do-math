"""Area-specific persisted-state invariants, for the current record families.

The checks establish record binding and currentness only.  They do not decide
whether a theorem, explanation, or academic assessment is substantively true.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .academic import academic_status


def _error(errors: list[str], subject: str, detail: str) -> None:
    errors.append(f"{subject}: {detail}")


def _source_errors(instance: dict, errors: list[str]) -> None:
    """Source names and paths are required and distinct; the record schema sets the rest."""
    seen = {"name": set(), "path": set()}
    for index, source in enumerate(instance.get("sources", [])):
        label = f"source[{index}]"
        for key in ("name", "path"):
            value = source.get(key)
            if not isinstance(value, str) or not value:
                _error(errors, label, f"missing {key}")
            elif value in seen[key]:
                _error(errors, label, f"duplicate {key}")
            else:
                seen[key].add(value)


def _supplement_errors(instance: dict, runtime: dict, errors: list[str]) -> None:
    cycles = runtime.get("review_cycles", {})
    for action in runtime.get("queue", []):
        if not isinstance(action, dict) or action.get("role") != "supplemental_research" or not action.get("review_cycle_id"):
            continue
        cycle = cycles.get(action["review_cycle_id"])
        request = cycle.get("research", {}).get(action.get("research_request_id")) if isinstance(cycle, dict) else None
        if not isinstance(cycle, dict) or cycle.get("status") != "working" or cycle.get("knowledge_id") != action.get("target") or not isinstance(request, dict) or request.get("status") != "pending" or request.get("action", {}).get("slot") != action.get("requesting_slot"):
            _error(errors, "supplemental review", "queued investigation is not linked to a pending review request")


def _goal_errors(instance: dict, runtime: dict, errors: list[str]) -> None:
    if runtime.get("status") != "completed":
        return
    group_id = instance.get("goal_assessment_basis")
    group = [item for item in instance.get("goal_judgments", []) if item.get("basis") == group_id]
    if not isinstance(group_id, str) or not group:
        _error(errors, "goal", "completed runtime lacks current audit group")
        return
    required = group[0].get("required", instance.get("config", {}).get("goal_auditors"))
    slots = [item.get("slot") for item in group]
    if not isinstance(required, int) or isinstance(required, bool) or len(group) != required or len(slots) != len(set(slots)) or any(item.get("decision") != "satisfied" or not item.get("scope_complete") or not item.get("current", True) for item in group):
        _error(errors, "goal", "completed runtime lacks complete current agreeing audits")


def state_errors(instance: dict, runtime: dict) -> list[str]:
    """Return persisted cross-record consistency errors without mutating inputs."""
    if not isinstance(instance, dict) or not isinstance(runtime, dict):
        return ["state: instance and runtime must be objects"]
    return [f['message'] for f in inspect_state(instance, runtime)['findings'] if f['status'] == 'blocked']


# These are inspection domains, not additional lifecycle state.  A domain can
# be incomplete because the selected implementation has not supplied its
# checker yet; that must never be rendered as a successful inspection.
CHECK_AREAS = (
    "record_storage", "governance_trust", "tasks_activities_executions",
    "preparation_selection", "mathematical_effect", "start_import_input",
    "self_check_stop", "repair_iteration",
)


def _finding(area: str, *, status: str, message: str, blocked_scope: list[str] | None = None,
             evidence: list[str] | None = None, next_owner: str = "operator") -> dict[str, Any]:
    return {"area": area, "status": status, "message": message,
            "blocked_scope": blocked_scope or [], "evidence": evidence or [],
            "next_owner": next_owner}


def inspection_exit_code(inspection):
    """One success rule for the four inspection states, not a second verdict."""
    if inspection.get('status') not in {'healthy', 'degraded', 'blocked', 'incomplete'}:
        raise ValueError('unknown inspection status')
    return 0 if inspection['status'] == 'healthy' else 1


def inspect_state(instance: dict, runtime: dict, *, requested_areas: list[str] | None = None,
                  snapshot: str | None = None, read_artifact=None, artifact_errors=None,
                  read_artifacts=None, artifact_sizes=None) -> dict[str, Any]:
    """Inspect declared persisted-state areas without inventing semantic facts.

    Each area lists its actual checked invariants and missing evidence.
    No result certifies mathematical truth, live providers or OS isolation.
    The state must be one the repository loaded: loading validated it under the
    state contract, and the areas add only conditions loading does not check.
    ``artifact_sizes(paths)`` and ``read_artifacts(paths)`` return the stored
    lengths or bytes of the paths present in the snapshot and omit absent ones.
    ``artifact_sizes`` replaces byte-hash checks of referenced artifacts with
    presence and stored-length checks; ``check`` omits it to compare bytes.
    """
    if requested_areas is None:
        requested_areas = list(CHECK_AREAS)
    if not isinstance(requested_areas, list) or any(not isinstance(name, str) for name in requested_areas):
        raise ValueError("requested_areas must be a list of area names")
    requested = list(dict.fromkeys(requested_areas))
    findings: list[dict[str, Any]] = []
    areas: list[dict[str, Any]] = []
    not_checked: list[str] = []
    for area in requested:
        if area not in CHECK_AREAS:
            not_checked.append(area)
            findings.append(_finding(area, status="incomplete", message="unknown inspection area",
                                     next_owner="operator"))
            areas.append({"name": area, "status": "incomplete", "checked": False, "findings": 1})
            continue
        try:
            local, checked, missing = _inspect_area(area, instance, runtime, read_artifact, read_artifacts, artifact_sizes)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            local = [_finding(area, status='blocked', message='malformed domain records: ' + str(error),
                              blocked_scope=[area], next_owner='maintenance')]
            checked, missing = [], ['remaining invariants after malformed records']
        if area == 'record_storage':
            local.extend(_finding(area, status='blocked', message=str(error), blocked_scope=['artifacts'], next_owner='maintenance') for error in artifact_errors or [])
        findings.extend(local)
        if missing:
            not_checked.append(area)
        statuses = {row['status'] for row in local}
        status = 'blocked' if 'blocked' in statuses else 'incomplete' if missing else 'degraded' if 'degraded' in statuses else 'healthy'
        areas.append({'name': area, 'status': status, 'checked': not missing,
                      'checked_invariants': checked, 'not_checked': missing, 'findings': len(local)})
    statuses = {finding["status"] for finding in findings}
    if "blocked" in statuses:
        overall = "blocked"
    elif not_checked or "incomplete" in statuses:
        overall = "incomplete"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"
    return {"status": overall, "snapshot": snapshot, "requested_areas": requested, "areas": areas,
            "not_checked": not_checked, "findings": findings,
            "checked_scope": "persisted records only; no new mathematical, provider, or host verification"}


def _inspect_area(area, instance, runtime, read_artifact, read_artifacts=None, artifact_sizes=None):
    """Inspect the conditions of one area that loading does not already establish.

    The state passed the state contract when it was loaded: record schemas,
    family validators, references, global record-ID uniqueness, the semantic
    rules of ``record_schemas.validate_semantics`` and the current lifecycle
    gate. Each area reports that fact and adds only its own conditions.
    """
    findings, checked, missing = [], ['load-time state contract validation'], []

    def defect(message, target='state', status='blocked'):
        findings.append(_finding(area, status=status, message=str(message),
                                 blocked_scope=[target] if status == 'blocked' else [],
                                 evidence=[target], next_owner='maintenance'))

    def run(name, function, target='state'):
        try:
            result = function()
            if isinstance(result, list):
                for error in result:
                    defect(error, target)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            defect(f'{target}: {error}', target)
        except OSError as error:
            missing.append(name)
            defect(f'{target}: {error}', target, 'incomplete')
        checked.append(name)

    def omitted(name):
        missing.append(name)
        defect(name + ' not examined', status='incomplete')

    if area == 'record_storage':
        def sources():
            errors = []; _source_errors(instance, errors)
            return errors
        run('source descriptor names and paths', sources)
        refs = list(instance.get('sources', []))
        for execution in runtime.get('executions', {}).values():
            refs.extend(execution.get('output_files', []))
        if artifact_sizes is not None:
            # Absent paths are omitted from the result; each is its own defect.
            sizes = artifact_sizes(list(dict.fromkeys(ref.get('artifact_ref') or ref.get('path') for ref in refs)))
            for ref in refs:
                def verify_size(ref=ref):
                    path = ref.get('artifact_ref') or ref.get('path')
                    if path not in sizes:
                        raise ValueError('artifact is missing')
                    if 'bytes' in ref and sizes[path] != ref['bytes']:
                        raise ValueError('artifact length differs')
                run('artifact presence and length', verify_size, ref.get('artifact_ref') or ref.get('path', 'source'))
        elif refs and read_artifact is None:
            omitted('referenced artifact bytes')
        elif read_artifact:
            from .context_store import prefetch_artifacts
            read = prefetch_artifacts([ref.get('artifact_ref') or ref.get('path') for ref in refs],
                                      read_artifact, read_artifacts)
            for ref in refs:
                def verify(ref=ref):
                    path = ref.get('artifact_ref') or ref.get('path')
                    raw = read(path)
                    if hashlib.sha256(raw).hexdigest() != ref.get('sha256') or ('bytes' in ref and len(raw) != ref['bytes']):
                        raise ValueError('artifact hash or length differs')
                run('artifact bytes', verify, ref.get('artifact_ref') or ref.get('path', 'source'))
        from .retention import pending_cleanup_failures
        for failure in pending_cleanup_failures(runtime):
            defect('local cleanup failed: ' + str(failure.get('path')) + ': ' + str(failure.get('error')),
                   failure['evidence_ref'], 'degraded')
        checked.append('unresolved cleanup failures from maintenance history')
    elif area == 'governance_trust':
        envs = instance.get('trust_environments', {})
        active = [key for key, value in envs.items() if value.get('status') == 'active']
        if len(active) > 1 or (instance.get('active_trust_environment') and active != [instance['active_trust_environment']]):
            defect('active trust environment is not unique or does not match pointer', 'trust_environments')
        checked.append('active trust environment uniqueness')
        from .trust_validation import environment_errors
        bindings = runtime.get('trust_bindings', {})
        for identifier, environment in envs.items():
            run('trust environment and binding structure',
                lambda e=environment, b=bindings.get(identifier): environment_errors(e, b), identifier)
        if envs:
            omitted('shared toolchain records and installed files (persisted snapshot inspection only)')
    elif area == 'tasks_activities_executions':
        from .execution_lifecycle import OUTCOMES
        from .task_contracts import validate_item_dispositions
        for identifier, task in runtime.get('tasks', {}).items():
            if task.get('scope_disposition', {}).get('kind') == 'withdraw':
                from .task_scope import validate_withdrawal_record
                run('withdrawal preserves returned work and residual scope', lambda t=task: validate_withdrawal_record(t), identifier)
            if task.get('status') in {'completed', 'closed'} and any(e.get('status') != 'ended' and e.get('action', {}).get('target') == identifier for e in runtime.get('executions', {}).values()):
                defect('terminal task has a live worker', identifier)
            # Loading checks the dispositions of every recorded assessment; a
            # completed task without one is this inspection's own finding.
            if task.get('status') == 'completed' and not task.get('assessment'):
                run('item dispositions and completion', lambda t=task: validate_item_dispositions(t, {}, require_complete=True), identifier)
            for disposition in task.get('assessment', {}).get('item_dispositions', []):
                if disposition.get('kind') in {'waived', 'transferred'} and disposition.get('authority_ref') not in instance.get('decisions', {}) and disposition.get('authority_ref') not in instance.get('grants', {}):
                    defect('obligation disposition has no resolving authority', identifier)
                if disposition.get('kind') == 'transferred':
                    target = runtime.get('tasks', {}).get(disposition.get('target_task_id'), {})
                    if disposition.get('target_obligation_id') not in {r['id'] for r in target.get('completion_obligations', [])}:
                        defect('transferred obligation target is absent', identifier)
        for identifier, execution in runtime.get('executions', {}).items():
            if execution.get('status') == 'ended' and execution.get('outcome') not in OUTCOMES:
                defect('ended execution lacks closed outcome or timestamp', identifier)
            for reservation_id in execution.get('capacity', {}).get('reservation_ids', []):
                reservation = runtime.get('reservations', {}).get(reservation_id)
                if not reservation or reservation.get('owner_id') != identifier:
                    defect('execution reservation does not resolve to its owner', identifier)
        checked.append('execution outcomes, task transfers and execution reservation owners')
        from .budget import _outstanding_sum
        for identifier, constraint in instance.get('capacity_constraints', {}).items():
            if constraint.get('kind') != 'concurrency':
                continue
            def capacity(c=constraint):
                reservations = runtime.get('reservations', {})
                units = {r['unit'] for r in reservations.values() if r['constraint_id'] == c['id']}
                for unit in units:
                    if _outstanding_sum(reservations, c['id'], unit) > c['work_slots']:
                        raise ValueError('reservation ledger exceeds work capacity')
            run('reservation work capacity', capacity, identifier)
        for identifier, operation in runtime.get('external_operations', {}).items():
            status = operation.get('status')
            execution_id = operation.get('execution_id')
            if execution_id is not None and (status != 'prepared' or execution_id in runtime.get('executions', {})):
                execution = runtime.get('executions', {}).get(execution_id, {})
                if execution.get('role') != 'external_action' or execution.get('operation_id') != identifier:
                    defect('external operation has missing EX execution mapping', identifier)
                for field in ('grant_id', 'request_sha256', 'source_ref'):
                    if execution.get(field) != operation.get(field):
                        defect('external execution ' + field + ' differs from ledger', identifier)
            if status == 'unknown' and operation.get('succeeded') is not None:
                defect('unknown external effect has a definitive success value', identifier)
            if status == 'cancelled' and operation.get('transmitted') is not False and operation.get('reconciliation', {}).get('evidence', {}).get('fact') != 'not_transmitted':
                defect('cancelled external effect was not confirmed untransmitted', identifier)
            if operation.get('handling') == 'reconciled' and not operation.get('reconciliation', {}).get('evidence', {}).get('evidence_ref'):
                defect('reconciled handling lacks external effect evidence', identifier)
        checked.append('external effect facts')
    elif area == 'mathematical_effect':
        from .knowledge_records import formal_usable
        for identifier, formal in instance.get('formal_results', {}).items():
            if formal.get('publication_state') == 'accepted' and formal.get('formal_use') == 'active':
                run('formal use currentness', lambda f=formal: [] if formal_usable(instance, f) else ['active formal result has stale verification or trust basis'], identifier)
        if instance.get('goal_status') == 'mathematically_solved' or runtime.get('status') == 'completed':
            def audits():
                errors = []
                _goal_errors(instance, {**runtime, 'status': 'completed'}, errors)
                return errors
            run('solved goal complete current agreeing audits', audits, 'goal')
        if runtime.get('status') == 'completed':
            from .academic_engine import current_solution_basis
            artifact_refs = [ref for record in runtime.get('academic_resolution_records', [])
                             for ref in record.get('evidence_refs', []) if ref.startswith('runtime/artifacts/')]
            if artifact_refs and read_artifact is None:
                omitted('current academic resolution artifact bytes')
            else:
                def completed_academic():
                    def resolve_evidence(ref):
                        if read_artifact is not None and ref.startswith('runtime/artifacts/'):
                            return read_artifact(ref)
                        return None
                    status = academic_status(instance, runtime, current_solution_basis(instance, runtime),
                                             resolve_evidence=resolve_evidence)
                    if status['status'] not in {'completed', 'not_applicable'}:
                        raise ValueError('completed runtime has incomplete current academic requirements')
                run('completed academic requirements and external receipts', completed_academic, 'goal')
    elif area == 'preparation_selection':
        live = [e for e in runtime.get('executions', {}).values() if e.get('status') != 'ended']
        for role in ('research_preparation', 'research_plan'):
            if sum(e.get('role') == role for e in live) > 1:
                defect('multiple live ' + role + ' executions', role)
        for action in runtime.get('queue', []):
            if action.get('role') == 'research_work' and action.get('target') not in runtime.get('tasks', {}):
                defect('selected work references absent task', action.get('id', 'queue'))
        checked.extend(['single live preparation/selection', 'queued work task references'])
        def supplements():
            errors = []; _supplement_errors(instance, runtime, errors); return errors
        run('supplementary research request ownership', supplements)
    elif area == 'start_import_input':
        for identifier, execution in runtime.get('executions', {}).items():
            manifest = execution.get('input_manifest')
            if execution.get('actor_kind') == 'machine':
                if not manifest:
                    defect('machine execution has no source manifest', identifier)
                checked.append('machine input manifest presence')
                continue
            if not isinstance(manifest, dict) or 'direct' not in manifest:
                omitted(identifier + ': role input manifest')
                continue
            from .context_store import verify_manifest_artifacts
            def input_bytes(m=manifest, identifier=identifier):
                # verify_manifest_artifacts validates the manifest before its bytes.
                absent = verify_manifest_artifacts(m, read_artifact, read_artifacts=read_artifacts,
                                                   artifact_sizes=artifact_sizes)
                if absent:
                    omitted(identifier + ': actual input bytes for ' + ', '.join(absent))
            run('published role input bytes', input_bytes, identifier)
        checked.append('execution manifest availability')
    elif area == 'self_check_stop':
        from .observations import validate_rules, self_check_feedback
        for identifier, obligation in runtime.get('self_check_obligations', {}).items():
            run('self-check due inputs', lambda o=obligation: (self_check_feedback(o), None)[1], identifier)
        for identifier, execution in runtime.get('executions', {}).items():
            if 'observation_rules' in execution:
                run('observation rules', lambda e=execution: (validate_rules(e['observation_rules']), None)[1], identifier)
    elif area == 'repair_iteration':
        from .task_contracts import repetition_lineages
        run('five repetition lineages', lambda: (repetition_lineages(runtime), None)[1])
    return findings, checked, missing
