"""실제 엔진의 입장·입력·복원 거부는 부분 적용과 게시를 남기지 않는다."""
from copy import deepcopy
import hashlib
import json

from do_math import review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm
from support.review_transition_inputs import replace_path


def setUpModule():
    warm()


class OwnerGuardTests(ReviewOwnerCase):
    def test_admission_ignores_unowned_or_non_ai_attempt(self):
        before = deepcopy(self.engine.runtime)
        self.assertEqual(self.engine._admit_review_execution({'role': 'maintenance'}, {'actor_kind': 'ai'}), {'disposition': 'not_applicable'})
        self.assertEqual(self.engine._admit_review_execution({'review_cycle_id': 'absent'}, {'actor_kind': 'machine'}), {'disposition': 'not_applicable'})
        self.assertEqual(self.engine.runtime, before)

    def test_repeated_admission_rejects_changed_owner(self):
        _, action, execution = self.registered()
        changed = {**execution, 'owner_activity_id': 'other'}
        self.assert_engine_rejected('review execution admission identity changed', lambda: self.engine._admit_review_execution(action, changed))

    def test_admission_requires_actual_owner(self):
        _, action = self.opened()
        self.assert_engine_rejected('review admission requires its actual owner activity',
            lambda: self.engine._admit_review_execution(action, {'id': 'ownerless', 'actor_kind': 'ai', 'status': 'queued'}))

    def test_review_cycle_rejects_wrong_role_missing_cycle_and_target(self):
        cid, action = self.opened()
        for field, value, reason in [('role', 'maintenance', 'action is not an identity review'),
                ('review_cycle_id', 'absent', '^review action refers to another or missing proposal$'),
                ('target', 'other', '^review action refers to another or missing proposal$')]:
            with self.subTest(field=field):
                self.assert_engine_rejected(reason, lambda field=field, value=value: self.engine._review_cycle({**action, field: value}))
        cycle = self.engine._review_cycle(action)
        self.assertEqual(cycle['knowledge_id'], action['target'])
        self.assertEqual(cycle, self.engine.runtime['review_cycles'][cid])

    def test_review_cycle_rejects_superseded_pointer(self):
        _, action = self.opened()
        self.engine.instance['knowledge']['K1']['review_cycle_id'] = 'other'
        self.assert_engine_rejected('review action belongs to a superseded proposal revision', lambda: self.engine._review_cycle(action))

    def test_review_schema_rejects_nonpending_slot(self):
        _, action = self.opened()
        self.assert_engine_rejected('review action is not pending', lambda: self.engine._review_schema({**action, 'slot': 'other'}))

    def test_prepared_context_is_required_before_recording(self):
        _, action = self.opened()
        self.assert_engine_rejected('the review execution has no matching prepared input', lambda: self.engine._record_review_input(action, 'absent'))

    def test_delivered_input_is_idempotent_but_changed_binding_is_rejected(self):
        cid, action, execution = self.registered()
        first = self.engine._record_review_input(action, execution['id'])
        before = deepcopy(self.engine.runtime)
        second = self.engine._record_review_input(action, execution['id'])
        self.assertEqual(first, second)
        self.assertEqual(self.engine.runtime, before)
        self.engine.runtime['review_cycles'][cid]['input_bindings'][execution['id']]['input_sha256'] = 'b' * 64
        self.assert_engine_rejected('delivered review input binding changed', lambda: self.engine._record_review_input(action, execution['id']))

    def test_preparation_rejects_changed_owner(self):
        _, action, _ = self.registered()
        self.assert_engine_rejected('review action changed its owner activity',
            lambda: self.engine._prepare_review_context({**action, 'owner_activity_id': 'other'}, self.root / 'other'))

    def test_result_requires_actual_execution(self):
        _, action = self.opened()
        self.assert_engine_rejected('identity review requires its actual execution record',
            lambda: self.engine._apply_identity_review(action, {}, 'absent'))

    def test_result_rejects_execution_with_an_unassigned_replacement_binding(self):
        _, action, execution = self.registered()
        execution['action']['replacement_for'] = 0
        self.assert_engine_rejected('execution replacement binding differs from its authorized action',
            lambda: self.engine._apply_identity_review(action, {}, execution['id']))

    def test_opening_rejects_missing_or_unfinished_previous_cycle(self):
        cid, _ = self.opened()
        self.assert_engine_rejected('previous review cycle does not exist', lambda: self.engine._start_identity_review('K1', 'absent'))
        self.assert_engine_rejected('finish or explicitly close the prior review before revising', lambda: self.engine._start_identity_review('K1', cid))

    def test_reopening_cannot_accept_a_changed_sealed_proposal(self):
        cid, _ = self.opened()
        self.engine.runtime['review_cycles'][cid]['proposal']['statement'] = '변조된 문장'
        self.assert_engine_rejected('sealed review proposal changed; submit an explicit new revision', lambda: self.engine._start_identity_review('K1'))

    def test_revision_must_name_the_previous_knowledge_item(self):
        cid, _ = self.opened()
        self.scene.execute()
        self.scene.execute()
        kid = self.scene.revise()
        self.engine.instance['knowledge'][kid]['supersedes'] = 'other'
        self.assert_engine_rejected('revision must name the previous knowledge item', lambda: self.engine._start_identity_review(kid, cid))

    def test_selected_scope_profile_must_match_the_actual_execution(self):
        from do_math.execution_profiles import profile_ref
        profile = self.engine._execution_profile({'role': 'identity_review', 'target': 'K1'})
        scope = {**self.scene.scope, 'selected_profile_ref': profile_ref(profile)}
        self.scene.start('K1', scope=scope)
        action = deepcopy(self.scene.pending())
        execution = self.engine._register_execution(action, {'id': 'EX-selected-profile', 'role': 'identity_review', 'status': 'running'})
        self.assertIsNotNone(execution)
        profile = next(p for p in self.engine.instance['execution_profiles'].values() if p['role'] == 'maintenance')
        execution['execution_profile_ref'] = profile_ref(profile)
        self.assert_engine_rejected('identity review execution did not use the scope assessment profile',
            lambda: self.engine._apply_identity_review(action, {}, execution['id']))

    def test_publication_rechecks_sealed_premises_before_writing_assessment(self):
        cid, action = self.opened()
        self.scene.execute()
        _, _, eid = self.scene.execute()
        cycle = deepcopy(self.engine.runtime['review_cycles'][cid])
        cycle['publication_premises']['review_policy']['id'] = 'other'
        self.assert_engine_rejected('review publication premises changed before publication',
            lambda: self.engine._publish_identity_review_result(action, cycle, eid))

    def test_recovery_retry_keeps_failed_slot_blocked_after_second_io_failure(self):
        cid, action = self.opened()
        self.engine._record_review_recovery(action, ValueError('원문 손실'), retryable=False)
        occupied = self.root / 'retry-file'
        occupied.write_bytes(b'not a directory')
        result = self.engine._retry_review_restoration(action, occupied)
        self.assertEqual(result['disposition'], 'recovery_recorded')
        cycle = self.engine.runtime['review_cycles'][cid]
        self.assertEqual(cycle['blocked_actions'], {rc.slot_key(action): 1})
        self.assertEqual(len(cycle['recovery_events']), 2)
        self.assertEqual(occupied.read_bytes(), b'not a directory')

    def test_retry_without_prior_block_preserves_precondition_error(self):
        cid, action = self.opened()
        self.engine.runtime['review_cycles'][cid]['activity_execution_limit'] += 1
        self.assert_engine_rejected('review policy, scope, profile, or activity input changed',
            lambda: self.engine._retry_review_restoration(action, self.root / 'retry'))

    def test_release_wait_preserves_other_slot_and_unmatched_activity_wait(self):
        from do_math.activities import wait_for
        from do_math.execution_lifecycle import transition_execution
        cid, action, execution = self.registered()
        transition_execution(execution, 'stopping', at=self.engine.ports.clock.now())
        transition_execution(execution, 'ended', at=self.engine.ports.clock.now(), outcome='cancelled')
        peer = {**action, 'slot': 'initial-1'}
        self.engine.runtime['waiting_actions'] = {
            'own': {'kind': 'review_input_restoration', 'action': action},
            'peer': {'kind': 'review_input_restoration', 'action': peer},
            'other-kind': {'kind': 'provider_wait', 'action': action}}
        wait_for(self.engine.runtime, execution['owner_activity_id'], kind='review_input_restoration', reason='review_input_restoration',
            condition={'recovery': {'review_cycle_id': cid, 'action': rc.review_action(peer)}},
            next_owner='review_recovery', at=self.engine.ports.clock.now())
        activity = deepcopy(self.engine.runtime['activities'][execution['owner_activity_id']])
        expected = {key: deepcopy(self.engine.runtime['waiting_actions'][key]) for key in ('peer', 'other-kind')}
        self.assertEqual(self.engine._release_review_wait(action), ['own'])
        self.assertEqual(self.engine.runtime['waiting_actions'], expected)
        self.assertEqual(self.engine.runtime['activities'][execution['owner_activity_id']], activity)
        self.assertEqual(self.engine.runtime['history'][-1]['waiting_action_ids'], ['own'])

    def test_changed_review_basis_rejects_acceptance_before_mutation(self):
        cid, action, execution = self.registered()
        self.engine.runtime['review_cycles'][cid]['activity_execution_limit'] += 1
        self.assert_engine_rejected('review inputs changed before acceptance', lambda: self.engine._checked_review_result(action, execution['id']))

    def test_obsolete_reason_distinguishes_missing_cycle_and_spent_slot(self):
        _, action = self.opened()
        before = deepcopy(self.engine.runtime)
        self.assertIsNone(self.engine._obsolete_review_reason({'role': 'maintenance'}))
        self.assertEqual(self.engine._obsolete_review_reason({**action, 'review_cycle_id': 'absent'}),
                         'The assigned review ended or its proposal revision was superseded')
        self.assertEqual(self.engine._obsolete_review_reason({**action, 'slot': 'other'}), 'The assigned review slot is no longer pending')
        self.assertEqual(self.engine.runtime, before)

    def test_prompt_requires_exact_text_and_artifact_reference(self):
        _, _, execution = self.registered()
        for prompt, ref in [(None, 'prompt.txt'), ('원문', ''), ('원문', None)]:
            with self.subTest(prompt=prompt, ref=ref):
                self.assert_engine_rejected('delivered review prompt requires exact text and artifact reference',
                    lambda: self.engine._record_review_prompt(execution['id'], prompt, artifact_ref=ref))

    def test_nonreview_prompt_and_observation_do_not_add_transcript(self):
        _, _, execution = self.registered()
        execution['action']['role'] = 'maintenance'
        before = deepcopy(self.engine.runtime)
        self.assertFalse(self.engine._record_review_prompt(execution['id'], '원문', artifact_ref='prompt.txt'))
        self.assertFalse(self.engine._record_review_observation(execution['id'], {}, artifact_ref='events.jsonl', event_index=0))
        self.assertEqual(self.engine.runtime, before)

    def test_observation_requires_ordered_coordinate_and_normalized_message(self):
        _, _, execution = self.registered()
        eid = execution['id']
        event = {'type': 'public_message', 'message': {'role': 'assistant', 'content': '공개 원문'}}
        for index, ref in [(True, 'events'), (-1, 'events'), (0, ''), ('0', 'events')]:
            with self.subTest(index=index, ref=ref):
                self.assert_engine_rejected('public review event requires an ordered artifact coordinate',
                    lambda: self.engine._record_review_observation(eid, event, artifact_ref=ref, event_index=index))
        event['message']['role'] = 'private'
        self.assert_engine_rejected('invalid normalized public message',
            lambda: self.engine._record_review_observation(eid, event, artifact_ref='events', event_index=0))

    def test_provider_blocks_preserve_public_tools_but_ignore_unknown_blocks(self):
        cid, action, execution = self.registered()
        blocks = ['ignored', {'type': 'thinking', 'thinking': 'PRIVATE'},
                  {'type': 'tool_use', 'id': 't', 'name': 'read', 'input': {}},
                  {'type': 'tool_result', 'tool_use_id': 't', 'content': '정확 결과'}]
        self.assertTrue(self.engine._record_review_observation(execution['id'],
            {'type': 'assistant', 'message': {'content': blocks}}, artifact_ref='events', event_index=0))
        turns = self.engine.runtime['review_cycles'][cid]['turns'][action['slot']]
        self.assertEqual([(r['role'], r['content']) for r in turns], [('assistant', blocks[2]), ('tool', blocks[3])])
        self.assertEqual([r['message_id'] for r in turns], [execution['id'] + ':public:0:0', execution['id'] + ':public:0:1'])

    def test_source_materialization_is_exact_and_repeated_read_is_identical(self):
        source = rc.inline_source_row('proposal', {'text': '원천'})
        workspace = self.root / 'materialized'
        before = deepcopy(self.engine.runtime)
        rows = self.engine._materialize_research_sources([source], workspace, slot='initial-0')
        self.assertEqual(rows, [{k: v for k, v in source.items() if k != 'inline'} |
                               {'local_path': 'input/review-research/0000-' + source['sha256'] + '.json'}])
        raw = (workspace / rows[0]['local_path']).read_bytes()
        self.assertEqual(raw, rc.inline_source_bytes(source))
        self.assertEqual(self.engine._materialize_research_sources([source], workspace), rows)
        self.assertEqual(self.engine.runtime, before)

    def test_inline_mismatch_reports_exact_source_coordinate(self):
        source = rc.inline_source_row('proposal', {'text': '원천'})
        source['inline']['text'] = '변조'
        with self.assertRaisesRegex(rc.ReviewRestorationError, 'fixed research source bytes changed') as caught:
            self.engine._materialize_research_sources([source], self.root / 'bad', slot='initial-0')
        self.assertEqual(caught.exception.diagnostics['cause_kind'], 'fixed_source_content_mismatch')
        self.assertEqual(caught.exception.diagnostics['coordinate'], {'slot': 'initial-0', 'source_index': 0,
            'source_ref': 'proposal', 'artifact_ref': None, 'snapshot': self.engine.head})
        self.assertEqual(list((self.root / 'bad' / 'input' / 'review-research').iterdir()), [])

    def test_materialized_source_collision_does_not_overwrite_existing_file(self):
        source = rc.inline_source_row('proposal', {'text': '원천'})
        workspace = self.root / 'collision'
        rows = self.engine._materialize_research_sources([source], workspace)
        path = workspace / rows[0]['local_path']
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(rc.ReviewRestorationError, 'research source file has different bytes') as caught:
            self.engine._materialize_research_sources([source], workspace)
        self.assertEqual(caught.exception.diagnostics['cause_kind'], 'materialized_content_mismatch')
        self.assertEqual(caught.exception.diagnostics['observed_sha256'], hashlib.sha256(b'changed').hexdigest())
        self.assertEqual(path.read_bytes(), b'changed')

    def test_actual_filesystem_error_becomes_nonretryable_recovery(self):
        cid, action = self.opened()
        occupied = self.root / 'occupied'
        occupied.write_text('파일이며 디렉터리가 아니다', encoding='utf-8')
        outcome = self.engine._prepare_review_context(action, occupied)
        self.assertEqual(outcome['disposition'], 'recovery_recorded')
        recovery = outcome['recovery']
        self.assertEqual(recovery['disposition'], 'replacement_authorization_required')
        self.assertEqual(recovery['recovery_event']['cause_kind'], 'io_failure')
        self.assertFalse(recovery['recovery_event']['retryable'])
        self.assertFalse(recovery['recovery_event']['continuity_broken'])
        self.assertEqual(self.engine.runtime['review_cycles'][cid]['decision'], None)
        self.assertEqual(occupied.read_text(encoding='utf-8'), '파일이며 디렉터리가 아니다')

    def test_recovery_retry_restores_block_on_precondition_failure(self):
        cid, action = self.opened()
        self.engine._record_review_recovery(action, ValueError('원문 손실'), retryable=False)
        cycle = self.engine.runtime['review_cycles'][cid]
        cycle['activity_execution_limit'] += 1
        before = deepcopy(cycle['blocked_actions'])
        with self.assertRaisesRegex(ValueError, 'review policy, scope, profile, or activity input changed'):
            self.engine._retry_review_restoration(action, self.root / 'retry')
        self.assertEqual(cycle['blocked_actions'], before)

    def test_research_nonapplicable_paths_leave_runtime_unchanged(self):
        _, _, execution = self.registered()
        before = deepcopy(self.engine.runtime)
        self.assertFalse(self.engine._defer_review_for_research({'role': 'maintenance'}, {}, execution['id']))
        self.assertFalse(self.engine._defer_review_for_research(execution['action'], {}, execution['id']))
        self.assertFalse(self.engine._abandon_review_research({'role': 'maintenance'}, execution['id'], '중단'))
        self.assertFalse(self.engine._finish_failed_investigation({'role': 'maintenance'}, execution['id'], '중단'))
        self.assertEqual(self.engine.runtime, before)

    def test_pending_research_rejects_nonresearch_or_absent_request(self):
        _, action = self.opened()
        self.assert_engine_rejected('action is not a review investigation', lambda: self.engine._pending_review_research(action))
        action.update(role='supplemental_research', research_request_id='absent', requesting_slot=action['slot'])
        self.assert_engine_rejected('review investigation is not pending', lambda: self.engine._pending_review_research(action))

    def test_reassessment_control_absence_and_wrong_role(self):
        before = deepcopy(self.engine.runtime)
        self.assertIsNone(self.engine._assessment_reassessment_control({'action': 'request'}))
        self.assertEqual(self.engine.runtime, before)
        self.assert_engine_rejected('assessment reassessment requires an identity_review request',
            lambda: self.engine._assessment_reassessment_control({'action': 'request', 'config': {'role': 'maintenance', 'assessment_reassessment': {}}}))

    def test_unknown_assessment_cannot_start_reassessment(self):
        self.assert_engine_rejected('reassessment requires the exact original assessment',
            lambda: self.engine._start_assessment_reassessment('absent', 'a' * 64, {}))

    def test_staged_candidate_rejects_closed_transition_and_absent_target(self):
        tid = self.staged()
        transition = self.engine.runtime['trust_transitions'][tid]
        self.assert_engine_rejected('staged review target is not in the transition',
            lambda: rc.staged_review_candidate(self.engine.instance, self.engine.runtime, tid, 'absent'))
        transition['status'] = 'active'
        self.assert_engine_rejected('staged transition is no longer reviewable',
            lambda: rc.staged_review_candidate(self.engine.instance, self.engine.runtime, tid, 'K1'))

    def test_staged_candidate_rejects_changed_basis_and_ineligible_environment(self):
        tid = self.staged()
        transition = self.engine.runtime['trust_transitions'][tid]
        target = next(t for t in transition['targets'] if t['id'] == 'K1')
        original = target['exposition_basis']
        target['exposition_basis'] = '0' * 64
        self.assert_engine_rejected('staged source basis changed', lambda: rc.staged_review_candidate(self.engine.instance, self.engine.runtime, tid, 'K1'))
        target['exposition_basis'] = original
        self.engine.instance['trust_environments']['TE-review-next']['status'] = 'invalid'
        self.assert_engine_rejected('staged verification or target environment is not eligible for review',
            lambda: rc.staged_review_candidate(self.engine.instance, self.engine.runtime, tid, 'K1'))

    def test_staged_reuse_preserves_queue_and_rejects_changed_candidate(self):
        tid = self.staged()
        cid = self.engine._start_staged_identity_review(tid, 'K1')
        before = deepcopy(self.engine.runtime['queue'])
        self.assertEqual(self.engine._start_staged_identity_review(tid, 'K1'), cid)
        self.assertEqual(self.engine.runtime['queue'], before)
        self.engine.runtime['trust_transitions'][tid]['results']['K1']['declaration_evidence']['sample']['value'] = '다른 증명항'
        self.assert_engine_rejected('staged review candidate changed; do not reuse its old review',
            lambda: self.engine._start_staged_identity_review(tid, 'K1'))

    def test_staged_receipt_rejects_another_transition_and_unfinished_cycle(self):
        tid = self.staged()
        cid = self.engine._start_staged_identity_review(tid, 'K1')
        self.assert_engine_rejected('staged review belongs to another transition target',
            lambda: self.engine._completed_staged_identity_review('other', 'K1', cid))
        self.assert_engine_rejected('staged identity review has no completed match',
            lambda: self.engine._completed_staged_identity_review(tid, 'K1', cid))

    def test_staged_review_rejects_changed_publication_premises(self):
        tid = self.staged()
        cid = self.engine._start_staged_identity_review(tid, 'K1')
        action = deepcopy(self.scene.pending())
        self.engine.runtime['review_cycles'][cid]['publication_premises']['review_policy']['id'] = 'other'
        self.assert_engine_rejected('staged review publication premises changed', lambda: self.engine._review_cycle(action))
