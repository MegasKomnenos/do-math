"""Instance trust environments: lexical contracts and live checks against toolchain records.

An environment copies the identity of one shared toolchain record and names
the record file. The runtime binding names the record baseline whose olean
fingerprint this instance last accepted. Checks cover accidental change only;
they do not isolate the checker from a writer with the same OS identity.
"""
from copy import deepcopy
from pathlib import Path
import re

from .file_io import file_fingerprint, fingerprint_json
from .values import SHA256_SCHEMA as _HASH, is_sha256
from .migration_defaults import clock_or_system
from .lean_evidence import AXIOMS

_AXIOM_SET = frozenset(AXIOMS)
# The ID of one shared toolchain record; its file is trust_inventory.record_path.
RECORD_ID_PATTERN = '^TC-[0-9a-f]{64}$'
_RECORD_ID = re.compile(RECORD_ID_PATTERN)
# The runtime binding: the accepted baseline of the record and its digests.
BINDING_FIELDS = ('baseline', 'fingerprint_sha256', 'content_sha256', 'validation_sha256')
BINDING_SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': list(BINDING_FIELDS),
                  'properties': {'baseline': {'type': 'integer', 'minimum': 0},
                                 **{key: _HASH for key in BINDING_FIELDS[1:]}}}
# The stored environment record: its state, the identity copied from one
# toolchain record and that record's file. The accepted baseline is the
# runtime binding above, outside this record. The storage schema and
# environment_errors both use these names.
ENVIRONMENT_STATUSES = frozenset({'registered', 'active', 'superseded', 'invalid'})
ENVIRONMENT_PROPERTIES = {
    'status': {'enum': sorted(ENVIRONMENT_STATUSES)}, 'toolchain': {'type': 'object'},
    'allowed_axioms': {'type': 'array', 'items': {'type': 'string'}}, 'source_ref': {'type': 'string'},
    'toolchain_record': {'type': 'object', 'additionalProperties': False, 'required': ['path', 'id'],
                         'properties': {'path': {'type': 'string'},
                                        'id': {'type': 'string', 'pattern': RECORD_ID_PATTERN}}},
    'validation_receipt': {'type': 'object'}, 'invalidated_reason': {'type': 'string'}}
ENVIRONMENT_REQUIRED = ('status', 'toolchain', 'allowed_axioms', 'source_ref', 'toolchain_record')
_ENVIRONMENT_FIELDS = {'id', *ENVIRONMENT_REQUIRED}
_OPTIONAL_FIELDS = set(ENVIRONMENT_PROPERTIES) - _ENVIRONMENT_FIELDS
REGISTER_FIELDS = {'operation', 'toolchain', 'allowed_axioms', 'toolchain_record', 'binding'}


def binding_errors(binding):
    if (not isinstance(binding, dict) or set(binding) != set(BINDING_FIELDS)
            or type(binding['baseline']) is not int or binding['baseline'] < 0
            or any(not is_sha256(binding[k]) for k in BINDING_FIELDS[1:])):
        return ['trust binding requires a baseline index and its fingerprint, content and validation digests']
    return []


def record_reference_errors(reference):
    from .trust_inventory import record_path
    if (not isinstance(reference, dict) or set(reference) != {'path', 'id'}
            or not isinstance(reference['path'], str) or not Path(reference['path']).is_absolute()
            or not isinstance(reference['id'], str) or not _RECORD_ID.fullmatch(reference['id'])
            or Path(reference['path']) != record_path(Path(reference['path']).parent, reference['id'])):
        return ['toolchain_record requires the absolute path of <record ID>.json and that ID']
    return []


def environment_errors(environment, binding):
    """Lexical contract of a stored environment and its runtime binding; no host IO."""
    from .trust_inventory import identity_errors
    if not isinstance(environment, dict):
        return ['trust environment absent']
    errors = []
    if not _ENVIRONMENT_FIELDS <= set(environment) or set(environment) - _ENVIRONMENT_FIELDS - _OPTIONAL_FIELDS:
        errors.append('trust environment fields differ from the current contract')
    errors.extend(identity_errors(environment.get('toolchain')))
    if not environment.get('source_ref'):
        errors.append('trust environment has no explicit adoption')
    axioms = environment.get('allowed_axioms')
    if (not isinstance(axioms, list) or any(not isinstance(a, str) for a in axioms)
            or len(axioms) != len(_AXIOM_SET) or set(axioms) != _AXIOM_SET):
        errors.append('foundation axiom profile differs')
    errors.extend(record_reference_errors(environment.get('toolchain_record')))
    errors.extend(binding_errors(binding))
    return errors


def register_request_errors(config):
    """Lexical shape of a registration request, before the record file is read."""
    from .trust_inventory import identity_errors
    if not isinstance(config, dict) or set(config) != REGISTER_FIELDS:
        return ['trust register requires exactly toolchain, allowed_axioms, toolchain_record and binding']
    return (identity_errors(config['toolchain']) + record_reference_errors(config['toolchain_record'])
            + binding_errors(config['binding']))


class EnvironmentUnavailable(ValueError):
    """A live check of the approved environment failed. The sealed result is kept
    until the toolchain record or the active environment changes."""
    def __init__(self, message, detail):
        super().__init__(message)
        self.detail = detail


