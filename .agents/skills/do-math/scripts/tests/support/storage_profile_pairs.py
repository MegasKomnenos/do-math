"""Real initialization/configure inputs and profile-family receivers (layer 2).

Only Git, clock, host and Jobs ports are synthetic. Public initialization,
profile authoring, admission, reservation settlement and storage stay real.
The four authoring inputs exercise independent choices without multiplying
every setting by every role. No produced record gains fixture-only fields.
"""
from copy import deepcopy
from dataclasses import dataclass
import sys

from contracts.pairs import Pair
from do_math import activities, execution_lifecycle, execution_profiles
from do_math.engine import initialize
from do_math.record_schemas import POSITIVE_SETTINGS
from do_math.session_slots import SessionSlots
from do_math.state_contract import default_state_contract
from support.entry import entry
from support.scheduling_hosts import host_configuration
from support.storage_records import INSTANCE_ID, record_store


@dataclass
class ProfileCase:
    name: str
    patch: dict
    instance: dict
    runtime: dict
    store: object
    head: str
    inputs: object


def profile_cases(root):
    """Four real public initializations, each already published and reloaded."""
    server = {'command': sys.executable, 'args': ['synthetic-e\u0301']}
    rich = {key: 17 for key in POSITIVE_SETTINGS if key.endswith('_limit')}
    rich.update(self_check_response_window_seconds=23, tool_review_window_seconds=29)
    claude = {tier: 'claude:claude-sonnet-5' for tier in ('low', 'medium', 'high')}
    choices = [
        ('codex-default', {'scholarly_enabled': False}, None),
        ('claude-host', {**host_configuration(), **rich, 'tier_models': claude,
            'session_limits': {'work': {'claude:claude-sonnet-5': 3}},
            'operator_enabled': False, 'scholarly_enabled': True, 'scholarly_server': server,
            'claude_only_assigned_model': True, 'observation_mode': 'periodic',
            'lean_command': ['synthetic-lean', 'e\u0301']}, None),
        ('codex-tools', {'operator_enabled': False, 'scholarly_enabled': True,
            'scholarly_server': server, 'claude_only_assigned_model': True,
            'observation_mode': 'periodic'}, ['discovered-synthetic-lean']),
        ('claude-plain', {'tier_models': claude,
            'session_limits': {'work': {'claude:claude-sonnet-5': 3}},
            'scholarly_enabled': False, 'host_resources': None}, None),
    ]
    cases = []
    for name, patch, discovered in choices:
        inputs = entry()
        inputs.ports.host.lean = discovered
        path = root / name
        store = record_store(path / 'repository', backend=inputs.ports.git_backend, clock=inputs.ports.clock)
        initialize(store.repository, goal='Preserve the supplied profile settings e\u0301',
            workspace=path / 'work', config=deepcopy(patch), instance_id=INSTANCE_ID,
            ports=inputs.ports, host_id=inputs.host_id, codex_home=inputs.codex_home)
        head, instance, runtime = store.load()
        cases.append(ProfileCase(name, patch, instance, runtime, store, head, inputs))
    return cases


def family_receiver(family):
    """The installed record-local receiving checks; Repository checks relations."""
    def receive(value):
        errors = list(family.checker.iter_errors(value))
        if errors:
            raise ValueError(str(errors[0]))
        if family.validator:
            family.validator(deepcopy(value))
    return receive


def profile_pairs(cases):
    """Pair's top-level required+optional field meaning, for the four object families.

    host_capacity_ref is a scalar and reservations come from actual acquire;
    their tests use their own shapes rather than pretending they are objects.
    """
    contract = default_state_contract()
    result = []
    for name in ('config', 'execution_profiles', 'capacity_constraints', 'role_profile_refs'):
        family = contract.family('research', name)
        samples = []
        for case in cases:
            value = case.instance[name]
            rows = value.values() if family.shape == 'map' else [value]
            samples.extend((case.name, row) for row in rows)
        result.append(Pair(name, lambda root, samples=samples: samples,
            family_receiver(family), frozenset(family.schema['properties'])))
    return result


def acquire_roles(root, case, roles):
    """A private stored branch, with real activity/execution creation and acquire.

    Returns (store, slots, head, instance, runtime). No Job is started. Admission
    is published before a caller may inspect or release the reservations.
    """
    instance, runtime = deepcopy(case.instance), deepcopy(case.runtime)
    store = record_store(root, backend=case.inputs.ports.git_backend, clock=case.inputs.ports.clock)
    head = store.initialize(instance, runtime)
    slots = SessionSlots(runtime, instance, clock=case.inputs.ports.clock,
        jobs=case.inputs.ports.jobs, host_id=case.inputs.host_id)
    for index, role in enumerate(roles):
        reference = instance['role_profile_refs'][role][0]
        acquire_profile(slots, instance, runtime, reference, index=index)
    head = store.save_with_state(head, instance, runtime)[0]
    return store, slots, head, instance, runtime


def acquire_profile(slots, instance, runtime, reference, *, index):
    """Create and actually admit one attempt on an explicit registered edition."""
    profile = instance['execution_profiles'][reference['id']]
    eid, aid = f'EX-profile-{index}', f'AY-profile-{index}'
    at = slots.clock.now()
    execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid,
        actor_kind=profile['actor_kind'], input_manifest=[], profile_ref=reference, created_at=at)
    execution['role'] = profile['role']
    activities.open_activity(runtime, activity_id=aid, activity_kind=profile['role'],
        owner_ref=instance['id'], input_refs=[], opened_at=at)
    activities.assign_execution(runtime, aid, execution)
    before = deepcopy(runtime)
    if not slots.admission_check(profile)['allowed'] or runtime != before:
        raise AssertionError('read-only admission must allow this fixture without publishing')
    if not slots.acquire(eid, profile=profile, execution=execution):
        raise AssertionError(slots.admission_wait)
    return execution
