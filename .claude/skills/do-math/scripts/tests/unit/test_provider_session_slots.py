"""Model capacity and provider gates (``session_slots.SessionSlots``, layer 2) on the Jobs and clock port fakes.

Admission reserves a work role's model slot and issues its launch ticket from
the Jobs port's owner identity; release returns the slot only when the port
confirms the ticket's named Job is empty. Operational roles reserve no slot.
Provider gates hold admission until their retry time and let one probe through.
"""
from copy import deepcopy
import unittest

from do_math import execution_profiles
from do_math.canonical import canonical_json
from do_math.configuration import DEFAULT_CONFIG, validate_config
from do_math.execution_profiles import build_profiles
from do_math.model_policy import selection
from do_math.session_slots import SessionSlots
from do_math.state_contract import default_state_contract, validate_record
from support.provider_inputs import PROFILE_CONFIG
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs


def work_profile(instance, **ai):
    return next(p for p in instance['execution_profiles'].values()
                if p['role'] == 'research_work' and all(p['ai'].get(key) == value for key, value in ai.items()))


def queued(execution_id, role='research_work'):
    return {'id': execution_id, 'role': role, 'status': 'queued'}


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.jobs, self.clock = ProviderJobs(), FakeClock()

    def slots(self, runtime, instance, **options):
        from support.entry import entry
        _entry = entry()
        return SessionSlots(runtime, instance, jobs=self.jobs, clock=self.clock, **options, host_id=_entry.host_id)

    def test_admission_probe_preserves_history_and_provider_gate_across_capacity_editions(self):
        from support.entry import entry
        _entry = entry()
        instance = {**build_profiles(PROFILE_CONFIG, host=_entry.ports.host), 'config': deepcopy(PROFILE_CONFIG)}
        profile = work_profile(instance)
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        slots = self.slots(runtime, instance)
        model = profile['ai']['model']
        self.assertTrue(slots.acquire('EX-history', profile=profile, execution=queued('EX-history')))
        self.assertTrue(slots.release('EX-history'))
        history_id = runtime['executions']['EX-history']['capacity']['reservation_ids'][0]
        history = deepcopy(runtime['reservations'][history_id])
        limits = deepcopy(PROFILE_CONFIG['session_limits'])
        limits['work'][model] = 1
        instance['config']['session_limits'] = limits
        execution_profiles.apply_editions(instance, build_profiles(instance['config'], host=_entry.ports.host))
        provider = profile['ai']['provider']
        runtime['provider_waits']['PW-' + provider] = {
            'id': 'PW-' + provider, 'provider': provider, 'generation': 1,
            'state': 'waiting', 'retry_at': 100, 'attempts': 1,
            'evidence': {'evidence_ref': 'fixture-limit'},
            'probe_owner': None, 'probe_started_at': None}
        before = deepcopy(runtime)
        observer = self.slots(runtime, instance, observer=True)
        self.assertTrue(observer.admission_check(profile, current_time=100)['allowed'])
        self.assertEqual(runtime, before)
        self.assertTrue(slots.acquire('EX-held', profile=profile, execution=queued('EX-held'), current_time=100))
        self.assertEqual(runtime['reservations'][history_id], history)
        held_id = runtime['executions']['EX-held']['capacity']['reservation_ids'][0]
        self.assertNotEqual(runtime['reservations'][held_id]['constraint_id'], history['constraint_id'])
        before = deepcopy(runtime)
        self.assertEqual(observer.admission_check(profile, current_time=100)['wait']['kind'], 'provider_limit')
        self.assertEqual(runtime, before)
        runtime['provider_waits'].clear()
        before = deepcopy(runtime)
        denied = observer.admission_check(profile, current_time=100)
        self.assertFalse(denied['allowed'])
        self.assertEqual(denied['wait']['kind'], 'capacity')
        self.assertEqual(runtime, before)

    def test_git_admission_all_or_nothing_and_unknown_release(self):
        from support.entry import entry
        _entry = entry()
        instance = build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        profile = work_profile(instance, model=PROFILE_CONFIG['tier_models']['low'])
        slots = self.slots(runtime, instance)
        for i in range(3):
            self.assertTrue(slots.acquire(f'EX-{i}', profile=profile, execution=queued(f'EX-{i}')))
        for reservation in runtime['reservations'].values():
            validate_record(default_state_contract().family('runtime', 'reservations').checker, reservation,
                            'reservation')
        before = deepcopy(runtime)
        self.assertFalse(slots.acquire('EX-over', profile=profile, execution=queued('EX-over')))
        self.assertEqual(runtime, before)
        name = runtime['executions']['EX-0']['launch_ticket']['job_name']
        identity = {'job_name': name, 'pid': 1}
        started = slots.started('EX-0', identity, at='2026-01-01T00:00:00+00:00')
        self.assertIs(started, runtime['executions']['EX-0'])
        self.assertEqual((started['status'], started['started_at'], started['capacity']['process']),
                         ('running', '2026-01-01T00:00:00+00:00', identity))
        repeated = deepcopy(runtime)
        self.assertIs(slots.started('EX-0', identity, at='2026-01-01T00:00:01+00:00'), started)
        self.assertEqual(runtime, repeated)
        from do_math.execution_lifecycle import transition_execution
        transition_execution(runtime['executions']['EX-1'], 'stopping', at='2026-01-01T00:00:01+00:00', reason='user_pause')
        before_stop = deepcopy(runtime)
        stop_identity = {'job_name': runtime['executions']['EX-1']['launch_ticket']['job_name'], 'pid': 2}
        slots.started('EX-1', stop_identity, at='2026-01-01T00:00:02+00:00')
        expected = deepcopy(before_stop)
        expected['executions']['EX-1']['capacity']['process'] = stop_identity
        expected['executions']['EX-1']['started_at'] = '2026-01-01T00:00:02+00:00'
        self.assertEqual(runtime, expected)
        self.assertEqual(runtime['executions']['EX-1']['status'], 'stopping')
        slots.started('EX-1', stop_identity, at='2026-01-01T00:00:03+00:00')
        self.assertEqual(runtime, expected)
        # The Jobs port cannot tell whether the ticket's named Job is empty: the slot stays counted.
        self.jobs.empty[name] = None
        self.assertFalse(slots.release('EX-0'))
        self.assertEqual(slots.snapshot()[profile['ai']['model']]['used'], 3)
        self.jobs.empty[name] = True
        self.assertTrue(slots.release('EX-0'))
        self.assertTrue(slots.release('EX-0'))
        self.assertEqual(slots.snapshot()[profile['ai']['model']]['used'], 2)
        # Operational AI roles reserve no model slot, even when every work slot is taken.
        self.assertTrue(slots.acquire('EX-3', profile=profile, execution=queued('EX-3')))
        operation = next(p for p in instance['execution_profiles'].values()
                         if p['role'] == 'maintenance' and p['ai']['model'] == profile['ai']['model'])
        self.assertEqual(operation['ai']['capacity_refs'], [])
        self.assertTrue(slots.acquire('EX-op', profile=operation, execution=queued('EX-op', 'maintenance')))
        self.assertEqual(runtime['executions']['EX-op']['capacity']['reservation_ids'], [])
        self.assertEqual(slots.snapshot()[profile['ai']['model']]['used'], 3)

    def test_admission_accepts_registered_queued_execution_exactly_once(self):
        from support.entry import entry
        _entry = entry()
        instance = build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        profile = work_profile(instance)
        execution = {**queued('EX-registered'), 'execution_profile_ref': execution_profiles.profile_ref(profile),
                     'owner_activity_id': 'AY-one'}
        runtime = {'executions': {execution['id']: execution}, 'reservations': {}}
        slots = self.slots(runtime, instance)
        self.assertTrue(slots.acquire(execution['id'], profile=profile, execution=execution))
        self.assertIs(runtime['executions'][execution['id']], execution)
        self.assertEqual(execution['owner_activity_id'], 'AY-one')
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, 'execution IDs are single-use; only the registered unreserved '
                                                'execution can be admitted'):
            slots.acquire(execution['id'], profile=profile, execution=execution)
        self.assertEqual(runtime, before)


