"""Independent obligation assessments, scoped transfers, and unperformed withdrawal."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from .planning import contract_hash
from .repository import exact_content_hash


_WITHDRAWABLE_STATES = {"planned", "waiting", "active"}


def result_ids(task: dict) -> set[str]:
    """IDs of the returned results a completion assessment of this task may cite."""
    return {row.get('id', row.get('execution_id')) for row in task.get('results', [])} - {None}


def require_evidence_refs(refs, admissible) -> None:
    """Completion evidence names a supplied record or a returned result, not a path or event.

    The producer passes its input's supplied_record_ids with the task's result IDs;
    the receiver passes current record IDs with the same result IDs.
    """
    invalid = sorted(set(refs) - set(admissible))
    if invalid:
        raise ValueError('completion evidence requires a supplied record ID; read the file and cite its producing '
                         'execution or source record; invalid_evidence_refs=' + repr(invalid))


def _task_execution(execution: dict, task_id: str) -> bool:
    return isinstance(execution, dict) and execution.get("action", {}).get("target") == task_id


def _validate(task: dict, snapshot_task: dict, runtime: dict, task_id: str, instance=None, *, actor_execution_id) -> None:
    if not isinstance(snapshot_task, dict) or contract_hash(task) != contract_hash(snapshot_task):
        raise ValueError("task contract changed since the execution input snapshot: " + task_id)
    validate_withdrawal_scope(task, snapshot_task)
    if task.get('results'):
        if not assessment_current(task, instance or {}, runtime):
            raise ValueError('performed obligations need current item dispositions for all returned work')
    producer_id = task.get("producer_execution")
    producer = runtime.get("executions", {}).get(producer_id)
    if not isinstance(producer_id, str) or not isinstance(producer, dict) or producer.get("role") != "research_preparation":
        raise ValueError("task is not attributable to a research preparation execution: " + task_id)
    for identifier, execution in runtime.get("executions", {}).items():
        if identifier == actor_execution_id and execution.get('role') in {'research_preparation', 'research_plan'}:
            continue
        if not _task_execution(execution, task_id):
            continue
        if execution.get("status") != "ended":
            raise ValueError("task has a live execution: " + task_id)


def validate_withdrawal_scope(task, snapshot_task, *, proposed_assessment=None):
    """Shared producer/receiver scope check, before live provenance checks."""
    from .task_contracts import validate_item_dispositions
    if task.get('status') not in _WITHDRAWABLE_STATES:
        raise ValueError('withdrawal requires an unfinished task')
    if proposed_assessment is not None and proposed_assessment.get('decision') != 'incomplete':
        raise ValueError('withdrawal cannot follow a terminal task assessment')
    if task.get('transferred_obligations') or task.get('user_required') or task.get('academic_requirement_id'):
        raise ValueError('protected obligations require authoritative item dispositions')
    if not task.get('results'):
        return
    assessment = proposed_assessment if proposed_assessment is not None else task.get('assessment', {})
    if (exact_content_hash(task['results']) != exact_content_hash(snapshot_task.get('results', []))
            or assessment.get('decision') != 'incomplete' or assessment.get('current') is False):
        raise ValueError('performed obligations need current item dispositions for all returned work')
    if proposed_assessment is None and (assessment.get('contract_sha256') != contract_hash(task)
            or assessment.get('results_sha256') != exact_content_hash(task['results'])):
        raise ValueError('item dispositions do not cover the current contract and results')
    validate_item_dispositions(task, assessment)


def apply_task_dispositions(instance: dict, runtime: dict, dispositions: list[dict], *,
                            execution_id: str, input_tasks: dict) -> tuple[dict, dict]:
    """Apply withdrawal requests after snapshot and provenance validation.

    The caller owns role authorization.  This function deliberately cannot alter
    goals, policies, grants, academic requirements, or user task-scope records.
    """
    if not isinstance(execution_id, str) or not execution_id:
        raise ValueError("task dispositions need an execution ID")
    if not isinstance(dispositions, list) or not isinstance(input_tasks, dict):
        raise ValueError("task dispositions and input tasks must be collections")
    # The sealed extension schema and the submission check fixed shape and distinct targets.
    requested = [(item["task_id"], item["reason"]) for item in dispositions]

    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    tasks = new_runtime.get("tasks", {})
    for task_id, _ in requested:
        task = tasks.get(task_id)
        if not isinstance(task, dict):
            raise ValueError("unknown task: " + task_id)
        _validate(task, input_tasks.get(task_id), new_runtime, task_id, new_instance,
                  actor_execution_id=execution_id)

    for task_id, reason in requested:
        task = tasks[task_id]
        removed_queue = [deepcopy(action) for action in new_runtime.get("queue", [])
                         if isinstance(action, dict) and action.get("target") == task_id]
        new_runtime["queue"] = [action for action in new_runtime.get("queue", [])
                                if not isinstance(action, dict) or action.get("target") != task_id]
        waiting_actions = new_runtime.get("waiting_actions", {})
        removed_waiting = []
        for action_id, entry in list(waiting_actions.items()):
            action = entry.get("action", {}) if isinstance(entry, dict) else {}
            if isinstance(action, dict) and action.get("target") == task_id:
                removed_waiting.append({"id": action_id, "entry": deepcopy(entry)})
                waiting_actions.pop(action_id)
        previous_hash = contract_hash(task)
        from .task_contracts import remaining_obligations
        assessment = task.get('assessment')
        remaining = remaining_obligations(task, assessment)
        if assessment:
            task.setdefault('assessment_history', []).append(deepcopy(assessment))
            del task['assessment']
        task["scope_disposition"] = {
            "kind": "withdraw", "actor_execution": execution_id, "reason": reason,
            "previous_revision": task.get("revision"), "previous_contract_sha256": previous_hash,
            "at": datetime.now(timezone.utc).isoformat(), "cancelled_queue_actions": removed_queue,
            "cancelled_waiting_actions": removed_waiting,
            'results_sha256': exact_content_hash(task.get('results', [])),
            'assessment_sha256': exact_content_hash(assessment) if assessment else None,
            'remaining_obligation_ids': remaining,
        }
        task.pop('waiting', None)
        task["status"] = "closed"
    return new_instance, new_runtime


def validate_withdrawal_record(task):
    """A closure preserves the actual incomplete assessment; it never fulfils it."""
    from .task_contracts import remaining_obligations
    record = task['scope_disposition']
    if task['status'] != 'closed' or record['previous_contract_sha256'] != contract_hash(task):
        raise ValueError('withdrawal contract or status differs')
    if record.get('results_sha256') != exact_content_hash(task.get('results', [])):
        raise ValueError('withdrawal results changed')
    assessment = next((a for a in task.get('assessment_history', [])
                       if exact_content_hash(a) == record.get('assessment_sha256')), None)
    if task.get('results') and (not assessment or assessment.get('decision') != 'incomplete'):
        raise ValueError('withdrawal lacks its preserved incomplete assessment')
    if record.get('remaining_obligation_ids') != remaining_obligations(
            {**task, 'status': 'waiting'}, assessment):
        raise ValueError('withdrawal residual scope differs')


def decision_is_current(decision, instance, runtime, *, evaluation_context=None):
    """Check the preserved user source, scope edition, and effect of a decision."""
    from .file_io import parse_utc
    from .input_basis import sources_current, aliases
    if decision.get('actor') != 'user' or not decision.get('source_ref') or not isinstance(decision.get('change'), dict):
        return False
    if (decision.get('revoked') or decision.get('status', 'active') != 'active'
            or decision.get('lifecycle', 'active') != 'active' or decision.get('current') is False):
        return False
    context = evaluation_context or {}
    now = parse_utc(context['now']) if context.get('now') else datetime.now(timezone.utc)
    if decision.get('expires_at') and parse_utc(decision['expires_at']) <= now:
        return False
    if decision.get('valid_from') and parse_utc(decision['valid_from']) > now:
        return False
    if decision.get('source_basis') and not sources_current(decision['source_basis'], instance):
        return False
    preserved = instance.get('governance_sources',{}).get(decision['source_ref'])
    source = next((s for s in instance.get('sources', []) if decision['source_ref'] in aliases(s)), None)
    if preserved:
        from .governance import validate_source
        try:
            validate_source(preserved)
        except ValueError:
            return False
        if decision.get('source_sha256') and decision['source_sha256'] != preserved['sha256']:
            return False
    elif source:
        if not decision.get('source_sha256') or decision['source_sha256'] != source.get('sha256'):
            return False
    elif callable(context.get('validate_decision_source')):
        if context['validate_decision_source'](decision) is not True:
            return False
    else:
        return False
    if any(decision.get(key) is not None for key in ('goal_revision', 'policy_revision')):
        from .planning import governance_revisions
        editions = governance_revisions(instance)
        if any(decision.get(key) is not None and decision[key] != value for key, value in editions.items()):
            return False
    return True


def validate_disposition_authority(task, row, instance, runtime, *, evaluation_context=None):
    """A local execution grant does not authorize changing a research obligation."""
    from .planning import contract_hash
    authority = instance.get('decisions', {}).get(row.get('authority_ref'))
    if not authority or not decision_is_current(authority, instance, runtime, evaluation_context=evaluation_context):
        raise ValueError('scope disposition requires a current source-bound user decision')
    change = authority['change']
    expected = 'transfer' if row['kind'] == 'transferred' else 'waive'
    if change.get('kind') != 'task_scope' or change.get('task_id') != task['id'] or change.get('disposition') != expected:
        raise ValueError('scope authority does not cover this task and disposition')
    if change.get('contract_sha256') != contract_hash(task) or change.get('revision') != task['revision']:
        raise ValueError('scope authority applies to a different contract edition')
    if row['obligation_id'] not in change.get('obligation_ids', []):
        raise ValueError('scope authority does not cover this obligation')
    if expected == 'transfer' and change.get('target_task_id') != row.get('target_task_id'):
        raise ValueError('transfer authority names a different recipient')
    return authority


def assessment_basis(task, assessment, instance, runtime):
    from .planning import record_index,task_reference_basis,condition_refs
    from .relation_refs import relation_references, relation_evidence_references
    records=record_index(instance,runtime)
    refs={ref for row in assessment.get('item_dispositions',[]) for ref in row.get('evidence_refs',[])}
    refs.update(row['authority_ref'] for row in assessment.get('item_dispositions',[]) if row.get('authority_ref'))
    refs.update(ref for row in assessment.get('unresolved',[]) for ref in row['missing_inputs'])
    direct = set(refs)
    strict = {ref for ref in direct if records.get(ref, (None,))[0] in
              {'formal-result', 'identity-assessment', 'assessment-use', 'goal-judgment'}}
    pending = list(refs)
    visited = set()
    while pending:
        ref = pending.pop()
        mode = (ref, ref in strict)
        if mode in visited:
            continue
        visited.add(mode)
        found = records.get(ref)
        if not found:
            continue
        family, record = found
        linked = {item for key in ('inputs', 'reuse', 'dependencies', 'basis_refs', 'authority_refs')
                  if isinstance(record.get(key), list) for item in record[key] if isinstance(item, str)}
        fields = ('formal_result_id', 'exposition_id', 'kind_definition_id', 'source_ref', 'assessment_id')
        if family != 'formal-result' or ref in strict:
            fields += ('trust_environment_id',)
        linked.update(record[key] for key in fields if isinstance(record.get(key), str))
        linked.update(row.get('id') or row['name'] for row in record.get('source_basis', [])
                      if isinstance(row.get('id') or row.get('name'), str))
        linked.update(row['id'] for row in record.get('profile_refs', []) if isinstance(row.get('id'), str))
        linked.update(condition_refs(record.get('occurrence_condition')))
        linked.update(relation_references(record.get('relation_claim') or {}))
        if family == 'relation':
            linked.update(relation_references(record))
            # Explicit expert evidence has the same force here as a direct
            # assessment citation; structural KN endpoints still bind content.
            judgments = {item for item in relation_evidence_references(record)
                if records.get(item, (None,))[0] in
                {'formal-result', 'identity-assessment', 'assessment-use', 'goal-judgment'}}
            pending.extend(judgments - strict)
            strict.update(judgments)
        for review in record.get('reviews', []):
            linked.update(row['id'] for row in review.get('decision_basis', {}).get('records', []))
        if family == 'identity-assessment':
            linked.update(row['id'] for row in instance.get('assessment_uses', {}).values()
                          if row.get('assessment_id') == ref)
        if family == 'knowledge' and ref in strict and record.get('formal_result_id'):
            linked.update(row['id'] for row in instance.get('identity_assessments', {}).values()
                if row.get('formal_result_id') == record['formal_result_id']
                and row.get('exposition_id') == record.get('exposition_id'))
        pending.extend(linked - refs)
        if ref in strict:
            pending.extend(linked - strict)
            strict.update(linked)
        refs.update(linked)
    refs.discard(task['id'])
    from .input_basis import aliases
    result={}
    for ref in sorted(refs):
        found=records.get(ref)
        if found is None:
            source = next((source for source in instance.get('sources', [])
                           if ref in aliases(source)), None)
            if source is not None:
                found = ('source', source)
        value=found[1] if found else next((r for r in task.get('results',[]) if ref in {r.get('id'),r.get('execution_id')}),None)
        if found and found[0]=='task':value=task_reference_basis(value)
        elif found and found[0] == 'knowledge':
            value = {key: item for key, item in value.items()
                     if key not in {'review_cycle_id', 'previous_review_cycle_id'}}
        elif found and found[0] == 'formal-result' and ref not in strict:
            # A KN citation binds submitted mathematics, not a judgment that
            # did not exist yet. Explicit FR citations still bind the full record.
            value = {key: value[key] for key in ('id', 'family', 'lean_code', 'declaration_names',
                     'dependencies', 'producer_execution', 'origin_refs') if key in value}
        result[ref]=exact_content_hash(value) if value is not None else None
    return result


def assessment_current(task,instance,runtime,*,evaluation_context=None):
    assessment=task.get('assessment',{})
    if (not assessment or assessment.get('current') is False or assessment.get('contract_sha256')!=contract_hash(task)
        or assessment.get('results_sha256')!=exact_content_hash(task.get('results',[]))
        or assessment.get('basis')!=assessment_basis(task,assessment,instance,runtime)):
        return False
    from .task_contracts import validate_item_dispositions
    try:
        validate_item_dispositions(task, assessment, require_complete=assessment.get('decision') in {'completed', 'closed'})
    except ValueError:
        return False
    for row in assessment.get('item_dispositions',[]):
        if row['kind'] == 'fulfilled':
            obligation = next(o for o in task['completion_obligations'] if o['id'] == row['obligation_id'])
            actor = runtime.get('executions', {}).get(assessment.get('execution_id'), {})
            if actor.get('role') not in obligation['judges'] and assessment.get('execution_id') not in obligation['judges']:
                support = assessment.get('specialist_support', {}).get(row['obligation_id'])
                if not support or designated_judgment(task, obligation, {**row, 'evidence_refs': [support]}, instance, runtime) != support:
                    return False
        if row['kind'] in {'waived','transferred'}:
            try:validate_disposition_authority(task,row,instance,runtime,evaluation_context=evaluation_context)
            except ValueError:return False
        if row['kind']=='transferred':
            target=runtime.get('tasks',{}).get(row['target_task_id'],{})
            original=next(o for o in task['completion_obligations'] if o['id']==row['obligation_id'])
            expected={**original,'id':row['target_obligation_id']}
            if expected not in target.get('completion_obligations',[]):return False
    return True


def refresh_task_assessments(instance,runtime,*,evaluation_context=None):
    changed=[]
    live = {row.get('action', {}).get('target') for row in runtime.get('executions', {}).values()
            if row.get('status') != 'ended' and row.get('role') in {'research_work', 'supplemental_research'}}
    for task in runtime.get('tasks',{}).values():
        # Keep the recorded basis until work ends, so the next refresh still
        # observes this change and requests assessment of the complete results.
        if task['id'] in live:
            continue
        if task.get('assessment') and task['assessment'].get('current') is not False and not assessment_current(task,instance,runtime,evaluation_context=evaluation_context):
            assessment = task['assessment']
            previous, current = assessment.get('basis', {}), assessment_basis(task, assessment, instance, runtime)
            refs = sorted(ref for ref in previous.keys() | current.keys() if previous.get(ref) != current.get(ref))
            assessment.update(current=False, invalidated_reason=(
                'Completion evidence changed: ' + ', '.join(refs) if refs else
                'Completion contract, results, scope authority or designated judgment is no longer current'))
            changed.append(task['id'])
    return changed


def designated_judgment(task, obligation, disposition, instance, runtime):
    """Resolve existing specialist judgments; the planner still checks semantic coverage.

    A judgment must concern a result of this task, be currently usable, and be
    explicitly cited. A role name, peer cycle ID, or prose claim is not a receipt.
    """
    from .knowledge_records import formal_usable, usable_links
    from .knowledge import validate_basis
    produced = {row.get('execution_id') for row in task.get('results', [])} - {None}
    records = [row for row in instance.get('knowledge', {}).values()
               if row.get('task_id') == task['id'] or row.get('producer_execution') in produced]
    judges = set(obligation['judges'])
    cited = set(disposition['evidence_refs'])
    for record in records:
        fid = record.get('formal_result_id')
        formal = instance.get('formal_results', {}).get(fid, {})
        if ('formal_check' in judges and fid in cited and formal_usable(instance, formal)
                and record.get('lifecycle') == 'active'):
            return fid
        if 'identity_review' in judges:
            for link in usable_links(instance, record['id']):
                if link['assessment_id'] in cited:
                    return link['assessment_id']
    if 'goal_audit' in judges:
        from .planning import governance_revisions
        from .input_basis import sources_current
        editions = governance_revisions(instance)
        owned = {row['id'] for row in records}
        for judgment in instance.get('goal_judgments', []):
            if (judgment.get('id') in cited and judgment.get('decision') == 'satisfied'
                    and judgment.get('scope_complete') is True and judgment.get('current') is True
                    and all(judgment.get(key) == value for key, value in editions.items())
                    and sources_current(judgment.get('source_basis', []), instance)
                    and owned.intersection(judgment.get('dependencies', []))
                    and validate_basis(judgment.get('record_basis', []), instance, runtime)['valid']
                    and all(usable_links(instance, kid) for kid in judgment.get('dependencies', [])
                            if kid in instance.get('knowledge', {}))):
                return judgment['id']
    return None


def apply_task_assessments(instance, runtime, assessments, *, execution_id, input_tasks, reference_tasks=None, evaluation_context=None):
    """Apply the whole assessment set on copies, including recipient obligations."""
    from .task_contracts import validate_item_dispositions, contract_obligations, judge_coverage_errors
    from .planning import record_index
    new_instance, new_runtime = deepcopy(instance), deepcopy(runtime)
    reference_tasks = input_tasks if reference_tasks is None else reference_tasks
    actor = new_runtime.get('executions', {}).get(execution_id)
    if not actor or actor.get('role') not in {'research_plan', 'operational_review'}:
        raise ValueError('completion requires a designated independent assessor execution')
    ids = [a['task_id'] for a in assessments]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate task assessment')
    tasks = new_runtime['tasks']
    transfers = []
    records = record_index(new_instance, new_runtime)
    families = {identifier: family for identifier, (family, _) in records.items()}
    for assessment in assessments:
        if assessment.get('decision') not in {'completed','closed','incomplete'}:
            raise ValueError('unknown completion decision')
        task = tasks[assessment['task_id']]
        old = input_tasks.get(task['id'])
        if not old or contract_hash(old) != contract_hash(task) or exact_content_hash(old.get('results', [])) != exact_content_hash(task.get('results', [])):
            raise ValueError('assessment contract or returned work changed')
        if task['status'] in {'completed', 'closed'} or not task.get('results'):
            raise ValueError('assessment requires unfinished returned work')
        if execution_id in {task.get('producer_execution'), *task.get('author_execution_ids', [])}:
            raise ValueError('contract author cannot assess its own obligations')
        if any(e.get('status') != 'ended' and e.get('action', {}).get('target') == task['id']
               and e.get('role') in {'research_work', 'supplemental_research'} for e in new_runtime.get('executions', {}).values()):
            raise ValueError('work execution must end before completion assessment')
        validate_item_dispositions(task, assessment, require_complete=assessment['decision'] in {'completed','closed'})
        coverage = judge_coverage_errors(actor['role'], execution_id, task, assessment, families)
        if coverage:
            raise ValueError(coverage[0])
        obligations = {o['id']: o for o in contract_obligations(task)}
        evidence_ids = set(records) | result_ids(task)
        for row in assessment['item_dispositions']:
            obligation = obligations[row['obligation_id']]
            if (row['kind'] == 'fulfilled' and actor['role'] not in obligation['judges']
                    and execution_id not in obligation['judges']
                    and not designated_judgment(task, obligation, row, new_instance, new_runtime)):
                raise ValueError('fulfilled obligation needs its designated judge or a current specialist judgment for this task')
            require_evidence_refs(row['evidence_refs'], evidence_ids)
            if row['kind'] in {'waived','transferred'}:
                validate_disposition_authority(task, row, new_instance, new_runtime, evaluation_context=evaluation_context)
            if row['kind'] == 'transferred':
                target = tasks.get(row['target_task_id'])
                if not target or target['id'] == task['id'] or target['id'] in ids or target['status'] in {'completed','closed'}:
                    raise ValueError('transfer requires a distinct unfinished recipient outside this assessment set')
                previous = reference_tasks.get(target['id'])
                if not previous or contract_hash(previous) != contract_hash(target):
                    raise ValueError('transfer recipient must be bound to the current input')
                if any(e.get('status') != 'ended' and e.get('action', {}).get('target') == target['id'] for e in new_runtime.get('executions', {}).values()):
                    raise ValueError('transfer recipient has a live execution')
                if row['target_obligation_id'] in {o['id'] for o in contract_obligations(target)}:
                    raise ValueError('transfer cannot overwrite an existing recipient obligation')
                transfers.append((task, target, row, obligation))
    changed_targets = set()
    for source, target, row, obligation in transfers:
        if target['id'] not in changed_targets:
            target.setdefault('revision_history', []).append({'revision':target['revision'], 'contract_sha256':contract_hash(target), 'reason':'obligation transfer','execution_id':execution_id})
            target['revision'] += 1
            target['reviews'] = []
            target.pop('assessment', None)
            target['status'] = 'planned'
            changed_targets.add(target['id'])
        if row['target_obligation_id'] in {o['id'] for o in target['completion_obligations']}:
            raise ValueError('duplicate transferred obligation ID')
        target['completion_obligations'].append({**deepcopy(obligation), 'id':row['target_obligation_id']})
        target.setdefault('transferred_obligations', []).append({'from_task':source['id'], 'from_revision':source['revision'],
            'from_obligation_id':obligation['id'], 'obligation_id':row['target_obligation_id'], 'authority_ref':row['authority_ref'], 'execution_id':execution_id})
    for target_id in changed_targets:
        target = tasks[target_id]
        from .repository import new_id
        cancelled=[a for a in new_runtime.setdefault('queue',[]) if a.get('target')==target_id]
        new_runtime['queue']=[a for a in new_runtime['queue'] if a.get('target')!=target_id]
        new_runtime['queue'].append({'id':new_id('AC'), 'role':'task_contract_review', 'target':target_id, 'reason':'Inherited obligations require independent approval'})
        new_runtime.setdefault('history',[]).append({'kind':'recipient_contract_revised','target':target_id,'execution_id':execution_id,'cancelled_actions':cancelled})
        target.pop('waiting',None)
        target.pop('revision_requested', None)
    for assessment in assessments:
        task = tasks[assessment['task_id']]
        if task.get('assessment'):
            task.setdefault('assessment_history', []).append(deepcopy(task['assessment']))
        task['assessment'] = {**deepcopy(assessment), 'execution_id':execution_id, 'contract_sha256':contract_hash(task),
                              'results_sha256':exact_content_hash(task['results']), 'current':True,
                              'basis':assessment_basis(task,assessment,new_instance,new_runtime)}
        task['assessment']['specialist_support'] = {
            row['obligation_id']: designated_judgment(task,
                next(o for o in task['completion_obligations'] if o['id'] == row['obligation_id']), row, new_instance, new_runtime)
            for row in assessment['item_dispositions'] if row['kind'] == 'fulfilled'
            and actor['role'] not in next(o for o in task['completion_obligations'] if o['id'] == row['obligation_id'])['judges']
            and execution_id not in next(o for o in task['completion_obligations'] if o['id'] == row['obligation_id'])['judges']}
        if assessment['decision'] in {'completed','closed'}:
            task['status'] = assessment['decision']; task.pop('waiting', None)
        else:
            task['status'] = 'waiting'
            unresolved = assessment.get('unresolved', [])
            task['waiting'] = {'kind':'assessment_input' if unresolved else 'research_followup',
                'target_refs':list(dict.fromkeys(ref for row in unresolved for ref in row['missing_inputs'])),
                'next_owner':unresolved[0]['next_owner'] if unresolved else 'research_plan', 'basis_ref':execution_id}
            if not unresolved and not any(a.get('role')=='research_plan' for a in new_runtime.setdefault('queue',[])):
                from .repository import new_id
                new_runtime['queue'].append({'id':new_id('AC'),'role':'research_plan','reason':'Select continuation for assessed remaining obligations','requested_by':execution_id})
        new_runtime.setdefault('history', []).append({'kind':'task_assessed','task_id':task['id'],'execution_id':execution_id,'decision':assessment['decision']})
    return new_instance, new_runtime
