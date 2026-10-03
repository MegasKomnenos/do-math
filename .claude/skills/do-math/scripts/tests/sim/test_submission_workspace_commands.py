"""3층 workspace 도구의 미도달 분기. 실제 저장·verifier/worker와 Ports를 연결한다."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from do_math import formal_preview, input_tool, submission_tool
from do_math.canonical import canonical_json
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template
from support.entry import entry


def setUpModule():
    warm_template()


def invoke(function, workspace, arguments, ports, environment):
    """실제 CLI가 쓰는 stdout.buffer를 보존한다."""
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding='utf-8')
    with contextlib.chdir(workspace), contextlib.redirect_stdout(stream):
        code = function(arguments, ports=ports, environment=environment)
    stream.flush()
    return code, json.loads(buffer.getvalue())


class ReadCommandTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        self.workspace = self.sim.root / 'read-command'
        (self.workspace / 'input/submission').mkdir(parents=True)
        self.path = 'runtime/artifacts/BA-command/text.txt'
        self.raw = '정확한 입력\n'.encode('utf-8')
        self.sim.engine._save({self.path: self.raw})
        self.snapshot = self.sim.engine.head
        self.identifier = next(iter(self.sim.runtime['executions']))
        self.context = {'snapshot': self.snapshot,
            'record_store': {'repository': str(self.sim.repository), 'instance_id': self.sim.instance_id},
            'record_index': {'runtime/executions': [self.identifier]},
            'record_map': {'ledger': 'readable', 'blocked_keys': []}}
        self.write_context()

    def write_context(self):
        (self.workspace / 'input/submission/context.json').write_bytes(canonical_json(self.context))

    def run_command(self, *arguments):
        return invoke(input_tool.read_main, self.workspace, list(arguments), self.sim.ports, self.sim.environment)

    def test_listing_and_batch_reads_use_one_fixed_snapshot_and_log_exact_bytes(self):
        code, summary = self.run_command('--list')
        self.assertEqual((code, summary), (0, {'snapshot': self.snapshot, 'status': 'ok',
                                             'ledger': 'readable', 'families': {'runtime/executions': 1}}))
        self.assertFalse((self.workspace / 'checks/reads.jsonl').exists())
        code, listed = self.run_command('--list', '--family', 'runtime/executions')
        self.assertEqual((code, listed['status'], [row['id'] for row in listed['records']]), (0, 'ok', [self.identifier]))
        first_time = self.sim.clock.now()
        self.sim.advance(3)
        from do_math.git_store import GitStateStore
        with ObservedCalls(read=GitStateStore.read_bytes) as calls:
            code, result = self.run_command('--path', self.path, '--id', self.identifier)
        self.assertEqual((code, result['snapshot'], result['status']), (0, self.snapshot, 'ok'))
        self.assertEqual(calls.count('read'), 2)
        self.assertEqual([row['commit'] for row in calls.captured('read')], [self.snapshot, self.snapshot])
        record, text = result['records']
        self.assertEqual(record['record']['id'], self.identifier)
        self.assertEqual(text, {'request': self.path, 'path': self.path, 'snapshot': self.snapshot,
            'status': 'ok', 'sha256': hashlib.sha256(self.raw).hexdigest(), 'bytes': len(self.raw), 'text': self.raw.decode()})
        logs = [json.loads(line) for line in (self.workspace / 'checks/reads.jsonl').read_bytes().splitlines()]
        self.assertEqual([row['at'] for row in logs], [first_time, self.sim.clock.now(), self.sim.clock.now()])
        self.assertNotEqual(first_time, self.sim.clock.now())
        self.assertEqual(logs[-1]['sha256'], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(logs[-1]['bytes'], len(self.raw))

    def test_output_writes_exact_bytes_and_refuses_fixed_input(self):
        code, result = self.run_command('--path', self.path, '--output', '.scratch/copy.txt')
        self.assertEqual((code, result['records'][0]['output']), (0, '.scratch/copy.txt'))
        self.assertEqual((self.workspace / '.scratch/copy.txt').read_bytes(), self.raw)
        original = (self.workspace / 'input/submission/context.json').read_bytes()
        code, result = self.run_command('--path', self.path, '--output', 'input/submission/context.json')
        self.assertEqual((code, result['records'][0]['status'], result['records'][0]['reason']),
                         (1, 'refused', '--output must not write into the fixed input/'))
        self.assertEqual((self.workspace / 'input/submission/context.json').read_bytes(), original)

    def test_unknown_id_and_family_are_refused_without_a_snapshot_read(self):
        from do_math.git_store import GitStateStore
        with ObservedCalls(read=GitStateStore.read_bytes, batch=GitStateStore.read_many) as calls:
            code, result = self.run_command('--id', 'EX-absent')
            self.assertEqual((code, result['records']), (1, [{'request': 'EX-absent', 'path': None,
                'snapshot': self.snapshot, 'status': 'refused',
                'reason': 'outside the record map of this input (record_index and record_map.ledger)'}]))
            code, result = self.run_command('--list', '--family', 'runtime/absent')
            self.assertEqual((code, result), (1, {'snapshot': self.snapshot, 'family': 'runtime/absent',
                                                 'status': 'refused', 'records': []}))
        self.assertEqual((calls.count('read'), calls.count('batch')), (0, 0))

    def test_missing_snapshot_file_is_an_error_with_the_exact_path(self):
        missing = 'runtime/artifacts/BA-command/missing.txt'
        code, result = self.run_command('--path', missing)
        self.assertEqual((code, result['records'][0]['status'], result['records'][0]['reason']),
            (1, 'error', f'git cat-file blob {self.snapshot}:{missing} failed: no blob at this path'))

    def test_family_batch_failure_keeps_exact_snapshot_and_one_read_log_entry(self):
        self.context['record_index']['runtime/executions'] = ['EX-missing']
        self.write_context()
        code, result = self.run_command('--list', '--family', 'runtime/executions')
        self.assertEqual((code, result['snapshot'], result['status'], result['records']),
                         (1, self.snapshot, 'error', []))
        self.assertIn('runtime/executions/EX-missing.json', result['reason'])
        logs = [json.loads(line) for line in (self.workspace / 'checks/reads.jsonl').read_bytes().splitlines()]
        self.assertEqual(logs, [{'at': self.sim.clock.now(), 'request': '--list runtime/executions',
            'path': 'runtime/executions', 'snapshot': self.snapshot, 'status': 'error', 'count': 0}])


class ArgumentRejectionTests(unittest.TestCase):
    def test_read_argument_errors_are_distinct_and_precede_context_access(self):
        values = entry()
        for args, reason in [([], 'give --list, or one or more --id or --path'),
            (['--list', '--id', 'EX-1'], 'give --list, or one or more --id or --path'),
            (['--id', 'EX-1', '--family', 'runtime/executions'], '--family requires --list'),
            (['--path', 'one', '--path', 'two', '--output', 'copy'], '--output takes exactly one --path')]:
            with self.subTest(args=args), tempfile.TemporaryDirectory() as directory:
                errors = io.StringIO()
                with contextlib.chdir(directory), contextlib.redirect_stderr(errors):
                    with self.assertRaisesRegex(SystemExit, '^2$'):
                        input_tool.read_main(args, ports=values.ports, environment=values.environment)
                self.assertIn('error: ' + reason + '\n', errors.getvalue())
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_submission_arguments_reject_missing_budget_and_conflicting_id_mode(self):
        values = entry()
        for args, reason in [([], '--output is required for checking, preview and submission'),
            (['--submit', '--output', 'draft.json'], 'central control requires an explicit --wait-seconds budget'),
            (['--new-knowledge-id', '--output', 'draft.json'], '--new-knowledge-id does not take output or wait arguments'),
            (['--new-knowledge-id', '--wait-seconds', '0'], '--new-knowledge-id does not take output or wait arguments')]:
            errors = io.StringIO()
            with self.subTest(args=args), contextlib.redirect_stderr(errors):
                with self.assertRaisesRegex(SystemExit, '^2$'):
                    submission_tool.main(args, ports=values.ports, environment=values.environment)
            self.assertIn('error: ' + reason + '\n', errors.getvalue())

    def test_closed_transport_does_not_wait_or_capture_a_draft(self):
        from do_math.control_transport import ControlTransport
        from do_math.control_server import wait_receipt
        from do_math import submission
        values = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input/submission').mkdir(parents=True)
            transport = ControlTransport(root / 'delivery', clock=values.ports.clock)
            binding = transport.issue('EX-closed', 'GR-closed', workspace=root)
            (root / 'input/submission/context.json').write_bytes(canonical_json({
                'execution_id': 'EX-closed', 'control_binding': binding}))
            transport.close(binding, reason='실행 종료')
            with ObservedCalls(wait=wait_receipt, seal=submission.seal_submission) as calls:
                delivery = submission_tool.request_control(root, 'draft.json', kind='submit_intent',
                    wait_seconds=0, clock=values.ports.clock)
            self.assertEqual((delivery['state'], delivery['reason']), ('closed', '실행 종료'))
            self.assertTrue(delivery['request_id'].startswith('submit-RQ-'))
            self.assertEqual((calls.count('wait'), calls.count('seal')), (0, 0))
            self.assertEqual(list((root / 'delivery').rglob('inbox/*.json')), [])

    def test_submit_and_preview_report_the_missing_binding_without_hiding_the_check(self):
        from do_math import contracts, submission
        from support.submission_obligations import maintenance_output
        values = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            submission.install_tools(root, {'execution_id': 'EX-unbound', 'snapshot': 'a' * 40,
                'action': {'role': 'maintenance'}}, contracts.schema_for('maintenance'), None, clock=values.ports.clock)
            (root / 'draft.json').write_bytes(canonical_json(maintenance_output()))
            for mode in ('--submit', '--preview'):
                with self.subTest(mode=mode):
                    code, result = invoke(submission_tool.main, root,
                        [mode, '--output', 'draft.json', '--wait-seconds', '0'], values.ports, values.environment)
                    self.assertEqual((code, result['delivery']),
                        (1, {'state': 'rejected', 'reason': 'draft has no matching execution control binding'}))
                    if mode == '--preview':
                        self.assertEqual((result['check']['passed'], result['check']['issues']), (True, []))
                    else:
                        self.assertEqual(set(result), {'delivery'})


class FormalPreviewCommandTests(unittest.TestCase):
    def test_missing_settings_is_an_unavailable_preview_with_no_authority(self):
        values = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input/submission').mkdir(parents=True)
            (root / 'input/submission/context.json').write_bytes(b'{}')
            code, result = invoke(formal_preview.main, root, ['--source', 'proof.lean', '--declaration', 't'],
                                  values.ports, values.environment)
            self.assertEqual((code, result), (1, {'status': 'unavailable', 'reason': "'formal_verifier'", 'authoritative': False}))

    def test_stop_and_missing_compiler_do_not_start_the_verifier(self):
        values = entry()
        from do_math.formal import verify_lean
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input/submission').mkdir(parents=True)
            (root / 'input/submission/context.json').write_bytes(canonical_json({
                'snapshot': 'a' * 40, 'formal_verifier': {'command': [], 'allowed_axioms': []}}))
            (root / 'proof.lean').write_text('theorem t : True := by trivial', encoding='utf-8')
            with ObservedCalls(verify=verify_lean) as calls:
                code, unavailable = invoke(formal_preview.main, root, ['--source', 'proof.lean', '--declaration', 't'],
                                           values.ports, values.environment)
                self.assertEqual((code, unavailable['status'], unavailable['reason'], unavailable['authoritative']),
                                 (1, 'unavailable', 'no compiler was supplied in this input', False))
                (root / '.control').mkdir()
                (root / '.control/stop-request.json').write_bytes(b'{}')
                code, stopped = invoke(formal_preview.main, root, ['--source', 'proof.lean', '--declaration', 't'],
                                       values.ports, values.environment)
                self.assertEqual((code, stopped['status'], stopped['reason'], stopped['input_snapshot']),
                                 (1, 'stopped', 'stop requested before compilation', 'a' * 40))
            self.assertEqual(calls.count('verify'), 0)

    def test_actual_verifier_worker_returns_signatures_without_central_evidence(self):
        sim = Sim.activated()
        root = sim.root / 'preview-command'
        (root / 'input/submission').mkdir(parents=True)
        source = 'theorem preview_contract : True := by trivial'
        sim.lean.allow(source, ['preview_contract'], signatures={'preview_contract': 'preview_contract : True'},
            declaration_evidence={'preview_contract': {'type': 'True', 'value': None}}, axioms={'preview_contract': []}, dependencies={'preview_contract': {}})
        (root / 'proof.lean').write_text(source, encoding='utf-8')
        (root / 'input/submission/context.json').write_bytes(canonical_json({'snapshot': sim.engine.head,
            'formal_verifier': {'command': sim.instance['config']['lean_command'], 'allowed_axioms': []}}))
        before = len(sim.lean.checks)
        head = sim.engine.head
        code, result = invoke(formal_preview.main, root, ['--source', 'proof.lean', '--declaration', 'preview_contract'],
                              sim.ports, sim.environment)
        self.assertEqual((code, result['status'], result['authoritative'], result['input_snapshot']),
                         (0, 'verified', False, head))
        self.assertEqual(result['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
        self.assertEqual(result['declarations'], ['preview_contract'])
        self.assertEqual(result['declaration_signatures'], {'preview_contract': 'preview_contract : True'})
        self.assertEqual(result['axioms'], {'preview_contract': []})
        self.assertEqual(sim.lean.checks[before:], [{'declarations': ['preview_contract'], 'extract': False,
                                                  'registered': True, 'synthetic': True}])
        self.assertEqual(sim.engine.head, head)
        self.assertNotIn('dependency_closure', result)
        self.assertEqual(list((root / '.scratch').iterdir()), [])
