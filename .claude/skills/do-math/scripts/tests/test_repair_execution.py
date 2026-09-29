"""Repair execution: the installation repair handoff and its routing, and retries of ended attempts over real Git."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import create_autospec, patch
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from record_fixtures import installation_repair_state
from research_fixtures import bare_engine





class InstallationRepairRoutingTests(unittest.TestCase):
    """Installation repair: routing a receiver defect to diagnosis, the repair request, and the work around it."""

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
        with patch.object(host.ports.calls, 'new', return_value=calls):
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
        with patch.object(host.ports.calls, 'new', return_value=calls):
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


if __name__ == "__main__":
    unittest.main()
