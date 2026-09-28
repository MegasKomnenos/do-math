import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.repository import new_id
from do_math.repository import ResearchRepository
from do_math.reporting import ASSURANCE, render_human_report, snapshot_report, timeline, timeline_csv
from do_math.cli import build_parser, execute
from record_fixtures import stored_surface_state, surface_state
from research_fixtures import git_init
from do_math import reporting


class ReportingTests(unittest.TestCase):
    def test_claude_usage_projection_survives_git_and_timeline(self):
        from do_math.claude_stream import parse_stream
        from do_math.payloads import json_safe
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
            git_init(root)
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
        from unittest.mock import create_autospec, patch
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

        store = create_autospec(ResearchRepository, instance=True)
        store.load.return_value = (head, instance, runtime)
        store.read.side_effect = store.read_many.side_effect = AssertionError('status reads no artifact bytes')
        store.blob_sizes.side_effect = sizes
        with patch('do_math.reporting.ResearchRepository', return_value=store):
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
        from unittest.mock import create_autospec, patch
        pending = {'id': 'AC-work', 'role': 'research_work', 'continuation_of': 'EX-second'}
        runtime = {'executions': {
            'EX-first': {'id': 'EX-first', 'status': 'ended', 'action': {'id': 'AC-work'}},
            'EX-second': {'id': 'EX-second', 'status': 'ended', 'continuation_of': 'EX-first',
                          'action': {'id': 'AC-work', 'continuation_of': 'EX-first'}}},
            'queue': [pending, {'id': 'AC-other', 'role': 'maintenance', 'continuation_of': 'EX-unrelated'}]}
        before = deepcopy(runtime)
        store = create_autospec(ResearchRepository, instance=True)
        store.load.side_effect = lambda snapshot=None: ('a' * 40, {}, runtime)
        with patch('do_math.reporting.ResearchRepository', return_value=store):
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
            git_init(root)
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

    def test_non_task_wait_projection_is_detached_and_printable(self):
        runtime = {'executions': {}, 'queue': [{'id': 'AC-prep', 'role': 'research_preparation',
            'dispatch_wait': {'kind': 'capacity', 'constraint_id': 'BC-old', 'next_owner': 'user'}}]}
        rows = reporting.dispatch_waits(runtime)
        text = '\n'.join(reporting.render_dispatch_waits({'tasks': [], 'dispatch_waits': rows}))
        self.assertIn('AC-prep', text)
        self.assertIn('capacity', text)
        self.assertIn('BC-old', text)
        rows[0]['wait']['kind'] = 'changed'
        self.assertEqual(runtime['queue'][0]['dispatch_wait']['kind'], 'capacity')
        runtime['executions']['EX-live'] = {'status': 'running', 'action': {'id': 'AC-prep'}}
        self.assertEqual(reporting.dispatch_waits(runtime), [])


    def test_task_rows_of_an_ended_instance_carry_no_readiness(self):
        from record_fixtures import approved_task
        task, instance, runtime = approved_task()
        task['status'] = 'active'
        self.assertEqual(reporting.task_status(instance, runtime)[0]['readiness']['state'], 'ready')
        for ended in ('closed', 'completed'):
            with self.subTest(status=ended):
                row, = reporting.task_status(instance, {**runtime, 'status': ended})
                self.assertIsNone(row['readiness'])
                self.assertEqual(row['waits'], [])


class StatusSnapshotTests(unittest.TestCase):
    def test_engine_cleanup_failure_reaches_snapshot_reporting(self):
        from do_math.repository import ResearchRepository as Repository
        from unittest.mock import create_autospec
        instance,runtime=surface_state()
        runtime['executions']['EX-1'].update(status='ended',outcome='execution_incomplete')
        from research_fixtures import bare_engine, dispatched_launch
        ex = runtime['executions']['EX-1']
        ex['launch_ticket'] = {**dispatched_launch(ex['id'], instance['execution_profiles'][ex['execution_profile_ref']['id']]), 'phase':'finished'}
        ex['capacity']={'local_termination':'confirmed'}
        with tempfile.TemporaryDirectory() as directory:
            instance['workspace']=directory
            (Path(directory)/'runs/EX-1').mkdir(parents=True)
            engine=bare_engine(instance,runtime,head='a'*40,store=create_autospec(Repository,instance=True))
            state={'executions':runtime['executions'],'runtime':runtime,'approved_execution_ids':['EX-1'],
                   'protected_references':[],'reference_records':{}}
            with patch.object(engine,'_cleanup_scope',return_value=['EX-1']), \
                 patch.object(engine,'_retention_state',return_value=state), \
                 patch.object(engine,'_save'), \
                 patch('do_math.retention._inventory',side_effect=PermissionError('cannot inspect files')):
                result=engine._maintenance_cleanup({},'EX-maint')
            self.assertEqual(result['status'],'degraded')
            self.assertEqual(runtime['history'][-1]['kind'],'maintenance_cleanup')
            engine.store.load.return_value=('a'*40,instance,runtime)
            with patch('do_math.reporting.ResearchRepository',return_value=engine.store):
                report=snapshot_report(Path(directory),'IN-1',requested_areas=['record_storage'])
            self.assertTrue(any(row['status']=='degraded' and 'cannot inspect files' in row['message']
                                for row in report['inspection']['findings']))
            self.assertEqual(report['cleanup_failures'][0]['next_owner'],'maintenance')
            self.assertIn('degraded',render_human_report(report))
            self.assertTrue((Path(directory)/'runs/EX-1').exists())

    def test_json_and_human_status_share_one_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git_init(root)
            identifier = new_id("RI")
            store = ResearchRepository(root, identifier)
            instance, runtime = stored_surface_state()
            instance.update(id=identifier, workspace=str(root / "workspace"))
            runtime["activities"]["AC-1"]["owner_ref"] = identifier
            head = store.initialize(instance, runtime)
            budget = {"work-model": {"limit": 1, "used": 0, "execution_ids": []}}
            report = snapshot_report(root, identifier, snapshot=head, host_observation={
                "budget": budget, "research_observed_at": "2026-09-20T00:00:00Z"})
            self.assertEqual(report["snapshot"], head)
            self.assertEqual(report["goal"], "Prove P")
            self.assertEqual(report["assurance"], ASSURANCE)
            self.assertEqual(report["research_observed_at"], "2026-09-20T00:00:00Z")
            self.assertEqual(report["budget"], budget)
            self.assertIsNone(report["pending_controls"], "an unobserved host field stays unobserved")
            human = render_human_report(report)
            self.assertIn(head, human)
            self.assertIn("inspection:", human)
            self.assertIn("work-model 0/1", human)
            with self.assertRaisesRegex(ValueError, "unknown fields: observed_at"):
                snapshot_report(root, identifier, snapshot=head, host_observation={"observed_at": "2026-09-20T00:00:00Z"})


if __name__ == '__main__':
    unittest.main()
