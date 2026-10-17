"""An issued operational-review input on a real engine and its central submit seam.

The target is supplied by the caller (a running call or an ended attempt).
Registration, context, schema, tools, capture and receipt publication are the
product's. The reviewer has no native process; tests stop at role reception.
"""
from copy import deepcopy
from pathlib import Path

from do_math import contracts, planning, submission
from do_math.canonical import canonical_json
from do_math.input_basis import capture_decision_basis
from support.submission_receiver import Scene, issue_input


def operational_scene(sim, target, disposition):
    engine = sim.engine
    action = {'id': 'AC-direct-operational', 'role': 'operational_review', 'target': target,
              **({'live': True} if engine.runtime['executions'][target]['status'] == 'running' else {})}
    engine._action_lifecycle_gate(action)
    eid, bundle = 'EX-direct-operational', 'BA-direct-operational-input'
    execution = engine._register_execution(action, {'id': eid, 'role': 'operational_review', 'status': 'running'})
    execution.update(input_snapshot=engine.head, input_bundle=bundle, grant_id=action['grant_id'],
        decision_basis=capture_decision_basis(engine.instance, engine.runtime, engine._decision_references(action)),
        **planning.governance_revisions(engine.instance))
    workspace = Path(engine.instance['workspace']) / 'runs' / eid / 'workspace'
    workspace.mkdir(parents=True)
    context = engine._context(action, workspace, execution_id=eid)
    context.update(action=deepcopy(action), execution_id=eid, snapshot=execution['input_snapshot'])
    schema = contracts.action_schema(action)
    submission.install_tools(workspace, context, schema, None, clock=sim.clock)
    issue_input(engine, execution, context, schema, bundle)
    output = {'summary': 'Keep the original accepted operational response', 'questions': [], 'used_sources': [],
              'disposition': deepcopy(disposition)}
    from support.role_answers import seal_response
    seal_response(output, context, workspace)
    draft = workspace / 'draft.json'
    draft.write_bytes(canonical_json(output))
    request = {'request_id': 'CT-direct-operational', 'execution_id': eid, 'grant_id': action['grant_id'],
               'kind': 'submit_intent', 'payload': {'draft_path': draft.name}}
    receipt = engine._publish_control_request(request)
    if receipt['state'] != 'accepted':
        raise AssertionError(receipt)
    from do_math.execution_lifecycle import transition_execution
    transition_execution(engine.runtime['executions'][eid], 'stopping', at=sim.clock.now())
    return Scene(sim, action=action, execution_id=eid, workspace=workspace, context=context, schema=schema,
                 output=output, request=request, receipt=receipt)
