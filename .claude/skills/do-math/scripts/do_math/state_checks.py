"""Area-specific persisted-state invariants, including separated v5 records.

The checks establish record binding and currentness only.  They do not decide
whether a theorem, explanation, or academic assessment is substantively true.
Feature-1 snapshots keep their original permissive wire shape.  Unknown later
feature versions are rejected, matching the executor's explicit migration gate.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from .academic import academic_status, solution_basis


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TERMINAL_OPERATION = {"confirmed", "failed", "unknown", "cancelled"}
_OPERATION_STATUS = {"prepared", "running", *_TERMINAL_OPERATION}
_SUSPENSION_KINDS = {"environment", "dependency", "semantic"}


def _is_feature2(instance: dict, runtime: dict) -> bool:
    return instance.get("feature_version", runtime.get("feature_version", 1)) in {2, 3, 4, 5}


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256.fullmatch(value))


def _error(errors: list[str], subject: str, detail: str) -> None:
    errors.append(f"{subject}: {detail}")


def _source_errors(instance: dict, errors: list[str]) -> None:
    seen = {"id": set(), "name": set(), "path": set()}
    for index, source in enumerate(instance.get("sources", [])):
        label = f"source[{index}]"
        if not isinstance(source, dict):
            _error(errors, label, "descriptor is not an object")
            continue
        for key in ("name", "path"):
            value = source.get(key)
            if not isinstance(value, str) or not value:
                _error(errors, label, f"missing {key}")
            elif value in seen[key]:
                _error(errors, label, f"duplicate {key}")
            else:
                seen[key].add(value)
        if "id" in source:
            value = source["id"]
            if not isinstance(value, str) or not value:
                _error(errors, label, "invalid id")
            elif value in seen["id"]:
                _error(errors, label, "duplicate id")
            else:
                seen["id"].add(value)
        if not _sha(source.get("sha256")):
            _error(errors, label, "invalid sha256")
        if "bytes" in source and (isinstance(source["bytes"], bool) or not isinstance(source["bytes"], int) or source["bytes"] < 0):
            _error(errors, label, "invalid byte count")


def _knowledge_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    environments = instance.get("trust_environments", {})
    active_environment = instance.get("active_trust_environment")
    executions = runtime.get("executions", {})
    cycles = runtime.get("review_cycles", {})
    for kid, record in instance.get("knowledge", {}).items():
        if not isinstance(record, dict):
            _error(errors, str(kid), "knowledge record is not an object")
            continue
        suspensions = record.get("use_suspensions")
        if feature2 and suspensions is not None:
            if not isinstance(suspensions, list):
                _error(errors, str(kid), "typed use_suspensions is not a list")
            else:
                for cause in suspensions:
                    if not isinstance(cause, dict) or cause.get("kind") not in _SUSPENSION_KINDS or not isinstance(cause.get("reason"), str) or not cause["reason"].strip():
                        _error(errors, str(kid), "invalid typed use suspension")
                        break
                if bool(record.get("use_suspended")) != bool(suspensions):
                    _error(errors, str(kid), "use_suspended disagrees with typed suspensions")
        if record.get("status") != "verified" or record.get("use_suspended"):
            continue
        formal = record.get("formal") if isinstance(record.get("formal"), dict) else {}
        if formal.get("status") != "verified":
            _error(errors, str(kid), "current K lacks verified formal result")
        source = record.get("lean_code")
        if not isinstance(source, str) or formal.get("source_sha256") != hashlib.sha256((source if isinstance(source, str) else "").encode("utf-8")).hexdigest():
            _error(errors, str(kid), "current K formal source is stale")
        if feature2:
            environment_id = formal.get("trust_environment_id")
            environment = environments.get(environment_id) if isinstance(environments, dict) else None
            if not isinstance(environment_id, str) or environment_id != active_environment or not isinstance(environment, dict) or environment.get("status") != "active" or formal.get("trust_environment_status") != "active":
                _error(errors, str(kid), "current K formal environment is not active")
            assessment = record.get("identity_assessment") if isinstance(record.get("identity_assessment"), dict) else {}
            cycle_id = record.get("review_cycle_id")
            cycle = cycles.get(cycle_id) if isinstance(cycles, dict) else None
            if not isinstance(cycle_id, str) or not isinstance(cycle, dict) or cycle.get("knowledge_id") != kid or cycle.get("status") != "completed" or cycle.get("decision") != "match" or not assessment.get("effective"):
                _error(errors, str(kid), "current K lacks an effective final identity cycle")
                continue
            if assessment.get("cycle_id") != cycle_id or assessment.get("proposal_digest") != cycle.get("proposal_digest") or assessment.get("decision") != "match":
                _error(errors, str(kid), "identity assessment is not bound to final cycle")
            execution_ids = assessment.get("execution_ids")
            if not isinstance(execution_ids, list) or not execution_ids or len(execution_ids) != len(set(execution_ids)):
                _error(errors, str(kid), "identity assessment has invalid final execution IDs")
            else:
                for execution_id in execution_ids:
                    execution = executions.get(execution_id)
                    action = execution.get("action", {}) if isinstance(execution, dict) else {}
                    if not isinstance(execution, dict) or execution.get("role") != "identity_review" or execution.get("outcome") != "output_accepted" or action.get("target") != kid or action.get("review_cycle_id") != cycle_id:
                        _error(errors, str(kid), "identity assessment references an unaccepted review execution")
                        break


def _task_errors(runtime: dict, errors: list[str], feature2: bool) -> None:
    executions = runtime.get("executions", {})
    for task_id, task in runtime.get("tasks", {}).items():
        if not isinstance(task, dict) or task.get("status") != "completed":
            continue
        assessment = task.get("assessment") if isinstance(task.get("assessment"), dict) else {}
        criteria = task.get("completion_criteria")
        checks = assessment.get("criteria_results")
        if assessment.get("current") is False and not (
                isinstance(assessment.get("invalidated_reason"), str) and assessment["invalidated_reason"].strip()):
            _error(errors, str(task_id), "suspended completed task assessment lacks an invalidation reason")
        if assessment.get("decision") != "completed" or not isinstance(criteria, list) or not isinstance(checks, list):
            _error(errors, str(task_id), "completed task lacks criteria assessment")
        else:
            names = [entry.get("criterion") for entry in checks if isinstance(entry, dict)]
            if len(names) != len(checks) or sorted(names) != sorted(criteria) or any(not entry.get("satisfied") or not isinstance(entry.get("evidence"), str) or not entry["evidence"].strip() for entry in checks):
                _error(errors, str(task_id), "completed task criteria evidence is incomplete")
        for execution in executions.values():
            action = execution.get("action", {}) if isinstance(execution, dict) else {}
            if isinstance(execution, dict) and execution.get("status") in {"starting", "running", "stopping"} and execution.get("role") in {"research_work", "supplemental_research"} and action.get("target") == task_id:
                _error(errors, str(task_id), "completed task has a live worker")
                break


def _external_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    if not feature2:
        return
    executions = runtime.get("executions", {})
    for operation_id, operation in runtime.get("external_operations", {}).items():
        if not isinstance(operation, dict) or operation.get("id") != operation_id:
            _error(errors, f"operation[{operation_id}]", "ledger key and id differ")
            continue
        status = operation.get("status")
        if status not in _OPERATION_STATUS:
            _error(errors, f"operation[{operation_id}]", "unknown status")
        execution_id = operation.get("execution_id")
        execution = executions.get(execution_id)
        # Preparation allocates an EX identifier before any execution record is
        # persisted.  It is an auditable queued operation, not a missing record.
        if status == "prepared" and execution is None:
            continue
        if not isinstance(execution_id, str) or not isinstance(execution, dict) or execution.get("role") != "external_action" or execution.get("operation_id") != operation_id:
            _error(errors, f"operation[{operation_id}]", "missing EX execution mapping")
            continue
        for key in ("grant_id", "request_sha256", "source_ref"):
            if execution.get(key) != operation.get(key):
                _error(errors, f"operation[{operation_id}]", f"EX {key} differs from ledger")
        if status in _TERMINAL_OPERATION:
            status_matches = execution.get("status") == "ended" and execution.get("outcome") == status
        elif status == "running":
            status_matches = execution.get("status") in {"starting", "running", "stopping"} and execution.get("outcome") in {None, "prepared", "running"}
        else:  # Some persisted snapshots capture the prepared transmission barrier.
            status_matches = execution.get("status") in {"prepared", "starting", "running"} and execution.get("outcome") in {None, "prepared", "running"}
        if not status_matches:
            _error(errors, f"operation[{operation_id}]", "EX status differs from ledger")
        http_status = operation.get("http_status")
        has_http_status = isinstance(http_status, int) and not isinstance(http_status, bool)
        expected_success = 200 <= http_status < 300 if has_http_status else None
        if has_http_status and (operation.get("succeeded") != expected_success or execution.get("succeeded") != expected_success):
            _error(errors, f"operation[{operation_id}]", "HTTP success flag differs from HTTP status")
        # User/adapter reconciliation can confirm an unknown operation without a
        # response body or HTTP status.  Its recorded reconciliation is the basis.
        if not has_http_status:
            reconciliation = operation.get("reconciliation", {})
            success = reconciliation.get("succeeded") if status == "confirmed" and reconciliation.get("source") in {"user", "adapter"} and reconciliation.get("evidence") else None
            if operation.get("succeeded") != success or execution.get("succeeded") != success:
                _error(errors, f"operation[{operation_id}]", "success flag lacks explicit reconciliation evidence")


def _supplement_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
    if not feature2:
        return
    cycles = runtime.get("review_cycles", {})
    for action in runtime.get("queue", []):
        if not isinstance(action, dict) or action.get("role") != "supplemental_research" or not action.get("review_cycle_id"):
            continue
        cycle = cycles.get(action["review_cycle_id"])
        request = cycle.get("research", {}).get(action.get("research_request_id")) if isinstance(cycle, dict) else None
        if not isinstance(cycle, dict) or cycle.get("status") != "working" or cycle.get("knowledge_id") != action.get("target") or not isinstance(request, dict) or request.get("status") != "pending" or request.get("action", {}).get("slot") != action.get("requesting_slot"):
            _error(errors, "supplemental review", "queued investigation is not linked to a pending review request")


def _solution_basis(instance: dict) -> dict | None:
    group = instance.get("goal_assessment_basis")
    judgments = [item for item in instance.get("goal_judgments", []) if item.get("basis") == group]
    if not isinstance(group, str) or not judgments or any(not item.get("current", True) for item in judgments):
        return None
    ids = sorted({reference for item in judgments for reference in item.get("dependencies", []) if reference in instance.get("knowledge", {})})
    records = [instance["knowledge"][record_id] for record_id in ids]
    records.extend({"id": item.get("execution_id"), **item} for item in judgments if isinstance(item.get("execution_id"), str))
    try:
        return solution_basis(f"{instance.get('goal_revision', 1)}:{group}", records)
    except (KeyError, TypeError, ValueError):
        return None


def _goal_errors(instance: dict, runtime: dict, errors: list[str], feature2: bool) -> None:
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
    if feature2 and instance.get("academic_requirements", {}).get("items"):
        basis = _solution_basis(instance)
        if academic_status(instance, runtime, basis).get("status") != "completed":
            _error(errors, "goal", "completed runtime has incomplete academic requirements")


def state_errors(instance: dict, runtime: dict) -> list[str]:
    """Return persisted cross-record consistency errors without mutating inputs."""
    if not isinstance(instance, dict) or not isinstance(runtime, dict):
        return ["state: instance and runtime must be objects"]
    if instance.get('feature_version') == 5 or runtime.get('feature_version') == 5:
        return [f['message'] for f in inspect_state(instance, runtime)['findings'] if f['status'] == 'blocked']
    errors: list[str] = []
    versions = (instance.get("feature_version", 1), runtime.get("feature_version", 1))
    supported_versions = all(type(value) is int and value in {1, 2, 3, 4, 5} for value in versions)
    if not supported_versions:
        errors.append("state: unsupported feature version")
    feature2 = _is_feature2(instance, runtime)
    _source_errors(instance, errors)
    _knowledge_errors(instance, runtime, errors, feature2)
    _task_errors(runtime, errors, feature2)
    _external_errors(instance, runtime, errors, feature2)
    _supplement_errors(instance, runtime, errors, feature2)
    _goal_errors(instance, runtime, errors, feature2)
    if supported_versions and min(versions) >= 4:
        questions = runtime.get("question_links")
        if not isinstance(questions, list):
            _error(errors, "questions", "feature 4 requires question_links")
        else:
            seen = set()
            for row in questions:
                if not isinstance(row, dict) or not row.get("id") or row["id"] in seen:
                    _error(errors, "questions", "question link IDs must be distinct")
                    continue
                seen.add(row["id"])
                if row.get("owner") not in {"user", "research", "operations", "unclassified"} or row.get("status") not in {"open", "resolved", "superseded"}:
                    _error(errors, row["id"], "invalid question owner or status")
                if row.get("owner") == "user" and not row.get("target_ids"):
                    _error(errors, row["id"], "user question requires affected targets")
                if row.get("status") != "open" and not row.get("resolution_ref"):
                    _error(errors, row["id"], "closed question requires a resolution source")
        for entry in runtime.get("waiting_actions", {}).values():
            if entry.get("kind") == "revision_dependency" and not entry.get("revision_targets"):
                _error(errors, "revision_dependency", "unresolved revision targets are required")
    return errors


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
                  read_artifacts=None) -> dict[str, Any]:
    """Inspect declared persisted-state areas without inventing semantic facts.

    Each area lists its actual checked invariants and missing evidence.
    No result certifies mathematical truth, live providers or OS isolation.
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
            local, checked, missing = _inspect_area(area, instance, runtime, read_artifact, read_artifacts)
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


