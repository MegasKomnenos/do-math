"""A maintenance fence drains execution without becoming a user pause."""
from copy import deepcopy


def apply_control(runtime, request):
    action = request['action']
    if action not in {'quiesce', 'release_quiesce'}:
        return False
    if request.get('origin') not in {'user','operator'}:
        raise ValueError('maintenance control requires a known origin')
    fence = runtime.get('maintenance_fence')
    if action == 'quiesce':
        if fence:
            raise ValueError('an existing maintenance fence must be released explicitly')
        runtime['maintenance_fence'] = {'request_id':request['id'], 'origin':request['origin'],
            'reason':request['text'], 'state':'draining', 'created_at':request['created_at']}
    else:
        if not fence or request.get('config', {}).get('fence_id') != fence['request_id']:
            raise ValueError('release must name the current maintenance fence')
        if request['origin'] == 'operator' and fence['origin'] != 'operator':
            raise ValueError('operator cannot release a user maintenance fence')
        if fence['state'] != 'quiescent':
            raise ValueError('maintenance has not reached its termination barrier')
        runtime.setdefault('history', []).append({'kind':'maintenance_released', 'fence':deepcopy(fence),
                                                 'request_id':request['id']})
        runtime.pop('maintenance_fence')
    return True


def settle(runtime):
    fence = runtime.get('maintenance_fence')
    if not fence:
        return False
    from .execution_lifecycle import transition_execution
    from datetime import datetime, timezone
    settled_at = datetime.now(timezone.utc).isoformat()
    publication = {w.get('execution_id') for w in runtime.get('waiting_actions', {}).values()
                   if w.get('kind') in {'submission_publication','environment_observation'}}
    for identifier in publication:
        execution = runtime.get('executions', {}).get(identifier)
        if (execution and execution['status'] == 'stopping'
                and execution.get('capacity', {}).get('local_termination') == 'confirmed'):
            transition_execution(execution, 'ended', at=settled_at, outcome='execution_incomplete',
                reason='publication preserved for maintenance', disposition={'kind':'deferred_publication'})
    pending = [e['id'] for e in runtime.get('executions', {}).values() if e['status'] != 'ended']
    held = [r['id'] for r in runtime.get('reservations', {}).values() if r.get('state') == 'held']
    fence.update(state='blocked' if pending or held else 'quiescent',
                 pending_executions=pending, held_reservations=held, settled_at=settled_at)
    return True
