"""Reject unsupported editions unchanged; retain currentness and conversation guards."""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.knowledge import capture_basis, validate_basis
from do_math.engine import ResearchEngine
from test_purpose_engine import PurposeHarness
from v5_fixtures import send_control
import tempfile


class Feature2MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.engine = ResearchEngine.__new__(ResearchEngine)
        self.engine.instance = {'feature_version': 5, 'contract_id': 'do-math-cli/5',
            'knowledge': {}, 'goal_judgments': []}
        self.engine.runtime = {'feature_version': 5, 'contract_id': 'do-math-cli/5', 'tasks': {}}

    def legacy(self, knowledge=True):
        engine = self.engine
        engine.instance.update(contract_id='do-math-cli/1', feature_version=1, goal_status='mathematically_solved')
        engine.runtime.update(contract_id='do-math-cli/1', feature_version=1, status='completed')
        if knowledge:
            engine.instance['knowledge']['K1'] = {'id': 'K1', 'status': 'verified', 'formal': {'toolchain': None},
                'reviews': [{'execution_id': 'old-review', 'slot': 0, 'decision': 'match', 'scope_complete': True}]}
            engine.instance['goal_judgments'] = [{'basis': 'legacy-whole-catalog-hash', 'decision': 'satisfied', 'used_sources': ['K1']}]
            engine.runtime['tasks']['T1'] = {'id': 'T1', 'inputs': ['K1'], 'status': 'completed', 'feature_version': 1}
        return engine

    def test_legacy_approval_is_rejected_without_rewriting_the_original(self):
        for version in (1, 2, 3, 4):
            with self.subTest(version=version):
                engine = self.legacy()
                engine.instance.update(feature_version=version, contract_id=f'do-math-cli/{version}')
                engine.runtime.update(feature_version=version, contract_id=f'do-math-cli/{version}')
                original = deepcopy((engine.instance, engine.runtime))
                with self.assertRaisesRegex(ValueError, 'unsupported feature version'):
                    engine._upgrade_runtime()
                self.assertEqual((engine.instance, engine.runtime), original)

    def test_completed_legacy_instance_without_knowledge_is_not_automatically_promoted(self):
        engine = self.legacy(knowledge=False)
        original = deepcopy((engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, 'unsupported feature version'):
            engine._upgrade_runtime()
        self.assertEqual((engine.instance, engine.runtime), original)

    def test_future_version_is_not_converted(self):
        self.engine.instance['feature_version'] = 6
        self.engine.runtime['feature_version'] = 6
        before = deepcopy((self.engine.instance, self.engine.runtime))
        with self.assertRaises(ValueError):
            self.engine._upgrade_runtime()
        self.assertEqual((self.engine.instance, self.engine.runtime), before)

    def test_public_resume_and_control_leave_legacy_git_head_and_artifacts_unchanged(self):
        import subprocess
        from do_math.engine import control
        from do_math.git_store import GitStateStore
        from do_math.repository import canonical_json
        repository = Path(self.temp.name) / 'legacy-repository'
        subprocess.run(['git', 'init', '-q', str(repository)], check=True)
        iid = 'RI-00000000000000000000000000'
        legacy = self.legacy()
        legacy.instance['id'] = iid
        raw = {
            'research/instance.json': canonical_json(legacy.instance),
            'runtime/state.json': canonical_json(legacy.runtime),
            'runtime/artifacts/legacy/original.bin': b'original legacy output\x00\xff',
        }
        # Seed unsupported input through the byte storage primitive. The tested
        # consumers below are the real public engine and control entry points.
        store = GitStateStore(repository, iid)
        head = store.publish(None, raw).head
        with self.assertRaises((ValueError, KeyError)):
            ResearchEngine(repository, iid)
        with self.assertRaises((ValueError, KeyError)):
            control(repository, iid, 'resume')
        self.assertEqual(store.read_snapshot().head, head)
        for path, content in raw.items():
            self.assertEqual(store.read_bytes(head, path), content)


class VersionFiveCurrentnessTests(PurposeHarness):
    def test_live_conversation_guard_expires_without_new_scheduler_activity(self):
        from datetime import datetime
        from do_math.repository import new_id
        from do_math.engine import now
        engine, _ = self.make()
        send_control(engine, 'conversation', config={'operation': 'attach', 'id': 'C', 'generation': 1,
            'lease_seconds': 3600, 'disconnect_policy': 'pause'})
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
        execution = engine._register_execution(action, {'id': new_id('EX'), 'role': action['role'],
            'status': 'running', 'created_at': now(), 'input_snapshot': engine.head})
        before = deepcopy(engine.runtime['conversations']['C'])
        future = datetime.fromisoformat(before['lease_expires_at']) + timedelta(seconds=1)
        engine.lifecycle_clock = lambda: future.isoformat()
        engine.lifecycle_monotonic = lambda: 0.0
        engine._clock_anchor = None  # Switch both clocks to one controlled epoch.
        self.assertTrue(engine._check_conversations())
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(execution['stop_requested'], 'conversation_lost')
        self.assertEqual(engine.runtime['conversations']['C']['last_heartbeat_at'], before['last_heartbeat_at'])
        self.assertFalse(engine._check_conversations())
        self.assertEqual(len([e for e in engine.runtime['events'] if e['kind'] == 'conversation_lost']), 1)

    def test_goal_dependency_detects_changed_relation_endpoint_even_when_proof_record_is_unchanged(self):
        from do_math.knowledge_io import import_candidate
        engine, _ = self.make()
        self.drive(engine)
        proof_id = next(iter(engine.instance['knowledge']))
        endpoint_ids = []
        for label in ('left endpoint', 'right endpoint'):
            engine.instance, engine.runtime, endpoint_id = import_candidate(engine.instance, engine.runtime, {'kind': 'question', 'title': label,
                'statement': 'Natural zero identity', 'explanation': 'Specify the exact natural-number endpoint',
                'summary': label, 'lean_code': '', 'declaration_names': [], 'dependencies': []},
                source_ref=engine.instance['id'], actor_ref=engine.instance['id'])
            endpoint_ids.append(endpoint_id)
        proof_basis = capture_basis(engine.instance, engine.runtime, [proof_id])
        endpoint_refs = [*endpoint_ids, *[engine.instance['knowledge'][kid]['exposition_id'] for kid in endpoint_ids]]
        endpoint_basis = capture_basis(engine.instance, engine.runtime, endpoint_refs)
        # The goal assessor explicitly used both relation endpoints as premises.
        judgment = engine.instance['goal_judgments'][-1]
        judgment['record_basis'] = capture_basis(engine.instance, engine.runtime, [proof_id, *endpoint_refs])
        endpoint = engine.instance['knowledge'][endpoint_ids[1]]
        exposition = engine.instance['expositions'][endpoint['exposition_id']]
        exposition['items'][0]['text'] = 'A different mathematical claim'
        self.assertTrue(validate_basis(proof_basis, engine.instance, engine.runtime)['valid'])
        self.assertFalse(validate_basis(endpoint_basis, engine.instance, engine.runtime)['valid'])
        engine._invalidate_goal_currentness()
        self.assertFalse(judgment['current'])
        self.assertEqual(engine.instance['goal_status'], 'unsolved')
        self.assertEqual(engine.runtime['status'], 'ready')


if __name__ == '__main__':
    unittest.main(verbosity=2)
