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
    output = io.StringIO()
    with redirect_stdout(output):
        code = cli.main(argv)
    return code, json.loads(output.getvalue())


class QueryInputTests(unittest.TestCase):
    def test_query_rejects_unused_filters_before_reading_in_both_interfaces(self):
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
                        cli.execute(build_parser().parse_args(base + options))
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


if __name__ == '__main__':
    unittest.main()
