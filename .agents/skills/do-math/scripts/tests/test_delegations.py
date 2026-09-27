"""Delegated decisions: independent judgments on one case, the stored case reference and reuse of a replacement authority."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import activities, execution_lifecycle, execution_profiles, governance, governance as gov
from do_math.delegations import (
    authorize_delegated_case,
    case_basis_reference_ids,
    prepare_application,
    record_judgment,
)
from do_math.repository import ResearchRepository
from research_fixtures import new_instance
from record_fixtures import domain_governance


def replacement_case():
    """``(instance, runtime, action, case)``: a delegated review replacement of ``K``'s review, not yet applied."""
    from do_math import delegations as d
    i = domain_governance()
    rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready',
          'review_cycles': {'RC': {'id': 'RC', 'knowledge_id': 'K', 'revision': 1}},
          'activities': {}}
    i['knowledge'] = {'K': {'id': 'K', 'revision': 1}}
    action = {'id': 'ACTION', 'role': 'identity_review', 'target': 'K',
              'actor_kind': 'ai', 'purpose': 'record_replacement', 'review_cycle_id': 'RC',
              'stage': 'initial', 'slot': 'R1', 'round': 0, 'replacement_for': 0,
              'continuity_break_cause': 'permanent_loss'}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'grant', 'decision_id': 'GRANT-DECISION',
        'grant': {'id': 'G', 'kind': 'local', 'roles': ['identity_review'], 'reuse': 'reusable',
                  'included_targets': ['K'], 'purposes': ['record_replacement']}}, source_ref='S')
    i['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user', 'kind': 'review_replacement', 'source_ref': 'S'}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {
        'id': 'DG', 'status': 'active', 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
        'included_targets': ['K'], 'excluded_targets': [], 'external_effects': [], 'resource_limits': {},
        'expires_at': '2099-01-01T00:00:00Z'}}, source_ref='S')
    effect = {key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round', 'replacement_for', 'continuity_break_cause')}
    case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K',
            'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': ['RC']}
    return i, rt, action, case


def checked_replacement_case():
    """``replacement_case`` whose delegation application both independent judgments found within scope."""
    from do_math import delegations as d
    i, rt, action, case = replacement_case()
    app = d.prepare_application(i, rt, 'DG', case)
    for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
        rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'delegation_input_sha256': app['input_sha256']}
        d.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                                       'reason': 'Synthetic matching case'}, execution_id=eid, stage=stage)
    return i, rt, action, {**case, 'application_id': app['id']}


