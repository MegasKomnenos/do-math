"""Small staged states using the existing stored review scene and domain producers."""
from copy import deepcopy


def staged_states(root):
    from do_math import knowledge
    from do_math.execution_lifecycle import transition_execution
    from support.knowledge_builders import formal_evidence
    from support.review_inputs import review_stage_output, scope_assessment
    from support.storage_knowledge_pairs import _registered_review_scene
    from support.trust_inputs import trust_environment, trust_fixture

    scene = _registered_review_scene(root)
    engine, clock = scene.engine, scene.engine.ports.clock
    environment, binding = trust_environment(trust_fixture(root, ['state-staged']),
        environment_id='TE-state-staged', status='registered')
    engine.instance['trust_environments'][environment['id']] = environment
    engine.runtime['trust_bindings'][environment['id']] = binding
    transition = knowledge.begin_transition(engine.instance, environment['id'], clock=clock)
    result = formal_evidence(engine.instance, 'K1', environment['id'])
    for declaration in result['declaration_evidence'].values():
        declaration['value'] = 'independently observed changed proof term'
    transition = knowledge.record_transition_result(engine.instance, transition, {'id': 'K1', **result})
    engine.runtime['trust_transitions'][transition['id']] = transition
    cid = engine._start_staged_identity_review(transition['id'], 'K1')
    pending = None
    for _ in range(3):
        action = scene.pending()
        execution = engine._register_execution(action, {'id': clock.new_id('EX'), 'role': 'identity_review',
            'status': 'running', 'input_snapshot': engine.head,
            'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        prepared = engine._prepare_review_context(action, root / execution['id'])
        if prepared['disposition'] != 'ready':
            raise AssertionError(prepared)
        engine._record_review_input(action, execution['id'])
        if pending is None:
            pending = deepcopy((engine.instance, engine.runtime))
        cycle = engine.runtime['review_cycles'][cid]
        output = review_stage_output(cycle, action['stage'])
        if action['stage'] == 'scope':
            output.update(scope_complete=True, scope_assessment=scope_assessment(
                cycle['review_policy'], ['initial-0', 'initial-1']))
        engine.runtime['queue'].remove(action)
        engine._apply_identity_review(action, output, execution['id'])
        execution.update(output=deepcopy(output), submission_receipt={
            'state': 'accepted', 'evidence_ref': 'synthetic:state-review'})
        transition_execution(execution, 'stopping', at=clock.now())
        transition_execution(execution, 'ended', at=clock.now(), outcome='output_accepted')
    candidate = deepcopy(transition)
    candidate['results']['K1']['identity_review'] = engine._completed_staged_identity_review(transition['id'], 'K1', cid)
    engine.instance = knowledge.activate_transition(engine.instance, candidate, runtime=engine.runtime,
        at=clock.now(), clock=clock)
    engine.runtime['trust_transitions'][transition['id']]['status'] = 'active'
    return engine.store, pending, deepcopy((engine.instance, engine.runtime)), cid, transition['id']
