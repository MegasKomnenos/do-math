import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retention import capture, conversation, output_limit, refusal
from runtime_support import archive_raw, archive_work


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

    def test_existing_archive_finishes_an_interrupted_removal_and_keeps_mismatched_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            work = session / 'work'
            (work / 'nested').mkdir(parents=True)
            (work / 'notes.md').write_bytes(b'Original mathematics')
            (work / 'nested/table.csv').write_bytes(b'n,value')
            self.assertTrue(archive_work(session))
            saved = (session / 'work.tar.xz').read_bytes()
            # A removal interrupted partway leaves part of work/, all of it already in the archive.
            (work / 'nested').mkdir(parents=True)
            (work / 'nested/table.csv').write_bytes(b'n,value')
            self.assertTrue(archive_work(session))
            self.assertFalse(work.exists())
            self.assertEqual((session / 'work.tar.xz').read_bytes(), saved)
            work.mkdir()
            (work / 'notes.md').write_bytes(b'Work absent from the existing archive')
            with self.assertRaisesRegex(RuntimeError, 'does not match'):
                archive_work(session)
            self.assertEqual((work / 'notes.md').read_bytes(), b'Work absent from the existing archive')
            self.assertEqual((session / 'work.tar.xz').read_bytes(), saved)

    def test_work_that_changed_while_it_was_archived_is_kept_and_no_archive_is_left(self):
        # Where a session was not contained, a computation it left behind can still write into work/ while
        # the archiver reads it (reference/operations.md, Commands). The archive then holds other bytes than
        # the scan of work/ recorded, so nothing is removed and no archive is left to stand for work/; the
        # next pass archives work/ as it then is. Only the moment of that write is arranged, between the
        # scan and the writing of the archive; the archive is written and read back as in operation.
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            notes = session / 'work/notes.md'
            notes.parent.mkdir()
            notes.write_bytes(b'Mathematics as the scan read it')
            opened = tarfile.open

            def written_meanwhile(name, mode='r', **options):
                if mode.startswith('w'):
                    notes.write_bytes(b'Mathematics written after the scan')
                return opened(name, mode, **options)

            with patch('runtime_support.tarfile.open', side_effect=written_meanwhile):
                with self.assertRaisesRegex(RuntimeError, 'does not match'):
                    archive_work(session)
            self.assertEqual(notes.read_bytes(), b'Mathematics written after the scan')
            self.assertFalse((session / 'work.tar.xz').exists())
            self.assertFalse((session / 'work.tar.xz.part').exists())
            self.assertTrue(archive_work(session))
            with tarfile.open(session / 'work.tar.xz', 'r:xz') as archive:
                self.assertEqual(archive.extractfile('work/notes.md').read(), b'Mathematics written after the scan')

    def test_read_only_work_files_are_removed_once_archived(self):
        # Git creates its object files read-only, and Windows refuses to delete a read-only file;
        # a session that used Git in work/ must still have that work replaced by its archive.
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            stored = session / 'work/repo/.git/objects/ab/cdef'
            stored.parent.mkdir(parents=True)
            stored.write_bytes(b'A Git object')
            os.chmod(stored, stat.S_IREAD)
            self.assertTrue(archive_work(session))
            self.assertFalse((session / 'work').exists())
            with tarfile.open(session / 'work.tar.xz', 'r:xz') as archive:
                self.assertEqual(archive.extractfile('work/repo/.git/objects/ab/cdef').read(), b'A Git object')

    def test_work_that_holds_one_file_under_two_names_is_archived_under_both(self):
        # A hard link gives one file a second name, as Git does for the object files of a repository that it
        # clones from a folder of the same disk. The scan of work/ reads the content under each name, so the
        # archive has to hold a file under each name as well. The link, the archive and the read-back are real.
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            first = session / 'work/clone/table.csv'
            first.parent.mkdir(parents=True)
            first.write_bytes(b'n,value\n1,1\n')
            (session / 'work/origin').mkdir()
            try:
                os.link(first, session / 'work/origin/table.csv')
            except OSError:
                self.skipTest('this file system gives a file no second name')
            self.assertTrue(archive_work(session))
            self.assertFalse((session / 'work').exists())
            with tarfile.open(session / 'work.tar.xz', 'r:xz') as archive:
                for name in ('work/clone/table.csv', 'work/origin/table.csv'):
                    self.assertTrue(archive.getmember(name).isfile(), name)
                    self.assertEqual(archive.extractfile(name).read(), b'n,value\n1,1\n', name)

    def test_linked_work_is_refused_and_left_in_place(self):
        # A link leads outside the session. Archiving through it and then removing work/ would
        # record or remove files the session does not own, so both forms of link are refused.
        def link(path, target):
            try:
                os.symlink(target, path, target_is_directory=True)
            except OSError:
                if os.name != 'nt':
                    raise
                # Without the symlink privilege, a junction is the directory link Windows allows.
                subprocess.run(['cmd', '/c', 'mklink', '/J', str(path), str(target)],
                               check=True, capture_output=True)
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / 'outside'
            outside.mkdir()
            (outside / 'shared.md').write_bytes(b'Mathematics outside the session')
            inner = Path(tmp) / 'inner'
            (inner / 'work').mkdir(parents=True)
            (inner / 'work/notes.md').write_bytes(b'Original mathematics')
            link(inner / 'work/linked', outside)
            whole = Path(tmp) / 'whole'
            whole.mkdir()
            link(whole / 'work', outside)
            for session, message in ((inner, 'contains a link'), (whole, 'inside its session directory')):
                with self.subTest(message=message):
                    with self.assertRaisesRegex(ValueError, message):
                        archive_work(session)
                    self.assertFalse((session / 'work.tar.xz').exists())
                    self.assertFalse((session / 'work.tar.xz.part').exists())
            self.assertEqual((inner / 'work/notes.md').read_bytes(), b'Original mathematics')
            self.assertEqual((outside / 'shared.md').read_bytes(), b'Mathematics outside the session')

    def test_the_raw_conversation_is_replaced_by_its_archive_and_everything_else_stays(self):
        # The raw conversation is the CLI stream of each turn and the copied transcript file. What a reader
        # opens first stays in the folder: the readable conversation, the receipt that names the raw files,
        # the folder the readable conversation points into, and whatever else a turn left.
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        raw = {'cli.stdout.jsonl': b'{"type": "assistant"}\n' * 400,
               'turns/0001/cli.stdout.jsonl': 'A resumed turn about ℕ.\n'.encode('utf-8'),
               'transcript-' + identity + '.jsonl': bytes(range(256)) * 300}
        kept = {'cli.stderr.log': b'', 'turns/0001/prompt.txt': b'Resume.',
                'conversation.md': b'# Retained conversation\n', 'retention.json': b'{}',
                'transcript-' + identity + '/subagents/agent-a1.jsonl': b'{"type": "assistant"}\n',
                'output/report.md': b'Retained report'}
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)
            for name, content in {**raw, **kept}.items():
                (session / name).parent.mkdir(parents=True, exist_ok=True)
                (session / name).write_bytes(content)
            self.assertTrue(archive_raw(session))
            for name in raw:
                self.assertFalse((session / name).exists(), name)
            for name, content in kept.items():
                self.assertEqual((session / name).read_bytes(), content, name)
            with tarfile.open(session / 'raw.tar.xz', 'r:xz') as archive:
                self.assertEqual(sorted(archive.getnames()), sorted(raw))
                for name, content in raw.items():
                    self.assertEqual(archive.extractfile(name).read(), content, name)
            self.assertFalse((session / 'raw.tar.xz.part').exists())
            saved = (session / 'raw.tar.xz').read_bytes()
            self.assertFalse(archive_raw(session))
            # A removal interrupted partway leaves a raw file that the archive already holds.
            (session / 'cli.stdout.jsonl').write_bytes(raw['cli.stdout.jsonl'])
            self.assertTrue(archive_raw(session))
            self.assertFalse((session / 'cli.stdout.jsonl').exists())
            # A raw file that the archive does not hold as it stands is kept, and so is the archive.
            (session / 'cli.stdout.jsonl').write_bytes(b'A stream that the archive does not hold')
            with self.assertRaisesRegex(RuntimeError, 'does not match'):
                archive_raw(session)
            self.assertEqual((session / 'cli.stdout.jsonl').read_bytes(), b'A stream that the archive does not hold')
            self.assertEqual((session / 'raw.tar.xz').read_bytes(), saved)


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
                # The summary that took the place of the conversation at a compaction is an item of the record.
                {'type': 'compacted', 'payload': {'message': 'Summary of the conversation so far: the bound holds for every n up to 7.'}},
            ]
            source = root / 'native.jsonl'
            source.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
            target = root / 'conversation.md'
            self.assertEqual(conversation(source, target, True), 4)
            result = target.read_text(encoding='utf-8')
            self.assertIn(middle, result)
            self.assertIn('The mathematical account.', result)
            self.assertIn('print(1 + 1)', result)
            self.assertIn('Summary of the conversation so far: the bound holds for every n up to 7.', result)
            self.assertNotIn('Duplicated transport event', result)
            self.assertNotIn('OPAQUE_TRANSPORT', result)

    def test_what_a_claude_session_read_of_its_own_pack_is_left_out_of_the_readable_conversation(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Path(tmp)

            def read(call, path, returned):
                return [{'type': 'assistant', 'message': {'role': 'assistant', 'content': [
                            {'type': 'tool_use', 'id': call, 'name': 'Read',
                             'input': {'file_path': str(path), 'offset': 501}}]}},
                        {'type': 'user', 'message': {'role': 'user', 'content': [
                            {'type': 'tool_result', 'tool_use_id': call, 'content': returned}]}}]
            rows = (read('call1', session / 'pack.md', '501\tTHE GUIDES OF THE PACK')
                    + read('call2', session / 'output/report.md', '501\tThe bound holds for every n up to 7.'))
            source = session / 'transcript.jsonl'
            source.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            self.assertEqual(conversation(source, session / 'conversation.md', True), 4)
            body = (session / 'conversation.md').read_text(encoding='utf-8')
            # The call stays, with the file and the range it read; what it returned of the pack stands beside
            # the conversation as pack.md. What a call returned of any other file is retained.
            self.assertIn('file_path:\n' + str(session / 'pack.md') + '\noffset:\n501', body)
            self.assertNotIn('THE GUIDES OF THE PACK', body)
            self.assertIn('The bound holds for every n up to 7.', body)

    def test_the_pack_that_a_first_prompt_carries_is_left_out_of_the_readable_conversation(self):
        # The first prompt of a session carries its pack below a few opening lines (context.assemble), and pack.md
        # beside the conversation holds the same text. The first form is the one in which the Claude CLI records
        # a prompt, a string with every character it was given. The second is a list of text blocks, from a CLI
        # that drops the newline at the end of a prompt.
        pack = '# Your do-math session\n\nTHE GUIDES OF THE PACK\n\n# Executable commands\n'
        opening = 'You are a do-math attempt session.\n\n'
        prompts = {'string': {'type': 'user', 'message': {'role': 'user', 'content': opening + pack}},
                   'blocks': {'type': 'response_item', 'payload': {'type': 'message', 'role': 'user', 'content': [
                       {'type': 'input_text', 'text': opening + pack.rstrip('\n')}]}}}
        # A message that quotes a part of the pack is retained as it is.
        quoting = {'type': 'assistant', 'message': {'role': 'assistant', 'content': [
            {'type': 'text', 'text': 'My pack ends with the heading "# Executable commands".'}]}}
        for form, prompt in prompts.items():
            with self.subTest(form=form), tempfile.TemporaryDirectory() as tmp:
                session = Path(tmp)
                (session / 'pack.md').write_bytes(pack.encode('utf-8'))
                source = session / 'transcript.jsonl'
                source.write_text('\n'.join(json.dumps(row) for row in (prompt, quoting)), encoding='utf-8')
                self.assertEqual(conversation(source, session / 'conversation.md', True), 2)
                body = (session / 'conversation.md').read_text(encoding='utf-8')
                # The opening lines stay, and a line that names pack.md stands where the pack stood.
                self.assertIn(opening + 'Left out here: the whole text of pack.md, which stands in this folder.', body)
                self.assertNotIn('THE GUIDES OF THE PACK', body)
                self.assertIn('My pack ends with the heading "# Executable commands".', body)

    def test_malformed_native_payload_does_not_hide_later_messages_and_tool_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = [{'type': 'response_item', 'payload': value}
                    for value in (None, [], 'invalid', 42)]
            rows += [
                # Half of a surrogate pair, as a text cut between the two halves leaves it. json.dumps writes it as
                # the escape \ud835, and the line parses to a character that UTF-8 does not encode.
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output',
                 'output': 'A goal cut after half of a character: \ud835'}},
                {'type': 'response_item', 'payload': {'type': 'message', 'role': 'assistant',
                 'content': [{'type': 'output_text', 'text': 'A recoverable mathematical result.'}]}},
                {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output',
                 'output': 'The calculation supporting the result.'}},
            ]
            source = root / 'native.jsonl'
            raw = ('\n'.join(json.dumps(row) for row in rows) + '\n').encode('utf-8')
            source.write_bytes(raw)
            target = root / 'conversation.md'
            self.assertEqual(conversation(source, target, True), 3)
            body = target.read_text(encoding='utf-8')
            # The half is retained as the escape it arrived as, and what follows it is retained whole.
            self.assertIn('A goal cut after half of a character: \\ud835', body)
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
                        # The report of a delegated agent that finished while the session was at work in a turn, and
                        # a message that the session's hook handed it. The CLI records each as an attachment and as
                        # no message. Beside the message it records what the hook printed, which holds the same text
                        # once more; that and an attachment of any other type are records of the CLI's own.
                        report = 'The delegated check found no counterexample for n up to 9.'
                        handed = 'Message from the operator of this research:\nThe bound is wanted for odd n as well.'
                        rows = [
                            {'type': 'assistant', 'message': {'model': 'claude-model', 'role': 'assistant',
                             'content': [{'type': 'text', 'text': message}], 'stop_reason': 'end_turn',
                             'usage': {'input_tokens': 2, 'cache_read_input_tokens': 861766}}},
                            {'type': 'user', 'message': {'role': 'user',
                             'content': [{'type': 'tool_result', 'tool_use_id': 'call1', 'content': tool_output}]}},
                            {'type': 'attachment', 'attachment': {
                                'type': 'queued_command', 'commandMode': 'task-notification',
                                'prompt': '<task-notification>\n<result>' + report + '</result>\n</task-notification>'}},
                            {'type': 'attachment', 'attachment': {
                                'type': 'hook_success', 'hookEvent': 'PostToolBatch', 'stdout': 'HOOK_OUTPUT_ONLY'}},
                            {'type': 'attachment', 'attachment': {
                                'type': 'hook_additional_context', 'hookEvent': 'PostToolBatch', 'content': [handed]}},
                            {'type': 'attachment', 'attachment': {'type': 'deferred_tools_record',
                                                                  'entries': ['CLI_RECORD_ONLY']}},
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
                    self.assertEqual(receipt['conversation_items'], 4 if provider == 'claude' else 2)
                    body = (session / receipt['conversation']).read_text(encoding='utf-8')
                    self.assertIn(message, body)
                    self.assertIn(tool_output, body)
                    self.assertNotIn('TRANSPORT_ONLY', body)
                    if provider == 'claude':
                        # The API's account of the call stays in the copied transcript, out of the readable text.
                        self.assertNotIn('cache_read_input_tokens', body)
                        # What reached the session in the middle of a turn is part of what it was told.
                        self.assertIn(report, body)
                        self.assertIn(handed, body)
                        self.assertNotIn('HOOK_OUTPUT_ONLY', body)
                        self.assertNotIn('CLI_RECORD_ONLY', body)

    def test_output_limit_is_read_from_the_claude_stream_only(self):
        message = "API Error: Claude's response exceeded the 64000 output token maximum."
        limited = [{'type': 'system', 'subtype': 'init', 'session_id': 's'},
                   {'type': 'assistant', 'is_api_error_message': True, 'api_error': 'max_output_tokens',
                    'message': {'model': '<synthetic>', 'content': [{'type': 'text', 'text': message}]}},
                   {'type': 'result', 'is_error': True, 'api_error': 'max_output_tokens', 'result': message}]
        other = [{'type': 'result', 'is_error': True, 'api_error': 'overloaded_error', 'result': 'API Error: 529'}]
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            stream = folder / 'cli.stdout.jsonl'
            stream.write_text('\n'.join(map(json.dumps, limited)) + '\nnot json\n', encoding='utf-8')
            self.assertEqual(output_limit(folder, 'claude'), message)
            self.assertIsNone(output_limit(folder, 'codex'))
            stream.write_text('\n'.join(map(json.dumps, other)), encoding='utf-8')
            self.assertIsNone(output_limit(folder, 'claude'))
            stream.unlink()
            self.assertIsNone(output_limit(folder, 'claude'))

    def test_a_turn_that_ended_because_the_model_refused_is_a_refusal_of_that_model(self):
        # The Claude CLI's own stream when the model refuses a request and the CLI has no other model to give
        # it to: a message of the CLI's own, and the result of the turn with the stop reason "refusal".
        message = "API Error: the model's safeguards flagged this message. Try rephrasing the request or change your model."
        refused = [{'type': 'system', 'subtype': 'init', 'session_id': 's'},
                   {'type': 'assistant', 'is_api_error_message': True, 'error': 'invalid_request',
                    'message': {'model': '<synthetic>', 'role': 'assistant', 'stop_reason': 'refusal',
                                'content': [{'type': 'text', 'text': message}]}},
                   {'type': 'result', 'subtype': 'success', 'is_error': True, 'stop_reason': 'refusal',
                    'terminal_reason': 'api_error', 'result': message}]
        # A turn that ended well and only speaks of a refusal is none.
        spoken = [{'type': 'result', 'subtype': 'success', 'is_error': False, 'stop_reason': 'end_turn',
                   'result': 'The stop reason "refusal" is discussed here.'}]
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            stream = folder / 'cli.stdout.jsonl'
            (folder / 'cli.stderr.log').write_text('', encoding='utf-8')
            stream.write_text('\n'.join(map(json.dumps, refused)), encoding='utf-8')
            found = refusal(folder, 'claude', 'claude/opus', None, 60)
            self.assertEqual((found['key'], found['reason'], found['source']),
                             ('model:claude/opus', 'model_refusal', 'backoff'))
            self.assertIsNone(refusal(folder, 'codex', 'codex/gpt-6.1-sol', None, 60))
            stream.write_text('\n'.join(map(json.dumps, spoken)), encoding='utf-8')
            self.assertIsNone(refusal(folder, 'claude', 'claude/opus', None, 60))

    def test_a_notice_of_usage_credits_that_a_response_to_the_session_follows_did_not_end_the_turn(self):
        # The CLI writes the notice into the stream where it occurs, also when an agent the session delegated to met
        # it under another model, and the turn can go on after it. The forms are those of the usage limit in
        # test_cli_adapter: a response of a model names that model, a message of the CLI's own names `<synthetic>`,
        # and an event of a delegated agent names the tool call that started the agent.
        notice = {'type': 'assistant', 'is_api_error_message': True, 'api_error': 'model_requires_usage_credits',
                  'message': {'model': '<synthetic>', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'Credits.'}]}}

        def response(parent=None):
            return {'type': 'assistant', 'parent_tool_use_id': parent,
                    'message': {'model': 'claude-model', 'role': 'assistant', 'content': [{'type': 'text', 'text': 'A step.'}]}}
        result = {'type': 'result', 'subtype': 'success', 'is_error': False}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'cli.stderr.log').write_text('', encoding='utf-8')

            def found(*rows):
                (folder / 'cli.stdout.jsonl').write_text('\n'.join(map(json.dumps, rows)), encoding='utf-8')
                signal = refusal(folder, 'claude', 'claude/opus', None, 60)
                return signal and (signal['key'], signal['reason'], signal['source'])
            blocked = ('model:claude/opus', 'model_requires_usage_credits', 'backoff')
            # The session was answered after the notice, so the turn went on and its model is not kept from sessions.
            self.assertIsNone(found(notice, response(), result))
            # A notice after the last response to the session counts, and so does one that only the response to a
            # delegated agent or the result of the turn follows.
            self.assertEqual(found(response(), notice), blocked)
            self.assertEqual(found(notice, response(), notice, result), blocked)
            self.assertEqual(found(notice, response(parent='toolu_1'), result), blocked)

    def test_claude_native_api_error_is_not_research_activity(self):
        # A refused Claude launch leaves only a synthetic error message in its native transcript.
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        for api_error, expected in ((True, False), (False, True)):
            with self.subTest(api_error=api_error), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                session = root / 'session'
                session.mkdir()
                native = root / 'profile/.claude/projects/project' / (identity + '.jsonl')
                native.parent.mkdir(parents=True)
                text = "You've hit your usage limit" if api_error else 'A first lemma about the root.'
                rows = [{'type': 'user', 'message': {'role': 'user', 'content': 'Begin the assigned research.'}},
                        {'type': 'assistant', 'isApiErrorMessage': api_error,
                         'message': {'role': 'assistant', 'content': [{'type': 'text', 'text': text}]}}]
                native.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
                (session / 'cli.stdout.jsonl').write_text(
                    json.dumps({'type': 'system', 'session_id': identity}), encoding='utf-8')
                (session / 'cli.stderr.log').write_text('', encoding='utf-8')
                with patch.dict(os.environ, {}, clear=True), patch('retention.Path.home', return_value=root / 'profile'):
                    receipt = capture(session, 'claude')
                self.assertEqual(receipt['native_transcripts'], ['transcript-' + identity + '.jsonl'])
                self.assertFalse(receipt['cli_activity'])
                self.assertIs(receipt['native_activity'], expected)

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

    def test_capture_copies_claude_output_stored_beside_the_transcript(self):
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / 'session'
            session.mkdir()
            project = root / 'profile/.claude/projects/project'
            stored = project / identity / 'tool-results/call1.txt'
            stored.parent.mkdir(parents=True)
            full_output = 'begin\n' + 'a' * 40000 + 'DECISIVE MIDDLE\nend'
            stored.write_text(full_output, encoding='utf-8')
            (project / identity / 'subagents').mkdir()
            (project / identity / 'subagents/agent-a1.jsonl').write_text('{"type": "assistant"}\n', encoding='utf-8')
            preview = ('<persisted-output>\nOutput too large. Full output saved to: ' + str(stored)
                       + '\n\nPreview (first 2KB):\nbegin\n</persisted-output>')
            (project / (identity + '.jsonl')).write_text(json.dumps({'type': 'user', 'message': {'role': 'user',
                'content': [{'type': 'tool_result', 'tool_use_id': 'call1', 'content': preview}]}}) + '\n', encoding='utf-8')
            (session / 'cli.stdout.jsonl').write_text(
                json.dumps({'type': 'system', 'session_id': identity}), encoding='utf-8')
            (session / 'cli.stderr.log').write_text('', encoding='utf-8')
            copy = session / ('transcript-' + identity)
            with patch.dict(os.environ, {}, clear=True), patch('retention.Path.home', return_value=root / 'profile'):
                self.assertEqual(capture(session, 'claude')['native_companions'], [copy.name])
                # Restart recovery can capture the same session again.
                self.assertEqual(capture(session, 'claude')['native_companions'], [copy.name])
            self.assertEqual((copy / 'tool-results/call1.txt').read_text(encoding='utf-8'), full_output)
            self.assertTrue((copy / 'subagents/agent-a1.jsonl').is_file())
            # The readable conversation holds the preview and names the copy that holds the full output.
            self.assertIn(copy.name + '/', (session / 'conversation.md').read_text(encoding='utf-8'))

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_capture_waits_for_a_file_of_the_cli_folder_that_another_process_holds(self):
        # The transcript and the folder beside it stand in the CLI's own folder, in the profile of the person who
        # runs the instance, where other programs open files as well. Windows refuses to open a file that another
        # process holds without read sharing. The runner calls capture and ends at any error (Runner.finish,
        # Runner.run), so a refused copy is made again until the file is let go (runtime_support.copy_to_disk).
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / 'session'
            session.mkdir()
            project = root / 'profile/.claude/projects/project'
            stored = project / identity / 'tool-results/call1.txt'
            stored.parent.mkdir(parents=True)
            stored.write_text('The full output.', encoding='utf-8')
            native = project / (identity + '.jsonl')
            raw = (json.dumps({'type': 'assistant', 'message': {'role': 'assistant', 'content': [
                {'type': 'text', 'text': 'A first lemma about the root.'}]}}) + '\n').encode('utf-8')
            native.write_bytes(raw)
            (session / 'cli.stdout.jsonl').write_text(
                json.dumps({'type': 'system', 'session_id': identity}), encoding='utf-8')
            (session / 'cli.stderr.log').write_text('', encoding='utf-8')
            # Real handles that share their file with no reader: one on the transcript, one on a file of the folder.
            held = []
            for path in (native, stored):
                handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise ctypes.WinError(ctypes.get_last_error())
                held.append(handle)
            pauses = []

            def let_go(seconds):
                # Each pause of the wait lets one file go, the transcript first.
                pauses.append(seconds)
                if held:
                    kernel.CloseHandle(held.pop(0))

            try:
                with patch.dict(os.environ, {}, clear=True), patch('retention.Path.home', return_value=root / 'profile'), \
                        patch('runtime_support.time.sleep', side_effect=let_go):
                    receipt = capture(session, 'claude')
            finally:
                for handle in held:
                    kernel.CloseHandle(handle)
            # Both files were let go by a pause of the wait, and both copies hold what their sources hold.
            self.assertEqual(held, [])
            self.assertGreaterEqual(len(pauses), 2)
            self.assertEqual((session / receipt['native_transcripts'][0]).read_bytes(), raw)
            self.assertEqual((session / receipt['native_companions'][0] / 'tool-results/call1.txt').read_text(encoding='utf-8'),
                             'The full output.')

    def test_what_capture_retains_is_on_the_disk_when_it_returns(self):
        # The runner saves, through to the disk, that a session is retained once capture has returned
        # (Runner.finish), and nothing captures that session again. A copy that the system still held in memory
        # when the machine lost power would stand in the session folder without its content. What reaches the
        # disk is seen at the system call that sends it there.
        identity = '01234567-89ab-cdef-0123-456789abcdef'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / 'session'
            session.mkdir()
            project = root / 'profile/.claude/projects/project'
            (project / identity / 'tool-results').mkdir(parents=True)
            (project / identity / 'tool-results/call1.txt').write_text('The full output.', encoding='utf-8')
            (project / (identity + '.jsonl')).write_text(json.dumps({'type': 'assistant', 'message': {
                'role': 'assistant', 'content': [{'type': 'text', 'text': 'A first lemma about the root.'}]}}) + '\n',
                encoding='utf-8')
            (session / 'cli.stdout.jsonl').write_text(
                json.dumps({'type': 'system', 'session_id': identity}), encoding='utf-8')
            (session / 'cli.stderr.log').write_text('', encoding='utf-8')
            flushed, fsync = set(), os.fsync

            def flush(descriptor):
                flushed.add(os.fstat(descriptor).st_ino)
                return fsync(descriptor)

            with patch.dict(os.environ, {}, clear=True), patch('retention.Path.home', return_value=root / 'profile'), \
                    patch.object(os, 'fsync', side_effect=flush):
                receipt = capture(session, 'claude')
            retained = [receipt['conversation'], *receipt['native_transcripts'],
                        *(name + '/tool-results/call1.txt' for name in receipt['native_companions'])]
            self.assertEqual(len(retained), 3)
            for name in retained:
                with (session / name).open('rb') as stream:
                    self.assertIn(os.fstat(stream.fileno()).st_ino, flushed, name)


if __name__ == '__main__':
    unittest.main()
