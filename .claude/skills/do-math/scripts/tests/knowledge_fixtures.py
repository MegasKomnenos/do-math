"""Knowledge candidates, their synthetic formal evidence and small knowledge states.

Compiler results here are explicit doubles (``formal_result``), never a Lean
run; identity assessments are recorded directly, never reviewed.

- ``knowledge_candidate(**changes)``: the theorem candidate "Truth"
  (``theorem truth : True := True.intro``); ``changes`` replace its fields.
- ``formal_result(source, declarations, toolchain, ...)``: a verified compiler
  result for ``source``; every declaration depends on ``closure`` and carries
  the given dependency and declaration evidence strings.
- ``formal_evidence(state, kid, env='TE-old')``: ``formal_result`` for the
  stored formal record of ``kid`` under trust environment ``env``.
- ``seal_knowledge(state, runtime, kid, env='TE-old')``: record that evidence and a
  matching identity assessment; returns ``(state, assessment ID)``.
- ``add_knowledge(state, runtime, *, verified=True, **changes)``: import a
  candidate and seal it; returns ``(state, runtime, kid, assessment ID)``.
- ``knowledge_graph()``: ``(state, runtime, ids)``, three sealed records ``a``,
  ``b`` (depends on ``a``) and ``c`` with a relation ``a``→``c``, a current goal
  judgment using ``b`` and completed tasks using ``b`` and ``c``.
- ``impact_declaration(state, runtime, roots)``: the complete computed impact a
  producer declares; ``revise_knowledge`` revises one record with it.
- ``verified_knowledge(environment=None, *, binding=None, identity=True, check=None)``:
  ``(state, runtime, kid, assessment ID)``, the candidate verified under
  ``TE-test`` and (unless ``identity=False``) assessed as a match. ``check``
  adds fields of the stored central check, such as its raw output.
- ``formal_boundary_engine(workspace, toolchain=None)``: ``(engine, kid)``, a
  bare engine with an adopted trust environment ``TE-old`` (the installed
  ``toolchain`` when given, else a synthetic one) and one unverified candidate
  whose formal check replaces admission, storage and review start with autospec
  doubles; its verifier returns ``formal_evidence``.
"""
from copy import deepcopy
from pathlib import Path

from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
from do_math.lean_evidence import lean_source_sha256
from do_math.canonical import exact_content_hash
from do_math.system_clock import new_id


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
    state = kr.record_formal_result(state, kid, formal_evidence(state, kid, env), env, runtime=runtime)
    return kr.record_identity_assessment(state, kid,
        {'decision': 'match', 'basis': kr.identity_basis(state, kid)}, 'policy:fixture', runtime=runtime)


def add_knowledge(state, runtime, *, verified=True, **changes):
    state, runtime, kid = io.import_candidate(state, runtime, knowledge_candidate(**changes),
                                              source_ref='fixture', actor_ref='producer')
    aid = None
    if verified: state, aid = seal_knowledge(state, runtime, kid)
    return state, runtime, kid, aid


def knowledge_graph():
    state = {'active_trust_environment': 'TE-old', 'trust_environments': {
        'TE-old': {'id': 'TE-old', 'status': 'active', 'toolchain': {'version': 'fixture-old'}, 'allowed_axioms': [],
                   'source_ref': 'fixture:trust', 'toolchain_record': {'path': str(Path.cwd() / 'records' / ('TC-' + '0' * 64 + '.json')),
                                                                        'id': 'TC-' + '0' * 64}}}}
    runtime = {'tasks': {}, 'queue': [], 'history': []}
    state, runtime, a, aa = add_knowledge(state, runtime)
    state, runtime, b, ba = add_knowledge(state, runtime, dependencies=[a])
    state, runtime, c, ca = add_knowledge(state, runtime)
    relation, goal, task, unrelated = (new_id(p) for p in ('RL', 'GJ', 'TK', 'TK'))
    state['relations'] = [{'id': relation, 'source': a, 'target': c, 'status': 'active'}]
    state['goal_judgments'] = [{'id': goal, 'used_sources': [b], 'current': True}]
    runtime['tasks'] = {task: {'id': task, 'status': 'completed', 'inputs': [b], 'assessment': {'decision': 'completed', 'current': True}},
                       unrelated: {'id': unrelated, 'status': 'completed', 'inputs': [c]}}
    return state, runtime, dict(a=a, b=b, c=c, aa=aa, ba=ba, ca=ca, relation=relation, goal=goal, task=task, unrelated=unrelated)


