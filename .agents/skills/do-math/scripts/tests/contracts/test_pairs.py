"""Every contract pair (설계 3.3; 의무 1-A, 1-C): each producer branch passes its receiving check, and the
receiver names no field that no producer branch writes. Branches a receiver rejects today are the known
defects below, each with its own reproduction."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import (PAIRS, TEXT_RULE_ID_SAMPLES, accepted_condition, accepted_rule_ids, enumerated_pointers,
                             stored_rule_id_errors)


class ContractPairTests(unittest.TestCase):
    def test_runner_samples_cover_success_bound_incomplete_and_stopped(self):
        pair = next(pair for pair in PAIRS if pair.name == 'runner result (stored artifact)')
        expected = {
            'collected': ('completed', {}, None, None, 'output_collected'),
            'collected, bound': ('completed', None, 'provider_evidence_only', None, 'output_collected'),
            'incomplete': ('failed', None, None, 'execution_failure', 'incomplete'),
            'stopped': ('stopped', None, None, 'execution_failure', 'output_collected'),
        }
        with tempfile.TemporaryDirectory() as directory:
            samples = pair.samples(Path(directory))
        self.assertEqual([label for label, _ in samples],
                         [provider + ', ' + branch for provider in ('codex', 'claude') for branch in expected])
        for label, result in samples:
            with self.subTest(branch=label):
                branch = label.split(', ', 1)[1]
                self.assertEqual((result['status'], result['output'], result.get('collection'),
                                  result.get('error_kind'), result['execution']['collect']['result']), expected[branch])
                collected = result['execution']['collect']
                self.assertEqual(collected['reasons'], ['cli_nonzero_exit'] if branch == 'incomplete' else [])
                self.assertEqual(result['error'], 'cli_nonzero_exit' if branch == 'incomplete' else
                                 'stop requested or timeout' if branch == 'stopped' else None)
                self.assertTrue(collected['termination_barrier']['confirmed'])
                for name in ('source_request', 'source_prompt', 'stdout', 'stderr', 'final'):
                    artifact = collected[name]
                    self.assertEqual(artifact['bytes'], len(artifact['raw']))
                    self.assertEqual(artifact['sha256'], hashlib.sha256(artifact['raw']).hexdigest())
                request = json.loads(collected['source_request']['raw'])
                self.assertEqual('control_binding' in request, branch == 'collected, bound')
                if branch == 'collected, bound':
                    self.assertEqual(request['control_binding']['execution_id'], result['execution_id'])
                    self.assertEqual(collected['final']['raw'], b'Draft submitted.')

    def test_every_producer_branch_is_received_and_every_named_field_is_produced(self):
        self.assertGreater(len(PAIRS), 0)
        for pair in PAIRS:
            with self.subTest(pair=pair.name), tempfile.TemporaryDirectory() as directory:
                samples = pair.samples(Path(directory))
                self.assertGreater(len(samples), 0, 'a pair needs producer samples')
                rejected = []
                for branch, value in samples:
                    try:
                        pair.receive(deepcopy(value))
                    except ValueError as error:
                        rejected.append((branch, str(error)))
                self.assertEqual(rejected, [], 'producer branches the receiving check rejects')
                if pair.fields is not None:
                    written = set().union(*(pair.written(value) for _, value in samples))
                    self.assertEqual(sorted(pair.fields - written), [],
                                     'fields the receiving check names that no producer branch writes')


    def test_worker_samples_preserve_both_assigned_model_flags_for_each_legal_assignment(self):
        from do_math.claude_adapter import ADAPTERS
        prefix = 'worker request ('
        pairs = {pair.name[len(prefix):-1]: pair for pair in PAIRS if pair.name.startswith(prefix)}
        self.assertEqual(set(pairs), set(ADAPTERS))
        for provider, pair in pairs.items():
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                assignments = {}
                for label, request in pair.samples(Path(directory)):
                    flags = label.split(',') if label != 'bare' else []
                    only = 'claude_only' in flags
                    key = tuple(flag for flag in flags if flag != 'claude_only')
                    choices = assignments.setdefault(key, {})
                    self.assertNotIn(only, choices, (provider, label))
                    choices[only] = request
                self.assertTrue(assignments, 'no worker assignments were examined')
                for assignment, choices in assignments.items():
                    with self.subTest(assignment=assignment):
                        self.assertEqual(set(choices), {False, True})
                        expected = deepcopy(choices[False])
                        if provider == 'claude':
                            expected['claude_only_assigned_model'] = True
                        self.assertEqual(choices[True], expected)


class KnownPairDefectTests(unittest.TestCase):
    def test_every_rule_id_the_tracker_accepts_is_storable(self):
        for rule_id, value in accepted_rule_ids(TEXT_RULE_ID_SAMPLES):
            with self.subTest(rule_id=rule_id):
                self.assertEqual(stored_rule_id_errors(value), [])

    def test_the_condition_grammar_rejects_values_outside_every_stored_enumeration(self):
        for family, space, pointer, enumeration in enumerated_pointers():
            with self.subTest(pointer=family + pointer):
                self.assertFalse(accepted_condition(space, family, pointer, 'not-a-stored-value'))


if __name__ == '__main__':
    unittest.main()
