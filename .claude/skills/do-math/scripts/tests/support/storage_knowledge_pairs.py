"""Actual knowledge producers through Repository, with the installed receiving fields.

The samples retain complete instance/runtime pairs, so reception checks the
real references and seals as well as the record schema. Git, time and compiler
evidence use the existing port fixtures. No stored field is supplied afterwards
to satisfy the reverse check.
"""
from copy import deepcopy

from contracts.pairs import Pair


def family_pair(store, root, family, samples, *, contract=None):
    """Receive stored producer states with the installed family's actual checker.

    Each sample has already passed complete Repository publication/reload,
    including references and cross-record semantics. The field walk need not
    repeat that entire state validation once for every projected family.
    """
    from do_math.state_contract import validate_record
    definition = (contract or store.contract).family(root, family)
    position = 0 if root == 'research' else 1
    if definition.shape == 'metadata':
        fields = frozenset({'/value'})
    elif definition.shape == 'singleton':
        fields = frozenset(definition.schema['additionalProperties']['properties'])
    elif definition.shape == 'map':
        fields = frozenset(definition.schema['properties'])
    else:
        raise ValueError('unsupported family shape')

    def receive(state):
        value = state[position].get(family, {})
        records = value.values() if definition.shape == 'map' else [value]
        for record in records:
            validate_record(definition.checker, record, root + '/' + family)
            if definition.validator is not None:
                definition.validator(record)

    def written(state):
        if definition.shape == 'metadata':
            return {'/value'} if family in state[position] else set()
        return set().union(*(set(row) for row in state[position].get(family, {}).values()))

    return Pair(root + '.' + family, lambda directory: samples, receive,
                fields, written)


def trust_samples(root):
    """Actual initialization, registration, transition, activation and invalidation."""
    from do_math.initialization import initialize_state
    from do_math.trust_validation import check_environment
    from support.fakes.clock import FakeClock
    from support.fakes.git_backend import InProcessGit
    from support.storage_records import INSTANCE_ID, engine_on, fake_ports, record_store
    from support.trust_inputs import trust_fixture
    clock, backend = FakeClock(), InProcessGit()
    ports = fake_ports(clock, backend)
    instance, runtime = initialize_state(instance_id=INSTANCE_ID, goal='Trust pair', workspace=root / 'work',
        config={}, source_input='Trust pair', clock=clock, host=ports.host)
    store = record_store(root / 'trust-state', clock=clock, backend=backend)
    engine, _ = engine_on(store, instance, runtime, workspace=root / 'work', ports=ports)
    samples = [('initialized null', deepcopy((engine.instance, engine.runtime)))]

    def keep(branch):
        engine._save()
        _, instance, runtime = store.load(engine.head)
        samples.append((branch, deepcopy((instance, runtime))))

    for index in range(2):
        request = trust_fixture(root, ['synthetic-trust-pair-' + str(index)])
        engine._trust_control(request, 'synthetic:user-adoption')
        eid = next(reversed(engine.instance['trust_environments']))
        if engine.runtime['trust_bindings'][eid] != request['binding']:
            raise AssertionError('registration changed the independent binding')
        keep('registered ' + str(index))
        engine._trust_control({'operation': 'transition', 'env_id': eid}, 'synthetic:user-adoption')
        tid = next(reversed(engine.runtime['trust_transitions']))
        keep('checking ' + str(index))
        check = check_environment(engine.instance['trust_environments'][eid],
            engine.runtime['trust_bindings'][eid], clock=clock, host=ports.host)
        if check['status'] != 'verified':
            raise AssertionError(check)
        engine._finish_trust_transition(tid, check)
        if engine.instance['active_trust_environment'] != eid:
            raise AssertionError('trust activation did not adopt the registered environment')
        keep('active ' + str(index))
    engine._trust_control({'operation': 'invalidate', 'env_id': eid, 'reason': 'User withdrawal'},
                         'synthetic:user-adoption')
    if engine.instance['active_trust_environment'] is not None:
        raise AssertionError('invalidated environment remained active')
    keep('invalidated')
    return samples


