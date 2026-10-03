"""실제 검토 교체 생산자의 단일 좌표 변조를 허가 경계에서 거부한다."""
from copy import deepcopy
import tempfile
import unittest

from do_math import governance as gov
from support.governance_cases import replacement_engine


class GovernanceReplacementInputTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.engine, self.action = replacement_engine(self.directory.name)

    def test_wrong_role_has_exact_denial(self):
        self.action['role'] = 'maintenance'
        before = deepcopy((self.engine.instance, self.engine.runtime))
        result = gov.authorize_review_replacement(self.engine.instance, self.engine.runtime, self.action,
                                                  at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'grant_id': self.action['grant_id'],
                                 'reason': 'replacement must identify its role and purpose'})
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_missing_failed_slot_has_exact_denial(self):
        del self.action['replacement_for']
        before = deepcopy((self.engine.instance, self.engine.runtime))
        result = gov.authorize_review_replacement(self.engine.instance, self.engine.runtime, self.action,
                                                  at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'grant_id': self.action['grant_id'],
                                 'reason': 'replacement needs the exact failed slot and cause'})
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_supplied_case_requires_delegation_identity(self):
        before = deepcopy((self.engine.instance, self.engine.runtime))
        result = gov.authorize_review_replacement(self.engine.instance, self.engine.runtime, self.action,
                                                  case={}, at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'grant_id': self.action['grant_id'],
                                 'reason': 'case reuse must identify its delegation'})
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_delegated_case_must_match_actual_replacement_effect(self):
        fields = ('review_cycle_id', 'stage', 'slot', 'round', 'replacement_for', 'continuity_break_cause')
        case = {'target_id': self.action['target'], 'effect': {key: self.action[key] for key in fields},
                'basis_refs': [self.action['review_cycle_id']]}
        case['effect']['slot'] = 'other'
        before = deepcopy((self.engine.instance, self.engine.runtime))
        result = gov.authorize_review_replacement(self.engine.instance, self.engine.runtime, self.action,
            delegation_id='DG-close', case=case, at=self.engine.ports.clock.now())
        self.assertEqual(result, {'allowed': False, 'grant_id': self.action['grant_id'],
            'reason': 'delegated replacement differs from the checked target, slot or cycle basis'})
        self.assertEqual((self.engine.instance, self.engine.runtime), before)
