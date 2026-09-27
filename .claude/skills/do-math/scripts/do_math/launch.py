"""Durable pre-launch identity; absence of a callback is never an exit receipt."""
import uuid
import re
from . import windows_job
from .execution_profiles import LEAN_ROLES
from .file_io import is_sha256


def ticket(execution_id, profile):
    native = profile['actor_kind'] == 'ai' or profile['role'] in LEAN_ROLES
    return {'execution_id':execution_id, 'profile_sha256':profile['sha256'],
            'kind':'native_job' if native else 'owner_thread', 'owner':windows_job.owner_identity(),
            'job_name':'Local\\DoMath-' + uuid.uuid4().hex if native else None,
            'phase':'reserved'}


def validate(value, *, execution_id=None, profile_sha256=None):
    if not isinstance(value, dict) or set(value) != {'execution_id','profile_sha256','kind','owner','job_name','phase'}:
        raise ValueError('exact launch ticket required')
    if (not isinstance(value['execution_id'], str) or not value['execution_id']
            or not is_sha256(value['profile_sha256'])
            or value['kind'] not in {'native_job','owner_thread'}
            or value['phase'] not in {'reserved','dispatched','finished','not_started'}):
        raise ValueError('invalid launch ticket')
    if execution_id is not None and value['execution_id'] != execution_id:
        raise ValueError('launch ticket execution differs')
    if profile_sha256 is not None and value['profile_sha256'] != profile_sha256:
        raise ValueError('launch ticket profile differs')
    owner = value['owner']
    if (not isinstance(owner, dict) or set(owner) != {'pid','creation_filetime','host','session'}
            or type(owner['pid']) is not int or owner['pid'] <= 0
            or not isinstance(owner['creation_filetime'], str) or not owner['creation_filetime'].isdigit()
            or not isinstance(owner['host'], str) or type(owner['session']) is not int):
        raise ValueError('launch owner identity invalid')
    if value['kind'] == 'native_job':
        name = value['job_name']
        if not isinstance(name, str) or not re.fullmatch(r'Local\\DoMath-[0-9a-f]{32}', name):
            raise ValueError('launch Job name invalid')
    elif value['job_name'] is not None:
        raise ValueError('thread launch cannot identify a native Job')
    return value


def mark_dispatched(value):
    """The owner handed the reserved launch to its runner or calculation."""
    if value['phase'] != 'reserved':
        raise ValueError('only a reserved launch can be dispatched')
    value['phase'] = 'dispatched'
    return value


def mark_returned(value, result=None):
    """The local call returned; ``not_started`` is a start-failure receipt.

    With a runner ``result``, its ``launch_not_created`` receipt decides. Without
    one, an already recorded start failure is kept. A returned phase is final.
    """
    if value['phase'] in {'finished', 'not_started'}:
        return value
    if value['phase'] not in {'reserved', 'dispatched'}:
        raise ValueError('invalid launch phase')
    value['phase'] = ('not_started' if result is not None and result.get('launch_not_created') is True
                      else 'finished')
    return value


def validate_start(value, **binding):
    validate(value, **binding)
    if value['phase'] != 'dispatched' or value['owner'] != windows_job.owner_identity():
        raise ValueError('launch ticket does not belong to this dispatched owner')
    return value


def termination_confirmed(value, *, recovering=False):
    ended = windows_job.owner_ended(value['owner'])
    if ended is None:
        return False
    if recovering:
        if ended is not True:
            return False
    elif ended is not True and value['phase'] not in {'reserved','finished','not_started'}:
        return False
    if value['phase'] == 'not_started':
        return True  # A local start failure receipt, never absence of metadata.
    if value['kind'] == 'native_job':
        return windows_job.named_job_empty(value['job_name']) is True
    return ended is True or value['phase'] in {'reserved','finished'}
