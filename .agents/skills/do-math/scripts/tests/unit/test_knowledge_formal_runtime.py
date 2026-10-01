"""Formal admission stays uncapped even under adopted host resource demands."""
import sys
import unittest


class FormalRuntimeTests(unittest.TestCase):
    def test_uncapped_lean_admission_with_an_adopted_host_budget(self):
        from do_math import execution_profiles as profiles
        from do_math.session_slots import SessionSlots
        from provider_fixtures import host_capacity_fixture
        from provider_fixtures import PROFILE_CONFIG
        _, _, constraint = host_capacity_fixture()
        bare = profiles.build_profiles(PROFILE_CONFIG)
        demands = {p['role']: {'jobs': 1, 'memory_bytes': 128*1024**2, 'cpu_rate_basis_points': 1000}
                   for p in bare['execution_profiles'].values() if p['role'] in profiles.HOST_ROLES}
        instance = profiles.build_profiles({**PROFILE_CONFIG, 'lean_command': [sys.executable],
            'host_resources': {'constraint': constraint, 'demands_by_role': demands}})
        profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'formal_check')
        self.assertIsNone(profiles.job_resource_limits(profile))
        invocation = profiles.machine_invocation(profile,
            trust_environment={'toolchain': {'configured_command': [sys.executable]}})
        self.assertNotIn("timeout_seconds", invocation)
        self.assertNotIn('resource_limits', invocation)
        runtime = {'executions': {}, 'reservations': {}}
        execution = {'id': 'EX-unlimited', 'role': 'formal_check', 'status': 'queued'}
        self.assertTrue(SessionSlots(runtime, instance).acquire(execution['id'],
            profile=profile, execution=execution))
        self.assertEqual(runtime['reservations'], {})
