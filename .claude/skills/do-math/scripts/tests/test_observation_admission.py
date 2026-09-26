"""Default bootstrap and immutable profile admission, without fixture defaults."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from do_math.initialization import initialize_state, activation_requirements
from do_math.observations import observation_settings_errors, tracker_config
from test_lifecycle_engine import FakeEngine
from test_categories import test_group


@test_group('unit')
class ObservationAdmissionTests(unittest.TestCase):
    def test_default_bootstrap_reports_exact_missing_settings_before_activation(self):
        with tempfile.TemporaryDirectory() as root:
            instance, runtime = initialize_state(instance_id='RI-default', goal='A goal', workspace=root, config=deepcopy(DEFAULT_CONFIG), source_input='Original request')
            instance.update(build_profiles(instance['config']))
            instance['lifecycle']['adoption']['profile_refs'] = [profile_ref(p) for p in instance['execution_profiles'].values()]
            result = activation_requirements(instance, runtime)
            self.assertFalse(result['satisfied'])
            self.assertIn('observation_configuration', result['missing'])
            errors = result['observation_errors']
            self.assertEqual({e['field'] for e in errors}, {'tool_review_window_seconds', 'self_check_response_window_seconds'})
            self.assertTrue(all(e['profile_id'] in instance['execution_profiles'] for e in errors))
            self.assertNotIn('intent_interpretation', {e['role'] for e in errors})
            self.assertEqual(instance['lifecycle']['immutable_input']['text'], 'Original request')
            # Initial-only adoption must not hide the role profiles dispatch uses later.
            instance['lifecycle']['adoption']['profile_refs'] = instance['role_profile_refs']['intent_interpretation']
            result = activation_requirements(instance, runtime)
            self.assertIn('observation_configuration', result['missing'])
            self.assertIn('research_work', {e['role'] for e in result['observation_errors']})

    def test_adoption_rejects_incomplete_profile_and_preserves_its_edition(self):
        with tempfile.TemporaryDirectory() as root:
            engine = FakeEngine(root)
            old = build_profiles(DEFAULT_CONFIG)['execution_profiles']
            profile = next(p for p in old.values() if p['role'] == 'research_work')
            engine.instance['execution_profiles'].update(old)
            with self.assertRaisesRegex(ValueError, 'observation_configuration.*research_work'):
                engine._initialization_control({'profile_refs': [profile_ref(profile)]}, 'UI-settings')
            self.assertEqual(engine.instance['execution_profiles'][profile['id']], profile)

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
        with tempfile.TemporaryDirectory() as root, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
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


@test_group('integration')
class PublicObservationAdmissionTests(unittest.TestCase):
    def test_public_default_init_rejects_unready_adoption_then_accepts_configured_edition(self):
        from do_math.engine import ResearchEngine, control
        from research_fixtures import new_instance
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / 'repo'
            instance_id = new_instance(repository, goal='Preserve this original', workspace=root / 'work',
                config={'scholarly_enabled': False, 'operator_enabled': False, 'lean_command': ['test-lean']})
            engine = ResearchEngine(repository, instance_id)
            old = deepcopy(engine.instance['role_profile_refs']['research_work'][0])
            request = control(repository, engine.instance['id'], 'decision', config={'change': {
                'kind': 'initialization', 'adopt_current_config': True, 'profile_refs': [old]}})
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
            request = control(repository, engine.instance['id'], 'decision', config={'change': {
                'kind': 'initialization', 'adopt_current_config': True, 'profile_refs': [fresh]}})
            engine.process_controls()
            self.assertEqual(engine.instance['lifecycle']['adoption']['profile_refs'], [fresh])
            self.assertIn(old['id'], engine.instance['execution_profiles'])
            self.assertEqual(engine.instance['lifecycle']['immutable_input']['text'], 'Preserve this original')
            self.assertEqual(engine.runtime['executions'], {})


if __name__ == '__main__':
    unittest.main()
