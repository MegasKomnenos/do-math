"""The command line refuses malformed input before it reads anything (``cli.main``, ``cli.execute``, layer 3).

No engine runs: these call the CLI's entry functions directly with a repository
path that is never opened. The legacy tests replaced ``cli.execute``,
``cli.ResearchRepository``, ``cli.query_records`` and ``cli.read_record`` to see
that none was reached; here the unchanged product runs and ``sys.monitoring``
counts the calls (``support.provider_probes.ObservedCalls``).
"""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest

from do_math import cli
from do_math.cli_contract import CliInputError, _json_arguments, build_parser
from do_math.core_engine import query_records, read_record
from do_math.repository import ResearchRepository
from support.provider_probes import ObservedCalls


def main(argv):
    """``cli.main(argv)`` in this process: ``(exit code, printed envelope)``."""
    from support.entry import entry
    _entry = entry()
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(argv, ports=_entry.ports, environment=_entry.environment, host_id=_entry.host_id, codex_home=_entry.codex_home)
    return code, json.loads(output.getvalue())


class QueryInputTests(unittest.TestCase):
    def test_query_rejects_unused_filters_before_reading_in_both_interfaces(self):
        from support.entry import entry
        _entry = entry()
        base = ['query', '--repository', '.', '--instance', 'RI-test']
        different = "invalid command payload: {'repository': '.', 'instance': 'RI-test', 'files': True, '%s': %s} " \
                    "should not be valid under {'anyOf': [{'required': ['kind']}, {'required': ['related_to']}, " \
                    "{'required': ['direction']}]}"
        combined = '--files cannot be combined with --kind, --related-to or --direction'
        cases = [
            (['--prefix', 'runtime/'], {'prefix': 'runtime/'}, '--prefix requires --files',
             "invalid command payload: {'repository': '.', 'instance': 'RI-test', 'prefix': 'runtime/'} "
             "should not be valid under {'required': ['prefix']}"),
            (['--direction', 'incoming'], {'direction': 'incoming'}, '--direction requires --related-to',
             "invalid command payload: 'related_to' is a dependency of 'direction'"),
            (['--files', '--kind', 'grant'], {'files': True, 'kind': 'grant'}, combined, different % ('kind', "'grant'")),
            (['--files', '--related-to', 'KN-one'], {'files': True, 'related_to': 'KN-one'}, combined,
             different % ('related_to', "'KN-one'")),
            (['--files', '--direction', 'both'], {'files': True, 'direction': 'both'}, combined,
             different % ('direction', "'both'")),
        ]
        for options, payload, argv_reason, json_reason in cases:
            with self.subTest(options=options):
                with ObservedCalls(repository=ResearchRepository.__init__, records=query_records) as calls:
                    with self.assertRaises(CliInputError) as refused:
                        cli.execute(build_parser().parse_args(base + options), codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
                    self.assertEqual(str(refused.exception), argv_reason)
                    with self.assertRaises(CliInputError) as refused:
                        _json_arguments(build_parser(), {'schema_version': 5, 'command': 'query',
                                                         'payload': {'repository': '.', 'instance': 'RI-test', **payload}})
                    self.assertEqual(str(refused.exception), json_reason)
                self.assertEqual((calls.count('repository'), calls.count('records')), (0, 0))


class RequestFileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / 'request.json'

    def test_record_output_path_is_rejected_before_reading(self):
        with ObservedCalls(read=read_record, repository=ResearchRepository.__init__) as calls:
            code, envelope = main(['read', '--repository', '.', '--instance', 'RI-test', '--id', 'KN-test',
                                   '--output', 'unused.json'])
        self.assertEqual(code, 2)
        self.assertEqual((calls.count('read'), calls.count('repository')), (0, 0))
        self.assertEqual(envelope['error']['message'], '--output requires --path')

    def test_common_request_rejects_malformed_identity_before_dispatch(self):
        base = {'schema_version': 5, 'command': 'pause', 'payload': {'repository': '.', 'instance': 'RI-test'}}
        cases = (({'request_id': False}, "invalid command request: False is not of type 'string'"),
                 ({'request_id': ''}, "invalid command request: '' does not match '^[A-Za-z0-9_-]{1,128}$'"),
                 ({'idempotency_key': 7}, "invalid command request: 7 is not of type 'string'"),
                 ({'command': ['pause']}, "invalid command request: ['pause'] is not of type 'string'"))
        for changes, message in cases:
            with self.subTest(changes=changes):
                self.path.write_text(json.dumps({**base, **changes}), encoding='utf-8')
                with ObservedCalls(dispatch=cli.execute) as calls:
                    code, envelope = main(['--request-file', str(self.path)])
                self.assertEqual(code, 2)
                self.assertEqual(calls.count('dispatch'), 0)
                self.assertEqual((envelope['error']['kind'], envelope['error']['message']), ('input_error', message))

    def test_json_request_validates_types_and_preserves_common_error(self):
        self.path.write_text(json.dumps({'schema_version': 5, 'command': 'query', 'caller': 'user',
            'payload': {'repository': '.', 'instance': 'RI-test', 'limit': True}}), encoding='utf-8')
        with ObservedCalls(dispatch=cli.execute) as calls:
            code, envelope = main(['--request-file', str(self.path)])
        self.assertEqual(code, 2)
        self.assertEqual(calls.count('dispatch'), 0)
        self.assertEqual(envelope['command'], 'query')
        self.assertNotIn('result', envelope)
        self.assertEqual(envelope['error'], {'kind': 'input_error', 'next_owner': 'user', 'retryable': False,
                                             'message': "invalid command payload: True is not of type 'integer'"})


class PublicInputBoundaryTests(unittest.TestCase):
    def test_unreadable_input_files_report_input_errors_without_repository_effects(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        identity = ['--repository', str(root / 'repository'), '--instance', 'RI-test']
        for raw in (None, b'\xff', b'{', b'{"duplicate":1,"duplicate":2}'):
            document = root / 'request.json'
            if raw is not None:
                document.write_bytes(raw)
            with self.subTest(raw=raw), ObservedCalls(repository=ResearchRepository.__init__) as calls:
                code, envelope = main(['configure', *identity, '--config-file', str(document)])
            self.assertEqual(code, 2)
            self.assertEqual({key: envelope['error'][key] for key in ('kind', 'next_owner', 'retryable')},
                             {'kind': 'input_error', 'next_owner': 'user', 'retryable': False})
            self.assertTrue(envelope['error']['message'].startswith(f'cannot read JSON file {document}: '), envelope)
            self.assertEqual(calls.count('repository'), 0)
            if raw is not None:
                self.assertEqual(document.read_bytes(), raw)
        for raw in (None, b'\xff'):
            document = root / 'input.txt'
            if raw is not None:
                document.write_bytes(raw)
            with self.subTest(text=raw), ObservedCalls(repository=ResearchRepository.__init__) as calls:
                code, envelope = main(['input', *identity, '--file', str(document)])
            self.assertEqual(code, 2)
            self.assertEqual(envelope['error']['kind'], 'input_error')
            self.assertTrue(envelope['error']['message'].startswith(f'cannot read text file {document}: '), envelope)
            self.assertEqual(calls.count('repository'), 0)
        self.assertFalse((root / 'repository').exists())

    def test_describe_publishes_the_parser_contract_and_rejects_extra_arguments(self):
        from do_math.cli_contract import describe_commands
        from do_math.canonical import exact_content_hash
        for argv, command in ((['--describe'], None), (['--describe', 'source'], 'source')):
            with self.subTest(argv=argv):
                code, envelope = main(argv)
                self.assertEqual(code, 0)
                self.assertEqual(envelope['command'], 'describe')
                self.assertEqual(envelope['request_id'], 'QR-' + exact_content_hash(argv))
                self.assertEqual(envelope['result'], describe_commands(build_parser(), command))
        for argv, reason in (
            (['--describe', 'source', 'extra'], '--describe accepts at most one command name'),
            (['--request-file'], '--request-file accepts exactly one path'),
            (['--request-file', 'one', 'two'], '--request-file accepts exactly one path'),
        ):
            with self.subTest(argv=argv):
                code, envelope = main(argv)
                self.assertEqual(code, 2)
                self.assertEqual(envelope['error'], {
                    'kind': 'input_error', 'message': reason, 'next_owner': 'user', 'retryable': False})

    def test_file_and_request_mode_errors_precede_repository_access(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        document = root / 'not-an-object.json'
        document.write_text('[]', encoding='utf-8')
        missing = root / 'missing'
        identity = ['--repository', str(root / 'repository'), '--instance', 'RI-test']
        cases = [
            (['configure', *identity, '--config-file', str(document)], 'JSON configuration must be an object'),
            (['source', *identity, '--file', str(missing)], '--file is not a file: ' + str(missing)),
            (['request', *identity, '--assessment-reassessment-file', str(missing), '--target', 'KN-missing'],
             '--assessment-reassessment-file cannot be combined with target or request text'),
            (['request', *identity, '--retry-action', 'AC-missing', '--reason', 'conflicting text'],
             '--retry-action cannot be combined with target or request text'),
            (['profile', '--provider', 'codex', '--claude-path', str(missing)],
             '--claude-path requires --provider claude'),
            (['profile', '--provider', 'claude', '--codex-path', str(missing)],
             '--codex-path requires --provider codex'),
        ]
        for argv, reason in cases:
            with self.subTest(argv=argv), ObservedCalls(repository=ResearchRepository.__init__) as calls:
                code, envelope = main(argv)
                self.assertEqual(code, 2)
                self.assertEqual(envelope['error']['kind'], 'input_error')
                self.assertEqual(envelope['error']['message'], reason)
                self.assertEqual(calls.count('repository'), 0)
        self.assertFalse((root / 'repository').exists())

    def test_missing_provider_executable_reports_unverified_surface(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for provider in ('codex', 'claude'):
            executable = root / (provider + '-absent.exe')
            with self.subTest(provider=provider):
                code, envelope = main(['profile', '--provider', provider,
                                       '--' + provider + '-path', str(executable)])
                self.assertEqual(code, 1)
                self.assertEqual(envelope['exit_code'], 1)
                self.assertEqual(envelope['result'], {
                    'cli_path': str(executable), 'verified': False, 'error_type': 'FileNotFoundError'})
                self.assertFalse(executable.exists())

    def test_script_help_exits_successfully_and_import_does_not_dispatch(self):
        import runpy
        import sys
        from unittest.mock import patch
        from support.storage_files import audit_events
        script = Path(cli.__file__).resolve().parents[1] / 'do_math.py'
        output = io.StringIO()
        with patch.object(sys, 'argv', [str(script), '--help']), redirect_stdout(output), \
                audit_events('subprocess.Popen') as started:
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(script), run_name='__main__')
        self.assertEqual(stopped.exception.code, 0)
        self.assertEqual(output.getvalue(), build_parser().format_help())
        self.assertEqual(started, [])
        output = io.StringIO()
        with patch.object(sys, 'argv', [str(script), '--help']), redirect_stdout(output), \
                audit_events('subprocess.Popen') as started:
            namespace = runpy.run_path(str(script), run_name='do_math_entry_import')
        self.assertIs(namespace['main'], cli.main)
        self.assertEqual(output.getvalue(), '')
        self.assertEqual(started, [])

if __name__ == '__main__':
    unittest.main()
