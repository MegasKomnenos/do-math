"""JSON 공개 명령의 주체·재전달 ID·배열·불리언 분기를 실제 parser로 대조한다."""
from pathlib import Path
import unittest

from do_math.cli_contract import (CliInputError, WIRE_VERSION, _json_arguments,
    build_parser, describe_commands, operator_schedule_after_configure)


class JsonRequestMatrixTests(unittest.TestCase):
    def test_request_caller_and_top_level_identity_reach_the_parser(self):
        parser = build_parser()
        request = {'schema_version': WIRE_VERSION, 'command': 'pause', 'caller': 'operator',
                   'request_id': 'UC-explicit', 'idempotency_key': 'try-2',
                   'payload': {'repository': '.', 'instance': 'RI-one', 'reason': '운영 중지'}}
        args = _json_arguments(parser, request)
        self.assertEqual((args.origin, args.request_id, args.idempotency_key, args.reason),
                         ('operator', 'UC-explicit', 'try-2', '운영 중지'))
        with self.assertRaisesRegex(CliInputError, '^caller differs from payload origin$'):
            _json_arguments(parser, {**request, 'payload': {**request['payload'], 'origin': 'user'}})
        for key in ('request_id', 'idempotency_key'):
            with self.subTest(key=key):
                with self.assertRaisesRegex(CliInputError, '^unexpected or duplicate ' + key + '$'):
                    _json_arguments(parser, {**request, 'payload': {**request['payload'], key: request[key]}})
                with self.assertRaisesRegex(CliInputError, '^unexpected or duplicate ' + key + '$'):
                    _json_arguments(parser, {'schema_version': WIRE_VERSION, 'command': 'status', key: request[key],
                        'payload': {'repository': '.', 'instance': 'RI-one'}})

    def test_boolean_and_multiple_argument_forms_preserve_exact_values(self):
        parser = build_parser()
        base = {'schema_version': WIRE_VERSION, 'payload': {'repository': '.', 'instance': 'RI-one'}}
        for value in (False, True):
            with self.subTest(value=value):
                args = _json_arguments(parser, {**base, 'command': 'run',
                    'payload': {**base['payload'], 'watch': value, 'until_active': value, 'max_steps': 7}})
                self.assertEqual((args.watch, args.until_active, args.max_steps), (value, value, 7))
        args = _json_arguments(parser, {**base, 'command': 'check',
            'payload': {**base['payload'], 'kinds': ['storage', 'input']}})
        self.assertEqual(args.kinds, ['storage', 'input'])
        args = _json_arguments(parser, {**base, 'command': 'status', 'caller': 'operator'})
        self.assertTrue(args.json)
        self.assertEqual(args.repository, Path('.'))

    def test_unknown_description_and_pending_configuration_are_explicit(self):
        with self.assertRaisesRegex(CliInputError, '^unknown command for --describe$'):
            describe_commands(build_parser(), 'unknown-command')
        self.assertEqual(operator_schedule_after_configure({'operator_enabled': True}, {'effect': 'pending engine processing'}),
                         {'status': 'pending', 'reason': 'run operator install or uninstall after the control is applied'})
