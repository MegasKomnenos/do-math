from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.lifecycle_engine import LifecycleEngineMixin
from do_math.scheduler import SchedulerMixin
from do_math.planning import contract_hash
from do_math.knowledge import register_environment
from do_math.state_checks import state_errors


class FakeEngine(LifecycleEngineMixin, SchedulerMixin):
    def __init__(self, root):
        self.root = Path(root)
        self.current_time = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
        self.lifecycle_clock = lambda: self.current_time.isoformat()
        self.instance = {'id': 'I1', 'goal': 'Prove the target', 'goal_kind': 'mathematical',
            'goal_status': 'unresolved', 'policies': 'Read all evidence', 'workspace': str(root),
            'knowledge': {}, 'relations': [], 'goal_judgments': [], 'sources': [],
            'config': {'research_reconsider_seconds': 60, 'lean_timeout_seconds': 5, 'external_timeout_seconds': 2,
                       'session_limits': None}}
        self.runtime = {'status': 'ready', 'tasks': {}, 'executions': {}, 'activities': {}, 'queue': [], 'history': [], 'questions': []}
        self.head = 'snapshot-1'
        self.store = object()
        self.saves = []
        self.formal_calls = []
        self.formal_behavior = None
        self.formal_verifier = self.verify
        self._upgrade_runtime()

    def _enqueue(self, role, target=None, **extra):
        action = {'role': role, **extra}
        if target is not None: action['target'] = target
        if action not in self.runtime['queue']: self.runtime['queue'].append(action)

    def _start_identity_review(self, knowledge_id, previous_cycle_id=None):
        cycle_id = 'RC-' + str(len(self.runtime.setdefault('review_cycles', {})) + 1)
        self.runtime['review_cycles'][cycle_id] = {'id': cycle_id, 'knowledge_id': knowledge_id, 'status': 'working', 'previous_cycle_id': previous_cycle_id}
        self.instance['knowledge'][knowledge_id]['review_cycle_id'] = cycle_id
        self._enqueue('identity_review', knowledge_id, review_cycle_id=cycle_id, stage='initial', slot='initial-0', round=1)
        return cycle_id

    def _controls(self):
        pass

    def _save(self, artifacts=None):
        self.saves.append({'instance': deepcopy(self.instance), 'runtime': deepcopy(self.runtime), 'artifacts': artifacts})
        self.head = f'snapshot-{len(self.saves)+1}'

    def verify(self, **kwargs):
        self.formal_calls.append(kwargs)
        if self.formal_behavior: return self.formal_behavior(kwargs)
        environment = next(env for env in self.instance['trust_environments'].values()
            if env['toolchain'].get('executable') == kwargs['lean_command'][0])
        return {'status': 'verified', 'source_sha256': hashlib.sha256(kwargs['source'].encode()).hexdigest(),
                'declarations': kwargs['declarations'], 'axioms': {}, 'toolchain': deepcopy(environment['toolchain'])}

    def task(self, task_id='T1', *, approved=True, condition=None, inputs=None):
        task = {'id': task_id, 'feature_version': 2, 'revision': 1, 'status': 'planned',
            'title': task_id, 'objective': 'Do the required work', 'completion_criteria': ['Deliver evidence'],
            'inputs': inputs or [], 'reuse': [], 'dependencies': [], 'reviews': [],
            'occurrence_condition': condition or {'op': 'always'}}
        self.runtime['tasks'][task_id] = task
        if approved:
            task['reviews'].append({'id': 'CR-' + task_id, 'decision': 'approved', 'revision': 1,
                'contract_sha256': contract_hash(task), 'goal_revision': self.instance['goal_revision'],
                'policy_revision': self.instance['policy_revision']})
        return task

    def control(self, action, config, request_id=None):
        request_id = request_id or 'user-' + str(len(self.runtime['extended_controls']))
        return self._apply_extended_control({'id': request_id, 'action': action, 'config': config})

    def knowledge(self, kid, env_id=None, dependencies=None):
        source = f'theorem {kid.lower()} : 1 = 1 := rfl'
        item = {'id': kid, 'revision': 1, 'status': 'verified', 'statement': 'One equals one',
                'summary': 'Reflexivity', 'lean_code': source, 'declaration_names': [kid.lower()],
                'dependencies': dependencies or [], 'reviews': [],
                'formal': {'status': 'verified', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                           'trust_environment_id': env_id}}
        self.instance['knowledge'][kid] = item
        return item

    def environment(self, name, active=False):
        chain = {'executable': name, 'sha256': hashlib.sha256(name.encode()).hexdigest(), 'version': 'fixture-' + name}
        self.instance, env_id = register_environment(self.instance, chain, ['propext'])
        if active:
            self.instance['active_trust_environment'] = env_id
            self.instance['trust_environments'][env_id]['status'] = 'active'
        return env_id

    def machine(self, role):
        action = next(action for action in self.runtime['queue'] if action['role'] == role)
        self.assert_machine = self._process_machine_action(action)
        return action


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = FakeEngine(self.temp.name)

    def test_trust_check_pause_preserves_target_until_explicit_resume(self):
        engine = self.engine
        old_environment = engine.environment('old', active=True)
        new_environment = engine.environment('new')
        engine.knowledge('K1', old_environment)
        engine.control('trust', {'operation': 'transition', 'env_id': new_environment})
        transition_id = next(iter(engine.runtime['trust_transitions']))
        def pause_during_check(arguments):
            engine.runtime['status'] = 'paused'
            self.assertTrue(arguments['should_stop']())
            return {'status': 'stopped', 'reason': 'user pause'}
        engine.formal_behavior = pause_during_check
        engine.machine('trust_check')
        stopped_id = next(iter(engine.runtime['executions']))
        self.assertEqual(engine.runtime['executions'][stopped_id]['status'], 'ended')
        self.assertEqual(engine.runtime['executions'][stopped_id]['outcome'], 'stopped')
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.instance['active_trust_environment'], old_environment)
        self.assertNotIn('K1', engine.runtime['trust_transitions'][transition_id]['results'])
        self.assertTrue(any(a['role'] == 'trust_check' and a['target'] == 'K1' for a in engine.runtime['queue']))
        engine.formal_behavior = None
        engine.runtime['status'] = 'ready'  # Explicit resume, as performed by the host executor.
        engine.machine('trust_check')
        self.assertEqual(len(engine.runtime['executions']), 2)
        self.assertEqual(engine.runtime['executions'][stopped_id]['outcome'], 'stopped')
        self.assertEqual(engine.instance['active_trust_environment'], new_environment)

    def test_upgrade_is_idempotent_and_does_not_invent_toolchain(self):
        engine = self.engine
        engine.instance['knowledge']['legacy'] = {'formal': {'status': 'verified', 'toolchain': None}}
        before = deepcopy((engine.instance, engine.runtime))
        engine._upgrade_runtime()
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.runtime['feature_version'], 2)
        self.assertIsNone(engine.instance['active_trust_environment'])
        self.assertFalse(engine.instance['trust_environments'])
        self.assertFalse(engine.runtime['conversations'])

    def test_current_contract_review_is_queued_once_and_policy_change_reopens(self):
        engine = self.engine
        task = engine.task(approved=False)
        engine._refresh_readiness()
        engine._refresh_readiness()
        reviews = [a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review']
        self.assertEqual(len(reviews), 1)
        basis = reviews[0]['contract_basis']
        engine.runtime['tasks']['T1']['reviews'].append({'decision': 'approved', **basis})
        engine.runtime['queue'].remove(reviews[0])
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['tasks']['T1']['status'], 'ready')
        engine.control('decision', {'change': {'kind': 'policy', 'text': 'Updated evidence policy'}})
        reviews = [a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review']
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['contract_basis']['policy_revision'], 2)

    def test_rejected_current_contract_is_not_repeated_without_change(self):
        engine = self.engine
        task = engine.task(approved=False)
        engine._refresh_readiness()
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'task_contract_review')
        engine.runtime['tasks']['T1']['reviews'].append({'decision': 'rejected', **action['contract_basis']})
        engine.runtime['queue'].remove(action)
        engine._refresh_readiness()
        self.assertFalse(any(a['role'] == 'task_contract_review' for a in engine.runtime['queue']))
        self.assertEqual(engine.runtime['task_readiness']['T1']['state'], 'not_ready')

    def test_missing_inputs_and_bad_conditions_remain_distinct(self):
        engine = self.engine
        engine.task(inputs=['missing-source'])
        engine.task('T2', condition={'op': 'unsupported_condition'})
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['task_readiness']['T1']['state'], 'not_ready')
        self.assertEqual(engine.runtime['task_readiness']['T2']['state'], 'evaluation_error')
        engine.instance['available_input_refs'] = ['missing-source']
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['tasks']['T1']['status'], 'ready')
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        self.assertTrue(plan['event_refs'])

    def test_completed_task_does_not_retain_ready_projection(self):
        engine = self.engine
        engine.task()
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['task_readiness']['T1']['state'], 'ready')

        engine.runtime['tasks']['T1']['status'] = 'completed'
        engine._refresh_readiness()

        self.assertNotIn('T1', engine.runtime['task_readiness'])

    def test_paused_events_survive_and_opened_at_sets_the_next_tick(self):
        engine = self.engine
        engine.runtime['status'] = 'paused'
        engine.runtime['next_research_reconsider_at'] = engine.current_time.isoformat()
        task = engine.task()
        task['newinput'] = True
        engine._refresh_readiness()
        pending = list(engine.runtime['pending_events'])
        engine.current_time += timedelta(seconds=5)
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['pending_events'], pending)
        self.assertFalse(any(a['role'] == 'research_preparation' for a in engine.runtime['queue']))
        engine.runtime['status'] = 'ready'
        engine._refresh_readiness()
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
        opened_at = action['opened_at']
        next_at = engine.runtime['next_research_reconsider_at']
        self.assertEqual(datetime.fromisoformat(next_at), datetime.fromisoformat(opened_at) + timedelta(seconds=60))
        engine.current_time += timedelta(seconds=70)
        engine.runtime['activities']['A'] = {'id': 'A', 'role': 'research_preparation', 'status': 'active', 'opened_at': opened_at}
        engine._refresh_readiness()
        self.assertTrue(engine.runtime['pending_events'])
        self.assertEqual(engine.runtime['next_research_reconsider_at'], next_at)
        self.assertEqual(action['opened_at'], opened_at)

    def test_assignment_keeps_events_pending_on_failure_and_never_changes_live_input(self):
        engine = self.engine
        first = engine._lifecycle_event('user_input_available', source_ref='user-first')
        engine._refresh_readiness()
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        original = deepcopy(action)
        self.assertIn(first['id'], engine.runtime['pending_events'])
        event = next(e for e in engine.runtime['events'] if e['id'] == first['id'])
        self.assertEqual(event['assigned_to'], action['id'])
        self.assertNotIn('consumed_at', event)
        engine.runtime['executions']['E'] = {'id': 'E', 'status': 'running', 'role': 'research_plan', 'action': deepcopy(action)}
        second = engine._lifecycle_event('user_input_available', source_ref='user-second')
        engine._refresh_readiness()
        live = next(a for a in engine.runtime['queue'] if a.get('id') == original['id'])
        self.assertEqual(live, original)
        following = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan' and a.get('id') != original['id'])
        self.assertEqual(following['event_refs'], [second['id']])
        engine.runtime['executions']['E'].update(status='ended', outcome='execution_incomplete')
        engine._refresh_readiness()
        self.assertEqual(set(engine.runtime['pending_events']), {first['id'], second['id']})
        self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'research_plan']), 2)

    def test_knowledge_revision_and_invalidation_reset_dependent_goal(self):
        engine = self.engine
        engine.knowledge('K1')
        engine.knowledge('K2', dependencies=['K1'])
        engine.instance['goal_judgments'] = [{'id': 'G1', 'decision': 'satisfied', 'current': True, 'used_sources': ['K2']}]
        engine.instance['goal_status'] = 'mathematically_solved'
        engine.runtime['status'] = 'completed'
        engine.control('knowledge', {'operation': 'revise', 'id': 'K1', 'changes': {'statement': 'Corrected statement'}, 'reason': 'User corrected the claim'})
        self.assertEqual(engine.instance['knowledge']['K1']['revision'], 2)
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'candidate')
        self.assertTrue(engine.instance['knowledge']['K2']['use_suspended'])
        self.assertFalse(engine.instance['goal_judgments'][0]['current'])
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertTrue(any(a['role'] == 'formal_check' for a in engine.runtime['queue']))
        engine.control('knowledge', {'operation': 'invalidate', 'id': 'K1', 'reason': 'Withdrawal'})
        self.assertEqual(engine.instance['knowledge']['K1']['status'], 'withdrawn')
        self.assertFalse(any(a['role'] == 'formal_check' and a.get('target') == 'K1' for a in engine.runtime['queue']))

    def test_control_idempotence_and_atomic_rejection(self):
        engine = self.engine
        config = {'change': {'kind': 'goal', 'goal': 'A new exact goal'}}
        engine.control('decision', config, 'command-one')
        state = deepcopy((engine.instance, engine.runtime))
        engine.control('decision', config, 'command-one')
        self.assertEqual((engine.instance, engine.runtime), state)
        with self.assertRaises(ValueError):
            engine.control('decision', {'change': {'kind': 'goal', 'goal': 'Another goal'}}, 'command-one')
        self.assertEqual((engine.instance, engine.runtime), state)
        with self.assertRaises(ValueError):
            engine.control('conversation', {'operation': 'attach', 'id': 'C', 'generation': 1, 'lease_seconds': 5})
        self.assertEqual((engine.instance, engine.runtime), state)
        self.assertFalse(engine._apply_extended_control({'action': 'pause'}))

    def test_conversation_lease_only_follows_real_signals(self):
        engine = self.engine
        engine.control('conversation', {'operation': 'attach', 'id': 'C', 'generation': 1, 'disconnect_policy': 'pause', 'lease_seconds': 10})
        engine.runtime['executions']['E'] = {'id': 'E', 'role': 'research_work', 'status': 'running'}
        engine.current_time += timedelta(seconds=5)
        engine.control('conversation', {'operation': 'heartbeat', 'id': 'C', 'generation': 1})
        engine.current_time += timedelta(seconds=11)
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['stop_requested'], 'conversation_lost')
        self.assertEqual(engine.runtime['executions']['E']['stop_requested'], 'conversation_lost')
        with self.assertRaises(ValueError):
            engine.control('conversation', {'operation': 'heartbeat', 'id': 'C', 'generation': 1})
        engine.control('conversation', {'operation': 'attach', 'id': 'C', 'generation': 2, 'disconnect_policy': 'pause', 'lease_seconds': 10})
        self.assertEqual(engine.runtime['status'], 'paused')
        with self.assertRaises(ValueError):
            engine.control('conversation', {'operation': 'heartbeat', 'id': 'C', 'generation': 1})

    def test_continue_policy_records_loss_without_stopping(self):
        engine = self.engine
        engine.control('conversation', {'operation': 'attach', 'id': 'C', 'generation': 1, 'disconnect_policy': 'continue_authorized', 'lease_seconds': 2})
        engine.current_time += timedelta(seconds=3)
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual(engine.runtime['conversations']['C']['status'], 'lost')
        count = len([e for e in engine.runtime['events'] if e['kind'] == 'conversation_lost'])
        engine._refresh_readiness()
        self.assertEqual(len([e for e in engine.runtime['events'] if e['kind'] == 'conversation_lost']), count)

    def test_formal_binding_requires_actual_fingerprint_and_never_implicitly_transitions(self):
        engine = self.engine
        unknown = engine._bind_formal_environment({'status': 'verified', 'toolchain': None})
        self.assertEqual(unknown['trust_environment_status'], 'unknown')
        self.assertFalse(engine.instance['trust_environments'])
        first = engine._bind_formal_environment({'status': 'verified', 'toolchain': {'sha256': 'a' * 64, 'version': 'fixture-a', 'executable': 'lean-a'}})
        second = engine._bind_formal_environment({'status': 'verified', 'toolchain': {'sha256': 'b' * 64, 'version': 'fixture-b', 'executable': 'lean-b'}})
        self.assertEqual(first['trust_environment_status'], 'active')
        self.assertEqual(second['trust_environment_status'], 'registered')
        self.assertEqual(engine.instance['active_trust_environment'], first['trust_environment_id'])

    def prepare_transition(self):
        engine = self.engine
        old = engine.environment('lean-old', active=True)
        engine.knowledge('K1', old)
        engine.knowledge('K2', old)
        new = engine.environment('lean-new')
        engine.control('trust', {'operation': 'transition', 'env_id': new})
        transition_id = next(iter(engine.runtime['trust_transitions']))
        return old, new, transition_id

    def test_full_trust_transition_runs_every_source_and_preserves_formal_artifacts(self):
        old, new, transition_id = self.prepare_transition()
        engine = self.engine
        engine.machine('trust_check')
        self.assertEqual(engine.instance['active_trust_environment'], old)
        engine.machine('trust_check')
        self.assertEqual(engine.instance['active_trust_environment'], new)
        self.assertEqual(engine.runtime['trust_transitions'][transition_id]['status'], 'active')
        self.assertEqual(len(engine.formal_calls), 2)
        self.assertTrue(all(call['lean_command'] == ['lean-new'] and call['allowed_axioms'] == ('propext',) for call in engine.formal_calls))
        artifacts = [s['artifacts'] for s in engine.saves if s['artifacts']]
        self.assertEqual(len(artifacts), 2)
        self.assertTrue(all(item['formal']['trust_environment_id'] == new for item in engine.instance['knowledge'].values()))

    def test_partial_failed_or_changed_trust_basis_never_activates(self):
        old, new, transition_id = self.prepare_transition()
        engine = self.engine
        engine.machine('trust_check')
        engine.instance['knowledge']['K2']['summary'] = 'Changed after transition began'
        engine.machine('trust_check')
        self.assertEqual(engine.instance['active_trust_environment'], old)
        self.assertEqual(engine.runtime['trust_transitions'][transition_id]['status'], 'failed')
        self.assertEqual(len(engine.formal_calls), 1)
        self.assertTrue(any(e['kind'] == 'trust_transition_failed' for e in engine.runtime['events']))

    def test_wrong_compiler_fingerprint_is_not_transition_evidence(self):
        old, _, transition_id = self.prepare_transition()
        engine = self.engine
        engine.formal_behavior = lambda call: {'status': 'verified', 'source_sha256': hashlib.sha256(call['source'].encode()).hexdigest(),
            'toolchain': {'sha256': 'wrong', 'version': 'fixture-lean-new'}}
        engine.machine('trust_check')
        engine.machine('trust_check')
        self.assertEqual(engine.instance['active_trust_environment'], old)
        self.assertEqual(engine.runtime['trust_transitions'][transition_id]['status'], 'failed')

    def test_trust_signature_change_queues_full_review_and_preserves_other_suspension(self):
        engine = self.engine
        old = engine.environment('lean-old', active=True)
        engine.knowledge('K1', old)
        engine.instance['knowledge']['K1']['formal'].update(signature_hash='old', declaration_signatures={'k1': 'k1 : True'})
        engine.control('trust', {'operation': 'invalidate', 'env_id': old, 'reason': 'old invalid'})
        engine.instance['knowledge']['K1'].setdefault('use_suspensions', []).append({'kind': 'dependency', 'reason': 'independent dependency'})
        engine.instance['knowledge']['K1']['use_suspended'] = True
        new = engine.environment('lean-new')
        engine.control('trust', {'operation': 'transition', 'env_id': new})
        def changed(call):
            environment = next(env for env in engine.instance['trust_environments'].values() if env['toolchain'].get('executable') == call['lean_command'][0])
            return {'status': 'verified', 'source_sha256': hashlib.sha256(call['source'].encode()).hexdigest(),
                    'toolchain': deepcopy(environment['toolchain']), 'signature_hash': 'new', 'declaration_signatures': {'k1': 'k1 : Nat'}}
        engine.formal_behavior = changed
        engine.machine('trust_check')
        item = engine.instance['knowledge']['K1']
        self.assertTrue(item['use_suspended'])
        self.assertTrue(any(cause['kind'] == 'dependency' for cause in item['use_suspensions']))
        self.assertTrue(any(cause['kind'] == 'semantic' for cause in item['use_suspensions']))
        self.assertTrue(any(action['role'] == 'identity_review' and action['target'] == 'K1' for action in engine.runtime['queue']))

    def test_new_goal_approval_is_not_invalidated_by_historical_stale_audit(self):
        engine = self.engine
        engine.instance['goal_status'] = 'mathematically_solved'
        engine.runtime['status'] = 'completed'
        engine.instance['goal_judgments'] = [{'id': 'old', 'basis': 'old-basis', 'current': False},
                                              {'id': 'new', 'basis': 'new-basis', 'current': True}]
        engine._refresh_readiness()
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        self.assertEqual(engine.runtime['status'], 'completed')

    def test_trust_result_recovery_activates_without_repeating_compiler(self):
        old, new, transition_id = self.prepare_transition()
        engine = self.engine
        engine.machine('trust_check')
        last_action = next(a for a in engine.runtime['queue'] if a['role'] == 'trust_check')
        engine.machine('trust_check')
        # Reopen the persisted snapshot immediately after the last result was
        # sealed, before the subsequent activation publication.
        snapshot = next(s for s in reversed(engine.saves) if s['artifacts'])
        engine.instance, engine.runtime = deepcopy(snapshot['instance']), deepcopy(snapshot['runtime'])
        self.assertEqual(engine.instance['active_trust_environment'], old)
        self.assertEqual(engine.runtime['trust_transitions'][transition_id]['status'], 'ready')
        engine._process_machine_action(last_action)
        self.assertEqual(engine.instance['active_trust_environment'], new)
        self.assertEqual(len(engine.formal_calls), 2)

    def test_invalid_environment_recovers_only_after_explicit_complete_transition(self):
        engine = self.engine
        old = engine.environment('lean-old', active=True)
        engine.knowledge('K1', old)
        task = engine.task()
        task['dependencies'] = ['K1']
        task['reviews'][0]['contract_sha256'] = contract_hash(task)
        engine.instance['goal_judgments'] = [{'id': 'G1', 'basis': 'goal-v1', 'current': True, 'used_sources': ['K1']}]
        engine.instance['goal_assessment_basis'] = 'goal-v1'
        engine.instance['goal_status'] = 'mathematically_solved'
        engine.runtime['status'] = 'completed'
        engine.control('trust', {'operation': 'invalidate', 'env_id': old, 'reason': 'Compiler bug confirmed'})
        self.assertIsNone(engine.instance['active_trust_environment'])
        self.assertTrue(engine.instance['knowledge']['K1']['use_suspended'])
        self.assertEqual(engine.runtime['task_readiness']['T1']['state'], 'not_ready')
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        new = engine.environment('lean-fixed')
        engine.control('trust', {'operation': 'transition', 'env_id': new})
        transition = next(t for t in engine.runtime['trust_transitions'].values() if t['to_environment'] == new)
        self.assertIsNone(transition['from_environment'])
        self.assertEqual([target['id'] for target in transition['targets']], ['K1'])
        self.assertIsNone(engine.instance['active_trust_environment'])
        engine.machine('trust_check')
        self.assertEqual(engine.instance['active_trust_environment'], new)
        self.assertFalse(engine.instance['knowledge']['K1']['use_suspended'])
        self.assertEqual(engine.runtime['tasks']['T1']['status'], 'ready')
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        self.assertFalse(engine.instance['goal_judgments'][0]['current'])

    def test_active_review_is_closed_before_explicit_knowledge_revision(self):
        engine = self.engine
        item = engine.knowledge('K1')
        item['review_cycle_id'] = 'RC1'
        item['identity_assessment'] = {'effective': False, 'status': 'working'}
        engine.runtime['review_cycles']['RC1'] = {'id': 'RC1', 'status': 'working', 'decision': None,
                                                'phase': 'initial', 'history': []}
        engine.runtime['executions']['review-ex'] = {'id': 'review-ex', 'role': 'identity_review',
            'status': 'running', 'action': {'target': 'K1'}}
        engine._enqueue('identity_review', 'K1', review_cycle_id='RC1')
        engine.control('knowledge', {'operation': 'revise', 'id': 'K1', 'changes': {'statement': 'New claim'}, 'reason': 'Explicit revision'})
        self.assertEqual(engine.runtime['review_cycles']['RC1']['status'], 'unresolved')
        self.assertEqual(engine.runtime['executions']['review-ex']['stop_requested'], 'knowledge_revise')
        self.assertFalse(any(a['role'] == 'identity_review' for a in engine.runtime['queue']))
        formal = next(a for a in engine.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(formal['previous_cycle_id'], 'RC1')

    def test_external_real_loopback_ledger_and_reconciliation_wake_waiting_task(self):
        engine = self.engine
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(self.path)
                body = b'confirmed local response'
                self.send_response(409 if self.path == '/reject' else 200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                received.append(self.path)
                self.close_connection = True
            def log_message(self, *args): pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        origin = f'http://127.0.0.1:{server.server_port}'
        engine.instance['grants']['HTTP'] = {'id': 'HTTP', 'kind': 'http', 'status': 'active',
            'allowed_origins': [origin], 'allowed_methods': ['GET', 'POST'], 'allowed_path_prefixes': ['/']}
        engine.control('external', {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP1', 'request': {'method': 'GET', 'url': origin + '/read'}})
        engine.machine('external_action')
        self.assertEqual(engine.runtime['external_operations']['OP1']['status'], 'confirmed')
        execution_id = engine.runtime['external_operations']['OP1']['execution_id']
        self.assertTrue(execution_id.startswith('EX-'))
        self.assertNotEqual(execution_id, 'OP1')
        self.assertEqual(engine.runtime['executions'][execution_id]['operation_id'], 'OP1')
        self.assertTrue(engine.runtime['external_operations']['OP1']['succeeded'])
        states = [s['runtime']['external_operations'].get('OP1', {}).get('status') for s in engine.saves]
        self.assertEqual({s['runtime']['external_operations']['OP1']['execution_id'] for s in engine.saves
                          if 'OP1' in s['runtime']['external_operations']}, {execution_id})
        self.assertIn('prepared', states)
        self.assertIn('running', states)
        self.assertIn('confirmed', states)
        engine.control('external', {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP-rejected', 'request': {'method': 'GET', 'url': origin + '/reject'}})
        engine.machine('external_action')
        self.assertEqual(engine.runtime['external_operations']['OP-rejected']['status'], 'confirmed')
        self.assertEqual(engine.runtime['external_operations']['OP-rejected']['http_status'], 409)
        self.assertFalse(engine.runtime['external_operations']['OP-rejected']['succeeded'])
        engine.control('external', {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP2', 'request': {'method': 'POST', 'url': origin + '/uncertain', 'body': 'local test'}})
        engine.task(condition={'op': 'record_field_equals', 'record_id': 'OP2', 'pointer': '/status', 'value': 'confirmed'})
        engine.machine('external_action')
        self.assertEqual(engine.runtime['external_operations']['OP2']['status'], 'unknown')
        unknown_execution_id = engine.runtime['external_operations']['OP2']['execution_id']
        self.assertNotEqual(engine.runtime['tasks']['T1']['status'], 'ready')
        engine._enqueue('external_action', 'OP2')
        engine.machine('external_action')
        self.assertEqual(received, ['/read', '/reject', '/uncertain'])
        engine.control('external', {'operation': 'reconcile', 'id': 'OP2', 'result': 'confirmed', 'succeeded': True,
                                    'evidence': 'Operator compared the local server receipt'})
        self.assertEqual(engine.runtime['tasks']['T1']['status'], 'ready')
        self.assertEqual(engine.runtime['external_operations']['OP2']['execution_id'], unknown_execution_id)
        self.assertTrue(engine.runtime['external_operations']['OP2']['succeeded'])
        self.assertEqual(engine.runtime['external_operations']['OP2']['reconciliation']['source'], 'user')
        self.assertTrue(engine.runtime['external_operations']['OP2']['reconciliation']['source_ref'].startswith('user-'))
        self.assertEqual(state_errors(engine.instance, engine.runtime), [])

    def test_external_retry_reuses_operation_identity_only_after_known_failure(self):
        engine = self.engine
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                received.append(self.path)
                body = b'retried receipt'
                self.send_response(200)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)
            def log_message(self, *args): pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start(); self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        origin = f'http://127.0.0.1:{server.server_port}'
        variable = 'DO_MATH_RETRY_TEST_TOKEN'
        os.environ.pop(variable, None)
        self.addCleanup(lambda: os.environ.pop(variable, None))
        engine.instance['grants']['HTTP'] = {'id': 'HTTP', 'kind': 'http', 'status': 'active',
            'allowed_origins': [origin], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/'],
            'credential_env': {'X-Test-Token': variable}, 'allow_idempotent_retry': False}
        request = {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP-retry',
                   'request': {'method': 'POST', 'url': origin + '/retry', 'body': 'fixed bytes'}}
        engine.control('external', request, 'prepare-retry')
        engine.machine('external_action')
        failed = deepcopy(engine.runtime['external_operations']['OP-retry'])
        self.assertEqual((failed['status'], failed['transmitted']), ('failed', False))
        self.assertEqual(received, [])
        os.environ[variable] = 'available-now'
        engine.control('external', {'operation': 'retry', 'id': 'OP-retry', 'grant_id': 'HTTP'}, 'retry-known-failure')
        prepared = engine.runtime['external_operations']['OP-retry']
        self.assertEqual((prepared['id'], prepared['request_sha256'], prepared['idempotency_key']),
                         (failed['id'], failed['request_sha256'], failed['idempotency_key']))
        self.assertNotEqual(prepared['execution_id'], failed['execution_id'])
        self.assertEqual(prepared['history'][-1]['previous_status'], 'failed')
        self.assertEqual(prepared['attempts'][-1]['outcome'], 'failed')
        engine.machine('external_action')
        confirmed = engine.runtime['external_operations']['OP-retry']
        self.assertEqual((confirmed['status'], confirmed['succeeded']), ('confirmed', True))
        self.assertEqual(received, ['/retry'])
        with self.assertRaises(ValueError):
            engine.control('external', {'operation': 'retry', 'id': 'OP-retry', 'grant_id': 'HTTP'}, 'retry-confirmed')
        self.assertEqual(received, ['/retry'])

    def test_unknown_requires_reconciliation_before_explicit_authorized_retry(self):
        engine = self.engine
        received = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                received.append(self.path)
                if len(received) == 1:
                    self.close_connection = True
                else:
                    body = b'retried'
                    self.send_response(200)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
            def log_message(self, *args): pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start(); self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        origin = f'http://127.0.0.1:{server.server_port}'
        engine.instance['grants']['HTTP'] = {'id': 'HTTP', 'kind': 'http', 'status': 'active',
            'allowed_origins': [origin], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/'], 'allow_idempotent_retry': True}
        engine.control('external', {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP-unknown-retry',
                                    'request': {'method': 'POST', 'url': origin + '/unknown', 'body': 'fixed'}}, 'prepare-unknown')
        engine.machine('external_action')
        self.assertEqual(engine.runtime['external_operations']['OP-unknown-retry']['status'], 'unknown')
        with self.assertRaises(ValueError):
            engine.control('external', {'operation': 'retry', 'id': 'OP-unknown-retry', 'grant_id': 'HTTP'}, 'retry-unknown')
        engine.control('external', {'operation': 'reconcile', 'id': 'OP-unknown-retry', 'result': 'failed',
                                    'evidence': 'User determined the remote outcome was a failure'}, 'reconcile-unknown-failed')
        engine.control('external', {'operation': 'retry', 'id': 'OP-unknown-retry', 'grant_id': 'HTTP'}, 'retry-reconciled-failure')
        engine.machine('external_action')
        self.assertEqual((engine.runtime['external_operations']['OP-unknown-retry']['status'], received), ('confirmed', ['/unknown', '/unknown']))


    def test_external_prepare_replay_preserves_ledger_states(self):
        engine = FakeEngine(self.temp.name)
        engine.control('decision', {'change': {'kind': 'grant', 'decision_id': 'grant-http', 'grant': {
            'id': 'HTTP', 'kind': 'http', 'allowed_origins': ['http://127.0.0.1:1'],
            'allowed_methods': ['GET'], 'allowed_path_prefixes': ['/'], 'credential_env': {}}}}, 'grant-control')
        payload = {'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP',
                   'request': {'method': 'GET', 'url': 'http://127.0.0.1:1/', 'body': ''}}
        engine.control('external', payload, 'prepare-control')
        original = deepcopy(engine.runtime['external_operations']['OP'])
        for state in ('prepared', 'running', 'unknown', 'confirmed'):
            engine.runtime['external_operations']['OP']['status'] = state
            engine.runtime['queue'] = []
            engine.control('external', payload, 'replay-' + state)
            self.assertEqual(engine.runtime['external_operations']['OP']['execution_id'], original['execution_id'])
            self.assertEqual(engine.runtime['external_operations']['OP']['status'], state)
            self.assertEqual(bool(engine.runtime['queue']), state == 'prepared')
        changed = deepcopy(payload); changed['request']['body'] = 'different'
        with self.assertRaises(ValueError): engine.control('external', changed, 'changed-payload')


class TrustCommandTests(unittest.TestCase):
    def test_transition_uses_the_full_recorded_verifier_command(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = FakeEngine(directory)
            old = engine.environment('lean-old', active=True)
            engine.knowledge('K1', old)
            new = engine.environment('lake-new')
            command = ['lake-new', '--dir', 'project', 'env', 'lean']
            engine.instance['trust_environments'][new]['toolchain']['configured_command'] = command
            engine.control('trust', {'operation': 'transition', 'env_id': new})
            engine.machine('trust_check')
            self.assertEqual(engine.formal_calls[0]['lean_command'], command)


if __name__ == '__main__':
    unittest.main()
