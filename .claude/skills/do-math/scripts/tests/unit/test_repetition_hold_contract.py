"""4-B/4-C: each configured lineage holds at its limit and has a public exit."""
from copy import deepcopy
import re
import unittest

from do_math import governance, revisions, task_contracts
from do_math.canonical import exact_content_hash
from do_math.configuration import DEFAULT_CONFIG
from support.fakes.clock import FakeClock
from support.state_builders import governance_start


class RepetitionHoldContractTests(unittest.TestCase):
    def test_every_lineage_keeps_its_hold_until_the_exact_user_continuation(self):
        for lineage in task_contracts.REPEAT_LINEAGES:
            with self.subTest(lineage=lineage):
                clock = FakeClock()
                instance = governance_start({'id': 'RI-hold', 'knowledge': {}, 'relations': [],
                    'goal_status': 'unresolved', 'config': {'goal_auditors': 2,
                        'max_artifact_bytes': DEFAULT_CONFIG['max_artifact_bytes'], lineage + '_limit': 2}})
                runtime = {'history': [], 'queue': [], 'tasks': {}, 'activities': {}, 'executions': {},
                    'questions': [], 'question_links': [], 'inputs': [], 'interpretations': {}, 'status': 'ready'}
                instance['governance_sources'] = {'UI-hold': governance.preserve_source(
                    'UI-hold', 'Continue only the current recorded repetition hold.', origin='user')}
                basis = exact_content_hash({'lineage': lineage, 'instance': instance['id']})
                role = 'intent_interpretation' if lineage == 'import_rework' else 'research_preparation' \
                    if lineage == 'exhaustion_empty' else 'research_plan'
                action = {'id': 'AC-held', 'role': role, 'repetition_bases': {lineage: basis}}
                if lineage == 'import_rework':
                    action['intent_repair'] = True
                runtime['queue'].append(action)
                versioned = lineage in {'contract_revision', 'proposal_version'}
                outcome = 'revised' if versioned else 'empty' if lineage == 'exhaustion_empty' \
                    else 'reauthored' if lineage == 'import_rework' else 'rejected'
                for number in (1, 2):
                    revisions.record_repetition(instance, runtime, lineage=lineage, lineage_id=basis,
                        event_ref='EX-attempt-' + str(number), outcome=outcome, owner='ai',
                        reason='Observed repetition result', version=number if versioned else None, clock=clock)
                    self.assertEqual(task_contracts.repetition_lineages(runtime)[lineage]['count'], number)
                    holds = revisions.action_repetition_waits(instance, runtime, action)
                    self.assertEqual(len(holds), 0 if number == 1 else 1)
                hold = revisions.repetition_hold(runtime, lineage, basis)
                self.assertEqual((hold['count'], hold['limit'], hold['next_owner']), (2, 2, 'user'))
                self.assertFalse(any('EX-attempt-2' in a.get('receipt_refs', [])
                                     for a in runtime['queue'] if a.get('repetition_lineage') == [lineage, basis]))
                before = deepcopy(runtime)
                revisions.record_repetition(instance, runtime, lineage=lineage, lineage_id=basis,
                    event_ref='EX-attempt-2', outcome=outcome, owner='ai', reason='Observed repetition result',
                    version=2 if versioned else None, clock=clock)
                self.assertEqual(runtime, before)
                change = {'kind': 'repetition_continue', 'decision_id': 'DC-hold', 'lineage': lineage,
                    'lineage_id': basis, 'hold_event_ref': hold['event_ref'],
                    'allowed_action': revisions.action_scope(action)}
                if versioned:
                    change['baseline_revision'] = 2
                wrong_hold = {**deepcopy(change), 'hold_event_ref': 'EX-other-hold'}
                wrong_scope = deepcopy(change)
                wrong_scope['allowed_action']['id'] = 'AC-other'
                for invalid, reason in (
                    (wrong_hold, 'continuation must name the current repetition hold'),
                    (wrong_scope, 'continuation scope differs from the current queued or waiting action')):
                    unchanged = deepcopy((instance, runtime))
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                        governance.apply_decision(instance, runtime, invalid, source_ref='UI-hold', clock=clock)
                    self.assertEqual((instance, runtime), unchanged)
                instance, runtime, decision = governance.apply_decision(instance, runtime, change,
                    source_ref='UI-hold', clock=clock)
                self.assertIsNone(revisions.repetition_hold(runtime, lineage, basis))
                self.assertEqual(task_contracts.repetition_lineages(runtime)[lineage]['count'], 0)
                self.assertEqual(revisions.action_repetition_waits(instance, runtime, action), [])
                self.assertEqual(decision['affected'], [hold['event_ref'], action['id']])
                resumed = next(row for row in runtime['queue'] if row['id'] == action['id'])
                self.assertEqual(revisions.action_scope(resumed), change['allowed_action'])
                self.assertFalse([row for row in runtime['question_links'] if row['status'] == 'open'])