def impact_declaration(state, runtime, roots):
    # Model a complete producer declaration; tests separately assert its locality.
    return k.plan_impact(state, runtime, roots, [])['computed_impact']


def revise_knowledge(state, runtime, kid, changes=None):
    changes = changes or {'statement': 'Revised statement'}
    return k.revise_knowledge(state, runtime, kid, changes, reason='correction', actor_ref='author',
        declared_impact=impact_declaration(state, runtime, k.revision_roots(state, kid)))


def verified_knowledge(environment=None, *, binding=None, identity=True, check=None):
    proposed = knowledge_candidate()
    state, runtime, kid = io.import_candidate({}, {}, proposed, source_ref="source", actor_ref="producer")
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
        {"decision": "match", "basis": kr.identity_basis(state, kid), "review_cycle_id": "RC-fixture"}, "policy:1", runtime=runtime)
    return state, runtime, kid, aid


def formal_boundary_engine(workspace, toolchain=None):
    from unittest.mock import Mock, create_autospec
    from do_math import activities
    from do_math.trust_validation import environment_errors
    from research_fixtures import bare_engine, trust_environment, trust_fixture, validation_fixture
    e = bare_engine()
    request = trust_fixture(workspace, toolchain['configured_command'] if toolchain else ['fixture'])
    if toolchain is not None:
        # The actual installation. Its content baseline is a double: only
        # --rerecord and --check-contents read it.
        from do_math import trust_inventory as records
        from do_math.canonical import exact_content_hash
        identity = deepcopy(toolchain)
        record = records.new_record(identity, records.new_baseline(records.observe_fingerprint(identity),
            {'files': {}, 'sha256': exact_content_hash({})}, validation_fixture(identity, workspace / 'smoke.lean')))
        path = workspace / 'records' / (record['id'] + '.json')
        records.write_record(path, record)
        request.update(toolchain=identity, toolchain_record={'path': str(path), 'id': record['id']},
                       binding=records.binding(record))
    trust, binding = trust_environment(request, environment_id='TE-old', source_ref='synthetic:test-adoption')
    errors = environment_errors(trust, binding)
    if errors:
        raise AssertionError('The synthetic trust environment does not validate: ' + repr(errors))
    e.instance = {'active_trust_environment': 'TE-old', 'trust_environments': {'TE-old': trust}}
    e.runtime = {'queue': [], 'history': []}
    e.instance, e.runtime, kid, _ = add_knowledge(e.instance, e.runtime, verified=False)
    # Deliberately different: central execution must use the approved command.
    e.instance.update(workspace=str(workspace), config={'lean_command': ['unapproved-config-command'], })
    e.runtime.update(status='ready', executions={}, activities={}, trust_transitions={},
                     trust_bindings={'TE-old': binding})
    e.head = 'fixture-snapshot'
    for name in ('_save', '_controls', '_execution_profile', '_settle_activity', '_remove_action',
                 '_start_identity_review', '_action_lifecycle_gate', '_require_action_clock', '_enqueue'):
        setattr(e, name, create_autospec(getattr(e, name)))
    from do_math.configuration import DEFAULT_CONFIG
    from do_math.execution_profiles import build_profiles
    profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': trust['toolchain']['configured_command'], })
    e._execution_profile.return_value = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'formal_check')
    # Registration is a host double here; no real shared reservation exists.
    # Compiler subprocesses remain real in PortableFormalBoundaryTests.
    from do_math.session_slots import SessionSlots
    e._session_slots = create_autospec(e._session_slots, return_value=create_autospec(SessionSlots, instance=True))
    activity = activities.open_activity(e.runtime, activity_id='AT-fixture', activity_kind='formal_check',
        owner_ref='fixture', input_refs=[kid], opened_at='2026-09-20T00:00:00Z')
    e._activity_for_action = create_autospec(e._activity_for_action, return_value=activity)
    e._check_conversations = create_autospec(e._check_conversations, return_value=False)
    def register(action, row, *, profile=None):
        from research_fixtures import dispatched_launch
        row['launch_ticket'] = dispatched_launch(row['id'], e._execution_profile.return_value)
        row.update(action=action, activity_id='AT-fixture')
        e.runtime['executions'][row['id']] = row
        return row
    e._register_execution = create_autospec(e._register_execution, side_effect=register)
    # This fixture replaces admission/storage, while the compiler Job is real.
    # Acknowledge its suspended start through that same synthetic owner.
    def started(execution_id, identity):
        e._save()
    e._machine_started = create_autospec(e._machine_started, side_effect=started)
    e.formal_verifier = Mock(return_value=formal_evidence(e.instance, kid))
    return e, kid
