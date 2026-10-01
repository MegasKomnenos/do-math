"""The send steps of one grant-bounded external HTTP operation (``external``, layer 2), moved from ``test_external``.

The legacy tests sent through the real urllib transport to a loopback server
(POST answered 201 ``ok``, GET redirected to another origin). Here the
operation sends through the HTTP port's fake (``support.fakes.http``): it runs
the product's request checks, answers from a table by URL path, refuses a
redirect as the real port does, and records every request with its headers.
The two implementations answer alike by the port contract
(``contracts``/``boundary.test_port_http``); the bytes urllib puts on the wire
are ``boundary.test_academic_http_bytes``. Time comes from the clock port fake.
"""
import os
import unittest
from unittest.mock import patch

from do_math.canonical import exact_content_hash
from do_math.external import (execute_operation, idempotency_key, prepare_operation, prepare_retry, recover_operation,
                              reconcile_operation, validate_operation)
from support.fakes.clock import FakeClock
from support.fakes.http import make_fake

ORIGIN = 'http://127.0.0.1:8123'
NOW = '2026-01-01T00:00:00Z'
ACCEPTED = (201, b'ok', None)  # the legacy server's answer to a POST
REDIRECT = (302, b'', 'http://evil/')  # its answer to a GET
E_ACUTE = '\N{LATIN SMALL LETTER E WITH ACUTE}'


def timeout(*_):
    raise TimeoutError()


class ExternalSendTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.grant = {'id': 'G', 'status': 'active', 'expires_at': None, 'allowed_origins': [ORIGIN],
                      'allowed_methods': ['POST', 'GET'], 'allowed_path_prefixes': ['/ok'],
                      'credential_env': {'X-Key': 'EXT_TEST_KEY'}}
        self.enterContext(patch.dict(os.environ, {'EXT_TEST_KEY': 'secret'}))

    def post(self, body='', **options):
        request = {'method': 'POST', 'url': ORIGIN + '/ok'}
        if body is not None:
            request['body'] = body
        return prepare_operation(request, 'G', 'S', **options)

    def test_method_body_contract_matches_preparation_validation_and_http_bytes(self):
        """Preparation and validation apply one method/body rule; a legacy GET or DELETE record with a body is refused
        before transport. The bytes urllib sends for each accepted pair: ``boundary.test_academic_http_bytes``."""
        from support.entry import entry
        _entry = entry()
        grant = {**self.grant, 'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'], 'credential_env': {}}
        for method in ('GET', 'POST', 'PUT', 'DELETE'):
            for body in (None, '', E_ACUTE, 7):
                with self.subTest(method=method, body=body):
                    request = {'method': method, 'url': ORIGIN + '/ok'}
                    if body is not None:
                        request['body'] = body
                    if body == 7:
                        with self.assertRaisesRegex(ValueError, '^body must be text$'):
                            prepare_operation(request, 'G', 'S')
                        continue
                    if method in ('GET', 'DELETE') and body == E_ACUTE:
                        with self.assertRaisesRegex(ValueError, '^GET and DELETE cannot carry a nonempty body$'):
                            prepare_operation(request, 'G', 'S')
                        continue
                    operation = prepare_operation(request, 'G', 'S')
                    self.assertEqual(operation['request'], {'method': method, 'url': ORIGIN + '/ok', 'body': body or ''})
                    self.assertIsNone(validate_operation(operation, grant, NOW))
                    if method in ('GET', 'DELETE'):
                        old = {**operation, 'request': {**operation['request'], 'body': 'legacy'}}
                        old['request_sha256'] = exact_content_hash(old['request'])
                        old['idempotency_key'] = idempotency_key(old['id'], old['request_sha256'])
                        calls = []
                        with self.assertRaisesRegex(ValueError, '^GET and DELETE cannot carry a nonempty body$'):
                            execute_operation(old, grant, persist=lambda _: True, clock=self.clock,
                                              transport=lambda *_: calls.append(1), environment=dict(os.environ))
                        self.assertEqual(calls, [])

    def test_persist_before_send_confirm_and_redact(self):
        from support.entry import entry
        _entry = entry()
        http = make_fake({'/ok': ACCEPTED})
        calls = []
        out = execute_operation(self.post('x'), self.grant, persist=lambda x: calls.append(x) or True, clock=self.clock,
                                transport=http.request, environment=dict(os.environ))
        self.assertEqual([x['status'] for x in calls], ['prepared', 'prepared', 'confirmed'])
        self.assertTrue(calls[1]['transmitted'])  # the send marker is stored before the response
        self.assertEqual(out['status'], 'confirmed')
        self.assertNotIn('secret', str(out))
        # The credential reached the port as a header only.
        self.assertEqual([header for _, header, _ in http.requests], [[('X-Key', 'secret')]])

    def test_unknown_retry_reconcile_and_scope(self):
        from support.entry import entry
        _entry = entry()
        op = self.post('')
        unknown = execute_operation(op, self.grant, persist=lambda x: True, clock=self.clock, transport=timeout, environment=dict(os.environ))
        self.assertEqual(unknown['status'], 'unknown')
        http = make_fake({'/ok': ACCEPTED})
        with self.assertRaisesRegex(ValueError, '^unknown operation requires reconciliation$'):
            execute_operation(unknown, self.grant, persist=lambda x: True, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(http.requests, [])
        with self.assertRaisesRegex(ValueError, '^invalid reconciliation$'):
            reconcile_operation(unknown, 'receipt', 'confirmed', source='adapter')
        evidence = {'operation_id': unknown['id'], 'request_sha256': unknown['request_sha256'],
                    'idempotency_key': unknown['idempotency_key'], 'fact': 'succeeded', 'evidence_ref': 'remote-receipt',
                    'observed_at': '2026-09-20T00:00:00Z'}
        self.assertEqual(reconcile_operation(unknown, evidence, 'confirmed', source='adapter', succeeded=True)['status'],
                         'confirmed')
        with self.assertRaisesRegex(ValueError, '^grant expired$'):
            validate_operation(op, {**self.grant, 'expires_at': '2000-01-01T00:00:00Z'}, NOW)
        with self.assertRaisesRegex(ValueError, '^unsafe external URL$'):
            prepare_operation({'method': 'GET', 'url': ORIGIN.replace('http://', 'http://x@') + '/ok'}, 'G', 'S')
        with self.assertRaisesRegex(ValueError, '^path traversal forbidden$'):
            prepare_operation({'method': 'GET', 'url': ORIGIN + '/ok/%2e%2e/outside'}, 'G', 'S')

    def test_redirect_and_stale_ledger(self):
        from support.entry import entry
        _entry = entry()
        op = prepare_operation({'method': 'GET', 'url': ORIGIN + '/ok', 'body': ''}, 'G', 'S')
        http = make_fake({'/ok': REDIRECT})
        with self.assertRaisesRegex(ValueError, '^operation ledger is stale; recover recorded transmission before retry$'):
            execute_operation(op, self.grant, persist=lambda _: False, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(http.requests, [])  # the refused first save stops before any send
        # The port refuses the redirect; the refusal is not taken for an unknown outcome.
        with self.assertRaisesRegex(ValueError, '^redirect forbidden$'):
            execute_operation(op, self.grant, persist=lambda _: True, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(len(http.requests), 1)

    def test_tampered_key_and_terminal_persist(self):
        from support.entry import entry
        _entry = entry()
        op = self.post('')
        op['idempotency_key'] = 'bad'
        with self.assertRaisesRegex(ValueError, '^request bytes or idempotency key changed$'):
            validate_operation(op, self.grant, NOW)
        calls = []
        os.environ.pop('EXT_TEST_KEY')  # setUp's patch.dict restores the environment
        out = execute_operation(self.post(''), self.grant, persist=lambda x: calls.append(x) or True, clock=self.clock,
                                transport=timeout, environment=dict(os.environ))
        self.assertEqual(out['status'], 'prepared')
        self.assertFalse(out['transmitted'])
        self.assertEqual(calls[-1]['waiting_reason']['kind'], 'credential_unavailable')

    def test_stop_before_send_is_explicitly_untransmitted(self):
        from support.entry import entry
        _entry = entry()
        http = make_fake({'/ok': ACCEPTED})
        out = execute_operation(self.post(''), self.grant, persist=lambda _: True, should_stop=lambda: True,
                                clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual((out['status'], out['transmitted']), ('cancelled', False))
        self.assertEqual(http.requests, [])

    def test_terminal_persist_failure_is_not_returned_as_committed_success(self):
        from support.entry import entry
        _entry = entry()
        op = self.post(None)
        calls = []

        def persist(record):
            if record['status'] == 'confirmed':
                return False
            calls.append(record)
            return True
        http = make_fake({'/ok': ACCEPTED})
        with self.assertRaisesRegex(ValueError, '^operation ledger is stale; recover recorded transmission before retry$'):
            execute_operation(op, self.grant, persist=persist, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(len(http.requests), 1)  # it was sent; only its confirmation was not stored
        self.assertEqual((calls[-1]['status'], calls[-1]['transmitted']), ('prepared', True))
        recovered = recover_operation(calls[-1])
        self.assertEqual(recovered['status'], 'unknown')
        with self.assertRaisesRegex(ValueError, '^unknown operation requires reconciliation$'):
            execute_operation(recovered, self.grant, persist=lambda _: True, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(len(http.requests), 1)

    def test_fresh_revocation_before_send_prevents_transport(self):
        from support.entry import entry
        _entry = entry()
        op = self.post(None)
        current = dict(self.grant)
        sent = []

        def persist(record):
            current['status'] = 'revoked'
            return True
        with self.assertRaisesRegex(ValueError, '^grant is inactive$'):
            execute_operation(op, self.grant, persist=persist, current_grant=lambda _: current, clock=self.clock,
                              transport=lambda *_: sent.append(1), environment=dict(os.environ))
        self.assertEqual(sent, [])

    def test_retries_need_exact_nonexpired_idempotency_evidence(self):
        from support.entry import entry
        _entry = entry()
        op = execute_operation(self.post(None), self.grant, persist=lambda _: True, clock=self.clock, transport=timeout, environment=dict(os.environ))
        evidence = {'kind': 'verified_idempotency', 'request_sha256': op['request_sha256'],
                    'idempotency_key': op['idempotency_key'], 'valid_until': '2099-01-01T00:00:00Z',
                    'evidence_ref': 'verified-service-contract'}
        with self.assertRaisesRegex(ValueError, '^retry evidence must bind exact request and key$'):
            prepare_retry(op, {**evidence, 'request_sha256': 'wrong'}, source='adapter', now_iso=NOW)
        with self.assertRaisesRegex(ValueError, '^idempotency evidence expired$'):
            prepare_retry(op, {**evidence, 'valid_until': '2000-01-01T00:00:00Z'}, source='adapter', now_iso=NOW)
        retry = prepare_retry(op, evidence, source='adapter', now_iso=NOW)
        http = make_fake({'/ok': ACCEPTED})
        self.assertEqual(execute_operation(retry, self.grant, persist=lambda _: True, clock=self.clock,
                                           transport=http.request, environment=dict(os.environ))['status'], 'confirmed')
        self.assertEqual(len(http.requests), 1)

    def test_credential_resume_loopback_clears_wait_and_preserves_identity(self):
        from support.entry import entry
        _entry = entry()
        grant = {**self.grant, 'kind': 'http', 'reuse': 'reusable'}
        op = prepare_operation({'method': 'POST', 'url': ORIGIN + '/ok', 'body': 'credential-resume'}, 'G', 'S', 'OP-resume')
        runtime = {'external_operations': {}, 'executions': {}}
        http = make_fake({'/ok': ACCEPTED})

        def persist(row):
            runtime['external_operations'][row['id']] = row
            return True
        with patch.dict(os.environ, {}, clear=True):
            waiting = execute_operation(op, grant, persist=persist, runtime=runtime, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(waiting['waiting_reason']['kind'], 'credential_unavailable')
        self.assertEqual(http.requests, [])
        result = execute_operation(waiting, grant, persist=persist, runtime=runtime, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(result['status'], 'confirmed')
        self.assertNotIn('waiting_reason', result)
        for key in ('id', 'request_sha256', 'idempotency_key'):
            self.assertEqual(result[key], op[key])
        with self.assertRaisesRegex(ValueError, '^recorded transmission requires recovery before another send$'):
            execute_operation(result, grant, persist=persist, runtime=runtime, clock=self.clock, transport=http.request, environment=dict(os.environ))
        self.assertEqual(len(http.requests), 1)


if __name__ == '__main__':
    unittest.main()
