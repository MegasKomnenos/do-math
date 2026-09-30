"""The model runner (``model_runner.ModelRunner``, layer 3) on real adapters, workers and collectors.

A runner starts its provider's worker Job through the Jobs port, and the
worker starts the CLI at its ``spawn`` seam (``support.provider_runs``). The
request the runner writes, the worker's check of it, the CLI command, the
stream the collector parses and the result's classification are the
product's; only the CLI and the Job are doubles, and time is the fake clock.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.configuration import DEFAULT_CONFIG, validate_config
from do_math.execution_profiles import build_profiles, runner_tools
from do_math.windows_job import WindowsJobUnsupportedError
from do_math import claude_worker
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs, ScriptedCLI, codex_stream, model_runner


class RunnerCase(unittest.TestCase):
    def call(self, cli=None, *, jobs=None, clock=None, schema=None, **options):
        """``(result, jobs, root)`` of one unpinned Codex call (model ``m``) with a one-second deadline by default."""
        clock = clock or FakeClock()
        jobs = jobs or ProviderJobs(cli, clock=clock)
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / 'ws').mkdir()
        call = {'prompt': 'x', 'model': 'm', 'effort': 'low', 'timeout_seconds': 1, **options}
        result = model_runner(root, jobs, clock).run(
            output_schema=schema if schema is not None else {'type': 'object', 'required': ['x']},
            workspace=root / 'ws', evidence_dir=root / 'e', **call)
        return result, jobs, root


class ResultTests(RunnerCase):
    def test_completed_only_after_schema(self):
        # The collector's parsed stream lists one usage row per report (codex_stream.parse_jsonl).
        result, _, _ = self.call(ScriptedCLI(stdout=codex_stream(b'{"x":1}', usage={'input_tokens': 1}),
                                             final=b'{"x":1}'))
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['usage'], {'input_tokens': 1})
        self.assertEqual(result['output'], {'x': 1})

    def test_invalid_output_keeps_parsed_value_and_actionable_schema_error(self):
        result, _, _ = self.call(ScriptedCLI(final=b'{}'))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result.get('error_kind'), 'output_validation')
        self.assertEqual(result['output'], {})
        self.assertEqual(result['error'], "output: 'x' is a required property")

    def test_incomplete_fails(self):
        result, _, _ = self.call(ScriptedCLI(stdout=b'{"type":"thread.started","thread_id":"t"}\nnot-json'))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error_kind'], 'execution_failure')
        self.assertIn('jsonl_parse_incomplete', result['error'].split('; '))

    def test_callback_failure_does_not_resume(self):
        cli = ScriptedCLI()
        jobs = ProviderJobs(cli)

        def failed_record(started):
            raise RuntimeError('the start record failed')
        with self.assertRaisesRegex(RuntimeError, 'the start record failed'):
            self.call(jobs=jobs, schema={}, on_started=failed_record)
        job, = jobs.launched
        self.assertTrue(job.terminations)
        self.assertFalse(job.resumed, 'a failed start record must not resume the root')
        self.assertEqual(cli.calls, [])

    def test_pre_start_stop_does_not_resume(self):
        cli = ScriptedCLI()
        jobs = ProviderJobs(cli)
        result, _, _ = self.call(jobs=jobs, schema={}, should_stop=lambda: True)
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(result['error'], 'stop requested before resume')
        job, = jobs.launched
        self.assertEqual(job.terminations, 1)
        self.assertFalse(job.resumed)
        self.assertEqual(cli.calls, [])

    def test_scholarly_server_is_written_to_the_immutable_worker_request(self):
        server = {'command': 'python', 'args': ['C:/server.py']}
        cli = ScriptedCLI()
        result, jobs, root = self.call(cli, schema={'type': 'object'}, scholarly_server=server)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(json.loads((root / 'e' / 'request.json').read_text(encoding='utf-8'))['scholarly_server'],
                         server)
        # The worker ran the private snapshot the adapter wrote at start, and its CLI received the server.
        snapshot = json.loads(Path(jobs.launched[0].argv[2]).read_text(encoding='utf-8'))
        self.assertEqual(snapshot['scholarly_server'], server)
        self.assertIn('mcp_servers.scholarly.command="python"', cli.calls[0]['command'])


class WithoutDeadlineTests(RunnerCase):
    def run_observed(self, *, timeout=None, stop=False):
        """A call whose Job stays alive for eight inspections while 10,000 s pass at each one."""
        clock = FakeClock()
        jobs = ProviderJobs(clock=clock, polls=9, advance=10000)
        started = clock.monotonic()
        result, _, root = self.call(jobs=jobs, clock=clock, schema={}, timeout_seconds=timeout,
                                    should_stop=lambda: stop and jobs.launched[0].inspections >= 4)
        return result, jobs.launched[0], root, clock.monotonic() - started

    def test_long_running_work_keeps_running_until_its_normal_return(self):
        result, job, root, elapsed = self.run_observed()
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(job.terminations, 0)
        self.assertGreaterEqual(job.inspections, 9)
        self.assertGreaterEqual(elapsed, 90000)
        self.assertIsNone(json.loads((root / 'e' / 'request.json').read_text(encoding='utf-8'))['max_runtime_seconds'])
        self.assertIsNone(json.loads(Path(job.argv[2]).read_text(encoding='utf-8'))['max_runtime_seconds'])

    def test_work_without_a_deadline_still_obeys_stop(self):
        result, job, _, _ = self.run_observed(stop=True)
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(job.terminations, 1)
        self.assertEqual([receipt['operation'] for receipt in result['execution']['collect']['stop_receipts']],
                         ['TerminateJobObject'])

    def test_a_finite_call_deadline_still_stops_the_runner(self):
        result, job, _, _ = self.run_observed(timeout=1)
        self.assertEqual(result['status'], 'stopped')
        self.assertEqual(job.terminations, 1)


class ObservationBurstTests(RunnerCase):
    """A burst over the 1 MiB read limit, a blank row and a UTF-8 character cut where the CLI's two writes met."""

    EXPECTED = [{"type": "item.updated", "index": index, "text": "x" * 960} for index in range(2000)]
    LAST = {"type": "item.updated", "index": 2000, "text": "가"}

    def burst(self, prefix, suffix):
        """``(result, batches, stream)`` of a call whose Job lives for three inspections after writing the stream."""
        encoded = json.dumps(self.LAST, ensure_ascii=False).encode('utf-8')
        cut = encoded.index('가'.encode('utf-8')) + 1
        first = prefix + b''.join(json.dumps(row).encode('utf-8') + b'\r\n' for row in self.EXPECTED) \
            + b'\r\n' + encoded[:cut]
        stream = first + encoded[cut:] + b'\r\n' + suffix
        observed = []
        clock = FakeClock()
        jobs = ProviderJobs(ScriptedCLI(stdout=stream), clock=clock, polls=4)
        result, _, _ = self.call(jobs=jobs, clock=clock, schema={}, prompt='fixture', model='fixture',
                                 timeout_seconds=None, on_observation=observed.append)
        return result, observed, stream

    def assert_delivered(self, observed, stream):
        events = [row for batch in observed for row in batch.events]
        self.assertEqual([row for row in events if row.get("type") == "item.updated"], [*self.EXPECTED, self.LAST])
        self.assertEqual(observed[-1].end_offset, len(stream))
        rows = [row for batch in observed for row in batch.rows]
        self.assertEqual(b"".join(rows), stream.replace(b"\r\n\r\n", b"\r\n"))
        numbers = [batch.first_row + index for batch in observed for index in range(len(batch.rows))]
        self.assertEqual(numbers, list(range(len(rows))))
        for batch in observed:
            for (start, end), row in zip(batch.offsets, batch.rows):
                self.assertEqual(stream[start:end], row)
        return events

    def test_observation_burst_preserves_order_and_split_utf8_tail(self):
        result, observed, stream = self.burst(b'', b'not-json\r\n' + b'{"type":')
        # Several batches: rows read inside the polling loop and after the Job ended.
        self.assertGreater(len(observed), 2)
        events = self.assert_delivered(observed, stream)
        # After the Job ends, the runner also delivers the unterminated last row.
        self.assertEqual([row for row in events if row.get("type") == "unparsed_observation"],
                         [{"type": "unparsed_observation", "bytes": len(b"not-json\r")},
                          {"type": "unparsed_observation", "bytes": len(b'{"type":')}])
        # The collector reads the same unparsable stream; the call returns its classification.
        self.assertEqual(result['status'], 'failed')
        self.assertIn('jsonl_parse_incomplete', result['error'].split('; '))

    def test_a_valid_burst_is_delivered_whole_and_completes(self):
        start = b'{"type":"thread.started","thread_id":"t"}\r\n{"type":"turn.started"}\r\n'
        end = (b'{"type":"item.completed","item":{"id":"i","type":"agent_message","text":"{}"}}\r\n'
               b'{"type":"turn.completed","usage":{"input_tokens":1}}\r\n')
        result, observed, stream = self.burst(start, end)
        self.assert_delivered(observed, stream)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['output'], {})


