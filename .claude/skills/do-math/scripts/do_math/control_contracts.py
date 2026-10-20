"""Pure input shapes shared by public control admission and inbox consumption.

Domain owners still check required fields, authority, references and currentness.
These shapes check consumed values before routing or mutation; they do not run
domain actions or silently convert malformed values to empty objects.
"""
import base64
import binascii
import hashlib
import re
from functools import cache

from jsonschema import Draft202012Validator
from .record_schemas.schemas import PROFILE_REF, RECORDS
from .values import check_path_segment, json_copy

# A caller-chosen control request ID; the CLI request schema and ENGINE share it.
REQUEST_ID_PATTERN = '^[A-Za-z0-9_-]{1,128}$'
# The roles a public ``request --role`` queues; the CLI choices and ENGINE admission share it.
REQUESTABLE_ROLES = ("research_preparation", "research_plan", "supplemental_research", "operational_review", "maintenance")
SOURCE_FIELDS = frozenset({'name', 'body_base64', 'sha256', 'bytes'})
# Resource capacity and model allocation settings. Only a user decision changes
# them: public configure admission and inbox application both refuse the operator.
USER_DECISION_SETTINGS = ('session_limits', 'tier_models', 'role_tiers', 'claude_only_assigned_model',
                          'host_resources')
# The control actions an operator-origin request may use. Public control admission refuses
# the others, and the CLI offers the operator origin only on the commands of these actions.
OPERATOR_ACTIONS = frozenset({'pause', 'resume', 'request', 'configure', 'source', 'quiesce', 'release_quiesce'})


def user_decision_changed(current: dict, candidate: dict) -> bool:
    """Whether a candidate configuration changes a setting that only a user decision may change."""
    return any(candidate.get(key) != current.get(key) for key in USER_DECISION_SETTINGS)


def control_request_id(instance_id, action, *, text='', config=None, origin='user', idempotency_key=None,
                       after=None):
    """Hash normalized content, not mutable admission state or delivery time.

    A source control is hashed in its normalized name/body/hash/size form. ``after`` names
    the latest accepted opposite control of a default pause or resume ID (ENGINE's
    ``control``), so a pause after a resume is a new request while a resend replays.
    """
    from .canonical import exact_content_hash
    if idempotency_key is not None and (not isinstance(idempotency_key, str) or not idempotency_key):
        raise ValueError('idempotency_key must be a nonempty string')
    value = {'schema_version': 5, 'command': action, 'caller': origin,
             'payload': {'instance_id': instance_id, 'text': text, 'config': config or {}},
             'idempotency_key': idempotency_key}
    if after is not None:
        value['after'] = after
    return 'UC-' + exact_content_hash(value)


def validate_request_id(request_id):
    if not isinstance(request_id, str) or re.fullmatch(REQUEST_ID_PATTERN, request_id) is None:
        raise ValueError('request_id must be a safe nonempty ASCII identifier')


