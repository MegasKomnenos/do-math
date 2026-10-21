"""Source-linked questions and explicitly scoped user decision requirements."""
from copy import deepcopy
from .canonical import exact_content_hash


# Who answers a question: the user, the research roles or the operational roles.
QUESTION_OWNERS = frozenset({"user", "research", "operations"})
# The roles that own operations questions.
OPERATIONS_ROLES = frozenset({"operational_review", "maintenance"})
OBLIGATION_KINDS = frozenset({'execution_support', 'input_retrieval', 'installation_defect', 'decision_conflict', 'other'})
QUESTION_DISPOSITIONS = frozenset({'resolved', 'superseded', 'waiting', 'transferred'})


def output_question_index(ref):
    """The one local question token shared by transfer and revision deferral."""
    import re
    match = re.fullmatch(r'output:questions/(0|[1-9][0-9]*)', ref)
    if not match:
        raise ValueError('local question reference must be output:questions/N')
    return int(match.group(1))


def obligation_schema():
    from .contracts import TEXT, closed_object
    return closed_object({'kind': {'enum': sorted(OBLIGATION_KINDS)}, 'subject_ref': TEXT, 'requirement_ref': TEXT})


def obligation_key(obligation):
    if (not isinstance(obligation, dict) or set(obligation) != {'kind', 'subject_ref', 'requirement_ref'}
            or obligation['kind'] not in OBLIGATION_KINDS
            or any(not isinstance(v, str) or not v.strip() for v in obligation.values())):
        raise ValueError('operations obligation requires kind, subject_ref and requirement_ref')
    return exact_content_hash(obligation)


def reference_basis(instance, runtime, ref):
    """Semantic subject observation, excluding report routing bookkeeping."""
    from . import planning, knowledge
    found = planning.record_index(instance, runtime, source_aliases=True).get(ref)
    if not found:
        return {'ref': ref, 'missing': True}
    family, value = found
    if family == 'task':
        value = planning.task_reference_basis(value)
    elif family == 'knowledge':
        value = knowledge.decision_reference(value, instance)
    elif family == 'execution':
        value = {key: value[key] for key in ('id', 'action', 'input_snapshot', 'execution_profile', 'result_ref',
                    'outcome', 'error_kind', 'output_files') if key in value}
    return {'ref': ref, 'family': family, 'sha256': exact_content_hash(value)}


def handling_wait_ready(row, instance, runtime, *, now):
    wait = row['handling']['waiting']
    if not wait:
        return row['handling']['state'] == 'pending'
    if wait['kind'] == 'question':
        return question_scope_state(runtime, wait['question_id'], wait['target_ids'])['resolved']
    if wait['kind'] == 'record_change':
        return reference_basis(instance, runtime, wait['ref']) != wait['basis']
    if wait['kind'] == 'time':
        from .values import parse_utc
        return parse_utc(now) >= parse_utc(wait['at'])
    return runtime['operational_dispositions'][wait['disposition_id']]['status'] in {'applied', 'failed', 'superseded'}


def route_schema():
    from .contracts import TEXT, REFS, closed_object, CONTRACT_REVIEW_ITEMS
    result = closed_object({'question_index': {'type': 'integer', 'minimum': 0},
        'owner': {'enum': sorted(QUESTION_OWNERS)}, 'target_ids': REFS, 'reason': TEXT,
        'blocks': {'type': 'boolean'}, 'obligation': obligation_schema(), 'existing_question_id': TEXT,
        'handler_role': {'enum': sorted(OPERATIONS_ROLES)}, 'reopen_basis_refs': REFS, 'reopen_reason': TEXT,
        'review_item_ids': {'type': 'array', 'uniqueItems': True, 'items': {'enum': list(CONTRACT_REVIEW_ITEMS)}}},
        ['question_index', 'owner', 'target_ids', 'reason'])
    result['allOf'] = [{'if': {'required': ['owner'], 'properties': {'owner': {'const': 'operations'}}},
                       'then': {'required': ['obligation'], 'properties': {'target_ids': {'minItems': 1}}}}]
    return result


