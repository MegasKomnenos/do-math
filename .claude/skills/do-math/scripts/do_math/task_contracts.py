"""Feature-5 task obligations, derived readiness, and repeat lineages.

The module is deliberately pure: activity waiting and lifecycle transitions remain
with their owners.  It supplies the task facts those owners must consume.
"""
from __future__ import annotations

from copy import deepcopy
from collections import Counter
from typing import Any


LIFECYCLE_STATES = frozenset({"planned", "active", "waiting", "completed", "closed"})
DISPOSITION_KINDS = frozenset({"fulfilled", "open", "waived", "transferred"})
REPEAT_LINEAGES = ("import_rework", "selection_failure", "exhaustion_empty", "proposal_version", "contract_revision")


def prepared_dependencies(candidate, condition, titles=None):
    """An extension adds prerequisites; omitted fields never erase the contract."""
    names = titles or {}
    return list(dict.fromkeys(names.get(ref, ref) for ref in
        [*candidate.get('dependencies', []), *condition.get('dependencies', [])]))


def _text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


def _distinct_ids(rows: list[dict], name: str) -> None:
    values = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or any(not isinstance(value, str) or not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{name} must have distinct stable IDs")


def contract_obligations(task: dict) -> list[dict]:
    """Return the authoritative completion obligations, never a cached remainder."""
    obligations = task.get("completion_obligations", [])
    if not isinstance(obligations, list):
        raise ValueError("completion_obligations must be a list")
    return obligations


def validate_task_contract(task: dict) -> None:
    if not isinstance(task, dict):
        raise ValueError("task contract must be an object")
    for name in ("id", "question"):
        _text(task.get(name), name)
    if type(task.get('revision')) is not int or task['revision']<1:
        raise ValueError('task revision must be a positive integer')
    if task.get("status", "planned") not in LIFECYCLE_STATES:
        raise ValueError("task status is not a feature-5 lifecycle state")
    scope = task.get("scope")
    if not isinstance(scope, dict) or set(scope) != {"included", "excluded"} or not all(isinstance(scope[key], list) and all(isinstance(x, str) and x.strip() for x in scope[key]) for key in scope):
        raise ValueError("scope requires included and excluded nonempty-text lists")
    expected = task.get("expected")
    if not isinstance(expected, dict) or set(expected) != {"outputs", "research_change"} or not isinstance(expected["outputs"], list):
        raise ValueError("expected requires outputs and research_change")
    _text(expected["research_change"], "expected.research_change")
    if not expected["outputs"] or not all(isinstance(x, str) and x.strip() for x in expected["outputs"]):
        raise ValueError("expected.outputs must be nonempty")
    for name in ("progress_criteria", "completion_obligations"):
        rows = task.get(name)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{name} must be a nonempty list")
        _distinct_ids(rows, name)
        for row in rows:
            _text(row.get("claim"), name + ".claim")
            evidence=row.get('evidence_required',[])
            if not isinstance(evidence,list) or any(not isinstance(v,str) or not v for v in evidence) or len(evidence)!=len(set(evidence)):
                raise ValueError(name + '.evidence_required must contain distinct references')
            descriptions = row.get('evidence_requirements', [])
            if (not isinstance(descriptions, list) or any(not isinstance(v, str) or not v.strip() for v in descriptions)
                    or len(descriptions) != len(set(descriptions))):
                raise ValueError(name + '.evidence_requirements must contain distinct requirement descriptions')
    for row in contract_obligations(task):
        judges = row.get("judges")
        if not isinstance(judges, list) or not judges or not all(isinstance(judge, str) and judge.strip() for judge in judges):
            raise ValueError("each completion obligation needs judges")
    for name in ("inputs", "reuse", "dependencies", "authority_refs", "basis_refs"):
        rows = task.get(name, [])
        if not isinstance(rows, list) or not all(isinstance(value, str) and value for value in rows) or len(rows) != len(set(rows)):
            raise ValueError(name + " must be a distinct reference list")
    profile_refs = task.get('profile_refs', [])
    if not isinstance(profile_refs, list):
        raise ValueError('profile_refs must be a list of sealed references')
    seen = set()
    for ref in profile_refs:
        if (not isinstance(ref, dict) or set(ref) != {'id', 'revision', 'sha256'}
                or not isinstance(ref['id'], str) or not ref['id'].strip()
                or type(ref['revision']) is not int or ref['revision'] < 1
                or not isinstance(ref['sha256'], str) or len(ref['sha256']) != 64
                or any(c not in '0123456789abcdef' for c in ref['sha256'])):
            raise ValueError('profile_refs require exact id, revision and sha256')
        if ref['id'] in seen:
            raise ValueError('profile_refs must identify distinct profiles')
        seen.add(ref['id'])


def _row_by_obligation(assessment: dict) -> dict[str, dict]:
    rows = assessment.get("item_dispositions", [])
    if not isinstance(rows, list):
        raise ValueError("item_dispositions must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("item disposition must be an object")
        identifier = row.get("obligation_id")
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ValueError("item dispositions must identify each obligation at most once")
        if row.get("kind") not in DISPOSITION_KINDS:
            raise ValueError("unknown item disposition")
        if "evidence_refs" not in row:
            raise ValueError("item disposition requires evidence_refs")
        evidence = row["evidence_refs"]
        if not isinstance(evidence, list) or not all(isinstance(value, str) and value for value in evidence) or len(evidence) != len(set(evidence)):
            raise ValueError("item disposition evidence_refs must be distinct references")
        result[identifier] = row
    return result


def validate_item_dispositions(task: dict, assessment: dict, *, require_complete: bool = False) -> None:
    validate_task_contract(task)
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be an object")
    terminal = assessment.get('decision') in {'completed', 'closed'}
    require_complete = require_complete or terminal
    if task.get('status') in {'completed', 'closed'} and assessment.get('decision') != task['status']:
        raise ValueError('terminal task status differs from its assessment decision')
    obligations = {row["id"]: row for row in contract_obligations(task)}
    rows = _row_by_obligation(assessment)
    if set(rows) - set(obligations):
        raise ValueError("item disposition names an unknown obligation")
    unresolved = assessment.get("unresolved", [])
    if not isinstance(unresolved, list):
        raise ValueError("unresolved must be a list")
    unresolved_ids = set()
    for row in unresolved:
        if not isinstance(row, dict) or set(row) != {"obligation_id", "missing_inputs", "next_owner"}:
            raise ValueError("unresolved inspection needs obligation_id, missing_inputs, and next_owner")
        identifier = row["obligation_id"]
        if identifier not in obligations or identifier in unresolved_ids or identifier in rows:
            raise ValueError("unresolved inspection must name one undisposed obligation")
        unresolved_ids.add(identifier)
        if not isinstance(row["missing_inputs"], list) or not row["missing_inputs"] or any(not isinstance(v,str) or not v for v in row['missing_inputs']):
            raise ValueError("unresolved inspection needs missing inputs")
        _text(row["next_owner"], "unresolved.next_owner")
    for identifier, row in rows.items():
        obligation = obligations[identifier]
        required = set(obligation.get("evidence_required", []))
        if row["kind"] == "fulfilled" and not required <= set(row["evidence_refs"]):
            raise ValueError("item disposition lacks required evidence: " + identifier)
        if row["kind"] == "waived":
            if not isinstance(row.get("authority_ref"), str) or not row["authority_ref"]:
                raise ValueError("waived obligation needs authority_ref")
        if row["kind"] == "transferred":
            if not all(isinstance(row.get(key), str) and row[key] for key in ("authority_ref", "target_task_id", "target_obligation_id")):
                raise ValueError("transferred obligation needs authority and target obligation")
    if set(obligations) != set(rows) | unresolved_ids:
        raise ValueError("every obligation requires a disposition or unresolved inspection")
    if require_complete and (set(obligations) - set(rows) or unresolved_ids):
        raise ValueError("unresolved or undisposed completion obligations remain")
    if require_complete and any(row['kind'] == 'open' for row in rows.values()):
        raise ValueError("terminal assessment retains open obligations")
    if assessment.get('decision') == 'completed' and any(row['kind'] == 'transferred' for row in rows.values()):
        raise ValueError('completed assessment retains transferred obligations; use closed for authorized scope termination')
    if assessment.get('decision') == 'closed' and not any(row['kind'] in {'waived', 'transferred'} for row in rows.values()):
        raise ValueError('closure needs an authoritative scope disposition')


def remaining_obligations(task: dict, assessment: dict | None = None) -> list[str]:
    """Compute residual task scope from current obligation dispositions."""
    obligations = {row["id"] for row in contract_obligations(task)}
    if assessment:
        validate_item_dispositions(task, assessment)
    rows = _row_by_obligation(assessment or {})
    closed = {identifier for identifier, row in rows.items() if row["kind"] in {"fulfilled", "waived", "transferred"}}
    return sorted(obligations - closed)


def readiness_for_task(task: dict, instance: dict, runtime: dict, **kwargs) -> dict:
    """Derived task readiness.  No task/status mutation or cache is produced."""
    from .planning import task_ready
    return task_ready(task, instance, runtime, **kwargs)


def returned_task_ids(tasks):
    from .planning import contract_hash
    from .repository import exact_content_hash
    return sorted(identifier for identifier, task in tasks.items()
        if task.get('status') not in {'completed', 'closed'} and task.get('results') and (
            task.get('assessment', {}).get('results_sha256') != exact_content_hash(task['results']) or
            task.get('assessment', {}).get('contract_sha256') != contract_hash(task) or
            task.get('assessment', {}).get('current') is False))


def selected_task_ids(plan):
    return [row['task_id'] for row in plan['dispositions'] if row['kind'] == 'selected']


def validate_plan_dispositions(plan: dict, tasks: dict, ready_ids: list[str]) -> None:
    if 'dispositions' not in plan:
        raise ValueError('plan requires one dispositions array')
    if set(ready_ids)-set(tasks):
        raise ValueError('ready population names an unknown task')
    for field in ('dispositions','task_assessments'):
        rows=plan.get(field,[])
        if not isinstance(rows,list) or any(not isinstance(row,dict) or not isinstance(row.get('task_id'),str) for row in rows):
            raise ValueError(field+' must contain identified task rows')
    supplied = [row['task_id'] for row in plan['dispositions']]
    counts = Counter(supplied)
    if len(supplied) != len(counts) or set(counts) != set(ready_ids):
        raise ValueError("plan must dispose every derived-ready task exactly once: "
            f"missing={sorted(set(ready_ids) - set(counts))}; "
            f"unexpected={sorted(set(counts) - set(ready_ids))}; "
            f"duplicate={sorted(identifier for identifier, count in counts.items() if count > 1)}")
    for row in plan['dispositions']:
        if row.get('kind') not in {'selected', 'not_selected', 'not_assessable'}:
            raise ValueError('unknown candidate disposition')
        for key in ('reason', 'next_owner'):
            _text(row.get(key), key)
        if row['kind'] == 'selected':
            _text(row.get('expected_research_change'), 'expected_research_change')
        else:
            revisit = row.get('revisit', {})
            if not revisit.get('event_refs') and not revisit.get('at'):
                raise ValueError('nonselection requires a reobservation condition')
            if revisit.get('at'):
                from .planning import _utc
                _utc(revisit['at'])
        if row['kind'] == 'not_assessable' and not row.get('missing_inputs'):
            raise ValueError('not_assessable requires missing inputs')
        parallel = row.get('parallel_task_ids', [])
        if len(parallel) != len(set(parallel)) or set(parallel) - set(tasks) or row['task_id'] in parallel:
            raise ValueError('parallel references must identify distinct other tasks')
    assessments = plan.get('task_assessments', [])
    assessed = [row['task_id'] for row in assessments]
    if len(assessed) != len(set(assessed)) or set(assessed) != set(returned_task_ids(tasks)):
        raise ValueError('plan must assess every returned task exactly once')
    if set(selected_task_ids(plan)) & set(assessed):
        raise ValueError('returned tasks require disposition before a later selection')
    for assessment in plan.get("task_assessments", []):
        task = tasks.get(assessment.get("task_id"))
        if task is None:
            raise ValueError("assessment names an unknown task")
        if assessment.get('decision') not in {'completed', 'incomplete', 'closed'}:
            raise ValueError('unknown completion decision')
        validate_item_dispositions(task, assessment, require_complete=assessment.get("decision") in {"completed", "closed"})


def repetition_lineages(runtime: dict, task_id: str | None = None, *,
                        include_events: bool = True) -> dict[str, dict]:
    """Count independent histories without turning a count into an authority decision."""
    rows = runtime.get("history", [])
    result = {name: {"count": 0, "owner": "ai", "events": []} for name in REPEAT_LINEAGES}
    baselines={}
    for row in rows:
        if not isinstance(row, dict) or row.get('kind') != 'task_repetition' or row.get('lineage') not in result:
            continue
        if task_id is not None and row['lineage'] == 'contract_revision' and row['lineage_id'] != task_id:
            continue
        name = row['lineage']
        counts = result[name].setdefault('by_lineage', {})
        key = row['lineage_id']
        if row['outcome']=='continued':baselines[name,key]=row.get('baseline_revision',0)
        if row['outcome'] in {'accepted', 'contracts_preserved', 'continued'}:
            counts[key] = 0
        elif 'version' in row:
            counts[key] = row['version']-baselines.get((name,key),0)
        elif row['outcome'] not in {'premises_changed', 'capacity_wait', 'input_overflow', 'waiting', 'transport_failure','unclassified_failure'}:
            counts[key] = counts.get(key, 0) + 1
        result[name]["count"] = sum(counts.values())
        if include_events:
            result[name]["events"].append(deepcopy(row))
        if row.get("owner") == "user":
            result[name]["owner"] = "user"
    return result
