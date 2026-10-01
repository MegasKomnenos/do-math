"""A central draft contract must not become a second provider-final contract: the runner, the adapters and the
workers (``model_runner``, ``codex_adapter``, ``claude_adapter``, the two workers; layer 3), moved from
``test_provider_final_contract``.

A research call bound to the control transport submits its draft centrally,
and its input bundle carries the draft schema; only an unbound call hands its
CLI a structured-final schema. The legacy test ran the runner over a scripted
collector (``provider_fixtures.Adapter``), so the adapter's start, the
worker's request check, the CLI command and the collection never ran. Here
they all run on the Jobs port fake and the scripted CLI at the worker's
``spawn`` seam (``support.provider_runs``), and the command the CLI actually
received is checked as well as the request on file.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from do_math import claude_worker, codex_worker, execution_profiles
from do_math.claude_adapter import ClaudePrintAdapter
from do_math.claude_stream import parse_stream
from do_math.control_transport import ControlTransport
from support.provider_inputs import PROFILE_CONFIG
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs
from support.provider_runs import ProviderJobs, ScriptedCLI, dispatched, model_runner

SCHEMA = {'type': 'object', 'properties': {'ids': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}},
          'required': ['ids'], 'additionalProperties': False}


class ProviderFinalContractTests(unittest.TestCase):
    def test_bound_draft_schema_stays_local_and_unbound_final_keeps_its_schema(self):
        from support.entry import entry
        _entry = entry()
        for provider, worker, model, flag in (
                ('codex', codex_worker, 'gpt-6-astra', '--output-schema'),
                ('claude', claude_worker, 'claude-opus-5', '--json-schema')):
            for bound in (True, False):
                with self.subTest(provider=model, bound=bound), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    workspace = root / 'workspace'; workspace.mkdir()
                    clock = FakeClock()
                    config = deepcopy(PROFILE_CONFIG)
                    config.update(tier_models={tier: model for tier in ('high', 'medium', 'low')},
                                  session_limits={'work': {model: 3}})
                    profile = next(p for p in execution_profiles.build_profiles(config, host=_entry.ports.host)['execution_profiles'].values()
                                   if p['role'] == 'research_work')
                    self.assertEqual(profile['ai']['provider'], provider)
                    prompt = execution_profiles.prepare_prompt('Use the provided draft schema.', profile)
                    binding = (ControlTransport(root / 'transport', clock=clock).issue('EX-final', 'GR-final',
                                                                                       workspace=workspace)
                               if bound else None)
                    # A bound call's final is prose (the draft went to the transport); an unbound one's is the output.
                    cli = ScriptedCLI(final=b'Draft submitted.' if bound else b'{"ids":[]}')
                    jobs = ProviderJobs(cli, clock=clock)
                    result = model_runner(root, jobs, clock).run(
                        prompt=prompt, input_seal=execution_profiles.prompt_seal(prompt), output_schema=SCHEMA,
                        workspace=workspace, evidence_dir=root / 'evidence', model=model,
                        effort=profile['ai']['effort'], timeout_seconds=60, execution_id='EX-final', profile=profile,
                        control_binding=binding, launch_ticket=dispatched('EX-final', profile, jobs, clock))
                    request = worker.load_request(root / 'evidence/request.json')
                    argv = worker.build_argv(request)
                    call, = cli.calls  # the worker accepted its request and started the CLI once
                    self.assertEqual('output_schema_path' in request, not bound)
                    self.assertEqual(flag in argv, not bound)
                    self.assertEqual(flag in call['command'], not bound)
                    # The CLI's schema file exists only for the unbound final it constrains,
                    # and holds the full draft schema, including the keyword rejected by
                    # the actual provider in REAL run009. A bound run's schema reaches the
                    # draft submission through its input bundle instead.
                    schema_file = root / 'evidence/output.schema.json'
                    self.assertEqual(schema_file.exists(), not bound)
                    if not bound:
                        self.assertEqual(json.loads(schema_file.read_text(encoding='utf-8')), SCHEMA)
                        sent = call['command'][call['command'].index(flag) + 1]
                        self.assertEqual(json.loads(sent) if provider == 'claude' else json.loads(
                            Path(sent).read_text(encoding='utf-8')), SCHEMA)
                    self.assertEqual(request.get('control_binding'), binding)
                    self.assertEqual(result['status'], 'completed')
                    if bound:
                        self.assertIsNone(result['output'])
                        self.assertEqual(result['collection'], 'provider_evidence_only')
                    else:
                        self.assertEqual(result['output'], {'ids': []})

    def test_claude_text_terminal_retains_protocol_checks_and_exact_text(self):
        text = 'Submitted Cafe\N{COMBINING ACUTE ACCENT}.'
        events = [{'type': 'system', 'subtype': 'init', 'session_id': 'session'},
                  {'type': 'result', 'subtype': 'success', 'is_error': False,
                   'session_id': 'session', 'result': text, 'num_turns': 1, 'usage': {}}]
        raw = b''.join(json.dumps(row, ensure_ascii=False).encode('utf-8') + b'\n' for row in events)
        # The stream parser requires a structured output unless told otherwise.
        self.assertFalse(parse_stream(raw)['parse_complete'])
        adapter = ClaudePrintAdapter('fixture-cli', jobs=FakeJobs(), clock=FakeClock())
        parsed = adapter.parse_response(raw, {})  # a request without an output schema
        self.assertTrue(parsed['parse_complete'])
        self.assertTrue(parsed['turn_completed'])
        self.assertNotIn('structured_output', parsed)
        self.assertEqual(adapter.validate_final(parsed, text.encode('utf-8')), [])
        # The precomposed spelling is the same text under normalization but different bytes.
        self.assertEqual(adapter.validate_final(parsed, 'Submitted Caf\N{LATIN SMALL LETTER E WITH ACUTE}.'.encode('utf-8')),
                         ['final_response_mismatch'])
        self.assertFalse(adapter.parse_response(raw + b'{', {})['parse_complete'])


if __name__ == '__main__':
    unittest.main()
