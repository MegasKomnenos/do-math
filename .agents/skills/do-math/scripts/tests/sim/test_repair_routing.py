"""Operational dispositions and installation repair on the real engine (``core_engine``, ``repair_execution``).

The dispositions are completed on the Sim's engine over the storage contract,
and the installation identity is the real hash of this installation.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import activities, execution_lifecycle
from do_math import scheduled_operator as operator
from do_math.repair_execution import installation_sha256
from support.repair_host import AT, repair_host
from support.sim import Sim, warm_template

setUpModule = warm_template
SKILL = Path(__file__).resolve().parents[3]


class OperationalDispositionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.host = repair_host(directory.name)
        self.engine = self.host.engine

    def test_operational_retry_of_an_ended_attempt_keeps_its_registered_successor(self):
        runtime = self.engine.runtime
        parent = runtime['executions']['EX-target']
        child = execution_lifecycle.create_execution(execution_id='EX-next', owner_activity_id=parent['owner_activity_id'],
            actor_kind='ai', input_manifest={}, profile_ref=parent['execution_profile_ref'], created_at=AT)
        child.update(role=parent['role'], continuation_of=parent['id'], action={**parent['action'], 'continuation_of': parent['id']})
        activities.assign_execution(runtime, parent['owner_activity_id'], child)
        self.engine._save()
        runtime = self.engine.runtime  # a save may replace the runtime object with the published one
        queue = list(runtime['queue'])
        result = self.engine._complete_operational_disposition(runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(result['status'], 'superseded')
        self.assertEqual(self.engine.runtime['queue'], queue)
        self.engine._save()
        _, _, stored = self.engine.store.load()
        self.assertEqual(stored['operational_dispositions']['OD-repair']['status'], 'superseded')
        self.assertEqual(stored['executions']['EX-next']['continuation_of'], 'EX-target')

    def test_installation_repair_handoff_preserves_failure_and_is_idempotent(self):
        runtime = self.engine.runtime
        target = runtime['executions']['EX-target']
        target.update(error='Installed receiver rejected valid output', result_ref=self.host.source)
        record = runtime['operational_dispositions']['OD-repair']
        record.update(status='repair_required', disposition={'kind': 'repair',
            'basis_refs': ['EX-target'], 'next_owner': 'installation_recovery',
            'reason': 'Repair the installed receiver', 'repair_target': 'installation:scripts/do_math/engine.py',
            'meaning_preserving': True, 'verification': 'Run the receiver regression'})
        self.engine._save()
        runtime = self.engine.runtime
        queue = list(runtime['queue'])
        result = self.engine._complete_operational_disposition(runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(result['status'], 'installation_repair_pending')
        self.assertEqual(result['result']['installation_repair'],
                         {'installation_sha256': installation_sha256(SKILL), 'evidence_refs': [self.host.source]})
        self.assertEqual(runtime['queue'], queue)
        self.assertEqual(self.host.destination.read_bytes(), b'damaged')
        head = self.engine.head
        _, _, stored = self.engine.store.load(head)
        self.assertEqual(stored['operational_dispositions']['OD-repair'], result)
        self.assertEqual(self.engine._complete_operational_disposition(result), result)
        self.assertEqual(self.engine.head, head)

    def test_a_repair_target_must_be_a_file_of_the_installed_skill(self):
        runtime = self.engine.runtime
        runtime['executions']['EX-target'].update(error='Installed receiver rejected valid output', result_ref=self.host.source)
        record = runtime['operational_dispositions']['OD-repair']
        record.update(status='repair_required', disposition={'kind': 'repair',
            'basis_refs': ['EX-target'], 'next_owner': 'installation_recovery', 'reason': 'Repair',
            'repair_target': 'installation:../outside.py', 'meaning_preserving': True, 'verification': 'Run it'})
        head = self.engine.head
        with self.assertRaisesRegex(ValueError, 'installation repair target must name an existing file inside the installed skill'):
            self.engine._complete_operational_disposition(record)
        self.assertEqual(self.engine.head, head)


    def test_complete_repair_consumes_only_the_current_repair_record(self):
        runtime = self.engine.runtime
        record = runtime['operational_dispositions']['OD-repair']
        with self.assertRaisesRegex(ValueError, 'complete_repair only consumes repair dispositions'):
            self.engine.complete_repair(record)
        with self.assertRaisesRegex(ValueError, 'repair must consume the current authoritative OD record'):
            self.engine.complete_repair({**record, 'status': 'changed'})
        with self.assertRaisesRegex(ValueError, 'repair must consume the current authoritative OD record'):
            self.engine.complete_repair({**record, 'id': 'OD-absent'})
        repaired = {**record, 'status': 'applied', 'disposition': {'kind': 'repair', 'basis_refs': ['EX-target'],
            'next_owner': 'installation_recovery', 'reason': 'Repair the installed receiver',
            'repair_target': 'installation:scripts/do_math/engine.py', 'meaning_preserving': True, 'verification': 'Run it'}}
        runtime['operational_dispositions']['OD-repair'] = repaired
        head = self.engine.head
        self.assertEqual(self.engine.complete_repair(repaired), repaired)
        self.assertEqual(self.engine.head, head)


class SubmissionReturnTests(unittest.TestCase):
    """An active instance restored from the template; the returns name executions the routing only refers to."""

    def test_repeated_submission_return_stops_producer_and_opens_one_diagnosis(self):
        sim = Sim.activated()
        engine = sim.engine
        self.assertEqual(engine.instance['config']['max_output_repairs'], 1)
        runtime = engine.runtime
        base = deepcopy(runtime['queue'])  # the template's own queue; each step is compared with the whole queue
        action = {'id': 'AC-producer', 'role': 'research_plan'}
        received = {'retry_bundle_ids': ['IN-failed'], 'bundles': [], 'issues': [{'rule_id': 'application'}]}
        engine.route_submission_return(action, received, 'EX-first', {'summary': 'preserved'})
        retry = {**action, 'continuation_of': 'EX-first', 'repair_attempt': 1, 'repair': {
            'execution_id': 'EX-first', 'previous_output': {'summary': 'preserved'}, 'retry_bundle_ids': ['IN-failed'],
            'bundle_results': [], 'issues': received['issues']}}
        self.assertEqual(runtime['queue'], base + [retry])
        runtime['queue'].pop()
        engine.route_submission_return(retry, received, 'EX-second', {'summary': 'preserved'})
        review = runtime['queue'][-1]
        self.assertEqual(runtime['queue'], base + [review])
        self.assertEqual((review['role'], review['target']), ('operational_review', 'EX-second'))
        self.assertIn('Bounded submission repair exhausted', review['reason'])
        wait = runtime['waiting_actions']['AC-producer']
        self.assertEqual((wait['kind'], wait['next_owner'], wait['execution_id']),
                         ('output_validation', 'operational_review', 'EX-second'))
        self.assertEqual(wait['action']['repair']['execution_id'], 'EX-second')
        self.assertEqual(wait['detail']['issues'], received['issues'])
        # Failed diagnostic output itself cannot open recursive diagnostics forever.
        engine.route_submission_return({**retry, 'role': 'operational_review'}, received, 'EX-op', {})
        self.assertEqual(runtime['queue'], base + [review])
        engine.instance['config']['max_output_repairs'] = 0
        engine.route_submission_return({'id': 'AC-zero', 'role': 'research_plan'}, received, 'EX-zero', {})
        second = runtime['queue'][-1]
        self.assertEqual(runtime['queue'], base + [review, second])
        self.assertEqual((second['role'], second['target']), ('operational_review', 'EX-zero'))
        self.assertIn('AC-zero', runtime['waiting_actions'])

    def test_a_rejected_submission_travels_with_the_repair(self):
        sim = Sim.activated()
        engine = sim.engine
        received = {'retry_bundle_ids': [], 'bundles': [], 'issues': [{'rule_id': 'schema.required'}]}
        rejected = {'check_ref': 'runtime/artifacts/BA-x/submission/check.json', 'submitted_output_ref': 'O'}
        engine.route_submission_return({'id': 'AC-rejected', 'role': 'research_plan'}, received, 'EX-rejected',
                                       {'summary': 'draft'}, rejected_submission=rejected)
        retry = next(a for a in engine.runtime['queue'] if a.get('id') == 'AC-rejected')
        self.assertEqual({key: retry['repair'][key] for key in ('execution_id', 'check_ref', 'submitted_output_ref', 'issues')},
                         {'execution_id': 'EX-rejected', **rejected, 'issues': received['issues']})


class EngineStartGuardTests(unittest.TestCase):
    def test_pending_installation_repair_prevents_a_redundant_engine_start(self):
        from support.entry import entry
        _entry = entry()
        status = {'status': 'ready', 'installation_repair': {'id': 'OD-pending'}}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / 'work'
            result = operator.engine_start_guard(Path(directory) / 'repo', 'RI-test', workspace, status=status, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports)
            self.assertEqual(result, {'outcome': 'installation_repair_waiting', 'before': status})
            operator.hold(workspace, reason='user hold', clock=_entry.ports.clock)
            self.assertEqual(operator.engine_start_guard(Path(directory) / 'repo', 'RI-test', workspace, status=status, codex_home=_entry.codex_home, environment=_entry.environment, host_id=_entry.host_id, ports=_entry.ports),
                             {'outcome': 'held'})


if __name__ == '__main__':
    unittest.main()
