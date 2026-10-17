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
from support.engine_context import assert_operational_documents, assert_operational_damage_rejected
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
    def test_normal_formal_completion_has_null_checkpoint_and_reports_unrestorable_sources(self):
        """Real repository reads and _context distinguish normal, missing, hash and size branches."""
        import tempfile
        from support.engine_context import context_engine, package
        result = b'{"status":"completed"}'
        output = b'checked output bytes'
        for fault in ('normal', 'normal_inline', 'missing_checkpoint', 'missing_result', 'output_hash', 'output_size', 'missing_output'):
            prefix = 'runtime/artifacts/BA-formal-diagnostic-' + fault + '/'
            files = {prefix + 'result.json': result, prefix + 'proof.txt': output}
            if fault == 'missing_result':
                del files[prefix + 'result.json']
            if fault == 'missing_output':
                del files[prefix + 'proof.txt']
            engine = context_engine(files=files)
            source = {'path': 'proof.txt', 'artifact_ref': prefix + 'proof.txt',
                      'sha256': hashlib.sha256(output).hexdigest(), 'bytes': len(output)}
            if fault == 'output_hash':
                source['sha256'] = '0' * 64
            if fault == 'output_size':
                source['bytes'] += 1
            role = 'research_preparation' if fault == 'missing_checkpoint' else 'formal_check'
            engine.runtime['executions']['EX-formal-diagnostic'] = {
                'id': 'EX-formal-diagnostic', 'role': role, 'status': 'ended',
                'action': {'role': role}, 'artifact_bundle': 'BA-formal-diagnostic-' + fault,
                'result_ref': prefix + 'result.json', 'output_files': [source]}
            if fault == 'normal_inline':
                engine.runtime['executions']['EX-parent'] = {
                    'id': 'EX-parent', 'role': 'formal_check', 'status': 'ended'}
                engine.runtime['executions']['EX-formal-diagnostic']['continuation_of'] = 'EX-parent'
                engine.runtime['executions']['EX-formal-diagnostic']['action']['continuation_of'] = 'EX-parent'
            with tempfile.TemporaryDirectory() as directory, self.subTest(fault=fault):
                root = Path(directory)
                context = engine._context({'role': 'operational_review', 'target': 'EX-formal-diagnostic'}, root)
                recovery = context['recovery_materials']
                if fault != 'missing_checkpoint':
                    self.assertIsNone(recovery['checkpoint_source'])
                self.assertEqual((recovery['result_kind'], recovery['final_result_status']),
                                 ('execution_result', 'available'))
                assert_operational_documents(self, context, root, engine, owner='recovery_materials')
                assert_operational_documents(self, context, root, engine, owner='operational_evidence')
                row = (recovery['result_source'] if fault == 'missing_result' else
                       recovery['checkpoint_source'] if fault == 'missing_checkpoint' else recovery['output_files'][0])
                if fault in ('normal', 'normal_inline'):
                    self.assertNotIn('restoration_error', row)
                    self.assertEqual((root / row['local_path']).read_bytes(), output)
                    assert_operational_damage_rejected(self, context, root, engine, owner='recovery_materials')
                else:
                    self.assertNotIn('local_path', row)
                    error = row['restoration_error']
                    self.assertEqual(row['snapshot'], engine.head)
                    if fault in ('output_hash', 'output_size'):
                        self.assertEqual(error['error_type'], 'ValueError')
                        reason = ('operational review artifact hash changed: ' + source['artifact_ref']
                                  if fault == 'output_hash' else 'operational review artifact size changed')
                        self.assertEqual(error['reason'], reason)
                        self.assertEqual((error['observed_sha256'], error['observed_bytes']),
                                         (hashlib.sha256(output).hexdigest(), len(output)))
                        self.assertEqual((row['sha256'], row['bytes']), (source['sha256'], source['bytes']))
                    else:
                        self.assertEqual((error['observed_sha256'], error['observed_bytes']), (None, None))
                        self.assertIn(row['artifact_ref'], error['reason'])
                    # Diagnostic coordinates remain readable, unverifiable bytes do not.
                    self.assertFalse((root / 'input/operational-review/EX-formal-diagnostic' /
                                      ('result.json' if fault == 'missing_result' else
                                       'checkpoint-recovery.json' if fault == 'missing_checkpoint' else 'files/proof.txt')).exists())
                    damaged = deepcopy(context)
                    bad = (damaged['recovery_materials']['result_source'] if fault == 'missing_result' else
                           damaged['recovery_materials']['checkpoint_source'] if fault == 'missing_checkpoint' else
                           damaged['recovery_materials']['output_files'][0])
                    bad['local_path'] = 'input/unchecked-bytes.txt'
                    with self.assertRaisesRegex(AssertionError, r"^'local_path' unexpectedly found in "):
                        assert_operational_documents(self, damaged, root, engine, owner='recovery_materials')
                fitted_root = root / 'packaged'
                fitted, _ = package(engine, fitted_root, role='operational_review', target='EX-formal-diagnostic')
                assert_operational_documents(self, fitted['context'], fitted_root, engine, owner='recovery_materials')

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
        assert_operational_documents(self, context, review_workspace, engine, owner='recovery_materials')
        assert_operational_documents(self, context, review_workspace, engine, owner='operational_evidence')
        assert_operational_damage_rejected(self, context, review_workspace, engine, owner='recovery_materials')
        assert_operational_damage_rejected(self, context, review_workspace, engine, owner='operational_evidence')
        # The same execution's genuine continuation source has a different owner/path.
        from do_math.context_store import restore_continuation
        resumed = restore_continuation(engine.runtime, {**execution['action'], 'continuation_of': execution['id']},
            review_workspace, snapshot=engine.head, read_artifact=lambda path: engine.store.read(path, engine.head))
        swapped = deepcopy(context)
        swapped['recovery_materials']['result_source'] = resumed['continuation_history'][-1]['result_source']
        # The sealed source is identical; only the continuation's local owner differs.
        continuation_source = swapped['recovery_materials']['result_source']
        self.assertEqual({key: value for key, value in continuation_source.items() if key != 'local_path'},
                         {key: value for key, value in recovery['result_source'].items() if key != 'local_path'})
        self.assertTrue(continuation_source['local_path'].startswith('input/resume-history/'))
        with self.assertRaises(AssertionError) as rejected_continuation:
            assert_operational_documents(self, swapped, review_workspace, engine, owner='recovery_materials')
        self.assertEqual(rejected_continuation.exception.args, ('False is not true',))
        swapped = deepcopy(context)
        swapped['recovery_materials']['result_source'] = context['operational_evidence']['checkpoint_source']
        with self.assertRaises(AssertionError) as rejected_checkpoint:
            assert_operational_documents(self, swapped, review_workspace, engine, owner='recovery_materials')
        self.assertIn('\n- ' + context['operational_evidence']['checkpoint_source']['artifact_ref'] + '\n',
                      str(rejected_checkpoint.exception))
        self.assertIn('\n+ ' + execution['result_ref'], str(rejected_checkpoint.exception))
        activity_result = b'{"report":"A separately preserved activity result."}'
        activity_ref = 'runtime/artifacts/BA-activity-result/diagnostic.json'
        engine.runtime['executions'][execution['id']]['result_ref'] = activity_ref
        engine._save({activity_ref: activity_result})
        other_workspace = sim.root / 'activity-result-review'
        other_context = engine._context(review, other_workspace)
        other = other_context['recovery_materials']
        self.assertEqual((other_workspace / other['result_source']['local_path']).read_bytes(), activity_result)
        self.assertNotEqual(other['result_source']['local_path'], other['checkpoint_source']['local_path'])
        self.assertEqual(other['result_kind'], 'activity_result')
        assert_operational_documents(self, other_context, other_workspace, engine, owner='recovery_materials')

    def test_recovery_captures_parent_and_inline_child_without_losing_action(self):
        sim = Sim.activated()
        engine = sim.engine
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        for eid, parent in [('EX-parent', None), ('EX-inline', 'EX-parent')]:
            attempt_action = action if parent is None else {'id': 'AC-inline', 'role': 'operational_review', 'target': parent}
            execution = engine._register_execution(attempt_action, {'id': eid, 'role': attempt_action['role'],
                'status': 'running', 'input_snapshot': engine.head, 'input_manifest': []})
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
            self.assertEqual(execution['action']['role'], 'research_preparation' if eid == 'EX-parent' else 'operational_review')
            if eid == 'EX-inline':
                self.assertEqual(execution['action']['target'], 'EX-parent')
            self.assertEqual(engine.store.read(execution['output_files'][0]['artifact_ref']), eid.encode())
            self.assertEqual(engine.store.load()[2]['executions'][eid], execution)
        review_workspace = sim.root / 'disappeared-review-preview'
        review_workspace.mkdir()
        context = engine._context({'role': 'operational_review', 'target': 'EX-parent'}, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['result_kind'], 'checkpoint_recovery')
        self.assertEqual(recovery['final_result_status'], 'not_produced')
        self.assertEqual(recovery['result_source'], recovery['checkpoint_source'])
        self.assertTrue((review_workspace / recovery['result_source']['local_path']).is_file())
        assert_operational_documents(self, context, review_workspace, engine, owner='recovery_materials')
        assert_operational_damage_rejected(self, context, review_workspace, engine, owner='recovery_materials')


if __name__ == '__main__':
    unittest.main()
