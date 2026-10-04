"""Long T3 7-A/2-D exploration, with shrinkable individual Sim events."""
import unittest

from hypothesis import settings
from support.cross_machine import assert_machine, DeadlineMachine, LiveMachine, LONG, ResearchMachine
from support.review_research import research_sim
from support.scheduling_parallel import ready_work_sim
from support.sim import warm_template

def setUpModule():
    warm_template()
    research_sim()
    ready_work_sim(1)
    DeadlineMachine().teardown()


class CrossResearchMachineTests(unittest.TestCase):
    def test_revised_research_closure_preserves_merged_request_reasons(self):
        from support.cross_obligations import assert_preserved_reasons
        from copy import deepcopy
        machine = ResearchMachine()
        self.addCleanup(machine.teardown)
        machine.revise_during_identity_review(0)
        machine.contracts_after_every_event()
        requests = deepcopy(machine.oracle.requests)
        self.assertTrue(requests)
        machine.close()
        machine.contracts_after_every_event()
        assert_preserved_reasons(requests, machine.sim.runtime)
        self.assertEqual(machine.sim.runtime['status'], 'closed')

    def test_long_transition_sequences(self):
        """Six twenty-event examples: worker calls and storage make this a flow budget."""
        assert_machine(ResearchMachine, LONG)

    def test_live_phase_transition_sequences(self):
        """Four eight-event examples, including live worker/owner interleavings."""
        assert_machine(LiveMachine, settings(LONG, max_examples=4, stateful_step_count=8))

    def test_regression_seeds_preserve_stop_authority_and_sealed_outputs(self):
        """A-06/B-12 seeds complement, rather than replace, the generated event sequences."""
        for phase in ('success', 'failure', 'pause', 'elapsed_work', 'tool_pause', 'sealed_quiesce'):
            with self.subTest(phase=phase):
                machine = LiveMachine()
                try:
                    machine.execution_event(phase)
                    machine.contracts_after_every_event()
                    machine.restart()
                    machine.contracts_after_every_event()
                    self.assertEqual(machine.sim.runtime['executions'][machine.observed[0]['id']]['status'], 'ended')
                finally:
                    machine.teardown()

    def test_operational_timeout_settles_before_restart(self):
        machine = DeadlineMachine()
        try:
            machine.operational_timeout()
            machine.restart()
            machine.contracts_after_every_event()
            self.assertEqual(len(machine.observed), 1)
        finally:
            machine.teardown()

    def test_revision_while_identity_review_is_open_seed(self):
        """A-39 regression order: open cycle -> revise -> owner pass -> restart."""
        machine = ResearchMachine()
        try:
            before = set(machine.sim.runtime['review_cycles'])
            self.assertTrue(any(c['status'] == 'working' for c in machine.sim.runtime['review_cycles'].values()))
            machine.revise_during_identity_review(0)
            machine.contracts_after_every_event()
            machine.owner_pass()
            machine.contracts_after_every_event()
            machine.restart()
            machine.contracts_after_every_event()
            self.assertTrue(before <= set(machine.sim.runtime['review_cycles']))
            self.assertTrue(all(machine.sim.runtime['review_cycles'][cid]['status'] != 'working' for cid in before))
        finally:
            machine.teardown()

    def test_expanded_scope_then_revision_does_not_poison_next_owner_pass(self):
        """B-47 seed: independently scoped extra slot -> user revision -> owner/restart."""
        machine = ResearchMachine()
        try:
            machine.sim.run_until(lambda s: bool(s.runtime['queue'])
                                  and s.runtime['queue'][0]['role'] == 'identity_review'
                                  and s.runtime['queue'][0].get('stage') == 'scope', max_steps=6)
            machine.expand_review_scope()
            machine.contracts_after_every_event()
            cycles = machine.sim.runtime['review_cycles']
            cid = next(cid for cid, c in cycles.items() if c.get('scope_assessment'))
            self.assertIn('initial-cross', [s['id'] for s in cycles[cid]['scope_assessment']['initial_slots']])
            machine.revise_during_identity_review(0)
            machine.contracts_after_every_event()
            machine.owner_pass()
            machine.contracts_after_every_event()
            machine.restart()
            machine.contracts_after_every_event()
            self.assertNotEqual(machine.sim.runtime['review_cycles'][cid]['status'], 'working')
            self.assertFalse(any(a.get('review_cycle_id') == cid for a in machine.sim.runtime['queue']))
        finally:
            machine.teardown()
