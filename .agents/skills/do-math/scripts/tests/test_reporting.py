import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import ResearchRepository, new_id
from do_math.reporting import timeline, timeline_csv
from do_math.cli import build_parser, execute


class ReportingTests(unittest.TestCase):
    def test_fixed_snapshot_preserves_unknown_times_and_crosses_the_kst_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            identifier = new_id('RI')
            store = ResearchRepository(root, identifier)
            instance = {'id': identifier, 'workspace': str(root / 'workspace')}
            runtime = {'executions': {'E': {'id': 'E', 'role': 'research_work', 'status': 'ended',
                'action': {'id': 'A', 'lineage_id': 'L', 'target': 'T'}, 'model': 'claude-opus-5',
                'created_at': '2026-09-18T15:01:02+00:00', 'ended_at': '2026-09-18T15:02:03+00:00',
                'outcome': 'output_accepted', 'budget_kind': 'work'}}, 'queue': []}
            head = store.initialize(instance, runtime)
            runtime['executions']['later'] = {'id': 'later', 'role': 'formal_check', 'status': 'ended'}
            store.save(head, instance, runtime)
            value = timeline(root, identifier, snapshot=head)
            self.assertEqual(value['counts_by_unit'], {'internal_execution': 1})
            row = value['rows'][0]
            self.assertEqual(row['created_at_local'], '2026-09-19T00:01:02+09:00')
            self.assertIsNone(row['started_at_utc'])
            self.assertIsNone(row['started_at_local'])
            self.assertEqual(row['lineage_id'], 'L')
            csv_row = next(csv.DictReader(io.StringIO(timeline_csv(value))))
            self.assertEqual(csv_row['started_at_utc'], '')
            args = build_parser().parse_args(['timeline', '--repository', str(root), '--instance', identifier,
                                              '--snapshot', head, '--format', 'csv'])
            actual, code = execute(args)
            self.assertEqual(code, 0)
            self.assertEqual(actual, timeline_csv(value))

    def test_local_operator_evidence_has_its_own_hash_and_count_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            identifier = new_id('RI')
            store = ResearchRepository(root, identifier)
            instance = {'id': identifier, 'workspace': str(root / 'workspace')}
            store.initialize(instance, {'executions': {}, 'queue': []})
            path = root / 'workspace/operator/runs/one/result.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'outcome': 'completed', 'ended_at': '2026-09-18T15:00:00Z',
                                       'result': {'assigned_model': 'claude-opus-5', 'usage': {'output_tokens': 10}}}))
            self.assertEqual(timeline(root, identifier)['rows'], [])
            value = timeline(root, identifier, include_operator=True)
            self.assertEqual(value['counts_by_unit'], {'independent_operator_invocation': 1})
            row = value['rows'][0]
            self.assertIsNone(row['snapshot'])
            self.assertEqual(len(row['evidence_source']['sha256']), 64)
            self.assertIn('observed_at', row['evidence_source'])


if __name__ == '__main__':
    unittest.main()
