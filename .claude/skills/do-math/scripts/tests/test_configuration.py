"""Public configuration has one current execution model."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import initialize
from do_math.configuration import DEFAULT_CONFIG, validate_config
from do_math.execution_profiles import WORK_ROLES, build_profiles


class ConfigurationTests(unittest.TestCase):
    def test_configuration_outside_the_current_contract_is_rejected_before_creating_an_instance(self):
        # The configuration section is closed: an undeclared key names no setting, and a declared one needs its type.
        for patch, message in (({'invented_setting': 1}, 'outside the stored configuration section: invented_setting'),
                               ({'session_limits': None}, 'config/session_limits: None is not of type')):
            with self.subTest(patch=patch), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaisesRegex(ValueError, message):
                    initialize(root / 'repository', goal='P', workspace=root / 'workspace',
                               config={'scholarly_enabled': False, **patch})
                self.assertFalse((root / 'workspace').exists())

    def test_model_selection_and_capacity_share_the_current_tier_configuration(self):
        config = deepcopy(DEFAULT_CONFIG)
        config['tier_models'] = {tier: 'fixture-model' for tier in ('low', 'medium', 'high')}
        config['session_limits'] = {'work': {'fixture-model': 2}}
        config['scholarly_enabled'] = False
        validate_config(config)
        profiles = build_profiles(config)
        constraint, = profiles['capacity_constraints'].values()
        self.assertEqual((constraint['kind'], constraint['model'], constraint['work_slots']),
                         ('concurrency', 'fixture-model', 2))
        ai_profiles = [profile for profile in profiles['execution_profiles'].values() if profile['actor_kind'] == 'ai']
        self.assertTrue(all(profile['ai']['model'] == 'fixture-model' for profile in ai_profiles))
        self.assertTrue(all(profile['ai']['capacity_refs'] == ([constraint['id']] if profile['role'] in WORK_ROLES else [])
                            for profile in ai_profiles))
        retired = deepcopy(config)
        retired['session_limits'] = {'work': {'fixture-model': 2}, 'operations': {'fixture-model': 1}}
        with self.assertRaises(ValueError):
            validate_config(retired)


if __name__ == '__main__':
    unittest.main()
