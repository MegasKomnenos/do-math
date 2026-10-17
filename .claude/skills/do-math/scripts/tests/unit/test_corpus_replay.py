"""Recorded-output replay (의무 9-B, 설계 4.5): every corpus entry, parsed by the product's layer-1 parser, gives
the judgment recorded with it.

``READERS`` maps each corpus kind to how its entry is parsed and which part of
the result is the judgment. A new kind of recording adds one reader here and
its entries to ``tests/corpus/manifest.json``; an entry of a kind with no
reader fails the walk.
"""
import json
from pathlib import Path
import unittest

CORPUS = Path(__file__).resolve().parents[1] / 'corpus'


def _codex_stream(entry):
    from do_math.codex_stream import parse_jsonl
    parsed = parse_jsonl((CORPUS / entry['path']).read_bytes())
    judged = {'turn_completed': parsed['turn_completed'], 'parse_complete': parsed['parse_complete'],
              'usage_fields': sorted(parsed['usage'][0]) if parsed['usage'] else [],
              'unknown_events': [row['kind'] for row in parsed['unknown_events']]}
    if 'turn_failed' in entry['verdict']:
        judged['turn_failed'] = parsed['turn_failed']
    if 'final_path' in entry:
        import hashlib
        final = (CORPUS / entry['final_path']).read_bytes()
        judged['final_sha256'] = hashlib.sha256(final).hexdigest()
        judged['final_is_selected_text'] = parsed.get('final_text', '').encode('utf-8') == final
    return judged


def _claude_stream(entry):
    from do_math.claude_stream import parse_stream
    parsed = parse_stream((CORPUS / entry['path']).read_bytes())
    return {'turn_completed': parsed['turn_completed'], 'turn_failed': parsed['turn_failed'],
            'parse_complete': parsed['parse_complete'], 'unknown_events': parsed['unknown_events'],
            'structured_output': parsed.get('structured_output'), 'reported_models': parsed['reported_models'],
            'result_segments': len(parsed['result_segments']), 'usage_segments': len(parsed['usage_segments']),
            'rate_limit_statuses': [row['info'].get('status') for row in parsed['rate_limits']],
            'background_event_types': [row['event']['subtype'] for row in parsed['background_events']],
            'post_result_event_types': [row['event']['subtype'] for row in parsed['post_result_events']]}


def _lean_output(entry):
    from do_math.lean_evidence import check_file, parse_evidence
    base = {'stdout': (CORPUS / entry['path']).read_text(encoding='utf-8'), 'declaration_signatures': {},
            'axioms': {}, 'dependency_closure': {}, 'declaration_evidence': {}}
    allowed = sorted({axiom for axioms in entry['verdict']['axioms'].values() for axiom in axioms})
    extract_evidence = entry.get('extract_evidence', False)
    parsed = parse_evidence(base, entry['declarations'], allowed, extract_evidence=extract_evidence)
    judged = {'status': parsed['status'], 'declaration_signatures': parsed['declaration_signatures'],
              'axioms': parsed['axioms']}
    if extract_evidence:
        judged.update({key: parsed[key] for key in
                       ('signature_hash', 'dependency_closure', 'declaration_evidence', 'dependency_evidence')})
    if 'compiled_path' in entry:
        judged['compiled_input_matches'] = check_file(
            (CORPUS / entry['source_path']).read_bytes(), entry['declarations'], extract_evidence=extract_evidence
        ) == (CORPUS / entry['compiled_path']).read_bytes()
    return judged


def _scholarly_config(entry):
    from do_math.scholarly_config import _from_config
    return _from_config(CORPUS / entry['path'])


def _scholarly_stream(entry):
    from do_math.codex_stream import parse_jsonl
    from support.scholarly_live import list_sources_observation
    raw = (CORPUS / entry['path']).read_bytes()
    registry = json.loads((CORPUS / entry['registry_path']).read_bytes())
    parsed = parse_jsonl(raw)
    observed = list_sources_observation(raw, registry['sources'])
    return {**{key: parsed[key] for key in ('turn_completed', 'turn_failed', 'parse_complete')},
            **{key: observed[key] for key in ('tool_id', 'server', 'tool', 'status', 'structured_content_present')},
            'source_ids': sorted(source['id'] for source in observed['sources'])}