class ProviderGateTests(unittest.TestCase):
    def test_provider_wait_is_canonical_and_serializes_retry_probe(self):
        from support.entry import entry
        _entry = entry()
        instance = build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        profile = work_profile(instance)
        slots = SessionSlots(runtime, instance, jobs=ProviderJobs(), clock=FakeClock(), host_id=_entry.host_id)

        def admit(eid, t):
            return slots.acquire(eid, profile=profile, execution=queued(eid), current_time=t)
        self.assertTrue(admit('EX-failure', 10))
        failure = {'kind': 'provider_limit', 'provider': profile['ai']['provider'],
                   'retry_at': '1970-01-01T00:00:20+00:00', 'evidence_ref': 'stdout.jsonl'}
        slots.provider_result_from_run('EX-failure', {'status': 'failed', 'error_kind': 'provider_limit',
                                                      'failure': failure}, PROFILE_CONFIG, current_time=10.5)
        self.assertTrue(runtime['provider_waits'])
        self.assertTrue(all(key == row['id'] for key, row in runtime['provider_waits'].items()),
                        'provider gates must persist as individual family records')
        try:
            canonical_json(runtime)
        except ValueError as error:
            self.fail('Git reservation path emits noncanonical state: ' + str(error))
        self.assertFalse(admit('EX-too-early', 19))
        self.assertTrue(admit('EX-probe', 21))
        self.assertFalse(admit('EX-concurrent-probe', 21))
        slots.provider_result_from_run('EX-probe', {'status': 'completed'}, PROFILE_CONFIG, current_time=22)
        self.assertTrue(admit('EX-after', 22))

    def test_zero_capacity_and_provider_probe_are_distinct_and_read_only(self):
        from support.entry import entry
        _entry = entry()
        config = deepcopy(DEFAULT_CONFIG)
        for model in config['session_limits']['work']:
            config['session_limits']['work'][model] = 0
        instance = {**build_profiles(config, host=_entry.ports.host), 'config': config}
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        profile = work_profile(instance)
        slots = SessionSlots(runtime, instance, jobs=ProviderJobs(), clock=FakeClock(), host_id=_entry.host_id)
        wait = slots.admission_check(profile)['wait']
        self.assertEqual((wait['kind'], wait['next_owner']), ('capacity', 'user'))
        self.assertNotIn('retry_at', wait)
        provider = profile['ai']['provider']
        runtime['provider_waits']['PW-' + provider] = {'provider': provider, 'state': 'waiting',
            'retry_at': 100, 'probe_owner': None, 'probe_started_at': None}
        before = deepcopy(runtime)
        self.assertEqual(slots.admission_check(profile, current_time=90)['wait']['kind'], 'provider_limit')
        self.assertEqual(slots.admission_check(profile, current_time=110)['wait']['kind'], 'capacity')
        self.assertEqual(runtime, before)


