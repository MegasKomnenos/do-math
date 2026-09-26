"""Currentness contracts; kernel evidence in these domain fixtures is a test double."""
from copy import deepcopy
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
from do_math.repository import new_id


def candidate(**changes):
    value = dict(kind='theorem', title='Truth', statement='True', explanation='Truth holds',
                 summary='Truth', lean_code='theorem truth : True := True.intro',
                 declaration_names=['truth'], dependencies=[])
    value.update(changes)
    return value


def evidence(state, kid, env='TE-old'):
    formal = state['formal_results'][state['knowledge'][kid]['formal_result_id']]
    names = formal['declaration_names']
    return dict(status='verified', source_sha256=hashlib.sha256(formal['lean_code'].encode()).hexdigest(),
        declarations=names, toolchain=deepcopy(state['trust_environments'][env]['toolchain']),
        axioms={n: [] for n in names}, dependency_closure={n: ['True', 'True.intro'] for n in names},
        dependency_evidence={n: {'True': 'fixture-type', 'True.intro': 'fixture-value'} for n in names},
        declaration_evidence={n: {'type': 'fixture-type', 'value': 'fixture-proof'} for n in names})


def seal(state, runtime, kid, env='TE-old'):
    state = kr.record_formal_result(state, kid, evidence(state, kid, env), env, runtime=runtime)
    return kr.record_identity_assessment(state, kid,
        {'decision': 'match', 'basis': kr.identity_basis(state, kid)}, 'policy:fixture', runtime=runtime)


def add(state, runtime, *, verified=True, **changes):
    state, runtime, kid = io.import_candidate(state, runtime, candidate(**changes), source_ref='fixture', actor_ref='producer')
    aid = None
    if verified: state, aid = seal(state, runtime, kid)
    return state, runtime, kid, aid


def fixture():
    state = {'active_trust_environment': 'TE-old', 'trust_environments': {
        'TE-old': {'id': 'TE-old', 'status': 'active', 'toolchain': {'version': 'fixture-old'}, 'allowed_axioms': [],
                   'source_ref': 'fixture:trust', 'toolchain_record': {'path': str(Path.cwd() / 'records' / ('TC-' + '0' * 64 + '.json')),
                                                                        'id': 'TC-' + '0' * 64}}}}
    runtime = {'tasks': {}, 'queue': [], 'history': []}
    state, runtime, a, aa = add(state, runtime)
    state, runtime, b, ba = add(state, runtime, dependencies=[a])
    state, runtime, c, ca = add(state, runtime)
    relation, goal, task, unrelated = (new_id(p) for p in ('RL', 'GJ', 'TK', 'TK'))
    state['relations'] = [{'id': relation, 'source': a, 'target': c, 'status': 'active'}]
    state['goal_judgments'] = [{'id': goal, 'used_sources': [b], 'current': True}]
    runtime['tasks'] = {task: {'id': task, 'status': 'completed', 'inputs': [b], 'assessment': {'decision': 'completed', 'current': True}},
                       unrelated: {'id': unrelated, 'status': 'completed', 'inputs': [c]}}
    return state, runtime, dict(a=a, b=b, c=c, aa=aa, ba=ba, ca=ca, relation=relation, goal=goal, task=task, unrelated=unrelated)


def declaration(state, runtime, roots):
    # Model a complete producer declaration; tests separately assert its locality.
    return k.plan_impact(state, runtime, roots, [])['computed_impact']


def revise(state, runtime, kid, changes=None):
    changes = changes or {'statement': 'Revised statement'}
    return k.revise_knowledge(state, runtime, kid, changes, reason='correction', actor_ref='author',
        declared_impact=declaration(state, runtime, k.revision_roots(state, kid)))


def withdraw(state, runtime, kid):
    return k.invalidate_knowledge(state, runtime, kid, reason='false', actor_ref='reviewer',
        declared_impact=declaration(state, runtime, [kid]))


def transition(state):
    state, env = k.register_environment(state, {'version': 'fixture-new'}, [])
    return state, env, k.begin_transition(state, env)


def finish_transition(state, env, tr):
    for target in tr['targets']:
        tr = k.record_transition_result(state, tr, {'id': target['id'], **evidence(state, target['id'], env)})
    return k.activate_transition(state, tr)


