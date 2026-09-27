"""External operations under grants: preparation, transmission state, reconciliation and scope metadata.

No request leaves the process; transports and responses are synthetic.
"""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import governance as gov
from do_math.external import execute_operation, prepare_operation
from do_math.governance import apply_decision
from research_fixtures import governance_start


class ExternalOperationTests(unittest.TestCase):
    def test_unknown_with_sent_marker_cannot_silently_retransmit(self):
        from do_math.external import prepare_operation, execute_operation
        op = prepare_operation({"method": "POST", "url": "https://example.test/p"}, "G", "S")
        op.update(transmitted=True, transmission_phase="recorded")
        grant = {"id": "G", "status": "active", "allowed_origins": ["https://example.test"], "allowed_methods": ["POST"], "allowed_path_prefixes": ["/"]}
        calls = []
        with self.assertRaises(ValueError): execute_operation(op, grant, persist=lambda _:True, transport=lambda *_: calls.append(1) or {"http_status":200,"body":b"ok"})
        self.assertEqual(calls, [])

    def test_reconciliation_cannot_assert_success_from_unbound_text(self):
        from do_math.external import reconcile_operation
        op=prepare_operation({"method":"POST","url":"https://example.test/p"},"G","S");op["status"]="unknown"
        with self.assertRaises(ValueError): reconcile_operation(op,"a receipt","confirmed",source="user",succeeded=True)

    def _grant(self, **extra):
        value = {
            "id": "G", "status": "active", "expires_at": None,
            "allowed_origins": ["https://example.test"],
            "allowed_methods": ["POST"], "allowed_path_prefixes": ["/submit"],
            "credential_env": {},
        }
        value.update(extra)
        return value

    def _operation(self):
        return prepare_operation(
            {"method": "POST", "url": "https://example.test/submit", "body": "proof"},
            "G", "source",
        )

    def test_non_2xx_is_failed_only_when_effect_absence_is_evidenced(self):
        operation = self._operation()
        result = execute_operation(
            operation, self._grant(), persist=lambda _: True,
            transport=lambda *_: {"http_status": 409, "body": b"rejected", "effect_absent": True},
        )
        self.assertEqual(result["status"], "failed")
        self.assertIs(result["succeeded"], False)
        self.assertTrue(result["effect_absent"])

    def test_missing_credential_preserves_prepared_operation_and_wait_reason(self):
        operation = self._operation()
        previous = os.environ.pop("DO_MATH_TEST_MISSING_SECRET", None)
        self.addCleanup(lambda: os.environ.__setitem__("DO_MATH_TEST_MISSING_SECRET", previous) if previous else None)
        result = execute_operation(
            operation, self._grant(credential_env={"Authorization": "DO_MATH_TEST_MISSING_SECRET"}),
            persist=lambda _: True,
        )
        self.assertEqual(result["status"], "prepared")
        self.assertFalse(result["transmitted"])
        self.assertEqual(result["waiting_reason"]["kind"], "credential_unavailable")

    def test_revocation_cancels_only_untransmitted_prepared_effects(self):
        instance = governance_start({'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize the HTTP grant, then revoke it.', origin='user')}})
        instance, _, _ = apply_decision(instance, {}, {'kind': 'grant', 'grant': {
            'id': 'G', 'kind': 'http', 'reuse': 'reusable', 'allowed_origins': ['https://example.test'],
            'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/submit'], 'credential_env': {}}}, source_ref='user')
        operation = self._operation()
        runtime = {"status": "ready", "tasks": {}, "queue": [], "executions": {}, "external_operations": {operation["id"]: operation}}
        _, updated, _ = apply_decision(instance, runtime, {"kind": "revoke", "grant_id": "G", "decision_id": "D"}, source_ref="user")
        self.assertEqual(updated["external_operations"][operation["id"]]["status"], "cancelled")
        self.assertFalse(updated["external_operations"][operation["id"]]["transmitted"])


class ExternalScopeConsumerTests(unittest.TestCase):
    def test_external_scope_metadata_is_checked_in_actual_send_and_once_ledger(self):
        from do_math.external import prepare_operation, execute_operation
        grant = {'id': 'G', 'kind': 'http', 'status': 'active', 'reuse': 'once',
            'included_targets': ['T'], 'purposes': ['publish'], 'subjects': ['external_operation'],
            'execution_kinds': ['machine'],
            'allowed_origins': ['https://example.test'], 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/']}
        op = prepare_operation({'method': 'POST', 'url': 'https://example.test/p'}, 'G', 'S',
            target_id='T', purpose='publish', subject='external_operation', actor_kind='machine')
        calls = []
        transport = lambda *args: calls.append(args) or {'http_status': 200, 'body': b'ok'}
        result = execute_operation(op, grant, persist=lambda row: True, transport=transport, runtime={})
        self.assertEqual(result['status'], 'confirmed')
        bad = deepcopy(op); bad['purpose'] = 'unapproved'
        with self.assertRaises(ValueError): execute_operation(bad, grant, persist=lambda row: True, transport=transport, runtime={})
        with self.assertRaises(ValueError): execute_operation(op, grant, persist=lambda row: True, transport=transport,
            runtime={'external_operations': {'USED': {**result, 'id': 'USED'}}})
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