def wait_schema(*, stored=False):
    from .contracts import TEXT, REFS, closed_object
    question = {'kind': {'const': 'question'}, 'question_id': TEXT}
    if stored:
        question['target_ids'] = REFS
    return {'oneOf': [
        closed_object(question),
        closed_object({'kind': {'const': 'record_change'}, 'ref': TEXT, 'basis': {'type': 'object'}}),
        closed_object({'kind': {'const': 'time'}, 'at': TEXT}),
        closed_object({'kind': {'const': 'operational_disposition'}, 'disposition_id': TEXT})]}


def question_wait(child, affected_ids):
    scope = [t for t in affected_ids if t in child['target_ids']]
    return {'kind': 'question', 'question_id': child['id'], 'target_ids': scope or list(child['unresolved_target_ids'])}


def resolution_schema(action=None):
    from .contracts import TEXT, REFS, closed_object
    result = closed_object({'question_id': TEXT, 'disposition': {'enum': sorted(QUESTION_DISPOSITIONS)},
        'evidence_refs': {**REFS, 'minItems': 1}, 'reason': TEXT,
        'generation': {'type': 'integer', 'minimum': 1}, 'affected_ids': {**REFS, 'minItems': 1},
        'replacement_question_id': TEXT, 'wait_for': wait_schema(),
        'next_owner': {'enum': ['user', 'research', 'installation_recovery', *sorted(OPERATIONS_ROLES)]}, 'recipient_ref': TEXT},
        ['question_id', 'disposition', 'evidence_refs', 'reason'])
    result['allOf'] = [
        {'if': {'required': ['disposition'], 'properties': {'disposition': {'const': disposition}}},
         'then': {'required': fields}}
        for disposition, fields in (('superseded', ['replacement_question_id']), ('waiting', ['wait_for']),
                                   ('transferred', ['next_owner']))]
    if action and action.get('question_ids'):
        result['required'].extend(['generation', 'affected_ids'])
        result['properties']['question_id'] = {'enum': list(action['question_ids'])}
        result['properties']['generation'] = {'const': action['question_generation']}
        result['properties']['affected_ids'] = {'type': 'array', 'uniqueItems': True,
            'items': {'enum': list(action['question_target_ids'])},
            'minItems': len(action['question_target_ids']), 'maxItems': len(action['question_target_ids'])}
    return result


def open_links(runtime, owner=None):
    return [row for row in runtime.get("question_links", []) if row["status"] == "open" and (owner is None or row["owner"] == owner)]


def open_targets(row):
    """The question targets that no applied resolution has covered yet."""
    return row["unresolved_target_ids"]


def current_question(runtime, identifier):
    by_id = {q['id']: q for q in runtime.get('question_links', [])}
    seen = set()
    owner = by_id[identifier]['owner'] if identifier in by_id else None
    while identifier in by_id:
        if identifier in seen:
            raise ValueError('cyclic question replacement')
        seen.add(identifier)
        row = by_id[identifier]
        if row['owner'] != owner:
            raise ValueError('question replacement cannot change its responsible owner')
        if row['status'] != 'superseded':
            return row
        identifier = row['resolution_history'][-1]['evidence']['replacement_question_id']
    raise ValueError('question replacement does not resolve')


