"""실제 해석과 검토 생산자가 보존한 질문 좌표의 읽기와 중복 방지."""
from copy import deepcopy
import unittest

from support.governance_cases import question_sim, question_bundle, review_question_sim


class GovernanceQuestionSourceTests(unittest.TestCase):
    def test_grant_question_formats_exact_preserved_text(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        row = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        row['question_kind'] = 'grant'
        before = deepcopy(sim.runtime)
        view = {q['id']: q for q in sim.engine._question_view()}
        self.assertEqual(view[row['id']]['text'], 'External action requires a user grant: 자연수 범위인가?')
        self.assertEqual(sim.runtime, before)

    def test_intent_output_cannot_publish_before_independent_import_check(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        before = deepcopy(sim.runtime)
        sim.engine._record_output_questions({'role': 'intent_interpretation'},
                                            bundle['output'], bundle['execution_id'])
        self.assertEqual(sim.runtime, before)
        self.assertEqual(sim.engine._user_questions(), ['자연수 범위인가?'])

    def test_missing_source_pointer_marks_only_view_unavailable(self):
        sim = question_sim()
        bundle = question_bundle(sim)
        row = next(q for q in sim.runtime['question_links'] if q.get('source_id') == bundle['id'])
        row['origin_field'] = 'output/questions/999'
        before = deepcopy(sim.runtime)
        view = {q['id']: q for q in sim.engine._question_view()}
        self.assertEqual((view[row['id']]['text'], view[row['id']]['source_status']), (None, 'unavailable'))
        self.assertEqual(sim.engine._user_questions(), [])
        self.assertEqual(sim.runtime, before)

    def test_public_review_question_uses_result_coordinate_and_is_idempotent(self):
        sim = review_question_sim()
        cycle = next(c for c in sim.runtime['review_cycles'].values()
                     if any(row.get('output', {}).get('questions') for row in c['results'].values()))
        key, result = next((key, row) for key, row in cycle['results'].items() if row.get('output', {}).get('questions'))
        eid = result['execution_id']
        action = sim.runtime['executions'][eid]['action']
        before = deepcopy(sim.runtime['question_links'])
        sim.engine._record_output_questions(action, result['output'], eid, public=False)
        self.assertEqual(sim.runtime['question_links'], before)
        sim.engine._record_output_questions(action, result['output'], eid, public=True)
        first = deepcopy(sim.runtime['question_links'])
        sim.engine._record_output_questions(action, result['output'], eid, public=True)
        self.assertEqual(sim.runtime['question_links'], first)
        row = next(q for q in first if q['origin_execution_id'] == eid and q['origin_field'] == 'results/' + key + '/output/questions/0')
        self.assertEqual((row['source_kind'], row['source_id'], row['owner']), ('review_cycle', cycle['id'], 'research'))
        view = {q['id']: q for q in sim.engine._question_view()}
        self.assertEqual(view[row['id']]['text'], '표현 범위의 후속 연구는?')
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['question_links'], first)