class ProviderRoutingTests(RunnerCase):
    def routed_requests(self, calls):
        """``(provider, worker request)`` for each ``(model, claude_only_assigned_model)`` call of one runner.

        The request is the private snapshot the started worker ran.
        """
        clock = FakeClock()
        jobs = ProviderJobs(clock=clock)
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        runner = model_runner(root, jobs, clock)
        adapters = dict(runner.adapters)
        requests = []
        for index, (model, lock) in enumerate(calls):
            workspace = root / f'workspace-{index}'
            workspace.mkdir()
            started = len(jobs.launched)
            result = runner.run(model=model, prompt='fixture', output_schema={}, workspace=workspace,
                                evidence_dir=root / f'evidence-{index}', effort='low', timeout_seconds=1,
                                claude_only_assigned_model=lock)
            self.assertEqual(result['status'], 'completed')
            for job in jobs.launched[started:]:
                provider = 'claude' if Path(job.argv[1]).name == 'claude_worker.py' else 'codex'
                requests.append((provider, json.loads(Path(job.argv[2]).read_text(encoding='utf-8'))))
        # One runner serves every call: its adapter table is the one it was built with.
        self.assertEqual(runner.adapters, adapters)
        return requests, jobs

    def test_model_lock_is_opt_in_and_reaches_only_claude(self):
        pinned = {**DEFAULT_CONFIG, 'claude_only_assigned_model': True, 'scholarly_enabled': False}
        profile = next(p for p in build_profiles(pinned)['execution_profiles'].values() if p['role'] == 'maintenance')
        # The runner reads the lock from this pinned edition, not from the current configuration.
        self.assertTrue(runner_tools(profile)['claude_only_assigned_model'])
        self.assertFalse(DEFAULT_CONFIG['claude_only_assigned_model'])
        with self.assertRaisesRegex(ValueError, "claude_only_assigned_model: 'true' is not of type 'boolean'"):
            validate_config({'claude_only_assigned_model': 'true'})
        requests, jobs = self.routed_requests([('claude-opus-5', True), ('gpt-5.6-sol', True)])
        self.assertEqual([(provider, request['model'], request.get('claude_only_assigned_model'))
                          for provider, request in requests],
                         [('claude', 'claude-opus-5', True), ('codex', 'gpt-5.6-sol', None)])
        # The Claude CLI the worker started is bound to the model.
        claude_command = jobs.cli.calls[0]['command']
        self.assertEqual(json.loads(claude_command[claude_command.index('--settings') + 1])['availableModels'],
                         ['claude-opus-5'])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'schema.json'
            path.write_text('{"type":"object"}', encoding='utf-8')
            request = {'claude_path': 'claude.exe', 'model': 'claude-opus-5', 'effort': 'high',
                       'cwd': d, 'output_schema_path': str(path)}
            argv = claude_worker.build_argv(request)
            self.assertNotIn('availableModels', json.loads(argv[argv.index('--settings') + 1]))
            request['claude_only_assigned_model'] = True
            argv = claude_worker.build_argv(request)
            settings = json.loads(argv[argv.index('--settings') + 1])
            self.assertEqual(settings['availableModels'], ['claude-opus-5'])
            self.assertEqual(settings['fallbackModel'], [])
            self.assertFalse(settings['switchModelsOnFlag'])
            self.assertEqual(settings['env']['CLAUDE_CODE_SUBAGENT_MODEL'], 'claude-opus-5')
            self.assertEqual(settings['env']['CLAUDE_CODE_SUBAGENT_MODEL_FORCE'], '1')
            self.assertEqual(settings['env']['ANTHROPIC_DEFAULT_HAIKU_MODEL'], 'claude-opus-5')

    def test_router_dispatches_claude_and_codex_without_mutating_shared_runner(self):
        requests, jobs = self.routed_requests([('claude:haiku', None), ('gpt-5.6-sol', None),
                                               ('claude-haiku-4-5-20251001', None)])
        # Each call reaches its provider's worker; a Claude CLI receives the name without ``claude:``.
        self.assertEqual([(provider, request['model']) for provider, request in requests],
                         [('claude', 'haiku'), ('codex', 'gpt-5.6-sol'), ('claude', 'claude-haiku-4-5-20251001')])
        self.assertEqual([call['command'][call['command'].index('--model') + 1] for call in jobs.cli.calls],
                         ['haiku', 'gpt-5.6-sol', 'claude-haiku-4-5-20251001'])
        with self.assertRaisesRegex(ValueError, 'requires a Claude model name'):
            self.routed_requests([('claude:', None)])


class StartFailureTests(RunnerCase):
    def test_unsupported_job_is_a_profile_failure_not_an_ordinary_retry(self):
        jobs = ProviderJobs(refuse=WindowsJobUnsupportedError('atomic admission unsupported'))
        try:
            result, _, root = self.call(jobs=jobs, schema={}, prompt='test', model='test')
        except WindowsJobUnsupportedError:
            self.fail('structural unsupported capability was not classified for the profile gate')
        self.assertEqual(result['error_kind'], 'profile_unsupported')
        self.assertEqual(result['capability_failure']['capability'], 'atomic_local_job')
        self.assertTrue(result['launch_not_created'])
        self.assertEqual(jobs.launched, [])


if __name__ == '__main__':
    unittest.main()
