"""Declared wait kinds, release conditions and resolver coordinates."""
from copy import deepcopy
from .values import require_text

ADMISSION_WAIT_RULES = {
    'capacity': {
        'constraint_kind': 'concurrency', 'slot': True, 'resource': True,
        'fields': ('model', 'profile_ref', 'reason', 'next_owner'),
        'resolvers': ('session_slots.SessionSlots.release', 'session_slots.SessionSlots.admission_check',
                      'governance_engine.GovernanceEngineMixin._configure_candidate'),
        'condition': 'Model reservations return or the user adopts an available model limit.',
    },
    'host_capacity': {
        'constraint_kind': 'host', 'slot': True, 'resource': True,
        'fields': ('model', 'profile_ref', 'constraint_id', 'constraint_kind', 'reason', 'next_owner'),
        'resolvers': ('session_slots.SessionSlots.release', 'session_slots.SessionSlots.admission_check',
                      'governance_engine.GovernanceEngineMixin._configure_candidate'),
        'condition': 'Host reservations return or the user adopts sufficient host capacity.',
    },
    'provider_limit': {
        'constraint_kind': None, 'slot': False, 'resource': False,
        'fields': ('model', 'profile_ref', 'provider', 'retry_at', 'reason', 'next_owner'),
        'resolvers': ('session_slots.SessionSlots.provider_wait', 'provider_wait.gate_open'),
        'condition': 'The recorded retry time permits one provider reobservation.',
    },
}

PROVIDER_WAIT = 'provider_limit'
SLOT_WAITS = frozenset(kind for kind, row in ADMISSION_WAIT_RULES.items() if row['slot'])
RESOURCE_WAITS = frozenset(kind for kind, row in ADMISSION_WAIT_RULES.items() if row['resource'])
ADMISSION_WAITS = frozenset(ADMISSION_WAIT_RULES)
BUDGET_WAIT_KINDS = {row['constraint_kind']: kind for kind, row in ADMISSION_WAIT_RULES.items()
                     if row['constraint_kind'] is not None}

REVIEW_WAIT_RULES = {
    'review_input_restoration': {
        'next_owner': 'review_recovery',
        'prepared_disposition': 'recovery_recorded', 'admission_disposition': 'review_input_restoration',
        'block_admission': True, 'restore_control': True,
        'resolvers': ('review_engine.ReviewEngineMixin._retry_review_restoration',
                      'review_engine.ReviewEngineMixin._authorize_review_replacement',
                      'review_engine.ReviewEngineMixin._release_review_wait'),
        'condition': 'Restore the exact slot input or authorize an independent replacement of that slot.',
    },
    'review_authority': {
        'next_owner': 'governance',
        'prepared_disposition': 'authorization_denied', 'admission_disposition': 'authorization_denied',
        'block_admission': False, 'restore_control': False,
        'resolvers': ('review_engine.ReviewEngineMixin._review_replacement_authority',
                      'review_engine.ReviewEngineMixin._authorize_review_replacement',
                      'review_engine.ReviewEngineMixin._release_review_wait'),
        'condition': 'The assigned replacement has current explicit grant or delegation authority.',
    },
}
REVIEW_WAITS = frozenset(REVIEW_WAIT_RULES)
REVIEW_ADMISSION_WAITS = frozenset(kind for kind, row in REVIEW_WAIT_RULES.items() if row['block_admission'])
REVIEW_RESTORATION_WAITS = frozenset(kind for kind, row in REVIEW_WAIT_RULES.items() if row['restore_control'])


def review_wait_kind(disposition):
    for kind, row in REVIEW_WAIT_RULES.items():
        if disposition in {row['prepared_disposition'], row['admission_disposition']}:
            return kind
    raise ValueError('review disposition has no declared wait: ' + repr(disposition))


def review_preparation_wait(action, prepared):
    recovery = prepared['recovery']
    return waiting_action({'action': deepcopy(action), 'kind': review_wait_kind(prepared['disposition']),
        'next_owner': recovery['next_owner'], 'reason': 'review input or authority requires resolution',
        'detail': deepcopy(recovery)})

