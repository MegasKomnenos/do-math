"""Delegated decisions (``delegations``, ``governance.authorize_review_replacement``), moved from ``test_delegations``.

A delegation lets one user decision cover a later case of the same kind within
its explicit scope, after two independent judgments on the sealed case found
it within scope. Every test calls the product functions on dictionary state
(``support.governance_delegation`` holds the legacy module's case builders);
every rejection is pinned to the product's reason, where the legacy tests
checked only the exception type or a false ``allowed``.
"""
from copy import deepcopy
import unittest

from do_math import delegations as d
from do_math import governance as gov
from do_math.delegations import authorize_delegated_case, case_basis_reference_ids
from support.record_builders import domain_governance
from support.governance_delegation import checked_replacement_case, replacement_case


class DelegationStorageTests(unittest.TestCase):
    def test_structured_case_reference_is_closed(self):
        with self.assertRaisesRegex(ValueError, r"^case basis reference must be a record ID or an exact \{'id': ID\} object$"):
            case_basis_reference_ids({"basis_refs": [{"id": "SO-one", "sha256": "not-a-binding"}]})


class DelegationJudgmentTests(unittest.TestCase):
    def test_delegation_requires_two_real_judgments_on_same_current_case(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = replacement_case()
        app = d.prepare_application(i, rt, "DG", case, now_iso=_entry.ports.clock.now())
        for eid, stage in (("E1", "interpret"), ("E2", "check")):
            rt["executions"][eid] = {"id": eid, "role": "intent_interpretation",
                                     "delegation_input_sha256": app["input_sha256"], "status": "ended"}
            d.record_judgment(rt, app["id"], {"decision": "within_scope", "reason": "same approved recovery",
                                              "input_sha256": app["input_sha256"]}, execution_id=eid, stage=stage)

        def effect(instance, runtime, value):
            runtime["replacement"] = value
            return instance, runtime
        result, state, record = d.apply_application(i, rt, app["id"], apply_effect=effect, now_iso=_entry.ports.clock.now())
        self.assertEqual(state["replacement"], case["effect"])
        self.assertNotIn(app["id"], result["decisions"])
        _, repeated, _ = d.apply_application(result, state, app["id"], apply_effect=lambda *_: self.fail("already applied"), now_iso=_entry.ports.clock.now())
        self.assertEqual(repeated, state)
        i["delegations"]["DG"]["status"] = "revoked"
        with self.assertRaisesRegex(ValueError, '^delegation inactive$'):
            d.apply_application(i, rt, app["id"], apply_effect=lambda a, b, e: (a, b), now_iso=_entry.ports.clock.now())

    def test_delegation_approval_must_bind_the_actual_delegation(self):
        # The delegation names the charter approval D, a user decision that is not this delegation's approval.
        from support.entry import entry
        _entry = entry()
        i, rt, _, case = replacement_case()
        i['delegations']['DG']['decision_id'] = 'D'
        with self.assertRaisesRegex(ValueError, '^approval does not bind the exact delegated scope$'):
            d.prepare_application(i, rt, "DG", case, now_iso=_entry.ports.clock.now())

    def test_case_delegation_requires_explicit_scope_and_independent_check(self):
        from support.entry import entry
        _entry = entry()
        delegation = {
            "id": "DG", "status": "active", "decision_kind": "task_scope",
            "original_decision_id": "DC", "included_targets": ["T"], "excluded_targets": [],
            "external_effects": [], "expires_at": None,
        }
        # A caller's independent flag resolves no real execution: without an application nothing is checked.
        for independent in (True, False):
            with self.subTest(independent=independent):
                self.assertEqual(authorize_delegated_case({"delegations": {"DG": delegation}}, "DG", {
                    "decision_kind": "task_scope", "target_id": "T",
                    "check": {"decision": "match", "scope_complete": True, "independent": independent}}, now_iso=_entry.ports.clock.now()),
                    {"allowed": False, "delegation_id": "DG", "reason": "application not found"})
        # The explicit scope the name states: a case outside it, and a delegation without one.
        i, rt, _, case = replacement_case()
        with self.assertRaisesRegex(ValueError, '^case outside delegation scope$'):
            d.prepare_application(i, rt, 'DG', {**case, 'target_id': 'RC'}, now_iso=_entry.ports.clock.now())
        i['delegations']['DG']['included_targets'] = []
        with self.assertRaisesRegex(ValueError, '^delegation needs explicit included scope$'):
            d.prepare_application(i, rt, 'DG', case, now_iso=_entry.ports.clock.now())

    def test_delegation_uses_case_hash_not_full_context_hash(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = replacement_case()
        app = d.prepare_application(i, rt, 'DG', case, now_iso=_entry.ports.clock.now())
        for eid, stage in [('AUTHOR', 'interpret'), ('CHECKER', 'check')]:
            rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation',
                                     'input_manifest': {'prompt': {'sha256': 'whole-context-' + eid}},
                                     'delegation_input_sha256': app['input_sha256']}
            d.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                'reason': 'Within exact delegated case'}, execution_id=eid, stage=stage)

        def effect(instance, runtime, change):
            runtime['review_cycles']['RC']['installed_effect'] = deepcopy(change)
            return instance, runtime
        updated, state, receipt = d.apply_application(i, rt, app['id'], apply_effect=effect, now_iso=_entry.ports.clock.now())
        self.assertEqual(receipt['effect'], case['effect'])
        self.assertEqual(updated['grants'], i['grants'])
        self.assertEqual(d.apply_application(updated, state, app['id'], apply_effect=effect, now_iso=_entry.ports.clock.now())[2], receipt)
        damaged = deepcopy(state)
        damaged['delegation_applications'][app['id']]['application']['sha256'] = '0' * 64
        before_damaged = deepcopy(damaged)
        self.assertEqual(d.authorize_delegated_case(updated, 'DG', {'application_id': app['id']},
            runtime=damaged, now_iso=_entry.ports.clock.now()),
            {'allowed': False, 'delegation_id': 'DG', 'reason': 'delegation receipt changed'})
        self.assertEqual(damaged, before_damaged)
        self.assertEqual(state['delegation_applications'][app['id']]['application'], receipt)
        rt['executions']['CHECKER']['role'] = 'research_work'
        self.assertEqual(d.authorize_delegated_case(i, 'DG', {'application_id': app['id']}, runtime=rt, now_iso=_entry.ports.clock.now()),
                         {'allowed': False, 'delegation_id': 'DG', 'reason': 'judgment execution must bind blind shared input'})

    def test_delegated_effect_cannot_rewrite_preserved_authority_source(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = checked_replacement_case()

        def bad_effect(instance, runtime, change):
            instance['governance_sources']['NEW'] = gov.preserve_source('NEW', 'Forged authority', origin='user')
            return instance, runtime
        with self.assertRaisesRegex(ValueError, '^delegated application cannot alter authority$'):
            d.apply_application(i, rt, case['application_id'], apply_effect=bad_effect, now_iso=_entry.ports.clock.now())


class ReplacementAuthorityTests(unittest.TestCase):
    def test_general_machine_grant_does_not_require_new_semantic_delegation(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = replacement_case()
        allowed = gov.authorize_review_replacement(i, rt, action, at=_entry.ports.clock.now())
        self.assertEqual((allowed['allowed'], allowed['grant_id'], allowed['authority_mode']), (True, 'G', 'machine_grant'))
        changed = deepcopy(i)
        changed['governance_sources']['S']['text'] += '!'
        self.assertEqual(gov.authorize_review_replacement(changed, rt, action, at=_entry.ports.clock.now()),
                         {'allowed': False, 'grant_id': None, 'reason': 'immutable source bytes or revision changed'})
        i['grants']['G']['expires_at'] = '2000-01-01T00:00:00Z'
        self.assertEqual(gov.authorize_review_replacement(i, rt, action, at=_entry.ports.clock.now()),
                         {'allowed': False, 'grant_id': None, 'reason': 'no current grant permits this action',
                          'rejected': [{'grant_id': 'G', 'reason': 'grant expired'}]})

    def test_real_checked_case_resolves_knowledge_and_rechecks_cycle_and_exact_effect(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = checked_replacement_case()
        allowed = gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case, at=_entry.ports.clock.now())
        self.assertEqual((allowed['allowed'], allowed['authority_mode'], allowed['delegation']['application_id']),
                         (True, 'checked_case', case['application_id']))
        forged = deepcopy(case)
        forged['effect']['slot'] = 'OTHER'
        self.assertEqual(d.authorize_delegated_case(i, 'DG', forged, runtime=rt, now_iso=_entry.ports.clock.now()),
                         {'allowed': False, 'delegation_id': 'DG', 'reason': 'requested case differs from independently checked effect'})
        rt['review_cycles']['RC']['revision'] = 2
        self.assertEqual(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case, at=_entry.ports.clock.now()),
                         {'allowed': False, 'delegation_id': 'DG', 'reason': 'delegation application stale'})

    def test_expired_or_missing_independent_check_denies_semantic_reuse(self):
        from support.entry import entry
        _entry = entry()
        i, rt, action, case = checked_replacement_case()
        self.assertEqual(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case,
                                                         at='2100-01-01T00:00:00Z'),
                         {'allowed': False, 'delegation_id': 'DG', 'reason': 'delegation expired'})
        rt['delegation_applications'][case['application_id']]['judgments'].pop('check')
        self.assertEqual(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case, at=_entry.ports.clock.now()),
                         {'allowed': False, 'delegation_id': 'DG', 'reason': 'two independent judgments required'})


if __name__ == '__main__':
    unittest.main()
