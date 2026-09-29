"""A running execution on a Sim's real engine, and the runner's observation batches for it.

``running_execution(sim, execution_id, role)`` opens an activity and registers
one execution of ``role`` through the product's own lifecycle functions
(``activities``, ``execution_lifecycle``), moves it to ``running`` and
publishes it with the engine's ``_save`` under the storage contract. It
returns the execution's workspace (``<instance workspace>/runs/<id>/workspace``).
Legacy tests put a bare ``{'status': 'running'}`` record into a memory engine
whose ``_save`` was a double; this record passes the real store. ``bind`` also
issues the execution's control transport binding, as input preparation does.

``batch(sim, events, stream_path, ...)`` is the ``ObservationBatch`` a
``ModelRunner`` hands the owner: consecutive JSON rows from ``start``, received
at the Sim clock's time (so no real time reaches the published state).
"""
import json
from pathlib import Path

from do_math import activities, execution_lifecycle
from do_math.execution_profiles import profile_ref
from do_math.observation_transport import ObservationBatch


def running_execution(sim, execution_id, role, *, action=None, bind=False):
    engine = sim.engine
    runtime = engine.runtime
    at = sim.clock.now()
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    activity = 'AY-' + execution_id
    activities.open_activity(runtime, activity_id=activity, activity_kind=role, owner_ref='engine', input_refs=[],
                             opened_at=at)
    execution = execution_lifecycle.create_execution(execution_id=execution_id, owner_activity_id=activity,
                                                     actor_kind='ai', input_manifest={},
                                                     profile_ref=profile_ref(profile), created_at=at)
    execution.update(role=role, action={'id': 'AC-' + execution_id, 'role': role, 'owner_activity_id': activity,
                                        **(action or {})})
    activities.assign_execution(runtime, activity, execution)
    for status in ('starting', 'running'):
        execution_lifecycle.transition_execution(runtime['executions'][execution_id], status, at=at)
    engine._save()
    workspace = Path(engine.instance['workspace']) / 'runs' / execution_id / 'workspace'
    workspace.mkdir(parents=True, exist_ok=True)
    if bind:
        engine._transport_bindings[execution_id] = engine._transport.issue(
            execution_id, 'GR-research-sim', workspace=workspace, self_check=True)
    return workspace


def batch(sim, events, stream_path, *, start=0, rows=None, first_row=0, terminated=False, received_monotonic=None):
    """The runner's batch of ``events``; ``rows`` gives their exact bytes (default: one JSON row each).

    ``received_monotonic`` is when the runner read the rows (default: the Sim clock now).
    """
    rows = rows if rows is not None else [json.dumps(event).encode('utf-8') + b'\n' for event in events]
    offsets, position = [], start
    for row in rows:
        offsets.append((position, position + len(row)))
        position += len(row)
    received = sim.clock.monotonic() if received_monotonic is None else received_monotonic
    return ObservationBatch(list(events), offsets, list(rows), first_row, sim.clock.now(), received,
                            position, Path(stream_path), lambda: terminated)
