"""정상 생산 후보의 한 필드를 바꿔 가져오기와 종류 계약의 거부를 확인한다."""
from copy import deepcopy
import re
import unittest
from pathlib import Path
import tempfile

from do_math import knowledge_io as io, knowledge_records as kr
from do_math.state_contract import default_state_contract
from support.fakes.clock import FakeClock
from support.knowledge_builders import knowledge_candidate
from support.state_builders import current_state
from support.storage_records import record_store


class ImportGuards(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        directory = self.enterContext(tempfile.TemporaryDirectory())
        store = record_store(Path(directory), clock=self.clock)
        head = store.initialize(*current_state())
        _, self.state, self.runtime = store.load(head)
        self.state, self.runtime, self.kid = io.import_candidate(
            self.state, self.runtime, knowledge_candidate(), source_ref='UI-fixture',
            actor_ref='user', clock=self.clock)
        default_state_contract().validate(self.state, self.runtime)

    def assert_rejected(self, candidate, reason):
        before = deepcopy((self.state, self.runtime, candidate))
        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
            io.import_candidate(self.state, self.runtime, candidate,
                source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        self.assertEqual((self.state, self.runtime, candidate), before)

    def test_unsupported_authority_field(self):
        self.assert_rejected(knowledge_candidate(formal_use='active'), 'candidate has unsupported fields')

    def test_invalid_candidate_text_fields(self):
        for field in ('kind', 'title', 'statement', 'explanation', 'summary', 'lean_code'):
            with self.subTest(field=field):
                self.assert_rejected(knowledge_candidate(**{field: 3}), 'candidate ' + field + ' is invalid')

    def test_declaration_shape_and_identifier(self):
        for names, reason in ((['truth', 'truth'], 'declaration_names must contain distinct strings'),
                              (['truth;'], 'declaration_names must be Lean identifiers'),
                              ([], 'a formal candidate requires exported declaration names')):
            with self.subTest(names=names):
                self.assert_rejected(knowledge_candidate(declaration_names=names), reason)

    def test_dependency_shape(self):
        for dependencies in ('not-a-list', [self.kid, self.kid], [False]):
            with self.subTest(dependencies=dependencies):
                self.assert_rejected(knowledge_candidate(dependencies=dependencies), 'dependencies must contain distinct references')

    def test_invalid_identifier(self):
        self.assert_rejected(knowledge_candidate(id='KN-invalid'), 'knowledge ID must be a canonical KN-prefixed ULID')

    def test_self_dependency(self):
        identifier = self.clock.new_id('KN')
        self.assert_rejected(knowledge_candidate(id=identifier, dependencies=[identifier]), 'candidate cannot depend on itself')

    def test_unknown_reused_result(self):
        self.assert_rejected(knowledge_candidate(formal_result_ref='FR-missing'), 'reused formal result must be current and accepted')

    def test_relation_claim_shape(self):
        self.assert_rejected(knowledge_candidate(relation_claim={'kind': 'supports'}),
                    'relation_claim needs kind, source, target and confirmed_scope')

    def test_relation_claim_endpoint(self):
        self.assert_rejected(knowledge_candidate(relation_claim=dict(kind='supports', source=self.kid,
                    target='KN-missing', confirmed_scope='True')), 'relation claim requires exact existing endpoints')

    def test_source_reference_shape(self):
        self.assert_rejected(knowledge_candidate(source_refs=[False]), 'source_refs must be a list of source references')

    def test_source_reference_existence(self):
        self.assert_rejected(knowledge_candidate(source_refs=['missing-source']), 'required source does not exist')

    def test_nonformal_import_without_planning_preserves_queue(self):
        before = deepcopy((self.state, self.runtime))
        state, runtime, kid = io.import_candidate(self.state, self.runtime,
            knowledge_candidate(lean_code='', declaration_names=[]), source_ref='UI-fixture',
            actor_ref='user', plan_nonformal=False, clock=self.clock)
        default_state_contract().validate(state, runtime)
        self.assertEqual(runtime['queue'], self.runtime['queue'])
        self.assertEqual(runtime['history'], [*self.runtime['history'], {
            'kind': 'knowledge_candidate_imported', 'knowledge_id': kid, 'source_ref': 'UI-fixture'}])
        self.assertIsNone(state['knowledge'][kid]['formal_result_id'])
        self.assertEqual(kr.proposal_view(state, kid)['lean_code'], '')
        self.assertEqual((self.state, self.runtime), before)

    def test_insight_references_require_known_distinct_records(self):
        insight = dict(kind='observation', title='관찰', statement='관찰 문장', summary='요약', evidence_ids=[self.kid])
        self.assertIsNone(io.validate_insight(self.state, self.runtime, insight))
        before = deepcopy((self.state, self.runtime))
        for refs, reason in (([self.kid, self.kid], 'insight evidence must contain distinct references'),
                             (['unknown'], 'unknown insight evidence: unknown')):
            with self.subTest(refs=refs), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                io.validate_insight(self.state, self.runtime, {**insight, 'evidence_ids': refs})
        self.assertEqual((self.state, self.runtime), before)

    def test_relation_rejection_and_invalid_id_are_atomic(self):
        valid = dict(kind='supports', source=self.kid, target=self.kid, evidence='관찰')
        before = deepcopy(self.state)
        for change, reason in (({'unknown': True}, 'invalid relation: unsupported_relation_fields'),
                               ({'kind': 'missing'}, 'invalid relation: unknown relation kind: missing'),
                               ({'id': 'RL-invalid'}, 'relation ID must be a canonical RL-prefixed ULID')):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                io.import_relation(self.state, {**valid, **change}, source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        self.assertEqual(self.state, before)

    def test_relation_missing_endpoints_and_evidence_are_exact(self):
        relation = dict(kind='supports', source='absent-source', target='absent-target')
        result = io.validate_relation(self.state, relation)
        self.assertEqual(result['reasons'], ['missing_source:absent-source', 'missing_target:absent-target', 'evidence_required'])
        self.assertFalse(result['valid'])
        self.assertEqual(result['definition'], io.lookup_definition(self.state, 'relation', 'supports'))

    def test_stored_relation_validation_projects_only_authored_claim(self):
        claim = dict(kind='supports', source=self.kid, target=self.kid, evidence='관찰')
        state, rid = io.import_relation(self.state, claim, source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        stored = next(r for r in state['relations'] if r['id'] == rid)
        self.assertEqual(io.validate_stored_relation(state, stored), {'valid': True, 'reasons': [],
            'definition': io.lookup_definition(state, 'relation', 'supports')})
        self.assertEqual(stored['authority'], 'research_connection')


class KindGuards(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.state = io.ensure_ontology({})
        self.definition = dict(family='knowledge', token='bounded_fact', meaning='유한 범위 관찰', constraints={})

    def test_kind_key_preserves_family_and_token(self):
        self.assertEqual(io._key('knowledge', 'bounded_fact'), 'knowledge:bounded_fact')
        self.assertEqual(io._key('relation', 'supports'), 'relation:supports')

    def test_definition_and_catalog_are_detached_from_live_registry(self):
        self.assertEqual(io._definition('knowledge', 'bounded_fact', '의미', mathematical=True, evidence=False),
            {'family': 'knowledge', 'token': 'bounded_fact', 'meaning': '의미', 'status': 'active', 'builtin': True,
             'constraints': {'mathematical_claim': True, 'requires_evidence': False,
                'requires_formal_results': True, 'requires_assessments': True}})
        before = deepcopy(self.state)
        catalog = io.catalog_definitions(self.state)
        expected = {family: [deepcopy(value) for _, value in sorted(self.state['kind_definitions'].items())
            if value['family'] == kind and value['status'] == 'active']
            for family, kind in (('knowledge', 'knowledge'), ('relations', 'relation'))}
        self.assertEqual(catalog, expected)
        catalog['knowledge'][0]['constraints'].clear()
        self.assertEqual(self.state, before)

    def test_multiple_current_definitions_are_rejected(self):
        state, token = io.register_kind_definition(self.state, self.definition, source_ref='source', actor_ref='user', clock=self.clock)
        row = deepcopy(io.lookup_definition(state, 'knowledge', token))
        row['id'] = self.clock.new_id('KD')
        state['kind_definitions'][row['id']] = row
        before = deepcopy(state)
        with self.assertRaisesRegex(ValueError, '^multiple current definitions of one kind$'):
            io.lookup_definition(state, 'knowledge', token)
        self.assertEqual(state, before)

    def test_definition_shape_family_and_constraint_rejections(self):
        cases = [({'unknown': True}, 'kind definition requires family, token, meaning and constraints'),
                 ({'family': 'unknown'}, 'kind definition has an invalid family or token'),
                 ({'token': 'Upper'}, 'kind definition has an invalid family or token'),
                 ({'constraints': {'unknown': True}}, 'kind definition has unsupported constraints'),
                 ({'constraints': {'requires_evidence': 1}}, 'kind boolean constraint expected'),
                 ({'constraints': {'required_fields': []}}, 'kind list constraints require distinct nonempty strings'),
                 ({'constraints': {'required_fields': ['title', 'title']}}, 'kind list constraints require distinct nonempty strings'),
                 ({'constraints': {'required_fields': ['formal_use']}}, 'required fields may not grant authority or add unknown fields')]
        before = deepcopy(self.state)
        for changes, reason in cases:
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                io.register_kind_definition(self.state, {**self.definition, **changes}, source_ref='source', actor_ref='user', clock=self.clock)
        self.assertEqual(self.state, before)

    def test_mathematical_definition_forces_both_evidence_requirements(self):
        state, token = io.register_kind_definition(self.state,
            {**self.definition, 'constraints': {'mathematical_claim': True}}, source_ref='source', actor_ref='user', clock=self.clock)
        self.assertEqual(token, 'bounded_fact')
        self.assertEqual(io.lookup_definition(state, 'knowledge', token)['constraints'],
            dict(mathematical_claim=True, requires_formal_results=True, requires_assessments=True))
        self.assertIsNone(io.lookup_definition(self.state, 'knowledge', token))

    def test_duplicate_token_and_unknown_lifecycle_targets(self):
        before = deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, '^kind token is already defined$'):
            io.register_kind_definition(self.state, {**self.definition, 'token': 'theorem'}, source_ref='source', actor_ref='user', clock=self.clock)
        for function, options in ((io.check_kind_definition, dict(check_ref='check', actor_ref='checker')),
                                  (io.activate_kind_definition, dict(approval_ref='approval', actor_ref='user')),
                                  (io.withdraw_kind_definition, dict(reason='오류', actor_ref='user', clock=self.clock))):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(ValueError, '^unknown kind definition$'):
                args = (self.state, {}, 'knowledge', 'missing') if function is io.withdraw_kind_definition else (self.state, 'knowledge', 'missing')
                function(*args, **options)
        self.assertEqual(self.state, before)

    def test_active_definition_cannot_be_checked_again(self):
        with self.assertRaisesRegex(ValueError, '^only candidate definitions can be checked$'):
            io.check_kind_definition(self.state, 'knowledge', 'theorem', check_ref='check', actor_ref='checker')
        self.assertEqual(io.lookup_definition(self.state, 'knowledge', 'theorem')['status'], 'active')

    def test_withdrawal_and_reregistration_preserve_predecessor(self):
        state, token = io.register_kind_definition(self.state, self.definition, source_ref='source', actor_ref='user', clock=self.clock)
        previous = deepcopy(io.lookup_definition(state, 'knowledge', token))
        withdrawn, runtime = io.withdraw_kind_definition(state, {}, 'knowledge', token, reason='수정', actor_ref='user', clock=self.clock)
        self.assertEqual(runtime, {})
        self.assertEqual(io.lookup_definition(withdrawn, 'knowledge', token)['status'], 'withdrawn')
        renewed, _ = io.register_kind_definition(withdrawn, self.definition, source_ref='source', actor_ref='user', clock=self.clock)
        self.assertEqual(io.lookup_definition(renewed, 'knowledge', token)['supersedes'], previous['id'])
        self.assertEqual(io.lookup_definition(state, 'knowledge', token), previous)

    def test_kind_constraints_reject_missing_authored_fields(self):
        for constraints, reason in (({'allowed_epistemic_statuses': ['conjecture']}, 'epistemic_status is not allowed by the kind definition'),
                                    ({'required_fields': ['confirmed_scope']}, 'candidate is missing kind-required fields')):
            with self.subTest(constraints=constraints):
                state, token = io.register_kind_definition(self.state, {**self.definition, 'constraints': constraints}, source_ref='source', actor_ref='user', clock=self.clock)
                state = io.check_kind_definition(state, 'knowledge', token, check_ref='check', actor_ref='checker')
                state = io.activate_kind_definition(state, 'knowledge', token, approval_ref='approval', actor_ref='user')
                before = deepcopy(state)
                with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                    io.import_candidate(state, {}, knowledge_candidate(kind=token), source_ref='source', actor_ref='user', clock=self.clock)
                self.assertEqual(state, before)
