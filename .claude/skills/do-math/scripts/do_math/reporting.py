"""Projections of research snapshots and separately observed local evidence."""
import csv
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import io
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .provider_wait import epoch_seconds
from .canonical import exact_content_hash
from .repository import ResearchRepository
from .wait_rules import ADMISSION_WAITS
from .session_slots import live_action_ids
from .state_checks import inspect_state

# One implementation-level scope for live and historical status. Runtime state
# has no assurance family, so a snapshot cannot supply a different value.
ASSURANCE = {"read_scope": "instructions_and_selected_inputs", "provider_operations": "not_observed",
             "token_usage": "CLI_reported_after_execution", "formal": "Lean_and_axiom_check",
             "review": "fresh_sessions_without_peer_results_in_inputs"}


def _zone(name):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if name == "Asia/Seoul":
            return timezone(timedelta(hours=9), name="Asia/Seoul")
        if name == "UTC":
            return timezone.utc
        raise ValueError("timezone database has no entry for " + name)


def _display(value, zone):
    seconds = epoch_seconds(value)
    return datetime.fromtimestamp(seconds, timezone.utc).astimezone(zone).isoformat() if seconds is not None else None


def display_time(value, timezone_name='Asia/Seoul'):
    return _display(value, _zone(timezone_name))


def dispatch_waits(runtime):
    """Project preserved queue reasons without performing a new admission check."""
    live = live_action_ids(runtime)
    return [deepcopy({'action_id': a.get('id'), 'role': a['role'], 'target': a.get('target'),
                      'model_selection': a.get('model_selection'), 'wait': a['dispatch_wait']})
            for a in runtime.get('queue', []) if a.get('dispatch_wait') and a.get('id') not in live]


def task_status(instance, runtime, *, evaluation_context=None):
    """Per-task rows; readiness uses ``evaluation_context`` so a current view judges as dispatch does."""
    from . import planning, questions, task_contracts
    def targets_task(action, identifier):
        return (action.get('target') == identifier
                or (action.get('role') == 'research_preparation' and any(identifier in action.get(field, {})
                    for field in ('assessment_targets', 'observation_rule_targets'))))
    rows = []
    pending_assessments = set(task_contracts.returned_task_ids(runtime.get('tasks', {})))
    live = [e for e in runtime.get("executions", {}).values() if e.get("status") != "ended"]
    ended = planning.instance_ended(instance, runtime)
    for identifier, task in runtime.get("tasks", {}).items():
        queued = [action for action in runtime.get("queue", []) if targets_task(action, identifier)]
        executions = [e for e in live if targets_task(e.get('action', {}), identifier)]
        running_ids = {e.get("action", {}).get("id") for e in executions}
        obligations = [aid for aid, entry in runtime.get("waiting_actions", {}).items()
                       if entry.get("action", {}).get("target") == identifier or identifier in entry.get("action", {}).get("revision_targets", {})
                       or identifier in entry.get("delegated_targets", {}).values()]
        waiting = []
        if not ended and task.get('waiting'):
            waiting.append(task['waiting'])
        for action in queued:
            if action.get('id') in running_ids:
                continue
            waiting.extend(questions.user_waits(action, instance, runtime))
            waiting.extend(planning.revision_waits(action, instance, runtime))
            if action.get('dispatch_wait', {}).get('kind') in ADMISSION_WAITS:
                waiting.append(action['dispatch_wait'])
        readiness = None
        if not ended and not executions and task.get('status') not in task_contracts.TERMINAL_TASK_STATUSES:
            readiness = deepcopy(planning.task_ready(task, instance, runtime, include_scheduling_waits=False,
                                                     evaluation_context=evaluation_context))
            if readiness['state'] != 'ready':
                if readiness.get('waits'):
                    waiting.extend(readiness['waits'])
                else:
                    waiting.append({'kind': 'contract_review' if planning.CONTRACT_REVIEW_MISSING in readiness['errors'] else 'required_input',
                                    'errors': readiness['errors']})
        waiting = deepcopy(list({json.dumps(row, sort_keys=True): row for row in waiting}.values()))
        next_owner = ('user' if any(row.get('kind') == 'user_decision' or row.get('next_owner') == 'user' for row in waiting) else
                      next((row['next_owner'] for row in waiting if row.get('next_owner')),
                           'task_contract_review' if any(row.get('kind') == 'contract_review' for row in waiting)
                           else queued[0]['role'] if queued else None))
        assessment = task.get('assessment', {})
        followups = [e['id'] for e in runtime.get('events', [])
                     if e['kind'] == 'task_assessment_invalidated' and e.get('target') == identifier]
        if assessment.get('current') is False and task['status'] in task_contracts.TERMINAL_TASK_STATUSES:
            next_owner = next_owner or 'research_plan'
        rows.append({"id": identifier, "title": task.get("title", task.get('question')), "status": task["status"], "revision": task.get("revision"),
                     "selected_actions": [a.get("id") for a in queued if a.get("id") not in running_ids],
                     "active_execution_ids": [e["id"] for e in executions],
                     "assessment_pending": identifier in pending_assessments,
                     'recorded_decision': assessment.get('decision'),
                     'assessment_current': assessment.get('current'),
                     'assessment_invalidated_reason': assessment.get('invalidated_reason'),
                     'assessment_followup_event_refs': followups,
                     "last_accepted_result": task.get("results", [])[-1].get("execution_id") if task.get("results") else None,
                     "unresolved_action_ids": obligations, "waits": waiting,
                     "readiness": readiness, "next_owner": next_owner,
                     "next_observation_at": next((row.get("retry_at") for row in waiting if row.get("retry_at")), None)})
    return rows


