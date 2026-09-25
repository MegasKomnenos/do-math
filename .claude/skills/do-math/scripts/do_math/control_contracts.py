"""Pure input shapes shared by public control admission and inbox consumption.

Domain owners still check required fields, authority, references and currentness.
These shapes check consumed values before routing or mutation; they do not run
domain actions or silently convert malformed values to empty objects.
"""
from jsonschema import Draft202012Validator
from .record_schemas.schemas import PROFILE_REF, RECORDS, RUNTIME_FIELDS

TEXT = {'type': 'string'}
TEXTS = {'type': 'array', 'items': TEXT}
BOOL = {'type': 'boolean'}
INTEGER = {'type': 'integer'}
OBJECT = {'type': 'object'}
TIME = {'type': ['string', 'null']}


def obj(properties=None):
    return {'type': 'object', 'properties': properties or {}}


def fields(*, text='', lists='', objects=''):
    return {**{key: TEXT for key in text.split()}, **{key: TEXTS for key in lists.split()},
            **{key: OBJECT for key in objects.split()}}


GOVERNANCE_RECORD = obj({**fields(text='id kind', lists='supersedes'), 'revision': INTEGER,
    'content': RECORDS['governance']['properties']['content'],
    'document': obj(fields(text='ref sha256'))})
GRANT = obj({**fields(text='id kind reuse', lists='roles task_ids included_targets excluded_targets subjects execution_kinds purposes allowed_origins excluded_origins allowed_methods allowed_path_prefixes excluded_path_prefixes'),
    'expires_at': TIME, 'valid_from': TIME, 'resource_limits': OBJECT,
    'credential_env': {'type': 'object', 'additionalProperties': TEXT},
    **{key: BOOL for key in ('initialization_only', 'academic_only', 'requires_academic')}})
DELEGATION = obj({**fields(text='id status decision_kind original_decision_id',
    lists='included_targets excluded_targets external_effects', objects='resource_limits'),
    'expires_at': TIME})
# These are existing action coordinates, not a newly generated queue record.
# Share their field types (including target=None), without requiring generated fields.
ACTION = obj({key: RECORDS['queue']['properties'][key] for key in (
    'id role target stage slot review_cycle_id lineage_id grant_id continuation_of '
    'revision_targets assessment_targets observation_rule_targets repetition_bases round profile_ref').split()})
CASE = obj({**fields(text='id decision_kind target_id application_id', lists='external_effects', objects='effect resources'),
    'basis_refs': {'type': 'array', 'items': {'anyOf': [TEXT, {'type': 'object',
        'properties': {'id': TEXT}, 'required': ['id'], 'additionalProperties': False}]}}})
RECOVERY = obj({**fields(text='grant_id delegation_id'), 'action': ACTION, 'case': CASE})
DECISION = obj({**fields(text='kind operation decision_id grant_id delegation_id task_id contract_sha256 disposition reason actor text import_id bundle_sha256 check_sha256 action_id procedure purpose lineage lineage_id hold_event_ref target_task_id',
    lists='replaces resolves_questions target_ids obligation_ids initial_grant_ids research_grant_ids',
    objects='review_policy config'), 'record': GOVERNANCE_RECORD, 'grant': GRANT, 'delegation': DELEGATION,
    'records': {'type': 'array', 'items': GOVERNANCE_RECORD}, 'allowed_action': ACTION,
    'revision': INTEGER, 'expires_at': TIME, 'profile_ref': PROFILE_REF, 'initial_profile_ref': PROFILE_REF,
    'profile_refs': {'type': 'array', 'items': PROFILE_REF},
    'unit_hashes': {'type': 'object', 'additionalProperties': TEXT},
    **{key: BOOL for key in ('adopt_current_config', 'adopt_current_governance', 'adopt_default_review_policy')},
    **fields(text='conversation_loss_policy external_policy')})
RELATION = obj(fields(text='id kind source target evidence confirmed_scope',
    lists='evidence_refs formal_result_refs assessment_refs'))
CANDIDATE = obj({**fields(text='id kind title statement explanation summary lean_code confirmed_scope epistemic_status selection_relevance formal_result_ref',
    lists='declaration_names dependencies origin_refs source_refs'),
    'relation_claim': {'anyOf': [RELATION, {'type': 'null'}]}, 'formal_result_ref': TIME})
CONFIRMATION = {'type': ['object', 'null'], 'properties': {
    **fields(text='plan_digest decision review_ref reviewer_ref producer_ref', lists='affected_ids')}}
EVIDENCE = obj(fields(text='kind operation_id request_sha256 idempotency_key evidence_ref observed_at fact valid_until'))
IMPORT_APPROVALS = {'type': 'object', 'additionalProperties': obj(
    fields(text='actor source_ref source_sha256 change_sha256'))}
