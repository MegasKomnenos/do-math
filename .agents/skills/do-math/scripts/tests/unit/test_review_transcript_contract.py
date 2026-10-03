"""전사·원천 생산물의 정확 바이트, 복원 진단, 슬롯 복구의 값과 부작용."""
from copy import deepcopy
import hashlib
import unittest

from do_math import review_cycle as rc
from do_math.values import compact_json_bytes
from support.review_transition_inputs import cycle_at, replace_path


class TranscriptContractTests(unittest.TestCase):
    def setUp(self):
        self.cycle = cycle_at()
        self.action = rc.next_actions(self.cycle)[0]
        self.slot = self.action['slot']
        self.messages = [{'role': 'user', 'content': '원문', 'message_id': 'first'},
                         {'role': 'tool', 'content': {'result': '정확 결과'}, 'message_id': 'second'}]
        self.recorded = rc.record_turn(self.cycle, self.slot, self.messages)

    def test_recording_hashes_exact_bytes_and_is_detached_and_idempotent(self):
        expected = [{'index': index, 'sha256': hashlib.sha256(compact_json_bytes(message)).hexdigest(),
                     'bytes': len(compact_json_bytes(message)), 'proposal_digest': self.cycle['proposal_digest'],
                     'ref': f"review-transcript:{self.cycle['review_lineage_id']}:{self.slot}:{index}"}
                    for index, message in enumerate(self.messages)]
        self.assertEqual(self.recorded['transcript_manifest'][self.slot], expected)
        self.assertEqual(rc.record_turn(self.recorded, self.slot, self.messages), self.recorded)
        self.assertEqual(rc.validate_transcript(self.recorded, self.slot), (self.messages, expected))
        self.assertEqual(self.cycle['turns'], {})
        self.messages[1]['content']['result'] = '별도 사본'
        self.assertEqual(self.recorded['turns'][self.slot][1]['content'], {'result': '정확 결과'})

    def test_record_turn_rejects_unknown_slot_and_nonlist(self):
        for slot, messages, reason in [('foreign', self.messages, 'unknown logical slot'),
                                      (self.slot, {}, 'messages must be a list')]:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                rc.record_turn(self.cycle, slot, messages)
        self.assertEqual(self.cycle['turns'], {})

    def test_record_turn_rejects_invalid_message_shapes(self):
        for message in (None, {'role': 'private', 'content': '숨김'}, {'role': 'user'}):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, 'invalid public transcript message'):
                rc.record_turn(self.cycle, self.slot, [message])
        self.assertEqual(self.cycle['transcript_manifest'], {})

    def test_message_id_cannot_change_content(self):
        before = deepcopy(self.recorded)
        with self.assertRaisesRegex(ValueError, 'transcript message ID changed content'):
            rc.record_turn(self.recorded, self.slot, [{**self.messages[0], 'content': '변조'}])
        self.assertEqual(self.recorded, before)

    def test_invalid_containers_and_missing_rows_have_precise_diagnostics(self):
        for family, value, cause, coordinate in [
                ('turns', {}, 'invalid_container', {'slot': self.slot}),
                ('transcript_manifest', {}, 'invalid_container', {'slot': self.slot}),
                ('turns', self.messages[:1], 'missing_record', {'slot': self.slot, 'index': 1}),
                ('transcript_manifest', self.recorded['transcript_manifest'][self.slot][:1], 'missing_record', {'slot': self.slot, 'index': 1})]:
            changed = replace_path(self.recorded, [family, self.slot], value)
            before = deepcopy(changed)
            with self.subTest(family=family, cause=cause), self.assertRaisesRegex(rc.ReviewRestorationError, 'transcript restoration is incomplete') as caught:
                rc.validate_transcript(changed, self.slot)
            self.assertEqual(caught.exception.diagnostics['cause_kind'], cause)
            self.assertEqual(caught.exception.diagnostics['coordinate'], coordinate)
            self.assertFalse(caught.exception.diagnostics['retryable'])
            self.assertEqual(changed, before)

    def test_manifest_shape_and_index_must_match_the_message(self):
        for value in (None, {}, {**self.recorded['transcript_manifest'][self.slot][1], 'index': 9}):
            changed = replace_path(self.recorded, ['transcript_manifest', self.slot, 1], value)
            with self.subTest(value=value), self.assertRaisesRegex(rc.ReviewRestorationError, 'manifest is incomplete') as caught:
                rc.validate_transcript(changed, self.slot)
            self.assertEqual(caught.exception.diagnostics['cause_kind'], 'invalid_manifest')
            self.assertEqual(caught.exception.diagnostics['preserved_range'], {'slot': self.slot, 'verified_indices': [0]})

    def test_message_corruption_reports_expected_and_observed_hashes(self):
        changed = replace_path(self.recorded, ['turns', self.slot, 1, 'content'], '변조')
        with self.assertRaisesRegex(rc.ReviewRestorationError, 'transcript bytes changed') as caught:
            rc.validate_transcript(changed, self.slot)
        diagnostics = caught.exception.diagnostics
        self.assertEqual(diagnostics['expected_sha256'], self.recorded['transcript_manifest'][self.slot][1]['sha256'])
        self.assertEqual(diagnostics['observed_sha256'], hashlib.sha256(compact_json_bytes(changed['turns'][self.slot][1])).hexdigest())
        self.assertEqual(diagnostics['coordinate'], {'slot': self.slot, 'index': 1})
        self.assertEqual(diagnostics['preserved_range']['verified_indices'], [0])

    def test_verified_transcript_keeps_only_matching_pairs_and_all_omitted_indices(self):
        manifests = deepcopy(self.recorded['transcript_manifest'][self.slot])
        manifests[1]['bytes'] += 1
        self.assertEqual(rc._verified_transcript(self.messages, manifests), ([(self.messages[0], manifests[0])], [1]))
        self.assertEqual(rc._verified_transcript(self.messages, manifests[:1]), ([(self.messages[0], manifests[0])], [1]))
        self.assertEqual(rc._verified_transcript(self.messages[:1], manifests), ([(self.messages[0], manifests[0])], [1]))

    def test_recovery_requires_pending_action_reason_and_typed_range(self):
        event = {'reason': '정확 원문 손실', 'retryable': False, 'preserved_range': {'slot': self.slot}}
        before = deepcopy(self.cycle)
        with self.assertRaisesRegex(ValueError, 'recovery event requires a pending review action'):
            rc.record_recovery_event(self.cycle, {**self.action, 'slot': 'other'}, event)
        for field, value, reason in [('reason', '', 'requires a reason'), ('retryable', 1, 'requires retryability and preserved range'),
                                     ('preserved_range', [], 'requires retryability and preserved range')]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, reason):
                rc.record_recovery_event(self.cycle, self.action, {**event, field: value})
        self.assertEqual(self.cycle, before)

    def test_retryable_and_permanent_recovery_preserve_the_other_slot(self):
        event = {'reason': '일시 읽기 실패', 'retryable': True, 'preserved_range': {'slot': self.slot}}
        retry = rc.record_recovery_event(self.cycle, self.action, event)
        self.assertEqual(rc.next_actions(retry), rc.next_actions(self.cycle))
        self.assertEqual(retry['blocked_actions'], {})
        permanent = rc.record_recovery_event(self.cycle, self.action, {**event, 'retryable': False, 'continuity_broken': False})
        self.assertEqual(permanent['blocked_actions'], {'initial:1:initial-0': 0})
        self.assertEqual(permanent['continuity_events'], [])
        self.assertEqual(rc.next_actions(permanent), [{'stage': 'initial', 'slot': 'initial-1', 'round': 1}])
        self.assertEqual(permanent['followup'][0]['recovery_event'], 0)
        self.assertEqual(self.cycle['recovery_events'], [])

    def test_context_rejects_nonpending_action(self):
        with self.assertRaisesRegex(ValueError, 'action is not pending'):
            rc.context_for(self.recorded, {**self.action, 'round': 2})

    def test_inline_source_exact_bytes_and_rejects_each_changed_binding(self):
        source = rc.inline_source_row('proposal', {'text': '검토'})
        raw = b'{"text":"' + '검토'.encode() + b'"}'
        self.assertEqual(rc.inline_source_bytes(source), raw)
        self.assertEqual(source, {'ref': 'proposal', 'inline': {'text': '검토'}, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
        for field, value in [('inline', {'text': '변경'}), ('bytes', len(raw) + 1), ('sha256', '0' * 64)]:
            changed = {**source, field: value}
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'inline source differs from its record'):
                rc.inline_source_bytes(changed)
        self.assertEqual(source['inline'], {'text': '검토'})

    def test_source_classification_covers_each_admitted_origin(self):
        proposal = {'formal': {'axioms': ['Nat']}}
        source = {'id': 'S1', 'path': 'sources/source.txt'}
        args = dict(proposal=proposal, issues={'I1': {'id': 'I1'}}, own_source_refs=['own'], sources=[source], knowledge_ids=['K1'])
        for reference, expected in [('proposal', ('proposal', proposal)), ('proposal:formal/axioms', ('proposal', ['Nat'])),
                ('issue:I1', ('issue', {'id': 'I1'})), ('own', ('transcript', 'own')),
                ('S1', ('source', source)), ('K1', ('knowledge', 'K1'))]:
            with self.subTest(reference=reference):
                self.assertEqual(rc.classify_research_source(reference, **args), expected)
        for reference, reason in [('proposal:formal/missing', 'unknown proposal source coordinate'),
                                  ('issue:absent', 'unknown public issue source'), ('foreign', 'research source must be')]:
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, reason):
                rc.classify_research_source(reference, **args)

    def test_action_projection_preserves_only_seat_and_replacement_authority(self):
        action = {**self.action, 'role': 'identity_review', 'target': 'K1', 'id': 'AC-1'}
        self.assertEqual(rc.review_action(action), self.action)
        action.update(replacement_for=0, grant_id='G', grant_sha256='a' * 64, continuity_broken=True,
                      actor_kind='ai', purpose='record_replacement', continuity_break_cause='원문 손실')
        self.assertEqual(rc.review_action(action), {k: v for k, v in action.items() if k not in ('role', 'target')})