def waiting_action_rows(runtime):
    """Project stored judgments and coordinates without recomputing a wait."""
    rows = {}
    coordinate_fields = ('target', 'owner_activity_id', 'profile_ref', 'grant_id', 'review_cycle_id',
        'stage', 'slot', 'round', 'replacement_for', 'sealedInputHash', 'execution_id', 'question_id',
        'import_id', 'constraint_id', 'constraint_kind', 'provider', 'retry_at', 'environment_id',
        'snapshot', 'input_snapshot', 'input_bundle', 'artifact_ref', 'source_ref')
    for identifier, entry in runtime.get('waiting_actions', {}).items():
        action = entry['action']
        coordinates = {'action_id': identifier}
        detail = entry.get('detail')
        for source in (action, entry, detail if isinstance(detail, dict) else {}):
            for field in coordinate_fields:
                if field in source and source[field] is not None:
                    coordinates[field] = deepcopy(source[field])
        rows[identifier] = {
            'role': action.get('role'), 'target': action.get('target'),
            'kind': entry.get('kind'), 'reason': entry.get('reason'),
            'execution_id': entry.get('execution_id'), 'failure_kind': entry.get('failure_kind'),
            'next_owner': deepcopy(entry.get('next_owner')),
            **deepcopy({key: value for key, value in entry.items() if key != 'action'}),
            'coordinates': coordinates,
        }
    return rows


def waiting_activity_rows(runtime):
    """All durable activity waits, including older waits outside the recent-result list."""
    return {identifier: deepcopy({
        'activity_kind': activity['activity_kind'], **activity['waiting'],
        'coordinates': {'activity_id': identifier, 'owner_ref': activity['owner_ref'],
                        'execution_ids': activity['assigned_execution_ids']},
    }) for identifier, activity in runtime.get('activities', {}).items() if activity['status'] == 'waiting'}


