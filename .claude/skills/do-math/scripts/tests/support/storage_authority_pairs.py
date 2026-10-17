"""Authority/ontology producers, published and loaded through the installed contract.

Only Git/time/host/compiler observations are doubles. Stored records are never
patched to fill receiving fields; proposals go through their domain producers.
"""
from copy import deepcopy

from contracts.pairs import Pair
from support.storage_records import record_store


def _named_fields(schema, values=None, prefix=''):
    """Named fields, including closed values in maps, tuples and schema branches.

    Boolean schemas and raw evidence have no named fields. With values, only
    fields actually present count; an empty container cannot produce its
    children's optional fields.
    """
    if isinstance(schema, bool):
        return set()
    fields = set()
    for name, child in schema.get('properties', {}).items():
        present = None if values is None else [value[name] for value in values
                                               if isinstance(value, dict) and name in value]
        if present == []:
            continue
        path = prefix + name
        fields.add(path)
        fields.update(_named_fields(child, present, path + '/'))
    additional = schema.get('additionalProperties')
    if isinstance(additional, dict):
        members = None if values is None else [member for value in values if isinstance(value, dict)
            for key, member in value.items() if key not in schema.get('properties', {})]
        fields.update(_named_fields(additional, members, prefix + '{}/'))
    for index, item in enumerate(schema.get('prefixItems', [])):
        members = None if values is None else [value[index] for value in values
            if isinstance(value, list) and len(value) > index]
        fields.update(_named_fields(item, members, prefix.rstrip('/') + '[' + str(index) + ']/'))
    item = schema.get('items', True)
    if isinstance(item, dict):
        start = len(schema.get('prefixItems', []))
        members = None if values is None else [member for value in values
            if isinstance(value, list) for member in value[start:]]
        fields.update(_named_fields(item, members, prefix.rstrip('/') + '[]/'))
    for keyword in ('anyOf', 'oneOf', 'allOf'):
        for branch in schema.get(keyword, []):
            fields.update(_named_fields(branch, values, prefix))
    if 'if' in schema:
        from jsonschema import Draft202012Validator
        condition = Draft202012Validator(schema['if'])
        for keyword, matches in (('then', True), ('else', False)):
            present = None if values is None else [value for value in values
                if condition.is_valid(value) == matches]
            fields.update(_named_fields(schema.get(keyword, True), present, prefix))
    return fields


def family_pair(store, family, samples, *, contract=None):
    """Project maps, list items and the open boolean/object approval value."""
    from do_math.state_contract import validate_record
    definition = (contract or store.contract).family('research', family)
    scalar = family == 'governance_approval'
    fields = frozenset({'/value'} if scalar else _named_fields(definition.schema))

    def records(state):
        if family not in state[0]:
            return []
        value = state[0][family]
        if scalar:
            return [value]
        if definition.shape == 'map':
            return list((value or {}).values())
        if definition.shape == 'list':
            return value or []
        raise ValueError('unsupported authority family shape')

    def receive(state):
        for value in records(state):
            validate_record(definition.checker, value, 'research/' + family)
            if definition.validator:
                definition.validator(value)

    def written(state):
        values = records(state)
        return {'/value'} if scalar and values else _named_fields(definition.schema, values)

    return Pair('research.' + family, lambda root: samples, receive, fields, written)


def _keep(store, samples, branch, state):
    """Check publication, exact reload and preservation of the previous head."""
    previous = store.load() if samples else None
    head = store.save_with_state(previous[0], *state)[0] if previous else store.initialize(*state)
    loaded, instance, runtime = store.load(head)
    if loaded != head or (instance, runtime) != state:
        raise AssertionError('producer content changed in storage: ' + branch)
    if previous and store.load(previous[0]) != previous:
        raise AssertionError('previous stored head changed: ' + branch)
    samples.append((branch, deepcopy((instance, runtime))))


