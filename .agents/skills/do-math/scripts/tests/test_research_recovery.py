"""Regressions for contract replacement and recovery, using temporary Git stores."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import DEFAULT_CONFIG, control
from test_purpose_engine import PurposeHarness, candidate, common


def empty_plan(**changes):
    return {**common('Compare the current task population.'), 'selections': [],
            'deferred': [], 'preparation_requests': [], 'goal_audit': False,
            'task_assessments': [], **changes}


class ResearchRecoveryTests(PurposeHarness):
    memory = False

    def test_default_call_budgets_are_unlimited(self):
        self.assertIsNone(DEFAULT_CONFIG['work_calls'])
        self.assertIsNone(DEFAULT_CONFIG['operations_calls'])

    def test_revised_contract_replaces_obsolete_criteria_and_preserves_history(self):
        engine, _ = self.make()
        engine.run(max_steps=2)
        old = deepcopy(next(iter(engine.runtime['tasks'].values())))
        proposal = candidate('A', revises=old['id'])
        proposal['completion_criteria'] = ['Report the base construction and each property separately.']
        proposal['scope'] = 'The base construction only; variants are outside this task.'
        class RevisionRunner:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return {'status': 'completed', 'output':
                        {**common('Replace the exploratory scope after contract review.'),
                         'candidates': [proposal]}, 'usage': {}, 'error': None}
        engine.runner = RevisionRunner()
        engine.runtime['queue'] = [{'id': 'AC-revision', 'role': 'research_preparation'}]
        engine._save()
        engine.run(max_steps=1)
        current = engine.runtime['tasks'][old['id']]
        self.assertEqual(current['completion_criteria'], proposal['completion_criteria'])
        self.assertEqual(current['revision_history'][-1]['completion_criteria'], old['completion_criteria'])
        self.assertEqual(current['reviews'], [])
        self.assertEqual(current['revision'], old['revision'] + 1)
        self.assertEqual(current['status'], 'planned')
        self.assertEqual(engine.instance['goal_revision'], 1)

    def test_plan_rejection_names_missing_unexpected_and_duplicate_ids(self):
        engine, _ = self.make()
        engine.run(max_steps=2)
        ready_id = next(iter(engine.runtime['tasks']))
        with self.assertRaises(ValueError) as caught:
            engine._apply_plan(empty_plan(selections=['TK-absent', 'TK-absent']), 'EX-plan')
        message = str(caught.exception)
        self.assertIn('missing', message)
        self.assertIn(ready_id, message)
        self.assertIn('unexpected', message)
        self.assertIn('TK-absent', message)
        self.assertIn('duplicate', message)

    def test_plan_input_always_has_authoritative_ready_ids(self):
        engine, _ = self.make()
        engine.run(max_steps=2)
        tid = next(iter(engine.runtime['tasks']))
        engine.runtime['tasks'][tid]['status'] = 'completed'
        engine._refresh_readiness()
        context = engine._context({'role': 'research_plan'}, self.root / 'plan-input')
        self.assertEqual(context.get('ready_task_ids'), [])
        self.assertNotIn(tid, context['task_readiness'])

    def test_exhausted_output_repair_does_not_stop_unrelated_work(self):
        engine, _ = self.make(max_output_repairs=0)
        class InvalidPlan:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return {'status': 'completed', 'output': empty_plan(selections=['TK-absent']),
                        'usage': {}, 'error': None}
        engine.runner = InvalidPlan()
        engine.runtime['queue'] = [{'id': 'AC-bad-plan', 'role': 'research_plan'},
                                   {'id': 'AC-independent', 'role': 'research_preparation'}]
        engine._save()
        engine.run(max_steps=1)
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertTrue(any(a['id'] == 'AC-independent' for a in engine.runtime['queue']))
        self.assertIn('AC-bad-plan', engine.runtime['waiting_actions'])
        failure = engine.runtime['waiting_actions']['AC-bad-plan']
        self.assertEqual(failure.get('kind'), 'output_validation')
        self.assertTrue(failure.get('execution_id'))

    def test_resume_keeps_failed_output_out_of_execution_queue(self):
        engine, _ = self.make()
        failed = {'id': 'AC-rejected', 'role': 'research_plan', 'repair_attempt': 1,
                  'repair': {'execution_id': 'EX-rejected', 'error': 'wrong population',
                             'previous_output': empty_plan(selections=['TK-completed'])}}
        engine.runtime.update(status='paused', queue=[{'id': 'AC-other', 'role': 'research_preparation'}],
            waiting_actions={'AC-rejected': {'action': failed, 'kind': 'output_validation',
                                           'reason': 'wrong population', 'execution_id': 'EX-rejected'}})
        engine._save()
        control(self.repo, engine.instance['id'], 'resume', text='Continue other available work.')
        engine.process_controls()
        self.assertNotIn('AC-rejected', [a.get('id') for a in engine.runtime['queue']])
        self.assertIn('AC-rejected', engine.runtime['waiting_actions'])
        self.assertIn('AC-other', [a.get('id') for a in engine.runtime['queue']])


class RecoveryRoutingTests(PurposeHarness):
    def test_control_processing_uses_acceptance_time_not_random_id_order(self):
        engine, _ = self.make()
        ids = ['UC-01M2KWMGGK0000000000000002', 'UC-01M2KWMGGK0000000000000001']
        times = ['2026-09-16T01:00:00.000001+00:00', '2026-09-16T01:00:00.000002+00:00']
        with patch('do_math.engine.new_id', side_effect=ids), patch('do_math.engine.now', side_effect=times):
            control(self.repo, engine.instance['id'], 'pause', text='first')
            control(self.repo, engine.instance['id'], 'resume', text='second')
        self.assertEqual([row['action'] for row in engine._inbox()], ['pause', 'resume'])
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')

    def test_preparation_cannot_replace_a_user_academic_requirement_contract(self):
        from test_academic_engine import requirement
        engine, _ = self.make()
        control(self.repo, engine.instance['id'], 'decision', config={'change': {
            'kind': 'academic_requirements', 'requirements': [requirement(['Preserve the required account.'])]}})
        engine.process_controls()
        self.drive(engine, predicate=lambda e: e.instance['goal_status'] == 'mathematically_solved')
        task = next(t for t in engine.runtime['tasks'].values() if t.get('academic_requirement_id'))
        before = deepcopy(task)
        proposal = candidate('Replacement', revises=task['id'])
        engine.runtime['executions']['EX-replacement'] = {
            'id': 'EX-replacement', 'role': 'research_preparation', 'status': 'ended', 'extensions': {}}
        with self.assertRaisesRegex(ValueError, 'academic'):
            engine._apply({'role': 'research_preparation'},
                          {**common('Replace criteria.'), 'candidates': [proposal]}, 'EX-replacement')
        self.assertEqual(engine.runtime['tasks'][task['id']], before)

    def failed_plan(self, engine):
        action = {'id': 'AC-failed', 'role': 'research_plan', 'repair_attempt': 1,
                  'repair': {'execution_id': 'EX-earlier', 'error': 'unexpected completed task',
                             'previous_output': empty_plan(selections=['TK-completed'])}}
        failed = {'id': 'EX-failed', 'role': 'research_plan', 'status': 'ended',
                  'outcome': 'execution_incomplete', 'error': 'output validation: unexpected completed task',
                  'action': deepcopy(action)}
        engine.runtime['executions'][failed['id']] = failed
        engine.runtime['waiting_actions'] = {action['id']: {'action': action,
            'kind': 'output_validation', 'reason': failed['error'], 'execution_id': failed['id']}}
        return failed

    def test_output_failure_opens_diagnosis_without_replaying_rejected_plan(self):
        engine, _ = self.make(max_output_repairs=0)
        class InvalidPlan:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return {'status': 'completed', 'output': empty_plan(selections=['TK-absent']),
                        'usage': {}, 'error': None}
        engine.runner = InvalidPlan()
        engine.runtime['queue'] = [{'id': 'AC-invalid', 'role': 'research_plan'}]
        engine._save()
        engine.run(max_steps=1)
        self.assertTrue(any(a['role'] == 'operational_review' for a in engine.runtime['queue']))
        self.assertFalse(any(a['id'] == 'AC-invalid' for a in engine.runtime['queue']))

    def test_diagnosed_plan_retry_uses_fresh_input_and_keeps_failure_evidence(self):
        engine, _ = self.make()
        failed = self.failed_plan(engine)
        engine.runtime['queue'] = []
        engine._apply({'role': 'operational_review', 'target': failed['id']},
                      {**common('Diagnosed the wrong selection population.'), 'decision': 'retry',
                       'reason': 'Recompute selection from current ready_task_ids, which is empty.'}, 'EX-diagnosis')
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertNotEqual(action['id'], failed['action']['id'])
        self.assertNotIn('repair', action)
        self.assertNotIn('repair_attempt', action)
        context = engine._context(action, self.root / 'fresh-plan')
        self.assertEqual(context['ready_task_ids'], [])
        self.assertNotIn('previous_execution', context)
        self.assertEqual(action['failure_diagnosis']['execution_id'], failed['id'])
        self.assertEqual(engine.runtime['executions'][failed['id']]['action'], failed['action'])

    def test_successful_fresh_plan_resolves_parked_failure_without_deleting_history(self):
        engine, _ = self.make()
        failed = self.failed_plan(engine)
        class ValidPlan:
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return {'status': 'completed', 'output': empty_plan(), 'usage': {}, 'error': None}
        engine.runner = ValidPlan()
        engine.runtime['queue'] = [{'id': 'AC-fresh', 'role': 'research_plan'}]
        engine._save()
        engine.run(max_steps=1)
        self.assertNotIn('AC-failed', engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['executions'][failed['id']]['outcome'], 'execution_incomplete')
        self.assertTrue(any(row.get('kind') == 'failed_action_resolved' for row in engine.runtime['history']))

    def test_diagnosis_wait_does_not_block_independent_actions(self):
        engine, _ = self.make()
        failed = self.failed_plan(engine)
        engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        engine._apply({'role': 'operational_review', 'target': failed['id']},
                      {**common('This action needs its execution configuration repaired.'),
                       'decision': 'wait', 'reason': 'Missing tool configuration.'}, 'EX-diagnosis')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual(engine.runtime['queue'][0]['id'], 'AC-other')

    def test_operator_resume_cannot_release_a_user_pause(self):
        engine, _ = self.make()
        control(self.repo, engine.instance['id'], 'pause', text='Wait for my decision.')
        engine.process_controls()
        self.assertEqual(engine.status()['user_pause']['reason'], 'Wait for my decision.')
        control(self.repo, engine.instance['id'], 'resume', origin='operator', text='Automatic recovery.')
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')
        control(self.repo, engine.instance['id'], 'resume', origin='user')
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertIsNone(engine.status()['user_pause'])

    def test_scholarly_configuration_reaches_the_actual_runner_call(self):
        engine, _ = self.make(scholarly_server={'command': sys.executable,
                                               'args': [str(self.root / 'server.py')]})
        received = []
        class CapturingRunner:
            def run(inner, **kwargs):
                received.append(kwargs.get('scholarly_server'))
                kwargs['on_started']({'fixture': True})
                return {'status': 'completed', 'output': {**common('No new candidate.'), 'candidates': []},
                        'usage': {}, 'error': None}
        engine.runner = CapturingRunner()
        engine.run(max_steps=1)
        self.assertEqual(received, [engine.instance['config']['scholarly_server']])

    def test_rejected_history_keeps_original_output_out_of_inline_action(self):
        engine, _ = self.make()
        failed = self.failed_plan(engine)
        workspace = self.root / 'history-reader'
        workspace.mkdir()
        history = engine._planning_history('research_plan', workspace)
        row = next(item for item in history if item['execution_id'] == failed['id'])
        self.assertNotIn('previous_output', row['action'].get('repair', {}))
        source = row['action_source']
        original = json.loads((workspace / source['local_path']).read_text(encoding='utf-8'))
        self.assertEqual(original, failed['action'])

    def test_status_failure_summary_does_not_repeat_rejected_output(self):
        engine, _ = self.make()
        self.failed_plan(engine)
        engine._save()
        failure = engine.status()['waiting_actions']['AC-failed']
        self.assertNotIn('previous_output', json.dumps(failure))
        self.assertEqual(failure['execution_id'], 'EX-failed')

    def test_operator_cannot_create_mathematical_or_external_controls(self):
        engine, _ = self.make()
        for action in ('decision', 'input', 'conversation', 'close', 'external', 'trust', 'knowledge'):
            with self.subTest(action=action), self.assertRaises(ValueError):
                control(self.repo, engine.instance['id'], action, origin='operator', text='operator request')

    def test_operator_cannot_increase_a_user_call_limit(self):
        engine, _ = self.make(work_calls=4)
        with self.assertRaises(ValueError):
            control(self.repo, engine.instance['id'], 'configure', origin='operator',
                    config={'work_calls': None})

    def test_conditional_hold_release_preserves_a_different_user_pause(self):
        engine, _ = self.make()
        control(self.repo, engine.instance['id'], 'pause', text='A newer independent user pause.')
        control(self.repo, engine.instance['id'], 'resume', config={
            'expected_user_pause_reason': 'User requested scheduled operator HOLD old-hold'})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['user_pause']['reason'], 'A newer independent user pause.')

    def test_conditional_hold_release_handles_a_pause_still_in_the_inbox(self):
        engine, _ = self.make()
        reason = 'User requested scheduled operator HOLD pending-hold'
        control(self.repo, engine.instance['id'], 'pause', text=reason)
        control(self.repo, engine.instance['id'], 'resume', config={'expected_user_pause_reason': reason})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertIsNone(engine.status()['user_pause'])

    def test_operator_respects_explicit_pause_on_conversation_loss(self):
        engine, _ = self.make()
        control(self.repo, engine.instance['id'], 'conversation', config={
            'operation': 'attach', 'id': 'C-user', 'generation': 1,
            'disconnect_policy': 'pause', 'lease_seconds': 60})
        control(self.repo, engine.instance['id'], 'conversation', config={
            'operation': 'detach', 'id': 'C-user', 'generation': 1})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')
        control(self.repo, engine.instance['id'], 'resume', origin='operator')
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')

    def test_exhausted_diagnosed_retry_is_parked_without_stopping_other_work(self):
        engine, _ = self.make()
        failed = self.failed_plan(engine)
        failed['action']['recovery_attempt'] = 1
        engine.runtime['queue'] = [deepcopy(failed['action']),
                                   {'id': 'AC-independent', 'role': 'research_preparation'}]
        engine._apply({'role': 'operational_review', 'target': failed['id']},
                      {**common('Another diagnosis cannot repeat the same failed attempt.'),
                       'decision': 'retry', 'reason': 'Requested retry.'}, 'EX-diagnosis')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual([a['id'] for a in engine.runtime['queue']], ['AC-independent'])
        self.assertIn('AC-failed', engine.runtime['waiting_actions'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
