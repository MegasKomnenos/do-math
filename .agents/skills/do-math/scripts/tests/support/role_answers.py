"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import json
from do_math.contracts import CONTRACT_REVIEW_ITEMS
from do_math.execution_profiles import profile_ref
from do_math.canonical import canonical_json


def read_fixture_context(prompt, workspace):
    """Read the same exact local sources exposed to the scripted role."""
    from do_math.context_store import read_source
    value = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
    def read(reference):
        result = read_source(workspace, reference, limit=max(1, reference['bytes']))
        if result['status'] != 'ok' or result['truncated']:
            raise AssertionError('Supplied context source could not be read exactly: ' + repr(result))
        contents = json.loads(result['bytes'])
        for token in reference.get('json_pointer', '').strip('/').split('/') if reference.get('json_pointer') else []:
            contents = contents[int(token)] if isinstance(contents, list) else contents[token]
        return contents
    for key, entry in list(value.items()):
        if isinstance(entry, dict) and isinstance(entry.get('source_ref'), dict):
            value[key] = read(entry['source_ref'])
    for index, task in enumerate(value.get('tasks', []) if isinstance(value.get('tasks'), list) else []):
        if isinstance(task.get('source_ref'), dict):
            task = value['tasks'][index] = {**task, **read(task['source_ref'])}
        for field in ('results', 'reviews', 'revision_history', 'assessment_history'):
            if task.get(field + '_source'):
                task[field] = read(task[field + '_source'])
    return value


def candidate(title="task", *, formal=False, revises=None, refs=None):
    return {"revises_task_id": revises, "title": title,
        "question": "Can the stated natural-number identity be established?",
        "scope": {"included": ["Natural numbers and addition of zero"], "excluded": ["Other domains"]},
        "expected": {"outputs": ["An argument or an explicit remaining obstacle"],
                     "research_change": "Resolve the stated zero-addition identity"},
        "progress_criteria": [{"id": "PC-argument", "claim": "Identify the argument and domain", "evidence_required": []}],
        "completion_obligations": [{"id": "OB-argument", "claim": "Report the exact argument and its domain",
                                     "judges": ["research_plan"], "evidence_required": []}],
        "inputs": list(refs or []), "reuse": list(refs or []), "dependencies": [],
        "profile_refs": [], "authority_refs": [], "basis_refs": [],
        "work_class": "formal" if formal else "nonformal"}


def bind_candidates(output, context):
    """Select only work profiles and current grants actually supplied to the author."""
    current = context.get("role_profile_refs", {}).get("research_work")
    for row in output.get("candidates", []):
        row["profile_refs"] = [profile_ref(p) for p in context["execution_profiles"]
                               if p["role"] == "research_work"
                               and (current is None or profile_ref(p) in current)]
        row["authority_refs"] = [g["id"] for g in context["grants"]
                                 if g["status"] == "active" and "research_work" in g.get("roles", [])]


def review_items(evidence_refs, *, decision="approved", next_owner="research_plan", findings=()):
    """A contract review output that reviews every product contract item alike."""
    return {"item_reviews": [{"item_id": item, "decision": decision,
        "evidence_refs": list(evidence_refs), "findings": list(findings),
        "missing_inputs": ["Contract clarification"] if decision == "unresolved" else [],
        "next_owner": next_owner} for item in CONTRACT_REVIEW_ITEMS]}


def contract_review(context, *, decision="approved", findings=()):
    task = context["task"]
    if not task.get("completion_obligations") or not task.get("scope"):
        raise AssertionError("The review fixture requires the actual structured contract")
    return review_items([task["id"]], decision=decision, next_owner="research_preparation", findings=findings)


def scope_response(context):
    review = context["role_review"]
    policy = review["review_policy"]
    perspectives = list(policy["required_perspectives"])
    for value in ("Statement and proof", "Explanation and domain"):
        if len(perspectives) < policy["minimum_initial_slots"]:
            perspectives.append(value)
    if len(perspectives) < policy["minimum_initial_slots"]:
        raise AssertionError("The explicit fixture only defines two independent perspectives")
    return {"proposal_digest": review["proposal_digest"], "scope_complete": True,
        "scope_assessment": {"assessment_id": "fixture-full-scope", "policy_id": policy["id"],
            "required_perspectives": list(policy["required_perspectives"]),
            "initial_slots": [{"id": "initial-" + str(i), "perspective": perspective,
                               "required_source_refs": ["proposal"]} for i, perspective in enumerate(perspectives)],
            "selected_profile_ref": profile_ref(context["execution_profile"]),
            "activity_execution_limit": policy["activity_execution_limit"],
            "overflow_disposition": policy["overflow_disposition"]}}


def disposition(task_id, *, kind="selected"):
    return {"task_id": task_id, "kind": kind, "reason": "Select the current independently approved contract",
        "uncertainty": "Completion of the contracted argument remains to be tested.",
        "parallel_task_ids": [], "expected_research_change": "Obtain the contracted argument",
        "revisit": {"event_refs": [], "at": None}, "missing_inputs": [], "next_owner": "research_work"}


