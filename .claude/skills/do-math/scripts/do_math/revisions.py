"""Declared revision boundaries and target-by-target disposition checks."""
from copy import deepcopy

from . import knowledge, planning
from .values import parse_utc
from .canonical import exact_content_hash
from .session_slots import live_action_ids


def regeneration_time_valid(regenerate_after, observed_at) -> bool:
    """A regeneration time must be a zoned time strictly after the machine observation.

    Malformed times raise ValueError."""
    return parse_utc(regenerate_after) > parse_utc(observed_at)


def capture_targets(instance, runtime, identifiers, *, required=False, source_ref=None):
    result = {}
    for identifier in identifiers:
        if identifier in runtime.get("tasks", {}):
            task = runtime["tasks"][identifier]
            row = {"revision": task.get("revision", 1), "contract_sha256": planning.contract_hash(task)}
        elif identifier in instance.get("knowledge", {}):
            item = instance["knowledge"][identifier]
            row = {"revision": item.get("revision", 1), "content_sha256": knowledge.content_hash(item)}
        else:
            raise ValueError("revision target must name an existing task or knowledge: " + identifier)
        row["required"] = required
        if source_ref:
            row["source_refs"] = [source_ref]
        result[identifier] = row
    return result


def target_changes(targets, instance, runtime):
    changes = []
    for identifier, previous in targets.items():
        try:
            current = capture_targets(instance, runtime, [identifier])[identifier]
        except ValueError:
            changes.append({"id": identifier, "field": "revision_target", "reason": "missing"})
            continue
        for key in ("revision", "contract_sha256", "content_sha256"):
            if previous.get(key) != current.get(key):
                changes.append({"id": identifier, "field": key, "before": previous.get(key), "after": current.get(key)})
    return changes


def submission_errors(output, extensions, context):
    action = context["action"]
    declared = action.get("revision_targets", {})
    tasks = {row["id"]: row for row in context.get("tasks", [])}
    if context.get("task"):
        tasks[context["task"]["id"]] = context["task"]
    known_knowledge = {row["id"] for row in context.get("knowledge_catalog", [])}
    errors = []
    def issue(path, message):
        errors.append({"path": "activity-extensions.json/" + path, "message": message})
    requests = [identifier for row in extensions.get("revision_requests", []) for identifier in row["record_ids"]]
    reference_tasks = tasks.keys() | {row['id'] for row in context.get('task_catalog', [])}
    if len(requests) != len(set(requests)) or set(requests) - reference_tasks - known_knowledge:
        issue("revision_requests", "revision requests must name distinct provided tasks or knowledge")
    if set(requests) & {row['task_id'] for row in output.get('dispositions', []) if row['kind'] == 'selected'}:
        issue("revision_requests", "the same output cannot revise and select a task")
    task_targets = [row["revises_task_id"] for row in output.get("candidates", []) if row.get("revises_task_id")]
    task_writes = set(task_targets)
    if len(task_targets) != len(task_writes):
        issue("revision_targets", "each existing task may have only one replacement candidate per response")
    knowledge_writes = {row["id"] for row in extensions.get("knowledge_changes", [])}
    if (task_writes | knowledge_writes) - declared.keys():
        issue("revision_targets", "existing records must be declared before this execution; submit revision_requests for new targets")
    resolutions = extensions.get("revision_resolutions", [])
    withdrawals = {row["task_id"] for row in extensions.get("task_dispositions", [])} & declared.keys()
    identifiers = [row["record_id"] for row in resolutions]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) & withdrawals or set(identifiers) | withdrawals != set(declared):
        issue("revision_resolutions", "resolve each declared target exactly once, using a task withdrawal only for task targets")
    prepared = {row["title"]: row for row in output.get("candidates", [])}
    conditions = {row.get("task_title"): row for row in extensions.get("task_conditions", []) if row.get("task_title")}
    for row in resolutions:
        identifier, disposition = row["record_id"], row["disposition"]
        if identifier not in declared:
            continue
        if disposition == "revised" and identifier not in task_writes | knowledge_writes:
            issue("revision_resolutions", "revised requires the corresponding authored change: " + identifier)
        if disposition != "revised" and identifier in task_writes | knowledge_writes:
            issue("revision_resolutions", "an authored revision must have disposition revised: " + identifier)
        if disposition == "unchanged":
            if declared[identifier].get("required") or planning.revision_required(tasks.get(identifier, {})):
                issue("revision_resolutions", "a required revision or rejected contract cannot be cancelled as unchanged")
        if disposition == "delegated":
            title = row.get("task_title")
            if identifier not in known_knowledge or title not in prepared or identifier not in conditions.get(title, {}).get("knowledge_revision_targets", []):
                issue("revision_resolutions", "delegated requires a prepared work task declaring this knowledge target")
        elif "task_title" in row:
            issue("revision_resolutions", "task_title belongs only to a delegated knowledge revision")
    for row in extensions.get("task_conditions", []):
        identifiers = set(row.get("knowledge_revision_targets", []))
        if identifiers - known_knowledge or identifiers - declared.keys():
            issue("task_conditions", "knowledge revision work must name declared knowledge targets")
    return errors


