"""탐침 입력·CLI 사건·파일 효과를 실제 러너와 작업자 위에서 확인한다."""
from contextlib import chdir, redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import probe_cli
from do_math.model_runner import ModelRunner
from support.entry import entry
from support.operator_probe_inputs import ProbeCLI
from support.provider_probes import ObservedCalls
from support.provider_runs import ProviderJobs


class ProbeContractTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.values = entry()
        self.home = self.root / 'codex-home'
        self.home.mkdir()
        configuration = self.root / '.codex'
        configuration.mkdir()
        (configuration / 'server.py').write_text('# 실제 외부 서버 호출을 하지 않는 시험 입력\n', encoding='utf-8')
        (configuration / 'config.toml').write_text(
            '[mcp_servers.scholarly]\ncommand = "python"\nargs = ["server.py"]\n', encoding='utf-8')

    def run_case(self, case, *, provider='codex', events=(), only_assigned=False,
                 model='fixture-model', scholarly=False, file_value='nonce', checkpoint=True,
                 models=None, polls=0):
        self.cli = ProbeCLI(case=case, events=events, file_value=file_value, checkpoint=checkpoint, models=models)
        self.jobs = ProviderJobs(self.cli, clock=self.values.ports.clock, polls=polls)
        self.ports = replace(self.values.ports, jobs=self.jobs)
        with chdir(self.root):
            result = probe_cli.run_case(self.root / 'evidence', case, ports=self.ports, provider=provider,
                model=model, effort='low', timeout=10, only_assigned=only_assigned, scholarly=scholarly,
                codex_home=self.home, environment=self.values.environment, host_id=self.values.host_id)
        self.report = json.loads(Path(result['report']).read_bytes())
        self.assertEqual(result, {'case': case, 'passed': self.report['passed'], 'checks': self.report['checks'],
                                  'report': str(self.root / 'evidence' / case / 'report.json')})
        self.assertEqual(len(self.cli.calls), 1)
        self.assertEqual(len(self.jobs.launched), 1)
        self.assertTrue(self.jobs.launched[0].closed)
        self.assertTrue(self.jobs.launched[0].done)
        return result

    def test_files_preserve_nonce_and_the_checkpoint_requested_by_product(self):
        result = self.run_case('files')
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
                                          'preserved_file': True, 'checkpoint': True})
        self.assertTrue(result['passed'])
        self.assertEqual((self.root / 'evidence/files/workspace/probe-evidence.txt').read_text(),
                         self.cli.calls[0]['output']['nonce'])

    def test_wrong_file_content_is_failed_even_with_completed_structured_response(self):
        result = self.run_case('files', file_value='wrong nonce')
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
                                          'preserved_file': False, 'checkpoint': True})
        self.assertFalse(result['passed'])

    def test_absent_file_and_checkpoint_are_both_reported(self):
        result = self.run_case('files', file_value=None, checkpoint=False)
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
                                          'preserved_file': False, 'checkpoint': False})
        self.assertFalse(result['passed'])
        workspace = self.root / 'evidence/files/workspace'
        self.assertEqual(sorted(path.relative_to(workspace).as_posix() for path in workspace.rglob('*')),
                         ['.scratch', '.scratch/.execution-temp'])

    def test_claude_scholarly_tool_is_observed_from_actual_stream(self):
        event = {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'tool-one', 'name': 'mcp__scholarly__list_sources', 'input': {}}]}}
        result = self.run_case('files', provider='claude', model='claude-opus-5', scholarly=True, events=[event])
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
            'preserved_file': True, 'checkpoint': True, 'scholarly_actual_tool': True})
        self.assertEqual(self.report['actual_tool_names'], ['mcp__scholarly__list_sources'])
        self.assertIn('list_sources tool once', self.cli.calls[0]['prompt'])

    def test_codex_scholarly_tool_name_joins_server_and_tool(self):
        event = {'type': 'item.started', 'item': {'id': 'tool-one', 'type': 'mcp_tool_call',
                                               'server': 'scholarly', 'tool': 'list_sources'}}
        result = self.run_case('files', scholarly=True, events=[event])
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], ['mcp__scholarly__list_sources'])

    def test_scholarly_file_success_does_not_substitute_for_missing_tool(self):
        result = self.run_case('files', scholarly=True)
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
            'preserved_file': True, 'checkpoint': True, 'scholarly_actual_tool': False})
        self.assertFalse(result['passed'])
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_other_scholarly_tool_does_not_satisfy_list_sources(self):
        """비슷한 이름의 다른 도구를 정확한 호출 증거로 세면 안 된다."""
        normal = {'type': 'item.started', 'item': {'id': 'tool-one', 'type': 'mcp_tool_call',
            'server': 'scholarly', 'tool': 'list_sources'}}
        event = deepcopy(normal)
        event['item']['tool'] = 'list_sources_preview'
        self.assertEqual({key for key in normal['item'] if normal['item'][key] != event['item'][key]}, {'tool'})
        result = self.run_case('files', scholarly=True, events=[event])
        self.assertEqual(self.report['actual_tool_names'], ['mcp__scholarly__list_sources_preview'])
        self.assertFalse(result['checks']['scholarly_actual_tool'])
        self.assertFalse(result['passed'])

    def test_message_nonlist_content_does_not_create_tool_observation(self):
        result = self.run_case('structured', provider='claude', model='claude-opus-5',
                               events=[{'type': 'assistant', 'message': {'content': 'text'}}])
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_nonobject_message_and_text_blocks_do_not_create_tool_observation(self):
        events = [{'type': 'assistant', 'message': 'text'},
                  {'type': 'assistant', 'message': {'content': ['text', {'type': 'text', 'text': 'observation'}]}}]
        result = self.run_case('structured', provider='claude', model='claude-opus-5', events=events)
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_codex_mcp_nonstring_tool_is_ignored_without_losing_later_tool(self):
        events = [{'type': 'item.started', 'item': {'type': 'mcp_tool_call', 'server': 'scholarly', 'tool': 7}},
                  {'type': 'item.started', 'item': {'type': 'mcp_tool_call', 'server': 'scholarly', 'tool': 'list_sources'}}]
        result = self.run_case('files', scholarly=True, events=events)
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], ['mcp__scholarly__list_sources'])

    def test_codex_nonobject_item_and_other_item_are_ignored(self):
        result = self.run_case('structured', events=[{'type': 'item.started', 'item': 'text'},
            {'type': 'item.started', 'item': {'type': 'reasoning', 'text': 'observation'}}])
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_claude_tool_requests_stop_and_collects_terminated_job(self):
        result = self.run_case('stop', provider='claude', model='claude-opus-5', polls=20,
            events=[{'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'command-one', 'name': 'Bash', 'input': {'command': 'sleep 120'}}]}}])
        self.assertEqual(result['checks'], {'local_termination': True, 'requested_stop': True})
        self.assertTrue(result['passed'])
        self.assertEqual(self.report['actual_tool_names'], ['Bash'])
        self.assertEqual(self.jobs.launched[0].terminations, 1)
        self.assertIn('waits 120 seconds', self.cli.calls[0]['prompt'])

    def test_codex_command_requests_stop_and_collects_terminated_job(self):
        result = self.run_case('stop', polls=20, events=[{'type': 'item.started', 'item': {
            'id': 'command-one', 'type': 'command_execution', 'command': 'sleep 120'}}])
        self.assertEqual(result['checks'], {'local_termination': True, 'requested_stop': True})
        self.assertTrue(result['passed'])
        self.assertEqual(self.jobs.launched[0].terminations, 1)
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_stop_case_without_command_fails_without_termination_request(self):
        result = self.run_case('stop')
        self.assertEqual(result['checks'], {'local_termination': True, 'requested_stop': False})
        self.assertFalse(result['passed'])
        self.assertEqual(self.jobs.launched[0].terminations, 0)

    def test_background_requires_started_event_wait_tool_and_completed_file(self):
        result = self.run_case('background', provider='claude', model='claude-opus-5', events=[
            {'type': 'system', 'subtype': 'task_started', 'task_id': 'background-one'},
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'wait-one', 'name': 'TaskOutput', 'input': {'task_id': 'background-one'}}]}}])
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
            'native_background_start': True, 'actual_wait_tool': True, 'completed_file': True})
        self.assertTrue(result['passed'], result)
        self.assertEqual(self.report['actual_tool_names'], ['TaskOutput'])
        self.assertIn('run_in_background=true', self.cli.calls[0]['prompt'])

    def test_background_without_events_and_file_fails_each_effect_check(self):
        result = self.run_case('background', provider='claude', model='claude-opus-5', file_value=None)
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True,
            'native_background_start': False, 'actual_wait_tool': False, 'completed_file': False})
        self.assertFalse(result['passed'])

    def test_locked_claude_reports_exact_requested_model(self):
        result = self.run_case('structured', provider='claude', model='claude-opus-5', only_assigned=True,
                               models=['claude-opus-5'])
        self.assertEqual(result['checks'], {'local_termination': True, 'structured_result': True, 'reported_models': True})
        self.assertTrue(result['passed'])
        self.assertEqual(self.report['result']['execution']['collect']['jsonl']['reported_models'], ['claude-opus-5'])

    def test_locked_claude_missing_model_evidence_is_not_success(self):
        result = self.run_case('structured', provider='claude', model='claude-opus-5', only_assigned=True)
        self.assertFalse(result['passed'])
        self.assertFalse(result['checks']['reported_models'])
        self.assertEqual(self.report['actual_tool_names'], [])

    def test_cli_rejects_missing_required_live_arguments_before_effects(self):
        destination = self.root / 'unused'
        valid = ['--provider', 'codex', '--model', 'fixture-model', '--output-dir', str(destination)]
        for options in ([], valid[:-2], valid + ['--timeout-seconds', '0']):
            errors = io.StringIO()
            with self.subTest(options=options), redirect_stderr(errors), ObservedCalls(run=ModelRunner.run) as calls:
                with self.assertRaises(SystemExit) as error:
                    probe_cli.main(options, ports=self.values.ports, environment=self.values.environment,
                                   host_id=self.values.host_id, codex_home=self.home)
                self.assertEqual(error.exception.code, 2)
                self.assertIn('live probes require explicit --provider, --model, --output-dir and a positive timeout', errors.getvalue())
                self.assertEqual(calls.count('run'), 0)
                self.assertFalse(destination.exists())

    def test_cli_rejects_model_disagreement_lock_alias_and_duplicate_cases(self):
        cases = [('claude', 'opus', ['--only-assigned-model'], 'model locking requires the full Claude model ID'),
                 ('codex', 'claude-opus-5', [], 'provider and model disagree'),
                 ('codex', 'fixture-model', ['--cases', 'files', 'files'], 'cases must be distinct')]
        destination = self.root / 'unused'
        for provider, model, extra, message in cases:
            errors = io.StringIO()
            with self.subTest(message=message), redirect_stderr(errors), ObservedCalls(run=ModelRunner.run) as calls:
                with self.assertRaises(SystemExit) as error:
                    probe_cli.main(['--provider', provider, '--model', model, '--output-dir', str(destination), *extra],
                        ports=self.values.ports, environment=self.values.environment, host_id=self.values.host_id, codex_home=self.home)
                self.assertEqual(error.exception.code, 2)
                self.assertIn(message, errors.getvalue())
                self.assertEqual(calls.count('run'), 0)
                self.assertFalse(destination.exists())

    def test_skill_only_uses_installed_bundle_without_model(self):
        output = io.StringIO()
        with redirect_stdout(output), ObservedCalls(run=ModelRunner.run) as calls:
            code = probe_cli.main(['--skill-only'], ports=self.values.ports, environment=self.values.environment,
                                  host_id=self.values.host_id, codex_home=self.home)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['status'], 'verified')
        self.assertEqual(calls.count('run'), 0)

    def test_cli_preserves_each_case_exception_and_complete_source_hashes(self):
        destination = self.root / 'reports'
        jobs = ProviderJobs(refuse=OSError('operator probe launch unavailable'))
        ports = replace(self.values.ports, jobs=jobs)
        with redirect_stdout(io.StringIO()):
            code = probe_cli.main(['--provider', 'codex', '--model', 'fixture-model', '--cases', 'structured', 'files',
                '--output-dir', str(destination)], ports=ports, environment=self.values.environment,
                host_id=self.values.host_id, codex_home=self.home)
        report = json.loads((destination / 'report.json').read_bytes())
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertEqual(report['cases'], [
            {'case': case, 'passed': False, 'error': 'OSError: operator probe launch unavailable'}
            for case in ('structured', 'files')])
        scripts = Path(probe_cli.__file__).parent
        self.assertEqual(report['sources'], {str(path.relative_to(scripts)): hashlib.sha256(path.read_bytes()).hexdigest()
                                            for path in (scripts / 'do_math').rglob('*.py')})
        self.assertEqual(jobs.launched, [])
