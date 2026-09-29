"""The purpose scenario: a scripted research run that proves one natural-number identity.

``PurposeRunner(scenario='direct', observation=None)`` answers every role from
its actual input: preparation proposes task ``A`` (a formal theorem, ``SOURCE``),
review approves, work returns ``theorem()``, identity review matches and the
goal audit is satisfied once a certified result exists. ``scenario`` selects
variants (``dependency``: ``B`` before ``A``; ``dispute``: one withdrawn
objection; ``currentness``: a downstream task that consumes the result;
``catalog``: a long report); ``observation`` drives live observation of the
first work call (``continue``, ``stop``, ``external_pause``). ``formal_fixture``
is its compiler double, which covers ``SOURCE`` only. ``parse_context``,
``common``, ``candidate`` and ``theorem`` are the pieces of its answers;
``GOAL``, ``STATEMENT``, ``EXPLANATION`` and ``NEW_GOAL`` are its texts.
``AcademicRunner`` extends it with academic tasks, resolutions and external
effects; ``CheckedRunner`` wraps a runner so that its output passes the
producer check and control transport as a worker's does.

Harnesses
---------
``PurposeHarness`` holds the scenario's configuration (``fixture_config``) and
``drive(engine, predicate=None, limit=45)``, which steps the engine until
``predicate`` (default: the goal is mathematically solved) and fails the test
if the flow stops first. ``ActivatedPurposeHarness`` hands out template copies
(``make``: the public activation; ``make_active(**config)``: the validated
synthetic active state), one live copy at a time.

Template builds (``research_fixtures.restore_template``)
--------------------------------------------------------
- ``solved_instance(root, shared, *, criteria)``: the public activation driven to
  the mathematical solution; ``criteria`` approves requirement ``writeup``
  (``requirement``) first. It returns the instance ID, the head the driving
  engine published last and the runner's work order. ``drive_to`` is the
  build's bounded drive.
- ``purpose_state(root, shared, *, config, until, ...)``: the synthetic active
  state driven until task ``A``'s work is queued (``until='prepared'``) or its
  identity review opens (``'review'``); ``purpose_copy`` gives a harness test
  an engine on a copy.
- ``assessment_preparation_instance(root, shared, *, config)``: two academic
  tasks awaiting model assessment; ``prepared_assessment_engine`` gives a
  harness test an engine on a copy with ``ASSESSMENT_CONFIG``.
``CURRENTNESS_CONFIG`` is the configuration of the currentness scenarios.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import time
import unittest
from unittest.mock import patch

import jsonschema

from do_math import submission
from do_math.control_server import wait_receipt
from do_math.control_transport import ControlTransport
from do_math.engine import ResearchEngine, control
from do_math.canonical import canonical_json
from research_fixtures import (FixtureAdapter, assessment, await_stop, bind_candidates, charter_change,
                               contract_review, disposition, install_adapter_fixture, intent_response,
                               local_job_runner, observation_batch, planning_model_assessments,
                               prepared_rule_conditions, read_fixture_context, restore_template,
                               scope_response, seal_response, send_control, submit_intent,
                               supply_observation_rules, candidate as v5_candidate)
from runner_fixtures import formal_ok, common as role_output
from state_fixtures import active_instance


SOURCE = 'theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n'


STATEMENT = 'For every natural number n, n + 0 = n.'


EXPLANATION = 'The variable n ranges over Nat. The proof applies Nat.add_zero to that n.'


GOAL = 'Establish that adding zero to any natural number leaves it unchanged.'


NEW_GOAL = 'Establish the same zero-addition identity with the natural-number domain explicit.'


def parse_context(prompt, workspace):
    return read_fixture_context(prompt, workspace)


def common(summary):
    return {'summary': summary, 'used_sources': [], 'questions': []}


def candidate(title, *, formal=True, revises=None, refs=None):
    return v5_candidate(title, formal=formal, revises=revises, refs=refs)


def theorem():
    return {'kind': 'theorem', 'title': 'Natural zero identity', 'statement': STATEMENT,
            'explanation': EXPLANATION, 'summary': 'Addition of zero preserves each natural number.',
            'lean_code': SOURCE, 'declaration_names': ['add_zero_fixture'], 'dependencies': []}


def formal_fixture(*, source, declarations, workspace, lean_command,
                   allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None, launch_ticket=None,
                   jobs=None):
    if source != SOURCE or declarations != ['add_zero_fixture']:
        raise AssertionError('The explicit formal test fixture only covers SOURCE/add_zero_fixture')
    result = formal_ok(source=source, declarations=declarations, workspace=workspace,
        lean_command=lean_command, allowed_axioms=allowed_axioms, expected_toolchain=expected_toolchain,
        launch_ticket=launch_ticket, jobs=jobs)
    result['reason'] = 'Explicit compiler fixture; not an actual Lean invocation'
    return result


class PurposeRunner:
    def __init__(self, scenario='direct', *, observation=None, pause_sender=None):
        self.scenario, self.observation, self.pause_sender = scenario, observation, pause_sender
        self.calls = []
        self.work_order = []
        self.preparations = 0
        self.currentness_prepared = False
        self.observed_workers = 0
        self.returned = []

    @local_job_runner
    def run(self, *, prompt, output_schema, workspace, evidence_dir, model, effort,
            timeout_seconds, should_stop, on_started, on_observation=None, scholarly_server=None, control_binding=None, **kwargs):
        role = prompt.split('You are the do-math role: ', 1)[1].split('.', 1)[0]
        context = parse_context(prompt, workspace)
        action = context['action']
        self.calls.append({'role': role, 'action': deepcopy(action), 'context': deepcopy(context), 'workspace': str(workspace),
                           'prompt': prompt})
        on_started()
        if action.get('repair'):
            raise AssertionError('A purpose fixture must not silently adapt to an engine validation failure: ' +
                                 str(action['repair'].get('error') or action['repair'].get('issues')))
        output = self.answer(role, context, workspace)
        if role == 'research_work' and self.observation and self.observed_workers == 0:
            self.observed_workers += 1
            checkpoint = {'current_claim': STATEMENT, 'evidence_paths': ['argument.txt'],
                'attempts': ['Reconstructed Nat.add_zero'], 'remaining_work': ['Write the final report'],
                'next_step': 'Finish the explicit report', 'progress_state': 'working', 'counters': {'attempts': 1}}
            (workspace / 'argument.txt').write_text('The domain is Nat; Nat.add_zero supplies the equality.', encoding='utf-8')
            (workspace / 'checkpoint.json').write_bytes(canonical_json(checkpoint))
            if on_observation is None: raise AssertionError('The real engine failed to supply its observation callback')
            offset = 0
            def deliver(*events):
                # Like the real runner (model_runner.observe): each read is one batch that
                # continues the stream offset; a read without rows is the idle tick.
                nonlocal offset
                batch = observation_batch(events, received_monotonic=time.monotonic(),
                                          stream_path=Path(evidence_dir) / 'stdout.jsonl', start=offset)
                offset = batch.end_offset
                on_observation(batch)
            deliver({'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'm1', 'text': 'The Nat domain is fixed.'}})
            if self.observation == 'external_pause':
                self.pause_sender()
            else:
                deliver({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
                time.sleep(1.05)
                deliver()
                until = time.monotonic() + 120
                ticked = time.monotonic()
                while time.monotonic() < until:
                    if should_stop():
                        break
                    feedback = workspace / '.control/observation-feedback.json'
                    if feedback.exists() and json.loads(feedback.read_bytes()).get('kind') == 'continue':
                        break
                    if time.monotonic() - ticked >= .5:
                        # Like the real runner, keep ticking: queued observations are
                        # applied, and their clock read, when the owner reaches them.
                        deliver()
                        ticked = time.monotonic()
                    time.sleep(.05)
                else:
                    raise AssertionError('The live reviewer did not return its disposition')
                if self.observation == 'continue':
                    deliver({'type': 'item.completed', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
            if self.observation in {'stop', 'external_pause'}:
                if not await_stop(should_stop): raise AssertionError('The owner did not judge the stop')
                if not (workspace / '.control/stop-request.json').exists(): raise AssertionError('Stop did not request a checkpoint')
                return {'status': 'stopped', 'output': None, 'usage': {'input_tokens': 30, 'output_tokens': 4}, 'error': 'Fixture honored the stop request'}
        if role == 'research_preparation' and action.get('revision_targets'):
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            revised = {candidate.get('revises_task_id') for candidate in output.get('candidates', [])}
            extensions['revision_resolutions'] = [{'record_id': identifier,
                'disposition': 'revised' if identifier in revised else 'deferred',
                'reason': 'The fixture replaces this contract.' if identifier in revised else 'The fixture preserves this remaining obligation.'}
                for identifier in action['revision_targets']]
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation':
            from runner_fixtures import contract_checks
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            targets = action.get('assessment_targets')
            identities = ([{'task_id': tid} for tid in targets] if targets else
                          [{'task_title': c['title']} for c in output['candidates']])
            extensions['model_assessments'] = [{**identity, 'difficulty': 'low', 'importance': 'medium',
                'reason': 'The fixture supplies a bounded natural-number identity'} for identity in identities]
            if output['candidates']:
                extensions['contract_checks'] = contract_checks(output['candidates'])
            path.write_bytes(canonical_json(extensions))
        if role == 'research_plan':
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            extensions['model_assessments'] = planning_model_assessments(output, context)
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation' and output.get('candidates'):
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            supply_observation_rules(output['candidates'], extensions)
            path.write_bytes(canonical_json(extensions))
        if role == 'research_preparation' and action.get('observation_rule_targets'):
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            extensions['task_conditions'] = prepared_rule_conditions(action['observation_rule_targets'])
            path.write_bytes(canonical_json(extensions))
        bind_candidates(output, context)
        seal_response(output, context, workspace)
        jsonschema.validate(output, output_schema)
        submit_intent(control_binding, workspace, output)
        self.returned.append({'role': role, 'action': deepcopy(action), 'output': deepcopy(output)})
        return {'status': 'completed', 'output': output, 'usage': {'input_tokens': 20, 'output_tokens': 10}, 'error': None}

    def answer(self, role, context, workspace):
        action = context['action']
        if role == 'research_preparation':
            if 'assessment_targets' in action or 'observation_rule_targets' in action:
                return {**common('Assess only the supplied contracts'), 'candidates': []}
            self.preparations += 1
            tasks = context.get('tasks', [])
            if self.scenario == 'dependency' and not tasks and not any(
                    k['title'] == 'Natural zero identity' for k in context.get('knowledge_catalog', [])):
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'task_conditions': [{
                    'task_title': 'A', 'occurrence_condition': {'op': 'task_disposition_is', 'task_id': 'B', 'value': 'completed'},
                    'dependencies': ['B']}]}))
                return {**common('Prepare B before A; the extension fixes the dependency'), 'candidates': [candidate('A'), candidate('B', formal=False)]}
            revision_targets = set(action.get('revision_targets', {}))
            if revision_targets:
                revisable = next((t for t in tasks if t['id'] in revision_targets), None)
                if revisable is None:
                    raise AssertionError('The preparation fixture did not receive its declared revision target')
                return {**common('Revise only the contract declared before this execution'),
                        'candidates': [candidate('A', revises=revisable['id'])]}
            if self.scenario == 'currentness' and any(k['title'] == 'Natural zero identity' and k['usable_as_k']
                                                      for k in context.get('knowledge_catalog', [])):
                source = next(k['id'] for k in context['knowledge_catalog']
                              if k['title'] == 'Natural zero identity' and k['usable_as_k'])
                self.currentness_prepared = True
                return {**common('Prepare a task that explicitly consumes the certified result'),
                        'candidates': [candidate('Dependent', formal=False, refs=[source])]}
            if tasks or any(k['title'] == 'Natural zero identity' for k in context.get('knowledge_catalog', [])):
                return {**common('Preserve existing contracts and supplied results when no revision target was declared'), 'candidates': []}
            return {**common('Prepare the exact natural-number identity'), 'candidates': [candidate('A')]}
        if role == 'task_contract_review':
            return {**common('Inspect the actual scope, obligations and evidence'), **contract_review(context)}
        if role == 'research_plan':
            tasks = context.get('tasks', [])
            ready = context['ready_task_ids']
            from do_math.task_contracts import returned_task_ids
            returned = set(returned_task_ids({t['id']: t for t in tasks}))
            assessments = [assessment(t) for t in tasks if t['id'] in returned]
            finished = all(t['status'] == 'completed' or t['id'] in returned for t in tasks)
            catalog = context.get('knowledge_catalog', [])
            certified = any(k['title'] == 'Natural zero identity' and k['usable_as_k'] for k in catalog)
            preparations = []
            if self.scenario == 'currentness' and not self.currentness_prepared and finished and certified:
                preparations = ['Prepare an explicit downstream task that uses Natural zero identity']
                finished = False
            return {**common('Select only enabled tasks and assess actual returned reports'), 'dispositions': [disposition(tid) for tid in ready],
                    'preparation_requests': preparations, 'goal_audit': finished and certified,
                    'task_assessments': assessments}
        if role == 'research_work':
            task = context['task']
            title = task['title']
            self.work_order.append(title)
            if self.scenario == 'dependency' and title == 'A':
                prerequisite = next(t for t in context['tasks'] if t['title'] == 'B')
                if prerequisite['status'] != 'completed': raise AssertionError('A started before B was assessed complete')
            if title == 'B':
                knowledge = [{'kind': 'observation', 'title': 'Domain note', 'statement': 'The domain is the natural numbers.',
                    'explanation': 'This note fixes the declared domain; it does not claim a formal theorem.',
                    'summary': 'Natural-number domain recorded.', 'lean_code': '', 'declaration_names': [], 'dependencies': []}]
            elif title == 'Dependent':
                knowledge = []
            else:
                knowledge = [theorem()]
            return {**common('The report fixes n : Nat and applies Nat.add_zero'),
                'used_sources': task.get('reuse', []), 'outcome': 'submitted',
                'report': EXPLANATION + ('\nAppendix records the same fixed Nat domain.' * 6000 if self.scenario == 'catalog' else ''),
                'knowledge': knowledge, 'relations': [], 'remaining_work': [], 'checkpoint': 'Argument and domain are explicit'}
        if role == 'identity_review':
            if action['stage'] == 'scope':
                return {**common('Inspect the full supplied proposal and assign independent perspectives'), **scope_response(context)}
            review = context['role_review']
            base = {**common('Compare the exact Nat statement, explanation and proof'), 'proposal_digest': review['proposal_digest'],
                    'used_sources': ['proposal:statement', 'proposal:explanation', 'proposal:lean_code']}
            stage = action['stage']
            if stage == 'initial':
                if self.scenario == 'dispute' and action['slot'] == 'initial-0':
                    return {**base, 'decision': 'mismatch', 'scope_complete': True,
                        'findings': [{'id': 'domain-objection', 'statement': 'The explanation might quantify over real numbers, unlike Nat in Lean.',
                                      'evidence': ['proposal:explanation']} ]}
                return {**base, 'decision': 'match', 'scope_complete': True, 'findings': []}
            if stage == 'organize':
                source = review['pending_findings'][0]['ref']
                return {**base, 'issues': [{'id': 'domain-issue', 'finding_refs': [source], 'answer_role_slot_id': 'initial-0'}]}
            if stage == 'answer':
                return {**base, 'answers': [{'issue_id': 'domain-issue', 'disposition': 'withdraw',
                    'statement': 'I withdraw the objection: the supplied explanation explicitly says that n ranges over Nat.',
                    'evidence': ['proposal:explanation']}], 'new_findings': []}
            return {**base, 'decision': 'match', 'scope_complete': True, 'new_findings': [],
                'issue_verdicts': [{'issue_id': 'domain-issue', 'decision': 'rejected',
                    'reason': 'The explanation explicitly fixes n : Nat, exactly as the Lean declaration does.',
                    'evidence': ['proposal:explanation', 'proposal:lean_code']}]}
        if role == 'goal_audit':
            eligible = context.get('eligible_knowledge', [])
            if not eligible: raise AssertionError('Goal audit was scheduled before effective formal evidence existed')
            if not all(item['links'] and all(a['decision'] == 'match' for a in item['identity_assessments']) for item in eligible):
                raise AssertionError('Goal audit did not receive the effective final identity assessment')
            return {**common('The certified Nat zero-addition theorem meets the exact requested identity'),
                    'used_sources': [k['id'] for k in eligible], 'decision': 'satisfied', 'scope_complete': True,
                    'additional_audits': [],
                    'reason': 'The requested domain and equality coincide with the reviewed theorem.'}
        if role == 'intent_interpretation':
            output = intent_response(context)
            if action.get('stage', 'interpret') == 'interpret' and context['user_request']['text'] == NEW_GOAL:
                current = context['governance']['charter']
                record = {'id': 'CH-proposed-new-goal', 'kind': 'charter', 'revision': current['revision'] + 1,
                    'supersedes': [current['id']], 'content': {**deepcopy(current['content']),
                        'goal': NEW_GOAL, 'success_criteria': [NEW_GOAL], 'included_scope': [NEW_GOAL]}}
                output['import_units'][0].update(owner_ref=record['id'], payload={'kind': 'charter', 'record': record})
            return output
        if role == 'operational_review':
            if not action.get('live'): raise AssertionError('Unexpected execution failure triggered a non-live operational review')
            proposal = {'kind': 'continue', 'basis_refs': [action['target']], 'next_owner': 'research_work',
                'reason': 'The visible checkpoint contains the fixture argument', 'next_review': None}
            if self.observation == 'stop':
                proposal = {'kind': 'retry', 'basis_refs': [action['target']], 'next_owner': 'research_work',
                    'reason': 'Preserve the partial argument before retrying the missing report',
                    'scope': 'Complete the report using the preserved checkpoint and current input',
                    'replay_safety': 'This attempt has published no theorem or external effect'}
            return {**common('A checkpoint and a visible observation are available'), 'disposition': proposal}
        raise AssertionError('Unexpected fixture role: ' + role)


class PurposeHarness(unittest.TestCase):
    """The purpose scenario's configuration (``fixture_config``) and its bounded ``drive``."""

    @staticmethod
    def fixture_config(**config):
        settings = {'reviewers': 2, 'goal_auditors': 2, 'review_rounds': 2,
                    'plan_settle_seconds': 1,
                    'max_input_bytes': 2_000_000,
                    'lean_command': ['test-double'],
                    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5,
                    'scholarly_enabled': False, 'operator_enabled': False, **config}
        return settings

    def drive(self, engine, predicate=None, limit=45):
        predicate = predicate or (lambda e: e.instance['goal_status'] == 'mathematically_solved')
        for _ in range(limit):
            engine.run(max_steps=1)
            if predicate(engine): return
            if engine.runtime['status'] in {'paused', 'closed', 'waiting'}:
                self.fail('Workflow stopped before its fixture outcome: ' + json.dumps({
                    'status': engine.runtime['status'], 'questions': engine.runtime['questions'],
                    'queue': engine.runtime['queue'], 'executions': [{k: ex.get(k) for k in ('role', 'outcome', 'error')} for ex in engine.runtime['executions'].values()]}, ensure_ascii=False))
        self.fail('Fixture did not finish within its bounded scenario: ' + str(engine.status()))