def dependency_cycles(tasks):
    """Return explicit task dependency cycles, including self-dependency."""
    cycles, done, path = [], set(), []
    def visit(identifier):
        if identifier in path:
            cycles.append(path[path.index(identifier):] + [identifier])
            return
        if identifier in done:
            return
        path.append(identifier)
        for dependency in tasks[identifier].get("dependencies", []):
            if dependency in tasks:
                visit(dependency)
        path.pop()
        done.add(identifier)
    for identifier in tasks:
        visit(identifier)
    return cycles


def active_repetition_holds(runtime):
    """Project unresolved configured repetition holds from their recorded authority."""
    history = runtime.get('history', [])
    holds = {}
    for row in history:
        key = row.get('lineage'), row.get('lineage_id')
        if row.get('kind') == 'repetition_hold':
            holds[key] = row
        elif row.get('kind') == 'task_repetition':
            if row.get('outcome') == 'continued':
                holds.pop(key, None)
    return deepcopy(holds)


def repetition_hold(runtime, lineage, lineage_id):
    return active_repetition_holds(runtime).get((lineage, lineage_id))


def action_repetition_waits(instance, runtime, action):
    if action.get('role') in {'operational_review','maintenance'}:
        return []
    if action.get('role') == 'intent_interpretation' and not import_rework(runtime, action):
        return []
    keys=list(action.get('repetition_bases',{}).items())
    from .model_policy import preparation_only
    if action.get('role') == 'research_preparation' and preparation_only(action):
        keys = [(lineage, key) for lineage, key in keys if lineage != 'exhaustion_empty']
    for identifier in action.get('revision_targets', {}).keys() | action.get('observation_rule_targets', {}).keys():
        lineage='contract_revision' if identifier in runtime.get('tasks',{}) else 'proposal_version'
        keys.append((lineage,identifier if lineage=='contract_revision' else proposal_lineage(instance,identifier)[0]))
    waits=[]
    for lineage,key in keys:
        hold=repetition_hold(runtime,lineage,key)
        if not hold or (lineage=='exhaustion_empty' and action.get('periodic_reconsideration')):
            continue
        waits.append(hold)
    return waits


def action_scope(action):
    """Bind authored scope, excluding scheduling caches and explanatory prose."""
    return {key: deepcopy(action[key]) for key in (
        'id', 'role', 'target', 'stage', 'owner_activity_id', 'continuation_of',
        'revision_targets', 'repetition_bases', 'import_id', 'previous_import_id',
        'intent_repair', 'review_cycle_id', 'grant_id', 'assessment_targets', 'observation_rule_targets') if key in action}


def record_import_rework(instance, runtime, action, execution_id, *, clock):
    """Count an actual reauthor attempt in the execution registration publication."""
    if import_rework(runtime, action):
        record_repetition(instance, runtime, lineage='import_rework',
            lineage_id=action['repetition_bases']['import_rework'], event_ref=execution_id,
            outcome='reauthored', owner='ai', reason='Registered interpretation reauthor attempt', clock=clock)


def import_rework(runtime, action):
    if action.get('role') != 'intent_interpretation' or action.get('stage', 'interpret') != 'interpret':
        return False
    if action.get('intent_repair') or action.get('previous_import_id'):
        return True
    predecessor = runtime.get('executions', {}).get(action.get('continuation_of'), {})
    return (predecessor.get('role') == 'intent_interpretation'
            and predecessor.get('action', {}).get('stage', 'interpret') == 'interpret')


