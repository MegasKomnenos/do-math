"""Regressions for contract replacement and recovery, using temporary Git stores."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_fixtures import local_job_runner
from do_math.engine import DEFAULT_CONFIG, control
from research_fixtures import charter_change, policy_change, producer_result, disposition, send_control
from test_purpose_engine import PurposeHarness, candidate, common


def empty_plan(**changes):
    return {**common('Compare the current task population.'), 'dispositions': [], 'preparation_requests': [], 'goal_audit': False,
            'task_assessments': [], **changes}


class RecoveryStorageConnectionTests(unittest.TestCase):
    def test_operational_retry_producer_survives_actual_git_storage(self):
        import test_input_recovery as seeds
        from do_math.engine import ResearchEngine, now
        from do_math.execution_lifecycle import transition_execution
        seeds.InputRecoveryPublicTests.setUp(self)
        engine = ResearchEngine(self.repo, self.identifier)
        action = {'id': 'AC-rejected', 'role': 'research_plan'}
        engine._action_lifecycle_gate(action)
        execution = engine._register_execution(action, {'id': 'EX-rejected', 'role': 'research_plan', 'status': 'starting'})
        transition_execution(execution, 'stopping', at=now(), stop_phase='terminating')
        transition_execution(execution, 'ended', at=now(), outcome='start_failed', reason='Explicit fixture failed before any process')
        # This test supplies only the already-decided operational verdict;
        # the actual retry producer and typed Git save/reload are under test.
        verdict = {'id': 'OD-fixture', 'target_execution_id': execution['id'],
            'disposition': {'kind': 'retry', 'reason': 'Retry from current input after a pre-start failure'}}
        engine._complete_operational_disposition(verdict)
        engine._save()
        restored = ResearchEngine(self.repo, self.identifier)
        retry = next(row for row in restored.runtime['queue'] if row.get('continuation_of') == execution['id'])
        self.assertEqual(retry['recovery']['execution_id'], execution['id'])
        self.assertEqual(retry['recovery']['disposition_id'], verdict['id'])
        self.assertEqual(restored.runtime['executions'][execution['id']]['outcome'], 'start_failed')


class ResearchRecoveryTests(PurposeHarness):

    def test_revised_contract_replaces_obsolete_criteria_and_preserves_history(self):
        from test_purpose_engine import ActiveStateHarness, PurposeRunner
        engine, _ = ActiveStateHarness.make(self, **self.fixture_config())
        self.drive(engine, predicate=lambda e: any(t.get('reviews') for t in e.runtime['tasks'].values()))
        old = deepcopy(next(iter(engine.runtime['tasks'].values())))
        proposal = candidate('A', revises=old['id'])
        proposal['completion_obligations'][0]['claim'] = 'Report the base construction and each property separately.'
        proposal['scope'] = {'included': ['The base construction'], 'excluded': ['Variants']}
        class RevisionRunner(PurposeRunner):
            def answer(inner, role, context, workspace):
                if role == 'research_preparation':
                    return {**common('Replace the exploratory scope after contract review.'),
                            'candidates': [deepcopy(proposal)]}
                return super().answer(role, context, workspace)
        engine.runner = RevisionRunner()
        engine.runtime['queue'] = []
        engine._enqueue('research_preparation', old['id'], id='AC-revision')
        engine._save()
        engine.run(max_steps=1)
        revised_execution = next(ex for ex in engine.runtime['executions'].values()
                                 if ex.get('action', {}).get('id') == 'AC-revision')
        self.assertEqual(revised_execution['outcome'], 'output_accepted', {
            'error': revised_execution.get('error'),
            'integration_result': revised_execution.get('integration_result'),
            'waiting_actions': engine.runtime['waiting_actions']})
        current = engine.runtime['tasks'][old['id']]
        self.assertEqual(current['completion_obligations'], proposal['completion_obligations'])
        self.assertEqual(current['revision_history'][-1]['completion_obligations'], old['completion_obligations'])
        self.assertEqual(current['reviews'], [])
        self.assertEqual(current['revision'], old['revision'] + 1)
        self.assertEqual(current['status'], 'planned')
        self.assertEqual(engine._governance()['goal_revision'], 1)

    def test_plan_rejection_names_missing_unexpected_and_duplicate_ids(self):
        from test_purpose_engine import ActiveStateHarness
        engine, _ = ActiveStateHarness.make(self, **self.fixture_config(max_output_repairs=0))
        self.drive(engine, predicate=lambda e: any(row['state'] == 'ready' for row in e._task_readiness.values())
                   and any(a['role'] == 'research_plan' for a in e.runtime['queue']))
        ready_id = next(tid for tid, row in engine._task_readiness.items() if row['state'] == 'ready')
        engine.runtime['queue'] = [next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')]
        class InvalidPlan:
            @local_job_runner
            def run(inner, **arguments):
                arguments['on_started']({'fixture': 'invalid population'})
                return producer_result({'status': 'completed', 'output': empty_plan(
                    dispositions=[disposition('TK-absent'),
                                  {**disposition('TK-absent'), 'reason': 'A distinct row with the same invalid task ID'}]), 'usage': {}}, arguments)
        engine.runner = InvalidPlan()
        engine._save()
        engine.run(max_steps=1)
        message = json.dumps(engine.runtime['waiting_actions'])
        for expected in ('missing', ready_id, 'unexpected', 'TK-absent', 'duplicate'):
            self.assertIn(expected, message)

    def test_plan_input_always_has_authoritative_ready_ids(self):
        from test_purpose_engine import ActiveStateHarness
        engine, _ = ActiveStateHarness.make(self, **self.fixture_config())
        engine.run(max_steps=2)
        tid = next(iter(engine.runtime['tasks']))
        engine.runtime['tasks'][tid]['status'] = 'completed'
        engine._refresh_readiness()
        context = engine._context({'role': 'research_plan'}, self.root / 'plan-input')
        self.assertEqual(context.get('ready_task_ids'), [])
        self.assertEqual(context['task_readiness'][tid]['state'], 'not_ready')

    def test_exhausted_output_repair_does_not_stop_unrelated_work(self):
        from test_purpose_engine import ActiveStateHarness
        engine, _ = ActiveStateHarness.make(self, **self.fixture_config(max_output_repairs=0))
        class InvalidPlan:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                # An invalid final response must reach the receiver; the valid
                # producer helper would raise before returning this response.
                return {'status': 'completed', 'output': empty_plan(dispositions=[disposition('TK-absent')]),
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
        from test_purpose_engine import ActiveStateHarness
        engine, _ = ActiveStateHarness.make(self, **self.fixture_config())
        failed = RecoveryRoutingTests.failed_plan(self, engine)
        send_control(engine, 'pause', text='Pause after preserving the rejected output')
        engine._enqueue('research_preparation', reason='Independent continuation', requested_by='UC-fixture')
        engine._save()
        send_control(engine, 'resume', text='Continue other available work.')
        self.assertNotIn(failed['action']['id'], [a.get('id') for a in engine.runtime['queue']])
        self.assertIn(failed['action']['id'], engine.runtime['waiting_actions'])
        self.assertTrue(any(a['role'] == 'research_preparation' for a in engine.runtime['queue']))


class RecoveryRoutingTests(PurposeHarness):
    def make_active(self, **config):
        from test_purpose_engine import ActiveStateHarness
        return ActiveStateHarness.make(self, **self.fixture_config(**config))

    def test_controls_with_identical_wall_time_preserve_acceptance_order(self):
        engine, _ = self.make_active()
        ids = ['UC-01M2KWMGGK0000000000000002', 'UC-01M2KWMGGK0000000000000001']
        with patch('do_math.engine.new_id', side_effect=ids), patch('do_math.engine.now', return_value='2026-09-16T01:00:00+00:00'):
            control(self.repo, engine.instance['id'], 'conversation', config={
                'operation': 'attach', 'id': 'C-user', 'generation': 1, 'disconnect_policy': 'pause', 'lease_seconds': 60})
            control(self.repo, engine.instance['id'], 'conversation', config={
                'operation': 'detach', 'id': 'C-user', 'generation': 1})
        self.assertEqual([row['config']['operation'] for row in engine._inbox()], ['attach', 'detach'])
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')

    def test_control_processing_uses_acceptance_time_not_random_id_order(self):
        engine, _ = self.make_active()
        ids = ['UC-01M2KWMGGK0000000000000002', 'UC-01M2KWMGGK0000000000000001']
        times = ['2026-09-16T01:00:00.000001+00:00', '2026-09-16T01:00:00.000002+00:00']
        with patch('do_math.engine.new_id', side_effect=ids), patch('do_math.engine.now', side_effect=times):
            control(self.repo, engine.instance['id'], 'pause', text='first')
            control(self.repo, engine.instance['id'], 'resume', text='second')
        pending = engine._inbox()
        self.assertEqual([row['action'] for row in pending], ['pause', 'resume'])
        self.assertEqual(int(pending[1]['accepted_order']) - int(pending[0]['accepted_order']), 1)
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')

    def test_controls_preserve_acceptance_order_when_wall_clock_moves_back(self):
        engine, _ = self.make_active()
        times = ['2026-09-16T01:00:01+00:00', '2026-09-16T01:00:00+00:00']
        with patch('do_math.engine.now', side_effect=times):
            control(self.repo, engine.instance['id'], 'pause', text='first')
            control(self.repo, engine.instance['id'], 'resume', text='second')
        self.assertEqual([row['action'] for row in engine._inbox()], ['pause', 'resume'])
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')

    def test_concurrent_controls_receive_distinct_durable_order(self):
        engine, _ = self.make_active()
        with ThreadPoolExecutor(max_workers=4) as pool:
            accepted = list(pool.map(lambda index: control(self.repo, engine.instance['id'],
                'pause', text=f'parallel {index}'), range(4)))
        identifiers = {row['request_id'] for row in accepted}
        pending = [row for row in engine._inbox() if row['id'] in identifiers]
        orders = sorted(int(row['accepted_order']) for row in pending)
        self.assertEqual(len(identifiers), 4)
        self.assertEqual(orders, list(range(orders[0], orders[0] + 4)))

    def test_preparation_cannot_replace_a_user_academic_requirement_contract(self):
        from test_academic_engine import requirement
        engine, _ = self.make_active()
        # This test concerns authoring authority; full proof construction has
        # separate end-to-end coverage. Keep this premise explicitly synthetic.
        self.enterContext(patch.object(engine, '_solution_basis', return_value={
            'goal_ref': 'synthetic-solution', 'records': []}))
        engine.instance['goal_status'] = 'mathematically_solved'
        engine._save()
        control(self.repo, engine.instance['id'], 'decision', config={'change': charter_change(engine, academic_requirements=[requirement(['Preserve the required account.'])])})
        engine.process_controls()
        engine._ensure_academic_followup()
        engine._save()
        task = next(t for t in engine.runtime['tasks'].values() if t.get('academic_requirement_id'))
        before = deepcopy(task)
        proposal = candidate('Replacement', revises=task['id'])
        engine.runtime['executions']['EX-replacement'] = {
            'id': 'EX-replacement', 'role': 'research_preparation', 'status': 'ended',
            'input_snapshot': engine.head, 'extensions': {}}
        with self.assertRaisesRegex(ValueError, 'academic'):
            engine._apply({'role': 'research_preparation'},
                          {**common('Replace criteria.'), 'candidates': [proposal]}, 'EX-replacement')
        self.assertEqual(engine.runtime['tasks'][task['id']], before)

    def failed_plan(self, engine):
        send_control(engine, 'configure', config={'max_output_repairs': 0})
        class InvalidPlan:
            @local_job_runner
            def run(inner, **arguments):
                arguments['on_started']({'fixture': 'rejected planner'})
                return producer_result({'status': 'completed', 'output': empty_plan(
                    dispositions=[disposition('TK-completed')]), 'usage': {}}, arguments)
        old_runner = engine.runner
        engine.runner = InvalidPlan()
        engine.runtime['queue'] = [{'id': 'AC-failed', 'role': 'research_plan'}]
        engine._save()
        engine.run(max_steps=1)
        engine.runner = old_runner
        failed = next(e for e in engine.runtime['executions'].values() if e['action'].get('id') == 'AC-failed')
        self.assertEqual(failed['outcome'], 'execution_incomplete')
        self.assertIn('AC-failed', engine.runtime['waiting_actions'])
        return failed

    def diagnose(self, engine, failed, kind='retry'):
        proposal = {'kind': kind, 'basis_refs': [failed['id']], 'next_owner': 'research_plan',
            'reason': 'Recompute the plan from the current task population.'}
        if kind == 'retry':
            proposal.update(scope='The rejected planning action', replay_safety='The rejected output was never applied')
        elif kind == 'repair':
            proposal.update(repair_target=failed['id'], meaning_preserving=True,
                verification='Validate the fresh output against the current input and role schema')
        class DiagnosisRunner:
            @local_job_runner
            def run(inner, **arguments):
                arguments['on_started']({'fixture': 'operational diagnosis'})
                return producer_result({'status': 'completed', 'output': {
                    **common('Preserved failed output requires an explicit recovery disposition'),
                    'disposition': proposal}, 'usage': {}}, arguments)
        previous = engine.runner
        engine.runner = DiagnosisRunner()
        engine.runtime['queue'].insert(0, {'id': 'AC-diagnose', 'role': 'operational_review', 'target': failed['id']})
        engine._save()
        engine.run(max_steps=1)
        engine.runner = previous

    def test_output_failure_opens_diagnosis_without_replaying_rejected_plan(self):
        engine, _ = self.make_active(max_output_repairs=0)
        class InvalidPlan:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                return producer_result({'status': 'completed', 'output': empty_plan(dispositions=[disposition('TK-absent')]),
                        'usage': {}, 'error': None}, kwargs)
        engine.runner = InvalidPlan()
        engine.runtime['queue'] = [{'id': 'AC-invalid', 'role': 'research_plan'}]
        engine._save()
        engine.run(max_steps=1)
        self.assertTrue(any(a['role'] == 'operational_review' for a in engine.runtime['queue']))
        self.assertFalse(any(a['id'] == 'AC-invalid' for a in engine.runtime['queue']))

    def test_diagnosed_plan_retry_uses_fresh_input_and_keeps_failure_evidence(self):
        engine, _ = self.make_active()
        failed = self.failed_plan(engine)
        engine.runtime['queue'] = []
        self.diagnose(engine, failed)
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        # The request and owning activity persist; its next execution is fresh.
        self.assertEqual(action['id'], failed['action']['id'])
        self.assertNotIn('repair', action)
        self.assertNotIn('repair_attempt', action)
        context = engine._context(action, self.root / 'fresh-plan')
        self.assertEqual(context['ready_task_ids'], [])
        self.assertEqual(context['previous_execution']['id'], failed['id'])
        self.assertEqual(context['previous_execution']['outcome'], 'execution_incomplete')
        self.assertEqual(context['snapshot'], engine.head)
        self.assertEqual(action['recovery']['execution_id'], failed['id'])
        self.assertEqual(action['continuation_of'], failed['id'])
        self.assertEqual(engine.runtime['executions'][failed['id']]['action'], failed['action'])

    def test_successful_fresh_plan_resolves_parked_failure_without_deleting_history(self):
        engine, _ = self.make_active()
        failed = self.failed_plan(engine)
        class ValidPlan:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                (kwargs['workspace'] / 'activity-extensions.json').write_text(json.dumps({'action_resolutions': [
                    {'action_id': 'AC-failed', 'evidence_execution_id': 'current', 'reason': 'This current complete plan explicitly supersedes the old population judgment.'}]}), encoding='utf-8')
                return producer_result({'status': 'completed', 'output': empty_plan(), 'usage': {}, 'error': None}, kwargs)
        engine.runner = ValidPlan()
        engine.runtime['queue'] = [{'id': 'AC-fresh', 'role': 'research_plan'}]
        engine._save()
        engine.run(max_steps=1)
        self.assertNotIn('AC-failed', engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['executions'][failed['id']]['outcome'], 'execution_incomplete')
        resolution = next(row for row in engine.runtime['history']
                          if row.get('kind') == 'failed_action_explicitly_resolved')
        activity = engine.runtime['activities'][failed['owner_activity_id']]
        self.assertEqual(activity['status'], 'finished')
        self.assertNotIn('waiting', activity)
        self.assertEqual(activity['unresolved'], [])
        self.assertIn(resolution['resolved_by'], activity['result_refs'])
        self.assertEqual(activity['followups'][0]['resolved_by'], resolution['resolved_by'])
        stored = engine.store.load()[2]['activities'][activity['id']]
        self.assertEqual(stored, activity)

    def test_diagnosis_wait_does_not_block_independent_actions(self):
        engine, _ = self.make_active()
        failed = self.failed_plan(engine)
        engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        self.diagnose(engine, failed, kind='repair')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual(engine.runtime['queue'][0]['id'], 'AC-other')

    def test_operator_resume_cannot_release_a_user_pause(self):
        engine, _ = self.make_active()
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
        engine, _ = self.make_active(scholarly_enabled=True, scholarly_server={'command': sys.executable,
                                               'args': [str(self.root / 'server.py')]})
        received = []
        class CapturingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                received.append(kwargs.get('scholarly_server'))
                kwargs['on_started']({'fixture': True})
                return producer_result({'status': 'completed', 'output': {**common('No new candidate.'), 'candidates': []},
                        'usage': {}, 'error': None}, kwargs)
        engine.runner = CapturingRunner()
        engine.run(max_steps=1)
        self.assertEqual(received, [engine.instance['config']['scholarly_server']])

    def test_rejected_history_keeps_original_output_out_of_inline_action(self):
        engine, _ = self.make_active()
        failed = self.failed_plan(engine)
        failed = engine.runtime['executions'][failed['id']]
        failed['action']['repair'] = {'execution_id': failed['id'],
            'previous_output': {'summary': 'Explicit rejected fixture output retained only as history'}}
        workspace = self.root / 'history-reader'
        workspace.mkdir()
        history = engine._planning_history('research_plan', workspace)
        row = next(item for item in history if item['execution_id'] == failed['id'])
        self.assertNotIn('previous_output', row['action'].get('repair', {}))
        source = row['action_source']
        original = json.loads((workspace / source['local_path']).read_text(encoding='utf-8'))
        self.assertEqual(original, failed['action'])

    def test_status_failure_summary_does_not_repeat_rejected_output(self):
        engine, _ = self.make_active()
        self.failed_plan(engine)
        engine._save()
        failure = engine.status()['waiting_actions']['AC-failed']
        self.assertNotIn('previous_output', json.dumps(failure))
        self.assertIn(failure['execution_id'], engine.runtime['executions'])

    def test_operator_cannot_create_mathematical_or_external_controls(self):
        engine, _ = self.make_active()
        for action in ('decision', 'input', 'conversation', 'close', 'external', 'trust', 'knowledge'):
            with self.subTest(action=action), self.assertRaises(ValueError):
                control(self.repo, engine.instance['id'], action, origin='operator', text='operator request')


    def test_conditional_hold_release_preserves_a_different_user_pause(self):
        engine, _ = self.make_active()
        control(self.repo, engine.instance['id'], 'pause', text='A newer independent user pause.')
        control(self.repo, engine.instance['id'], 'resume', config={
            'expected_user_pause_reason': 'User requested scheduled operator HOLD old-hold'})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['user_pause']['reason'], 'A newer independent user pause.')

    def test_conditional_hold_release_handles_a_pause_still_in_the_inbox(self):
        engine, _ = self.make_active()
        reason = 'User requested scheduled operator HOLD pending-hold'
        control(self.repo, engine.instance['id'], 'pause', text=reason)
        control(self.repo, engine.instance['id'], 'resume', config={'expected_user_pause_reason': reason})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertIsNone(engine.status()['user_pause'])

    def test_operator_respects_explicit_pause_on_conversation_loss(self):
        engine, _ = self.make_active()
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

    def test_retry_count_does_not_substitute_for_an_operational_disposition(self):
        engine, _ = self.make_active()
        failed = self.failed_plan(engine)
        failed['action']['recovery_attempt'] = 1
        preserved = deepcopy(failed)
        engine.runtime['queue'] = [{'id': 'AC-independent', 'role': 'research_preparation'}]
        self.diagnose(engine, failed)
        retries = [a for a in engine.runtime['queue'] if a.get('continuation_of') == failed['id']]
        self.assertEqual(len(retries), 1)
        self.assertIn('AC-independent', [a['id'] for a in engine.runtime['queue']])
        self.assertEqual(engine.runtime['executions'][failed['id']], preserved)
        self.assertFalse(engine.runtime['questions'])


class LimitedRecoveryCallTests(PurposeHarness):
    def test_actual_ai_call_keeps_pause_and_honors_a_new_stop(self):
        from datetime import datetime, timedelta, timezone
        from test_purpose_engine import ActiveStateHarness
        for stop_again in (False, True):
            with self.subTest(stop_again=stop_again):
                engine, _ = ActiveStateHarness.make(self, **self.fixture_config())
                engine.runtime['queue'] = []
                engine._enqueue('maintenance', engine.instance['id'], id='AC-limited',
                    reason='Inspect the preserved recovery state and report remaining work')
                engine._save()
                send_control(engine, 'pause', text='Keep general research paused')
                action = next(a for a in engine.runtime['queue'] if a['id'] == 'AC-limited')
                grant_id = engine.instance['lifecycle']['adoption']['research_grant_ids'][0]
                send_control(engine, 'decision', config={'change': {
                    'kind': 'limited_recovery', 'action_id': action['id'], 'grant_id': grant_id,
                    'profile_ref': engine._select_model(action)['profile_ref'],
                    'purpose': 'Inspect the preserved recovery state',
                    'procedure': 'Read the supplied state and return a maintenance report',
                    'expires_at': (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()}})
                calls = []
                case = self
                class Runner:
                    @local_job_runner
                    def run(inner, **arguments):
                        calls.append(arguments['execution_id'])
                        arguments['on_started']()
                        case.assertEqual(engine.runtime['status'], 'paused')
                        case.assertEqual(engine.instance['lifecycle']['state'], 'paused')
                        case.assertFalse(arguments['should_stop']())
                        if stop_again:
                            control(case.repo, engine.instance['id'], 'pause',
                                text='Stop the approved recovery too')
                            case.assertTrue(arguments['should_stop']())
                            return {'status': 'stopped', 'output': None, 'usage': {},
                                    'error': 'New user pause observed'}
                        return producer_result({'status': 'completed', 'usage': {}, 'output': {
                            **common('Limited recovery inspection complete'),
                            'report': 'Inspected only the supplied recovery state.',
                            'remaining_work': []}}, arguments)
                engine.runner = Runner()
                engine.run(max_steps=1)
                self.assertEqual(len(calls), 1)
                execution = engine.runtime['executions'][calls[0]]
                self.assertEqual(execution['outcome'], 'cancelled' if stop_again else 'output_accepted',
                                 execution.get('error'))
                self.assertEqual(engine.runtime['status'], 'paused')
                self.assertEqual(engine.instance['lifecycle']['state'], 'paused')
                self.assertIn('user_pause', engine.runtime)


if __name__ == '__main__':
    unittest.main(verbosity=2)