FORMAL_WAIT_RULES = {
    'formal_environment': {
        'next_owner': 'trust_governance',
        'resume': 'environment_changed',
        'resolvers': ('formal_engine.FormalEngineMixin._resume_formal_waits', 'trust_validation.environment_changed'),
        'condition': 'The recorded toolchain state or active environment changes.',
    },
    'formal_authority': {
        'next_owner': 'trust_governance',
        'resume': 'authority_and_environment',
        'resolvers': ('formal_engine.FormalEngineMixin._resume_formal_waits', 'governance.authorize'),
        'condition': 'A current environment and the pinned action authority both permit the formal check.',
    },
    'formal_stopped': {
        'next_owner': 'trust_governance',
        'resume': 'recoverable_stop',
        'resolvers': ('formal_engine.FormalEngineMixin._resume_formal_waits', 'governance.authorize'),
        'condition': 'A recoverable stop has current environment and authority; an explicit execution stop stays held.',
    },
}
FORMAL_RECOVERABLE_STOPS = frozenset({'instance_paused', 'authority_changed', 'trust_environment_changed', 'input_changed'})


def formal_wait(action, kind, reason, *, execution_id=None, detail=None):
    if not isinstance(kind, str) or kind not in FORMAL_WAIT_RULES:
        raise ValueError('unregistered formal wait: ' + repr(kind))
    result = waiting_action({'action': deepcopy(action), 'kind': kind, 'reason': reason,
              'next_owner': FORMAL_WAIT_RULES[kind]['next_owner']})
    if execution_id is not None:
        result['execution_id'] = execution_id
    if detail is not None:
        result['detail'] = deepcopy(detail)
    return result

PREPARATION_WAIT_RULES = {
    'observation_rules': {
        'task_observation': True, 'input_deferral': False, 'input_version': None,
        'next_owner': 'research_preparation',
        'resolvers': ('planning_engine.PlanningEngineMixin._resolve_task_observation_waits',),
        'condition': 'The task receives valid execution-bound observation rules through preparation.',
    },
    'observation_configuration': {
        'task_observation': True, 'input_deferral': False, 'input_version': None,
        'next_owner': 'execution_profile',
        'resolvers': ('planning_engine.PlanningEngineMixin._retry_observation_configuration',
                      'planning_engine.PlanningEngineMixin._resolve_task_observation_waits'),
        'condition': 'A newly adopted valid profile or a newly prepared task replaces the invalid observation settings.',
    },
    'model_assessment_input': {
        'task_observation': False, 'input_deferral': True, 'input_version': 'assessment',
        'next_owner': 'research_preparation',
        'resolvers': ('planning_engine.PlanningEngineMixin._ensure_model_assessments',),
        'condition': 'The recorded assessment inputs or target task edition changes.',
    },
    'observation_rule_input': {
        'task_observation': False, 'input_deferral': True, 'input_version': 'rules',
        'next_owner': 'research_preparation',
        'resolvers': ('planning_engine.PlanningEngineMixin._ensure_model_assessments',),
        'condition': 'The recorded rule deferral inputs or target task edition changes.',
    },
}
TASK_OBSERVATION_WAITS = frozenset(kind for kind, row in PREPARATION_WAIT_RULES.items() if row['task_observation'])
PREPARATION_INPUT_WAITS = frozenset(kind for kind, row in PREPARATION_WAIT_RULES.items() if row['input_deferral'])

AUTHORITY_WAIT_RULES = {
    'action_authority': {
        'next_owner': 'user',
        'resolvers': ('governance_engine.GovernanceEngineMixin._resume_action_authority_waits',
                      'governance.authorize'),
        'condition': 'Exactly one current grant permits the preserved unstarted action and its existing grant binding.',
    },
}


def action_authority_wait(action, authority):
    kind = 'action_authority'
    return waiting_action({'action': deepcopy(action), 'kind': kind, 'reason': authority['reason'],
            'next_owner': AUTHORITY_WAIT_RULES[kind]['next_owner'], 'detail': deepcopy(authority)})


def observation_preparation_wait(action, reason, *, task_rules):
    kind = 'observation_rules' if task_rules else 'observation_configuration'
    return waiting_action({'action': deepcopy(action), 'kind': kind, 'reason': reason,
            'next_owner': PREPARATION_WAIT_RULES[kind]['next_owner']})


def preparation_deferral_kind(rule_deferrals):
    return 'observation_rule_input' if rule_deferrals else 'model_assessment_input'


