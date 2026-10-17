"""A trust transition interrupted by a maintenance fence keeps its attempt lineage through the save and the retry.

The public path on an active Sim: a new toolchain is registered and a
transition requested by control; while the activation's environment check runs
(the host port observes the toolchain identity), a user quiesce control
arrives. The owner applies it before the check's result, the activation stops
and is requeued as a continuation, and after the release it succeeds.
"""
from copy import deepcopy
import json
import unittest

from support.trust_inputs import trust_fixture
from support.sim import Sim, warm_template
from support.wait_reporting import assert_activity_wait_row
from support.engine_lifecycle import (applied, executions, lifecycle_sim, only, prepared_environment,
                                      run_machine, transition)

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
        owner = first['owner_activity_id']
        held = deepcopy(engine.runtime['activities'][owner])
        self.assertEqual(held['waiting']['kind'], 'environment_interrupted')
        self.assertEqual(held['waiting']['condition'], {'transition_id': action['transition_id']})
        assert_activity_wait_row(self, engine.status(), owner, held)
        self.assertEqual(engine.runtime['activities'][owner], held)
        evidence_ref = 'runtime/artifacts/' + first['id'] + '/environment.json'
        evidence = engine.store.read(evidence_ref, engine.head)
        self.assertEqual(json.loads(evidence)['environment_id'], environment)
        for _ in range(2):
            engine.run(max_steps=1)
            self.assertEqual(engine.runtime['activities'][owner], held)
            self.assertEqual([row['id'] for row in _activations(sim) if row['id'] not in before], [first['id']])

        sim.control('release_quiesce', text='release the fence', config={'fence_id': fence['request_id']})
        sim.run_until(lambda s: engine.instance['active_trust_environment'] == environment, max_steps=4)
        successor, = [row for row in _activations(sim) if row['id'] not in before | {first['id']}]
        self.assertEqual(successor['continuation_of'], first['id'])
        self.assertEqual(successor['owner_activity_id'], first['owner_activity_id'])
        self.assertEqual(successor['outcome'], 'output_accepted')
        self.assertNotIn(owner, engine.status()['waiting_activities'])
        self.assertEqual(engine.store.read(evidence_ref, engine.head), evidence)
        self.assertFalse(engine.runtime.get('maintenance_fence'))
        self.assertEqual(sim.real_time_leaks(), [])

    def test_stopped_trust_check_keeps_condition_and_evidence_until_public_resume(self):
        """A reviewed-theorem template supplies real fixed transition targets."""
        sim = lifecycle_sim()
        tid = transition(sim, prepared_environment(sim))
        only(sim, 'trust_check', 'trust_activate')
        engine = sim.engine
        action = next(row for row in sim.runtime['queue'] if row['role'] == 'trust_check')
        spawn, requests = sim.lean.spawn, []

        def pause_during_check(command, **options):
            if not requests:
                requests.append(sim.control('pause', text='pause the exact trust check'))
            return spawn(command, **options)

        sim.lean.spawn = pause_during_check
        engine._save()
        sim.step()  # The scheduler applies the inbox before judging the compiler return.
        sim.lean.spawn = spawn
        first, = executions(sim, 'trust_check')
        self.assertEqual(first['outcome'], 'execution_incomplete')
        self.assertNotIn('submission_receipt', first)
        owner = first['owner_activity_id']
        held = deepcopy(sim.runtime['activities'][owner])
        self.assertEqual(held['waiting']['kind'], 'trust_check_stopped')
        self.assertEqual(held['waiting']['condition'], {'transition_id': tid, 'target': action['target'], 'resume': True})
        assert_activity_wait_row(self, engine.status(), owner, held)
        raw = engine.store.read(first['result_ref'], engine.head)
        self.assertEqual(json.loads(raw)['status'], 'stopped')
        self.assertNotIn(action['target'], sim.runtime['trust_transitions'][tid]['results'])
        for _ in range(2):
            engine.run(max_steps=1)
            self.assertEqual(sim.runtime['activities'][owner], held)
            self.assertEqual(len(executions(sim, 'trust_check')), 1)
        applied(sim, 'resume')
        applied(sim, 'resume')
        pending, = [row for row in sim.runtime['queue'] if row['id'] == action['id']]
        self.assertEqual(pending['continuation_of'], first['id'])
        run_machine(sim, 'trust_check')
        second, = [row for row in executions(sim, 'trust_check') if row['id'] != first['id']]
        self.assertEqual((second['continuation_of'], second['owner_activity_id'], second['outcome']),
                         (first['id'], owner, 'output_accepted'))
        self.assertEqual(sim.runtime['executions'][first['id']], first)
        self.assertEqual(engine.store.read(first['result_ref'], engine.head), raw)
        self.assertNotIn(owner, engine.status()['waiting_activities'])


if __name__ == '__main__':
    unittest.main()