CONFIG_PATCH = obj({
    **fields(text='effort operator_effort observation_mode', lists='allowed_axioms'),
    **{key: INTEGER for key in ('call_timeout_seconds reviewers goal_auditors max_input_bytes max_output_repairs '
        'review_rounds review_research_limit research_reconsider_seconds observation_interval_seconds '
        'plan_settle_seconds checkpoint_grace_seconds max_artifact_bytes operator_interval_seconds '
        'operator_timeout_seconds provider_retry_initial_seconds provider_retry_max_seconds finish_notice_seconds '
        'tool_review_window_seconds self_check_response_window_seconds no_progress_limit import_rework_limit '
        'selection_failure_limit exhaustion_empty_limit proposal_version_limit contract_revision_limit').split()},
    **{key: BOOL for key in ('operator_enabled', 'scholarly_enabled', 'claude_only_assigned_model')},
    **{key: {'type': 'object', 'additionalProperties': TEXT} for key in ('tier_models', 'role_tiers')},
    'session_limits': {'type': 'object', 'additionalProperties': {'type': 'object', 'additionalProperties': INTEGER}},
    'lean_command': {'type': ['array', 'null'], 'items': TEXT},
    'host_resources': {'type': ['object', 'null']}, 'scholarly_server': {'type': ['object', 'null']}})

PAYLOADS = {
    'pause': obj({'model_policy_violation': RUNTIME_FIELDS['model_policy_violation']}),
    'resume': obj({'expected_user_pause_reason': TIME}),
    'close': OBJECT, 'quiesce': OBJECT,
    'release_quiesce': obj(fields(text='fence_id')),
    'input': obj({'responds_to': TEXTS, 'import_approvals': IMPORT_APPROVALS}),
    'configure': CONFIG_PATCH,
    'request': obj({**fields(text='role retry_action', lists='cleanup_execution_ids'),
        'target': {'type': ['string', 'null']},
        'assessment_reassessment': obj({**fields(text='assessment_id assessment_sha256'), 'evidence': OBJECT}),
        'review_restoration': RECOVERY, 'review_replacement': RECOVERY}),
    'decision': obj({'change': DECISION}),
    'knowledge': obj({**fields(text='operation id reason family token check_ref'),
        'candidate': CANDIDATE, 'relation': RELATION, 'changes': OBJECT,
        'definition': obj({**fields(text='family token meaning'), 'constraints': OBJECT}),
        'declared_impact': {'type': ['array', 'null'], 'items': TEXT}, 'independent_confirmation': CONFIRMATION}),
    'trust': obj({**fields(text='operation env_id reason', objects='toolchain manifest'), 'allowed_axioms': TEXTS}),
    'external': obj({**fields(text='operation id grant_id source_ref target_id purpose subject budget_kind actor_kind result'),
        'request': obj(fields(text='method url body')), 'evidence': EVIDENCE,
        'idempotency_evidence': {'type': ['string', 'null']}}),
    'conversation': obj({**fields(text='operation id disconnect_policy reason'), 'generation': INTEGER,
        'lease_seconds': {'type': 'integer', 'minimum': 1}}),
    'source': obj({**fields(text='path name body_base64 sha256'), 'bytes': {'type': 'integer', 'minimum': 0}}),
}
_VALIDATORS = {key: Draft202012Validator(schema) for key, schema in PAYLOADS.items()}
_DECISION_VALIDATOR = Draft202012Validator(DECISION)
_APPROVAL_VALIDATOR = Draft202012Validator(IMPORT_APPROVALS)


def _check(validator, value, path):
    error = next(validator.iter_errors(value), None)
    if error is not None:
        location = '/'.join([path, *(str(part) for part in error.absolute_path)])
        raise ValueError(location + ': invalid ' + error.validator + ' (expected ' +
                         str(error.validator_value) + ')')


def validate_decision_shape(change):
    _check(_DECISION_VALIDATOR, change, 'change')


def validate_import_approvals(approvals):
    _check(_APPROVAL_VALIDATOR, approvals, 'import_approvals')


def validate_config_shape(config):
    _check(_VALIDATORS['configure'], config, 'config')


def validate_control_payload(action, text, config):
    if not isinstance(action, str) or action not in _VALIDATORS:
        raise ValueError('unknown control action')
    if not isinstance(text, str):
        raise ValueError('control text must be a string')
    _check(_VALIDATORS[action], config, 'config')
    if action == 'trust' and config.get('operation') == 'register':
        from .trust_validation import manifest_structure_errors
        from .formal import toolchain_errors
        errors = (manifest_structure_errors(config.get('manifest'))
                  + toolchain_errors(config.get('toolchain')))
        if errors:
            raise ValueError('config: ' + '; '.join(errors))