def planning_model_assessments(output, context):
    tasks = {task['id']: task for task in context.get('tasks', [])}
    selected = [row['task_id'] for row in output.get('dispositions', []) if row.get('kind') == 'selected']
    assessments = []
    for task_id in selected:
        task = tasks.get(task_id)
        prior = task.get('model_assessment') if task else None
        if not prior:
            raise AssertionError('The planning fixture cannot assess a selected task without its supplied model assessment')
        assessments.append({'task_id': task_id, 'difficulty': prior['difficulty'],
            'importance': prior['importance'],
            'reason': 'The planner explicitly re-assesses the supplied bounded contract'})
    return assessments


def assessment(task):
    reports = task.get("results", [])
    if not reports or not all(row.get("report") for row in reports):
        raise AssertionError("Completion fixture requires a supplied nonempty report")
    return {"task_id": task["id"], "decision": "completed", "reason": "The supplied report states the argument and domain",
        "item_dispositions": [{"obligation_id": row["id"], "kind": "fulfilled",
                               "evidence_refs": [r["execution_id"] for r in reports]}
                              for row in task["completion_obligations"]], "unresolved": []}


def assessment_awaiting_required_evidence(task):
    """A fixture whose report exists but every obligation still lacks its named evidence."""
    if not task['completion_obligations'] or any(not row['evidence_required'] for row in task['completion_obligations']):
        raise AssertionError('Missing-evidence fixture requires named evidence for every obligation')
    return {'task_id': task['id'], 'decision': 'incomplete',
        'reason': 'The report is present; the required evidence is still missing.',
        'item_dispositions': [], 'unresolved': [{'obligation_id': row['id'],
            'missing_inputs': list(row['evidence_required']), 'next_owner': 'research_work'}
            for row in task['completion_obligations']]}


def intent_response(context):
    if context["action"].get("stage", "interpret") == "interpret":
        source = context["user_request"]
        return {"summary": "Preserve the supplied input verbatim for independent inspection",
            "used_sources": [], "questions": [], "question_details": [],
            "import_units": [{"unit_id": "IU-original", "source_range": {"start": 0, "end": len(source["text"])},
                "interpretation": source["text"], "owner_kind": "charter",
                "owner_ref": context["governance"]["charter"]["id"],
                "payload": {}, "decision_refs": [], "question_refs": []}]}
    bundle = context["interpretation_to_check"]
    source = bundle["source"]["text"]
    units = bundle["output"]["import_units"]
    if "".join(u["interpretation"] for u in units) != source:
        raise AssertionError("This fixture only approves verbatim, complete interpretation")
    return {"summary": "Independently compare supplied units with the exact original input",
        "used_sources": [], "questions": [], "decision": "approved", "scope_complete": True,
        "bundle_sha256": bundle["sha256"], "unit_ids": [u["unit_id"] for u in units],
        "question_ids": [q["id"] for q in bundle["output"]["question_details"]], "findings": []}


def seal_response(output, context, workspace):
    """Producer declares its real output/extension coordinates as one coupled unit."""
    from do_math.integration import mutation_members
    members = ["output"]
    role = context["action"]["role"]
    if role == 'research_preparation':
        from do_math.model_policy import preparation_only
        if not preparation_only(context['action']) and context.get('observed_at'):
            from datetime import datetime, timedelta
            output.setdefault('regenerate_after', (datetime.fromisoformat(context['observed_at'].replace('Z', '+00:00'))
                                                  + timedelta(hours=1)).isoformat())
    if role in {"research_work", "supplemental_research"} and not context["action"].get("review_cycle_id"):
        members += [f"output/{key}/{i}" for key in ("knowledge", "relations") for i, _ in enumerate(output.get(key, []))]
    path = workspace / "activity-extensions.json"
    extensions = json.loads(path.read_bytes()) if path.exists() else {}
    members += [f"activity-extensions.json/{family}/{i}" for family, rows in extensions.items() for i, _ in enumerate(rows)]
    identifier = "IN-" + hashlib.sha256(canonical_json({"action": context["action"], "output": output,
                                                       "extensions": extensions})).hexdigest()[:24]
    visible = {row["id"]: row for family in ("tasks", "knowledge_catalog")
               for row in context.get(family, []) if row.get("id")}
    mutation_ids = {target for _, _, target, _ in mutation_members(output, extensions)}
    previous_hashes = {}
    for target in mutation_ids:
        record = visible.get(target)
        if record is None or not record.get("content_sha256"):
            raise AssertionError("The fixture cannot revise a record absent from its fixed input: " + str(target))
        previous_hashes[target] = record["content_sha256"]
    output["integration_bundles"] = [{"integration_id": identifier, "members": members,
                                      "impact_set": [], "authority_refs": [],
                                      "previous_hashes": previous_hashes}]
    return output
