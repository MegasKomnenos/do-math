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

    def test_repair_waits_for_the_actual_review_to_end_before_local_effects(self):
        """Real registration and the existing repair host establish the local effect barrier."""
        engine = self.engine
        reviewer = engine._register_execution({'id': 'AC-live-repair-review', 'role': 'operational_review', 'target': 'EX-target'},
            {'id': 'EX-live-repair-review', 'role': 'operational_review'})
        record = engine.runtime['operational_dispositions']['OD-repair']
        record.update(execution_id=reviewer['id'], disposition={'kind': 'repair', 'basis_refs': ['EX-target'],
            'next_owner': 'installation_recovery', 'reason': 'Retain the review termination barrier',
            'repair_target': 'installation:scripts/do_math/engine.py', 'meaning_preserving': True,
            'verification': 'Inspect the actual receiver failure'})
        stored = engine.store.load()
        queue = deepcopy(engine.runtime['queue'])
        self.assertIs(engine._complete_operational_disposition(record), record)
        self.assertEqual(record['status'], 'repair_required')
        self.assertEqual(reviewer['status'], 'queued')
        self.assertEqual(engine.runtime['queue'], queue)
        self.assertEqual(engine.store.load(), stored)
        self.assertEqual(self.host.destination.read_bytes(), b'damaged')

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
        self.engine._run_pending_operational_repairs()
        result = self.engine.runtime['operational_dispositions']['OD-repair']
        self.assertEqual(result['status'], 'superseded')
        self.assertEqual(self.engine.runtime['queue'], queue)
        self.assertIs(self.engine._complete_operational_disposition(result), result)
        from support.engine_context import issue
        reviewer = self.engine.runtime['executions']['EX-review']
        issue(self.engine, reviewer, {'admissible_basis_refs': ['EX-target']}, 'BA-superseded-review')
        before_ids = set(self.engine.runtime['operational_dispositions'])
        self.engine._apply_operational_disposition({'target': 'EX-target'}, {
            'kind': 'retry', 'reason': 'The original review arrives after a successor was registered',
            'basis_refs': ['EX-target'], 'scope': 'Same unfinished work',
            'replay_safety': 'Keep the existing successor', 'next_owner': 'engine'}, reviewer['id'])
        new_id, = set(self.engine.runtime['operational_dispositions']) - before_ids
        self.assertEqual(self.engine.runtime['operational_dispositions'][new_id]['status'], 'superseded')
        self.assertEqual(self.engine.runtime['queue'], queue)
        self.engine._save()
        _, _, stored = self.engine.store.load()
        self.assertEqual(stored['operational_dispositions']['OD-repair']['status'], 'superseded')
        self.assertEqual(stored['executions']['EX-next']['continuation_of'], 'EX-target')
        before = self.engine.head
        self.engine._run_pending_operational_repairs()
        self.assertEqual(self.engine.head, before)
        self.assertEqual(self.engine.runtime['queue'], queue)

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
        from do_math.questions import handling_wait_ready
        question_wait = {'handling': {'state': 'waiting', 'waiting': {'kind': 'operational_disposition',
            'disposition_id': result['id']}}}
        self.assertFalse(handling_wait_ready(question_wait, self.engine.instance, self.engine.runtime,
            now=self.engine.ports.clock.now()), 'A pending installation handoff is not a repair receipt')
        self.assertEqual(result['result']['installation_repair'],
                         {'installation_sha256': installation_sha256(SKILL), 'evidence_refs': [self.host.source]})
        self.assertEqual(runtime['queue'], queue)
        self.assertEqual(self.host.destination.read_bytes(), b'damaged')
        head = self.engine.head
        _, _, stored = self.engine.store.load(head)
        self.assertEqual(stored['operational_dispositions']['OD-repair'], result)
        self.assertEqual(self.engine._complete_operational_disposition(result), result)
        self.assertEqual(self.engine.head, head)
        # This boundary receives the already verified repair receipt. It does
        # not run the external installer or claim that its verification ran.
        from do_math.repair_execution import resume_installation_repair
        resume_installation_repair(self.engine.runtime, self.engine.runtime['operational_dispositions'][result['id']],
            repaired_by='verified-repair-receipt', at=self.engine.ports.clock.now())
        self.assertTrue(handling_wait_ready(question_wait, self.engine.instance, self.engine.runtime,
            now=self.engine.ports.clock.now()))

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

    def returned(self):
        from do_math import submission
        from support.submission_receiver import history
        scene = history()
        self.assertEqual(submission.payload_issues(scene.output, scene.schema, scene.context,
            {}, scene.workspace, clock=scene.engine.ports.clock), [])
        output = deepcopy(scene.output)
        output['summary'] = []
        issues = submission.payload_issues(output, scene.schema, scene.context, {}, scene.workspace,
                                          clock=scene.engine.ports.clock)
        received = scene.engine._apply_submission_bundles(scene.action, output, {}, scene.execution_id,
                                                         scene.context, issues)
        self.assertEqual(received['status'], 'returned')
        self.assertTrue(received['issues'])
        return scene, received, output

    def test_exact_rejected_candidate_reaches_the_final_repair_role_input(self):
        import hashlib
        import json
        from do_math.canonical import canonical_json
        from do_math.context_store import prepare_role_input
        from support.engine_context import assert_delivery_documents, publish, review_input_value
        scene, received, output = self.returned()
        engine = scene.engine
        raw = canonical_json(output) + b' \r\n'
        ref = 'runtime/artifacts/BA-rejected/submission/raw-output.txt'
        publish(engine, {ref: raw})
        previous = engine.runtime['executions'][scene.execution_id]
        previous.update(status='ended', outcome='output_returned', output=deepcopy(output))
        engine.route_submission_return(scene.action, received, scene.execution_id, output,
            rejected_submission={'raw_output_ref': ref, 'raw_output_sha256': hashlib.sha256(raw).hexdigest()})
        retry = next(a for a in engine.runtime['queue'] if a.get('id') == scene.action['id'])
        self.assertEqual(retry['role'], scene.action['role'])
        self.assertEqual(retry['owner_activity_id'], previous['owner_activity_id'])
        workspace = scene.workspace / 'repair-input'
        context = engine._context(retry, workspace)
        prepared = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
            role=retry['role'], profile=engine._execution_profile(retry), snapshot=engine.head,
            workspace=workspace, activity_id=retry['id'], clock=engine.ports.clock)
        final = review_input_value(self, prepared['context'], 'action', workspace, manifest=prepared['manifest'])
        assert_delivery_documents(self, final['repair'], owner='repair', output=output,
            received=received, execution_id=scene.execution_id)
        self.assertEqual(final['continuation_of'], scene.execution_id)
        history = prepared['context']['continuation_history']
        self.assertEqual(history[-1]['execution_id'], scene.execution_id)
        response = history[-1]['rejected_response']
        self.assertEqual(response['artifact_ref'], ref)
        restored = (workspace / response['local_path']).read_bytes()
        self.assertEqual(restored, raw)
        self.assertEqual(json.loads(restored), output)
        self.assertEqual(response['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(response['bytes'], len(raw))

    def test_repeated_submission_return_stops_producer_and_opens_one_diagnosis(self):
        from support.engine_context import assert_delivery_documents
        scene, received, output = self.returned()
        engine = scene.engine
        self.assertEqual(engine.instance['config']['max_output_repairs'], 1)
        runtime = engine.runtime
        base = deepcopy(runtime['queue'])  # the template's own queue; each step is compared with the whole queue
        action = deepcopy(scene.action)
        engine.route_submission_return(action, received, 'EX-first', output)
        retry = {**action, 'continuation_of': 'EX-first', 'repair_attempt': 1, 'repair': {
            'execution_id': 'EX-first', 'previous_output': output, 'retry_bundle_ids': received['retry_bundle_ids'],
            'bundle_results': received['bundles'], 'issues': received['issues']}}
        self.assertEqual(runtime['queue'], base + [retry])
        assert_delivery_documents(self, runtime['queue'][-1]['repair'], owner='repair',
            output=output, received=received, execution_id='EX-first')
        for fault in ('missing_output', 'other_output', 'other_execution', 'wrong_scope'):
            changed = deepcopy(runtime['queue'][-1]['repair'])
            if fault == 'missing_output':
                del changed['previous_output']
            elif fault == 'other_output':
                changed['previous_output'] = {'summary': 'another candidate'}
            elif fault == 'other_execution':
                changed['execution_id'] = 'EX-other'
            else:
                changed['retry_bundle_ids'] = ['IN-other']
            reason = {'missing_output': 'repair.previous_output',
                      'other_output': 'another candidate',
                      'other_execution': "'EX-other' != 'EX-first'",
                      'wrong_scope': 'IN-other'}[fault]
            with self.subTest(fault=fault), self.assertRaisesRegex(AssertionError, reason):
                assert_delivery_documents(self, changed, owner='repair', output=output,
                    received=received, execution_id='EX-first')
        runtime['queue'].pop()
        engine.route_submission_return(retry, received, 'EX-second', output)
        review = runtime['queue'][-1]
        self.assertEqual(runtime['queue'], base + [review])
        self.assertEqual((review['role'], review['target']), ('operational_review', 'EX-second'))
        self.assertIn('Bounded submission repair exhausted', review['reason'])
        wait = runtime['waiting_actions'][action['id']]
        self.assertEqual((wait['kind'], wait['next_owner'], wait['execution_id']),
                         ('output_validation', 'operational_review', 'EX-second'))
        self.assertEqual(wait['action']['repair']['execution_id'], 'EX-second')
        assert_delivery_documents(self, wait['action']['repair'], owner='repair',
            output=output, received=received, execution_id='EX-second')
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
        scene, received, output = self.returned()
        engine = scene.engine
        rejected = {'check_ref': 'runtime/artifacts/BA-x/submission/check.json', 'submitted_output_ref': 'O'}
        engine.route_submission_return({'id': 'AC-rejected', 'role': 'research_plan'}, received, 'EX-rejected',
                                       output, rejected_submission=rejected)
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
