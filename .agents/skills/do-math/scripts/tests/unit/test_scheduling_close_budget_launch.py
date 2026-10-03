"""첫 full T3의 budget/launch 음성 분기: 정상 생산물의 한 필드만 변경한다."""
from copy import deepcopy
import unittest

from do_math import budget, launch
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs


def reservation():
    return budget.plan_reservations([], {'CC': {
        'kind': 'concurrency', 'accounting_unit': 'execution', 'work_slots': 1}},
        {'id': 'EP', 'revision': 1, 'sha256': 'a' * 64, 'ai': {'capacity_refs': ['CC']}},
        owner_id='EX')[0]


class ReservationRejectionTests(unittest.TestCase):
    def test_every_required_string_keeps_its_specific_rejection(self):
        for key in ('id', 'constraint_id', 'unit', 'state'):
            for value in (None, '', 0, []):
                with self.subTest(key=key, value=value):
                    row = reservation()
                    row[key] = value
                    before = deepcopy(row)
                    with self.assertRaisesRegex(budget.BudgetInputError, '^reservation lacks valid ' + key + '$'):
                        budget.validate_reservation(row)
                    self.assertEqual(row, before)

    def test_nonnegative_fields_reject_bool_negative_and_noninteger(self):
        for key in ('reserved', 'confirmed_consumed', 'returned'):
            for value in (True, False, -1, 0.5, '0', None):
                with self.subTest(key=key, value=value):
                    row = {**reservation(), key: value}
                    with self.assertRaisesRegex(budget.BudgetInputError, '^' + key + ' must be a non-negative integer$'):
                        budget.validate_reservation(row)

    def test_reservation_state_and_accounting_rejections(self):
        for changes, reason in (
            ({'state': 'unknown'}, 'reservation has an invalid state'),
            ({'confirmed_consumed': 1, 'returned': 1}, 'confirmed_consumed \\+ returned exceeds reserved'),
            ({'state': 'settled'}, 'settled reservation must account for reserved exactly'),
            ({'state': 'settled', 'returned': 1}, 'settled reservation requires evidence_refs'),
        ):
            with self.subTest(changes=changes):
                row = {**reservation(), **changes}
                with self.assertRaisesRegex(budget.BudgetInputError, '^' + reason + '$'):
                    budget.validate_reservation(row)
        row = reservation()
        del row['reobserve']
        with self.assertRaisesRegex(budget.BudgetInputError, '^held reservation requires reobserve$'):
            budget.validate_reservation(row)

    def test_settlement_requires_nonempty_evidence_sequence_without_mutating_input(self):
        row = reservation()
        before = deepcopy(row)
        for evidence in (None, [], {}, '', 'receipt', b'receipt', 1):
            with self.subTest(evidence=evidence):
                with self.assertRaisesRegex(budget.BudgetInputError, '^settlement requires actual evidence_refs$'):
                    budget.settle_reservation(row, confirmed_consumed=0, returned=1, evidence_refs=evidence)
                self.assertEqual(row, before)
        result = budget.settle_reservation(row, confirmed_consumed=0, returned=1, evidence_refs=[{'receipt': 'end'}])
        expected = {**before, 'state': 'settled', 'returned': 1, 'evidence_refs': [{'receipt': 'end'}]}
        del expected['reobserve']
        self.assertEqual(result, expected)
        self.assertIsNone(budget.validate_reservation(result))
        self.assertEqual(row, before)


class LaunchRejectionTests(unittest.TestCase):
    def setUp(self):
        self.jobs = FakeJobs()
        self.ticket = launch.ticket('EX', {'sha256': 'a' * 64, 'actor_kind': 'ai', 'role': 'research_work'},
                                    jobs=self.jobs, clock=FakeClock())

    def test_exact_outer_shape_and_binding(self):
        for value in (None, [], {}, {**self.ticket, 'extra': 1}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, '^exact launch ticket required$'):
                    launch.validate(value)
        with self.assertRaisesRegex(ValueError, '^launch ticket profile differs$'):
            launch.validate(self.ticket, profile_sha256='b' * 64)
        self.assertIs(launch.validate(self.ticket, execution_id='EX', profile_sha256='a' * 64), self.ticket)

    def test_invalid_scalar_fields_keep_valid_outer_ticket(self):
        for key, value in (('execution_id', ''), ('execution_id', 0), ('profile_sha256', 'bad'),
                           ('kind', 'other'), ('phase', 'other')):
            with self.subTest(key=key, value=value):
                with self.assertRaisesRegex(ValueError, '^invalid launch ticket$'):
                    launch.validate({**self.ticket, key: value})

    def test_owner_identity_and_native_name(self):
        for key, value in (('pid', True), ('pid', 0), ('creation_filetime', 'bad'),
                           ('creation_filetime', 123), ('host', None), ('session', True)):
            with self.subTest(key=key, value=value):
                row = deepcopy(self.ticket)
                row['owner'][key] = value
                with self.assertRaisesRegex(ValueError, '^launch owner identity invalid$'):
                    launch.validate(row)
        for value in (None, 'Local\\DoMath-bad', 'Global\\DoMath-' + 'a' * 32):
            with self.subTest(name=value):
                with self.assertRaisesRegex(ValueError, '^launch Job name invalid$'):
                    launch.validate({**self.ticket, 'job_name': value})
        with self.assertRaisesRegex(ValueError, '^thread launch cannot identify a native Job$'):
            launch.validate({**self.ticket, 'kind': 'owner_thread'})

    def test_native_start_needs_dispatched_phase_and_same_owner(self):
        with self.assertRaisesRegex(ValueError, '^formal runner needs the dispatched native launch ticket$'):
            launch.require_dispatched_native(self.ticket)
        with self.assertRaisesRegex(ValueError, '^launch ticket does not belong to this dispatched owner$'):
            launch.validate_start(self.ticket, jobs=self.jobs)
        self.assertIs(launch.mark_dispatched(self.ticket), self.ticket)
        self.assertIs(launch.require_dispatched_native(self.ticket), self.ticket)
        self.assertIs(launch.validate_start(self.ticket, jobs=self.jobs), self.ticket)
        with self.assertRaisesRegex(ValueError, '^only a reserved launch can be dispatched$'):
            launch.mark_dispatched(self.ticket)
        row = deepcopy(self.ticket)
        row['owner']['pid'] += 1
        with self.assertRaisesRegex(ValueError, '^launch ticket does not belong to this dispatched owner$'):
            launch.validate_start(row, jobs=self.jobs)

    def test_return_is_final_and_invalid_phase_is_rejected(self):
        for receipt, phase in ((None, 'finished'), ({'launch_not_created': True}, 'not_started')):
            with self.subTest(phase=phase):
                row = deepcopy(self.ticket)
                self.assertIs(launch.mark_returned(row, receipt), row)
                self.assertEqual(row, {**self.ticket, 'phase': phase})
                self.assertIs(launch.mark_returned(row, {'launch_not_created': False}), row)
                self.assertEqual(row['phase'], phase)
        with self.assertRaisesRegex(ValueError, '^invalid launch phase$'):
            launch.mark_returned({**self.ticket, 'phase': 'unknown'})