def question_scope_state(runtime, identifier, targets):
    """Accepted receipts for a consumer's fixed scope, including replacement recipients."""
    rows = {q['id']: q for q in runtime.get('question_links', [])}
    if identifier not in rows:
        raise ValueError('question scope reference does not resolve')
    owner = rows[identifier]['owner']
    def visit(qid, scope, path):
        if qid in path:
            raise ValueError('cyclic question replacement')
        if qid not in rows:
            raise ValueError('question replacement does not resolve')
        row = rows[qid]
        if row['owner'] != owner:
            raise ValueError('question replacement cannot change its responsible owner')
        receipts, forwarded_ready = set(), True
        for entry in row.get('resolution_history', []):
            covered = set(scope) & set(entry['affected_ids'])
            replacement = entry.get('evidence', {}).get('replacement_question_id')
            if replacement and (covered or not scope):
                child = visit(replacement, sorted(covered), {*path, qid})
                forwarded_ready &= child['resolved']
                receipts.update(child['resolution_refs'])
            if covered and entry['kind'] not in {'waiting', 'transferred'}:
                receipts.add(entry['resolution_ref'])
        resolved = (not set(scope).intersection(open_targets(row))) if scope else row['status'] != 'open'
        if not scope and row.get('resolution_ref'):
            receipts.add(row['resolution_ref'])
        return {'resolved': bool(resolved and forwarded_ready), 'resolution_refs': sorted(receipts)}
    return visit(identifier, targets, set())


def user_waits(action, instance, runtime, *, records=None):
    """records may carry planning.record_index() of this same state."""
    if action.get("role") in {"intent_interpretation", "operational_review", "maintenance"}:
        return []
    from .planning import action_read_ids
    reads = set() if action.get("role") == "research_plan" else action_read_ids(action, instance, runtime, records=records)
    targets = reads | {action.get("target"), action.get("id"), instance.get("id")}
    retry = action.get("input_overflow_retry", {})
    retry_question = retry.get("question_id") if retry.get("state", "pending") == "pending" else None
    return [{"kind": "user_decision", "question_id": row["id"], "target_ids": open_targets(row), "next_owner": "user"}
            for row in open_links(runtime, "user") if row["id"] != retry_question and row.get("blocks", False)
            and targets & set(open_targets(row))]


def action_waits(action, instance, runtime, *, records=None):
    waits = user_waits(action, instance, runtime, records=records)
    if action.get('role') in {'intent_interpretation', 'operational_review', 'maintenance', 'research_plan', 'research_preparation'}:
        return waits
    from .planning import action_read_ids
    targets = action_read_ids(action, instance, runtime, records=records) | {action.get('target'), instance.get('id')}
    for row in open_links(runtime, 'operations'):
        blocked = {target for origin in row['origins'] if origin['blocks']
                   for target in origin['target_ids']} & set(open_targets(row)) & targets
        if blocked:
            waits.append({'kind': 'question_dependency', 'question_id': row['id'],
                'generation': row['handling']['generation'], 'target_ids': sorted(blocked),
                'next_owner': row['handling']['role']})
    return waits


