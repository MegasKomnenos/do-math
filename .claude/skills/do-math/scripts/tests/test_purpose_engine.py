"""Purpose-level tests of the real engine with explicit scripted semantics.

The runner and compiler are test doubles. MemoryRepository tests orchestration
with snapshot CAS and immutable artifacts; GitPurposeTests uses the real Git
repository. Neither category establishes actual-model or actual-Lean accuracy.
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


SOURCE = 'theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n'
STATEMENT = 'For every natural number n, n + 0 = n.'
EXPLANATION = 'The variable n ranges over Nat. The proof applies Nat.add_zero to that n.'
GOAL = 'Establish that adding zero to any natural number leaves it unchanged.'
NEW_GOAL = 'Establish the same zero-addition identity with the natural-number domain explicit.'
TOOLCHAIN = {'executable': 'test-double', 'sha256': 'a' * 64, 'version': 'fixture'}


class MemoryRepository:
    """Cheap test storage with CAS roots and immutable snapshot artifact bytes."""
    databases = {}

    def __init__(self, repository, instance_id):
        self.key = (str(Path(repository).resolve()), instance_id)

    def writer_lock(self):
        return nullcontext()

    def initialize(self, instance, runtime):
        if self.key in self.databases: raise ValueError('instance already exists')
        self.databases[self.key] = {'head': None, 'snapshots': {}, 'artifacts': {}, 'bundles': set()}
        return self.save(None, instance, runtime)

    def load(self, snapshot=None):
        data = self.databases[self.key]
        selected = snapshot or data['head']
        instance, runtime, _ = data['snapshots'][selected]
        return selected, deepcopy(instance), deepcopy(runtime)

    def save(self, expected_head, instance, runtime, artifacts=None):
        data = self.databases[self.key]
        if expected_head != data['head']: raise ValueError('stale snapshot CAS')
        artifacts = artifacts or {}
        bundles = {path.split('/')[2] for path in artifacts}
        if bundles & data['bundles']: raise ValueError('artifact bundle is immutable')
        if any(not isinstance(raw, bytes) for raw in artifacts.values()): raise TypeError('artifact must be bytes')
        data['artifacts'].update(artifacts)
        data['bundles'].update(bundles)
        head = hashlib.sha256(canonical_json({'sequence': len(data['snapshots']), 'instance': instance, 'runtime': runtime})).hexdigest()
        data['snapshots'][head] = (deepcopy(instance), deepcopy(runtime), dict(data['artifacts']))
        data['head'] = head
        return head

    def read(self, path, snapshot=None):
        data = self.databases[self.key]
        return data['snapshots'][snapshot or data['head']][2][path]


def parse_context(prompt, workspace):
    value = json.loads(prompt.split('--- CANONICAL INPUT CONTEXT ---\n', 1)[1].split('\n--- OUTPUT JSON SCHEMA ---', 1)[0])
    # Read exact, hash-checked catalog source files if context_store externalizes
    # a list. This is an input read, not a derivation of expected test outcomes.
    for key, entry in list(value.items()):
        if isinstance(entry, dict) and 'source_ref' in entry:
            reference = entry['source_ref']
            if isinstance(reference, dict) and reference.get('path'):
                raw = (workspace / reference['path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != reference['sha256']: raise AssertionError('catalog bytes changed')
                value[key] = json.loads(raw)
    return value


def common(summary):
    return {'summary': summary, 'used_sources': [], 'questions': []}


def candidate(title, *, formal=True, revises=None, refs=None):
    return {'revises_task_id': revises, 'title': title, 'question': 'Can the stated natural-number identity be established?',
        'scope': 'Natural numbers and addition of zero', 'expected_result': 'A proof or a precise explanation of the remaining obstacle',
        'completion_criteria': [f'{title}: report the exact argument and its domain'], 'inputs': refs or [],
        'work_class': 'formal' if formal else 'nonformal', 'reuse': refs or []}


def theorem():
    return {'kind': 'theorem', 'title': 'Natural zero identity', 'statement': STATEMENT,
            'explanation': EXPLANATION, 'summary': 'Addition of zero preserves each natural number.',
            'lean_code': SOURCE, 'declaration_names': ['add_zero_fixture'], 'dependencies': []}


def formal_fixture(*, source, declarations, workspace, lean_command, timeout_seconds,
                   allowed_axioms=(), should_stop=None):
    if source != SOURCE or declarations != ['add_zero_fixture']:
        raise AssertionError('The explicit formal test fixture only covers SOURCE/add_zero_fixture')
    return {'status': 'verified', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'declarations': declarations, 'axioms': {'add_zero_fixture': []}, 'toolchain': deepcopy(TOOLCHAIN),
            'signature_hash': hashlib.sha256(b'add_zero_fixture : (n : Nat) -> n + 0 = n').hexdigest(),
            'allowed_axioms': list(allowed_axioms), 'reason': 'Explicit compiler test double; not an actual Lean invocation'}


class PurposeRunner:
    def __init__(self, scenario='direct', *, observation=None, pause_sender=None):
        self.scenario, self.observation, self.pause_sender = scenario, observation, pause_sender
        self.calls = []
        self.work_order = []
        self.preparations = 0
        self.observed_workers = 0
        self.returned = []

    def run(self, *, prompt, output_schema, workspace, evidence_dir, model, effort,
            timeout_seconds, should_stop, on_started, on_observation=None):
        role = prompt.split('You are the do-math role: ', 1)[1].split('.', 1)[0]
        context = parse_context(prompt, workspace)
        action = context['action']
        self.calls.append({'role': role, 'action': deepcopy(action), 'context': deepcopy(context), 'workspace': str(workspace)})
        on_started({'pid': 12345, 'source': 'scripted test process identity'})
        if action.get('repair'):
            raise AssertionError('A purpose fixture must not silently adapt to an engine validation failure: ' + action['repair']['error'])
        output = self.answer(role, context, workspace)
        if role == 'research_work' and self.observation and self.observed_workers == 0:
            self.observed_workers += 1
            checkpoint = {'current_claim': STATEMENT, 'evidence_paths': ['argument.txt'],
                'attempts': ['Reconstructed Nat.add_zero'], 'remaining_work': ['Write the final report'],
                'next_step': 'Finish the explicit report', 'progress_state': 'working'}
            (workspace / 'argument.txt').write_text('The domain is Nat; Nat.add_zero supplies the equality.', encoding='utf-8')
            (workspace / 'checkpoint.json').write_bytes(canonical_json(checkpoint))
            if on_observation is None: raise AssertionError('The real engine failed to supply its observation callback')
            on_observation({'type': 'item.completed', 'item': {'type': 'agent_message', 'id': 'm1', 'text': 'The Nat domain is fixed.'}})
            time.sleep(1.05)
            on_observation({'type': 'tick'})
            if self.observation == 'external_pause':
                self.pause_sender()
            if self.observation in {'stop', 'external_pause'}:
                should_stop()
                if not (workspace / 'stop-request.json').exists(): raise AssertionError('Stop did not request a checkpoint')
                return {'status': 'stopped', 'output': None, 'usage': {'input_tokens': 30, 'output_tokens': 4}, 'error': 'Fixture honored the stop request'}
        jsonschema.validate(output, output_schema)
        self.returned.append({'role': role, 'action': deepcopy(action), 'output': deepcopy(output)})
        return {'status': 'completed', 'output': output, 'usage': {'input_tokens': 20, 'output_tokens': 10}, 'error': None}

    def answer(self, role, context, workspace):
        action = context['action']
        if role == 'research_preparation':
            self.preparations += 1
            tasks = context.get('tasks', [])
            if self.scenario == 'dependency' and not tasks:
                (workspace / 'activity-extensions.json').write_bytes(canonical_json({'task_conditions': [{
                    'task_title': 'A', 'occurrence_condition': {'op': 'task_disposition_is', 'task_id': 'B', 'value': 'completed'},
                    'dependencies': ['B']}]}))
                return {**common('Prepare B before A; the extension fixes the dependency'), 'candidates': [candidate('A'), candidate('B', formal=False)]}
            if self.scenario == 'currentness' and tasks:
                source = next(k['id'] for k in context['knowledge_catalog'] if k['title'] == 'Natural zero identity')
                return {**common('Prepare a task that explicitly consumes the certified result'),
                        'candidates': [candidate('Dependent', formal=False, refs=[source])]}
            revisable = next((t for t in tasks if t['status'] in {'needs_revision', 'planned', 'waiting'}), None)
            return {**common('Prepare the exact natural-number identity'), 'candidates': [candidate('A', revises=revisable['id'] if revisable else None)]}
        if role == 'task_contract_review':
            return {**common('The scope and criterion are precise and executable'), 'decision': 'approved', 'findings': []}
        if role == 'research_plan':
            tasks = context.get('tasks', [])
            ready = [t['id'] for t in tasks if t['status'] == 'ready']
            assessments = [{'task_id': t['id'], 'decision': 'completed', 'reason': 'The returned report states the argument and its Nat domain',
                'criteria_results': [{'criterion': criterion, 'satisfied': True, 'evidence': 'The submitted report explicitly names Nat and Nat.add_zero'}
                                     for criterion in t['completion_criteria']]} for t in tasks if t['status'] == 'assessing']
            finished = all(t['status'] in {'completed', 'assessing'} for t in tasks) and bool(tasks)
            catalog = context.get('knowledge_catalog', [])
            certified = any(k['title'] == 'Natural zero identity' and k['status'] == 'verified' for k in catalog)
            preparations = []
            if self.scenario == 'currentness' and len(tasks) == 1 and finished and certified:
                preparations = ['Prepare an explicit downstream task that uses Natural zero identity']
                finished = False
            return {**common('Select only enabled tasks and assess actual returned reports'), 'selections': ready, 'deferred': [],
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
            if not all(item.get('identity_assessment', {}).get('decision') == 'match' and item['identity_assessment'].get('effective') for item in eligible):
                raise AssertionError('Goal audit did not receive the effective final identity assessment')
            return {**common('The certified Nat zero-addition theorem meets the exact requested identity'),
                    'used_sources': [k['id'] for k in eligible], 'decision': 'satisfied', 'scope_complete': True,
                    'reason': 'The requested domain and equality coincide with the reviewed theorem.'}
        if role == 'intent_interpretation':
            if action.get('stage', 'interpret') == 'interpret':
                return {**common('The user explicitly requests the new goal below'), 'interpretation': NEW_GOAL,
                    'proposed_changes': [{'kind': 'goal', 'text': NEW_GOAL, 'reason': 'This is the preserved user request'}], 'needs_clarification': False}
            return {**common('The interpretation preserves the user request exactly'), 'decision': 'match', 'findings': [], 'scope_complete': True}
        if role == 'operational_review':
            if not action.get('live'): raise AssertionError('Unexpected execution failure triggered a non-live operational review')
            return {**common('A checkpoint and a short visible idle interval are available'),
                    'decision': 'stop' if self.observation == 'stop' else 'continue',
                    'reason': 'Stop after preserving the checkpoint' if self.observation == 'stop' else 'The exact argument is already obtained; allow the final report'}
        raise AssertionError('Unexpected fixture role: ' + role)


class PurposeHarness(unittest.TestCase):
    memory = True

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repository'
        self.repo.mkdir()
        self.runners = []
        self.engines = []
        if self.memory:
            MemoryRepository.databases = {}
            self.patch = patch.object(engine_module, 'ResearchRepository', MemoryRepository)
            self.patch.start()
            self.addCleanup(self.patch.stop)
        else:
            subprocess.run(['git', '-C', str(self.repo), 'init', '-q'], check=True)
        self.addCleanup(self.temporary.cleanup)

    def tearDown(self):
        destination = os.environ.get('DO_MATH_PURPOSE_TEST_REPORT')
        if destination:
            directory = Path(destination)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (self.id().split('.')[-1] + '.json')).write_bytes(canonical_json({
                'test': self.id(), 'repository_kind': 'memory-CAS' if self.memory else 'actual-temp-Git',
                'model_and_lean': 'Explicit test doubles',
                'engines': [{'instance': e.instance, 'runtime': e.runtime, 'head': e.head} for e in self.engines],
                'runners': [{'work_order': r.work_order, 'calls': r.calls, 'returned': r.returned} for r in self.runners]}))

    def make(self, scenario='direct', *, observation=None, **config):
        runner = PurposeRunner(scenario, observation=observation)
        initialized = initialize(self.repo, goal=GOAL, workspace=self.root / ('work-' + str(len(self.engines))),
            config={'reviewers': 2, 'goal_auditors': 2, 'review_rounds': 2, 'max_cycles': 10,
                    'work_calls': 50, 'operations_calls': 60, 'max_input_bytes': 2_000_000,
                    'lean_command': ['test-double'], 'observation_idle_seconds': 1,
                    'max_observation_reviews': 1, 'checkpoint_grace_seconds': 1, **config})
        engine = ResearchEngine(self.repo, initialized['instance_id'], runner=runner, formal_verifier=formal_fixture)
        runner.pause_sender = lambda: control(self.repo, initialized['instance_id'], 'pause', text='Stop the current research after preserving its checkpoint')
        self.runners.append(runner); self.engines.append(engine)
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
        self.assertEqual([call['action']['stage'] for call in reviews], ['initial', 'initial', 'organize', 'judge', 'judge', 'judge', 'answer', 'judge', 'judge', 'judge'])
        self.assertEqual(reviews[6]['action']['slot'], 'initial-0')
        self.assertEqual(reviews[1]['context']['role_review']['completed_results'], {})
        self.assertFalse(any(entry['stage'] == 'judge' for entry in reviews[4]['context']['role_review']['completed_results'].values()))
        item = next(item for item in engine.instance['knowledge'].values() if item['title'] == 'Natural zero identity')
        self.assertTrue(item['identity_assessment']['effective'])
        self.assertEqual(item['identity_assessment']['decision'], 'match')
        self.assertEqual(len(item['identity_assessment']['execution_ids']), 3)

    def test_policy_control_invalidates_old_contract_approval_before_work(self):
        engine, runner = self.make()
        engine.run(max_steps=2)
        task = next(iter(engine.runtime['tasks'].values()))
        self.assertEqual(task['reviews'][0]['policy_revision'], 1)
        control(self.repo, engine.instance['id'], 'decision', config={'change': {'kind': 'policy', 'text': 'Every report must name the natural-number domain explicitly.'}})
        engine.process_controls()
        self.assertEqual(engine.instance['policy_revision'], 2)
        self.assertEqual(engine.runtime['task_readiness'][task['id']]['state'], 'not_ready')
        self.drive(engine)
        task = engine.runtime['tasks'][task['id']]
        self.assertTrue(any(r['policy_revision'] == 2 and r['decision'] == 'approved' for r in task['reviews']))
        work = next(call for call in runner.calls if call['role'] == 'research_work')
        self.assertEqual(work['context']['policy_revision'], 2)

    def test_user_input_requires_distinct_interpretation_check_before_goal_change(self):
        engine, runner = self.make()
        engine.run(max_steps=2)
        control(self.repo, engine.instance['id'], 'input', text=NEW_GOAL)
        self.drive(engine)
        interpretation = next(iter(engine.runtime['interpretations'].values()))
        self.assertNotEqual(interpretation['execution_id'], interpretation['check']['execution_id'])
        self.assertEqual(interpretation['check']['decision'], 'match')
        self.assertEqual(engine.instance['goal'], NEW_GOAL)
        self.assertEqual(engine.instance['goal_revision'], 2)
        task = next(iter(engine.runtime['tasks'].values()))
        self.assertGreaterEqual(task['revision'], 2)
        self.assertTrue(all(r['goal_revision'] == 2 for r in task['reviews']))

    def test_knowledge_currentness_loss_and_revision_recover_through_fresh_review(self):
        engine, runner = self.make('currentness')
        self.drive(engine)
        item = next(item for item in engine.instance['knowledge'].values() if item['title'] == 'Natural zero identity')
        kid, previous_cycle = item['id'], item['review_cycle_id']
        downstream = next(t for t in engine.runtime['tasks'].values() if t['title'] == 'Dependent')
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation': 'invalidate', 'id': kid, 'reason': 'The previous explanation is disputed and its use is withdrawn'})
        engine.process_controls()
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        self.assertEqual(engine.runtime['tasks'][downstream['id']]['status'], 'waiting')
        self.assertFalse(engine.instance['goal_judgments'][-1]['current'])
        control(self.repo, engine.instance['id'], 'knowledge', config={'operation': 'revise', 'id': kid,
            'changes': {'explanation': EXPLANATION + ' This revision explicitly resolves the disputed domain description.'},
            'reason': 'The replacement explanation fixes the domain explicitly'})
        self.drive(engine, limit=55)
        item = engine.instance['knowledge'][kid]
        self.assertEqual(item['status'], 'verified')
        self.assertNotEqual(item['review_cycle_id'], previous_cycle)
        self.assertIn(previous_cycle, item['review_history'])
        self.assertGreaterEqual(runner.work_order.count('Dependent'), 2)
        self.assertTrue(engine.instance['goal_judgments'][-1].get('current', True))

    def test_work_budget_execution_is_not_bounded_by_operations_call_timeout(self):
        engine, runner = self.make(call_timeout_seconds=1, run_timeout_seconds=3600)
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
        self.assertTrue(work and all(timeout > 1 for timeout in work))
        self.assertTrue(operations and all(timeout <= 1 for timeout in operations))

    def test_live_continue_preserves_checkpoint_and_uses_operating_budget(self):
        engine, runner = self.make(observation='continue')
        self.drive(engine)
        live = [e for e in engine.runtime['executions'].values() if e['role'] == 'operational_review' and e['action'].get('live')]
        self.assertEqual(len(live), 1)
        parent = engine.runtime['executions'][live[0]['parent_execution_id']]
        self.assertEqual(parent['budget_kind'], 'work')
        self.assertEqual(live[0]['budget_kind'], 'operations')
        self.assertEqual(engine.runtime['checkpoints'][parent['id']]['kind'], 'worker_checkpoint')
        self.assertEqual(engine.runtime['observations'][parent['id']]['operational_decision']['decision'], 'continue')

    def test_operating_review_runs_even_when_the_worker_used_the_last_work_call(self):
        engine, runner = self.make(observation='continue', work_calls=2)
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'research_work' and ex.get('outcome') == 'output_accepted'
                                                 for ex in e.runtime['executions'].values()))
        work = [ex for ex in engine.runtime['executions'].values() if ex.get('budget_kind') == 'work']
        operating = [ex for ex in engine.runtime['executions'].values() if ex['role'] == 'operational_review']
        self.assertEqual(len(work), 2)
        self.assertEqual(len(operating), 1)
        self.assertEqual(operating[0]['outcome'], 'output_accepted')
        self.assertEqual(operating[0]['budget_kind'], 'operations')

    def test_large_history_uses_exact_context_source_files_without_losing_work(self):
        engine, runner = self.make('catalog', max_input_bytes=180000)
        self.drive(engine)
        reductions = [entry for execution in engine.runtime['executions'].values()
                      for entry in execution.get('input_reductions', [])]
        self.assertTrue(any(entry['key'] == 'tasks' for entry in reductions))
        self.assertEqual(runner.work_order, ['A'])
        plan_contexts = [call['context'] for call in runner.calls if call['role'] == 'research_plan']
        self.assertTrue(any(any(task.get('results') and len(task['results'][0]['report']) > 180000 for task in ctx['tasks'])
                            for ctx in plan_contexts))

    def test_live_stop_keeps_partial_artifacts_without_publishing_a_theorem(self):
        engine, runner = self.make(observation='stop')
        self.drive(engine, predicate=lambda e: any(ex.get('after_stop', {}).get('decision') == 'stop' and ex.get('status') == 'ended' for ex in e.runtime['executions'].values()))
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'execution_incomplete')
        self.assertEqual(worker['stop_requested'], 'operational_stop')
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertTrue(any(f['path'] == 'argument.txt' for f in worker['output_files']))
        self.assertFalse(engine.instance['knowledge'])

    def test_external_user_pause_is_processed_during_running_work(self):
        engine, runner = self.make(observation='external_pause')
        self.drive(engine, predicate=lambda e: e.runtime['status'] == 'paused')
        self.assertEqual(engine.runtime['status'], 'paused')
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'execution_incomplete')
        self.assertEqual(engine.runtime['checkpoints'][worker['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(h.get('kind') == 'user_control' and h['request']['action'] == 'pause' for h in engine.runtime['history']))
        self.assertFalse(engine.instance['knowledge'])

    def test_memory_repository_enforces_snapshot_cas_and_artifact_immutability(self):
        engine, _ = self.make()
        engine.run(max_steps=1)
        head, instance, runtime = engine.store.load()
        with self.assertRaises(ValueError): engine.store.save('stale', instance, runtime)
        execution = next(iter(runtime['executions'].values()))
        bundle = execution['input_bundle']
        with self.assertRaises(ValueError): engine.store.save(head, instance, runtime, artifacts={f'runtime/artifacts/{bundle}/new.txt': b'changed'})

    def test_environment_revalidation_does_not_clear_independent_meaning_dispute(self):
        engine, _ = self.make()
        self.drive(engine)
        kid = next(iter(engine.instance['knowledge']))
        old_environment = engine.instance['active_trust_environment']
        control(self.repo, engine.instance['id'], 'trust', config={'operation': 'invalidate', 'env_id': old_environment, 'reason': 'Compiler environment needs revalidation'})
        engine.process_controls()
        # A previously preserved independent semantic suspension is explicit test
        # input. Compiler reruns cannot supply its missing semantic judgment.
        item = engine.instance['knowledge'][kid]
        item['use_suspensions'].append({'kind': 'semantic', 'root_ids': [kid], 'reason': 'Meaning dispute remains open'})
        item['use_suspension_reasons'].append('Meaning dispute remains open')
        engine._save()
        control(self.repo, engine.instance['id'], 'trust', config={'operation': 'register',
            'toolchain': deepcopy(TOOLCHAIN), 'allowed_axioms': ['propext']})
        engine.process_controls()
        new_environment = next(env_id for env_id in engine.instance['trust_environments'] if env_id != old_environment)
        control(self.repo, engine.instance['id'], 'trust', config={'operation': 'transition', 'env_id': new_environment})
        engine.process_controls()
        self.drive(engine, predicate=lambda e: e.instance['active_trust_environment'] == new_environment)
        self.assertTrue(engine.instance['knowledge'][kid]['use_suspended'])
        self.assertEqual(engine.instance['knowledge'][kid]['use_suspensions'],
                         [{'kind': 'semantic', 'root_ids': [kid], 'reason': 'Meaning dispute remains open'}])
        self.assertEqual(engine.instance['goal_status'], 'unresolved')


class GitPurposeTests(PurposeHarness):
    memory = False

    def test_actual_temp_git_full_formal_review_and_goal_flow(self):
        engine, runner = self.make()
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
