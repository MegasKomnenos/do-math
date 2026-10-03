"""공개 활성화부터 실제 작업자 제출·HTTP 영수·독립 평가까지 생산한 장면."""
from support.academic_scenes import academic_responder, drive_to, unfinished
from support.engine_lifecycle import applied
from support.engine_purpose import PURPOSE_CONFIG
from support.purpose_answers import requirement
from support.state_builders import charter_change
from support.sim import Sim, built

ORIGIN = 'https://academic.example.test'


def _build(root, shared):
    sim = Sim(root, shared=shared, config=PURPOSE_CONFIG)
    sim.activate(external_policy='explicit_grants')
    sim.model.responder = academic_responder(effect_request={
        'grant_id': 'HTTP', 'request': {'method': 'POST', 'url': ORIGIN + '/submit', 'body': 'proof'}})
    sim.ports.http.table['/submit'] = (200, b'accepted', None)
    applied(sim, 'decision', config={'change': {'kind': 'grant', 'grant': {
        'id': 'HTTP', 'kind': 'http', 'allowed_origins': [ORIGIN], 'allowed_methods': ['POST'],
        'allowed_path_prefixes': ['/submit'], 'reuse': 'reusable'}}})
    applied(sim, 'decision', config={'change': charter_change(sim.engine, academic_requirements=[requirement(
        ['send manuscript'], external_effects=[{'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'HTTP'}])])})
    drive_to(sim, lambda current: current.runtime['status'] == 'completed', limit=35)
    unfinished(sim.engine)
    return sim


def confirmed_effect_sim():
    return built('academic-confirmed-effect-validation', _build)
