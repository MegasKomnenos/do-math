"""A runner pinned to an execution profile (``model_runner``, layer 3, with ``model_call.runner_assignment``).

A pinned call carries its execution ID, the dispatched launch ticket of the
Jobs port's owner, and the UTF-8 seal of its prompt. The profile alone
supplies the call's tools, model lock and deadline window. The worker, the CLI
command and the collection are real (``support.provider_runs``).
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from do_math import claude_worker, codex_worker
from do_math.canonical import exact_content_hash
from do_math.codex_adapter import LocalCLIAdapter
from do_math.configuration import DEFAULT_CONFIG
from do_math.context_store import prepare_role_input
from do_math.contracts import schema_for
from do_math.control_server import mcp_server_config
from do_math.control_transport import ControlTransport
from do_math.execution_profiles import (WINDOW_KEYS, boundary_prompt, build_profiles, execution_observation,
                                        prepare_prompt, profile_ref, prompt_seal, seal_profile)
from do_math.windows_job import WindowsJobUnsupportedError
from do_math.worker_request import validate_execution_binding
from support.provider_inputs import CLAUDE_INIT, CLAUDE_RESULT, PROFILE_CONFIG, claude_stream
from support.record_builders import surface_state
from support.fakes.clock import FakeClock
from support.provider_probes import ObservedCalls
from support.provider_runs import ProviderJobs, ScriptedCLI, claude_result, dispatched, model_runner


def role_profile(config, role):
    from support.entry import entry
    _entry = entry()
    return next(p for p in build_profiles(config, host=_entry.ports.host)['execution_profiles'].values() if p['role'] == role)


class PinnedCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()

    def run_pinned(self, profile, execution_id, *, jobs=None, prompt=None, evidence='evidence', workspace='ws',
                   **options):
        """``(result, jobs)`` of one call pinned to ``profile`` under its dispatched ticket and prompt seal."""
        jobs = jobs or ProviderJobs(clock=self.clock)
        (self.root / workspace).mkdir(exist_ok=True)
        prompt = prepare_prompt('fixture', profile) if prompt is None else prompt
        options = {'output_schema': {}, 'timeout_seconds': 1, 'input_seal': prompt_seal(prompt), **options}
        result = model_runner(self.root, jobs, self.clock).run(
            prompt=prompt, workspace=self.root / workspace, evidence_dir=self.root / evidence,
            model=profile['ai']['model'], effort=profile['ai']['effort'], execution_id=execution_id, profile=profile,
            launch_ticket=dispatched(execution_id, profile, jobs, self.clock), **options)
        return result, jobs


class ModelLockTests(PinnedCase):
    def test_claude_lock_in_pinned_profile_keeps_codex_request_valid(self):
        profile = role_profile({**DEFAULT_CONFIG, 'claude_only_assigned_model': True, 'scholarly_enabled': False},
                               'maintenance')
        self.assertTrue(profile['ai']['claude_only_assigned_model'])
        result, jobs = self.run_pinned(profile, 'EX-codex-lock')
        request = codex_worker.load_request(self.root / 'evidence' / 'request.json')
        self.assertNotIn('claude_only_assigned_model', request)
        self.assertEqual(request['profile_ref'], profile_ref(profile))
        self.assertEqual(result['status'], 'completed')
        # The Codex worker accepted the request it ran and started its CLI once.
        self.assertEqual(len(jobs.cli.calls), 1)


class RequestPinTests(PinnedCase):
    def test_work_has_no_deadline_and_operations_keep_their_call_window(self):
        from support.entry import entry
        _entry = entry()
        profiles = build_profiles(PROFILE_CONFIG, host=_entry.ports.host)['execution_profiles']
        for role, timeout in (('research_work', None), ('operational_review', 600)):
            profile = next(p for p in profiles.values() if p['role'] == role)
            self.assertEqual(set(profile['window']), set(WINDOW_KEYS))
            result, jobs = self.run_pinned(profile, 'EX-' + role, evidence=role, timeout_seconds=timeout)
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(self.request(role)['max_runtime_seconds'], timeout)
            self.assertEqual(json.loads(Path(jobs.launched[0].argv[2]).read_text(encoding='utf-8'))['max_runtime_seconds'],
                             timeout)
            if role == 'operational_review':
                for invalid in (None, PROFILE_CONFIG['call_timeout_seconds'] + 1):
                    with self.assertRaisesRegex(ValueError, 'runner deadline exceeds the pinned profile'):
                        self.run_pinned(profile, 'EX-' + role, evidence=role + '-over', timeout_seconds=invalid)
                    self.assertFalse((self.root / (role + '-over')).exists())

    def request(self, evidence='evidence'):
        return json.loads((self.root / evidence / 'request.json').read_text(encoding='utf-8'))

    def test_runner_pins_request_and_exposes_reported_evidence(self):
        # A Claude stream reports its stop reason and usage; a Codex stream has no such surface.
        profile = role_profile({**PROFILE_CONFIG, 'tier_models': {tier: 'claude-opus-5' for tier in ('high', 'medium', 'low')},
                                'session_limits': {'work': {'claude-opus-5': 3}}}, 'research_work')
        cli = ScriptedCLI(stdout=claude_stream(CLAUDE_INIT, claude_result(b'{}', usage={'output_tokens': 3},
                                                                          stop_reason='end_turn')))
        result, _ = self.run_pinned(profile, 'EX-bound', jobs=ProviderJobs(cli, clock=self.clock), timeout_seconds=600)
        request = self.request()
        self.assertEqual(request['execution_id'], 'EX-bound')
        self.assertEqual(request['profile_ref'], profile_ref(profile))
        self.assertEqual(result['status'], 'completed')
        observation = result['provider_observation']
        self.assertEqual(observation['stop_reason'], 'end_turn')
        self.assertEqual(observation['remote_termination'], 'unknown')
        self.assertEqual(observation['usage_scope'], 'reported_execution_counters_not_invoice')
        self.assertEqual(observation['usage'], {'output_tokens': 3})
        self.assertEqual(result['execution_id'], 'EX-bound')

    def test_runner_preserves_exact_utf8_input_after_seal(self):
        p = role_profile({**PROFILE_CONFIG, 'lean_command': ['lean-A']}, 'maintenance')
        text = 'exact input\n한글\n' + boundary_prompt(p)
        seal = {'bytes': len(text.encode('utf-8')), 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}
        result, jobs = self.run_pinned(p, 'EX-exact', prompt=text, input_seal=seal)
        self.assertEqual((self.root / 'evidence' / 'input.txt').read_bytes(), text.encode('utf-8'))
        # The CLI read exactly those bytes on its standard input.
        self.assertEqual(jobs.cli.calls[0]['stdin'], text.encode('utf-8'))
        with self.assertRaisesRegex(ValueError, 'runner input differs from its UTF-8 seal'):
            self.run_pinned(p, 'EX-exact', prompt=text + 'extra', input_seal=seal, evidence='changed')
        self.assertFalse((self.root / 'changed').exists())
        with self.assertRaisesRegex(ValueError, 'runner input differs from its UTF-8 seal'):
            self.run_pinned(p, 'EX-exact', prompt=text, input_seal=None, evidence='missing')
        self.assertFalse((self.root / 'missing').exists())

    def test_surface_seal_and_runner_deliver_identical_complete_input(self):
        from support.entry import entry
        _entry = entry()
        schema = schema_for('research_preparation')
        state, runtime = surface_state()
        p = next(p for p in state['execution_profiles'].values() if p['role'] == 'research_preparation')
        workspace = self.root / 'ws'
        workspace.mkdir()
        fitted = prepare_role_input({'action': {}, 'resources': {}, 'knowledge_catalog': [], 'blocked_actions': []},
                                    instance=state, runtime=runtime, role='research_preparation', profile=p,
                                    snapshot='a' * 40, workspace=workspace, activity_id='AC-1', output_schema=schema,
                                    artifact_prefix='runtime/artifacts/EX-seal', clock=_entry.ports.clock)
        self.assertIsNone(fitted['overflow'])
        prompt = fitted['prompt']
        self.assertEqual(prompt.count(boundary_prompt(p)), 1)
        expected = prompt_seal(prompt)
        self.assertEqual({k: fitted['manifest']['prompt'][k] for k in expected}, expected)
        _, jobs = self.run_pinned(p, 'EX-seal', prompt=prompt, input_seal=fitted['manifest']['prompt'],
                                  output_schema=schema)
        delivered = fitted['artifacts'][fitted['manifest']['prompt']['artifact_ref']]
        self.assertEqual((self.root / 'evidence' / 'input.txt').read_bytes(), delivered)
        self.assertEqual(jobs.cli.calls[0]['stdin'], delivered)


class ControlBindingTests(PinnedCase):
    def test_execution_control_binding_reaches_both_workers_and_is_checked(self):
        profile = role_profile({**PROFILE_CONFIG, 'scholarly_server': {
            'command': sys.executable, 'args': [str(Path(__file__).resolve())]}}, 'research_work')
        transport = ControlTransport(self.root / 'transport', clock=self.clock)
        binding = transport.issue('EX-bound', 'GR-bound', self_check=True)  # a research work execution
        result, jobs = self.run_pinned(profile, 'EX-bound', timeout_seconds=600, control_binding=binding)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['collection'], 'provider_evidence_only')
        snapshot = json.loads(Path(jobs.launched[0].argv[2]).read_text(encoding='utf-8'))
        self.assertEqual(snapshot['control_binding'], binding)
        request = codex_worker.load_request(self.root / 'evidence' / 'request.json')
        self.assertEqual(request['control_binding'], binding)
        config = mcp_server_config(binding)
        registered = ['mcp_servers.execution_control.command=' + json.dumps(config['command'], ensure_ascii=False),
                      'mcp_servers.execution_control.args=' + json.dumps(config['args'], ensure_ascii=False)]
        for argv in (codex_worker.build_argv(request), jobs.cli.calls[0]['command']):
            for entry in registered:
                self.assertIn(entry, argv)
        claude_request = {k: v for k, v in request.items()
                          if k not in {'codex_path', 'sandbox', 'windows_sandbox', 'approval_policy', 'final_path'}}
        claude_request['claude_path'] = 'claude'
        path = self.root / 'claude-request.json'
        path.write_text(json.dumps(claude_request), encoding='utf-8')
        argv = claude_worker.build_argv(claude_worker.load_request(path))
        servers = json.loads(argv[argv.index('--mcp-config') + 1])['mcpServers']
        self.assertEqual(servers['execution_control'], config)
        self.assertEqual(set(servers), {'execution_control', 'scholarly'})
        for worker_request in (request, claude_request):
            worker_request['control_binding'] = {**binding, 'execution_id': 'EX-other'}
            with self.assertRaisesRegex(ValueError, 'control binding must identify this execution'):
                validate_execution_binding(worker_request)
        with self.assertRaisesRegex(ValueError, 'control binding must identify this execution'):
            self.run_pinned(profile, 'EX-other', timeout_seconds=600, control_binding=binding, evidence='wrong')
        self.assertFalse((self.root / 'wrong').exists())

    def test_issued_workspace_binding_reaches_both_runners_and_worker_contracts(self):
        invalid = [('unexpected', 'reject', 'control binding must identify this execution and an absolute local endpoint'),
                   ('execution_id', 'EX-other', 'control binding must identify this execution and an absolute local endpoint'),
                   ('endpoint', 'relative', 'control binding must identify this execution and an absolute local endpoint'),
                   ('workspace', 'relative', 'control binding workspace must be an absolute local path'),
                   ('workspace', '', 'control binding workspace must be an absolute local path'),
                   ('workspace', None, 'control binding workspace must be an absolute local path'),
                   ('workspace', 'other', 'control binding workspace differs from execution cwd')]
        for provider, worker, model in (('codex', codex_worker, 'gpt-6-astra'), ('claude', claude_worker, 'claude-opus-5')):
            with self.subTest(provider=model):
                root = self.root / provider
                workspace = root / 'workspace'
                workspace.mkdir(parents=True)
                config = {**PROFILE_CONFIG, 'tier_models': {tier: model for tier in ('high', 'medium', 'low')},
                          'session_limits': {'work': {model: 3}}}
                profile = role_profile(config, 'research_work')
                binding = ControlTransport(root / 'transport', clock=self.clock).issue('EX-bound', 'GR-bound',
                                                                                        workspace=workspace)
                jobs = ProviderJobs(clock=self.clock)
                result, _ = self.run_pinned(profile, 'EX-bound', jobs=jobs, workspace=provider + '/workspace',
                                            evidence=provider + '/evidence', timeout_seconds=60, control_binding=binding)
                self.assertEqual(result['status'], 'completed')
                request_path = root / 'evidence' / 'request.json'
                request = worker.load_request(request_path)
                self.assertEqual(request['control_binding'], binding)
                self.assertIn('--workspace=' + str(workspace.resolve()), mcp_server_config(binding)['args'])
                self.assertTrue(worker.build_argv(request))
                self.assertEqual(Path(jobs.launched[0].argv[1]).name, provider + '_worker.py')
                for index, (key, value, message) in enumerate(invalid):
                    wrong = dict(binding, **{key: str(root / value) if value == 'other' else value})
                    with self.subTest(invalid=index):
                        request_path.write_text(json.dumps({**request, 'control_binding': wrong}), encoding='utf-8')
                        with self.assertRaisesRegex(ValueError, message):
                            worker.load_request(request_path)
                        evidence = f'{provider}/invalid-{index}'
                        with self.assertRaisesRegex(ValueError, message):
                            self.run_pinned(profile, 'EX-bound', jobs=jobs, workspace=provider + '/workspace',
                                            evidence=evidence, timeout_seconds=60, control_binding=wrong)
                        self.assertFalse((self.root / evidence).exists())


class StartFailureEvidenceTests(PinnedCase):
    def test_structural_failure_emits_identity_bound_negative_evidence(self):
        p = role_profile({**PROFILE_CONFIG, 'lean_command': ['lean-A']}, 'maintenance')
        jobs = ProviderJobs(refuse=WindowsJobUnsupportedError('fixture structural failure'), clock=self.clock)
        with ObservedCalls(identity=LocalCLIAdapter.capability_identity) as calls:
            result, _ = self.run_pinned(p, 'EX-failure', jobs=jobs, prompt='input' + boundary_prompt(p))
        self.assertEqual(calls.count('identity'), 1)
        self.assertEqual(result['error_kind'], 'profile_unsupported')
        self.assertIn('capability_evidence', result)
        evidence = result['capability_evidence']
        # The identity the failed start recorded is this host's identity of the adapter's CLI and sources.
        expected = model_runner(self.root, jobs, self.clock).adapters[p['ai']['provider']].capability_identity()
        self.assertEqual(evidence['identity'], expected)
        self.assertEqual(json.loads((self.root / 'evidence' / 'capability-failure.json').read_bytes())['identity'],
                         expected)
        self.assertEqual(evidence['execution_profile_ref'], profile_ref(p))
        self.assertEqual(evidence['capabilities']['atomic_local_job']['status'], 'unsupported')
        self.assertEqual(evidence['id'], 'CE-' + exact_content_hash({k: v for k, v in evidence.items() if k != 'id'}))

    def test_identity_is_observed_only_for_a_structural_start_failure(self):
        p = role_profile({**PROFILE_CONFIG, 'lean_command': ['lean-A']}, 'maintenance')
        # Another Job already holds the ticket's name: a launch conflict, not a structural failure.
        jobs = ProviderJobs(refuse=FileExistsError('execution Job name already exists'), clock=self.clock)
        with ObservedCalls(identity=LocalCLIAdapter.capability_identity) as calls:
            result, _ = self.run_pinned(p, 'EX-conflict', jobs=jobs, prompt='input' + boundary_prompt(p))
        self.assertEqual(result['error_kind'], 'launch_conflict')
        self.assertTrue(result['launch_not_created'])
        # Hashing the CLI and adapter sources is evidence for a failed start only.
        self.assertEqual(calls.count('identity'), 0)


class NativeReportTests(PinnedCase):
    def test_native_claude_report_reaches_normal_result_without_scope_expansion(self):
        p = deepcopy(role_profile({**PROFILE_CONFIG, 'lean_command': ['lean-A']}, 'maintenance'))
        p['ai'].update(model='claude:haiku', provider='claude')
        p = seal_profile(p)
        native = {**CLAUDE_RESULT, 'stop_reason': 'max_tokens', 'modelUsage': {'haiku': {'costUSD': 0.125}},
                  'total_cost_usd': 0.125}
        stream = claude_stream(CLAUDE_INIT, native)
        result, _ = self.run_pinned(p, 'EX-native', jobs=ProviderJobs(ScriptedCLI(stdout=stream), clock=self.clock),
                                    prompt=prepare_prompt('sealed native report fixture', p))
        self.assertEqual(result['execution']['collect']['result'], 'output_collected',
                         result['execution']['collect']['reasons'])
        self.assertEqual(result['status'], 'completed')
        stored = execution_observation(result)
        reported = json.loads(stored['reported_fields_json'])
        self.assertEqual(stored['stop_reason'], 'max_tokens')
        self.assertEqual(reported['usage'], native['usage'])
        self.assertEqual(reported['model_usage_reported'], native['modelUsage'])
        self.assertEqual(reported['operation_count'], 'unknown')
        self.assertEqual(reported['remote_termination'], 'unknown')
        stdout = (self.root / 'evidence' / 'stdout.jsonl').read_bytes()
        self.assertEqual(stdout, stream)
        self.assertEqual(reported['evidence_sha256'], hashlib.sha256(stdout).hexdigest())


if __name__ == '__main__':
    unittest.main()
