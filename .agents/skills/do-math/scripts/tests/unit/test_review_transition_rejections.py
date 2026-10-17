"""정상 단계 생산물의 한 좌표를 바꾸어 거부 사유와 입력 불변성을 확인한다."""
from copy import deepcopy
import unittest

from do_math import review_cycle as rc
from support.review_inputs import scoped_start, review_stage_output, deferred_research_cycle, research_answer
from support.review_transition_inputs import cycle_at, stage_input, replace_path


class TransitionRejectionTests(unittest.TestCase):
    def test_visible_empty_organize_closes_only_its_private_view(self):
        from support.gap_inputs import ExecutedLines, observation
        cycle, initial, _ = stage_input('initial')
        context = rc.context_for(cycle, initial)
        action = {**initial, 'stage': 'organize', 'slot': 'organize'}
        output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'No mapping',
                  'used_sources': [], 'questions': [], 'issues': []}
        before = deepcopy((cycle, context, action, output))
        # A direct visible-input boundary, not a publicly scheduled organizer.
        with ExecutedLines(rc._organize) as reached:
            rc.validate_visible_output(context, action, output)
        observation('R2-visible', lines=reached.lines, crossed_884_885=reached.crossed(884, 885))
        self.assertEqual((cycle, context, action, output), before)
        view = deepcopy(cycle)
        rc._organize(view, output)
        self.assertEqual((view['status'], view['phase'], view['decision']),
                         ('unresolved', 'ended', 'unresolved'))
        self.assertEqual(view['history'][-1], {'round': cycle['round'], 'event': 'closed',
                                              'reason': 'No complete issue mapping was available'})
        self.assertEqual(view['issues'], {})
        self.assertEqual(view['pending_findings'], [])
        # A real nonempty organize input still rejects omission, then accepts its mapping.
        normal, pending, mapping = stage_input('organize')
        visible = rc.context_for(normal, pending)
        with self.assertRaisesRegex(ValueError, '^organizer omitted original findings$'):
            rc.validate_visible_output(visible, pending, {**mapping, 'issues': []})
        rc.validate_visible_output(visible, pending, mapping)
        self.assertEqual((cycle, context, action, output), before)

    def assert_result_rejected(self, stage, path, value, reason):
        cycle, action, output = stage_input(stage)
        output = replace_path(output, path, value)
        before = deepcopy((cycle, action, output))
        with self.assertRaisesRegex(ValueError, reason):
            rc.accept_result(cycle, action, output, 'fresh-review-ex')
        self.assertEqual((cycle, action, output), before)

    def test_stage_schema_rejects_unknown_stage(self):
        with self.assertRaisesRegex(ValueError, 'unknown review stage'):
            rc.stage_schema('review')

    def test_start_rejects_missing_revision(self):
        for proposal in ({}, [], {'statement': '합성'}):
            with self.subTest(proposal=proposal), self.assertRaisesRegex(ValueError, 'proposal requires an exact revision'):
                rc.start_review(proposal, 2)

    def test_allocation_rejects_nonpositive_count_and_invalid_ids(self):
        for count in (0, -1):
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, 'invalid allocation'):
                rc.start_review({'revision': 1}, count)
        for slots in (True, '', [], [''], [1]):
            with self.subTest(slots=slots), self.assertRaisesRegex(ValueError, 'positive count or list of slot IDs'):
                rc.start_review({'revision': 1}, slots)

    def test_start_rejects_invalid_judge_count_and_round_limit(self):
        for judges, rounds in ((2, 2), (4, 2), (3, True), (3, 0), (3, '2')):
            with self.subTest(judges=judges, rounds=rounds), self.assertRaisesRegex(ValueError, 'exactly three judges and a positive round limit'):
                rc.start_review({'revision': 1}, 2, judges, rounds)

    def test_revision_requires_new_revision_and_retained_slots(self):
        previous = cycle_at()
        before = deepcopy(previous)
        with self.assertRaisesRegex(ValueError, 'new review requires a new proposal revision'):
            scoped_start(previous['proposal'], 2, previous=previous, max_rounds=2)
        seed = cycle_at()
        assessment = deepcopy(seed['scope_assessment'])
        assessment['initial_slots'][1]['id'] = 'new-slot'
        with self.assertRaisesRegex(ValueError, 'existing logical slots must be retained'):
            rc.start_review({'revision': 2}, 2, max_rounds=2, previous=previous,
                            policy=previous['review_policy'], scope_assessment=assessment)
        self.assertEqual(previous, before)

    def test_revision_cannot_change_lineage_or_frozen_policy(self):
        previous = cycle_at()
        with self.assertRaisesRegex(ValueError, 'changes the inherited review lineage'):
            rc.start_review({'revision': 2, 'review_lineage_id': 'other'}, 2, previous=previous,
                            policy=previous['review_policy'])
        with self.assertRaisesRegex(ValueError, 'retain its frozen review policy'):
            rc.start_review({'revision': 2}, 2, previous=previous,
                            policy={**previous['review_policy'], 'id': 'other'})

    def test_result_requires_pending_action_and_fresh_execution(self):
        cycle, action, output = stage_input('initial')
        with self.assertRaisesRegex(ValueError, 'action is not pending'):
            rc.accept_result(cycle, {**action, 'slot': 'other'}, output, 'fresh')
        for eid in ('', None, 1):
            with self.subTest(eid=eid), self.assertRaisesRegex(ValueError, 'execution ID is required'):
                rc.accept_result(cycle, action, output, eid)
        accepted = rc.accept_result(cycle, action, output, 'used')
        with self.assertRaisesRegex(ValueError, 'execution ID already used'):
            rc.accept_result(accepted, rc.next_actions(accepted)[0], output, 'used')
        self.assertEqual(cycle['results'], {})

    def test_manifest_rejects_wrong_type_digest_and_slot(self):
        cycle, action, output = stage_input('initial')
        for manifest, reason in [([], 'input manifest must be an object'),
                ({'proposal_digest': 'other'}, 'input manifest belongs to another proposal'),
                ({'role_slot_id': 'other'}, 'input manifest has another role slot')]:
            with self.subTest(manifest=manifest), self.assertRaisesRegex(ValueError, reason):
                rc.accept_result(cycle, action, output, 'fresh', manifest)
        self.assertEqual(cycle['results'], {})

    def test_manifest_blocks_unsealed_peer_visibility(self):
        cycle, action, output = stage_input('initial')
        cycle = rc.accept_result(cycle, action, output, 'peer')
        action = rc.next_actions(cycle)[0]
        for field in ('visible_execution_ids', 'result_execution_ids'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'input contains unsealed peer results'):
                rc.accept_result(cycle, action, output, 'fresh', {field: ['peer']})
        self.assertEqual(cycle['sealed'], [])

    def test_manifest_blocks_peer_context_for_both_lineage_fields(self):
        cycle, action, output = stage_input('initial')
        cycle = rc.accept_result(cycle, action, output, 'peer')
        action = rc.next_actions(cycle)[0]
        for field in ('context_origin', 'continuation_of'):
            for value in ('peer', ['peer']):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, "a logical slot cannot inherit another slot's conversation"):
                    rc.accept_result(cycle, action, output, 'fresh', {field: value})

    def test_judge_blocks_initial_and_organizer_origins(self):
        cycle, action, output = stage_input('judge')
        for field in ('context_origin', 'continuation_of'):
            for eid in ('initial-ex-0', 'organize-ex'):
                with self.subTest(field=field, eid=eid), self.assertRaisesRegex(ValueError, 'judge cannot inherit initial-review or organizer context'):
                    rc.accept_result(cycle, action, output, 'fresh', {field: eid})

    def test_initial_rejects_wrong_proposal(self):
        self.assert_result_rejected('initial', ['proposal_digest'], 'other', 'result belongs to another proposal')

    def test_stage_schema_rejects_a_missing_required_summary(self):
        cycle, action, output = stage_input('initial')
        del output['summary']
        before = deepcopy((cycle, output))
        with self.assertRaisesRegex(ValueError, "'summary' is a required property"):
            rc.accept_result(cycle, action, output, 'fresh')
        self.assertEqual((cycle, output), before)

    def test_visible_output_validator_rejects_wrong_proposal_at_every_stage(self):
        for stage in ('initial', 'organize', 'answer', 'judge'):
            cycle, action, output = stage_input(stage)
            context = rc.context_for(cycle, action)
            output['proposal_digest'] = 'other'
            before = deepcopy(context)
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, 'result belongs to another proposal'):
                rc.validate_visible_output(context, action, output)
            self.assertEqual(context, before)

    def test_initial_match_requires_scope(self):
        self.assert_result_rejected('initial', ['scope_complete'], False, 'match requires complete scope')

    def test_initial_match_cannot_hide_questions(self):
        self.assert_result_rejected('initial', ['questions'], ['어떤 범위인가'], 'match requires no open findings or questions')

    def test_initial_mismatch_requires_finding(self):
        self.assert_result_rejected('initial', ['decision'], 'mismatch', 'mismatch requires findings')

    def test_findings_require_evidence_and_nonreserved_id(self):
        for finding in ({'id': 'f', 'statement': '반례', 'evidence': []},
                        {'id': '__question_0', 'statement': '반례', 'evidence': ['proposal']}):
            with self.subTest(finding=finding):
                self.assert_result_rejected('initial', ['findings'], [finding], 'finding requires evidence and a nonreserved ID')

    def test_organizer_rejects_empty_original_refs(self):
        self.assert_result_rejected('organize', ['issues', 0, 'finding_refs'], [], 'issue requires original finding references')

    def test_organizer_rejects_forged_reference(self):
        self.assert_result_rejected('organize', ['issues', 0, 'finding_refs', 0, 'id'], 'other', 'organizer forged or reused an original finding')

    def test_organizer_rejects_wrong_owner(self):
        self.assert_result_rejected('organize', ['issues', 0, 'answer_role_slot_id'], 'initial-1', 'answer must return to its original reviewer')

    def test_organizer_rejects_omission(self):
        self.assert_result_rejected('organize', ['issues'], [], 'organizer omitted original findings')

    def test_organizer_rejects_merging_peer_ownership(self):
        cycle, action, output = stage_input('organize')
        output['issues'][0]['finding_refs'].append(output['issues'][1]['finding_refs'][0])
        before = deepcopy(cycle)
        with self.assertRaisesRegex(ValueError, "distinct reviewers' findings must retain separate ownership"):
            rc.accept_result(cycle, action, output, 'fresh')
        self.assertEqual(cycle, before)

    def test_answer_requires_all_assigned_issues(self):
        self.assert_result_rejected('answer', ['answers'], [], 'answer must cover every assigned issue exactly once')

    def test_answer_requires_evidence(self):
        self.assert_result_rejected('answer', ['answers', 0, 'evidence'], [], 'answer disposition requires evidence')

    def test_split_requires_two_descendants(self):
        self.assert_result_rejected('answer', ['answers', 0, 'disposition'], 'split', 'split must identify at least two derived findings')

    def test_answer_findings_retain_own_lineage(self):
        finding = {'id': 'new', 'statement': '새 반례', 'evidence': ['proposal'], 'parent_issue_ids': ['i1']}
        self.assert_result_rejected('answer', ['new_findings'], [finding], "retain this answerer's original issue lineage")

    def test_judge_requires_all_current_issues(self):
        self.assert_result_rejected('judge', ['issue_verdicts'], [], 'judge must assess every current issue exactly once')

    def test_decisive_judge_requires_evidence(self):
        self.assert_result_rejected('judge', ['issue_verdicts', 0, 'evidence'], [], 'decisive issue verdict requires evidence')

    def test_judge_match_cannot_hide_approved_objection(self):
        self.assert_result_rejected('judge', ['decision'], 'match', 'match cannot conceal an open or established objection')

    def test_mismatch_needs_identified_objection(self):
        cycle, action, output = stage_input('judge')
        output['issue_verdicts'] = [{**v, 'decision': 'rejected'} for v in output['issue_verdicts']]
        before = deepcopy(cycle)
        with self.assertRaisesRegex(ValueError, 'mismatch requires an identified objection'):
            rc.accept_result(cycle, action, output, 'fresh')
        self.assertEqual(cycle, before)

    def test_provisional_requires_same_proposal_and_unresolved(self):
        cycle, action, output = stage_input('initial')
        for changed, reason in [({**output, 'proposal_digest': 'other'}, 'result belongs to another proposal'),
                                (output, 'must return unresolved provisionally')]:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                rc.validate_provisional(cycle['proposal_digest'], action, changed)

    def test_research_deferral_rejects_invalid_limit_and_source_count(self):
        cycle, action, output = stage_input('initial')
        output['decision'] = 'unresolved'
        requests = [{'id': 'r', 'question': '범위는 무엇인가', 'source_refs': ['proposal']}]
        for limit in (True, -1, '1'):
            with self.subTest(limit=limit), self.assertRaisesRegex(ValueError, 'invalid research limit'):
                rc.defer_for_research(cycle, action, output, requests, 'fresh', [[]], limit=limit)
        with self.assertRaisesRegex(ValueError, 'each research request needs its sealed source rows'):
            rc.defer_for_research(cycle, action, output, requests, 'fresh', [], limit=1)
        self.assertEqual(cycle['research'], {})

    def test_research_answer_binding_status_and_freshness(self):
        cycle, action = deferred_research_cycle()
        rid = next(iter(cycle['research']))
        answer = research_answer(cycle)
        before = deepcopy(cycle)
        for field in ('research_request_id', 'request_digest'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'different fixed question'):
                rc.accept_research_result(cycle, rid, {**answer, field: 'other'}, 'fresh')
        for status in ('unknown', 'incomplete'):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, 'incomplete investigation cannot supply an answered result'):
                rc.accept_research_result(cycle, rid, answer, 'fresh', execution_status=status)
        for eid in ('requester', '', None):
            with self.subTest(eid=eid), self.assertRaisesRegex(ValueError, 'fresh execution distinct from review slots'):
                rc.accept_research_result(cycle, rid, answer, eid)
        self.assertEqual(cycle, before)

    def test_answered_investigation_requires_evidence_scope_and_no_question(self):
        cycle, _ = deferred_research_cycle()
        rid = next(iter(cycle['research']))
        answer = research_answer(cycle)
        for field, value in [('scope_complete', False), ('evidence_refs', []), ('questions', ['남은 의문'])]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'complete scope, exact evidence and no unresolved question'):
                rc.accept_research_result(cycle, rid, {**answer, field: value}, 'fresh')
        self.assertEqual(cycle['research'][rid]['status'], 'pending')

    def test_research_result_is_consumed_once_and_returns_only_to_requester(self):
        cycle, action = deferred_research_cycle()
        rid = next(iter(cycle['research']))
        answer = research_answer(cycle)
        accepted = rc.accept_research_result(cycle, rid, answer, 'fresh')
        self.assertEqual(accepted['research'][rid]['result']['output'], answer)
        self.assertEqual(accepted['deferred_actions'], {})
        self.assertEqual(cycle['research'][rid]['result'], None)
        own = rc.context_for(accepted, action)
        peer = rc.context_for(accepted, next(a for a in rc.next_actions(accepted) if a['slot'] != action['slot']))
        self.assertEqual(own['supplemental_results'], [accepted['research'][rid]])
        self.assertEqual(peer['supplemental_results'], [])
        with self.assertRaisesRegex(ValueError, 'investigation is not pending'):
            rc.accept_research_result(accepted, rid, answer, 'second')

    def test_deferral_rejects_nonpending_action_and_reused_requester(self):
        cycle, action, output = stage_input('initial')
        output['decision'] = 'unresolved'
        requests = [{'id': 'r', 'question': '범위는 무엇인가', 'source_refs': ['proposal']}]
        rc.validate_research_requests(requests)
        with self.assertRaisesRegex(ValueError, 'duplicate research request ID'):
            rc.validate_research_requests([*requests, {**requests[0], 'question': '다른 고정 질문'}])
        sources = [[rc.inline_source_row('proposal', cycle['proposal'])]]
        deferred = rc.defer_for_research(cycle, action, output, requests, 'requester', sources, limit=3)
        with self.assertRaisesRegex(ValueError, 'review action is not pending'):
            rc.defer_for_research(deferred, action, output, requests, 'fresh', sources, limit=3)
        peer = rc.next_actions(deferred)[0]
        for eid in ('', 1, 'requester'):
            with self.subTest(eid=eid), self.assertRaisesRegex(ValueError, 'research request requires a fresh review execution'):
                rc.defer_for_research(deferred, peer, output, requests, eid, sources, limit=3)
        self.assertEqual(list(deferred['research']), ['requester:r'])

    def test_composite_request_key_collision_is_rejected_without_partial_append(self):
        cycle, action, output = stage_input('initial')
        output['decision'] = 'unresolved'
        sources = [[rc.inline_source_row('proposal', cycle['proposal'])]]
        first = rc.defer_for_research(cycle, action, output,
            [{'id': 'c', 'question': '첫 질문', 'source_refs': ['proposal']}], 'a:b', sources, limit=3)
        before = deepcopy(first)
        with self.assertRaisesRegex(ValueError, 'research request execution was already used'):
            rc.defer_for_research(first, rc.next_actions(first)[0], output,
                [{'id': 'b:c', 'question': '둘째 질문', 'source_refs': ['proposal']}], 'a', sources, limit=3)
        self.assertEqual(first, before)

    def test_existing_issue_cannot_be_replaced_by_second_round_organizer(self):
        cycle = cycle_at('judge')
        for index in range(3):
            action = rc.next_actions(cycle)[0]
            output = review_stage_output(cycle, 'judge')
            if index == 0:
                output['new_findings'] = [{'id': 'late', 'statement': '새 반례', 'evidence': ['proposal']}]
            cycle = rc.accept_result(cycle, action, output, 'first-judge-' + str(index))
        self.assertEqual((cycle['phase'], cycle['round']), ('organize', 2))
        output = review_stage_output(cycle, 'organize')
        output['issues'][0]['id'] = 'i0'
        before = deepcopy(cycle)
        with self.assertRaisesRegex(ValueError, 'organizer cannot replace an existing issue'):
            rc.accept_result(cycle, rc.next_actions(cycle)[0], output, 'next-organizer')
        self.assertEqual(cycle, before)

    def test_sealed_established_objection_cannot_be_overturned_without_new_version(self):
        cycle = cycle_at('judge')
        for index in range(3):
            action = rc.next_actions(cycle)[0]
            output = review_stage_output(cycle, 'judge')
            output['issue_verdicts'][1]['decision'] = 'unresolved'
            cycle = rc.accept_result(cycle, action, output, 'first-judge-' + str(index))
        self.assertEqual(cycle['answer_requests'], ['i1'])
        action = rc.next_actions(cycle)[0]
        cycle = rc.accept_result(cycle, action, review_stage_output(cycle, 'answer'), 'second-answer')
        for index in range(3):
            action = rc.next_actions(cycle)[0]
            output = review_stage_output(cycle, 'judge', decision='match')
            output['issue_verdicts'] = [{**v, 'decision': 'rejected'} for v in output['issue_verdicts']]
            cycle = rc.accept_result(cycle, action, output, 'second-judge-' + str(index))
        self.assertEqual((cycle['status'], cycle['decision']), ('unresolved', 'unresolved'))
        self.assertEqual((cycle['issues']['i0']['version'], cycle['issues']['i0']['status']), (1, 'approved'))
        self.assertEqual(cycle['followup'], [{'reason': 'match conflicts with an established objection', 'issue_ids': ['i0']}])
        self.assertEqual(rc.next_actions(cycle), [])
