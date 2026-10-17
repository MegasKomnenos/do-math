"""A delegation application stored and reloaded through the repository (``delegations``, ``repository``), moved from ``test_delegations``.

The legacy test initialized an instance with one source through the public
``initialize`` on a real Git repository (``research_fixtures.new_instance``) and
saved and reloaded the state through ``ResearchRepository``. Here the public
``initialize`` runs on a Sim (``Sim(root, sources=...)``), and the repository is
the Sim engine's ``ResearchRepository`` over the Git port's fake; every save
passes the storage contract.
"""
from pathlib import Path
from copy import deepcopy
import tempfile
import unittest

from do_math import activities, execution_lifecycle, execution_profiles, governance
from do_math.delegations import authorize_delegated_case, prepare_application, record_judgment
from support.sim import Sim


class DelegationStorageTests(unittest.TestCase):
    def test_delegated_judges_receive_the_same_case_and_no_peer_verdict(self):
        """A publicly produced theorem and review, then the actual recovery/context producers.

        The user decision and delegation are explicit domain inputs; no sparse
        review-only fixture is expanded with invented context defaults.
        """
        from do_math.context_store import prepare_role_input
        from support.role_input_requirements import assert_judgment_inputs
        from support.execution_inputs import delegated_judgment_scene
        sim, judges, shared = delegated_judgment_scene()
        engine = sim.engine
        request = next(row['request'] for row in sim.runtime['history']
                       if row.get('request', {}).get('id') == 'REQUEST-delegated-input')
        for index, judge in enumerate(judges):
            workspace = sim.root / ('delegated-input-' + str(index))
            context = engine._context(judge, workspace)
            profile = execution_profiles.resolve_profile(sim.instance['execution_profiles'],
                sim.instance['role_profile_refs']['intent_interpretation'][0])
            fitted = prepare_role_input(context, instance=sim.instance, runtime=sim.runtime,
                role='intent_interpretation', profile=profile, snapshot=engine.head,
                workspace=workspace, activity_id='AY-delegated-input-' + str(index),
                install_submission_tools=True, clock=sim.clock)
            assert_judgment_inputs(self, 'intent_interpretation', fitted, workspace, producer_context=context)
            self.assertEqual(fitted['context']['delegation_case'], shared)
            self.assertEqual(fitted['context']['user_request']['request'], request)
            self.assertEqual(fitted['context']['record_map']['ledger'], 'supplied_only')
            for private in ('recent_history', 'user_inputs', 'open_questions', 'question_links'):
                self.assertNotIn(private, fitted['context'])
            if index == 0:
                from support.governance_sim import returned
                execution = returned(engine, judge, 'EX-delegation-private-judgment')
                execution['delegation_input_sha256'] = shared['input_sha256']
                record_judgment(sim.runtime, judge['delegation_application_id'], {
                    'input_sha256': shared['input_sha256'], 'decision': 'within_scope',
                    'reason': 'PRIVATE-FIRST-DELEGATION-JUDGMENT'},
                    execution_id=execution['id'], stage='interpret')
                engine._save()
            else:
                self.assertNotIn('PRIVATE-FIRST-DELEGATION-JUDGMENT', fitted['prompt'])
                from do_math.context_store import readable_snapshot_path
                self.assertFalse(readable_snapshot_path(fitted['validation_context'],
                    'runtime/executions/EX-delegation-private-judgment.json'))
                self.assertFalse(readable_snapshot_path(fitted['validation_context'],
                    'runtime/delegation_applications/' + judge['delegation_application_id'] + '.json'))

    def test_revoke_delegation_preserves_original_and_publishes_one_event(self):
        from support.governance_cases import delegated_sim
        sim = delegated_sim()
        before = deepcopy((sim.instance, sim.runtime))
        change = {'kind': 'revoke_delegation', 'delegation_id': 'DG-close', 'decision_id': 'DC-close-revoke'}
        result, state, event = governance.apply_decision(sim.instance, sim.runtime, change,
            source_ref='GS-close-delegation', clock=sim.clock)
        self.assertEqual((sim.instance, sim.runtime), before)
        self.assertEqual(result['delegations']['DG-close'], {**before[0]['delegations']['DG-close'],
            'status': 'revoked', 'revoked_by': 'DC-close-revoke', 'revoked_at': sim.clock.now()})
        self.assertEqual(event['delegation_id'], 'DG-close')
        self.assertEqual(state['history'], before[1]['history'] + [
            {'kind': 'governance_decision', 'decision_id': 'DC-close-revoke', 'source_ref': 'GS-close-delegation'}])
        sim.engine.instance, sim.engine.runtime = result, state
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1]['delegations']['DG-close'], result['delegations']['DG-close'])
        published = deepcopy(sim.engine.store.load())
        head, instance, runtime = published
        for reference, reason in (
                ('DC-missing', '^delegations references unknown record: DC-missing$'),
                ('GS-close-delegation', '^delegations reference has wrong family: GS-close-delegation$')):
            with self.subTest(reference=reference):
                damaged = deepcopy(instance)
                damaged['delegations']['DG-close']['revoked_by'] = reference
                before_damaged = deepcopy(damaged)
                with self.assertRaisesRegex(ValueError, reason):
                    sim.engine.store.save_with_state(head, damaged, deepcopy(runtime))
                self.assertEqual(damaged, before_damaged)
                self.assertEqual(sim.engine.store.load(), published)

    def test_storage_rejects_each_damaged_application_binding_without_publication(self):
        from copy import deepcopy
        from do_math.canonical import exact_content_hash
        from do_math.state_contract import default_state_contract
        from support.governance_cases import delegated_sim

        sim = delegated_sim()
        store = sim.engine.store
        published = deepcopy(store.load())
        head, instance, runtime = published
        produced, = [row for row in runtime['delegation_applications'].values()
                     if row['delegation_id'] == 'DG-close']
        application_id = produced['id']
        self.assertEqual(set(produced['judgments']), {'interpret', 'check'})
        self.assertEqual(len({j['execution_id'] for j in produced['judgments'].values()}), 2)
        self.assertTrue(produced['basis']['references'])
        self.assertEqual(authorize_delegated_case(instance, 'DG-close',
            {'application_id': application_id}, runtime=runtime, now_iso=sim.clock.now()),
            {'allowed': True, 'delegation_id': 'DG-close', 'application_id': application_id,
             'original_decision_id': produced['basis']['original_decision']['id']})
        family = default_state_contract().family('runtime', 'delegation_applications')
        family.checker.validate(produced)
        self.assertIsNone(family.validator(deepcopy(produced)))

        cases = (('basis_hash', 'delegation application basis hash mismatch'),
                 ('frozen_references', 'delegation frozen references differ from declared case basis'),
                 ('interpret_output', 'delegation judgment provenance mismatch'),
                 ('check_output', 'delegation judgment provenance mismatch'),
                 ('same_execution', 'delegation judgments must use distinct executions'))
        for damage, reason in cases:
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                row = broken['delegation_applications'][application_id]
                if damage == 'basis_hash':
                    row['basis']['case']['effect']['operation'] += '-changed'
                elif damage == 'frozen_references':
                    row['basis']['references'].pop(next(iter(row['basis']['references'])))
                    row['input_sha256'] = exact_content_hash(row['basis'])
                elif damage.endswith('_output'):
                    stage = damage.removesuffix('_output')
                    row['judgments'][stage]['output']['reason'] += ' changed after sealing'
                else:
                    row['judgments']['check']['execution_id'] = row['judgments']['interpret']['execution_id']
                family.checker.validate(row)
                before = deepcopy((instance, broken))
                with self.assertRaises(ValueError) as leaf:
                    family.validator(deepcopy(row))
                self.assertIs(type(leaf.exception), ValueError)
                self.assertEqual(str(leaf.exception), reason)
                with self.assertRaises(ValueError) as caught:
                    store.save_with_state(head, instance, broken)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((instance, broken), before)
                self.assertEqual(store.load(), published)

    def test_reference_factory_preserves_produced_scalar_and_list_bindings(self):
        from copy import deepcopy
        from do_math.record_schemas import refs
        from support.governance_cases import delegated_sim

        sim = delegated_sim()
        store = sim.engine.store
        published = deepcopy(store.load())
        head, instance, runtime = published
        application, = [row for row in runtime['delegation_applications'].values()
                        if row['delegation_id'] == 'DG-close']
        execution_id = application['judgments']['interpret']['execution_id']
        execution = runtime['executions'][execution_id]
        activity_id = execution['owner_activity_id']
        activity = runtime['activities'][activity_id]
        self.assertIn(execution_id, activity['assigned_execution_ids'])
        scalar_refs = refs(('owner_activity_id', 'activities'), ('continuation_of', 'executions'),
                           ('operation_id', 'external_operations'))
        self.assertTrue(callable(scalar_refs))
        self.assertIsNone(execution.get('continuation_of'))
        self.assertIsNone(execution.get('operation_id'))
        self.assertEqual(list(scalar_refs(execution)), [(activity_id, 'activities')])
        list_refs = refs(lists=(('assigned_execution_ids', 'executions'),))
        self.assertTrue(callable(list_refs))
        self.assertEqual(list(list_refs(activity)),
                         [(identifier, 'executions') for identifier in activity['assigned_execution_ids']])
        delegation_refs = refs(('delegation_id', 'delegations'))
        self.assertTrue(callable(delegation_refs))
        self.assertEqual(list(delegation_refs(application)), [('DG-close', 'delegations')])

        cases = (('scalar_missing', 'delegation_applications references unknown record: DG-missing-factory'),
                 ('scalar_wrong_family', 'delegation_applications reference has wrong family: ' + execution_id),
                 ('list_missing', 'activities references unknown record: EX-missing-factory'),
                 ('list_wrong_family', 'activities reference has wrong family: DG-close'))
        for damage, reason in cases:
            with self.subTest(damage=damage):
                broken = deepcopy(runtime)
                if damage.startswith('scalar_'):
                    broken['delegation_applications'][application['id']]['delegation_id'] = (
                        'DG-missing-factory' if damage == 'scalar_missing' else execution_id)
                else:
                    broken['activities'][activity_id]['assigned_execution_ids'] = [
                        'EX-missing-factory' if damage == 'list_missing' else 'DG-close']
                before = deepcopy((instance, broken))
                with self.assertRaises(ValueError) as caught:
                    store.save_with_state(head, instance, broken)
                self.assertIs(type(caught.exception), ValueError)
                self.assertEqual(str(caught.exception), reason)
                self.assertEqual((instance, broken), before)
                self.assertEqual(store.load(), published)

    def test_structured_reference_survives_git_and_stales_when_its_record_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "source.txt"
            source_path.write_text("The original source bytes.", encoding="utf-8")
            sim = Sim(root / "sim", goal="Preserve an independently checked delegated case.", sources=[source_path])
            store = sim.engine.store
            head, instance, runtime = store.load()
            source_id = instance["sources"][0]["id"]
            instance.setdefault("governance_sources", {})["GS-delegation"] = governance.preserve_source(
                "GS-delegation", "User authorizes this bounded delegated grant case.", origin="user")
            instance, runtime, _ = governance.apply_decision(instance, runtime,
                {"kind": "grant", "decision_id": "DC-original", "grant": {
                    "id": "GR-original", "kind": "local", "roles": ["maintenance"], "reuse": "reusable"}},
                source_ref="GS-delegation", clock=sim.ports.clock)
            instance, runtime, _ = governance.apply_decision(instance, runtime,
                {"kind": "delegation", "decision_id": "DC-delegation", "delegation": {
                    "id": "DG-source", "status": "active", "decision_kind": "grant",
                    "original_decision_id": "DC-original", "included_targets": [source_id],
                    "excluded_targets": [], "external_effects": [], "resource_limits": {}, "expires_at": None}},
                source_ref="GS-delegation", clock=sim.ports.clock)
            case = {"id": "CASE-source", "decision_kind": "grant", "target_id": source_id,
                    "external_effects": [], "resources": {}, "effect": {"operation": "bounded source review"},
                    "basis_refs": [{"id": source_id}]}
            application = prepare_application(instance, runtime, "DG-source", case, now_iso=sim.ports.clock.now())
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)

            profile = next(profile for profile in instance["execution_profiles"].values()
                           if profile["role"] == "intent_interpretation")
            for stage, suffix in (("interpret", "one"), ("check", "two")):
                activity_id, execution_id = "AY-judgment-" + suffix, "EX-judgment-" + suffix
                activities.open_activity(runtime, activity_id=activity_id, activity_kind="delegation_judgment",
                                         owner_ref=application["id"], input_refs=[], opened_at="2026-09-21T00:00:00Z")
                execution = execution_lifecycle.create_execution(
                    execution_id=execution_id, owner_activity_id=activity_id, actor_kind="ai",
                    input_manifest={}, profile_ref=execution_profiles.profile_ref(profile),
                    created_at="2026-09-21T00:00:00Z")
                execution.update(role="intent_interpretation", delegation_input_sha256=application["input_sha256"])
                activities.assign_execution(runtime, activity_id, execution)
                record_judgment(runtime, application["id"],
                    {"input_sha256": application["input_sha256"], "decision": "within_scope",
                     "reason": "The checked case remains within the preserved grant decision."},
                    execution_id=execution_id, stage=stage)
            head = store.save_with_state(head, instance, runtime)[0]
            head, instance, runtime = store.load(head)
            allowed = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime, now_iso=sim.ports.clock.now())
            self.assertTrue(allowed["allowed"], allowed)

            instance["sources"][0]["revision"] = 2
            head = store.save_with_state(head, instance, runtime)[0]
            _, instance, runtime = store.load(head)
            rejected = authorize_delegated_case(instance, "DG-source", {"application_id": application["id"]}, runtime=runtime, now_iso=sim.ports.clock.now())
            self.assertFalse(rejected["allowed"])
            self.assertEqual(rejected["reason"], "delegation application stale")


if __name__ == '__main__':
    unittest.main()