def _inspect_area(area, instance, runtime, read_artifact, read_artifacts=None):
    from copy import deepcopy
    findings, checked, missing = [], [], []

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

    v5 = instance.get('feature_version') == 5 or runtime.get('feature_version') == 5
    if v5:
        from .state_contract import default_state_contract
        from jsonschema import Draft202012Validator
        families = {
            'record_storage': ('sources', 'events'),
            'governance_trust': ('governance', 'governance_sources', 'decisions', 'grants', 'trust_environments', 'capability_evidence'),
            'tasks_activities_executions': ('tasks', 'activities', 'executions', 'execution_profiles', 'capacity_constraints', 'reservations', 'external_operations'),
            'preparation_selection': ('plans', 'preparations'),
            'mathematical_effect': ('knowledge', 'formal_results', 'expositions', 'identity_assessments', 'assessment_uses', 'relations', 'goal_judgments'),
            'start_import_input': ('integrations',),
            'self_check_stop': ('self_check_obligations', 'self_check_responses', 'observation_facts', 'operational_dispositions'),
            'repair_iteration': ('recoveries',),
        }[area]
        contract = default_state_contract()
        for root, container in (('research', instance), ('runtime', runtime)):
            for name in families:
                if name not in container:
                    continue
                family = contract.family(root, name)
                if family is None:
                    omitted(root + '/' + name + ': installed schema')
                    continue
                values = container[name]
                rows = values.values() if isinstance(values, dict) else values if isinstance(values, list) else [values]
                for index, row in enumerate(rows):
                    target = row.get('id', str(index)) if isinstance(row, dict) else str(index)
                    run(name + ' current record schema', lambda r=row, schema=family.schema:
                        [error.message for error in Draft202012Validator(schema).iter_errors(r)], target)
    if area == 'record_storage':
        def records():
            from .repository import validate_storage_value
            validate_storage_value(instance); validate_storage_value(runtime)
            seen = {}
            for root, obj in [('research', instance), ('runtime', runtime)]:
                for family, values in obj.items():
                    rows = values.values() if isinstance(values, dict) else values if isinstance(values, list) else []
                    for row in rows:
                        if not isinstance(row, dict) or not isinstance(row.get('id'), str):
                            continue
                        identifier = row['id']
                        if identifier in seen:
                            defect('duplicate record ID: ' + identifier, root + '/' + family)
                        seen[identifier] = root + '/' + family
            errors = []; _source_errors(instance, errors)
            return errors
        run('canonical values, record IDs and source descriptors', records)
        if instance.get('feature_version') != 5 or runtime.get('feature_version') != 5:
            defect('current state requires feature_version 5 in both families')
        refs = list(instance.get('sources', []))
        for execution in runtime.get('executions', {}).values():
            refs.extend(execution.get('output_files', []))
        if refs and read_artifact is None:
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
        if v5:
            from .governance import validate_governance_state
            run('governance records, original sources and approvals', lambda: validate_governance_state(instance), 'governance')
        envs = instance.get('trust_environments', {})
        active = [key for key, value in envs.items() if value.get('status') == 'active']
        if len(active) > 1 or (instance.get('active_trust_environment') and active != [instance['active_trust_environment']]):
            defect('active trust environment is not unique or does not match pointer', 'trust_environments')
        checked.append('active trust environment uniqueness')
        from .initialization import trust_environment_errors
        for identifier, environment in envs.items():
            run('fixed trust manifest structure', lambda e=environment: trust_environment_errors(e, verify_files=False), identifier)
        if envs:
            omitted('live installed trust-environment files (persisted snapshot inspection only)')
    elif area == 'tasks_activities_executions':
        if v5:
            from .activities import validate_activities
            from .execution_lifecycle import EXECUTION_STATUSES, OUTCOMES, STOP_PHASES
            from .task_contracts import validate_task_contract, validate_item_dispositions
            from .task_contracts import LIFECYCLE_STATES
            from .execution_profiles import resolve_profile, validate_profile
            from .budget import _validate_reservation
            run('activity ownership and continuation', lambda: validate_activities(deepcopy(runtime)), 'activities')
            for identifier, task in runtime.get('tasks', {}).items():
                run('task contract obligations', lambda t=task: validate_task_contract(t), identifier)
                if task.get('scope_disposition', {}).get('kind') == 'withdraw':
                    from .task_scope import validate_withdrawal_record
                    run('withdrawal preserves returned work and residual scope', lambda t=task: validate_withdrawal_record(t), identifier)
                if task.get('status') not in LIFECYCLE_STATES:
                    defect('invalid task lifecycle status', identifier)
                if task.get('status') in {'completed', 'closed'} and any(e.get('status') != 'ended' and e.get('action', {}).get('target') == identifier for e in runtime.get('executions', {}).values()):
                    defect('terminal task has a live worker', identifier)
                if task.get('assessment') or task.get('status') == 'completed':
                    run('item dispositions and completion', lambda t=task: validate_item_dispositions(t, t.get('assessment', {}), require_complete=t.get('status') == 'completed'), identifier)
                for disposition in task.get('assessment', {}).get('item_dispositions', []):
                    if disposition.get('kind') in {'waived', 'transferred'} and disposition.get('authority_ref') not in instance.get('decisions', {}) and disposition.get('authority_ref') not in instance.get('grants', {}):
                        defect('obligation disposition has no resolving authority', identifier)
                    if disposition.get('kind') == 'transferred':
                        target = runtime.get('tasks', {}).get(disposition.get('target_task_id'), {})
                        if disposition.get('target_obligation_id') not in {r['id'] for r in target.get('completion_obligations', [])}:
                            defect('transferred obligation target is absent', identifier)
            for identifier, profile in instance.get('execution_profiles', {}).items():
                run('immutable profile content', lambda p=profile: validate_profile(p), identifier)
                capacity_refs = profile.get('ai', {}).get('capacity_refs', []) + profile.get('ai', {}).get('usage_constraint_ids', []) + profile.get('host_capacity_refs', [])
                if set(capacity_refs) - set(instance.get('capacity_constraints', {})):
                    defect('profile capacity reference is absent', identifier)
            for identifier, execution in runtime.get('executions', {}).items():
                state = execution.get('status')
                if execution.get('id') != identifier or state not in EXECUTION_STATUSES:
                    defect('invalid execution ID or status', identifier)
                if state == 'stopping' and execution.get('stop_phase') not in STOP_PHASES:
                    defect('stopping execution lacks stop phase', identifier)
                if state == 'ended' and (execution.get('outcome') not in OUTCOMES or not execution.get('ended_at')):
                    defect('ended execution lacks closed outcome or timestamp', identifier)
                def profile_binding(e=execution):
                    p = resolve_profile(instance.get('execution_profiles', {}), e.get('execution_profile_ref'))
                    if p['role'] != e.get('role') or p['actor_kind'] != e.get('actor_kind'):
                        raise ValueError('execution differs from selected profile')
                run('execution profile binding', profile_binding, identifier)
                for reservation_id in execution.get('reservation_ids', []):
                    reservation = runtime.get('reservations', {}).get(reservation_id)
                    if not reservation or reservation.get('owner_id') != identifier:
                        defect('execution reservation does not resolve to its owner', identifier)
            for identifier, reservation in runtime.get('reservations', {}).items():
                run('reservation accounting', lambda r=reservation: _validate_reservation(r), identifier)
                if reservation.get('constraint_id') not in instance.get('capacity_constraints', {}):
                    defect('reservation constraint is absent', identifier)
                owner = reservation.get('owner_id')
                if reservation.get('owner_kind') == 'execution' and owner not in runtime.get('executions', {}):
                    defect('reservation execution owner is absent', identifier)
            checked.append('execution states, task transfers and reservation references')
            from .budget import _outstanding_sum
            for identifier, constraint in instance.get('capacity_constraints', {}).items():
                if constraint.get('kind') != 'concurrency':
                    continue
                def capacity(c=constraint):
                    if c['work_slots'] + c['operations_slots'] > c['total_slots']:
                        raise ValueError('work and operations capacity exceed total')
                    reservations = runtime.get('reservations', {})
                    units = {r['unit'] for r in reservations.values() if r['constraint_id'] == c['id']}
                    for unit in units:
                        total = _outstanding_sum(reservations, c['id'], unit)
                        if total > c['total_slots']:
                            raise ValueError('reservation ledger exceeds total capacity')
                        for pool in ('work', 'operations'):
                            if _outstanding_sum(reservations, c['id'], unit, budget_kind=pool) > c[pool + '_slots']:
                                raise ValueError('reservation ledger exceeds ' + pool + ' capacity')
                run('reservation capacity pool separation', capacity, identifier)
            for identifier, operation in runtime.get('external_operations', {}).items():
                status = operation.get('effect_status', operation.get('status'))
                execution_id = operation.get('execution_id')
                if execution_id is not None and (status != 'prepared' or execution_id in runtime.get('executions', {})):
                    execution = runtime.get('executions', {}).get(execution_id, {})
                    if execution.get('role') != 'external_action' or execution.get('operation_id') != identifier:
                        defect('external operation has missing EX execution mapping', identifier)
                    for field in ('grant_id', 'request_sha256', 'source_ref'):
                        if execution.get(field) != operation.get(field):
                            defect('external execution ' + field + ' differs from ledger', identifier)
                if status not in _OPERATION_STATUS:
                    defect('unknown external effect status', identifier)
                if status == 'unknown' and operation.get('succeeded') is not None:
                    defect('unknown external effect has a definitive success value', identifier)
                if status == 'failed' and operation.get('effect_absent') is not True:
                    defect('failed external effect lacks absence evidence', identifier)
                if status == 'confirmed' and operation.get('succeeded') is not True:
                    defect('confirmed external effect lacks success evidence', identifier)
                if status == 'cancelled' and operation.get('transmitted') is not False and operation.get('reconciliation', {}).get('evidence', {}).get('fact') != 'not_transmitted':
                    defect('cancelled external effect was not confirmed untransmitted', identifier)
                if operation.get('request'):
                    import json
                    raw = json.dumps(operation['request'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
                    digest = hashlib.sha256(raw).hexdigest()
                    if digest != operation.get('request_sha256') or hashlib.sha256((identifier + digest).encode()).hexdigest() != operation.get('idempotency_key'):
                        defect('external request or idempotency binding changed', identifier)
                if operation.get('handling') == 'reconciled' and not operation.get('reconciliation', {}).get('evidence', {}).get('evidence_ref'):
                    defect('reconciled handling lacks external effect evidence', identifier)
            checked.append('external effect facts')
        else:
            def legacy():
                errors = []; _task_errors(runtime, errors, True); _external_errors(instance, runtime, errors, True)
                return errors
            run('legacy task and external mappings', legacy)
    elif area == 'mathematical_effect':
        if v5:
            from .knowledge_records import validate_knowledge_records, formal_usable, validate_formal_evidence, _assessment_basis
            run('separated knowledge references and effect states', lambda: validate_knowledge_records(instance), 'knowledge')
            for identifier, formal in instance.get('formal_results', {}).items():
                if formal.get('publication_state') == 'accepted' and formal.get('formal_use') == 'active':
                    run('formal use currentness', lambda f=formal: [] if formal_usable(instance, f) else ['active formal result has stale verification or trust basis'], identifier)
                if formal.get('verification') or formal.get('publication_state') == 'accepted':
                    run('formal source, dependency and trust evidence', lambda f=formal: validate_formal_evidence(f, f.get('verification', {}), instance.get('trust_environments', {}).get(f.get('trust_environment_id'), {})), identifier)
            for identifier, assessment in instance.get('identity_assessments', {}).items():
                def identity_basis(a=assessment):
                    expected = _assessment_basis(instance['formal_results'][a['formal_result_id']], instance['expositions'][a['exposition_id']])
                    if a.get('basis') != expected:
                        raise ValueError('identity assessment premise differs from immutable inputs')
                run('identity assessment exact input basis', identity_basis, identifier)
            if instance.get('goal_status') == 'mathematically_solved' or runtime.get('status') == 'completed':
                def audits():
                    errors = []
                    _goal_errors(instance, {**runtime, 'status': 'completed'}, errors, False)
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
        else:
            def legacy_k():
                errors = []; _knowledge_errors(instance, runtime, errors, _is_feature2(instance, runtime)); return errors
            run('legacy K evidence', legacy_k)
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
            errors = []; _supplement_errors(instance, runtime, errors, True); return errors
        run('supplementary research request ownership', supplements)
        for plan in runtime.get('plans', []):
            from .task_contracts import validate_plan_dispositions
            if isinstance(plan.get('ready_ids'), list):
                run('plan all-candidate dispositions', lambda p=plan: validate_plan_dispositions(p, runtime.get('tasks', {}), p['ready_ids']), plan.get('id', 'plan'))
            else:
                omitted('plan fixed candidate population')
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
            from .context_store import validate_role_manifest, verify_manifest_artifacts
            run('role input byte and revision manifest', lambda m=manifest: validate_role_manifest(m), identifier)
            def input_bytes(m=manifest, identifier=identifier):
                absent = verify_manifest_artifacts(m, read_artifact, read_artifacts=read_artifacts)
                if absent:
                    omitted(identifier + ': actual input bytes for ' + ', '.join(absent))
            run('published role input bytes', input_bytes, identifier)
        checked.append('execution manifest availability')
    elif area == 'self_check_stop':
        from .observations import validate_rules, self_check_feedback
        for identifier, rules in runtime.get('task_observation_rules', {}).items():
            run('current task observation rule operators and units', lambda rules=rules: (validate_rules(rules, allow_empty=True), None)[1], identifier)
        for identifier, obligation in runtime.get('self_check_obligations', {}).items():
            run('self-check due inputs', lambda o=obligation: (self_check_feedback(o), None)[1], identifier)
            if obligation.get('execution_id') not in runtime.get('executions', {}):
                defect('self-check obligation has no execution', identifier)
        for identifier, response in runtime.get('self_check_responses', {}).items():
            if response.get('kind') == 'self_check_rejected':
                continue
            obligation = runtime.get('self_check_obligations', {}).get(response.get('obligation_id'), {})
            if not obligation or obligation.get('execution_id') != response.get('execution_id'):
                defect('self-check response has no matching execution obligation', identifier)
        from .operational_dispositions import validate_disposition
        for identifier, record in runtime.get('operational_dispositions', {}).items():
            run('six operating dispositions', lambda r=record: validate_disposition(r.get('disposition')), identifier)
        for identifier, execution in runtime.get('executions', {}).items():
            if 'observation_rules' in execution:
                run('observation rules', lambda e=execution: (validate_rules(e['observation_rules']), None)[1], identifier)
            for obligation in execution.get('self_check_obligations', []):
                if not obligation.get('id') or not obligation.get('status'):
                    defect('self-check obligation lacks identity or state', identifier)
                if obligation.get('status') in {'fulfilled', 'resolved'} and not obligation.get('response_ref'):
                    defect('closed self-check lacks response reference', identifier)
            if execution.get('status') == 'stopping' and not execution.get('stop_phase'):
                defect('stop has no phase', identifier)
        checked.extend(['self-check response bindings', 'stop phase'])
    elif area == 'repair_iteration':
        for identifier, waiting in runtime.get('waiting_actions', {}).items():
            if waiting.get('resolved') and not (waiting.get('resolution_ref') or waiting.get('resolved_by')):
                defect('resolved repair lacks accepted resolution evidence', identifier)
        from .task_contracts import repetition_lineages
        run('five repetition lineages', lambda: (repetition_lineages(instance, runtime), None)[1])
        checked.append('repair resolution references')
    return findings, checked, missing