class MixedProviderTests(unittest.TestCase):
    def test_mixed_models_use_existing_selection_and_per_model_work_slots(self):
        from support.entry import entry
        _entry = entry()
        config = {**DEFAULT_CONFIG, 'tier_models': {'high': 'claude:opus', 'medium': 'gpt-5.6-sol', 'low': 'claude:haiku'},
                  'session_limits': {'work': {'claude:opus': 1, 'gpt-5.6-sol': 1, 'claude:haiku': 1}}}
        validate_config(config, host_id=_entry.host_id)
        self.assertEqual(selection(config, {'role': 'research_plan'}, {}, {})['model'], 'claude:opus')
        self.assertEqual(selection(config, {'role': 'task_contract_review'}, {}, {})['model'], 'gpt-5.6-sol')
        state = {**build_profiles(config, host=_entry.ports.host), 'config': config}
        runtime = {'executions': {}, 'reservations': {}}
        slots = SessionSlots(runtime=runtime, instance=state, jobs=ProviderJobs(), clock=FakeClock(), host_id=_entry.host_id)

        def acquire(eid, role, model):
            profile = next(p for p in state['execution_profiles'].values()
                           if p['role'] == role and p.get('ai', {}).get('model') == model)
            return slots.acquire(eid, profile=profile, execution={'id': eid, 'role': role, 'status': 'queued'})
        self.assertTrue(acquire('one', 'research_work', 'claude:opus'))
        self.assertFalse(acquire('two', 'research_work', 'claude:opus'))
        # An operational role reserves no work slot of its model.
        self.assertTrue(acquire('three', 'research_plan', 'claude:opus'))
        self.assertEqual(runtime['executions']['three']['capacity']['reservation_ids'], [])
        self.assertTrue(acquire('four', 'research_work', 'gpt-5.6-sol'))
        # No Job was ever launched under the ticket's name, so the port confirms it empty.
        self.assertTrue(slots.release('one'))
        self.assertTrue(acquire('two', 'research_work', 'claude:opus'))


if __name__ == '__main__':
    unittest.main()
