"""현재 해결·실제 반려 생산자·종료된 계획 실행을 연결한 저장 가능한 장면."""
from copy import deepcopy

from support.academic_scenes import consumer_sim, ended, user_source


def rejection_case():
    sim = consumer_sim()
    engine = sim.engine
    basis = engine._solution_basis()
    engine._academic_control({'id': user_source(engine), 'action': 'decision', 'created_at': sim.clock.now(),
        'config': {'change': {'kind': 'academic_rejection', 'actor': '합성 심사자', 'text': '논증 설명을 보완하라'}}})
    execution = ended(engine, 'EX-academic-resolution', 'research_plan', input_solution_basis=deepcopy(basis))
    rejection = engine.runtime['external_rejections'][-1]
    reference = next(iter(engine.instance['knowledge']))
    resolution = {'id': rejection['id'], 'decision': 'resolved', 'evidence': '합성 증거가 반려 사유에 답한다',
                  'evidence_refs': [reference]}
    engine._save()
    return sim, execution['id'], resolution
