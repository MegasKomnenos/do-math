"""Authored import and ontology contracts using the v5 authoritative families."""
from copy import deepcopy
import unittest
from test_knowledge import candidate, fixture, add, seal, revise
from do_math import knowledge_io as io, knowledge_records as kr
from do_math.repository import new_id


def activate(state, token, family='relation', definition=None):
    definition = definition or next(t for t in io.relation_templates() if t['token'] == token)
    state, _ = io.register_kind_definition(state, definition, source_ref='source', actor_ref='author')
    state = io.check_kind_definition(state, family, token, check_ref='check:fixture', actor_ref='checker')
    return io.activate_kind_definition(state, family, token, approval_ref='approval:fixture', actor_ref='reviewer')


class KnowledgeIoTests(unittest.TestCase):
    def test_uncertainty_metadata_matches_storage_types_at_import(self):
        from do_math.state_contract import default_state_contract
        import jsonschema
        for value in ('Not a proof', {'claim': 'Not a proof', 'scope': 'finite search only'}):
            with self.subTest(accepted=value):
                ins, _, kid = io.import_candidate({}, {}, candidate(uncertainty_assessment=value), source_ref='s', actor_ref='u')
                self.assertEqual(ins['knowledge'][kid]['uncertainty_assessment'], value)
                schema = default_state_contract().family('research', 'knowledge').schema
                self.assertEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(ins['knowledge'][kid])), [])
        for value in (None, [], 7, False):
            with self.subTest(rejected=value), self.assertRaises(ValueError):
                io.import_candidate({}, {}, candidate(uncertainty_assessment=value), source_ref='s', actor_ref='u')
    def test_candidate_import_is_not_usable_and_queues_formal_check(self):
        before = {}
        ins, run, kid = io.import_candidate(before, {}, candidate(), source_ref='source', actor_ref='user')
        record = ins['knowledge'][kid]
        self.assertEqual(record['lifecycle'], 'active')
        self.assertNotIn('formal', record)
        self.assertNotIn('reviews', record)
        self.assertNotIn('statement', record)
        self.assertEqual(ins['formal_results'][record['formal_result_id']]['publication_state'], 'candidate')
        self.assertEqual(ins['formal_results'][record['formal_result_id']]['verification'], {})
        self.assertEqual(kr.usable_links(ins, kid), [])
        self.assertIn('source', record['origin_refs'])
        for authored in (record, ins['expositions'][record['exposition_id']],
                         ins['formal_results'][record['formal_result_id']]):
            self.assertNotIn('producer_execution', authored)
            self.assertIn('user', authored['origin_refs'])
        self.assertEqual(run['queue'][-1]['role'], 'formal_check')
        self.assertEqual(before, {})
        ai, _, aid = io.import_candidate({}, {'executions': {'EX-author': {'id': 'EX-author'}}},
                                         candidate(), source_ref='source', actor_ref='EX-author')
        authored = ai['knowledge'][aid]
        for row in (authored, ai['expositions'][authored['exposition_id']],
                    ai['formal_results'][authored['formal_result_id']]):
            self.assertEqual(row['producer_execution'], 'EX-author')

    def test_same_id_import_rejected_explicit_revision_preserves_old_authorities(self):
        ins, run, ids = fixture()
        kid = ids['a']
        with self.assertRaises(ValueError):
            io.import_candidate(ins, run, candidate(id=kid), source_ref='source', actor_ref='user')
        changed, queued = revise(ins, run, kid, {'statement': 'Rephrased True'})
        replacement = next(row for row in changed['knowledge'].values() if row.get('supersedes') == kid)
        self.assertNotEqual(replacement['id'], kid)
        self.assertEqual(replacement['formal_result_id'], ins['knowledge'][kid]['formal_result_id'])
        self.assertEqual(changed['identity_assessments'], ins['identity_assessments'])
        self.assertEqual(kr.proposal_view(changed, kid)['statement'], 'True')
        self.assertEqual(kr.usable_links(changed, replacement['id']), [])
        self.assertEqual(queued['queue'][-1]['role'], 'identity_review')

    def test_unknown_kind_requires_candidate_check_and_activation(self):
        definition = dict(family='knowledge', token='computational_lemma', meaning='A bounded computational lemma.', constraints={})
        with self.assertRaises(ValueError): io.import_candidate({}, {}, candidate(kind=definition['token']), source_ref='s', actor_ref='u')
        ins, token = io.register_kind_definition({}, definition, source_ref='s', actor_ref='u')
        with self.assertRaises(ValueError): io.import_candidate(ins, {}, candidate(kind=token), source_ref='s', actor_ref='u')
        with self.assertRaises(ValueError): io.activate_kind_definition(ins, 'knowledge', token, approval_ref='a', actor_ref='u')
        ins = io.check_kind_definition(ins, 'knowledge', token, check_ref='check', actor_ref='checker')
        with self.assertRaises(ValueError): io.import_candidate(ins, {}, candidate(kind=token), source_ref='s', actor_ref='u')
        ins = io.activate_kind_definition(ins, 'knowledge', token, approval_ref='approval', actor_ref='reviewer')
        ins, _, kid = io.import_candidate(ins, {}, candidate(kind=token), source_ref='s', actor_ref='u')
        self.assertEqual(ins['knowledge'][kid]['kind'], token)

    def test_missing_dependency_is_rejected_without_mutation(self):
        ins, run, _ = fixture()
        before = deepcopy(ins)
        with self.assertRaises(ValueError):
            io.import_candidate(ins, run, candidate(dependencies=[new_id('KN')]), source_ref='s', actor_ref='u')
        self.assertEqual(ins, before)

    def test_research_analogy_is_distinct_from_mathematical_connection(self):
        ins, run, ids = fixture()
        for token in ('analogous_to', 'formally_implies'): ins = activate(ins, token)
        analogy = dict(kind='analogous_to', source=ids['a'], target=ids['b'], evidence='Same recurrence shape')
        self.assertTrue(io.validate_relation(ins, analogy)['valid'])
        ins, rid = io.import_relation(ins, analogy, source_ref='s', actor_ref='u')
        self.assertEqual(next(r for r in ins['relations'] if r['id'] == rid)['authority'], 'research_connection')
        self.assertFalse(io.validate_relation(ins, {**analogy, 'kind': 'formally_implies'})['valid'])

    def test_mathematical_relation_requires_exact_formal_identity_and_current_endpoints(self):
        ins, run, ids = fixture()
        ins = activate(ins, 'formally_implies')
        claim = dict(kind='formally_implies', source=ids['a'], target=ids['b'], confirmed_scope='True implies True')
        relation = {**claim, 'evidence': 'proof', 'formal_result_refs': [ins['knowledge'][ids['a']]['formal_result_id']],
                    'assessment_refs': [ids['aa']]}
        self.assertFalse(io.validate_relation(ins, relation)['valid'])
        ins, run, proof, assessment = add(ins, run, relation_claim=claim)
        relation.update(formal_result_refs=[ins['knowledge'][proof]['formal_result_id']], assessment_refs=[assessment])
        self.assertTrue(io.validate_relation(ins, relation)['valid'])
        changed, rid = io.import_relation(ins, relation, source_ref='s', actor_ref='u')
        self.assertEqual(next(r for r in changed['relations'] if r['id'] == rid)['authority'], 'mathematical_connection')
        self.assertFalse(io.validate_relation(ins, {**relation, 'assessment_refs': [ids['aa']]})['valid'])
        ins['knowledge'][ids['b']]['title'] = 'Changed endpoint'
        self.assertFalse(io.validate_relation(ins, relation)['valid'])

    def test_relation_revision_keeps_id_and_history(self):
        ins, run, ids = fixture()
        ins = activate(ins, 'supports')
        first = dict(id=new_id('RL'), kind='supports', source=ids['a'], target=ids['b'], evidence='e1')
        ins, rid = io.import_relation(ins, first, source_ref='s1', actor_ref='u')
        ins, again = io.import_relation(ins, {**first, 'evidence': 'e2'}, source_ref='s2', actor_ref='u')
        row = next(r for r in ins['relations'] if r['id'] == rid)
        self.assertEqual(again, rid)
        self.assertEqual(row['revision'], 2)
        self.assertEqual(row['history'][-1]['evidence'], 'e1')

    def test_catalog_exposes_only_active_definitions(self):
        definition = dict(family='relation', token='translates_to', meaning='An explicitly scoped translation.', constraints={'requires_evidence': True})
        ins, _ = io.register_kind_definition({}, definition, source_ref='s', actor_ref='u')
        self.assertEqual(io.catalog_definitions(ins)['relations'], [])
        self.assertTrue(any(d['token'] == 'theorem' for d in io.catalog_definitions(ins)['knowledge']))
        ins = io.check_kind_definition(ins, 'relation', 'translates_to', check_ref='check', actor_ref='checker')
        ins = io.activate_kind_definition(ins, 'relation', 'translates_to', approval_ref='approval', actor_ref='reviewer')
        self.assertEqual([d['token'] for d in io.catalog_definitions(ins)['relations']], ['translates_to'])
        ins, _ = io.withdraw_kind_definition(ins, {}, 'relation', 'translates_to', reason='meaning defect', actor_ref='reviewer')
        self.assertEqual(io.catalog_definitions(ins)['relations'], [])


if __name__ == '__main__': unittest.main(verbosity=2)
