"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
from do_math.lean_evidence import lean_source_sha256
from do_math.canonical import exact_content_hash


def knowledge_candidate(**changes):
    value = dict(kind='theorem', title='Truth', statement='True', explanation='Truth holds',
                 summary='Truth', lean_code='theorem truth : True := True.intro',
                 declaration_names=['truth'], dependencies=[])
    value.update(changes)
    return value


def formal_result(source, declarations, toolchain, *, closure=('True', 'True.intro'),
                  dependency_evidence=('fixture-type', 'fixture-value'),
                  declaration_evidence=('fixture-type', 'fixture-proof'), **extra):
    """A verified compiler result for ``source``; ``extra`` adds fields such as ``allowed_axioms``.

    ``dependency_evidence`` labels the closure's bodies; the result stores their hashes."""
    return dict(status='verified', source_sha256=lean_source_sha256(source),
        declarations=list(declarations), toolchain=deepcopy(toolchain), **extra,
        axioms={n: [] for n in declarations}, dependency_closure={n: list(closure) for n in declarations},
        dependency_evidence={name: exact_content_hash(label) for name, label in zip(closure, dependency_evidence)},
        declaration_evidence={n: {'type': declaration_evidence[0], 'value': declaration_evidence[1]}
                              for n in declarations})


def formal_evidence(state, kid, env='TE-old'):
    formal = state['formal_results'][state['knowledge'][kid]['formal_result_id']]
    return formal_result(formal['lean_code'], formal['declaration_names'],
                         state['trust_environments'][env]['toolchain'])


def seal_knowledge(state, runtime, kid, env='TE-old'):
    from support.entry import entry
    _entry = entry()
    state = kr.record_formal_result(state, kid, formal_evidence(state, kid, env), env, runtime=runtime)
    return kr.record_identity_assessment(state, kid,
        {'decision': 'match', 'basis': kr.identity_basis(state, kid)}, 'policy:fixture', runtime=runtime, clock=_entry.ports.clock)


def add_knowledge(state, runtime, *, verified=True, **changes):
    from support.entry import entry
    _entry = entry()
    state, runtime, kid = io.import_candidate(state, runtime, knowledge_candidate(**changes),
                                              source_ref='fixture', actor_ref='producer', clock=_entry.ports.clock)
    aid = None
    if verified: state, aid = seal_knowledge(state, runtime, kid)
    return state, runtime, kid, aid


def knowledge_graph():
    from support.entry import entry
    _entry = entry()
    state = {'active_trust_environment': 'TE-old', 'trust_environments': {
        'TE-old': {'id': 'TE-old', 'status': 'active', 'toolchain': {'version': 'fixture-old'}, 'allowed_axioms': [],
                   'source_ref': 'fixture:trust', 'toolchain_record': {'path': str(Path.cwd() / 'records' / ('TC-' + '0' * 64 + '.json')),
                                                                        'id': 'TC-' + '0' * 64}}}}
    runtime = {'tasks': {}, 'queue': [], 'history': []}
    state, runtime, a, aa = add_knowledge(state, runtime)
    state, runtime, b, ba = add_knowledge(state, runtime, dependencies=[a])
    state, runtime, c, ca = add_knowledge(state, runtime)
    relation, goal, task, unrelated = (_entry.ports.clock.new_id(p) for p in ('RL', 'GJ', 'TK', 'TK'))
    state['relations'] = [{'id': relation, 'source': a, 'target': c, 'status': 'active'}]
    state['goal_judgments'] = [{'id': goal, 'used_sources': [b], 'current': True}]
    runtime['tasks'] = {task: {'id': task, 'status': 'completed', 'inputs': [b], 'assessment': {'decision': 'completed', 'current': True}},
                       unrelated: {'id': unrelated, 'status': 'completed', 'inputs': [c]}}
    return state, runtime, dict(a=a, b=b, c=c, aa=aa, ba=ba, ca=ca, relation=relation, goal=goal, task=task, unrelated=unrelated)


def impact_declaration(state, runtime, roots):
    # Model a complete producer declaration; tests separately assert its locality.
    return k.plan_impact(state, runtime, roots, [])['computed_impact']


def revise_knowledge(state, runtime, kid, changes=None):
    from support.entry import entry
    _entry = entry()
    changes = changes or {'statement': 'Revised statement'}
    return k.revise_knowledge(state, runtime, kid, changes, reason='correction', actor_ref='author',
        declared_impact=impact_declaration(state, runtime, k.revision_roots(state, kid)), clock=_entry.ports.clock)


def verified_knowledge(environment=None, *, binding=None, identity=True, check=None):
    from support.entry import entry
    _entry = entry()
    proposed = knowledge_candidate()
    state, runtime, kid = io.import_candidate({}, {}, proposed, source_ref="source", actor_ref="producer", clock=_entry.ports.clock)
    state.update(active_trust_environment="TE-test", trust_environments={"TE-test": {
        "id": "TE-test", "status": "active", "toolchain": {"version": "test-fixture"}, "allowed_axioms": []}})
    if environment is not None:
        state['trust_environments']['TE-test'] = deepcopy(environment)
    if binding is not None:
        runtime['trust_bindings'] = {'TE-test': deepcopy(binding)}
    verification = formal_result(proposed["lean_code"], ["truth"], state['trust_environments']['TE-test']['toolchain'],
                                 dependency_evidence=('fixture-type', 'fixture-constructor'),
                                 declaration_evidence=('True', 'True.intro'), **(check or {}))
    state = kr.record_formal_result(state, kid, verification, "TE-test", runtime=runtime)
    if not identity:
        return state, runtime, kid, None
    state, aid = kr.record_identity_assessment(state, kid,
        {"decision": "match", "basis": kr.identity_basis(state, kid), "review_cycle_id": "RC-fixture"}, "policy:1", runtime=runtime, clock=_entry.ports.clock)
    return state, runtime, kid, aid
