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
from support.provider_runs import ProviderJobs, ScriptedCLI, model_runner


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


class CollectorCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.clock = FakeClock()

    def codex_request(self, **changes):
        """A checked Codex worker request whose outputs lie in ``evidence`` outside the workspace ``ws``."""
        evidence, workspace = self.root / 'evidence', self.root / 'ws'
        evidence.mkdir(exist_ok=True)
        workspace.mkdir(exist_ok=True)
        prompt = evidence / 'prompt'
        prompt.write_bytes(b'p')
        request = {"codex_path": str(self.root / 'codex.exe'), "prompt_path": str(prompt), "cwd": str(workspace),
                   "model": "m", "effort": "low", "sandbox": "read-only", "approval_policy": "never",
                   "max_runtime_seconds": 1, **{key: str(evidence / name) for key, name in (
                       ("stdout_path", "out"), ("stderr_path", "err"), ("final_path", "final"),
                       ("status_path", "status"))}, **changes}
        path = evidence / 'request.json'
        path.write_text(json.dumps(request), encoding='utf-8')
        return path

    def adapter(self, jobs):
        return CodexExecAdapter(str(self.root / 'codex.exe'), jobs=jobs, clock=self.clock)


class CodexCollectionTests(CollectorCase):
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
        execution = adapter.start(self.codex_request(), cwd=self.root, env={})
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
        execution = adapter.start(self.codex_request(), cwd=self.root, env={})
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

    def test_start_rejects_preexisting_output_before_creating_a_job(self):
        jobs = ProviderJobs(clock=self.clock)
        request = self.codex_request()
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


if __name__ == '__main__':
    unittest.main()