def link(runtime, *, execution_id, field, owner, targets, source_ref=None, reason=None, blocks=False, checked_by=None,
         obligation=None, existing_question_id=None, handler_role=None, observation_basis=None, reopen_reason=None,
         source_kind=None, source_id=None, clock):
    if owner not in QUESTION_OWNERS or type(blocks) is not bool:
        raise ValueError("question owner and blocking decision required")
    if not isinstance(targets, list) or any(not isinstance(t, str) or not t for t in targets) or (blocks and not targets):
        raise ValueError("blocking questions require explicit affected targets")
    rows = runtime.setdefault("question_links", [])
    key = obligation_key(obligation) if owner == 'operations' else None
    if owner != 'operations' and (obligation or existing_question_id or handler_role or observation_basis):
        raise ValueError('operations routing metadata belongs to operations questions')
    if handler_role and handler_role not in OPERATIONS_ROLES:
        raise ValueError('unknown operations handler')
    origin = {'execution_id': execution_id, 'field': field, 'target_ids': list(dict.fromkeys(targets)),
              'blocks': blocks, 'reason': reason}
    if source_ref:
        origin['source_ref'] = source_ref
    if source_kind:
        origin['source_kind'] = source_kind
    if source_id:
        origin['source_id'] = source_id
    if obligation:
        origin['obligation'] = deepcopy(obligation)
    if observation_basis is not None:
        origin.update(observation_basis=deepcopy(observation_basis), reopen_reason=reopen_reason)
    existing = next((row for row in rows if any(o['execution_id'] == execution_id and o['field'] == field
                     for o in row['origins'])), None)
    if existing:
        previous = next(o for o in existing['origins'] if o['execution_id'] == execution_id and o['field'] == field)
        if existing['owner'] != owner or previous != origin:
            raise ValueError("question source cannot be rerouted silently")
        return existing
    if existing_question_id:
        existing = next((q for q in rows if q['id'] == existing_question_id and q['owner'] == 'operations'), None)
        if not existing or not reason or not reason.strip():
            raise ValueError('existing_question_id must name the same supplied operations obligation with a reason')
    elif key:
        existing = next((q for q in rows if q.get('obligation_key') == key or any(
            obligation_key(o['obligation']) == key for o in q['origins'] if o.get('obligation'))), None)
    if existing and existing['status'] == 'superseded':
        existing = current_question(runtime, existing['id'])
    if existing:
        new_targets = [t for t in targets if t not in existing['target_ids']]
        handling = existing['handling']
        recurrence = (observation_basis is not None and observation_basis != handling['observation_basis'])
        if recurrence and not reopen_reason:
            raise ValueError('a new observation requires a reopening reason')
        existing['origins'].append(origin)
        existing['target_ids'].extend(new_targets)
        existing['blocks'] |= blocks
        reopened = list(dict.fromkeys([*new_targets, *(targets if recurrence else [])]))
        existing['unresolved_target_ids'] = list(dict.fromkeys([*open_targets(existing), *reopened]))
        if reopened:
            existing.update(status='open', resolution_ref=None)
            if handling['state'] in {'resolved', 'superseded'}:
                handling.update(generation=handling['generation'] + 1, state='pending', action_id=None,
                                waiting=None)
        if observation_basis is not None:
            handling['observation_basis'] = deepcopy(observation_basis)
        return existing
    row = {"id": clock.new_id("QU"), "origin_execution_id": execution_id, "origin_field": field,
           "owner": owner, "target_ids": list(dict.fromkeys(targets)), "unresolved_target_ids": list(dict.fromkeys(targets)),
           "blocks": blocks, "status": "open", "resolution_ref": None, "checked_by": checked_by}
    row['origins'] = [origin]
    if key:
        row.update(obligation=deepcopy(obligation), obligation_key=key,
            handling={'generation': 1, 'role': handler_role or 'maintenance', 'state': 'pending',
                'action_id': None, 'owner_activity_id': None, 'execution_ids': [], 'waiting': None,
                'last_resolution_ref': None, 'observation_basis': deepcopy(observation_basis)})
    if source_ref:
        row["source_ref"] = source_ref
    if source_kind:
        row['source_kind'] = source_kind
    if source_id:
        row['source_id'] = source_id
    if reason:
        row["routing_reason"] = reason
    rows.append(row)
    return row


def close(row, *, kind, resolution_ref, affected_ids, status="resolved", evidence=None, preserve_ids=()):
    """The only resolving transition: resolve affected targets, closing the question with its last one.

    Every closing path appends the same history entry shape."""
    remaining = (set(open_targets(row)) - set(affected_ids)) | (set(preserve_ids) & set(open_targets(row)))
    row["unresolved_target_ids"] = [target for target in row["target_ids"] if target in remaining]
    entry = {"kind": kind, "resolution_ref": resolution_ref,
             "affected_ids": sorted(set(affected_ids) & set(row["target_ids"]))}
    if evidence is not None:
        entry["evidence"] = deepcopy(evidence)
    row.setdefault("resolution_history", []).append(entry)
    if not remaining:
        row.update(status=status, resolution_ref=resolution_ref)
    if row['owner'] == 'operations':
        row['handling'].update(last_resolution_ref=resolution_ref, waiting=None,
                              state=status if not remaining else 'pending')
        if remaining:
            row['handling'].update(generation=row['handling']['generation'] + 1,
                                  action_id=None)


