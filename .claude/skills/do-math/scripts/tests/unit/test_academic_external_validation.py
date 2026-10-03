"""정상 생산 외부 기록의 한 필드 변조, 재시도와 대조의 결과·효과를 검사한다."""
from copy import deepcopy
import unittest

from do_math import external
from do_math.http_request import check_url, check_body
from support.academic_external_cases import AcademicExternalCase, ORIGIN


class ExternalValidationTests(unittest.TestCase):
    def setUp(self):
        self.case = AcademicExternalCase()

    def test_request_shape_rejection_precedes_parsing(self):
        for request in (None, [], {}, {'method': 'PATCH', 'url': ORIGIN}, {'method': 'POST', 'url': 7}):
            with self.subTest(request=request):
                with self.assertRaisesRegex(ValueError, '^request needs HTTP method and URL$'):
                    check_url(request)
        self.assertEqual(self.case.http.requests, [])

    def test_url_and_body_return_exact_request_components(self):
        request = self.case.operation['request']
        parsed = check_url(request)
        self.assertEqual((parsed.scheme, parsed.netloc, parsed.path, parsed.query),
                         ('https', 'academic.example.test', '/submit', ''))
        self.assertEqual(check_body(request), '합성 본문')

    def test_prepare_rejects_empty_source_and_grant_refs(self):
        for grant, source in (('', 'user'), ('G', ''), (None, 'user'), ('G', 7)):
            with self.subTest(grant=grant, source=source):
                with self.assertRaisesRegex(ValueError, '^grant and source refs required$'):
                    external.prepare_operation(self.case.operation['request'], grant, source)
        self.assertEqual(self.case.saved, [])

    def test_prepare_rejects_each_invalid_scope_field(self):
        for field in ('target_id', 'purpose', 'subject', 'actor_kind'):
            for value in ('', ' ', 7):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, '^external action scope fields must be nonempty text$'):
                        external.prepare_operation(self.case.operation['request'], 'G', 'user', **{field: value})
        self.assertEqual(self.case.saved, [])

    def test_grant_scope_rejections_do_not_send_or_persist(self):
        cases = [('allowed_origins', [], 'origin outside grant'), ('allowed_methods', [], 'method outside grant'),
                 ('allowed_path_prefixes', [], 'path outside grant'),
                 ('excluded_path_prefixes', ['/submit'], 'path explicitly excluded'),
                 ('excluded_origins', [ORIGIN], 'origin explicitly excluded'),
                 ('credential_env', {'Host': 'SECRET'}, 'credential headers cannot override operation identity or routing')]
        for field, value, reason in cases:
            with self.subTest(field=field):
                case = AcademicExternalCase()
                case.grant[field] = value
                before = deepcopy(case.operation)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    case.send()
                self.assertEqual(case.operation, before)
                self.assertEqual(case.saved, [])
                self.assertEqual(case.http.requests, [])

    def test_request_binding_rejects_each_identity_component(self):
        self.assertTrue(external.request_binding_current(self.case.operation))
        for field in ('id', 'request_sha256', 'idempotency_key'):
            with self.subTest(field=field):
                operation = {**self.case.operation, field: 'changed'}
                self.assertFalse(external.request_binding_current(operation))
                with self.assertRaisesRegex(ValueError, '^request bytes or idempotency key changed$'):
                    self.case.send(operation)
        self.assertEqual(self.case.http.requests, [])
        self.assertEqual(self.case.saved, [])

    def test_non_startable_status_is_rejected_before_save(self):
        operation = {**self.case.operation, 'status': 'failed'}
        with self.assertRaisesRegex(ValueError, '^operation is not startable$'):
            self.case.send(operation)
        self.assertEqual(self.case.saved, [])
        self.assertEqual(self.case.http.requests, [])

    def test_attempt_without_bound_retry_evidence_is_rejected(self):
        unknown = self.case.unknown()
        retry = external.prepare_retry(unknown, self.case.retry_evidence(unknown), source='user', now_iso=self.case.clock.now())
        retry['retry_evidence']['evidence_ref'] = ''
        before = deepcopy((self.case.saved, self.case.http.requests))
        with self.assertRaisesRegex(ValueError, '^retry lacks request-bound evidence$'):
            self.case.send(retry)
        self.assertEqual((self.case.saved, self.case.http.requests), before)

    def test_attempt_rejects_changed_retry_kind(self):
        unknown = self.case.unknown()
        retry = external.prepare_retry(unknown, self.case.retry_evidence(unknown), source='user', now_iso=self.case.clock.now())
        retry['retry_evidence']['kind'] = 'unverified'
        before = deepcopy((self.case.saved, self.case.http.requests))
        with self.assertRaisesRegex(ValueError, '^invalid retry evidence kind$'):
            self.case.send(retry)
        self.assertEqual((self.case.saved, self.case.http.requests), before)

    def test_attempt_rechecks_idempotency_expiration_at_send(self):
        unknown = self.case.unknown()
        evidence = self.case.retry_evidence(unknown)
        retry = external.prepare_retry(unknown, evidence, source='user', now_iso=self.case.clock.now())
        retry['retry_evidence']['valid_until'] = self.case.clock.now()
        before = deepcopy((self.case.saved, self.case.http.requests))
        with self.assertRaisesRegex(ValueError, '^idempotency assurance expired$'):
            self.case.send(retry)
        self.assertEqual((self.case.saved, self.case.http.requests), before)

    def test_second_stop_check_cancels_without_transmission(self):
        checks = []
        def stop():
            checks.append(len(checks) + 1)
            return len(checks) == 2
        result = self.case.send(should_stop=stop)
        self.assertEqual(checks, [1, 2])
        self.assertEqual(result, {**self.case.operation, 'status': 'cancelled',
                                 'transmitted': False, 'transmission_phase': 'not_started'})
        self.assertEqual(self.case.saved[-1], result)
        self.assertEqual(self.case.http.requests, [])

    def test_non_bytes_transport_body_leaves_only_durable_send_marker(self):
        self.case.http.table['/submit'] = (201, 'text', None)
        with self.assertRaisesRegex(ValueError, '^transport body must be bytes$'):
            self.case.send()
        self.assertEqual(len(self.case.http.requests), 1)
        self.assertEqual([row['status'] for row in self.case.saved], ['prepared', 'prepared'])
        self.assertTrue(self.case.saved[-1]['transmitted'])
        self.assertEqual(external.recover_operation(self.case.saved[-1]),
                         {**self.case.saved[-1], 'status': 'unknown', 'handling': 'reconciliation_required'})

    def test_recovery_of_untransmitted_operation_is_a_distinct_equal_record(self):
        result = external.recover_operation(self.case.operation)
        self.assertEqual(result, self.case.operation)
        self.assertIsNot(result, self.case.operation)

    def test_prepare_retry_rejects_completed_status_or_untrusted_source(self):
        unknown = self.case.unknown()
        evidence = self.case.retry_evidence(unknown)
        for operation, source in (({**unknown, 'status': 'confirmed'}, 'user'), (unknown, 'model')):
            with self.subTest(source=source, status=operation['status']):
                before = deepcopy(operation)
                with self.assertRaisesRegex(ValueError, '^retry needs an uncertain or absent-effect operation and authorized evidence source$'):
                    external.prepare_retry(operation, evidence, source=source, now_iso=self.case.clock.now())
                self.assertEqual(operation, before)

    def test_prepare_retry_rejects_unsupported_evidence_kind(self):
        unknown = self.case.unknown()
        evidence = {**self.case.retry_evidence(unknown), 'kind': 'receipt'}
        with self.assertRaisesRegex(ValueError, '^unsupported retry evidence$'):
            external.prepare_retry(unknown, evidence, source='user', now_iso=self.case.clock.now())
        self.assertEqual(unknown['status'], 'unknown')

    def test_effect_absence_retry_requires_established_absence(self):
        unknown = self.case.unknown()
        evidence = {**self.case.retry_evidence(unknown), 'kind': 'effect_absent'}
        with self.assertRaisesRegex(ValueError, '^effect absence not established$'):
            external.prepare_retry(unknown, evidence, source='user', now_iso=self.case.clock.now())
        failed = external.reconcile_operation(unknown, self.case.evidence(unknown, 'effect_absent'),
                                              'failed', source='user', effect_absent=True)
        result = external.prepare_retry(failed, evidence, source='user', now_iso=self.case.clock.now())
        self.assertEqual(result, {**failed, 'status': 'prepared', 'transmitted': False,
            'transmission_phase': 'not_started', 'retry_evidence': {**evidence, 'source': 'user'}, 'previous_outcome': 'failed'})
        self.assertEqual(len(self.case.http.requests), 1)

    def test_reconciliation_rejects_each_unbound_evidence_field(self):
        unknown = self.case.unknown()
        for field in ('operation_id', 'request_sha256', 'idempotency_key', 'evidence_ref', 'observed_at'):
            with self.subTest(field=field):
                evidence = {**self.case.evidence(unknown), field: ''}
                before = deepcopy(unknown)
                with self.assertRaisesRegex(ValueError, '^reconciliation evidence must bind the exact external operation$'):
                    external.reconcile_operation(unknown, evidence, 'confirmed', source='user', succeeded=True)
                self.assertEqual(unknown, before)
        self.assertEqual(len(self.case.http.requests), 1)

    def test_reconciliation_rejects_fact_different_from_outcome(self):
        unknown = self.case.unknown()
        with self.assertRaisesRegex(ValueError, '^evidence fact differs from asserted outcome$'):
            external.reconcile_operation(unknown, self.case.evidence(unknown, 'effect_absent'),
                                         'confirmed', source='user', succeeded=True)
        self.assertEqual(unknown['status'], 'unknown')

    def test_reconciliation_requires_explicit_success_or_absence_boolean(self):
        unknown = self.case.unknown()
        for result, fact in (('confirmed', 'succeeded'), ('failed', 'effect_absent')):
            with self.subTest(result=result):
                with self.assertRaisesRegex(ValueError, '^reconciliation needs evidence for the asserted external-effect fact$'):
                    external.reconcile_operation(unknown, self.case.evidence(unknown, fact), result, source='user')
                self.assertEqual(unknown['status'], 'unknown')

    def test_reconciliation_cancellation_preserves_evidence_and_original(self):
        unknown = self.case.unknown()
        before = deepcopy(unknown)
        evidence = self.case.evidence(unknown, 'not_transmitted')
        result = external.reconcile_operation(unknown, evidence, 'cancelled', source='user')
        self.assertEqual(result, {**unknown, 'status': 'cancelled', 'succeeded': None, 'effect_absent': None,
            'handling': 'reconciled', 'external_id': None, 'reconciliation': {'source': 'user', 'evidence': evidence,
            'succeeded': None, 'effect_absent': None, 'idempotency_evidence': None}})
        self.assertEqual(unknown, before)
        self.assertEqual(len(self.case.http.requests), 1)
