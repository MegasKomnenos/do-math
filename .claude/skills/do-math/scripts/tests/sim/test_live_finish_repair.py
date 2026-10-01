"""The scheduler drains existing calculations and blocks new work during repair."""
from copy import deepcopy
from dataclasses import replace
import tempfile
import unittest

from do_math.engine import ResearchEngine
from do_math.parallel import ModelCalls
from do_math.execution_lifecycle import transition_execution
from support.engine_lifecycle import clear_work, task
from support.fakes.calls import DeterministicCalls
from support.live_finish_drain import ExistingCalculation
from support.provider_live import running_execution
from support.provider_probes import ObservedCalls
from support.repair_host import repair_host
from support.sim import Sim, warm_template


setUpModule = warm_template


class InstallationRepairRoutingTests(unittest.TestCase):
    def test_scheduler_drains_existing_calls_without_dispatching_new_work_during_installation_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            host = repair_host(directory)
            sim = host.sim
            target = sim.runtime['executions']['EX-target']
            target.update(error='Installed receiver rejected valid output', result_ref=host.source)
            record = sim.runtime['operational_dispositions']['OD-repair']
            record.update(status='repair_required', disposition={'kind': 'repair', 'basis_refs': ['EX-target'],
                'next_owner': 'installation_recovery', 'reason': 'Repair the installed receiver',
                'repair_target': 'installation:scripts/do_math/engine.py', 'meaning_preserving': True,
                'verification': 'Run the receiver regression'})
            sim.engine._save()
            sim.engine._complete_operational_disposition(sim.runtime['operational_dispositions']['OD-repair'])
            sim.runtime['queue'] = [{'id': 'AC-independent', 'role': 'research_work'}]
            sim.engine._save()
            calls = ExistingCalculation(sim.clock)
            engine = ResearchEngine(sim.repository, sim.instance_id, ports=replace(sim.ports, calls=calls), codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
            with ObservedCalls(collect=ModelCalls.collect, close=DeterministicCalls.close,
                               dispatch=engine._dispatchable) as observed:
                engine._run_parallel()
            self.assertEqual(observed.count('collect'), 2)
            self.assertEqual(observed.count('close'), 1)
            self.assertEqual(observed.count('dispatch'), 0)
            self.assertEqual(calls.returned, [{'status': 'completed', 'output': None, 'usage': {}}])
            self.assertEqual(engine.runtime['status'], 'waiting')
            self.assertEqual(engine.runtime['queue'], [{'id': 'AC-independent', 'role': 'research_work'}])

    def test_scheduler_dispatches_no_research_while_an_installation_recovery_has_not_ended(self):
        sim = Sim.activated()
        clear_work(sim)
        selected = task(sim.engine, 'TK-independent')
        sim.runtime['queue'] = [{'id': 'AC-independent', 'role': 'research_work', 'target': selected['id']}]
        running_execution(sim, 'EX-repair', 'recovery')
        transition_execution(sim.runtime['executions']['EX-repair'], 'stopping', at=sim.clock.now())
        sim.runtime['status'] = 'ready'
        sim.engine._save()
        queue = deepcopy(sim.runtime['queue'])
        with ObservedCalls(dispatch=sim.engine._dispatchable) as observed:
            sim.engine._run_parallel()
        self.assertEqual(observed.count('dispatch'), 0)
        self.assertEqual(sim.runtime['queue'], queue)
