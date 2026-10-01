"""External operations under grants: preparation, transmission state, reconciliation and scope metadata
(``external``, layer 2; the grant revocation in ``governance``), moved from ``test_external_operations``.

No request leaves the process: the HTTP port is a response callable the test
passes as ``transport``, and time comes from the clock port fake.
"""
from copy import deepcopy
import os
import unittest
from unittest.mock import patch

from do_math import governance as gov
from do_math.external import execute_operation, prepare_operation, reconcile_operation
from support.state_builders import governance_start
from support.fakes.clock import FakeClock


def _grant(**extra):
    return {"id": "G", "status": "active", "expires_at": None, "allowed_origins": ["https://example.test"],
            "allowed_methods": ["POST"], "allowed_path_prefixes": ["/submit"], "credential_env": {}, **extra}


def _operation():
    return prepare_operation({"method": "POST", "url": "https://example.test/submit", "body": "proof"}, "G", "source")


class ExternalOperationTests(unittest.TestCase):
    def test_unknown_with_sent_marker_cannot_silently_retransmit(self):
        """A recorded send marker (status still ``prepared``) refuses another send before any transport."""
        from support.entry import entry
        _entry = entry()
        op = prepare_operation({"method": "POST", "url": "https://example.test/p"}, "G", "S")
        op.update(transmitted=True, transmission_phase="recorded")
        grant = {"id": "G", "status": "active", "allowed_origins": ["https://example.test"], "allowed_methods": ["POST"],
                 "allowed_path_prefixes": ["/"]}
        calls = []
        with self.assertRaisesRegex(ValueError, "^recorded transmission requires recovery before another send$"):
            execute_operation(op, grant, persist=lambda _: True, clock=FakeClock(),
                              transport=lambda *_: calls.append(1) or {"http_status": 200, "body": b"ok"}, environment=dict(os.environ))
        self.assertEqual(calls, [])

    def test_reconciliation_cannot_assert_success_from_unbound_text(self):
        op = prepare_operation({"method": "POST", "url": "https://example.test/p"}, "G", "S")
        op["status"] = "unknown"
        with self.assertRaisesRegex(ValueError, "^invalid reconciliation$"):
            reconcile_operation(op, "a receipt", "confirmed", source="user", succeeded=True)

    def test_non_2xx_is_failed_only_when_effect_absence_is_evidenced(self):
        from support.entry import entry
        _entry = entry()
        clock = FakeClock()
        result = execute_operation(_operation(), _grant(), persist=lambda _: True, clock=clock,
                                   transport=lambda *_: {"http_status": 409, "body": b"rejected", "effect_absent": True}, environment=dict(os.environ))
        self.assertEqual(result["status"], "failed")
        self.assertIs(result["succeeded"], False)
        self.assertTrue(result["effect_absent"])
        # Without the evidence the same response leaves the outcome unknown.
        unproven = execute_operation(_operation(), _grant(), persist=lambda _: True, clock=clock,
                                     transport=lambda *_: {"http_status": 409, "body": b"rejected"}, environment=dict(os.environ))
        self.assertEqual((unproven["status"], unproven["succeeded"], unproven["error"]),
                         ("unknown", None, "non-success response does not establish effect absence"))

    def test_missing_credential_preserves_prepared_operation_and_wait_reason(self):
        from support.entry import entry
        _entry = entry()
        from support.entry import entry
        _entry = entry()
        with patch.dict(os.environ):
            os.environ.pop("DO_MATH_TEST_MISSING_SECRET", None)
            result = execute_operation(_operation(), _grant(credential_env={"Authorization": "DO_MATH_TEST_MISSING_SECRET"}),
                                       persist=lambda _: True, clock=FakeClock(), environment=dict(os.environ), transport=_entry.ports.http.request)
        self.assertEqual(result["status"], "prepared")
        self.assertFalse(result["transmitted"])
        self.assertEqual(result["waiting_reason"]["kind"], "credential_unavailable")

    def test_revocation_cancels_only_untransmitted_prepared_effects(self):
        clock = FakeClock()
        instance = governance_start({'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize the HTTP grant, then revoke it.', origin='user')}})
        instance, _, _ = gov.apply_decision(instance, {}, {'kind': 'grant', 'grant': {
            'id': 'G', 'kind': 'http', 'reuse': 'reusable', 'allowed_origins': ['https://example.test'],
            'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/submit'], 'credential_env': {}}},
            source_ref='user', clock=clock)
        operation = _operation()
        # A second operation whose send marker was recorded: revocation cannot prove it was not sent.
        sent = {**prepare_operation({"method": "POST", "url": "https://example.test/submit", "body": "sent"}, "G", "source"),
                "transmitted": True, "transmission_phase": "recorded"}
        runtime = {"status": "ready", "tasks": {}, "queue": [], "executions": {},
                   "external_operations": {operation["id"]: operation, sent["id"]: sent}}
        _, updated, _ = gov.apply_decision(instance, runtime, {"kind": "revoke", "grant_id": "G", "decision_id": "D"},
                                           source_ref="user", clock=clock)
        self.assertEqual(updated["external_operations"][operation["id"]]["status"], "cancelled")
        self.assertFalse(updated["external_operations"][operation["id"]]["transmitted"])
        self.assertEqual((updated["external_operations"][sent["id"]]["status"],
                          updated["external_operations"][sent["id"]]["handling"]), ("unknown", "reconciliation_required"))


class ExternalScopeConsumerTests(unittest.TestCase):
    def test_external_scope_metadata_is_checked_in_actual_send_and_once_ledger(self):
        from support.entry import entry
        _entry = entry()
        grant = {'id': 'G', 'kind': 'http', 'status': 'active', 'reuse': 'once',
                 'included_targets': ['T'], 'purposes': ['publish'], 'subjects': ['external_operation'],
                 'execution_kinds': ['machine'],
                 'allowed_origins': ['https://example.test'], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/']}
        op = prepare_operation({'method': 'POST', 'url': 'https://example.test/p'}, 'G', 'S',
                               target_id='T', purpose='publish', subject='external_operation', actor_kind='machine')
        calls = []

        def transport(*args):
            calls.append(args)
            return {'http_status': 200, 'body': b'ok'}
        clock = FakeClock()
        result = execute_operation(op, grant, persist=lambda row: True, transport=transport, runtime={}, clock=clock, environment=dict(os.environ))
        self.assertEqual(result['status'], 'confirmed')
        bad = deepcopy(op)
        bad['purpose'] = 'unapproved'
        with self.assertRaisesRegex(ValueError, '^purpose outside grant$'):
            execute_operation(bad, grant, persist=lambda row: True, transport=transport, runtime={}, clock=clock, environment=dict(os.environ))
        with self.assertRaisesRegex(ValueError, '^one-case grant already reserved or consumed$'):
            execute_operation(op, grant, persist=lambda row: True, transport=transport, clock=clock,
                              runtime={'external_operations': {'USED': {**result, 'id': 'USED'}}}, environment=dict(os.environ))
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