def normalized_source(name, raw):
    """The one admitted form of source bytes: exact body, hash and size."""
    return {'name': name, 'body_base64': base64.b64encode(raw).decode('ascii'),
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def normalized_source_bytes(spec):
    """Return the exact bytes of a normalized source, or raise ValueError.

    ENGINE's public ``control`` checks the source it produced with this rule,
    and the owner applies the same rule to the inbox copy before import.
    """
    if not isinstance(spec, dict) or set(spec) != SOURCE_FIELDS:
        raise ValueError('normalized source requires exact name, body, hash and size')
    name = spec['name']
    if not isinstance(name, str):
        raise ValueError('source name must be a file name')
    try:
        # The name becomes a workspace file name (input/sources/<n>-<name>), so
        # it obeys the one Windows path segment rule (values.check_path_segment).
        check_path_segment(name)
    except ValueError:
        raise ValueError('source name must be a file name') from None
    try:
        raw = base64.b64decode(spec['body_base64'], validate=True)
    except (binascii.Error, TypeError) as error:
        raise ValueError('source body is not strict base64') from error
    if hashlib.sha256(raw).hexdigest() != spec['sha256'] or len(raw) != spec['bytes']:
        raise ValueError('source bytes differ from their declared hash or size')
    return raw

TEXT = {'type': 'string'}
TEXTS = {'type': 'array', 'items': TEXT}
BOOL = {'type': 'boolean'}
INTEGER = {'type': 'integer'}
OBJECT = {'type': 'object'}
TIME = {'type': ['string', 'null']}


def obj(properties=None):
    return json_copy({'type': 'object', 'properties': properties or {}})


def fields(*, text='', lists='', objects=''):
    return json_copy({**{key: TEXT for key in text.split()}, **{key: TEXTS for key in lists.split()},
                      **{key: OBJECT for key in objects.split()}})


GOVERNANCE_RECORD = obj({**fields(text='id kind', lists='supersedes'), 'revision': INTEGER,
    'content': RECORDS['governance']['properties']['content'],
    'document': obj(fields(text='ref sha256'))})
# Closed like the stored grant, so a field the grant cannot store is refused at admission.
GRANT = {**obj({**fields(text='id kind reuse', lists='roles task_ids included_targets excluded_targets subjects execution_kinds purposes allowed_origins excluded_origins allowed_methods allowed_path_prefixes excluded_path_prefixes'),
    'expires_at': TIME, 'valid_from': TIME,
    'credential_env': {'type': 'object', 'additionalProperties': TEXT},
    **{key: BOOL for key in ('initialization_only', 'academic_only', 'requires_academic')}}), 'additionalProperties': False}
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
DECISION = obj({**fields(text='kind operation decision_id grant_id delegation_id task_id contract_sha256 config_sha256 disposition reason actor text import_id bundle_sha256 check_sha256 action_id procedure purpose lineage lineage_id hold_event_ref target_task_id',
    lists='replaces resolves_questions target_ids obligation_ids initial_grant_ids research_grant_ids',
    objects='review_policy config'), 'record': GOVERNANCE_RECORD, 'grant': GRANT, 'delegation': DELEGATION,
    'records': {'type': 'array', 'items': GOVERNANCE_RECORD}, 'allowed_action': ACTION,
    'revision': INTEGER, 'expires_at': TIME, 'profile_ref': PROFILE_REF, 'initial_profile_ref': PROFILE_REF,
    'profile_refs': {'type': 'array', 'items': PROFILE_REF},
    'unit_hashes': {'type': 'object', 'additionalProperties': TEXT},
    **{key: BOOL for key in ('adopt_current_governance', 'adopt_default_review_policy')},
    **fields(text='conversation_loss_policy external_policy')})
RELATION = obj(fields(text='id kind source target evidence confirmed_scope',
    lists='evidence_refs formal_result_refs assessment_refs'))
CANDIDATE = obj({**fields(text='id kind title statement explanation summary lean_code confirmed_scope epistemic_status selection_relevance',
    lists='declaration_names dependencies origin_refs source_refs'),
    'relation_claim': {'anyOf': [RELATION, {'type': 'null'}]}, 'formal_result_ref': TIME})
CONFIRMATION = {'type': ['object', 'null'], 'properties': {
    **fields(text='plan_digest decision review_ref reviewer_ref producer_ref', lists='affected_ids')}}
EVIDENCE = obj(fields(text='kind operation_id request_sha256 idempotency_key evidence_ref observed_at fact valid_until'))
IMPORT_APPROVALS = {'type': 'object', 'additionalProperties': obj(
    fields(text='actor source_ref source_sha256 change_sha256'))}
def _json_types(schema):
    if 'anyOf' in schema:
        return [kind for part in schema['anyOf'] for kind in _json_types(part)]
    if 'type' in schema:
        return [schema['type']]
    return ['string']  # The configuration enums are strings.


@cache
def _configure_validator():
    """The configure payload shape: each configuration key with only its JSON type.

    Keys and types come from the stored configuration section. Ranges and
    nested shapes stay with engine validation, which also resolves aliases
    such as a host constraint's request authority before storage.
    """
    from .record_schemas import config_schema
    properties = config_schema()['properties']
    return Draft202012Validator({'type': 'object', 'additionalProperties': False,
        'properties': {key: {'type': _json_types(schema)} for key, schema in properties.items()}})


PAYLOADS = {
    'pause': OBJECT,
    'resume': obj({'expected_user_pause_reason': TIME}),
    'close': OBJECT, 'quiesce': OBJECT,
    'release_quiesce': obj(fields(text='fence_id')),
    'input': {**obj({'responds_to': TEXTS}), 'additionalProperties': False},
    'request': obj({**fields(text='role retry_action', lists='cleanup_execution_ids'),
        'target': {'type': ['string', 'null']},
        'assessment_reassessment': obj({**fields(text='assessment_id assessment_sha256'), 'evidence': OBJECT}),
        'review_restoration': RECOVERY, 'review_replacement': RECOVERY}),
    'decision': obj({'change': DECISION}),
    'knowledge': obj({**fields(text='id reason family token'),
        'operation': {'enum': ['import', 'register-kind', 'withdraw-kind', 'import-relation', 'revise', 'invalidate']},
        'candidate': CANDIDATE, 'relation': RELATION, 'changes': OBJECT,
        'definition': obj({**fields(text='family token meaning'), 'constraints': OBJECT}),
        'declared_impact': {'type': ['array', 'null'], 'items': TEXT}, 'independent_confirmation': CONFIRMATION}),
    'trust': obj({**fields(text='env_id reason', objects='toolchain toolchain_record binding'),
        'operation': {'enum': ['register', 'transition', 'invalidate']}, 'allowed_axioms': TEXTS}),
    'external': obj({**fields(text='operation id grant_id source_ref target_id purpose subject actor_kind result'),
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


def validate_control_payload(action, text, config):
    if not isinstance(action, str) or action not in {*_VALIDATORS, 'configure'}:
        raise ValueError('unknown control action')
    if not isinstance(text, str):
        raise ValueError('control text must be a string')
    _check(_configure_validator() if action == 'configure' else _VALIDATORS[action], config, 'config')
    if action == 'trust' and config.get('operation') == 'register':
        from .trust_validation import register_request_errors
        errors = register_request_errors(config)
        if errors:
            raise ValueError('config: ' + '; '.join(errors))
