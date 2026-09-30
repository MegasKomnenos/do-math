"""Knowledge state rules (layer 2) over the three-record graph: revision, withdrawal, impact, source currentness
and trust-environment transition and recovery.

The graph (``knowledge_fixtures.knowledge_graph``): records ``a``, ``b`` (depends on
``a``) and ``c``, sealed by judgments ``aa``, ``ba``, ``ca`` in the active
environment ``TE-old``; a relation ``a -> c``; a current goal judgment using
``b``; a completed task on ``b`` and an unrelated completed task on ``c``.
Kernel evidence in these states is the fixture's synthetic formal result.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import knowledge as k, knowledge_records as kr
from do_math.knowledge import assess_research_use
from do_math.knowledge_records import create_candidate, reader_view
from do_math.record_schemas import RECORDS
from do_math.system_clock import new_id
from knowledge_fixtures import (add_knowledge, formal_evidence, impact_declaration, knowledge_graph,
                                revise_knowledge, seal_knowledge, verified_knowledge)
from support.provider_probes import ObservedCalls


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


class RevisionTests(unittest.TestCase):
    def test_explanation_revision_reuses_only_current_formal_evidence(self):
        for status in ('candidate', 'rejected', 'suspended', 'verified'):
            with self.subTest(status=status):
                ins = {'active_trust_environment': 'TE-old', 'trust_environments': {
                    'TE-old': {'id': 'TE-old', 'status': 'active',
                               'toolchain': {'version': 'fixture-old'}, 'allowed_axioms': []}}}
                ins, run, kid, _ = add_knowledge(ins, {}, verified=False)
                if status != 'candidate':
                    checked = formal_evidence(ins, kid)
                    if status == 'rejected':
                        checked['status'] = 'failed'
                    ins = kr.record_formal_result(ins, kid, checked, 'TE-old', runtime=run)
                old_fid = ins['knowledge'][kid]['formal_result_id']
                if status == 'suspended':
                    ins['formal_results'][old_fid]['formal_use'] = 'suspended'
                old_formal = deepcopy(ins['formal_results'][old_fid])
                changed, queued = revise_knowledge(ins, run, kid, {'summary': 'Corrected summary'})
                replacement = next(row for row in changed['knowledge'].values() if row.get('supersedes') == kid)
                current_fid = replacement['formal_result_id']
                reused = status == 'verified'
                self.assertEqual(current_fid == old_fid, reused)
                self.assertEqual(changed['formal_results'][old_fid], old_formal)
                self.assertEqual([a['role'] for a in queued['queue'] if a.get('target') == replacement['id']],
                                 ['identity_review' if reused else 'formal_check'])
                self.assertFalse(any(a.get('target') == kid and a['role'] == 'formal_check' for a in queued['queue']))
                if not reused:
                    self.assertEqual(changed['formal_results'][current_fid]['verification'], {})
                    self.assertEqual(changed['formal_results'][current_fid]['publication_state'], 'candidate')

    def test_nonformal_explanation_revision_still_returns_to_planning(self):
        ins, run, kid, _ = add_knowledge({}, {}, verified=False, lean_code='', declaration_names=[])
        changed, queued = revise_knowledge(ins, run, kid, {'summary': 'Corrected observation'})
        replacement = next(row for row in changed['knowledge'].values() if row.get('supersedes') == kid)
        self.assertIsNone(replacement['formal_result_id'])
        self.assertEqual([a['role'] for a in queued['queue'] if a.get('target') == replacement['id']], ['research_plan'])

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

    def test_history_is_not_a_current_dependency(self):
        ins, run, ids = knowledge_graph()
        ins['knowledge'][ids['b']]['history'] = [{'previous': {'dependencies': [ids['c']]}}]
        changed, _ = revise_knowledge(ins, run, ids['c'])
        self.assertTrue(k.assess_use(changed['knowledge'][ids['b']], changed)['valid'])


class WithdrawalTests(unittest.TestCase):
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

    def test_fresh_plan_is_applied_without_recomputing_the_closure(self):
        ins, run, ids = knowledge_graph()
        with ObservedCalls(plan_impact=k.plan_impact) as plans:
            changed, _ = withdraw(ins, run, ids['a'])
        # One producer declaration and one plan inside invalidate_knowledge.
        self.assertEqual(plans.count('plan_impact'), 2)
        self.assertEqual((plans.count('plan_impact', caller='knowledge_fixtures'),
                          plans.count('plan_impact', caller='do_math.knowledge')), (1, 1))
        self.assertEqual(changed['knowledge'][ids['a']]['lifecycle'], 'withdrawn')


class ImpactTests(unittest.TestCase):
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
        ins['knowledge'][ids['b']]['origin_refs'] = ['proposal:1', 'input/knowledge/KN-X.json',
                                                     {'path': 'catalog.json', 'sha256': '0'}]
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

    def test_observed_propagation_plans_twice_and_applies_to_the_callers_copy(self):
        ins, run, _ = knowledge_graph()
        with ObservedCalls(plan_impact=k.plan_impact) as plans:
            _, changed_run = k.invalidate_environment(ins, run, 'TE-old', 'environment defect')
        # Preview and plan inside propagate; no third recomputation on apply.
        self.assertEqual(plans.count('plan_impact'), 2)
        self.assertEqual(plans.count('plan_impact', caller='do_math.knowledge'), 2)
        self.assertEqual(changed_run['history'][-1]['kind'], 'knowledge_reassessment_required')
        self.assertNotIn('knowledge_reassessment_required', [h.get('kind') for h in run['history']])


class SourceCurrentnessTests(unittest.TestCase):
    def test_source_currentness_and_reassessment_preserve_judgment(self):
        ins, run, ids = knowledge_graph()
        ins['sources'] = [{'name': 'paper', 'path': 'sources/paper', 'sha256': 'old'}]
        ins, run, kid, aid = add_knowledge(ins, run, source_refs=['paper'])
        saved = deepcopy(ins['identity_assessments'][aid])
        self.assertTrue(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        ins['sources'][0]['sha256'] = 'new'
        self.assertFalse(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        changed, _ = k.suspend_for_source_change(ins, run, kid, source_name='paper', reason='source changed',
                                                 actor_ref='user')
        self.assertEqual(changed['identity_assessments'][aid], saved)
        ins['sources'][0]['sha256'] = changed['sources'][0]['sha256'] = 'old'
        self.assertTrue(k.assess_use(ins['knowledge'][kid], ins)['valid'])
        self.assertFalse(k.assess_use(changed['knowledge'][kid], changed)['valid'])

    def test_research_reuse_keeps_dependency_and_source_currentness(self):
        instance = {'sources': [{'id': 'S', 'name': 'data', 'sha256': 'a' * 64, 'path': 'data'}],
                    'kind_definitions': {'KD': {'id': 'KD', 'status': 'active'}}}
        instance, parent = create_candidate(instance, {'id': 'KN-parent', 'kind_definition_id': 'KD',
                                                       'statement': 'Finite observation',
                                                       'source_basis': [{'name': 'data', 'sha256': 'a' * 64}]},
                                            source_ref='S', actor_ref='AUTHOR')
        instance, child = create_candidate(instance, {'id': 'KN-child', 'kind_definition_id': 'KD',
                                                      'statement': 'Uses that observation', 'dependencies': [parent]},
                                           source_ref='S', actor_ref='AUTHOR')
        self.assertTrue(assess_research_use(instance['knowledge'][child], instance)['valid'])
        instance['sources'][0]['sha256'] = 'b' * 64
        self.assertFalse(assess_research_use(instance['knowledge'][child], instance)['valid'])

    def test_knowledge_input_exposes_exact_formal_and_identity_records(self):
        instance, _, kid, aid = verified_knowledge()
        view = reader_view(instance, kid)
        self.assertEqual(view['formal_result']['id'], view['formal_result_id'])
        self.assertEqual(view['identity_assessments'][0]['id'], aid)
        self.assertEqual(view['assessment_uses'][0]['assessment_id'], aid)


class TrustTransitionTests(unittest.TestCase):
    def test_partial_failure_keeps_old_environment(self):
        ins, _, ids = knowledge_graph()
        ins, env, tr = transition(ins)
        tr = k.record_transition_result(ins, tr, {'id': ids['a'], 'status': 'failed'})
        with self.assertRaisesRegex(ValueError, 'all transition targets must be verified'):
            k.activate_transition(ins, tr)
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
        with self.assertRaisesRegex(ValueError, 'unknown or invalid transition environment'):
            k.begin_transition(ins, 'TE-missing')
        with self.assertRaisesRegex(ValueError, 'unknown trust environment: TE-missing'):
            k.invalidate_environment(ins, run, 'TE-missing', 'bad')

    def test_complete_transition_preserves_old_evidence_and_changes_links(self):
        ins, _, ids = knowledge_graph()
        ins, env, tr = transition(ins)
        changed = finish_transition(ins, env, tr)
        self.assertEqual(changed['active_trust_environment'], env)
        self.assertEqual(changed['trust_environments']['TE-old']['status'], 'superseded')
        for rid, row in ins['formal_results'].items():
            self.assertEqual(changed['formal_results'][rid], row)
        for rid, row in ins['identity_assessments'].items():
            self.assertEqual(changed['identity_assessments'][rid], row)
        for kid in (ids['a'], ids['b'], ids['c']):
            self.assertTrue(k.assess_use(changed['knowledge'][kid], changed)['valid'])
            self.assertNotEqual(changed['knowledge'][kid]['formal_result_id'], ins['knowledge'][kid]['formal_result_id'])

    def test_invalidated_environment_recovery_rechecks_all_accepted_results(self):
        ins, run, ids = knowledge_graph()
        stopped, _ = k.invalidate_environment(ins, run, 'TE-old', 'kernel defect')
        jsonschema.validate(stopped['trust_environments']['TE-old'], RECORDS['trust_environments'])
        self.assertEqual(stopped['trust_environments']['TE-old']['invalidated_reason'], 'kernel defect')
        self.assertIsNone(stopped['active_trust_environment'])
        stopped, env, tr = transition(stopped)
        self.assertEqual({t['id'] for t in tr['targets']}, {ids['a'], ids['b'], ids['c']})
        self.assertTrue(all(t['previous_environment_ids'] == ['TE-old'] for t in tr['targets']))
        recovered = finish_transition(stopped, env, tr)
        self.assertEqual(recovered['trust_environments']['TE-old']['status'], 'invalid')
        for kid in (ids['a'], ids['b'], ids['c']):
            self.assertTrue(k.assess_use(recovered['knowledge'][kid], recovered)['valid'])

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


if __name__ == '__main__':
    unittest.main()
