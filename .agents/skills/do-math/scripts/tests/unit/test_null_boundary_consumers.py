"""Actual null producers at the query, observation and provider boundaries."""
import csv
import errno
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math import cli, reporting
from do_math.claude_stream import parse_stream, provider_limit
from do_math.core_engine import query_records
from do_math.observations import ObservationTracker, self_check_feedback
from do_math.operation_trace import tracing
from do_math.state_contract import default_state_contract, validate_record
from do_math.supervision import wake_need
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.fakes.jobs import FakeJobs
from support.observation_inputs import acknowledge, observation_rule, observe, self_check_response, write_checkpoint
from support.provider_inputs import admit, finish, report
from support.provider_state import gate_store, transact
from support.state_builders import current_state
from support.storage_records import INSTANCE_ID, record_store


class NullBoundaryTests(unittest.TestCase):
    def test_identity_free_descriptors_are_excluded_from_public_record_query(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backend, clock = InProcessGit(), FakeClock()
            store = record_store(root, backend=backend, clock=clock)
            head = store.initialize(*current_state({'id': INSTANCE_ID, 'workspace': str(root / 'work')}))
            _, _, _, rows = store.load_records(head)
            anonymous = [row for row in rows if row['id'] is None]
            self.assertEqual({row['root'] for row in anonymous if row['family'] == 'metadata'},
                             {'research', 'runtime'})
            result = query_records(root, INSTANCE_ID, snapshot=head, backend=backend, clock=clock)
            self.assertEqual({row['record']['id'] for row in result['items']},
                             {row['id'] for row in rows if row['id'] is not None})
            self.assertIsNone(result['next_cursor'])
            self.assertFalse(result['truncated'])
            page = store.query(snapshot=head, limit=1000)
            self.assertIsNone(page['next_cursor'])
            self.assertFalse(page['truncated'])
            self.assertEqual(store.load()[0], head)

    def test_unfinished_trace_has_unknown_end_and_duration_in_timeline_and_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'work'
            backend, clock = InProcessGit(), FakeClock()
            store = record_store(root / 'repository', backend=backend, clock=clock)
            head = store.initialize(*current_state({'id': INSTANCE_ID, 'workspace': str(workspace)}))
            with patch.dict('os.environ', {}, clear=True):
                with tracing(workspace / 'operations') as trace:
                    trace.emit({'span_id': 'span', 'parent_span_id': None,
                                'phase': 'unfinished', 'event': 'started'})
            raw = trace.path.read_bytes()
            value = reporting.timeline(store.repository, INSTANCE_ID, snapshot=head,
                include_operations=True, timezone_name='UTC', backend=backend, clock=clock)
            row, = value['rows']
            for name in ('parent_operation_id', 'parent_span_id', 'ended_at_utc',
                         'ended_at_local', 'elapsed_ns', 'snapshot'):
                self.assertIn(name, row)
                self.assertIsNone(row[name])
            self.assertNotIn('outcome', row)
            self.assertEqual(row['created_at_utc'], json.loads(raw)['observed_at'])
            rendered, = csv.DictReader(io.StringIO(reporting.timeline_csv(value)))
            self.assertEqual((rendered['ended_at_utc'], rendered['elapsed_ns'], rendered['snapshot']), ('', '', ''))
            self.assertEqual(trace.path.read_bytes(), raw)
            self.assertEqual(store.load()[0], head)

    def test_no_window_and_malformed_response_preserve_distinct_null_meanings(self):
        with tempfile.TemporaryDirectory() as directory:
            root, clock = Path(directory), FakeClock()
            tracker = ObservationTracker('EX-null', root, {'observation_mode': 'event_driven',
                'research_self_checks': True, 'observation_rules': [observation_rule()]}, time_port=clock)
            write_checkpoint(root, counters={'attempts': 2})
            observe(tracker, {'type': 'tick'})
            oid, = tracker.obligations
            obligation = tracker.obligations[oid]
            self.assertIsNone(obligation['deadline_offset_ms'])
            self.assertIsNone(obligation['due'][0]['next_boundary'])
            self.assertIsNone(self_check_feedback(obligation)['deadline_offset_ms'])
            acknowledge(tracker, oid)
            clock.advance(10000)
            observe(tracker, {'type': 'tick'})
            self.assertEqual(obligation['status'], 'open')
            self.assertNotIn('missed_reason', obligation)
            accepted = tracker.record_self_check_response(self_check_response(obligation),
                                                          available_evidence_refs={'EV-1'})
            self.assertEqual(accepted['kind'], 'self_check_received')
            self.assertIsNone(accepted['receipt_ref'])
            self.assertIsNone(accepted['next_self_check_offset_ms'])
            self.assertEqual(accepted['followup'], {'kind': 'continue', 'next_owner': 'engine'})
            rejected = tracker.record_self_check_response(None)
            self.assertEqual(rejected['errors'], ['invalid_response_schema', 'unknown_obligation'])
            self.assertIsNone(rejected['obligation_id'])
            self.assertIsNone(rejected['worker_feedback']['obligation_id'])
            self.assertEqual(rejected['response_json'], 'null')
            self.assertEqual(rejected['followup']['basis_refs'], [rejected['id']])
            self.assertEqual(obligation['response_ref'], accepted['id'])
            contract = default_state_contract()
            for record in (accepted, rejected):
                validate_record(contract.family('runtime', 'self_check_responses').checker, record, 'self_check_responses')
            self.assertEqual(tracker.stored_obligations()[oid]['deadline_offset_ms'], None)

    def test_native_limit_without_timestamp_or_artifact_survives_gate_projection(self):
        raw = b'{"type":"rate_limit_event","rate_limit_info":{"status":"rejected"}}\n'
        failure = provider_limit(parse_stream(raw))
        self.assertIsNone(failure['retry_at'])
        self.assertEqual(failure['limit_windows'], [{'type': None, 'resetsAt': None}])
        self.assertNotIn('evidence_ref', failure)
        with tempfile.TemporaryDirectory() as directory:
            clock, backend, jobs = FakeClock(), InProcessGit(), FakeJobs()
            store = gate_store(Path(directory), clock=clock, backend=backend)
            def limited(slots, instance, runtime):
                self.assertTrue(admit(slots, instance, runtime, 'EX-limit', current=100))
                self.assertIsNone(runtime['executions']['EX-limit']['capacity']['process'])
                result = report(slots, instance, 'EX-limit', 100, failure)
                finish(slots, runtime, 'EX-limit', 100)
                return result
            gate = transact(store, limited, clock=clock, jobs=jobs)
            self.assertIsNone(gate['evidence']['evidence_ref'])
            self.assertEqual(json.loads(gate['evidence']['reported_fields_json']), failure)
            self.assertIsNone(gate['probe_owner'])
            self.assertIsNone(gate['probe_started_at'])
            self.assertFalse(gate['open'])
            self.assertEqual(gate['retry_at'], '1970-01-01T00:06:40+00:00')
            stored = store.load()[2]['provider_waits']['PW-claude']
            self.assertIsNone(stored['evidence']['evidence_ref'])
            self.assertEqual(stored['retry_at'], 400)
            self.assertEqual(wake_need({'status': 'ready', 'operator_enabled': True},
                {'claude': gate}, held=False), {'wanted': {'key': 'claude:1', 'retry_at': gate['retry_at']}})
            def recovered(slots, instance, runtime):
                self.assertTrue(admit(slots, instance, runtime, 'EX-probe', current=400))
                result = report(slots, instance, 'EX-probe', 401)
                finish(slots, runtime, 'EX-probe', 401)
                return result
            available = transact(store, recovered, clock=clock, jobs=jobs)
            self.assertTrue(available['open'])
            self.assertEqual(available['state'], 'available')
            for key in ('retry_at', 'probe_owner', 'probe_started_at'):
                self.assertIsNone(available[key])
            self.assertEqual(wake_need({'status': 'ready', 'operator_enabled': True},
                {'claude': available}, held=False), {'status': 'not_needed'})

    def test_console_discovery_failure_reports_null_reconciliation_command(self):
        with tempfile.TemporaryDirectory() as directory:
            interpreter = Path(directory) / 'pythonw.exe'
            interpreter.touch()
            console = interpreter.with_name('python.exe')
            self.assertFalse(console.exists())
            with patch('sys.executable', str(interpreter)):
                result, code = cli._schedule_failure({'instance_id': INSTANCE_ID},
                    RuntimeError('scheduler unavailable'), Path('.'), INSTANCE_ID)
        self.assertEqual(result['operator_schedule'], {'status': 'failed', 'error': 'scheduler unavailable',
            'reconcile': None, 'reconcile_error': str(FileNotFoundError(
                errno.ENOENT, 'console Python sibling is not a file', str(console)))})
        self.assertEqual(code, cli.ERROR_EXIT_CODES['tool_error'])
        self.assertIn('"reconcile": null', json.dumps(result))
