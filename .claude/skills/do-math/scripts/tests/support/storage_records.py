"""Record-family storage over the in-process Git fake: repositories, a real engine on them, and a lost ref race.

Tests of the storage contract (``repository``, ``git_store``, layer 2) and of
the producers whose records it stores use the real ``ResearchRepository`` on
the Git port's fake and the fake clock (설계 4.3), so every publication passes
the storage contract.

- ``record_store(root)``: a repository at ``root`` for ``INSTANCE_ID``.
- ``RecordingGit``: the Git fake that also lists the objects a publication writes.
- ``held_ref_lock(store)``: another writer holds the instance ref, as a
  concurrent Git ref transaction does, so the next compare-and-swap fails and
  the ref stays where it was.
- ``engine_on(store, instance, runtime, ...)``: the real ``ResearchEngine`` on the
  port fakes over a repository initialized with a supplied state, for engine
  producers (layer 2 mixins) that tests call directly; its ``_save`` publishes
  through the storage contract.
- ``apply_control(sim, action, ...)``: a public control applied by one owner
  control pass; a rejected control fails at once (조사 K-35).
- ``reference_fixture_instance``, ``task_with_reference_locators`` and
  ``approved_governance_instance``: the storage inputs ``test_family_records``
  built from the product's producers.
"""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from do_math.repository import ResearchRepository
from support.fakes.calls import make_fake as fake_calls
from support.fakes.clock import FakeClock
from support.fakes.git_backend import InProcessGit, make_repository
from support.fakes.host import make_fake as fake_host
from support.fakes.http import make_fake as fake_http
from support.fakes.jobs import FakeJobs
from support.fakes.scheduler import make_fake as fake_scheduler

INSTANCE_ID = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'
# A second instance in the same repository, for a store with its own contract.
OTHER_INSTANCE_ID = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAW'


class RecordingGit(InProcessGit):
    """The in-process Git fake that lists every object written through the port as ``(kind, oid)``."""

    def __init__(self, objects=None):
        super().__init__(objects)
        self.writes = []

    def write_object(self, repository, kind, body):
        oid = super().write_object(repository, kind, body)
        self.writes.append((kind, oid))
        return oid


def record_store(root, *, instance_id=INSTANCE_ID, contract=None, object_format='sha1', backend=None, clock=None):
    """A ``ResearchRepository`` for ``instance_id`` over the Git fake; ``root`` becomes a new repository unless it is one."""
    root = Path(root)
    if not (root / '.git').is_dir():
        make_repository(root, object_format)
    return ResearchRepository(root, instance_id, contract=contract, backend=backend or InProcessGit(),
                              clock=clock or FakeClock())


@contextmanager
def held_ref_lock(store):
    """Another writer holds the instance ref's lock file while the block runs (Git's ref transaction lock)."""
    git = store._store
    lock = Path(git.git_dir) / (git.ref + '.lock')
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_bytes(b'')
    try:
        yield
    finally:
        lock.unlink()


def fake_ports(clock, git_backend):
    """A Ports bundle of fakes sharing ``clock`` and ``git_backend`` with a store."""
    from do_math.ports import Ports
    return Ports(clock=clock, git_backend=git_backend, calls=fake_calls(clock), jobs=FakeJobs([]),
                 scheduler=fake_scheduler(), http=fake_http({}), host=fake_host())


def engine_on(store, instance, runtime, *, workspace, ports, instance_id=INSTANCE_ID):
    """``(engine, head)``: ``store`` initialized with the state, and the real engine loaded from it on ``ports``.

    ``ports`` shares the store's clock and Git fake (``fake_ports``). The engine
    opens its control transport under the instance workspace, which a
    synthetic state names here.
    """
    from do_math.engine import ResearchEngine
    head = store.initialize({**instance, 'workspace': str(workspace)}, runtime)
    return ResearchEngine(store.repository, instance_id, ports=ports), head


def apply_control(sim, action, **options):
    """Queue a public control on ``sim``, run one control pass, and fail if that request was rejected."""
    request = sim.control(action, **options)
    sim.engine.process_controls()
    rejected = [row for row in sim.runtime['history'] if row.get('kind') == 'rejected_user_control'
                and row.get('request', {}).get('id') == request['request_id']]
    if rejected:
        raise AssertionError('public control was rejected: ' + repr(rejected))
    return request


def reference_fixture_instance():
    """An instance with the default profiles, a preserved source and a local research grant bound to it."""
    from do_math.configuration import DEFAULT_CONFIG
    from do_math.execution_profiles import build_profiles
    from do_math.governance import apply_decision, preserve_source
    from research_fixtures import current_state, governance_start
    config = {**deepcopy(DEFAULT_CONFIG), 'lean_command': ['fixture-lean'], 'scholarly_enabled': False}
    instance = current_state(governance_start({**build_profiles(config), 'governance_sources': {
        'GS-reference': preserve_source('GS-reference', 'Authorize the fixture research.', origin='user')}}))[0]
    instance, _, _ = apply_decision(instance, {}, {'kind': 'grant', 'grant': {
        'id': 'GR-reference', 'kind': 'local', 'roles': ['research_work'],
        'reuse': 'reusable'}}, source_ref='GS-reference')
    return instance


def task_with_reference_locators():
    """A planned stored task (``task_candidate_record``) whose inputs and basis hold source, context and tool locators."""
    from do_math.contracts import task_candidate_record
    from do_math.execution_profiles import profile_ref
    from research_fixtures import candidate
    instance = reference_fixture_instance()
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == 'research_work')
    wire = candidate('Reference locator fixture')
    wire.update(inputs=['source:NatAddZero.lean', 'tool:lean'],
                basis_refs=['context:goal', 'context:policy', 'tool:lean'],
                profile_refs=[profile_ref(profile)], authority_refs=['GR-reference'])
    task = task_candidate_record(wire, task_id='TK-reference-locators')
    task.pop('revises_task_id')
    task['status'] = 'planned'
    return task


def approved_governance_instance():
    """An instance whose charter ``CH-1`` (goal "Prove P") is adopted from source ``GS-1`` by decision ``DC-1``."""
    from research_fixtures import approved_governance, charter, current_state
    record = charter('CH-1', rationale='Study P', desired_result='Proof', partial_success_criteria=[],
                     priorities=[], evidence_boundary='proof')
    instance = approved_governance({'id': INSTANCE_ID}, [record], source=('GS-1', 'Study P'), approval_id='DC-1')
    return current_state(instance)[0]
