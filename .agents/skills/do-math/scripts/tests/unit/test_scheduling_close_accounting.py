"""첫 빈 분기의 현행·과거 용량과 공급자 재관찰 입력. 실제 예약 계산을 쓴다."""
from copy import deepcopy
import unittest

from do_math import execution_profiles as profiles
from do_math.launch import mark_returned
from support.entry import entry
from support.provider_inputs import PROFILE_CONFIG, host_capacity_fixture
from support.scheduling_hosts import admit, host_slots


def allocator():
    instance = profiles.build_profiles(PROFILE_CONFIG, host=entry().ports.host)
    profile = instance['execution_profiles'][instance['role_profile_refs']['research_work'][-1]['id']]
    runtime = {'executions': {}, 'reservations': {}}
    return instance, profile, runtime, host_slots(runtime, instance)


class AccountingBranchTests(unittest.TestCase):
    def test_sealed_profile_with_other_approved_scope_is_rejected_before_reservation(self):
        instance, selected, constraint = host_capacity_fixture()
        profile = deepcopy(selected['research_work'])
        foreign = profiles.host_constraint(host_id='different-host',
            limits={'jobs': constraint['max_jobs'], 'memory_bytes': constraint['memory_bytes'],
                    'cpu_rate_basis_points': constraint['cpu_rate_basis_points']},
            control_reserve=constraint['control_reserve'], authority_refs=constraint['authority_refs'])
        instance['capacity_constraints'][foreign['id']] = foreign
        instance['host_capacity_ref'] = foreign['id']
        profile['host_capacity_refs'] = [foreign['id']]
        profile['host_resources']['constraint_id'] = foreign['id']
        profile = profiles.seal_profile(profile)
        instance['execution_profiles'][profile['id']] = profile
        runtime = {'executions': {}, 'reservations': {}}
        book = host_slots(runtime, instance)
        with self.assertRaisesRegex(ValueError, '^profile and approved host scope differ$'):
            book.admission_check(profile)
        self.assertEqual(runtime, {'executions': {}, 'reservations': {}})

    def test_missing_current_model_accounting_refuses_pinned_profile_without_writes(self):
        instance, profile, runtime, book = allocator()
        model = profile['ai']['model']
        instance['role_profile_refs'] = {role: [ref for ref in refs
            if instance['execution_profiles'][ref['id']].get('ai', {}).get('model') != model]
            for role, refs in instance['role_profile_refs'].items()}
        before = deepcopy(runtime)
        self.assertEqual(book.admission_check(profile), {'allowed': False, 'wait': {
            'kind': 'capacity', 'model': model, 'profile_ref': profiles.profile_ref(profile),
            'reason': 'pinned profile has no current adopted accounting constraint', 'next_owner': 'user'}})
        self.assertEqual(runtime, before)

    def test_snapshot_keeps_old_model_reservation_with_zero_current_limit(self):
        instance, profile, runtime, book = allocator()
        self.assertTrue(admit(book, 'EX-old-model', profile)[0])
        model = profile['ai']['model']
        instance['role_profile_refs'] = {role: [ref for ref in refs
            if instance['execution_profiles'][ref['id']].get('ai', {}).get('model') != model]
            for role, refs in instance['role_profile_refs'].items()}
        before = deepcopy(runtime)
        self.assertEqual(book.snapshot()[model], {'limit': 0, 'used': 1,
            'execution_ids': ['EX-old-model'], 'available': 0})
        self.assertEqual(runtime, before)

    def test_provider_probe_without_response_increments_retry_and_release_cannot_open_gate(self):
        instance, profile, runtime, book = allocator()
        provider = profile['ai']['provider']
        config = {'provider_retry_initial_seconds': 10, 'provider_retry_max_seconds': 100}
        self.assertTrue(admit(book, 'EX-limit', profile)[0])
        failure = {'kind': 'provider_limit', 'provider': provider, 'retry_at': None,
                   'evidence_ref': 'synthetic-limit.json', 'limit_windows': []}
        book.provider_result_from_run('EX-limit', {'status': 'failed', 'error_kind': 'provider_limit',
                                                'failure': failure}, config, current_time=100)
        mark_returned(runtime['executions']['EX-limit']['launch_ticket'], {'launch_not_created': True})
        self.assertTrue(book.release('EX-limit'))
        row = runtime['provider_waits']['PW-' + provider]
        self.assertEqual((row['state'], row['attempts'], row['retry_at']), ('waiting', 1, 110))
        execution = {'id': 'EX-probe', 'role': profile['role'], 'status': 'queued'}
        self.assertTrue(book.acquire('EX-probe', profile=profile, execution=execution, current_time=110))
        self.assertEqual((row['state'], row['probe_owner'], row['probe_started_at']), ('checking', 'EX-probe', 110))
        book.provider_result_from_run('EX-probe', {'status': 'failed', 'error_kind': 'execution_failure'}, config, current_time=111)
        self.assertEqual((row['state'], row['attempts'], row['retry_at'], row['probe_owner']), ('waiting', 2, 131, None))
        mark_returned(execution['launch_ticket'], {'launch_not_created': True})
        self.assertTrue(book.release('EX-probe'))
        self.assertEqual(row['state'], 'waiting')

    def test_release_of_unanswered_checking_probe_returns_to_waiting(self):
        instance, profile, runtime, book = allocator()
        provider = profile['ai']['provider']
        config = {'provider_retry_initial_seconds': 10, 'provider_retry_max_seconds': 100}
        self.assertTrue(admit(book, 'EX-first', profile)[0])
        book.provider_result_from_run('EX-first', {'status': 'failed', 'error_kind': 'provider_limit',
            'failure': {'kind': 'provider_limit', 'provider': provider, 'retry_at': None,
                        'limit_windows': [], 'evidence_ref': 'synthetic-limit.json'}}, config, current_time=100)
        mark_returned(runtime['executions']['EX-first']['launch_ticket'], {'launch_not_created': True})
        self.assertTrue(book.release('EX-first'))
        execution = {'id': 'EX-retry', 'role': profile['role'], 'status': 'queued'}
        self.assertTrue(book.acquire('EX-retry', profile=profile, execution=execution, current_time=110))
        mark_returned(execution['launch_ticket'], {'launch_not_created': True})
        self.assertTrue(book.release('EX-retry'))
        row = runtime['provider_waits']['PW-' + provider]
        self.assertEqual((row['state'], row['probe_owner'], row['probe_started_at'], row['retry_at']),
                         ('waiting', None, None, 110))

    def test_missing_ticket_keeps_unknown_capacity_and_every_reservation_held(self):
        instance, profile, runtime, book = allocator()
        accepted, execution = admit(book, 'EX-no-ticket', profile)
        self.assertTrue(accepted)
        del execution['launch_ticket']
        before = deepcopy(runtime)
        self.assertFalse(book.release('EX-no-ticket'))
        self.assertEqual(runtime, before)
        self.assertEqual(execution['capacity']['local_termination'], 'unknown')
