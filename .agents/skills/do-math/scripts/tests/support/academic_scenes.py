"""Academic-requirement scenes on the Sim: approved academic requirements, a solved goal and the academic tasks.

The legacy academic tests replaced the engine's ``_solution_basis`` with a
synthetic basis (``bare_engine`` and ``create_autospec``, or ``patch.object``
on a template engine) and set ``goal_status`` directly. Here the basis is the
product's own: the configured goal auditors judge the goal satisfied on a
reviewed theorem (``support.engine_lifecycle.theorems`` and ``solve_goal``), so
``_solution_basis`` computes it from the state, and the goal-audit receiver's
academic follow-up generates the requirement's task; or the purpose scenario
drives the public activation through the real solution. Nothing here replaces
an engine method or the store. Every template is built once per process and a
test restores its copy (``support.sim.built``).

Templates:
- ``theorem_sim()``: the public activation with the purpose configuration
  adopting explicit HTTP grants, plus the reviewed theorem ``k1``; the goal is
  not solved, so a test approves requirements (and grants) by public controls
  first and then solves (``solve_with``).
- ``consumer_sim()``: the default activation with requirement ``MANUSCRIPT``
  (two criteria) approved and the goal solved; the follow-up generated one
  academic task and queued its preparation.
- ``assessment_sim()``: the legacy ``purpose_fixtures.assessment_preparation_instance``
  on the public activation with the purpose configuration: requirement ``r``
  approved by the user's charter decision, two academic tasks
  ``TK-academic-1``/``-2`` without model assessments injected with their contract
  reviews queued, and the published readiness, which replaced the reviews with
  one assessment-only preparation. ``rule_prepared()`` restores it without
  queued work or observation rules, so readiness queues one combined
  preparation of rules and model assessments for both tasks.
- ``solved_sim(criteria)``: the purpose scenario's public activation driven
  through the real solution, with requirement ``writeup`` approved first when
  ``criteria`` is given (the legacy ``purpose_fixtures.solved_instance``).
  ``explicit_sim()`` is the same activation adopting explicit HTTP grants, not driven.

Steps and records:
- ``solve_with(sim, requirements)`` approves ``requirements`` by the user's
  charter decision, then solves the goal on ``k1``.
- ``decide_requirements(engine, requirements)`` applies a charter decision
  changing only the academic requirements by the governance rule the public
  decision applies (``governance.apply_decision``), without the engine's
  control step. Through the control, the engine marks the solved goal's
  judgments stale on any charter revision (KD-1200); a test of what follows a
  requirement change on a current solution uses this.
- ``academic_responder(effect_request=None)`` answers as the legacy
  ``AcademicAnswers``; ``drive_to`` drives a template build (preserved rule K-33).
- ``ended(engine, identifier, role, **fields)``: a returned execution registered
  as the engine registers one, with ``fields`` (such as a target or the solution
  basis it read) on its action and record.
"""
from __future__ import annotations

from copy import deepcopy
import json

from support.state_builders import charter_change
from support.engine_lifecycle import applied, clear_work, solve_goal, theorems
from support.sim import Sim, built

MANUSCRIPT = {'id': 'AR', 'scope': 'Prepare a manuscript', 'assessor': 'research_plan',
              'criteria': ['Explain the proof', 'Discuss the limitations']}
ASSESSED_REQUIREMENT = {'id': 'r', 'scope': 'solution', 'criteria': ['Explain the supplied argument'],
                        'assessor': 'research_plan'}
ACADEMIC_TASKS = ('TK-academic-1', 'TK-academic-2')
THEOREM = 'k1'


def unfinished(engine):
    """A template ends with every execution ended: a copy's owner would recover the others (preserved rule K-21)."""
    open_ids = [row['id'] for row in engine.runtime['executions'].values() if row['status'] != 'ended']
    if open_ids:
        raise AssertionError('A template must not end with unfinished executions: ' + repr(open_ids))


def theorem_id(sim):
    return next(k for k, row in sim.instance['knowledge'].items() if row['title'] == THEOREM)


def solve_with(sim, requirements):
    """Approve ``requirements`` by the user's charter decision, then solve the goal on the reviewed theorem.

    Returns the theorem's knowledge ID. The requirements come first: a goal
    solved without one completes the instance, which then refuses lifecycle
    controls. The goal-audit receiver runs the academic follow-up.
    """
    kid = theorem_id(sim)
    applied(sim, 'decision', config={'change': charter_change(sim.engine, academic_requirements=requirements)})
    solve_goal(sim.engine, kid)
    if sim.engine.instance['goal_status'] != 'mathematically_solved':
        raise AssertionError('the goal auditors did not solve the goal: ' + repr(sim.engine.instance['goal_status']))
    sim.engine._save()
    return kid


