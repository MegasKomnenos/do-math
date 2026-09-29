"""Knowledge records: currentness, impact, revision, kinds and trust environments. Kernel evidence in the domain fixtures is a test double; the Lean-labelled tests run the installed compiler."""
from copy import deepcopy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import copy
import tempfile
import hashlib
import os
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import knowledge, knowledge as k, knowledge_io, knowledge_records as kr
from do_math.canonical import exact_content_hash
from do_math.system_clock import new_id
from knowledge_fixtures import (add_knowledge, formal_evidence, impact_declaration, knowledge_graph,
                                revise_knowledge, seal_knowledge)
from do_math.lean_evidence import portable_bin
from do_math.formal import toolchain_root, verify_lean
from knowledge_fixtures import knowledge_candidate, verified_knowledge
from research_fixtures import git_init
from test_categories import test_group as category


def withdraw(state, runtime, kid):
    return k.invalidate_knowledge(state, runtime, kid, reason='false', actor_ref='reviewer',
        declared_impact=impact_declaration(state, runtime, [kid]))


def transition(state):
    state, env = deepcopy(state), 'TE-new'
    state.setdefault('trust_environments', {})[env] = {'id': env, 'toolchain': {'version': 'fixture-new'},
                                                        'allowed_axioms': [], 'status': 'registered'}
    return state, env, k.begin_transition(state, env)


def finish_transition(state, env, tr):
    for target in tr['targets']:
        tr = k.record_transition_result(state, tr, {'id': target['id'], **formal_evidence(state, target['id'], env)})
    return k.activate_transition(state, tr)


