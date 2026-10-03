"""실제 소유 작업과 독립 전문 판정이 만든 완료 평가의 누락·인용 경계를 확인한다."""
from copy import deepcopy
import unittest

from do_math import planning, task_scope
from support.planning_contract_inputs import specialist_sim, warm_specialist, only_task

setUpModule = warm_specialist


class SpecialistJudgmentTests(unittest.TestCase):
    def test_missing_specialist_support_invalidates_an_otherwise_current_assessment(self):
        sim = specialist_sim()
        task = only_task(sim)
        self.assertTrue(task_scope.assessment_current(task, sim.instance, sim.runtime))
        self.assertEqual(set(task['assessment']['specialist_support']), {'OB-argument'})
        task['assessment']['specialist_support'] = {}
        before = deepcopy((sim.instance, sim.runtime))
        self.assertFalse(task_scope.assessment_current(task, sim.instance, sim.runtime))
        self.assertEqual((sim.instance, sim.runtime), before)

    def test_uncited_usable_identity_receipt_cannot_fulfil_the_obligation(self):
        sim = specialist_sim()
        task = only_task(sim)
        obligation = task['completion_obligations'][0]
        disposition = deepcopy(task['assessment']['item_dispositions'][0])
        support = task['assessment']['specialist_support'][obligation['id']]
        self.assertEqual(task_scope.designated_judgment(task, obligation, disposition, sim.instance, sim.runtime), support)
        disposition['evidence_refs'] = []
        before = deepcopy((sim.instance, sim.runtime, disposition))
        self.assertIsNone(task_scope.designated_judgment(task, obligation, disposition, sim.instance, sim.runtime))
        self.assertEqual((sim.instance, sim.runtime, disposition), before)

    def test_unavailable_extra_relation_judgment_is_not_a_structural_parse_error(self):
        sim = specialist_sim()
        relation = sim.instance['relations'][-1]
        condition = {'op': 'relation_exists', 'subkind': relation['kind'],
                     'from_id': relation['source'], 'to_id': relation['target']}
        baseline = planning.evaluate_condition(condition, sim.instance, sim.runtime)
        self.assertEqual(baseline['state'], 'ready')
        endpoint = sim.instance['knowledge'][relation['source']]
        other = next(a['id'] for a in sim.instance['identity_assessments'].values()
                     if a['formal_result_id'] == endpoint['formal_result_id'] and a['decision'] == 'match')
        relation['assessment_refs'] = [*relation['assessment_refs'], other]
        before = deepcopy((sim.instance, sim.runtime))
        result = planning.evaluate_condition(condition, sim.instance, sim.runtime)
        self.assertEqual((result['state'], result['errors']), ('not_ready', []))
        self.assertEqual(result['basis'][-1], {'absencequery': condition})
        self.assertEqual([r['id'] for r in result['basis'][:-1]], [relation['id'], *sorted({
            relation['source'], relation['target'], *relation['formal_result_refs'], *relation['assessment_refs']})])
        self.assertEqual((sim.instance, sim.runtime), before)