def user_source(engine):
    """The preserved user text the current charter's approval cites."""
    from do_math.governance import governance_view
    charter = governance_view(engine.instance)['charter']
    return engine.instance['decisions'][charter['approval_ref']]['source_ref']


def decide_requirements(engine, requirements):
    """The user's charter decision replacing only the academic requirements, applied by the governance rule."""
    from do_math import governance
    engine.instance, engine.runtime, decision = governance.apply_decision(
        engine.instance, engine.runtime, charter_change(engine, academic_requirements=requirements),
        source_ref=user_source(engine), clock=engine.ports.clock)
    return decision


def _build_theorem(root, shared):
    from support.engine_purpose import PURPOSE_CONFIG
    sim = Sim(root, shared=shared, config=PURPOSE_CONFIG)
    sim.activate(external_policy='explicit_grants')
    theorems(sim, THEOREM)
    unfinished(sim.engine)
    return sim


def theorem_sim():
    """The purpose-configured activation adopting explicit HTTP grants with the reviewed theorem ``k1``; unsolved."""
    return built('academic-theorem', _build_theorem)


def _build_consumer(root, shared):
    sim = Sim(root, shared=shared)
    sim.activate()
    theorems(sim, THEOREM)
    solve_with(sim, [MANUSCRIPT])
    unfinished(sim.engine)
    return sim


def consumer_sim():
    """An active instance with requirement ``MANUSCRIPT`` approved and the goal solved; its task generated."""
    return built('academic-consumer', _build_consumer)


def warm_consumer():
    consumer_sim()


def _build_assessment(root, shared):
    from do_math.academic import current_requirements
    from support.role_answers import candidate
    from support.observation_inputs import prepared_rule_conditions
    from support.engine_purpose import PURPOSE_CONFIG
    sim = Sim(root, shared=shared, config=PURPOSE_CONFIG)
    sim.activate()
    engine = sim.engine
    applied(sim, 'decision', config={'change': charter_change(engine, academic_requirements=[ASSESSED_REQUIREMENT])})
    requirement_hash = current_requirements(engine.instance)['sha256']
    engine.runtime['queue'] = []
    grants = [g['id'] for g in engine.instance['grants'].values()
              if g.get('kind') == 'local' and g.get('status') == 'active' and 'research_work' in g.get('roles', [])]
    for number, tid in enumerate(ACADEMIC_TASKS, 1):
        task = {**candidate(str(number)), 'id': tid, 'revision': 1, 'status': 'planned', 'academic_requirement_id': 'r',
                'requirements_sha256': requirement_hash, 'results': [], 'reviews': [], 'dependencies': [],
                'occurrence_condition': {'op': 'always'},
                'initial_observation_rules': prepared_rule_conditions([tid])[0]['observation_rules'],
                'profile_refs': deepcopy(engine.instance['role_profile_refs']['research_work']), 'authority_refs': grants}
        task.pop('revises_task_id')
        engine.runtime['tasks'][tid] = task
        engine._enqueue('task_contract_review', tid)
    engine._refresh_readiness()
    engine._save()
    unfinished(engine)
    return sim


def assessment_sim():
    """Two academic tasks of requirement ``r`` without model assessments; one assessment-only preparation queued."""
    return built('academic-assessment', _build_assessment)


def warm_assessment():
    assessment_sim()


def rule_prepared():
    """``assessment_sim`` without queued work or observation rules; readiness queues one combined preparation."""
    sim = assessment_sim()
    engine = sim.engine
    engine.runtime['queue'] = []
    for task in engine.runtime['tasks'].values():
        task['initial_observation_rules'] = []
    engine._refresh_readiness()
    engine._save()
    return sim


REVIEW_FINDING = 'model_assessment.reason: explain the impact on later verification.'


class RejectingResponder:
    """An independent contract reviewer whose every item decision is ``decision`` (the legacy ``RejectingRunner``).

    Its answer needs the actual structured contract (``research_fixtures.contract_review``);
    any other role is refused.
    """

    def __init__(self, decision):
        self.decision, self.calls = decision, []

    def respond(self, role, context, workspace):
        from support.role_answers import contract_review
        from support.default_responder import common
        self.calls.append(role)
        if role != 'task_contract_review':
            raise AssertionError('the rejecting reviewer was asked for ' + role)
        return {**common(role), **contract_review(context, decision=self.decision, findings=[REVIEW_FINDING])}


_REJECTED = {}


