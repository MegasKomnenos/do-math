"""저장 검증을 통과한 정상 기록에서 한 전제만 손상시킨다. 실행 성적은 별도다."""
from copy import deepcopy
import re

from do_math import knowledge as k, knowledge_io as io, knowledge_records as kr
from support.knowledge_builders import knowledge_candidate
from support.knowledge_roundtrip import KnowledgeRoundtripHarness


class RecordGuards(KnowledgeRoundtripHarness):
    def setUp(self):
        super().setUp()
        self.aid = self.assessment()
        self.roundtrip()
        self.fid = self.state['knowledge'][self.kid]['formal_result_id']
        self.xid = self.state['knowledge'][self.kid]['exposition_id']

    def test_formal_evidence_rejects_each_fixed_input_change(self):
        formal = self.state['formal_results'][self.fid]
        environment = self.state['trust_environments']['TE-test']
        cases = [('toolchain', {}, 'verification toolchain differs from approved environment'),
                 ('source_sha256', '0' * 64, 'verification source differs from formal result'),
                 ('declarations', ['other'], 'verification declarations differ from formal result'),
                 ('declaration_evidence', {}, 'verification evidence incomplete: declaration_evidence'),
                 ('dependency_closure', {}, 'verification evidence incomplete: dependency_closure'),
                 ('axioms', {}, 'verification evidence incomplete: axioms'),
                 ('dependency_evidence', {}, 'dependency body evidence differs from the closure'),
                 ('axioms', {'truth': ['sorryAx']}, 'verification uses unapproved axioms')]
        before = deepcopy(self.state)
        for field, value, reason in cases:
            with self.subTest(field=field, value=value):
                verification = {**deepcopy(formal['verification']), field: value}
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    kr.validate_formal_evidence(formal, verification, environment)
        self.assertEqual(self.state, before)

    def test_sealed_formal_replay_is_exact_and_changed_result_is_rejected(self):
        verification = deepcopy(self.state['formal_results'][self.fid]['verification'])
        self.assertEqual(kr.record_formal_result(self.state, self.kid, verification, 'TE-test', runtime=self.runtime), self.state)
        verification['status'] = 'failed'
        with self.assertRaisesRegex(ValueError, '^sealed formal result must be replaced with a new result ID$'):
            kr.record_formal_result(self.state, self.kid, verification, 'TE-test', runtime=self.runtime)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_publication_waits_for_transition(self):
        state = deepcopy(self.state)
        state['trust_environments']['TE-next'] = {**deepcopy(state['trust_environments']['TE-test']),
            'id': 'TE-next', 'status': 'registered'}
        run = deepcopy(self.runtime)
        run['trust_bindings']['TE-next'] = deepcopy(run['trust_bindings']['TE-test'])
        pending = k.begin_transition(state, 'TE-next', clock=self.clock)
        run.setdefault('trust_transitions', {})[pending['id']] = pending
        self.repo.validate_candidate(state, run)
        verification = self.state['formal_results'][self.fid]['verification']
        with self.assertRaisesRegex(ValueError, '^formal publication waits for the trust transition$'):
            kr.record_formal_result(state, self.kid, verification, 'TE-test', runtime=run)
        with self.assertRaisesRegex(ValueError, '^identity publication waits for the trust transition$'):
            kr.record_identity_assessment(state, self.kid,
                {'decision': 'match', 'basis': kr.identity_basis(state, self.kid)}, 'policy', runtime=run, clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_identity_replay_and_collision(self):
        assessment = deepcopy(self.state['identity_assessments'][self.aid])
        state, aid = kr.record_identity_assessment(self.state, self.kid, assessment,
            assessment['policy_ref'], runtime=self.runtime, clock=self.clock)
        self.assertEqual((state, aid), (self.state, self.aid))
        assessment['decision'] = 'mismatch'
        with self.assertRaisesRegex(ValueError, '^immutable assessment ID already exists$'):
            kr.record_identity_assessment(self.state, self.kid, assessment,
                assessment['policy_ref'], runtime=self.runtime, clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_identity_policy_and_decision_guards(self):
        assessment = {'decision': 'match', 'basis': kr.identity_basis(self.state, self.kid)}
        for changes, policy, reason in (({}, ' ', 'identity assessment requires a fixed policy reference'),
                                       ({'decision': 'yes'}, 'policy', 'invalid identity decision'),
                                       ({'basis': {}}, 'policy', 'identity assessment must name the exact current formal and exposition basis')):
            with self.subTest(changes=changes, policy=policy), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                kr.record_identity_assessment(self.state, self.kid, {**assessment, **changes}, policy, runtime=self.runtime, clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_obsolete_assessment_cannot_restore(self):
        state = deepcopy(self.state)
        state['expositions'][self.xid]['lifecycle'] = 'superseded'
        before = deepcopy(state)
        with self.assertRaisesRegex(ValueError, '^cannot restore an obsolete assessment$'):
            kr.set_assessment_use(state, self.aid, 'active', '확인', 'user')
        self.assertEqual(state, before)
        self.assertFalse(kr.assessment_current(state, self.aid))

    def test_use_status_and_cardinality_guards(self):
        for status, reason, actor in (('unknown', '사유', 'user'), ('active', '', 'user'), ('active', '사유', '')):
            with self.subTest(status=status, reason=reason, actor=actor), self.assertRaisesRegex(ValueError, '^assessment use requires status, reason and actor$'):
                kr.set_assessment_use(self.state, self.aid, status, reason, actor)
        state = deepcopy(self.state)
        state['assessment_uses'] = {}
        with self.assertRaisesRegex(ValueError, '^assessment must have exactly one use record$'):
            kr.set_assessment_use(state, self.aid, 'suspended', '사유', 'user')
        self.assertEqual(state['assessment_uses'], {})

    def test_withdrawn_use_cannot_be_revived(self):
        state = kr.set_assessment_use(self.state, self.aid, 'withdrawn', '결함', 'user')
        before = deepcopy(state)
        with self.assertRaisesRegex(ValueError, '^withdrawn assessment use cannot be restored$'):
            kr.set_assessment_use(state, self.aid, 'active', '복구', 'user')
        self.assertEqual(state, before)
        self.assertEqual(state['identity_assessments'], self.state['identity_assessments'])
        use = next(u for u in state['assessment_uses'].values() if u['assessment_id'] == self.aid)
        self.assertEqual(use['history'], [{'from': 'active', 'to': 'withdrawn', 'reason': '결함', 'actor_ref': 'user'}])

    def test_duplicate_exposition_items_are_rejected_by_storage(self):
        state = deepcopy(self.state)
        items = state['expositions'][self.xid]['items']
        items[1]['id'] = items[0]['id']
        with self.assertRaisesRegex(ValueError, 'duplicate exposition item ID'):
            self.repo.validate_candidate(state, self.runtime)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_duplicate_assessment_use_is_rejected_by_storage(self):
        state = deepcopy(self.state)
        use = deepcopy(next(u for u in state['assessment_uses'].values() if u['assessment_id'] == self.aid))
        use['id'] = self.clock.new_id('AU')
        state['assessment_uses'][use['id']] = use
        with self.assertRaisesRegex(ValueError, 'duplicate assessment use'):
            self.repo.validate_candidate(state, self.runtime)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_reused_source_and_declarations_cannot_differ(self):
        for change, reason in (({'lean_code': 'theorem other : True := True.intro'}, 'reused formal source differs'),
                               ({'declaration_names': ['other']}, 'reused formal declarations differ')):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                io.import_candidate(self.state, self.runtime, knowledge_candidate(formal_result_ref=self.fid, **change),
                    source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_reader_and_judgment_views_are_detached(self):
        before = deepcopy(self.state)
        view = kr.reader_view(self.state, self.kid)
        self.assertEqual(view['identity_assessments'], [self.state['identity_assessments'][self.aid]])
        self.assertEqual(view['formal_result']['verification'], kr.judged_verification(self.state['formal_results'][self.fid]['verification']))
        self.assertEqual(view['status'], 'verified')
        view['identity_assessments'][0]['decision'] = 'mismatch'
        view['formal_result']['verification']['toolchain'].clear()
        self.assertEqual(self.state, before)

    def test_formal_overlay_does_not_publish(self):
        before = deepcopy(self.state)
        overlay = kr.formal_overlay(self.state, self.fid, formal_use='suspended')
        self.assertEqual(overlay['formal_results'][self.fid]['formal_use'], 'suspended')
        self.assertEqual(kr.usable_links(overlay, self.kid), [])
        self.assertEqual(self.state, before)
        self.assertEqual(self.repo.load()[1], before)

    def test_unknown_authority_family_has_exact_reason(self):
        record = self.state['expositions'][self.xid]
        self.assertEqual(k.assess_use(record, self.state), {'valid': False,
            'reasons': ['record_is_not_a_verified_knowledge_authority'], 'basis': []})
        with self.assertRaisesRegex(TypeError, '^record must be an object$'):
            k.assess_use([], self.state)

    def test_exposition_items_reject_blank_list_member(self):
        candidate = knowledge_candidate(definitions=[' '])
        before = deepcopy(candidate)
        with self.assertRaisesRegex(ValueError, '^exposition text must be nonempty$'):
            kr.exposition_items(candidate)
        self.assertEqual(candidate, before)

    def test_knowledge_view_reports_exact_live_links(self):
        record = self.state['knowledge'][self.kid]
        use = next(u for u in self.state['assessment_uses'].values() if u['assessment_id'] == self.aid)
        self.assertEqual(kr.knowledge_view(self.state), [{'id': self.kid, 'title': record['title'],
            'lifecycle': 'active', 'formal_result_id': self.fid, 'formal_valid': True, 'usable': True,
            'links': [{'formal_result_id': self.fid, 'exposition_id': self.xid,
                'assessment_id': self.aid, 'assessment_use_id': use['id']}]}])
        self.assertTrue(kr.validate_knowledge_records(self.state))

    def test_decision_reference_keeps_currentness_separate_from_content(self):
        record = self.state['knowledge'][self.kid]
        before = deepcopy(self.state)
        self.assertEqual(k.decision_reference(record, self.state), {'id': self.kid,
            'revision': record.get('revision', 1), 'content_sha256': k.content_hash(record),
            'status': 'active', 'use_suspended': False, 'usable': True,
            'trust_environment_id': 'TE-test', 'trust_environment_state': {'status': 'active', 'active': True},
            'source_basis': record['source_basis']})
        self.assertEqual(k.content_hash({**record, 'revision': 30, 'history': ['bookkeeping']}), k.content_hash(record))
        self.assertNotEqual(k.content_hash({**record, 'title': '수정'}), k.content_hash(record))
        self.assertEqual(self.state, before)

    def test_source_change_suspends_uses_without_rewriting_judgments(self):
        before = deepcopy((self.state, self.runtime))
        changed, runtime = k.suspend_for_source_change(self.state, self.runtime, self.kid,
            source_name='source', reason='원천 변경', actor_ref='user', clock=self.clock)
        use = next(u for u in changed['assessment_uses'].values() if u['assessment_id'] == self.aid)
        self.assertEqual(use['status'], 'suspended')
        self.assertEqual(use['use_history'][-1], {'reason': '원천 변경', 'source_name': 'source', 'actor_ref': 'user'})
        self.assertEqual(changed['identity_assessments'], self.state['identity_assessments'])
        self.assertEqual(kr.usable_links(changed, self.kid), [])
        self.assertEqual((self.state, self.runtime), before)
