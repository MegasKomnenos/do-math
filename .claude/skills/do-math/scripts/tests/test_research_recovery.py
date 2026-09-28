"""Recovery of research work: contract replacement, retries, diagnoses, operational dispositions and repairs.

Git-backed tests use temporary repositories; the rest run on in-memory engines."""
import hashlib
import json
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, contracts, execution_profiles, operational_dispositions, repair_execution
from do_math.configuration import DEFAULT_CONFIG
from do_math.engine import control, ResearchEngine
from do_math.repository import ResearchRepository
from engine_fixtures import context_engine, initial_failure_engine, package, routing_engine, start_repair_host
from purpose_fixtures import ActivatedPurposeHarness, candidate, common, formal_fixture, PurposeRunner
from record_fixtures import surface_state
from research_fixtures import (await_stop, bare_engine, charter_change, disposition, local_job_runner,
                               producer_result, restore_template, send_control)
from state_fixtures import active_instance


def empty_plan(**changes):
    return {**common('Compare the current task population.'), 'dispositions': [], 'preparation_requests': [], 'goal_audit': False,
            'task_assessments': [], **changes}


def purpose_engine(root, instance_id):
    return ResearchEngine(root / 'repository', instance_id, runner=PurposeRunner(), formal_verifier=formal_fixture)


def reviewed_task(root, shared, *, config):
    """``restore_template`` build: one task from a real preparation, ready after a real
    contract review, with the plan it opened queued. Returns the instance ID."""
    instance_id = active_instance(root, shared, config=config)
    engine = purpose_engine(root, instance_id)
    for _ in range(45):
        engine.run(max_steps=1)
        if (any(row['state'] == 'ready' for row in engine._task_readiness.values())
                and any(a['role'] == 'research_plan' for a in engine.runtime['queue'])):
            return instance_id
        if engine.runtime['status'] in {'paused', 'closed', 'waiting'}:
            break
    raise AssertionError('No reviewed task and plan: ' + json.dumps({
        'status': engine.runtime['status'], 'queue': engine.runtime['queue']}))


def parked_failed_plan(root, shared, *, config):
    """``restore_template`` build: a plan whose invalid output was rejected and parked.

    A public ``configure`` sets ``max_output_repairs`` to 0; the plan's execution
    ends ``execution_incomplete`` and ``AC-failed`` waits in ``waiting_actions``.
    Returns the instance ID and that execution (``failed``).
    """
    instance_id = active_instance(root, shared, config=config)
    engine = purpose_engine(root, instance_id)
    send_control(engine, 'configure', config={'max_output_repairs': 0})
    class InvalidPlan:
        @local_job_runner
        def run(inner, **arguments):
            arguments['on_started']({'fixture': 'rejected planner'})
            return producer_result({'status': 'completed', 'output': empty_plan(
                dispositions=[disposition('TK-completed')]), 'usage': {}}, arguments)
    engine.runner = InvalidPlan()
    engine.runtime['queue'] = [{'id': 'AC-failed', 'role': 'research_plan'}]
    engine._save()
    engine.run(max_steps=1)
    failed = next(e for e in engine.runtime['executions'].values() if e['action'].get('id') == 'AC-failed')
    if failed['outcome'] != 'execution_incomplete' or 'AC-failed' not in engine.runtime['waiting_actions']:
        raise AssertionError('The invalid plan was not parked: ' + json.dumps(failed))
    return {'instance_id': instance_id, 'failed': failed}


def paused_limited_recovery(root, shared, *, config):
    """``restore_template`` build: a user pause and an approved limited recovery of ``AC-limited``.

    Both the pause and the recovery decision go through public controls; the
    decision expires five minutes after the build. Returns the instance ID.
    """
    from datetime import datetime, timedelta, timezone
    instance_id = active_instance(root, shared, config=config)
    engine = purpose_engine(root, instance_id)
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
    return instance_id


class RecoveryStorageConnectionTests(unittest.TestCase):
    def test_operational_retry_producer_survives_actual_git_storage(self):
        from state_fixtures import active_repository
        from do_math.file_io import now
        from do_math.execution_lifecycle import transition_execution
        _, self.repo, self.identifier = active_repository()
        engine = ResearchEngine(self.repo, self.identifier)
        action = {'id': 'AC-rejected', 'role': 'research_plan'}
        engine._action_lifecycle_gate(action)
        execution = engine._register_execution(action, {'id': 'EX-rejected', 'role': 'research_plan', 'status': 'starting'})
        transition_execution(execution, 'stopping', at=now())
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


class RecoveryHarness(ActivatedPurposeHarness):
    def reviewed(self):
        """A copy of ``reviewed_task`` (``max_output_repairs`` 0) with a new engine."""
        self.root, instance_id = restore_template(reviewed_task, config=self.fixture_config(max_output_repairs=0))
        return self._engine(instance_id, PurposeRunner())

    def failed_plan(self):
        """A copy of ``parked_failed_plan``: the engine and the failed plan execution."""
        self.root, value = restore_template(parked_failed_plan, config=self.fixture_config())
        engine, _ = self._engine(value['instance_id'], PurposeRunner())
        return engine, value['failed']

    def active(self, **config):
        return ActivatedPurposeHarness.make_active(self, **self.fixture_config(**config))


