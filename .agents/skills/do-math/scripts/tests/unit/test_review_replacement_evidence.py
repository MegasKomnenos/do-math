"""실제 부여·복구·위임 생산물의 대체 권한을 다시 검증한다."""
from copy import deepcopy

from do_math import review_cycle as rc, governance, delegations
from do_math.canonical import exact_content_hash
from support.review_inputs import grant_replacement, review_stage_output
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm


def setUpModule():
    warm()


class ReplacementEvidenceTests(ReviewOwnerCase):
    def blocked(self):
        grant_replacement(self.engine)
        cid, action = self.opened()
        cycle = rc.record_turn(self.engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'user', 'message_id': 'good', 'content': '검증된 원문'},
            {'role': 'tool', 'message_id': 'lost', 'content': '손실될 원문'}])
        cycle['turns'][action['slot']][1]['content'] = '변조'
        self.engine.runtime['review_cycles'][cid] = cycle
        self.engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
        return cid, action

    def authorized(self):
        cid, action = self.blocked()
        outcome = self.engine._authorize_review_replacement(action, grant_id='GR-review')
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        return cid, action, outcome

    def authorize_copy(self, cycle, action):
        return rc.authorize_record_replacement(cycle, rc.review_action(action), self.engine.instance,
            runtime=self.engine.runtime, grant_id='GR-review', clock=self.engine.ports.clock)

    def test_nonpending_or_unblocked_slot_cannot_be_replaced(self):
        cid, action = self.opened()
        cycle = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(self.authorize_copy(cycle, {**action, 'round': 9})['disposition'], 'invalid_action')
        outcome = self.authorize_copy(cycle, action)
        self.assertEqual(outcome['disposition'], 'not_waiting_for_replacement')
        self.assertIs(outcome['cycle'], cycle)
        self.assertEqual(cycle['replacement_actions'], {})

    def test_blocked_index_must_name_an_actual_recovery_event(self):
        cid, action = self.blocked()
        original = self.engine.runtime['review_cycles'][cid]
        for index in (True, -1, 99, '0'):
            cycle = deepcopy(original)
            cycle['blocked_actions'][rc.slot_key(action)] = index
            before = deepcopy(cycle)
            with self.subTest(index=index):
                outcome = self.authorize_copy(cycle, action)
                self.assertEqual(outcome['disposition'], 'invalid_recovery_record')
                self.assertEqual(cycle, before)

    def test_recovery_event_must_be_permanent_and_same_slot(self):
        cid, action = self.blocked()
        original = self.engine.runtime['review_cycles'][cid]
        for field, value in [('retryable', True), ('action', {'stage': 'initial', 'slot': 'other', 'round': 1})]:
            cycle = deepcopy(original)
            cycle['recovery_events'][0][field] = value
            with self.subTest(field=field):
                self.assertEqual(self.authorize_copy(cycle, action)['disposition'], 'invalid_recovery_record')
                self.assertEqual(cycle['replacement_actions'], {})

    def test_nonlist_transcript_cannot_be_reconstructed_by_authorization(self):
        cid, action = self.blocked()
        original = self.engine.runtime['review_cycles'][cid]
        for family in ('turns', 'transcript_manifest'):
            cycle = deepcopy(original)
            cycle[family][action['slot']] = {}
            with self.subTest(family=family):
                result = self.authorize_copy(cycle, action)
                self.assertEqual(result['disposition'], 'invalid_recovery_record')
                self.assertEqual(result['reason'], 'transcript containers cannot be reconstructed as ordered messages')
                self.assertIs(result['cycle'], cycle)

    def test_repeated_authorization_returns_same_action_and_preserves_archive(self):
        cid, action, first = self.authorized()
        before = deepcopy(self.engine.runtime['review_cycles'][cid])
        second = self.authorize_copy(self.engine.runtime['review_cycles'][cid], action)
        self.assertEqual(second['disposition'], 'replacement_ready')
        self.assertEqual(second['action'], first['action'])
        self.assertEqual(second['cycle'], before)
        self.assertEqual(len(before['transcript_replacements']), 1)
        self.assertEqual(before['transcript_replacements'][0]['omitted_indices'], [1])
        self.assertEqual([m['content'] for m in before['turns'][action['slot']]], ['검증된 원문'])

    def test_replacement_manifest_must_name_exact_grant(self):
        cid, _, outcome = self.authorized()
        cycle, action = self.engine.runtime['review_cycles'][cid], outcome['action']
        output = review_stage_output(cycle, action['stage'])
        manifest = {'replacement_for': action['replacement_for'], 'grant_id': action['grant_id'], 'grant_sha256': action['grant_sha256']}
        before = deepcopy(cycle)
        for field in ('grant_id', 'grant_sha256'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'replacement input manifest has another authorization'):
                rc.accept_result(cycle, action, output, 'fresh', {**manifest, field: 'other'})
        self.assertEqual(cycle, before)

    def test_replacement_authority_rejects_changed_grant_hash(self):
        cid, _, outcome = self.authorized()
        cycle = self.engine.runtime['review_cycles'][cid]
        replacement = deepcopy(cycle['replacement_actions'][rc.slot_key(outcome['action'])])
        replacement['grant_sha256'] = '0' * 64
        self.assertEqual(rc.replacement_authority(self.engine.instance, self.engine.runtime, cycle, replacement,
            clock=self.engine.ports.clock, at=self.engine.ports.clock.now()), {'allowed': False, 'reason': 'replacement grant changed'})

    def test_engine_rejects_nonmatching_authorized_action(self):
        _, action, outcome = self.authorized()
        full = {**action, **outcome['action'], 'grant_sha256': '0' * 64}
        before = deepcopy(self.engine.runtime)
        self.assertEqual(self.engine._review_replacement_authority(full),
                         {'allowed': False, 'reason': 'replacement does not match the authorized slot'})
        self.assertEqual(self.engine.runtime, before)

    def test_revocation_blocks_admission_and_acceptance(self):
        _, action, outcome = self.authorized()
        full = {**action, **outcome['action']}
        self.engine.instance['grants']['GR-review']['status'] = 'revoked'
        before = deepcopy(self.engine.runtime)
        result = self.engine._admit_review_execution(full, {'id': 'new', 'actor_kind': 'ai', 'owner_activity_id': 'AY-new', 'status': 'queued'})
        self.assertEqual(result['disposition'], 'authorization_denied')
        self.assertFalse(result['authority']['allowed'])
        self.assertEqual(self.engine.runtime, before)
        self.assert_engine_rejected('replacement authority is no longer current', lambda: self.engine._apply_identity_review(full, {}, 'new'))

    def test_revocation_after_admission_rejects_first_delivered_input(self):
        _, action, outcome = self.authorized()
        full = {**action, **outcome['action']}
        execution = self.engine._register_execution(full, {'id': 'EX-admitted-replacement', 'role': 'identity_review',
            'status': 'running', 'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        self.assertIsNotNone(execution)
        execution['input_snapshot'] = self.engine.head
        self.assertEqual(self.engine._prepare_review_context(full, self.root / 'replacement-input')['disposition'], 'ready')
        self.engine.instance['grants']['GR-review']['status'] = 'revoked'
        self.assert_engine_rejected('replacement authority is no longer current',
            lambda: self.engine._record_review_input(full, execution['id']))

    def test_denied_retry_restores_the_original_block_without_new_recovery_event(self):
        cid, action, outcome = self.authorized()
        full = {**action, **outcome['action']}
        self.engine.instance['grants']['GR-review']['status'] = 'revoked'
        before = deepcopy(self.engine.runtime['review_cycles'][cid])
        result = self.engine._retry_review_restoration(full, self.root / 'denied-retry')
        self.assertEqual(result['disposition'], 'authorization_denied')
        after = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(after['blocked_actions'], before['blocked_actions'])
        self.assertEqual(after['recovery_events'], before['recovery_events'])

    def finished_replacement(self):
        cid, _, _ = self.authorized()
        for _ in range(2):
            self.scene.execute()
        cycle = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['decision'], 'match')
        self.assertEqual(len(cycle['replacement_receipts']), 1)
        return cycle

    def test_sealed_replacement_requires_current_instance(self):
        cycle = self.finished_replacement()
        with self.assertRaisesRegex(ValueError, 'replacement replay requires current governance sources'):
            rc.validate_sealed_review(cycle, self.engine.runtime, clock=self.engine.ports.clock, at=self.engine.ports.clock.now())
        self.assertEqual(cycle['decision'], 'match')

    def test_sealed_replacement_rejects_missing_receipt_authorization_and_archive(self):
        original = self.finished_replacement()
        for field, value, reason in [('replacement_receipts', [], 'replacement has no preserved authorization and sealed input'),
                ('transcript_replacements', [], 'replacement transcript archive is missing')]:
            cycle = {**original, field: value}
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, reason):
                rc.validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance,
                    clock=self.engine.ports.clock, at=self.engine.ports.clock.now())

    def test_sealed_replacement_rejects_changed_recovery_coordinate(self):
        cycle = deepcopy(self.finished_replacement())
        cycle['recovery_events'][0]['retryable'] = True
        with self.assertRaisesRegex(ValueError, 'replacement recovery coordinate changed'):
            rc.validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance,
                clock=self.engine.ports.clock, at=self.engine.ports.clock.now())

    def test_sealed_replacement_rechecks_revoked_authority(self):
        cycle = self.finished_replacement()
        self.engine.instance['grants']['GR-review']['status'] = 'revoked'
        with self.assertRaisesRegex(ValueError, 'replacement authority is not current'):
            rc.validate_sealed_review(cycle, self.engine.runtime, instance=self.engine.instance,
                clock=self.engine.ports.clock, at=self.engine.ports.clock.now())

    def delegated(self):
        cid, action = self.blocked()
        engine = self.engine
        engine.instance['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user',
            'kind': 'review_replacement', 'source_ref': 'SOURCE-review'}
        engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
            {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {'id': 'DG', 'status': 'active',
             'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
             'included_targets': ['K1'], 'excluded_targets': [], 'external_effects': [],
             'resource_limits': {}, 'expires_at': None}}, source_ref='SOURCE-review', clock=engine.ports.clock)
        case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K1', 'basis_refs': [cid],
                'external_effects': [], 'resources': {}, 'effect': {'review_cycle_id': cid,
                'stage': action['stage'], 'slot': action['slot'], 'round': action['round'],
                'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}}
        app = delegations.prepare_application(engine.instance, engine.runtime, 'DG', case, now_iso=engine.ports.clock.now())
        for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
            judgment_action = {'id': 'AC-' + eid, 'role': 'intent_interpretation',
                               'delegation_application_id': app['id'], 'delegation_stage': stage}
            execution = engine._register_execution(judgment_action, {'id': eid, 'role': 'intent_interpretation',
                'status': 'running', 'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
            self.assertIsNotNone(execution)
            execution['delegation_input_sha256'] = app['input_sha256']
            delegations.record_judgment(engine.runtime, app['id'], {'input_sha256': app['input_sha256'],
                'decision': 'within_scope', 'reason': '승인된 동일 슬롯 복구'}, execution_id=eid, stage=stage)
        case['application_id'] = app['id']
        outcome = engine._authorize_review_replacement(action, grant_id='GR-review', delegation_id='DG', case=case)
        self.assertEqual(outcome['disposition'], 'replacement_ready')
        full = {**action, **outcome['action']}
        replacement = deepcopy(engine.runtime['review_cycles'][cid]['replacement_actions'][rc.slot_key(full)])
        engine._prepare_review_context(full, self.root / 'delegated')
        execution = engine._register_execution(full, {'id': 'EX-delegated', 'role': 'identity_review', 'status': 'running',
            'input_manifest': {'prompt': {'sha256': 'a' * 64}}})
        self.assertIsNotNone(execution)
        return cid, replacement, execution['id'], app['id']

    def test_consumed_delegation_rejects_changed_application(self):
        cid, replacement, eid, aid = self.delegated()
        self.engine.runtime['delegation_applications'][aid]['application']['status'] = 'changed'
        result = rc.replacement_authority(self.engine.instance, self.engine.runtime,
            self.engine.runtime['review_cycles'][cid], replacement, eid, clock=self.engine.ports.clock, at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'reason': 'applied delegation receipt changed'})

    def test_consumed_delegation_rejects_changed_scope(self):
        cid, replacement, eid, _ = self.delegated()
        self.engine.instance['delegations']['DG']['included_targets'].append('K-other')
        result = rc.replacement_authority(self.engine.instance, self.engine.runtime,
            self.engine.runtime['review_cycles'][cid], replacement, eid, clock=self.engine.ports.clock, at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'reason': 'delegation authority changed after admission'})

    def test_consumed_delegation_rejects_another_application_or_delegation(self):
        cid, replacement, eid, _ = self.delegated()
        for field in ('case', 'delegation_id'):
            changed = deepcopy(replacement)
            changed[field] = {'application_id': 'other'} if field == 'case' else 'other'
            with self.subTest(field=field):
                self.assertEqual(rc.replacement_authority(self.engine.instance, self.engine.runtime,
                    self.engine.runtime['review_cycles'][cid], changed, eid, clock=self.engine.ports.clock, at=self.engine.ports.clock.now()),
                    {'allowed': False, 'reason': 'replacement names another applied delegation'})

    def test_consumed_delegation_rejects_changed_decisions_sources_and_judgments(self):
        cid, replacement, eid, aid = self.delegated()
        instance, runtime = deepcopy(self.engine.instance), deepcopy(self.engine.runtime)
        app = runtime['delegation_applications'][aid]
        cases = [('decisions', app['basis'][name]['id'], 'delegation approval changed after admission')
                 for name in ('original_decision', 'approval')]
        cases += [('governance_sources', app['basis'][name]['id'], 'delegation source changed after admission')
                  for name in ('source', 'original_source')]
        for family, identifier, reason in cases:
            changed = deepcopy(instance)
            changed[family][identifier] = {**changed[family][identifier], 'changed': True}
            with self.subTest(family=family, identifier=identifier):
                self.assertEqual(rc.replacement_authority(changed, runtime, runtime['review_cycles'][cid], replacement, eid,
                    clock=self.engine.ports.clock, at=self.engine.ports.clock.now()), {'allowed': False, 'reason': reason})
        changed = deepcopy(runtime)
        judgment = next(iter(app['judgments'].values()))['execution_id']
        changed['executions'][judgment]['context_origin'] = ['other']
        self.assertEqual(rc.replacement_authority(instance, changed, changed['review_cycles'][cid], replacement, eid,
            clock=self.engine.ports.clock, at=self.engine.ports.clock.now()),
            {'allowed': False, 'reason': 'delegation judgment execution changed after admission'})
