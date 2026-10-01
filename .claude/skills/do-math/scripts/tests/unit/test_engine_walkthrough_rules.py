"""Design walkthroughs 8 to 10 (통합-설계.md 17.3) on the observation tracker and the review cycle (layer 2).

These walkthroughs replay only public domain functions: an ``ObservationTracker``
on a settable clock with the worker's checkpoint in a temporary workspace, and
the pure ``review_cycle`` state machine with declared reviewer responses. Model
and reviewer verdicts are fixtures, as in the legacy walkthroughs.
"""
from support.observation_clock import scripted_clock
from pathlib import Path
import tempfile
import unittest

from do_math import review_cycle as review
from do_math.observations import ObservationTracker
from do_math.system_clock import new_id
from support.observation_inputs import Clock, observation_rule, observe, write_checkpoint


def start_review(proposal=None, *, previous=None, rounds=2):
    policy = {'id': 'RP-fixture', 'required_perspectives': [], 'minimum_initial_slots': 2,
              'judge_slots': ['judge-0', 'judge-1', 'judge-2'], 'round_limit': rounds,
              'activity_execution_limit': 2 + rounds * 6, 'overflow_disposition': 'unresolved'}
    scope = {'assessment_id': 'SA-fixture', 'policy_id': policy['id'], 'required_perspectives': [],
             'initial_slots': [{'id': f'initial-{i}', 'perspective': str(i), 'required_source_refs': ['proposal']}
                               for i in range(2)], 'selected_profile_ref': None,
             'activity_execution_limit': policy['activity_execution_limit'], 'overflow_disposition': 'unresolved'}
    return review.start_review(proposal or {'revision': 1, 'proof': 'P'}, 2, max_rounds=rounds,
                               previous=previous, policy=policy, scope_assessment=scope)


def respond(cycle, **changes):
    action = review.next_actions(cycle)[0]
    stage = action['stage']
    output = {'proposal_digest': cycle['proposal_digest'], 'summary': 'Fixture full-source response',
              'used_sources': ['proposal:1'], 'questions': []}
    if stage == 'initial':
        output.update(decision='match', scope_complete=True, findings=[])
    elif stage == 'organize':
        output['issues'] = [{'id': f'i{index}', 'finding_refs': [f['ref']],
            'answer_role_slot_id': f['ref']['slot'] if f['ref']['stage'] in {'initial', 'answer'} else 'initial-0'}
            for index, f in enumerate(review.context_for(cycle, action)['pending_findings'], start=len(cycle['issues']))]
    elif stage == 'answer':
        output.update(answers=[{'issue_id': i, 'disposition': 'maintain', 'statement': 'Still applies',
            'evidence': ['proposal:1']} for i in review.context_for(cycle, action)['answer_requests']], new_findings=[])
    elif stage == 'judge':
        output.update(decision='mismatch', scope_complete=True, issue_verdicts=[{'issue_id': i,
            'decision': 'approved', 'reason': 'Source comparison', 'evidence': ['proposal:1']}
            for i in cycle['issues']], new_findings=[])
    output.update(changes)
    return review.accept_result(cycle, action, output, new_id('EX'))


def rule(threshold=2):
    return observation_rule(threshold=threshold, id='R-attempts', required_evidence=['EV-attempts'], repeat_interval=2)


def self_check(tracker, obligation, status='normal', **changes):
    return tracker.record_self_check_response({'execution_id': tracker.execution_id,
        'obligation_id': obligation['id'], 'rule_revision': obligation['rule_revision'],
        'progress': 'progress', 'attempts': ['Inspected bounded cases'], 'next_method': 'Check the next case', 'rule_results': [
            {'rule_id': 'R-attempts', 'status': status, 'evidence_refs': ['EV-attempts'],
             'missing_evidence_refs': [], 'reason': 'Observed the preserved event log'}], **changes},
        available_evidence_refs={'EV-attempts'})


