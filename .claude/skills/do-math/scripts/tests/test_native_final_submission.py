"""Native bytes use central capture; provider responses are explicit fixtures."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.codex_adapter import _artifact
from do_math.model_runner import verified_native_final
from engine_fixtures import native_result, start_native_final, submit_history


def job_native_result(case, execution, context, raw, workspace):
    """Real Windows Job and adapter collector; only CLI response generation is scripted."""
    import os, uuid
    from do_math.windows_job import WindowsJob, process_identity
    from do_math.codex_adapter import CLIExecution, CodexExecAdapter
    result = native_result(execution, context, raw, workspace)
    collected = result['execution']['collect']
    evidence = workspace.parent / 'native-evidence'; evidence.mkdir()
    payload = {'stdout.jsonl': collected['stdout']['raw'].decode(), 'final.txt': raw.decode(),
        'stderr.txt': '', 'status.json': json.dumps(collected['worker_status'])}
    # The suspended process itself writes all terminal evidence after resume.
    script = "from pathlib import Path; import json,sys; p=Path(sys.argv[1]); d=json.loads(sys.argv[2]); [(p/k).write_bytes(v.encode('utf-8')) for k,v in d.items()]"
    argv = (sys.executable, '-B', '-c', script, str(evidence), json.dumps(payload, ensure_ascii=False))
    execution['launch_ticket']['phase'] = 'dispatched'
    execution['capacity']['local_termination'] = 'unknown'
    job = WindowsJob(argv, cwd=evidence, env=os.environ, name=execution['launch_ticket']['job_name'])
    native = CLIExecution(collected['source_request']['sha256'], collected['source_prompt']['sha256'], argv,
        evidence/'stdout.jsonl', evidence/'stderr.txt', evidence/'final.txt', evidence/'status.json',
        job, None, collected['source_request']['raw'], collected['source_prompt']['raw'])
    adapter = CodexExecAdapter('fixture-cli')
    try:
        early = adapter.collect(native)
        case.assertFalse(early['artifacts_read'])
        case.assertFalse((evidence/'final.txt').exists())
        started = {**process_identity(job), 'job_name': job.name, 'request_sha256': native.request_sha256,
            'execution_id': execution['id'], 'profile_ref': execution['execution_profile_ref']}
        execution['capacity']['process'] = deepcopy(started)
        result['execution']['started'] = started
        adapter.resume(native)
        case.assertTrue(adapter.wait_for_termination(native, 10))
        result['execution']['collect'] = adapter.collect(native)
        case.assertEqual(result['execution']['collect']['result'], 'output_collected')
        case.assertTrue(result['execution']['collect']['termination_barrier']['confirmed'])
    finally:
        job.close()
    execution['launch_ticket']['phase'] = 'finished'
    execution['capacity']['local_termination'] = 'confirmed'
    return result


class NativeFinalProtocolTests(unittest.TestCase):
    def setUp(self):
        self.execution = {'id': 'EX-native', 'grant_id': 'GR-native', 'execution_profile_ref': {'id': 'EP-native', 'sha256': 'a'*64}}
        self.context = {'execution_id': 'EX-native', 'action': {'grant_id': 'GR-native'}}
        self.raw = '{"text":"e\u0301 · é · 한글 · 😀"}'.encode()
        self.result = native_result(self.execution, self.context, self.raw, Path('C:/workspace'))

    def test_verified_native_stream_retains_exact_bytes_and_serialized_evidence(self):
        from do_math.payloads import json_safe
        for value in [self.result, json_safe(self.result)]:
            self.assertEqual(verified_native_final(value, self.execution, self.context), self.raw)

    def test_collected_digests_are_compared_as_records_without_rehashing(self):
        from unittest.mock import patch
        from do_math.payloads import json_safe
        serialized = json_safe(self.result)
        with patch('hashlib.sha256', side_effect=AssertionError('collection already hashed these bytes')):
            for value in [self.result, serialized]:
                self.assertEqual(verified_native_final(value, self.execution, self.context), self.raw)
        # The serialized copy and the collected record must still name the same digest.
        serialized['execution']['collect']['stdout']['raw']['sha256'] = 'c' * 64
        with self.assertRaisesRegex(ValueError, 'serialized native artifact differs'):
            verified_native_final(serialized, self.execution, self.context)

    def test_changed_creation_identity_or_pid_and_float_identity_are_rejected(self):
        mutations = [lambda r: r['execution']['started'].update(creation_filetime=134345064658094592),
            lambda r: r['execution']['collect']['process_identity'].update(creation_filetime=134345064658094592),
            lambda r: r['execution']['collect']['process_identity'].update(pid=124),
            lambda r: r['execution']['started'].update(creation_filetime=float(134345064658094591))]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                result = deepcopy(self.result); mutate(result)
                with self.assertRaises(ValueError): verified_native_final(result, self.execution, self.context)

    def test_status_alone_bad_stream_changed_request_and_unconfirmed_barrier_rejected(self):
        variants = [lambda r: r.pop('execution'), lambda r: r.update(status='stopped'),
            lambda r: r['execution']['collect']['termination_barrier'].update(active_processes=1),
            lambda r: r['execution']['collect'].update(stdout=_artifact(r['execution']['collect']['stdout']['raw'] + b'{')),
            lambda r: r['execution']['collect'].update(final=_artifact(b'{"text":"different"}')),
            lambda r: r['execution']['collect']['worker_status'].update(request_sha256='b'*64)]
        for mutate in variants:
            with self.subTest(mutation=variants.index(mutate)):
                result = deepcopy(self.result); mutate(result)
                with self.assertRaises(ValueError): verified_native_final(result, self.execution, self.context)


class NativeFinalGitTests(unittest.TestCase):
    def setUp(self):
        start_native_final(self)

    def test_native_capture_git_reload_summary_and_early_seal_precedence(self):
        from do_math.engine import ResearchEngine
        execution = self.engine.runtime['executions']['EX-history']
        output = {k:v for k,v in self.output.items() if k != 'integration_bundles'}
        output['report'] = 'Exact e\u0301 · é · 한글 · 😀'
        raw = json.dumps(output, ensure_ascii=False, indent=3).encode()
        result = job_native_result(self, execution, self.context, raw, self.workspace)
        collected = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(collected['status'], 'completed', collected)
        self.assertEqual(collected['collection'], 'sealed_submission')
        self.engine = ResearchEngine(self.repo, self.identifier)
        execution = self.engine.runtime['executions']['EX-history']
        self.assertEqual(execution['submission_receipt']['kind'], 'native_final')
        self.assertFalse(self.engine.runtime.get('control_receipts'))
        self.assertEqual(self.engine.store.read(execution['submission_intent']['output_ref'], self.engine.head), raw)
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], 1)
        head = self.engine.head
        other = deepcopy(result); other['execution']['collect']['final'] = _artifact(b'different final')
        replay = self.engine._collect_submitted_result(execution, other, self.context, self.schema, self.workspace)
        self.assertEqual(replay['output'], output)
        self.assertEqual(self.engine.head, head)
        applied = self.engine._apply_submission_bundles(self.context['action'], replay['output'], {}, execution['id'], self.context, [])
        self.assertEqual(applied['status'], 'accepted', applied)

    def test_rejected_native_final_leaves_explicit_retry_to_the_existing_fresh_execution_path(self):
        from do_math.payloads import json_safe
        from do_math.canonical import canonical_json
        execution = self.engine.runtime['executions']['EX-history']
        result = native_result(execution, self.context, b'{malformed', self.workspace)
        failed = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(failed['status'], 'failed')
        self.assertIn('central structural validation', failed['error'])
        execution = self.engine.runtime['executions']['EX-history']
        reference = 'runtime/artifacts/BA-native-rejection/result.json'
        execution['result_ref'] = reference
        self.engine._save({reference: canonical_json(json_safe(failed))})
        head = self.engine.head
        execution = self.engine.runtime['executions']['EX-history']
        self.assertFalse(self.engine._resume_initial_native_final(
            {'id': 'UC-explicit-retry'}, {}, execution))
        self.assertNotIn('submission_intent', execution)
        self.assertEqual(self.engine.head, head)
        self.assertEqual(json.loads(self.engine.store.read(reference))['error'], failed['error'])

    def test_explicit_early_seal_precedes_different_final_and_damage_never_falls_back(self):
        from unittest.mock import patch
        _, receipt = submit_history(self, 'CT-early', json.dumps(self.output, ensure_ascii=False).encode())
        self.assertEqual(receipt['state'], 'accepted', receipt)
        execution = self.engine.runtime['executions']['EX-history']
        result = {'status': 'completed', 'output': {'summary': 'alternate'}, 'collection': 'provider_evidence_only'}
        collected = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(collected['output'], self.output)
        head = self.engine.head
        from do_math import repository
        # Sealed rows are matched once per process (이음새-정본.md §3); damage is found by a
        # process that has not matched the row yet, modelled by an empty match set.
        with patch.object(self.engine.store, 'read', return_value=b'{"summary":"damaged"}'), \
                patch.dict(repository.VERIFIED_ARTIFACTS, clear=True):
            rejected = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(rejected['status'], 'failed')
        self.assertIsNone(rejected['output'])
        self.assertEqual(self.engine.head, head)

    def test_stopped_currentness_and_revoked_authority_preserve_without_capture(self):
        execution = self.engine.runtime['executions']['EX-history']
        raw = json.dumps(self.output).encode()
        result = native_result(execution, self.context, raw, self.workspace)
        original_runtime, original_instance = deepcopy(self.engine.runtime), deepcopy(self.engine.instance)
        head = self.engine.head
        for boundary in ('user_stop', 'paused', 'changed_input', 'revoked_grant', 'stopped_result', 'no_barrier'):
            with self.subTest(boundary=boundary):
                self.engine.runtime, self.engine.instance = deepcopy(original_runtime), deepcopy(original_instance)
                execution = self.engine.runtime['executions']['EX-history']; value = deepcopy(result)
                if boundary == 'user_stop': execution['stop_requested'] = 'user'
                elif boundary == 'paused':
                    self.engine.runtime['status'] = 'paused'
                    self.engine.instance['lifecycle']['state'] = 'paused'
                elif boundary == 'changed_input': execution['currentness_changes'] = [{'field':'test'}]
                elif boundary == 'revoked_grant': self.engine.instance['grants'][execution['grant_id']]['status'] = 'revoked'
                elif boundary == 'stopped_result': value['status'] = 'stopped'
                else: value['execution']['collect']['termination_barrier']['confirmed'] = False
                rejected = self.engine._collect_submitted_result(execution, value, self.context, self.schema, self.workspace)
                self.assertEqual(rejected['status'], 'failed', rejected)
                self.assertNotIn('submission_intent', execution)
                self.assertEqual(self.engine.head, head)
                self.assertFalse(any(e['kind']=='submission_checked' for e in self.engine.runtime['events']))

    def test_lost_cas_acknowledgment_resolves_one_native_capture(self):
        from unittest.mock import patch
        execution = self.engine.runtime['executions']['EX-history']
        result = native_result(execution, self.context, json.dumps(self.output).encode(), self.workspace)
        save = self.engine._save
        def committed_then_lost(artifacts):
            save(artifacts)
            raise OSError('acknowledgment lost after actual Git commit')
        with patch.object(self.engine, '_save', side_effect=committed_then_lost):
            collected = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(collected['status'], 'completed', collected)
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], 1)

    def test_malformed_native_json_is_preserved_as_one_rejected_central_check(self):
        execution = self.engine.runtime['executions']['EX-history']
        raw = b'{"report":'
        result = native_result(execution, self.context, raw, self.workspace)
        rejected = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(rejected['status'], 'failed')
        self.assertNotIn('submission_intent', self.engine.runtime['executions']['EX-history'])
        summary = self.engine._submission_check_summary(self.engine.head, self.engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], 1, rejected)
        self.assertTrue(summary['unresolved'])
        head = self.engine.head
        self.engine._collect_submitted_result(self.engine.runtime['executions']['EX-history'], result, self.context, self.schema, self.workspace)
        self.assertEqual(self.engine.head, head)


class NativeRepairTests(unittest.TestCase):
    def setUp(self):
        # The running maintenance execution is registered on a copy of the synthetic active state.
        start_native_final(self)

    def test_normal_malformed_final_routes_back_to_producer(self):
        execution = self.engine.runtime['executions']['EX-history']
        raw = b'{"report":'
        result = native_result(execution, self.context, raw, self.workspace)
        received = self.engine._collect_submitted_result(execution, result, self.context, self.schema, self.workspace)
        self.assertEqual(received['error_kind'], 'output_validation')
        from do_math.execution_lifecycle import transition_execution
        transition_execution(self.engine.runtime['executions'][execution['id']], 'stopping',
                             at='2026-09-22T12:00:00+00:00')
        self.engine._receive_submission(self.context['action'], received, execution['id'], self.context, self.schema, self.workspace)
        retry = next(a for a in self.engine.runtime['queue'] if a.get('continuation_of') == execution['id'])
        self.assertEqual(retry['role'], self.context['action']['role'])
        self.assertEqual(retry['repair_attempt'], 1)
        self.assertEqual(self.engine.store.read(retry['repair']['raw_output_ref'], self.engine.head), raw)


if __name__ == '__main__': unittest.main()