class ActivatedPurposeHarness(PurposeHarness):
    """``PurposeHarness`` whose instances are copies of templates built once per process.

    ``make`` hands out the state the public ``initialize`` and ``activate``
    publish for the scenario (``research_fixtures.activated_instance`` with
    ``fixture_config``), restored byte for byte (``research_fixtures.restore_template``);
    ``make_active`` does the same for the validated synthetic active state
    (``state_fixtures.active_instance``) with the given configuration. Only
    the engine object is new, as after a restart. Each call replaces the
    previous copy, so a test holds one live instance at a time.
    """

    def setUp(self):
        install_adapter_fixture(self)

    def _engine(self, instance_id, runner):
        self.repo = self.root / 'repository'
        engine = ResearchEngine(self.repo, instance_id, runner=runner, formal_verifier=formal_fixture)
        runner.pause_sender = lambda: control(self.repo, instance_id, 'pause', text='Stop the current research after preserving its checkpoint')
        return engine, runner

    def make(self, scenario='direct', *, observation=None, external_policy='disabled', review_policy=None, **config):
        from research_fixtures import activated_instance
        if observation in {'continue', 'stop'}:
            config.setdefault('tool_review_window_seconds', 1)
        self.root, instance_id = restore_template(activated_instance, goal=GOAL,
            config=self.fixture_config(**config), external_policy=external_policy, review_policy=review_policy)
        return self._engine(instance_id, PurposeRunner(scenario, observation=observation))

    def make_active(self, **config):
        self.root, instance_id = restore_template(active_instance, config=config)
        return self._engine(instance_id, PurposeRunner())

