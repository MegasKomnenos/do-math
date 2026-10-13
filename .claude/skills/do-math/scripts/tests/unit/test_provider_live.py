"""Offline preparation checks for the paid provider smoke; no provider is called here."""
import json
from pathlib import Path
import sys
import unittest

from do_math.contracts import action_schema
from do_math.observations import checkpoint_value
from support.provider_live import smoke_inputs, smoke_request, smoke_read_events


class ProviderSmokePreparationTests(unittest.TestCase):
    def test_missing_inputs_fail_before_calling_any_provider(self):
        with self.assertRaisesRegex(ValueError, 'provider smoke requires explicit inputs: DO_MATH_SMOKE_CODEX_CLI'):
            smoke_inputs('codex', {})

    def test_inputs_are_explicit_and_do_not_fall_back_to_global_defaults(self):
        inputs = smoke_inputs('codex', {'DO_MATH_SMOKE_CODEX_CLI': sys.executable,
            'DO_MATH_SMOKE_CODEX_MODEL': 'configured-model', 'DO_MATH_SMOKE_CODEX_EFFORT': 'low',
            'DO_MATH_SMOKE_HOST': 'test-host'})
        self.assertEqual(inputs, {'cli': sys.executable, 'model': 'configured-model', 'effort': 'low', 'host': 'test-host'})

    def test_request_retains_the_complete_current_role_schema_and_valid_checkpoint(self):
        prompt, schema, expected, checkpoint = smoke_request(Path('workspace'), 'nonce')
        self.assertEqual(schema, action_schema({'role': 'maintenance'}))
        self.assertIn('integration_bundles', schema['properties'])
        self.assertIn('repair_responses', schema['properties'])
        self.assertEqual(expected['report'], 'nonce')
        self.assertEqual(checkpoint_value(json.dumps(checkpoint).encode()), checkpoint)
        self.assertIn('separate shell tool call', prompt)

    def test_codex_read_requires_successful_tool_result_and_exact_parsed_value(self):
        event = {'type': 'item.completed', 'item': {'id': 'read', 'type': 'command_execution',
            'exit_code': 0, 'status': 'completed', 'aggregated_output': '{"read_nonce":"nonce"}\n'}}
        self.assertEqual(smoke_read_events('codex', [event], 'nonce'),
                         [{'event_index': 0, 'tool_id': 'read', 'value': {'read_nonce': 'nonce'}}])
        for changed in ({'exit_code': 1}, {'aggregated_output': 'nonce'}, {'status': 'in_progress'},
                        {'aggregated_output': '{"read_nonce":"wrong"}'}):
            with self.subTest(changed=changed):
                self.assertEqual(smoke_read_events('codex', [{**event, 'item': {**event['item'], **changed}}], 'nonce'), [])

    def test_claude_read_requires_matching_prior_bash_identity_and_nonerror_result(self):
        use = {'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'id': 'read'}]}}
        result = {'type': 'tool_result', 'tool_use_id': 'read', 'content': '{"read_nonce":"nonce"}', 'is_error': False}
        event = {'message': {'content': [result]}}
        self.assertEqual(smoke_read_events('claude', [use, event], 'nonce'),
                         [{'event_index': 1, 'tool_id': 'read', 'value': {'read_nonce': 'nonce'}}])
        for events in ([event], [event, use], [use, {'message': {'content': [{**result, 'is_error': True}]}}],
                       [use, {'message': {'content': [{**result, 'tool_use_id': 'other'}]}}]):
            with self.subTest(events=events):
                self.assertEqual(smoke_read_events('claude', events, 'nonce'), [])
