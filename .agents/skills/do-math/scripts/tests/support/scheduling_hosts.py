"""Host reservation helpers of the scheduling region: slot ledgers on port fakes, unknown Job ends, tickets, host settings.

- ``host_slots(runtime, instance, *, jobs=None)``: the slots ledger with a fake
  clock and a Jobs port (default: a ``FakeJobs``). Its tickets name the fake
  owner, and a named Job the fake never launched is empty.
- ``admit(slots, eid, profile)``: moved from ``test_host_resources.HostReservations.admit``.
  Admit a queued execution of the profile's role; returns ``(accepted, execution)``.
- ``UnknownJobs``: a Jobs fake that cannot tell whether a named Job is empty
  (``named_job_empty`` is ``None``), as the real port answers when it cannot
  open or query the Job.
- ``dispatched(eid, profile, *, jobs, clock)``: moved from
  ``research_fixtures.dispatched_launch`` with its ports passed: the ticket a
  native runner receives after dispatch.
- ``host_configuration()``: moved from ``test_host_resources.HostConfigurationTests.configuration``.
  The default settings with a host approval of 4 jobs, 512 MiB and 80 % CPU (a
  control reserve of 1 job, 128 MiB and 20 %) and, for every capped role, a
  demand of 1 job, 128 MiB and 20 %.
"""
from __future__ import annotations

from copy import deepcopy
import platform

from do_math import execution_profiles
from do_math.launch import mark_dispatched, ticket
from do_math.session_slots import SessionSlots
from support.fakes.clock import FakeClock
from support.fakes.jobs import FakeJobs


def host_slots(runtime, instance, *, jobs=None):
    return SessionSlots(runtime, instance, clock=FakeClock(), jobs=jobs if jobs is not None else FakeJobs())


def admit(slots, eid, profile):
    execution = {"id": eid, "role": profile["role"], "status": "queued"}
    accepted = slots.acquire(eid, profile=profile, execution=execution)
    return accepted, execution


class UnknownJobs(FakeJobs):
    def named_job_empty(self, name):
        return None


def dispatched(execution_id, profile, *, jobs, clock):
    return mark_dispatched(ticket(execution_id, profile, jobs=jobs, clock=clock))


def host_configuration():
    from do_math.configuration import DEFAULT_CONFIG
    settings = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False}
    roles = execution_profiles.build_profiles(settings)['role_profile_refs']
    host = execution_profiles.host_constraint(host_id=platform.node(),
        limits={'jobs': 4, 'memory_bytes': 536870912, 'cpu_rate_basis_points': 8000},
        control_reserve={'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000},
        authority_refs=['configuration:request'])
    settings['host_resources'] = {'constraint': host, 'demands_by_role': {
        role: {'jobs': 1, 'memory_bytes': 134217728, 'cpu_rate_basis_points': 2000}
        for role in roles if role in execution_profiles.HOST_ROLES}}
    return settings
