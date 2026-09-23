"""A central draft contract must not become a second provider-final contract."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import claude_worker, codex_worker, execution_profiles
from do_math.control_transport import ControlTransport
from do_math.model_runner import ClaudeModelRunner, CodexModelRunner
from test_model_runner import Adapter
from test_redesign_PROFILES import CONFIG


class ProviderFinalContractTests(unittest.TestCase):
    def test_bound_draft_schema_stays_local_and_unbound_final_keeps_its_schema(self):
        schema = {'type': 'object', 'properties': {'ids': {'type': 'array',
            'items': {'type': 'string'}, 'uniqueItems': True}},
            'required': ['ids'], 'additionalProperties': False}
        for runner_type, worker, model, flag in (
                (CodexModelRunner, codex_worker, 'gpt-6-astra', '--output-schema'),
                (ClaudeModelRunner, claude_worker, 'claude-opus-5', '--json-schema')):
            for bound in (True, False):
                with self.subTest(provider=model, bound=bound), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    workspace = root / 'workspace'; workspace.mkdir()
                    config = deepcopy(CONFIG)
                    config.update(tier_models={tier: model for tier in ('high', 'medium', 'low')},
                        session_limits={pool: {model: 3} for pool in ('work', 'operations')})
                    profile = next(p for p in execution_profiles.build_profiles(config)['execution_profiles'].values()
                                   if p['role'] == 'research_work')
                    prompt = execution_profiles.prepare_prompt('Use the provided draft schema.', profile)
                    binding = (ControlTransport(root / 'transport').issue('EX-final', 'GR-final', workspace=workspace)
                               if bound else None)
                    raw_final = b'Draft submitted.' if bound else b'{"ids":[]}'
                    adapter = Adapter({'result': 'output_collected', 'final': {'raw': raw_final}, 'jsonl': {}})
                    runner = runner_type('fixture-cli'); runner._adapter = adapter
                    result = runner.run(prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt),
                        output_schema=schema, workspace=workspace, evidence_dir=root / 'evidence',
                        model=model, effort=profile['ai']['effort'], timeout_seconds=60,
                        execution_id='EX-final', profile=profile, control_binding=binding)
                    request = worker.load_request(root / 'evidence/request.json')
                    argv = worker.build_argv(request)
                    self.assertEqual('output_schema_path' in request, not bound)
                    self.assertEqual(flag in argv, not bound)
                    # The full draft schema is preserved, including the keyword
                    # rejected by the actual provider in REAL run009.
                    self.assertEqual(json.loads((root / 'evidence/output.schema.json').read_text(encoding='utf-8')), schema)
                    self.assertEqual(request.get('control_binding'), binding)
                    self.assertEqual(result['status'], 'completed')
                    if bound:
                        self.assertIsNone(result['output'])
                        self.assertEqual(result['collection'], 'provider_evidence_only')

    def test_unsubmitted_provider_terminal_is_not_a_research_result(self):
        from do_math.engine import ResearchEngine
        engine = object.__new__(ResearchEngine)
        result = {'status': 'completed', 'output': None, 'collection': 'provider_evidence_only'}
        rejected = engine._collect_submitted_result({}, result, {}, {}, None)
        self.assertEqual(rejected['status'], 'failed')
        self.assertEqual(rejected['error_kind'], 'execution_failure')
        self.assertIsNone(rejected['output'])

    def test_claude_text_terminal_retains_protocol_checks_and_exact_text(self):
        from do_math.claude_stream import parse_stream
        from do_math.claude_adapter import ClaudePrintAdapter
        text = 'Submitted Cafe\u0301.'
        events = [{'type': 'system', 'subtype': 'init', 'session_id': 'session'},
                  {'type': 'result', 'subtype': 'success', 'is_error': False,
                   'session_id': 'session', 'result': text, 'num_turns': 1, 'usage': {}}]
        raw = b''.join(json.dumps(row, ensure_ascii=False).encode('utf-8') + b'\n' for row in events)
        self.assertFalse(parse_stream(raw)['parse_complete'])
        adapter = ClaudePrintAdapter('fixture-cli')
        parsed = adapter.parse_response(raw, {})
        self.assertTrue(parsed['parse_complete'])
        self.assertTrue(parsed['turn_completed'])
        self.assertNotIn('structured_output', parsed)
        self.assertEqual(adapter.validate_final(parsed, text.encode('utf-8')), [])
        self.assertEqual(adapter.validate_final(parsed, 'Submitted Caf\u00e9.'.encode('utf-8')), ['final_text_mismatch'])
        self.assertFalse(adapter.parse_response(raw + b'{', {})['parse_complete'])


if __name__ == '__main__':
    unittest.main()
