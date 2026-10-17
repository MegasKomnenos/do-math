"""The command-line contract (``cli_contract``, layer 2) and the inspection exit rule (``state_checks``, layer 2).

``build_parser`` and ``_json_arguments`` turn argv and a JSON request into one
namespace, ``describe_commands`` publishes the contract, and
``operator_schedule_after_configure`` decides what a ``configure`` receipt means
for the operator schedule. All are pure: no repository, engine or process.
"""
from pathlib import Path
import unittest

from do_math.cli_contract import (CliInputError, _command_parsers, _json_arguments, build_parser, describe_commands,
                                  operator_schedule_after_configure)
from do_math.control_contracts import OPERATOR_ACTIONS
from do_math.state_checks import inspection_exit_code

INSTANCE = ('--repository', '.', '--instance', 'RI-test')


class RequestModeTests(unittest.TestCase):
    def test_run_manifest_path_has_the_same_cli_and_json_contract(self):
        parser = build_parser()
        cli = parser.parse_args(['run', *INSTANCE, '--installation-manifest', 'frozen/manifest.json'])
        structured = _json_arguments(parser, {'schema_version': 5, 'command': 'run',
            'payload': {'repository': '.', 'instance': 'RI-test', 'installation_manifest': 'frozen/manifest.json'}})
        self.assertEqual(cli.installation_manifest, Path('frozen/manifest.json'))
        self.assertEqual(structured.installation_manifest, cli.installation_manifest)
        self.assertIsNone(parser.parse_args(['run', *INSTANCE]).installation_manifest)

    def test_query_json_arguments_preserve_valid_modes_and_refuse_incompatible_combinations(self):
        parser = build_parser()
        def arguments(**payload):
            return _json_arguments(parser, {'schema_version': 5, 'command': 'query',
                'payload': {'repository': '.', 'instance': 'RI-test', **payload}})
        self.assertFalse(arguments().files)
        self.assertTrue(arguments(files=True, prefix='runtime/').files)
        self.assertEqual(arguments(related_to='KN-test', direction='incoming').direction, 'incoming')
        for payload in ({'related_to': 'KN-test', 'direction': 'sideways'},
                        {'files': True, 'kind': 'grant'}, {'files': True, 'direction': 'both'},
                        {'prefix': 'runtime/'}, {'direction': 'incoming'}):
            with self.subTest(payload=payload), self.assertRaisesRegex(CliInputError, 'invalid command payload'):
                arguments(**payload)
        with self.assertRaisesRegex(CliInputError, "argument --direction: invalid choice: 'sideways'"):
            parser.parse_args(['query', *INSTANCE, '--related-to', 'KN-test', '--direction', 'sideways'])

    def test_retry_action_is_a_distinct_request_mode(self):
        parser = build_parser()
        retry = parser.parse_args(('request', *INSTANCE, '--retry-action', 'AC-held'))
        self.assertEqual(retry.retry_action, 'AC-held')
        self.assertIsNone(retry.role)
        with self.assertRaisesRegex(CliInputError, '^argument --retry-action: not allowed with argument --role$'):
            parser.parse_args(('request', *INSTANCE, '--role', 'maintenance', '--retry-action', 'AC-held'))
        with self.assertRaisesRegex(CliInputError, '^unrecognized arguments: --text inspect state$'):
            parser.parse_args(('request', *INSTANCE, '--role', 'maintenance', '--text', 'inspect state'))
        schema = describe_commands(parser, 'request')['commands']['request']['payload_schema']
        self.assertIn('reason', schema['properties'])
        self.assertNotIn('text', schema['properties'])
        with self.assertRaisesRegex(CliInputError, r"^invalid command payload: Additional properties are not allowed "
                                                   r"\('text' was unexpected\)$"):
            _json_arguments(parser, {'schema_version': 5, 'command': 'request', 'payload': {
                'repository': '.', 'instance': 'RI-test', 'role': 'maintenance', 'text': 'inspect state'}})

    def test_json_string_values_preserve_leading_hyphens(self):
        parser = build_parser()
        for command, field in (('input', 'text'), ('pause', 'reason'), ('init', 'goal')):
            for value in ('--literal-user-text', '-P', '--', ''):
                with self.subTest(command=command, value=value):
                    payload = {'repository': '.', field: value}
                    payload.update({'workspace': '.'} if command == 'init' else {'instance': 'RI-test'})
                    args = _json_arguments(parser, {'schema_version': 5, 'command': command, 'payload': payload})
                    self.assertEqual(getattr(args, field), value)
        args = _json_arguments(parser, {'schema_version': 5, 'command': 'init', 'payload': {
            'repository': '.', 'workspace': '.', 'goal': 'P', 'source': ['--first.txt', '-second.txt']}})
        self.assertEqual(args.source, [Path('--first.txt'), Path('-second.txt')])

    def test_operator_origin_is_offered_only_where_control_admission_accepts_it(self):
        parser = build_parser()
        offered = {}
        for name, command in _command_parsers(parser).items():
            origin = next((action for action in command._actions if action.dest == 'origin'), None)
            if origin is not None:
                offered[name.replace('-', '_')] = 'operator' in origin.choices
        self.assertIn('decision', offered)
        self.assertEqual({name for name, operator in offered.items() if operator}, set(OPERATOR_ACTIONS))
        with self.assertRaisesRegex(CliInputError, r"^argument --origin: invalid choice: 'operator' \(choose from user\)$"):
            parser.parse_args(['decision', *INSTANCE, '--file', 'unused.json', '--origin', 'operator'])


class ConfigureScheduleTests(unittest.TestCase):
    def test_configure_receipt_does_not_reapply_scheduler(self):
        requested = {'operator_enabled': False}
        receipt = {'accepted': True, 'request_id': 'UC-test', 'snapshot': 'a' * 40, 'config': requested}
        self.assertEqual(operator_schedule_after_configure(requested, {**receipt, 'effect': 'applied', 'replayed': True}),
                         {'status': 'not_reapplied', 'reason': 'original control receipt replayed; explicit '
                          'operator install or uninstall reconciles current configuration'})
        self.assertEqual(operator_schedule_after_configure(requested, {**receipt, 'effect': 'rejected', 'replayed': False}),
                         {'status': 'not_applied', 'reason': 'configuration was rejected'})
        # The same receipt newly applied is the one that reconciles the schedule.
        self.assertEqual(operator_schedule_after_configure(requested, {**receipt, 'effect': 'applied'}), 'reconcile')

    def test_operator_effort_alone_leaves_the_schedule_untouched(self):
        # The recovery AI reads operator_effort from the recovery profile that configure rebuilds.
        receipt = {'accepted': True, 'request_id': 'UC-test', 'effect': 'applied', 'snapshot': 'a' * 40,
                   'config': {'operator_enabled': True, 'operator_interval_seconds': 7200,
                              'operator_timeout_seconds': 5400}}
        self.assertIsNone(operator_schedule_after_configure({'operator_effort': 'max'}, receipt))


class InspectionExitTests(unittest.TestCase):
    def test_check_exit_uses_actual_inspection_status(self):
        for status, expected in (('healthy', 0), ('incomplete', 1), ('blocked', 1), ('degraded', 1)):
            with self.subTest(status=status):
                self.assertEqual(inspection_exit_code({'status': status}), expected)
        with self.assertRaisesRegex(ValueError, '^unknown inspection status$'):
            inspection_exit_code({'status': 'passed'})


if __name__ == '__main__':
    unittest.main()