def record_repetition(instance, runtime, *, lineage, lineage_id, event_ref, outcome, owner, reason,
                      decision_ref=None, regenerate_after=None, observed_at=None, version=None, clock):
    """Record an idempotent real receipt and its next owner in the same candidate."""
    from .task_contracts import REPEAT_LINEAGES
    from .task_contracts import repetition_outcome
    classification = repetition_outcome(outcome)
    if lineage not in REPEAT_LINEAGES or owner not in {'ai','user'}:
        raise ValueError('unknown repetition lineage or owner')
    if not all(isinstance(s,str) and s.strip() for s in (lineage_id,event_ref,outcome,reason)):
        raise ValueError('repetition needs its lineage, actual event, outcome and reason')
    if regenerate_after:
        if not observed_at or not regeneration_time_valid(regenerate_after, observed_at):
            raise ValueError('regeneration time must follow the machine observation')
    row={'kind':'task_repetition','lineage':lineage,'lineage_id':lineage_id,'event_ref':event_ref,
         'outcome':outcome,'owner':owner,'reason':reason}
    if version is not None:
        if type(version) is not int or version<1 or lineage not in {'contract_revision','proposal_version'}:
            raise ValueError('version receipt requires a positive semantic version')
        row['version']=version
    if decision_ref: row['decision_ref']=decision_ref
    if outcome=='continued':
        row['baseline_revision']=instance.get('decisions',{}).get(decision_ref,{}).get('change',{}).get('baseline_revision',0)
    if regenerate_after: row.update(regenerate_after=regenerate_after, observed_at=observed_at)
    history=runtime.setdefault('history',[])
    previous=next((r for r in history if r.get('kind')=='task_repetition' and
        (r.get('lineage'),r.get('lineage_id'),r.get('event_ref'))==(lineage,lineage_id,event_ref)),None)
    if previous:
        if previous != row: raise ValueError('same repetition receipt has different content')
        return deepcopy(previous)
    if outcome == 'continued':
        from .task_scope import decision_is_current
        decision=instance.get('decisions',{}).get(decision_ref,{})
        change=decision.get('change',{});hold=repetition_hold(runtime,lineage,lineage_id)
        if not decision_is_current(decision,instance,runtime) or not hold or change.get('kind')!='repetition_continue' or (
            change.get('lineage'),change.get('lineage_id'),change.get('hold_event_ref'))!=(lineage,lineage_id,hold['event_ref']) or not change.get('allowed_action'):
            raise ValueError('continuation reset requires its explicit current decision')
        if lineage in {'contract_revision','proposal_version'} and (type(row['baseline_revision']) is not int or row['baseline_revision']<1):
            raise ValueError('version continuation needs its current baseline revision')
        if lineage in {'contract_revision','proposal_version'}:
            current=max((r.get('version',0) for r in history if r.get('lineage')==lineage and r.get('lineage_id')==lineage_id),default=0)
            if row['baseline_revision']!=current:raise ValueError('continuation cannot invent a future version baseline')
    history.append(row)
    from .task_contracts import repetition_lineages
    limit=instance.get('config',{}).get(lineage+'_limit')
    if limit is not None and (type(limit) is not int or limit<1):
        history.pop();raise ValueError('repetition limit must be an adopted positive integer')
    count=repetition_lineages(runtime,include_events=False)[lineage].get('by_lineage',{}).get(lineage_id,0)
    if limit is not None and count>=limit and not repetition_hold(runtime,lineage,lineage_id):
        question = (f'Repetition limit reached for {lineage}/{lineage_id}: {count}/{limit}. '
                    f'Basis: {event_ref}. {reason} '
                    'Which exact continuation or replacement strategy do you authorize?')
        history.append({'kind':'repetition_hold','lineage':lineage,'lineage_id':lineage_id,'event_ref':event_ref,
            'count':count,'limit':limit,'owner':'user','next_owner':'user',
            'release_condition':'explicit scoped continuation or replacement strategy', 'reason':reason,
            'question': question})
        from .questions import link
        linked = link(runtime, execution_id=event_ref, field=f'{len(history) - 1}/question',
             owner='user', targets=[event_ref], reason='Configured repetition limit reached; scoped continuation required', clock=clock)
        linked['source_kind'] = 'history'
    if classification['diagnose']:
        if repetition_hold(runtime, lineage, lineage_id):
            return deepcopy(row)
        role = 'operational_review'
        queue=runtime.setdefault('queue',[])
        live = live_action_ids(runtime)
        available = [a for a in queue if a.get('role')==role and not a.get('live') and a.get('id') not in live]
        pending = next((a for a in available if a.get('target')==event_ref
                        and a.get('repetition_lineage') in (None, [lineage,lineage_id])), None)
        if pending is None:
            pending = next((a for a in available if a.get('repetition_lineage')==[lineage,lineage_id]), None)
        if pending:
            pending.setdefault('repetition_lineage', [lineage,lineage_id])
            if event_ref not in pending.setdefault('receipt_refs',[]): pending['receipt_refs'].append(event_ref)
        else:
            queue.append({'id':clock.new_id('AC'),'role':role,'target':event_ref,
                          'reason':reason,'repetition_lineage':[lineage,lineage_id],'receipt_refs':[event_ref]})
    return deepcopy(row)


