"""Formal admission stays uncapped even under adopted host resource demands."""
import sys
import unittest


class FormalRuntimeTests(unittest.TestCase):
    def test_uncapped_lean_admission_with_an_adopted_host_budget(self):
        from support.entry import entry
        _entry = entry()
        from do_math import execution_profiles as profiles
        from do_math.session_slots import SessionSlots
        from support.provider_inputs import host_capacity_fixture
        from support.provider_inputs import PROFILE_CONFIG
        _, _, constraint = host_capacity_fixture()
        bare = profiles.build_profiles(PROFILE_CONFIG, host=_entry.ports.host)
        demands = {p['role']: {'jobs': 1, 'memory_bytes': 128*1024**2, 'cpu_rate_basis_points': 1000}
                   for p in bare['execution_profiles'].values() if p['role'] in profiles.HOST_ROLES}
        instance = profiles.build_profiles({**PROFILE_CONFIG, 'lean_command': [sys.executable],
            'host_resources': {'constraint': constraint, 'demands_by_role': demands}}, host=_entry.ports.host)
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'formal_check')
        self.assertIsNone(profiles.job_resource_limits(profile, host_id=_entry.host_id))
        invocation = profiles.machine_invocation(profile,
            trust_environment={'toolchain': {'configured_command': [sys.executable]}})
        self.assertNotIn("timeout_seconds", invocation)
        self.assertNotIn('resource_limits', invocation)
        runtime = {'executions': {}, 'reservations': {}}
        execution = {'id': 'EX-unlimited', 'role': 'formal_check', 'status': 'queued'}
        self.assertTrue(SessionSlots(runtime, instance, clock=_entry.ports.clock, host_id=_entry.host_id, jobs=_entry.ports.jobs).acquire(execution['id'],
            profile=profile, execution=execution))
        self.assertEqual(runtime['reservations'], {})


class MachineResultReceiverTests(unittest.TestCase):
    """Layer-2 receiver inputs, not claims about a possible Lean producer result.

    Real producer/owner wiring is covered by flows.test_scheduling_machine_calls
    and flows.test_lifecycle_engine_trust. No callable is replaced here.
    """

    def test_wrong_compiler_is_rejected(self):
        """The restored lifecycle input preserves real trust/storage contracts; only the layer-2 continuation is exercised."""
        from support.engine_lifecycle import lifecycle_sim, prepared_environment, transition
        sim = lifecycle_sim()
        tid = transition(sim, prepared_environment(sim))
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'trust_check')
        receiver = sim.engine._trust_check_steps(action)
        self.addCleanup(receiver.close)
        eid, arguments = next(receiver)
        # verify_lean copies the pinned expected_toolchain after validating it;
        # a verified result with this fingerprint is a receiver-only input.
        result = {'status': 'verified', 'source_sha256': sim.runtime['trust_transitions'][tid]['targets'][0]['source_sha256'],
                  'toolchain': {'sha256': 'wrong'}, 'launch_not_created': True}
        sim.engine._local_call_returned(eid, result)
        with self.assertRaisesRegex(StopIteration, '^$'):
            receiver.send(result)
        received = sim.runtime['trust_transitions'][tid]['results'][action['target']]
        self.assertEqual(received['status'], 'rejected')
        self.assertEqual(received['reason'], 'Compiler fingerprint or source differs from the fixed transition input')

    def test_interrupted_receiver_preserves_bytes_decimal_and_routes_failure(self):
        """The restored formal scene supplies valid capacity/storage inputs to the layer-2 interruption receiver."""
        import base64
        import json
        from do_math.canonical import canonical_json
        from do_math.payloads import json_safe
        from support.scheduling_machine import formal_scene
        sim, action, _ = formal_scene()
        receiver = sim.engine._formal_steps(action)
        self.addCleanup(receiver.close)
        eid, arguments = next(receiver)
        cycles = set(sim.runtime.get('review_cycles', {}))
        result = {'status': 'stopped', 'reason': 'owner stopped', 'launch_not_created': True,
                  'stdout': b'preserved evidence\xff', 'usage': {'cost_usd': 0.25}}
        raw = canonical_json(json_safe(result))
        artifacts = sim.engine._record_interrupted_calls([(eid, raw, 'synthetic:local-result', result)])
        sim.engine._save(artifacts)
        execution = sim.runtime['executions'][eid]
        preserved = json.loads(sim.engine.store.read(execution['result_ref']))
        self.assertEqual(base64.b64decode(preserved['stdout']['base64']), b'preserved evidence\xff')
        self.assertEqual(preserved['usage']['cost_usd'], {'reported_decimal': '0.25'})
        self.assertEqual((execution['status'], execution['capacity']['local_termination']), ('ended', 'confirmed'))
        self.assertEqual(set(sim.runtime.get('review_cycles', {})), cycles)
        self.assertEqual(sim.runtime['waiting_actions'][action['id']]['kind'], 'execution_failure')
        self.assertFalse(any(a.get('id') == action['id'] for a in sim.runtime['queue']))
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == eid for a in sim.runtime['queue']))
        self.assertEqual(sim.runtime['activities'][execution['owner_activity_id']]['status'], 'waiting')
