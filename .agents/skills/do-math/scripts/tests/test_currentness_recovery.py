"""Source replacement, crash recovery and adaptive observation regression cases."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v5_fixtures import local_job_runner
from do_math.engine import control
from do_math.observations import ObservationTracker, validate_rules
from do_math.planning import task_ready, contract_hash
from do_math.input_basis import capture_decision_basis
from v5_fixtures import producer_result
from test_purpose_engine import ActiveStateHarness, common


class CurrentnessTests(ActiveStateHarness):
    def make(self, **config):
        settings = {'max_input_bytes': 2_000_000, 'max_cycles': 10,
            'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5,
            'checkpoint_grace_seconds': 1, 'observation_idle_seconds': 1,
            'max_observation_reviews': 1, 'scholarly_enabled': False, 'operator_enabled': False}
        return super().make(**{**settings, **config})

    def test_same_source_is_idempotent_changed_source_preserves_completed_task_history(self):
        engine, runner = self.make()
        source = self.root / 'source.txt'
        source.write_text('old', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        first = deepcopy(engine.instance['sources'][0])
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        self.assertEqual(first, engine.instance['sources'][0])
        answer = runner.answer
        def reading_source(role, context, workspace):
            output = answer(role, context, workspace)
            if role == 'research_preparation':
                for candidate in output['candidates']:
                    candidate['inputs'].append('source:source.txt')
            return output
        runner.answer = reading_source
        self.drive(engine, predicate=lambda e: any(t['status'] == 'completed' for t in e.runtime['tasks'].values()))
        task = next(iter(engine.runtime['tasks'].values()))
        completed_assessment = deepcopy(task['assessment'])
        from v5_fixtures import candidate, contract_review
        from do_math.planning import seal_contract_review
        downstream = {**candidate('Downstream'), 'id': 'TK-downstream', 'status': 'planned', 'revision': 1,
            'results': [], 'reviews': [], 'dependencies': [task['id']], 'occurrence_condition': {'op': 'always'},
            'profile_refs': list(task['profile_refs']), 'authority_refs': list(task['authority_refs'])}
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        downstream['reviews'] = [seal_contract_review(downstream, contract_review({'task': downstream}),
            unfinished_instance, engine.runtime, execution_id='EX-downstream-review')]
        self.assertEqual(task_ready(downstream, unfinished_instance, engine.runtime)['state'], 'ready')
        engine._save()
        source.write_text('new', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        current = engine.runtime['tasks'][task['id']]
        self.assertEqual(current['status'], 'completed')
        self.assertEqual(current['assessment']['decision'], completed_assessment['decision'])
        self.assertEqual(current['assessment']['item_dispositions'], completed_assessment['item_dispositions'])
        self.assertFalse(current['assessment']['current'])
        self.assertIn('source content changed', current['assessment']['invalidated_reason'].lower())
        self.assertEqual(engine.instance['sources'][0]['revision'], 2)
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        readiness = task_ready(downstream, unfinished_instance, engine.runtime)
        self.assertEqual(readiness['state'], 'not_ready')
        self.assertIn('blocked dependencies', readiness['errors'][0])
        self.assertFalse(any(error.startswith(task['id'] + ':') for error in engine.check()['errors']))

    def test_graceful_output_on_changed_source_is_preserved_but_not_accepted(self):
        engine, _ = self.make(max_output_repairs=0)
        source = self.root / 'basis.txt'; source.write_text('old')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        class ChangingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                source.write_text('new')
                control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
                kwargs['should_stop']()
                (kwargs['workspace'] / 'partial.txt').write_text('The old input was read.')
                return producer_result({'status': 'completed', 'output': {**common('Old-source response'),
                    'used_sources': ['basis.txt'], 'candidates': []}, 'usage': {}}, kwargs)
        engine.runner = ChangingRunner()
        engine.run(max_steps=1)
        execution = next(row for row in engine.runtime['executions'].values()
                         if row['role'] == 'research_preparation')
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['error_kind'], 'currentness_changed')
        issues = execution['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and 'source' in row['message']
                            for row in issues), issues)
        self.assertEqual(engine.runtime['cycles'], 0)
        entry = next(f for f in execution['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual(engine.store.read(entry['artifact_ref']), b'The old input was read.')

    def _plan_citing_task_while(self, change):
        engine, runner = self.make()
        self.drive(engine, predicate=lambda e: e.runtime['queue'] and e.runtime['queue'][0]['role'] == 'research_plan'
                   and bool(e._task_readiness) and any(row['state'] == 'ready' for row in e._task_readiness.values()))
        task_id = next(tid for tid, row in engine._task_readiness.items() if row['state'] == 'ready')
        answer = runner.answer
        def citing_answer(role, context, workspace):
            output = answer(role, context, workspace)
            if role == 'research_plan':
                output['used_sources'] = [*output.get('used_sources', []), task_id]
            return output
        runner.answer = citing_answer
        class ConcurrentChange:
            def run(inner, **kwargs):
                result = runner.run(**kwargs)
                change(engine.runtime['tasks'][task_id])
                return result
        engine.runner = ConcurrentChange()
        engine.run(max_steps=1)
        return engine, task_id, next(e for e in reversed(list(engine.runtime['executions'].values())) if e['role'] == 'research_plan')

    def test_cited_task_lifecycle_change_during_plan_does_not_reject_the_plan(self):
        engine, task_id, plan = self._plan_citing_task_while(
            lambda task: task.update(deferred_reason='Concurrent planner note', reviews=[*task['reviews'], {'note': 'concurrent'}]))
        self.assertEqual(plan['outcome'], 'output_accepted', plan.get('error'))
        sealed = json.loads(engine.store.read(plan['submission_intent']['output_ref']))
        self.assertIn(task_id, sealed['used_sources'])
        self.assertEqual(plan['integration_result']['status'], 'accepted')
        self.assertEqual(engine.runtime['tasks'][task_id]['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == task_id for a in engine.runtime['queue']))

    def test_cited_task_contract_change_during_plan_rejects_the_plan(self):
        engine, task_id, plan = self._plan_citing_task_while(lambda task: task.update(scope={**task['scope'], 'included': [*task['scope']['included'], 'A revised domain']}))
        self.assertEqual(plan['outcome'], 'execution_incomplete')
        self.assertEqual(plan['error_kind'], 'currentness_changed')
        issues = plan['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and
            task_id in row['message'] and 'contract_sha256' in row['message'] for row in issues), issues)
        self.assertFalse(any(a['role'] == 'research_work' and a.get('target') == task_id
                             for a in engine.runtime['queue']))

    def test_failed_execution_materials_are_restored_for_its_operational_review(self):
        engine, _ = self.make()
        class FailingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                (kwargs['workspace'] / 'partial.txt').write_text('Reusable partial result.', encoding='utf-8')
                checkpoint = {'current_claim': 'A partial lemma is established.',
                    'evidence_paths': ['partial.txt'], 'attempts': ['Checked the bounded case.'],
                    'remaining_work': ['Prove the general case.'], 'next_step': 'Resume from the partial lemma.',
                    'progress_state': 'blocked'}
                (kwargs['workspace'] / 'checkpoint.json').write_text(json.dumps(checkpoint), encoding='utf-8')
                return producer_result({'status': 'failed', 'output': None, 'usage': {}, 'error': 'fixture interruption'}, kwargs)
        engine.runner = FailingRunner()
        engine.run(max_steps=1)
        execution = next(value for value in engine.runtime['executions'].values()
                         if value['role'] == 'research_preparation')
        review = next(action for action in engine.runtime['queue'] if action['role'] == 'operational_review')
        review_workspace = self.root / 'operational-review-preview'; review_workspace.mkdir()
        context = engine._context(review, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['execution_id'], execution['id'])
        self.assertEqual((recovery['result_kind'], recovery['final_result_status']),
                         ('execution_result', 'available'))
        self.assertEqual(recovery['checkpoint'], engine.runtime['checkpoints'][execution['id']])
        for source in [recovery['result_source'], recovery['checkpoint_source'], *recovery['output_files']]:
            raw = (review_workspace / source['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
            self.assertEqual(len(raw), source['bytes'])
            self.assertEqual(engine.store.read(source['artifact_ref'], source['snapshot']), raw)
        restored = next(f for f in recovery['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual((review_workspace / restored['local_path']).read_bytes(), b'Reusable partial result.')

        activity_result = b'{"report":"A separately preserved activity result."}'
        activity_ref = 'runtime/artifacts/BA-activity-result/diagnostic.json'
        engine.runtime['executions'][execution['id']]['result_ref'] = activity_ref
        engine._save({activity_ref: activity_result})
        other_workspace = self.root / 'activity-result-review'
        other = engine._context(review, other_workspace)['recovery_materials']
        self.assertEqual((other_workspace / other['result_source']['local_path']).read_bytes(), activity_result)
        self.assertNotEqual(other['result_source']['local_path'], other['checkpoint_source']['local_path'])

    def test_recovery_captures_parent_and_inline_child_without_losing_action(self):
        engine, _ = self.make()
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        for eid, parent in [('EX-parent', None), ('EX-inline', 'EX-parent')]:
            attempt_action = action if parent is None else {'id': 'AC-inline', 'role': 'operational_review', 'target': parent}
            execution = engine._register_execution(attempt_action, {'id': eid, 'role': attempt_action['role'],
                'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': parent})
            execution['process'] = {'job_name': 'synthetic-ended-' + eid}
            folder = Path(engine.instance['workspace'])/'runs'/eid/'workspace'; folder.mkdir(parents=True)
            (folder/'partial.txt').write_text(eid)
        engine.runtime.update(active_execution='EX-parent', status='running', queue=[action])
        engine._save()
        # No process was started in this fixture. Its termination observation
        # is explicit; unknown real processes must remain unreleased.
        with patch('do_math.windows_job.named_job_empty', return_value=True), engine.store.writer_lock():
            engine._recover_disappeared()
        self.assertIsNone(engine.runtime['active_execution'])
        self.assertTrue(engine.runtime['recoveries'])
        self.assertEqual(engine.runtime['waiting_actions']['AC-fixture']['execution_id'], 'EX-parent')
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == 'EX-parent'
                            for a in engine.runtime['queue']))
        for eid in ('EX-parent', 'EX-inline'):
            execution = engine.runtime['executions'][eid]
            self.assertEqual(execution['status'], 'ended')
            self.assertEqual(engine.store.read(execution['output_files'][0]['artifact_ref']), eid.encode())
        review_workspace = self.root / 'disappeared-review-preview'; review_workspace.mkdir()
        context = engine._context({'role': 'operational_review', 'target': 'EX-parent'}, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['result_kind'], 'checkpoint_recovery')
        self.assertEqual(recovery['final_result_status'], 'not_produced')
        self.assertEqual(recovery['result_source'], recovery['checkpoint_source'])
        self.assertTrue((review_workspace / recovery['result_source']['local_path']).is_file())

    def test_live_rules_repeat_exact_thresholds_and_preserve_last_valid_update(self):
        folder = self.root / 'observed'; folder.mkdir()
        clock = [0]
        rules = [{'id': 'steps', 'operator': 'counter_gte', 'subject': {'kind': 'counter', 'id': 'attempts'},
                  'basis': {'source': 'execution_events', 'unit': 'count'}, 'threshold': 2,
                  'repeat_interval': 2, 'required_evidence': ['EV-iteration']}]
        tracker = ObservationTracker('EX', folder, {'observation_contract_version': 5,
            'observation_rules': rules, 'self_check_response_window_seconds': 60}, clock=lambda: clock[0])
        first = next(row for row in tracker.observe({'type': 'tick', 'counters': {'attempts': 2}})
                     if row['kind'] == 'self_check_due')
        self.assertEqual(first['due'][0]['boundary'], 2)
        self.assertFalse(any(row['kind'] == 'self_check_due' for row in
                             tracker.observe({'type': 'tick', 'counters': {'attempts': 2}})))
        (folder / 'observation-rules.json').write_text('{')
        events = tracker.observe({'type': 'tick', 'counters': {'attempts': 4}})
        second = next(row for row in events if row['kind'] == 'self_check_due')
        self.assertEqual(second['due'][0]['boundary'], 4)
        self.assertTrue(any(row['kind'] == 'observation_rules_rejected' for row in events))
        self.assertEqual(tracker.rules, rules)
        with self.assertRaises(ValueError):
            validate_rules([{**rules[0], 'threshold': True}])



if __name__ == '__main__': unittest.main()
