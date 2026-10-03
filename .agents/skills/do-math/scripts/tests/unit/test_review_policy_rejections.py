"""정상 정책·범위 생산물의 단일 필드 변조와 불변 입력 계약."""
from copy import deepcopy
import unittest

from do_math.review_policy import build_review_policy, minimum_scope_executions, validate_scope_assessment
from support.review_inputs import scope_assessment


class PolicyRejectionTests(unittest.TestCase):
    def setUp(self):
        self.policy = build_review_policy(reviewer_count=2, max_rounds=2)
        self.scope = scope_assessment(self.policy, ['initial-0', 'initial-1'])

    def assert_policy_rejected(self, value, reason):
        before = deepcopy(value)
        with self.assertRaisesRegex(ValueError, reason):
            build_review_policy(value)
        self.assertEqual(value, before)

    def assert_scope_rejected(self, field, value, reason):
        scope = deepcopy(self.scope)
        scope[field] = value
        before = deepcopy((scope, self.policy))
        with self.assertRaisesRegex(ValueError, reason):
            validate_scope_assessment(scope, self.policy)
        self.assertEqual((scope, self.policy), before)

    def test_policy_requires_an_object(self):
        for value in ([], 'policy', 3, False):
            with self.subTest(value=value):
                self.assert_policy_rejected(value, 'review policy must be an object')

    def test_policy_rejects_extra_or_missing_fields(self):
        for key in self.policy:
            with self.subTest(missing=key):
                changed = deepcopy(self.policy)
                del changed[key]
                self.assert_policy_rejected(changed, 'fields differ from the policy contract')
        self.assert_policy_rejected({**self.policy, 'unexpected': 1}, 'fields differ from the policy contract')

    def test_policy_id_is_nonempty_text(self):
        for value in ('', 3, False, None):
            with self.subTest(value=value):
                self.assert_policy_rejected({**self.policy, 'id': value}, 'review policy ID is required')

    def test_counts_are_positive_integers_not_booleans(self):
        for field in ('minimum_initial_slots', 'round_limit', 'activity_execution_limit'):
            for value in (False, True, 0, -1, '2', 1.5):
                with self.subTest(field=field, value=value):
                    self.assert_policy_rejected({**self.policy, field: value}, 'must be a positive integer')

    def test_exactly_three_distinct_judges(self):
        for judges in (['j0'], ['j0', 'j1'], ['j0', 'j1', 'j2', 'j3']):
            with self.subTest(judges=judges):
                self.assert_policy_rejected({**self.policy, 'judge_slots': judges}, 'exactly three judge slots')

    def test_overflow_is_a_closed_policy_choice(self):
        self.assert_policy_rejected({**self.policy, 'overflow_disposition': 'approve'}, 'unsupported review overflow disposition')

    def test_policy_and_scope_returns_are_detached(self):
        policy = build_review_policy(self.policy)
        scope = validate_scope_assessment(self.scope, policy)
        self.assertEqual(policy, self.policy)
        self.assertEqual(scope, self.scope)
        policy['judge_slots'].append('detached')
        scope['initial_slots'][0]['required_source_refs'].append('detached')
        self.assertEqual(self.policy['judge_slots'], ['judge-0', 'judge-1', 'judge-2'])
        self.assertEqual(self.scope['initial_slots'][0]['required_source_refs'], ['proposal'])

    def test_scope_rejects_another_policy(self):
        self.assert_scope_rejected('policy_id', 'other', 'belongs to another review policy')

    def test_scope_rejects_omitted_policy_perspective(self):
        self.policy['required_perspectives'] = ['formal']
        self.assert_scope_rejected('required_perspectives', [], 'omits a required perspective')

    def test_scope_rejects_too_few_slots(self):
        self.assert_scope_rejected('initial_slots', self.scope['initial_slots'][:1], 'too few initial slots')

    def test_scope_rejects_duplicate_and_reserved_slots(self):
        for identifier, reason in [('initial-0', 'duplicate scope assessment slot'), ('scope', 'reuses an independent role slot'),
                                   ('organize', 'reuses an independent role slot'), ('judge-0', 'reuses an independent role slot')]:
            slots = deepcopy(self.scope['initial_slots'])
            slots[1]['id'] = identifier
            with self.subTest(identifier=identifier):
                self.assert_scope_rejected('initial_slots', slots, reason)

    def test_scope_requires_a_slot_for_every_perspective(self):
        self.assert_scope_rejected('required_perspectives', ['missing'], 'no slot for a required perspective')

    def test_scope_cannot_expand_limit_or_change_overflow(self):
        self.assert_scope_rejected('activity_execution_limit', self.policy['activity_execution_limit'] + 1, 'exceeds the policy execution limit')
        self.assert_scope_rejected('overflow_disposition', 'defer', 'changes the policy overflow disposition')

    def test_minimum_budget_includes_used_attempts_and_both_round_shapes(self):
        self.assertEqual(minimum_scope_executions(2, 1, 4), 10)
        self.assertEqual(minimum_scope_executions(2, 2, 4), 15)
        scope = {**self.scope, 'activity_execution_limit': 11}
        self.assertEqual(validate_scope_assessment(scope, self.policy), scope)
        with self.assertRaisesRegex(ValueError, 'requires at least 12 attempts including 1 already used'):
            validate_scope_assessment(scope, self.policy, executions_used=1)
        self.assertEqual(scope['activity_execution_limit'], 11)