def resolution_error(row, role):
    """Why an AI extension cannot resolve this question row now; None when it can.

    Submission checks call this on the fixed input, and application calls it again
    because another execution may have closed the question in between."""
    if not row or row["status"] != "open" or row["owner"] not in QUESTION_OWNERS - {"user"}:
        return "only distinct open research or operations questions can be resolved by an AI extension"
    if row["owner"] == "operations" and role not in OPERATIONS_ROLES:
        return "an operations question requires an operational role"
    return None


def validate_state(instance, runtime):
    """Machine-produced links must survive publication and the first reader unchanged."""
    from . import planning
    records = planning.record_index(instance, runtime, source_aliases=True, question_links=True)
    actions = {a['id']: a for a in runtime.get('queue', [])}
    actions.update((w['action']['id'], w['action']) for w in runtime.get('waiting_actions', {}).values())
    actions.update((e['action']['id'], e['action']) for e in runtime.get('executions', {}).values() if 'action' in e)
    for row in runtime.get('question_links', []):
        question_scope_state(runtime, row['id'], row['target_ids'])
        if set(open_targets(row)) - set(row['target_ids']) or (row['status'] == 'open') != bool(open_targets(row)) and row['target_ids']:
            raise ValueError('question unresolved scope differs from status or routing history')
        sources = [(o['execution_id'], o['field']) for o in row['origins']]
        if len(sources) != len(set(sources)):
            raise ValueError('question origins must be distinct')
        for origin in row['origins']:
            if origin['execution_id'] is not None and origin['execution_id'] not in runtime.get('executions', {}):
                raise ValueError('question report execution does not resolve')
        if row['status'] == 'superseded':
            current_question(runtime, row['id'])
        for resolution in row.get('resolution_history', []):
            if resolution['kind'] in {'ai_resolution', 'waiting', 'transferred'} and not any(
                    receipt['execution_id'] == resolution['resolution_ref'] and receipt.get('response_sha256')
                    for receipt in runtime.get('integrations', {}).values()):
                raise ValueError('question disposition requires its published response receipt')
        if row['owner'] != 'operations':
            continue
        if row['obligation_key'] != obligation_key(row['obligation']):
            raise ValueError('question obligation key differs from descriptor')
        h = row['handling']
        if (row['status'] != 'open') != (h['state'] in {'resolved', 'superseded'}):
            raise ValueError('question handling state differs from resolution')
        if (h['state'] == 'waiting') != (h['waiting'] is not None):
            raise ValueError('question waiting state requires its concrete release condition')
        if h['action_id']:
            action = actions.get(h['action_id'])
            if not action or action.get('question_ids') != [row['id']]:
                raise ValueError('question action does not bind its handling obligation')
            if action['question_generation'] != h['generation']:
                raise ValueError('question handling action generation differs')
        for eid in h['execution_ids']:
            execution = runtime.get('executions', {}).get(eid)
            if not execution or execution['action'].get('question_ids') != [row['id']]:
                raise ValueError('question handler execution does not resolve to its assignment')
        if h['owner_activity_id'] and h['owner_activity_id'] not in runtime.get('activities', {}):
            raise ValueError('question handler activity does not resolve')
        wait = h['waiting']
        if wait and wait['kind'] == 'question' and (wait['question_id'] == row['id'] or
                records.get(wait['question_id'], (None,))[0] != 'question'):
            raise ValueError('question wait child does not resolve')
        if wait and wait['kind'] == 'question' and set(wait['target_ids']) - set(records[wait['question_id']][1]['target_ids']):
            raise ValueError('question wait scope does not resolve in its child')
        if wait and wait['kind'] == 'operational_disposition' and wait['disposition_id'] not in runtime.get('operational_dispositions', {}):
            raise ValueError('question repair disposition does not resolve')
    for action in actions.values():
        fields = {'question_ids', 'question_generation', 'question_target_ids'}
        if fields & action.keys():
            if (not fields <= action.keys() or action['role'] not in OPERATIONS_ROLES or action.get('stage') != 'question'
                    or any(records.get(qid, (None,))[0] != 'question' for qid in action['question_ids'])):
                raise ValueError('question action requires its full assigned scope and handler role')