PRODUCER_WAIT_RULES = {
    'input_overflow': {
        'next_owner': 'research_plan',
        'resolvers': ('core_engine.CoreEngineMixin._resume_input_overflow_action',
                      'core_engine.CoreEngineMixin._apply_input_overflow_resolutions'),
        'condition': 'A public retry or accepted plan selects an authorized profile for the exact preserved obligation.',
    },
    'output_validation': {
        'next_owner': 'operational_review', 'failure_retry': True,
        'resolvers': ('repair_execution.RepairExecutionMixin.continue_initial_retries',
                      'core_engine.CoreEngineMixin._complete_operational_disposition',
                      'decision_engine.DecisionEngineMixin._apply_action_resolutions'),
        'condition': 'An accepted bounded diagnosis continues the failed input or explicitly resolves the same judgment scope.',
    },
    'submission_failure': {
        'next_owner': 'operational_review', 'failure_retry': True,
        'resolvers': ('repair_execution.RepairExecutionMixin.continue_initial_retries',
                      'core_engine.CoreEngineMixin._complete_operational_disposition'),
        'condition': 'Confirmed local termination and intact input evidence allow an accepted diagnosis to continue the failed obligation safely.',
    },
    'execution_failure': {
        'next_owner': 'operational_review', 'failure_retry': True,
        'resolvers': ('repair_execution.RepairExecutionMixin.continue_initial_retries',
                      'core_engine.CoreEngineMixin._complete_operational_disposition',
                      'decision_engine.DecisionEngineMixin._apply_action_resolutions'),
        'condition': 'An accepted current diagnosis permits one safe continuation or resolves the same failed judgment scope.',
    },
    'submission_publication': {
        'next_owner': 'engine',
        'resolvers': ('core_engine.CoreEngineMixin._retry_submission_publications',),
        'condition': 'Publication premises or the recorded environment changes so the preserved sealed result can be reconsidered.',
    },
    'impact_review': {
        'next_owner': 'impact_review', 'retry_impact': True, 'impact_wait': True,
        'resolvers': ('core_engine.CoreEngineMixin._retry_impact_reviews',),
        'condition': 'All independently requested impact judgments end and approve the exact preserved mutation.',
    },
    'impact_review_changed': {
        'next_owner': 'research_preparation', 'impact_wait': True,
        'resolvers': ('task_scope.apply_task_dispositions',),
        'condition': 'A valid accepted withdrawal retires the unperformed AI task and preserves the held mutation evidence; protected or performed obligations retain their checks.',
    },
    'impact_review_blocked': {
        'next_owner': 'research_preparation', 'impact_wait': True,
        'resolvers': ('task_scope.apply_task_dispositions',),
        'condition': 'A valid accepted withdrawal retires the unperformed AI task without applying blocked mutation bytes; protected or performed obligations retain their checks.',
    },
    'import_application_authority': {
        'next_owner': 'user', 'intent_import': True,
        'resolvers': ('governance.apply_import_control',),
        'condition': 'Exact source-bound public approvals apply the preserved independently checked import units.',
    },
    'import_user_decision': {
        'next_owner': 'user', 'intent_import': True,
        'resolvers': ('governance_engine.GovernanceEngineMixin._resume_import_question_waits',),
        'condition': 'Every blocking question has an applied public answer and the unsuperseded import is reworked once.',
    },
    'revision_dependency': {
        'next_owner': 'research_preparation',
        'resolvers': ('revision_engine.RevisionEngineMixin._apply_revision_followup',
                      'revision_engine.RevisionEngineMixin._retire_closed_revision_targets'),
        'condition': 'Accepted revision dispositions resolve or transfer the retained targets, or explicit target retirement removes them.',
    },
    'review_initialization': {
        'next_owner': 'review_policy',
        'resolvers': ('review_engine.ReviewEngineMixin._retry_review_initialization',),
        'condition': 'The exact adopted review policy returns for the same current accepted formal result and trust environment.',
    },
}

WAITING_ACTION_RULES = {
    **REVIEW_WAIT_RULES, **FORMAL_WAIT_RULES, **PREPARATION_WAIT_RULES,
    **AUTHORITY_WAIT_RULES, **PRODUCER_WAIT_RULES,
}
FAILED_ACTION_WAITS = frozenset(kind for kind, row in WAITING_ACTION_RULES.items() if row.get('failure_retry'))
IMPACT_PENDING_WAITS = frozenset(kind for kind, row in WAITING_ACTION_RULES.items() if row.get('retry_impact'))
IMPACT_ACTION_WAITS = frozenset(kind for kind, row in WAITING_ACTION_RULES.items() if row.get('impact_wait'))
IMPORT_ACTION_WAITS = frozenset(kind for kind, row in WAITING_ACTION_RULES.items() if row.get('intent_import'))


