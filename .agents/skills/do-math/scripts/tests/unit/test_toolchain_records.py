"""Shared toolchain records and the record writer's judgments (``trust_inventory``, layer 2).

``setup_lean`` (layer 3) observes the host, holds the writer lock and writes;
the judgments it applies are these functions. The synthetic toolchain and its
record come from ``research_fixtures.trust_fixture`` over real files.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from do_math import trust_inventory as records
from do_math.canonical import exact_content_hash
from research_fixtures import trust_fixture, validation_fixture


class RecordFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.request = trust_fixture(self.root, ['synthetic-lean'])
        self.path = Path(self.request['toolchain_record']['path'])
        self.record = records.read_record(self.path)
        self.identity = self.record['identity']
        self.olean = Path(self.identity['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'


class RecordContractTests(RecordFixture):
    def test_a_record_names_its_identity_and_first_content_baseline(self):
        baseline = self.record['baselines'][0]
        self.assertEqual(self.record['id'], records.record_id(self.identity, baseline['content']['sha256']))
        self.assertEqual(self.record['identity_sha256'], exact_content_hash(self.identity))
        self.assertEqual(self.path, records.record_path(self.path.parent, self.record['id']))
        self.assertEqual(records.record_errors(self.record), [])
        self.assertEqual(records.binding(self.record), {
            'baseline': 0, 'fingerprint_sha256': baseline['fingerprint']['sha256'],
            'content_sha256': baseline['content']['sha256'], 'validation_sha256': baseline['validation_sha256']})
        self.assertEqual(baseline['validation_sha256'], records.validation_sha256(baseline['validation']))
        self.assertEqual(records.registration_request(self.record, self.path, records.binding(self.record)), self.request)

    def test_record_errors_name_the_broken_rule(self):
        cases = {
            'schema': (lambda r: r.update(schema='other'), 'toolchain record differs from do-math-toolchain-record/1: schema'),
            'identity digest': (lambda r: r.update(identity_sha256='0' * 64),
                                'toolchain record identity digest differs from its identity'),
            'record ID': (lambda r: r.update(id='TC-' + '0' * 64),
                          'toolchain record ID differs from its identity and first content baseline'),
            'absent baseline': (lambda r: r['checks'].append({'checked_at': 'now', 'baseline': 1, 'result': 'passed',
                                                             'mismatched': []}),
                                'toolchain record check names an absent baseline'),
            'identity scope': (lambda r: r['identity'].update(version=''), 'toolchain.version must be nonempty'),
        }
        for name, (change, message) in cases.items():
            with self.subTest(name):
                record = deepcopy(self.record)
                change(record)
                errors = records.record_errors(record)
                self.assertTrue(any(message in error for error in errors), errors)
                with self.assertRaisesRegex(ValueError, message.split(':')[0]):
                    records.write_record(self.root / 'written.json', record)
        self.assertFalse((self.root / 'written.json').exists())

    def test_read_record_refuses_a_record_that_breaks_its_contract(self):
        record = json.loads(self.path.read_text(encoding='utf-8'))
        record['identity_sha256'] = '0' * 64
        self.path.write_text(json.dumps(record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'toolchain record identity digest differs from its identity'):
            records.read_record(self.path)

    def test_usable_needs_a_verified_current_compile_and_no_later_mismatch(self):
        self.assertEqual(records.usable_errors(self.record), [])
        failed = deepcopy(self.record)
        failed['baselines'][-1]['validation'].update(status='failed')
        self.assertEqual(records.usable_errors(failed), ['current toolchain baseline has no successful representative check'])
        nonzero = deepcopy(self.record)
        nonzero['baselines'][-1]['validation'].update(exit_code=3)
        self.assertEqual(records.usable_errors(nonzero), ['current toolchain baseline has no successful representative check'])
        mismatched = deepcopy(self.record)
        mismatched['checks'].append({'checked_at': 'now', 'baseline': 0, 'result': 'mismatch', 'mismatched': ['x']})
        self.assertEqual(records.usable_errors(mismatched),
                         ['a content check found files that differ from the current toolchain baseline'])

    def test_the_validation_program_follows_the_project(self):
        self.assertEqual(records.validation_program({'project': None}), (records.CORE_SMOKE, 'lean_core_representative_proofs'))
        self.assertEqual(records.validation_program({'project': {'source_identity': {}}}),
                         (records.SMOKE, 'mathlib_import_and_representative_proofs'))
        project = {'executable': str(self.root / 'lean' / 'lean.exe'),
                   'project': {'source_identity': {'root': str(self.root / 'project')}}}
        self.assertEqual(records.roots(project), {'toolchain': self.root / 'lean', 'project': self.root / 'project'})

    def test_representative_check_seconds_round_up(self):
        self.assertEqual(records.representative_check_seconds(
            {'started_at': '2026-09-20T00:00:00Z', 'finished_at': '2026-09-20T00:03:59.2Z'}), 240)
        self.assertEqual(records.representative_check_seconds(
            {'started_at': '2026-09-20T00:00:00Z', 'finished_at': '2026-09-20T00:00:01Z'}), 1)


class FingerprintTests(RecordFixture):
    def test_fingerprint_and_content_name_every_judgment_file(self):
        fingerprint = records.observe_fingerprint(self.identity)
        self.assertEqual(set(fingerprint['files']), {'toolchain/bin/libleanshared.dll', 'toolchain/lib/lean/Init/Prelude.olean'})
        self.assertEqual(fingerprint['sha256'], exact_content_hash(fingerprint['files']))
        content = records.content_hashes(self.identity, fingerprint['files'])
        self.assertEqual(content, self.record['baselines'][0]['content'])
        (self.olean.parent / '.git').mkdir()
        (self.olean.parent / '.git' / 'Hidden.olean').write_bytes(b'not a module')
        self.assertEqual(records.observe_fingerprint(self.identity)['files'], fingerprint['files'])

    def test_changed_files_lists_added_removed_and_different_rows(self):
        self.assertEqual(records.changed_files({'a': 1, 'b': 2, 'c': 3}, {'a': 1, 'b': 9, 'd': 4}), ['b', 'c', 'd'])
        self.assertEqual(records.changed_files({'a': 1}, {'a': 1}), [])


class WriterJudgmentTests(RecordFixture):
    """What ``setup_lean`` refuses, reuses or records, given the observed identity, fingerprint and contents."""

    def test_a_baseline_needs_a_verified_compile_and_unmoved_files(self):
        validation = validation_fixture(self.identity, self.root / 'smoke.lean')
        self.assertIsNone(records.baseline_refusal(validation))
        failed = {**validation, 'status': 'failed'}
        self.assertEqual(records.baseline_refusal(failed), {'status': 'failed', 'validation': failed,
                                                            'reason': 'the representative compile did not succeed'})
        fingerprint = records.observe_fingerprint(self.identity)
        self.assertIsNone(records.fingerprint_moved_refusal(fingerprint, fingerprint))
        self.assertEqual(records.fingerprint_moved_refusal({'sha256': '0' * 64}, fingerprint),
                         {'status': 'failed', 'reason': 'judgment files changed while the baseline was being recorded'})

    def test_a_compile_is_verified_only_when_it_ran_to_exit_code_zero(self):
        self.assertEqual(records.validation_status(0, False), 'verified')
        self.assertEqual(records.validation_status(1, False), 'failed')
        self.assertEqual(records.validation_status(None, True), 'failed')
        self.assertEqual(records.validation_status(0, True), 'failed')

    def test_evidence_must_be_outside_the_recorded_roots(self):
        self.assertIsNone(records.check_evidence_outside_roots(self.root / 'evidence', self.identity))
        with self.assertRaisesRegex(ValueError, 'validation evidence must be outside the recorded toolchain and project roots'):
            records.check_evidence_outside_roots(Path(self.identity['executable']).parents[1] / 'evidence', self.identity)

    def test_the_matching_usable_record_is_reused_and_a_changed_one_is_not(self):
        fingerprint = records.observe_fingerprint(self.identity)
        candidates = records.records_for(self.path.parent, self.identity)
        self.assertEqual(candidates, [(self.path, self.record)])
        self.assertEqual(records.reusable_record(candidates, fingerprint), (self.path, self.record))
        self.assertIsNone(records.reusable_record(candidates, {'sha256': '0' * 64}))
        unusable = deepcopy(self.record)
        unusable['baselines'][-1]['validation']['status'] = 'failed'
        self.assertIsNone(records.reusable_record([(self.path, unusable)], fingerprint))
        self.assertEqual(records.records_for(self.path.parent, {**self.identity, 'version': 'other'}), [])
        self.assertEqual(records.rerecord_required(self.path), {
            'status': 'rerecord_required', 'record_path': str(self.path),
            'reason': 'the installed bytes match this record but its metadata or check history changed; '
                      'a user or operator decides whether to run --rerecord'})

    def test_a_command_without_a_record_name_needs_exactly_one_record(self):
        self.assertEqual(records.only_record([(self.path, self.record)]), (self.path, self.record))
        with self.assertRaisesRegex(ValueError, 'name the record with --record; records of the current identity: none'):
            records.only_record([])
        with self.assertRaisesRegex(ValueError, 'records of the current identity: ' + self.record['id'] + ', '):
            records.only_record([(self.path, self.record), (self.path, self.record)])

    def test_a_rerecord_keeps_the_identity_and_the_judgment_file_contents(self):
        self.assertIsNone(records.identity_refusal(self.record, self.identity, self.path))
        refused = records.identity_refusal(self.record, {**self.identity, 'version': 'Lean test 4.33.0'}, self.path)
        self.assertEqual((refused['status'], refused['record_path']), ('refused', str(self.path)))
        self.assertIn('the installed identity differs from the record', refused['reason'])
        content = self.record['baselines'][-1]['content']
        self.assertIsNone(records.contents_refusal(self.record, content, self.path))
        changed = {'files': {**content['files'], 'toolchain/lib/lean/Init/Prelude.olean': '0' * 64}}
        refused = records.contents_refusal(self.record, changed, self.path)
        self.assertEqual(refused['mismatched'], ['toolchain/lib/lean/Init/Prelude.olean'])
        self.assertIn('judgment file contents differ from the current baseline', refused['reason'])

    def test_a_content_check_compares_with_the_current_baseline(self):
        content = self.record['baselines'][-1]['content']
        self.assertEqual(records.content_check(self.record, content, checked_at='T'),
                         {'checked_at': 'T', 'baseline': 0, 'result': 'passed', 'mismatched': []})
        changed = {'files': {**content['files'], 'toolchain/extra.dll': '1' * 64}}
        self.assertEqual(records.content_check(self.record, changed, checked_at='T'),
                         {'checked_at': 'T', 'baseline': 0, 'result': 'mismatch', 'mismatched': ['toolchain/extra.dll']})

    def test_a_writer_excludes_other_writers(self):
        directory = self.root / 'new-records'
        with records.writer_lock(directory):
            self.assertTrue((directory / '.lock').exists())
            with self.assertRaises(OSError) as refused:
                with records.writer_lock(directory):
                    self.fail('a second writer entered')
            self.assertIsInstance(refused.exception, OSError)
        with records.writer_lock(directory):
            self.assertTrue(directory.is_dir())


if __name__ == '__main__':
    unittest.main()
