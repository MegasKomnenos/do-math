"""The governance view before charter adoption (``initialization.governance_or_initial_view``, layer 2).

The legacy test read it through ``ResearchEngine._governance`` on a bare engine,
which only passes the engine's instance and runtime to this function.
"""
import unittest

from do_math.initialization import governance_or_initial_view


class InitialGovernanceViewTests(unittest.TestCase):
    def test_paused_initialization_reads_original_input_but_active_corruption_fails(self):
        instance = {'governance': {}, 'lifecycle': {'state': 'paused', 'input_id': 'UC-one',
                                                    'immutable_input': {'ref': 'UC-one'}}}
        runtime = {'resume_lifecycle': 'initializing', 'inputs': [{'id': 'UC-one', 'config': {'goal': 'Original goal'}}]}
        view = governance_or_initial_view(instance, runtime)
        self.assertEqual((view['goal'], view['status']), ('Original goal', 'unadopted_input'))
        instance['governance'] = {'GD-policy': {'kind': 'policy', 'status': 'active'}}
        self.assertEqual(governance_or_initial_view(instance, runtime)['goal'], 'Original goal')
        instance['lifecycle']['state'] = 'active'
        with self.assertRaisesRegex(ValueError, 'no unique approved charter'):
            governance_or_initial_view(instance, runtime)


if __name__ == '__main__':
    unittest.main()
