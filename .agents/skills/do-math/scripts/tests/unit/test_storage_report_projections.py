"""저장 snapshot의 timeline/CSV와 관찰 필드 거부를 실제 Repository 위에서 검사한다."""
import csv
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest

from do_math import reporting
from do_math.supervision import supervision_facts
from support.doc_code import (documents, field_schemas, scoped_field_issues,
                              status_field_schema, unowned_field_references)
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.record_builders import stored_surface_state
from support.state_builders import current_state
from support.storage_records import INSTANCE_ID, record_store


class ReportProjections(unittest.TestCase):
    def test_timezone_display_and_csv_preserve_null_and_nested_values(self):
        self.assertEqual(reporting.display_time('2026-10-01T00:00:00Z', 'Asia/Seoul'), '2026-10-01T09:00:00+09:00')
        self.assertEqual(reporting.display_time('2026-10-01T00:00:00Z', 'UTC'), '2026-10-01T00:00:00+00:00')
        self.assertIsNone(reporting.display_time(None, 'UTC'))
        with self.assertRaisesRegex(ValueError, '^timezone database has no entry for Missing/StorageZone$'):
            reporting.display_time(None, 'Missing/StorageZone')
        source = {'unit': 'internal_execution', 'id': 'EX-one', 'snapshot': None, 'usage': {'한국어': [1, 2]}}
        text = reporting.timeline_csv({'rows': [source]})
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(rows, [{'unit': 'internal_execution', 'id': 'EX-one', 'snapshot': '',
                                 'usage': json.dumps(source['usage'], ensure_ascii=False, sort_keys=True)}])
        self.assertEqual(reporting.timeline_csv({'rows': []}), 'unit,id,snapshot\r\n')

    def test_timeline_uses_stored_execution_times_and_exact_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend, clock = InProcessGit(), FakeClock()
            repo = record_store(root, backend=backend, clock=clock)
            instance, runtime = stored_surface_state()
            instance.update(id=INSTANCE_ID, workspace=str(root / 'workspace'))
            runtime['activities']['AC-1']['owner_ref'] = INSTANCE_ID
            head = repo.initialize(instance, runtime)
            stored = repo.load(head)[2]['executions']
            result = reporting.timeline(root, INSTANCE_ID, snapshot=head, timezone_name='UTC', backend=backend, clock=clock)
            self.assertEqual(result['snapshot'], head)
            self.assertEqual(result['timezone'], 'UTC')
            self.assertEqual(result['counts_by_unit'], {'internal_execution': len(stored)})
            self.assertEqual(sorted(row['id'] for row in result['rows']), sorted(stored))
            for row in result['rows']:
                execution = stored[row['id']]
                self.assertEqual(row['evidence_source'], {'kind': 'research_snapshot', 'snapshot': head})
                self.assertEqual(row['status'], execution['status'])
                for stage in ('created', 'started', 'ended'):
                    self.assertEqual(row[stage + '_at_utc'], execution.get(stage + '_at'))
            self.assertEqual(result['rows'], sorted(result['rows'], key=lambda row: (
                row['created_at_utc'] or row['started_at_utc'] or row['ended_at_utc'] or '', row['id'])))

    def test_status_refuses_unknown_observation_before_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            clock = FakeClock()
            repo = record_store(Path(directory), clock=clock)
            head = repo.initialize(*current_state({'id': INSTANCE_ID, 'workspace': str(Path(directory) / 'workspace')}))
            _, instance, runtime = repo.load(head)
            for observation in (None, {'research_observed_at': clock.now()}):
                report = reporting.status_report(repo, head, instance, runtime, observation=observation)
                self.assertEqual({name: report[name] for name in reporting.OBSERVED_FIELDS},
                                 {name: (observation or {}).get(name) for name in reporting.OBSERVED_FIELDS})
            with self.assertRaisesRegex(ValueError, '^status observation has unknown fields: storage_unknown$'):
                reporting.status_report(repo, head, instance, runtime, observation={'storage_unknown': 1})


    def test_operation_timeline_preserves_producer_trace_bytes_and_null_snapshot(self):
        import hashlib
        from do_math.operation_trace import phase, tracing

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'
            backend, clock = InProcessGit(), FakeClock()
            repo = record_store(root / 'repository', backend=backend, clock=clock)
            head = repo.initialize(*current_state({'id': INSTANCE_ID, 'workspace': str(workspace)}))
            empty = reporting.timeline(repo.repository, INSTANCE_ID, snapshot=head,
                include_operations=True, timezone_name='UTC', backend=backend, clock=clock)
            self.assertEqual(empty['rows'], [])
            self.assertEqual(empty['counts_by_unit'], {})
            with tracing(workspace / 'operations') as trace:
                self.assertIsNotNone(trace)
                with phase('storage_export'):
                    pass
            raw = trace.path.read_bytes()
            events = [json.loads(line) for line in raw.splitlines()]
            self.assertEqual([row['event'] for row in events], ['started', 'completed'])
            self.assertEqual(events[0]['span_id'], events[1]['span_id'])
            value = reporting.timeline(repo.repository, INSTANCE_ID, snapshot=head,
                include_operations=True, timezone_name='UTC', backend=backend, clock=clock)
            row, = value['rows']
            self.assertEqual(row, {
                'unit': 'operation_phase', 'id': trace.id + ':' + events[0]['span_id'],
                'operation_id': trace.id, 'span_id': events[0]['span_id'],
                'parent_span_id': events[0]['parent_span_id'],
                'parent_operation_id': events[0]['parent_operation_id'],
                'phase': 'storage_export', 'created_at_utc': events[0]['observed_at'],
                'ended_at_utc': events[1]['observed_at'], 'elapsed_ns': events[1]['elapsed_ns'],
                'trace_write_errors': 0,
                'outcome': 'completed', 'snapshot': None,
                'created_at_local': reporting.display_time(events[0]['observed_at'], 'UTC'),
                'ended_at_local': reporting.display_time(events[1]['observed_at'], 'UTC'),
                'evidence_source': {'kind': 'local_operation_file', 'path': str(trace.path),
                    'sha256': hashlib.sha256(raw).hexdigest(), 'observed_at': clock.now()}})
            self.assertIs(type(row['elapsed_ns']), int)
            self.assertIsNone(row['snapshot'])
            self.assertEqual(value['snapshot'], head)
            self.assertEqual(value['counts_by_unit'], {'operation_phase': 1})
            self.assertEqual(trace.path.read_bytes(), raw)
            self.assertTrue(trace.closed)
            self.assertIsNone(trace.stream)
            self.assertIsNone(trace.timer)
            self.assertFalse(trace.live.exists())
            csv_row, = csv.DictReader(io.StringIO(reporting.timeline_csv(value)))
            self.assertEqual(csv_row['snapshot'], '')
            self.assertEqual(json.loads(csv_row['evidence_source']), row['evidence_source'])
            historical = reporting.timeline(repo.repository, INSTANCE_ID, snapshot=head,
                include_operations=False, timezone_name='UTC', backend=backend, clock=clock)
            self.assertEqual(historical['rows'], [])
            self.assertEqual(repo.load()[0], head)

    def test_human_report_preserves_loaded_initialization_blocker_and_machine_finding(self):
        from support.record_builders import execution_state
        from support.engine_lifecycle import task_wait_report

        task_report = task_wait_report()
        task_row, = task_report['tasks']
        self.assertEqual(task_row['waits'], [{
            'kind': 'research_followup', 'target_refs': ['TK-status-wait'],
            'next_owner': 'research_plan', 'basis_ref': 'EX-review-TK-status-wait',
            'reason': 'Select the next research step'}])
        task_token = '`status.tasks[].waits`'
        self.assertEqual(scoped_field_issues(task_token, {'status': status_field_schema(task_report)}), [])
        damaged = deepcopy(task_report)
        del damaged['tasks'][0]['waits']
        self.assertEqual(scoped_field_issues(task_token, {'status': status_field_schema(damaged)}),
                         [('scoped field', 'status.tasks[].waits')])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = record_store(root)
            instance, runtime = execution_state()
            instance.update(id=INSTANCE_ID, workspace=str(root / 'workspace'))
            head = repo.initialize(instance, runtime)
            _, instance, runtime = repo.load(head)
            report = reporting.status_report(repo, head, instance, runtime,
                                              requested_areas=['start_import_input'])
            # This existing repository boundary owns the status namespace in
            # the same document population as structure.test_doc_code.
            skill = Path(__file__).resolve().parents[3]
            texts = [(document.relative_to(skill).as_posix(), document.read_text(encoding='utf-8'))
                     for document in documents(skill)]
            schemas = field_schemas()
            self.assertEqual(report['tasks'], [])
            self.assertEqual(scoped_field_issues(task_token, {'status': status_field_schema(report)}),
                             [('scoped field', 'status.tasks[].waits')])
            schemas['status'] = status_field_schema(report, task_report=task_report)
            self.assertEqual([(name, *issue) for name, text in texts
                              for issue in scoped_field_issues(text, schemas, defer_operation_progress=True,
                                                              defer_query_record=True, defer_query_result=True,
                                                              defer_continuations=('result_source', 'rejected_response', 'previous_output_files'),
                                                              defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                                                              defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                                                              defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'),
                                                              defer_cli_results=('init_result', 'scheduling_result', 'selection_result'), defer_tool_inputs=('execution_window', 'scholarly', 'formal_verifier', 'preview', 'record_map.read_tool', 'submission_contract'), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))], [])
            self.assertEqual([(name, token) for name, text in texts
                              for token in unowned_field_references(text, schemas)], [])
            self.assertEqual(scoped_field_issues('`status.operating_summary.primary_blocker` '
                '`status.budget` `status.operating_summary.supervision.configured_enabled` '
                '`status.status` `status.user_pause` `status.maintenance_fence` `status.model_policy_violation` '
                '`status.conversation_lost` `status.installation_repair` `status.operator_enabled` '
                '`status.question_links` `status.repetition_holds`', schemas), [])
            alias = '`result.config_sha256` <!-- do-math fields: result=status -->'
            self.assertEqual(scoped_field_issues(alias, schemas), [])
            for token in ('status.allowed_profiles', 'status.configured_enabled',
                          'status.user_pause.reason', 'status.installation_repair.id',
                          'status.operating_summary.primary_blocker.kind',
                          'status.operating_summary.grants[].id'):
                with self.subTest(token=token):
                    self.assertEqual(scoped_field_issues('`' + token + '`', schemas), [('scoped field', token)])
            facts = supervision_facts(instance, runtime)
            self.assertEqual({name: report[name] for name in facts}, facts)
            self.assertEqual(report['operating_summary'], reporting.operating_summary(instance, runtime))
            for name in ('operating_summary', *facts, *reporting.OBSERVED_FIELDS, 'config_sha256',
                         'question_links', 'repetition_holds'):
                with self.subTest(omitted=name):
                    omitted = dict(report)
                    del omitted[name]
                    schemas['status'] = status_field_schema(omitted)
                    token = 'status.' + name
                    self.assertEqual(scoped_field_issues('`' + token + '`', schemas), [('scoped field', token)])
                    if name in {'operating_summary', 'budget', 'config_sha256', 'question_links', 'repetition_holds'}:
                        self.assertTrue([(path, *issue) for path, text in texts
                                         for issue in scoped_field_issues(text, schemas, defer_operation_progress=True,
                                                                         defer_query_record=True, defer_query_result=True,
                                                                         defer_continuations=('result_source', 'rejected_response', 'previous_output_files'),
                                                                         defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                                                                         defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                                                                         defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'),
                                                                         defer_cli_results=('init_result', 'scheduling_result', 'selection_result'), defer_tool_inputs=('execution_window', 'scholarly', 'formal_verifier', 'preview', 'record_map.read_tool', 'submission_contract'), defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources'), defer_delivery_inputs=('submission_check', 'repair'), defer_governance=('import_payload', 'import_check', 'governance', 'academic_validation'), defer_waits=('change', 'plan_settle_wait'), defer_trust=('project', 'toolchain', 'environment_check'))])
                    if name == 'config_sha256':
                        self.assertEqual(scoped_field_issues(alias, schemas), [('scoped field', 'result.config_sha256')])
            for path in (('operating_summary', 'supervision'),
                         ('operating_summary', 'supervision', 'configured_enabled')):
                omitted = deepcopy(report)
                parent = omitted
                for name in path[:-1]:
                    parent = parent[name]
                del parent[path[-1]]
                schemas['status'] = status_field_schema(omitted)
                token = 'status.' + '.'.join(path)
                self.assertEqual(scoped_field_issues('`' + token + '`', schemas), [('scoped field', token)])
            self.assertEqual(report['inspection']['status'], 'blocked')
            self.assertEqual(report['operating_summary']['primary_blocker'],
                             {'kind': 'initialization', 'next_owner': 'operator', 'missing': []})
            rendered = reporting.render_human_report(report)
            self.assertIs(type(rendered), str)
            lines = rendered.splitlines()
            self.assertIn('blocking: initialization next=operator', lines)
            self.assertIn('  start_import_input: blocked — machine execution has no source manifest (next: maintenance)',
                          lines)
            self.assertIn('status: initializing  snapshot: ' + head, lines)
            self.assertEqual(repo.load(), (head, instance, runtime))


if __name__ == '__main__':
    unittest.main()