CURRENTNESS_CONFIG = {'max_input_bytes': 2_000_000,
    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5,
    'scholarly_enabled': False, 'operator_enabled': False}

# The requirement approved before the real solution; test_model_assessment_flow shares this solved state.
SOLVED_REQUIREMENT_CRITERIA = ["draft account", "cite reviewed equality"]


def requirement(criteria: list[str], *, required_inputs=None, external_effects=None) -> dict:
    return {
        "id": "writeup",
        "scope": "A reader-facing account of the solved natural-number theorem.",
        "criteria": criteria,
        "assessor": "research_plan",
        "required_inputs": required_inputs or [],
        "external_effects": external_effects or [],
    }


class AcademicRunner(PurposeRunner):
    """Purpose fixture that supplies an explicit planner resolution when asked."""

    def __init__(self, *args, effect_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.effect_request = effect_request

    def answer(self, role, context, workspace):
        action = context["action"]
        if role == "research_plan" and action.get("rejection_id"):
            (workspace / "activity-extensions.json").write_bytes(canonical_json({
                "academic_resolutions": [{
                    "id": action["rejection_id"], "decision": "resolved",
                    "evidence": "The planner compared the preserved objection with the completed reviewed task report.",
                    "evidence_refs": [row['id'] for row in context['knowledge_catalog'] if row.get('usable_as_k')],
                }],
            }))
        if role == "research_work" and context["task"].get("academic_requirement_id"):
            task = context["task"]
            effects = task.get("required_external_effects", [])
            if effects and self.effect_request:
                (workspace / "activity-extensions.json").write_bytes(canonical_json({"external_requests": [{
                    "id": "academic-effect", "academic_effect_id": effects[0]["id"],
                    "grant_id": effects[0].get("grant_id") or self.effect_request["grant_id"],
                    "purpose": effects[0]["scope"], "request": deepcopy(self.effect_request["request"]),
                }]}))
            self.work_order.append(task["title"])
            return {
                "summary": "The academic criterion is addressed by the submitted reader-facing account.",
                "used_sources": task.get("reuse", []), "questions": [], "outcome": "submitted",
                "report": "The report explains the exact natural-number domain and the reviewed equality.",
                "knowledge": [], "relations": [], "remaining_work": [],
                "checkpoint": "The required account and its evidence are ready for independent assessment.",
            }
        return super().answer(role, context, workspace)


def drive_to(engine, predicate, limit=45):
    """``PurposeHarness.drive`` for a template build, which has no test case to fail."""
    for _ in range(limit):
        engine.run(max_steps=1)
        if predicate(engine):
            return
        if engine.runtime["status"] in {"paused", "closed", "waiting"}:
            raise AssertionError("Workflow stopped before its fixture outcome: " + repr(engine.status()))
    raise AssertionError("Fixture did not finish within its bounded scenario: " + repr(engine.status()))


def solved_instance(root, shared, *, criteria):
    """``restore_template`` build: public activation, then the real mathematical solution.

    This is the public ``initialize`` and ``activate`` (``activated_instance``)
    followed by driving to ``mathematically_solved``. ``criteria`` None solves
    without academic requirements, so the runtime completes. A list approves
    requirement ``writeup`` with those criteria first, so the solution generates
    its academic task through the real path and the runtime stays open.
    ``AcademicRunner`` answers like ``PurposeRunner`` until an academic task or
    an academic rejection exists. Returns ``{'instance_id', 'head', 'work_order'}``:
    the head the driving engine published last and the order in which the
    runner answered research work.
    """
    from research_fixtures import activated_instance
    instance_id = activated_instance(root, shared, goal=GOAL, config=PurposeHarness.fixture_config())
    engine = ResearchEngine(root / "repository", instance_id, runner=AcademicRunner(), formal_verifier=formal_fixture)
    with patch("do_math.initialization.adapter_for", side_effect=lambda profile: FixtureAdapter()):
        if criteria is not None:
            send_control(engine, "decision", config={"change": charter_change(engine,
                academic_requirements=[requirement(criteria)])})
        drive_to(engine, lambda current: current.instance["goal_status"] == "mathematically_solved")
    return {"instance_id": instance_id, "head": engine.head, "work_order": list(engine.runner.work_order)}

def signed_formal_fixture(**kwargs):
    result = formal_fixture(**kwargs)
    result['declaration_signatures'] = {'add_zero_fixture': '(n : Nat) -> n + 0 = n'}
    return result


_STOPS = {'prepared': lambda engine: any(a['role'] == 'research_work' for a in engine.runtime['queue']),
          'review': lambda engine: bool(engine.runtime['review_cycles'])}


def purpose_state(root, shared, *, config, until, review_policy=None, external_policy='disabled', signed=True):
    """``restore_template`` build: synthetic active state advanced by ``PurposeRunner('direct')``.

    ``until='prepared'``: task A is prepared, its contract approved and the plan
    selected it; its ``research_work`` is queued. ``until='review'``: A's work
    returned the theorem, its formal check passed and its identity review cycle
    opened; the scope review is queued with whatever else the flow queued.
    ``signed`` checks formally with ``signed_formal_fixture``, else ``formal_fixture``.
    Formal checks need ``lean_command=list(ACTIVE_LEAN_COMMAND)`` in ``config``.
    Returns the instance ID.
    """
    instance_id = active_instance(root, shared, config=config, external_policy=external_policy,
                                  review_policy=review_policy)
    engine = ResearchEngine(root / 'repository', instance_id, runner=PurposeRunner(),
                            formal_verifier=signed_formal_fixture if signed else formal_fixture)
    with patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
        for _ in range(45):
            engine.run(max_steps=1)
            if _STOPS[until](engine):
                break
            if engine.runtime['status'] in {'paused', 'closed', 'waiting'}:
                raise AssertionError('The purpose flow stopped before ' + until + ': ' + repr(engine.status()))
        else:
            raise AssertionError('The purpose flow did not reach ' + until + ': ' + repr(engine.status()))
    unfinished = [e['id'] for e in engine.runtime['executions'].values() if e['status'] != 'ended']
    if unfinished:
        raise AssertionError('A template must not end with unfinished executions: ' + repr(unfinished))
    return instance_id


def purpose_copy(test, runner, *, until, config, **build):
    """Engine and ``runner`` on a fresh copy of ``purpose_state`` for an ``ActivatedPurposeHarness`` test."""
    test.root, instance_id = restore_template(purpose_state, until=until, config=config, **build)
    engine, runner = test._engine(instance_id, runner)
    engine.formal_verifier = signed_formal_fixture if build.get('signed', True) else formal_fixture
    return engine, runner

class CheckedRunner:
    """Script only the model answer; use actual producer and control protocols."""
    def __init__(self, runner):
        self.runner = runner

    @local_job_runner
    def run(self, **args):
        ctx = parse_context(args["prompt"], args["workspace"])
        if ctx["action"].get("stage") == "scope" and ctx["action"]["role"] == "identity_review":
            args["on_started"]({"fixture": "scope response"})
            result = {"status": "completed", "output": {**role_output("identity_review"), **scope_response(ctx)}, "usage": {}}
        else:
            result = self.runner.run(**args)
        output = result.get("output")
        if output is not None:
            bind_candidates(output, ctx)
            if "integration_bundles" not in output:
                seal_response(output, ctx, args["workspace"])
            draft = args["workspace"] / ".scratch/submission.json"
            draft.parent.mkdir(exist_ok=True)
            draft.write_bytes(canonical_json(output))
            check = submission.producer_check(args["workspace"], draft)
            binding = args["control_binding"]
            payload = {"draft_path": check["raw_output_path"]}
            request_id = "submit-" + check["id"]
            ControlTransport.worker_submit(binding, request_id=request_id, kind="submit_intent", payload=payload)
            wait_receipt(binding, request_id, 60)  # The owner receives it on its next pass.
        return result

ASSESSMENT_CONFIG = PurposeHarness.fixture_config(scholarly_enabled=False, operator_enabled=False)


def assessment_preparation_instance(root, shared, *, config):
    """``restore_template`` build: two academic tasks of requirement ``r`` without model assessments.

    The validated synthetic active state supplies grants; a public charter
    control supplies the requirement and its pending event history. The tasks
    and their contract reviews are injected, and the published readiness has
    replaced the reviews with one assessment-only preparation.
    """
    from do_math.academic import current_requirements
    instance_id = active_instance(root, shared, config=config)
    engine = ResearchEngine(root / "repository", instance_id)
    send_control(engine, "decision", config={"change": charter_change(engine, academic_requirements=[
        {"id": "r", "scope": "solution", "criteria": ["Explain the supplied argument"], "assessor": "research_plan"}])})
    requirement_hash = current_requirements(engine.instance)["sha256"]
    engine.runtime["queue"] = []
    for number in (1, 2):
        tid = f"TK-academic-{number}"
        engine.runtime["tasks"][tid] = {**v5_candidate(str(number)), "id": tid, "revision": 1,
            "status": "planned", "academic_requirement_id": "r",
            "requirements_sha256": requirement_hash, "results": [], "reviews": [], "dependencies": [],
            "occurrence_condition": {"op": "always"},
            "initial_observation_rules": prepared_rule_conditions([tid])[0]['observation_rules']}
        engine.runtime["tasks"][tid]["profile_refs"] = deepcopy(engine.instance["role_profile_refs"]["research_work"])
        engine.runtime["tasks"][tid]["authority_refs"] = [g["id"] for g in engine.instance["grants"].values()
            if g.get("kind") == "local" and g.get("status") == "active" and "research_work" in g.get("roles", [])]
        engine.runtime["tasks"][tid].pop("revises_task_id")
        engine._enqueue("task_contract_review", tid)
    engine._refresh_readiness()
    engine._save()
    return instance_id


def prepared_assessment_engine(test):
    """An engine for ``test`` (an ``ActivatedPurposeHarness``) on a copy of ``assessment_preparation_instance``."""
    test.root, instance_id = restore_template(assessment_preparation_instance, config=ASSESSMENT_CONFIG)
    engine, _ = test._engine(instance_id, PurposeRunner())
    return engine