def operating_summary(instance, runtime):
    """One persisted-state handoff view; scheduler/process observations stay separate."""
    from .supervision import supervision_block, supervision_facts
    lifecycle=instance.get('lifecycle',{})
    facts=supervision_facts(instance,runtime)
    code=supervision_block({key:value for key,value in facts.items() if key!='operator_enabled'})
    repair=facts['installation_repair']
    if code=='user_pause':
        blocker={'kind':'user_pause','next_owner':'user',**facts['user_pause']}
    elif code=='maintenance':
        blocker={'kind':'maintenance_fence','next_owner':'operator','reason':runtime['maintenance_fence'].get('state')}
    elif code=='model_policy':
        blocker={'kind':'model_policy','next_owner':'user'}
    elif code=='paused':
        blocker={'kind':'paused','next_owner':'operator','reason':runtime.get('stop_requested'),
                 'questions':deepcopy(runtime.get('questions',[]))}
    elif code=='installation_repair':
        blocker={'kind':'installation_repair','next_owner':'installation_recovery',
                 'record_id':repair['id'],'reason':repair['disposition']['reason']}
    elif lifecycle.get('state')=='initializing':
        blocker={'kind':'initialization','next_owner':'operator',
                 'missing':deepcopy(lifecycle.get('activation',{}).get('missing',[]))}
    elif runtime.get('status') in {'waiting','capacity_waiting'}:
        waits=runtime.get('waiting_actions',{})
        owners=sorted({row['next_owner'] for row in waits.values() if row.get('next_owner')})
        blocker={'kind':runtime['status'],'next_owner':owners[0] if len(owners)==1 else None,
                 'owners':owners}
    else:
        blocker=None
    config=instance.get('config',{})
    return {'scope':'persisted_state_not_host_process_observation','lifecycle':lifecycle.get('state'),
        'initialization':deepcopy(lifecycle.get('activation',{})),
        'execution_status':runtime.get('status'),'goal_status':instance.get('goal_status'),
        'primary_blocker':blocker,'workspace':instance.get('workspace'),
        'conversation_loss_policy':instance.get('conversation_loss_policy'),
        'active_execution_ids':sorted(e['id'] for e in runtime.get('executions',{}).values() if e['status']!='ended'),
        'supervision':{'configured_enabled':config.get('operator_enabled'),
                       'interval_seconds':config.get('operator_interval_seconds'),
                       'actual_schedule':'operator status'},
        'grants':[{'id':g['id'],'status':g.get('status'),'expires_at':g.get('expires_at')}
                  for g in instance.get('grants',{}).values()]}


# Status fields a caller observes on this host at query time. A persisted
# snapshot cannot truthfully hold a live slot count or a clock-dependent
# judgment, so a status projection without an observation shows them as None.
OBSERVED_FIELDS = ("research_observed_at", "research_wake_reasons", "operation_progress",
                   "pending_controls", "budget", "provider_waits")


