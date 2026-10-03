"""학술 과제의 실제 TASKS 평가 생산자로 독립 판정 입력을 만든다."""
from copy import deepcopy

from do_math.task_scope import apply_task_assessments
from support.academic_scenes import consumer_sim, ended
from support.role_answers import assessment


def assessed_case(*, criterion=None, unresolved=False):
    sim = consumer_sim()
    engine = sim.engine
    task, = [row for row in engine.runtime['tasks'].values() if row.get('academic_requirement_id')]
    if criterion is not None:
        task['completion_obligations'][0]['claim'] = criterion
    work = ended(engine, 'EX-academic-returned', 'research_work', target=task['id'])
    planner = ended(engine, 'EX-academic-assessor', 'research_plan', input_solution_basis=engine._solution_basis())
    task['results'] = [{'execution_id': work['id'], 'report': '합성 원고 보고서'}]
    value = assessment(task)
    if unresolved:
        value['decision'] = 'incomplete'
        value['item_dispositions'].pop(0)
        value['unresolved'] = [{'obligation_id': task['completion_obligations'][0]['id'],
            'missing_inputs': ['source:paper'], 'next_owner': 'research_plan'}]
    engine.instance, engine.runtime = apply_task_assessments(engine.instance, engine.runtime, [value],
        execution_id=planner['id'], input_tasks=deepcopy(engine.runtime['tasks']), clock=sim.clock)
    engine._save()
    return sim, task['id'], value, planner['id']
