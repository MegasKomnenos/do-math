"""첫 full 측정에서 비어 있던 수집 판정과 스트림 음성 분기의 결과를 고정한다."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math.claude_stream import parse_stream, provider_limit
from do_math.codex_stream import parse_jsonl
from do_math.cli_execution import collection_reasons, decode_status, checked_start_paths
from do_math.provider_final import EXECUTABLE_KEYS, request_provider, final_mismatch
from do_math.provider_wait import epoch_seconds, utc
from do_math.worker_request import STATUS_BINDING_KEYS
from support.fakes.clock import FakeClock
from support.provider_close_inputs import request_seed
from support.provider_runs import ProviderJobs, CLAUDE_INIT, claude_result


class CollectorGapTests(unittest.TestCase):

    def test_all_binding_fields_report_only_their_own_mismatch(self):
        request = {'execution_id': 'EX-one', 'profile_ref': {'id': 'EP-one', 'revision': 1, 'sha256': 'a' * 64}}
        status = {**deepcopy(request), 'state': 'exited', 'cli_exit_code': 0,
                  'stdin_sha256': 'prompt', 'request_sha256': 'request', 'schema_sha256': 'schema'}
        parsed = {'turn_failed': False, 'turn_completed': True, 'parse_complete': True, 'final_text': '{}'}
        for key in STATUS_BINDING_KEYS:
            for missing in (False, True):
                with self.subTest(key=key, missing=missing):
                    changed = deepcopy(status)
                    if missing:
                        del changed[key]
                    else:
                        changed[key] = 'different'
                    self.assertEqual(collection_reasons(changed, parsed, b'{}', request,
                        prompt_sha256='prompt', request_sha256='request', schema_sha256='schema',
                        final_check=final_mismatch), ['worker_' + key + '_mismatch'])
        self.assertEqual(collection_reasons(status, parsed, b'{}', request,
            prompt_sha256='prompt', request_sha256='request', schema_sha256='schema',
            final_check=final_mismatch), [])

    def test_invalid_status_bytes_and_provider_cardinality(self):
        for raw in (b'{', b'\xff'):
            self.assertEqual(decode_status(raw), {'state': 'invalid_status_json'})
        self.assertIsNone(decode_status(None))
        for request in ({}, {key: 'cli' for key in EXECUTABLE_KEYS.values()}):
            with self.assertRaisesRegex(ValueError, '^worker request names no single provider executable$'):
                request_provider(request)
        for provider, key in EXECUTABLE_KEYS.items():
            self.assertEqual(request_provider({key: 'cli'}), provider)

    def test_start_paths_reject_duplicate_existing_and_in_workspace_outputs(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        seed = request_seed('codex', root, jobs=ProviderJobs(), clock=FakeClock())
        cli = seed['codex_path']
        request_path = root / 'request.json'
        before = deepcopy(seed)
        with self.assertRaisesRegex(ValueError, '^request CLI executable differs from adapter executable$'):
            checked_start_paths({**seed, 'codex_path': str(root / 'different-codex.exe')}, request_path,
                                cli_path=cli, executable_key='codex_path')
        self.assertEqual(seed, before)
        with self.assertRaisesRegex(ValueError, '^request, prompt, and output paths must be distinct$'):
            checked_start_paths({**seed, 'stdout_path': seed['prompt_path']}, request_path,
                                cli_path=cli, executable_key='codex_path')
        with self.assertRaisesRegex(ValueError, '^worker outputs and status must be outside the model workspace$'):
            checked_start_paths({**seed, 'stdout_path': str(root / 'workspace/stdout')}, request_path,
                                cli_path=cli, executable_key='codex_path')
        existing = root / 'existing'
        existing.write_bytes(b'prior')
        with self.assertRaisesRegex(FileExistsError, '^output paths must be newly allocated$'):
            checked_start_paths({**seed, 'stdout_path': str(existing)}, request_path,
                                cli_path=cli, executable_key='codex_path')
        self.assertEqual(existing.read_bytes(), b'prior')

    def test_codex_unknown_shape_and_type_keep_exact_byte_coordinates(self):
        prefix = b'{"type":"thread.started","thread_id":"one"}\n{"type":"turn.started"}\n'
        tail = b'{"type":"turn.completed"}\n'
        for value in (None, [], 0, 'x', True):
            row = json.dumps(value).encode() + b'\n'
            parsed = parse_jsonl(prefix + row + tail)
            self.assertEqual(parsed['unknown_events'], [{'kind': 'unknown_jsonl_event', 'offset': len(prefix)}])
            self.assertEqual(parsed['parsed_bytes'], len(prefix + row + tail))
            self.assertFalse(parsed['parse_complete'])
        row = b'{"type":"alien"}\n'
        parsed = parse_jsonl(prefix + row + tail)
        self.assertEqual(parsed['unknown_events'], [
            {'kind': 'unknown_event_type', 'offset': len(prefix), 'length': len(row), 'type': 'alien'},
            {'kind': 'invalid_event_between_turn_start_and_terminal'}])

    def test_claude_missing_incomplete_and_invalid_bytes_have_distinct_reasons(self):
        self.assertEqual(parse_stream(None)['unknown_events'], ['stdout_missing'])
        for raw, reason in ((b'{}', 'incomplete_jsonl_line'), (b'null\n', 'invalid_jsonl'), (b'\xff\n', 'invalid_jsonl')):
            parsed = parse_stream(raw)
            self.assertEqual(parsed['unknown_events'], [reason, 'invalid_session_start', 'terminal_missing'])
            self.assertEqual((parsed['parsed_bytes'], parsed['unparsed_tail_bytes']), (0, len(raw)))
            self.assertFalse(parsed['turn_completed'])
        raw = b'\n' + b''.join(json.dumps(event).encode() + b'\n' for event in
            (CLAUDE_INIT, CLAUDE_INIT, claude_result(b'{}')))
        self.assertEqual(parse_stream(raw)['unknown_events'], ['unfinished_segment'])

    def test_unrepresentable_rate_limit_epoch_preserves_evidence_without_retry_date(self):
        info = {'status': 'rejected', 'rateLimitType': 'five_hour', 'resetsAt': 1e100}
        failure = provider_limit({'rate_limits': [{'line': 7, 'info': info}]})
        self.assertEqual(failure, {'kind': 'provider_limit', 'provider': 'claude', 'retry_at': None,
            'limit_windows': [{'type': 'five_hour', 'resetsAt': 1e100}], 'evidence_line': 7, 'native_info': info})
        for value in ('not-a-date', '2026-01-01T00:00:00', None, True, [], float('inf')):
            self.assertIsNone(epoch_seconds(value))
        self.assertEqual(epoch_seconds('1970-01-01T00:00:01Z'), 1.0)
        self.assertEqual(utc(1), '1970-01-01T00:00:01+00:00')
        self.assertIsNone(utc(None))
