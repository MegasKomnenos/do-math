"""Input/extension producers with validated publications and cold decoding.

Only external ports are doubles. Samples are never filled to satisfy a schema.
The open per-cycle insight content has one value obligation, then independent
content assertions; pending kind items have their own closed field obligation.
"""
from copy import deepcopy
from pathlib import Path

from contracts.pairs import Pair
from do_math.repository import ResearchRepository
from do_math.state_contract import validate_record
from support.state_builders import installed_contract
from support.storage_authority_pairs import _named_fields
from support.storage_kind_checks import kind_scene, propose_kinds

FAMILIES = (('research', 'sources'), ('runtime', 'inputs'),
            ('runtime', 'private_insights'), ('runtime', 'pending_kind_checks'))


def reader(engine):
    return ResearchRepository(engine.store.repository, engine.store._store.instance_id, contract=installed_contract(),
        backend=engine.ports.git_backend, clock=engine.ports.clock)


def keep(engine, samples, branch, *, previous=None):
    cold = reader(engine)
    loaded = cold.load(engine.head)
    if loaded != (engine.head, engine.instance, engine.runtime):
        raise AssertionError('cold decode differs from producer: ' + branch)
    if previous is not None and cold.load(previous[0]) != previous:
        raise AssertionError('previous head changed: ' + branch)
    samples.append((branch, deepcopy(loaded[1:])))
    return loaded


def family_pair(contract, root, name, samples):
    family = contract.family(root, name)
    index = 0 if root == 'research' else 1
    pending, opened = name == 'pending_kind_checks', name == 'private_insights'
    schema = family.schema['items'] if pending else family.schema

    def records(state):
        if name not in state[index]:
            return []
        value = state[index][name]
        return [value] if family.shape == 'singleton' else value

    def receive(state):
        for value in records(state):
            validate_record(family.checker, value, root + '/' + name)
            if family.validator:
                family.validator(value)

    def written(state):
        values = records(state)
        if opened:
            return {'/value'} if values else set()
        if pending:
            values = [item for value in values for item in value]
        return _named_fields(schema, values)

    return Pair(root + '.' + name, lambda path: samples, receive,
        frozenset({'/value'} if opened else _named_fields(schema)), written)


def public_input_samples(root):
    """Initialization's empty list/file input, followed by exact inbox records."""
    from do_math.control_contracts import normalized_source
    from support.sim import Sim
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    raw = '원문 e\u0301 \u212a\r\n다음 줄\n'.encode('utf-8') + b'\x00\xff'
    source = root / 'e\u0301.bin'
    source.write_bytes(raw)
    # Separate actual initialization branches; neither fabricates a stored row.
    empty = Sim(root / 'empty', goal='최초 e\u0301\r\n입력\n')
    samples = []
    keep(empty.engine, samples, 'empty sources and initial input')
    sim = Sim(root / 'files', goal='최초 e\u0301\r\n입력\n', sources=[source])
    keep(sim.engine, samples, 'initial file')
    requests = []
    for branch, body in (('same initial bytes', raw), ('changed bytes', raw + b'next\r\n'),
                         ('same changed bytes', raw + b'next\r\n')):
        previous = reader(sim.engine).load(sim.engine.head)
        request = sim.control('source', config=normalized_source(source.name, body),
                              request_id='UC-' + branch.replace(' ', '-'))
        sim.engine.process_controls()
        requests.append((branch, request, body))
        keep(sim.engine, samples, branch, previous=previous)
    previous = reader(sim.engine).load(sim.engine.head)
    spec = normalized_source('추가.bin', b'\x80\x00new\r\n')
    added = sim.control('source', config=spec, request_id='UC-new-source')
    sim.engine.process_controls()
    requests.append(('new source', added, spec))
    keep(sim.engine, samples, 'new source', previous=previous)
    for number, text in enumerate(('첫 추가 e\u0301\r\n', '두 번째 \u212a\n')):
        config = {'responds_to': []}
        previous = reader(sim.engine).load(sim.engine.head)
        envelope = sim.control('input', text=text, config=config, request_id=f'UC-input-{number}')
        sim.engine.process_controls()
        requests.append(('input', envelope, (text, config)))
        keep(sim.engine, samples, f'input {number}', previous=previous)
        if number == 0:
            replay = sim.control('input', text=text, config=config, request_id=f'UC-input-{number}')
            sim.engine.process_controls()
            if replay['request_id'] != envelope['request_id']:
                raise AssertionError('replay identity changed')
            sim.restart()
            keep(sim.engine, samples, 'replayed and restarted')
    return sim, samples, source.name, raw, requests