def knowledge_samples(root):
    """Creation, relation, continuity, source loss and environment loss, all stored/read.

    Relations have two independently imported endpoints; continuity replaces a
    checked formal result/exposition without altering its sealed predecessor.
    Source loss, explicit suspension and environment loss use independent copies
    of the valid baseline rather than a fixture repair of their resulting fields.
    """
    from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
    from support.entry import entry
    from support.fakes.clock import FakeClock
    from support.fakes.git_backend import InProcessGit
    from support.knowledge_builders import formal_evidence, knowledge_candidate
    from support.review_inputs import reviewed_candidate
    from support.storage_records import record_store
    from support.trust_inputs import trust_environment, trust_fixture

    clock = entry().ports.clock
    instance, runtime, kid, aid = reviewed_candidate(root, verified=True)
    store = record_store(root / 'samples', backend=InProcessGit(), clock=FakeClock())
    samples = []

    def keep(branch, state):
        head = store.initialize(*state) if not samples else store.save_with_state(
            store.load()[0], *state)[0]
        loaded, saved, running = store.load(head)
        if loaded != head or (saved, running) != state:
            raise AssertionError('knowledge producer state changed in storage: ' + branch)
        samples.append((branch, deepcopy((saved, running))))

    keep('verified review', (instance, runtime))
    # Independent branches use independent stores: immutable parents must not
    # turn source-loss versus environment-loss into successive publications.
    def branch(name, state):
        other = record_store(root / name, backend=InProcessGit(), clock=FakeClock())
        head = other.initialize(*state)
        _, saved, running = other.load(head)
        if (saved, running) != state:
            raise AssertionError('knowledge producer state changed in storage: ' + name)
        samples.append((name, deepcopy((saved, running))))

    branch('explicit suspension', (kr.set_assessment_use(instance, aid, 'suspended', 'objection', 'user'), runtime))
    branch('assessment withdrawal', (kr.set_assessment_use(instance, aid, 'withdrawn', 'withdrawal', 'user'), runtime))
    branch('source loss', k.suspend_for_source_change(instance, runtime, kid,
        source_name='input', reason='source replaced', actor_ref='user', clock=clock))
    branch('environment loss', k.invalidate_environment(instance, runtime,
        instance['active_trust_environment'], 'environment withdrawn', clock=clock))
    branch('explicit revision', k.revise_knowledge(instance, runtime, kid,
        {'explanation': 'A revised explanation'}, reason='clarify scope', actor_ref='user', clock=clock))
    branch('withdrawal', k.invalidate_knowledge(instance, runtime, kid,
        reason='withdraw this result', actor_ref='user', clock=clock))
    branch('kind withdrawal', io.withdraw_kind_definition(instance, runtime, 'knowledge', 'theorem',
        reason='withdraw this definition', actor_ref='user', clock=clock))

    eid = 'TE-continuity'
    environment, binding = trust_environment(trust_fixture(root, ['synthetic-continuity']),
        environment_id=eid, status='registered')
    successor, running = deepcopy((instance, runtime))
    successor['trust_environments'][eid] = environment
    running['trust_bindings'][eid] = binding
    transition = k.begin_transition(successor, eid, clock=clock)
    if not k.validate_basis([transition['targets'][0]['basis']], successor, running)['valid']:
        raise AssertionError('transition basis does not pass its actual currentness receiver')
    changed = deepcopy(successor)
    changed['knowledge'][kid]['title'] = 'A different mathematical proposal'
    if k.validate_basis([transition['targets'][0]['basis']], changed, running)['valid']:
        raise AssertionError('transition basis ignored changed authored content')
    transition = k.record_transition_result(successor, transition,
        {'id': kid, **formal_evidence(successor, kid, eid)})
    successor = k.activate_transition(successor, transition, at=clock.now(), clock=clock)
    transition['status'] = 'active'
    running['trust_transitions'][transition['id']] = transition
    branch('continuity', (successor, running))

    related, running = deepcopy((instance, runtime))
    related, running, endpoint = io.import_candidate(related, running,
        knowledge_candidate(title='Second endpoint', lean_code='', declaration_names=[], source_refs=[],
            confirmed_scope='Finite scope', epistemic_status='conjecture', selection_relevance='Relevant case',
            uncertainty_assessment={'scope': 'finite'}, origin_refs=['input']),
        source_ref='input', actor_ref='user', clock=clock)
    related, running, _ = io.import_candidate(related, running,
        knowledge_candidate(relation_claim={'kind': 'formally_implies', 'source': kid,
            'target': endpoint, 'confirmed_scope': 'Truth implies truth'}),
        source_ref='input', actor_ref='user', clock=clock)
    for dependencies in ([kid], [kid, endpoint]):
        related, running, _ = io.import_candidate(related, running,
            knowledge_candidate(title='Dependent result', lean_code='', declaration_names=[], dependencies=dependencies),
            source_ref='input', actor_ref='user', clock=clock)
    branch('relation claim', (related, running))
    return samples


