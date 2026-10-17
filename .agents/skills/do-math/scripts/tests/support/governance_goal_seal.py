"""A committed goal audit seal of the governance region on a Sim: the start of the recovery test in ``test_goal_audit``.

The legacy test sealed a goal audit on an engine built without its
constructor: a hand-written judgment and producer, a store autospec whose
``read`` returned the sealed bytes, and patched ``_save``, ``_session_slots``,
``windows_job.named_job_empty`` and ``owner_ended``. Here the same seal is made
on a restored Sim's real engine and published under the storage contract:

- ``committed_goal_audit(sim)`` registers the goal auditor ``EX-original`` for
  ``AC-original`` (slot 0 of 2 at the engine's goal basis), binds the audit
  input it read, applies its satisfied verdict through the engine's own receiver
  (``_apply``, so the judgment in ``goal_judgments`` is the product's), records
  the output's integration receipt, and seals its submission: output,
  extensions and the receiver's check are published as artifacts and named by
  the submission intent and the accepted receipt. The execution is left
  ``stopping`` with its capacity returned, the original result and input
  bundle named, and a dispatched launch ticket of the current owner process:
  that process disappears (``sim.restart()``) before the goal auditor's final
  bookkeeping. Returns ``(action, judgment)``.
- ``ended_owner_ticket(sim, execution)``: the execution's launch ticket once its
  launching owner is known to have ended (the fake's process ID now names a
  process of another creation time); the Jobs port reports it ended, and no Job
  of its name holds a process.

The legacy first recovery found no launch ticket at all; the storage contract
rejects a started execution without one (``record_schemas.validate_semantics``,
``launch.validate``: "exact launch ticket required"), so no published state
holds that input. The negative recovery scene explicitly persists a different
owner identity whose termination the external Jobs world has not observed.
Restart ends the local owner; it leaves that other owner unknown until the
scene supplies its termination observation.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from do_math import contracts, execution_lifecycle, integration, submission
from do_math.canonical import canonical_json
from do_math.launch import ticket

EXECUTION = 'EX-original'
RESULT_REF = 'runtime/artifacts/BA-original/result.json'
INPUT_BUNDLE = 'BA-original-input'


def committed_goal_audit(sim, *, required=2, slot=0, local_termination='confirmed'):
    engine = sim.engine
    action = {'id': 'AC-original', 'role': 'goal_audit', 'target': None, 'basis': engine._goal_basis_key(),
              'slot': slot, 'required': required}
    execution = engine._register_execution(action, {'id': EXECUTION, 'role': 'goal_audit'})
    context = engine._context(action, Path(engine.instance['workspace']), execution_id=EXECUTION)
    engine._bind_governance_input(action, execution, context)
    output = {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [], 'questions': [],
              'summary': 'original', 'reason': 'The original sealed goal verdict', 'additional_audits': []}
    engine._apply(action, output, EXECUTION)
    (judgment,) = [row for row in engine.instance['goal_judgments'] if row['execution_id'] == EXECUTION]
    output['integration_bundles'] = [{'integration_id': 'IN-original', 'members': ['output'],
                                      'impact_set': [], 'authority_refs': []}]
    fixed = {**context, 'action': action, 'snapshot': engine.head}
    schema = engine._response_schema(action)
    bundle = next(integration.split_bundles(output, {}, fixed))
    engine.runtime.setdefault('integrations', {})['IN-original'] = {
        'id': 'IN-original', 'execution_id': EXECUTION, 'payload_sha256': bundle['payload_sha256'],
        'members': ['output'], 'input_snapshot': engine.head}
    execution = engine.runtime['executions'][EXECUTION]
    at = engine._lifecycle_now().isoformat()
    for status in ('starting', 'stopping'):
        execution_lifecycle.transition_execution(execution, status, at=at)
    profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
    execution.update(result_ref=RESULT_REF, input_bundle=INPUT_BUNDLE, input_snapshot=engine.head,
                     launch_ticket={**ticket(EXECUTION, profile, jobs=sim.ports.jobs, clock=sim.clock), 'phase': 'dispatched'},
                     capacity={'local_termination': local_termination, 'reservation_ids': [], 'provider': None,
                               'process': None})
    artifacts = {RESULT_REF: b'{"status":"completed"}',
                 f'runtime/artifacts/{INPUT_BUNDLE}/input/submission/context.json': canonical_json(fixed),
                 f'runtime/artifacts/{INPUT_BUNDLE}/schema.json': canonical_json(schema)}
    check = submission.check_submission(output, schema, fixed, {}, Path(engine.instance['workspace']),
                                        mode='receiver', execution_id=EXECUTION, tool_sha256='a' * 64, clock=sim.ports.clock)
    if not check['passed']:
        raise AssertionError('the sealed goal audit output fails the receiver check: ' + repr(check['issues']))
    execution['submission_intent'] = {'schema_ref': contracts.schema_reference(schema)}
    refs = []
    for name, value in (('output', output), ('extensions', {}), ('check', check)):
        ref = 'runtime/artifacts/BA-original/' + name + '.json'
        raw = canonical_json(value)
        artifacts[ref] = raw
        digest = hashlib.sha256(raw).hexdigest()
        execution['submission_intent'].update({name + '_ref': ref, name + '_sha256': digest})
        refs.append({'path': ref, 'sha256': digest, 'bytes': len(raw)})
    execution['submission_receipt'] = {'state': 'accepted', 'execution_id': EXECUTION,
                                       'payload': {'submission_check': {'artifacts': refs}}}
    engine._save(artifacts)
    return action, judgment


def ended_owner_ticket(sim, execution):
    # The launch owner has ended: its process ID now names another process (another creation time).
    return {**execution['launch_ticket'], 'owner': {**sim.jobs.owner_identity(), 'creation_filetime': '1'}}
