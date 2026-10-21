"""Fixed declarations fail identically before live-state callbacks run."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import integration, knowledge, submission
from support.fakes.clock import FakeClock


class FixedInputTests(unittest.TestCase):
    def setUp(self):
        self.task = {'id': 'TK-fixed', 'title': 'A fixed task', 'question': 'Compute it'}
        self.digest = knowledge.content_hash(self.task)
        self.context = {'action': {'role': 'research_preparation'}, 'snapshot': 'a' * 40,
                        'tasks': [{**self.task, 'content_sha256': self.digest}]}
        self.extensions = {'revision_resolutions': [{'record_id': self.task['id']}]}
        self.output = {'integration_bundles': [{'integration_id': 'IN-fixed',
            'members': ['output', 'activity-extensions.json/revision_resolutions/0'],
            'impact_set': [], 'authority_refs': []}]}

    def apply(self, output, context=None, current=lambda *args: None):
        return integration.apply_bundles({}, {}, output, self.extensions, context or self.context,
            execution_id='EX-fixed', validate_current=current,
            apply_bundle=lambda *args: None, validate_candidate=lambda *args: None,
            publish=lambda *args: None)

    def test_missing_and_wrong_hash_are_output_errors_at_every_boundary(self):
        for prior in (None, {}, {'TK-fixed': '0' * 64}):
            output = deepcopy(self.output)
            if prior is not None:
                output['integration_bundles'][0]['previous_hashes'] = prior
            with self.subTest(prior=prior), tempfile.TemporaryDirectory() as directory:
                expected = integration.inspect_bundles(output, self.extensions, self.context)
                self.assertEqual([row['rule_id'] for row in expected], ['integration.previous_hash'])
                # The permissive payload schema isolates the shared envelope rule.
                schema = {'type': 'object', 'properties': {'integration_bundles': {}}}
                for mode in ('producer', 'receiver', 'preview'):
                    check = submission.check_submission(output, schema, self.context, self.extensions,
                        Path(directory), mode=mode, execution_id='EX-fixed', tool_sha256='f' * 64,
                        clock=FakeClock())
                    self.assertTrue(all(row in check['issues'] for row in expected))
                receipt = self.apply(output, current=lambda *args: self.fail('invalid declaration reached live state'))
                self.assertEqual(receipt['issues'], expected)
                self.assertEqual(integration.submission_outcome(receipt), 'output_rejected')
                self.assertEqual(integration.failure_kind(receipt['issues']), 'output_contract')
                self.assertEqual(receipt['bundles'][0]['next_owner'], 'producer')

    def test_missing_checker_hash_and_unknown_target_cannot_skip_validation(self):
        output = deepcopy(self.output)
        output['integration_bundles'][0]['previous_hashes'] = {'TK-fixed': self.digest}
        for records, rule, outcome in (([self.task], 'integration.input_context', 'publication_wait'),
                                       ([], 'integration.mutation_target', 'output_rejected')):
            with self.subTest(records=records):
                receipt = self.apply(output, {**self.context, 'tasks': records},
                                     current=lambda *args: self.fail('invalid input reached live state'))
                self.assertEqual([row['rule_id'] for row in receipt['issues']], [rule])
                self.assertEqual(integration.submission_outcome(receipt), outcome)

    def test_correct_hash_passes_the_shared_fixed_check(self):
        output = deepcopy(self.output)
        output['integration_bundles'][0]['previous_hashes'] = {'TK-fixed': self.digest}
        self.assertEqual(integration.inspect_bundles(output, self.extensions, self.context), [])
        self.assertEqual(self.apply(output)['status'], 'accepted')

    def test_a_plain_validation_error_is_not_evidence_of_changed_premises(self):
        output = deepcopy(self.output)
        output['integration_bundles'][0]['previous_hashes'] = {'TK-fixed': self.digest}
        def invalid(*args):
            raise ValueError('malformed declaration discovered by live validator')
        receipt = self.apply(output, current=invalid)
        self.assertEqual(integration.submission_outcome(receipt), 'output_rejected')
        self.assertNotIn('integration.currentness', [row['rule_id'] for row in receipt['issues']])
