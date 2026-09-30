"""Governance scenes of the governance region on a Sim: interpretations, checked imports and later approvals.

The legacy ``engine_fixtures.governance_host`` loaded ``record_fixtures.checked_import``
into an engine built without ``__init__`` and replaced its initial-intent and
activation methods; here the same states are reached by events. A user's
input (or the initial input during public activation) is interpreted by the
model double through the worker, checked independently by the default
responder, and waits for the user as the product decides. Nothing replaces an
engine method or the store.

- ``interpreted(change=None, question=None)``: the model double's answer for
  ``intent_interpretation``. Its interpret stage keeps the default responder's
  one unit covering the exact original; ``change(context)`` returns a payload
  the unit proposes (so the checked import waits for the user's exact
  approval), ``question`` makes the unit ask one blocking question ``Q-domain``
  about the instance. The check stage keeps the default approving answer.
- ``charter_change(goal='Prove Q', identifier='CH2')``: a ``change`` proposing a
  charter that supersedes the current one with ``goal``.
- ``configuration_change(config)``: a ``change`` proposing a configuration patch.
- ``approval(bundle, **changes)``: the user's exact later approval of a checked
  bundle, as the ``import_approval`` decision change.
- ``checked_sim(kind='charter')``: a restored active instance where the input
  ``INPUT`` was interpreted as proposing ``kind`` (``'charter'``: goal
  ``Prove Q``; ``'configuration'``: ``CONFIGURATION``), checked, and waits for the
  user's approval (``import_application_authority``). ``checked_bundle(sim)`` is
  that import. Built once per process for each kind.
- ``initial_sim(root, change=None, question=None)``: a public activation whose
  initial interpretation is ``interpreted(change, question)``; the activation
  stops where the instance waits for the user. ``initial_checked_sim()`` is the
  restored template of ``initial_sim(change=charter_change())``.
- ``adopt_audit(sim, mapping=AUDIT_MAPPING)``: the user's public decision
  adopting additional audit ``AU`` over the current charter.
- ``returned(engine, action, execution_id)``: an execution the engine registers
  for ``action`` (``_register_execution``) and that has ended without a result.
- ``goal_auditor(engine, verdict='partial')``: ``(action, output)`` of one returned
  goal auditor at the engine's goal basis, bound to the audit input it read,
  answering a satisfied goal with ``AU``'s ``verdict``.
- ``theorem_sim()``: a restored active instance whose theorem ``k1`` the Lean
  double verified and identity review matched (``engine_lifecycle.theorems``).
"""
from __future__ import annotations

from copy import deepcopy

from do_math.canonical import exact_content_hash
from support.model import Answer
from support.sim import Sim, built

INPUT = 'Change the goal to Q'
CONFIGURATION = {'call_timeout_seconds': 901}


def charter_change(goal='Prove Q', identifier='CH2'):
    def change(context):
        current = context['governance']['charter']
        return {'kind': 'charter', 'record': {'id': identifier, 'kind': 'charter', 'revision': current['revision'] + 1,
                'supersedes': [current['id']], 'content': {**deepcopy(current['content']), 'goal': goal}}}
    return change


def configuration_change(config):
    def change(context):
        return {'kind': 'configuration', 'config': deepcopy(config)}
    return change


def interpreted(change=None, question=None):
    def make(output, context):
        if context['action'].get('stage', 'interpret') != 'interpret':
            return output
        unit = output['import_units'][0]
        if change is not None:
            payload = change(context)
            unit.update(owner_kind=payload['kind'], payload=payload,
                        owner_ref=payload['record']['id'] if 'record' in payload else context['instance_id'])
        if question is not None:
            output['questions'] = [question]
            output['question_details'] = [{'id': 'Q-domain', 'question_index': 0, 'blocks': True,
                'target_ids': [context['instance_id']], 'reason': 'Domain is needed',
                'source_unit_ids': [unit['unit_id']], 'options': []}]
            unit['question_refs'] = ['Q-domain']
        return output
    return Answer(make)


def approval(bundle, **changes):
    """The ``import_approval`` change naming ``bundle``'s exact seal, check and unit payloads."""
    return {'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
            'check_sha256': bundle['check']['sha256'],
            'unit_hashes': {unit['unit_id']: exact_content_hash(unit['payload'])
                            for unit in bundle['output']['import_units'] if unit['payload']}, **changes}


