"""Currentness of research state as sources, tasks and knowledge change.

Source replacement, plans citing changed tasks, interrupted work restored for
its review, operational evidence replaced before application, live observation
rules, conversation guards and goal dependencies. A return caused only by
changed premises is refreshed, not repaired. Model answers are fixtures."""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import control, ResearchEngine
from do_math.knowledge import capture_basis, validate_basis
from do_math.observations import ObservationTracker, validate_rules
from do_math.planning import task_ready
from purpose_fixtures import (ActivatedPurposeHarness, common, CURRENTNESS_CONFIG, formal_fixture,
                              PurposeRunner)
from do_math.git_store import ARTIFACT_ROOT
from do_math.repository import new_id
from research_fixtures import (await_control, local_job_runner, observe, producer_result, read_fixture_context,
                               restore_template, send_control, write_checkpoint)


def plan_ready_instance(root, shared, *, config):
    """``restore_template`` build: the synthetic active state driven until a plan heads the queue beside a ready task.

    The drive is ``PurposeRunner``'s preparation and contract review (with any
    model assessment they request). ``_task_readiness`` is process-local, so a
    test calls ``_refresh_readiness()`` on its engine before reading it.
    """
    from state_fixtures import active_instance
    from purpose_fixtures import drive_to
    instance_id = active_instance(root, shared, config=config)
    engine = ResearchEngine(root / 'repository', instance_id, runner=PurposeRunner(), formal_verifier=formal_fixture)
    drive_to(engine, lambda e: e.runtime['queue'] and e.runtime['queue'][0]['role'] == 'research_plan'
             and bool(e._task_readiness) and any(row['state'] == 'ready' for row in e._task_readiness.values()))
    return instance_id