class ResearchRecoveryTests(RecoveryHarness):

    def test_revised_contract_replaces_obsolete_criteria_and_preserves_history(self):
        engine, _ = self.reviewed()
        old = deepcopy(next(iter(engine.runtime['tasks'].values())))
        self.assertTrue(old['reviews'])
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
        engine, _ = self.reviewed()
        engine._refresh_readiness()
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
        engine, _ = self.reviewed()
        tid = next(iter(engine.runtime['tasks']))
        engine.runtime['tasks'][tid]['status'] = 'completed'
        engine._refresh_readiness()
        context = engine._context({'role': 'research_plan'}, self.root / 'plan-input')
        self.assertEqual(context.get('ready_task_ids'), [])
        self.assertEqual(context['task_readiness'][tid]['state'], 'not_ready')

    def test_exhausted_output_repair_does_not_stop_unrelated_work(self):
        engine, _ = self.active(max_output_repairs=0)
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
        engine, failed = self.failed_plan()
        send_control(engine, 'pause', text='Pause after preserving the rejected output')
        engine._enqueue('research_preparation', reason='Independent continuation', requested_by='UC-fixture')
        engine._save()
        send_control(engine, 'resume', text='Continue other available work.')
        self.assertNotIn(failed['action']['id'], [a.get('id') for a in engine.runtime['queue']])
        self.assertIn(failed['action']['id'], engine.runtime['waiting_actions'])
        self.assertTrue(any(a['role'] == 'research_preparation' for a in engine.runtime['queue']))


class RecoveryRoutingTests(RecoveryHarness):
    def test_controls_with_identical_wall_time_preserve_acceptance_order(self):
        engine, _ = self.active()
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
        engine, _ = self.active()
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
        engine, _ = self.active()
        times = ['2026-09-16T01:00:01+00:00', '2026-09-16T01:00:00+00:00']
        with patch('do_math.engine.now', side_effect=times):
            control(self.repo, engine.instance['id'], 'pause', text='first')
            control(self.repo, engine.instance['id'], 'resume', text='second')
        self.assertEqual([row['action'] for row in engine._inbox()], ['pause', 'resume'])
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')

    def test_concurrent_controls_receive_distinct_durable_order(self):
        engine, _ = self.active()
        with ThreadPoolExecutor(max_workers=4) as pool:
            accepted = list(pool.map(lambda index: control(self.repo, engine.instance['id'],
                'pause', text=f'parallel {index}'), range(4)))
        identifiers = {row['request_id'] for row in accepted}
        pending = [row for row in engine._inbox() if row['id'] in identifiers]
        orders = sorted(int(row['accepted_order']) for row in pending)
        self.assertEqual(len(identifiers), 4)
        self.assertEqual(orders, list(range(orders[0], orders[0] + 4)))

    def test_preparation_cannot_replace_a_user_academic_requirement_contract(self):
        from purpose_fixtures import requirement
        engine, _ = self.active()
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
        engine, _ = self.active(max_output_repairs=0)
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

    def test_diagnosed_plan_retry_uses_fresh_input_and_preserves_failure_and_independent_work(self):
        engine, failed = self.failed_plan()
        preserved = deepcopy(failed)
        engine.runtime['queue'] = [{'id': 'AC-independent', 'role': 'research_preparation'}]
        self.diagnose(engine, failed)
        retries = [a for a in engine.runtime['queue'] if a.get('continuation_of') == failed['id']]
        self.assertEqual(len(retries), 1)
        action = retries[0]
        # The request and owning activity persist; its next execution is fresh.
        self.assertEqual(action['role'], 'research_plan')
        self.assertEqual(action['id'], failed['action']['id'])
        self.assertNotIn('repair', action)
        self.assertNotIn('repair_attempt', action)
        context = engine._context(action, self.root / 'fresh-plan')
        self.assertEqual(context['ready_task_ids'], [])
        self.assertEqual(context['previous_execution']['id'], failed['id'])
        self.assertEqual(context['previous_execution']['outcome'], 'execution_incomplete')
        self.assertEqual(context['snapshot'], engine.head)
        self.assertEqual(action['recovery']['execution_id'], failed['id'])
        self.assertIn('AC-independent', [a['id'] for a in engine.runtime['queue']])
        self.assertEqual(engine.runtime['executions'][failed['id']], preserved)
        self.assertFalse(engine.runtime['questions'])

    def test_successful_fresh_plan_resolves_parked_failure_without_deleting_history(self):
        engine, failed = self.failed_plan()
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
        engine, failed = self.failed_plan()
        engine.runtime['queue'] = [{'id': 'AC-other', 'role': 'research_preparation'}]
        self.diagnose(engine, failed, kind='repair')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual(engine.runtime['queue'][0]['id'], 'AC-other')

    def test_operator_resume_cannot_release_a_user_pause(self):
        engine, _ = self.active()
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
        # Only validated as an absolute path; no server runs.
        server = {'command': sys.executable, 'args': [str(Path(__file__).resolve().with_name('scholarly-fixture-server.py'))]}
        engine, _ = self.active(scholarly_enabled=True, scholarly_server=server)
        received = []
        class CapturingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                # A pinned profile alone supplies the runner's tools (ModelRunner.run
                # rejects a separate scholarly_server argument beside a profile).
                received.append((kwargs.get('scholarly_server'), kwargs['profile']['ai']['scholarly_server']))
                kwargs['on_started']({'fixture': True})
                return producer_result({'status': 'completed', 'output': {**common('No new candidate.'), 'candidates': []},
                        'usage': {}, 'error': None}, kwargs)
        engine.runner = CapturingRunner()
        engine.run(max_steps=1)
        self.assertEqual(received, [(None, engine.instance['config']['scholarly_server'])])
        self.assertEqual(engine.instance['config']['scholarly_server'], server)

    def test_rejected_history_keeps_original_output_out_of_inline_action(self):
        engine, failed = self.failed_plan()
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
        engine, _ = self.failed_plan()
        engine._save()
        failure = engine.status()['waiting_actions']['AC-failed']
        self.assertNotIn('previous_output', json.dumps(failure))
        self.assertIn(failure['execution_id'], engine.runtime['executions'])

    def test_operator_cannot_create_mathematical_or_external_controls(self):
        engine, _ = self.active()
        for action in ('decision', 'input', 'conversation', 'close', 'external', 'trust', 'knowledge'):
            with self.subTest(action=action), self.assertRaises(ValueError):
                control(self.repo, engine.instance['id'], action, origin='operator', text='operator request')


    def test_conditional_hold_release_preserves_a_different_user_pause(self):
        engine, _ = self.active()
        control(self.repo, engine.instance['id'], 'pause', text='A newer independent user pause.')
        control(self.repo, engine.instance['id'], 'resume', config={
            'expected_user_pause_reason': 'User requested scheduled operator HOLD old-hold'})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['user_pause']['reason'], 'A newer independent user pause.')

    def test_conditional_hold_release_handles_a_pause_still_in_the_inbox(self):
        engine, _ = self.active()
        reason = 'User requested scheduled operator HOLD pending-hold'
        control(self.repo, engine.instance['id'], 'pause', text=reason)
        control(self.repo, engine.instance['id'], 'resume', config={'expected_user_pause_reason': reason})
        engine.process_controls()
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertIsNone(engine.status()['user_pause'])

    def test_operator_respects_explicit_pause_on_conversation_loss(self):
        engine, _ = self.active()
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

