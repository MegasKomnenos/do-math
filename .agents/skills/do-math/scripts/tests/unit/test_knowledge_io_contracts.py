"""Authored knowledge imports, kind definitions and relations (``knowledge_io``, layer 2) on small states.

Tests start from an empty state or ``knowledge_fixtures.knowledge_graph()``:
three sealed records ``a``, ``b`` (depends on ``a``) and ``c``, a relation
``a``->``c``, a current goal judgment using ``b`` and completed tasks using ``b``
and ``c``, in the active trust environment ``TE-old``. The fixture's formal
evidence is synthetic (no Lean run) and its identity assessments are recorded
directly, never reviewed.
"""
from copy import deepcopy
import unittest

import jsonschema

from do_math import knowledge, knowledge_io as io, knowledge_records as kr
from do_math.knowledge import assess_use
from do_math.state_contract import default_state_contract
from do_math.system_clock import new_id
from support.knowledge_builders import add_knowledge, formal_evidence, knowledge_candidate, knowledge_graph, revise_knowledge
from support.state_builders import current_state


class CandidateImportTests(unittest.TestCase):
    def test_uncertainty_metadata_matches_storage_types_at_import(self):
        from support.entry import entry
        _entry = entry()
        schema = default_state_contract().family('research', 'knowledge').schema
        for value in ('Not a proof', {'claim': 'Not a proof', 'scope': 'finite search only'}):
            with self.subTest(accepted=value):
                ins, _, kid = io.import_candidate({}, {}, knowledge_candidate(uncertainty_assessment=value),
                                                  source_ref='s', actor_ref='u', clock=_entry.ports.clock)
                self.assertEqual(ins['knowledge'][kid]['uncertainty_assessment'], value)
                self.assertEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(ins['knowledge'][kid])), [])
        for value in (None, [], 7, False):
            with self.subTest(rejected=value), \
                    self.assertRaisesRegex(ValueError, '^uncertainty_assessment must be text or an object$'):
                io.import_candidate({}, {}, knowledge_candidate(uncertainty_assessment=value), source_ref='s', actor_ref='u', clock=_entry.ports.clock)

    def test_candidate_import_is_not_usable_and_queues_formal_check(self):
        from support.entry import entry
        _entry = entry()
        before = {}
        ins, run, kid = io.import_candidate(before, {}, knowledge_candidate(), source_ref='source', actor_ref='user', clock=_entry.ports.clock)
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
                                         knowledge_candidate(), source_ref='source', actor_ref='EX-author', clock=_entry.ports.clock)
        authored = ai['knowledge'][aid]
        for row in (authored, ai['expositions'][authored['exposition_id']],
                    ai['formal_results'][authored['formal_result_id']]):
            self.assertEqual(row['producer_execution'], 'EX-author')

    def test_same_id_import_rejected_explicit_revision_preserves_old_authorities(self):
        from support.entry import entry
        _entry = entry()
        ins, run, ids = knowledge_graph()
        kid = ids['a']
        with self.assertRaisesRegex(ValueError, '^record ID already exists; revisions require a new ID$'):
            io.import_candidate(ins, run, knowledge_candidate(id=kid), source_ref='source', actor_ref='user', clock=_entry.ports.clock)
        changed, queued = revise_knowledge(ins, run, kid, {'statement': 'Rephrased True'})
        replacement = next(row for row in changed['knowledge'].values() if row.get('supersedes') == kid)
        self.assertNotEqual(replacement['id'], kid)
        self.assertEqual(replacement['formal_result_id'], ins['knowledge'][kid]['formal_result_id'])
        self.assertEqual(changed['identity_assessments'], ins['identity_assessments'])
        self.assertEqual(kr.proposal_view(changed, kid)['statement'], 'True')
        self.assertEqual(kr.usable_links(changed, replacement['id']), [])
        self.assertEqual(queued['queue'][-1]['role'], 'identity_review')

    def test_relation_claim_endpoint_basis_matches_the_storage_contract(self):
        from support.entry import entry
        _entry = entry()
        ins, run = current_state({'object_format': 'sha1'})
        endpoints = []
        for title in ('Source endpoint', 'Target endpoint'):
            ins, run, kid = io.import_candidate(ins, run,
                knowledge_candidate(title=title, lean_code='', declaration_names=[]),
                source_ref='fixture', actor_ref='user', clock=_entry.ports.clock)
            endpoints.append(kid)
        claim = dict(kind='formally_implies', source=endpoints[0],
                     target=endpoints[1], confirmed_scope='True implies True')
        ins, run, proof = io.import_candidate(ins, run, knowledge_candidate(relation_claim=claim),
            source_ref='fixture', actor_ref='user', clock=_entry.ports.clock)
        expected = knowledge.capture_basis(ins, run, endpoints)
        self.assertEqual(ins['knowledge'][proof]['relation_endpoint_basis'], expected)
        contract = default_state_contract()
        contract.validate(ins, run)
        self.assertTrue(knowledge.validate_basis(expected, ins, run)['valid'])
        schema = contract.family('research', 'knowledge').schema
        invalid = [
            ({}, r"^\{\} is not of type 'array'\n"),
            ([{'id': endpoints[0], 'sha256': 'not-a-hash', 'status': 'active'}], r"^'not-a-hash' does not match "),
            ([{'id': endpoints[0], 'sha256': expected[0]['sha256']}], r"^'status' is a required property\n"),
            ([{**expected[0], 'unregistered': True}], r"^Additional properties are not allowed \('unregistered' was unexpected\)\n"),
        ]
        for basis, reason in invalid:
            with self.subTest(basis=basis), self.assertRaisesRegex(jsonschema.ValidationError, reason) as caught:
                jsonschema.validate({**ins['knowledge'][proof], 'relation_endpoint_basis': basis}, schema)
            self.assertEqual(list(caught.exception.absolute_path)[0], 'relation_endpoint_basis')

    def test_missing_dependency_is_rejected_without_mutation(self):
        from support.entry import entry
        _entry = entry()
        ins, run, _ = knowledge_graph()
        before = deepcopy(ins)
        missing = new_id('KN')
        with self.assertRaisesRegex(ValueError, '^candidate dependencies do not exist: ' + missing + '$'):
            io.import_candidate(ins, run, knowledge_candidate(dependencies=[missing]), source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        self.assertEqual(ins, before)


class KindDefinitionTests(unittest.TestCase):
    def test_unknown_kind_requires_candidate_check_and_activation(self):
        from support.entry import entry
        _entry = entry()
        definition = dict(family='knowledge', token='computational_lemma', meaning='A bounded computational lemma.', constraints={})
        unknown = '^unknown knowledge kind: computational_lemma$'
        with self.assertRaisesRegex(ValueError, unknown):
            io.import_candidate({}, {}, knowledge_candidate(kind=definition['token']), source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        ins, token = io.register_kind_definition({}, definition, source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        with self.assertRaisesRegex(ValueError, unknown):
            io.import_candidate(ins, {}, knowledge_candidate(kind=token), source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        with self.assertRaisesRegex(ValueError, '^kind definition must be checked before activation$'):
            io.activate_kind_definition(ins, 'knowledge', token, approval_ref='a', actor_ref='u')
        ins = io.check_kind_definition(ins, 'knowledge', token, check_ref='check', actor_ref='checker')
        with self.assertRaisesRegex(ValueError, unknown):
            io.import_candidate(ins, {}, knowledge_candidate(kind=token), source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        ins = io.activate_kind_definition(ins, 'knowledge', token, approval_ref='approval', actor_ref='reviewer')
        ins, _, kid = io.import_candidate(ins, {}, knowledge_candidate(kind=token), source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        self.assertEqual(ins['knowledge'][kid]['kind'], token)

    def test_catalog_exposes_only_active_definitions(self):
        # A new relation kind still passes an independent check before any use.
        from support.entry import entry
        _entry = entry()
        installed = sorted(d['token'] for d in io.BUILTIN_DEFINITIONS if d['family'] == 'relation')
        definition = dict(family='relation', token='translates_to', meaning='An explicitly scoped translation.',
                          constraints={'requires_evidence': True})
        ins, _ = io.register_kind_definition({}, definition, source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        relations = lambda: sorted(d['token'] for d in io.catalog_definitions(ins)['relations'])
        self.assertEqual(relations(), installed)
        self.assertTrue(any(d['token'] == 'theorem' for d in io.catalog_definitions(ins)['knowledge']))
        ins = io.check_kind_definition(ins, 'relation', 'translates_to', check_ref='check', actor_ref='checker')
        self.assertEqual(relations(), installed)
        ins = io.activate_kind_definition(ins, 'relation', 'translates_to', approval_ref='approval', actor_ref='reviewer')
        self.assertEqual(relations(), sorted([*installed, 'translates_to']))
        ins, _ = io.withdraw_kind_definition(ins, {}, 'relation', 'translates_to', reason='meaning defect', actor_ref='reviewer', clock=_entry.ports.clock)
        self.assertEqual(relations(), installed)


class RelationTests(unittest.TestCase):
    def test_research_analogy_is_distinct_from_mathematical_connection(self):
        from support.entry import entry
        _entry = entry()
        ins, run, ids = knowledge_graph()
        analogy = dict(kind='analogous_to', source=ids['a'], target=ids['b'], evidence='Same recurrence shape')
        self.assertTrue(io.validate_relation(ins, analogy)['valid'])
        ins, rid = io.import_relation(ins, analogy, source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        self.assertEqual(next(r for r in ins['relations'] if r['id'] == rid)['authority'], 'research_connection')
        self.assertFalse(io.validate_relation(ins, {**analogy, 'kind': 'formally_implies'})['valid'])

    def test_mathematical_relation_requires_match_in_addition_to_active_use(self):
        from support.entry import entry
        _entry = entry()
        for decision in ('mismatch', 'unresolved'):
            with self.subTest(decision=decision):
                ins, run, ids = knowledge_graph()
                claim = dict(kind='formally_implies', source=ids['a'], target=ids['b'],
                             confirmed_scope='True implies True')
                ins, run, proof, _ = add_knowledge(ins, run, verified=False, relation_claim=claim)
                ins = kr.record_formal_result(ins, proof, formal_evidence(ins, proof), 'TE-old', runtime=run)
                ins, negative = kr.record_identity_assessment(ins, proof,
                    {'decision': decision, 'basis': kr.identity_basis(ins, proof)},
                    'policy:fixture', runtime=run, clock=_entry.ports.clock)
                relation = {**claim, 'evidence': 'proof',
                    'formal_result_refs': [ins['knowledge'][proof]['formal_result_id']],
                    'assessment_refs': [negative]}
                self.assertTrue(assess_use(ins['identity_assessments'][negative], ins)['valid'])
                checked = io.validate_relation(ins, relation)
                self.assertFalse(checked['valid'])
                self.assertTrue(any(r.startswith('formal_result_does_not_establish_this_relation:')
                                    for r in checked['reasons']))
                ins, positive = kr.record_identity_assessment(ins, proof,
                    {'decision': 'match', 'basis': kr.identity_basis(ins, proof)},
                    'policy:fixture', runtime=run, clock=_entry.ports.clock)
                checked = io.validate_relation(ins, relation)
                self.assertFalse(checked['valid'])
                self.assertIn('assessment_not_effective:' + negative, checked['reasons'])
                relation['assessment_refs'] = [positive]
                self.assertTrue(io.validate_relation(ins, relation)['valid'])

    def test_mathematical_relation_requires_exact_formal_identity_and_current_endpoints(self):
        from support.entry import entry
        _entry = entry()
        ins, run, ids = knowledge_graph()
        claim = dict(kind='formally_implies', source=ids['a'], target=ids['b'], confirmed_scope='True implies True')
        relation = {**claim, 'evidence': 'proof', 'formal_result_refs': [ins['knowledge'][ids['a']]['formal_result_id']],
                    'assessment_refs': [ids['aa']]}
        self.assertFalse(io.validate_relation(ins, relation)['valid'])
        ins, run, proof, assessment = add_knowledge(ins, run, relation_claim=claim)
        relation.update(formal_result_refs=[ins['knowledge'][proof]['formal_result_id']], assessment_refs=[assessment])
        self.assertTrue(io.validate_relation(ins, relation)['valid'])
        changed, rid = io.import_relation(ins, relation, source_ref='s', actor_ref='u', clock=_entry.ports.clock)
        self.assertEqual(next(r for r in changed['relations'] if r['id'] == rid)['authority'], 'mathematical_connection')
        self.assertFalse(io.validate_relation(ins, {**relation, 'assessment_refs': [ids['aa']]})['valid'])
        ins['knowledge'][ids['b']]['title'] = 'Changed endpoint'
        self.assertFalse(io.validate_relation(ins, relation)['valid'])

    def test_relation_revision_keeps_id_and_history(self):
        from support.entry import entry
        _entry = entry()
        ins, run, ids = knowledge_graph()
        first = dict(id=new_id('RL'), kind='supports', source=ids['a'], target=ids['b'], evidence='e1')
        ins, rid = io.import_relation(ins, first, source_ref='s1', actor_ref='u', clock=_entry.ports.clock)
        ins, again = io.import_relation(ins, {**first, 'evidence': 'e2'}, source_ref='s2', actor_ref='u', clock=_entry.ports.clock)
        row = next(r for r in ins['relations'] if r['id'] == rid)
        self.assertEqual(again, rid)
        self.assertEqual(row['revision'], 2)
        self.assertEqual(row['history'][-1]['evidence'], 'e1')

    def test_installed_relation_kinds_are_usable_without_activation(self):
        ins, run, ids = knowledge_graph()
        support = dict(kind='supports', source=ids['a'], target=ids['b'], evidence='Same recurrence shape')
        self.assertTrue(io.validate_relation(ins, support)['valid'])
        # An installed mathematical kind is active too; its evidence requirement still applies.
        result = io.validate_relation(ins, {**support, 'kind': 'formally_implies'})
        self.assertFalse(result['valid'])
        self.assertIn('formal_result_refs_required', result['reasons'])
        self.assertIn('assessment_refs_required', result['reasons'])


if __name__ == '__main__':
    unittest.main()