def status_report(store, head, instance, runtime, *, observation=None, requested_areas=None,
                  evaluation_context=None) -> dict:
    """The one status projection: every field of the persisted snapshot at ``head``.

    ``observation`` holds the OBSERVED_FIELDS the caller observed now; each
    field it omits is None. ``store`` reads the snapshot's artifacts.
    ``evaluation_context`` is the engine's current evaluation context, so task
    readiness sees this host's facts (a discovered Lean, the clock) exactly as
    dispatch does. A snapshot projection supplies its query time without live
    host capability observations.
    """
    from .academic import academic_status, stored_evidence
    from .academic import current_solution_basis
    from .execution_profiles import WORK_ROLES
    from .initialization import governance_or_initial_view
    from .knowledge_records import knowledge_view
    from .question_engine import question_view, user_questions
    from .retention import pending_cleanup_failures
    from .revisions import active_repetition_holds
    from .supervision import supervision_facts
    from .wait_rules import SLOT_WAITS
    observed = dict.fromkeys(OBSERVED_FIELDS)
    unknown = set(observation or {}) - set(OBSERVED_FIELDS)
    if unknown:
        raise ValueError("status observation has unknown fields: " + ", ".join(sorted(unknown)))
    observed.update(observation or {})
    governance_view = governance_or_initial_view(instance, runtime)
    executions = list(runtime.get("executions", {}).values())
    live = [e["id"] for e in executions if e["status"] != "ended"]
    waits = dispatch_waits(runtime)
    questions = question_view(instance, runtime, lambda refs: store.read_many(refs, head))
    return {"instance_id": instance["id"], "snapshot": head, "title": instance.get("title"),
            "operating_summary": operating_summary(instance, runtime),
            # Deriving check diagnostics reads every sealed check artifact; ``check`` does it.
            "submission_checks": {"status": "not_evaluated",
                "reason": "status reports persisted records; check derives submission check diagnostics"},
            "goal": governance_view["goal"], "goal_status": instance.get("goal_status"),
            "status": runtime.get("status"), "active_execution": live[0] if live else None,
            # The configuration a capability probe or an initialization adoption names (config_sha256).
            "config_sha256": exact_content_hash(instance.get("config", {})),
            "pending_actions": len(runtime.get("queue", [])), "cycles": runtime.get("cycles"),
            "tasks": task_status(instance, runtime, evaluation_context=evaluation_context), "dispatch_waits": waits,
            "knowledge": {"K": sum(row["usable"] for row in knowledge_view(instance)),
                          "formal_results": len(instance.get("formal_results", {})),
                          "expositions": len(instance.get("expositions", {})),
                          "identity_assessments": len(instance.get("identity_assessments", {}))},
            "inspection": inspect_state(instance, runtime, snapshot=head, requested_areas=requested_areas,
                read_artifact=lambda path: store.read(path, head),
                read_artifacts=lambda paths: store.read_many(paths, head, missing="omit"),
                artifact_sizes=lambda paths: store.blob_sizes(paths, head, missing="omit")),
            "budget_unit": "concurrent_sessions",
            "active_executions": live,
            "execution_attempts": {"work": sum(e.get("role") in WORK_ROLES for e in executions),
                                   "operations": sum(e.get("role") not in WORK_ROLES for e in executions)},
            "capacity_waiting": [{k: a[k] for k in ('role', 'target', 'model_selection')}
                                 for a in waits if a['wait']['kind'] in SLOT_WAITS],
            "usage": [e.get("usage", {}) for e in executions if e.get("usage")],
            "latest_results": list(runtime.get("activities", {}).values())[-5:],
            "questions": user_questions(questions),
            "question_links": questions,
            "repetition_holds": list(active_repetition_holds(runtime).values()),
            "operational_notices": deepcopy(runtime.get("questions", [])),
            # user_pause, conversation_lost, model_policy_violation, maintenance_fence,
            # installation_repair and operator_enabled: the facts supervision decides on.
            **supervision_facts(instance, runtime),
            "waiting_actions": waiting_action_rows(runtime),
            "waiting_activities": waiting_activity_rows(runtime),
            "grants": [{"id": g["id"], "kind": g.get("kind"), "status": g.get("status"), "expires_at": g.get("expires_at")}
                       for g in instance.get("grants", {}).values()],
            "pending_events": runtime.get("pending_events", []),
            "observations": runtime.get("observations", {}),
            "checkpoints": runtime.get("checkpoints", {}),
            "external_operations": list(runtime.get("external_operations", {}).values()),
            "active_trust_environment": instance.get("active_trust_environment"),
            "academic_validation": ({"status": "initialization_incomplete"}
                if governance_view.get("status") == "unadopted_input" else
                academic_status(instance, runtime, current_solution_basis(instance, runtime),
                                resolve_evidence=lambda ref: stored_evidence(store, head, ref))),
            "cleanup_failures": pending_cleanup_failures(runtime),
            "assurance": deepcopy(ASSURANCE),
            **observed}


def snapshot_report(repository: Path, instance_id: str, *, snapshot: str | None = None,
                    host_observation: dict | None = None, requested_areas=None, backend, clock) -> dict:
    """The status projection of one persisted snapshot (``status_report``).

    Host observations are deliberately caller-supplied and separately dated:
    a live slot count cannot truthfully be represented as historical snapshot
    state. Without ``host_observation`` the OBSERVED_FIELDS are None.
    """
    store = ResearchRepository(repository, instance_id, backend=backend, clock=clock)
    head, instance, runtime = store.load(snapshot)
    return status_report(store, head, instance, runtime, observation=host_observation,
                         requested_areas=requested_areas, evaluation_context={'now': clock.now()})


