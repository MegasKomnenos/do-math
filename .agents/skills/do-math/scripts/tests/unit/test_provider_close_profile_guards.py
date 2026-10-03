"""불변 프로필은 봉인을 다시 만든 뒤 목표 guard의 사유를 확인한다."""
from copy import deepcopy
import re
import unittest

from do_math import execution_profiles as profiles
from do_math.canonical import exact_content_hash


class ProfileGuardTests(unittest.TestCase):
    def seed(self):
        return {'revision': 1, 'role': 'maintenance', 'actor_kind': 'ai',
                'ai': {'model': 'test'}, 'boundary': profiles.BOUNDARY,
                'observation': {'mode': 'deadline_only', 'rule_bindings': []}}

    def sealed(self, body):
        digest = exact_content_hash(body)
        return {**deepcopy(body), 'id': 'EP-' + digest, 'sha256': digest}

    def test_role_model_boundary_and_edition_guards(self):
        cases = [({'revision': 0}, 'unsupported profile edition'),
            ({'actor_kind': 'outside'}, 'profile requires an actor'),
            ({'ai': {}}, 'AI profile requires a model'),
            ({'ai': {'model': 'test', 'capacity_refs': ['CP-one']}}, 'only work roles reserve a model slot'),
            ({'observation': {'mode': 'outside', 'rule_bindings': []}}, 'observation mode differs from role responsibility'),
            ({'observation': {'mode': 'deadline_only', 'rule_bindings': None}}, 'profile observation bindings differ from the supported role contract'),
            ({'boundary': 'outside'}, 'this implementation supports only the declared instruction boundary'),
            ({'host_capacity_refs': ['CP-one']}, 'host references require pinned execution demands')]
        for changes, reason in cases:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    profiles.validate_profile(self.sealed({**self.seed(), **changes}))
        profile = self.sealed(self.seed())
        self.assertIsNone(profiles.validate_profile(profile))
        self.assertEqual(profiles.profile_ref(profile), {key: profile[key] for key in ('id', 'revision', 'sha256')})

    def test_host_amounts_reject_shape_type_range_and_multi_job_demand(self):
        seed = {'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 100}
        for value, demand, reason in (({}, False, 'host amounts require explicit jobs, memory_bytes and cpu_rate_basis_points'),
            ({**seed, 'jobs': True}, False, 'host amounts must be explicit nonnegative integers (positive for a demand)'),
            ({**seed, 'jobs': 0}, True, 'host amounts must be explicit nonnegative integers (positive for a demand)'),
            ({**seed, 'jobs': 2}, True, 'CPU cap must be at most 10000 and one execution owns one simultaneous Job tree'),
            ({**seed, 'cpu_rate_basis_points': 10001}, False, 'CPU cap must be at most 10000 and one execution owns one simultaneous Job tree')):
            with self.subTest(value=value, demand=demand):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                    profiles._host_amounts(value, demand=demand)
        self.assertIsNone(profiles._host_amounts(seed, demand=True))

    def test_host_constraint_requires_exact_approved_edition(self):
        limits = {'jobs': 2, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000}
        reserve = {'jobs': 1, 'memory_bytes': 512, 'cpu_rate_basis_points': 500}
        valid = profiles.host_constraint(host_id='host', limits=limits, control_reserve=reserve, authority_refs=['GS-one'])
        self.assertIsNone(profiles.validate_host_constraint(valid))
        with self.assertRaisesRegex(ValueError, '^host constraint must be an object$'):
            profiles.validate_host_constraint(None)
        with self.assertRaisesRegex(ValueError, '^host constraint differs from its approved immutable edition$'):
            profiles.validate_host_constraint({**valid, 'id': 'CP-other'})
        with self.assertRaisesRegex(ValueError, '^host constraint needs host, approval and reserve within the adopted limits$'):
            profiles.host_constraint(host_id='host', limits=limits, control_reserve={**reserve, 'jobs': 3}, authority_refs=['GS-one'])

    def test_host_and_machine_populations_keep_exact_guards(self):
        for role in profiles.MACHINE_ROLES:
            body = {**self.seed(), 'role': role, 'actor_kind': 'machine'}
            with self.subTest(role=role):
                with self.assertRaisesRegex(ValueError, '^machine profile cannot contain AI fields$'):
                    profiles.validate_profile(self.sealed(body))
        limits = {'jobs': 2, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000}
        reserve = {'jobs': 1, 'memory_bytes': 512, 'cpu_rate_basis_points': 500}
        constraint = profiles.host_constraint(host_id='host', limits=limits, control_reserve=reserve, authority_refs=['GS-one'])
        demand = {'jobs': 1, 'memory_bytes': 100, 'cpu_rate_basis_points': 100}
        host = {'constraint': constraint, 'demands_by_role': {role: deepcopy(demand) for role in profiles.HOST_ROLES}}
        self.assertIsNone(profiles.validate_host_resources(host))
        for value, reason in (({}, 'host authoring requires an approved constraint and explicit demands_by_role'),
            ({**host, 'demands_by_role': []}, 'host demands_by_role must be an object')):
            with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
                profiles.validate_host_resources(value)
        bad = self.sealed({**self.seed(), 'host_resources': {}})
        with self.assertRaisesRegex(ValueError, '^host profile requires one exact local instance constraint$'):
            profiles.validate_profile(bad)

    def test_capacity_and_capability_gaps_use_the_actual_profile_producer(self):
        from do_math.configuration import DEFAULT_CONFIG
        from support.entry import entry
        host = entry().ports.host
        config = deepcopy(DEFAULT_CONFIG)
        config['session_limits']['work'] = {}
        with self.assertRaisesRegex(ValueError, '^tier model has no adopted capacity$'):
            profiles.build_profiles(config, host=host)
        profile = next(iter(profiles.build_profiles(DEFAULT_CONFIG, host=host)['execution_profiles'].values()))
        with self.assertRaisesRegex(ValueError, '^unsupported local structural capability$'):
            profiles.structural_failure_evidence(profile, {}, observed_at='2090-01-01T00:00:00+00:00',
                execution_id='EX-one', evidence_ref='artifact:one', capability='outside')
        with self.assertRaisesRegex(ValueError, '^capability evidence requires current identity and observation time$'):
            profiles.capability_evidence(profile, {'identity': {}}, observed_at='2090-01-01T00:00:00+00:00')