class CurrentnessTests(ActivatedPurposeHarness):
    def make(self, **config):
        return self.make_active(**{**CURRENTNESS_CONFIG, **config})

    def test_same_source_is_idempotent_changed_source_preserves_completed_task_history(self):
        engine, runner = self.make()
        source = self.root / 'source.txt'
        source.write_text('old', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        first = deepcopy(engine.instance['sources'][0])
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        self.assertEqual(first, engine.instance['sources'][0])
        answer = runner.answer
        def reading_source(role, context, workspace):
            output = answer(role, context, workspace)
            if role == 'research_preparation':
                for candidate in output['candidates']:
                    candidate['inputs'].append('source:source.txt')
            return output
        runner.answer = reading_source
        self.drive(engine, predicate=lambda e: any(t['status'] == 'completed' for t in e.runtime['tasks'].values()))
        task = next(iter(engine.runtime['tasks'].values()))
        completed_assessment = deepcopy(task['assessment'])
        from research_fixtures import candidate, contract_review
        from do_math.planning import seal_contract_review
        downstream = {**candidate('Downstream'), 'id': 'TK-downstream', 'status': 'planned', 'revision': 1,
            'results': [], 'reviews': [], 'dependencies': [task['id']], 'occurrence_condition': {'op': 'always'},
            'profile_refs': list(task['profile_refs']), 'authority_refs': list(task['authority_refs'])}
        downstream.pop('revises_task_id')  # A stored task record; the wire candidate's revision link is not stored.
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        downstream['reviews'] = [seal_contract_review(downstream, contract_review({'task': downstream}),
            unfinished_instance, engine.runtime, execution_id='EX-downstream-review')]
        self.assertEqual(task_ready(downstream, unfinished_instance, engine.runtime)['state'], 'ready')
        engine._save()
        source.write_text('new', encoding='utf-8')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        current = engine.runtime['tasks'][task['id']]
        self.assertEqual(current['status'], 'completed')
        self.assertEqual(current['assessment']['decision'], completed_assessment['decision'])
        self.assertEqual(current['assessment']['item_dispositions'], completed_assessment['item_dispositions'])
        self.assertFalse(current['assessment']['current'])
        self.assertIn('source content changed', current['assessment']['invalidated_reason'].lower())
        self.assertEqual(engine.instance['sources'][0]['revision'], 2)
        unfinished_instance = deepcopy(engine.instance)
        unfinished_instance['goal_status'] = 'unsolved'
        readiness = task_ready(downstream, unfinished_instance, engine.runtime)
        self.assertEqual(readiness['state'], 'not_ready')
        self.assertIn('blocked dependencies', readiness['errors'][0])
        self.assertFalse(any(error.startswith(task['id'] + ':') for error in engine.check()['errors']))

    def test_graceful_output_on_changed_source_is_preserved_but_not_accepted(self):
        engine, _ = self.make(max_output_repairs=0)
        source = self.root / 'basis.txt'; source.write_text('old')
        control(self.repo, engine.instance['id'], 'source', config={'path': str(source)})
        engine.process_controls()
        class ChangingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                source.write_text('new')
                await_control(engine, control(self.repo, engine.instance['id'], 'source', config={'path': str(source)}))
                (kwargs['workspace'] / 'partial.txt').write_text('The old input was read.')
                return producer_result({'status': 'completed', 'output': {**common('Old-source response'),
                    'used_sources': ['basis.txt'], 'candidates': []}, 'usage': {}}, kwargs)
        engine.runner = ChangingRunner()
        engine.run(max_steps=1)
        execution = next(row for row in engine.runtime['executions'].values()
                         if row['role'] == 'research_preparation')
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['error_kind'], 'currentness_changed')
        issues = execution['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and 'source' in row['message']
                            for row in issues), issues)
        self.assertEqual(engine.runtime['cycles'], 0)
        # With no output repair allowed, the changed premise is still refreshed once.
        refreshed = [a for a in engine.runtime['queue'] if a.get('refresh', {}).get('execution_id') == execution['id']]
        self.assertEqual(len(refreshed), 1)
        self.assertNotIn('repair', refreshed[0])
        self.assertNotIn(execution['action']['id'], engine.runtime.get('waiting_actions', {}))
        entry = next(f for f in execution['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual(engine.store.read(entry['artifact_ref']), b'The old input was read.')

    def _plan_citing_task_while(self, change):
        self.root, instance_id = restore_template(plan_ready_instance, config=CURRENTNESS_CONFIG)
        engine, runner = self._engine(instance_id, PurposeRunner())
        engine._refresh_readiness()
        self.assertEqual(engine.runtime['queue'][0]['role'], 'research_plan')
        task_id = next(tid for tid, row in engine._task_readiness.items() if row['state'] == 'ready')
        answer = runner.answer
        def citing_answer(role, context, workspace):
            output = answer(role, context, workspace)
            if role == 'research_plan':
                output['used_sources'] = [*output.get('used_sources', []), task_id]
            return output
        runner.answer = citing_answer
        # The concurrent change is an owner-published state change made after the
        # plan's input was fixed and before its submission is received. Applying it
        # on the owner thread keeps the test free of a worker/owner race.
        receive = engine._receive_submission
        def changed_then_received(action, *args, **kwargs):
            if action['role'] == 'research_plan':
                change(engine.runtime['tasks'][task_id])
                engine._save()
            return receive(action, *args, **kwargs)
        with patch.object(engine, '_receive_submission', changed_then_received):
            engine.run(max_steps=1)
        return engine, task_id, next(e for e in reversed(list(engine.runtime['executions'].values())) if e['role'] == 'research_plan')

    def test_cited_task_lifecycle_change_during_plan_does_not_reject_the_plan(self):
        engine, task_id, plan = self._plan_citing_task_while(
            lambda task: task.update(deferred_reason='Concurrent planner note', reviews=[*task['reviews'], {'note': 'concurrent'}]))
        self.assertEqual(plan['outcome'], 'output_accepted', plan.get('error'))
        sealed = json.loads(engine.store.read(plan['submission_intent']['output_ref']))
        self.assertIn(task_id, sealed['used_sources'])
        self.assertEqual(plan['integration_result']['status'], 'accepted')
        self.assertEqual(engine.runtime['tasks'][task_id]['status'], 'active')
        self.assertTrue(any(a['role'] == 'research_work' and a.get('target') == task_id for a in engine.runtime['queue']))

    def test_cited_task_contract_change_during_plan_rejects_the_plan(self):
        engine, task_id, plan = self._plan_citing_task_while(lambda task: task.update(scope={**task['scope'], 'included': [*task['scope']['included'], 'A revised domain']}))
        self.assertEqual(plan['outcome'], 'execution_incomplete')
        self.assertEqual(plan['error_kind'], 'currentness_changed')
        issues = plan['integration_result']['issues']
        self.assertTrue(any(row['rule_id'] == 'integration.currentness' and
            task_id in row['message'] and 'contract_sha256' in row['message'] for row in issues), issues)
        self.assertFalse(any(a['role'] == 'research_work' and a.get('target') == task_id
                             for a in engine.runtime['queue']))

    def test_failed_execution_materials_are_restored_for_its_operational_review(self):
        engine, _ = self.make()
        class FailingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                (kwargs['workspace'] / 'partial.txt').write_text('Reusable partial result.', encoding='utf-8')
                checkpoint = {'current_claim': 'A partial lemma is established.',
                    'evidence_paths': ['partial.txt'], 'attempts': ['Checked the bounded case.'],
                    'remaining_work': ['Prove the general case.'], 'next_step': 'Resume from the partial lemma.',
                    'progress_state': 'blocked'}
                (kwargs['workspace'] / 'checkpoint.json').write_text(json.dumps(checkpoint), encoding='utf-8')
                return producer_result({'status': 'failed', 'output': None, 'usage': {}, 'error': 'fixture interruption'}, kwargs)
        engine.runner = FailingRunner()
        engine.run(max_steps=1)
        execution = next(value for value in engine.runtime['executions'].values()
                         if value['role'] == 'research_preparation')
        review = next(action for action in engine.runtime['queue'] if action['role'] == 'operational_review')
        review_workspace = self.root / 'operational-review-preview'; review_workspace.mkdir()
        context = engine._context(review, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['execution_id'], execution['id'])
        self.assertEqual((recovery['result_kind'], recovery['final_result_status']),
                         ('execution_result', 'available'))
        self.assertEqual(recovery['checkpoint'], context['operational_evidence']['checkpoint'])
        self.assertEqual(recovery['checkpoint']['sha256'], engine.runtime['checkpoints'][execution['id']]['sha256'])
        self.assertNotIn('checkpoint', recovery['checkpoint'])
        for source in [recovery['result_source'], recovery['checkpoint_source'], *recovery['output_files']]:
            raw = (review_workspace / source['local_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
            self.assertEqual(len(raw), source['bytes'])
            self.assertEqual(engine.store.read(source['artifact_ref'], source['snapshot']), raw)
        restored = next(f for f in recovery['output_files'] if f['path'] == 'partial.txt')
        self.assertEqual((review_workspace / restored['local_path']).read_bytes(), b'Reusable partial result.')

        activity_result = b'{"report":"A separately preserved activity result."}'
        activity_ref = 'runtime/artifacts/BA-activity-result/diagnostic.json'
        engine.runtime['executions'][execution['id']]['result_ref'] = activity_ref
        engine._save({activity_ref: activity_result})
        other_workspace = self.root / 'activity-result-review'
        other = engine._context(review, other_workspace)['recovery_materials']
        self.assertEqual((other_workspace / other['result_source']['local_path']).read_bytes(), activity_result)
        self.assertNotEqual(other['result_source']['local_path'], other['checkpoint_source']['local_path'])

    def _review_after_checkpoint_replacement(self, disposition):
        """Run an operational review of a failed attempt whose checkpoint is replaced after the review input.

        ``disposition(failed_id, cited_checkpoint_ref)`` is the reviewer's answer.
        Returns the engine, the reviewed execution ID, the cited reference and the review execution.
        """
        engine, _ = self.make()
        class FailingRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                (kwargs['workspace'] / 'checkpoint.json').write_text(json.dumps({
                    'current_claim': 'A partial lemma is established.', 'evidence_paths': [],
                    'attempts': ['Checked the bounded case.'], 'remaining_work': ['Prove the general case.'],
                    'next_step': 'Resume from the partial lemma.', 'progress_state': 'blocked'}), encoding='utf-8')
                return producer_result({'status': 'failed', 'output': None, 'usage': {}, 'error': 'fixture interruption'}, kwargs)
        engine.runner = FailingRunner()
        engine.run(max_steps=1)
        failed = next(e['id'] for e in engine.runtime['executions'].values() if e['role'] == 'research_preparation')
        cited = engine.runtime['checkpoints'][failed]['artifact_ref']
        class ReviewRunner:
            @local_job_runner
            def run(inner, **kwargs):
                kwargs['on_started']({'fixture': True})
                context = read_fixture_context(kwargs['prompt'], kwargs['workspace'])
                if cited not in context['admissible_basis_refs']:
                    raise AssertionError('The fixture must cite a checkpoint that its input admitted')
                output = {**common('The failed attempt kept a reusable checkpoint'),
                          'disposition': disposition(failed, cited)}
                return producer_result({'status': 'completed', 'output': output, 'usage': {}}, kwargs)
        engine.runner = ReviewRunner()
        receive = engine._receive_submission
        def checkpoint_replaced_then_received(action, *args, **kwargs):
            # The target's newest checkpoint changes after the review input was fixed.
            if action['role'] == 'operational_review':
                checkpoint = engine.runtime['checkpoints'][failed]
                replacement = ARTIFACT_ROOT + new_id('BA') + '/checkpoint.json'
                raw = engine.store.read(checkpoint['artifact_ref'], engine.head)
                engine.runtime['checkpoints'][failed] = {**checkpoint, 'artifact_ref': replacement}
                engine._save({replacement: raw})
            return receive(action, *args, **kwargs)
        with patch.object(engine, '_receive_submission', checkpoint_replaced_then_received):
            engine.run(max_steps=1)
        review = next(e for e in engine.runtime['executions'].values() if e['role'] == 'operational_review')
        return engine, failed, cited, review

    def test_operational_basis_replaced_after_input_is_refreshed_without_output_repair(self):
        engine, failed, cited, review = self._review_after_checkpoint_replacement(lambda target, checkpoint: {
            'kind': 'continue', 'basis_refs': [target, checkpoint], 'next_owner': 'engine',
            'reason': 'The preserved checkpoint records the partial lemma.', 'next_review': None})
        self.assertEqual(review['error_kind'], 'currentness_changed', review.get('integration_result'))
        self.assertTrue(any(cited in change['reason'] and 'admissible at input' in change['reason']
                            for change in review['currentness_changes']), review['currentness_changes'])
        followups = [a for a in engine.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed]
        self.assertEqual([a.get('refresh', {}).get('execution_id') for a in followups], [review['id']])
        self.assertNotIn('repair', followups[0], 'A changed premise does not spend an output repair')
        self.assertNotIn(review['action']['id'], engine.runtime.get('waiting_actions', {}))

    def test_replaced_operational_basis_with_another_application_error_stays_a_producer_repair(self):
        engine, failed, cited, review = self._review_after_checkpoint_replacement(lambda target, checkpoint: {
            'kind': 'repair', 'basis_refs': [target, checkpoint], 'next_owner': 'installation_recovery',
            'reason': 'The receiver rejected the preserved checkpoint.', 'repair_target': 'installation:missing.py',
            'meaning_preserving': True, 'verification': 'Rerun the receiver on the preserved checkpoint.'})
        self.assertEqual(review['error_kind'], 'output_contract', review.get('integration_result'))
        self.assertTrue(any('installation repair target' in row['message']
                            for row in review['integration_result']['issues']), review['integration_result'])
        followups = [a for a in engine.runtime['queue'] if a['role'] == 'operational_review' and a.get('target') == failed]
        self.assertEqual([a.get('repair', {}).get('execution_id') for a in followups], [review['id']])
        self.assertNotIn('refresh', followups[0])

    def test_recovery_captures_parent_and_inline_child_without_losing_action(self):
        engine, _ = self.make()
        action = {'id': 'AC-fixture', 'role': 'research_preparation'}
        for eid, parent in [('EX-parent', None), ('EX-inline', 'EX-parent')]:
            attempt_action = action if parent is None else {'id': 'AC-inline', 'role': 'operational_review', 'target': parent}
            execution = engine._register_execution(attempt_action, {'id': eid, 'role': attempt_action['role'],
                'status': 'running', 'input_snapshot': engine.head, 'input_manifest': [], 'parent_execution_id': parent})
            from research_fixtures import dispatched_launch
            profile = engine.instance['execution_profiles'][execution['execution_profile_ref']['id']]
            execution['launch_ticket'] = dispatched_launch(eid, profile)
            # An admitted launch: its capacity holds the started Job's identity.
            execution['capacity'] = {'reservation_ids': [], 'provider': profile['ai']['provider'],
                'process': {'job_name': execution['launch_ticket']['job_name']}, 'local_termination': 'unknown'}
            folder = Path(engine.instance['workspace'])/'runs'/eid/'workspace'; folder.mkdir(parents=True)
            (folder/'partial.txt').write_text(eid)
        engine.runtime.update(status='running', queue=[action])
        engine._save()
        # No process was started in this fixture. Its termination observation
        # is explicit; unknown real processes must remain unreleased.
        with patch('do_math.windows_job.named_job_empty', return_value=True), \
                patch('do_math.windows_job.owner_ended', return_value=True), engine.store.writer_lock():
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
        review_workspace = self.root / 'disappeared-review-preview'; review_workspace.mkdir()
        context = engine._context({'role': 'operational_review', 'target': 'EX-parent'}, review_workspace)
        recovery = context['recovery_materials']
        self.assertEqual(recovery['result_kind'], 'checkpoint_recovery')
        self.assertEqual(recovery['final_result_status'], 'not_produced')
        self.assertEqual(recovery['result_source'], recovery['checkpoint_source'])
        self.assertTrue((review_workspace / recovery['result_source']['local_path']).is_file())

    def test_live_rules_repeat_exact_thresholds_and_preserve_last_valid_update(self):
        folder = Path(self.enterContext(tempfile.TemporaryDirectory())) / 'observed'; folder.mkdir()
        clock = [0]
        rules = [{'id': 'steps', 'operator': 'counter_gte', 'subject': {'kind': 'counter', 'id': 'attempts'},
                  'basis': {'source': 'checkpoint', 'unit': 'count'}, 'threshold': 2,
                  'repeat_interval': 2, 'required_evidence': ['EV-iteration']}]
        tracker = ObservationTracker('EX', folder, {
            'observation_rules': rules, 'self_check_response_window_seconds': 60}, clock=lambda: clock[0])
        write_checkpoint(folder, counters={'attempts': 2})
        first = next(row for row in observe(tracker, {'type': 'tick'})
                     if row['kind'] == 'self_check_due')
        self.assertEqual(first['due'][0]['boundary'], 2)
        write_checkpoint(folder, counters={'attempts': 2}, claim='same count')
        self.assertFalse(any(row['kind'] == 'self_check_due' for row in observe(tracker, {'type': 'tick'})))
        (folder / 'observation-rules.json').write_text('{')
        write_checkpoint(folder, counters={'attempts': 4})
        events = observe(tracker, {'type': 'tick'})
        second = next(row for row in events if row['kind'] == 'self_check_due')
        self.assertEqual(second['due'][0]['boundary'], 4)
        self.assertTrue(any(row['kind'] == 'observation_rules_rejected' for row in events))
        self.assertEqual(tracker.rules, rules)
        with self.assertRaises(ValueError):
            validate_rules([{**rules[0], 'threshold': True}])


class SolvedStateCurrentnessTests(ActivatedPurposeHarness):
    """Both start from copies of templates: the public activation, and the real solution after it."""

    def test_live_conversation_guard_expires_without_new_scheduler_activity(self):
        from datetime import datetime
        from do_math.repository import new_id
        from do_math.file_io import now
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
        from purpose_fixtures import solved_instance
        # The public activation driven to mathematically_solved, built once per process.
        self.root, solved = restore_template(solved_instance, criteria=None)
        engine, _ = self._engine(solved['instance_id'], PurposeRunner())
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


class OperationalBasisPremiseTests(unittest.TestCase):
    def test_only_evidence_admitted_at_input_can_become_a_changed_premise(self):
        from do_math.operational_dispositions import basis_premise_changes
        at_input, current = ['EX-target', 'BA-old'], ['EX-target', 'BA-new']
        changed = basis_premise_changes({'basis_refs': ['EX-target', 'BA-old']}, at_input, current)
        self.assertEqual([row['id'] for row in changed], ['BA-old'])
        self.assertEqual(basis_premise_changes({'basis_refs': ['BA-old', 'OF-never-supplied']}, at_input, current), [],
                         'A citation outside the input stays a producer error')
        self.assertEqual(basis_premise_changes({'basis_refs': ['EX-target']}, at_input, current), [])


class CurrentnessReturnRoutingTests(unittest.TestCase):
    def test_currentness_return_beside_an_accepted_bundle_is_refreshed_not_repaired(self):
        # A split response can accept one bundle while another returns on changed premises. The
        # result status is then 'partial', exactly as when nothing was accepted, so the receiver
        # routes by the returned issues (integration.failure_kind), never by that status.
        import uuid
        from unittest.mock import create_autospec
        from do_math import integration, submission
        from do_math.repository import ResearchRepository
        from engine_fixtures import routing_engine
        from research_fixtures import sealed_maintenance_submission
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            intent, artifacts = sealed_maintenance_submission(workspace, 'EX-work')
            prefix = intent['output_ref'].removesuffix('output.json')
            intent.update(extensions_ref=prefix + 'extensions.json', check_ref=prefix + 'check.json')
            engine = routing_engine()
            engine.store = create_autospec(ResearchRepository, instance=True)
            engine.store.read.side_effect = lambda path, head: artifacts[path]
            engine.store.git_dir = 'git-' + uuid.uuid4().hex
            engine.head = 'fixture-snapshot'
            context = submission.load_json((workspace / 'input/submission/context.json').read_bytes())
            receipt_artifacts = [{'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                                 for path, raw in artifacts.items()]
            action = context['action']
            engine.runtime['executions']['EX-work'] = {'id': 'EX-work', 'role': action['role'], 'action': action,
                'status': 'stopping', 'submission_intent': intent,
                'submission_receipt': {'kind': 'submit_intent', 'state': 'accepted', 'execution_id': 'EX-work',
                                       'payload': {'submission_check': {'artifacts': receipt_artifacts}}}}
            stale = integration.issue('integration.currentness', 'output/integration_bundles',
                                      'a source changed after the input was fixed', 'IN-two')
            engine._apply_submission_bundles = create_autospec(engine._apply_submission_bundles, return_value={
                'status': 'partial', 'retry_bundle_ids': ['IN-two'], 'issues': [stale], 'bundles': [
                    {'integration_id': 'IN-one', 'status': 'accepted', 'issues': []},
                    {'integration_id': 'IN-two', 'status': 'returned', 'issues': [stale], 'next_owner': 'producer'}]})
            engine._record_task_receipt = create_autospec(engine._record_task_receipt)
            engine._receive_submission(action, {}, 'EX-work', context, engine._response_schema(action), workspace)
        execution = engine.runtime['executions']['EX-work']
        self.assertEqual(execution['error_kind'], 'currentness_changed')
        self.assertEqual([row['integration_id'] for row in execution['currentness_changes']], ['IN-two'])
        refreshed, = engine.runtime['queue']
        self.assertEqual(refreshed['refresh']['execution_id'], 'EX-work')
        self.assertNotIn('repair', refreshed)
        self.assertNotIn(action['id'], engine.runtime.get('waiting_actions', {}))
        # The refresh records this execution's outcome once; the ordinary receipt is not recorded again.
        engine._record_task_receipt.assert_not_called()


if __name__ == '__main__': unittest.main()
