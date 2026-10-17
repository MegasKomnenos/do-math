"""Delegated review replacement cases of the governance region, moved from ``test_delegations``'s module helpers.

Both build dictionary state with the product's ``governance.apply_decision``
and ``delegations`` functions; nothing is replaced.

- ``replacement_case()``: ``(instance, runtime, action, case)``, a delegated
  review replacement of ``K``'s review cycle ``RC``, not yet applied. The
  instance (``record_fixtures.domain_governance``) holds knowledge ``K``, a
  local machine grant ``G`` for its identity review replacement, the user's
  original ``review_replacement`` decision ``ORIGINAL`` and the adopted
  delegation ``DG`` of it over ``K`` (expiring 2099). ``case`` carries the
  action's six replacement fields as its effect and names ``RC`` as its basis.
- ``checked_replacement_case()``: the same, with the delegation application
  prepared and both independent judgments (``INTERPRET``, ``CHECK``) recorded
  as within scope; ``case`` also names the application.
"""
from __future__ import annotations

from do_math import delegations
from do_math import governance as gov
from support.record_builders import domain_governance


def lose_review_input(sim, action):
    """At a clock-port turn, make this attempt's input path a real file.

    The normal owner creates and abandons the attempt, records the filesystem
    failure and holds its activity. No product function or state is replaced.
    """
    from dataclasses import replace
    from pathlib import Path
    from support.cross_states import drive
    class InputLossClock:
        injected = False

        def __getattr__(self, name):
            return getattr(sim.clock, name)

        def monotonic(self):
            if not self.injected:
                for execution in sim.runtime['executions'].values():
                    if execution.get('action', {}).get('id') != action['id']:
                        continue
                    workspace = Path(sim.instance['workspace']) / 'runs' / execution['id'] / 'workspace'
                    if workspace.is_dir() and not (workspace / 'input').exists():
                        (workspace / 'input').mkdir()
                        (workspace / 'input' / 'review-sources').write_bytes(b'Unavailable exact review input directory.')
                        self.injected = True
                        break
            return sim.clock.monotonic()
    clock = InputLossClock()
    ports = sim.engine.ports
    sim.engine.ports = replace(ports, clock=clock)
    try:
        drive(sim, lambda s: action['id'] in s.runtime.get('waiting_actions', {}))
    finally:
        sim.engine.ports = ports
    assert clock.injected
    cycle = sim.runtime['review_cycles'][action['review_cycle_id']]
    return cycle['recovery_events'][-1]


def _build_public_replacement(root, shared):
    """Public original scope replacement, then a delegated initial-slot case.

    The only injected fault is an unavailable input directory. The engine
    produces recovery facts; decisions, grants and judgments are never seeded.
    """
    from copy import deepcopy
    from support.cross_states import applied, drive, queued, _build_review_stage
    sim = _build_review_stage(root, shared, stage='scope')
    original = deepcopy(queued(sim, 'identity_review', 'scope'))
    lose_review_input(sim, original)
    grant_id, = [g['id'] for g in sim.instance['grants'].values()
                 if g['status'] == 'active' and 'identity_review' in g.get('roles', [])]
    applied(sim, 'request', request_id='UC-public-original', text='Replace this scope seat from its verified records.', config={
        'role': 'maintenance', 'review_replacement': {'action': original, 'grant_id': grant_id}})
    decision, = [row for row in sim.instance['decisions'].values()
                 if row.get('kind') == 'review_replacement']
    assert decision['source_ref'] == 'UC-public-original', decision
    drive(sim, lambda s: queued(s, 'identity_review', 'initial') is not None)
    action = deepcopy(queued(sim, 'identity_review', 'initial'))
    event = lose_review_input(sim, action)
    from do_math.review_cycle import next_actions
    drive(sim, lambda s: not next_actions(s.runtime['review_cycles'][action['review_cycle_id']]))
    applied(sim, 'decision', text='Reuse my scope replacement choice for later review seats on this proposal.',
        config={'change': {'kind': 'delegation', 'decision_id': 'DC-public-delegation', 'delegation': {
            'id': 'DG-public', 'status': 'active', 'decision_kind': 'review_replacement',
            'original_decision_id': decision['id'], 'included_targets': [action['target']],
            'excluded_targets': [], 'external_effects': [], 'resource_limits': {}, 'expires_at': None}}})
    return sim