def engine_knowledge_samples(root):
    """Actual work-bundle and incidental-insight imports on the stored engine."""
    from do_math import contracts, knowledge, knowledge_io, knowledge_records
    from support.fakes.clock import FakeClock
    from support.fakes.git_backend import InProcessGit
    from support.knowledge_builders import knowledge_candidate
    from support.record_builders import execution_state
    from support.role_answers import candidate
    from support.storage_records import engine_on, fake_ports, record_store

    clock, backend = FakeClock(), InProcessGit()
    instance, runtime = execution_state('research_work')
    runtime.update(queue=[], history=[], questions=[])
    instance = knowledge_records.initialize_families(knowledge_io.ensure_ontology(instance))
    task = contracts.task_candidate_record(candidate(), task_id='TK-pair')
    task.pop('revises_task_id')
    task['status'] = 'planned'
    runtime['tasks'] = {task['id']: task}
    store = record_store(root / 'engine', clock=clock, backend=backend)
    engine, _ = engine_on(store, instance, runtime, workspace=root / 'work', ports=fake_ports(clock, backend))
    action = {'id': 'AC-pair', 'role': 'research_work', 'target': task['id']}
    ids = engine._import_research_records(action, {'knowledge': [knowledge_candidate(
        kind='observation', title='Produced work', lean_code='', declaration_names=[])], 'relations': []}, 'EX-1')
    engine._save()
    _, instance, runtime = store.load(engine.head)
    samples = [('work bundle', deepcopy((instance, runtime)))]
    original = engine.head
    engine.instance, engine.runtime = knowledge.invalidate_knowledge(engine.instance, engine.runtime,
        ids[0], reason='evidence withdrawn after input', actor_ref='user', clock=clock)
    # The original evidence was withdrawn after the input snapshot. The actual
    # currentness check must therefore publish a suspended incidental insight.
    engine.runtime['executions']['EX-1'].update(input_snapshot=original, extensions={'research_insights': [{
        'kind': 'observation', 'title': 'Incidental result', 'statement': 'Bounded observation',
        'summary': 'Needs current evidence', 'evidence_ids': ids}]})
    engine._apply_extensions(action, 'EX-1')
    incidental, = [row for row in engine.instance['knowledge'].values() if row['id'] not in ids]
    if incidental.get('use_suspended') is not True or not incidental.get('use_suspensions'):
        raise AssertionError('changed incidental evidence was not suspended')
    engine._save()
    _, instance, runtime = store.load(engine.head)
    samples.append(('incidental changed evidence', deepcopy((instance, runtime))))
    return samples


def _registered_review_scene(root):
    from do_math.execution_lifecycle import transition_execution
    from support.review_scene import ReviewScene
    scene = ReviewScene(root)
    engine, clock = scene.engine, scene.engine.ports.clock
    author = engine._register_execution({'id': 'AC-pair-author', 'role': 'research_work'},
        {'id': 'author', 'role': 'research_work', 'status': 'running'})
    if author is None:
        raise AssertionError('author registration failed')
    transition_execution(author, 'stopping', at=clock.now())
    transition_execution(author, 'ended', at=clock.now(), outcome='execution_incomplete')
    return scene


