"""Reject unsupported editions unchanged; retain currentness and conversation guards."""
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.knowledge import capture_basis, validate_basis
from do_math.engine import ResearchEngine
from test_purpose_engine import ActivatedPurposeHarness, PurposeRunner
from research_fixtures import send_control, restore_template


class CurrentnessTests(ActivatedPurposeHarness):
    """Both start from copies of templates: the public activation, and the real solution after it."""

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
        from test_academic_engine import solved_instance
        # PurposeHarness.make and drive to mathematically_solved, built once per process.
        self.root, instance_id = restore_template(solved_instance, criteria=None)
        engine, _ = self._engine(instance_id, PurposeRunner())
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
