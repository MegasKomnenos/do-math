"""Scenes of the submission region's second batch on a Sim's engine and store.

They build on ``support.submission_receiver`` (the history scene) and replace
nothing in the product: faults come from the Git port fake, and state a
legacy test put on an in-memory engine is put on a Sim's real engine.

- ``native_scene()``: the legacy ``engine_fixtures.start_native_final``: the
  history scene whose running execution ``EX-history`` also records its
  decision basis in memory, as a native final needs.
- ``lost_acknowledgment(sim)``: while open, the first ref update that succeeds
  moves the ref and then raises ``OSError``, as when a Git commit landed and
  its acknowledgment was lost. The legacy test replaced the engine's ``_save``
  with a wrapper that saved and then raised. Yields the list of lost commits.
- ``unmatched(sim)``: the engine of a copy of the Sim's repository at another
  path, as another process sees it. The repository remembers the sealed rows
  it already matched per Git directory (이음새-정본.md §3); the copy's Git
  directory was never matched, so it compares sealed bytes again. The legacy
  tests cleared ``repository.VERIFIED_ARTIFACTS`` for that.
- ``withhold_publication(sim, execution_id)``: from now until
  ``release_publication(sim)``, every ref update the engine makes while it
  applies ``execution_id``'s submission bundles (``_apply_submission_bundles``
  on the call stack for that execution) fails, as when another writer holds the
  instance ref during that publication. The receiver then returns the bundle to
  the engine and the action waits for the publication (``submission_publication``);
  every other publication goes through.
"""
from __future__ import annotations

from contextlib import contextmanager
import shutil
import sys

from support.submission_receiver import history


def native_scene():
    from do_math.input_basis import capture_decision_basis
    scene = history()
    engine = scene.engine
    engine.runtime['executions']['EX-history']['decision_basis'] = capture_decision_basis(
        engine.instance, engine.runtime, [])
    return scene


@contextmanager
def lost_acknowledgment(sim):
    backend = sim.ports.git_backend
    real = backend.update_ref
    lost = []

    def update_ref(repository, ref, new, old):
        moved = real(repository, ref, new, old)
        if moved and not lost:
            lost.append(new)
            raise OSError('acknowledgment lost after actual Git commit')
        return moved
    backend.update_ref = update_ref
    try:
        yield lost
    finally:
        del backend.update_ref


def withhold_publication(sim, execution_id):
    from do_math.engine import ResearchEngine
    application = ResearchEngine._apply_submission_bundles.__code__
    backend = sim.ports.git_backend
    real = type(backend).update_ref.__get__(backend)

    def update_ref(repository, ref, new, old):
        frame = sys._getframe(1)
        while frame is not None:
            if frame.f_code is application and frame.f_locals.get('execution_id') == execution_id:
                return False
            frame = frame.f_back
        return real(repository, ref, new, old)
    backend.update_ref = update_ref


def release_publication(sim):
    sim.ports.git_backend.__dict__.pop('update_ref', None)


def unmatched(sim, name='repository-unmatched'):
    from do_math.engine import ResearchEngine
    copy = sim.root / name
    shutil.copytree(sim.repository, copy)
    objects = sim.ports.git_backend.objects
    objects[str((copy / '.git').absolute())] = dict(objects[str((sim.repository / '.git').absolute())])
    return ResearchEngine(copy, sim.instance_id, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