def resolve_user(runtime, identifiers, *, resolution_ref, affected_ids):
    questions = {row["id"]: row for row in runtime.get("question_links", [])}
    if not isinstance(identifiers, list) or len(identifiers) != len(set(identifiers)):
        raise ValueError("resolves_questions must be distinct question IDs")
    for identifier in identifiers:
        row = questions.get(identifier)
        if not row or row["owner"] != "user" or row["status"] != "open":
            raise ValueError("user decision must name an open user question: " + str(identifier))
        if not set(open_targets(row)) & set(affected_ids):
            raise ValueError("the applied decision does not affect the question target: " + identifier)
    for identifier in identifiers:
        close(questions[identifier], kind="user_decision", resolution_ref=resolution_ref, affected_ids=affected_ids)


def validate_extensions(output, extensions, context):
    # A route target is an ID the role may use (공통-실행.md 「시작할 때 입력을 확인한다」):
    # a supplied input reference, a record the input shows, or a record of its record_index.
    # The citation check reads the same population through the same two functions.
    from .submission import record_index_ids, supplied_reference_ids
    errors = []
    known = supplied_reference_ids(context) | record_index_ids(context) | set(context.get("available_input_refs", []))
    indices = set()
    for route in extensions.get("question_routes", []):
        index = route["question_index"]
        if index in indices or not 0 <= index < len(output.get("questions", [])):
            errors.append({"path": "question_routes", "message": "route each supplied question index at most once"})
        indices.add(index)
        if set(route["target_ids"]) - known or (route["owner"] == "user" and not route["target_ids"]):
            errors.append({"path": "question_routes", "message": "route targets must be IDs this input supplies or "
                           "lists in its record_index, and a user question needs at least one"})
        if route['owner'] == 'operations':
            try:
                obligation_key(route.get('obligation'))
                if route['obligation']['subject_ref'] not in known or not route['target_ids']:
                    raise ValueError('operations subject and affected targets must be supplied')
                if route.get('handler_role') == 'operational_review' and not route['obligation']['subject_ref'].startswith('EX-'):
                    raise ValueError('operational_review requires a supplied execution subject')
                existing = next((q for q in context.get('question_links', []) if q['id'] == route.get('existing_question_id')), None)
                if route.get('existing_question_id') and (not existing or existing['owner'] != 'operations'):
                    raise ValueError('existing_question_id must name a supplied operations question')
                if bool(route.get('reopen_basis_refs')) != bool(route.get('reopen_reason')):
                    raise ValueError('reopening requires observation evidence and reason together')
            except ValueError as error:
                errors.append({'path': 'question_routes', 'message': str(error)})
        elif any(key in route for key in ('obligation', 'existing_question_id', 'handler_role', 'reopen_basis_refs', 'reopen_reason')):
            errors.append({'path': 'question_routes', 'message': 'operations metadata requires operations owner'})
    if context['action']['role'] in OPERATIONS_ROLES:
        for index in set(range(len(output.get('questions', [])))) - indices:
            errors.append({'path': 'question_routes', 'message': 'operational reports must explicitly route each question'})
    if context['action']['role'] == 'task_contract_review':
        unresolved = {r['item_id'] for r in output.get('item_reviews', []) if r['decision'] == 'unresolved'}
        covered = {i for r in extensions.get('question_routes', []) for i in r.get('review_item_ids', [])}
        if unresolved - covered:
            errors.append({'path': 'question_routes', 'message': 'route every unresolved contract review item to its missing-input question'})
    questions = {row["id"]: row for row in context.get("question_links", [])}
    role = context["action"]["role"]
    seen = set()
    for resolution in extensions.get("question_resolutions", []):
        identifier = resolution["question_id"]
        # A repeated ID is rejected like an unknown one.
        error = resolution_error(None if identifier in seen else questions.get(identifier), role)
        if error:
            errors.append({"path": "question_resolutions", "message": error})
        else:
            row = questions[identifier]
            def issue(message):
                errors.append({'path': 'question_resolutions', 'message': message})
            disposition = resolution['disposition']
            assigned = identifier in context['action'].get('question_ids', [])
            if row['owner'] == 'operations':
                if (not assigned or resolution.get('generation') != context['action'].get('question_generation')
                        or set(resolution.get('affected_ids', [])) != set(context['action'].get('question_target_ids', []))):
                    issue('operations resolution must cover its assigned generation and exact fixed targets')
                if disposition in {'waiting', 'transferred'}:
                    if disposition == 'waiting':
                        wait = resolution.get('wait_for', {})
                        if not wait:
                            issue('waiting requires a real wait_for condition')
                        elif wait['kind'] == 'question':
                            if wait['question_id'] == identifier or wait['question_id'] not in questions:
                                issue('question wait requires a distinct supplied question')
                            else:
                                scope = question_wait(questions[wait['question_id']], resolution.get('affected_ids', []))
                                if question_scope_state({'question_links': list(questions.values())},
                                        wait['question_id'], scope['target_ids'])['resolved']:
                                    issue('question wait scope already has its resolution evidence')
                        elif wait['kind'] == 'record_change':
                            bases = {ref: basis for q in context.get('operations_questions', [])
                                     for ref, basis in q.get('record_bases', {}).items()}
                            if wait.get('basis') != bases.get(wait['ref']) or wait['ref'] not in bases:
                                issue('record_change must bind the supplied record basis')
                        elif wait['kind'] == 'time':
                            from .values import parse_utc
                            try:
                                if parse_utc(wait['at']) <= parse_utc(context['observed_at']):
                                    issue('time wait must follow the supplied observation time')
                            except (ValueError, KeyError):
                                issue('time wait needs a valid observation and future UTC time')
                        elif wait['kind'] == 'operational_disposition':
                            ods = {r['id'] for r in context.get('operational_dispositions', [])}
                            if wait['disposition_id'] not in ods:
                                issue('wait must name a supplied operational disposition')
                    elif resolution.get('next_owner') in OPERATIONS_ROLES:
                        if resolution['next_owner'] == role:
                            issue('transfer must change the actual handler')
                        if resolution['next_owner'] == 'operational_review' and not row['obligation']['subject_ref'].startswith('EX-'):
                            issue('operational transfer requires an execution subject')
                    else:
                        recipient = resolution.get('recipient_ref', '')
                        if recipient == 'current:operational_disposition':
                            if role != 'operational_review' or output.get('disposition', {}).get('kind') != 'repair':
                                issue('current disposition recipient requires an actual repair disposition')
                        elif recipient.startswith('output:questions/'):
                            try:
                                index = output_question_index(recipient)
                                route = next(r for r in extensions.get('question_routes', []) if r['question_index'] == index)
                                if (not 0 <= index < len(output.get('questions', [])) or route['owner'] != resolution.get('next_owner')
                                        or set(resolution['affected_ids']) - set(route['target_ids'])):
                                    raise ValueError()
                                if (role == 'operational_review' and output.get('disposition', {}).get('kind') == 'user_decision'
                                        and resolution.get('next_owner') == 'user'
                                        and output['questions'][index] != output['disposition']['question']):
                                    issue('the transferred child must carry the actual operational user decision question')
                            except (StopIteration, ValueError):
                                issue('transfer requires a routed child question covering assigned targets')
                        else:
                            issue('transfer requires an actual handler or child question recipient')
            elif disposition in {'waiting', 'transferred'}:
                issue('only assigned operations handlers can wait or transfer')
            if disposition == 'superseded':
                replacement = questions.get(resolution.get('replacement_question_id'))
                if (not replacement or replacement['id'] == identifier or replacement['owner'] != row['owner']
                        or replacement['status'] != 'open'):
                    issue('superseded requires a distinct open question of the same owner')
        seen.add(identifier)
    if set(context['action'].get('question_ids', [])) - seen:
        errors.append({'path': 'question_resolutions', 'message': 'resolve every assigned question exactly once'})
    return errors

