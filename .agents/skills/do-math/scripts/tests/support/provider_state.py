"""Provider-region states over the in-process Git fake: a real engine on a small state, and the provider-gate store.

- ``engine_over(root, instance=None, runtime=None, *, config=None)``: ``(engine,
  store)``: the real ``ResearchEngine`` on the port fakes, loaded from a new
  repository under ``root`` initialized with the smallest state the storage
  contract accepts (``research_fixtures.current_state``), a ``ready`` runtime,
  ``config`` (default: ``DEFAULT_CONFIG``) with its profiles, and the given
  fields. It stands in for the legacy ``bare_engine`` and ``routing_engine``,
  which built an engine object over an in-memory store (조사 S-02, S-04).
- ``gate_store(root, *, clock, backend)``: the legacy
  ``provider_fixtures.provider_repository`` on the Git fake: one ``ready``
  instance whose every tier uses ``PROVIDER_MODEL`` with three work slots.
- ``transact(store, operation, *, clock, jobs)``: the legacy
  ``provider_fixtures.transact`` with the clock and Jobs ports passed to the
  session slots: under the writer lock, load, ``operation(slots, instance,
  runtime)``, and publish the result through the storage contract. The legacy
  helper built its slots without ports, which then fell back to the system
  clock and the Windows Jobs.

The session-slot operations ``admit``, ``report`` and ``finish`` stay in
``provider_fixtures``; they patch nothing, and ``finish`` keeps its check that
the release settled (조사 K-47).
"""
from copy import deepcopy
from pathlib import Path

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles
from do_math.session_slots import SessionSlots
from support.provider_inputs import PROVIDER_MODEL
from support.state_builders import current_state
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit
from support.provider_runs import ProviderJobs, fake_ports
from support.storage_records import INSTANCE_ID, engine_on, record_store


def engine_over(root, instance=None, runtime=None, *, config=None):
    """``(engine, store)``: the real engine on the port fakes over a small initialized state under ``root``.

    The state is written directly (``storage_records.engine_on``), not reached by
    the public ``initialize``/``activate``: it passes the storage contract but
    lacks families ``initialize_state`` always writes (``knowledge``,
    ``relations``, ``grants``, ``governance``; runtime ``availability``,
    ``events``, ``cycles``), so the product never holds it. It exists to call
    one engine method whose reads stay inside the given families (the provider
    receipt methods ``_apply_model_metadata``, ``_ensure_model_assessments``,
    ``_collect_submitted_result``), replacing the old stateless ``bare_engine``.
    A test whose method reads more starts from ``Sim`` instead.
    """
    from support.entry import entry
    _entry = entry()
    root = Path(root)
    clock, backend = FakeClock(), InProcessGit()
    config = deepcopy(DEFAULT_CONFIG) if config is None else config
    store = record_store(root / 'repository', backend=backend, clock=clock)
    state = current_state({'id': INSTANCE_ID, 'config': config, **build_profiles(config, host=_entry.ports.host), **(instance or {})},
                          {'status': 'ready', 'executions': {}, 'reservations': {}, 'provider_waits': {},
                           'queue': [], **(runtime or {})})
    engine, _ = engine_on(store, *state, workspace=root / 'work',
                          ports=fake_ports(clock, backend, ProviderJobs(clock=clock)))
    return engine, store


def gate_store(root, *, clock, backend):
    """A store under ``root`` holding one ready instance whose tiers all use ``PROVIDER_MODEL``."""
    from support.entry import entry
    _entry = entry()
    config = {**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False,
              'tier_models': {tier: PROVIDER_MODEL for tier in ('low', 'medium', 'high')},
              'session_limits': {'work': {PROVIDER_MODEL: 3}}}
    instance, runtime = current_state(
        {'id': INSTANCE_ID, 'workspace': str(Path(root) / 'work'), 'config': config, **build_profiles(config, host=_entry.ports.host)},
        {'status': 'ready', 'executions': {}, 'activities': {}, 'reservations': {}, 'provider_waits': {}})
    store = record_store(Path(root) / 'repository', backend=backend, clock=clock)
    store.initialize(instance, runtime)
    return store


def transact(store, operation, *, clock, jobs):
    """Load under the writer lock, apply ``operation(slots, instance, runtime)`` and publish; returns its result."""
    from support.entry import entry
    _entry = entry()
    with store.writer_lock():
        head, instance, runtime = store.load()
        slots = SessionSlots(runtime, instance, clock=clock, jobs=jobs, host_id=_entry.host_id)
        result = operation(slots, instance, runtime)
        store.save_with_state(head, instance, runtime)
        return result
