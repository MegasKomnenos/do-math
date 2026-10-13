"""The installed read tool on a real Git snapshot, and where an independent judgment's secret can reach it.

The read tool (``input/tools/read_input.py``, ``input_tool.read_main``) runs in
the producer's own process from the support archive the engine installs, and
reads the input snapshot through its own ``GitStateStore`` with no ports. So
these tests keep what they check real: a Git repository written by the git
program and the tool run as a child process. ``research_fixtures.role_reach``
reads a role's prompt, its workspace files and, through the tool, every indexed
record and every snapshot file that holds the secret.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_categories import test_group

from do_math import contracts, submission
from do_math.canonical import canonical_json
from do_math.git_store import GitStateStore
from do_math.state_contract import STATE_CONTRACT_ID
from support.record_builders import surface_state
from support.fakes.git_backend import make_repository
from support.cli_inputs import role_reach
from support.engine_context import prepare
from support.host_live import snapshot_read_fixture, snapshot_read_context, run_windowless_read

INSTANCE = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'
SCRIPTS = Path(__file__).resolve().parents[2]
PYTHONW = Path(sys.executable).with_name('pythonw.exe')



def envelope(family, record):
    return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})


@test_group('resource')
class SnapshotReachTests(unittest.TestCase):
    def snapshot(self, root, files):
        """``(record store binding, snapshot)`` of a new Git repository holding ``files``."""
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        repository = root / 'repository'
        repository.mkdir()
        make_repository(repository)
        store = {'repository': str(repository), 'instance_id': INSTANCE}
        return store, GitStateStore(repository, INSTANCE, backend=_entry.ports.git_backend, clock=_entry.ports.clock).publish(None, files).head

    def test_goal_auditor_cannot_reach_another_auditors_judgment(self):
        """About 5 s: a real Git snapshot and the read tool as a child process are what it checks."""
        # 계약/목표-감사.md 13: each audit slot seals its judgment in research/goal_judgments while
        # the other slots of the same round may still be unjudged; they must not read or cite it.
        secret = 'PRIVATE-PEER-AUDIT'
        judgment = {'id': 'GJ-peer', 'basis': 'BASIS', 'slot': 0, 'required': 2, 'decision': 'satisfied',
                    'summary': secret}
        instance, runtime = surface_state()
        instance['goal_judgments'] = [judgment]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'
            workspace.mkdir()
            store, snapshot = self.snapshot(root, {
                'research/goal_judgments/GJ-peer.json': envelope('goal_judgments', judgment),
                'runtime/executions/EX-1.json': envelope('executions', {'id': 'EX-1', 'role': 'research_work'})})
            fitted = prepare({'role': 'goal_audit', 'basis': 'BASIS', 'slot': 1, 'required': 2},
                             {'eligible_knowledge': []}, instance=instance, runtime=runtime,
                             extra={'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                             root=workspace, snapshot=snapshot, install=True)
            reached, held = role_reach(fitted['prompt'], workspace, secret)
            try:
                submission.validate_reference('GJ-peer', fitted['validation_context'], workspace)
                cited = True
            except ValueError:
                cited = False
        self.assertEqual(held, ['research/goal_judgments/GJ-peer.json'])
        self.assertEqual((reached, cited), ([], False))

    def test_operational_review_of_an_audit_slot_cannot_reach_another_slots_judgment(self):
        """About 5 s: a real Git snapshot and the read tool as a child process are what it checks."""
        # 계약/목표-감사.md 13: a live operational review of a running audit slot publishes its
        # disposition reason to that slot (engine: publish_worker_feedback), so the reviewer must
        # not see the round's other judgments either: inline, in the history or in the snapshot.
        from do_math import operational_dispositions
        secret = 'PRIVATE-PEER-AUDIT'
        judgment = {'id': 'GJ-peer', 'basis': 'BASIS', 'slot': 0, 'required': 2, 'decision': 'satisfied',
                    'summary': secret}
        audit = {'id': 'EX-audit', 'role': 'goal_audit', 'status': 'running',
                 'action': {'role': 'goal_audit', 'basis': 'BASIS', 'slot': 1, 'required': 2}}
        instance, runtime = surface_state()
        instance['goal_judgments'] = [judgment]
        runtime['executions']['EX-audit'] = audit
        action = {'role': 'operational_review', 'target': 'EX-audit', 'live': True}
        direct = {'execution_to_review': deepcopy(audit), 'observation': {}, 'operational_evidence': {},
                  'admissible_basis_refs': operational_dispositions.admissible_basis_refs(instance, runtime, action)}
        # The engine gives an operational review the goal judgments and the recent history.
        extra = {'goal_judgments': [judgment],
                 'recent_history': [{'role': 'goal_audit', 'execution_id': 'EX-peer', 'summary': secret}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'
            workspace.mkdir()
            store, snapshot = self.snapshot(root, {
                'research/goal_judgments/GJ-peer.json': envelope('goal_judgments', judgment),
                'runtime/executions/EX-audit.json': envelope('executions', audit)})
            fitted = prepare(action, direct, instance=instance, runtime=runtime,
                             extra={**extra, 'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                             root=workspace, snapshot=snapshot, install=True)
            reached, held = role_reach(fitted['prompt'], workspace, secret)
            try:
                submission.validate_reference('GJ-peer', fitted['validation_context'], workspace)
                cited = True
            except ValueError:
                cited = False
        self.assertEqual(held, ['research/goal_judgments/GJ-peer.json'])
        self.assertEqual((reached, cited), ([], False))

    def test_independent_judgment_cannot_reach_unpublished_work_of_the_execution_ledger(self):
        """About 16 s: each of three scopes runs the installed read tool in a child process on a real Git snapshot."""
        # Scopes whose ledger reach was judged only from the code: a delegation judge and the
        # executions it stays independent of (계약/의도-해석.md 69, delegations.record_judgment),
        # the interpreter's unfixed checkpoint (계약/의도-해석.md 50) and the unsealed lineage record
        # behind a review seat's operational review (공통-실행.md 「질문의 소유자와 영향을 받는 대상을
        # 밝힌다」). Each secret lives only in the execution ledger, and each input is built as the
        # engine builds it, so a supplied reference that names a ledger record is really supplied.
        from do_math import delegations, operational_dispositions
        from support.engine_context import INTENT_DIRECT
        secret = 'PRIVATE-UNPUBLISHED-WORK'
        instance, runtime = surface_state()
        seat = {'id': 'EX-seat', 'role': 'identity_review', 'status': 'running',
                'action': {'role': 'identity_review', 'review_cycle_id': 'RC-1'}}
        author = {'id': 'EX-author', 'role': 'intent_interpretation', 'status': 'ended'}
        runtime['executions'].update({'EX-seat': seat, 'EX-author': author})
        runtime['review_cycles'] = {'RC-1': {'id': 'RC-1'}}
        # The case names its original decision's author, whose execution the judge stays independent of.
        runtime['delegation_applications'] = {'DA-1': {'id': 'DA-1', 'input_sha256': 'c' * 64, 'judgments': {},
            'basis': {'original_decision': {'id': 'DC-1', 'actor': 'user', 'author_execution_ids': ['EX-author']},
                      'case': {'id': 'CASE-1', 'basis_refs': []}}}}
        delegation_case = delegations.judgment_input(runtime, 'DA-1')
        review_target = {'role': 'operational_review', 'target': 'EX-seat'}
        # A published canon record: every snapshot holds a research subtree.
        canon = {'research/decisions/DC-1.json': envelope('decisions', {'id': 'DC-1', 'actor': 'user'})}
        cases = [  # (action, direct inputs, snapshot files that hold the secret, other snapshot files)
            ({'role': 'intent_interpretation', 'stage': 'delegation_check', 'delegation_application_id': 'DA-1'},
             {'user_request': {'request': {'id': 'UI-1'}, 'delegation_case': deepcopy(delegation_case)},
              'delegation_case': deepcopy(delegation_case), 'interpretation_to_check': None},
             {'runtime/delegation_applications/DA-1.json': envelope('delegation_applications', {
                  'id': 'DA-1', 'judgments': {'interpret': {'execution_id': 'EX-peer', 'output': {'reason': secret}}}}),
              'runtime/executions/EX-author.json': envelope('executions', {**author, 'summary': secret})}, {}),
            ({'role': 'intent_interpretation', 'stage': 'check'}, INTENT_DIRECT,
             {'runtime/artifacts/BA-interpreter/checkpoint.json': secret.encode('utf-8')}, {}),
            (review_target, {'execution_to_review': deepcopy(seat), 'observation': {}, 'operational_evidence': {},
                             'admissible_basis_refs': operational_dispositions.admissible_basis_refs(
                                 instance, runtime, review_target)},
             {'runtime/review_cycles/RC-1.json': envelope('review_cycles', {'id': 'RC-1', 'summary': secret})},
             {'runtime/executions/EX-seat.json': envelope('executions', seat)}),
        ]
        for action, direct, unpublished, published in cases:
            with self.subTest(action=action), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workspace = root / 'workspace'
                workspace.mkdir()
                store, snapshot = self.snapshot(root, {**canon, **unpublished, **published})
                fitted = prepare(action, direct, instance=instance, runtime=runtime,
                                 extra={'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}},
                                 root=workspace, snapshot=snapshot, install=True)
                self.assertEqual(fitted['context']['record_map']['ledger'], 'supplied_only')
                reached, held = role_reach(fitted['prompt'], workspace, secret)
                self.assertEqual(held, sorted(unpublished))
                self.assertEqual(reached, [])
                if action is review_target:
                    # The seat's target is supplied and readable; only the lineage record it names is not.
                    self.assertIn('EX-seat', fitted['validation_context']['record_index']['runtime/executions'])


@test_group('resource')
class SnapshotReadToolTests(unittest.TestCase):
    """The installed read tool reads the fixed input snapshot within the record map and logs each read."""

    def setUp(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repository, self.decision, self.result, self.snapshot = snapshot_read_fixture(
            self.root, _entry.ports, INSTANCE)

    def workspace_context(self, ledger):
        return snapshot_read_context(self.root, self.repository, self.snapshot, INSTANCE, ledger)

    def read(self, ledger, *arguments, windowless=False):
        workspace, context = self.workspace_context(ledger)
        if windowless:
            observed = run_windowless_read(workspace, context, arguments, SCRIPTS)
            self.assertEqual(Path(observed['parent_executable']), PYTHONW)
            self.assertEqual(observed['parent_console'], 0)
            issued = json.loads((workspace / 'input/submission/context.json').read_bytes())
            self.assertEqual(issued['record_map']['read_tool']['command'][0], str(PYTHONW.with_name('python.exe')))
            self.assertEqual(observed['stderr'], '')
            code, stdout = observed['returncode'], observed['stdout']
        else:
            from support.entry import entry
            submission.install_tools(workspace, context, contracts.schema_for('maintenance'), None, clock=entry().ports.clock)
            result = subprocess.run([*context['record_map']['read_tool']['command'], *arguments], cwd=workspace,
                                    text=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            code, stdout = result.returncode, result.stdout
        log = (workspace / 'checks/reads.jsonl').read_text(encoding='utf-8').splitlines()
        return code, json.loads(stdout), [json.loads(line) for line in log]

    @unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')
    def test_indexed_record_is_read_from_the_input_snapshot_and_logged(self):
        """The real pythonw installer runs its issued command through PowerShell and collects JSON and exit status."""
        code, output, log = self.read('readable', '--id', 'DC-1', windowless=True)
        self.assertEqual(code, 0, output)
        row, = output['records']
        self.assertEqual((row['status'], row['path'], row['record']), ('ok', 'research/decisions/DC-1.json', self.decision))
        self.assertEqual([(entry['request'], entry['status'], entry['snapshot']) for entry in log],
                         [('DC-1', 'ok', self.snapshot)])

    @unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')
    def test_record_outside_the_index_is_refused_and_logged(self):
        code, output, log = self.read('supplied_only', '--id', 'EX-1', windowless=True)
        self.assertEqual(code, 1)
        self.assertEqual(output['records'][0]['status'], 'refused')
        self.assertNotIn('record', output['records'][0])
        self.assertEqual([(entry['request'], entry['status']) for entry in log], [('EX-1', 'refused')])

    def test_ledger_artifact_is_readable_only_where_the_ledger_is(self):
        path = 'runtime/artifacts/BA-1/result.json'
        code, output, _ = self.read('readable', '--path', path)
        self.assertEqual((code, output['records'][0]['text']), (0, self.result.decode()))
        code, output, _ = self.read('supplied_only', '--path', path)
        self.assertEqual((code, output['records'][0]['status']), (1, 'refused'))

    def test_family_listing_summarizes_its_indexed_records(self):
        code, output, log = self.read('readable', '--list', '--family', 'research/decisions')
        self.assertEqual(code, 0, output)
        self.assertEqual([(row['id'], row['kind']) for row in output['records']], [('DC-1', 'approval')])
        self.assertEqual(log[-1]['status'], 'ok')

    def test_invalid_output_path_is_refused_in_the_json_result(self):
        # 공통-실행.md 「읽기 도구로 읽는다」: the result is one JSON value and every request is logged.
        code, output, log = self.read('readable', '--path', 'runtime/artifacts/BA-1/result.json',
                                      '--output', '../outside.json')
        self.assertEqual((code, output['records'][0]['status']), (1, 'refused'))
        self.assertEqual(log[-1]['status'], 'refused')


if __name__ == '__main__':
    unittest.main()
