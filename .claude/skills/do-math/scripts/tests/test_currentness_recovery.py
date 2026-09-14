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
from test_purpose_engine import PurposeHarness, common


class CurrentnessTests(PurposeHarness):
    def test_same_source_is_idempotent_changed_source_reopens_completed_task(self):
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
        engine._save()
        source.write_text('new', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        self.assertNotEqual(engine.runtime['tasks'][task['id']]['status'], 'completed')
        self.assertFalse(engine.runtime['tasks'][task['id']]['assessment']['current'])
        self.assertEqual(engine.instance['sources'][0]['revision'], 2)

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
