"""Every contract pair (설계 3.3; 의무 1-A, 1-C): each producer branch passes its receiving check, and the
receiver names no field that no producer branch writes. Branches a receiver rejects today are the known
defects below, each with its own reproduction."""
from copy import deepcopy
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from contracts.pairs import (PAIRS, TEXT_RULE_ID_SAMPLES, accepted_condition, accepted_rule_ids, enumerated_pointers,
                             stored_rule_id_errors, worker_request_run, worker_request_runs)


class ContractPairTests(unittest.TestCase):
    def test_runner_samples_cover_success_bound_incomplete_and_stopped(self):
        """Eight real results also retain their receipts through both JSON consumers.

        The external Job/CLI fakes leave the producer and serializers real (~0.4s locally).
        """
        pair = next(pair for pair in PAIRS if pair.name == 'runner result (stored artifact)')
        receivers = [pair for pair in PAIRS if pair.name.startswith('runner result (')]
        self.assertEqual(len(receivers), 2)
        expected = {
            'collected': ('completed', {}, None, None, 'output_collected'),
            'collected, bound': ('completed', None, 'provider_evidence_only', None, 'output_collected'),
            'incomplete': ('failed', None, None, 'execution_failure', 'incomplete'),
            'stopped': ('stopped', None, None, 'execution_failure', 'output_collected'),
        }
        with tempfile.TemporaryDirectory() as directory:
            samples = pair.samples(Path(directory))
        self.assertEqual([label for label, _ in samples],
                         [provider + ', ' + branch for provider in ('codex', 'claude') for branch in expected])
        for label, result in samples:
            with self.subTest(branch=label):
                branch = label.split(', ', 1)[1]
                self.assertEqual((result['status'], result['output'], result.get('collection'),
                                  result.get('error_kind'), result['execution']['collect']['result']), expected[branch])
                collected = result['execution']['collect']
                self.assertEqual(collected['reasons'], ['cli_nonzero_exit'] if branch == 'incomplete' else [])
                self.assertEqual(result['error'], 'cli_nonzero_exit' if branch == 'incomplete' else
                                 'stop requested or timeout' if branch == 'stopped' else None)
                self.assertTrue(collected['termination_barrier']['confirmed'])
                for name in ('source_request', 'source_prompt', 'stdout', 'stderr', 'final'):
                    artifact = collected[name]
                    self.assertEqual(artifact['bytes'], len(artifact['raw']))
                    self.assertEqual(artifact['sha256'], hashlib.sha256(artifact['raw']).hexdigest())
                request = json.loads(collected['source_request']['raw'])
                self.assertEqual('control_binding' in request, branch == 'collected, bound')
                if branch == 'collected, bound':
                    self.assertEqual(request['control_binding']['execution_id'], result['execution_id'])
                    self.assertEqual(collected['final']['raw'], b'Draft submitted.')
                for receiver in receivers:
                    with self.subTest(receiver=receiver.name):
                        stored = receiver.receive(deepcopy(result))
                        self.assert_received_runner_result(label, result, stored, expected[branch],
                                                           artifact=receiver.name == pair.name)

    def assert_received_runner_result(self, label, result, stored, expected, *, artifact):
        """Compare decoded consumer output with fixture semantics and exact collected bytes.

        Expectations do not call json_safe, bytes_evidence or either receiving serializer.
        """
        provider, branch = label.split(', ', 1)
        bound = branch == 'collected, bound'
        self.assertEqual(set(stored), set(result), 'preserve absent fields as well as present nulls')
        self.assertEqual((stored['status'], stored['output'], stored.get('collection'),
                          stored.get('error_kind'), stored['execution']['collect']['result']), expected)
        self.assertEqual('collection' in stored, bound)
        self.assertEqual('error_kind' in stored, branch in ('incomplete', 'stopped'))
        self.assertEqual(stored['error'], 'cli_nonzero_exit' if branch == 'incomplete' else
                         'stop requested or timeout' if branch == 'stopped' else None)
        for name in ('evidence_dir', 'assigned_model', 'execution_id', 'profile_ref', 'provider_observation'):
            self.assertEqual(stored[name], result[name])
        self.assertEqual(stored['usage'], {'input_tokens': 1, 'output_tokens': 1} if provider == 'codex' else
                         {'input_tokens': 7, 'output_tokens': 3})
        self.assertEqual(set(stored['execution']), {'started', 'collect'})
        self.assertEqual(stored['execution']['started'], result['execution']['started'])
        collected, received = result['execution']['collect'], stored['execution']['collect']
        self.assertEqual(set(received), set(collected))
        for name in ('worker_status', 'process_identity', 'stop_receipts',
                     'provider_observation', 'result', 'reasons', 'execution_id', 'profile_ref'):
            self.assertEqual(received[name], collected[name])
        self.assertEqual(received['worker_argv'], list(collected['worker_argv']))
        self.assertEqual(received['termination_barrier'], {'active_processes': 0, 'process_ids': [],
                                                         'root_signaled': True, 'confirmed': True})
        self.assertIsNone(received['host_resources'])
        self.assertEqual('execution_id' in received['worker_status'], bound)
        self.assertEqual('profile_ref' in received['worker_status'], bound)
        if bound:
            self.assertEqual(received['execution_id'], 'EX-pair')
            self.assertIsNone(received['worker_status']['schema_sha256'])
        else:
            self.assertIsNone(stored['execution_id'])
            self.assertIsNone(stored['profile_ref'])
            self.assertIsNone(received['execution_id'])
            self.assertIsNone(received['profile_ref'])
        for name in ('source_request', 'source_prompt', 'stdout', 'stderr', 'final'):
            raw = collected[name]['raw']
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(received[name], {'present': True, 'bytes': len(raw), 'sha256': digest,
                'raw': {'sha256': digest, 'text': raw.decode('utf-8', 'replace'),
                        'base64': base64.b64encode(raw).decode('ascii')}})
        parsed = received['jsonl']
        self.assertTrue(parsed['parse_complete'])
        self.assertEqual(parsed['unknown_events'], [])
        self.assertEqual('total_cost_usd' in parsed, provider == 'claude')
        if provider == 'claude':
            self.assertEqual(parsed['total_cost_usd'], {'reported_decimal': '0.0123'} if artifact else 0.0123)
            for selected in (parsed['selected_result'], stored['selected_result']):
                self.assertIsNone(selected['origin'])
                self.assertIsNone(selected['num_turns'])
            self.assertEqual(stored['model_usage_reported'], {'claude-sonnet-5': {'inputTokens': 1}})
            self.assertEqual(stored['usage_segments'], [{'segment': 0, 'line': 2,
                'usage': {'input_tokens': 7, 'output_tokens': 3}}])
            expected_parsed = deepcopy(collected['jsonl'])
            expected_parsed['total_cost_usd'] = {'reported_decimal': '0.0123'} if artifact else 0.0123
            self.assertEqual(parsed, expected_parsed)
        else:
            self.assertNotIn('selected_result', stored)
            self.assertNotIn('model_usage_reported', stored)
            self.assertEqual(parsed, collected['jsonl'])

    def test_every_producer_branch_is_received_and_every_named_field_is_produced(self):
        """All pairs, including forty real worker requests and two sets of eight results (~4.5s locally).

        Storing and receiving real producer values is necessary for the reverse field contract.
        """
        self.assertGreater(len(PAIRS), 0)
        for pair in PAIRS:
            with self.subTest(pair=pair.name), tempfile.TemporaryDirectory() as directory:
                samples = pair.samples(Path(directory))
                self.assertGreater(len(samples), 0, 'a pair needs producer samples')
                rejected = []
                for branch, value in samples:
                    try:
                        pair.receive(deepcopy(value))
                    except ValueError as error:
                        rejected.append((branch, str(error)))
                self.assertEqual(rejected, [], 'producer branches the receiving check rejects')
                if pair.fields is not None:
                    written = set().union(*(pair.written(value) for _, value in samples))
                    self.assertEqual(sorted(pair.fields - written), [],
                                     'fields the receiving check names that no producer branch writes')


    def test_worker_samples_preserve_both_assigned_model_flags_for_each_legal_assignment(self):
        """Twenty real runs per provider preserve assignments, snapshots and CLI tool/lock semantics.

        The runner must store and collect each branch; pure request dictionaries cannot establish this contract.
        Forty file/worker/CLI/collector runs took ~2.4s locally, above the pure contract budget.
        """
        from do_math.claude_adapter import ADAPTERS
        prefix = 'worker request ('
        pairs = {pair.name[len(prefix):-1]: pair for pair in PAIRS if pair.name.startswith(prefix)}
        self.assertEqual(set(pairs), set(ADAPTERS))
        for provider, pair in pairs.items():
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                assignments = {}
                for label, run in worker_request_runs(Path(directory), provider):
                    with self.subTest(branch=label):
                        self.assert_worker_run(provider, run)
                    request = run['request']
                    flags = label.split(',') if label != 'bare' else []
                    only = 'claude_only' in flags
                    key = tuple(flag for flag in flags if flag != 'claude_only')
                    choices = assignments.setdefault(key, {})
                    self.assertNotIn(only, choices, (provider, label))
                    choices[only] = run
                self.assertEqual(len(assignments), 10, 'twenty legal inputs per provider, paired by lock')
                for assignment, choices in assignments.items():
                    with self.subTest(assignment=assignment):
                        self.assertEqual(set(choices), {False, True})
                        unlocked, locked = choices[False], choices[True]
                        # Exact identity/ref/binding checks above precede this comparison.
                        # Lock changes a pinned profile's edition; it must not be normalized as an equal ref.
                        if unlocked['profile'] is not None:
                            self.assertNotEqual(unlocked['request']['profile_ref'], locked['request']['profile_ref'])
                        expected = self.request_without_run_paths(unlocked)
                        if provider == 'claude':
                            expected['claude_only_assigned_model'] = True
                        self.assertEqual(self.request_without_run_paths(locked), expected)
                        if provider == 'codex':
                            # The only different CLI paths are the final file and private schema snapshot.
                            commands = []
                            for run in (unlocked, locked):
                                command = list(run['jobs'].cli.calls[0]['command'])
                                for flag in ('--output-last-message', '--output-schema'):
                                    if flag in command:
                                        command[command.index(flag) + 1] = flag + '-per-run-path'
                                commands.append(command)
                            self.assertEqual(*commands, 'Codex lock has no CLI argv effect')
                            self.assertEqual(unlocked['jobs'].cli.calls[0]['stdin'], locked['jobs'].cli.calls[0]['stdin'])

    @staticmethod
    def request_without_run_paths(run):
        """Remove only checked profile refs and per-call evidence paths for the lock effect comparison.

        Workspace, tools and control bindings remain exact (the runs share these inputs).
        """
        request = deepcopy(run['request'])
        request.pop('profile_ref', None)
        for key in ('prompt_path', 'stdout_path', 'stderr_path', 'status_path', 'final_path', 'output_schema_path'):
            if key in request:
                request[key] = key + '-per-run-path'
        return request

    def assert_worker_run(self, provider, run):
        """Check fixture inputs against stored files and the existing external fakes while paths still exist."""
        from do_math import claude_worker, codex_worker
        from do_math.control_server import mcp_server_config
        from do_math.execution_profiles import profile_ref, prompt_seal
        from do_math.provider_final import output_contract
        worker = codex_worker if provider == 'codex' else claude_worker
        request, staged, jobs = run['request'], run['staged'], run['jobs']
        self.assertTrue(Path(request['prompt_path']).is_file(),
                        'worker samples must come from the runner saved input')
        self.assertEqual(worker.load_request(run['request_path']), request)
        self.assertEqual(worker.load_request(run['staged_path']), staged)
        self.assertEqual(len(jobs.launched), 1)
        job = jobs.launched[0]
        self.assertEqual(Path(job.argv[1]).name, provider + '_worker.py')
        self.assertEqual(job.argv[2], str(run['staged_path']))
        self.assertTrue(job.resumed and job.done and job.closed)
        self.assertEqual(job.exit_code, 0)
        self.assertEqual(job.terminations, 0)
        self.assertEqual(job.resource_limits, run['resource_limits'])
        self.assertEqual(len(jobs.cli.calls), 1)
        call = jobs.cli.calls[0]
        command = call['command']
        self.assertFalse(call['shell'])
        self.assertEqual(call['cwd'], request['cwd'])
        self.assertEqual(command[0], request[provider + '_path'])
        self.assertEqual(command[command.index('--model') + 1], run['model'].removeprefix('claude:'))
        self.assertEqual(request['model'], run['model'].removeprefix('claude:'))
        self.assertEqual(request['effort'], run['effort'])
        self.assertEqual(request['max_runtime_seconds'], 600)
        prompt_raw = run['prompt'].encode('utf-8')
        self.assertEqual(Path(request['prompt_path']).read_bytes(), prompt_raw)
        self.assertEqual(Path(staged['prompt_path']).read_bytes(), prompt_raw)
        self.assertEqual(call['stdin'], prompt_raw)
        self.assertNotEqual(request['prompt_path'], staged['prompt_path'])
        expected_staged = deepcopy(request)
        expected_staged['prompt_path'] = staged['prompt_path']
        profile = run['profile']
        if profile is None:
            for key in ('execution_id', 'profile_ref', 'resource_limits', 'control_binding'):
                self.assertNotIn(key, request)
            self.assertIsNone(run['ticket'])
        else:
            self.assertEqual(profile['role'], 'research_work')
            self.assertEqual(profile['actor_kind'], 'ai')
            self.assertEqual(profile['ai']['model'], run['model'])
            self.assertEqual(profile['ai']['effort'], run['effort'])
            self.assertEqual(profile['ai']['scholarly_server'], run['server'])
            self.assertEqual(profile['ai']['claude_only_assigned_model'], run['only'])
            self.assertEqual(request['execution_id'], run['execution_id'])
            self.assertEqual(request['profile_ref'], profile_ref(profile))
            self.assertEqual(job.name, run['ticket']['job_name'])
        if run['resource_limits'] is None:
            self.assertNotIn('resource_limits', request)
            self.assertEqual(run['publications'], [])
        else:
            self.assertEqual(request['resource_limits'], run['resource_limits'])
            self.assertEqual(len(run['publications']), 1)
            publication = run['publications'][0]
            self.assertFalse(publication['resumed'])
            self.assertEqual(publication['cli_calls'], 0)
            self.assertEqual(publication['started']['execution_id'], run['execution_id'])
            self.assertEqual(publication['started']['profile_ref'], profile_ref(profile))
            self.assertEqual(publication['started']['host_resources']['limits'], run['resource_limits'])
            self.assertEqual(publication['started'], run['result']['execution']['started'])
        if run['binding'] is None:
            self.assertNotIn('control_binding', request)
            self.assertIn('output_schema_path', request)
            expected_schema = output_contract(provider, run['schema'])
            self.assertEqual(json.loads(Path(request['output_schema_path']).read_bytes()), expected_schema)
            self.assertEqual(Path(staged['output_schema_path']).read_bytes(),
                             Path(request['output_schema_path']).read_bytes())
            self.assertNotEqual(request['output_schema_path'], staged['output_schema_path'])
            expected_staged['output_schema_path'] = staged['output_schema_path']
            self.assertEqual(json.loads((run['request_path'].parent / 'output.schema.json').read_bytes()), run['schema'])
            if provider == 'codex':
                self.assertEqual(command[command.index('--output-schema') + 1], staged['output_schema_path'])
            else:
                self.assertEqual(json.loads(command[command.index('--json-schema') + 1]), run['schema'])
        else:
            self.assertEqual(request['control_binding'], run['binding'])
            self.assertEqual(request['control_binding']['execution_id'], run['execution_id'])
            self.assertEqual(request['control_binding']['workspace'], request['cwd'])
            self.assertNotIn('output_schema_path', request)
            self.assertFalse((run['request_path'].parent / 'output.schema.json').exists())
            self.assertNotIn('--output-schema', command)
            self.assertNotIn('--json-schema', command)
            self.assertEqual(run['result']['collection'], 'provider_evidence_only')
        self.assertEqual(staged, expected_staged, 'only prompt/schema paths change during staging')
        server = run['server']
        if server is None:
            self.assertNotIn('scholarly_server', request)
        else:
            self.assertEqual(request['scholarly_server'], server)
        if provider == 'codex':
            config = dict(command[i + 1].split('=', 1) for i, arg in enumerate(command) if arg == '--config')
            self.assertEqual(json.loads(config['model_reasoning_effort']), run['effort'])
            self.assertNotIn('claude_only_assigned_model', request)
            servers = {name: {key: json.loads(config[f'mcp_servers.{name}.{key}']) for key in ('command', 'args')}
                       for name in ('execution_control', 'scholarly') if f'mcp_servers.{name}.command' in config}
        else:
            self.assertEqual(command[command.index('--effort') + 1], run['effort'])
            self.assertEqual('claude_only_assigned_model' in request, run['only'])
            if run['only']:
                self.assertIs(request['claude_only_assigned_model'], True)
            settings = json.loads(command[command.index('--settings') + 1])
            expected_settings = {'disableAllHooks': True, 'autoMemoryEnabled': False}
            if run['only']:
                model = run['model'].removeprefix('claude:')
                expected_settings.update(availableModels=[model], fallbackModel=[], switchModelsOnFlag=False,
                                         env={'ANTHROPIC_DEFAULT_HAIKU_MODEL': model,
                                              'CLAUDE_CODE_SUBAGENT_MODEL': model,
                                              'CLAUDE_CODE_SUBAGENT_MODEL_FORCE': '1'})
            self.assertEqual(settings, expected_settings)
            servers = json.loads(command[command.index('--mcp-config') + 1])['mcpServers']
        expected_servers = {}
        if run['binding'] is not None:
            expected_servers['execution_control'] = mcp_server_config(run['binding'])
        if server is not None:
            expected_servers['scholarly'] = {**server, 'args': [*server['args'], '--data-dir',
                                                              str(Path(request['cwd']) / 'scholarly-data')]}
        self.assertEqual(servers, expected_servers)
        result = run['result']
        self.assertEqual(result['status'], 'completed')
        collected = result['execution']['collect']
        self.assertEqual(collected['result'], 'output_collected')
        self.assertEqual(collected['reasons'], [])
        self.assertTrue(collected['termination_barrier']['confirmed'])
        status = json.loads(Path(request['status_path']).read_bytes())
        self.assertEqual(status['state'], 'exited')
        self.assertEqual(status['cli_exit_code'], 0)
        self.assertEqual(status['request_sha256'], hashlib.sha256(run['staged_path'].read_bytes()).hexdigest())
        self.assertEqual(status['stdin_sha256'], prompt_seal(run['prompt'])['sha256'])
        self.assertEqual(status['argv_sha256'], hashlib.sha256('\0'.join(command).encode('utf-8')).hexdigest())
        self.assertEqual(status['schema_sha256'], hashlib.sha256(Path(staged['output_schema_path']).read_bytes()).hexdigest()
                         if 'output_schema_path' in staged else None)
        for key in ('execution_id', 'profile_ref'):
            self.assertEqual(key in status, profile is not None)
            if profile is not None:
                self.assertEqual(status[key], request[key])
        self.assertEqual(collected['source_request']['raw'], run['staged_path'].read_bytes())

    def test_scholarly_args_zero_one_and_many_reach_both_worker_commands(self):
        """Six stored calls (~0.4s locally) are needed to check ordered args at both actual worker CLI seams."""
        for provider in ('codex', 'claude'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                absolute_server = str(root / 'server.py')
                for index, args in enumerate(([], [absolute_server], [absolute_server, '--flag'])):
                    with self.subTest(args=args):
                        run = worker_request_run(root, provider, identity=True, limits=True, control=True,
                                                 scholarly=True, only=True, scholarly_args=args,
                                                 evidence_name='args-' + str(index))
                        self.assertEqual(run['server']['args'], args)
                        self.assert_worker_run(provider, run)


class KnownPairDefectTests(unittest.TestCase):
    def test_every_rule_id_the_tracker_accepts_is_storable(self):
        for rule_id, value in accepted_rule_ids(TEXT_RULE_ID_SAMPLES):
            with self.subTest(rule_id=rule_id):
                self.assertEqual(stored_rule_id_errors(value), [])

    def test_the_condition_grammar_rejects_values_outside_every_stored_enumeration(self):
        for family, space, pointer, enumeration in enumerated_pointers():
            with self.subTest(pointer=family + pointer):
                self.assertFalse(accepted_condition(space, family, pointer, 'not-a-stored-value'))


if __name__ == '__main__':
    unittest.main()