def _scheduler_json(entry):
    from subprocess import CompletedProcess
    from do_math.powershell_scheduler import PowerShellScheduler

    def recorded_process(command, **kwargs):
        return CompletedProcess(command, entry['returncode'],
                                (CORPUS / entry['path']).read_text(encoding='utf-8'), '')

    return PowerShellScheduler(runner=recorded_process).run('status', entry['arguments'])


def _cli_surface(entry):
    from subprocess import CompletedProcess
    from do_math.claude_adapter import ADAPTERS
    from do_math.cli_execution import surface_report
    adapter = ADAPTERS[entry['provider']]
    recordings = entry['recordings']
    if len(recordings) != len(adapter.help_commands) + 1:
        raise ValueError('every current help command and the version need a recording')
    results = [CompletedProcess(row['command'], row['exit_code'], (CORPUS / row['path']).read_bytes())
               for row in recordings]
    parsed = surface_report(results[0], [(result, flags) for result, (_, flags) in zip(results[1:], adapter.help_commands)],
                            identity={}, provider=entry['provider'], cli_path=recordings[0]['command'][0],
                            surface=adapter.surface_capabilities, unknown=adapter.unknown_capabilities)
    return {key: parsed[key] for key in ('verified', 'supported', 'scope', 'unknown',
                                       'version_sha256', 'exec_help_sha256')}


READERS = {'codex_stream': _codex_stream, 'claude_stream': _claude_stream, 'lean_output': _lean_output,
           'scholarly_config': _scholarly_config, 'scholarly_stream': _scholarly_stream,
           'scheduler_json': _scheduler_json, 'cli_surface': _cli_surface}


