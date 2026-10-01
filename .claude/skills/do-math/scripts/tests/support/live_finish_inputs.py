"""Stored planning snapshots for the remaining legacy role input boundaries."""
import hashlib

from do_math.canonical import canonical_json
from do_math.execution_lifecycle import transition_execution
from support.engine_context import package
from support.engine_lifecycle import clear_work, task, approve
from support.sim import Sim


def artifact_scene():
    sim = Sim.activated()
    clear_work(sim)
    raw = b'valid evidence\n'
    path = 'runtime/artifacts/BA-evidence/proof.txt'
    sim.engine._save({path: raw})
    sim.instance['sources'].append({'id': 'SO-1', 'name': 'source', 'path': path,
                                   'sha256': hashlib.sha256(raw).hexdigest()})
    row = task(sim.engine, 'TK-1', approved=False, inputs=['SO-1'], condition={'op': 'artifact_valid', 'artifact_ref': {
        'snapshot': sim.engine.head, 'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}})
    row['basis_refs'] = ['SO-1']
    approve(sim.engine, row)
    sim.engine._save()
    return sim, sim.runtime['tasks'][row['id']]


def issued_plan(sim):
    engine = sim.engine
    root = sim.root / 'packaged-plan'
    fitted, fixed = package(engine, root)
    action = fixed['action']
    engine._action_lifecycle_gate(action)
    row = engine._register_execution(action, {'id': 'EX-plan', 'role': 'research_plan', 'status': 'running'})
    row.update(input_snapshot=engine.head, input_bundle='BA-plan', goal_revision=fixed['goal_revision'],
               policy_revision=fixed['policy_revision'])
    at = sim.clock.now()
    transition_execution(row, 'stopping', at=at)
    transition_execution(row, 'ended', at=at, outcome='execution_incomplete')
    engine._save({'runtime/artifacts/BA-plan/input/submission/context.json': canonical_json(fixed)})
    return root, fitted, fixed
