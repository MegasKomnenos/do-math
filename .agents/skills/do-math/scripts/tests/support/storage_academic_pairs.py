"""Actual goal/academic producers and exact validated repository publications.

The domain engine, TASKS application and repository are real. Clock, Git,
host, compiler and model answers are existing port doubles. No stored field
is filled after production. Open evidence/maps keep their existing contract.
"""
from copy import deepcopy

from contracts.pairs import Pair
from support.storage_authority_pairs import _named_fields

FAMILIES = (('research', 'goal_judgments'), ('research', 'goal_assessment_basis'),
            ('research', 'goal_status'), ('runtime', 'academic_assessments'),
            ('runtime', 'external_rejections'), ('runtime', 'academic_resolution_records'))


def family_pair(contract, root, family, samples):
    """Explicit projection for list records, scalars and the typed list singleton."""
    from do_math.state_contract import validate_record
    definition = contract.family(root, family)
    index = 0 if root == 'research' else 1
    scalar = family in {'goal_status', 'goal_assessment_basis'}
    typed_list = family == 'academic_assessments'
    # _named_fields already owns the closed nested-field walk. Wrap the typed
    # singleton so its actual item/basis/evidence fields participate too.
    schema = {'properties': {'items': definition.schema}} if typed_list else definition.schema

    def values(state):
        if family not in state[index]:
            return []
        value = state[index][family]
        return [value] if scalar or typed_list else value

    def receive(state):
        for value in values(state):
            validate_record(definition.checker, value, root + '/' + family)
            if definition.validator:
                definition.validator(value)

    def written(state):
        rows = values(state)
        if scalar:
            return {'/value'} if rows else set()
        projected = [{'items': row} for row in rows] if typed_list else rows
        return _named_fields(schema, projected)

    return Pair(root + '.' + family, lambda unused: samples, receive,
                frozenset({'/value'} if scalar else _named_fields(schema)), written)


def _keep(engine, samples, branch, artifacts=None):
    """Every sample is a loaded publication; the previous head remains exact."""
    from do_math.record_schemas import install
    from do_math.repository import ResearchRepository
    from do_math.state_contract import StateContract
    old = engine.store.load(engine.head)
    expected = deepcopy((engine.instance, engine.runtime))
    engine._save(artifacts)
    # A separately installed contract gives this reader its own validation
    # cache key: it decodes stored blobs rather than reusing the writer's view.
    contract = StateContract()
    install(contract)
    reader = ResearchRepository(engine.store.repository, engine.instance['id'], contract=contract,
        backend=engine.ports.git_backend, clock=engine.ports.clock)
    head, instance, runtime = reader.load(engine.head)
    # _save also updates unrelated lifecycle timestamps. Compare each target's
    # pre-publication content, including presence, without inventing those times.
    actual = (instance, runtime)
    if head != engine.head or any(
            (family in actual[index]) != (family in expected[index])
            or actual[index].get(family) != expected[index].get(family)
            for root, family in FAMILIES for index in [0 if root == 'research' else 1]):
        raise AssertionError('producer content changed in storage: ' + branch)
    if reader.load(old[0]) != old:
        raise AssertionError('previous head changed: ' + branch)
    if artifacts and reader.read_many(list(artifacts), head) != artifacts:
        raise AssertionError('stored artifact bytes changed: ' + branch)
    samples.append((branch, deepcopy((instance, runtime))))


def goal_samples(root):
    from do_math import knowledge
    from do_math.governance import governance_view
    from jsonschema import Draft202012Validator
    from support.academic_scenes import theorem_sim, theorem_id, ended, MANUSCRIPT
    from support.engine_lifecycle import applied, clear_work
    from support.governance_sim import adopt_audit
    from support.state_builders import charter_change

    sim, samples = theorem_sim(), []
    engine = sim.engine
    _keep(engine, samples, 'unsolved without judgments')
    applied(sim, 'decision', config={'change': charter_change(engine, academic_requirements=[MANUSCRIPT])})
    adopt_audit(sim)
    clear_work(sim)
    basis, required = engine._goal_basis_key(), engine.instance['config']['goal_auditors']
    kid = theorem_id(sim)
    for slot in range(required):
        eid = 'EX-stored-goal-' + str(slot)
        execution = ended(engine, eid, 'goal_audit')
        action = {'role': 'goal_audit', 'basis': basis, 'slot': slot, 'required': required}
        engine._bind_governance_input(action, execution, engine._governance_context(action, {}))
        output = {'decision': 'satisfied', 'scope_complete': True,
            'used_sources': [kid] if slot == 0 else [], 'questions': [],
            'summary': 'Exact stored goal audit', 'reason': 'The supplied theorem establishes the approved scope',
            'additional_audits': [{'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'pass',
                'reason': 'The supplied charter scope is covered',
                'input_hashes': execution['additional_audit_input'][0]['input_hashes']}]}
        Draft202012Validator(engine._response_schema(action)).validate(output)
        engine._apply(action, output, eid)
        _keep(engine, samples, 'independent goal slot ' + str(slot))
    if engine.instance['goal_status'] != 'mathematically_solved':
        raise AssertionError('the complete actual audit group did not establish the goal')
    charter = governance_view(engine.instance)['charter']
    if any(row['goal_revision'] != charter['revision'] for row in engine.instance['goal_judgments']):
        raise AssertionError('judgments lost the actual charter edition')
    engine.instance, engine.runtime = knowledge.invalidate_knowledge(engine.instance, engine.runtime, kid,
        reason='Withdraw the exact mathematical premise', actor_ref='user', clock=sim.clock)
    engine._invalidate_goal_currentness()
    _keep(engine, samples, 'withdrawn dependency invalidates goal')
    return samples


def assessment_samples(root):
    from support.academic_assessment_cases import assessed_case
    samples = []
    for decision, arguments in (('satisfied', {}), ('not_satisfied', {'decision': 'incomplete'}),
                                ('unresolved', {'unresolved': True})):
        sim, tid, assessment, eid = assessed_case(**arguments)
        engine = sim.engine
        engine._record_academic_assessment(engine.runtime['tasks'][tid], assessment, eid)
        _keep(engine, samples, decision)
    return samples


ACTOR = ' 심사자 e\u0301 '
REJECTION = ' 원문 e\u0301\r\n논증의 경계를 설명하라.\n '
RESPONSE = ' 답변 e\u0301\r\n유한 범위의 근거.\n'.encode('utf-8')
EVIDENCE_REF = 'runtime/artifacts/BA-academic-pair/response.md'


def resolution_samples(root):
    from support.academic_resolution_cases import rejection_case
    samples = []
    sim, eid, resolution = rejection_case(actor=ACTOR, text=REJECTION)
    engine = sim.engine
    _keep(engine, samples, 'exact external rejection', {EVIDENCE_REF: RESPONSE})
    for decision in ('unresolved', 'resolved'):
        engine._apply_academic_resolutions({'role': 'research_plan'}, eid,
            [{**resolution, 'decision': decision, 'evidence_refs': [EVIDENCE_REF]}])
        _keep(engine, samples, decision)
    return samples
