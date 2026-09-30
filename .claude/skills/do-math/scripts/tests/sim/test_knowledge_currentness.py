"""Currentness of research state on the Sim (설계 4.1): conversation guards, goal dependencies and recovery materials.

Every test starts from a restored template and runs the product's engine on
the port fakes; nothing is replaced. Time moves on the Sim clock.

- A conversation lease expires by moving the Sim clock past it (the legacy test
  replaced the engine's lifecycle clocks).
- The goal judgment is the one the engine's receiver recorded for satisfied
  goal audits of a reviewed theorem (``engine_lifecycle.solve_goal`` on
  ``review_sim.reviewed_sim``), instead of the legacy ``solved_instance``
  template the purpose runner drove to a solution.
- A failed attempt is a provider call the CLI double interrupts after writing
  partial files and a checkpoint (``knowledge_currentness.interrupt``); the
  legacy ``FailingRunner`` returned ``failed`` from a real Job.
- Disappeared executions are recovered with launch tickets the Jobs port fake
  issued; their owner ended because the fake's owner process now has another
  creation time under the same process ID (the legacy test patched
  ``windows_job.named_job_empty`` and ``owner_ended``).
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from do_math.knowledge import capture_basis, validate_basis
from do_math.knowledge_io import import_candidate
from do_math.launch import ticket
from do_math.state_contract import default_state_contract, validate_record
from support.engine_lifecycle import applied, solve_goal
from support.knowledge_currentness import currentness_model
from support.review_sim import reviewed_sim as reviewed_theorem_sim, theorem_id, warm_reviewed
from support.sim import Sim, warm_template

PARTIAL = b'Reusable partial result.'
CHECKPOINT = {'current_claim': 'A partial lemma is established.', 'evidence_paths': ['partial.txt'],
              'attempts': ['Checked the bounded case.'], 'remaining_work': ['Prove the general case.'],
              'next_step': 'Resume from the partial lemma.', 'progress_state': 'blocked'}


def setUpModule():
    warm_template()
    warm_reviewed()


def interrupted_preparation(context, workspace):
    (workspace / 'partial.txt').write_bytes(PARTIAL)
    (workspace / 'checkpoint.json').write_text(json.dumps(CHECKPOINT), encoding='utf-8')


class ConversationGuardTests(unittest.TestCase):
    def test_live_conversation_guard_expires_without_new_scheduler_activity(self):
        sim = Sim.activated()
        applied(sim, 'conversation', config={'operation': 'attach', 'id': 'C', 'generation': 1,
                                             'lease_seconds': 3600, 'disconnect_policy': 'pause'})
        engine = sim.engine
        action = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
        execution = engine._register_execution(action, {'id': sim.ports.clock.new_id('EX'), 'role': action['role'],
            'status': 'running', 'created_at': sim.ports.clock.now(), 'input_snapshot': engine.head})
        before = deepcopy(engine.runtime['conversations']['C'])
        # No owner activity: only the clock passes the lease.
        sim.advance(3600 + 1)
        self.assertTrue(engine._check_conversations())
        self.assertEqual(engine.runtime['status'], 'paused')
        self.assertEqual(engine.runtime['executions'][execution['id']]['stop_requested'], 'conversation_lost')
        self.assertEqual(engine.runtime['conversations']['C']['last_heartbeat_at'], before['last_heartbeat_at'])
        self.assertFalse(engine._check_conversations())
        self.assertEqual(len([e for e in engine.runtime['events'] if e['kind'] == 'conversation_lost']), 1)


class GoalDependencyTests(unittest.TestCase):
    def test_goal_dependency_detects_changed_relation_endpoint_even_when_proof_record_is_unchanged(self):
        sim = reviewed_theorem_sim()
        engine = sim.engine
        proof_id = theorem_id(sim)
        solve_goal(engine, proof_id)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        endpoint_ids = []
        for label in ('left endpoint', 'right endpoint'):
            engine.instance, engine.runtime, endpoint_id = import_candidate(engine.instance, engine.runtime, {
                'kind': 'question', 'title': label, 'statement': 'Natural zero identity',
                'explanation': 'Specify the exact natural-number endpoint', 'summary': label, 'lean_code': '',
                'declaration_names': [], 'dependencies': []},
                source_ref=engine.instance['id'], actor_ref=engine.instance['id'], clock=sim.ports.clock)
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
        # The invalidated judgment is still a record the storage contract accepts.
        validate_record(default_state_contract().family('research', 'goal_judgments').checker,
                        judgment, 'goal_judgments')
        self.assertEqual(engine.instance['goal_status'], 'unsolved')
        self.assertEqual(engine.runtime['status'], 'ready')


class RecoveryMaterialTests(unittest.TestCase):
    def test_failed_execution_materials_are_restored_for_its_operational_review(self):
        sim = Sim.activated()
        currentness_model(sim).interrupt('research_preparation', interrupted_preparation)
        sim.step()
        engine = sim.engine
        execution = next(value for value in engine.runtime['executions'].values()
                         if value['role'] == 'research_preparation')
        self.assertEqual((execution['outcome'], execution['error_kind']), ('execution_incomplete', 'execution_failure'))
        review = next(action for action in engine.runtime['queue'] if action['role'] == 'operational_review')
        review_workspace = sim.root / 'operational-review-preview'
        review_workspace.mkdir()
        context = engine._context(review, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['execution_id'], execution['id'])
        self.assertEqual((recovery['result_kind'], recovery['final_result_status']), ('execution_result', 'available'))
        self.assertEqual(recovery['checkpoint'], context['operational_evidence']['checkpoint'])
        self.assertEqual(recovery['checkpoint']['sha256'], engine.runtime['checkpoints'][execution['id']]['sha256'])
        self.assertNotIn('checkpoint', recovery['checkpoint'])
        for source in [recovery['result_source'], recovery['checkpoint_source'], *recovery['output_files']]:
            raw = (review_workspace / source['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
            self.assertEqual(len(raw), source['bytes'])
            self.assertEqual(engine.store.read(source['artifact_ref'], source['snapshot']), raw)
        restored = next(f for f in recovery['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual((review_workspace / restored['local_path']).read_bytes(), PARTIAL)
        activity_result = b'{"report":"A separately preserved activity result."}'
        activity_ref = 'runtime/artifacts/BA-activity-result/diagnostic.json'
        engine.runtime['executions'][execution['id']]['result_ref'] = activity_ref
        engine._save({activity_ref: activity_result})
        other_workspace = sim.root / 'activity-result-review'
        other = engine._context(review, other_workspace)['recovery_materials']
        self.assertEqual((other_workspace / other['result_source']['local_path']).read_bytes(), activity_result)
        self.assertNotEqual(other['result_source']['local_path'], other['checkpoint_source']['local_path'])

    def test_recovery_captures_parent_and_inline_child_without_losing_action(self):
        sim = Sim.activated()
        engine = sim.engine
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        for eid, parent in [('EX-parent', None), ('EX-inline', 'EX-parent')]:
            attempt_action = action if parent is None else {'id': 'AC-inline', 'role': 'operational_review', 'target': parent}
            execution = engine._register_execution(attempt_action, {'id': eid, 'role': attempt_action['role'],
                'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': parent})
            profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
            execution['launch_ticket'] = {**ticket(eid, profile, jobs=sim.ports.jobs, clock=sim.clock), 'phase': 'dispatched'}
            # An admitted launch: its capacity holds the started Job's identity.
            execution['capacity'] = {'reservation_ids': [], 'provider': profile['ai']['provider'],
                'process': {'job_name': execution['launch_ticket']['job_name']}, 'local_termination': 'unknown'}
            folder = Path(engine.instance['workspace']) / 'runs' / eid / 'workspace'
            folder.mkdir(parents=True)
            (folder / 'partial.txt').write_text(eid)
        engine.runtime.update(status='running', queue=[action])
        engine._save()
        # No process was started: the launch owner has ended (a new process holds its process ID) and
        # no Job of either name exists. Unknown real processes must remain unreleased.
        sim.jobs.owner = {**sim.jobs.owner, 'creation_filetime': str(int(sim.jobs.owner['creation_filetime']) + 1)}
        with engine.store.writer_lock():
            engine._recover_disappeared()
        self.assertFalse([e['id'] for e in engine.runtime['executions'].values() if e['status'] != 'ended'])
        self.assertTrue(engine.runtime['recoveries'])
        self.assertEqual(engine.runtime['waiting_actions']['AC-fixture']['execution_id'], 'EX-parent')
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == 'EX-parent'
                            for a in engine.runtime['queue']))
        for eid in ('EX-parent', 'EX-inline'):
            execution = engine.runtime['executions'][eid]
            self.assertEqual(execution['status'], 'ended')
            self.assertEqual(engine.store.read(execution['output_files'][0]['artifact_ref']), eid.encode())
        review_workspace = sim.root / 'disappeared-review-preview'
        review_workspace.mkdir()
        context = engine._context({'role': 'operational_review', 'target': 'EX-parent'}, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['result_kind'], 'checkpoint_recovery')
        self.assertEqual(recovery['final_result_status'], 'not_produced')
        self.assertEqual(recovery['result_source'], recovery['checkpoint_source'])
        self.assertTrue((review_workspace / recovery['result_source']['local_path']).is_file())


if __name__ == '__main__':
    unittest.main()