def public_replacement_case():
    """Restore the quiescent public prefix and return its exact held request."""
    from copy import deepcopy
    from support.sim import built
    from support.cross_states import _review_responder
    sim = built('governance-public-replacement', _build_public_replacement)
    sim.model.responder = _review_responder('initial')
    action, = [deepcopy(w['action']) for w in sim.runtime['waiting_actions'].values()
               if w['kind'] == 'review_input_restoration' and w['action']['stage'] == 'initial']
    cycle = sim.runtime['review_cycles'][action['review_cycle_id']]
    from do_math.review_cycle import slot_key
    index = cycle['blocked_actions'][slot_key(action)]
    event = cycle['recovery_events'][index]
    grant_id = sim.instance['lifecycle']['adoption']['research_grant_ids'][0]
    effect = {**{key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round')},
              'replacement_for': index, 'continuity_break_cause': event['reason']}
    case = {'id': 'CASE-public', 'decision_kind': 'review_replacement', 'target_id': action['target'],
            'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': [action['review_cycle_id']]}
    return sim, {'role': 'maintenance', 'review_replacement': {
        'action': action, 'grant_id': grant_id, 'delegation_id': 'DG-public', 'case': case}}


def original_replacement(engine, action, *, source_ref='SOURCE-review', decision_id='ORIGINAL', grant_id='GR-review'):
    """Domain-only scenes use the same original decision producer as controls."""
    engine.instance, engine.runtime, decision = gov.apply_decision(engine.instance, engine.runtime,
        {'kind': 'review_replacement', 'decision_id': decision_id,
         **({'grant_id': grant_id} if grant_id is not None else {}),
         'allowed_action': {key: action[key] for key in ('id', 'role', 'target', 'review_cycle_id', 'stage', 'slot', 'round')}},
        source_ref=source_ref, clock=engine.ports.clock)
    return decision


def replacement_case():
    from support.entry import entry
    _entry = entry()
    i = domain_governance()
    from do_math.review_cycle import next_actions, record_recovery_event
    from support.review_inputs import scoped_start
    cycle = scoped_start({'revision': 1}, reviewers=1)
    cycle.update(id='RC', knowledge_id='K', revision=1)
    slot = next_actions(cycle)[0]
    cycle = record_recovery_event(cycle, slot, {'reason': 'permanent_loss', 'retryable': False,
                                             'preserved_range': {'slot': slot['slot']}})
    rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready',
          'review_cycles': {'RC': cycle},
          'activities': {}}
    i['knowledge'] = {'K': {'id': 'K', 'revision': 1}}
    action = {'id': 'ACTION', 'role': 'identity_review', 'target': 'K',
              'actor_kind': 'ai', 'purpose': 'record_replacement', 'review_cycle_id': 'RC',
              **slot, 'replacement_for': 0,
              'continuity_break_cause': 'permanent_loss'}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'grant', 'decision_id': 'GRANT-DECISION',
        'grant': {'id': 'G', 'kind': 'local', 'roles': ['identity_review'], 'reuse': 'reusable',
                  'included_targets': ['K'], 'purposes': ['record_replacement']}}, source_ref='S', clock=_entry.ports.clock)
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'review_replacement', 'decision_id': 'ORIGINAL',
        'allowed_action': {key: action[key] for key in ('id', 'role', 'target', 'review_cycle_id', 'stage', 'slot', 'round')},
        'grant_id': 'G'}, source_ref='S', clock=_entry.ports.clock)
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {
        'id': 'DG', 'status': 'active', 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
        'included_targets': ['K'], 'excluded_targets': [], 'external_effects': [], 'resource_limits': {},
        'expires_at': '2099-01-01T00:00:00Z'}}, source_ref='S', clock=_entry.ports.clock)
    effect = {key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round', 'replacement_for',
                                           'continuity_break_cause')}
    case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K',
            'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': ['RC']}
    return i, rt, action, case


def checked_replacement_case():
    from support.entry import entry
    _entry = entry()
    i, rt, action, case = replacement_case()
    app = delegations.prepare_application(i, rt, 'DG', case, now_iso=_entry.ports.clock.now())
    for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
        rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'delegation_input_sha256': app['input_sha256']}
        delegations.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                                                    'reason': 'Synthetic matching case'}, execution_id=eid, stage=stage)
    return i, rt, action, {**case, 'application_id': app['id']}