class KnowledgeTests(unittest.TestCase):
    def test_explanation_revision_reuses_only_current_formal_evidence(self):
        for status in ("candidate", "rejected", "suspended", "verified"):
            with self.subTest(status=status):
                ins = {"active_trust_environment": "TE-old", "trust_environments": {
                    "TE-old": {"id": "TE-old", "status": "active",
                               "toolchain": {"version": "fixture-old"}, "allowed_axioms": []}}}
                ins, run, kid, _ = add(ins, {}, verified=False)
                if status != "candidate":
                    checked = evidence(ins, kid)
                    if status == "rejected":
                        checked["status"] = "failed"
                    ins = kr.record_formal_result(ins, kid, checked, "TE-old", runtime=run)
                old_fid = ins["knowledge"][kid]["formal_result_id"]
                if status == "suspended":
                    ins["formal_results"][old_fid]["formal_use"] = "suspended"
                old_formal = deepcopy(ins["formal_results"][old_fid])
                changed, queued = revise(ins, run, kid, {"summary": "Corrected summary"})
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
        ins, run, kid, _ = add({}, {}, verified=False, lean_code="", declaration_names=[])
        changed, queued = revise(ins, run, kid, {"summary": "Corrected observation"})
        replacement = next(row for row in changed["knowledge"].values()
                           if row.get("supersedes") == kid)
        self.assertIsNone(replacement["formal_result_id"])
        self.assertEqual([a["role"] for a in queued["queue"]
                          if a.get("target") == replacement["id"]], ["research_plan"])
    def test_candidate_dependency_not_promoted_by_prerequisite_reverification(self):
        ins, run, ids = fixture()
        ins = kr.set_assessment_use(ins, ids['ba'], 'suspended', 'requires review', 'reviewer')
        changed, _ = revise(ins, run, ids['a'])
        replacement = next(r['id'] for r in changed['knowledge'].values() if r.get('supersedes') == ids['a'])
        changed, _ = seal(changed, run, replacement)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])

    def test_revision_preserves_history_and_only_actual_dependencies_change(self):
        ins, run, ids = fixture()
        new, nrun = revise(ins, run, ids['a'])
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
        ins, run, ids = fixture()
        run['tasks'][ids['task']].update(inputs=[], dependencies=[ids['b']])
        _, changed = revise(ins, run, ids['a'])
        self.assertFalse(changed['tasks'][ids['task']]['input_current'])
        self.assertEqual(changed['tasks'][ids['task']]['status'], 'completed')

    def test_terminal_history_and_unfinished_lifecycle_are_preserved(self):
        ins, run, ids = fixture()
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
        ins, run, ids = fixture()
        new, nrun = withdraw(ins, run, ids['a'])
        self.assertEqual(new['knowledge'][ids['a']]['lifecycle'], 'withdrawn')
        self.assertEqual(new['knowledge'][ids['c']], ins['knowledge'][ids['c']])
        self.assertEqual(new['relations'][0]['status'], 'suspended')
        self.assertTrue(k.assess_use(new['knowledge'][ids['c']], new)['valid'])
        self.assertEqual(nrun['tasks'][ids['unrelated']], run['tasks'][ids['unrelated']])

    def test_basis_hash_covers_exact_family_record(self):
        ins, run, ids = fixture()
        xid = ins['knowledge'][ids['a']]['exposition_id']
        basis = k.capture_basis(ins, run, [ids['a'], xid, ids['task']])
        self.assertTrue(k.validate_basis(basis, ins, run)['valid'])
        ins['expositions'][xid]['items'][0]['text'] = 'changed'
        self.assertIn('hash_changed:' + xid, k.validate_basis(basis, ins, run)['reasons'])
        self.assertFalse(k.assess_use(ins['knowledge'][ids['a']], ins)['valid'])

    def test_source_locators_are_not_missing_record_ids(self):
        ins, run, ids = fixture()
        ins['knowledge'][ids['b']]['origin_refs'] = ['proposal:1', 'input/knowledge/KN-X.json', {'path': 'catalog.json', 'sha256': '0'}]
        self.assertEqual(k.plan_impact(ins, run, [ids['b']], [])['unresolved_refs'], [])
        ins['knowledge'][ids['b']]['dependencies'].append('KN-MISSING')
        self.assertIn('KN-MISSING', k.plan_impact(ins, run, [ids['b']], [])['unresolved_refs'])

    def test_known_source_propagates_but_locator_does_not(self):
        ins, run, ids = fixture()
        ins['knowledge'][ids['c']]['used_sources'] = ['proposal:1', 'input/knowledge/KN-X.json', ids['a']]
        plan = k.plan_impact(ins, run, [ids['a']], [])
        self.assertIn(ids['c'], plan['computed_impact'])
        self.assertNotIn('input/knowledge/KN-X.json', plan['unresolved_refs'])

    def test_source_currentness_and_reassessment_preserve_judgment(self):
        ins, run, ids = fixture()
        ins['sources'] = [{'name': 'paper', 'path': 'sources/paper', 'sha256': 'old'}]
        ins, run, kid, aid = add(ins, run, source_refs=['paper'])
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
        ins, _, ids = fixture()
        ins, env, tr = transition(ins)
        tr = k.record_transition_result(ins, tr, {'id': ids['a'], 'status': 'failed'})
        with self.assertRaises(ValueError): k.activate_transition(ins, tr)
        self.assertEqual(ins['active_trust_environment'], 'TE-old')

    def test_one_failure_in_complete_multi_target_batch_preserves_every_original_record(self):
        ins, _, _ = fixture()
        ins, env, tr = transition(ins)
        for target in tr['targets']:
            tr = k.record_transition_result(ins, tr, {'id': target['id'], **evidence(ins, target['id'], env)})
        failed = tr['targets'][1]['id']
        tr = k.record_transition_result(ins, tr, {'id': failed, 'status': 'failed'})
        before = deepcopy(ins)
        with self.assertRaisesRegex(ValueError, 'all transition targets'):
            k.activate_transition(ins, tr)
        self.assertEqual(ins, before)

    def test_unknown_environment_rejected(self):
        ins, run, _ = fixture()
        with self.assertRaises(ValueError): k.begin_transition(ins, 'TE-missing')
        with self.assertRaises(ValueError): k.invalidate_environment(ins, run, 'TE-missing', 'bad')

    def test_complete_transition_preserves_old_evidence_and_changes_links(self):
        ins, _, ids = fixture()
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertEqual(changed['active_trust_environment'], env)
        self.assertEqual(changed['trust_environments']['TE-old']['status'], 'superseded')
        for rid, row in ins['formal_results'].items(): self.assertEqual(changed['formal_results'][rid], row)
        for rid, row in ins['identity_assessments'].items(): self.assertEqual(changed['identity_assessments'][rid], row)
        for kid in (ids['a'], ids['b'], ids['c']):
            self.assertTrue(k.assess_use(changed['knowledge'][kid], changed)['valid'])
            self.assertNotEqual(changed['knowledge'][kid]['formal_result_id'], ins['knowledge'][kid]['formal_result_id'])

    def test_environment_invalidation_is_local_to_constant_closure(self):
        ins, run, ids = fixture()
        ins, run, isolated, _ = add(ins, run, lean_code='theorem isolated : True := True.intro', declaration_names=['isolated'])
        fid = ins['knowledge'][isolated]['formal_result_id']
        changed, nrun = k.invalidate_environment(ins, run, 'TE-old', 'constant defect',
            affected_constants=['isolated'], scope_evidence='checked closure boundary')
        self.assertEqual(changed['formal_results'][fid]['formal_use'], 'suspended')
        self.assertTrue(k.assess_use(changed['knowledge'][ids['c']], changed)['valid'])
        self.assertEqual(nrun['tasks'][ids['unrelated']], run['tasks'][ids['unrelated']])

    def test_invalidated_environment_recovery_rechecks_all_accepted_results(self):
        ins, run, ids = fixture()
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
        ins, run, ids = fixture()
        ins, run, pending, _ = add(ins, run, verified=False)
        ins, run = withdraw(ins, run, ids['c'])
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'bad')
        ins, env, tr = transition(ins)
        self.assertNotIn(pending, {t['id'] for t in tr['targets']})
        self.assertNotIn(ids['c'], {t['id'] for t in tr['targets']})
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][pending], changed)['valid'])
        self.assertEqual(changed['knowledge'][ids['c']]['lifecycle'], 'withdrawn')

    def test_recovery_preserves_later_semantic_suspension(self):
        ins, run, ids = fixture()
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        ins = kr.set_assessment_use(ins, ids['aa'], 'suspended', 'meaning challenged', 'reviewer')
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['a']], changed)['valid'])
        self.assertTrue(k.assess_use(changed['knowledge'][ids['c']], changed)['valid'])

    def test_environment_recovery_cannot_clear_a_later_source_reassessment(self):
        ins, run, _ = fixture()
        ins['sources'] = [{'name': 'paper', 'path': 'sources/paper', 'sha256': 'old'}]
        ins, run, kid, aid = add(ins, run, source_refs=['paper'])
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
        ins, run, ids = fixture()
        ins, run = withdraw(ins, run, ids['a'])
        ins, run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertFalse(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])
        self.assertEqual(changed['knowledge'][ids['a']]['lifecycle'], 'withdrawn')

    def test_history_is_not_a_current_dependency(self):
        ins, run, ids = fixture()
        ins['knowledge'][ids['b']]['history'] = [{'previous': {'dependencies': [ids['c']]}}]
        changed, _ = revise(ins, run, ids['c'])
        self.assertTrue(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])

    def test_fresh_plan_is_applied_without_recomputing_the_closure(self):
        ins, run, ids = fixture()
        with patch.object(k, 'plan_impact', wraps=k.plan_impact) as plans:
            changed, _ = withdraw(ins, run, ids['a'])
        # One producer declaration and one plan inside invalidate_knowledge.
        self.assertEqual(plans.call_count, 2)
        self.assertEqual(changed['knowledge'][ids['a']]['lifecycle'], 'withdrawn')

    def test_observed_propagation_plans_twice_and_applies_to_the_callers_copy(self):
        ins, run, _ = fixture()
        with patch.object(k, 'plan_impact', wraps=k.plan_impact) as plans:
            _, changed_run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        # Preview and plan inside _propagate; no third recomputation on apply.
        self.assertEqual(plans.call_count, 2)
        self.assertEqual(changed_run['history'][-1]['kind'], 'knowledge_reassessment_required')
        self.assertNotIn('knowledge_reassessment_required', [h.get('kind') for h in run['history']])


if __name__ == '__main__': unittest.main(verbosity=2)