def render_human_report(report: dict) -> str:
    """Render a status report without reopening state or deriving new facts."""
    inspection = report["inspection"]
    tasks = report["tasks"]
    budget = report.get("budget")
    lines = [f"goal: {report.get('goal') or 'unknown'}",
             f"goal_status: {report.get('goal_status') or 'unknown'}",
             f"status: {report.get('status')}  snapshot: {report['snapshot']}",
             "work sessions: " + (", ".join(f"{model} {row['used']}/{row['limit']}" for model, row in budget.items())
                                  if budget is not None else "not observed"),
             "tasks: " + (", ".join(f"{task['id']}={task['status']}" for task in tasks) or "none"),
             "observed (Asia/Seoul): " + str(display_time(report['research_observed_at'])
                                             if report.get('research_observed_at') else 'not observed'),
             "unknown or bounded scope: " + ", ".join(f"{key}={value}" for key, value in report["assurance"].items()),
             f"inspection: {inspection['status']} ({inspection['checked_scope']})"]
    summary = report.get('operating_summary', {})
    blocker = summary.get('primary_blocker')
    if blocker:
        lines.append('blocking: '+str(blocker['kind'])+' next='+str(blocker.get('next_owner')))
        if blocker['kind'] == 'user_pause':
            for field in ('reason', 'request_id', 'created_at'):
                lines.append('  ' + field + ': ' + str(blocker[field]))
    if summary.get('lifecycle') == 'initializing':
        lines.append('initialization missing: '+', '.join(summary.get('initialization', {}).get('missing', [])))
    for finding in inspection["findings"]:
        lines.append(f"  {finding['area']}: {finding['status']} — {finding['message']} (next: {finding['next_owner']})")
    for task in tasks:
        waits = ', '.join(row.get('kind', 'unknown') for row in task.get('waits', [])) or 'none'
        lines.append(f"  {task['id']} revision={task.get('revision', 'unknown')} stage={task['status']} "
                     f"assessment_pending={str(task.get('assessment_pending', False)).lower()} "
                     f"active_records={','.join(task.get('active_execution_ids', [])) or 'none'} "
                     f"queued={','.join(str(value) for value in task.get('selected_actions', [])) or 'none'} "
                     f"waits={waits} next={task.get('next_owner') or 'none'}")
        for wait in task.get('waits', []):
            lines.append('    wait: ' + json.dumps(wait, ensure_ascii=False, sort_keys=True))
        if task.get('readiness') and task['readiness']['errors']:
            lines.append('    readiness: ' + '; '.join(task['readiness']['errors']))
    for row in report.get('question_links', []):
        if row['status'] != 'open':
            continue
        lines.append(f"question {row['id']}: status=open next={row['owner']} "
                     f"blocks={str(row['blocks']).lower()} reason={row.get('routing_reason')}")
        lines.append('  text: ' + json.dumps(row.get('text'), ensure_ascii=False))
        coordinates = {field: row[field] for field in ('origin_execution_id', 'origin_field',
            'source_ref', 'source_kind', 'source_id', 'source_status') if field in row}
        lines.append('  coordinates: ' + json.dumps(coordinates, ensure_ascii=False, sort_keys=True))
        lines.append('  targets: ' + json.dumps({field: row[field] for field in
            ('target_ids', 'unresolved_target_ids')}, ensure_ascii=False, sort_keys=True))
    for row in report.get('repetition_holds', []):
        lines.append(f"repetition hold: {row['lineage']}/{row['lineage_id']} "
                     f"count={row['count']}/{row['limit']} next={row['next_owner']} reason={row['reason']}")
        lines.append('  event_ref: ' + row['event_ref'])
        lines.append('  release_condition: ' + row['release_condition'])
    for name, gate in (report.get('provider_waits') or {}).get('providers', {}).items():
        lines.append(f"provider {name}: {gate['state']} retry={display_time(gate.get('retry_at')) or 'unknown'} "
                     f"generation={gate['generation']}")
    lines.extend(render_dispatch_waits(report))
    lines.extend(render_waiting_actions(report))
    lines.extend(render_waiting_activities(report))
    return "\n".join(lines)


def render_waiting_actions(report):
    lines = []
    for identifier, row in report.get('waiting_actions', {}).items():
        lines.append(f"action {identifier}: {row['role']} wait={row['kind']} next={row['next_owner']} "
                     f"reason={row['reason']}")
        lines.append('  coordinates: ' + json.dumps(row['coordinates'], ensure_ascii=False, sort_keys=True))
    return lines