def rejected_sim(decision='revision_required'):
    """``assessment_sim`` keeping ``TK-academic-1`` rated, whose independent contract review returned ``decision``.

    The review runs as one owner pass: the worker, the model double as
    ``RejectingResponder`` and the workspace submission. Returns
    ``(sim, task_id, original)``: ``original`` is the task before the review.
    """
    from support.default_responder import rating
    name = 'academic-rejected-' + decision

    def build(root, shared, *, decision):
        name = 'academic-rejected-' + decision
        from support.default_responder import rating
        sim = _build_assessment(root, shared)
        engine = sim.engine
        tid = ACADEMIC_TASKS[0]
        engine.runtime['tasks'].pop(ACADEMIC_TASKS[1])
        task = engine.runtime['tasks'][tid]
        task['model_assessment'] = rating()
        engine.runtime['queue'] = []
        _REJECTED[name] = deepcopy(task)
        engine._enqueue('task_contract_review', tid)
        engine._save()
        sim.model.responder = RejectingResponder(decision)
        sim.step()
        if sim.model.responder.calls != ['task_contract_review']:
            raise AssertionError('the rejecting review did not run once: ' + repr(sim.model.responder.calls))
        unfinished(sim.engine)
        return sim
    sim = built('academic-rejected', build, decision=decision)
    return sim, ACADEMIC_TASKS[0], deepcopy(_REJECTED[name])


def academic_responder(scenario='direct', *, effect_request=None):
    """A ``support.engine_purpose.PurposeResponder`` answering as the legacy ``support.purpose_answers.AcademicAnswers``.

    A planner asked about an external rejection resolves it with the usable
    knowledge as evidence; academic research work returns a reader-facing report
    and, given ``effect_request``, asks for the task's first required external
    effect. Everything else, and every input check, is ``PurposeAnswers``'s.
    """
    from support.purpose_answers import AcademicAnswers
    from support.engine_purpose import PurposeResponder
    responder = PurposeResponder(scenario)
    responder.runner = AcademicAnswers(scenario, effect_request=effect_request)
    return responder


def drive_to(sim, predicate, limit=45):
    """Owner passes until ``predicate(sim)``, for a template build with no test case to fail.

    Fails at once when the responder refused its input or the instance paused,
    closed or waits, and after ``limit`` passes (preserved rule K-33).
    """
    for _ in range(limit):
        sim.step()
        failures = getattr(sim.model.responder, 'failures', None)
        if failures:
            raise AssertionError('The responder refused its input: ' + '; '.join(failures))
        if predicate(sim):
            return
        if sim.runtime['status'] in {'paused', 'closed', 'waiting'}:
            raise AssertionError('Workflow stopped before its fixture outcome: ' + json.dumps(sim.waiting(), default=str))
    raise AssertionError('Fixture did not finish within its bounded scenario: ' + json.dumps(sim.waiting(), default=str))


def solved_sim(criteria):
    """The public activation with the purpose configuration, driven through the real solution.

    ``criteria`` None solves without academic requirements, so the runtime
    completes. A list first approves requirement ``writeup`` with those criteria
    by the user's charter decision, so the solution generates its academic task
    through the real path and the runtime stays open. The model double of a
    copy answers by the default responder until a test sets its own.
    """
    from support.purpose_answers import requirement
    from support.engine_purpose import PURPOSE_CONFIG

    def build(root, shared, *, criteria):
        from support.purpose_answers import requirement
        from support.engine_purpose import PURPOSE_CONFIG
        sim = Sim(root, shared=shared, config=PURPOSE_CONFIG)
        sim.activate()
        sim.model.responder = academic_responder()
        if criteria is not None:
            applied(sim, 'decision', config={'change': charter_change(
                sim.engine, academic_requirements=[requirement(list(criteria))])})
        drive_to(sim, lambda s: s.instance['goal_status'] == 'mathematically_solved')
        unfinished(sim.engine)
        return sim
    return built('academic-solved', build, criteria=criteria)


def no_repair_sim():
    """The public activation with the purpose configuration and no output repair (``max_output_repairs=0``)."""
    from support.engine_purpose import PURPOSE_CONFIG

    def build(root, shared):
        from support.engine_purpose import PURPOSE_CONFIG
        sim = Sim(root, shared=shared, config={**PURPOSE_CONFIG, 'max_output_repairs': 0})
        sim.activate()
        return sim
    return built('academic-no-repair', build)


def explicit_sim():
    """The public activation with the purpose configuration adopting explicit HTTP grants; queue as activation left it."""
    from support.engine_purpose import PURPOSE_CONFIG

    def build(root, shared):
        from support.engine_purpose import PURPOSE_CONFIG
        sim = Sim(root, shared=shared, config=PURPOSE_CONFIG)
        sim.activate(external_policy='explicit_grants')
        return sim
    return built('academic-explicit', build)


def ended(engine, identifier, role, **fields):
    """The returned execution ``identifier`` of ``role``; ``target`` goes on its action, other fields on the record."""
    from do_math.execution_lifecycle import transition_execution
    action = {'id': 'AC-' + identifier, 'role': role}
    if 'target' in fields:
        action['target'] = fields.pop('target')
    execution = engine._register_execution(action, {'id': identifier, 'role': role, 'status': 'running', **fields})
    at = engine._lifecycle_now().isoformat()
    transition_execution(execution, 'stopping', at=at)
    transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
    return execution
