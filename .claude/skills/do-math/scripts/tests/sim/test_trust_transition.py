"""A trust transition interrupted by a maintenance fence keeps its attempt lineage through the save and the retry.

The public path on an active Sim: a new toolchain is registered and a
transition requested by control; while the activation's environment check runs
(the host port observes the toolchain identity), a user quiesce control
arrives. The owner applies it before the check's result, the activation stops
and is requeued as a continuation, and after the release it succeeds.
"""
import unittest

from support.trust_inputs import trust_fixture
from support.sim import Sim, warm_template

setUpModule = warm_template


def _activations(sim):
    return [row for row in sim.runtime['executions'].values() if row.get('role') == 'trust_activate']


class TrustContinuationTests(unittest.TestCase):
    def test_interrupted_activation_preserves_explicit_lineage_through_save_and_retry(self):
        """About 3 s, over the 2 s Sim budget: a template restore and two owner passes of a real trust transition."""
        sim = Sim.activated()
        engine = sim.engine
        old = engine.instance['trust_environments'][engine.instance['active_trust_environment']]
        request = trust_fixture(sim.root / 'next-trust', old['toolchain']['configured_command'])
        sim.control('trust', text='register the next toolchain', config=request)
        engine.process_controls()
        environment = next(key for key, row in engine.instance['trust_environments'].items()
                           if row['toolchain'] == request['toolchain'])
        sim.control('trust', text='move to the next toolchain', config={'operation': 'transition', 'env_id': environment})
        engine.process_controls()
        action = next(row for row in engine.runtime['queue'] if row['role'] == 'trust_activate')
        before = {row['id'] for row in _activations(sim)}

        fence = {}
        host = sim.ports.host
        observe = host.toolchain_identity_errors

        def observed_during_the_check(toolchain, **options):
            if not fence:  # the fence arrives while the short check runs
                fence.update(sim.control('quiesce', text='audit controlled interruption'))
            return observe(toolchain, **options)
        host.toolchain_identity_errors = observed_during_the_check
        sim.run_until(lambda s: any(row['id'] not in before for row in _activations(s)), max_steps=4)
        first, = [row for row in _activations(sim) if row['id'] not in before]
        self.assertTrue(fence)
        self.assertEqual((first['status'], first['outcome'], first['result_disposition']),
                         ('ended', 'execution_incomplete', {'kind': 'environment_interrupted'}))
        self.assertTrue(engine.runtime.get('maintenance_fence'))
        queued = next(row for row in engine.runtime['queue'] if row['id'] == action['id'])
        self.assertEqual(queued['continuation_of'], first['id'])
        _, _, persisted = engine.store.load()
        persisted_action = next(row for row in persisted['queue'] if row['id'] == action['id'])
        self.assertEqual(persisted_action['continuation_of'], first['id'])
        self.assertNotEqual(engine.instance['active_trust_environment'], environment)

        sim.control('release_quiesce', text='release the fence', config={'fence_id': fence['request_id']})
        sim.run_until(lambda s: engine.instance['active_trust_environment'] == environment, max_steps=4)
        successor, = [row for row in _activations(sim) if row['id'] not in before | {first['id']}]
        self.assertEqual(successor['continuation_of'], first['id'])
        self.assertEqual(successor['owner_activity_id'], first['owner_activity_id'])
        self.assertEqual(successor['outcome'], 'output_accepted')
        self.assertFalse(engine.runtime.get('maintenance_fence'))
        self.assertEqual(sim.real_time_leaks(), [])


if __name__ == '__main__':
    unittest.main()
