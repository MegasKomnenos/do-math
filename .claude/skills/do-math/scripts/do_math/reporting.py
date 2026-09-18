"""Projections of research snapshots and separately observed local evidence."""
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .provider_wait import timestamp
from .repository import ResearchRepository


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
    seconds = timestamp(value)
    return datetime.fromtimestamp(seconds, timezone.utc).astimezone(zone).isoformat() if seconds is not None else None


def display_time(value, timezone_name='Asia/Seoul'):
    return _display(value, _zone(timezone_name))


def task_status(instance, runtime):
    from . import planning, questions
    rows = []
    live = [e for e in runtime.get("executions", {}).values() if e.get("status") != "ended"]
    for identifier, task in runtime.get("tasks", {}).items():
        queued = [action for action in runtime.get("queue", []) if action.get("target") == identifier]
        executions = [e for e in live if e.get("action", {}).get("target") == identifier]
        running_ids = {e.get("action", {}).get("id") for e in executions}
        obligations = [aid for aid, entry in runtime.get("waiting_actions", {}).items()
                       if entry.get("action", {}).get("target") == identifier or identifier in entry.get("revision_targets", {})
                       or identifier in entry.get("delegated_targets", {}).values()]
        waiting = []
        for action in queued:
            if action.get('id') in running_ids:
                continue
            waiting.extend(questions.user_waits(action, instance, runtime))
            waiting.extend(planning.revision_waits(action, instance, runtime))
            if action.get('dispatch_wait', {}).get('kind') in {'capacity', 'provider_limit'}:
                waiting.append(action['dispatch_wait'])
        readiness = None if task.get('status') in planning.TERMINAL_TASK_STATUSES else runtime.get('task_readiness', {}).get(identifier)
        if not executions and task.get('status') not in planning.TERMINAL_TASK_STATUSES:
            readiness = planning.task_ready({**task, 'status': 'ready'}, instance, runtime, include_scheduling_waits=False)
            if readiness['state'] != 'ready':
                waiting.append({'kind': 'contract_review' if 'current revision lacks approved contract review' in readiness['errors'] else 'required_input',
                                'errors': readiness['errors']})
        waiting = list({json.dumps(row, sort_keys=True): row for row in waiting}.values())
        next_owner = ('user' if any(row.get('kind') == 'user_decision' for row in waiting) else
                      'task_contract_review' if any(row.get('kind') == 'contract_review' for row in waiting) else
                      queued[0]['role'] if queued else None)
        rows.append({"id": identifier, "title": task["title"], "status": task["status"], "revision": task.get("revision"),
                     "selected_actions": [a.get("id") for a in queued if a.get("id") not in running_ids],
                     "active_execution_ids": [e["id"] for e in executions],
                     "last_accepted_result": task.get("results", [])[-1].get("execution_id") if task.get("results") else None,
                     "unresolved_action_ids": obligations, "waits": waiting,
                     "readiness": readiness, "next_owner": next_owner,
                     "next_observation_at": next((row.get("retry_at") for row in waiting if row.get("retry_at")), None)})
    return rows


def timeline(repository: Path, instance_id: str, *, snapshot=None, timezone_name="Asia/Seoul", include_operator=False):
    store = ResearchRepository(repository, instance_id)
    head, instance, runtime = store.load(snapshot)
    zone = _zone(timezone_name)
    rows = []
    for execution in runtime.get("executions", {}).values():
        action = execution.get("action", {})
        created, started, ended = (execution.get(key) for key in ("created_at", "started_at", "ended_at"))
        rows.append({"unit": "internal_execution", "id": execution["id"], "snapshot": head,
            "input_snapshot": execution.get("input_snapshot"), "action_id": action.get("id"), "lineage_id": action.get("lineage_id"),
            "role": execution.get("role"), "target": action.get("target"), "budget_kind": execution.get("budget_kind"),
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
            "next_actions": [a for a in runtime.get("queue", []) if any(a.get(key, {}).get("execution_id") == execution["id"] for key in ("repair", "refresh", "recovery"))],
            "evidence_source": {"kind": "research_snapshot", "snapshot": head}})
    if include_operator:
        for path in sorted((Path(instance["workspace"]) / "operator/runs").glob("*/result.json")):
            raw = path.read_bytes()
            report = json.loads(raw)
            result = report.get("result") or {}
            rows.append({"unit": "independent_operator_invocation", "id": path.parent.name, "snapshot": None,
                "role": "independent_operator", "ended_at_utc": report.get("ended_at"),
                "ended_at_local": _display(report.get("ended_at"), zone), "outcome": report.get("outcome"),
                "assigned_model": result.get("assigned_model") or report.get("model_selection", {}).get("model"),
                "reported_models": result.get("reported_models"), "usage": result.get("usage"),
                "usage_segments": result.get("usage_segments"), "model_usage_reported": result.get("model_usage_reported"),
                "usage_scope": result.get("usage_scope"), "failure_kind": result.get("error_kind"),
                "evidence_source": {"kind": "local_operator_file", "path": str(path),
                    "sha256": hashlib.sha256(raw).hexdigest(), "observed_at": datetime.now(timezone.utc).isoformat()}})
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
