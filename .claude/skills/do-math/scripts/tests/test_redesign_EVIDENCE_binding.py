"""Negative specimens for archived MAIN run evidence; no real test-pass claims."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_coverage


class ArchivedEvidenceTests(unittest.TestCase):
    def fixture(self, root):
        folder = root / 'checks/run'
        snapshot = folder / 'repository'
        code = snapshot / '.claude/skills/do-math/scripts/tests/test_sample.py'
        code.parent.mkdir(parents=True)
        code.write_text('class Sample:\n    def test_one(self): pass\n', encoding='utf-8')
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        metadata = {'command': ['python', '-m', 'unittest', '-v', 'test_sample'],
            'started_at': 'fixture-start', 'ended_at': 'fixture-end', 'returncode': 0,
            'files': {'scripts/tests/test_sample.py': digest(code)}, 'support_files': {}}
        (folder / 'run.json').write_text(json.dumps(metadata), encoding='utf-8')
        log = folder / 'stderr.txt'
        log.write_text('test_one (test_sample.Sample.test_one) ... ok\n\nRan 1 test in 0.1s\n\nOK\n', encoding='utf-8')
        coord = '.claude/skills/do-math/scripts/tests/test_sample.py::Sample.test_one'
        run = {'directory': 'checks/run', 'manifest_sha256': digest(folder / 'run.json'),
            'log_sha256': digest(log), 'tests': {coord: 'passed'},
            'boundary': 'Synthetic evidence-reader fixture, not execution evidence'}
        trace = {'observed_runs': {'sample': run}, 'vectors': {'V01': {
            'implementation': [], 'evidence': [{'coordinate': coord, 'observations': [
                {'run_id': 'sample', 'outcome': 'passed'}]}]}}}
        return trace, code, folder

    def test_archived_bytes_log_outcomes_and_completion_are_bound(self):
        for mutation, message in [('bytes', 'snapshot bytes'), ('log', 'log digest'),
                                  ('outcome', 'observed outcomes'), ('unfinished', 'completed run'),
                                  ('missing_test', 'cited test'), ('escape', 'archive directory')]:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                trace, code, folder = self.fixture(root)
                self.assertEqual(check_coverage.validate_observations(trace, root), [])
                run = trace['observed_runs']['sample']
                if mutation == 'bytes': code.write_text('changed', encoding='utf-8')
                elif mutation == 'log': (folder / 'stderr.txt').write_text('OK', encoding='utf-8')
                elif mutation == 'outcome': run['tests'][next(iter(run['tests']))] = 'failed'
                elif mutation == 'unfinished':
                    path = folder / 'run.json'; metadata = json.loads(path.read_text())
                    metadata.pop('ended_at'); path.write_text(json.dumps(metadata), encoding='utf-8')
                    run['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                elif mutation == 'missing_test':
                    trace['vectors']['V01']['evidence'][0]['coordinate'] = 'absent.py::Missing.test_no'
                else: run['directory'] = '../outside'
                self.assertTrue(any(message in e for e in check_coverage.validate_observations(trace, root)))

    def test_old_snapshot_does_not_claim_current_source_equality(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); trace, _, _ = self.fixture(root)
            current = root / '.claude/skills/do-math/scripts/tests/test_sample.py'
            current.parent.mkdir(parents=True)
            current.write_text('a newer implementation', encoding='utf-8')
            # Historical observation is valid; no current-edition pass is asserted.
            self.assertEqual(check_coverage.validate_observations(trace, root), [])

    def test_gap_classification_cannot_drop_a_gap_or_invent_a_category(self):
        row = {'gaps': ['untested transition'], 'unproven': [{'gap_indexes': [0],
            'category': 'b', 'basis': 'Real transition exists; its replay has no assertion.',
            'owners': ['ENGINE']}]}
        self.assertEqual(check_coverage.unproven_errors('V01', row), [])
        for field, value in [('gap_indexes', []), ('category', 'passed'), ('basis', ''), ('owners', [])]:
            with self.subTest(field=field):
                specimen = json.loads(json.dumps(row)); specimen['unproven'][0][field] = value
                self.assertTrue(check_coverage.unproven_errors('V01', specimen))

    def test_partial_execution_requires_a_cited_observed_test(self):
        from test_redesign_EVIDENCE import ROOT, TRACE
        trace = json.loads(TRACE.read_text(encoding='utf-8'))
        row = json.loads(json.dumps(trace['vectors']['V45']))
        row['execution'] = {'state': 'partial', 'run_ids': ['bounded-run']}
        coordinate = row['evidence'][0]['coordinate']
        run = {'tests': {coordinate: 'passed'}, 'file_sha256': {
            c.partition('::')[0]: 'fixture' for c in row['implementation']}}
        errors = []
        check_coverage._item(ROOT, 'V45', row, trace['semantic_groups'], {'bounded-run': run}, errors)
        self.assertEqual(errors, [])
        run['tests'] = {'unrelated.py::T.test_unrelated': 'passed'}
        errors = []
        check_coverage._item(ROOT, 'V45', row, trace['semantic_groups'], {'bounded-run': run}, errors)
        self.assertTrue(any('partial execution needs a cited observed test' in e for e in errors))


    def test_feature_pass_cannot_hide_a_gap_or_a_cited_failure(self):
        from test_redesign_EVIDENCE import ROOT, TRACE
        trace = json.loads(TRACE.read_text(encoding='utf-8'))
        row = json.loads(json.dumps(trace['vectors']['V45']))
        row.update(mapping='mapped', gaps=[])
        row['execution'] = {'state': 'passed', 'run_ids': ['good']}
        coordinate = row['evidence'][0]['coordinate']
        run = {'tests': {coordinate: 'passed'}, 'file_sha256': {
            c.partition('::')[0]: 'fixture' for c in row['implementation']}}
        def errors_for(specimen, runs):
            errors = []
            check_coverage._item(ROOT, 'V45', specimen, trace['semantic_groups'], runs, errors)
            return errors
        self.assertEqual(errors_for(row, {'good': run}), [])
        incomplete = json.loads(json.dumps(row))
        incomplete.update(mapping='partial', gaps=['concurrent creation not replayed'])
        self.assertTrue(any('pass requires complete semantic mapping' in e
                            for e in errors_for(incomplete, {'good': run})))
        contradictory = json.loads(json.dumps(row))
        contradictory['execution']['run_ids'].append('bad')
        failed = {**run, 'tests': {coordinate: 'failed'}}
        self.assertTrue(any('pass includes a cited failure' in e
                            for e in errors_for(contradictory, {'good': run, 'bad': failed})))


if __name__ == '__main__': unittest.main()
