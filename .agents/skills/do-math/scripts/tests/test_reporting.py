import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import new_id
from do_math.engine import _repository as ResearchRepository
from do_math.reporting import timeline, timeline_csv
from do_math.cli import build_parser, execute
from test_redesign_SURFACE import stored_surface_state, surface_state


class ReportingTests(unittest.TestCase):
    def test_claude_usage_projection_survives_git_and_timeline(self):
        from do_math.claude_stream import parse_stream
        from do_math.engine import json_safe
        from do_math.execution_profiles import execution_observation
        rows = [
            {"type": "system", "subtype": "init", "session_id": "fixture"},
            {"type": "result", "subtype": "success", "is_error": False,
             "session_id": "fixture", "structured_output": {},
             "usage": {"input_tokens": 10, "output_tokens": 5},
             "modelUsage": {"claude-opus-5": {"inputTokens": 10, "costUSD": 0.01}}},
        ]
        raw = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
        parsed = parse_stream(raw)
        self.assertTrue(parsed["turn_completed"])
        keys = ("usage_segments", "model_usage_reported", "usage_scope", "reported_models")
        projected = json_safe({key: parsed[key] for key in keys})
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            identifier = new_id("RI")
            store = ResearchRepository(root, identifier)
            instance, runtime = stored_surface_state()
            instance.update(id=identifier, workspace=str(root / "workspace"))
            runtime["activities"]["AC-1"]["owner_ref"] = identifier
            execution = runtime["executions"]["EX-1"]
            execution.update(status="ended", outcome="cancelled",
                ended_at="2026-09-25T00:00:00Z", usage=parsed["usage_total"], **projected)
            execution["provider_observation"] = execution_observation({
                "provider_observation": {key: parsed[key] for key in keys}})
            head = store.initialize(instance, runtime)
            saved = store.load(head)[2]["executions"]["EX-1"]
            report = timeline(root, identifier, snapshot=head)["rows"][0]
            for key in keys:
                self.assertEqual(saved[key], projected[key])
                self.assertEqual(report[key], projected[key])
            self.assertEqual(report["usage"], {"input_tokens": 10, "output_tokens": 5})
            preserved = json.loads(saved["provider_observation"]["reported_fields_json"])
            self.assertEqual(preserved["model_usage_reported"], parsed["model_usage_reported"])
            self.assertEqual(saved["model_usage_reported"]["claude-opus-5"]["costUSD"],
                             {"reported_decimal": "0.01"})

    def test_status_reports_artifact_presence_and_length_in_one_batch_without_bytes(self):
        import hashlib
        from types import SimpleNamespace
        from unittest.mock import Mock, patch
        from do_math.reporting import snapshot_report
        from do_math.git_store import GitStateStoreError
        instance, runtime = surface_state()
        raw = b'preserved result'
        paths = ['runtime/artifacts/BA-1/' + str(index) for index in range(12)]
        runtime['executions']['EX-1']['output_files'] = [
            {'path': str(index), 'artifact_ref': path,
             'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
            for index, path in enumerate(paths)]
        head = 'a' * 40
        stored = dict.fromkeys(paths, len(raw))

        def sizes(requested, snapshot, *, missing='raise'):
            self.assertEqual(snapshot, head)
            if missing != 'omit' and any(path not in stored for path in requested):
                raise GitStateStoreError('batch size did not return a blob')
            return {path: stored[path] for path in requested if path in stored}

        store = SimpleNamespace(load=Mock(return_value=(head, instance, runtime)),
            read=Mock(side_effect=AssertionError('status reads no artifact bytes')),
            read_many=Mock(side_effect=AssertionError('status reads no artifact bytes')),
            blob_sizes=Mock(side_effect=sizes))
        with patch('do_math.reporting._repository', return_value=store):
            report = snapshot_report(Path('.'), 'RI-test', requested_areas=['record_storage'])
            self.assertEqual(report['inspection']['status'], 'healthy')
            store.blob_sizes.assert_called_once_with(paths, head, missing='omit')
            # A changed length or a missing artifact blocks; same-length byte changes are for check.
            stored[paths[0]] = len(raw) + 1
            del stored[paths[1]]
            report = snapshot_report(Path('.'), 'RI-test', requested_areas=['record_storage'])
        self.assertEqual(report['inspection']['status'], 'blocked')
        blocked = {evidence for row in report['inspection']['findings'] for evidence in row['evidence']}
        self.assertEqual(blocked & set(paths), {paths[0], paths[1]})
    def test_timeline_preserves_explicit_continuation_and_pending_successor(self):
        from copy import deepcopy
        from types import SimpleNamespace
        from unittest.mock import patch
        pending = {'id': 'AC-work', 'role': 'research_work', 'continuation_of': 'EX-second'}
        runtime = {'executions': {
            'EX-first': {'id': 'EX-first', 'status': 'ended', 'action': {'id': 'AC-work'}},
            'EX-second': {'id': 'EX-second', 'status': 'ended', 'continuation_of': 'EX-first',
                          'action': {'id': 'AC-work', 'continuation_of': 'EX-first'}}},
            'queue': [pending, {'id': 'AC-other', 'role': 'maintenance', 'continuation_of': 'EX-unrelated'}]}
        before = deepcopy(runtime)
        store = SimpleNamespace(load=lambda snapshot: ('a' * 40, {}, runtime))
        with patch('do_math.reporting._repository', return_value=store):
            value = timeline(Path('.'), 'RI-test', snapshot='a' * 40)
        rows = {row['id']: row for row in value['rows']}
        self.assertIsNone(rows['EX-first']['continuation_of'])
        self.assertEqual(rows['EX-second']['continuation_of'], 'EX-first')
        self.assertEqual(rows['EX-second']['next_actions'], [pending])
        self.assertEqual(rows['EX-first']['next_actions'], [])
        exported = {row['id']: row for row in csv.DictReader(io.StringIO(timeline_csv(value)))}
        self.assertEqual(exported['EX-second']['continuation_of'], 'EX-first')
        self.assertEqual(json.loads(exported['EX-second']['next_actions']), [pending])
        self.assertEqual(runtime, before)

    def test_fixed_snapshot_preserves_unknown_times_and_crosses_the_kst_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', '-C', str(root), 'init', '-q'], check=True)
            identifier = new_id('RI')
            store = ResearchRepository(root, identifier)
            instance, runtime = stored_surface_state()
            instance.update(id=identifier, workspace=str(root / 'workspace'))
            runtime['activities']['AC-1']['owner_ref'] = identifier
            runtime['executions']['EX-1'].update(status='ended',
                action={'id': 'A', 'role': 'research_work', 'lineage_id': 'L'}, model='claude-opus-5',
                created_at='2026-09-18T15:01:02+00:00', ended_at='2026-09-18T15:02:03+00:00',
                outcome='cancelled')
            head = store.initialize(instance, runtime)
            instance['title'] = 'later metadata'
            store.save_with_state(head, instance, runtime)[0]
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


if __name__ == '__main__':
    unittest.main()
