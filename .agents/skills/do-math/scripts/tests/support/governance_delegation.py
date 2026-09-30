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
from record_fixtures import domain_governance


def replacement_case():
    i = domain_governance()
    rt = {'tasks': {}, 'executions': {}, 'queue': [], 'status': 'ready',
          'review_cycles': {'RC': {'id': 'RC', 'knowledge_id': 'K', 'revision': 1}},
          'activities': {}}
    i['knowledge'] = {'K': {'id': 'K', 'revision': 1}}
    action = {'id': 'ACTION', 'role': 'identity_review', 'target': 'K',
              'actor_kind': 'ai', 'purpose': 'record_replacement', 'review_cycle_id': 'RC',
              'stage': 'initial', 'slot': 'R1', 'round': 0, 'replacement_for': 0,
              'continuity_break_cause': 'permanent_loss'}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'grant', 'decision_id': 'GRANT-DECISION',
        'grant': {'id': 'G', 'kind': 'local', 'roles': ['identity_review'], 'reuse': 'reusable',
                  'included_targets': ['K'], 'purposes': ['record_replacement']}}, source_ref='S')
    i['decisions']['ORIGINAL'] = {'id': 'ORIGINAL', 'actor': 'user', 'kind': 'review_replacement', 'source_ref': 'S'}
    i, rt, _ = gov.apply_decision(i, rt, {'kind': 'delegation', 'decision_id': 'DD', 'delegation': {
        'id': 'DG', 'status': 'active', 'decision_kind': 'review_replacement', 'original_decision_id': 'ORIGINAL',
        'included_targets': ['K'], 'excluded_targets': [], 'external_effects': [], 'resource_limits': {},
        'expires_at': '2099-01-01T00:00:00Z'}}, source_ref='S')
    effect = {key: action[key] for key in ('review_cycle_id', 'stage', 'slot', 'round', 'replacement_for',
                                           'continuity_break_cause')}
    case = {'id': 'CASE', 'decision_kind': 'review_replacement', 'target_id': 'K',
            'external_effects': [], 'resources': {}, 'effect': effect, 'basis_refs': ['RC']}
    return i, rt, action, case


def checked_replacement_case():
    i, rt, action, case = replacement_case()
    app = delegations.prepare_application(i, rt, 'DG', case)
    for eid, stage in [('INTERPRET', 'interpret'), ('CHECK', 'check')]:
        rt['executions'][eid] = {'id': eid, 'role': 'intent_interpretation', 'delegation_input_sha256': app['input_sha256']}
        delegations.record_judgment(rt, app['id'], {'input_sha256': app['input_sha256'], 'decision': 'within_scope',
                                                    'reason': 'Synthetic matching case'}, execution_id=eid, stage=stage)
    return i, rt, action, {**case, 'application_id': app['id']}