class LimitedRecoveryCallTests(ActivatedPurposeHarness):
    def test_actual_ai_call_keeps_pause_and_honors_a_new_stop(self):
        for stop_again in (False, True):
            with self.subTest(stop_again=stop_again):
                self.root, instance_id = restore_template(paused_limited_recovery, config=self.fixture_config())
                engine, _ = self._engine(instance_id, PurposeRunner())
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
                            case.assertTrue(await_stop(arguments['should_stop']))
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


class InitialDiagnosisTests(unittest.TestCase):
    def test_exhausted_initial_repairs_have_a_reachable_diagnostic_owner(self):
        requests = []
        engine = bare_engine({'lifecycle':{'state':'initializing'}, 'config':{'max_output_repairs':1}},
            {'queue':[], 'waiting_actions':{}})
        engine._enqueue = create_autospec(engine._enqueue, side_effect=lambda *a, **kw: requests.append((a,kw)))
        action = {'id':'AC-original','role':'intent_interpretation','target':'UI-original','repair_attempt':1}
        engine.route_submission_return(action,{'retry_bundle_ids':[],'bundles':[],'issues':[]},'EX-bad',None)
        self.assertEqual(requests[0][0], ('maintenance','EX-bad'))
        self.assertTrue(requests[0][1]['initial_submission_diagnosis'])

    def test_diagnosis_and_bound_rules_fit_the_persisted_contract(self):
        import jsonschema
        from do_math.record_schemas import RECORDS
        action = {'id':'AC-diagnose','role':'maintenance','target':'EX-bad', 'initial_submission_diagnosis':True}
        jsonschema.Draft202012Validator(RECORDS['queue']).validate(action)
        retry = {'id':'AC-original','role':'intent_interpretation','diagnosis_attempt':1}
        jsonschema.Draft202012Validator(RECORDS['queue']).validate(retry)
        self.assertIn('observation_rules', RECORDS['executions']['properties'])

    def test_diagnosis_retry_preserves_the_original_and_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            engine, action, wait = initial_failure_engine(Path(directory), 'output_validation')
            engine._save = create_autospec(engine._save)
            diagnostic = {'target': 'EX-bad', 'initial_submission_diagnosis': True}
            engine.apply_initial_diagnosis(diagnostic,
                {'initial_submission_diagnosis':{'decision':'retry','guidance':'Return the missing required field'}}, 'EX-diagnosis')
            self.assertEqual(engine.runtime['queue'], [])
            engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
            engine.continue_initial_retries()
            self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
            retry = engine.runtime['queue'].pop()
            self.assertEqual(retry['target'], 'UI-original')
            self.assertEqual(retry['owner_activity_id'], 'AY-original')
            self.assertEqual(retry['diagnosis_attempt'], 1)
            engine.route_submission_return(retry,{'retry_bundle_ids':[],'bundles':[],'issues':[]},'EX-again',None)
            self.assertEqual(engine.runtime['queue'], [])


