"""Design walkthrough scenes of the engine region on the Sim's real engine and store.

The legacy walkthroughs ran on ``engine_fixtures.evidence_engine``: an engine
built without ``__init__``, a synthetic approved charter, a fixed clock and an
input-snapshot store double that served one archived context. Here the engine
is the restored public activation's; its store is the real repository over the
Git port, a plan's input snapshot is a published head and its issued input is
archived below its input bundle (``support.engine_context.issue``). As in the
legacy walkthroughs, only the Lean and reviewer verdicts are fixtures; the
knowledge import, formal binding, use gates and receivers are the product's.

- ``evidence_sim(**charter)``: a restored active instance with an empty queue;
  ``charter`` fields (``goal``, ``academic_requirements``) replace the current
  charter's through the user's public decision.
- ``charter_change(engine, **content)``: that decision's change.
- ``accept_knowledge(engine, proposed=None)``: ``(kid, assessment ID)`` of a
  candidate imported, bound to a verified compiler result under the instance's
  active trust environment, and matched by an identity assessment.
- ``audit_goal(engine, kid, decision='satisfied')``: every configured goal
  auditor returns ``decision`` on ``kid`` through the engine's receiver.
- ``apply_plan(engine, plan, execution_id='EX-plan', snapshot=None)``: a returned
  plan that read a published head (by default the engine's state, published
  now) with the current tasks and ready task IDs archived as its issued input,
  and answered ``plan``, received by the engine. ``accept_knowledge`` records
  a synthetic identity match that the storage contract refuses to publish
  (a match needs a sealed review cycle), so a walkthrough that accepts
  knowledge in memory passes the snapshot it published before.
- ``plan_output(**changes)``, ``truth_candidate(statement, source, **changes)``:
  the legacy outputs and candidates.
"""
from copy import deepcopy

from do_math import knowledge_io, knowledge_records as kr, planning
from support.engine_context import issue
from support.engine_lifecycle import _ended_execution, applied, clear_work
from support.sim import Sim


def charter_change(engine, **content):
    current = engine._governance()['charter']
    return {'kind': 'charter', 'record': {'id': engine.ports.clock.new_id('CH'), 'kind': 'charter',
            'revision': current['revision'] + 1, 'supersedes': [current['id']],
            'content': {**deepcopy(current['content']), **deepcopy(content)}}}


def evidence_sim(**charter):
    sim = Sim.activated()
    if charter:
        applied(sim, 'decision', text='Adopt this exact charter', config={'change': charter_change(sim.engine, **charter)})
    clear_work(sim)
    return sim


def truth_candidate(statement='True', source='theorem truth : True := True.intro', **changes):
    """``knowledge_candidate`` stating ``statement`` in every exposition field, proved by ``source``."""
    from knowledge_fixtures import knowledge_candidate
    return knowledge_candidate(title=statement, statement=statement, explanation=statement, summary=statement,
                               lean_code=source, **changes)


def accept_knowledge(engine, proposed=None):
    """Only Lean and identity verdicts are fixtures; the import, binding and use gates run."""
    from knowledge_fixtures import formal_result
    proposed = proposed or truth_candidate()
    engine.instance, engine.runtime, kid = knowledge_io.import_candidate(engine.instance, engine.runtime, proposed,
        source_ref='fixture:source', actor_ref='EX-producer')
    environment = engine.instance['active_trust_environment']
    trust = engine.instance['trust_environments'][environment]
    response = formal_result(proposed['lean_code'], ['truth'], trust['toolchain'],
                             dependency_evidence=('fixture-type', 'fixture-constructor'),
                             declaration_evidence=(proposed['statement'], 'fixture-proof'),
                             allowed_axioms=deepcopy(trust['allowed_axioms']))
    engine.instance = kr.record_formal_result(engine.instance, kid, response, environment, runtime=engine.runtime)
    engine.instance, aid = kr.record_identity_assessment(engine.instance, kid, {'decision': 'match',
        'basis': kr.identity_basis(engine.instance, kid)}, 'policy:fixture', runtime=engine.runtime)
    return kid, aid


def audit_goal(engine, kid, decision='satisfied'):
    basis, required = engine._goal_basis_key(), engine.instance['config']['goal_auditors']
    for slot in range(required):
        eid = 'EX-goal-' + str(slot) + '-' + str(len(engine.instance['goal_judgments']))
        _ended_execution(engine, eid, 'goal_audit')
        engine._bind_governance_input({'role': 'goal_audit'}, engine.runtime['executions'][eid],
                                      engine._governance_context({'role': 'goal_audit'}, {}))
        engine._apply({'role': 'goal_audit', 'slot': slot, 'basis': basis, 'required': required},
                      {'decision': decision, 'scope_complete': True, 'used_sources': [kid],
                       'summary': 'Fixture auditor response for the stated charter', 'questions': []}, eid)


def plan_output(**changes):
    return dict({'dispositions': [], 'task_assessments': [], 'goal_audit': False, 'preparation_requests': []}, **changes)


def apply_plan(engine, plan, execution_id='EX-plan', *, snapshot=None):
    """The plan read ``snapshot`` (default: the engine's state, published now) and the current tasks."""
    if snapshot is None:
        engine._save()
        snapshot = engine.head
    _ended_execution(engine, execution_id, 'research_plan')
    execution = engine.runtime['executions'][execution_id]
    execution.update(input_snapshot=snapshot, extensions={})
    issue(engine, execution, {'snapshot': snapshot, 'tasks': deepcopy(list(engine.runtime['tasks'].values())),
                              'ready_task_ids': planning.ready_task_ids(engine.runtime, engine.instance)},
          'BA-' + execution_id)
    engine._apply({'id': 'AC-' + execution_id, 'role': 'research_plan'}, plan, execution_id)
