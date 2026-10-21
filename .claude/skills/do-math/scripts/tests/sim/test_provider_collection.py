"""The local CLI collector (``codex_adapter.LocalCLIAdapter`` and its providers, layer 3): start, barrier and collection.

``start`` checks a request, snapshots its request and prompt privately and
launches the worker's Job through the Jobs port; ``collect`` reads the
worker's files only behind a confirmed Job termination barrier. The worker and
its CLI run in process (``support.provider_runs``), so the collected files are
the ones the product's worker wrote.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from do_math import file_io
from do_math.claude_adapter import ClaudePrintAdapter
from do_math.codex_adapter import CodexExecAdapter
from do_math.control_transport import ControlTransport
from support.provider_inputs import CLAUDE_INIT, CLAUDE_RESULT, claude_stream
from support.fakes.clock import FakeClock
from support.provider_probes import ObservedCalls, settle
from support.provider_runs import ProviderJobs, ScriptedCLI, collector_request, model_runner


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


class CollectorCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()

    def adapter(self, jobs):
        return CodexExecAdapter(str(self.root / 'codex.exe'), jobs=jobs, clock=self.clock)


class CodexCollectionTests(CollectorCase):
    def test_model_catalog_timeout_is_diagnostic_evidence_for_success_and_failure(self):
        from do_math.canonical import canonical_json
        from do_math.payloads import json_safe
        import base64

        # Exact manager log from EX-01M5D097XN0TR7G5S582K1MKX4. Other stderr
        # stays raw; a quoted message from a different component is not this diagnostic.
        log = (b'2026-10-20T15:55:28.118316Z ERROR codex_models_manager::manager: '
               b'failed to refresh available models: request timed out\n')
        prefix = 'unrelated stderr \uac00\ub098\ub2e4\r\n'.encode('utf-8')
        stderr = prefix + log
        failed_stream = (b'{"type":"thread.started","thread_id":"rejected"}\n'
                         b'{"type":"turn.started"}\n'
                         b'{"type":"error","message":"request rejected"}\n'
                         b'{"type":"turn.failed","error":{"message":"request rejected"}}\n')
        cases = [('completed', {}, None),
                 ('nonzero', {'returncode': 1}, 'cli_nonzero_exit'),
                 ('turn_failed', {'stdout': failed_stream}, 'turn_failed'),
                 ('timeout', {'timeout': True}, 'max_runtime_elapsed'),
                 ('unrelated', {'stderr': prefix}, None)]
        for name, options, failure in cases:
            with self.subTest(case=name):
                root = self.root / name
                cli = ScriptedCLI(**{'stderr': stderr, **options})
                jobs = ProviderJobs(cli, clock=self.clock)
                result = model_runner(root, jobs, self.clock).run(
                    prompt='x', output_schema={}, workspace=root / 'ws', evidence_dir=root / 'e',
                    model='m', effort='low', timeout_seconds=1)
                collected = result['execution']['collect']
                self.assertEqual(collected['stderr']['raw'], cli.stderr)
                self.assertEqual(collected['stderr']['sha256'], sha256(cli.stderr))
                self.assertTrue(collected['termination_barrier']['confirmed'])
                self.assertEqual(collected['remote_termination'], 'unknown')
                self.assertEqual(result['status'], 'failed' if failure else 'completed')
                if failure:
                    self.assertEqual(result['error_kind'], 'execution_failure')
                    self.assertIn(failure, collected['reasons'])
                else:
                    self.assertEqual(collected['reasons'], [])
                    self.assertNotIn('error_kind', result)
                expected = [] if name == 'unrelated' else [{
                    'kind': 'model_catalog_refresh_timeout', 'scope': 'cli_model_catalog',
                    'reported_at': '2026-10-20T15:55:28.118316Z', 'reported_level': 'ERROR',
                    'source': {'artifact': 'stderr', 'offset': len(prefix), 'bytes': len(log)}}]
                self.assertEqual(collected['diagnostics'], expected)
                # The existing result artifact serialization retains both the index and exact bytes.
                preserved = json.loads(canonical_json(json_safe(result)))['execution']['collect']
                self.assertEqual(preserved['diagnostics'], expected)
                self.assertEqual(base64.b64decode(preserved['stderr']['raw']['base64']), cli.stderr)
                self.assertEqual(len(cli.calls), 1)
                if expected:
                    from support.doc_code import result_field_issues
                    from support.engine_context import assert_result_documents
                    artifact = json.loads(canonical_json(json_safe(result)))
                    assert_result_documents(self, artifact, root / 'ws', owner='call_result', expected=result)
                    token = 'call_result.execution.collect.diagnostics[].source.offset'
                    self.assertEqual(result_field_issues('`' + token + '`', 'call_result', artifact), [])
                    del artifact['execution']['collect']['diagnostics'][0]['source']['offset']
                    self.assertEqual(result_field_issues('`' + token + '`', 'call_result', artifact),
                                     [('actual field', token)])
                    self.assertEqual(result_field_issues('`call_result.execution.collect.nonexistent`',
                        'call_result', artifact), [('actual field', 'call_result.execution.collect.nonexistent')])

    def test_collect_rejects_malformed_tail_even_with_turn_completed(self):
        jobs = ProviderJobs(ScriptedCLI(stdout=b'{"type":"turn.completed"}\nbroken', final=b'final'), clock=self.clock)
        (self.root / 'ws').mkdir()
        result = model_runner(self.root, jobs, self.clock).run(
            prompt='x', output_schema={}, workspace=self.root / 'ws', evidence_dir=self.root / 'e', model='m',
            effort='low', timeout_seconds=1)
        collected = result['execution']['collect']
        self.assertTrue(collected['jsonl']['turn_completed'])
        self.assertEqual(collected['result'], 'incomplete')
        # The parse stops at the broken row, before any final agent message, so the final file matches nothing.
        self.assertEqual(collected['reasons'], ['jsonl_parse_incomplete', 'final_response_mismatch'])
        self.assertEqual(result['status'], 'failed')

    def test_collect_reports_start_snapshot_bytes_without_rereading_them(self):
        adapter = self.adapter(ProviderJobs(clock=self.clock))
        execution = adapter.start(collector_request(self.root), cwd=self.root, env={})
        snapshot = Path(execution.worker_argv[-1])
        request_raw = snapshot.read_bytes()
        adapter.resume(execution)
        # After the worker ran, the private snapshots change; the collector keeps the bytes it hashed at start.
        snapshot.write_bytes(b'{}')
        (snapshot.parent / 'prompt.bin').write_bytes(b'changed')
        collected = adapter.collect(execution)
        self.assertEqual(collected['result'], 'output_collected')
        self.assertEqual(execution.request_sha256, sha256(request_raw))
        self.assertEqual(collected['source_request'], {"present": True, "bytes": len(request_raw),
                                                       "sha256": sha256(request_raw), "raw": request_raw})
        self.assertEqual(collected['source_prompt'], {"present": True, "bytes": 1, "sha256": sha256(b'p'),
                                                      "raw": b'p'})

    def test_timeout_with_descendant_still_in_job_cannot_collect_stale_files(self):
        # The CLI wrote output, then outlived the request's runtime limit; one process stays in the Job.
        jobs = ProviderJobs(ScriptedCLI(stdout=b'old', final=b'old', timeout=True), clock=self.clock, remaining=(99,))
        adapter = self.adapter(jobs)
        execution = adapter.start(collector_request(self.root), cwd=self.root, env={})
        adapter.resume(execution)
        status = json.loads(execution.status_path.read_bytes())
        self.assertEqual((status['state'], status['runner_stop_required']), ('timeout', True))
        self.assertEqual(execution.stdout_path.read_bytes(), b'old')
        collected = adapter.collect(execution)
        self.assertFalse(collected['artifacts_read'])
        self.assertEqual(collected['reasons'], ['termination_barrier_unconfirmed'])
        self.assertEqual(collected['termination_barrier'], {'active_processes': 1, 'process_ids': (99,),
                                                            'root_signaled': True, 'confirmed': False})
        self.assertNotIn('stdout', collected)
        self.assertNotIn('diagnostics', collected)

    def test_start_rejects_preexisting_output_before_creating_a_job(self):
        jobs = ProviderJobs(clock=self.clock)
        request = collector_request(self.root)
        (self.root / 'evidence' / 'final').write_bytes(b'old')
        with self.assertRaisesRegex(FileExistsError, 'output paths must be newly allocated'):
            self.adapter(jobs).start(request, cwd=self.root, env={})
        self.assertEqual(jobs.launched, [])


class SnapshotTests(CollectorCase):
    def test_both_adapters_snapshot_the_exact_control_binding(self):
        work = self.root / 'workspace'
        work.mkdir()
        binding = ControlTransport(self.root / 'transport', clock=self.clock).issue('EX-snapshot', 'GR-snapshot',
                                                                                     workspace=work)
        prompt, schema = self.root / 'input.txt', self.root / 'schema.json'
        prompt.write_text('test', encoding='utf-8')
        schema.write_text('{}', encoding='utf-8')
        common = {'prompt_path': str(prompt), 'output_schema_path': str(schema), 'cwd': str(work),
                  'model': 'test', 'effort': 'low', 'max_runtime_seconds': 10,
                  **{key: str(self.root / key) for key in ('stdout_path', 'stderr_path', 'status_path')},
                  'execution_id': 'EX-snapshot', 'profile_ref': {'id': 'EP-test', 'revision': 1, 'sha256': 'a' * 64},
                  'control_binding': binding}
        jobs = ProviderJobs(clock=self.clock)
        for adapter, options in ((CodexExecAdapter('codex', jobs=jobs, clock=self.clock),
                                  {'codex_path': 'codex', 'sandbox': 'danger-full-access', 'approval_policy': 'never',
                                   'final_path': str(self.root / 'final_path')}),
                                 (ClaudePrintAdapter('claude', jobs=jobs, clock=self.clock), {'claude_path': 'claude'})):
            with self.subTest(provider=adapter.provider):
                request = self.root / (adapter.executable_key + '.json')
                request.write_text(json.dumps({**common, **options}), encoding='utf-8')
                execution = adapter.start(request, cwd=self.root, env={})
                # The worker runs the snapshot request its argv names, not the original file.
                snapshot = Path(execution.worker_argv[-1])
                self.assertEqual(jobs.launched[-1].argv, list(execution.worker_argv))
                snap = json.loads(snapshot.read_text(encoding='utf-8'))
                self.assertEqual(snap['control_binding'], binding)
                self.assertEqual(snap['execution_id'], binding['execution_id'])
                request.write_text('{}', encoding='utf-8')
                self.assertEqual(json.loads(snapshot.read_text(encoding='utf-8'))['control_binding'], binding)


class IdentityTests(CollectorCase):
    def test_capability_identity_has_host_worker_and_cli_hashes(self):
        """About 2.5 s as a process's first identity, over the 2 s Sim budget: the host query and every source hash are the subject."""
        from support.entry import entry
        _entry = entry()
        path = self.root / 'cli.exe'
        path.write_bytes(b'first')
        adapter = CodexExecAdapter(str(path), jobs=_entry.ports.jobs, clock=_entry.ports.clock)
        first = adapter.capability_identity()
        self.assertIn('windows_job', first['module_sha256'])
        path.write_bytes(b'second')
        second = adapter.capability_identity()
        self.assertEqual((first['cli_sha256'], second['cli_sha256']), (sha256(b'first'), sha256(b'second')))
        self.assertEqual(first['module_sha256'], second['module_sha256'])
        self.assertIn('host', first)
        # Every module a worker runs in its Job, or its collector uses, identifies the implementation.
        self.assertEqual(set(CodexExecAdapter('codex', jobs=_entry.ports.jobs, clock=_entry.ports.clock).capability_identity()['module_sha256']),
                         {'cli_worker', 'codex_worker', 'control_transport', 'control_protocol', 'file_io', 'values',
                          'windows_job', 'scholarly', 'codex_adapter', 'codex_stream', 'provider_final',
                          'control_server', 'worker_request', 'cli_execution'})
        self.assertEqual(set(ClaudePrintAdapter('claude', jobs=_entry.ports.jobs, clock=_entry.ports.clock).capability_identity()['module_sha256']),
                         {'claude_worker', 'cli_worker', 'codex_worker', 'control_transport', 'control_protocol',
                          'file_io', 'values', 'windows_job', 'scholarly', 'codex_adapter', 'codex_stream',
                          'provider_final', 'control_server', 'worker_request', 'cli_execution', 'claude_adapter',
                          'claude_stream'})

    def test_unchanged_cli_and_sources_are_not_rehashed_for_each_identity(self):
        from support.entry import entry
        _entry = entry()
        path = self.root / 'cli.exe'
        path.write_bytes(b'first')
        # A fresh file's fingerprint is trusted only once its times lie outside the racy window.
        settle(path)
        adapter = CodexExecAdapter(str(path), jobs=_entry.ports.jobs, clock=_entry.ports.clock)
        with ObservedCalls(hash=file_io.sha256_file) as first_calls:
            first = adapter.capability_identity()
        self.assertEqual(first['cli_sha256'], sha256(b'first'))
        with ObservedCalls(hash=file_io.sha256_file) as calls:
            self.assertEqual(adapter.capability_identity(), first)
        self.assertEqual(calls.count('hash'), 0, 'unchanged file was rehashed')
        # A changed CLI is hashed again.
        path.write_bytes(b'other')
        settle(path)
        with ObservedCalls(hash=file_io.sha256_file) as changed:
            self.assertEqual(adapter.capability_identity()['cli_sha256'], sha256(b'other'))
        self.assertEqual([captured['path'] for captured in changed.captured('hash')],
                         [os.path.normcase(os.path.abspath(path.resolve()))])