def proposal_lineage(instance, identifier):
    """A replacement ID does not reset the mathematical proposal's version."""
    seen=set();version=0
    while identifier:
        if identifier in seen: raise ValueError('cyclic proposal revision lineage')
        seen.add(identifier);version+=1
        record=instance.get('knowledge',{}).get(identifier)
        if not record: raise ValueError('missing proposal revision ancestor')
        parent=record.get('supersedes')
        if not parent:return identifier,version
        identifier=parent


def continue_repetition(instance, runtime, change, decision, *, clock):
    """Apply a user decision to an existing exact queued/waiting obligation."""
    lineage, key = change.get('lineage'), change.get('lineage_id')
    hold = repetition_hold(runtime, lineage, key)
    if not hold or hold['event_ref'] != change.get('hold_event_ref'):
        raise ValueError('continuation must name the current repetition hold')
    allowed = change.get('allowed_action')
    if not isinstance(allowed, dict) or not isinstance(allowed.get('id'), str) or not allowed['id'].strip():
        raise ValueError('allowed_action requires the exact action_scope object')
    candidates = list(runtime.get('queue', [])) + [r['action'] for r in runtime.get('waiting_actions', {}).values()]
    action = next((a for a in candidates if a.get('id') == allowed['id']), None)
    create = False
    if action is None and lineage == 'exhaustion_empty':
        predecessor = runtime.get('executions', {}).get(hold['event_ref'], {})
        expected = {'id': allowed['id'], 'role': 'research_preparation',
                    'repetition_bases': {'exhaustion_empty': key}, 'revision_targets': {}}
        if (allowed == expected and predecessor.get('outcome') == 'output_accepted'
                and not any(e.get('action', {}).get('id') == allowed['id'] for e in runtime.get('executions', {}).values())
                and not any(a.get('repetition_bases', {}).get(lineage) == key for a in candidates)):
            action, create = deepcopy(expected), True
    if action is None or action_scope(action) != allowed:
        raise ValueError('continuation scope differs from the current queued or waiting action')
    if hold not in action_repetition_waits(instance, runtime, action):
        raise ValueError('continued action is outside this held lineage')
    if action['id'] in live_action_ids(runtime):
        raise ValueError('continuation cannot overlap a live attempt')
    record_repetition(instance, runtime, lineage=lineage, lineage_id=key,
        event_ref=decision['id'], outcome='continued', owner='user',
        reason=change.get('reason') or 'User authorized the scoped continuation', decision_ref=decision['id'], clock=clock)
    if create:
        action['reason'] = 'User continued the held empty preparation'
        action['receipt_refs'] = [hold['event_ref']]
        runtime.setdefault('queue', []).append(action)
    # Repetition holds are history/dispatch conditions. Registered input,
    # authority and publication waiting_actions keep their own release owner.
    from .questions import open_links, resolve_user
    question_field = f"{runtime['history'].index(hold)}/question"
    questions = [q['id'] for q in open_links(runtime, 'user') if q.get('origin_execution_id') == hold['event_ref']
        and q.get('source_kind') == 'history' and q.get('origin_field') == question_field]
    if questions:
        resolve_user(runtime, questions, resolution_ref=decision['id'], affected_ids=[hold['event_ref']])
    decision['affected'] = [hold['event_ref'], action['id']]
    if runtime.get('status') == 'waiting' and not runtime.get('user_pause'):
        runtime['status'] = 'ready'


