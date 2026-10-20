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
                 'profile_selection', 'pending_revisions', 'blocked_actions',
                 'configuration_source', 'relations', 'sources', 'formal_verifier',
                 'task_readiness', 'events'),
    },
    'research_plan': {
        'contract': '계약/연구-계획.md',
        'keys': ('action', 'governance', 'tasks', 'task_catalog', 'task_readiness',
                 'ready_task_ids', 'returned_task_ids', 'ongoing_work',
                 'knowledge_catalog', 'recent_history', 'academic_phase',
                 'academic_requirements', 'academic_validation', 'resources',
                 'profile_selection', 'input_overflow_requests', 'review_followups',
                 'configuration_source', 'relations', 'sources', 'blocked_actions',
                 'pending_revisions', 'queued_work', 'external_rejections', 'events'),
    },
    'research_work': {
        'contract': '계약/연구-수행.md',
        'keys': ('action', 'governance', 'task', 'knowledge_catalog', 'relations',
                 'sources', 'formal_verifier', 'grants'),
    },
    'task_contract_review': {
        'contract': '계약/작업-계약-검토.md',
        'keys': ('action', 'governance', 'task', 'available_input_refs',
                 'knowledge_catalog', 'sources', 'model_policy', 'record_index', 'record_map',
                 'formal_verifier', 'grants'),
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
    keys.extend(('snapshot', 'execution_profile', 'record_map', 'record_index'))
    if role == 'supplemental_research':
        keys.extend(('review_research', 'proposal') if action.get('review_cycle_id') else
                    ('task', 'knowledge_catalog', 'relations', 'sources', 'formal_verifier', 'grants'))
    elif role == 'intent_interpretation':
        if action.get('delegation_application_id'):
            keys.append('delegation_case')
        else:
            keys.extend(('original_source', 'import_consumers', 'governance_records',
                         'decisions', 'grants', 'delegations', 'tasks', 'question_links',
                         'sources', 'reference_catalog', 'record_index', 'configuration_source'))
            if action.get('stage') == 'check':
                keys.append('interpretation_to_check')
    elif role == 'maintenance':
        if action.get('kind_definition_id'):
            keys.append('kind_definition_to_check')
        elif action.get('stage') == 'impact_review':
            keys.append('impact_review_input')
        elif action.get('initial_submission_diagnosis'):
            keys.append('initial_submission_diagnosis')
    return tuple(dict.fromkeys(keys))


def judgment_input_paths(role, action, *, context):
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
    elif role == 'operational_review':
        paths.extend('operational_evidence.' + key for key in
                     ('checkpoint_status', 'checkpoint_source', 'checkpoint_files',
                      'checkpoint_evidence_omitted', 'execution_status', 'source_snapshot'))
        if context['operational_evidence']['checkpoint_status'] == 'preserved':
            paths.extend('operational_evidence.checkpoint_source.' + key for key in ('local_path', 'sha256', 'bytes'))
        if recovery_materials_required(action, context):
            paths.extend('recovery_materials.' + key for key in
                         ('execution_id', 'source_snapshot', 'checkpoint', 'checkpoint_source',
                          'result_source', 'result_kind', 'final_result_status', 'output_files'))
    elif role == 'goal_audit':
        paths.extend('additional_audit_input[].' + key for key in ('audit', 'inputs', 'input_hashes'))
        paths.extend('eligible_knowledge[].' + key for key in ('formal_result', 'identity_assessments'))
        paths.extend('eligible_knowledge[].formal_result.verification.' + key for key in
                     ('declarations', 'declaration_signatures', 'axioms', 'source_sha256'))
    if action.get('continuation_of'):
        paths.extend(('previous_execution', 'previous_output_files', 'resume_checkpoint', 'continuation_history'))
    return tuple(paths)


def judgment_source_lists(role, action, *, context):
    """Contract-owned lists whose local source files must actually be readable."""
    if role == 'identity_review':
        return ('role_review.source_refs',)
    if role == 'supplemental_research' and action.get('review_cycle_id'):
        return ('review_research.sources',)
    if role == 'maintenance' and action.get('initial_submission_diagnosis'):
        return ('initial_submission_diagnosis.materials',)
    if role == 'operational_review':
        return ('operational_evidence.checkpoint_files',) + (
            ('recovery_materials.output_files',) if recovery_materials_required(action, context) else ())
    if role in ('research_preparation', 'research_plan', 'research_work', 'task_contract_review'):
        return ('sources',)
    if role == 'supplemental_research':
        return ('sources',)
    return ()


def recovery_materials_required(action, context):
    """Ended diagnostic inputs of executions with a preserved artifact bundle."""
    return not action.get('live', False) and bool(context['execution_to_review'].get('artifact_bundle'))


def judgment_source_refs(role, action, *, context):
    """Single exact files, with explicit missing/failed evidence left distinguishable."""
    if role in ('research_preparation', 'research_plan'):
        return ('configuration_source', 'profile_selection.profiles_ref', 'task_catalog[].source_ref')
    if role == 'intent_interpretation' and not action.get('delegation_application_id'):
        return ('configuration_source',)
    if role != 'operational_review':
        return ()
    paths = []
    if context['operational_evidence']['checkpoint_status'] == 'preserved':
        paths.append('operational_evidence.checkpoint_source')
    if recovery_materials_required(action, context):
        paths.extend(('recovery_materials.result_source', 'recovery_materials.checkpoint_source'))
    return tuple(paths)
