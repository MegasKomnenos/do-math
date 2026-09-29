"""Default bootstrap and immutable profile admission, without fixture defaults."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.local_host import LocalHost
from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles
from do_math.initialization import initialize_state, activation_requirements
from do_math.observations import observation_settings_errors, tracker_config
from do_math.canonical import exact_content_hash
from engine_fixtures import FakeEngine


class ObservationAdmissionTests(unittest.TestCase):
    def test_default_bootstrap_reports_exact_missing_settings_before_activation(self):
        with tempfile.TemporaryDirectory() as root:
            instance, runtime = initialize_state(instance_id='RI-default', goal='A goal', workspace=root, config=deepcopy(DEFAULT_CONFIG), source_input='Original request')
            instance.update(build_profiles(instance['config']))
            result = activation_requirements(instance, runtime, host=LocalHost())
            self.assertFalse(result['satisfied'])
            # The current role profiles are the adopted editions; no separate profile list is required.
            self.assertNotIn('profiles', result['missing'])
            self.assertIn('observation_configuration', result['missing'])
            errors = result['observation_errors']
            self.assertEqual({e['field'] for e in errors}, {'tool_review_window_seconds', 'self_check_response_window_seconds'})
            self.assertTrue(all(e['profile_id'] in instance['execution_profiles'] for e in errors))
            self.assertNotIn('intent_interpretation', {e['role'] for e in errors})
            self.assertIn('research_work', {e['role'] for e in errors})
            self.assertEqual(instance['lifecycle']['immutable_input']['text'], 'Original request')

    def test_adopting_a_configuration_whose_role_profiles_lack_settings_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            config = deepcopy(DEFAULT_CONFIG)
            engine.instance['config'] = config
            engine.instance.update(build_profiles(config))
            with self.assertRaisesRegex(ValueError, 'observation_configuration.*research_work'):
                engine._initialization_control({'config_sha256': exact_content_hash(config)}, 'UI-settings')
            self.assertNotIn('config_sha256', engine.instance['lifecycle']['adoption'])

    def test_adoption_of_a_configuration_other_than_the_current_one_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            with self.assertRaisesRegex(ValueError, 'config_sha256'):
                engine._initialization_control({'config_sha256': '0' * 64}, 'UI-stale')
            self.assertNotIn('config_sha256', engine.instance['lifecycle']['adoption'])

    def test_adoption_takes_no_profile_list(self):
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            reference = engine.instance['role_profile_refs']['research_work'][0]
            with self.assertRaisesRegex(ValueError, 'profile_refs'):
                engine._initialization_control({'profile_refs': [reference]}, 'UI-profiles')

    def test_configured_settings_do_not_require_task_rules_until_execution(self):
        configured = build_profiles({**DEFAULT_CONFIG, 'tool_review_window_seconds': 60,
                                     'self_check_response_window_seconds': 5})
        for profile in configured['execution_profiles'].values():
            self.assertEqual(observation_settings_errors(profile), [])
            if profile['role'] == 'research_work':
                with self.assertRaisesRegex(ValueError, 'rules'):
                    tracker_config(profile)
            else:
                tracker_config(profile)

    def test_nonpositive_boolean_and_fractional_millisecond_values_are_rejected(self):
        profile = next(p for p in build_profiles(DEFAULT_CONFIG)['execution_profiles'].values()
                       if p['role'] == 'research_work')
        for value in (None, 0, -1, True, '0.0001', 'NaN'):
            with self.subTest(value=value):
                profile['observation']['settings'].update(tool_review_window_seconds=value,
                    self_check_response_window_seconds=5)
                self.assertEqual([e['field'] for e in observation_settings_errors(profile)], ['tool_review_window_seconds'])

    def test_active_wait_rebinds_review_but_reprepares_a_tasks_fixed_profile(self):
        from types import MethodType
        from do_math.engine import ResearchEngine
        from research_fixtures import FixtureAdapter
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as root, patch('do_math.local_host.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(root)
            engine.activate()
            engine._execution_profile = MethodType(ResearchEngine._execution_profile, engine)
            old = build_profiles(DEFAULT_CONFIG)
            engine.instance['execution_profiles'].update(old['execution_profiles'])
            task = engine.task('TK-old', approved=False)
            task['profile_refs'] = old['role_profile_refs']['research_work']
            prior = deepcopy(task['profile_refs'])
            engine.runtime['waiting_actions'] = {
                'AC-review': {'action': {'id': 'AC-review', 'role': 'task_contract_review', 'target': task['id'],
                    'profile_ref': old['role_profile_refs']['task_contract_review'][1]},
                    'kind': 'observation_configuration', 'reason': 'missing window'},
                'AC-work': {'action': {'id': 'AC-work', 'role': 'research_work', 'target': task['id']},
                    'kind': 'observation_configuration', 'reason': 'missing window'}}
            engine._retry_observation_configuration()
            self.assertNotIn('AC-review', engine.runtime['waiting_actions'])
            self.assertIn('AC-work', engine.runtime['waiting_actions'])
            self.assertEqual(task['profile_refs'], prior)
            self.assertTrue(any(a['role'] == 'research_preparation' and a.get('target') == task['id'] for a in engine.runtime['queue']))


class PublicObservationAdmissionTests(unittest.TestCase):
    def test_public_default_init_rejects_unready_adoption_then_adopts_the_configured_one(self):
        from do_math.engine import ResearchEngine, control
        from research_fixtures import new_instance
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / 'repo'
            instance_id = new_instance(repository, goal='Preserve this original', workspace=root / 'work',
                config={'scholarly_enabled': False, 'operator_enabled': False, 'lean_command': ['test-lean']})
            engine = ResearchEngine(repository, instance_id)
            old = deepcopy(engine.instance['role_profile_refs']['research_work'][0])
            # The operator reads the hash of the configuration it inspected from status.
            unready = engine.status()['config_sha256']
            request = control(repository, engine.instance['id'], 'decision', config={'change': {
                'kind': 'initialization', 'config_sha256': unready}})
            engine.process_controls()
            rejected = next(h for h in engine.runtime['history'] if h.get('kind') == 'rejected_user_control'
                            and h['request']['id'] == request['request_id'])
            self.assertIn('tool_review_window_seconds', rejected['reason'])
            self.assertIn('self_check_response_window_seconds', rejected['reason'])
            self.assertEqual(engine.instance['lifecycle']['state'], 'initializing')
            control(repository, engine.instance['id'], 'configure', config={
                'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5})
            engine.process_controls()
            fresh = deepcopy(engine.instance['role_profile_refs']['research_work'][0])
            self.assertNotEqual(fresh, old)
            configured = engine.status()['config_sha256']
            self.assertNotEqual(configured, unready)
            second = control(repository, engine.instance['id'], 'decision', config={'change': {
                'kind': 'initialization', 'config_sha256': configured}})
            self.assertNotEqual(second['request_id'], request['request_id'])
            engine.process_controls()
            self.assertEqual(engine.control_result(second['request_id'])['effect'], 'applied')
            self.assertEqual(engine.instance['lifecycle']['adoption']['config_sha256'],
                             exact_content_hash(engine.instance['config']))
            self.assertIn(old['id'], engine.instance['execution_profiles'])
            self.assertEqual(engine.instance['lifecycle']['immutable_input']['text'], 'Preserve this original')
            self.assertEqual(engine.runtime['executions'], {})


if __name__ == '__main__':
    unittest.main()
