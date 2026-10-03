"""실제 지식 수입·형식 검증·목표 감사로 공유 의존을 가진 해결 근거를 만든다."""
import unittest

from do_math.canonical import exact_content_hash
from support.academic_scenes import theorem_sim, theorem_id, ended, MANUSCRIPT
from support.engine_lifecycle import applied, clear_work
from support.state_builders import charter_change


class AcademicSolutionDependencyValidationTests(unittest.TestCase):
    def test_shared_dependency_is_sealed_once_across_goal_roots(self):
        sim = theorem_sim()
        engine = sim.engine
        first = theorem_id(sim)
        source = 'theorem academic_second : 1 = 1 := rfl'
        sim.lean.allow(source, ['academic_second'], signatures={'academic_second': 'academic_second : 1 = 1'},
            declaration_evidence={'academic_second': {'type': '1 = 1', 'value': None}}, axioms={'academic_second': []}, dependencies={'academic_second': {}})
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': {
            'kind': 'theorem', 'title': 'academic_second', 'statement': '합성 두 번째 항등식',
            'summary': '합성 공유 의존', 'explanation': '반사성', 'lean_code': source,
            'declaration_names': ['academic_second'], 'dependencies': [first]}})
        second = next(k for k, row in engine.instance['knowledge'].items() if row['title'] == 'academic_second')
        sim.run_until(lambda current: bool(current.instance['knowledge'][second].get('review_cycle_id')) and
            current.runtime['review_cycles'][current.instance['knowledge'][second]['review_cycle_id']]['status'] != 'working',
            max_steps=12)
        cycle = engine.runtime['review_cycles'][engine.instance['knowledge'][second]['review_cycle_id']]
        self.assertEqual(cycle['decision'], 'match')
        clear_work(sim)
        applied(sim, 'decision', config={'change': charter_change(engine, academic_requirements=[MANUSCRIPT])})
        basis, required = engine._goal_basis_key(), engine.instance['config']['goal_auditors']
        for slot in range(required):
            eid = 'EX-academic-shared-' + str(slot)
            ended(engine, eid, 'goal_audit')
            engine._bind_governance_input({'role': 'goal_audit'}, engine.runtime['executions'][eid],
                                         engine._governance_context({'role': 'goal_audit'}, {}))
            engine._apply({'role': 'goal_audit', 'slot': slot, 'basis': basis, 'required': required},
                {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [first, second],
                 'summary': '합성 공유 의존 목표 감사', 'questions': []}, eid)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        solution = engine._solution_basis()
        ids = [row['id'] for row in solution['records']]
        self.assertEqual(ids.count(first), 1)
        self.assertEqual(ids.count(second), 1)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({row['id']: row['sha256'] for row in solution['records'] if row['id'] in {first, second}},
                         {kid: exact_content_hash(engine.instance['knowledge'][kid]) for kid in (first, second)})
        engine._save()
        self.assertEqual(engine.store.load()[1]['knowledge'][second]['dependencies'], [first])
