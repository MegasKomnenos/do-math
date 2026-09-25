"""Completion preserves unexecuted obligations without claiming their success."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import activities, retention
from do_math.engine import ResearchEngine
from test_categories import test_group


@test_group('unit')
class CompletionSettlementTests(unittest.TestCase):
    def engine(self):
        engine = object.__new__(ResearchEngine)
        engine.instance = {'id': 'RI-test', 'knowledge': {}}
        engine.runtime = {'status': 'completed', 'queue': [], 'waiting_actions': {},
                          'activities': {}, 'executions': {}, 'tasks': {},
                          'questions': [], 'history': []}
        for aid in ('AC-input', 'AC-review', 'AC-producer'):
            activities.open_activity(engine.runtime, activity_id=aid, activity_kind='research',
                owner_ref='RI-test', input_refs=[], opened_at='2026-09-24T00:00:00+00:00')
        return engine

    def test_completion_records_input_and_held_submission_before_finishing_activities(self):
        engine = self.engine()
        incoming = {'id': 'A-input', 'role': 'intent_interpretation', 'target': 'UI-late',
                    'owner_activity_id': 'AC-input'}
        review = {'id': 'A-review', 'role': 'maintenance', 'stage': 'impact_review',
                  'target': 'EX-producer', 'owner_activity_id': 'AC-review'}
        held = {'action': {'id': 'A-producer', 'role': 'research_work',
                          'owner_activity_id': 'AC-producer'}, 'kind': 'impact_review',
                'execution_id': 'EX-producer', 'review_requests': {'IB-one': {'payload_sha256': 'sealed'}}}
        engine.runtime['queue'] = [incoming, review]
        engine.runtime['waiting_actions']['A-producer'] = deepcopy(held)
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(engine.runtime['waiting_actions'], {})
        events = engine.runtime['history']
        self.assertEqual({row['action']['id'] for row in events}, {'A-input', 'A-review', 'A-producer'})
        self.assertEqual(next(row['waiting'] for row in events if row['action']['id'] == 'A-producer'), held)
        self.assertTrue(any('UI-late' in question for question in engine.runtime['questions']))
        for activity in engine.runtime['activities'].values():
            self.assertEqual(activity['status'], 'finished')
            self.assertTrue(activity['unresolved'])
            self.assertEqual(activity['followups'][-1]['next_owner'], 'user')
        before = deepcopy(engine.runtime)
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime, before)

    def test_live_activity_finishes_only_after_its_attempt_and_keeps_undispatched_work(self):
        engine = self.engine()
        activity = engine.runtime['activities']['AC-input']
        activity.update(status='working', assigned_execution_ids=['EX-live'])
        execution = {'id': 'EX-live', 'owner_activity_id': activity['id'],
                     'status': 'running', 'outcome': None, 'action': {}}
        engine.runtime['executions']['EX-live'] = execution
        engine.runtime['queue'] = [{'id': 'A-later', 'role': 'research_work',
                                    'owner_activity_id': activity['id']}]
        engine._settle_goal_completion()
        self.assertEqual(activity['status'], 'working')
        execution.update(status='ended', outcome='output_accepted')
        engine._settle_review_resource_dispositions = lambda: None
        engine._settle_activity('EX-live')
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][-1]['action_id'], 'A-later')
        self.assertEqual(activity['followups'][-1]['next_owner'], 'user')

    def test_academic_completion_uses_the_same_settlement(self):
        engine = self.engine()
        engine._solution_basis = lambda: {'records': []}
        engine._academic_status = lambda: {'status': 'not_applicable'}
        engine.runtime['queue'] = [{'id': 'A-input', 'role': 'intent_interpretation',
                                    'target': 'UI-late', 'owner_activity_id': 'AC-input'}]
        with patch('do_math.academic.current_requirements', return_value={'sha256': 'current', 'items': []}):
            engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['activities']['AC-input']['status'], 'finished')
        self.assertEqual(engine.runtime['history'][0]['action']['id'], 'A-input')

    def test_delayed_publication_settles_each_role_and_preserves_pending_followups(self):
        from unittest.mock import Mock
        for role in ('maintenance', 'identity_review', 'research_work', 'goal_audit'):
            for followup in (False, True):
                with self.subTest(role=role, followup=followup):
                    engine = self.engine()
                    engine.instance['workspace'] = 'unused'
                    engine.runtime['status'] = 'ready'
                    action = {'id': 'A-publication', 'role': role,
                              'owner_activity_id': 'AC-producer'}
                    execution = {'id': 'EX-publication', 'role': role, 'action': action,
                        'owner_activity_id': 'AC-producer', 'status': 'stopping',
                        'input_bundle': 'BA-input', 'result_ref': 'runtime/artifacts/BA-result/result.json'}
                    engine.runtime['executions'][execution['id']] = execution
                    engine.runtime['activities']['AC-producer'].update(
                        status='working', assigned_execution_ids=[execution['id']])
                    engine.runtime['waiting_actions'][action['id']] = {
                        'kind': 'submission_publication', 'action': action,
                        'execution_id': execution['id']}
                    engine.head = 'snapshot'
                    engine.store = Mock()
                    engine.store.read.return_value = b'{}'
                    engine._save = Mock()
                    engine._settle_review_resource_dispositions = lambda: None
                    def receive(*args, **kwargs):
                        engine.runtime = deepcopy(engine.runtime)
                        engine.runtime['executions']['EX-publication'].update(
                            status='ended', outcome='output_accepted')
                        del engine.runtime['waiting_actions']['A-publication']
                        if followup:
                            engine.runtime['queue'].append({'id': 'A-next', 'role': role,
                                'owner_activity_id': 'AC-producer'})
                    engine._receive_submission = Mock(side_effect=receive)
                    engine._retry_submission_publications()
                    activity = engine.runtime['activities']['AC-producer']
                    self.assertEqual(activity['status'], 'working' if followup else 'finished')
                    self.assertEqual(activity['result_refs'], [execution['result_ref']])
                    self.assertEqual(activity['unresolved'], [])
                    engine._receive_submission.assert_called_once()
                    engine._save.assert_called_once()


@test_group('unit')
class CleanupInterruptionTests(unittest.TestCase):
    def test_later_exact_deletion_resolves_an_interrupted_attempt(self):
        runtime = {'history': []}
        retention.record_cleanup_interruption(runtime, ['EX-one'], 'EX-maint', 'inaccessible', history_start=0)
        self.assertEqual(retention.pending_cleanup_failures(runtime)[0]['path'], 'runs/EX-one')
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-next',
            'result': {'deleted': ['runs/other'], 'failures': []}})
        self.assertEqual(len(retention.pending_cleanup_failures(runtime)), 1)
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-next',
            'result': {'deleted': ['runs/EX-one'], 'failures': []}})
        self.assertEqual(retention.pending_cleanup_failures(runtime), [])

    def test_failed_final_save_does_not_reopen_already_deleted_paths(self):
        runtime = {'history': [{'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint',
            'result': {'deleted': ['runs/EX-one'], 'failures': []}}]}
        retention.record_cleanup_interruption(runtime, ['EX-one', 'EX-two'], 'EX-maint',
                                             'save interrupted', history_start=0)
        self.assertEqual([row['path'] for row in retention.pending_cleanup_failures(runtime)], ['runs/EX-two'])
        self.assertEqual(runtime['history'][-1]['completed_paths'], ['runs/EX-one'])


if __name__ == '__main__':
    unittest.main()
