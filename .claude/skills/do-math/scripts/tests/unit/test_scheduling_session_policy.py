"""Model tiers, capacity limits and session slot admission on profile editions (``model_policy``, ``session_slots``; layer 2)."""
from copy import deepcopy
import unittest

from do_math.configuration import DEFAULT_CONFIG, validate_config
from do_math.execution_profiles import apply_editions, build_profiles
from do_math.model_policy import LIMITS, MODELS, assessment_tier, selection, validate_policy
from do_math.session_slots import SessionSlots


class SessionPolicyTests(unittest.TestCase):
    def test_old_profile_cannot_bypass_a_new_zero_capacity_limit(self):
        config = deepcopy(DEFAULT_CONFIG)
        instance = {'config': config, **build_profiles(config)}
        runtime = {'executions': {}, 'reservations': {}, 'provider_waits': {}}
        old = next(profile for profile in instance['execution_profiles'].values()
                   if profile['role'] == 'research_work' and profile['ai'].get('tier') == 'high')
        slots = SessionSlots(runtime, instance)

        lower = deepcopy(config['session_limits'])
        lower['work'][MODELS['high']] = 0
        config['session_limits'] = lower
        apply_editions(instance, build_profiles(config))
        execution = {'id': 'EX-old-profile', 'role': 'research_work', 'status': 'queued'}
        self.assertFalse(slots.acquire(execution['id'], profile=old, execution=execution))
        self.assertEqual(slots.admission_wait['kind'], 'capacity')
        self.assertEqual(slots.admission_wait['next_owner'], 'user')
        self.assertEqual(runtime['reservations'], {})

        raised = deepcopy(lower)
        raised['work'][MODELS['high']] = 1
        config['session_limits'] = raised
        apply_editions(instance, build_profiles(config))
        self.assertTrue(slots.acquire(execution['id'], profile=old, execution=execution))
        current = next(instance['execution_profiles'][ref['id']] for ref in instance['role_profile_refs']['research_work']
                       if instance['execution_profiles'][ref['id']]['ai'].get('tier') == 'high')
        self.assertEqual(next(iter(runtime['reservations'].values()))['constraint_id'], current['ai']['capacity_refs'][0])

    def test_defaults_and_max_of_difficulty_and_importance(self):
        self.assertEqual(MODELS, {'high': 'gpt-6-astra', 'medium': 'gpt-5.6-sol', 'low': 'gpt-5.6-terra'})
        self.assertEqual(LIMITS, {'work': {'gpt-6-astra': 3, 'gpt-5.6-sol': 3, 'gpt-5.6-terra': 3}})
        self.assertEqual((DEFAULT_CONFIG['tier_models'], DEFAULT_CONFIG['session_limits']), (MODELS, LIMITS))
        self.assertEqual(assessment_tier({'difficulty': 'low', 'importance': 'high', 'reason': 'goal-wide impact'}), 'high')
        config = deepcopy(DEFAULT_CONFIG)
        config['session_limits']['work'][MODELS['high']] = 0
        selected = selection(config, {'role': 'research_work', 'model_assessment': {
            'difficulty': 'high', 'importance': 'medium', 'reason': 'new proof approach'}}, {}, {})
        self.assertEqual(selected['model'], MODELS['high'])

    def test_model_names_extend_without_closed_catalogue(self):
        config = deepcopy(DEFAULT_CONFIG)
        config['tier_models']['high'] = 'configured-future-model'
        config['session_limits']['work']['configured-future-model'] = 2
        self.assertIsNone(validate_policy(config))

    def test_bad_capacity_and_missing_tier_model_are_rejected(self):
        # The configuration schema owns the capacity range; the policy owns cross-field rules.
        for value in (-1, True, None, 1.5):
            with self.subTest(value=value):
                config = deepcopy(DEFAULT_CONFIG)
                config['session_limits']['work'][MODELS['high']] = value
                with self.assertRaisesRegex(ValueError, 'config/session_limits/work'):
                    validate_config(config)
        config = deepcopy(DEFAULT_CONFIG)
        config['session_limits']['work'][' '] = 1
        with self.assertRaisesRegex(ValueError, 'session_limits.work must map model names to nonnegative integers'):
            validate_policy(config)
        for tier in ('low', 'medium', 'high'):
            with self.subTest(tier=tier):
                config = deepcopy(DEFAULT_CONFIG)
                del config['tier_models'][tier]
                with self.assertRaisesRegex(ValueError, 'tier_models must name a model for low, medium and high'):
                    validate_policy(config)

    def test_role_floor_raises_low_assessment_and_unassessed_work_uses_high(self):
        config = deepcopy(DEFAULT_CONFIG)
        low = {'difficulty': 'low', 'importance': 'low', 'reason': 'bounded local comparison'}
        review = selection(config, {'role': 'task_contract_review', 'model_assessment': low}, {}, {})
        self.assertEqual((review['tier'], review['model']), ('medium', MODELS['medium']))
        unassessed = selection(config, {'role': 'research_work'}, {}, {})
        self.assertEqual((unassessed['tier'], unassessed['model']), ('high', MODELS['high']))


if __name__ == '__main__':
    unittest.main()
