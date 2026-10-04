"""Counterexamples for contract-derived observers, without starting a Sim."""
from copy import deepcopy
import unittest

from support.cross_obligations import (assert_preserved_reasons, assert_single_owners,
    assert_replacement, assert_no_resume_replay, judgment_evidence)


class CrossObligationTests(unittest.TestCase):
    def test_activation_text_and_notes_do_not_prove_the_initialization_failure_origin(self):
        from support.cross_failure_evidence import matches_recorded_failure
        error = ValueError('closed/completed instance cannot activate')
        error.add_note('state.close()\nstate.owner_pass()')
        self.assertFalse(matches_recorded_failure(error, 'closed_initialization'))

    def test_a_known_question_issue_cannot_cover_an_additional_unknown_issue(self):
        import json
        from pathlib import Path
        import tempfile
        from support.cross_failure_evidence import matches_recorded_failure
        known = {'rule_id': 'integration.candidate', 'message':
                 "runtime/operational_dispositions/OD-case/: Additional properties are not allowed ('question_id' was unexpected)"}
        with tempfile.TemporaryDirectory() as directory:
            repair = {'execution_id': 'current', 'issues': [known]}
            evidence = {'runtime': {'waiting_actions': {'wait': {'action': {'repair': repair}}},
                'executions': {'current': {'status': 'ended', 'outcome': 'execution_incomplete', 'error_kind': 'output_contract',
                    'action': {'id': 'AC-current', 'role': 'operational_review', 'target': 'failed'}},
                    'failed': {'status': 'ended'}}}, 'observed': [{
                        'action': {'id': 'AC-current'}, 'event': 'operation', 'value': 'user_decision',
                        'output': {'disposition': {'kind': 'user_decision'}}}]}
            path = Path(directory) / 'evidence.json'
            path.write_text(json.dumps(evidence), encoding='utf-8')
            error = AssertionError(('event not accepted', 'operation', 'user_decision', directory,
                                    [('current', 'execution_incomplete', 'rejected')]))
            self.assertTrue(matches_recorded_failure(error, 'operational_question'))
            repair['issues'].append({'rule_id': 'other', 'message': 'another failure'})
            path.write_text(json.dumps(evidence), encoding='utf-8')
            self.assertFalse(matches_recorded_failure(error, 'operational_question'))


    def test_a_close_note_cannot_classify_reason_loss_without_its_producer_evidence(self):
        from support.cross_failure_evidence import matches_recorded_failure
        error = AssertionError(('lost request reasons', {'an unrelated request'}))
        error.add_note('state.close()\nstate.assert_contracts_after_every_event()')
        self.assertFalse(matches_recorded_failure(error, 'closed_reasons'))

    def test_known_closure_requires_matching_identity_loss_and_completed_other_checks(self):
        from support.cross_failure_evidence import matches_recorded_failure
        from support.cross_obligations import RequestReasonLoss
        requests = [{'id': 'AC-request', 'reasons': ['first origin', 'second origin']}]
        witness = {'last_event': ('close', {}),
                   'control': {'action': 'close', 'request_id': 'UC-close',
                               'result': {'effect': 'applied', 'status': 'closed', 'snapshot': 'published'}},
                   'lifecycle': {'permanently_closed': True,
                                 'history': [{'kind': 'closed', 'source_ref': 'UC-close'}]}}
        def failure():
            error = RequestReasonLoss(requests, [], {'status': 'closed'})
            error.other_invariants_checked = True
            error.previous_status = 'active'
            error.closure_witness = deepcopy(witness)
            return error
        self.assertTrue(matches_recorded_failure(failure(), 'closed_reasons'))
        variants = []
        error = failure(); error.other_invariants_checked = False; variants.append(error)
        error = failure(); error.previous_status = 'closed'; variants.append(error)
        error = failure(); error.runtime_status = 'active'; variants.append(error)
        error = failure(); error.closure_witness['last_event'] = ('step',); variants.append(error)
        error = failure(); error.closure_witness['control']['request_id'] = 'another'; variants.append(error)
        error = failure(); error.closure_witness['control']['result']['effect'] = 'rejected'; variants.append(error)
        error = failure(); error.closure_witness['control']['result']['snapshot'] = None; variants.append(error)
        error = failure(); error.closure_witness['lifecycle']['history'] = []; variants.append(error)
        error = failure(); error.requests = [{'id': 'different', 'reason': 'unrelated'}]; variants.append(error)
        error = failure(); error.args = (('another failure', error.lost),); variants.append(error)
        error = failure(); error.preserved = deepcopy(requests); variants.append(error)
        for index, error in enumerate(variants):
            with self.subTest(variant=index):
                self.assertFalse(matches_recorded_failure(error, 'closed_reasons'))

    def test_generated_known_fault_matching_does_not_cover_unrelated_failures(self):
        from support.cross_failure_evidence import matches_recorded_failure
        lost = AssertionError(('lost request reasons', {'preserve this source'}))
        self.assertFalse(matches_recorded_failure(lost, 'closed_reasons'))
        lost.add_note('state.close()\nstate.assert_contracts_after_every_event()')
        self.assertFalse(matches_recorded_failure(lost, 'closed_reasons'))
        other = AssertionError(('cross producer bound', 12))
        other.add_note('state.close()')
        self.assertFalse(matches_recorded_failure(other, 'closed_reasons'))
        self.assertFalse(matches_recorded_failure(other, 'operational_question'))
        activation = ValueError('closed/completed instance cannot activate')
        self.assertFalse(matches_recorded_failure(activation, 'closed_initialization'))
        activation.add_note('state.close()\nstate.owner_pass()')
        self.assertFalse(matches_recorded_failure(activation, 'closed_initialization'))
        self.assertFalse(matches_recorded_failure(ValueError('another failure'), 'closed_initialization'))
        import json
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory(prefix='cross-fault-binding-') as directory:
            issue = {'rule_id': 'integration.candidate', 'message':
                "runtime/operational_dispositions/OD-case/: Additional properties are not allowed ('question_id' was unexpected)"}
            evidence = {'runtime': {'waiting_actions': {'wait': {'action': {'repair': {
                'execution_id': 'older', 'issues': [issue]}}}}, 'executions': {
                    'current': {'status': 'ended', 'outcome': 'execution_incomplete', 'error_kind': 'output_contract',
                                'action': {'id': 'AC-current', 'role': 'operational_review', 'target': 'failed'}},
                    'failed': {'status': 'ended'}}}, 'observed': [{
                        'action': {'id': 'AC-current'}, 'event': 'operation', 'value': 'user_decision',
                        'output': {'disposition': {'kind': 'user_decision'}}}]}
            path = Path(directory) / 'evidence.json'
            path.write_text(json.dumps(evidence), encoding='utf-8')
            error = AssertionError(('event not accepted', 'operation', 'user_decision', directory,
                                    [('current', 'execution_incomplete', 'rejected')]))
            self.assertFalse(matches_recorded_failure(error, 'operational_question'),
                             'an older known receipt must not hide a new failure')
            evidence['runtime']['waiting_actions']['wait']['action']['repair']['execution_id'] = 'current'
            path.write_text(json.dumps(evidence), encoding='utf-8')
            self.assertTrue(matches_recorded_failure(error, 'operational_question'))
            for label, change in (
                    ('wrong sender', lambda value: value['runtime']['executions']['current']['action'].update(role='research_work')),
                    ('live target', lambda value: value['runtime']['executions']['failed'].update(status='running')),
                    ('worker failure', lambda value: value['runtime']['executions']['current'].update(error_kind='worker_error')),
                    ('different event', lambda value: value['observed'][0].update(value='continue')),
                    ('duplicate producer', lambda value: value['observed'].append(deepcopy(value['observed'][0])))):
                variant = deepcopy(evidence)
                change(variant)
                path.write_text(json.dumps(variant), encoding='utf-8')
                with self.subTest(cause=label):
                    self.assertFalse(matches_recorded_failure(error, 'operational_question'))
            path.write_text(json.dumps(evidence), encoding='utf-8')
            self.assertFalse(matches_recorded_failure(AssertionError((
                'event not accepted', 'operation', 'user_decision', directory, [])), 'operational_question'))

    def test_late_integration_needs_its_receipt_and_preserves_physical_termination(self):
        from support.cross_obligations import assert_ended_evidence
        before = {'id': 'producer', 'status': 'ended', 'ended_at': 'fixed',
                  'outcome': 'execution_incomplete', 'submission_receipt': {'id': 'sealed'}}
        current = {**before, 'outcome': 'output_accepted', 'result_disposition': {
            'kind': 'submission_integrated', 'integration_ids': ['bundle']}}
        runtime = {'integrations': {'bundle': {'execution_id': 'producer'}}}
        assert_ended_evidence(before, current, runtime)
        with self.assertRaisesRegex(AssertionError, 'another producer'):
            assert_ended_evidence(before, current, {'integrations': {}})
        with self.assertRaisesRegex(AssertionError, 'evidence changed'):
            assert_ended_evidence(before, {**current, 'ended_at': 'new'}, runtime)
        with self.assertRaisesRegex(AssertionError, 'lost sealed receipt'):
            assert_ended_evidence(before, {**current, 'submission_receipt': {'id': 'new'}}, runtime)

    def test_merged_request_requires_both_reasons_after_retirement(self):
        before = [{'id': 'a', 'reason': 'revise the target'}, {'id': 'b', 'reason': 'independent research'}]
        runtime = {'queue': [{'id': 'a', 'role': 'research_preparation', 'reason': 'independent research'}],
                   'executions': {}, 'history': [{'action': before[0]}]}
        assert_preserved_reasons(before, runtime)
        runtime['history'] = []
        with self.assertRaisesRegex(AssertionError, 'lost request reasons'):
            assert_preserved_reasons(before, runtime)

    def test_waiting_owner_counts_against_the_same_lineage_slot_contract(self):
        action = {'id': 'a', 'lineage_id': 'origin', 'role': 'research_work',
                  'target': 'task', 'selected_contract_sha256': 'contract'}
        runtime = {'queue': [action], 'executions': {}, 'waiting_actions': {
            'b': {'action': {**action, 'id': 'b'}}}}
        with self.assertRaisesRegex(AssertionError, 'duplicate lineage owner'):
            assert_single_owners(runtime)

    def test_replacement_rejects_union_even_when_old_contract_is_preserved(self):
        old = {'revision': 1, 'scope': {'included': ['A', 'B']}, 'completion_obligations': ['A', 'B'],
               'expected': ['A', 'B'], 'progress_criteria': ['A', 'B']}
        submitted = {k: deepcopy(v) for k, v in old.items() if k != 'revision'}
        submitted['completion_obligations'] = ['A']
        current = {**deepcopy(submitted), 'revision': 2, 'revision_history': [deepcopy(old)]}
        assert_replacement(old, submitted, current)
        current['completion_obligations'].append('B')
        with self.assertRaisesRegex(AssertionError, 'revision must replace'):
            assert_replacement(old, submitted, current)

    def test_resume_cannot_requeue_an_unchanged_failed_request(self):
        waits = {'a': {'kind': 'output_validation', 'execution_id': 'e'}}
        runtime = {'queue': [], 'executions': {'e': {'status': 'ended'}}}
        assert_no_resume_replay(waits, runtime)
        runtime['queue'].append({'id': 'a'})
        with self.assertRaisesRegex(AssertionError, 'resurrected'):
            assert_no_resume_replay(waits, runtime)

    def test_currentness_annotation_can_change_without_erasing_judgment(self):
        original = [{'id': 'j', 'decision': 'satisfied', 'basis': 'original', 'current': True}]
        invalidated = [{**original[0], 'current': False, 'invalidated_reason': 'new source'}]
        self.assertEqual(judgment_evidence(original), judgment_evidence(invalidated))
        invalidated[0]['basis'] = 'replacement'
        self.assertNotEqual(judgment_evidence(original), judgment_evidence(invalidated))