class KnowledgeTests(unittest.TestCase):
    def test_explanation_revision_reuses_only_current_formal_evidence(self):
        for status in ("candidate", "rejected", "suspended", "verified"):
            with self.subTest(status=status):
                ins = {"active_trust_environment": "TE-old", "trust_environments": {
                    "TE-old": {"id": "TE-old", "status": "active",
                               "toolchain": {"version": "fixture-old"}, "allowed_axioms": []}}}
                ins, run, kid, _ = add_knowledge(ins, {}, verified=False)
                if status != "candidate":
                    checked = formal_evidence(ins, kid)
                    if status == "rejected":
                        checked["status"] = "failed"
                    ins = kr.record_formal_result(ins, kid, checked, "TE-old", runtime=run)
                old_fid = ins["knowledge"][kid]["formal_result_id"]
                if status == "suspended":
                    ins["formal_results"][old_fid]["formal_use"] = "suspended"
                old_formal = deepcopy(ins["formal_results"][old_fid])
                changed, queued = revise_knowledge(ins, run, kid, {"summary": "Corrected summary"})
                replacement = next(row for row in changed["knowledge"].values()
                                   if row.get("supersedes") == kid)
                current_fid = replacement["formal_result_id"]
                reused = status == "verified"
                self.assertEqual(current_fid == old_fid, reused)
                self.assertEqual(changed["formal_results"][old_fid], old_formal)
                self.assertEqual([a["role"] for a in queued["queue"]
                                  if a.get("target") == replacement["id"]],
                                 ["identity_review" if reused else "formal_check"])
                self.assertFalse(any(a.get("target") == kid and a["role"] == "formal_check"
                                     for a in queued["queue"]))
                if not reused:
                    self.assertEqual(changed["formal_results"][current_fid]["verification"], {})
                    self.assertEqual(changed["formal_results"][current_fid]["publication_state"], "candidate")

    def test_nonformal_explanation_revision_still_returns_to_planning(self):
        ins, run, kid, _ = add_knowledge({}, {}, verified=False, lean_code="", declaration_names=[])
        changed, queued = revise_knowledge(ins, run, kid, {"summary": "Corrected observation"})
        replacement = next(row for row in changed["knowledge"].values()
                           if row.get("supersedes") == kid)
        self.assertIsNone(replacement["formal_result_id"])
        self.assertEqual([a["role"] for a in queued["queue"]
                          if a.get("target") == replacement["id"]], ["research_plan"])
    def test_candidate_dependency_not_promoted_by_prerequisite_reverification(self):
        ins, run, ids = knowledge_graph()
        ins = kr.set_assessment_use(ins, ids['ba'], 'suspended', 'requires review', 'reviewer')
        changed, _ = revise_knowledge(ins, run, ids['a'])
        replacement = next(r['id'] for r in changed['knowledge'].values() if r.get('supersedes') == ids['a'])
        changed, _ = seal_knowledge(changed, run, replacement)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])

    def test_revision_preserves_history_and_only_actual_dependencies_change(self):
        ins, run, ids = knowledge_graph()
        new, nrun = revise_knowledge(ins, run, ids['a'])
        replacement = next(row for row in new['knowledge'].values() if row.get('supersedes') == ids['a'])
        self.assertEqual(replacement['revision'], ins['knowledge'][ids['a']].get('revision', 1) + 1)
        self.assertEqual(new['identity_assessments'], ins['identity_assessments'])
        self.assertEqual(set(new['formal_results']), set(ins['formal_results']))
        for fid, formal in ins['formal_results'].items():
            self.assertEqual(new['formal_results'][fid]['verification'], formal['verification'])
        dependent_fid = ins['knowledge'][ids['b']]['formal_result_id']
        self.assertEqual(new['formal_results'][dependent_fid]['formal_use'], 'suspended')
        self.assertEqual(kr.proposal_view(ins, ids['a'])['statement'], 'True')
        self.assertEqual(new['knowledge'][ids['a']]['lifecycle'], 'superseded')
        self.assertFalse(k.assess_use(new['knowledge'][ids['b']], new)['valid'])
        self.assertTrue(k.assess_use(new['knowledge'][ids['c']], new)['valid'])
        self.assertFalse(nrun['tasks'][ids['task']]['assessment']['current'])
        self.assertEqual(nrun['tasks'][ids['unrelated']], run['tasks'][ids['unrelated']])
        self.assertFalse(new['goal_judgments'][0]['current'])
        replacement = next(r for r in new['knowledge'].values() if r.get('supersedes') == ids['a'])
        self.assertTrue(any(a['role'] == 'identity_review' and a.get('target') == replacement['id']
                            and a['reason'] == 'correction' for a in nrun['queue']))
        self.assertTrue(all(a['id'] == a['lineage_id'] for a in nrun['queue']))
        self.assertEqual(len({a['id'] for a in nrun['queue']}), len(nrun['queue']))

    def test_task_dependencies_are_strong_reassessment_edges(self):
        ins, run, ids = knowledge_graph()
        run['tasks'][ids['task']].update(inputs=[], dependencies=[ids['b']])
        _, changed = revise_knowledge(ins, run, ids['a'])
        self.assertFalse(changed['tasks'][ids['task']]['input_current'])
        self.assertEqual(changed['tasks'][ids['task']]['status'], 'completed')

    def test_terminal_history_and_unfinished_lifecycle_are_preserved(self):
        ins, run, ids = knowledge_graph()
        closed, planned = new_id('TK'), new_id('TK')
        disposition = {'kind': 'withdraw', 'reason': 'user withdrawal'}
        run['tasks'][closed] = {'id': closed, 'status': 'closed', 'inputs': [ids['b']], 'scope_disposition': disposition,
                               'assessment': {'decision': 'closed', 'current': True}}
        run['tasks'][planned] = {'id': planned, 'status': 'planned', 'inputs': [ids['b']]}
        _, changed = withdraw(ins, run, ids['a'])
        for tid, status in ((ids['task'], 'completed'), (closed, 'closed'), (planned, 'planned')):
            self.assertEqual(changed['tasks'][tid]['status'], status)
            self.assertFalse(changed['tasks'][tid]['input_current'])
        self.assertEqual(changed['tasks'][closed]['scope_disposition'], disposition)
        self.assertEqual(changed['tasks'][closed]['assessment'], {'decision': 'closed', 'current': False})

    def test_invalidation_preserves_record_and_relation_neighbor(self):
        ins, run, ids = knowledge_graph()
        new, nrun = withdraw(ins, run, ids['a'])
        self.assertEqual(new['knowledge'][ids['a']]['lifecycle'], 'withdrawn')
        self.assertEqual(new['knowledge'][ids['c']], ins['knowledge'][ids['c']])
        self.assertEqual(new['relations'][0]['status'], 'suspended')
        self.assertTrue(k.assess_use(new['knowledge'][ids['c']], new)['valid'])
        self.assertEqual(nrun['tasks'][ids['unrelated']], run['tasks'][ids['unrelated']])

    def test_withdrawn_record_retires_its_pending_checks(self):
        ins, run, ids = knowledge_graph()
        run['queue'] = [{'id': new_id('AC'), 'role': role, 'target': ids['a'], **extra} for role, extra in (
            ('formal_check', {}), ('identity_review', {}),
            ('supplemental_research', {'review_cycle_id': 'RC-review'}), ('maintenance', {}))]
        _, changed = withdraw(ins, run, ids['a'])
        self.assertEqual([a['role'] for a in changed['queue'] if a.get('target') == ids['a']], ['maintenance'])

    def test_basis_hash_covers_exact_family_record(self):
        ins, run, ids = knowledge_graph()
        xid = ins['knowledge'][ids['a']]['exposition_id']
        basis = k.capture_basis(ins, run, [ids['a'], xid, ids['task']])
        self.assertTrue(k.validate_basis(basis, ins, run)['valid'])
        ins['expositions'][xid]['items'][0]['text'] = 'changed'
        self.assertIn('hash_changed:' + xid, k.validate_basis(basis, ins, run)['reasons'])
        self.assertFalse(k.assess_use(ins['knowledge'][ids['a']], ins)['valid'])

    def test_source_locators_are_not_missing_record_ids(self):
        ins, run, ids = knowledge_graph()
        ins['knowledge'][ids['b']]['origin_refs'] = ['proposal:1', 'input/knowledge/KN-X.json', {'path': 'catalog.json', 'sha256': '0'}]
        self.assertEqual(k.plan_impact(ins, run, [ids['b']], [])['unresolved_refs'], [])
        ins['knowledge'][ids['b']]['dependencies'].append('KN-MISSING')
        self.assertIn('KN-MISSING', k.plan_impact(ins, run, [ids['b']], [])['unresolved_refs'])

    def test_system_propagation_applies_computed_impact_and_names_unresolved_refs(self):
        ins, run, ids = knowledge_graph()
        ins['knowledge'][ids['c']]['used_sources'] = [ids['a']]
        ins['knowledge'][ids['c']]['dependencies'].append('KN-MISSING')
        k.propagate(ins, run, [ids['a']], 'trust environment invalidated')
        event = run['history'][-1]
        self.assertEqual(event['kind'], 'knowledge_reassessment_required')
        self.assertIn(ids['c'], event['affected_ids'])
        self.assertIn('KN-MISSING', event['reason'])

    def test_known_source_propagates_but_locator_does_not(self):
        ins, run, ids = knowledge_graph()
        ins['knowledge'][ids['c']]['used_sources'] = ['proposal:1', 'input/knowledge/KN-X.json', ids['a']]
        plan = k.plan_impact(ins, run, [ids['a']], [])
        self.assertIn(ids['c'], plan['computed_impact'])
        self.assertNotIn('input/knowledge/KN-X.json', plan['unresolved_refs'])

    def test_source_currentness_and_reassessment_preserve_judgment(self):
        ins, run, ids = knowledge_graph()
        ins['sources'] = [{'name': 'paper', 'path': 'sources/paper', 'sha256': 'old'}]
        ins, run, kid, aid = add_knowledge(ins, run, source_refs=['paper'])
        saved = deepcopy(ins['identity_assessments'][aid])
        self.assertTrue(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        ins['sources'][0]['sha256'] = 'new'
        self.assertFalse(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        changed, _ = k.suspend_for_source_change(ins, run, kid, source_name='paper', reason='source changed', actor_ref='user')
        self.assertEqual(changed['identity_assessments'][aid], saved)
        ins['sources'][0]['sha256'] = changed['sources'][0]['sha256'] = 'old'
        self.assertTrue(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        self.assertFalse(k.assess_use(changed['knowledge'][kid], changed)['valid'])

    def test_partial_failure_keeps_old_environment(self):
        ins, _, ids = knowledge_graph()
        ins, env, tr = transition(ins)
        tr = k.record_transition_result(ins, tr, {'id': ids['a'], 'status': 'failed'})
        with self.assertRaises(ValueError): k.activate_transition(ins, tr)
        self.assertEqual(ins['active_trust_environment'], 'TE-old')

    def test_one_failure_in_complete_multi_target_batch_preserves_every_original_record(self):
        ins, _, _ = knowledge_graph()
        ins, env, tr = transition(ins)
        for target in tr['targets']:
            tr = k.record_transition_result(ins, tr, {'id': target['id'], **formal_evidence(ins, target['id'], env)})
        failed = tr['targets'][1]['id']
        tr = k.record_transition_result(ins, tr, {'id': failed, 'status': 'failed'})
        before = deepcopy(ins)
        with self.assertRaisesRegex(ValueError, 'all transition targets'):
            k.activate_transition(ins, tr)
        self.assertEqual(ins, before)

    def test_unknown_environment_rejected(self):
        ins, run, _ = knowledge_graph()
        with self.assertRaises(ValueError): k.begin_transition(ins, 'TE-missing')
        with self.assertRaises(ValueError): k.invalidate_environment(ins, run, 'TE-missing', 'bad')

    def test_complete_transition_preserves_old_evidence_and_changes_links(self):
        ins, _, ids = knowledge_graph()
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertEqual(changed['active_trust_environment'], env)
        self.assertEqual(changed['trust_environments']['TE-old']['status'], 'superseded')
        for rid, row in ins['formal_results'].items(): self.assertEqual(changed['formal_results'][rid], row)
        for rid, row in ins['identity_assessments'].items(): self.assertEqual(changed['identity_assessments'][rid], row)
        for kid in (ids['a'], ids['b'], ids['c']):
            self.assertTrue(k.assess_use(changed['knowledge'][kid], changed)['valid'])
            self.assertNotEqual(changed['knowledge'][kid]['formal_result_id'], ins['knowledge'][kid]['formal_result_id'])

    def test_invalidated_environment_recovery_rechecks_all_accepted_results(self):
        ins, run, ids = knowledge_graph()
        stopped, _ = k.invalidate_environment(ins, run, 'TE-old', 'kernel defect')
        import jsonschema
        from do_math.record_schemas import RECORDS
        jsonschema.validate(stopped['trust_environments']['TE-old'], RECORDS['trust_environments'])
        self.assertEqual(stopped['trust_environments']['TE-old']['invalidated_reason'], 'kernel defect')
        self.assertIsNone(stopped['active_trust_environment'])
        stopped, env, tr = transition(stopped)
        self.assertEqual({t['id'] for t in tr['targets']}, {ids['a'], ids['b'], ids['c']})
        self.assertTrue(all(t['previous_environment_ids'] == ['TE-old'] for t in tr['targets']))
        recovered = finish_transition(stopped, env, tr)
        self.assertEqual(recovered['trust_environments']['TE-old']['status'], 'invalid')
        for kid in (ids['a'], ids['b'], ids['c']): self.assertTrue(k.assess_use(recovered['knowledge'][kid], recovered)['valid'])

    def test_recovery_does_not_promote_unchecked_or_withdrawn(self):
        ins, run, ids = knowledge_graph()
        ins, run, pending, _ = add_knowledge(ins, run, verified=False)
        ins, run = withdraw(ins, run, ids['c'])
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'bad')
        ins, env, tr = transition(ins)
        self.assertNotIn(pending, {t['id'] for t in tr['targets']})
        self.assertNotIn(ids['c'], {t['id'] for t in tr['targets']})
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][pending], changed)['valid'])
        self.assertEqual(changed['knowledge'][ids['c']]['lifecycle'], 'withdrawn')

    def test_recovery_preserves_later_semantic_suspension(self):
        ins, run, ids = knowledge_graph()
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        ins = kr.set_assessment_use(ins, ids['aa'], 'suspended', 'meaning challenged', 'reviewer')
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['a']], changed)['valid'])
        self.assertTrue(k.assess_use(changed['knowledge'][ids['c']], changed)['valid'])

    def test_environment_recovery_cannot_clear_a_later_source_reassessment(self):
        ins, run, _ = knowledge_graph()
        ins['sources'] = [{'name': 'paper', 'path': 'sources/paper', 'sha256': 'old'}]
        ins, run, kid, aid = add_knowledge(ins, run, source_refs=['paper'])
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        ins['sources'][0]['sha256'] = 'new'
        ins, run = k.suspend_for_source_change(ins, run, kid, source_name='paper',
            reason='source requires independent reassessment', actor_ref='user')
        # Restoring bytes resolves currentness, not the separate review obligation.
        ins['sources'][0]['sha256'] = 'old'
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][kid], changed)['valid'])

    def test_recovery_preserves_dependency_on_withdrawn_knowledge(self):
        ins, run, ids = knowledge_graph()
        ins, run = withdraw(ins, run, ids['a'])
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])
        self.assertEqual(changed['knowledge'][ids['a']]['lifecycle'], 'withdrawn')

    def test_history_is_not_a_current_dependency(self):
        ins, run, ids = knowledge_graph()
        ins['knowledge'][ids['b']]['history'] = [{'previous': {'dependencies': [ids['c']]}}]
        changed, _ = revise_knowledge(ins, run, ids['c'])
        self.assertTrue(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])

    def test_fresh_plan_is_applied_without_recomputing_the_closure(self):
        ins, run, ids = knowledge_graph()
        with patch.object(k, 'plan_impact', wraps=k.plan_impact) as plans:
            changed, _ = withdraw(ins, run, ids['a'])
        # One producer declaration and one plan inside invalidate_knowledge.
        self.assertEqual(plans.call_count, 2)
        self.assertEqual(changed['knowledge'][ids['a']]['lifecycle'], 'withdrawn')

    def test_observed_propagation_plans_twice_and_applies_to_the_callers_copy(self):
        ins, run, _ = knowledge_graph()
        with patch.object(k, 'plan_impact', wraps=k.plan_impact) as plans:
            _, changed_run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        # Preview and plan inside propagate; no third recomputation on apply.
        self.assertEqual(plans.call_count, 2)
        self.assertEqual(changed_run['history'][-1]['kind'], 'knowledge_reassessment_required')
        self.assertNotIn('knowledge_reassessment_required', [h.get('kind') for h in run['history']])

    def test_research_reuse_keeps_dependency_and_source_currentness(self):
        from do_math.knowledge import assess_research_use
        from do_math.knowledge_records import create_candidate
        instance = {'sources': [{'id': 'S', 'name': 'data', 'sha256': 'a'*64, 'path': 'data'}],
            'kind_definitions': {'KD': {'id': 'KD', 'status': 'active'}}}
        instance, parent = create_candidate(instance, {'id': 'KN-parent', 'kind_definition_id': 'KD',
            'statement': 'Finite observation', 'source_basis': [{'name': 'data', 'sha256': 'a'*64}]},
            source_ref='S', actor_ref='AUTHOR')
        instance, child = create_candidate(instance, {'id': 'KN-child', 'kind_definition_id': 'KD',
            'statement': 'Uses that observation', 'dependencies': [parent]}, source_ref='S', actor_ref='AUTHOR')
        self.assertTrue(assess_research_use(instance['knowledge'][child], instance)['valid'])
        instance['sources'][0]['sha256'] = 'b'*64
        self.assertFalse(assess_research_use(instance['knowledge'][child], instance)['valid'])

    def test_knowledge_input_exposes_exact_formal_and_identity_records(self):
        from do_math.knowledge_records import reader_view
        instance, _, kid, aid = verified_knowledge()
        view = reader_view(instance, kid)
        self.assertEqual(view['formal_result']['id'], view['formal_result_id'])
        self.assertEqual(view['identity_assessments'][0]['id'], aid)
        self.assertEqual(view['assessment_uses'][0]['assessment_id'], aid)