class ClaudeFinalTests(unittest.TestCase):
    def test_final_is_selected_from_the_stream_and_preserved_bytes_must_match_it(self):
        from support.entry import entry
        _entry = entry()
        adapter = ClaudePrintAdapter("unused", jobs=_entry.ports.jobs, clock=_entry.ports.clock)
        self.assertTrue(adapter.final_from_stream)
        parsed = adapter.parse_response(claude_stream(CLAUDE_INIT, CLAUDE_RESULT), {"output_schema_path": "schema.json"})
        final = adapter.final_bytes(parsed)
        self.assertEqual(json.loads(final), CLAUDE_RESULT["structured_output"])
        self.assertEqual(adapter.validate_final(parsed, final), [])
        # Equal meaning is not enough: the preserved bytes must be the stream's selected serialization.
        for changed in (b'{"ok":1}', b'{"ok":false,"ok":true}', b'{"ok":true}'):
            with self.subTest(final=changed):
                self.assertEqual(adapter.validate_final(parsed, changed), ["final_response_mismatch"])
        self.assertIsNone(adapter.final_bytes(adapter.parse_response(claude_stream(CLAUDE_INIT), {})))


class ProducedRequestCollectionTests(CollectorCase):
    def produced_request(self, provider, directory):
        from support.provider_close_inputs import request_seed
        jobs = ProviderJobs(clock=self.clock)
        request = request_seed(provider, directory, jobs=jobs, clock=self.clock)
        Path(request['cwd']).mkdir(parents=True)
        Path(request['prompt_path']).parent.mkdir(parents=True)
        Path(request['prompt_path']).write_bytes(b'Preserve the request binding.')
        Path(request['output_schema_path']).write_text('{"type":"object"}', encoding='utf-8')
        path = directory / 'request.json'
        path.write_text(json.dumps(request), encoding='utf-8')
        adapter = (CodexExecAdapter if provider == 'codex' else ClaudePrintAdapter)(
            request[provider + '_path'], jobs=jobs, clock=self.clock)
        return path, request, adapter, jobs

    def test_schema_path_cannot_alias_the_prompt_before_job_creation(self):
        for provider in ('codex', 'claude'):
            with self.subTest(provider=provider):
                path, request, adapter, jobs = self.produced_request(provider, self.root / provider)
                request['output_schema_path'] = request['prompt_path']
                path.write_text(json.dumps(request), encoding='utf-8')
                before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                          for p in self.root.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError, '^request, prompt, and output paths must be distinct$'):
                    adapter.start(path, cwd=self.root, env={})
                self.assertEqual(jobs.launched, [])
                self.assertEqual({p.relative_to(self.root).as_posix(): p.read_bytes()
                                  for p in self.root.rglob('*') if p.is_file()}, before)

    def test_timeout_and_changed_worker_hashes_remain_incomplete_after_termination(self):
        for provider in ('codex', 'claude'):
            for fault in ('timeout', 'stdin_sha256', 'request_sha256'):
                with self.subTest(provider=provider, fault=fault):
                    directory = self.root / (provider + '-' + fault)
                    path, request, adapter, jobs = self.produced_request(provider, directory)
                    jobs.cli.timeout = fault == 'timeout'
                    execution = adapter.start(path, cwd=directory, env={})
                    self.addCleanup(execution.job.close)
                    adapter.resume(execution)
                    status = json.loads(execution.status_path.read_bytes())
                    if fault == 'timeout':
                        self.assertEqual(status['state'], 'timeout')
                        self.assertTrue(status['runner_stop_required'])
                        reason = 'max_runtime_elapsed'
                    else:
                        self.assertEqual(status['state'], 'exited')
                        self.assertEqual(status['cli_exit_code'], 0)
                        # Corrupt only one external status-file coordinate after
                        # the real worker has produced and hashed all normal bytes.
                        status[fault] = '0' * 64
                        execution.status_path.write_text(json.dumps(status), encoding='utf-8')
                        reason = ('worker_stdin_hash_mismatch' if fault == 'stdin_sha256'
                                  else 'worker_request_hash_mismatch')
                    collected = adapter.collect(execution)
                    self.assertTrue(collected['termination_barrier']['confirmed'])
                    self.assertEqual(collected['result'], 'incomplete')
                    self.assertEqual(collected['reasons'], [reason])
                    self.assertEqual(len(jobs.cli.calls), 1)
                    self.assertEqual(jobs.cli.calls[0]['stdin'], Path(request['prompt_path']).read_bytes())

if __name__ == '__main__':
    unittest.main()
