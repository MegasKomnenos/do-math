"""7-A terminal absorption uses an actually completed research state and public controls."""
import unittest

from support.cross_contracts import ContractOracle
from support.engine_lifecycle import lifecycle_sim, solve_goal, THEOREMS


class TerminalAbsorptionTests(unittest.TestCase):
    def test_completed_research_cannot_become_assignable_after_stop_resume_or_configuration(self):
        """A completed theorem/goal fixture is a long flow; no terminal state is hand constructed."""
        sim = lifecycle_sim()
        identifier = next(key for key, row in sim.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(sim.engine, identifier)
        sim.engine._save()
        self.assertEqual(sim.runtime['status'], 'completed')
        oracle = ContractOracle(sim)
        before = set(sim.runtime['executions'])
        for action, options in (
            ('pause', {}), ('resume', {}), ('configure', {'config': {'plan_settle_seconds': 3}}),
        ):
            with self.subTest(action=action):
                result = sim.control(action, text='Terminal absorption probe', **options)
                sim.engine.process_controls()
                received = sim.engine.control_result(result['request_id'])
                if action == 'configure':
                    self.assertEqual(received['effect'], 'applied')
                    self.assertEqual(sim.instance['config']['plan_settle_seconds'], 3)
                else:
                    self.assertEqual(received['effect'], 'rejected')
                    self.assertIn('closed/completed', received['reason'])
                oracle.check(sim)
                self.assertEqual(sim.runtime['status'], 'completed')
                self.assertEqual(set(sim.runtime['executions']), before)
        sim.restart()
        oracle.check(sim)
        self.assertEqual(sim.runtime['status'], 'completed')
        self.assertEqual(set(sim.runtime['executions']), before)
