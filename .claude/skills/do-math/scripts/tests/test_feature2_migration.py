"""Known feature-1 migration and live currentness guards."""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.knowledge import capture_basis, validate_basis
from test_lifecycle_engine import FakeEngine
import tempfile


class Feature2MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = FakeEngine(self.temp.name)

    def legacy(self, knowledge=True):
        engine = self.engine
        engine.instance.update(contract_id='do-math-cli/1', feature_version=1, goal_status='mathematically_solved')
        engine.runtime.update(contract_id='do-math-cli/1', feature_version=1, status='completed')
        if knowledge:
            item = engine.knowledge('K1')
            item['reviews'] = [{'execution_id': 'old-review', 'slot': 0, 'decision': 'match', 'scope_complete': True}]
            item['formal']['toolchain'] = None
            engine.instance['goal_judgments'] = [{'basis': 'legacy-whole-catalog-hash', 'decision': 'satisfied', 'used_sources': ['K1']}]
            task = engine.task(inputs=['K1'])
            task.update(status='completed', feature_version=1)
        return engine

    def test_known_legacy_approval_is_preserved_but_cannot_remain_usable(self):
        engine = self.legacy()
        original = deepcopy(engine.instance['knowledge']['K1'])
        engine._upgrade_runtime()
        item = engine.instance['knowledge']['K1']
        self.assertEqual(item['status'], 'candidate')
        self.assertEqual(item['formal'], {})
        self.assertEqual(item['reviews'], [])
        self.assertEqual(item['history'][-1]['previous'], original)
        self.assertEqual(item['legacy_approval_ref']['feature_version'], 1)
        self.assertEqual(item['id'], 'K1')
        self.assertIsNone(engine.instance['active_trust_environment'])
        self.assertFalse(engine.instance['goal_judgments'][0]['current'])
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual(engine.runtime['tasks']['T1']['status'], 'completed')
        self.assertTrue(any(event.get('kind') == 'knowledge_reassessment_required' and 'T1' in event['tasks']
                            for event in engine.runtime['history']))
        self.assertEqual(len([a for a in engine.runtime['queue'] if a['role'] == 'formal_check']), 1)
        state = deepcopy((engine.instance, engine.runtime))
        engine._upgrade_runtime()
        self.assertEqual((engine.instance, engine.runtime), state)

    def test_no_legacy_approval_does_not_reopen_completed_instance(self):
        engine = self.legacy(knowledge=False)
        engine._upgrade_runtime()
        self.assertEqual(engine.runtime['status'], 'completed')
        self.assertEqual(engine.runtime['queue'], [])

    def test_future_version_is_not_converted(self):
        self.engine.instance['feature_version'] = 5
        before = deepcopy((self.engine.instance, self.engine.runtime))
        with self.assertRaises(ValueError): self.engine._upgrade_runtime()
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_live_conversation_guard_expires_without_new_scheduler_activity(self):
        engine = self.engine
        engine.control('conversation', {'operation': 'attach', 'id': 'C', 'generation': 1, 'lease_seconds': 5, 'disconnect_policy': 'pause'})
        engine.runtime['executions']['EX-live'] = {'id': 'EX-live', 'status': 'running', 'role': 'research_work'}
        old_heartbeat = engine.runtime['conversations']['C']['last_heartbeat_at']
        engine.current_time += timedelta(seconds=6)
        self.assertTrue(engine._check_conversations())
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['executions']['EX-live']['stop_requested'], 'conversation_lost')
        self.assertEqual(engine.runtime['conversations']['C']['last_heartbeat_at'], old_heartbeat)
        self.assertFalse(engine._check_conversations())
        self.assertEqual(len([e for e in engine.runtime['events'] if e['kind'] == 'conversation_lost']), 1)

    def test_goal_dependency_detects_changed_relation_endpoint_even_when_proof_record_is_unchanged(self):
        engine = self.engine
        for key in ('F1', 'F2'):
            engine.instance['knowledge'][key] = {'id': key, 'kind': 'question', 'status': 'candidate', 'statement': 'Natural zero identity'}
        proof = engine.knowledge('K-proof')
        proof['relation_claim'] = {'kind': 'equivalent', 'source': 'F1', 'target': 'F2', 'confirmed_scope': 'Natural zero identity'}
        proof['relation_endpoint_basis'] = capture_basis(engine.instance, engine.runtime, ['F1', 'F2'])
        proof_basis = capture_basis(engine.instance, engine.runtime, ['K-proof'])
        engine.instance['goal_judgments'] = [{'id': 'G', 'basis': 'current', 'current': True, 'dependencies': ['K-proof'], 'record_basis': proof_basis}]
        engine.instance.update(goal_status='mathematically_solved', goal_assessment_basis='current')
        engine.runtime['status'] = 'completed'
        engine.instance['knowledge']['F2']['statement'] = 'A different mathematical claim'
        self.assertTrue(validate_basis(proof_basis, engine.instance, engine.runtime)['valid'])
        engine._invalidate_goal_currentness()
        self.assertFalse(engine.instance['goal_judgments'][0]['current'])
        self.assertEqual(engine.instance['goal_status'], 'unresolved')
        self.assertEqual(engine.runtime['status'], 'ready')


if __name__ == '__main__':
    unittest.main(verbosity=2)