def authority_samples(root):
    from do_math import governance as gov
    from support.governance_cases import initial_approval_scene, replacement_engine
    from support.state_builders import charter

    sim, before_i, before_r, source, approval, approval_source, records = initial_approval_scene()
    store, samples = record_store(root / 'authority'), []
    _keep(store, samples, 'unapproved initialization', (before_i, before_r))
    instance, runtime = deepcopy((sim.instance, sim.runtime))
    _keep(store, samples, 'exact initial approval', (instance, runtime))
    clock = sim.clock
    raw = '승인 e\u0301\r\n권한의 범위는 이 원문 그대로다.\n'
    preserved = gov.preserve_source('GS-authority-pair', raw, origin='user', revision=2)
    instance['governance_sources'][preserved['id']] = preserved

    def decide(branch, change):
        nonlocal instance, runtime
        proposed = deepcopy(change)
        instance, runtime, event = gov.apply_decision(instance, runtime, change,
            source_ref=preserved['id'], clock=clock)
        if change != proposed or event['change'] != proposed or event['source_sha256'] != preserved['sha256']:
            raise AssertionError('decision did not preserve the exact approved change: ' + branch)
        payload = proposed.get('grant') or proposed.get('delegation') or proposed.get('record')
        if payload:
            family = {'grant': 'grants', 'delegation': 'delegations'}.get(proposed['kind'], 'governance')
            written = instance[family][payload['id']]
            if any(written.get(key) != value for key, value in payload.items()):
                raise AssertionError('installed record differs from user proposal: ' + branch)
        _keep(store, samples, branch, (instance, runtime))
        return event

    original = records[0]
    proposal = charter('CH-authority-pair', goal='Explicit successor goal')
    proposal['content']['academic_requirements'] = [{'id': 'AR-authority-pair', 'scope': 'Report the bounded result',
        'criteria': ['Preserve the statement', 'Name the unresolved scope'], 'assessor': 'research_plan',
        'required_inputs': [original['id']], 'external_effects': [
            {'id': 'EF-authority-pair', 'scope': 'An explicitly ungranted publication', 'grant_id': None}]}]
    proposal.update(revision=original['revision'] + 1, supersedes=[original['id']],
                    document={'ref': 'user:charter-exact', 'sha256': 'a' * 64})
    decide('explicit charter supersession', {'kind': 'charter', 'record': proposal})
    for record in [
        {'id': 'PO-authority-pair', 'kind': 'policy', 'revision': 1, 'supersedes': [],
         'content': {'rule_id': 'bounded', 'text': 'Only this scope', 'scope': ['P'],
                     'reason_refs': [proposal['id']], 'audit_refs': []}},
        {'id': 'CX-authority-pair', 'kind': 'research_context', 'revision': 1, 'supersedes': [],
         'content': {'terms': [{'term': 'P', 'definition': 'The exact proposition', 'boundary': 'natural numbers',
                               'avoid_synonyms': ['Q'], 'record_refs': [proposal['id']]}]}},
        {'id': 'AU-authority-pair', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [],
         'content': {'scope': ['P'], 'required_inputs': [proposal['id']], 'assessor': 'goal_audit',
                     'verdict_mapping': {'yes': 'satisfied', 'no': 'not_satisfied', 'unknown': 'unresolved'}}},
    ]:
        decide('install ' + record['kind'], {'kind': record['kind'], 'record': record})

    local = {'id': 'GR-authority-local', 'kind': 'local', 'roles': ['research_work'],
             'task_ids': [], 'reuse': 'reusable', 'included_targets': [instance['id']],
             'excluded_targets': ['TK-excluded'], 'subjects': ['bounded case'],
             'execution_kinds': ['ai'], 'purposes': ['research'],
             'valid_from': '2020-01-01T00:00:00Z', 'expires_at': '2099-01-01T00:00:00Z',
             'initialization_only': True, 'academic_only': False, 'requires_academic': False}
    original_decision = decide('local grant', {'kind': 'grant', 'grant': local})
    decide('http grant', {'kind': 'grant', 'grant': {
        'id': 'GR-authority-http', 'kind': 'http', 'allowed_origins': ['https://example.test'],
        'excluded_origins': ['https://blocked.test'], 'allowed_methods': ['GET'],
        'allowed_path_prefixes': ['/research/'], 'excluded_path_prefixes': ['/research/private/'],
        'credential_env': {'Authorization': 'SYNTHETIC_TOKEN_NAME'}}})
    decide('grant replacement', {'kind': 'grant', 'grant': {**local, 'id': 'GR-authority-replacement'},
                                'replaces': [local['id']]})
    decide('grant revocation', {'kind': 'revoke', 'grant_id': 'GR-authority-http'})
    decide('delegation of actual original decision', {'kind': 'delegation', 'delegation': {
        'id': 'DG-authority-pair', 'status': 'active', 'decision_kind': 'grant',
        'original_decision_id': original_decision['id'], 'included_targets': [instance['id']],
        'excluded_targets': ['TK-excluded'], 'external_effects': ['bounded-read'],
        'resource_limits': {'steps': 2}, 'expires_at': '2099-01-01T00:00:00Z'}})
    decide('delegation revocation', {'kind': 'revoke_delegation', 'delegation_id': 'DG-authority-pair'})

    # A short existing stored review scene supplies the recovery prerequisite;
    # the actual decision producer writes effect, rather than a fabricated row.
    engine, action = replacement_engine(root / 'replacement')
    engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime,
        {'kind': 'review_replacement', 'allowed_action': {key: action[key] for key in
            ('id', 'role', 'target', 'review_cycle_id', 'stage', 'slot', 'round')},
         'grant_id': 'GR-review'}, source_ref='SOURCE-review', clock=engine.ports.clock)
    engine._save()
    _, saved, running = engine.store.load(engine.head)
    decision = next(row for row in saved['decisions'].values() if row.get('kind') == 'review_replacement')
    expected = {key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round',
                                           'replacement_for', 'continuity_break_cause')}
    if decision['effect'] != expected or decision['affected'] != ['K1']:
        raise AssertionError('review decision changed the exact authorized replacement')
    samples.append(('review replacement decision', deepcopy((saved, running))))
    return samples


