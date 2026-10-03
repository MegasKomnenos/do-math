"""실행 생성·전이·제출의 음성 분기는 대상 전체의 불변도 함께 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import execution_lifecycle as lifecycle

AT = '2090-01-01T00:00:00+00:00'


def execution(**changes):
    return lifecycle.create_execution(execution_id='EX-one', owner_activity_id='AY-one',
        actor_kind='ai', input_manifest={}, profile_ref={}, created_at=AT, **changes)


class LifecycleGapTests(unittest.TestCase):
    def test_creation_rejects_invalid_actor_missing_inputs_and_self_continuation(self):
        seed = dict(execution_id='EX-one', owner_activity_id='AY-one', actor_kind='ai',
                    input_manifest={}, profile_ref={}, created_at=AT)
        cases = [({'actor_kind': 'outside'}, 'actor_kind must be ai or machine'),
            ({'input_manifest': None}, 'input_manifest and profile_ref are required'),
            ({'profile_ref': None}, 'input_manifest and profile_ref are required'),
            ({'continuation_of': 'EX-one'}, 'an execution cannot continue itself')]
        cases += [({'context_origin': value}, 'context_origin must be a list of execution IDs')
                  for value in ('EX-parent', [None], [''])]
        for changes, reason in cases:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    lifecycle.create_execution(**{**seed, **changes})

    def test_bad_transitions_leave_the_entire_execution_unchanged(self):
        cases = [('outside', {}, 'execution status is invalid'),
            ('running', {}, 'illegal execution transition queued -> running'),
            ('starting', {'outcome': 'cancelled'}, 'outcome exists only at ended'),
            ('ended', {}, 'ended execution requires termination evidence'),
            ('ended', {'outcome': 'output_accepted'}, 'accepted output lacks submission receipt'),
            ('ended', {'outcome': 'execution_incomplete'}, 'a queued execution can end only as cancelled or start_failed')]
        for target, options, reason in cases:
            row = execution()
            before = deepcopy(row)
            with self.subTest(target=target, options=options):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    lifecycle.transition_execution(row, target, at=AT, **options)
                self.assertEqual(row, before)
        row = execution()
        self.assertIs(lifecycle.transition_execution(row, 'queued', at=AT), row)
        self.assertEqual(row, execution())

    def test_submission_rejections_preserve_execution_and_first_receipt(self):
        intent = {'candidate_id': 'CA-one', 'output_ref': 'output.json'}
        receipt = {'id': 'RQ-one', 'kind': lifecycle.NATIVE_FINAL_RECEIPT,
            'state': 'accepted', 'execution_id': 'EX-one', 'received_at': AT}
        row = execution()
        for target in ('starting', 'running'):
            lifecycle.transition_execution(row, target, at=AT)
        for bad_intent, bad_receipt, reason in (
            ({}, receipt, 'submission intent requires a centrally sealed candidate'),
            (intent, {**receipt, 'state': 'rejected'}, 'submission intent requires an accepted control receipt'),
            (intent, {**receipt, 'execution_id': 'EX-other'}, 'submission receipt belongs to another execution')):
            before = deepcopy(row)
            with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                lifecycle.record_submission_intent(row, bad_intent, bad_receipt)
            self.assertEqual(row, before)
        self.assertIs(lifecycle.record_submission_intent(row, intent, receipt), row)
        self.assertEqual(row['submission_intent'], intent)
        self.assertEqual(row['submission_receipt'], receipt)
        self.assertEqual(row['status'], 'stopping')
        before = deepcopy(row)
        self.assertEqual(lifecycle.record_submission_intent(row, intent, receipt), before)
        with self.assertRaisesRegex(ValueError, '^a different submission intent or receipt was already recorded$'):
            lifecycle.record_submission_intent(row, {**intent, 'candidate_id': 'CA-other'}, receipt)
        self.assertEqual(row, before)

    def test_preparation_rejects_nonqueued_nonboolean_and_reserved_execution(self):
        row = execution()
        lifecycle.transition_execution(row, 'starting', at=AT)
        before = deepcopy(row)
        with self.assertRaisesRegex(ValueError, '^input preparation requires a queued execution$'):
            lifecycle.begin_preparation(row, at=AT)
        self.assertEqual(row, before)
        for changes, cancelled, reason in (({}, 0, 'cancelled must be boolean'),
            ({'capacity': {'reservation': 'held'}}, False,
             'admitted preparation must reconcile reservations and process before ending')):
            row = {**execution(), **changes}
            before = deepcopy(row)
            with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                lifecycle.end_preparation(row, at=AT, stage='context', reason='시험 중단', cancelled=cancelled)
            self.assertEqual(row, before)
