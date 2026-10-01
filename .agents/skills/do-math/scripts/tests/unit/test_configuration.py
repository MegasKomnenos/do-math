"""Stored configuration: its defaults and the cross-field rules of ``configuration.validate_config`` (layer 2)."""
from copy import deepcopy
from pathlib import Path
import re
import unittest

from do_math.configuration import DEFAULT_CONFIG, validate_config
from do_math.execution_profiles import HOST_ROLES, WORK_ROLES, build_profiles, host_constraint

SKILL = Path(__file__).resolve().parents[3]


class ConfigurationDefaultTests(unittest.TestCase):
    def test_default_input_limit_is_two_million_bytes_in_code_and_config_list(self):
        # The user's decision; the config list is the one document that states defaults.
        document = (SKILL / 'references' / 'CLI-실행-계약.md').read_text(encoding='utf-8')
        documented, = re.findall(r'^\| `max_input_bytes` \| (\d+) \|', document, flags=re.MULTILINE)
        self.assertEqual((DEFAULT_CONFIG['max_input_bytes'], int(documented)), (2_000_000, 2_000_000))


class ConfigurationRuleTests(unittest.TestCase):
    def test_model_selection_and_capacity_share_the_current_tier_configuration(self):
        from support.entry import entry
        _entry = entry()
        config = deepcopy(DEFAULT_CONFIG)
        config['tier_models'] = {tier: 'fixture-model' for tier in ('low', 'medium', 'high')}
        config['session_limits'] = {'work': {'fixture-model': 2}}
        config['scholarly_enabled'] = False
        self.assertIsNone(validate_config(config, host_id=_entry.host_id))
        profiles = build_profiles(config, host=_entry.ports.host)
        constraint, = profiles['capacity_constraints'].values()
        self.assertEqual((constraint['kind'], constraint['model'], constraint['work_slots']),
                         ('concurrency', 'fixture-model', 2))
        ai_profiles = [profile for profile in profiles['execution_profiles'].values() if profile['actor_kind'] == 'ai']
        self.assertTrue(ai_profiles)
        self.assertTrue(all(profile['ai']['model'] == 'fixture-model' for profile in ai_profiles))
        self.assertTrue(all(profile['ai']['capacity_refs'] == ([constraint['id']] if profile['role'] in WORK_ROLES else [])
                            for profile in ai_profiles))
        retired = deepcopy(config)
        retired['session_limits'] = {'work': {'fixture-model': 2}, 'operations': {'fixture-model': 1}}
        with self.assertRaisesRegex(ValueError, r"config/session_limits: Additional properties are not allowed "
                                                r"\('operations' was unexpected\)"):
            validate_config(retired, host_id=_entry.host_id)

    def test_each_rule_names_the_field_it_refuses(self):
        from support.entry import entry
        _entry = entry()
        cases = [
            ({'invented_setting': 1}, 'outside the stored configuration section: invented_setting'),
            ({'allowed_axioms': ['propext']}, 'outside the stored configuration section: allowed_axioms'),
            ({'session_limits': None}, 'config/session_limits: None is not of type'),
            ({'provider_retry_initial_seconds': 600, 'provider_retry_max_seconds': 300},
             'provider retry maximum must be at least the initial interval'),
            ({'lean_command': ['lean', 'bad\0argument']}, 'lean_command arguments must be NUL-free strings'),
        ]
        for change, message in cases:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, re.escape(message)):
                validate_config(change, host_id=_entry.host_id)
        self.assertIsNone(validate_config({'provider_retry_initial_seconds': 300, 'provider_retry_max_seconds': 300,
                                           'lean_command': ['lean', 'file.lean']}, host_id=_entry.host_id))

    def test_a_scholarly_server_is_an_absolute_command_without_a_data_directory(self):
        from support.entry import entry
        _entry = entry()
        absolute = str(SKILL / 'server.exe')
        self.assertIsNone(validate_config({'scholarly_server': {'command': absolute, 'args': []}}, host_id=_entry.host_id))
        with self.assertRaisesRegex(ValueError, 'scholarly args must not override the execution data directory'):
            validate_config({'scholarly_server': {'command': absolute, 'args': ['--data-dir=elsewhere']}}, host_id=_entry.host_id)
        with self.assertRaisesRegex(ValueError, 'relative scholarly command needs a configuration-file base'):
            validate_config({'scholarly_server': {'command': './server.exe', 'args': []}}, host_id=_entry.host_id)

    def test_host_resources_name_this_host_and_every_capped_role(self):
        constraint = host_constraint(host_id='fixture-host',
                                     limits={'jobs': 3, 'memory_bytes': 4096, 'cpu_rate_basis_points': 10000},
                                     control_reserve={'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000},
                                     authority_refs=['GS-fixture'])
        demands = {role: {'jobs': 1, 'memory_bytes': 1024, 'cpu_rate_basis_points': 1000} for role in HOST_ROLES}
        host = {'constraint': constraint, 'demands_by_role': demands}
        self.assertIsNone(validate_config({'host_resources': host}, host_id='fixture-host'))
        with self.assertRaisesRegex(ValueError, 'host_resources must name this local host'):
            validate_config({'host_resources': host}, host_id='another-host')
        missing = {**host, 'demands_by_role': {role: row for role, row in demands.items() if role != 'research_work'}}
        with self.assertRaisesRegex(ValueError, 'every capped role needs an explicit host demand'):
            validate_config({'host_resources': missing}, host_id='fixture-host')


if __name__ == '__main__':
    unittest.main()
