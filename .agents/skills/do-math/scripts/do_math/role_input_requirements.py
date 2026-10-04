"""Judgment inputs declared by the installed role contracts (3-B).

These are semantic inputs, independent of whether context_store keeps them
inline or puts them behind an exact source. The table does not grant access to
another review seat, and absent evidence is never supplied with defaults.
"""


ROLE_INPUT_REQUIREMENTS = {
    'research_preparation': {
        'contract': '계약/후보-준비.md',
        'keys': ('action', 'governance', 'tasks', 'task_catalog', 'ongoing_work',
                 'preparation_history', 'recent_history', 'knowledge_catalog',
                 'academic_phase', 'academic_requirements', 'resources',
                 'profile_selection', 'pending_revisions', 'blocked_actions'),
    },
    'research_plan': {
        'contract': '계약/연구-계획.md',
        'keys': ('action', 'governance', 'tasks', 'task_catalog', 'task_readiness',
                 'ready_task_ids', 'returned_task_ids', 'ongoing_work',
                 'knowledge_catalog', 'recent_history', 'academic_phase',
                 'academic_requirements', 'academic_validation', 'resources',
                 'profile_selection', 'input_overflow_requests', 'review_followups'),
    },
    'research_work': {
        'contract': '계약/연구-수행.md',
        'keys': ('action', 'governance', 'task', 'knowledge_catalog', 'relations',
                 'sources', 'formal_verifier', 'grants'),
    },
    'task_contract_review': {
        'contract': '계약/작업-계약-검토.md',
        'keys': ('action', 'governance', 'task', 'available_input_refs',
                 'knowledge_catalog', 'sources', 'model_policy', 'record_index', 'record_map'),
    },
    'identity_review': {
        'contract': '계약/동일성-검토.md',
        'keys': ('action', 'governance', 'role_review'),
    },
    'goal_audit': {
        'contract': '계약/목표-감사.md',
        'keys': ('action', 'governance', 'eligible_knowledge', 'knowledge_catalog',
                 'additional_audit_input'),
    },
    'supplemental_research': {
        'contract': '계약/보충-조사.md',
        'keys': ('action', 'governance'),
    },
    'operational_review': {
        'contract': '계약/운영-점검.md',
        'keys': ('action', 'governance', 'execution_to_review', 'observation',
                 'operational_evidence', 'admissible_basis_refs'),
    },
    'intent_interpretation': {
        'contract': '계약/의도-해석.md',
        'keys': ('action', 'governance', 'user_request'),
    },
    'maintenance': {
        'contract': '계약/유지보수.md',
        'keys': ('action', 'governance', 'record_index', 'record_map'),
    },
}


# A review seat always receives its own full proposal and public history;
# stage-specific inputs add obligations rather than narrow that population.
REVIEW_STAGE_INPUTS = {
    'scope': ('review_policy', 'retained_reviewer_slots', 'scope_executions_used',
              'minimum_scope_execution_limit'),
    'initial': ('required_source_refs', 'slot_perspective'),
    'organize': ('pending_findings', 'issues'),
    'answer': ('issues', 'answer_requests'),
    'judge': ('issues', 'completed_results'),
}


def judgment_input_keys(role, action):
    """Required readable keys for this role's current action variant.

    Conditional paths name the evidence's owner, rather than requiring a
    checkpoint or source that the contract permits to be explicitly absent.
    Recovery fields are added by the recovery producer; its exact contents
    remain that producer's contract, not a made-up replacement here.
    """
    keys = list(ROLE_INPUT_REQUIREMENTS[role]['keys'])
    if role == 'supplemental_research':
        keys.extend(('review_research', 'proposal') if action.get('review_cycle_id') else ('task',))
    elif role == 'intent_interpretation':
        if action.get('delegation_application_id'):
            keys.append('delegation_case')
        else:
            keys.extend(('original_source', 'import_consumers', 'governance_records',
                         'decisions', 'grants', 'delegations', 'tasks', 'question_links',
                         'sources', 'reference_catalog', 'record_index'))
            if action.get('stage') == 'check':
                keys.append('interpretation_to_check')
    elif role == 'maintenance':
        if action.get('kind_definition_id'):
            keys.append('kind_definition_to_check')
        elif action.get('stage') == 'impact_review':
            keys.append('impact_review_input')
        elif action.get('initial_submission_diagnosis'):
            keys.append('initial_submission_diagnosis')
    return tuple(keys)


def judgment_input_paths(role, action):
    """Required nested coordinates, in addition to whole readable key values."""
    paths = []
    if role == 'identity_review':
        fields = ('proposal', 'proposal_digest', 'policy_ref', 'self_messages',
                  'completed_results', 'source_refs', 'supplemental_results', 'previous_reviews')
        fields += REVIEW_STAGE_INPUTS[action['stage']]
        paths.extend('role_review.' + key for key in dict.fromkeys(fields))
    elif role == 'supplemental_research' and action.get('review_cycle_id'):
        paths.extend('review_research.' + key for key in
                     ('id', 'request_digest', 'proposal_digest', 'question', 'sources'))
    elif role == 'maintenance':
        if action.get('stage') == 'impact_review':
            paths.extend('impact_review_input.' + key for key in ('request', 'output', 'extensions', 'records'))
        elif action.get('initial_submission_diagnosis'):
            paths.extend('initial_submission_diagnosis.' + key for key in
                         ('failed_execution', 'checkpoint', 'preserved_output_files', 'materials'))
    elif role == 'intent_interpretation' and not action.get('delegation_application_id'):
        paths.append('user_request.text')
    if action.get('continuation_of'):
        paths.extend(('previous_execution', 'previous_output_files', 'resume_checkpoint', 'continuation_history'))
    return tuple(paths)