def identity_samples(root):
    """Real admission/publication of a relation review and a changed-proof transition.

    ReviewScene supplies only its stored start state. Actual owner registration
    supplies complete executions; synthetic reviewer answers bypass transport.
    """
    from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
    from support.knowledge_builders import formal_evidence, knowledge_candidate
    from support.trust_inputs import trust_environment, trust_fixture

    samples = []
    scene = _registered_review_scene(root / 'review')
    engine, clock = scene.engine, scene.engine.ports.clock
    from do_math.execution_lifecycle import transition_execution
    from support.review_inputs import review_stage_output, scope_assessment

    def execute_review():
        action = scene.pending()
        execution = engine._register_execution(action, {'id': clock.new_id('EX'), 'role': 'identity_review',
            'status': 'running', 'input_snapshot': engine.head,
            'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        if execution is None:
            raise AssertionError('review registration failed')
        prepared = engine._prepare_review_context(action, root / execution['id'])
        if prepared['disposition'] != 'ready':
            raise AssertionError(prepared)
        keep('pending ' + execution['id'])
        execution = engine.runtime['executions'][execution['id']]
        cycle = engine.runtime['review_cycles'][action['review_cycle_id']]
        output = review_stage_output(cycle, action['stage'])
        if action['stage'] == 'scope':
            output.update(scope_complete=True, scope_assessment=scope_assessment(
                cycle['review_policy'], ['initial-0', 'initial-1']))
        engine.runtime['queue'].remove(action)
        engine._apply_identity_review(action, output, execution['id'])
        execution.update(output=deepcopy(output), submission_receipt={
            'state': 'accepted', 'evidence_ref': 'synthetic:review-pair'})
        transition_execution(execution, 'stopping', at=clock.now())
        transition_execution(execution, 'ended', at=clock.now(), outcome='output_accepted')

    def keep(branch):
        engine._save()
        _, instance, runtime = engine.store.load(engine.head)
        samples.append((branch, deepcopy((instance, runtime))))

    engine.instance, engine.runtime, endpoint = io.import_candidate(engine.instance, engine.runtime,
        knowledge_candidate(title='Relation endpoint', lean_code='', declaration_names=[]),
        source_ref='input', actor_ref='user', clock=clock)
    fid = engine.instance['knowledge']['K1']['formal_result_id']
    engine.instance, engine.runtime, kid = io.import_candidate(engine.instance, engine.runtime,
        knowledge_candidate(title='Relation judgment', formal_result_ref=fid, lean_code='', declaration_names=[],
            relation_claim={'kind': 'formally_implies', 'source': 'K1', 'target': endpoint,
                            'confirmed_scope': 'The exact relation'}),
        source_ref='input', actor_ref='user', clock=clock)
    # This direct mixin test consumes the import's unbound scheduling request
    # when opening its cycle, as the owner does before queuing concrete seats.
    engine.runtime['queue'][:] = [action for action in engine.runtime['queue']
                                  if not (action['role'] == 'identity_review' and action.get('target') == kid)]
    engine._start_identity_review(kid)
    execute_review()
    execute_review()
    execute_review()
    keep('relation assessment')

    eid = 'TE-staged-pair'
    environment, binding = trust_environment(trust_fixture(root, ['synthetic-staged-pair']),
        environment_id=eid, status='registered')
    engine.instance['trust_environments'][eid] = environment
    engine.runtime['trust_bindings'][eid] = binding
    transition = k.begin_transition(engine.instance, eid, clock=clock)
    for target in transition['targets']:
        result = formal_evidence(engine.instance, target['id'], eid)
        # This independently supplied compiler observation changes the proof
        # term, requiring the actual staged review rather than continuity reuse.
        for declaration in result['declaration_evidence'].values():
            declaration['value'] = 'independent staged proof term'
        transition = k.record_transition_result(engine.instance, transition, {'id': target['id'], **result})
    engine.runtime['trust_transitions'][transition['id']] = transition
    candidate = deepcopy(transition)
    for target in transition['targets']:
        cid = engine._start_staged_identity_review(transition['id'], target['id'])
        for _ in range(3):
            execute_review()
        candidate['results'][target['id']]['identity_review'] = engine._completed_staged_identity_review(
            transition['id'], target['id'], cid)
    engine.instance = k.activate_transition(engine.instance, candidate, runtime=engine.runtime,
        at=clock.now(), clock=clock)
    engine.runtime['trust_transitions'][transition['id']]['status'] = 'active'
    keep('staged identity activation')
    return samples


def replacement_samples(root):
    """Actual recovery and grant-authorized transcript replacement, before model transport."""
    from do_math.review_cycle import record_turn
    from support.review_inputs import grant_replacement
    scene = _registered_review_scene(root / 'replacement')
    engine = scene.engine
    grant_replacement(engine)
    cid = engine._start_identity_review('K1')
    action = scene.pending()
    engine._activity_for_action(action)
    cycle = record_turn(engine.runtime['review_cycles'][cid], action['slot'], [
        {'role': 'user', 'content': 'Preserved source', 'message_id': 'good'},
        {'role': 'tool', 'content': 'Lost source', 'message_id': 'bad'}])
    cycle['turns'][action['slot']][1]['content'] = 'Damaged bytes'
    engine.runtime['review_cycles'][cid] = cycle
    outcome = engine._prepare_review_context(action, root / 'damaged-input')
    if outcome['disposition'] != 'recovery_recorded':
        raise AssertionError(outcome)
    outcome = engine._authorize_review_replacement(action, grant_id='GR-review')
    if outcome['disposition'] != 'replacement_ready':
        raise AssertionError(outcome)
    replacement, = [a for a in engine.runtime['queue'] if a.get('replacement_for') is not None]
    outcome = engine._prepare_review_context(replacement, root / 'replacement-input')
    if outcome['disposition'] != 'ready':
        raise AssertionError(outcome)
    engine._save()
    _, instance, runtime = engine.store.load(engine.head)
    return [('grant-authorized transcript replacement', deepcopy((instance, runtime)))]