def waiting_action(record):
    """Construct one current registered wait without sharing mutable evidence."""
    kind = record.get('kind')
    if not isinstance(kind, str) or kind not in WAITING_ACTION_RULES:
        raise ValueError('unregistered action wait: ' + repr(kind))
    if not isinstance(record.get('action'), dict) or 'reason' not in record:
        raise ValueError('action wait requires its actual action and reason')
    result = deepcopy(record)
    if 'next_owner' not in result:
        result['next_owner'] = WAITING_ACTION_RULES[kind]['next_owner']
    if not isinstance(result['next_owner'], str) or not result['next_owner'].strip():
        raise ValueError('action wait requires its actual next owner')
    return result


def update_waiting_action(record, **changes):
    """Validate the next kind before changing the caller-owned whole record."""
    candidate = {**record, **changes}
    if 'kind' in changes and changes['kind'] != record['kind'] and 'next_owner' not in changes:
        candidate.pop('next_owner', None)
    candidate = waiting_action(candidate)
    record.clear()
    record.update(candidate)


# Action-owned activity waits retain their existing release rule. Other activity
# waits have their own cause even when their human explanation is arbitrary text.
ACTIVITY_EXTRA_WAIT_RULES = {
    'machine_capacity': {'resolvers': ('core_engine.CoreEngineMixin._register_execution',),
        'condition': 'Machine admission permits the preserved action after local resources return.'},
    'operational_repair': {'resolvers': ('core_engine.CoreEngineMixin._settle_activity', 'repair_execution.resume_installation_repair'),
        'condition': 'The operational repair is applied and its exact obligation can continue.'},
    'provider_admission': {'resolvers': ('provider_engine.ProviderEngineMixin._provider_admit', 'core_engine.CoreEngineMixin._register_execution'),
        'condition': 'The preserved provider gate permits the next admitted attempt.'},
    'environment_interrupted': {'resolvers': ('formal_engine.FormalEngineMixin._trust_activation_steps',),
        'condition': 'The queued continuation rechecks the current transition environment.'},
    'trust_check_stopped': {'resolvers': ('formal_engine.FormalEngineMixin._trust_check_steps',),
        'condition': 'A public resume permits the preserved trust target continuation.'},
    'external_reconciliation': {'resolvers': ('external_engine.ExternalEngineMixin._external_control', 'external_engine.ExternalEngineMixin._external_execution_record'),
        'condition': 'A public external reconciliation confirms the effect and assigns its followup.'},
    'external_followup': {'resolvers': ('external_engine.ExternalEngineMixin._external_control', 'external_engine.ExternalEngineMixin._external_execution_record'),
        'condition': 'A public external decision resolves the failed or cancelled effect obligation.'},
    'review_resource_deferred': {'resolvers': ('review_engine.ReviewEngineMixin._settle_review_resource_dispositions',),
        'condition': 'The fixed proposal is superseded or withdrawn, or the instance ends; the deferred scope is retired with its unresolved obligation preserved.'},
    'installation_repair_retry': {'resolvers': ('scheduled_operator.recovery',),
        'condition': 'The current installation and failure evidence permit another authorized recovery attempt.'},
    'user_resume': {'resolvers': ('activities.resume_activity',),
        'condition': 'The caller supplies the exact publicly released pause condition.'},
    'required_input': {'resolvers': ('activities.resume_activity',),
        'condition': 'The caller supplies the exact satisfied input condition.'},
}
ACTIVITY_WAIT_RULES = {
    **{kind: {'resolvers': row['resolvers'], 'condition': row['condition']}
       for kind, row in WAITING_ACTION_RULES.items()},
    **ACTIVITY_EXTRA_WAIT_RULES,
}


def activity_wait_record(kind, *, reason, condition, next_owner, at):
    """One typed activity wait; explanation text never selects its release rule."""
    if not isinstance(kind, str) or kind not in ACTIVITY_WAIT_RULES:
        raise ValueError('unregistered activity wait: ' + repr(kind))
    require_text(reason, 'reason')
    require_text(at, 'at')
    if condition is None or next_owner is None:
        raise ValueError('condition and next_owner are required')
    return {'kind': kind, 'reason': reason, 'condition': deepcopy(condition),
            'next_owner': deepcopy(next_owner), 'at': at}
