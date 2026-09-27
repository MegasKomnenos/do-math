"""Public configuration has one current execution model."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import DEFAULT_CONFIG, initialize, validate_config
from do_math.execution_profiles import WORK_ROLES, build_profiles


class CurrentContractTests(unittest.TestCase):
    def test_retired_configuration_is_rejected_before_creating_an_instance(self):
        for patch in ({'session_limits': None}, {'work_calls': 10}, {'operations_calls': None},
                      {'model': 'old-model'}, {'role_models': {}}, {'operator_model': 'old-model'},
                      {'run_timeout_seconds': 1}, {'dispatch_reserve_seconds': 1},
                      {'lean_timeout_seconds': 1}, {'max_cycles': 1}):
            with self.subTest(patch=patch), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaises(ValueError):
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
