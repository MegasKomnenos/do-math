"""Purpose-level tests of the real engine with explicit scripted semantics.

The runner and compiler are test doubles. Every purpose test uses a temporary
real Git repository with the installed schemas, CAS and immutable artifacts. Neither category establishes actual-model or actual-Lean accuracy.
"""
from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_math.engine as engine_module
from do_math.engine import ResearchEngine, initialize, control
from do_math.repository import canonical_json
from research_fixtures import local_job_runner, planning_model_assessments, supply_observation_rules, read_fixture_context
from research_fixtures import (charter_change, policy_change, candidate as v5_candidate, contract_review, disposition, assessment,
                         intent_response, seal_response, submit_intent, activate, install_adapter_fixture, bind_candidates)
from test_engine import ScriptedRunner, formal_ok


SOURCE = 'theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n'
STATEMENT = 'For every natural number n, n + 0 = n.'
EXPLANATION = 'The variable n ranges over Nat. The proof applies Nat.add_zero to that n.'
GOAL = 'Establish that adding zero to any natural number leaves it unchanged.'
NEW_GOAL = 'Establish the same zero-addition identity with the natural-number domain explicit.'
TOOLCHAIN = {'executable': 'test-double', 'sha256': 'a' * 64, 'version': 'fixture'}


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
                   allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None):
    if source != SOURCE or declarations != ['add_zero_fixture']:
        raise AssertionError('The explicit formal test fixture only covers SOURCE/add_zero_fixture')
    result = formal_ok(source=source, declarations=declarations, workspace=workspace,
        lean_command=lean_command,  allowed_axioms=allowed_axioms, expected_toolchain=expected_toolchain)
    result['dependency_closure'] = {'add_zero_fixture': ['Nat', 'Nat.add_zero']}
    result['dependency_evidence'] = {'add_zero_fixture': {'Nat': 'fixture-Nat', 'Nat.add_zero': 'fixture-Nat.add_zero'}}
    result['declaration_evidence'] = {'add_zero_fixture': {'type': '(n : Nat) -> n + 0 = n', 'value': 'Nat.add_zero'}}
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
        self.calls.append({'role': role, 'action': deepcopy(action), 'context': deepcopy(context), 'workspace': str(workspace)})
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
            on_observation({'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'm1', 'text': 'The Nat domain is fixed.'}})
            if self.observation == 'external_pause':
                self.pause_sender()
            else:
                on_observation({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
                time.sleep(1.05)
                on_observation({'type': 'tick'})
                until = time.monotonic() + 120
                while time.monotonic() < until:
                    if should_stop():
                        break
                    feedback = workspace / '.control/observation-feedback.json'
                    if feedback.exists() and json.loads(feedback.read_bytes()).get('kind') == 'continue':
                        break
                    time.sleep(.05)
                else:
                    raise AssertionError('The live reviewer did not return its disposition')
                if self.observation == 'continue':
                    on_observation({'type': 'item.completed', 'item': {'type': 'command_execution', 'id': 'observed-tool'}})
            if self.observation in {'stop', 'external_pause'}:
                should_stop()
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
        if role == 'research_preparation' and context.get('budget_unit') == 'concurrent_sessions':
            from test_engine import contract_checks
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            targets = action.get('assessment_targets')
            identities = ([{'task_id': tid} for tid in targets] if targets else
                          [{'task_title': c['title']} for c in output['candidates']])
            extensions['model_assessments'] = [{**identity, 'difficulty': 'low', 'importance': 'medium',
                'reason': 'The fixture supplies a bounded natural-number identity'} for identity in identities]
            if output['candidates']:
                extensions['contract_checks'] = contract_checks(output['candidates'])
                if self.scenario == 'dependency':
                    for check in extensions['contract_checks']:
                        if check['task_title'] == 'A':
                            check['outcome_branches'] = [
                                {'outcome': 'B establishes the natural-number domain',
                                 'completion': 'Use the established domain to prove the identity'},
                                {'outcome': 'B leaves the domain unresolved',
                                 'completion': 'Preserve the unmet premise and do not claim the identity'}]
            path.write_bytes(canonical_json(extensions))
        if role == 'research_plan' and context.get('budget_unit') == 'concurrent_sessions':
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
            from research_fixtures import prepared_rule_conditions
            path = workspace / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes()) if path.exists() else {}
            extensions['task_conditions'] = prepared_rule_conditions(action['observation_rule_targets'])
            path.write_bytes(canonical_json(extensions))
        bind_candidates(output, context)
        seal_response(output, context, workspace)
        jsonschema.validate(output, output_schema)
        submit_intent(control_binding, should_stop, workspace, output)
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
                from research_fixtures import scope_response
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


class PurposeFixtureContractTests(unittest.TestCase):
    def test_goal_fixture_declares_the_empty_additional_audit_population(self):
        from do_math.contracts import schema_for
        engine = object.__new__(ResearchEngine)
        engine.instance = {'governance': {}}
        action = {'role': 'goal_audit'}
        context = {'action': action, 'additional_audit_input': [], 'eligible_knowledge': [
            {'id': 'KN-goal', 'links': ['fixture-link'], 'identity_assessments': [{'decision': 'match'}]}]}
        output = PurposeRunner().answer('goal_audit', context, None)
        with tempfile.TemporaryDirectory() as directory:
            seal_response(output, context, Path(directory))
            jsonschema.validate(output, engine._governance_schema(action, schema_for('goal_audit')))
        self.assertEqual(output['additional_audits'], [])

    def test_candidate_fixture_chooses_declared_current_profile_editions(self):
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        prior = build_profiles(DEFAULT_CONFIG)
        current = build_profiles({**DEFAULT_CONFIG, 'tool_review_window_seconds':60,
                                  'self_check_response_window_seconds':5})
        context = {'execution_profiles':list({**prior['execution_profiles'],**current['execution_profiles']}.values()),
                   'role_profile_refs':current['role_profile_refs'], 'grants':[]}
        output = {'candidates':[candidate('one exact edition per model')]}
        bind_candidates(output,context)
        self.assertEqual(output['candidates'][0]['profile_refs'],
                         [r for r in current['role_profile_refs']['research_work']])

    def test_fixture_reads_returned_report_from_the_actual_supplied_task_source(self):
        from test_redesign_SURFACE import surface_state
        from do_math.context_store import prepare_role_input
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'results': [{'execution_id': 'EX-work', 'report': 'The supplied report states the argument.'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fitted = prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {},
                'ready_task_ids': [], 'knowledge_catalog': [], 'tasks': deepcopy(list(runtime['tasks'].values()))},
                instance=instance, runtime=runtime, role='research_plan', profile=profile,
                snapshot='a'*40, workspace=workspace, activity_id='AC-1')
            self.assertNotIn('results', fitted['context']['tasks'][0])
            observed = parse_context(fitted['prompt'], workspace)
            self.assertEqual(observed['tasks'][0]['results'], runtime['tasks']['TK-returned']['results'])

    def test_completed_comparison_population_can_request_audit_from_the_supplied_usable_goal_result(self):
        context = {'action': {'role': 'research_plan'}, 'tasks': [], 'ready_task_ids': [],
                   'knowledge_catalog': [{'id': 'KN-goal', 'title': 'Natural zero identity', 'usable_as_k': True}]}
        output = PurposeRunner().answer('research_plan', context, None)
        self.assertTrue(output['goal_audit'])
        context['knowledge_catalog'][0]['usable_as_k'] = False
        self.assertFalse(PurposeRunner().answer('research_plan', context, None)['goal_audit'])
        context['action'] = {'role': 'research_preparation'}
        for usable in (False, True):
            context['knowledge_catalog'][0]['usable_as_k'] = usable
            self.assertEqual(PurposeRunner().answer('research_preparation', context, None)['candidates'], [])

    def test_plan_fixture_assesses_exactly_the_selected_task_population(self):
        from do_math import model_policy, submission
        action = {'role': 'research_plan'}
        output = {'dispositions': [
            disposition('TK-selected'), disposition('TK-deferred', kind='not_selected')]}
        context = {'tasks': [
            {'id': 'TK-selected', 'model_assessment': {'difficulty': 'high', 'importance': 'medium'}},
            {'id': 'TK-deferred', 'model_assessment': {'difficulty': 'low', 'importance': 'low'}}]}
        extensions = {'model_assessments': planning_model_assessments(output, context)}
        jsonschema.validate(extensions, submission.extension_schema(action, {}))
        identified = model_policy.validate_assessments(action, output, extensions, required=True)
        self.assertEqual(set(identified), {'TK-selected'})
        self.assertEqual(identified['TK-selected']['difficulty'], 'high')
        self.assertEqual(identified['TK-selected']['importance'], 'medium')

    def test_plan_fixture_does_not_invent_a_missing_selected_task_assessment(self):
        output = {'dispositions': [{'task_id': 'TK-missing', 'kind': 'selected'}]}
        with self.assertRaisesRegex(AssertionError, 'without its supplied model assessment'):
            planning_model_assessments(output, {'tasks': [{'id': 'TK-missing'}]})


class PurposeHarness(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repository'
        self.repo.mkdir()
        self.runners = []
        self.engines = []
        subprocess.run(['git', '-C', str(self.repo), 'init', '-q'], check=True)
        install_adapter_fixture(self)
        self.addCleanup(self.temporary.cleanup)

    def tearDown(self):
        destination = os.environ.get('DO_MATH_PURPOSE_TEST_REPORT')
        if destination:
            directory = Path(destination)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (self.id().split('.')[-1] + '.json')).write_bytes(canonical_json({
                'test': self.id(), 'repository_kind': 'actual-temp-Git',
                'model_and_lean': 'Explicit test doubles',
                'engines': [{'instance': e.instance, 'runtime': e.runtime, 'head': e.head} for e in self.engines],
                'runners': [{'work_order': r.work_order, 'calls': r.calls, 'returned': r.returned} for r in self.runners]}))

    @staticmethod
    def fixture_config(**config):
        settings = {'reviewers': 2, 'goal_auditors': 2, 'review_rounds': 2,
                    'plan_settle_seconds': 1,
                    'max_input_bytes': 2_000_000,
                    'lean_command': ['test-double'], 'observation_idle_seconds': 1,
                    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5,
                    'max_observation_reviews': 1, 'checkpoint_grace_seconds': 1,
                    'scholarly_enabled': False, 'operator_enabled': False, **config}
        return settings

    def make(self, scenario='direct', *, observation=None, external_policy='disabled', review_policy=None, **config):
        if observation in {'continue', 'stop'}:
            config.setdefault('tool_review_window_seconds', 1)
        runner = PurposeRunner(scenario, observation=observation)
        initialized = initialize(self.repo, goal=GOAL, workspace=self.root / ('work-' + str(len(self.engines))),
                                 config=self.fixture_config(**config))
        engine = ResearchEngine(self.repo, initialized['instance_id'], runner=runner, formal_verifier=formal_fixture)
        runner.pause_sender = lambda: control(self.repo, initialized['instance_id'], 'pause', text='Stop the current research after preserving its checkpoint')
        self.runners.append(runner); self.engines.append(engine)
        activate(engine, self.root, initialization_runner=ScriptedRunner(), external_policy=external_policy,
                 review_policy=review_policy)
        return engine, runner

    def drive(self, engine, predicate=None, limit=45):
        predicate = predicate or (lambda e: e.instance['goal_status'] == 'mathematically_solved')
        for _ in range(limit):
            engine.run(max_steps=1)
            if predicate(engine): return
            if engine.runtime['status'] in {'paused', 'closed', 'budget_exhausted', 'waiting'}:
                self.fail('Workflow stopped before its fixture outcome: ' + json.dumps({
                    'status': engine.runtime['status'], 'questions': engine.runtime['questions'],
                    'queue': engine.runtime['queue'], 'executions': [{k: ex.get(k) for k in ('role', 'outcome', 'error')} for ex in engine.runtime['executions'].values()]}, ensure_ascii=False))
        self.fail('Fixture did not finish within its bounded scenario: ' + str(engine.status()))


class ActiveStateHarness(PurposeHarness):
    """Start focused post-initialization checks from validated synthetic state."""

    def make(self, **config):
        from state_fixtures import active_engine
        from test_lifecycle_engine import AdapterDouble
        self.enterContext(patch('do_math.initialization.adapter_for', return_value=AdapterDouble()))
        runner = PurposeRunner()
        engine = active_engine(self.repo, self.root / ('work-' + str(len(self.engines))),
            config=config, runner=runner, formal_verifier=formal_fixture)
        self.runners.append(runner)
        self.engines.append(engine)
        return engine, runner


class PurposeEngineTests(PurposeHarness):
    def test_task_dependency_extension_blocks_A_until_B_completed_then_solves_goal(self):
        engine, runner = self.make('dependency')
        self.drive(engine)
        self.assertEqual(runner.work_order, ['B', 'A'])
        tasks = {t['title']: t for t in engine.runtime['tasks'].values()}
        self.assertEqual(tasks['A']['dependencies'], [tasks['B']['id']])
        self.assertNotIn('"task_id": "B"', json.dumps(tasks['A']['occurrence_condition']))
        self.assertTrue(all(task['status'] == 'completed' for task in tasks.values()))
        self.assertEqual(engine.status()['knowledge']['K'], 1)
        self.assertTrue(any(ex['role'] == 'formal_check' for ex in engine.runtime['executions'].values()))

    def test_objection_judgment_answer_and_final_approval_use_real_engine(self):
        engine, runner = self.make('dispute')
        self.drive(engine)
        reviews = [call for call in runner.calls if call['role'] == 'identity_review']
        self.assertEqual([call['action']['stage'] for call in reviews], ['scope', 'initial', 'initial', 'organize', 'judge', 'judge', 'judge', 'answer', 'judge', 'judge', 'judge'])
        self.assertEqual(reviews[7]['action']['slot'], 'initial-0')
        self.assertEqual(set(reviews[2]['context']['role_review']['completed_results']), {'scope:1:scope'})
        self.assertFalse(any(entry['action']['stage'] == 'judge' for entry in reviews[5]['context']['role_review']['completed_results'].values()))
        item = next(item for item in engine.instance['knowledge'].values() if item['title'] == 'Natural zero identity')
        from do_math.knowledge_records import usable_links
        links = usable_links(engine.instance, item['id'])
        self.assertTrue(links)
        final = engine.instance['identity_assessments'][links[0]['assessment_id']]
        self.assertEqual(final['decision'], 'match')
        self.assertEqual(len(final['execution_ids']), 3)

    def test_policy_control_invalidates_old_contract_approval_before_work(self):
        engine, runner = self.make()
        self.drive(engine, predicate=lambda e: any(t.get('reviews') for t in e.runtime['tasks'].values()))
        task = next(t for t in engine.runtime['tasks'].values() if t.get('reviews'))
        previous_policy = engine._governance()['policy_revision']
        self.assertEqual(task['reviews'][0]['policy_revision'], previous_policy)
        control(self.repo, engine.instance['id'], 'decision', config={'change': policy_change(engine, 'Every report must name the natural-number domain explicitly.')})
        engine.process_controls()
        current_policy = engine._governance()['policy_revision']
        self.assertNotEqual(current_policy, previous_policy)
        self.assertEqual(engine._task_readiness[task['id']]['state'], 'not_ready')
        self.drive(engine, predicate=lambda e: any(call['role'] == 'research_work'
            and call['context']['policy_revision'] == current_policy for call in runner.calls))
        task = engine.runtime['tasks'][task['id']]
        self.assertTrue(any(r['policy_revision'] == current_policy and r['decision'] == 'approved' for r in task['reviews']))
        work = next(call for call in runner.calls if call['role'] == 'research_work'
                    and call['context']['policy_revision'] == current_policy)
        self.assertEqual(work['context']['policy_revision'], current_policy)
        self.assertTrue(any(ex['role'] == 'research_work' and ex.get('outcome') == 'output_accepted'
                            for ex in engine.runtime['executions'].values()))

    def test_user_input_is_independently_checked_without_becoming_goal_authority(self):
        engine, runner = self.make()
        before = deepcopy(engine._governance()['charter'])
        control(self.repo, engine.instance['id'], 'input', text=NEW_GOAL)
        self.drive(engine, predicate=lambda e: any(b['source']['text'] == NEW_GOAL and b.get('check')
                                                  for b in e.runtime.get('intent_imports', {}).values()))
        bundle = next(b for b in engine.runtime['intent_imports'].values() if b['source']['text'] == NEW_GOAL)
        self.assertNotEqual(bundle['execution_id'], bundle['check']['execution_id'])
        self.assertEqual(bundle['check']['decision'], 'approved')
        self.assertEqual(engine._governance()['charter'], before)
        self.assertTrue(any(w['kind'] == 'import_application_authority' for w in engine.runtime['waiting_actions'].values()))
        # An exact public decision, separate from the model's semantic check,
        # authorizes the new goal and preserves the previous charter.
        from research_fixtures import send_control
        send_control(engine, 'decision', config={'change': charter_change(engine, goal=NEW_GOAL,
            success_criteria=[NEW_GOAL], included_scope=[NEW_GOAL])})
        self.assertEqual(engine._governance()['goal'], NEW_GOAL)
        self.assertEqual(engine.instance['governance'][before['id']]['status'], 'superseded')

    def test_knowledge_currentness_loss_and_revision_recover_through_fresh_review(self):
        engine, runner = self.make('currentness')
        self.drive(engine, predicate=lambda e: any(t['title'] == 'Dependent' and t['status'] == 'completed'
                                                   for t in e.runtime['tasks'].values()))
        completed_downstream = {t['id']: deepcopy(t['results']) for t in engine.runtime['tasks'].values()
                                if t['title'] == 'Dependent' and t['status'] == 'completed'}
        self.assertTrue(completed_downstream)
        downstream_work_before_revision = runner.work_order.count('Dependent')
        item = next(item for item in engine.instance['knowledge'].values() if item['title'] == 'Natural zero identity')
        kid, previous_cycle = item['id'], item['review_cycle_id']
        previous_assessments = deepcopy(engine.instance['identity_assessments'])
        downstream = next(t for t in engine.runtime['tasks'].values() if t['title'] == 'Dependent')
        from do_math import knowledge
        from research_fixtures import send_control
        send_control(engine, 'knowledge', config={'operation': 'invalidate', 'id': kid,
            'reason': 'The previous explanation is disputed and its use is withdrawn',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, [kid], [])['computed_impact']})
        self.assertEqual(engine.instance['goal_status'], 'unsolved')
        suspended = engine.runtime['tasks'][downstream['id']]
        self.assertEqual(suspended['status'], 'completed')
        self.assertFalse(suspended['assessment']['current'])
        self.assertTrue(any('disputed' in row['reason'] for row in suspended['use_history']))
        self.assertFalse(any(j.get('current') for j in engine.instance.get('goal_judgments', [])))
        changes = {'explanation': EXPLANATION + ' This revision explicitly resolves the disputed domain description.'}
        roots = knowledge.revision_roots(engine.instance, kid, changes)
        send_control(engine, 'knowledge', config={'operation': 'revise', 'id': kid, 'changes': changes,
            'reason': 'The replacement explanation fixes the domain explicitly',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, roots, [])['computed_impact']})
        replacement_id = next(row['id'] for row in engine.instance['knowledge'].values() if row.get('supersedes') == kid)
        self.drive(engine, limit=55)
        item = engine.instance['knowledge'][replacement_id]
        self.assertTrue(__import__('do_math.knowledge_records', fromlist=['usable_links']).usable_links(engine.instance, replacement_id))
        self.assertNotEqual(item['review_cycle_id'], previous_cycle)
        self.assertIn(previous_cycle, engine.runtime['review_cycles'])
        self.assertEqual(engine.instance['knowledge'][kid]['lifecycle'], 'superseded')
        for identifier, record in previous_assessments.items():
            self.assertEqual(engine.instance['identity_assessments'][identifier], record)
        preserved = engine.runtime['tasks'][downstream['id']]
        self.assertEqual(preserved['status'], 'completed')
        self.assertFalse(preserved['assessment']['current'])
        self.assertEqual(runner.work_order.count('Dependent'), downstream_work_before_revision)
        for task_id, results in completed_downstream.items():
            task = engine.runtime['tasks'][task_id]
            self.assertEqual(task['status'], 'completed')
            self.assertEqual(task['results'], results)
            self.assertFalse(task['assessment']['current'])
        self.assertTrue(engine.instance['goal_judgments'][-1].get('current', True))

    def test_work_budget_execution_is_not_bounded_by_operations_call_timeout(self):
        engine, runner = self.make(call_timeout_seconds=1, )
        seen = []
        original = runner.run
        def recording_run(**arguments):
            role = arguments['prompt'].split('You are the do-math role: ', 1)[1].split('.', 1)[0]
            seen.append((role, arguments['timeout_seconds']))
            return original(**arguments)
        runner.run = recording_run
        self.drive(engine, predicate=lambda current: any(role == 'research_work' for role, _ in seen))
        work = [timeout for role, timeout in seen if role in {'research_work', 'task_contract_review'}]
        operations = [timeout for role, timeout in seen if role in {'research_preparation', 'research_plan'}]
        self.assertTrue(work and all(timeout is None for timeout in work))
        self.assertTrue(operations and all(timeout <= 1 for timeout in operations))

    def test_live_continue_preserves_checkpoint_and_uses_operating_budget(self):
        engine, runner = self.make(observation='continue',  )
        self.drive(engine, predicate=lambda e: any(
            row['disposition']['kind'] == 'continue' and row['target_execution_id'] in e.runtime['checkpoints']
            for row in e.runtime['operational_dispositions'].values()))
        live = [e for e in engine.runtime['executions'].values() if e['role'] == 'operational_review' and e['action'].get('live')]
        self.assertEqual(len(live), 1)
        parent = engine.runtime['executions'][live[0]['action']['target']]
        self.assertEqual(parent['budget_kind'], 'work')
        self.assertEqual(live[0]['budget_kind'], 'operations')
        self.assertEqual(live[0]['outcome'], 'output_accepted')
        self.assertIsNone(engine.status()['budget']['operations']['limit'])
        self.assertEqual(engine.runtime['checkpoints'][parent['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(r['target_execution_id'] == parent['id'] and r['disposition']['kind'] == 'continue'
                            for r in engine.runtime['operational_dispositions'].values()))

    def test_operating_review_runs_even_when_the_worker_used_the_last_work_call(self):
        engine, runner = self.make(observation='continue', )
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'research_work' and ex.get('outcome') == 'output_accepted'
                                                 for ex in e.runtime['executions'].values()))
        work = [ex for ex in engine.runtime['executions'].values() if ex.get('budget_kind') == 'work']
        operating = [ex for ex in engine.runtime['executions'].values() if ex['role'] == 'operational_review']
        self.assertEqual(len(work), 2)
        self.assertEqual(len(operating), 1)
        self.assertEqual(operating[0]['outcome'], 'output_accepted')
        self.assertEqual(operating[0]['budget_kind'], 'operations')

    def test_large_history_uses_exact_context_source_files_without_losing_work(self):
        engine, runner = self.make('catalog')
        self.drive(engine, predicate=lambda e: any(call['role'] == 'research_plan'
            and any(task.get('results') and len(task['results'][0]['report']) > 180000
                    for task in call['context']['tasks']) for call in runner.calls))
        # Comparison population stays direct. Large record details are exact
        # sources independently of optional whole-field input reductions.
        task_sources = [entry for execution in engine.runtime['executions'].values()
                        if execution.get('role') == 'research_plan' and execution.get('outcome') == 'output_accepted'
                        and isinstance(execution.get('input_manifest'), dict)
                        for entry in execution.get('input_manifest', {}).get('detail_sources', [])
                        if entry['path'].startswith('input/details/tasks/') and entry['bytes'] > 180000]
        self.assertTrue(task_sources)
        for entry in task_sources:
            raw = engine.store.read(entry['artifact_ref'], engine.head)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry['sha256'])
            self.assertEqual(len(raw), entry['bytes'])
        self.assertEqual(runner.work_order, ['A'])
        plan_contexts = [call['context'] for call in runner.calls if call['role'] == 'research_plan']
        self.assertTrue(any(any(task.get('results') and len(task['results'][0]['report']) > 180000 for task in ctx['tasks'])
                            for ctx in plan_contexts))

    def test_live_retry_stops_the_attempt_and_keeps_partial_artifacts_without_publishing_a_theorem(self):
        engine, runner = self.make(observation='stop')
        self.drive(engine, predicate=lambda e: any(ex.get('stop_requested') == 'operational_retry' and ex.get('status') == 'ended' for ex in e.runtime['executions'].values()))
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'execution_incomplete')
        self.assertEqual(worker['stop_requested'], 'operational_retry')
        self.assertTrue(any(a.get('continuation_of') == worker['id'] for a in engine.runtime['queue']))
        self.assertTrue(any(f['path'] == 'argument.txt' for f in worker['output_files']))
        self.assertFalse(engine.instance['knowledge'])

    def test_external_user_pause_is_processed_during_running_work(self):
        engine, runner = self.make(observation='external_pause')
        self.drive(engine, predicate=lambda e: e.runtime['status'] == 'paused')
        self.assertEqual(engine.runtime['status'], 'paused')
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'cancelled')
        self.assertEqual(engine.runtime['checkpoints'][worker['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(h.get('kind') == 'user_control' and h['request']['action'] == 'pause' for h in engine.runtime['history']))
        self.assertFalse(engine.instance['knowledge'])

    def test_repository_enforces_snapshot_cas_and_artifact_immutability(self):
        engine, _ = self.make()
        engine.run(max_steps=1)
        head, instance, runtime = engine.store.load()
        with self.assertRaises(ValueError): engine.store.save_with_state('stale', instance, runtime)[0]
        execution = next(ex for ex in runtime['executions'].values() if ex.get('input_bundle'))
        bundle = execution['input_bundle']
        with self.assertRaises(ValueError): engine.store.save_with_state(head, instance, runtime, artifacts={f'runtime/artifacts/{bundle}/new.txt': b'changed'})[0]

    def test_environment_revalidation_does_not_clear_independent_meaning_dispute(self):
        from do_math.knowledge_records import usable_links
        from do_math import knowledge
        engine, _ = self.make(plan_settle_seconds=1)
        self.drive(engine, predicate=lambda e: any(usable_links(e.instance, kid) for kid in e.instance['knowledge']))
        kid = next(iter(engine.instance['knowledge']))
        old_environment = engine.instance['active_trust_environment']
        control(self.repo, engine.instance['id'], 'trust', config={'operation': 'invalidate', 'env_id': old_environment, 'reason': 'Compiler environment needs revalidation'})
        engine.process_controls()
        from research_fixtures import send_control, trust_fixture
        send_control(engine, 'knowledge', config={'operation': 'invalidate', 'id': kid,
            'reason': 'Meaning dispute remains open',
            'declared_impact': knowledge.plan_impact(engine.instance, engine.runtime, [kid], [])['computed_impact']})
        before_assessments = deepcopy(engine.instance['identity_assessments'])
        self.assertEqual(usable_links(engine.instance, kid), [])
        send_control(engine, 'trust', config=trust_fixture(self.root / 'replacement-environment',
            engine.instance['config']['lean_command']))
        new_environment = next(env_id for env_id in engine.instance['trust_environments'] if env_id != old_environment)
        send_control(engine, 'trust', config={'operation': 'transition', 'env_id': new_environment})
        self.drive(engine, predicate=lambda e: e.instance['active_trust_environment'] == new_environment)
        self.assertEqual(engine.instance['identity_assessments'], before_assessments)
        self.assertEqual(usable_links(engine.instance, kid), [])
        self.assertEqual(engine.instance['goal_status'], 'unsolved')


class GitPurposeTests(PurposeHarness):
    def test_actual_temp_git_full_formal_review_and_goal_flow(self):
        # This single-goal path does not test delayed review batching.
        engine, runner = self.make(plan_settle_seconds=1)
        self.drive(engine)
        snapshot, instance, runtime = engine.store.load()
        self.assertEqual(instance['goal_status'], 'mathematically_solved')
        self.assertEqual(snapshot, engine.head)
        self.assertTrue(all(e.get('outcome') in {'output_accepted', 'verified'} for e in runtime['executions'].values()))
        for execution in runtime['executions'].values():
            if execution.get('input_bundle'):
                raw = engine.store.read(f"runtime/artifacts/{execution['input_bundle']}/input.txt", snapshot)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), execution['input_sha256'])
        self.assertEqual(runner.work_order, ['A'])
        report = os.environ.get('DO_MATH_PURPOSE_TEST_REPORT')
        if report:
            destination = Path(report)
            destination.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', '-C', str(self.repo), 'bundle', 'create', str(destination / 'purpose-git.bundle'), '--all'], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    program = unittest.main(verbosity=2, exit=False)
    report = os.environ.get('DO_MATH_PURPOSE_TEST_REPORT')
    if report:
        destination = Path(report)
        destination.mkdir(parents=True, exist_ok=True)
        label = 'git' if any('GitPurposeTests' in arg for arg in sys.argv[1:]) else 'memory' if any('PurposeEngineTests' in arg for arg in sys.argv[1:]) else 'all'
        (destination / f'{label}-results.json').write_bytes(canonical_json({'tests_run': program.result.testsRun,
            'passed': program.result.wasSuccessful(), 'failures': [{'test': str(test), 'traceback': trace} for test, trace in program.result.failures],
            'errors': [{'test': str(test), 'traceback': trace} for test, trace in program.result.errors],
            'skipped': [{'test': str(test), 'reason': reason} for test, reason in program.result.skipped]}))
    sys.exit(0 if program.result.wasSuccessful() else 1)
