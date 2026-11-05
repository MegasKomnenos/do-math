import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retention import capture, conversation
from runtime_support import archive_work


class ArchiveTests(unittest.TestCase):
    def test_transient_directory_scan_failure_keeps_unarchived_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            nested = session / 'work/nested'
            nested.mkdir(parents=True)
            notes = nested / 'notes.md'
            payload = b'Mathematics that must survive a failed directory scan'
            notes.write_bytes(payload)
            original_scandir = os.scandir
            failed = False

            def scan(path):
                nonlocal failed
                if path == str(nested) and not failed:
                    failed = True
                    raise PermissionError('temporary directory scan failure')
                return original_scandir(path)

            with patch('runtime_support.os.scandir', side_effect=scan):
                with self.assertRaisesRegex(PermissionError, 'temporary directory scan failure'):
                    archive_work(session)
            self.assertTrue(failed)
            self.assertEqual(notes.read_bytes(), payload)
            self.assertFalse((session / 'work.tar.xz').exists())
            self.assertFalse((session / 'work.tar.xz.part').exists())

    def test_archived_work_preserves_bytes_and_directories_before_removing_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            work = session / 'work'
            (work / 'empty').mkdir(parents=True)
            (work / '자료').mkdir()
            payload = bytes(range(256)) * 300
            (work / '자료/calculation.bin').write_bytes(payload)
            (session / 'output').mkdir()
            (session / 'output/report.md').write_bytes(b'Retained report')
            self.assertTrue(archive_work(session))
            self.assertFalse(work.exists())
            with tarfile.open(session / 'work.tar.xz', 'r:xz') as archive:
                self.assertTrue(archive.getmember('work/empty').isdir())
                self.assertEqual(archive.extractfile('work/자료/calculation.bin').read(), payload)
            self.assertEqual((session / 'output/report.md').read_bytes(), b'Retained report')
            saved = (session / 'work.tar.xz').read_bytes()
            self.assertFalse(archive_work(session))
            self.assertEqual((session / 'work.tar.xz').read_bytes(), saved)

    def test_existing_archive_mismatch_keeps_both_archive_and_remaining_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            work = session / 'work'
            work.mkdir()
            (work / 'notes.md').write_bytes(b'Original mathematics')
            self.assertTrue(archive_work(session))
            saved = (session / 'work.tar.xz').read_bytes()
            work.mkdir()
            (work / 'notes.md').write_bytes(b'Work absent from the existing archive')
            with self.assertRaisesRegex(RuntimeError, 'does not match'):
                archive_work(session)
            self.assertEqual((work / 'notes.md').read_bytes(), b'Work absent from the existing archive')
            self.assertEqual((session / 'work.tar.xz').read_bytes(), saved)


