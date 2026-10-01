"""A native final collected from a real Windows Job reaches central capture (tier T4).

The provider CLI's response is scripted, but its process is real: a suspended
Windows Job whose root, once resumed, writes the terminal evidence (stream,
final message, status) itself, and the product's Codex adapter collects it
through its termination barrier. The engine that captures it is a Sim's real
engine and store (``support.submission_scenes.native_scene``); reopening it is
``sim.restart()``.
"""
from copy import deepcopy
import json
import os
import sys
import unittest

from do_math.codex_adapter import CLIExecution, CodexExecAdapter, _artifact
from do_math.windows_job import WindowsJob, process_identity
from support.sim import warm_template
from support.submission_receiver import native_result
from support.submission_scenes import native_scene
from test_categories import test_group

setUpModule = warm_template


def job_native_result(case, scene, execution, raw):
    """Real Windows Job and adapter collector; only CLI response generation is scripted."""
    from support.entry import entry
    _entry = entry()
    from do_math.wiring import real_ports
    _entry.ports = real_ports(environment=_entry.environment)
    result = native_result(scene.sim, execution, scene.context, raw, scene.workspace)
    collected = result['execution']['collect']
    evidence = scene.workspace.parent / 'native-evidence'
    evidence.mkdir()
    payload = {'stdout.jsonl': collected['stdout']['raw'].decode(), 'final.txt': raw.decode(),
               'stderr.txt': '', 'status.json': json.dumps(collected['worker_status'])}
    # The suspended process itself writes all terminal evidence after resume.
    script = ("from pathlib import Path; import json,sys; p=Path(sys.argv[1]); d=json.loads(sys.argv[2]); "
              "[(p/k).write_bytes(v.encode('utf-8')) for k,v in d.items()]")
    argv = (sys.executable, '-B', '-c', script, str(evidence), json.dumps(payload, ensure_ascii=False))
    execution['launch_ticket']['phase'] = 'dispatched'
    execution['capacity']['local_termination'] = 'unknown'
    job = WindowsJob(argv, cwd=evidence, env=os.environ, name=execution['launch_ticket']['job_name'])
    native = CLIExecution(collected['source_request']['sha256'], collected['source_prompt']['sha256'], argv,
                          evidence / 'stdout.jsonl', evidence / 'stderr.txt', evidence / 'final.txt',
                          evidence / 'status.json', job, None, collected['source_request']['raw'],
                          collected['source_prompt']['raw'])
    adapter = CodexExecAdapter('fixture-cli', jobs=_entry.ports.jobs, clock=_entry.ports.clock)
    try:
        early = adapter.collect(native)
        case.assertFalse(early['artifacts_read'])
        case.assertFalse((evidence / 'final.txt').exists())
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


@test_group('resource')
class NativeFinalJobTests(unittest.TestCase):
    def test_native_capture_git_reload_summary_and_early_seal_precedence(self):
        scene = native_scene()
        engine = scene.engine
        # The public activation already sealed its own central checks; this capture adds one seal.
        base = engine._submission_check_summary(engine.head, engine.runtime)
        execution = engine.runtime['executions']['EX-history']
        output = {k: v for k, v in scene.output.items() if k != 'integration_bundles'}
        output['report'] = 'Exact e\u0301 \u00b7 \u00e9 \u00b7 \ud55c\uae00 \u00b7 \U0001f600'
        raw = json.dumps(output, ensure_ascii=False, indent=3).encode()
        result = job_native_result(self, scene, execution, raw)
        receipts_before = deepcopy(engine.runtime.get('control_receipts') or {})
        collected = engine._collect_submitted_result(execution, result, scene.context, scene.schema, scene.workspace)
        self.assertEqual(collected['status'], 'completed', collected)
        self.assertEqual(collected['collection'], 'sealed_submission')
        scene.sim.restart()
        engine = scene.engine
        execution = engine.runtime['executions']['EX-history']
        self.assertEqual(execution['submission_receipt']['kind'], 'native_final')
        # No worker control request was invented: the capture added no control receipt.
        self.assertEqual(dict(engine.runtime.get('control_receipts') or {}), receipts_before)
        self.assertFalse(any(row.get('execution_id') == 'EX-history'
                             for row in (engine.runtime.get('control_receipts') or {}).values()))
        self.assertEqual(engine.store.read(execution['submission_intent']['output_ref'], engine.head), raw)
        summary = engine._submission_check_summary(engine.head, engine.runtime)
        self.assertEqual(summary['status'], 'verified', summary)
        self.assertEqual(summary['seal_count'], base['seal_count'] + 1)
        head = engine.head
        other = deepcopy(result)
        other['execution']['collect']['final'] = _artifact(b'different final')
        replay = engine._collect_submitted_result(execution, other, scene.context, scene.schema, scene.workspace)
        self.assertEqual(replay['output'], output)
        self.assertEqual(engine.head, head)
        applied = engine._apply_submission_bundles(scene.context['action'], replay['output'], {}, execution['id'],
                                                   scene.context, [])
        self.assertEqual(applied['status'], 'accepted', applied)


if __name__ == '__main__':
    unittest.main()
