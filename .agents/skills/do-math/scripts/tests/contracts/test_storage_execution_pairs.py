"""Stored execution-family outputs, exact gate ownership and scheduler returns."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from do_math import activities
from do_math.provider_wait import utc
from do_math.scheduled_operator import hold, release
from do_math.state_contract import default_state_contract
from contracts.pairs import assert_pair
from support.storage_execution_pairs import execution_scene, stored_activity_samples, stored_pair
from support.storage_execution_pairs import StoredExecutions, stored_execution_inputs, stored_kind_input
from support.storage_execution_pairs import (stored_provider_returns, stored_observation_and_stop,
    stored_operator_runner, stored_operational_dispositions, stored_late_return)
from support.storage_profile_pairs import acquire_profile, family_receiver, profile_cases


class StorageExecutionPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.cases = profile_cases(cls.root / 'inputs')

    def assert_pair(self, pair):
        assert_pair(self, pair, pair.samples(self.root))

    def test_executions_cover_every_required_and_optional_receiver_field(self):
        """About 70 s cold, over the contract budget: real role inputs and Git publications are the subject.

        Content assertions and the reverse walk consume the same produced rows;
        public preparation/review prefixes are shared by the existing templates.
        """
        from dataclasses import replace
        from support.storage_execution_pairs import (
            assert_stored_delegation_input, assert_stored_provider_failure,
            stored_recovery_and_machine_outputs,
            assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs,
            assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup,
            assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload)
        samples = StoredExecutions(self)
        for scene in (stored_execution_inputs, assert_stored_delegation_input, stored_kind_input, stored_provider_returns,
                      assert_stored_provider_failure,
                      stored_observation_and_stop, stored_operator_runner,
                      stored_operational_dispositions, stored_late_return,
                      stored_recovery_and_machine_outputs):
            with self.subTest(scene=scene.__name__):
                scene(samples)
        assert_stored_unsealed_return_preserves_the_exact_rejected_candidate_and_check_refs(self, samples)
        assert_stored_maintenance_archive_writes_termination_and_collection_before_local_cleanup(self, samples)
        assert_stored_prepared_call_and_returned_evidence_keep_their_own_inputs_after_reload(self, samples)
        pair = stored_pair('executions', samples.snapshots)
        self.assert_pair(pair)
        # Adding an unproduced optional field must fail the very same reverse
        # check, even though every actual row still passes its receiver.
        with self.assertRaisesRegex(AssertionError, 'no producer branch writes'):
            self.assert_pair(replace(pair, fields=pair.fields | {'unproduced_optional'}))

    def test_activity_fields_and_preparation_attempts_survive_each_publication(self):
        """Nine small storage publications; no calls or native Jobs."""
        scene = stored_activity_samples(self.root / 'activity', self.cases[0])
        self.assert_pair(stored_pair('activities', scene.samples))
        states = {branch: runtime for branch, _, runtime in scene.samples}
        self.assertEqual(states['empty']['activities'], {})
        ready = states['ready']['activities']['AY-storage']
        self.assertEqual(ready, {'id': 'AY-storage', 'activity_kind': 'maintenance',
            'owner_ref': {'kind': 'storage-example', 'text': 'e\u0301\r\n'},
            'opened_at': scene.engine.ports.clock.now(), 'input_refs': ['IN-one', {'input': 'two'}],
            'status': 'ready', 'stage': 'collect', 'execution_limit': 2,
            'assigned_execution_ids': [], 'result_refs': [], 'unresolved': [], 'followups': []})
        self.assertEqual([len(states[b]['executions']) for b in ('ready', 'ended-0', 'ended-1')], [0, 1, 2])
        for index, outcome in enumerate(('start_failed', 'cancelled')):
            execution = states[f'ended-{index}']['executions'][f'EX-storage-{index}']
            family_receiver(default_state_contract().family('runtime', 'executions'))(execution)
            self.assertEqual((execution['actor_kind'], execution['status'], execution['outcome']),
                             ('ai', 'ended', outcome))
            self.assertEqual(execution['input_manifest'], [])
            self.assertNotIn('capacity', execution)
            self.assertEqual(execution['continuation_of'], 'EX-storage-0' if index else None)
            self.assertEqual(execution['context_origin'], ['EX-storage-0'] if index else [])
            self.assertEqual(execution['input_preparation']['reason'], 'Explicit synthetic input failure')
            self.assertEqual(execution['result_disposition'], {'kind': 'input_preparation',
                'stage': 'context', 'reason': 'Explicit synthetic input failure'})
        waiting = states['waiting']['activities']['AY-storage']
        self.assertEqual(waiting['status'], 'waiting')
        self.assertEqual(waiting['waiting'], {'kind': 'required_input', 'reason': 'Need exact input',
            'condition': {'input': 'e\u0301'}, 'next_owner': 'user', 'at': scene.engine.ports.clock.now()})
        resumed = states['resumed']['activities']['AY-storage']
        self.assertEqual(resumed['status'], 'ready')
        self.assertNotIn('waiting', resumed)
        self.assertEqual(resumed['resumed_at'], scene.engine.ports.clock.now())
        finished = states['finished']['activities']['AY-storage']
        self.assertEqual((finished['status'], finished['result_refs'], finished['unresolved'], finished['followups']),
                         ('finished', ['IN-one'], [{'input': 'two'}], ['Ask user']))
        self.assertEqual(finished['finished_at'], scene.engine.ports.clock.now())
        self.assertEqual(scene.store.load(scene.samples[1][1])[2]['activities']['AY-storage'], ready)
        self.assertEqual(scene.engine.ports.jobs.launched, [])

    def test_wrong_activity_condition_cannot_change_a_stored_wait(self):
        scene = execution_scene(self.root / 'condition', self.cases[0])
        engine = scene.engine
        activities.open_activity(engine.runtime, activity_id='AY-condition', activity_kind='maintenance',
            owner_ref=engine.instance['id'], input_refs=[], opened_at=engine.ports.clock.now())
        activities.wait_for(engine.runtime, 'AY-condition', kind='required_input', reason='Exact condition',
            condition={'input': 'e\u0301'}, next_owner='user', at=engine.ports.clock.now())
        before = scene.publish('waiting')
        with self.assertRaisesRegex(ValueError, 'the resolved condition differs from the recorded wait'):
            activities.resume_activity(engine.runtime, 'AY-condition', condition={'input': '\u00e9'}, at=engine.ports.clock.now())
        self.assertEqual(scene.publish('unchanged'), before)
        self.assertEqual(scene.samples[0][1], scene.samples[1][1])

    def test_provider_wait_fields_preserve_failure_probe_and_exact_owner_results(self):
        """Two providers on accepted public profiles; each gate state is actually stored."""
        for case in self.cases[:2]:
            with self.subTest(provider=case.name):
                scene = execution_scene(self.root / ('gate-' + case.name), case)
                engine, clock = scene.engine, scene.engine.ports.clock
                ref = engine.instance['role_profile_refs']['maintenance'][0]
                profile = engine.instance['execution_profiles'][ref['id']]
                provider = profile['ai']['provider']
                scene.publish('empty')
                original = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=0)
                now = int(clock.wall().timestamp())
                failure = {'kind': 'provider_limit', 'provider': provider, 'retry_at': utc(now + 300),
                           'evidence_ref': 'synthetic-e\u0301.json', 'limit_windows': [], 'reported_decimal': 1.25}
                result = {'status': 'failed', 'error_kind': 'provider_limit', 'failure': failure}
                scene.slots.provider_result_from_run(original['id'], result, engine.instance['config'], current_time=now)
                first = scene.publish('waiting')['provider_waits']['PW-' + provider]
                self.assertEqual(first, {'id': 'PW-' + provider, 'provider': provider, 'generation': 1,
                    'state': 'waiting', 'retry_at': now + 300, 'attempts': 1,
                    'probe_owner': None, 'probe_started_at': None,
                    'evidence': {'execution_id': 'EX-profile-0', 'kind': 'provider_limit', 'provider': provider,
                        'evidence_ref': 'synthetic-e\u0301.json',
                        'reported_fields_json': json.dumps(failure, ensure_ascii=False, allow_nan=False)}})
                self.assertEqual(json.loads(first['evidence']['reported_fields_json']), failure)
                self.assertFalse(scene.slots.admission_check(profile, current_time=now + 299)['allowed'])
                # At retry, acquire publishes the exact owner, not an available gate.
                clock.advance(300)
                probe = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=1)
                checking = scene.publish('checking')['provider_waits']['PW-' + provider]
                self.assertEqual((checking['state'], checking['probe_owner'], checking['probe_started_at']),
                                 ('checking', probe['id'], now + 300))
                scene.slots.provider_result_from_run(original['id'], {'status': 'completed'}, engine.instance['config'])
                self.assertEqual(scene.publish('wrong-owner')['provider_waits']['PW-' + provider], checking)
                self.assertTrue(scene.slots.release(probe['id']))
                released = scene.publish('local-only')['provider_waits']['PW-' + provider]
                self.assertEqual((released['state'], released['probe_owner'], released['probe_started_at']),
                                 ('waiting', None, None))
                self.assertEqual((released['generation'], released['attempts'], released['evidence']), (1, 1, first['evidence']))
                probe = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=2)
                # An owner result with no provider response returns to backoff.
                scene.slots.provider_result_from_run(probe['id'], {'status': 'failed'}, engine.instance['config'])
                unobserved = scene.publish('unobserved')['provider_waits']['PW-' + provider]
                self.assertEqual((unobserved['state'], unobserved['attempts'], unobserved['retry_at']),
                                 ('waiting', 2, now + 900))
                clock.advance(600)
                probe = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=3)
                scene.slots.provider_result_from_run(probe['id'], {'status': 'failed', 'execution': {'collect': {
                    'jsonl': {'turn_failed': True}}}}, engine.instance['config'])
                available = scene.publish('available')['provider_waits']['PW-' + provider]
                self.assertEqual({k: available[k] for k in ('state', 'retry_at', 'attempts', 'probe_owner', 'probe_started_at')},
                                 {'state': 'available', 'retry_at': None, 'attempts': 0, 'probe_owner': None, 'probe_started_at': None})
                self.assertEqual((available['generation'], available['evidence']), (1, first['evidence']))
                self.assert_pair(stored_pair('provider_waits', scene.samples))
                self.assertEqual(scene.store.load(scene.samples[1][1])[2]['provider_waits']['PW-' + provider], first)
                self.assertEqual(engine.ports.jobs.launched, [])

    def test_scheduler_wake_outputs_are_stored_with_exact_content(self):
        """Only the scheduler port is substituted; reconciliation and saving are real."""
        scene = execution_scene(self.root / 'wake', self.cases[0])
        engine, clock = scene.engine, scene.engine.ports.clock
        scheduler = engine.ports.scheduler
        engine.instance['config']['operator_enabled'] = False
        engine._schedule_provider_wake()
        self.assertNotIn('provider_wake', scene.publish('disabled'))
        self.assertEqual(scheduler.calls, [])
        engine.instance['config']['operator_enabled'] = True
        engine._schedule_provider_wake()
        self.assertEqual(scene.publish('no-wait')['provider_wake'], {'status': 'not_needed'})
        ref = engine.instance['role_profile_refs']['maintenance'][0]
        execution = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=0)
        failure = {'kind': 'provider_limit', 'provider': 'codex', 'retry_at': None}
        scene.slots.provider_result_from_run(execution['id'],
            {'status': 'failed', 'error_kind': 'provider_limit', 'failure': failure}, engine.instance['config'])
        scene.publish('gate')
        retry_at = utc(int(clock.wall().timestamp()) + 300)
        engine._schedule_provider_wake()
        scheduled = scene.publish('registered')['provider_wake']
        self.assertEqual(scheduled, {'status': 'scheduled', 'key': 'codex:1', 'retry_at': retry_at})
        self.assertEqual([action for action, _ in scheduler.calls], ['status', 'schedule-wake'])
        marker = Path(engine.instance['workspace']) / 'operator' / 'wake-registration.json'
        self.assertEqual(json.loads(marker.read_bytes()), {'key': 'codex:1', 'retry_at': retry_at})
        engine._schedule_provider_wake()
        self.assertEqual(scene.publish('existing')['provider_wake'], scheduled)
        self.assertEqual([action for action, _ in scheduler.calls], ['status', 'schedule-wake', 'status'])
        hold(Path(engine.instance['workspace']), reason='Synthetic hold', clock=clock)
        engine._schedule_provider_wake()
        self.assertEqual(scene.publish('held')['provider_wake'], {'status': 'held'})
        self.assertEqual(scheduler.calls[-1][0], 'cancel-wake')
        self.assertFalse(marker.exists())
        release(Path(engine.instance['workspace']), clock=clock)
        engine._schedule_provider_wake()
        self.assertEqual(scene.publish('registered-again')['provider_wake'], scheduled)
        engine.instance['config']['operator_enabled'] = False
        engine._schedule_provider_wake()
        self.assertEqual(scene.publish('disabled-existing')['provider_wake'], {'status': 'not_needed'})
        self.assertEqual(scheduler.calls[-1][0], 'cancel-wake')
        self.assertFalse(marker.exists())
        family = default_state_contract().family('runtime', 'provider_wake')
        self.assertEqual(family.shape, 'singleton')
        self.assertNotIn('properties', family.schema)
        for _, _, runtime in scene.samples:
            if 'provider_wake' in runtime:
                value = runtime['provider_wake']
                family_receiver(family)(value)
                self.assertNotIn('observed', value)
        self.assertEqual(scene.store.load(scene.samples[3][1])[2]['provider_wake'], scheduled)

    def test_scheduler_failure_is_preserved_by_the_open_evidence_receiver(self):
        from unittest.mock import patch
        for failing_action in ('status', 'schedule-wake', 'cancel-wake'):
            with self.subTest(action=failing_action):
                scene = execution_scene(self.root / ('wake-failed-' + failing_action), self.cases[0])
                engine = scene.engine
                ref = engine.instance['role_profile_refs']['maintenance'][0]
                execution = acquire_profile(scene.slots, engine.instance, engine.runtime, ref, index=0)
                scene.slots.provider_result_from_run(execution['id'], {'status': 'failed', 'error_kind': 'provider_limit',
                    'failure': {'kind': 'provider_limit', 'provider': 'codex', 'retry_at': None}}, engine.instance['config'])
                if failing_action == 'cancel-wake':
                    engine._schedule_provider_wake()
                    engine.instance['config']['operator_enabled'] = False
                run = engine.ports.scheduler.run

                def schedule(action, arguments):
                    if action == failing_action:
                        raise RuntimeError('Scheduler e\u0301\r\nfailed: ' + action)
                    return run(action, arguments)

                with patch.object(engine.ports.scheduler, 'run', side_effect=schedule):
                    engine._schedule_provider_wake()
                saved = scene.publish('failed')['provider_wake']
                self.assertEqual(saved, {'status': 'failed', 'error': 'Scheduler e\u0301\r\nfailed: ' + failing_action})
                family_receiver(default_state_contract().family('runtime', 'provider_wake'))(saved)

    def test_two_provider_rows_keep_admitted_identity_and_select_the_earliest_wake(self):
        """Actual configuration and admissions produce both rows; no gate fixtures are injected."""
        scene = execution_scene(self.root / 'two-providers', self.cases[0])
        engine, clock = scene.engine, scene.engine.ports.clock
        adopted, runtime = engine._configure_candidate(engine.instance, engine.runtime, {'origin': 'user', 'config': {
            'tier_models': {'low': 'claude:claude-sonnet-5', 'medium': 'gpt-6-astra', 'high': 'gpt-6-astra'},
            'session_limits': {'work': {'claude:claude-sonnet-5': 3, 'gpt-6-astra': 3}}}})
        engine.instance, engine.runtime = adopted, runtime
        scene.publish('configured')
        references = engine.instance['role_profile_refs']['maintenance']
        selected = {engine.instance['execution_profiles'][ref['id']]['ai']['provider']: ref for ref in references}
        self.assertEqual(set(selected), {'codex', 'claude'})
        for index, provider in enumerate(('codex', 'claude')):
            execution = acquire_profile(scene.slots, engine.instance, engine.runtime, selected[provider], index=index)
            before = deepcopy(engine.runtime)
            with self.assertRaisesRegex(ValueError, 'provider failure differs from admission'):
                scene.slots.provider_result_from_run(execution['id'], {'status': 'failed', 'error_kind': 'provider_limit',
                    'failure': {'kind': 'provider_limit', 'provider': 'claude' if provider == 'codex' else 'codex'}},
                    engine.instance['config'])
            self.assertEqual(engine.runtime, before)
            scene.slots.provider_result_from_run(execution['id'], {'status': 'failed', 'error_kind': 'provider_limit',
                'failure': {'kind': 'provider_limit', 'provider': provider, 'retry_at': utc(int(clock.wall().timestamp()) + 600 - 300 * index)}},
                engine.instance['config'])
            loaded = scene.publish(provider)['provider_waits']
            self.assertEqual(set(loaded), {'PW-codex'} if index == 0 else {'PW-codex', 'PW-claude'})
            self.assertIsNone(loaded['PW-' + provider]['evidence']['evidence_ref'])
            self.assertEqual(loaded['PW-' + provider]['evidence']['execution_id'], f'EX-profile-{index}')
        engine._schedule_provider_wake()
        saved = scene.publish('earliest')
        self.assertEqual(saved['provider_wake'], {'status': 'scheduled', 'key': 'claude:1',
            'retry_at': utc(int(clock.wall().timestamp()) + 300)})
        self.assertEqual(scene.store.load(scene.samples[1][1])[2]['provider_waits'].keys(), {'PW-codex'})


if __name__ == '__main__':
    unittest.main()
