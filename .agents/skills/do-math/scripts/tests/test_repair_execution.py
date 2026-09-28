"""Repair execution: the installation repair handoff and its routing, and retries of ended attempts over real Git."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import create_autospec, patch
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import activities, execution_lifecycle
from do_math.engine import ResearchEngine
from do_math import repair_execution
from engine_fixtures import start_repair_host
from record_fixtures import installation_repair_state
from research_fixtures import bare_engine

AT = "2026-09-20T00:00:00Z"


class RepairExecutionTests(unittest.TestCase):
    def test_operational_retry_of_an_ended_attempt_keeps_its_registered_successor(self):
        host=self.host
        parent=host.runtime['executions']['EX-target']
        child=execution_lifecycle.create_execution(execution_id='EX-next',owner_activity_id=parent['owner_activity_id'],
            actor_kind='ai',input_manifest={},profile_ref=parent['execution_profile_ref'],created_at=AT)
        child.update(role=parent['role'],continuation_of=parent['id'],
                     action={**parent['action'],'continuation_of':parent['id']})
        activities.assign_execution(host.runtime,parent['owner_activity_id'],child)
        host._save()
        record=host.runtime['operational_dispositions']['OD-repair']
        result=ResearchEngine._complete_operational_disposition(host,record)
        self.assertEqual(result['status'],'superseded')
        self.assertEqual(host.runtime['queue'],[])
        host._save()
        _,_,stored=host.store.load()
        self.assertEqual(stored['operational_dispositions']['OD-repair']['status'],'superseded')
        self.assertEqual(stored['executions']['EX-next']['continuation_of'],'EX-target')

    def setUp(self):
        start_repair_host(self)

    def test_installation_repair_handoff_preserves_failure_and_is_idempotent(self):
        host = self.host
        target = host.runtime["executions"]["EX-target"]
        target.update(error="Installed receiver rejected valid output", result_ref=self.source)
        record = host.runtime["operational_dispositions"]["OD-repair"]
        record.update(status="repair_required", disposition={"kind": "repair",
            "basis_refs": ["EX-target"], "next_owner": "installation_recovery",
            "reason": "Repair the installed receiver", "repair_target": "installation:scripts/do_math/engine.py",
            "meaning_preserving": True, "verification": "Run the receiver regression"})
        host._save()
        with patch.object(repair_execution, "installation_sha256", return_value="a" * 64):
            result = ResearchEngine._complete_operational_disposition(host,
                host.runtime["operational_dispositions"]["OD-repair"])
        self.assertEqual(result["status"], "installation_repair_pending")
        self.assertEqual(host.runtime["queue"], [])
        self.assertEqual(self.destination.read_bytes(), b"damaged")
        head = host.head
        self.assertEqual(ResearchEngine._complete_operational_disposition(host, result), result)
        self.assertEqual(host.head, head)


class InstallationIdentityTests(unittest.TestCase):
    def test_identity_covers_the_installed_skill_but_not_its_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('scripts/do_math/a.py', 'scripts/tests/test_a.py', 'examples/case.json'):
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text('one', encoding='utf-8')
            before = repair_execution.installation_sha256(root)
            # A regression test alone does not reopen the same failure's automatic repair.
            (root / 'scripts/tests/test_a.py').write_text('two', encoding='utf-8')
            self.assertEqual(repair_execution.installation_sha256(root), before)
            (root / 'examples/case.json').write_text('two', encoding='utf-8')
            self.assertNotEqual(repair_execution.installation_sha256(root), before)


class InstallationRepairRoutingTests(unittest.TestCase):
    """Installation repair: routing a receiver defect to diagnosis, the repair request, and the work around it."""

    def test_repeated_submission_return_stops_producer_and_opens_one_diagnosis(self):
        opened = []
        engine = bare_engine({'config':{'max_output_repairs':1}}, {'queue':[], 'waiting_actions':{}})
        engine._enqueue = create_autospec(engine._enqueue, side_effect=lambda *a, **k: opened.append((a, k)))
        action = {'id':'AC-producer','role':'research_plan'}
        received = {'retry_bundle_ids':['IN-failed'], 'bundles':[], 'issues':[{'rule_id':'application'}]}
        engine.route_submission_return(action, received, 'EX-first', {'summary':'preserved'})
        retry = engine.runtime['queue'].pop()
        self.assertEqual(retry['repair_attempt'], 1)
        engine.route_submission_return(retry, received, 'EX-second', {'summary':'preserved'})
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(opened[0][0], ('operational_review','EX-second'))
        wait = engine.runtime['waiting_actions']['AC-producer']
        self.assertEqual(wait['action']['repair']['execution_id'], 'EX-second')
        self.assertEqual(wait['detail']['issues'], received['issues'])
        # Failed diagnostic output itself cannot open recursive diagnostics forever.
        engine.route_submission_return({**retry,'role':'operational_review'}, received, 'EX-op', {})
        self.assertEqual(len(opened), 1)
        engine.instance['config']['max_output_repairs'] = 0
        engine.route_submission_return({'id':'AC-zero','role':'research_plan'}, received, 'EX-zero', {})
        self.assertEqual(engine.runtime['queue'], [])
        self.assertIn('AC-zero', engine.runtime['waiting_actions'])

    def test_installation_request_requires_accepted_diagnosis_and_keeps_stable_identity(self):
        from do_math.repair_execution import installation_failure
        runtime, record = installation_repair_state()
        before = installation_failure(runtime, record)
        record['result']['installation_repair'].update(status='failed', attempted_by='EX-repair')
        record['status'] = 'installation_repair_waiting'
        self.assertEqual(installation_failure(runtime, record), before)
        runtime['executions']['EX-failed']['contract_sha256'] = 'changed-contract'
        self.assertNotEqual(installation_failure(runtime, record)['failure_sha256'], before['failure_sha256'])
        runtime['executions']['EX-diagnosis']['outcome'] = 'execution_incomplete'
        with self.assertRaises(ValueError): installation_failure(runtime, record)

    def test_unattempted_installation_diagnosis_is_not_starved_by_an_old_wait(self):
        from do_math.repair_execution import pending_installation_repair
        runtime, record = installation_repair_state()
        record['status'] = 'installation_repair_waiting'
        fresh = {**deepcopy(record),'id':'OD-fresh','status':'installation_repair_pending'}
        runtime['operational_dispositions'][fresh['id']] = fresh
        self.assertEqual(pending_installation_repair(runtime)['id'], 'OD-fresh')

    def test_pending_installation_repair_prevents_a_redundant_engine_start(self):
        from do_math import scheduled_operator as operator
        with tempfile.TemporaryDirectory() as directory, patch.object(operator,'read_status',return_value={
                'status':'ready','installation_repair':{'id':'OD-pending'}}):
            result = operator.engine_start_guard(Path(directory)/'repo','RI-test',Path(directory)/'work')
            self.assertEqual(result['outcome'],'installation_repair_waiting')

    def test_scheduler_drains_existing_calls_without_dispatching_new_work_during_installation_repair(self):
        from do_math.parallel import ModelCalls
        runtime, _ = installation_repair_state()
        runtime['queue'] = [{'id':'AC-independent','role':'research_work'}]
        calls = create_autospec(ModelCalls, instance=True)
        calls.futures = {'existing':object()}
        calls.collect.side_effect = lambda: calls.futures.clear() if calls.collect.call_count == 2 else None
        def dispatchable(action): raise AssertionError('new work must not be dispatched')
        host = bare_engine({'workspace':'.','id':'RI-test','config':{}}, runtime)
        host._controls = create_autospec(host._controls)
        host._check_installation = create_autospec(host._check_installation)
        host._save = create_autospec(host._save)
        host._settle_stops = create_autospec(host._settle_stops)  # stop judgment is not this rule
        host._dispatchable = create_autospec(host._dispatchable, side_effect=dispatchable)
        with patch('do_math.scheduler.ModelCalls',return_value=calls):
            host._run_parallel()
        self.assertEqual(calls.collect.call_count,2)
        self.assertTrue(calls.close.called)
        self.assertEqual(runtime['status'],'waiting')
        self.assertEqual(runtime['queue'],[{'id':'AC-independent','role':'research_work'}])

    def test_scheduler_dispatches_no_research_while_an_installation_recovery_has_not_ended(self):
        # The supervisor released its locks, but the restart recovery could not confirm that the
        # repair AI's local Job ended; it may still be changing the installation.
        from do_math.parallel import ModelCalls
        runtime = {'queue':[{'id':'AC-independent','role':'research_work'}], 'status':'ready',
                   'executions':{'EX-repair':{'id':'EX-repair','role':'recovery','status':'stopping'}},
                   'activities':{}, 'waiting_actions':{}, 'operational_dispositions':{}}
        calls = create_autospec(ModelCalls, instance=True)
        calls.futures = {}
        def dispatchable(action): raise AssertionError('new work must not be dispatched')
        host = bare_engine({'workspace':'.','id':'RI-test','config':{}}, runtime)
        for name in ('_controls', '_check_installation', '_save', '_settle_stops',
                     '_refresh_readiness', '_resume_formal_waits'):
            setattr(host, name, create_autospec(getattr(host, name)))
        host._scan_due = create_autospec(host._scan_due, return_value=True)
        host._dispatchable = create_autospec(host._dispatchable, side_effect=dispatchable)
        with patch('do_math.scheduler.ModelCalls',return_value=calls):
            host._run_parallel()
        self.assertEqual(runtime['queue'],[{'id':'AC-independent','role':'research_work'}])

    def test_supervisor_routes_diagnosed_live_engine_defect_and_probe_stays_read_only(self):
        from do_math import scheduled_operator as operator
        from types import SimpleNamespace
        runtime, record = installation_repair_state()
        # The engine status carries the pending diagnosis; probe reads its snapshot only.
        status = {'status':'ready','snapshot':'head','operator_enabled':True,
                  'installation_repair':deepcopy(record)}
        repository = SimpleNamespace(load=lambda snapshot: (snapshot,{'config':{'operator_enabled':True}},runtime))
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(operator,'read_status',return_value=status), \
                patch.object(operator,'ResearchRepository',return_value=repository), \
                patch.object(operator,'recovery',return_value={'outcome':'routed'}) as recover, \
                patch.object(operator,'schedule') as schedule:
            args = (Path(directory)/'repo', 'RI-test', Path(directory)/'work')
            probed = operator.check(*args,probe=True)
            self.assertEqual(probed['outcome'],'installation_repair_pending')
            self.assertEqual(probed['failure']['diagnosis_id'],record['id'])
            recover.assert_not_called(); schedule.assert_not_called()
            self.assertEqual(operator.check(*args)['outcome'],'routed')
            # Recovery rereads the pending diagnosis under its own lock.
            recover.assert_called_once_with(*args)
            operator.hold(args[2],reason='user hold')
            recover.reset_mock()
            self.assertEqual(operator.check(*args)['outcome'],'held')
            recover.assert_not_called()

    def test_installation_repair_continues_latest_rejected_bundles_without_resetting_count(self):
        from do_math.repair_execution import resume_installation_repair
        runtime, record = installation_repair_state()
        action = resume_installation_repair(runtime, record, repaired_by='EX-repair', at='2026-09-22T01:00:00Z')
        self.assertEqual(action['repair']['execution_id'],'EX-failed')
        self.assertEqual(action['repair_attempt'],2)
        self.assertEqual(action['continuation_of'],'EX-failed')
        self.assertEqual(runtime['waiting_actions'],{})
        self.assertEqual(record['status'],'applied')
        self.assertEqual(runtime['activities']['AY-work']['status'],'waiting')
        self.assertEqual(runtime['queue'],[action])


if __name__ == "__main__":
    unittest.main()
