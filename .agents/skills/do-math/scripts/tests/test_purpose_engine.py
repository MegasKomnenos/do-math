"""Purpose-level tests of the real engine with explicit scripted semantics.

The runner and compiler are test doubles. Every purpose test uses a temporary
real Git repository with the installed schemas, CAS and immutable artifacts. Neither category establishes actual-model or actual-Lean accuracy.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine, control
from research_fixtures import bare_engine, planning_model_assessments
from research_fixtures import charter_change, policy_change, disposition, seal_response, bind_candidates
from purpose_fixtures import (EXPLANATION, NEW_GOAL, ActivatedPurposeHarness, PurposeHarness, PurposeRunner, candidate,
                              parse_context, solved_instance)


class PurposeFixtureContractTests(unittest.TestCase):
    def test_goal_fixture_declares_the_empty_additional_audit_population(self):
        from do_math.contracts import schema_for
        engine = bare_engine({'governance': {}})
        action = {'role': 'goal_audit'}
        context = {'action': action, 'additional_audit_input': [], 'eligible_knowledge': [
            {'id': 'KN-goal', 'links': ['fixture-link'], 'identity_assessments': [{'decision': 'match'}]}]}
        output = PurposeRunner().answer('goal_audit', context, None)
        with tempfile.TemporaryDirectory() as directory:
            seal_response(output, context, Path(directory))
            jsonschema.validate(output, engine._governance_schema(action, schema_for('goal_audit')))
        self.assertEqual(output['additional_audits'], [])

    def test_candidate_fixture_chooses_declared_current_profile_editions(self):
        from do_math.configuration import DEFAULT_CONFIG
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
        from record_fixtures import surface_state
        from do_math.context_store import prepare_role_input
        instance, runtime = surface_state()
        runtime['tasks'] = {'TK-returned': {'id': 'TK-returned', 'status': 'waiting',
            'results': [{'execution_id': 'EX-work', 'report': 'The supplied report states the argument.'}]}}
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_plan')
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            fitted = prepare_role_input({'action': {'role': 'research_plan'}, 'resources': {},
                'ready_task_ids': [], 'knowledge_catalog': [],
                'tasks': deepcopy(list(runtime['tasks'].values()))},
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
        jsonschema.validate(extensions, submission.extension_schema(action))
        identified = model_policy.validate_assessments(action, output, extensions)
        self.assertEqual(set(identified), {'TK-selected'})
        self.assertEqual(identified['TK-selected']['difficulty'], 'high')
        self.assertEqual(identified['TK-selected']['importance'], 'medium')

    def test_restored_template_is_an_independent_copy_of_the_published_state(self):
        from do_math.repository import ResearchRepository
        from research_fixtures import restore_template
        from state_fixtures import active_instance
        config = PurposeHarness.fixture_config()
        root, instance_id = restore_template(active_instance, config=config)
        head, instance, runtime = ResearchRepository(root / 'repository', instance_id).load()
        self.assertEqual(Path(instance['workspace']), root / 'work-0')
        control(root / 'repository', instance_id, 'pause', text='Change only this copy')
        ResearchEngine(root / 'repository', instance_id, runner=PurposeRunner()).process_controls()
        self.assertNotEqual(ResearchRepository(root / 'repository', instance_id).load()[0], head)
        again = restore_template(active_instance, config=config)
        self.assertEqual(again, (root, instance_id))
        self.assertEqual(ResearchRepository(root / 'repository', instance_id).load(), (head, instance, runtime))
        self.assertFalse(list((root / 'work-0' / 'control' / instance_id).glob('*.json')))

    def test_plan_fixture_does_not_invent_a_missing_selected_task_assessment(self):
        output = {'dispositions': [{'task_id': 'TK-missing', 'kind': 'selected'}]}
        with self.assertRaisesRegex(AssertionError, 'without its supplied model assessment'):
            planning_model_assessments(output, {'tasks': [{'id': 'TK-missing'}]})


class PurposeEngineTests(ActivatedPurposeHarness):
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
        from do_math.knowledge_records import usable_links
        # The round cap is 3, so a cycle that closes in round 2 was closed by the
        # confirmed withdrawal, not by the cap.
        engine, runner = self.make('dispute', review_rounds=3)
        # Runs to the goal: the goal audit fixture checks that, after the
        # withdrawn objection, it receives only the final matching assessment.
        self.drive(engine)
        reviews = [call for call in runner.calls if call['role'] == 'identity_review']
        self.assertEqual([call['action']['stage'] for call in reviews], ['scope', 'initial', 'initial', 'organize', 'judge', 'judge', 'judge', 'answer', 'judge', 'judge', 'judge'])
        self.assertEqual(reviews[7]['action']['slot'], 'initial-0')
        self.assertEqual(set(reviews[2]['context']['role_review']['completed_results']), {'scope:1:scope'})
        self.assertFalse(any(entry['action']['stage'] == 'judge' for entry in reviews[5]['context']['role_review']['completed_results'].values()))
        item = next(item for item in engine.instance['knowledge'].values() if item['title'] == 'Natural zero identity')
        links = usable_links(engine.instance, item['id'])
        self.assertTrue(links)
        final = engine.instance['identity_assessments'][links[0]['assessment_id']]
        self.assertEqual(final['decision'], 'match')
        self.assertEqual(len(final['execution_ids']), 3)
        cycle = engine.runtime['review_cycles'][item['review_cycle_id']]
        self.assertEqual((cycle['decision'], cycle['round']), ('match', 2))

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
        # Research work reads the policy edition from its governance input.
        self.drive(engine, predicate=lambda e: any(call['role'] == 'research_work'
            and call['context']['governance']['policy_revision'] == current_policy for call in runner.calls))
        task = engine.runtime['tasks'][task['id']]
        self.assertTrue(any(r['policy_revision'] == current_policy and r['decision'] == 'approved' for r in task['reviews']))
        work = next(call for call in runner.calls if call['role'] == 'research_work'
                    and call['context']['governance']['policy_revision'] == current_policy)
        self.assertEqual(work['context']['governance']['policy_revision'], current_policy)
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
        roots = knowledge.revision_roots(engine.instance, kid)
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

    def test_live_continue_preserves_checkpoint_and_reserves_no_work_slot(self):
        from do_math.execution_profiles import resolve_profile
        engine, runner = self.make(observation='continue',  )
        # Both families first appear with their first record; earlier steps have neither.
        self.drive(engine, predicate=lambda e: any(
            row['disposition']['kind'] == 'continue' and row['target_execution_id'] in e.runtime.get('checkpoints', {})
            for row in e.runtime.get('operational_dispositions', {}).values()))
        live = [e for e in engine.runtime['executions'].values() if e['role'] == 'operational_review' and e['action'].get('live')]
        self.assertEqual(len(live), 1)
        parent = engine.runtime['executions'][live[0]['action']['target']]
        profiles = engine.instance['execution_profiles']
        # The worker's profile reserves a model work slot; the live operational
        # review's profile reserves none and so no model slot ever bounds it.
        self.assertTrue(resolve_profile(profiles, parent['execution_profile_ref'])['ai']['capacity_refs'])
        self.assertEqual(resolve_profile(profiles, live[0]['execution_profile_ref'])['ai']['capacity_refs'], [])
        self.assertEqual(live[0]['outcome'], 'output_accepted')
        self.assertFalse([row for row in engine.runtime.get('reservations', {}).values()
                          if row['owner_id'] == live[0]['id'] and row['unit'] == 'execution'])
        self.assertEqual(engine.runtime['checkpoints'][parent['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(r['target_execution_id'] == parent['id'] and r['disposition']['kind'] == 'continue'
                            for r in engine.runtime['operational_dispositions'].values()))

    def test_operating_review_runs_even_when_the_worker_used_the_last_work_call(self):
        engine, runner = self.make(observation='continue', )
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'research_work' and ex.get('outcome') == 'output_accepted'
                                                 for ex in e.runtime['executions'].values()))
        from do_math.execution_profiles import WORK_ROLES, resolve_profile
        work = [ex for ex in engine.runtime['executions'].values() if ex['role'] in WORK_ROLES]
        operating = [ex for ex in engine.runtime['executions'].values() if ex['role'] == 'operational_review']
        self.assertEqual(len(work), 2)
        self.assertEqual(len(operating), 1)
        self.assertEqual(operating[0]['outcome'], 'output_accepted')
        # The operational review holds no work slot, so exhausted work slots cannot block it.
        self.assertEqual(resolve_profile(engine.instance['execution_profiles'],
                                         operating[0]['execution_profile_ref'])['ai']['capacity_refs'], [])

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

    def test_environment_revalidation_does_not_clear_independent_meaning_dispute(self):
        from do_math.knowledge_records import usable_links
        from do_math import knowledge
        from state_fixtures import ACTIVE_LEAN_COMMAND
        # The rule starts after initialization; public activation has its own test.
        engine, _ = self.make_active(**self.fixture_config(
            plan_settle_seconds=1, lean_command=list(ACTIVE_LEAN_COMMAND)))
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


class SolvedPurposeTests(unittest.TestCase):
    """The public initialization and activation driven to the goal, built once per process.

    ``purpose_fixtures.solved_instance`` runs that path with the purpose
    scenario; these assertions read the state it published and the facts its
    build returned.
    """

    def test_public_activation_reaches_the_solution_with_archived_role_inputs(self):
        from do_math.repository import ResearchRepository
        from research_fixtures import restore_template
        root, solved = restore_template(solved_instance, criteria=None)
        store = ResearchRepository(root / 'repository', solved['instance_id'])
        snapshot, instance, runtime = store.load()
        self.assertEqual(instance['goal_status'], 'mathematically_solved')
        self.assertEqual(snapshot, solved['head'])
        self.assertTrue(all(e.get('outcome') in {'output_accepted', 'verified'} for e in runtime['executions'].values()))
        for execution in runtime['executions'].values():
            if execution.get('input_bundle'):
                # The role input manifest names the archived prompt and its digest.
                prompt = execution['input_manifest']['prompt']
                self.assertEqual(prompt['artifact_ref'], f"runtime/artifacts/{execution['input_bundle']}/input.txt")
                raw = store.read(prompt['artifact_ref'], snapshot)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), prompt['sha256'])
        self.assertEqual(solved['work_order'], ['A'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
