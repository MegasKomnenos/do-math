"""Cross-obligation oracles from the current execution/storage contracts.

통합-설계 4, 5, 6: local termination returns local reservations exactly once;
terminal tasks are not assignable; ended executions and sealed evidence survive
controls/restarts. 연구-계획: judgment history is retained, even when its basis
is no longer current. These assertions do not repair or refresh product state.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import unittest

from do_math.execution_profiles import resolve_profile
from do_math.task_contracts import TERMINAL_TASK_STATUSES


def worker_executions(sim):
    """Read the actual requests launched by ModelRunner through the Jobs port."""
    return [json.loads(Path(job.argv[2]).read_bytes())['execution_id']
            for job in sim.jobs.launched
            if len(job.argv) > 2 and Path(job.argv[1]).name in {'codex_worker.py', 'claude_worker.py'}]


def assert_call_records(test, sim):
    ids = worker_executions(sim)
    test.assertEqual(len(ids), len(set(ids)), 'one worker Job per model execution')
    rows = [sim.runtime['executions'][eid] for eid in ids]
    test.assertCountEqual([r['action']['id'] for r in rows], [c['action']['id'] for c in sim.model.calls])
    test.assertEqual(Counter(r['role'] for r in rows), Counter(c['role'] for c in sim.model.calls))
    return Counter(c['role'] for c in sim.model.calls)


class ContractOracle:
    def __init__(self, sim):
        self.test = unittest.TestCase()
        self.history = []
        self.decisions = {}
        self.judgments = []
        self.ended = {}
        self.settled = {}
        self.artifacts = {}
        self.proposals = {}
        self.seen_executions = set(sim.runtime['executions'])
        self.closed = False
        self.check(sim)

    def check(self, sim):
        t, e, runtime = self.test, sim.engine, sim.runtime
        head, stored_instance, stored_runtime = e.store.load()
        t.assertEqual(head, e.head)
        # Repository.load uses the real storage contract, not a test-side store.
        for name in ('executions', 'reservations', 'tasks', 'history'):
            t.assertEqual(stored_runtime.get(name), runtime.get(name), 'unpublished ' + name)
        t.assertEqual(stored_instance['knowledge'], sim.instance['knowledge'])
        t.assertEqual(runtime['history'][:len(self.history)], self.history, 'history was overwritten')
        self.history = deepcopy(runtime['history'])
        for key, old in self.decisions.items():
            t.assertEqual(sim.instance['decisions'][key], old, 'decision evidence was overwritten')
        self.decisions = deepcopy(sim.instance['decisions'])
        t.assertEqual(sim.instance['goal_judgments'][:len(self.judgments)], self.judgments,
                      'a new goal basis erased an earlier judgment')
        self.judgments = deepcopy(sim.instance['goal_judgments'])
        if self.closed:
            t.assertEqual(runtime['status'], 'closed', 'terminal instance reopened')
        self.closed |= runtime['status'] == 'closed'
        if runtime.get('user_pause') and not self.closed:
            t.assertEqual(runtime['status'], 'paused')
            t.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        for tid in e._task_readiness:
            t.assertIn(tid, runtime['tasks'])
            t.assertNotIn(runtime['tasks'][tid]['status'], TERMINAL_TASK_STATUSES)
        t.assertEqual(len({a['id'] for a in runtime['queue']}), len(runtime['queue']))
        live = [row for row in runtime['executions'].values() if row['status'] != 'ended']
        t.assertEqual(len({row['action']['id'] for row in live}), len(live), 'duplicate live action owner')
        slots = {}
        for action in runtime['queue'] + [row['action'] for row in live]:
            if action['role'] in {'identity_review', 'goal_audit'}:
                key = tuple(action.get(name) for name in ('role', 'target', 'review_cycle_id', 'basis',
                                                          'stage', 'round', 'slot'))
                t.assertEqual(slots.setdefault(key, action['id']), action['id'], 'two owners of one review slot')
        for cid, cycle in runtime['review_cycles'].items():
            proposal = cycle['proposal']
            if cid in self.proposals:
                t.assertEqual(proposal, self.proposals[cid], 'revision mutated the old sealed proposal')
            self.proposals[cid] = deepcopy(proposal)
        for row in runtime['executions'].values():
            if row['id'] in self.ended:
                t.assertEqual((row['status'], row.get('outcome')), self.ended[row['id']])
            if row['status'] == 'ended':
                self.ended[row['id']] = (row['status'], row.get('outcome'))
                if row.get('capacity'):
                    t.assertEqual(row['capacity']['local_termination'], 'confirmed')
            if row.get('execution_profile_ref'):
                profile = resolve_profile(sim.instance['execution_profiles'], row['execution_profile_ref'])
                if profile['actor_kind'] == 'ai':
                    t.assertEqual(row['model'], profile['ai']['model'])
                    if row['id'] not in self.seen_executions and row.get('started_at'):
                        # Rules apply grant changes between owner calls. Check
                        # new starts only: later revocation must not rewrite an
                        # already completed execution's historical authority.
                        grant = sim.instance['grants'][row['action']['grant_id']]
                        t.assertEqual(grant['status'], 'active', 'model started under revoked authority')
                        if grant.get('expires_at'):
                            t.assertLess(datetime.fromisoformat(row['started_at']),
                                         datetime.fromisoformat(grant['expires_at']),
                                         'model started after its grant expired')
            for item in row.get('output_files', []):
                if item.get('artifact_ref'):
                    self.artifacts.setdefault(item['artifact_ref'], item['sha256'])
        self.seen_executions.update(runtime['executions'])
        for path, digest in self.artifacts.items():
            t.assertEqual(hashlib.sha256(e.store.read(path, head)).hexdigest(), digest, 'lost sealed output ' + path)
        for key, row in runtime.get('reservations', {}).items():
            t.assertIn(row['owner_id'], runtime['executions'])
            t.assertLessEqual(row['confirmed_consumed'] + row['returned'], row['reserved'])
            if row['state'] == 'settled':
                t.assertEqual(row['confirmed_consumed'] + row['returned'], row['reserved'])
                t.assertTrue(row['evidence_refs'])
                if key in self.settled:
                    t.assertEqual(row, self.settled[key], 'reservation settled twice')
                self.settled[key] = deepcopy(row)
            elif runtime['executions'][row['owner_id']].get('capacity', {}).get('local_termination') == 'confirmed':
                t.fail('confirmed local termination left its local reservation held: ' + key)
        for job in sim.jobs.launched:
            t.assertTrue(job.done, 'owner returned before its local Job ended')
            t.assertTrue(job.closed, 'owner returned without closing its local Job')
