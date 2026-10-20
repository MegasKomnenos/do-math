"""모델 평가 생산자의 답과 정책 기본값에서 한 필드씩 계약을 벗어난다."""
from copy import deepcopy
import unittest

from do_math import model_policy as policy
from do_math.configuration import DEFAULT_CONFIG
from do_math.planning import contract_hash
from support.default_responder import rating
from support.role_answers import candidate


class ModelPolicyValidationTests(unittest.TestCase):
    def test_model_lock_rejects_aliases_at_configuration_before_worker_start(self):
        for model in ('opus', 'sonnet', 'claude-opus-5-5'):
            config = deepcopy(DEFAULT_CONFIG)
            config['claude_only_assigned_model'] = True
            config['tier_models']['high'] = 'claude:' + model
            config['session_limits']['work']['claude:' + model] = 1
            if model.startswith('claude-'):
                policy.validate_policy(config)
            else:
                with self.subTest(model=model), self.assertRaisesRegex(ValueError, 'requires a full Claude model ID'):
                    policy.validate_policy(config)

    def test_assessment_tier_requires_substantive_reason(self):
        assessment = rating()
        assessment['reason'] = ' \t\n'
        before = deepcopy(assessment)
        with self.assertRaisesRegex(ValueError, '^model assessment requires a substantive reason$'):
            policy.assessment_tier(assessment)
        self.assertEqual(assessment, before)

    def test_assessment_tier_uses_higher_dimension(self):
        for difficulty in policy.TIERS:
            for importance in policy.TIERS:
                with self.subTest(difficulty=difficulty, importance=importance):
                    value = {**rating(), 'difficulty': difficulty, 'importance': importance}
                    expected = max((difficulty, importance), key=policy.TIERS.index)
                    self.assertEqual(policy.assessment_tier(value), expected)

    def test_preparation_key_and_empty_target_presence_are_distinct(self):
        ordinary = {'role': 'research_preparation'}
        self.assertFalse(policy.preparation_only(ordinary))
        self.assertEqual(policy.assessment_key(ordinary), 'task_title')
        for key in ('assessment_targets', 'observation_rule_targets'):
            action = {**ordinary, key: {}}
            self.assertTrue(policy.preparation_only(action))
            self.assertEqual(policy.assessment_key(action), 'task_id')
        self.assertEqual(policy.assessment_key({'role': 'research_plan'}), 'task_id')

    def test_assessment_deferral_duplicates_are_rejected(self):
        action = {'role': 'research_preparation', 'assessment_targets': {'TK': {}}}
        entry = {'task_id': 'TK', 'reason': '합성 입력 대기'}
        extensions = {'model_assessment_deferrals': [entry, deepcopy(entry)]}
        before = deepcopy(extensions)
        with self.assertRaisesRegex(ValueError, '^assessment and deferral must identify each target exactly once$'):
            policy.validate_assessments(action, {'candidates': []}, extensions, {})
        self.assertEqual(extensions, before)

    def test_assessment_and_deferral_overlap_is_rejected(self):
        action = {'role': 'research_preparation', 'assessment_targets': {'TK': {}}}
        extensions = {'model_assessments': [rating(task_id='TK')],
                      'model_assessment_deferrals': [{'task_id': 'TK', 'reason': '합성 입력 대기'}]}
        before = deepcopy(extensions)
        with self.assertRaisesRegex(ValueError, '^assessment and deferral must identify each target exactly once$'):
            policy.validate_assessments(action, {'candidates': []}, extensions, {})
        self.assertEqual(extensions, before)

    def test_assessment_deferral_partition_returns_only_actual_ratings(self):
        action = {'role': 'research_preparation', 'assessment_targets': {'TK': {}, 'OTHER': {}}}
        extensions = {'model_assessments': [rating(task_id='TK')],
                      'model_assessment_deferrals': [{'task_id': 'OTHER', 'reason': '합성 입력 대기'}]}
        self.assertEqual(policy.validate_assessments(action, {'candidates': []}, extensions, {}), {'TK': rating()})

    def test_assessment_only_rejects_unassigned_extension_family(self):
        action = {'role': 'research_preparation', 'assessment_targets': {'TK': {}}}
        extensions = {'model_assessments': [rating(task_id='TK')], 'task_dispositions': []}
        before = deepcopy(extensions)
        with self.assertRaisesRegex(ValueError, '^assessment-only preparation may only assess or defer its assigned tasks$'):
            policy.validate_assessments(action, {'candidates': []}, extensions, {})
        self.assertEqual(extensions, before)

    def test_policy_rejects_unknown_role_or_tier(self):
        for roles in ({'unknown': 'low'}, {'research_work': 'unknown'}, []):
            with self.subTest(roles=roles):
                config = deepcopy(DEFAULT_CONFIG)
                config['role_tiers'] = roles
                before = deepcopy(config)
                with self.assertRaisesRegex(ValueError, '^role_tiers contains an unknown role or tier$'):
                    policy.validate_policy(config)
                self.assertEqual(config, before)

    def test_policy_requires_capacity_entry_for_every_tier_model(self):
        config = deepcopy(DEFAULT_CONFIG)
        config['session_limits']['work'].pop(config['tier_models']['high'])
        before = deepcopy(config)
        with self.assertRaisesRegex(ValueError, '^session_limits.work must explicitly include every tier model, including zero capacity$'):
            policy.validate_policy(config)
        self.assertEqual(config, before)

    def test_policy_rejects_blank_capacity_model_name(self):
        config = deepcopy(DEFAULT_CONFIG)
        config['session_limits']['work'][' '] = 1
        with self.assertRaisesRegex(ValueError, '^session_limits.work must map model names to nonnegative integers$'):
            policy.validate_policy(config)
        self.assertEqual(config['session_limits']['work'][' '], 1)

    def test_policy_rejects_missing_or_blank_tier_models(self):
        for models in ({}, {**policy.MODELS, 'high': ' '}, []):
            with self.subTest(models=models):
                config = deepcopy(DEFAULT_CONFIG)
                config['tier_models'] = models
                with self.assertRaisesRegex(ValueError, '^tier_models must name a model for low, medium and high$'):
                    policy.validate_policy(config)
                self.assertEqual(config['tier_models'], models)

    def test_work_admission_rejects_non_work_role_before_selection(self):
        task = {**candidate(), 'id': 'TK', 'revision': 1}
        before = deepcopy(task)
        with self.assertRaisesRegex(ValueError, '^work profile admission requires a work role$'):
            policy.work_profile_selection(DEFAULT_CONFIG, task, {}, action={'role': 'research_plan', 'target': 'TK'})
        self.assertEqual(task, before)

    def test_edition_basis_and_terminal_status_are_independent(self):
        task = {**candidate(), 'id': 'TK', 'revision': 1, 'status': 'planned'}
        basis = policy.assessment_basis(task)
        self.assertEqual(basis, {'revision': 1, 'contract_sha256': contract_hash(task)})
        self.assertTrue(policy.edition_current(task, basis))
        self.assertFalse(policy.edition_current({**task, 'revision': 2}, basis))
        for status in ('closed', 'completed'):
            self.assertFalse(policy.edition_current({**task, 'status': status}, basis))
        self.assertFalse(policy.edition_current(None, basis))

    def test_selection_inherits_knowledge_task_rating_and_copies_it(self):
        task = {**candidate(), 'id': 'TK', 'model_assessment': {**rating(), 'importance': 'high'}}
        result = policy.selection(DEFAULT_CONFIG, {'role': 'research_work', 'target': 'K'},
                                  {'TK': task}, {'K': {'task_id': 'TK'}})
        self.assertEqual(result, {'tier': 'high', 'model': DEFAULT_CONFIG['tier_models']['high'],
                                 'assessment': task['model_assessment'], 'reason': task['model_assessment']['reason']})
        result['assessment']['reason'] = '변조'
        self.assertEqual(task['model_assessment']['reason'], rating()['reason'])