def record_state(environment):
    """Cheap change marker of the named record file, or None when it cannot be read."""
    try:
        return fingerprint_json(file_fingerprint(environment['toolchain_record']['path']))
    except OSError:
        return None


def wait_detail(instance):
    environment_id = instance.get('active_trust_environment')
    environment = instance.get('trust_environments', {}).get(environment_id)
    return {'environment_id': environment_id, 'record_state': record_state(environment) if environment else None}


def environment_changed(instance, detail):
    """True once a re-record, a repair or a transition may have resolved an environment wait."""
    return wait_detail(instance) != {key: detail.get(key) for key in ('environment_id', 'record_state')}


def check_environment(environment, binding, *, identity=True, clock=None, host=None):
    """Live admission: record contract, identity and the olean fingerprint.

    ``host`` (the host port) observes the toolchain identity where the check needs it.

    A different fingerprint is accepted only when it equals the record's current
    baseline, the bound baseline is older and the identity still matches. The
    caller then rebinds; this function never writes a baseline.
    """
    clock = clock_or_system(clock)
    from .trust_inventory import read_record, usable_errors, observe_fingerprint, binding as baseline_binding, changed_files
    from .canonical import exact_content_hash
    reference = environment['toolchain_record']
    result = {'environment_id': environment.get('id'), 'toolchain_record': deepcopy(reference),
              'record_state': record_state(environment), 'checked_at': clock.now(),
              'identity_sha256': exact_content_hash(environment['toolchain']), 'binding': deepcopy(binding)}
    try:
        record = read_record(reference['path'])
    except (OSError, ValueError) as error:
        return {**result, 'status': 'invalid', 'errors': ['toolchain record unavailable: ' + str(error)]}
    errors = []
    if record['id'] != reference['id']:
        errors.append('toolchain record ID differs from the registered record')
    if record['identity'] != environment['toolchain']:
        errors.append('toolchain record identity differs from the registered environment')
    errors.extend(usable_errors(record))
    if not errors and identity:
        errors.extend(host.toolchain_identity_errors(environment['toolchain']))
    if errors:
        return {**result, 'status': 'invalid', 'errors': errors}
    try:
        fingerprint = observe_fingerprint(record['identity'])
    except OSError as error:
        return {**result, 'status': 'invalid', 'errors': ['judgment files unavailable: ' + str(error)]}
    result['fingerprint_sha256'] = fingerprint['sha256']
    if fingerprint['sha256'] == binding['fingerprint_sha256']:
        return {**result, 'status': 'verified', 'errors': []}
    current = baseline_binding(record)
    if fingerprint['sha256'] == current['fingerprint_sha256'] and current != binding:
        if not identity:
            errors.extend(host.toolchain_identity_errors(environment['toolchain']))
        if not errors:
            entry = record['baselines'][current['baseline']]
            return {**result, 'status': 'verified', 'errors': [], 'binding': current,
                    'rebind': {'previous': deepcopy(binding), 'current': current,
                               'recorded_at': entry['recorded_at']}}
        return {**result, 'status': 'invalid', 'errors': errors}
    bound = record['baselines'][binding['baseline']] if binding['baseline'] < len(record['baselines']) else None
    expected = (bound['fingerprint']['files'] if bound and bound['fingerprint']['sha256'] == binding['fingerprint_sha256']
                else record['baselines'][-1]['fingerprint']['files'])
    changed = changed_files(expected, fingerprint['files'])
    return {**result, 'status': 'invalid', 'changed_files': changed[:50], 'changed_file_count': len(changed),
            'errors': ['olean fingerprint differs from the bound toolchain baseline; '
                       'setup_lean.py --rerecord (user or operator) or a new record and transition is required']}


def verify_formal(*, environment, binding, verifier, clock=None, host=None, **arguments):
    """Check the record and fingerprint before compiling; nothing is re-observed afterwards."""
    check = check_environment(environment, binding, identity=False, clock=clock, host=host)
    if check['status'] != 'verified':
        return {'status': 'failed', 'reason': 'environment admission failed: ' + '; '.join(check['errors']),
                'error_kind': 'trust_environment', 'environment_check': check, 'launch_not_created': True}
    result = verifier(**arguments)
    result['environment_check'] = check
    return result


def require_active_environment(instance, runtime, *, current_identity=False, host=None):
    """Formal-use admission: an active, structurally valid environment and, at
    publication gates, the current local identity of its executables, checker and project."""
    if any(row.get('status') in {'checking', 'ready'} for row in runtime.get('trust_transitions', {}).values()):
        raise ValueError('formal admission is blocked during a trust transition')
    environment_id = instance.get('active_trust_environment')
    environment = instance.get('trust_environments', {}).get(environment_id)
    errors = environment_errors(environment, runtime.get('trust_bindings', {}).get(environment_id))
    if not environment or environment.get('status') != 'active' or errors:
        raise ValueError('approved fixed trust environment required: ' + '; '.join(errors))
    if current_identity:
        errors = host.toolchain_identity_errors(environment['toolchain'])
        if errors:
            raise EnvironmentUnavailable('current trust identity required: ' + '; '.join(errors), wait_detail(instance))
    return deepcopy(environment)