class RetryEffectTests(unittest.TestCase):
    def test_retry_waits_for_unknown_effect_from_an_ancestor(self):
        engine = routing_engine()
        engine.runtime['executions'] = {
            'EX-original': {'id': 'EX-original', 'status': 'ended', 'action': {}},
            'EX-later': {'id': 'EX-later', 'status': 'ended', 'continuation_of': 'EX-original', 'action': {}}}
        engine.runtime['external_operations'] = {'EO-one': {
            'status': 'unknown', 'producer_executions': ['EX-original']}}
        record = {'id': 'OD', 'execution_id': 'EX-review', 'target_execution_id': 'EX-later',
                  'disposition': {'kind': 'retry'}}
        with self.assertRaisesRegex(ValueError, 'reconciliation'):
            engine._complete_operational_disposition(record)
        self.assertEqual(engine.runtime['queue'], [])


class RecoveryOwnershipTests(unittest.TestCase):
    def runtime(self, status='running', *, successor=True):
        target={'id':'EX-old','status':'ended','owner_activity_id':'AY-one',
                'action':{'id':'AC-one','role':'research_plan'},'error':'returned'}
        runtime={'executions':{'EX-old':target},'activities':{},'queue':[],'operational_dispositions':{}}
        if successor:
            runtime['executions']['EX-new']={'id':'EX-new','status':status,'owner_activity_id':'AY-one',
                'continuation_of':'EX-old','action':{'id':'AC-one','role':'research_plan'}}
        return runtime

    def record(self, kind='retry'):
        return {'id':'OD-one','status':'applied','target_execution_id':'EX-old',
                'disposition':{'kind':kind}}

    def test_live_and_ended_successors_supersede_old_retry_and_resume(self):
        for kind in ('retry','resume'):
            for status in ('starting','running','ended'):
                with self.subTest(kind=kind,status=status):
                    runtime=self.runtime(status)
                    record=self.record(kind)
                    self.assertTrue(operational_dispositions.reconcile_recovery(runtime,record))
                    self.assertEqual(record['status'],'superseded')
                    self.assertEqual(runtime['queue'],[])
                    self.assertEqual(runtime['executions']['EX-old']['error'],'returned')

    def test_unrelated_success_cannot_supersede_failure(self):
        runtime=self.runtime('ended')
        runtime['executions']['EX-new']['owner_activity_id']='AY-other'
        self.assertIsNone(activities.successor_state(runtime,'EX-old'))
        self.assertFalse(operational_dispositions.reconcile_recovery(runtime,self.record()))

    def test_queued_continuation_already_owns_recovery(self):
        runtime=self.runtime(successor=False)
        runtime['queue']=[{'id':'AC-one','continuation_of':'EX-old','owner_activity_id':'AY-one'}]
        before=deepcopy(runtime)
        self.assertTrue(operational_dispositions.reconcile_recovery(runtime,self.record()))
        self.assertEqual(runtime,before)

    def test_task_continuation_does_not_discharge_a_separate_installation_defect(self):
        runtime=self.runtime()
        runtime['executions']['EX-other']={'id':'EX-other','status':'ended','owner_activity_id':'AY-other'}
        old={**self.record('repair'),'status':'installation_repair_pending'}
        current={**old,'id':'OD-other','target_execution_id':'EX-other'}
        runtime['operational_dispositions']={old['id']:old,current['id']:current}
        self.assertEqual(repair_execution.pending_installation_repair(runtime),old)
        self.assertFalse(operational_dispositions.reconcile_recovery(runtime,old))

    def test_successful_installation_repair_preserves_the_existing_continuation(self):
        runtime=self.runtime()
        record={**self.record('repair'),'status':'installation_repair_pending'}
        result=repair_execution.resume_installation_repair(runtime,record,repaired_by='EX-repair',at='2026-09-25T00:00:00Z')
        self.assertIsNone(result)
        self.assertEqual(runtime['queue'],[])
        self.assertEqual(record['status'],'applied')
        self.assertEqual(record['result']['installation_repair']['successor']['live_execution_ids'],['EX-new'])

    def test_already_applied_retry_keeps_its_receipt(self):
        record={**self.record(),'result':{'continuation_action_id':'AC-one'}}
        self.assertFalse(operational_dispositions.reconcile_recovery(self.runtime(),record))
        self.assertEqual(record['status'],'applied')


AT = '2026-09-22T00:00:00+00:00'


