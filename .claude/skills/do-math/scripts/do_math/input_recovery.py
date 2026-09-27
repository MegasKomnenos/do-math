"""Fixed planning choices for existing input-overflow obligations."""
from copy import deepcopy

from .execution_profiles import profile_ref, match_profile_ref
from .model_policy import selection
from .planning import contract_hash


def overflow_requests(instance, runtime):
    rows = []
    for identifier, waiting in sorted(runtime.get('waiting_actions', {}).items()):
        action = waiting.get('action', {})
        if (waiting.get('kind') != 'input_overflow' or waiting.get('next_owner') != 'research_plan'
                or action.get('role') != 'research_work' or action.get('review_cycle_id')):
            continue
        task = runtime.get('tasks', {}).get(action.get('target'))
        if not task or task.get('status') in {'completed', 'closed'}:
            continue
        candidates = waiting.get('detail', {}).get('allowed_profile_candidates', [])
        allowed = []
        for reference in task.get('profile_refs', []):
            try:
                profile = match_profile_ref(instance['execution_profiles'], reference)
                ref = profile_ref(profile)
                if profile['id'] not in candidates:
                    continue
                selection(instance['config'], {**action, 'profile_ref': ref}, runtime['tasks'],
                          instance.get('knowledge', {}), instance=instance)
                allowed.append(ref)
            except ValueError:
                continue
        rows.append({'action_id': identifier, 'owner_activity_id': action.get('owner_activity_id'),
            'task_id': task['id'], 'contract_revision': task['revision'],
            'contract_sha256': action.get('selected_contract_sha256', contract_hash(task)),
            'question_id': waiting['question_id'], 'detail': deepcopy(waiting['detail']),
            'model_assessment': deepcopy(action.get('model_assessment', task.get('model_assessment'))),
            'allowed_profile_refs': allowed})
    return rows


def validate_resolutions(rows, requests):
    available = {row['action_id']: row for row in requests}
    seen = set()
    for row in rows:
        identifier = row['action_id']
        if identifier in seen:
            raise ValueError('input overflow resolutions must name distinct actions')
        seen.add(identifier)
        if identifier not in available:
            raise ValueError('input overflow action was not available for planning: ' + identifier)
        if row['profile_ref'] not in available[identifier]['allowed_profile_refs']:
            raise ValueError('input overflow profile was not offered for this action: ' + identifier)