def pending_kind_scene(root):
    sim = kind_scene()
    engine = sim.engine
    samples = []
    keep(engine, samples, 'no proposals')
    definitions = propose_kinds(engine)
    keep(engine, samples, 'two proposals')
    return sim, samples, definitions


def review_insight_scene(root, *, unresolved=False, withdraw_held=False):
    """Two actual review cycles; layer-2 synthetic replies, real registration/application."""
    from do_math import knowledge_io, knowledge_records as kr
    from do_math.execution_lifecycle import transition_execution
    from support.engine_lifecycle import _ended_execution
    from support.review_scene import ReviewScene
    from support.review_inputs import review_stage_output, scope_assessment
    scene = ReviewScene(root)
    engine = scene.engine
    _ended_execution(engine, 'author', 'research_work')
    # A separate candidate/cycle has the same immutable proof, its own identity.
    proposal = kr.proposal_view(engine.instance, 'K1')
    candidate = dict(id='K-other', kind='theorem', title='Independent cycle',
        statement='One equals one', summary='A second exposition', explanation='By reflexivity',
        lean_code=proposal['lean_code'], declaration_names=proposal['declaration_names'],
        dependencies=[], revision=1, kind_definition_id=proposal['kind_definition_id'],
        formal_result_ref=proposal['formal_result_id'])
    engine.instance, _ = kr.create_candidate(engine.instance, candidate,
        source_ref='author', actor_ref='author', clock=engine.ports.clock)
    primary = engine._start_identity_review('K1')
    other = engine._start_identity_review('K-other')
    samples, authored = [], []

    def execute(cid, insights=None, *, incomplete=False):
        previous = reader(engine).load(engine.head)
        action = next(a for a in engine.runtime['queue'] if a.get('review_cycle_id') == cid)
        identifier = engine.ports.clock.new_id('EX')
        execution = engine._register_execution(action, {'id': identifier, 'role': 'identity_review', 'status': 'running',
            'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        if execution is None:
            raise AssertionError('review was not admitted')
        prepared = engine._prepare_review_context(action, Path(root) / identifier)
        if prepared['disposition'] != 'ready':
            raise AssertionError(prepared)
        execution.update(input_snapshot=engine.head, extensions={'research_insights': deepcopy(insights or [])})
        for insight in insights or []:
            knowledge_io.validate_insight(engine.instance, engine.runtime, insight)
        output = review_stage_output(engine.runtime['review_cycles'][cid], action['stage'])
        if action['stage'] == 'scope':
            output.update(scope_complete=True, scope_assessment=scope_assessment(
                engine.runtime['review_cycles'][cid]['review_policy'], ['initial-0', 'initial-1']))
        if incomplete:
            output.update(decision='unresolved', scope_complete=False)
        engine.runtime['queue'].remove(action)
        engine._apply_identity_review(action, output, identifier)
        execution.update(output=deepcopy(output), submission_receipt={
            'state': 'accepted', 'evidence_ref': 'synthetic:input-storage-review'})
        for status in ('stopping', 'ended'):
            transition_execution(execution, status, at=engine.ports.clock.now(),
                                 **({'outcome': 'output_accepted'} if status == 'ended' else {}))
        engine._apply_extensions(action, identifier)
        engine._save()
        if insights is not None:
            authored.append((identifier, deepcopy(insights)))
        keep(engine, samples, identifier, previous=previous)
        return identifier

    execute(primary)
    execute(other)
    originals = [dict(kind='observation' if withdraw_held else 'question',
                      title='원 통찰 ' + str(i), statement='질문 e\u0301\r\n' + str(i),
                      summary='순서 ' + str(i), evidence_ids=[]) for i in range(2)]
    first = execute(primary, originals)
    isolated = dict(kind='observation', title='별도 cycle', statement='격리된 원문', summary='격리', evidence_ids=[])
    second = execute(other, [isolated])
    if withdraw_held:
        engine.instance, engine.runtime = knowledge_io.withdraw_kind_definition(engine.instance, engine.runtime,
            'knowledge', 'observation', reason='의미 철회', actor_ref='user', clock=engine.ports.clock)
    final = dict(kind='question', title='마지막 통찰', statement='마지막 원문', summary='마지막', evidence_ids=[])
    # The second initial reply finishes match or unresolved via the real review producer.
    last = execute(primary, [final], incomplete=unresolved)
    return engine, samples, primary, other, authored, (first, second, last)
