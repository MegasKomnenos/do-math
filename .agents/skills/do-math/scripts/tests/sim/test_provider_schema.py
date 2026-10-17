"""Unbound Codex transmission and semantic receipt through the real runner and worker.

Only the external CLI and Jobs port are doubles. Expected values come from
the role/repair contracts and the explicit caller values, not the decoder.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import jsonschema

from do_math.contracts import action_schema
from do_math.supervision import repair_report_schema
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs, ScriptedCLI, cli_schemas, codex_stream, model_runner


class ProviderSchemaTests(unittest.TestCase):
    def call(self, schema, value=None, *, raw=None, stream=None):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / 'workspace').mkdir()
        saved = deepcopy((schema, value))
        if raw is None:
            raw = json.dumps({'output_json': json.dumps(value, ensure_ascii=False)}, ensure_ascii=False).encode('utf-8')
        cli = ScriptedCLI(final=raw, stdout=codex_stream(raw) if stream is None else stream)
        clock = FakeClock()
        jobs = ProviderJobs(cli, clock=clock)
        result = model_runner(root, jobs, clock).run(
            prompt='Return the requested semantic value.', output_schema=schema,
            workspace=root / 'workspace', evidence_dir=root / 'evidence',
            model='gpt-6-astra', effort='low', timeout_seconds=None)
        self.assertEqual((schema, value), saved)
        self.assertTrue(jobs.launched[0].done and jobs.launched[0].closed)
        self.assertTrue(result['execution']['collect']['termination_barrier']['confirmed'])
        self.assertEqual((root / 'evidence/final.txt').read_bytes(), raw)
        return result, root, cli.calls[0]

    def maintenance(self):
        return {'summary': '', 'used_sources': [], 'questions': [], 'report': '한글 e\u0301', 'remaining_work': []}

    def test_full_maintenance_contract_is_carried_without_requiring_optional_fields(self):
        schema = action_schema({'role': 'maintenance'})
        value = self.maintenance()
        jsonschema.validate(value, schema)
        result, root, call = self.call(schema, value)
        argv = call['command']
        sent = Path(argv[argv.index('--output-schema') + 1]).read_bytes()
        transport = json.loads(sent)
        self.assertEqual(set(transport['required']), set(transport['properties']))
        self.assertEqual(set(transport['properties']), {'output_json'})
        self.assertEqual(transport['properties']['output_json']['type'], 'string')
        self.assertFalse(transport['additionalProperties'])
        # The embedded contract is the complete original schema, not its intersection
        # with the provider's restricted schema language.
        self.assertEqual(json.loads(transport['properties']['output_json']['description'].split('\n', 1)[1]), schema)
        self.assertEqual(json.loads((root / 'evidence/output.schema.json').read_bytes()), schema)
        self.assertEqual(result['execution']['collect']['worker_status']['schema_sha256'], hashlib.sha256(sent).hexdigest())
        self.assertEqual(call['stdin'], b'Return the requested semantic value.')
        self.assertEqual(result['status'], 'completed', result.get('error'))
        self.assertEqual(result['output'], value)

    def test_maintenance_absence_empty_and_nonempty_values_remain_distinct(self):
        schema = action_schema({'role': 'maintenance'})
        bundle = {'integration_id': 'IG-1', 'members': ['output'], 'impact_set': [], 'authority_refs': []}
        cases = [self.maintenance(), {**self.maintenance(), 'repair_responses': []},
                 {**self.maintenance(), 'integration_bundles': [bundle]},
                 {**self.maintenance(), 'integration_bundles': [{**bundle, 'previous_hashes': {}}]},
                 {**self.maintenance(), 'used_sources': ['file'], 'remaining_work': ['next'],
                  'integration_bundles': [{**bundle, 'previous_hashes': {'output': 'hash'}}],
                  'repair_responses': [{'issue_id': 'IS-1', 'disposition': 'resolved', 'reason': 'checked'}]}]
        for value in cases:
            with self.subTest(value=value):
                jsonschema.validate(value, schema)
                result, _, _ = self.call(schema, value)
                self.assertEqual(result['status'], 'completed', result.get('error'))
                self.assertEqual(result['output'], value)

    def test_original_maintenance_constraints_reject_invalid_values_without_repair(self):
        schema = action_schema({'role': 'maintenance'})
        base = self.maintenance()
        bundle = {'integration_id': 'IG-1', 'members': ['output'], 'impact_set': [], 'authority_refs': []}
        cases = [{k: v for k, v in base.items() if k != missing} for missing in schema['required']]
        cases += [{**base, key: None} for key in schema['properties']]
        cases += [{**base, 'integration_bundles': []}, {**base, 'extra': 1},
                  {**base, 'used_sources': [1]}, {**base, 'repair_responses': [{}]},
                  {**base, 'repair_responses': [{'issue_id': 'IS-1', 'disposition': 'other', 'reason': 'x'}]}]
        for patch in ({'previous_hashes': None}, {'previous_hashes': {'output': ''}},
                      {'members': []}, {'members': ['output', 'output']}, {'integration_id': ' '}, {'extra': 1}):
            cases.append({**base, 'integration_bundles': [{**bundle, **patch}]})
        cases.append({**base, 'integration_bundles': [{k: v for k, v in bundle.items() if k != 'members'}]})
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(jsonschema.ValidationError) as invalid:
                    jsonschema.validate(value, schema)
                result, _, _ = self.call(schema, value)
                self.assertEqual(result['status'], 'failed')
                self.assertEqual(result['error_kind'], 'output_validation')
                self.assertEqual(result['output'], value)
                path = 'output' + ''.join('/' + str(part) for part in invalid.exception.absolute_path)
                self.assertEqual(result['error'], path + ': ' + invalid.exception.message)

    def test_repair_consumer_keeps_its_full_schema_and_exact_result(self):
        for diagnosed in (False, True):
            schema = repair_report_schema(diagnosed=diagnosed)
            empty = {'summary': '', 'observed_status': '', 'actions': [], 'evidence_paths': [],
                     'user_questions': [], 'next_step': '', 'installation_version': '', 'source_commit': None}
            if diagnosed:
                empty.update(repair_outcome='', verification_evidence=[])
            nonempty = {k: ['proof'] if isinstance(v, list) else 'done' for k, v in empty.items()}
            for value in (empty, nonempty):
                with self.subTest(diagnosed=diagnosed, value=value):
                    result, _, _ = self.call(schema, value)
                    self.assertEqual(result['status'], 'completed', result.get('error'))
                    self.assertEqual(result['output'], value)
            for value in ({k: v for k, v in empty.items() if k != 'next_step'},
                          {k: v for k, v in empty.items() if k != 'installation_version'},
                          {k: v for k, v in empty.items() if k != 'source_commit'},
                          {**empty, 'installation_version': None}, {**empty, 'source_commit': 7},
                          {**empty, 'actions': [None]}, {**empty, 'next_step': None}, {**empty, 'extra': 1}):
                with self.subTest(diagnosed=diagnosed, invalid=value):
                    result, _, _ = self.call(schema, value)
                    self.assertEqual(result['status'], 'failed')
                    self.assertEqual(result['error_kind'], 'output_validation')
                    self.assertEqual(result['output'], value)

    def test_invalid_envelope_and_json_never_become_successful_semantic_values(self):
        for raw in (b'broken', b'[]', b'{}', b'{"output_json":null}', b'{"output_json":{}}',
                    b'{"output_json":"{}","extra":1}', b'{"output_json":"{}","output_json":"{}"}',
                    b'{"output_json":"broken"}', b'{"output_json":"{\\"x\\":1,\\"x\\":2}"}',
                    b'{"output_json":"{\\"x\\":NaN}"}'):
            with self.subTest(raw=raw):
                result, _, _ = self.call({}, raw=raw)
                self.assertEqual(result['status'], 'failed')
                self.assertEqual(result['error_kind'], 'output_validation')
                self.assertIsNone(result['output'])

    def test_probe_consumer_receives_its_original_result_through_the_transport(self):
        import probe_cli
        from support.entry import entry

        class ProbeResponseCLI(ScriptedCLI):
            def spawn(self, command, **options):
                semantic, _ = cli_schemas(command)
                self.expected = {'status': semantic['properties']['status']['const'],
                                 'nonce': semantic['properties']['nonce']['const'], 'phase': 'finished'}
                self.final = json.dumps(self.expected).encode('utf-8')
                return super().spawn(command, **options)

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        values = entry()
        cli = ProbeResponseCLI()
        jobs = ProviderJobs(cli, clock=values.ports.clock)
        result = probe_cli.run_case(root, 'structured', ports=replace(values.ports, jobs=jobs),
            provider='codex', model='gpt-6-astra', effort='low', only_assigned=False,
            codex_home=root, environment=values.environment, host_id=values.host_id)
        report = json.loads(Path(result['report']).read_bytes())
        self.assertTrue(result['passed'], result)
        self.assertEqual(report['result']['status'], 'completed')
        self.assertEqual(report['result']['output'], cli.expected)
        self.assertEqual(cli.expected['status'], 'CLI_OK')
        self.assertTrue(jobs.launched[0].done and jobs.launched[0].closed)

    def test_native_final_mismatch_is_rejected_before_decoding(self):
        result, _, _ = self.call({}, raw=b'{"output_json":"{}"}', stream=codex_stream(b'{"output_json":"[]"}'))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error_kind'], 'execution_failure')
        self.assertIn('final_response_mismatch', result['error'])
        self.assertIsNone(result['output'])
