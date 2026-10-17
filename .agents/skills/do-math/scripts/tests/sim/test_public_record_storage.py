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

    def test_setup_published_requests_reach_public_registration_and_stored_environments(self):
        from do_math.trust_validation import environment_errors
        from support.trust_inputs import setup_request_runs
        sim = Sim(self.root / 'consumer', goal='Store the actual setup request')
        runs = list(setup_request_runs(self.root / 'producer'))
        selected = [runs[0], runs[-1]]  # core baseline 0 and project(paths=2) baseline 1
        for branch, run in selected:
            with self.subTest(branch=branch):
                request = run['request']
                apply_control(sim, 'trust', config=request)
                eid = next(key for key, environment in sim.instance['trust_environments'].items()
                           if environment['toolchain_record'] == request['toolchain_record'])
                _, instance, runtime = sim.engine.store.load()
                environment = instance['trust_environments'][eid]
                binding = runtime['trust_bindings'][eid]
                self.assertEqual(environment_errors(environment, binding), [])
                self.assertEqual(set(environment), {'id', 'status', 'toolchain', 'allowed_axioms',
                                                    'source_ref', 'toolchain_record'})
                self.assertEqual(environment['status'], 'registered')
                self.assertEqual(environment['toolchain'], run['record']['identity'])
                self.assertEqual(environment['allowed_axioms'], request['allowed_axioms'])
                self.assertEqual(environment['toolchain_record'], request['toolchain_record'])
                self.assertEqual(binding, request['binding'])
                self.assertIn(environment['source_ref'], instance['governance_sources'])
                self.assertNotIn('binding', environment, 'runtime binding is a separate stored object')
                sim.restart()
                self.assertEqual(sim.instance['trust_environments'][eid], environment)
                self.assertEqual(sim.runtime['trust_bindings'][eid], binding)

    def test_tracker_open_boundary_rule_response_and_execution_stop_survive_reload(self):
        from support.engine_control import running_work
        from support.observation_inputs import observation_rule, self_check_response, write_checkpoint
        from do_math.state_contract import default_state_contract, validate_record
        sim = Sim.activated()
        rules = [observation_rule(required_evidence=['workspace:checkpoint.json'])]
        with running_work(sim, rules=rules) as call:
            call.observe({'type': 'item.started', 'item': {'id': 'C', 'type': 'command_execution'}})
            write_checkpoint(call.workspace, counters={'attempts': 2})
            call.observe({'type': 'tick'})
            obligation, = call.tracker.obligations.values()
            oid = obligation['id']
            opened = call.engine.store.load()[2]['self_check_obligations'][oid]
            self.assertEqual(opened['status'], 'open')
            self.assertIn('deadline_held_offset_ms', opened)
            call.submit('safety_boundary', {'inflight_calls': False, 'call_ids': ['C']}, 'boundary-storage')
            call.receive()
            boundary = call.receipt('boundary-storage')
            self.assertEqual(boundary['state'], 'accepted')
            self.assertNotIn('deadline_held_offset_ms', call.tracker.stored_obligations()[oid])
            proposal = {'current_revision': 0, 'reason': 'repeat at the next attempts boundary',
                        'rules': [observation_rule(id='renamed', repeat_interval=2,
                                                 required_evidence=['workspace:checkpoint.json'])]}
            response = {**self_check_response(obligation), 'rule_proposal': proposal}
            sent = call.self_check(oid, response)
            call.receive()
            receipt = call.receipt(sent['request_id'])
            self.assertEqual(receipt['state'], 'accepted')
            record, = [row for row in call.engine.runtime['self_check_responses'].values()
                       if row['obligation_id'] == oid]
            self.assertEqual(record['receipt_ref'], receipt['publication_id'])
            self.assertEqual(record['rule_update']['kind'], 'observation_rules_accepted')
            self.assertEqual(record['rule_update']['rules'], proposal['rules'])
            import json
            self.assertEqual(json.loads(record['response_json']), response)
            self.assertEqual(call.tracker.stored_obligations()[oid]['response_ref'], record['id'])
            self.assertEqual(call.tracker.stored_obligations()[oid]['status'], 'answered')
            # Current close boundary: a submitted result requests execution stop.
            # No current tracker API produces the legacy obligation status 'closed'.
            delivery = call.draft()
            call.receive()
            self.assertEqual(call.receipt(delivery['request_id'])['state'], 'accepted')
            self.assertEqual(call.execution['status'], 'stopping')
            expected = {family: deepcopy(call.engine.runtime[family]) for family in
                        ('observation_facts', 'self_check_obligations', 'self_check_responses', 'control_receipts')}
            expected_execution = deepcopy(call.execution)
            contract = default_state_contract()
            for family in ('observation_facts', 'self_check_obligations', 'self_check_responses'):
                for value in expected[family].values():
                    validate_record(contract.family('runtime', family).checker, value, family)
                    self.assertNotIn('control_call_ids', value)
            sim.restart()
            for family, values in expected.items():
                self.assertEqual(sim.runtime[family], values)
            self.assertEqual(sim.runtime['executions'][call.execution_id], expected_execution)
            self.assertEqual(sim.runtime['executions'][call.execution_id]['safe_boundary_report'],
                             {'receipt_id': boundary['publication_id'], 'inflight_calls': False, 'call_ids': ['C']})

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
        from support.trust_inputs import trust_fixture
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
        check = check_environment(environment, binding, host=LocalHost(clock=sim.ports.clock, environment=sim.environment, jobs=sim.ports.jobs, git_backend=sim.ports.git_backend), clock=sim.ports.clock)
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
