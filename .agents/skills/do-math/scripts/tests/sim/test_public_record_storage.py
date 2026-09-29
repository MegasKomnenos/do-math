"""Records the public controls make survive storage, and a widened or reshaped record is refused.

Each test starts from the public ``initialize`` on ``Sim`` (the real engine on
the port fakes) and applies public controls through the owner's control pass
(``apply_control``, which fails on a rejected control). The stored grant,
request and trust environment are then read back and one field is broken
against the storage contract.
"""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim
from support.storage_records import apply_control


class PublicRecordStorageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_public_initialize_control_and_source_bound_grant_round_trip(self):
        from do_math.governance import validate_grant_source
        sim = Sim(self.root, goal='Preserve original request')
        apply_control(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-test', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable',
            'execution_kinds': ['ai'], 'purposes': ['maintenance'], 'subjects': ['maintenance']}}})
        sim.restart()
        grant = sim.instance['grants']['GR-test']
        validate_grant_source(sim.instance, grant)
        self.assertEqual(grant['subjects'], ['maintenance'])
        changed = deepcopy(sim.instance)
        changed['grants']['GR-test']['subjects'].append('unapproved publication')
        with self.assertRaisesRegex(ValueError, 'approved scope'):
            sim.engine.store.validate_candidate(changed, sim.runtime)
        apply_control(sim, 'request', text='Inspect this run', config={'role': 'maintenance'})
        _, _, runtime = sim.engine.store.load()
        self.assertTrue(any(row.get('requested_by') for row in runtime['queue']))

    def test_public_initial_grant_adoption_preserves_exact_approved_scope(self):
        sim = Sim(self.root, goal='Check explicit initial grant adoption')
        apply_control(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
            'id': 'GR-initial', 'kind': 'local', 'roles': ['intent_interpretation'], 'reuse': 'reusable',
            'expires_at': (sim.clock.wall() + timedelta(days=1)).isoformat()}}})
        approved = deepcopy(sim.instance['grants']['GR-initial'])
        apply_control(sim, 'decision', config={'change': {'kind': 'initialization', 'initial_grant_ids': ['GR-initial']}})
        _, instance, runtime = sim.engine.store.load()
        self.assertEqual(instance['grants']['GR-initial'], approved)
        broken = deepcopy(instance)
        broken['grants']['GR-initial']['initialization_only'] = True
        with self.assertRaisesRegex(ValueError, '^grant differs from the actual approved scope$'):
            sim.engine.store.validate_candidate(broken, runtime)

    def test_public_trust_owner_flow_round_trip_requires_the_current_record_shape(self):
        from do_math.local_host import LocalHost
        from do_math.trust_validation import check_environment, environment_errors
        from research_fixtures import trust_fixture
        sim = Sim(self.root, goal='Check a synthetic environment contract')
        # Real files/owner flow, synthetic toolchain bytes: this is not Lean evidence.
        config = trust_fixture(self.root, ['synthetic-lean'])
        apply_control(sim, 'trust', config=config)
        eid = next(reversed(sim.instance['trust_environments']))
        environment, binding = sim.instance['trust_environments'][eid], sim.runtime['trust_bindings'][eid]
        self.assertEqual(environment_errors(environment, binding), [])
        self.assertEqual(binding, config['binding'])
        apply_control(sim, 'trust', config={'operation': 'transition', 'env_id': eid})
        # The real host observation of the synthetic toolchain, as the legacy test made it.
        check = check_environment(environment, binding, host=LocalHost())
        self.assertEqual((check['status'], check['fingerprint_sha256']), ('verified', binding['fingerprint_sha256']))
        sim.engine._finish_trust_transition(next(reversed(sim.runtime['trust_transitions'])), check)
        sim.engine._save()
        _, instance, runtime = sim.engine.store.load()
        self.assertEqual(instance['active_trust_environment'], eid)
        self.assertEqual(runtime['trust_bindings'][eid], binding)
        self.assertEqual(instance['trust_environments'][eid]['validation_receipt'], check)
        for field, value in (('manifest', {'files': []}), ('toolchain_record', {'path': 'relative.json', 'id': 'TC-x'})):
            broken = deepcopy(instance)
            broken['trust_environments'][eid][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'trust|additional'):
                sim.engine.store.validate_candidate(broken, runtime)
        unbound = deepcopy(runtime)
        del unbound['trust_bindings'][eid]
        with self.assertRaisesRegex(ValueError, 'trust binding'):
            sim.engine.store.validate_candidate(instance, unbound)


if __name__ == '__main__':
    unittest.main()