class DelegationStorageTests(unittest.TestCase):
    def test_structured_case_reference_is_closed(self):
        with self.assertRaisesRegex(ValueError, "case basis reference"):
            case_basis_reference_ids({"basis_refs": [{"id": "SO-one", "sha256": "not-a-binding"}]})

    def test_structured_reference_survives_git_and_stales_when_its_record_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "repository"
            source_path = root / "source.txt"
            source_path.write_text("The original source bytes.", encoding="utf-8")
            instance_id = new_instance(
                repository,
                goal="Preserve an independently checked delegated case.",
                workspace=root / "workspace",
                sources=[source_path],
                config={ "scholarly_enabled": False, "operator_enabled": False,
                        "lean_command": ["fixture-lean"]},
            )
            store = ResearchRepository(repository, instance_id)
            head, instance, runtime = store.load()
            source_id = instance["sources"][0]["id"]
            instance.setdefault("governance_sources", {})["GS-delegation"] = governance.preserve_source(
                "GS-delegation", "User authorizes this bounded delegated grant case.", origin="user"
            )
            instance, runtime, _ = governance.apply_decision(
                instance,
                runtime,
                {"kind": "grant", "decision_id": "DC-original", "grant": {
                    "id": "GR-original", "kind": "local", "roles": ["maintenance"],
                    "reuse": "reusable",
                }},
                source_ref="GS-delegation",
            )
            instance, runtime, _ = governance.apply_decision(
                instance,
                runtime,
                {"kind": "delegation", "decision_id": "DC-delegation", "delegation": {
                    "id": "DG-source", "status": "active", "decision_kind": "grant",
                    "original_decision_id": "DC-original", "included_targets": [source_id],
                    "excluded_targets": [], "external_effects": [], "resource_limits": {}, "expires_at": None,
                }},
                source_ref="GS-delegation",
            )
            case = {
                "id": "CASE-source", "decision_kind": "grant", "target_id": source_id,
                "external_effects": [], "resources": {},
                "effect": {"operation": "bounded source review"},
                "basis_refs": [{"id": source_id}],
            }
            application = prepare_application(instance, runtime, "DG-source", case)
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)

            profile = next(profile for profile in instance["execution_profiles"].values()
                           if profile["role"] == "intent_interpretation")
            for stage, suffix in (("interpret", "one"), ("check", "two")):
                activity_id, execution_id = "AY-judgment-" + suffix, "EX-judgment-" + suffix
                activities.open_activity(runtime, activity_id=activity_id, activity_kind="delegation_judgment",
                                         owner_ref=application["id"], input_refs=[],
                                         opened_at="2026-09-21T00:00:00Z")
                execution = execution_lifecycle.create_execution(
                    execution_id=execution_id, owner_activity_id=activity_id, actor_kind="ai",
                    input_manifest={}, profile_ref=execution_profiles.profile_ref(profile),
                    created_at="2026-09-21T00:00:00Z",
                )
                execution.update(role="intent_interpretation", delegation_input_sha256=application["input_sha256"])
                activities.assign_execution(runtime, activity_id, execution)
                record_judgment(
                    runtime,
                    application["id"],
                    {"input_sha256": application["input_sha256"], "decision": "within_scope",
                     "reason": "The checked case remains within the preserved grant decision."},
                    execution_id=execution_id,
                    stage=stage,
                )
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)
            allowed = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime)
            self.assertTrue(allowed["allowed"], allowed)

            instance["sources"][0]["revision"] = 2
            head = store.save_with_state(head, instance, runtime)[0]
            _, instance, runtime = store.load(head)
            rejected = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime)
            self.assertFalse(rejected["allowed"])
            self.assertEqual(rejected["reason"], "delegation application stale")