def render_waiting_activities(report):
    lines = []
    for identifier, row in report.get('waiting_activities', {}).items():
        lines.append(f"activity {identifier}: {row['activity_kind']} wait={row['kind']} next={row['next_owner']} "
                     f"reason={row['reason']}")
        lines.append('  coordinates: ' + json.dumps(row['coordinates'], ensure_ascii=False, sort_keys=True))
        lines.append('  condition: ' + json.dumps(row['condition'], ensure_ascii=False, sort_keys=True))
    return lines


def render_dispatch_waits(report):
    task_ids = {task['id'] for task in report.get('tasks', [])}
    return [f"action {row['action_id']}: {row['role']} wait={row['wait']['kind']} "
            f"constraint={row['wait'].get('constraint_id') or row['wait'].get('provider') or 'none'} "
            f"next={row['wait'].get('next_owner') or 'none'} "
            f"reason={row['wait'].get('reason') or row['wait']['kind']}"
            for row in report.get('dispatch_waits', []) if row.get('target') not in task_ids]


def timeline(repository: Path, instance_id: str, *, snapshot=None, timezone_name="Asia/Seoul", include_operations=False, backend, clock):
    store = ResearchRepository(repository, instance_id, backend=backend, clock=clock)
    head, instance, runtime = store.load(snapshot)
    zone = _zone(timezone_name)
    rows = []
    for execution in runtime.get("executions", {}).values():
        action = execution.get("action", {})
        created, started, ended = (execution.get(key) for key in ("created_at", "started_at", "ended_at"))
        rows.append({"unit": "internal_execution", "id": execution["id"], "snapshot": head,
            "input_snapshot": execution.get("input_snapshot"), "action_id": action.get("id"), "lineage_id": action.get("lineage_id"),
            "continuation_of": execution.get("continuation_of") or action.get("continuation_of"),
            "role": execution.get("role"), "target": action.get("target"),
            "assigned_model": execution.get("model"), "reported_models": execution.get("reported_models"),
            "created_at_utc": created, "started_at_utc": started, "ended_at_utc": ended,
            "created_at_local": _display(created, zone), "started_at_local": _display(started, zone), "ended_at_local": _display(ended, zone),
            "effective_deadline_at": execution.get("execution_window", {}).get("effective_deadline_at"),
            "status": execution.get("status"), "outcome": execution.get("outcome"),
            "failure_kind": execution.get("error_kind"), "error": execution.get("error"),
            "currentness_changes": execution.get("currentness_changes"),
            "output_files": execution.get("output_files", []), "artifact_bundle": execution.get("artifact_bundle"),
            "usage": execution.get("usage"), "usage_segments": execution.get("usage_segments"),
            "model_usage_reported": execution.get("model_usage_reported"), "usage_scope": execution.get("usage_scope"),
            "next_actions": [a for a in runtime.get("queue", [])
                if a.get("continuation_of") == execution["id"] or any(
                    a.get(key, {}).get("execution_id") == execution["id"] for key in ("repair", "refresh", "recovery"))],
            "evidence_source": {"kind": "research_snapshot", "snapshot": head}})
    if include_operations:
        from .trace_report import phase_rows
        for row in phase_rows(Path(instance['workspace']) / 'operations', clock=clock):
            row['snapshot'] = None
            row['created_at_local'] = _display(row['created_at_utc'], zone)
            row['ended_at_local'] = _display(row['ended_at_utc'], zone)
            rows.append(row)
    rows.sort(key=lambda row: (row.get("created_at_utc") or row.get("started_at_utc") or row.get("ended_at_utc") or "", row["id"]))
    return {"snapshot": head, "timezone": timezone_name, "rows": rows,
            "counts_by_unit": {unit: sum(row["unit"] == unit for row in rows) for unit in sorted({row["unit"] for row in rows})},
            "observation": "Local operator evidence is separately observed; unknown historical timestamps are null."}


def timeline_csv(value):
    fields = list(dict.fromkeys(["unit", "id", "snapshot", *(key for row in value["rows"] for key in row)]))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in value["rows"]:
        writer.writerow({key: json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else item
                         for key, item in row.items()})
    return output.getvalue()