class KnowledgeRecordTests(unittest.TestCase):
    @category('lean')
    def test_installed_lean_extracts_transitive_constants(self):
        command = [os.environ.get("DO_MATH_KNOWLEDGE_TEST_LEAN", str(portable_bin(toolchain_root()) / "lean.exe"))]
        if not Path(command[0]).is_file():
            self.skipTest("installed Lean is unavailable")
        # Use the installed compiler through its actual local Job transport.
        with tempfile.TemporaryDirectory() as directory:
            result = verify_lean(source="def base : Nat := 1\ndef mid : Nat := base\ntheorem leaf : mid = base := rfl",
                declarations=["leaf"], workspace=Path(directory), lean_command=command)
        self.assertEqual(result["status"], "verified", result)
        self.assertIn("dependency_closure", result)
        self.assertIn("base", result["dependency_closure"]["leaf"])
        self.assertIn("mid", result["dependency_closure"]["leaf"])
        self.assertIn("leaf", result["declaration_evidence"])

    def test_import_separates_formal_and_exposition_authority(self):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref="source", actor_ref="producer")
        record = state["knowledge"][kid]
        self.assertNotIn("lean_code", record)
        self.assertNotIn("formal", record)
        self.assertIn(record["formal_result_id"], state["formal_results"])
        self.assertIn(record["exposition_id"], state["expositions"])

    def test_installed_relation_kinds_are_active_from_installation(self):
        state = knowledge_io.ensure_ontology({})
        installed = {row["token"] for row in knowledge_io.BUILTIN_DEFINITIONS if row["family"] == "relation"}
        catalog = knowledge_io.catalog_definitions(state)["relations"]
        self.assertEqual({row["token"] for row in catalog}, installed)
        self.assertTrue(all(row["status"] == "active" and row["builtin"] for row in catalog))
        supports = next(row for row in catalog if row["token"] == "supports")
        with self.assertRaisesRegex(ValueError, "already defined"):
            knowledge_io.register_kind_definition(state, {key: supports[key] for key in
                ("family", "token", "meaning", "constraints")}, source_ref="source", actor_ref="producer")

    def test_kind_registration_requires_explicit_check_and_activation(self):
        definition = dict(family="knowledge", token="bounded_result", meaning="A bounded result", constraints={})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref="source", actor_ref="producer")
        definition = next(r for r in state["kind_definitions"].values() if r["token"] == token)
        self.assertEqual(definition["status"], "candidate")

    def test_kind_definitions_use_record_ids_and_allow_explicit_replacement(self):
        state = knowledge_io.ensure_ontology({})
        self.assertTrue(all(key == value["id"] for key, value in state["kind_definitions"].items()))
        state, runtime = knowledge_io.withdraw_kind_definition(state, {}, "knowledge", "theorem", reason="replacement", actor_ref="review")
        state, token = knowledge_io.register_kind_definition(state,
            {"family": "knowledge", "token": "theorem", "meaning": "Revised theorem kind", "constraints": {}},
            source_ref="revision", actor_ref="author")
        replacement = next(d for d in state["kind_definitions"].values() if d["token"] == token and d["status"] == "candidate")
        self.assertIn(replacement["supersedes"], state["kind_definitions"])

    def test_impact_planning_does_not_mutate_and_includes_relations(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"}},
                 "relations": [{"id": "RL-a", "source": "KN-a", "target": "KN-a", "status": "active"}]}
        before = copy.deepcopy(state)
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["RL-a"])
        self.assertEqual(state, before)
        self.assertIn("RL-a", plan["computed_impact"])

    def test_explanation_revision_preserves_formal_evidence_and_old_judgment(self):
        state, runtime, kid, aid = verified_knowledge()
        formal = copy.deepcopy(state["formal_results"])
        assessment = copy.deepcopy(state["identity_assessments"][aid])
        declared = [aid, next(u["id"] for u in state["assessment_uses"].values() if u["assessment_id"] == aid)]
        revised, _ = knowledge.revise_knowledge(state, runtime, kid, {"summary": "Revised summary"},
            reason="clarify", actor_ref="author", declared_impact=declared)
        self.assertEqual(revised["formal_results"], formal)
        self.assertEqual(revised["identity_assessments"][aid], assessment)
        self.assertEqual(revised["knowledge"][kid]["lifecycle"], "superseded")
        replacements = [r for r in revised["knowledge"].values() if r.get("supersedes") == kid]
        self.assertEqual(len(replacements), 1)
        self.assertFalse(knowledge.assess_use(replacements[0], revised)["valid"])
        old_use = next(u for u in revised["assessment_uses"].values() if u["assessment_id"] == aid)
        self.assertEqual(old_use["status"], "suspended")
        self.assertEqual(revised["expositions"][state["knowledge"][kid]["exposition_id"]]["lifecycle"], "superseded")

    def test_decision_reference_reports_actual_split_environment(self):
        state, runtime, kid, aid = verified_knowledge()
        self.assertEqual(knowledge.decision_reference(state["knowledge"][kid], state)["trust_environment_id"], "TE-test")

    def test_revision_reuses_candidate_kind_and_dependency_validation(self):
        state, runtime, kid, aid = verified_knowledge()
        declared = [aid, next(u["id"] for u in state["assessment_uses"].values() if u["assessment_id"] == aid)]
        for changes in ({"kind": "unregistered_kind"}, {"dependencies": ["KN-missing"]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                knowledge.revise_knowledge(state, runtime, kid, changes, reason="revision", actor_ref="author", declared_impact=declared)

    def test_revision_changes_name_only_authored_fields(self):
        # The producer check and the application share this one rule.
        for field in sorted(knowledge.AUTHORED_FIELDS):
            with self.subTest(field=field):
                knowledge.validate_changes({field: "value"})
        for field in ("id", "status", "formal", "verified_at", "identity_assessment", "producer_execution_ids",
                      "unknown_field"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                knowledge.validate_changes({field: "value"})

    def test_common_execution_names_exactly_the_authored_fields(self):
        """「공통 실행」 gives revision authors the closed field set that validate_changes accepts."""
        import re
        text = (Path(__file__).resolve().parents[2] / 'references' / '공통-실행.md').read_text(encoding='utf-8')
        match = re.search(r'`changes`의 키는 저작 필드 (.+?) 가운데서만 고른다', text)
        self.assertIsNotNone(match)
        self.assertEqual(set(re.findall(r'`(\w+)`', match.group(1))), knowledge.AUTHORED_FIELDS)

    def test_import_captures_required_source_and_rejects_unknown_source(self):
        state = {"sources": [{"name": "paper", "path": "research/sources/paper.txt", "sha256": "original"}]}
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate(state, {}, knowledge_candidate(source_refs=["absent"]), source_ref="submission", actor_ref="author")
        changed, _, kid = knowledge_io.import_candidate(state, {}, knowledge_candidate(source_refs=["paper"]), source_ref="submission", actor_ref="author")
        self.assertEqual(changed["knowledge"][kid]["source_basis"][0]["sha256"], "original")

    def test_assessment_suspension_is_local_and_reversible(self):
        state, runtime, kid, aid = verified_knowledge()
        before = copy.deepcopy(state["identity_assessments"])
        suspended = kr.set_assessment_use(state, aid, "suspended", "review defect", "reviewer")
        self.assertEqual(suspended["identity_assessments"], before)
        self.assertFalse(knowledge.assess_use(suspended["knowledge"][kid], suspended)["valid"])
        self.assertTrue(kr.knowledge_view(suspended)[0]["formal_valid"])
        restored = kr.set_assessment_use(suspended, aid, "active", "defect resolved", "reviewer")
        self.assertTrue(knowledge.assess_use(restored["knowledge"][kid], restored)["valid"])

    def test_independent_expositions_share_one_formal_result(self):
        state, runtime, kid, aid = verified_knowledge()
        fid = state["knowledge"][kid]["formal_result_id"]
        data = knowledge_candidate(formal_result_ref=fid)
        data["explanation"] = "A second explanation"
        state, runtime, other = knowledge_io.import_candidate(state, runtime, data, source_ref="second-source", actor_ref="other-author")
        self.assertEqual(len(state["formal_results"]), 1)
        self.assertEqual(runtime["queue"][-1]["role"], "identity_review")
        state, second_assessment = kr.record_identity_assessment(state, other,
            {"decision": "match", "basis": kr.identity_basis(state, other)}, "policy:1", runtime=runtime)
        state = kr.set_assessment_use(state, aid, "suspended", "first explanation defect", "reviewer")
        self.assertFalse(knowledge.assess_use(state["knowledge"][kid], state)["valid"])
        self.assertTrue(knowledge.assess_use(state["knowledge"][other], state)["valid"])

    def test_mathematical_relation_consumes_separate_result_and_assessment(self):
        state, runtime, kid, aid = verified_knowledge()
        token = "formally_implies"
        fid = state["knowledge"][kid]["formal_result_id"]
        claim = {"kind": token, "source": kid, "target": kid, "confirmed_scope": "reflexive implication"}
        state["formal_results"][fid]["relation_claim"] = claim
        state["identity_assessments"][aid]["relation_claim"] = claim
        relation = {**claim, "formal_result_refs": [fid], "assessment_refs": [aid], "evidence_refs": [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)["valid"])
        stopped = kr.set_assessment_use(state, aid, "suspended", "recheck", "reviewer")
        self.assertFalse(knowledge_io.validate_relation(stopped, relation)["valid"])

    def test_relation_claim_is_bound_through_import_and_identity(self):
        state, runtime, kid, aid = verified_knowledge()
        token = "formally_implies"
        claim = {"kind": token, "source": kid, "target": kid, "confirmed_scope": "reflexive"}
        state, runtime, proof = knowledge_io.import_candidate(state, runtime, knowledge_candidate(relation_claim=claim), source_ref="source", actor_ref="author")
        verification = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        state = kr.record_formal_result(state, proof, verification, "TE-test", runtime=runtime)
        state, identity = kr.record_identity_assessment(state, proof,
            {"decision": "match", "basis": kr.identity_basis(state, proof)}, "policy:1", runtime=runtime)
        relation = {**claim, "formal_result_refs": [state["knowledge"][proof]["formal_result_id"]],
                    "assessment_refs": [identity], "evidence_refs": [kid]}
        self.assertTrue(knowledge_io.validate_relation(state, relation)["valid"])
        state["knowledge"][kid]["title"] = "changed endpoint"
        self.assertFalse(knowledge_io.validate_relation(state, relation)["valid"])

    def test_trust_transition_uses_split_results_and_compares_evidence(self):
        state, runtime, kid, aid = verified_knowledge()
        state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
        transition = knowledge.begin_transition(state, "TE-next")
        self.assertEqual(len(transition["targets"]), 1)
        self.assertIn("dependency_closure", transition["targets"][0])
        self.assertIn("axioms", transition["targets"][0])
        result = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        result.update(id=kid, toolchain={"version": "next"})
        transition = knowledge.record_transition_result(state, transition, result)
        activated = knowledge.activate_transition(state, transition)
        self.assertEqual(activated["active_trust_environment"], "TE-next")
        self.assertTrue(knowledge.assess_use(activated["knowledge"][kid], activated)["valid"])
        self.assertEqual(activated["identity_assessments"][aid], state["identity_assessments"][aid])
        result["dependency_evidence"]["True"] = exact_content_hash("changed-type")
        transition = knowledge.record_transition_result(state, knowledge.begin_transition(state, "TE-next"), result)
        with self.assertRaises(ValueError):
            knowledge.activate_transition(state, transition)

    def test_identity_review_cannot_replace_missing_new_kernel_evidence(self):
        state, runtime, kid, aid = verified_knowledge()
        state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
        transition = knowledge.begin_transition(state, "TE-next")
        result = copy.deepcopy(state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"])
        result.update(id=kid, toolchain={"version": "next"})
        result.pop("dependency_closure")
        result["identity_review"] = {"decision": "match", "result_digest": exact_content_hash(result), "review_ref": "review", "policy_ref": "policy:1"}
        transition = knowledge.record_transition_result(state, transition, result)
        with self.assertRaises(ValueError):
            knowledge.activate_transition(state, transition)

    def test_rejects_unapproved_environment_and_replayed_identity_basis(self):
        state, runtime, kid, aid = verified_knowledge()
        assessment = {"decision": "match", "basis": {"formal": "old", "exposition": "old"}}
        with self.assertRaises(ValueError):
            kr.record_identity_assessment(state, kid, assessment, "policy:1", runtime=runtime)
        result = state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"]
        state["trust_environments"]["TE-test"]["status"] = "registered"
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, result, "TE-test", runtime=runtime)

    def test_storage_registration_roundtrip_uses_split_family_files(self):
        from do_math.repository import ResearchRepository
        from do_math.system_clock import new_id
        from do_math.state_contract import default_state_contract
        contract = default_state_contract()
        with tempfile.TemporaryDirectory() as directory:
            # Real Git and domain validators; compiler/reviewer/approval evidence is synthetic.
            from research_fixtures import trust_environment, trust_fixture
            from do_math.trust_validation import check_environment, environment_errors
            from do_math.execution_profiles import build_profiles, profile_ref
            from do_math.configuration import DEFAULT_CONFIG
            from do_math import activities, execution_lifecycle
            from do_math.review_cycle import accept_result, identity_assessment, next_actions
            from review_fixtures import scoped_start
            environment, binding = trust_environment(trust_fixture(Path(directory), ['synthetic-lean']),
                                                     environment_id='TE-test', source_ref='synthetic:approval')
            self.assertEqual(environment_errors(environment, binding), [])
            self.assertEqual(check_environment(environment, binding)['status'], 'verified')
            state, runtime, kid, _ = verified_knowledge(environment, binding=binding, identity=False)
            profiles = build_profiles(DEFAULT_CONFIG)
            profile = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'identity_review')
            state.update(execution_profiles={profile['id']: profile}, capacity_constraints=profiles['capacity_constraints'])
            activity = activities.open_activity(runtime, activity_id=new_id('AT'), activity_kind='identity_review',
                owner_ref=kid, input_refs=[kid], opened_at='2026-09-20T00:00:00Z')
            cycle = scoped_start({**kr.proposal_view(state, kid), 'revision': 1}, reviewers=2)
            for _ in range(2):
                action = next_actions(cycle)[0]
                eid = new_id('EX')
                output = dict(proposal_digest=cycle['proposal_digest'], summary='Synthetic complete review',
                    used_sources=['proposal'], questions=[], decision='match', scope_complete=True, findings=[])
                cycle = accept_result(cycle, action, output, eid)
                execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
                    actor_kind='ai', input_manifest={'proposal_digest': cycle['proposal_digest']},
                    profile_ref=profile_ref(profile), created_at='2026-09-20T00:00:00Z')
                execution.update(role='identity_review')
                activities.assign_execution(runtime, activity['id'], execution)
                for status in ('starting', 'running'):
                    execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
                execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:review'}
                execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z')
                execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
            self.assertEqual(cycle['status'], 'completed')
            cycle.update(id=new_id('RC'), knowledge_id=kid, identity_basis=kr.identity_basis(state, kid), policy_ref='policy:fixture')
            runtime['review_cycles'] = {cycle['id']: cycle}
            assessment = identity_assessment(cycle, reason='Synthetic sealed review')
            state, aid = kr.record_identity_assessment(state, kid,
                {**assessment, 'basis': cycle['identity_basis']}, cycle['policy_ref'], runtime=runtime)
            git_init(directory)
            repo = ResearchRepository(Path(directory), new_id("RI"), contract=contract)
            # Every stored state passes the current lifecycle gate.
            from research_fixtures import current_state
            state, runtime = current_state(state, runtime)
            repo.initialize(state, runtime)
            head, loaded, loaded_runtime = repo.load()
            self.assertEqual(loaded["formal_results"], state["formal_results"])
            self.assertEqual(loaded["identity_assessments"], state["identity_assessments"])
            self.assertTrue(knowledge.assess_use(loaded["knowledge"][kid], loaded)["valid"])

    def test_import_rejects_malformed_registry_id(self):
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate({}, {}, knowledge_candidate(id="KN-not-a-ulid"), source_ref="source", actor_ref="author")

    def test_formal_verification_requires_dependency_body_evidence(self):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref="source", actor_ref="producer")
        fixture, _, _, _ = verified_knowledge()
        state.update(active_trust_environment="TE-test", trust_environments=fixture["trust_environments"])
        verification = copy.deepcopy(next(iter(fixture["formal_results"].values()))["verification"])
        verification.pop("dependency_evidence")
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, verification, "TE-test", runtime=runtime)

    def test_dependency_body_evidence_is_one_hash_table_over_the_declared_closures(self):
        state, runtime, kid = knowledge_io.import_candidate({}, {}, knowledge_candidate(), source_ref="source", actor_ref="producer")
        fixture, _, _, _ = verified_knowledge()
        state.update(active_trust_environment="TE-test", trust_environments=fixture["trust_environments"])
        verification = copy.deepcopy(next(iter(fixture["formal_results"].values()))["verification"])
        closure = verification["dependency_closure"]["truth"]
        table = {name: exact_content_hash(name) for name in closure}
        accepted = kr.record_formal_result(state, kid, {**verification, "dependency_evidence": table}, "TE-test", runtime=runtime)
        fid = accepted["knowledge"][kid]["formal_result_id"]
        self.assertEqual(accepted["formal_results"][fid]["verification"]["dependency_evidence"], table)
        for invalid in ({"truth": table}, {name: table[name] for name in closure[:-1]},
                        {**table, closure[0]: "not-a-hash"}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                kr.record_formal_result(state, kid, {**verification, "dependency_evidence": invalid}, "TE-test", runtime=runtime)

    def test_transition_targets_store_the_dependency_hash_table(self):
        from do_math.state_contract import default_state_contract, validate_record
        state, runtime, kid, aid = verified_knowledge()
        state["trust_environments"]["TE-next"] = {"id": "TE-next", "status": "registered", "toolchain": {"version": "next"}, "allowed_axioms": []}
        transition = knowledge.begin_transition(state, "TE-next")
        checker = default_state_contract().family("runtime", "trust_transitions").checker
        validate_record(checker, transition, "transition")
        nested = copy.deepcopy(transition)
        nested["targets"][0]["dependency_evidence"] = {"truth": transition["targets"][0]["dependency_evidence"]}
        with self.assertRaises(ValueError):
            validate_record(checker, nested, "transition")

    def test_changed_approved_toolchain_rejects_before_source_execution(self):
        from do_math import formal
        binary_hash = hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()
        approved = dict(executable=sys.executable, sha256=binary_hash, configured_command=[sys.executable],
            version='approved-version', version_exit=0, project=None,
            verifier_sha256=hashlib.sha256(Path(formal.__file__).read_bytes()).hexdigest(),
            verifier_path=str(Path(formal.__file__).resolve()),
            executables={str(Path(sys.executable).resolve()): binary_hash})
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "lean.exe"
            executable.write_bytes(b"approved executable bytes")
            command = [str(executable)]
            digest = hashlib.sha256(executable.read_bytes()).hexdigest()
            approved.update(executable=str(executable), sha256=digest, configured_command=command,
                            executables={str(executable.resolve()): digest})
            executable.write_bytes(b"changed executable bytes")
            with patch("do_math.formal._job_run", side_effect=AssertionError("changed executable must not start")) as run:
                result = verify_lean(source=knowledge_candidate()["lean_code"], declarations=["truth"], workspace=Path(directory),
                    lean_command=command, expected_toolchain=approved)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "approved toolchain changed before execution")
        run.assert_not_called()

    def test_publication_reads_runtime_transition_barrier(self):
        state, runtime, kid, aid = verified_knowledge()
        runtime["trust_transitions"] = {"TR-test": {"status": "checking"}}
        result = state["formal_results"][state["knowledge"][kid]["formal_result_id"]]["verification"]
        with self.assertRaises(ValueError):
            kr.record_formal_result(state, kid, result, "TE-test", runtime=runtime)
        with self.assertRaises(ValueError):
            kr.record_identity_assessment(state, kid, {"decision": "match", "basis": kr.identity_basis(state, kid)}, "policy:1", runtime=runtime)

    def test_impact_mismatch_and_staleness_reject_without_mutation(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"},
                               "KN-b": {"id": "KN-b", "lifecycle": "active"}},
                 "relations": [{"id": "RL-a", "source": "KN-a", "target": "KN-a", "status": "active"}]}
        before = copy.deepcopy(state)
        # A declared record beyond the computed closure needs an independent confirmation.
        mismatch = knowledge.plan_impact(state, {}, ["KN-a"], ["RL-a", "KN-b"])
        with self.assertRaises(ValueError):
            knowledge.apply_impact(state, {}, mismatch, reason="change")
        self.assertEqual(state, before)
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["RL-a"])
        state["relations"][0]["target"] = "KN-changed"
        with self.assertRaises(ValueError):
            knowledge.apply_impact(state, {}, plan, reason="change")

    def test_impact_tracks_origin_refs_and_missing_split_refs(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"},
                               "KN-b": {"id": "KN-b", "lifecycle": "active", "origin_refs": ["KN-a"], "formal_result_refs": ["FR-missing"]}}}
        plan = knowledge.plan_impact(state, {}, ["KN-a"], ["KN-b"])
        self.assertIn("KN-b", plan["computed_impact"])
        self.assertIn("FR-missing", plan["unresolved_refs"])

    def test_impact_preserves_terminal_task_and_suspends_its_judgment(self):
        state = {"knowledge": {"KN-a": {"id": "KN-a", "lifecycle": "active"}},
                 "goal_judgments": [{"id": "GJ-a", "used_sources": ["KN-a"], "current": True}]}
        runtime = {"tasks": {"TK-a": {"id": "TK-a", "status": "completed", "inputs": ["KN-a"], "assessment": {"current": True}}}}
        plan = knowledge.plan_impact(state, runtime, ["KN-a"], ["TK-a", "GJ-a"])
        changed, run = knowledge.apply_impact(state, runtime, plan, reason="premise changed")
        self.assertEqual(run["tasks"]["TK-a"]["status"], "completed")
        self.assertFalse(run["tasks"]["TK-a"]["assessment"]["current"])
        self.assertFalse(changed["goal_judgments"][0]["current"])

    def test_kind_constraints_and_withdrawal(self):
        definition = dict(family="knowledge", token="bounded_result", meaning="A bounded result",
                          constraints={"allowed_epistemic_statuses": ["tentative"], "required_fields": ["confirmed_scope"]})
        state, token = knowledge_io.register_kind_definition({}, definition, source_ref="source", actor_ref="author")
        with self.assertRaises(ValueError):
            knowledge_io.activate_kind_definition(state, "knowledge", token, approval_ref="review", actor_ref="reviewer")
        state = knowledge_io.check_kind_definition(state, "knowledge", token, check_ref="check", actor_ref="checker")
        state = knowledge_io.activate_kind_definition(state, "knowledge", token, approval_ref="review", actor_ref="reviewer")
        data = knowledge_candidate(); data["kind"] = token
        with self.assertRaises(ValueError):
            knowledge_io.import_candidate(state, {}, data, source_ref="source", actor_ref="author")
        data.update(epistemic_status="tentative", confirmed_scope="finite case")
        state, runtime, kid = knowledge_io.import_candidate(state, {}, data, source_ref="source", actor_ref="author")
        state, runtime = knowledge_io.withdraw_kind_definition(state, runtime, "knowledge", token, reason="bad semantics", actor_ref="reviewer")
        self.assertTrue(state["knowledge"][kid]["kind_use_suspended"])


if __name__ == '__main__': unittest.main(verbosity=2)