class DelegationJudgmentTests(unittest.TestCase):
    def test_delegation_requires_two_real_judgments_on_same_current_case(self):
        from do_math import delegations as d
        i = domain_governance()
        i["decisions"]["ORIGINAL"] = {"id": "ORIGINAL", "actor": "user", "source_ref": "S", "kind": "review_replacement", "status": "active"}
        i["delegations"] = {"DG": {"id": "DG", "status": "active", "decision_kind": "review_replacement",
              "original_decision_id": "ORIGINAL", "included_targets": ["T"], "excluded_targets": [],
              "external_effects": [], "resource_limits": {}, "expires_at": None, "source_ref": "S", "decision_id": "D"}}
        i["delegations"]["DG"]["decision_id"] = "DD"
        i["decisions"]["DD"] = {"id":"DD", "kind":"delegation", "actor":"user", "source_ref":"S",
            "change":{"delegation":{k:deepcopy(v) for k,v in i["delegations"]["DG"].items() if k not in {"source_ref","decision_id","created_at"}}}}
        rt = {"executions": {}, "tasks": {"T": {"id": "T", "status": "waiting"}}}
        case = {"id": "CASE", "target_id": "T", "decision_kind": "review_replacement", "external_effects": [], "resources": {}, "effect": {"replace_slot": "R"}}
        app = d.prepare_application(i, rt, "DG", case)
        for eid, stage in (("E1", "interpret"), ("E2", "check")):
            rt["executions"][eid] = {"id": eid, "role": "intent_interpretation", "delegation_input_sha256": app["input_sha256"], "status": "ended"}
            d.record_judgment(rt, app["id"], {"decision": "within_scope", "reason": "same approved recovery", "input_sha256": app["input_sha256"]}, execution_id=eid, stage=stage)
        def effect(a,b,value):
            b["tasks"]["T"]["status"]="ready";b["replacement"]=value
            return a,b
        result, state, record = d.apply_application(i, rt, app["id"], apply_effect=effect)
        self.assertEqual(state["replacement"], {"replace_slot": "R"})
        self.assertNotIn(app["id"], result["decisions"])
        _, repeated, _ = d.apply_application(result,state,app["id"],apply_effect=lambda *_:self.fail("already applied"))
        self.assertEqual(repeated,state)
        i["delegations"]["DG"]["status"] = "revoked"
        with self.assertRaises(ValueError): d.apply_application(i, rt, app["id"], apply_effect=lambda a,b,e:(a,b))

    def test_delegation_approval_must_bind_the_actual_delegation(self):
        from do_math import delegations as d
        i=domain_governance();i["decisions"]["ORIG"]={"id":"ORIG","kind":"custom_case","actor":"user","source_ref":"S"}
        i["delegations"]={"DG":{"id":"DG","status":"active","decision_kind":"custom_case","original_decision_id":"ORIG",
             "included_targets":["T"],"excluded_targets":[],"external_effects":[],"resource_limits":{},"source_ref":"S","decision_id":"D"}}
        case={"id":"C","target_id":"T","decision_kind":"custom_case","external_effects":[],"resources":{},"effect":{}}
        with self.assertRaises(ValueError):d.prepare_application(i,{"tasks":{"T":{"id":"T"}}},"DG",case)

    def test_case_delegation_requires_explicit_scope_and_independent_check(self):
        from do_math.delegations import authorize_delegated_case

        delegation = {
            "id": "DG", "status": "active", "decision_kind": "task_scope",
            "original_decision_id": "DC", "included_targets": ["T"], "excluded_targets": [],
            "external_effects": [], "expires_at": None,
        }
        allowed = authorize_delegated_case(
            {"delegations": {"DG": delegation}}, "DG",
            {"decision_kind": "task_scope", "target_id": "T", "check": {"decision": "match", "scope_complete": True, "independent": True}},
        )
        # A caller's independent=True flag does not resolve either real execution.
        self.assertFalse(allowed["allowed"])
        denied = authorize_delegated_case(
            {"delegations": {"DG": delegation}}, "DG",
            {"decision_kind": "task_scope", "target_id": "T", "check": {"decision": "match", "scope_complete": True, "independent": False}},
        )
        self.assertFalse(denied["allowed"])

    def test_delegation_uses_case_hash_not_full_context_hash(self):
        from do_math import delegations as d
        i, rt, action, case = replacement_case()
        app = d.prepare_application(i, rt, 'DG', case)
        for eid, stage in [('AUTHOR', 'interpret'), ('CHECKER', 'check')]:
            rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'input_manifest': {'prompt': {'sha256': 'whole-context-' + eid}},
                                     'delegation_input_sha256': app['input_sha256']}
            d.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                'reason': 'Within exact delegated case'}, execution_id=eid, stage=stage)
        def effect(i, rt, change):
            rt['review_cycles']['RC']['installed_effect'] = deepcopy(change); return i, rt
        updated, state, receipt = d.apply_application(i, rt, app['id'], apply_effect=effect)
        self.assertEqual(receipt['effect'], case['effect'])
        self.assertEqual(updated['grants'], i['grants'])
        self.assertEqual(d.apply_application(updated, state, app['id'], apply_effect=effect)[2], receipt)
        rt['executions']['CHECKER']['role'] = 'research_work'
        self.assertFalse(d.authorize_delegated_case(i, 'DG', {'application_id': app['id']}, runtime=rt)['allowed'])

    def test_delegated_effect_cannot_rewrite_preserved_authority_source(self):
        from do_math import delegations as d
        i, rt, action, case = checked_replacement_case()
        def bad_effect(i, rt, change):
            i['governance_sources']['NEW'] = gov.preserve_source('NEW', 'Forged authority', origin='user'); return i, rt
        with self.assertRaises(ValueError): d.apply_application(i, rt, case['application_id'], apply_effect=bad_effect)

    def test_actual_engine_delegation_control_to_independent_judgments_effect_and_receipt(self):
        import tempfile
        from do_math.engine import ResearchEngine
        from do_math import delegations as d
        from review_fixtures import ReviewFakeEngine, grant_replacement
        with tempfile.TemporaryDirectory() as root:
            engine = ReviewFakeEngine(root)
            grant_replacement(engine)
            cid = engine.start('K1')
            action = deepcopy(engine.pending())
            engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
            engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
                'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
            engine.instance, engine.runtime, _ = gov.apply_decision(engine.instance, engine.runtime,
                {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
                 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
                 'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
                 'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review')
            effect = {**{key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round')},
                      'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
            case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1',
                    'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': [cid]}
            request = {'id': 'REQUEST', 'action': 'request', 'config': {'role': 'maintenance', 'review_replacement': {
                'action': action, 'grant_id': 'GR-review', 'delegation_id': 'DG', 'case': case}}}
            engine.runtime.setdefault('history', []).append({'kind': 'user_control', 'request': request})
            self.assertTrue(ResearchEngine._review_recovery_control(engine, request))
            stages = [a for a in engine.runtime['queue'] if a.get('delegation_application_id')]
            self.assertEqual(len(stages), 2)
            app_id = stages[0]['delegation_application_id']
            shared = d.judgment_input(engine.runtime, app_id)
            before_authority = deepcopy({key: engine.instance.get(key) for key in ('decisions', 'grants', 'delegations')})
            for index, stage in enumerate(stages):
                self.assertEqual(d.judgment_input(engine.runtime, app_id), shared)
                eid = 'DG-' + str(index)
                engine.runtime['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'status': 'ended',
                    'input_sha256': 'full-context-' + eid, 'delegation_input_sha256': shared['input_sha256']}
                ResearchEngine._apply_delegation_judgment(engine, stage, {'delegation_judgment': {
                    'input_sha256': shared['input_sha256'], 'decision': 'within_scope',
                    'reason': 'Exact case is covered by original authority'}}, eid)
            app = engine.runtime['delegation_applications'][app_id]
            self.assertEqual(set(app['judgments']), {'interpret', 'check'})
            self.assertEqual(app['application']['effect'], effect)
            self.assertEqual({key: engine.instance.get(key) for key in before_authority}, before_authority)
            replacement = next(a for a in engine.runtime['queue'] if a.get('replacement_for') is not None)
            engine.runtime['queue'].remove(replacement); engine.runtime['queue'].insert(0, replacement)
            engine.execute(record_first=True)
            engine.execute()
            self.assertTrue(engine.usable())
            self.assertTrue(engine.runtime['review_cycles'][cid]['replacement_receipts'])


class ReplacementAuthorityTests(unittest.TestCase):
    def test_general_machine_grant_does_not_require_new_semantic_delegation(self):
        i, rt, action, case = replacement_case()
        self.assertTrue(gov.authorize_review_replacement(i, rt, action)['allowed'])
        changed = deepcopy(i); changed['governance_sources']['S']['text'] += '!'
        self.assertFalse(gov.authorize_review_replacement(changed, rt, action)['allowed'])
        i['grants']['G']['expires_at'] = '2000-01-01T00:00:00Z'
        self.assertFalse(gov.authorize_review_replacement(i, rt, action)['allowed'])

    def test_real_checked_case_resolves_knowledge_and_rechecks_cycle_and_exact_effect(self):
        from do_math import delegations as d
        i, rt, action, case = checked_replacement_case()
        self.assertTrue(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])
        forged = deepcopy(case); forged['effect']['slot'] = 'OTHER'
        self.assertFalse(d.authorize_delegated_case(i, 'DG', forged, runtime=rt)['allowed'])
        rt['review_cycles']['RC']['revision'] = 2
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])

    def test_expired_or_missing_independent_check_denies_semantic_reuse(self):
        i, rt, action, case = checked_replacement_case()
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case,
                                                        at='2100-01-01T00:00:00Z')['allowed'])
        rt['delegation_applications'][case['application_id']]['judgments'].pop('check')
        self.assertFalse(gov.authorize_review_replacement(i, rt, action, delegation_id='DG', case=case)['allowed'])


if __name__ == "__main__":
    unittest.main()