class DesignWalkthroughs(unittest.TestCase):
    def workspace(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return Path(directory.name)

    def test_w08_self_check_defect_and_late_objection_reach_fresh_judges(self):
        from support.entry import entry
        _entry = entry()
        workspace = self.workspace()
        tracker = ObservationTracker('EX-repeat', workspace, {
            'self_check_revision': 1, 'observation_rules': [rule()], 'self_check_response_window_seconds': 5},  time_port=scripted_clock(Clock()))
        write_checkpoint(workspace, counters={'attempts': 2})
        due = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
        receipt = self_check(tracker, due, 'defect')
        self.assertEqual(receipt['followup']['kind'], 'operational_review_due')
        self.assertIn(due['id'], receipt['followup']['basis_refs'])
        cycle = respond(start_review(), decision='mismatch',
                        findings=[{'id': 'f1', 'statement': 'Original defect', 'evidence': ['proposal:1']}])
        cycle = respond(respond(cycle))  # independent peer, then organization
        cycle = respond(cycle, new_findings=[{'id': 'late', 'statement': 'Late independent defect', 'evidence': ['proposal:2']}])
        cycle = respond(respond(cycle))
        self.assertEqual((cycle['phase'], cycle['round']), ('organize', 2))
        cycle = respond(cycle)
        self.assertEqual(review.next_actions(cycle)[0]['stage'], 'answer')
        cycle = respond(cycle)
        self.assertEqual([a['slot'] for a in review.next_actions(cycle)], ['judge-0', 'judge-1', 'judge-2'])
        cycle = respond(cycle, new_findings=[{'id': 'at-cap', 'statement': 'Unanswered at cap', 'evidence': ['proposal:3']}])
        cycle = respond(respond(cycle))
        self.assertEqual(cycle['decision'], 'unresolved')
        self.assertTrue(cycle['pending_findings'])

    def test_w09_new_edition_reopens_all_slots_and_restoration_is_local(self):
        old = respond(respond(start_review()))
        self.assertEqual(old['decision'], 'match')
        fresh = start_review({'revision': 2, 'proof': 'P with local edit', 'unchanged_part': 'old defect'}, previous=old)
        self.assertEqual(len(review.next_actions(fresh)), 2)
        fresh = respond(fresh, decision='mismatch', findings=[{'id': 'old-defect',
            'statement': 'Error in unchanged part', 'evidence': ['proposal:unchanged_part']}])
        fresh = respond(respond(fresh))
        self.assertEqual(fresh['phase'], 'judge')
        action = review.next_actions(fresh)[0]
        recovered = review.record_recovery_event(fresh, action, {'reason': 'source_read_error',
            'retryable': True, 'preserved_range': {'slot': action['slot'], 'through_index': 0}})
        self.assertIn(action, review.next_actions(recovered))
        lost = review.record_recovery_event(recovered, action, {'reason': 'permanent_loss',
            'retryable': False, 'preserved_range': {'slot': action['slot'], 'through_index': 0}})
        self.assertNotIn(action, review.next_actions(lost))
        self.assertEqual(len(review.next_actions(lost)), 2)
        self.assertNotEqual(lost.get('decision'), 'match')

    def test_w10_rule_revision_preserves_old_obligation_deadline_and_rejects_replay(self):
        from support.entry import entry
        _entry = entry()
        workspace = self.workspace()
        tracker = ObservationTracker('EX-adapt', workspace, {
            'self_check_revision': 1, 'observation_rules': [rule()], 'self_check_response_window_seconds': 5},  time_port=scripted_clock(Clock()))
        write_checkpoint(workspace, counters={'attempts': 2})
        due = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
        deadline = due['deadline_offset_ms']
        # A valid response may adapt rules. A free-standing file must not
        # erase obligations. Leave the first obligation open while a second
        # real boundary supplies the response that changes the rules.
        write_checkpoint(workspace, counters={'attempts': 4})
        second = next(r for r in observe(tracker, {'type': 'tick'}) if r['kind'] == 'self_check_due')
        receipt = self_check(tracker, second, rule_proposal={'current_revision': 1,
            'reason': 'Next search stage uses a larger batch', 'rules': [rule(6)]})
        self.assertEqual(receipt['rule_update']['kind'], 'observation_rules_accepted')
        self.assertEqual(tracker.obligations[due['id']]['deadline_offset_ms'], deadline)
        bad = tracker.record_self_check_response({'obligation_id': due['id'], 'rule_revision': 2})
        self.assertEqual(bad['kind'], 'self_check_rejected')
        self.assertEqual(bad['errors'], ['execution_mismatch', 'invalid_response_schema', 'revision_mismatch'])
        self.assertEqual(tracker.obligations[due['id']]['status'], 'open')
        self.assertEqual(self_check(tracker, due)['followup']['kind'], 'continue')
        replay = self_check(tracker, due)
        self.assertEqual((replay['kind'], replay['errors']), ('self_check_rejected', ['obligation_not_open']))


if __name__ == '__main__':
    unittest.main()
