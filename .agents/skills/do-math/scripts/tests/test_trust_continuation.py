from pathlib import Path
import sys
from copy import deepcopy

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
import test_input_recovery as input_fixtures
from do_math.engine import ResearchEngine
from do_math import maintenance_gate
from do_math.trust_validation import check_environment

def interrupted_activation():
    fixture = input_fixtures.InputRecoveryPublicTests()
    fixture.setUp()
    try:
        owner = ResearchEngine(fixture.repo, fixture.identifier)
        old = owner.instance['trust_environments'][owner.instance['active_trust_environment']]
        from research_fixtures import trust_fixture
        request = trust_fixture(fixture.root / 'next-trust', old['toolchain']['configured_command'])
        owner._apply_extended_control({'id':'UC-audit-register', 'action':'trust', 'origin':'user', 'config':request})
        env = next(k for k, v in owner.instance['trust_environments'].items() if v['toolchain'] == request['toolchain'])
        owner._apply_extended_control({'id':'UC-audit-transition', 'action':'trust', 'origin':'user',
            'config':{'operation':'transition', 'env_id':env}})
        owner._save()
        action = next(a for a in owner.runtime['queue'] if a['role'] == 'trust_activate')
        generator = owner._trust_activation_steps(action)
        execution_id, arguments = next(generator)
        owner._live_execution_ids.add(execution_id)
        maintenance_gate.apply_control(owner.runtime, {'id':'UC-fence', 'action':'quiesce', 'origin':'user',
            'text':'audit controlled interruption', 'created_at':owner.runtime['last_observed_utc']})
        # The short check completes; the fence found after it interrupts the activation.
        result = check_environment(**arguments)
        assert result['status'] == 'verified', result
        owner._local_call_returned(execution_id, result)
        try: generator.send(result)
        except StopIteration: pass
        queued = next(a for a in owner.runtime['queue'] if a['id'] == action['id'])
        _, _, persisted = owner.store.load()
        persisted_action = next(a for a in persisted['queue'] if a['id'] == action['id'])
        first = deepcopy(owner.runtime['executions'][execution_id])
        maintenance_gate.settle(owner.runtime)
        maintenance_gate.apply_control(owner.runtime, {'id':'UC-release', 'action':'release_quiesce', 'origin':'user',
            'config':{'fence_id':'UC-fence'}, 'created_at':owner.runtime['last_observed_utc']})
        owner._save()
        successor_action = next(a for a in owner.runtime['queue'] if a['id'] == action['id'])
        second_generator = owner._trust_activation_steps(successor_action)
        second_id, second_args = next(second_generator)
        successor = deepcopy(owner.runtime['executions'][second_id])
        owner._live_execution_ids.add(second_id)
        second_result = check_environment(**second_args)
        owner._local_call_returned(second_id, second_result)
        try: second_generator.send(second_result)
        except StopIteration: pass
        return {'first_execution':execution_id, 'first_status':first['status'],
            'local_action_continuation':action.get('continuation_of'),
            'queued_continuation':queued.get('continuation_of'),
            'persisted_action_continuation':persisted_action.get('continuation_of'),
            'successor_continuation':successor.get('continuation_of'),
            'same_owner_activity':first['owner_activity_id'] == successor['owner_activity_id'],
            'successor_outcome':owner.runtime['executions'][second_id].get('outcome')}
    finally:
        fixture.doCleanups()


import unittest
from test_categories import test_group

@test_group('integration')
class TrustContinuationTests(unittest.TestCase):
    def test_interrupted_activation_preserves_explicit_lineage_through_save_and_retry(self):
        result = interrupted_activation()
        for field in ('queued_continuation', 'persisted_action_continuation', 'successor_continuation'):
            self.assertEqual(result[field], result['first_execution'], field)
        self.assertTrue(result['same_owner_activity'])
        self.assertEqual(result['successor_outcome'], 'output_accepted')

if __name__ == '__main__':
    unittest.main()
