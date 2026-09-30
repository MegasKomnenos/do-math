"""Governance records and grants (``governance``, layer 2): the charter, policies, context, audits and authority.

The records come from ``record_fixtures`` (built by the product's own
``initialize_governance`` and ``apply_decision``); every test calls the product's
governance functions on them directly. A rejection is pinned to its reason:
the product message, or the ``rejected`` reason ``authorize`` returns.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from do_math import governance as gov
from do_math.canonical import exact_content_hash
from do_math.governance import apply_decision, authorize
from record_fixtures import domain_governance
from research_fixtures import charter, governance_start

SKILL = Path(__file__).resolve().parents[3]


class DomainGovernanceTests(unittest.TestCase):
    def test_initialized_charter_is_single_authority_and_binds_approved_original(self):
        i = domain_governance()
        self.assertNotIn("goal", i)
        self.assertNotIn("policies", i)
        self.assertEqual(gov.governance_view(i)["goal"], "Prove P")
        self.assertEqual(i["governance"]["CH1"]["approval_ref"], "D")
        changed = deepcopy(i["governance_sources"]["S"]); changed["text"] += "!"
        with self.assertRaisesRegex(ValueError, "^immutable source bytes or revision changed$"):
            gov.initialize_governance(governance_start({"id": "I"}), changed, i["decisions"]["D"], [charter()])
        # A correctly preserved changed original is still not the one the approval D binds.
        preserved = gov.preserve_source("S", changed["text"], origin="user")
        with self.assertRaisesRegex(ValueError, "^initialization requires actual user approval of the immutable input$"):
            gov.initialize_governance(governance_start({"id": "I"}), preserved, i["decisions"]["D"], [charter()])

    def test_policy_coexists_and_only_explicit_supersession_retires_old_rule(self):
        i = domain_governance(); runtime = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        for identifier, replaces in (("P1", []), ("P2", []), ("P3", ["P1"])):
            record = {"id": identifier, "kind": "policy", "revision": 1, "supersedes": replaces,
                      "content": {"rule_id": identifier, "scope": ["P"], "text": identifier,
                                  "reason_refs": ["D"], "audit_refs": []}}
            change = {"kind": "policy", "record": record, "decision_id": "D" + identifier}
            i, runtime, _ = gov.apply_decision(i, runtime, change, source_ref="S")
        self.assertEqual({r["id"] for r in gov.governance_view(i)["policy_records"]}, {"P2", "P3"})
        self.assertEqual(i["governance"]["P1"]["status"], "superseded")
        with self.assertRaisesRegex(ValueError, "^governance decision requires a structured governance record$"):
            gov.apply_decision(i, runtime, {"kind": "policy", "text": "replace all"}, source_ref="S")

    def test_context_and_audit_require_owned_meaning_and_exact_verdict_mapping(self):
        i = domain_governance(); rt = {"tasks": {}, "executions": {}, "queue": [], "status": "ready"}
        context = {"id": "CX", "kind": "research_context", "revision": 1, "supersedes": [],
                   "content": {"terms": [{"term": "P", "definition": "the target", "boundary": "this problem",
                                          "avoid_synonyms": [], "record_refs": []}]}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "research_context", "record": context}, source_ref="S")
        audit = {"id": "AU", "kind": "additional_audit", "revision": 1, "supersedes": [],
                 "content": {"scope": ["P"], "required_inputs": ["CH1"], "assessor": "goal_audit",
                             "verdict_mapping": {"pass": "satisfied", "fail": "not_satisfied", "unknown": "unresolved"}}}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")
        self.assertEqual(gov.governance_view(i)["additional_audits"][0]["id"], "AU")
        audit["id"] = "AU2"; audit["content"]["verdict_mapping"]["pass"] = "unsupported_assurance"
        with self.assertRaisesRegex(ValueError, r"^change/record/content/verdict_mapping/pass: invalid enum"):
            gov.apply_decision(i, rt, {"kind": "additional_audit", "record": audit}, source_ref="S")

    def test_explicit_once_grant_and_exclusions_use_existing_execution_ledger(self):
        i = {"grants": {"G": {"id": "G", "kind": "local", "status": "active",
             "roles": ["research_work"], "task_ids": [], "excluded_targets": ["B"], "reuse": "once",
             "source_ref": "S", "subjects": ["research_work"]}}}
        rt = {"executions": {"E": {"id": "E", "grant_id": "G", "action": {"id": "A1"}}}}
        consumed = gov.authorize(i, {"id": "A2", "role": "research_work", "target": "A"}, runtime=rt)
        self.assertFalse(consumed["allowed"])
        self.assertEqual(consumed["rejected"], [{"grant_id": "G", "reason": "one-case grant already reserved or consumed"}])
        excluded = gov.authorize(i, {"id": "A1", "role": "research_work", "target": "B"}, runtime={})
        self.assertFalse(excluded["allowed"])
        self.assertEqual(excluded["rejected"], [{"grant_id": "G", "reason": "target excluded"}])

    def test_grant_decision_shape_names_no_resource_limit(self):
        # No reservation owner enforces a limit written on a grant, and the stored grant has no such field.
        from do_math.control_contracts import validate_decision_shape
        spec = {"id": "G", "kind": "local", "roles": ["research_work"], "reuse": "reusable"}
        for limits in ({}, {"jobs": 1}):
            with self.subTest(limits=limits), self.assertRaisesRegex(ValueError, "change/grant: invalid additionalProperties"):
                validate_decision_shape({"kind": "grant", "grant": {**spec, "resource_limits": limits}})

    def test_initialization_cannot_rebind_another_immutable_original(self):
        source = gov.preserve_source("S", "P", origin="user")
        records = [charter()]
        approval = {"id": "D", "actor": "user", "source_ref": "S", "source_sha256": source["sha256"],
                    "record_hashes": {"CH1": exact_content_hash(records[0])}}
        with self.assertRaisesRegex(ValueError, "^initial charter source differs from initialization immutable input$"):
            gov.initialize_governance(governance_start({"lifecycle": {"immutable_input": {
                "text": "Q", "sha256": "different", "bytes": 1}}}), source, approval, records)

    def test_raw_initial_charter_compares_lossless_input_not_nfc_projection(self):
        import hashlib
        import unicodedata
        text = 'e\u0301 has two codepoints'; raw = text.encode(); work = unicodedata.normalize('NFC', text).encode()
        source = gov.preserve_source('S', text, origin='user')
        record = charter()
        instance = governance_start({'id': 'I', 'lifecycle': {'immutable_input': {
            'text': text, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}}})
        approval = {'id': 'D', 'actor': 'user', 'source_ref': 'S', 'source_sha256': source['sha256'],
                    'record_hashes': {'CH1': exact_content_hash(record)}}
        result = gov.initialize_governance(instance, source, approval, [record])
        self.assertEqual(result['governance_sources']['S']['text'], text)
        changed = gov.preserve_source('S', work.decode(), origin='user')
        with self.assertRaisesRegex(ValueError, '^initial charter source differs from initialization immutable input$'):
            gov.initialize_governance(instance, changed, approval, [record])

    def test_stored_governance_content_must_still_match_approved_proposal(self):
        i = domain_governance(); i["governance"]["CH1"]["content"]["goal"] = "Unapproved Q"
        with self.assertRaisesRegex(ValueError, "^governance content differs from approved proposal$"):
            gov.validate_governance_state(i)

    def test_additional_audit_consumes_exact_required_inputs_and_mapping(self):
        i = domain_governance(); rt = {"tasks": {}, "executions": {}, "queue": []}
        r = {"id": "AU", "kind": "additional_audit", "revision": 1, "supersedes": [],
             "content": {"scope": ["P"], "required_inputs": ["CH1"], "assessor": "goal_audit",
                         "verdict_mapping": {"pass": "satisfied", "fail": "not_satisfied", "unknown": "unresolved"}}}
        i, _, _ = gov.apply_decision(i, rt, {"kind": "additional_audit", "record": r}, source_ref="S")
        with self.assertRaisesRegex(ValueError, "^audit inputs differ from the approved required set$"):
            gov.evaluate_additional_audit(i, "AU", "pass", assessor="goal_audit", input_hashes={})
        verdict = gov.evaluate_additional_audit(i, "AU", "pass", assessor="goal_audit",
                                                input_hashes={"CH1": exact_content_hash(i["governance"]["CH1"])})
        self.assertEqual(verdict["decision"], "satisfied")
        self.assertEqual(i["goal_status"], "unsolved")

    def test_grant_replacement_revokes_the_replaced_grant_and_stops_its_consumers(self):
        i = domain_governance(); rt = {"tasks": {}, "executions": {}, "queue": []}
        spec = {"id": "G", "kind": "local", "roles": ["research_work"], "reuse": "reusable", "expires_at": "2099-01-01T00:00:00Z"}
        i, rt, _ = gov.apply_decision(i, rt, {"kind": "grant", "grant": spec}, source_ref="S")
        rt["executions"]["E"] = {"id": "E", "status": "running", "grant_id": "G"}
        replacement = {**spec, "id": "G2", "expires_at": "2099-01-02T00:00:00Z"}
        i, rt, event = gov.apply_decision(i, rt, {"kind": "grant", "grant": replacement, "replaces": ["G"]}, source_ref="S")
        self.assertEqual(i["grants"]["G"]["status"], "revoked")
        self.assertEqual(i["grants"]["G"]["revoked_by"], event["id"])
        self.assertEqual(rt["executions"]["E"]["stop_requested"], "grant_revoked")

    def test_local_execution_kind_is_not_ignored(self):
        i = {"grants": {"G": {"id": "G", "kind": "local", "status": "active", "roles": ["research_work"],
                              "reuse": "reusable", "execution_kinds": ["machine"]}}}
        decision = gov.authorize(i, {"role": "research_work", "actor_kind": "ai"}, runtime={})
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["rejected"], [{"grant_id": "G", "reason": "execution kind outside grant"}])

    def test_initial_original_and_later_explicit_approval_remain_distinct(self):
        source = gov.preserve_source("ORIG", "Research P", origin="user")
        approval_source = gov.preserve_source("APPROVAL", "Approve this exact charter", origin="user")
        record = charter()
        approval = {"id": "D", "actor": "user", "source_ref": "APPROVAL", "source_sha256": approval_source["sha256"],
                    "input_source_ref": "ORIG", "input_source_sha256": source["sha256"],
                    "record_hashes": {"CH1": exact_content_hash(record)}}
        i = gov.initialize_governance(governance_start({"id": "I", "lifecycle": {"immutable_input": {
            k: source[k] for k in ("text", "sha256", "bytes")}}}), source, approval, [record], approval_source=approval_source)
        self.assertEqual(i["governance"]["CH1"]["source_ref"], "ORIG")
        self.assertEqual(i["decisions"]["D"]["source_ref"], "APPROVAL")
        self.assertIsNone(gov.validate_governance_state(i))

    def test_overlapping_grants_are_not_selected_by_identifier_order(self):
        instance = governance_start({'id': 'I', 'governance_sources': {'user': gov.preserve_source(
            'user', 'Authorize two reusable work grants.', origin='user')}})
        runtime = {'tasks': {}, 'executions': {}, 'queue': []}
        for identifier in ('A', 'B'):
            instance, runtime, _ = apply_decision(instance, runtime, {'kind': 'grant', 'grant': {
                'id': identifier, 'kind': 'local', 'reuse': 'reusable', 'roles': ['research_work']}},
                source_ref='user')
        decision = authorize(instance, {'id': 'AC', 'role': 'research_work', 'actor_kind': 'ai'}, runtime=runtime)
        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "ambiguous current grants")

    def test_once_http_operation_and_its_execution_share_logical_case(self):
        grant = {'id': 'G', 'status': 'active', 'reuse': 'once'}
        operation = {'id': 'OP', 'grant_id': 'G', 'request_sha256': 'request'}
        action = {'id': 'AC-OP', 'role': 'external_action', 'target': 'OP', 'grant_id': 'G'}
        rt = {'external_operations': {'OP': operation}, 'executions': {
            'EX': {'id': 'EX', 'role': 'external_action', 'grant_id': 'G', 'action': action}}}
        self.assertIsNone(gov.grant_scope_reason(grant, action, rt))
        self.assertIsNone(gov.grant_scope_reason(grant, {'id': 'OP', 'role': 'external_operation'}, rt))
        self.assertEqual(gov.grant_scope_reason(grant, {'id': 'OTHER', 'case_id': 'OP'}, rt),
                         'one-case grant already reserved or consumed')
        rt['external_operations']['SECOND'] = {'id': 'SECOND', 'grant_id': 'G'}
        self.assertEqual(gov.grant_scope_reason(grant, action, rt), 'one-case grant already reserved or consumed')


class DocumentedGrantTests(unittest.TestCase):
    def test_documented_research_grant_permits_formal_check(self):
        path = SKILL / 'references' / '초기화-운전.md'
        blocks = path.read_text(encoding='utf-8').split('```json\n')[1:]
        grant = next(json.loads(block.split('```')[0])['grant'] for block in blocks
                     if '"id": "GR-research-01"' in block.split('```')[0])
        # The document's expiry is a placeholder the operator replaces with the approved period.
        self.assertTrue(grant['expires_at'].startswith('<'), grant['expires_at'])
        grant.update(status='active', expires_at='2026-09-23T00:00:00+00:00')
        self.assertTrue(gov.authorize({'grants': {grant['id']: grant}}, {'role': 'formal_check'},
                                      at='2026-09-22T00:00:00+00:00')['allowed'])


if __name__ == "__main__":
    unittest.main()
