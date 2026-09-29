"""An initializing Sim whose runtime holds one ended attempt and its pending operational disposition.

Moved from ``engine_fixtures.start_repair_host``, which built the same records
on a bare engine over a Git process; here the engine is the Sim's real engine
on the port fakes, and the records are published through its own ``_save``
under the storage contract. ``EX-target`` (research_work) and ``EX-review``
(operational_review) ended; the review's disposition ``OD-repair`` retries the
target's unfinished activity in a fresh workspace. The target's sealed input
holds ``raw`` at ``relative`` under bundle ``BA-target`` (artifact ``source``),
while the workspace copy at ``destination`` is damaged.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
from pathlib import Path

from do_math import activities, execution_lifecycle
from do_math.canonical import canonical_json
from do_math.execution_profiles import profile_ref
from support.sim import Sim

AT = '2026-09-20T00:00:00Z'


@dataclass
class RepairHost:
    sim: Sim
    raw: bytes
    digest: str
    relative: str
    source: str
    destination: Path
    record: dict

    @property
    def engine(self):
        return self.sim.engine


def repair_host(root):
    sim = Sim(root)
    engine = sim.engine
    runtime = engine.runtime
    runtime.setdefault('operational_dispositions', {})
    for eid, role, aid in [('EX-target', 'research_work', 'AY-target'), ('EX-review', 'operational_review', 'AY-review')]:
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
        activities.open_activity(runtime, activity_id=aid, activity_kind=role, owner_ref='engine', input_refs=[],
                                 opened_at=AT)
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=aid, actor_kind='ai',
                                                         input_manifest={}, profile_ref=profile_ref(profile), created_at=AT)
        execution.update(role=role, action={'id': 'AC-' + eid, 'role': role, 'owner_activity_id': aid})
        activities.assign_execution(runtime, aid, execution)
        execution_lifecycle.transition_execution(execution, 'ended', at=AT, outcome='cancelled')
    raw = b'sealed mathematical input\n'
    digest = hashlib.sha256(raw).hexdigest()
    relative = 'input/catalog/tasks.json'
    target = runtime['executions']['EX-target']
    target['input_bundle'] = 'BA-target'
    target['input_manifest'] = {'catalog': [{'path': relative, 'sha256': digest, 'bytes': len(raw)}],
                                'execution_profile_ref': target['execution_profile_ref']}
    source = 'runtime/artifacts/BA-target/' + relative
    destination = Path(engine.instance['workspace']) / 'runs/EX-target/workspace' / relative
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b'damaged')
    record = {'id': 'OD-repair', 'execution_id': 'EX-review', 'target_execution_id': 'EX-target',
              'created_at': AT, 'status': 'pending', 'disposition': {
                  'kind': 'retry', 'basis_refs': ['EX-target'], 'next_owner': 'engine',
                  'reason': 'Use a fresh workspace for the unfinished activity',
                  'scope': 'Same unfinished activity', 'replay_safety': 'No external effects'}}
    runtime['operational_dispositions'][record['id']] = deepcopy(record)
    runtime['executions']['EX-review']['action']['target'] = 'EX-target'
    engine._save({source: raw, 'runtime/artifacts/BA-target/manifest.json': canonical_json(target['input_manifest'])})
    return RepairHost(sim, raw, digest, relative, source, destination, record)
