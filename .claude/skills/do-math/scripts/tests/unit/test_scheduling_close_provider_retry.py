"""동일 공급자 대기의 후퇴 금지와 호스트 단위의 모델 슬롯 집계 제외."""
from copy import deepcopy
import unittest

from support.provider_inputs import host_capacity_fixture
from support.scheduling_hosts import admit, host_slots


class RetryAccountingTests(unittest.TestCase):
    def test_waiting_provider_cannot_shorten_its_existing_retry(self):
        instance, selected, _ = host_capacity_fixture()
        runtime = {'executions': {}, 'reservations': {}}
        book = host_slots(runtime, instance)
        profile = selected['research_work']
        accepted, execution = admit(book, 'EX-held', profile)
        self.assertTrue(accepted)
        provider = execution['capacity']['provider']
        failure = {'status': 'failed', 'error_kind': 'provider_limit', 'failure': {
            'kind': 'provider_limit', 'provider': provider, 'retry_at': None,
            'limit_windows': [], 'evidence_ref': 'synthetic-provider-limit.json'}}
        book.provider_result_from_run('EX-held', failure, {
            'provider_retry_initial_seconds': 10, 'provider_retry_max_seconds': 100}, current_time=100)
        old = deepcopy(runtime['provider_waits']['PW-' + provider])
        book.provider_result_from_run('EX-held', failure, {
            'provider_retry_initial_seconds': 1, 'provider_retry_max_seconds': 100}, current_time=101)
        row = runtime['provider_waits']['PW-' + provider]
        self.assertEqual((row['state'], row['retry_at'], row['attempts'], row['generation']),
                         ('waiting', old['retry_at'], 1, old['generation'] + 1))
        self.assertEqual(row['retry_at'], 110)
        self.assertEqual(row['probe_owner'], None)

    def test_host_units_do_not_inflate_model_execution_counts(self):
        instance, selected, _ = host_capacity_fixture()
        runtime = {'executions': {}, 'reservations': {}}
        book = host_slots(runtime, instance)
        profile = selected['research_work']
        self.assertTrue(admit(book, 'EX-one', profile)[0])
        self.assertEqual({r['unit'] for r in runtime['reservations'].values()},
                         {'execution', 'jobs', 'memory_bytes', 'cpu_rate_basis_points'})
        before = deepcopy(runtime)
        self.assertEqual(book.snapshot()[profile['ai']['model']], {
            'limit': instance['capacity_constraints'][profile['ai']['capacity_refs'][0]]['work_slots'],
            'used': 1, 'execution_ids': ['EX-one'],
            'available': instance['capacity_constraints'][profile['ai']['capacity_refs'][0]]['work_slots'] - 1})
        self.assertEqual(runtime, before)