def ontology_samples(root):
    from do_math import knowledge, knowledge_io as io, knowledge_records as kr
    from support.entry import entry
    from support.knowledge_builders import knowledge_candidate
    from support.review_inputs import reviewed_candidate

    clock = entry().ports.clock
    instance, runtime, source, _ = reviewed_candidate(root, verified=True)
    store, samples = record_store(root / 'ontology'), []
    _keep(store, samples, 'builtins and zero relations', (instance, runtime))
    instance, runtime, target = io.import_candidate(instance, runtime,
        knowledge_candidate(title='Independent target', lean_code='', declaration_names=[]),
        source_ref='input', actor_ref='user', clock=clock)

    def keep(branch):
        _keep(store, samples, branch, (instance, runtime))

    definition = {'family': 'knowledge', 'token': 'bounded_fact', 'meaning': 'A bounded observation.',
        'constraints': {'mathematical_claim': False, 'requires_evidence': False,
                        'required_fields': ['confirmed_scope'], 'allowed_epistemic_statuses': ['conjecture']}}
    for family, token in (('knowledge', 'bounded_fact'), ('relation', 'connects_to')):
        proposed = definition if family == 'knowledge' else {
            'family': family, 'token': token, 'meaning': 'An evidence-backed research connection.',
            'constraints': {'requires_evidence': True}}
        instance, _ = io.register_kind_definition(instance, proposed, source_ref='user:proposal', actor_ref='author', clock=clock)
        keep('candidate ' + family)
        instance = io.check_kind_definition(instance, family, token, check_ref='user:check', actor_ref='checker')
        keep('checked ' + family)
        instance = io.activate_kind_definition(instance, family, token, approval_ref='user:approval', actor_ref='user')
        keep('active ' + family)
        actual = io.lookup_definition(instance, family, token)
        if (any(actual[key] != value for key, value in proposed.items())
                or (actual['status'], actual['builtin'], actual['source_ref'], actual['actor_ref'],
                    actual['check_ref'], actual['checked_by'], actual['approval_ref'], actual['activated_by']) !=
                   ('active', False, 'user:proposal', 'author', 'user:check', 'checker', 'user:approval', 'user')):
            raise AssertionError('kind registration/check/approval changed the declared meaning')
    instance, runtime, _ = io.import_candidate(instance, runtime, knowledge_candidate(kind='bounded_fact',
        lean_code='', declaration_names=[], confirmed_scope='finite', epistemic_status='conjecture'),
        source_ref='input', actor_ref='user', clock=clock)
    relation = {'kind': 'connects_to', 'source': source, 'target': target, 'evidence': 'Exact e\u0301\r\nconnection',
                'evidence_refs': ['input'], 'confirmed_scope': 'Finite research scope'}
    instance, rid = io.import_relation(instance, relation, source_ref='input', actor_ref='user', clock=clock)
    keep('one relation')
    instance, _ = io.import_relation(instance, {**relation, 'id': rid, 'evidence': 'Revised exact evidence'},
        source_ref='user:revision', actor_ref='reviser', clock=clock)
    keep('same relation new revision')

    instance, _ = io.import_relation(instance, {'kind': 'analogous_to', 'source': target,
        'target': source, 'evidence_refs': ['input']}, source_ref='input', actor_ref='user', clock=clock)
    keep('several research relations')
    claim = {'kind': 'formally_implies', 'source': source, 'target': target, 'confirmed_scope': 'True implies True'}
    instance, runtime, proof = io.import_candidate(instance, runtime,
        knowledge_candidate(relation_claim=claim), source_ref='input', actor_ref='user', clock=clock)
    from support.knowledge_builders import formal_evidence
    instance = kr.record_formal_result(instance, proof, formal_evidence(instance, proof, 'TE-reviewed'),
                                       'TE-reviewed', runtime=runtime)
    instance, aid = _review_claim(instance, runtime, proof, clock)
    instance, _ = io.import_relation(instance, {**claim, 'evidence_refs': [proof],
        'formal_result_refs': [instance['knowledge'][proof]['formal_result_id']], 'assessment_refs': [aid]},
        source_ref='input', actor_ref='user', clock=clock)
    keep('mathematical relation with sealed evidence')
    instance, runtime = io.withdraw_kind_definition(instance, runtime, 'relation', 'connects_to',
        reason='Withdraw this meaning', actor_ref='user', clock=clock)
    keep('withdraw relation kind and suspend relation')
    instance, runtime = io.withdraw_kind_definition(instance, runtime, 'knowledge', 'bounded_fact',
        reason='Refine the meaning', actor_ref='user', clock=clock)
    keep('withdraw knowledge kind')
    instance, _ = io.register_kind_definition(instance, definition, source_ref='user:renewal', actor_ref='author', clock=clock)
    keep('reregister with predecessor')
    instance, runtime = knowledge.invalidate_knowledge(instance, runtime, source,
        reason='Endpoint withdrawn', actor_ref='user', clock=clock)
    keep('endpoint withdrawal propagates to relations')
    return _core_kind_check_samples() + samples


