"""Source replacement, crash recovery and adaptive observation regression cases."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control
from do_math.observations import ObservationTracker, validate_rules
from do_math.planning import task_ready
from test_purpose_engine import PurposeHarness, common


class CurrentnessTests(PurposeHarness):
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
        self.drive(engine)
        task = next(iter(engine.runtime['tasks'].values()))
        task['inputs'] = ['source:source.txt']
        completed_assessment = deepcopy(task['assessment'])
        downstream = {'id': 'TK-downstream', 'status': 'planned', 'revision': 1,
                      'reviews': [{'revision': 1, 'decision': 'approved', 'inputs_current': True}],
                      'inputs': [], 'reuse': [], 'dependencies': [task['id']],
                      'occurrence_condition': {'op': 'always'}}
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        self.assertEqual(task_ready(downstream, unfinished_instance, engine.runtime)['state'], 'ready')
        engine._save()
        source.write_text('new', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        current = engine.runtime['tasks'][task['id']]
        self.assertEqual(current['status'], 'completed')
        self.assertEqual(current['assessment']['decision'], completed_assessment['decision'])
        self.assertEqual(current['assessment']['criteria_results'], completed_assessment['criteria_results'])
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
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                source.write_text('new')
                control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
                kwargs['should_stop']()
                (kwargs['workspace'] / 'partial.txt').write_text('The old input was read.')
                return {'status': 'completed', 'output': {**common('Old-source response'), 'candidates': []}, 'usage': {}}
        engine.runner = ChangingRunner()
        engine.run(max_steps=1)
        execution = list(engine.runtime['executions'].values())[-1]
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertIn('source content changed', execution['error'])
        self.assertEqual(engine.runtime['cycles'], 0)
        entry = next(f for f in execution['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual(engine.store.read(entry['artifact_ref']), b'The old input was read.')

    def test_failed_execution_materials_are_restored_for_its_operational_review(self):
        engine, _ = self.make()
        class FailingRunner:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                (kwargs['workspace'] / 'partial.txt').write_text('Reusable partial result.', encoding='utf-8')
                checkpoint = {'current_claim': 'A partial lemma is established.',
                    'evidence_paths': ['partial.txt'], 'attempts': ['Checked the bounded case.'],
                    'remaining_work': ['Prove the general case.'], 'next_step': 'Resume from the partial lemma.',
                    'progress_state': 'blocked'}
                (kwargs['workspace'] / 'checkpoint.json').write_text(json.dumps(checkpoint), encoding='utf-8')
                return {'status': 'failed', 'output': None, 'usage': {}, 'error': 'fixture interruption'}
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
        engine.runtime['activities'][execution['activity_id']]['result_ref'] = activity_ref
        engine._save({activity_ref: activity_result})
        other_workspace = self.root / 'activity-result-review'
        other = engine._context(review, other_workspace)['recovery_materials']
        self.assertEqual((other_workspace / other['result_source']['local_path']).read_bytes(), activity_result)
        self.assertNotEqual(other['result_source']['local_path'], other['checkpoint_source']['local_path'])

    def test_recovery_captures_parent_and_inline_child_without_losing_action(self):
        engine, _ = self.make()
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        for eid, parent in [('EX-parent', None), ('EX-inline', 'EX-parent')]:
            engine.runtime['executions'][eid] = {'id': eid, 'role': 'research_preparation' if parent is None else 'operational_review',
                'status': 'running', 'activity_id': 'AY-'+eid, 'action': action if parent is None else {'id':'AC-inline','role':'operational_review'},
                'parent_execution_id': parent}
            engine.runtime['activities']['AY-'+eid] = {'id':'AY-'+eid,'role':'research_preparation','execution_ids':[eid],'status':'active'}
            folder = Path(engine.instance['workspace'])/'runs'/eid/'workspace'; folder.mkdir(parents=True)
            (folder/'partial.txt').write_text(eid)
        engine.runtime.update(active_execution='EX-parent', status='running', queue=[action])
        engine._save(); engine.run(max_steps=1)
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertIsNone(engine.runtime['active_execution'])
        self.assertEqual([a['id'] for a in engine.runtime['queue']], ['AC-fixture'])
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
        engine, _ = self.make()
        folder = self.root/'observed'; folder.mkdir()
        clock = [0]
        tracker = ObservationTracker('EX', folder, {'observation_idle_seconds':999,'max_observation_reviews':5}, clock=lambda:clock[0])
        rules = [{'id':'steps','op':'iteration_gte','threshold':2,'repeat_interval':2}]
        (folder/'observation-rules.json').write_text(json.dumps(rules))
        checkpoint = {'current_claim':'partial','evidence_paths':[],'attempts':[], 'remaining_work':[],
                      'next_step':'iterate','progress_state':'working','iteration':2}
        (folder/'checkpoint.json').write_text(json.dumps(checkpoint))
        first = tracker.observe({'type':'tick'})
        self.assertEqual(first[-1]['rule_basis']['boundary'], 2)
        self.assertFalse(tracker.observe({'type':'tick'}))
        (folder/'observation-rules.json').write_text('{')
        checkpoint['iteration'] = 4
        (folder/'checkpoint.json').write_text(json.dumps(checkpoint))
        self.assertEqual(tracker.observe({'type':'tick'})[-1]['rule_basis']['boundary'], 4)
        self.assertEqual(tracker.rules, rules)
        with self.assertRaises(ValueError): validate_rules([{'id':'bad','op':'active_duration_gte','threshold':True}])


if __name__ == '__main__': unittest.main()
