"""A checked active delegation built by real governance, interpretation and storage producers."""
from do_math import delegations, governance
from support.governance_sim import returned
from support.sim import Sim, built


def _delegated(root, shared):
    sim = Sim.activated(root, shared=shared)
    source = governance.preserve_source('GS-close-delegation', '인스턴스의 한정된 검토를 위임한다.', origin='user')
    sim.instance['governance_sources'][source['id']] = source
    changes = [
        {'kind': 'grant', 'decision_id': 'DC-close-original', 'grant': {
            'id': 'GR-close', 'kind': 'local', 'roles': ['maintenance'], 'reuse': 'reusable'}},
        {'kind': 'delegation', 'decision_id': 'DC-close-delegation', 'delegation': {
            'id': 'DG-close', 'status': 'active', 'decision_kind': 'grant',
            'original_decision_id': 'DC-close-original', 'included_targets': [sim.instance['id']],
            'excluded_targets': [], 'external_effects': [], 'resource_limits': {'steps': 2},
            'expires_at': '2099-01-01T00:00:00Z'}},
    ]
    for change in changes:
        sim.engine.instance, sim.engine.runtime, _ = governance.apply_decision(
            sim.instance, sim.runtime, change, source_ref=source['id'], clock=sim.clock)
    case = {'id': 'CASE-close', 'decision_kind': 'grant', 'target_id': sim.instance['id'],
            'external_effects': [], 'resources': {'steps': 1}, 'effect': {'operation': 'bounded_review'},
            'basis_refs': [governance.governance_view(sim.instance)['charter']['id']]}
    application = delegations.prepare_application(sim.instance, sim.runtime, 'DG-close', case, now_iso=sim.clock.now())
    for stage, eid in (('interpret', 'EX-close-interpret'), ('check', 'EX-close-check')):
        execution = returned(sim.engine, {'id': 'AC-' + eid, 'role': 'intent_interpretation',
            'target': sim.instance['lifecycle']['input_id'], 'delegation_application_id': application['id']}, eid)
        execution['delegation_input_sha256'] = application['input_sha256']
        delegations.record_judgment(sim.runtime, application['id'], {
            'input_sha256': application['input_sha256'], 'decision': 'within_scope',
            'reason': '보존한 사용자 결정의 범위와 일치한다.'}, execution_id=eid, stage=stage)
    sim.engine._save()
    return sim

def delegated_sim():
    return built('governance-close-delegated', _delegated)
