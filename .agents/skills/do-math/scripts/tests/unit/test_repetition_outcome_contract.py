"""4-C: every declared repetition result has one counting and follow-up rule."""
from copy import deepcopy
import re
import unittest

from do_math import governance, revisions, task_contracts as tc
from do_math.configuration import DEFAULT_CONFIG
from support.fakes.clock import FakeClock
from support.state_builders import governance_start


def continued_receipt(clock):
    instance = governance_start({'id': 'RI-counter', 'knowledge': {}, 'relations': [],
        'goal_status': 'unresolved', 'config': {'goal_auditors': 2,
            'max_artifact_bytes': DEFAULT_CONFIG['max_artifact_bytes'], 'exhaustion_empty_limit': 2}})
    runtime = {'tasks': {}, 'activities': {}, 'executions': {}, 'queue': [], 'questions': [],
        'question_links': [], 'history': [], 'inputs': [], 'interpretations': {}, 'status': 'ready'}
    instance['governance_sources'] = {'UI-counter': governance.preserve_source(
        'UI-counter', 'Continue this exact empty preparation.', origin='user')}
    original = {'id': 'AC-original', 'role': 'research_preparation'}
    revisions.bind_repetition_bases(instance, runtime, original)
    basis = original['repetition_bases']['exhaustion_empty']
    for number in range(2):
        identifier = 'EX-empty-' + str(number)
        runtime['executions'][identifier] = {'id': identifier, 'role': 'research_preparation',
            'status': 'ended', 'outcome': 'output_accepted', 'action': deepcopy(original)}
        revisions.record_execution_outcome(instance, runtime, original, {'summary': 'No candidate'},
            identifier, accepted=True, clock=clock)
    hold = revisions.repetition_hold(runtime, 'exhaustion_empty', basis)
    change = {'kind': 'repetition_continue', 'decision_id': 'DC-counter', 'lineage': 'exhaustion_empty',
        'lineage_id': basis, 'hold_event_ref': hold['event_ref'],
        'allowed_action': {'id': 'AC-counter', 'role': 'research_preparation', 'revision_targets': {},
                           'repetition_bases': {'exhaustion_empty': basis}}}
    before = tc.repetition_lineages(runtime)['exhaustion_empty']['count']
    instance, runtime, _ = governance.apply_decision(instance, runtime, change,
        source_ref='UI-counter', clock=clock)
    return before, 'exhaustion_empty', runtime


class RepetitionOutcomeContractTests(unittest.TestCase):
    def test_every_declared_outcome_counts_and_diagnoses_as_declared(self):
        for outcome, rule in tc.REPETITION_OUTCOMES.items():
            with self.subTest(outcome=outcome):
                clock = FakeClock()
                if outcome == 'continued':
                    before, lineage, runtime = continued_receipt(clock)
                else:
                    lineage = 'exhaustion_empty' if outcome == 'empty' else 'selection_failure'
                    instance = {'id': 'RI-counter', 'config': {}}
                    runtime = {'history': [], 'queue': [], 'question_links': []}
                    for number in range(2):
                        revisions.record_repetition(instance, runtime, lineage=lineage, lineage_id='input-one',
                            event_ref='EX-base-' + str(number), outcome='rejected', owner='ai',
                            reason='Rejected baseline', clock=clock)
                    before = tc.repetition_lineages(runtime)[lineage]['count']
                    revisions.record_repetition(instance, runtime, lineage=lineage, lineage_id='input-one',
                        event_ref='EX-outcome', outcome=outcome, owner='ai', reason='Outcome receipt', clock=clock)
                    preserved = deepcopy(runtime)
                    revisions.record_repetition(instance, runtime, lineage=lineage, lineage_id='input-one',
                        event_ref='EX-outcome', outcome=outcome, owner='ai', reason='Outcome receipt', clock=clock)
                    self.assertEqual(runtime, preserved)
                self.assertEqual(before, 2)
                expected = {'reset': 0, 'retain': before, 'increment': before + 1}[rule['counter']]
                self.assertEqual(tc.repetition_lineages(runtime)[lineage]['count'], expected)
                diagnostics = [row for row in runtime['queue'] if row['role'] == 'operational_review'
                               and 'EX-outcome' in row.get('receipt_refs', [])]
                self.assertEqual(bool(diagnostics), rule['diagnose'])
                if outcome == 'continued':
                    self.assertEqual([row['id'] for row in runtime['queue']], ['AC-counter'])
                    self.assertEqual(revisions.active_repetition_holds(runtime), {})

    def test_unknown_result_is_rejected_before_any_receipt_or_followup(self):
        for outcome in ('unknown-result', None, [], True):
            instance, runtime = {'config': {}}, {'history': [], 'queue': []}
            before = deepcopy((instance, runtime))
            reason = 'unknown repetition outcome: ' + repr(outcome)
            with self.subTest(outcome=outcome), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                revisions.record_repetition(instance, runtime, lineage='selection_failure', lineage_id='input-one',
                    event_ref='EX-unknown', outcome=outcome, owner='ai', reason='Unknown receipt', clock=FakeClock())
            self.assertEqual((instance, runtime), before)

    def test_semantic_version_counts_its_actual_version_without_diagnostic(self):
        for lineage in ('proposal_version', 'contract_revision'):
            for outcome in ('authored', 'revised'):
                runtime = {'history': [], 'queue': []}
                with self.subTest(lineage=lineage, outcome=outcome):
                    revisions.record_repetition({'config': {}}, runtime, lineage=lineage, lineage_id='item-one',
                        event_ref='EX-version', outcome=outcome, version=7, owner='ai',
                        reason='Actual semantic version', clock=FakeClock())
                    self.assertEqual(tc.repetition_lineages(runtime)[lineage]['count'], 7)
                    self.assertEqual(runtime['queue'], [])