def _core_kind_check_samples():
    """One core verdict, published and first decoded by a new installed reader."""
    from do_math.canonical import exact_content_hash
    from do_math.repository import ResearchRepository
    from support.state_builders import installed_contract
    from support.storage_kind_checks import kind_checker, kind_scene, propose_kinds

    engine = kind_scene().engine
    propose_kinds(engine)

    def cold_reader():
        return ResearchRepository(engine.store.repository, engine.store._store.instance_id,
            contract=installed_contract(), backend=engine.ports.git_backend, clock=engine.ports.clock)

    previous = cold_reader().load(engine.head)
    if previous != (engine.head, engine.instance, engine.runtime):
        raise AssertionError('cold kind proposals differ from producer')
    pending = engine.runtime['pending_kind_checks'][0]
    action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id') == pending['definition_id'])
    checker, definition = kind_checker(engine, action, 'EX-ontology-kind-reader')
    engine._apply_kind_definition_check(action, {
        'definition_id': definition['id'], 'definition_sha256': exact_content_hash(definition),
        'decision': 'unresolved', 'findings': ['정확한 미해결 근거 e\u0301\r\n추가 증거 필요']}, checker['id'])
    engine._save()
    cold = cold_reader()
    loaded = cold.load(engine.head)
    if loaded != (engine.head, engine.instance, engine.runtime):
        raise AssertionError('cold kind check differs from producer')
    if cold.load(previous[0]) != previous:
        raise AssertionError('kind check changed the proposal head')
    return [('core kind proposals', deepcopy(previous[1:])),
            ('core unresolved kind check', deepcopy(loaded[1:]))]


def _review_claim(instance, runtime, kid, clock):
    """Two real scope/initial review steps; synthetic answers, no sealed-row edits."""
    from do_math import knowledge_records as kr, review_cycle as rc
    from do_math.execution_lifecycle import create_execution
    from do_math.activities import assign_execution
    from support.review_inputs import scope_assessment
    cycle = rc.start_review({**kr.proposal_view(instance, kid), 'revision': 1}, reviewers=1, max_rounds=1)
    cycle.update(id='RC-relation-pair', owner_activity_id='AT-1', knowledge_id=kid,
        identity_basis=kr.identity_basis(instance, kid), input_snapshot='a' * 40, producer_execution_ids=[],
        policy_ref='policy-test', slot_profiles={}, input_bindings={}, publication_premises={}, review_input_basis={})
    profile = runtime['executions']['EX-1']['execution_profile_ref']
    for stage in ('scope', 'initial'):
        action = rc.next_actions(cycle)[0]
        eid = 'EX-relation-pair-' + stage
        execution = create_execution(execution_id=eid, owner_activity_id='AT-1', actor_kind='ai',
            input_manifest={}, profile_ref=profile, created_at=clock.now())
        execution['role'] = 'identity_review'
        assign_execution(runtime, 'AT-1', execution)
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'Synthetic exact relation judgment',
                  'used_sources': ['proposal'], 'questions': [], 'scope_complete': True}
        if stage == 'scope':
            scope = scope_assessment(cycle['review_policy'], ['initial-0'])
            scope['selected_profile_ref'] = profile
            output['scope_assessment'] = scope
        else:
            output.update(decision='match', findings=[])
        cycle = rc.accept_result(cycle, action, output, eid,
            input_manifest={'proposal_digest': cycle['proposal_digest'], 'role_slot_id': action['slot']})
    runtime['review_cycles'][cycle['id']] = cycle
    assessment = rc.identity_assessment(cycle, reason='The exact relation claim was reviewed')
    assessment['basis'] = kr.identity_basis(instance, kid)
    return kr.record_identity_assessment(instance, kid, assessment, cycle['policy_ref'], runtime=runtime, clock=clock)
