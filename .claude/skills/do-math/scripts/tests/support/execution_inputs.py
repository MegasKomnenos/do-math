"""Canonical synthetic inputs and real producers; no engine or storage replacement."""
from __future__ import annotations

from pathlib import Path
from do_math.canonical import canonical_json
from support.role_answers import seal_response


IDENTITY = {"host": "CORE_TESTS synthetic host", "implementation": "CORE_TESTS synthetic adapter"}


def dispatched_launch(execution_id, profile, *, jobs, clock):
    """The current explicit runner contract used by native boundary fixtures."""
    from do_math.launch import ticket
    value = ticket(execution_id, profile, clock=clock, jobs=jobs)
    value['phase'] = 'dispatched'
    return value


def sealed_maintenance_submission(workspace, execution_id):
    """Create real central seal bytes for lifecycle/storage fixture assertions."""
    from support.entry import entry
    _entry = entry()
    from do_math import contracts, submission
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    context = {'action': {'id': 'AC-fixture', 'role': 'maintenance'},
               'execution_id': execution_id, 'snapshot': 'fixture-input',
               'tasks': [], 'knowledge_catalog': [], 'sources': [], 'kind_definitions': {}}
    schema = contracts.schema_for('maintenance')
    submission.install_tools(workspace, context, schema, None, clock=_entry.ports.clock)
    output = {'summary': 'Inspect fixture', 'used_sources': [], 'questions': [],
              'report': 'Explicit synthetic maintenance output.', 'remaining_work': []}
    seal_response(output, context, workspace)
    (workspace / 'draft.json').write_bytes(canonical_json(output))
    sealed = submission.seal_submission(workspace, 'draft.json', execution_id=execution_id,
        context=context, schema=schema, max_artifact_bytes=1024*1024, clock=_entry.ports.clock)
    if not sealed['passed']:
        raise AssertionError(sealed['check']['issues'])
    prefix = 'runtime/artifacts/BA-fixture-submission/'
    return ({**sealed['intent'], 'output_ref': prefix + 'output.json'},
            {prefix + path: raw for path, raw in sealed['artifacts'].items()})


def delegated_judgment_scene():
    """Real public replacement request and its two queued blind judgments."""
    from copy import deepcopy
    from do_math import governance
    from do_math.delegations import judgment_input
    from support.review_sim import opened_sim
    sim = opened_sim()
    sim.step()  # the real scope worker opens the initial review seats
    engine = sim.engine
    action = deepcopy(next(a for a in sim.runtime['queue']
                           if a['role'] == 'identity_review' and a['stage'] == 'initial'))
    engine._record_review_recovery(action, ValueError('permanent_loss'), retryable=False)
    source = governance.preserve_source('GS-delegated-input', 'Authorize the exact review replacement.', origin='user')
    engine.instance['governance_sources'][source['id']] = source
    effect = {**{key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round')},
              'replacement_for': 0, 'continuity_break_cause': 'permanent_loss'}
    from support.governance_delegation import original_replacement
    original_replacement(engine, action, source_ref=source['id'],
        decision_id='DC-original-replacement', grant_id=None)
    engine.instance, engine.runtime, _ = governance.apply_decision(engine.instance, engine.runtime,
        {'kind': 'delegation', 'decision_id': 'DC-delegate-replacement', 'delegation': {
            'id': 'DG-replacement-input', 'status': 'active', 'decision_kind': 'review_replacement',
            'original_decision_id': 'DC-original-replacement', 'included_targets': [action['target']],
            'excluded_targets': [], 'external_effects': [], 'resource_limits': {}, 'expires_at': None}},
        source_ref=source['id'], clock=sim.clock)
    request = {'id': 'REQUEST-delegated-input', 'action': 'request', 'config': {
        'role': 'maintenance', 'review_replacement': {'action': action, 'delegation_id': 'DG-replacement-input',
            'case': {'id': 'CASE-delegated-input', 'decision_kind': 'review_replacement',
                     'target_id': action['target'], 'external_effects': [], 'resources': {},
                     'effect': effect, 'basis_refs': [action['review_cycle_id']]}}}}
    engine.runtime['history'].append({'kind': 'user_control', 'request': request})
    if not engine._review_recovery_control(request):
        raise AssertionError("delegated replacement request was not accepted")
    judges = [a for a in sim.runtime['queue'] if a.get('requested_by') == request['id']]
    if [a['stage'] for a in judges] != ['delegation_interpret', 'delegation_check']:
        raise AssertionError(judges)
    engine._save()
    shared = judgment_input(sim.runtime, judges[0]['delegation_application_id'])
    return sim, judges, shared