def bind_repetition_bases(instance,runtime,action):
    """Bind semantic premises before starting, keeping retry request identity out."""
    from .model_policy import preparation_only
    if action.get('role') == 'research_preparation' and preparation_only(action):
        return
    if action.get('repetition_bases'):
        return
    role=action.get('role')
    if role not in {'research_plan','research_preparation','intent_interpretation'}:
        return
    common={'instance':instance.get('id'),'governance':instance.get('governance', {}),
            'sources':instance.get('sources',[]),'grants':instance.get('grants',{}),'trust':instance.get('active_trust_environment')}
    if role=='research_plan':
        common['population']={key:planning.task_reference_basis(value) for key,value in runtime.get('tasks',{}).items()}
        lineage='selection_failure'
    elif role=='research_preparation':
        common['population']={key:planning.contract_hash(value) for key,value in runtime.get('tasks',{}).items()}
        lineage='exhaustion_empty'
    else:
        # The preserved original input survives new import/action IDs.
        common = {'instance': instance.get('id'), 'input_id': action.get('target')}
        lineage='import_rework'
    action['repetition_bases']={lineage:exact_content_hash(common)}


def record_execution_outcome(instance, runtime, action, output, execution_id, *, accepted, clock):
    """Called on receipt, after actual candidate application or on rejection."""
    execution=runtime.get('executions',{}).get(execution_id)
    if not execution or execution.get('role') != action.get('role'):
        raise ValueError('repetition outcome requires the actual assigned execution')
    role=action['role']
    reason=execution.get('error') or output.get('summary') or 'execution receipt'
    if role=='research_plan':
        failure=execution.get('error_kind')
        result='accepted' if accepted else {'currentness_changed':'premises_changed',
            'output_validation':'rejected','output_parse':'rejected','output_schema':'rejected',
            'output_contract':'rejected','publication_failure':'waiting'}.get(failure,'unclassified_failure')
        basis=action.get('repetition_bases',{}).get('selection_failure') or exact_content_hash({
            'instance':instance['id'],'population':execution.get('ready_task_ids',[]),'basis':execution.get('decision_basis',{})})
        record_repetition(instance,runtime,lineage='selection_failure',lineage_id=basis,event_ref=execution_id,
                          outcome=result,owner='ai',reason=reason, clock=clock)
    from .model_policy import preparation_only
    if role=='research_preparation' and not preparation_only(action):
        preserved=[t for t in runtime.get('tasks',{}).values() if t.get('producer_execution')==execution_id or
                   any(h.get('execution_id')==execution_id for h in t.get('revision_history',[]))]
        basis=action.get('repetition_bases',{}).get('exhaustion_empty') or exact_content_hash({
            'instance':instance['id'],'governance':instance.get('governance', {}),
            'sources':instance.get('sources',[])})
        observed_at = execution.get('observed_at') or execution.get('started_at')
        regenerate_after = output.get('regenerate_after') if not preserved else None
        if regenerate_after:
            try:
                if not observed_at or not regeneration_time_valid(regenerate_after, observed_at):
                    regenerate_after = None
            except (ValueError, TypeError, AttributeError):
                regenerate_after = None
        if preserved or accepted:
            record_repetition(instance,runtime,lineage='exhaustion_empty',lineage_id=basis,event_ref=execution_id,
                              outcome='contracts_preserved' if preserved else 'empty',owner='ai',reason=reason,
                              observed_at=observed_at, regenerate_after=regenerate_after, clock=clock)
    for identifier,current in runtime.get('tasks',{}).items():
        previous=action.get('revision_targets',{}).get(identifier,{})
        authored=current.get('producer_execution')==execution_id or any(h.get('execution_id')==execution_id for h in current.get('revision_history',[]))
        if authored or (accepted and previous and current.get('revision',0)>previous.get('revision',0)):
            record_repetition(instance,runtime,lineage='contract_revision',lineage_id=identifier,event_ref=execution_id,
                outcome='authored' if current['revision']==1 else 'revised',version=current['revision'],owner='ai',reason=reason, clock=clock)
    for identifier,current in instance.get('knowledge',{}).items():
        if current.get('producer_execution')==execution_id:
            root,version=proposal_lineage(instance,identifier)
            record_repetition(instance,runtime,lineage='proposal_version',lineage_id=root,event_ref=execution_id,
                outcome='authored' if version==1 else 'revised',version=version,owner='ai',reason=reason, clock=clock)