class RecoveryBoundaryTests(unittest.TestCase):
    def test_restart_finishes_an_accepted_retry_after_target_termination_once(self):
        start_repair_host(self)
        host = self.host
        target = host.runtime['executions']['EX-target']
        target.pop('input_bundle')
        target['pending_operational_disposition'] = 'OD-repair'
        record = host.runtime['operational_dispositions']['OD-repair']
        record.update(status='awaiting_termination', disposition={'kind': 'retry', 'reason': 'Restart after ended target',
            'scope': 'Same unfinished activity', 'replay_safety': 'No external effects',
            'basis_refs': ['EX-target'], 'next_owner': 'engine'})
        host.runtime['status'] = 'paused'
        host._save()  # Reloaded state models interruption after the target ended.
        host._complete_operational_disposition = lambda row: ResearchEngine._complete_operational_disposition(host, row)
        ResearchEngine._run_pending_operational_repairs(host)
        self.assertEqual(host.runtime['queue'], [])
        host.runtime['status'] = 'ready'; host._save()
        ResearchEngine._run_pending_operational_repairs(host)
        ResearchEngine._run_pending_operational_repairs(host)
        _, _, saved = host.store.load()
        self.assertEqual(len(saved['queue']), 1)
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertNotIn('pending_operational_disposition', saved['executions']['EX-target'])

    def test_initial_diagnosis_receives_the_original_role_contract_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            engine, action, wait = initial_failure_engine(root)
            adopted, _ = surface_state()
            engine.instance.update({key: adopted[key] for key in ('governance', 'governance_sources')})
            engine.runtime['executions']['EX-bad']['input_bundle'] = 'BA-original'
            prefix = 'runtime/artifacts/BA-original'
            originals = {prefix + '/input.txt': b'Original role contract and fixed prompt',
                prefix + '/schema.json': b'{"type":"object"}',
                prefix + '/input/submission/context.json': b'{"fixed":"original input"}'}
            # The role input manifest names the archived prompt.
            prompt = originals[prefix + '/input.txt']
            engine.runtime['executions']['EX-bad']['input_manifest'] = {'prompt': {
                'artifact_ref': prefix + '/input.txt', 'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}}
            engine.store.read.side_effect = lambda ref, head: originals[ref]
            engine.store.read_many.side_effect = lambda refs, head: {ref: originals[ref] for ref in refs}
            engine._documents = {'maintenance': contracts.prompt_documents('maintenance')}
            engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint, side_effect=lambda: None)
            engine._session_slots = create_autospec(engine._session_slots)
            engine._academic_status = create_autospec(engine._academic_status, side_effect=lambda: {})
            workspace = root / 'diagnosis'
            context = engine._context({'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad',
                                       'initial_submission_diagnosis': True}, workspace)
            materials = context['initial_submission_diagnosis']['materials']
            self.assertEqual({row['artifact_ref'] for row in materials}, set(originals))
            for row in materials:
                raw = (workspace / row['local_path']).read_bytes()
                self.assertEqual(raw, originals[row['artifact_ref']])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])

    def test_initial_diagnosis_receives_the_failed_checkpoint_evidence_files(self):
        # 계약/유지보수.md 42 and 공통-실행.md 49: the diagnosis reads the checkpoint and its evidence.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            engine, action, wait = initial_failure_engine(root)
            adopted, _ = surface_state()
            engine.instance.update({key: adopted[key] for key in ('governance', 'governance_sources')})
            evidence = b'partial interpretation notes'
            reference = 'runtime/artifacts/BA-checkpoint/evidence/notes.txt'
            engine.runtime.setdefault('checkpoints', {})['EX-bad'] = {'kind': 'worker_checkpoint',
                'checkpoint': {'current_claim': 'partial'}, 'evidence_files': [{'path': 'notes.txt',
                'artifact_ref': reference, 'sha256': hashlib.sha256(evidence).hexdigest(), 'bytes': len(evidence)}]}
            engine.store.read.side_effect = lambda ref, head: {reference: evidence}[ref]
            engine._documents = {'maintenance': contracts.prompt_documents('maintenance')}
            engine._preparation_checkpoint = create_autospec(engine._preparation_checkpoint, side_effect=lambda: None)
            engine._session_slots = create_autospec(engine._session_slots)
            engine._academic_status = create_autospec(engine._academic_status, side_effect=lambda: {})
            workspace = root / 'diagnosis'
            context = engine._context({'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad',
                                       'initial_submission_diagnosis': True}, workspace)
            row = next(row for row in context['initial_submission_diagnosis']['materials'] if row['artifact_ref'] == reference)
            self.assertEqual((workspace / row['local_path']).read_bytes(), evidence)

    def test_retry_queue_and_disposition_publish_together_and_replay_is_noop(self):
        start_repair_host(self)
        host = self.host
        target = host.runtime['executions']['EX-target']
        target.pop('input_bundle')  # This case isolates queue/CAS publication.
        record = host.runtime['operational_dispositions']['OD-repair']
        record.update(status='pending', disposition={'kind': 'retry', 'reason': 'Use fresh input',
            'scope': 'Same unfinished activity', 'replay_safety': 'No external effects',
            'basis_refs': ['EX-target'], 'next_owner': 'engine'})
        host._save()
        before = host.head
        record = host.runtime['operational_dispositions']['OD-repair']
        ResearchEngine._complete_operational_disposition(host, record)
        self.assertEqual(host.store.load()[2]['queue'], [])
        host._save()
        after, _, saved = host.store.load()
        self.assertNotEqual(after, before)
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertEqual(saved['operational_dispositions']['OD-repair']['result']['continuation_action_id'], saved['queue'][0]['id'])
        ResearchEngine._complete_operational_disposition(host, host.runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(len(host.runtime['queue']), 1)
        self.assertEqual(self.destination.read_bytes(), b'damaged')

    def test_initial_failure_kinds_and_stages_reach_one_authorized_followup(self):
        for kind in ('output_validation', 'execution_failure', 'submission_failure'):
            for stage in ('interpret', 'check'):
                with self.subTest(kind=kind, stage=stage), tempfile.TemporaryDirectory() as directory:
                    engine, action, wait = initial_failure_engine(Path(directory), kind, stage)
                    original = deepcopy(engine.instance['lifecycle']['immutable_input'])
                    engine.route_failed_action(action, 'EX-bad', reason='Diagnose actual failure')
                    diagnostic = engine.runtime['queue'].pop()
                    self.assertEqual(diagnostic['role'], 'maintenance')
                    engine._action_lifecycle_gate(diagnostic)
                    engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                        'status': 'running', 'action': diagnostic}
                    engine.apply_initial_diagnosis(diagnostic,
                        {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': 'Use the preserved contract'}}, 'EX-diagnosis')
                    self.assertEqual(engine.runtime['queue'], [], 'candidate application cannot publish a native recovery')
                    engine._save = create_autospec(engine._save)
                    engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                        'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
                    engine.continue_initial_retries()
                    self.assertTrue(engine.runtime['queue'], engine.runtime['waiting_actions'])
                    retry = engine.runtime['queue'].pop()
                    self.assertEqual(retry['stage'], stage)
                    self.assertEqual(retry['owner_activity_id'], 'AY-original')
                    self.assertEqual(retry['continuation_of'], 'EX-bad')
                    self.assertEqual(retry['diagnosis_attempt'], 1)
                    self.assertEqual(engine.instance['lifecycle']['immutable_input'], original)
                    if kind == 'output_validation':
                        self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-pending'])
                    engine.route_submission_return(retry,
                        {'retry_bundle_ids': [], 'bundles': [], 'issues': []}, 'EX-again', None)
                    self.assertEqual(engine.runtime['queue'], [])

    def test_failed_diagnosed_retry_is_recorded_once_and_remains_storable(self):
        from do_math.record_schemas import RUNTIME_FIELDS
        from jsonschema import Draft202012Validator
        with tempfile.TemporaryDirectory() as directory:
            engine, action, wait = initial_failure_engine(Path(directory))
            diagnostic = {'id': 'AC-diagnosis', 'role': 'maintenance', 'target': 'EX-bad', 'initial_submission_diagnosis': True}
            engine.apply_initial_diagnosis(diagnostic,
                {'initial_submission_diagnosis': {'decision': 'retry', 'guidance': 'Retry original input'}}, 'EX-diagnosis')
            engine.runtime['executions']['EX-diagnosis'] = {'id': 'EX-diagnosis', 'role': 'maintenance',
                'status': 'ended', 'outcome': 'output_accepted', 'action': diagnostic}
            engine.instance['grants']['GR-init']['status'] = 'revoked'
            engine._save = create_autospec(engine._save)
            engine.continue_initial_retries()
            engine.continue_initial_retries()
            self.assertIn('retry_error', wait['diagnosis'])
            self.assertEqual(engine.runtime['queue'], [])
            engine._save.assert_called_once()
            Draft202012Validator(RUNTIME_FIELDS['waiting_actions']).validate(engine.runtime['waiting_actions'])

    def test_initial_diagnosis_does_not_bypass_termination_source_or_authority(self):
        for changed in ('termination', 'source', 'grant'):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as directory:
                engine, action, wait = initial_failure_engine(Path(directory))
                if changed == 'termination':
                    engine.runtime['executions']['EX-bad']['capacity']['local_termination'] = 'unknown'
                elif changed == 'source':
                    engine.runtime['inputs'][0]['text'] = 'changed'
                else:
                    engine.instance['grants']['GR-init']['status'] = 'revoked'
                with self.assertRaises(ValueError):
                    engine._continue_initial_execution(wait, request_id='EX-diagnosis',
                        diagnosis={'decision': 'retry', 'guidance': 'Retry'})
                self.assertEqual(engine.runtime['queue'], [])


    def test_retry_keeps_pending_bundles_and_never_restores_old_input(self):
        from do_math import activities, execution_lifecycle, execution_profiles
        engine = context_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, fixed = package(engine, root, 'research_work')
            artifacts = engine._input_artifacts('BA-plan', contracts.schema_for('research_work'), fitted, root)
            engine.store.read.side_effect = lambda path, head: artifacts[path]
            profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'research_work')
            activities.open_activity(engine.runtime, activity_id='AY-work', activity_kind='research_work',
                                    owner_ref='engine', input_refs=[], opened_at=AT)
            target = execution_lifecycle.create_execution(execution_id='EX-work', owner_activity_id='AY-work',
                actor_kind='ai', input_manifest=fitted['manifest'], profile_ref=execution_profiles.profile_ref(profile), created_at=AT)
            target.update(role='research_work', input_bundle='BA-plan', action={'id': 'AC-work',
                'role': 'research_work', 'owner_activity_id': 'AY-work'})
            activities.assign_execution(engine.runtime, 'AY-work', target)
            execution_lifecycle.transition_execution(target, 'starting', at=AT)
            execution_lifecycle.transition_execution(target, 'stopping', at=AT)
            execution_lifecycle.transition_execution(target, 'ended', at=AT, outcome='execution_incomplete')
            activities.wait_for(engine.runtime, 'AY-work', reason='returned', condition={'action_ids': ['AC-work']},
                                next_owner='operations', at=AT)
            engine.runtime['waiting_actions']['AC-work'] = {'execution_id': 'EX-work',
                'action': {**target['action'], 'repair': {'execution_id': 'EX-work', 'retry_bundle_ids': ['IN-left'],
                    'previous_output': {}, 'bundle_results': [], 'issues': []}}}
            record = {'id': 'OD-retry', 'target_execution_id': 'EX-work', 'status': 'pending',
                'disposition': {'kind': 'retry', 'reason': 'Fresh input copy', 'scope': 'Remaining bundles',
                    'replay_safety': 'Applied bundles stay recorded', 'next_owner': 'engine', 'basis_refs': ['EX-work']}}
            engine.runtime['operational_dispositions'] = {record['id']: record}
            damaged = root / 'input/submission/context.json'; damaged.write_bytes(b'damaged')
            engine._complete_operational_disposition(record)
            engine._complete_operational_disposition(record)
            self.assertEqual(damaged.read_bytes(), b'damaged')
            self.assertEqual(len(engine.runtime['queue']), 1)
            retry = engine.runtime['queue'][0]
            self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-left'])
            self.assertEqual(record['result']['continuation_action_id'], retry['id'])
            self.assertNotIn('AC-work', engine.runtime['waiting_actions'])
            fresh = root / 'next'
            context = engine._context(retry, fresh, execution_id='EX-next')
            self.assertEqual(context['previous_execution']['id'], 'EX-work')
            self.assertTrue((fresh / 'input/implementation/SKILL.md').is_file())
            self.assertEqual(damaged.read_bytes(), b'damaged')


class ExecutionConnections(unittest.TestCase):
    def test_retry_retains_activity_with_explicit_parent_and_profile(self):
        engine = routing_engine()
        engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
        engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
        engine._select_model = create_autospec(engine._select_model, return_value={"model": DEFAULT_CONFIG["tier_models"]["medium"]})
        action = {"id": "AC-work", "role": "research_work", "lineage_id": "AC-work"}
        first = engine._register_execution(action, {"id": "EX-first", "role": "research_work",
            "status": "starting", "created_at": "2026-09-20T00:00:00+00:00", "input_manifest": []})
        first["status"] = "ended"
        first["outcome"] = "execution_incomplete"
        retry_action = {**action, "continuation_of": first["id"]}
        second = engine._register_execution(retry_action, {"id": "EX-second", "role": "research_work",
            "status": "starting", "created_at": "2026-09-20T00:01:00+00:00", "input_manifest": []})
        self.assertEqual(first["owner_activity_id"], second["owner_activity_id"])
        self.assertEqual(second["continuation_of"], first["id"])
        self.assertEqual(first["execution_profile_ref"], second["execution_profile_ref"])
        self.assertEqual(len(engine.runtime["activities"]), 1)
        self.assertEqual(activities.validate_activities(engine.runtime), [])

    def test_missing_explicit_continuation_does_not_infer_from_same_target(self):
        engine = routing_engine()
        engine.instance["config"] = deepcopy(DEFAULT_CONFIG)
        engine.instance.update(execution_profiles.build_profiles(engine.instance["config"]))
        action = {"id": "AC-machine", "role": "formal_check", "target": "KN-one"}
        engine.runtime["executions"]["EX-unrelated"] = {"id": "EX-unrelated", "role": "formal_check",
            "status": "ended", "action": {"target": "KN-one"}, "owner_activity_id": "AY-unrelated"}
        row = engine._register_execution(action, {"id": "EX-new", "role": "formal_check", "status": "running",
            "created_at": "2026-09-20T00:00:00+00:00", "input_manifest": []})
        self.assertIsNone(row["continuation_of"])
        self.assertNotEqual(row["owner_activity_id"], "AY-unrelated")
        self.assertNotIn("model", row)


class FinalBoundaryConnections(unittest.TestCase):
    def test_operational_completion_and_transfer_use_real_task_domain_validation(self):
        from record_fixtures import transfer_assessment, apply_assessment
        from do_math import planning
        instance, runtime, assessment = transfer_assessment()
        assessment["decision"] = "closed"
        for obligation in runtime["tasks"]["TK-1"]["completion_obligations"]:
            obligation["judges"] = ["operational_review"]
        instance["decisions"]["DC-1"]["change"]["contract_sha256"] = planning.contract_hash(runtime["tasks"]["TK-1"])
        runtime["executions"].pop("EX-plan")
        runtime["executions"].update({"EX-work": {"id": "EX-work", "role": "research_work", "status": "ended", "action": {"target": "TK-1"}},
            "EX-review": {"id": "EX-review", "role": "operational_review", "input_snapshot": "input", "output": {"task_assessments": [assessment]}}})
        engine = routing_engine(); engine.instance, engine.runtime = instance, runtime
        engine.store = create_autospec(ResearchRepository, instance=True); engine.store.view.return_value = ("input", deepcopy(instance), deepcopy(runtime))
        engine._evaluation_context = create_autospec(engine._evaluation_context, return_value={})
        record = {"id": "OD-one", "execution_id": "EX-review", "target_execution_id": "EX-work",
            "disposition": {"kind": "task_disposition", "task_id": "TK-1", "task_state": "closed"}}
        engine.runtime["operational_dispositions"] = {record["id"]: record}
        before = deepcopy((engine.instance, engine.runtime))
        engine.instance["decisions"]["DC-1"]["source_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "current"):
            engine._complete_operational_disposition(record)
        self.assertNotEqual(engine.runtime["tasks"]["TK-1"]["status"], "closed")
        engine.instance, engine.runtime = before
        engine._complete_operational_disposition(engine.runtime["operational_dispositions"]["OD-one"])
        self.assertEqual(engine.runtime["tasks"]["TK-1"]["status"], "closed")
        self.assertEqual(engine.runtime["tasks"]["TK-2"]["completion_obligations"][-1]["id"], "OB-inherited")
        self.assertEqual(engine.runtime["tasks"]["TK-2"]["reviews"], [])

    def test_paused_initialization_reads_original_input_but_active_corruption_fails(self):
        engine = routing_engine()
        engine.instance.update(governance={}, lifecycle={"state": "paused", "input_id": "UC-one", "immutable_input": {"ref": "UC-one"}})
        engine.runtime.update(resume_lifecycle="initializing", inputs=[{"id": "UC-one", "config": {"goal": "Original goal"}}])
        self.assertEqual(engine._governance()["goal"], "Original goal")
        self.assertEqual(engine._governance()["status"], "unadopted_input")
        engine.instance["governance"] = {"GD-policy": {"kind": "policy", "status": "active"}}
        self.assertEqual(engine._governance()["goal"], "Original goal")
        engine.instance["lifecycle"]["state"] = "active"
        with self.assertRaisesRegex(ValueError, "charter"):
            engine._governance()

    def test_operational_task_disposition_uses_authoritative_item_assessment(self):
        engine = routing_engine()
        assessment = {"task_id": "TK-one", "decision": "completed", "reason": "All obligations assessed", "item_dispositions": [], "unresolved": []}
        engine.runtime["tasks"]["TK-one"] = {"id": "TK-one", "status": "active"}
        engine.runtime["executions"] = {"EX-work": {"id": "EX-work", "status": "ended", "action": {"target": "TK-one"}},
            "EX-review": {"input_snapshot": "input", "output": {"task_assessments": [assessment]}}}
        engine.store = create_autospec(ResearchRepository, instance=True); engine.store.view.return_value = ("input", {}, {"tasks": {"TK-one": {"id": "TK-one"}}})
        engine._evaluation_context = create_autospec(engine._evaluation_context, return_value={"snapshot": "current"})
        record = {"id": "OD-one", "execution_id": "EX-review", "target_execution_id": "EX-work", "disposition": {"kind": "task_disposition", "task_id": "TK-one", "task_state": "completed"}}
        completed = deepcopy(engine.runtime); completed["tasks"]["TK-one"]["status"] = "completed"
        with patch("do_math.engine.task_scope.apply_task_assessments", return_value=(engine.instance, completed)) as apply:
            engine._complete_operational_disposition(record)
        self.assertEqual(apply.call_args.args[2], [assessment])
        self.assertEqual(apply.call_args.kwargs["execution_id"], "EX-review")
        self.assertEqual(apply.call_args.kwargs["evaluation_context"], {"snapshot": "current"})
        self.assertEqual(engine.runtime["tasks"]["TK-one"]["status"], "completed")


class OperationalRepairCandidateTests(unittest.TestCase):
    def test_operational_repair_candidate_never_mutates_files_or_publishes(self):
        engine = routing_engine(); engine._save = create_autospec(engine._save)
        engine.runtime["executions"] = {"EX-target": {"id": "EX-target", "status": "ended"}}
        proposal = {"kind": "repair", "basis_refs": ["EX-target"], "next_owner": "engine", "reason": "Restore input",
                    "repair_target": "input/catalog/task.json", "meaning_preserving": True, "verification": "sha256:" + "a" * 64}
        with patch.object(type(engine), "complete_repair") as effect:
            # The disposition schema admits only installation: repair targets.
            with self.assertRaisesRegex(ValueError, 'repair/repair_target'):
                engine._apply_operational_disposition({"target": "EX-target"}, proposal, "EX-review")
            effect.assert_not_called()
        engine._save.assert_not_called()
        self.assertFalse(engine.runtime.get('operational_dispositions'))
        self.assertEqual(engine.runtime["queue"], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
