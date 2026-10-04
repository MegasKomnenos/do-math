"""4-C: recovery results, report receipt and local termination are independent."""
from copy import deepcopy
import re
import unittest

from do_math import activities, execution_lifecycle, repair_execution as repair

AT = '2026-09-22T00:00:00Z'
IDENTITY = {'failure_sha256': 'f' * 64, 'installation_sha256': 'a' * 64}


def recovery_execution(received):
    runtime = {'executions': {}, 'activities': {}, 'queue': []}
    activities.open_activity(runtime, activity_id='AY-recovery', activity_kind='recovery',
        owner_ref='operator', input_refs=[], opened_at=AT)
    execution = execution_lifecycle.create_execution(execution_id='EX-recovery', owner_activity_id='AY-recovery',
        actor_kind='ai', input_manifest={'repair_identity': IDENTITY},
        profile_ref={'id': 'EP-recovery', 'revision': 1, 'sha256': 'b' * 64}, created_at=AT)
    execution['role'] = 'recovery'
    activities.assign_execution(runtime, 'AY-recovery', execution)
    for state in ('starting', 'running'):
        execution_lifecycle.transition_execution(execution, state, at=AT)
    if received:
        execution['submission_receipt'] = repair.recovery_report_receipt('EX-recovery',
            evidence_ref='runtime/artifacts/BA-recovery/report.json', observed_at=AT)
    return runtime, execution


class RecoveryOutcomeContractTests(unittest.TestCase):
    def test_every_recovery_result_has_its_declared_count_and_settlement(self):
        for outcome, rule in repair.RECOVERY_OUTCOMES.items():
            for received in (False, True):
                with self.subTest(outcome=outcome, report_received=received):
                    runtime, execution = recovery_execution(received)
                    before = deepcopy(runtime)
                    arguments = {'activity_id': 'AY-recovery', 'owner': IDENTITY, 'outcome': outcome,
                        'diagnosis': None, 'execution_id': 'EX-recovery', 'at': AT}
                    if not rule['terminal']:
                        with self.assertRaisesRegex(ValueError, '^unconfirmed recovery cannot settle its execution$'):
                            repair.record_recovery_attempt(runtime, execution, **arguments)
                        self.assertEqual(runtime, before)
                        self.assertEqual(execution['status'], 'running')
                        continue
                    if rule['report'] == 'required' and not received or rule['report'] == 'absent' and received:
                        reason = ('recovery outcome requires a received repair report: ' if not received else
                                  'recovery outcome cannot carry a repair report: ') + outcome
                        with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                            repair.record_recovery_attempt(runtime, execution, **arguments)
                        self.assertEqual(runtime, before)
                        continue
                    repair.record_recovery_attempt(runtime, execution, **arguments)
                    expected = False if rule['counter'] == 'exclude' else received if rule['counter'] == 'report' else True
                    self.assertEqual(repair.recovery_attempt_counts(execution), expected)
                    self.assertEqual(repair.already_attempted(runtime, **IDENTITY), expected)
                    self.assertFalse(repair.already_attempted(runtime, 'f' * 64, 'c' * 64))
                    self.assertFalse(repair.already_attempted(runtime, 'd' * 64, 'a' * 64))
                    self.assertEqual(execution['status'], 'ended')
                    self.assertEqual(execution['result_disposition'], {'recovery': outcome})
                    self.assertEqual(execution['outcome'], 'output_accepted' if received else 'execution_incomplete')
                    activity = runtime['activities']['AY-recovery']
                    self.assertEqual(activity['status'], 'finished' if rule['finish'] else 'waiting')
                    if not rule['finish']:
                        self.assertEqual(activity['waiting'], {'kind': 'installation_repair_retry', 'reason': outcome,
                            'condition': {'kind': 'installation_repair_retry', 'failure': IDENTITY},
                            'next_owner': 'recovery', 'at': AT})

    def test_unregistered_recovery_result_cannot_change_the_execution_or_activity(self):
        for outcome in ('new-undeclared-recovery', None, [], True):
            runtime, execution = recovery_execution(False)
            before = deepcopy(runtime)
            with self.subTest(outcome=outcome), self.assertRaisesRegex(ValueError,
                    '^' + re.escape('unknown recovery outcome: ' + repr(outcome)) + '$'):
                repair.record_recovery_attempt(runtime, execution, activity_id='AY-recovery', owner=IDENTITY,
                    outcome=outcome, diagnosis=None, execution_id='EX-recovery', at=AT)
            self.assertEqual(runtime, before)


    def test_unconfirmed_recovery_cannot_settle_its_execution_or_activity(self):
        runtime, execution = recovery_execution(False)
        before = deepcopy(runtime)
        with self.assertRaisesRegex(ValueError, '^unconfirmed recovery cannot settle its execution$'):
            repair.record_recovery_attempt(runtime, execution, activity_id='AY-recovery', owner=IDENTITY,
                outcome='recovery_termination_unknown', diagnosis=None, execution_id='EX-recovery', at=AT)
        self.assertEqual(runtime, before)
        self.assertEqual(execution['status'], 'running')