class RetentionTests(unittest.TestCase):
    def test_native_reasoning_preserves_readable_content_with_and_without_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [
                {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [],
                 'content': [{'type': 'reasoning_text', 'text': 'An argument without a summary.'}]}},
                {'type': 'response_item', 'payload': {'type': 'reasoning',
                 'summary': [{'type': 'summary_text', 'text': 'A short summary.'}],
                 'content': [{'type': 'reasoning_text', 'text': 'The necessary hypothesis absent from that summary.'}],
                 'encrypted_content': 'OPAQUE_TRANSPORT'}},
                {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [],
                 'encrypted_content': 'OPAQUE_ONLY'}},
            ]
            source = root / 'native.jsonl'
            raw = ('\n'.join(json.dumps(row) for row in rows) + '\n').encode('utf-8')
            source.write_bytes(raw)
            destination = root / 'conversation.md'
            self.assertEqual(conversation(source, destination, True), 2)
            body = destination.read_text(encoding='utf-8')
            self.assertIn('An argument without a summary.', body)
            self.assertIn('A short summary.', body)
            self.assertIn('The necessary hypothesis absent from that summary.', body)
            self.assertNotIn('OPAQUE_TRANSPORT', body)
            self.assertNotIn('OPAQUE_ONLY', body)
            self.assertEqual(source.read_bytes(), raw)

    def test_native_messages_and_tool_output_are_not_truncated_or_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            middle = 'begin\n' + ('a' * 4000) + 'THE DECISIVE MIDDLE' + ('z' * 4000) + '\nend'
            rows = [
                {'type': 'event_msg', 'payload': {'type': 'agent_message', 'message': 'Duplicated transport event'}},
                {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant', 'content': [{'type': 'output_text', 'text': 'The mathematical account.'}]}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'name': 'exec', 'input': 'print(1 + 1)'}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'output': middle}},
                {'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': [], 'encrypted_content': 'OPAQUE_TRANSPORT'}},
            ]
            source = root / 'native.jsonl'
            source.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
            target = root / 'conversation.md'
            self.assertEqual(conversation(source, target, True), 3)
            result = target.read_text(encoding='utf-8')
            self.assertIn(middle, result)
            self.assertIn('The mathematical account.', result)
            self.assertIn('print(1 + 1)', result)
            self.assertNotIn('Duplicated transport event', result)
            self.assertNotIn('OPAQUE_TRANSPORT', result)

    def test_malformed_native_payload_does_not_hide_later_messages_and_tool_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [{'type': 'response_item', 'payload': value}
                    for value in (None, [], 'invalid', 42)]
            rows += [
                {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                 'content': [{'type': 'output_text', 'text': 'A recoverable mathematical result.'}]}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output',
                 'output': 'The calculation supporting the result.'}},
            ]
            source = root / 'native.jsonl'
            raw = ('\n'.join(json.dumps(row) for row in rows) + '\n').encode('utf-8')
            source.write_bytes(raw)
            target = root / 'conversation.md'
            self.assertEqual(conversation(source, target, True), 2)
            body = target.read_text(encoding='utf-8')
            self.assertIn('A recoverable mathematical result.', body)
            self.assertIn('The calculation supporting the result.', body)
            self.assertEqual(source.read_bytes(), raw)

    def test_capture_finds_native_transcripts_and_prefers_them_to_cli_text(self):
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        message = 'The original argument uses ℕ, including zero.'
        tool_output = 'begin\n' + 'a' * 4000 + 'DECISIVE MIDDLE' + 'z' * 4000 + '\nend'
        for provider in ('codex', 'claude'):
            for configured in (False, True):
                with self.subTest(provider=provider, configured=configured), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    profile = root / 'profile'
                    session = root / 'session'
                    session.mkdir()
                    storage = root / 'configured' if configured else profile / ('.codex' if provider == 'codex' else '.claude')
                    if provider == 'codex':
                        native = storage / 'sessions/2026/11/05' / ('rollout-' + identity + '.jsonl')
                        announcement = {'type': 'thread.started', 'thread_id': identity}
                        rows = [
                            {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                             'content': [{'type': 'output_text', 'text': message}]}},
                            {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'output': tool_output}},
                        ]
                        stream_item = {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'TRANSPORT_ONLY'}}
                    else:
                        native = storage / 'projects/project' / (identity + '.jsonl')
                        announcement = {'type': 'system', 'session_id': identity}
                        rows = [
                            {'type': 'assistant', 'message': {'role': 'assistant',
                             'content': [{'type': 'text', 'text': message}]}},
                            {'type': 'user', 'message': {'role': 'user',
                             'content': [{'type': 'tool_result', 'tool_use_id': 'call1', 'content': tool_output}]}},
                        ]
                        stream_item = {'type': 'assistant', 'message': {'content': 'TRANSPORT_ONLY'}}
                    native.parent.mkdir(parents=True)
                    raw = ('\n'.join(json.dumps(row, ensure_ascii=False) for row in rows) + '\n').encode('utf-8')
                    native.write_bytes(raw)
                    (session / 'cli.stdout.jsonl').write_text(
                        '\n'.join(json.dumps(row) for row in (announcement, stream_item)), encoding='utf-8')
                    (session / 'cli.stderr.log').write_text('', encoding='utf-8')
                    environment = {('CODEX_HOME' if provider == 'codex' else 'CLAUDE_CONFIG_DIR'): str(storage)} if configured else {}
                    with patch.dict(os.environ, environment, clear=True), patch('retention.Path.home', return_value=profile):
                        receipt = capture(session, provider)
                    copied = 'transcript-' + identity + '.jsonl'
                    self.assertEqual(receipt['native_transcripts'], [copied])
                    self.assertEqual((session / copied).read_bytes(), raw)
                    self.assertTrue(receipt['cli_activity'])
                    self.assertIsNone(receipt['limitation'])
                    self.assertEqual(receipt['conversation_items'], 2)
                    body = (session / receipt['conversation']).read_text(encoding='utf-8')
                    self.assertIn(message, body)
                    self.assertIn(tool_output, body)
                    self.assertNotIn('TRANSPORT_ONLY', body)

    def test_capture_retains_cli_text_when_the_identified_native_log_is_missing(self):
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        for provider in ('codex', 'claude'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                announcement = ({'type': 'thread.started', 'thread_id': identity} if provider == 'codex'
                                else {'type': 'system', 'session_id': identity})
                item = ({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Available CLI material.'}}
                        if provider == 'codex' else {'type': 'assistant', 'message': {'content': 'Available CLI material.'}})
                (root / 'cli.stdout.jsonl').write_text(
                    '\n'.join(json.dumps(row) for row in (announcement, item)), encoding='utf-8')
                (root / 'cli.stderr.log').write_text('', encoding='utf-8')
                with patch.dict(os.environ, {}, clear=True), patch('retention.Path.home', return_value=root / 'empty-profile'):
                    receipt = capture(root, provider)
                self.assertEqual(receipt['native_transcripts'], [])
                self.assertTrue(receipt['limitation'])
                self.assertEqual(receipt['streams'], ['cli.stdout.jsonl', 'cli.stderr.log'])
                self.assertEqual(receipt['conversation_items'], 1)
                self.assertIn('Available CLI material.', (root / receipt['conversation']).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
