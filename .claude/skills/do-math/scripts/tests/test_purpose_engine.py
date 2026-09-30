"""Purpose-level tests of the real engine with explicit scripted semantics.

The runner and compiler are test doubles. Every purpose test uses a temporary
real Git repository with the installed schemas, CAS and immutable artifacts. Neither category establishes actual-model or actual-Lean accuracy.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from purpose_fixtures import ActivatedPurposeHarness


class PurposeEngineTests(ActivatedPurposeHarness):
    def test_live_continue_preserves_checkpoint_and_reserves_no_work_slot(self):
        from do_math.execution_profiles import resolve_profile
        engine, runner = self.make(observation='continue',  )
        # Both families first appear with their first record; earlier steps have neither.
        self.drive(engine, predicate=lambda e: any(
            row['disposition']['kind'] == 'continue' and row['target_execution_id'] in e.runtime.get('checkpoints', {})
            for row in e.runtime.get('operational_dispositions', {}).values()))
        live = [e for e in engine.runtime['executions'].values() if e['role'] == 'operational_review' and e['action'].get('live')]
        self.assertEqual(len(live), 1)
        parent = engine.runtime['executions'][live[0]['action']['target']]
        profiles = engine.instance['execution_profiles']
        # The worker's profile reserves a model work slot; the live operational
        # review's profile reserves none and so no model slot ever bounds it.
        self.assertTrue(resolve_profile(profiles, parent['execution_profile_ref'])['ai']['capacity_refs'])
        self.assertEqual(resolve_profile(profiles, live[0]['execution_profile_ref'])['ai']['capacity_refs'], [])
        self.assertEqual(live[0]['outcome'], 'output_accepted')
        self.assertFalse([row for row in engine.runtime.get('reservations', {}).values()
                          if row['owner_id'] == live[0]['id'] and row['unit'] == 'execution'])
        self.assertEqual(engine.runtime['checkpoints'][parent['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(r['target_execution_id'] == parent['id'] and r['disposition']['kind'] == 'continue'
                            for r in engine.runtime['operational_dispositions'].values()))

    def test_operating_review_runs_even_when_the_worker_used_the_last_work_call(self):
        engine, runner = self.make(observation='continue', )
        self.drive(engine, predicate=lambda e: any(ex['role'] == 'research_work' and ex.get('outcome') == 'output_accepted'
                                                 for ex in e.runtime['executions'].values()))
        from do_math.execution_profiles import WORK_ROLES, resolve_profile
        work = [ex for ex in engine.runtime['executions'].values() if ex['role'] in WORK_ROLES]
        operating = [ex for ex in engine.runtime['executions'].values() if ex['role'] == 'operational_review']
        self.assertEqual(len(work), 2)
        self.assertEqual(len(operating), 1)
        self.assertEqual(operating[0]['outcome'], 'output_accepted')
        # The operational review holds no work slot, so exhausted work slots cannot block it.
        self.assertEqual(resolve_profile(engine.instance['execution_profiles'],
                                         operating[0]['execution_profile_ref'])['ai']['capacity_refs'], [])

    def test_live_retry_stops_the_attempt_and_keeps_partial_artifacts_without_publishing_a_theorem(self):
        engine, runner = self.make(observation='stop')
        self.drive(engine, predicate=lambda e: any(ex.get('stop_requested') == 'operational_retry' and ex.get('status') == 'ended' for ex in e.runtime['executions'].values()))
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'execution_incomplete')
        self.assertEqual(worker['stop_requested'], 'operational_retry')
        self.assertTrue(any(a.get('continuation_of') == worker['id'] for a in engine.runtime['queue']))
        self.assertTrue(any(f['path'] == 'argument.txt' for f in worker['output_files']))
        self.assertFalse(engine.instance['knowledge'])

    def test_external_user_pause_is_processed_during_running_work(self):
        engine, runner = self.make(observation='external_pause')
        self.drive(engine, predicate=lambda e: e.runtime['status'] == 'paused')
        self.assertEqual(engine.runtime['status'], 'paused')
        worker = next(e for e in engine.runtime['executions'].values() if e['role'] == 'research_work')
        self.assertEqual(worker['outcome'], 'cancelled')
        self.assertEqual(engine.runtime['checkpoints'][worker['id']]['kind'], 'worker_checkpoint')
        self.assertTrue(any(h.get('kind') == 'user_control' and h['request']['action'] == 'pause' for h in engine.runtime['history']))
        self.assertFalse(engine.instance['knowledge'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