class CorpusReplayTests(unittest.TestCase):
    def scholarly_recording(self):
        entries = json.loads((CORPUS / 'manifest.json').read_bytes())['entries']
        recordings = [entry for entry in entries if entry['kind'] == 'scholarly_stream']
        self.assertTrue(recordings, 'actual list_sources completion must have a recording')
        return recordings

    def test_scholarly_completion_is_bound_to_exact_final_and_worker_isolation(self):
        import hashlib
        from do_math.codex_stream import parse_jsonl
        from do_math.codex_worker import build_argv
        from do_math.provider_final import final_bytes, semantic_output, output_contract
        from jsonschema import Draft202012Validator
        for entry in self.scholarly_recording():
            with self.subTest(entry=entry['id']):
                parsed = parse_jsonl((CORPUS / entry['path']).read_bytes())
                final = (CORPUS / entry['final_path']).read_bytes()
                self.assertEqual(final_bytes(parsed), final)
                schema = json.loads((CORPUS / entry['schema_path']).read_bytes())
                transport = json.loads((CORPUS / entry['transport_schema_path']).read_bytes())
                self.assertEqual(transport, output_contract('codex', schema))
                output = semantic_output('codex', final)
                self.assertEqual(output, {'status': 'CLI_OK', 'nonce': schema['properties']['nonce']['const'], 'phase': 'finished'})
                self.assertEqual(list(Draft202012Validator(schema).iter_errors(output)), [])
                request_raw = (CORPUS / entry['request_path']).read_bytes()
                request = json.loads(request_raw)
                worker = json.loads((CORPUS / entry['worker_status_path']).read_bytes())
                argv = build_argv(request)
                data_dir = str(Path(request['cwd']).resolve() / 'scholarly-data')
                server = request['scholarly_server']
                self.assertIn('mcp_servers.scholarly.args=' + json.dumps(
                    [*server['args'], '--data-dir', data_dir], ensure_ascii=False), argv)
                self.assertEqual(worker['request_sha256'], hashlib.sha256(request_raw).hexdigest())
                self.assertEqual(worker['argv_sha256'], hashlib.sha256('\0'.join(argv).encode('utf-8')).hexdigest())
                self.assertEqual(worker['schema_sha256'], hashlib.sha256((CORPUS / entry['transport_schema_path']).read_bytes()).hexdigest())
                self.assertEqual((worker['state'], worker['cli_exit_code']), ('exited', 0))
                # Replay the captured inputs through the collector's judgment and
                # the runner's semantic receiver, without starting a process.
                from do_math.claude_adapter import ADAPTERS
                from do_math.cli_execution import collection_reasons
                from do_math.codex_stream import provider_observation
                from do_math.model_call import classify_run
                adapter = ADAPTERS['codex']('unused', jobs=None, clock=None)
                raw = (CORPUS / entry['path']).read_bytes()
                parsed = adapter.parse_response(raw, request)
                prompt = (CORPUS / entry['prompt_path']).read_bytes()
                reasons = collection_reasons(worker, parsed, final, request,
                    prompt_sha256=hashlib.sha256(prompt).hexdigest(),
                    request_sha256=hashlib.sha256(request_raw).hexdigest(),
                    schema_sha256=hashlib.sha256((CORPUS / entry['transport_schema_path']).read_bytes()).hexdigest(),
                    final_check=adapter.validate_final)
                self.assertEqual(reasons, [])
                collected = {'result': 'output_collected', 'jsonl': parsed,
                             'provider_observation': provider_observation(request, parsed, raw),
                             'source_request': {'raw': request_raw}, 'final': {'raw': final}}
                result = classify_run(collected, started={}, stopped=False, cli_model=request['model'],
                    claude_only_assigned_model=False, control_binding=None, output_schema=schema,
                    evidence_dir=CORPUS, execution_id=None, reference=None,
                    provider_failure=adapter.provider_failure, now=lambda: entry['recorded_at'])
                self.assertEqual((result['status'], result['output']), ('completed', output))
                self.assertNotIn('error_kind', result)
                self.assertEqual(result['provider_observation']['evidence_sha256'], entry['source_sha256'])
                self.assertEqual(adapter.validate_final(parsed, b'{}'), ['final_response_mismatch'])

    def test_scholarly_started_failed_missing_or_incomplete_response_is_rejected(self):
        from copy import deepcopy
        from support.scholarly_live import list_sources_observation
        for entry in self.scholarly_recording():
            raw = (CORPUS / entry['path']).read_bytes()
            expected = json.loads((CORPUS / entry['registry_path']).read_bytes())['sources']
            original = [json.loads(line) for line in raw.splitlines() if line.strip()]
            completions = [index for index, event in enumerate(original) if event['type'] == 'item.completed'
                           and event.get('item', {}).get('type') == 'mcp_tool_call']
            self.assertEqual(len(completions), 1)
            index = completions[0]
            # Positive control is original bytes, independently checked against registry summaries.
            self.assertEqual(list_sources_observation(raw, expected)['status'], 'ok')
            cases = []
            started = deepcopy(original)
            del started[index]
            cases.append(('start_only', started, '^scholarly requires exactly one start and one completion$'))
            for name, changes, reason in (
                    ('error_completion', {'status': 'failed', 'error': {'message': 'fixture failure'}}, '^scholarly native completion failed$'),
                    ('wrong_id', {'id': 'different-request'}, '^scholarly completion is not bound to its start$'),
                    ('no_result', {'result': None}, '^scholarly MCP result is absent or an error$'),
                    ('other_tool', {'tool': 'fetch'}, '^scholarly probe called an unassigned MCP tool$')):
                events = deepcopy(original)
                events[index]['item'].update(changes)
                cases.append((name, events, reason))
            for name in ('isError', 'empty_content', 'broken_text', 'no_sources', 'missing_source',
                         'duplicate_id', 'missing_summary_field', 'wrong_summary', 'structured_disagrees'):
                events = deepcopy(original)
                result = events[index]['item']['result']
                payload = json.loads(result['content'][0]['text'])
                reason = '^scholarly source summaries differ from the server registry$'
                if name == 'isError':
                    result['isError'] = True
                    reason = '^scholarly MCP result is absent or an error$'
                elif name == 'empty_content':
                    result['content'] = []
                    reason = '^scholarly response must preserve its complete text content$'
                elif name == 'broken_text':
                    result['content'][0]['text'] = '{'
                    reason = '^Expecting property name enclosed in double quotes:'
                else:
                    if name == 'no_sources':
                        del payload['sources']
                        reason = '^scholarly response is not an ok source list$'
                    elif name == 'missing_source':
                        payload['sources'].pop()
                    elif name == 'duplicate_id':
                        payload['sources'].append(deepcopy(payload['sources'][0]))
                        reason = '^scholarly source IDs are missing or duplicated$'
                    elif name == 'missing_summary_field':
                        del payload['sources'][0]['verification']
                    elif name == 'wrong_summary':
                        payload['sources'][0]['implementation'] = 'invented'
                    result['content'][0]['text'] = json.dumps(payload, ensure_ascii=False)
                    if result.get('structured_content') is not None:
                        result['structured_content'] = payload
                    if name == 'structured_disagrees':
                        result['structured_content'] = {'status': 'error'}
                        reason = '^scholarly content and structuredContent disagree$'
                cases.append((name, events, reason))
            for name, events, reason in cases:
                with self.subTest(entry=entry['id'], case=name), self.assertRaisesRegex(ValueError, reason):
                    list_sources_observation(b''.join(json.dumps(event, ensure_ascii=False).encode('utf-8') + b'\n'
                                                    for event in events), expected)
            with self.subTest(entry=entry['id'], case='truncated_stream'), self.assertRaisesRegex(
                    ValueError, '^scholarly stream did not complete successfully$'):
                list_sources_observation(raw[:-10], expected)

    def test_every_entry_parses_to_its_recorded_judgment(self):
        entries = json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
        for entry in entries:
            with self.subTest(entry=entry['id']):
                self.assertIn(entry['kind'], READERS, 'a corpus kind needs a reader')
                self.assertEqual(READERS[entry['kind']](entry), entry['verdict'])

    def test_recorded_schema_rejection_is_an_execution_failure_without_a_final(self):
        from do_math.claude_adapter import ADAPTERS
        from do_math.codex_stream import provider_observation
        from do_math.model_call import classify_run
        from do_math.provider_final import final_bytes
        entries = json.loads((CORPUS / 'manifest.json').read_bytes())['entries']
        # These independent historical verdicts name HTTP 400 invalid_json_schema.
        failures = [entry for entry in entries if entry['kind'] == 'codex_stream'
                    and entry.get('verdict', {}).get('turn_failed')]
        self.assertTrue(failures)
        for entry in failures:
            with self.subTest(entry=entry['id']):
                raw = (CORPUS / entry['path']).read_bytes()
                events = [json.loads(line) for line in raw.splitlines() if line.strip()]
                self.assertTrue(any('invalid_json_schema' in json.dumps(event)
                                    for event in events if event['type'] in ('error', 'turn.failed')))
                adapter = ADAPTERS['codex']('unused', jobs=None, clock=None)
                parsed = adapter.parse_response(raw, {})
                self.assertTrue(parsed['parse_complete'])
                self.assertFalse(parsed['turn_completed'])
                self.assertTrue(parsed['turn_failed'])
                self.assertIsNone(final_bytes(parsed))
                # A layer-2 input with the recorded native failure. This is not
                # a replay of an unrecorded request or a new Job termination.
                collected = {'result': 'incomplete', 'reasons': ['turn_failed'], 'jsonl': parsed,
                             'provider_observation': provider_observation({}, parsed, raw)}
                result = classify_run(collected, started={}, stopped=False, cli_model='unused',
                    claude_only_assigned_model=False, control_binding=None, output_schema={},
                    evidence_dir=CORPUS, execution_id=None, reference=None,
                    provider_failure=adapter.provider_failure, now=lambda: entry['recorded_at'])
                self.assertEqual((result['status'], result['error_kind'], result['error']),
                                 ('failed', 'execution_failure', 'turn_failed'))
                self.assertIsNone(result['output'])
                self.assertNotIn('failure', result)

    def test_historical_preinit_and_cleanup_select_the_native_submission(self):
        from do_math.claude_adapter import ClaudePrintAdapter
        from do_math.provider_final import final_bytes, semantic_output
        entries = {entry['id']: entry for entry in json.loads((CORPUS / 'manifest.json').read_bytes())['entries']}
        adapter = ClaudePrintAdapter('unused', jobs=None, clock=None)
        for identifier in ('claude-rate-before-init-21276', 'claude-terminal-cleanup-21276'):
            with self.subTest(entry=identifier):
                entry = entries[identifier]
                raw = (CORPUS / entry['path']).read_bytes()
                native = [json.loads(line) for line in raw.splitlines() if line.strip()]
                parsed = adapter.parse_response(raw, {'output_schema_path': 'recorded-probe-schema'})
                self.assertTrue(parsed['parse_complete'])
                self.assertTrue(parsed['turn_completed'])
                self.assertFalse(parsed['turn_failed'])
                self.assertIsNone(adapter.provider_failure(parsed))
                final = json.dumps(entry['verdict']['structured_output'], ensure_ascii=False).encode('utf-8')
                self.assertEqual(final_bytes(parsed), final)
                self.assertEqual(adapter.validate_final(parsed, final), [])
                self.assertEqual(semantic_output('claude', final), entry['verdict']['structured_output'])
                if identifier == 'claude-rate-before-init-21276':
                    self.assertEqual(native[0]['type'], 'rate_limit_event')
                    self.assertEqual(native[1]['subtype'], 'init')
                    self.assertEqual(parsed['rate_limits'][0]['line'], 1)
                else:
                    self.assertFalse(entry['live_passed'])
                    self.assertEqual(semantic_output('claude', final)['phase'], 'pending')
                    self.assertEqual(parsed['selected_result']['result_line'], 10)
                    self.assertEqual([row['event']['subtype'] for row in parsed['post_result_events']],
                                     ['background_tasks_changed', 'task_updated', 'task_notification'])
                    self.assertEqual(parsed['post_result_events'][-1]['event']['status'], 'stopped')
                # Synthetic truncation of a positive raw control is a refusal
                # test; it is not a separately recorded external incident.
                truncated = adapter.parse_response(raw[:-1], {'output_schema_path': 'recorded-probe-schema'})
                self.assertFalse(truncated['parse_complete'])
                self.assertFalse(truncated['turn_completed'])
                self.assertIn('incomplete_jsonl_line', truncated['unknown_events'])
                self.assertIsNone(final_bytes(truncated))

    def test_recorded_scholarly_client_timeouts_are_not_inherited_by_the_worker(self):
        import tempfile
        import tomllib
        from do_math.codex_worker import build_argv
        from do_math.scholarly_config import resolve_scholarly_server
        entries = json.loads((CORPUS / 'manifest.json').read_bytes())['entries']
        recordings = [entry for entry in entries if entry['kind'] == 'scholarly_config']
        self.assertTrue(recordings)
        for entry in recordings:
            with self.subTest(entry=entry['id']), tempfile.TemporaryDirectory() as directory:
                raw = (CORPUS / entry['path']).read_bytes()
                table = tomllib.loads(raw.decode('utf-8'))['mcp_servers']['scholarly']
                self.assertEqual((table['startup_timeout_sec'], table['tool_timeout_sec']), (30, 1800))
                root = Path(directory)
                (root / '.codex').mkdir()
                (root / '.codex/config.toml').write_bytes(raw)
                server = resolve_scholarly_server(None, start=root, codex_home=root / 'unused-home')
                self.assertEqual(server, entry['verdict'])
                # Reuse the actual recorded worker request as the consumer input;
                # only replace its scholarly command/args with the resolved pair.
                for stream in self.scholarly_recording():
                    request = json.loads((CORPUS / stream['request_path']).read_bytes())
                    argv = build_argv({**request, 'scholarly_server': server})
                    data_dir = str(Path(request['cwd']).resolve() / 'scholarly-data')
                    self.assertIn('mcp_servers.scholarly.command=' + json.dumps(server['command']), argv)
                    self.assertIn('mcp_servers.scholarly.args=' + json.dumps(
                        [*server['args'], '--data-dir', data_dir], ensure_ascii=False), argv)
                    self.assertFalse(any('startup_timeout_sec' in arg or 'tool_timeout_sec' in arg for arg in argv))

    def test_maintenance_recordings_keep_the_role_schema_and_exact_selected_final(self):
        from jsonschema import Draft202012Validator
        from do_math.claude_adapter import ADAPTERS
        from do_math.claude_stream import parse_stream
        from do_math.codex_stream import parse_jsonl
        from do_math.contracts import action_schema
        from do_math.provider_final import final_bytes, output_contract, semantic_output
        entries = [entry for entry in json.loads((CORPUS / 'manifest.json').read_text(encoding='utf-8'))['entries']
                   if entry['role'] == 'maintenance']
        self.assertEqual({entry['kind'].removesuffix('_stream') for entry in entries}, set(ADAPTERS))
        for entry in entries:
            with self.subTest(entry=entry['id']):
                schema = json.loads((CORPUS / entry['schema_path']).read_bytes())
                self.assertEqual(schema, action_schema({'role': 'maintenance'}))
                parser = parse_jsonl if entry['kind'] == 'codex_stream' else parse_stream
                parsed = parser((CORPUS / entry['path']).read_bytes())
                final = final_bytes(parsed)
                if entry['verdict']['turn_completed']:
                    self.assertFalse(parsed['turn_failed'])
                    self.assertEqual(final, (CORPUS / entry['final_path']).read_bytes())
                    output = semantic_output(entry['kind'].removesuffix('_stream'), final)
                    self.assertEqual(list(Draft202012Validator(schema).iter_errors(output)), [])
                    if entry['kind'] == 'claude_stream':
                        from do_math.claude_stream import provider_limit
                        from do_math.codex_stream import provider_observation
                        from do_math.model_call import classify_run
                        # The semantic receiver's layer-2 input, built from the
                        # recorded stdout/final. No new worker/Job is asserted.
                        raw = (CORPUS / entry['path']).read_bytes()
                        collected = {'result': 'output_collected', 'jsonl': parsed,
                                     'provider_observation': provider_observation({}, parsed, raw),
                                     'source_request': {'raw': b'{"claude_path":"unused"}'},
                                     'final': {'raw': final}}
                        result = classify_run(collected, started={}, stopped=False, cli_model=entry['model'],
                            claude_only_assigned_model=False, control_binding=None, output_schema=schema,
                            evidence_dir=CORPUS, execution_id=None, reference=None,
                            provider_failure=provider_limit, now=lambda: entry['recorded_at'])
                        self.assertIsNone(provider_limit(parsed))
                        self.assertEqual((result['status'], result['output']), ('completed', output))
                        self.assertEqual(result['selected_result'], parsed['selected_result'])
                        self.assertEqual(result['usage'], parsed['usage_total'])
                    if 'transport_schema_path' in entry:
                        transport = json.loads((CORPUS / entry['transport_schema_path']).read_bytes())
                        self.assertEqual(transport, output_contract('codex', schema))
                        self.assertEqual(list(Draft202012Validator(transport).iter_errors(json.loads(final))), [])
                        self.assertEqual(output, entry['semantic_output'])
                        worker = json.loads((CORPUS / entry['worker_status_path']).read_bytes())
                        self.assertEqual(worker['schema_sha256'], entry['transport_schema_sha256'])
                        self.assertEqual(worker['argv_sha256'], entry['command_sha256'])
                        self.assertEqual((worker['state'], worker['cli_exit_code']), ('exited', 0))
                else:
                    self.assertTrue(parsed['turn_failed'])
                    self.assertFalse(entry['live_passed'])
                    self.assertIsNone(final)


if __name__ == '__main__':
    unittest.main()
