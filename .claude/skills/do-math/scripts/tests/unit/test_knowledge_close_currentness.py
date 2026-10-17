"""현재성·영향·신뢰 전환의 전제별 거부와 부작용을 저장된 정상 상태에서 확인한다."""
from copy import deepcopy
import re

from do_math import knowledge as k, knowledge_records as kr
from support.knowledge_roundtrip import KnowledgeRoundtripHarness


class CurrentnessGuards(KnowledgeRoundtripHarness):
    def setUp(self):
        super().setUp()
        self.aid = self.assessment()
        self.roundtrip()

    def test_capture_basis_requires_distinct_existing_ids(self):
        for ids, reason in (([self.kid, self.kid], 'record_ids must be a list of distinct IDs'),
                            ((self.kid,), 'record_ids must be a list of distinct IDs'),
                            (['missing'], 'unknown record ID: missing')):
            with self.subTest(ids=ids), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k.capture_basis(self.state, self.runtime, ids)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_basis_rejections_identify_each_bad_row(self):
        basis = k.capture_basis(self.state, self.runtime, [self.kid])
        for changed, reasons in (({}, ['basis_not_a_list']), ([{}], ['invalid_basis_row']),
                                ([basis[0], basis[0]], ['duplicate_or_invalid_id:' + self.kid]),
                                ([{**basis[0], 'id': 'missing'}], ['missing:missing']),
                                ([{**basis[0], 'id': 1}], ['duplicate_or_invalid_id:1']),
                                ([{**basis[0], 'sha256': '0' * 64}], ['hash_changed:' + self.kid]),
                                ([{**basis[0], 'status': 'withdrawn'}], ['status_changed:' + self.kid])):
            with self.subTest(changed=changed):
                self.assertEqual(k.validate_basis(changed, self.state, self.runtime), {'valid': False, 'reasons': reasons})
        self.assertEqual(k.validate_basis(basis, self.state, self.runtime), {'valid': True, 'reasons': []})

    def test_reference_locators_do_not_treat_prose_as_records(self):
        known = {self.kid}
        self.assertEqual(k._field_refs({'path': 'input/file', 'hash': 'digest'}, strict=False, known_ids=known), set())
        self.assertEqual(k._field_refs({'nested': [self.kid, {'ref': 'unknown'}]}, strict=True, known_ids=known), {self.kid, 'unknown'})
        self.assertEqual(k._field_refs({'id': self.kid, 'path': 'ignored'}, strict=True, known_ids=known), {self.kid})
        self.assertEqual(k._explicit_refs({'history': [{'dependencies': ['old']}], 'nested': [{'dependencies': [self.kid]}]}, known), {self.kid})

    def test_basis_ignores_scheduling_and_history_but_preserves_content_and_effect(self):
        """~0.44s: keep real schema publication/reload and synthetic sealed review provenance."""
        record = self.state['knowledge'][self.kid]
        fid, xid = record['formal_result_id'], record['exposition_id']
        uid = next(iter(self.state['assessment_uses']))
        ids = [self.kid, fid, xid, self.aid, uid]
        basis = k.capture_basis(self.state, self.runtime, ids)
        # A real review-cycle producer supplies the scheduling coordinate. Its
        # executions and cycle also go through the existing storage harness.
        cycle = self.cycle()
        record['review_cycle_id'] = cycle['id']
        exact_before = {rid: k._hash(row) for rid, row in kr.all_records(self.state).items() if rid in ids}
        # Scheduling belongs to knowledge; authored exposition and sealed
        # identity judgments have no mutable administrative history.
        record['previous_review_cycle_id'] = cycle['id']
        self.state['assessment_uses'][uid]['history'].append({'reason': 'administrative annotation'})
        for family, identifier in (('formal_results', fid), ('assessment_uses', uid)):
            self.state[family][identifier].setdefault('use_history', []).append({'reason': 'administrative annotation'})
        self.roundtrip()
        self.assertEqual(k.validate_basis(basis, self.state, self.runtime), {'valid': True, 'reasons': []})
        self.assertTrue(all(k._hash(kr.all_records(self.state)[rid]) != exact_before[rid]
                            for rid in (self.kid, fid, uid)),
                        'exact record identity still includes the administrative bytes')
        for rid in (xid, self.aid):
            self.assertEqual(k._hash(kr.all_records(self.state)[rid]), exact_before[rid])
        mutations = [('knowledge', self.kid, 'title', 'Corrected title'),
                     ('knowledge', self.kid, 'revision', 2),
                     ('knowledge', self.kid, 'origin_refs', ['changed provenance']),
                     ('knowledge', self.kid, 'use_suspended', True),
                     ('formal_results', fid, 'publication_state', 'rejected'),
                     ('formal_results', fid, 'formal_use', 'suspended'),
                     ('formal_results', fid, 'verification', {}),
                     ('formal_results', fid, 'trust_environment_id', 'TE-other'),
                     ('expositions', xid, 'items', []),
                     ('identity_assessments', self.aid, 'decision', 'unresolved'),
                     ('identity_assessments', self.aid, 'review_cycle_id', cycle['id']),
                     ('assessment_uses', uid, 'status', 'suspended')]
        for family, identifier, field, value in mutations:
            changed = deepcopy(self.state)
            changed[family][identifier][field] = value
            with self.subTest(family=family, field=field):
                self.assertIn('hash_changed:' + identifier, k.validate_basis(basis, changed, self.runtime)['reasons'])
        changed = deepcopy(self.state)
        del changed['knowledge'][self.kid]
        self.assertIn('missing:' + self.kid, k.validate_basis(basis, changed, self.runtime)['reasons'])

    def test_research_use_rejects_missing_identifier_and_suspended_record(self):
        for field, value, reasons in (('id', '', ['missing_or_cyclic_research_dependency']),
                                     ('use_suspended', True, ['research_record_not_active']),
                                     ('exposition_id', 'missing', ['research_exposition_not_active'])):
            record = {**self.state['knowledge'][self.kid], field: value}
            with self.subTest(field=field):
                self.assertEqual(k.assess_research_use(record, self.state), {'valid': False, 'reasons': reasons})
        self.assertEqual(k.assess_research_use(self.state['knowledge'][self.kid], self.state), {'valid': True, 'reasons': []})

    def test_research_dependency_cycle_and_missing_dependency(self):
        for dependency in (self.kid, 'missing'):
            state = deepcopy(self.state)
            state['knowledge'][self.kid]['dependencies'] = [dependency]
            with self.subTest(dependency=dependency):
                self.assertEqual(k.assess_research_use(state['knowledge'][self.kid], state),
                    {'valid': False, 'reasons': ['research_dependency_not_current:' + dependency]})
                self.assertEqual(kr.usable_links(state, self.kid), [])
        self.assertEqual(self.repo.load()[1], self.state)

    def test_impact_roots_declarations_and_exclusions_must_exist(self):
        for roots, declared, excluded, reason in (([], [], [], 'impact roots must exist'),
                (['missing'], [], [], 'impact roots must exist'),
                ([self.kid], ['missing'], [], 'declared impact refers to unknown records'),
                ([self.kid], [], ['missing'], 'excluded impact dependents must exist')):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k.plan_impact(self.state, self.runtime, roots, declared, excluded_dependents=excluded)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_confirmation_requires_exact_digest_scope_and_independence(self):
        plan = k.plan_impact(self.state, self.runtime, [self.kid], [], sensitive=True)
        confirmation = dict(plan_digest=plan['digest'], decision='approve', review_ref='review',
            reviewer_ref='independent', producer_ref='producer', affected_ids=plan['computed_impact'])
        self.assertEqual(k._confirmed_impact(plan, confirmation), set(plan['computed_impact']))
        for field, value in (('plan_digest', '0' * 64), ('decision', 'reject'), ('review_ref', ''),
                              ('reviewer_ref', 'producer'), ('producer_ref', ''), ('affected_ids', ['missing'])):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, '^impact requires independent scope and disposition confirmation$'):
                k._confirmed_impact(plan, {**confirmation, field: value})
        with self.assertRaisesRegex(ValueError, '^impact plan digest is invalid$'):
            k._confirmed_impact({**plan, 'digest': '0' * 64}, confirmation)

    def test_reviewed_impacts_require_a_nonempty_mapping(self):
        for plans in ({}, []):
            with self.subTest(plans=plans), self.assertRaisesRegex(ValueError, '^reviewed impacts require at least one named plan$'):
                k.apply_reviewed_impacts(self.state, self.runtime, plans, {}, reason='재검토', clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_stale_impact_rejects_without_effects(self):
        plan = k.plan_impact(self.state, self.runtime, [self.kid], [])
        changed = deepcopy(self.state)
        changed['knowledge'][self.kid]['title'] = '다른 제목'
        before = deepcopy((changed, self.runtime))
        with self.assertRaisesRegex(ValueError, '^impact plan is stale or altered$'):
            k.apply_impact(changed, self.runtime, plan, reason='재검토', clock=self.clock)
        self.assertEqual((changed, self.runtime), before)

    def test_suspension_requires_concrete_objection_references(self):
        for refs in ([], '', [False], ['']):
            with self.subTest(refs=refs), self.assertRaisesRegex(ValueError, '^suspension requires concrete defect or independent objection references$'):
                k.suspend_assessment_use(self.state, self.runtime, self.aid,
                    reason='결함', actor_ref='user', reason_refs=refs, clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_repeated_suspension_records_reason_without_mutating_sealed_vote(self):
        state, runtime = k.suspend_assessment_use(self.state, self.runtime, self.aid,
            reason='첫 결함', actor_ref='user', reason_refs=['defect:first'], clock=self.clock)
        state, runtime = k.suspend_assessment_use(state, runtime, self.aid,
            reason='두번째 결함', actor_ref='user', reason_refs=['defect:second'], clock=self.clock)
        use = next(u for u in state['assessment_uses'].values() if u['assessment_id'] == self.aid)
        self.assertEqual(use['history'][-1], {'from': 'suspended', 'to': 'suspended',
            'reason': '두번째 결함', 'actor_ref': 'user', 'reason_refs': ['defect:second']})
        self.assertEqual(state['identity_assessments'], self.state['identity_assessments'])
        self.assertEqual(kr.usable_links(state, self.kid), [])

    def test_reassessment_requires_original_policy_and_proposal(self):
        before = deepcopy((self.state, self.runtime))
        with self.assertRaisesRegex(ValueError, '^reassessment must identify the exact original judgment and policy$'):
            k.apply_assessment_reassessment(self.state, self.runtime, self.aid, 'missing',
                reason='재검토', actor_ref='user', clock=self.clock, at=self.clock.now())
        self.assertEqual((self.state, self.runtime), before)

    def test_transition_unknown_invalid_and_active_environment(self):
        for environment_id in ('missing', 'TE-test'):
            reason = 'unknown or invalid transition environment' if environment_id == 'missing' else 'new trust environment is already active'
            with self.subTest(environment_id=environment_id), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k.begin_transition(self.state, environment_id, clock=self.clock)
        with self.assertRaisesRegex(ValueError, '^unknown trust environment: missing$'):
            k.invalidate_environment(self.state, self.runtime, 'missing', '결함', clock=self.clock)
        self.assertEqual(self.repo.load()[1], self.state)

    def transition(self):
        state = deepcopy(self.state)
        state['trust_environments']['TE-next'] = {**deepcopy(state['trust_environments']['TE-test']),
            'id': 'TE-next', 'status': 'registered'}
        transition = k.begin_transition(state, 'TE-next', clock=self.clock)
        formal = state['formal_results'][state['knowledge'][self.kid]['formal_result_id']]
        result = {**deepcopy(formal['verification']), 'id': self.kid}
        return state, transition, result

    def test_transition_results_reject_wrong_environment_target_and_status(self):
        state, transition, result = self.transition()
        before = deepcopy((state, transition))
        for change, reason in (({'id': 'missing'}, 'result is not for a transition target: missing'),
                               ({'status': 'stopped'}, 'transition result has an unsupported status')):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k.record_transition_result(state, transition, {**result, **change})
        with self.assertRaisesRegex(ValueError, '^unknown trust environment: missing$'):
            k.record_transition_result(state, {**transition, 'to_environment': 'missing'}, result)
        self.assertEqual((state, transition), before)

    def test_activation_requires_verified_complete_and_unchanged_basis(self):
        state, transition, result = self.transition()
        ready = k.record_transition_result(state, transition, result)
        self.assertEqual(ready['status'], 'ready')
        for changed, pending, reason in ((state, transition, 'all transition targets must be verified'),
                ({**state, 'active_trust_environment': None}, ready, 'active trust environment changed during transition'),
                (state, {**ready, 'to_environment': 'missing'}, 'transition environment is unavailable')):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                k.activate_transition(changed, pending, runtime=self.runtime, clock=self.clock, at=self.clock.now())
        state['knowledge'][self.kid]['title'] = '변경된 제목'
        before = deepcopy(state)
        with self.assertRaisesRegex(ValueError, '^transition basis changed: ' + re.escape(self.kid) + '$'):
            k.activate_transition(state, ready, runtime=self.runtime, clock=self.clock, at=self.clock.now())
        self.assertEqual(state, before)

    def test_staged_review_rejects_missing_stored_transition(self):
        state, transition, result = self.transition()
        result['declaration_evidence']['truth']['type'] = '다른 표현'
        transition = k.record_transition_result(state, transition, result)
        before = deepcopy(state)
        with self.assertRaisesRegex(ValueError, '^staged identity review transition is stale or belongs to another transition$'):
            k.activate_transition(state, transition, runtime=self.runtime, clock=self.clock, at=self.clock.now())
        self.assertEqual(state, before)

    def test_staged_review_target_must_exist(self):
        state, transition, result = self.transition()
        transition = k.record_transition_result(state, transition, result)
        with self.assertRaisesRegex(ValueError, '^staged review target is not in the transition$'):
            k._staged_review_basis(state, transition, 'missing')
        basis = k._staged_review_basis(state, transition, self.kid)
        self.assertEqual(basis['record'], state['knowledge'][self.kid])
        self.assertEqual(basis['target_environment'], state['trust_environments']['TE-next'])
        self.assertEqual(basis['live_identity_basis'], kr.identity_basis(state, self.kid))

    def test_transition_normalization_removes_only_review_receipts(self):
        state, transition, result = self.transition()
        transition = k.record_transition_result(state, transition, result)
        expected = deepcopy(transition)
        transition['results'][self.kid]['identity_review'] = {'decision': 'match'}
        self.assertEqual(k._transition_without_identity_reviews(transition), expected)
        self.assertEqual(transition['results'][self.kid]['identity_review'], {'decision': 'match'})

    def test_empty_revision_changes_are_rejected(self):
        for changes in ({}, []):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, '^changes must be a nonempty object$'):
                k.validate_changes(changes)
        self.assertEqual(self.repo.load()[1], self.state)

    def test_formal_authority_assessment_returns_exact_basis(self):
        formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        self.assertEqual(k.assess_use(formal, self.state), {'valid': True, 'reasons': [], 'basis': []})
        self.assertEqual(k.assess_use({**formal, 'formal_use': 'suspended'}, self.state),
            {'valid': False, 'reasons': ['formal_result_not_current'], 'basis': []})

    def test_withdraw_relation_kind_suspends_only_matching_relations(self):
        from do_math import knowledge_io as io
        state, rid = io.import_relation(self.state, dict(kind='supports', source=self.kid,
            target=self.kid, evidence='관찰'), source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        state, other = io.import_relation(state, dict(kind='cites', source=self.kid,
            target=self.kid, evidence='인용'), source_ref='UI-fixture', actor_ref='user', clock=self.clock)
        self.repo.validate_candidate(state, self.runtime)
        before = deepcopy(state)
        changed, runtime = io.withdraw_kind_definition(state, self.runtime, 'relation', 'supports',
            reason='의미 결함', actor_ref='user', clock=self.clock)
        self.assertEqual(next(r for r in changed['relations'] if r['id'] == rid)['status'], 'suspended')
        self.assertEqual(next(r for r in changed['relations'] if r['id'] == other), next(r for r in state['relations'] if r['id'] == other))
        self.assertEqual(state, before)
        self.assertEqual(changed['identity_assessments'], state['identity_assessments'])

    def test_invalidating_unused_environment_preserves_active_knowledge(self):
        state, _, _ = self.transition()
        before = deepcopy(state)
        changed, runtime = k.invalidate_environment(state, self.runtime, 'TE-next', '결함', clock=self.clock)
        self.assertEqual(changed['active_trust_environment'], 'TE-test')
        self.assertEqual(changed['formal_results'], state['formal_results'])
        self.assertEqual(runtime, self.runtime)
        self.assertEqual(changed['trust_environments']['TE-next']['status'], 'invalid')
        self.assertEqual(state, before)

    def test_repeated_impact_does_not_duplicate_planner_action(self):
        plan = k.plan_impact(self.state, self.runtime, [self.aid], [])
        first, runtime = k.apply_reviewed_impacts(self.state, self.runtime, {'vote': plan}, {}, reason='결함', clock=self.clock)
        second, repeated = k.apply_reviewed_impacts(first, runtime, {'vote': plan}, {}, reason='결함', clock=self.clock)
        self.assertEqual(repeated['queue'], runtime['queue'])
        self.assertEqual(second['formal_results'], self.state['formal_results'])
        self.assertEqual(second['identity_assessments'], self.state['identity_assessments'])
        self.assertEqual(repeated['history'], [*runtime['history'], runtime['history'][-1]])