def waits(sim, kind):
    return {key: row for key, row in sim.runtime.get('waiting_actions', {}).items() if row.get('kind') == kind}


def _checked(kind):
    def build(root, shared):
        sim = Sim.activated(root, shared=shared)
        change = charter_change() if kind == 'charter' else configuration_change(CONFIGURATION)
        sim.model.on('intent_interpretation').reply(interpreted(change))
        text = INPUT if kind == 'charter' else 'Set call timeout to 901 seconds'
        sim.control('input', text=text, request_id='input-Q')
        sim.run_until(lambda s: waits(s, 'import_application_authority'), max_steps=12)
        return sim
    return build


def checked_sim(kind='charter'):
    return built('governance-checked-' + kind, _checked(kind))


def checked_bundle(sim):
    """The import ``checked_sim`` left waiting for the user's approval."""
    (wait,) = waits(sim, 'import_application_authority').values()
    return sim.runtime['intent_imports'][wait['import_id']]


def initial_sim(root, change=None, question=None, *, shared=None):
    """A public activation whose initial interpretation waits for the user; the instance stays initializing."""
    sim = Sim(root, shared=shared)
    sim.model.on('intent_interpretation').reply(interpreted(change, question))
    try:
        sim.activate()
    except AssertionError as error:
        if 'public activation did not reach active' not in str(error):
            raise
    else:
        raise AssertionError('the activation did not wait for the user')
    return sim


def initial_checked_sim():
    return built('governance-initial-checked', lambda root, shared: initial_sim(root, charter_change(), shared=shared))


AUDIT_MAPPING = {'pass': 'satisfied', 'partial': 'not_satisfied', 'unknown': 'unresolved'}


def adopt_audit(sim, mapping=AUDIT_MAPPING, identifier='AU'):
    """The user's public decision adopting additional audit ``identifier`` over the current charter."""
    from do_math.governance import governance_view
    from support.engine_lifecycle import applied
    charter = governance_view(sim.instance)['charter']['id']
    record = {'id': identifier, 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
        'scope': ['P'], 'required_inputs': [charter], 'assessor': 'goal_audit', 'verdict_mapping': dict(mapping)}}
    applied(sim, 'decision', text='Require this exact audit and mapping',
            config={'change': {'kind': 'additional_audit', 'record': record}})
    return record


def returned(engine, action, execution_id):
    """``execution_id`` registered by the engine for ``action`` and ended, as a returned model call leaves it."""
    from do_math.execution_lifecycle import transition_execution
    execution = engine._register_execution(action, {'id': execution_id, 'role': action['role'], 'status': 'running'})
    at = engine._lifecycle_now().isoformat()
    transition_execution(execution, 'stopping', at=at)
    transition_execution(execution, 'ended', at=at, outcome='execution_incomplete')
    return engine.runtime['executions'][execution_id]


def goal_auditor(engine, execution_id='AUDITOR', verdict='partial'):
    """``(action, output)``: one returned goal auditor bound to the audit input it read, and its answer.

    The answer is a satisfied goal verdict whose additional audit ``AU`` has
    ``verdict``, with the input hashes the auditor received.
    """
    action = {'id': 'AC-' + execution_id, 'role': 'goal_audit', 'basis': engine._goal_basis_key(), 'slot': 0,
              'required': 1}
    execution = returned(engine, action, execution_id)
    engine._bind_governance_input(action, execution, engine._governance_context({'role': 'goal_audit'}, {}))
    output = {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [],
              'summary': 'Ordinary goal verdict cannot override audit', 'questions': [], 'findings': [],
              'reason': 'Use only the supplied eligible formal records',
              'additional_audits': [{'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': verdict,
                                     'reason': 'Only part of the approved scope has evidence',
                                     'input_hashes': execution['additional_audit_input'][0]['input_hashes']}]}
    return action, output


def _theorem(root, shared):
    from support.engine_lifecycle import theorems
    sim = Sim.activated(root, shared=shared)
    theorems(sim, 'k1')
    return sim


def theorem_sim():
    """A restored active instance with one theorem ``k1`` the Lean double verified and identity review matched."""
    return built('governance-theorem', _theorem)
