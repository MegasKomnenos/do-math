"""Final goal assurance and the mapping of additional audits (``academic.apply_goal_assurance``, ``governance``), moved from ``test_goal_audit``.

Every rejection is pinned to the product's phrase, where the legacy tests
checked only the exception type. The legacy input of the unavailable formal
reference test is rejected by the recorded judgment group check before the
formal evidence is read; that input keeps its reason, and an added input whose
judgment group is complete reaches the rule the test's name states. The legacy
omitted-audit test replaced ``knowledge_records.formal_usable``; the additional
audit check runs before any formal evidence is read, so the same input is
rejected for the same reason without it.
"""
import unittest

import jsonschema

from do_math import governance as gov
from do_math.academic import apply_goal_assurance
from do_math.canonical import exact_content_hash
from record_fixtures import audited_governance, domain_governance


class GoalAssuranceTests(unittest.TestCase):
    def test_nonformal_task_does_not_establish_final_goal_assurance(self):
        with self.assertRaisesRegex(ValueError, '^nonformal final goal assurance is not supported$'):
            apply_goal_assurance(domain_governance(), decision="unsupported_assurance", basis="B",
                                 judgments=[{"decision": "satisfied"}])

    def test_final_goal_record_cannot_rely_on_unresolved_formal_references(self):
        instance = domain_governance()
        with self.assertRaisesRegex(ValueError, '^final status must consume the complete recorded judgment group$'):
            apply_goal_assurance(instance, decision="mathematically_solved", basis="B",
                                 judgments=[{"decision": "satisfied", "current": True, "formal_result_refs": ["MISSING"]}])
        judgment = {'id': 'J', 'execution_id': 'AUDIT', 'slot': 0, 'basis': 'B', 'required': 1, 'decision': 'satisfied',
                    'scope_complete': True, 'current': True, 'formal_result_refs': ['MISSING']}
        instance['goal_judgments'] = [judgment]
        with self.assertRaisesRegex(ValueError, '^final goal cites unavailable formal evidence$'):
            apply_goal_assurance(instance, decision="mathematically_solved", basis="B", judgments=[judgment])

    def test_goal_audit_maps_actual_results_and_rejects_missing_or_stale_input(self):
        i, rt = audited_governance()
        basis = gov.additional_audit_input(i, rt)
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': basis}
        row = {'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial', 'reason': 'Only partial',
               'input_hashes': {'CH1': exact_content_hash(i['governance']['CH1'])}}
        jsonschema.Draft202012Validator(gov.additional_audit_schema(i)).validate([row])
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        self.assertEqual(mapped[0]['decision'], 'not_satisfied')
        with self.assertRaisesRegex(ValueError, '^additional audit does not establish goal satisfaction$'):
            gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        with self.assertRaisesRegex(ValueError, '^all additional audits require actual verdicts$'):
            gov.evaluate_goal_audits(i, rt, 'AUDIT', [])
        row['verdict'] = 'pass'
        mapped = gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])
        self.assertEqual(mapped[0]['decision'], 'satisfied')
        gov.validate_goal_additional_audits(i, [{'execution_id': 'AUDIT', 'additional_audits': mapped}])
        i['governance']['CH1']['content']['goal'] += ' changed'
        with self.assertRaisesRegex(ValueError, '^goal auditor did not receive these current additional-audit inputs$'):
            gov.evaluate_goal_audits(i, rt, 'AUDIT', [row])

    def test_audit_assessor_must_resolve_to_actual_execution_not_producer_claim(self):
        i, rt = audited_governance()
        rt['executions']['AUDIT'] = {'role': 'goal_audit', 'additional_audit_input': gov.additional_audit_input(i, rt)}
        with self.assertRaisesRegex(ValueError, '^audit assessor or verdict differs from approval$'):
            gov.evaluate_goal_audits(i, rt, 'AUDIT', [{
                'audit_ref': 'AU', 'verdict': 'pass', 'assessor': 'someone-else', 'reason': 'Claimed authority',
                'input_hashes': {'CH1': exact_content_hash(i['governance']['CH1'])}}])

    def test_goal_assurance_cannot_omit_active_additional_audit(self):
        i, rt = audited_governance()
        judgment = {'id': 'J', 'execution_id': 'AUDIT', 'slot': 0, 'basis': 'B', 'required': 1,
                    'decision': 'satisfied', 'scope_complete': True, 'current': True, 'formal_result_refs': ['FR']}
        i['goal_judgments'] = [judgment]
        i['formal_results'] = {'FR': {'id': 'FR'}}
        with self.assertRaisesRegex(ValueError, '^goal judgment omits a current additional audit$'):
            apply_goal_assurance(i, decision='mathematically_solved', basis='B', judgments=[judgment])


if __name__ == '__main__':
    unittest.main()
