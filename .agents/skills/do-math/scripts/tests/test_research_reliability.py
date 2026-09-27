"""Historical failure shapes, rebuilt with current contracts and no live research."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group
from do_math import contracts, task_scope
from do_math.model_runner import CodexModelRunner
from test_model_runner import Adapter
from test_static_review_repairs import context_engine
import test_redesign_TASKS as task_fixtures
from do_math.observation_transport import ObservationBatch
from do_math.observations import ObservationTracker
from test_redesign_OBSERVATION import Clock
from research_fixtures import write_checkpoint


class ObservationCollectionTests(unittest.TestCase):
    def test_owner_distinguishes_preview_and_boundary_from_self_check(self):
        from unittest.mock import create_autospec
        from test_redesign_ENGINE import routing_engine
        from test_redesign_OBSERVATION import rule
        for provider in ('codex', 'claude'):
            for kind in ('submission_preview', 'safety_boundary', 'self_check'):
                with self.subTest(provider=provider, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    tracker = ObservationTracker('EX-one', root, {'observation_rules': [rule()],
                        'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=Clock())
                    write_checkpoint(root, counters={'attempts': 2})
                    obligation = next(row for row in tracker.observe({'type': 'tick'})
                                      if row['kind'] == 'self_check_due')
                    tracker.issue_self_check(obligation['id'])
                    tracker.record_delivery(obligation['id'], source_offset=0)
                    tool = 'control_self_check' if kind == 'self_check' else 'control_submit'
                    arguments = ({'self_check_id': obligation['id']} if kind == 'self_check' else
                        {'request_id': 'NEXT', 'kind': kind, 'payload': {'inflight_calls': False, 'call_ids': []}})
                    event = ({'type': 'item.started', 'item': {'id': 'CALL', 'type': 'mcp_tool_call',
                        'server': 'execution_control', 'tool': tool, 'arguments': arguments}}
                        if provider == 'codex' else {'type': 'assistant', 'message': {'content': [
                            {'type': 'tool_use', 'id': 'CALL', 'name': 'mcp__execution_control__' + tool,
                             'input': arguments}]}})
                    engine = routing_engine()
                    engine._controls = create_autospec(engine._controls)
                    engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
                    engine._save = create_autospec(engine._save); engine._enqueue = create_autospec(engine._enqueue)
                    engine._review_observation_source = create_autospec(engine._review_observation_source, return_value=None)
                    engine.runtime['executions']['EX-one'] = {'id': 'EX-one', 'status': 'running',
                        'role': 'research_work', 'action': {'role': 'research_work'}}
                    engine._observe_running('EX-one', tracker, event)
                    self.assertEqual(tracker.obligations[obligation['id']].get('missed_reason'),
                                     'research_action_before_response' if kind == 'submission_preview' else None)
                    self.assertEqual('CALL' in tracker.self_check_call_ids, kind == 'self_check')
                    self.assertEqual('CALL' in tracker.boundary_call_ids, kind == 'safety_boundary')

    def test_self_check_is_discoverable_inside_the_assigned_workspace(self):
        from do_math.control_transport import ControlTransport
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'; workspace.mkdir()
            transport = ControlTransport(root / 'transport')
            binding = transport.issue('EX-one', 'GR-one', workspace=workspace)
            request = transport.request_self_check(binding, request={'self_check_id': 'SC-one',
                'execution_id': 'EX-one', 'payload': {'claim': 'check'}})
            surface = workspace / '.control/self-checks/SC-one.json'
            self.assertTrue(surface.is_file(), 'An ID-required poll needs a discoverable request in the allowed workspace')
            self.assertEqual(json.loads(surface.read_bytes()), request)
            self.assertEqual(transport.worker_self_check(binding, self_check_id='SC-one'), request)

    def test_native_poll_ack_requires_the_exact_successful_returned_request(self):
        from test_redesign_OBSERVATION import rule
        for variant in ('ok', 'started', 'failed', 'wrong_payload', 'error_result', 'claude'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [rule()],
                    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=Clock())
                write_checkpoint(directory, counters={'attempts': 2})
                obligation = next(r for r in tracker.observe({'type': 'tick'})
                                  if r['kind'] == 'self_check_due')
                # The poll returns the exact request object the tracker issued and hashed.
                envelope = deepcopy(tracker.issue_self_check(obligation['id']))
                tracker.record_delivery(obligation['id'], source_offset=100)
                if variant == 'wrong_payload': envelope['payload']['rule_revision'] += 1
                item = {'id': 'poll', 'type': 'mcp_tool_call', 'server': 'execution_control',
                    'tool': 'control_self_check', 'arguments': {'self_check_id': obligation['id']},
                    'status': 'failed' if variant == 'failed' else 'completed',
                    'result': {'content': [{'type': 'text', 'text': json.dumps(envelope)}],
                               'isError': variant == 'error_result'}}
                source = {'stream': 'stdout.jsonl', 'start_offset': 100, 'end_offset': 150,
                          'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 1}
                if variant == 'claude':
                    tracker.observe({'type': 'assistant', 'message': {'content': [{'type': 'tool_use',
                        'id': 'poll', 'name': 'mcp__execution_control__control_self_check', 'input': item['arguments']}]}},
                        source=source, evaluate=False)
                    event = {'type': 'user', 'message': {'content': [{'type': 'tool_result',
                        'tool_use_id': 'poll', 'content': json.dumps(envelope)}]}}
                else:
                    event = {'type': 'item.started' if variant == 'started' else 'item.completed', 'item': item}
                tracker.observe(event, source=source, evaluate=False)
                rows = tracker.observe({'type': 'item.started', 'item': {'id': 'new', 'type': 'command_execution'}},
                    source={**source, 'start_offset': 150, 'end_offset': 200, 'received_monotonic': 2}, evaluate=False)
                self.assertEqual(any(r['kind'] == 'self_check_missed' for r in rows), variant in {'ok', 'claude'})

    def test_native_command_after_delivery_without_ack_is_only_missing_response_evidence(self):
        from test_redesign_OBSERVATION import rule
        with tempfile.TemporaryDirectory() as directory:
            clock = Clock()
            tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [rule()],
                'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(directory, counters={'attempts': 2})
            obligation = next(r for r in tracker.observe({'type': 'tick'})
                              if r['kind'] == 'self_check_due')
            tracker.issue_self_check(obligation['id'])
            tracker.record_delivery(obligation['id'], source_offset=100)
            source = {'stream': 'stdout.jsonl', 'start_offset': 200, 'end_offset': 300,
                      'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 1}
            rows = tracker.observe({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'late'}},
                                   source=source, evaluate=False)
            self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows),
                             'Publication after delivery does not establish receipt of this self-check')
            clock.value = 6
            rows = tracker.observe({'type': 'tick'})
            self.assertTrue(any(r.get('reason') == 'response_deadline_passed' for r in rows))

    def test_checkpoint_capture_preserves_its_evidence_before_live_file_changes(self):
        from test_redesign_ENGINE import routing_engine
        from unittest.mock import create_autospec
        engine = routing_engine()
        engine.instance['config']['max_artifact_bytes'] = 4096
        engine._controls = create_autospec(engine._controls)
        engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._save = create_autospec(engine._save)
        engine.runtime['executions']['EX-one'] = {'id': 'EX-one', 'status': 'running',
            'role': 'research_work', 'action': {'role': 'research_work'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proof = b'exact submitted source'
            (root / 'proof.lean').write_bytes(proof)
            (root / 'checkpoint.json').write_text(json.dumps({'current_claim': 'candidate',
                'evidence_paths': ['proof.lean'], 'attempts': [], 'remaining_work': ['check'],
                'next_step': 'verify', 'progress_state': 'working'}), encoding='utf-8')
            tracker = ObservationTracker('EX-one', root, {'observation_mode': 'deadline_only'}, clock=Clock())
            batch = ObservationBatch([], [], [], 0, '2026-09-25T00:00:00Z', 1.25, 0, 0,
                                     root / 'stdout.jsonl', lambda: False)
            engine._observe_running('EX-one', tracker, batch)
            record = engine.runtime['checkpoints']['EX-one']
            self.assertEqual(len(record.get('evidence_files', [])), 1)
            (root / 'proof.lean').write_bytes(b'changed later')
            artifacts = engine._save.call_args.args[0]
            self.assertEqual(artifacts[record['evidence_files'][0]['artifact_ref']], proof)

    def test_returned_result_is_collected_before_unrelated_observation_callbacks(self):
        import threading
        import time
        from do_math.parallel import ModelCalls
        calls = ModelCalls()
        order = []
        def continuation():
            result = yield
            order.append('result')
        ready = continuation(); next(ready)
        calls.start_call(ready, lambda: {'status': 'completed'}, {}, execution_id='EX-ready').result(timeout=5)
        release = threading.Event()
        def observe_then_wait(on_observation):
            on_observation()
            release.wait(5)
            return {'status': 'completed'}
        live = continuation(); next(live)
        future = calls.start_call(live, observe_then_wait, {'on_observation': lambda: order.append('observation')},
                                  execution_id='EX-live')
        until = time.monotonic() + 5
        while not future.observations and time.monotonic() < until:
            time.sleep(.01)
        try:
            self.assertEqual(calls.collect(), 1)
            self.assertEqual(order, ['result', 'observation'])
        finally:
            release.set()
            calls.close()

    def test_buffered_command_before_delivery_is_not_a_new_action_violation(self):
        from test_redesign_OBSERVATION import rule
        with tempfile.TemporaryDirectory() as directory:
            clock = Clock()
            tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [rule()],
                'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(directory, counters={'attempts': 2})
            obligation = next(r for r in tracker.observe({'type': 'tick'})
                              if r['kind'] == 'self_check_due')
            envelope = tracker.issue_self_check(obligation['id'])
            tracker.record_delivery(obligation['id'], source_offset=100)
            source = {'stream': 'stdout.jsonl', 'start_offset': 0, 'end_offset': 80, 'received_at': '2026-09-25T00:00:00Z',
                      'received_monotonic': 1}
            old = {'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'old'}}
            rows = tracker.observe(old, source=source, evaluate=False)
            self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows))
            new = {'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'new'}}
            partial = {**old, 'item': {**old['item'], 'id': 'partial-before-delivery'}}
            rows = tracker.observe(partial, source={**source, 'start_offset': 80, 'end_offset': 160}, evaluate=False)
            self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows),
                             'The beginning of a partially written old event predates delivery')
            poll = {'type': 'item.completed', 'item': {'id': 'poll', 'type': 'mcp_tool_call',
                'server': 'execution_control', 'tool': 'control_self_check',
                'arguments': {'self_check_id': obligation['id']}, 'status': 'completed',
                'result': {'content': [{'type': 'text', 'text': json.dumps(envelope)}]}}}
            tracker.observe(poll, source={**source, 'start_offset': 100, 'end_offset': 160}, evaluate=False)
            rows = tracker.observe(new, source={**source, 'start_offset': 160, 'end_offset': 200, 'received_monotonic': 2}, evaluate=False)
            self.assertTrue(any(r['kind'] == 'self_check_missed' for r in rows))

    def test_terminated_stream_replay_preserves_events_without_live_reviews(self):
        from test_redesign_ENGINE import routing_engine
        from unittest.mock import create_autospec
        engine = routing_engine()
        engine._controls = create_autospec(engine._controls)
        engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._save = create_autospec(engine._save)
        engine.runtime['executions']['EX-one'] = {'id': 'EX-one', 'status': 'running',
            'role': 'research_work', 'action': {'role': 'research_work'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clock = Clock()
            tracker = ObservationTracker('EX-one', root, {'observation_mode': 'periodic',
                'observation_interval_seconds': 300}, clock=clock)
            clock.value = 900
            events = [{'type': 'turn.started'}, {'type': 'item.started',
                      'item': {'id': 'old-command', 'type': 'command_execution'}}]
            rows = [json.dumps(event).encode() + b'\n' for event in events]
            batch = ObservationBatch(events, [(0, 20), (20, 100)], rows, 0, '2026-09-25T00:00:00Z',
                                     301.25, 100, 100, root / 'stdout.jsonl', lambda: True)
            engine._observe_running('EX-one', tracker, batch)
            self.assertFalse(any(a['role'] == 'operational_review' for a in engine.runtime['queue']))
            self.assertEqual(len(engine.runtime['observation_facts']), 2)
            self.assertEqual(engine._save.call_count, 1)
            self.assertFalse(tracker.obligations)

    def test_one_native_chunk_is_one_owner_transaction(self):
        events = [{'type': 'item.completed', 'item': {'id': str(i), 'type': 'agent_message', 'text': str(i)}}
                  for i in range(20)]
        class Burst(Adapter):
            polls = 0
            def wait_for_termination(self, *args):
                self.polls += 1
                if self.polls == 1:
                    Path(self.request['stdout_path']).write_text(
                        ''.join(json.dumps(e) + '\n' for e in events), encoding='utf-8')
                return self.polls >= 2
        with tempfile.TemporaryDirectory() as directory, patch('do_math.model_runner.time.sleep'):
            root = Path(directory)
            runner = CodexModelRunner('fixture')
            runner._adapter = Burst({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}})
            delivered = []
            result = runner.run(prompt='fixture', output_schema={}, workspace=root,
                evidence_dir=root / 'evidence', model='fixture', effort='low',
                timeout_seconds=None, on_observation=delivered.append)
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(len(delivered), 1, 'One buffered stream chunk must not require 20 state transactions')
            self.assertEqual(delivered[0].events, events)


class OperationalInputTests(unittest.TestCase):
    def fixture(self):
        engine = context_engine()
        engine._documents['operational_review'] = contracts.prompt_documents('operational_review')
        target = {'id': 'EX-work', 'role': 'research_work', 'status': 'running',
                  'action': {'role': 'research_work', 'target': 'TK-work'}}
        engine.runtime['executions'][target['id']] = target
        value = {'current_claim': 'The exact source passed the preview.', 'evidence_paths': ['proof.lean'],
                 'attempts': ['checked'], 'remaining_work': ['central verification'],
                 'next_step': 'submit', 'progress_state': 'ready_to_submit'}
        raw = (json.dumps(value) + '\n').encode()
        checkpoint = {'kind': 'worker_checkpoint', 'execution_id': target['id'], 'status': 'valid',
            'value': value, 'artifact_ref': 'runtime/artifacts/BA-check/checkpoint.json',
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        engine.runtime['checkpoints'] = {target['id']: checkpoint}
        engine.store.read.return_value = raw
        action = {'id': 'AC-review', 'role': 'operational_review', 'target': target['id'],
                  'live': True, 'observation_refs': ['OF-one'], 'obligation_ids': ['SC-one']}
        return engine, action, checkpoint, raw

    def test_live_review_receives_the_already_sealed_target_checkpoint(self):
        engine, action, checkpoint, raw = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            context = engine._context(action, workspace, execution_id='EX-review')
            evidence = context.get('operational_evidence', {})
            self.assertEqual(evidence.get('checkpoint'), {k: v for k, v in checkpoint.items() if k != 'value'})
            source = evidence['checkpoint_source']
            self.assertEqual((workspace / source['local_path']).read_bytes(), raw)
            self.assertEqual(source['sha256'], checkpoint['sha256'])

    def test_large_checkpoint_stays_readable_without_becoming_mandatory_prompt_text(self):
        from do_math.context_store import prepare_role_input
        engine, action, checkpoint, _ = self.fixture()
        checkpoint['value']['current_claim'] = 'Evidence retained. ' * 40000
        raw = json.dumps(checkpoint['value']).encode()
        checkpoint.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        engine.store.read.return_value = raw
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-review', install_submission_tools=True)
            self.assertIsNone(fitted['overflow'], 'Checkpoint text is available through its exact file reference')
            source = fitted['context']['operational_evidence']['checkpoint_source']
            self.assertEqual((root / source['local_path']).read_bytes(), raw)

    def test_review_gets_the_same_canonical_basis_set_as_application(self):
        engine, action, checkpoint, raw = self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            context = engine._context(action, Path(directory), execution_id='EX-review')
            self.assertEqual(set(context.get('admissible_basis_refs', [])),
                             {'EX-work', 'OF-one', 'SC-one', checkpoint['artifact_ref']})

    def test_live_review_receives_exact_checkpoint_evidence_files(self):
        engine, action, checkpoint, raw = self.fixture()
        proof = b'theorem proof (n : Nat) : n + 0 = n := rfl\n'
        source = {'path': 'proof.lean', 'artifact_ref': 'runtime/artifacts/BA-check/proof.lean',
                  'sha256': hashlib.sha256(proof).hexdigest(), 'bytes': len(proof)}
        checkpoint['evidence_files'] = [source]
        engine.store.read.side_effect = lambda path, snapshot: proof if path == source['artifact_ref'] else raw
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            files = context['operational_evidence'].get('checkpoint_files', [])
            self.assertEqual(len(files), 1)
            self.assertEqual((root / files[0]['local_path']).read_bytes(), proof)

    def test_assigned_role_uses_exact_registry_references_even_below_input_limit(self):
        from do_math.context_store import fit_context, read_source
        engine, _, _, _ = self.fixture()
        profiles = list(engine.instance['execution_profiles'].values())
        context = {'action': {'role': 'research_work'}, 'task': {'id': 'TK-one', 'question': 'Fixed'},
                   'execution_profiles': profiles, 'role_profile_refs': engine.instance['role_profile_refs'],
                   'tasks': [{'id': 'TK-one', 'question': 'Fixed'}] * 10}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = fit_context(context, max_bytes=10_000_000, workspace=root,
                                 mandatory_keys=['task'], role='research_work')
            self.assertIsInstance(result['context']['execution_profiles'], dict,
                                  'The already assigned role need not repeatedly inline the full registry')
            ref = result['context']['execution_profiles']['source_ref']
            self.assertEqual(json.loads(read_source(root, ref)['bytes']), profiles)
            self.assertEqual(result['context']['task'], context['task'])
            self.assertLess(result['actual_bytes'], result['original_bytes'])

    def test_packaged_operational_submission_checks_the_advertised_basis(self):
        from do_math.context_store import prepare_role_input
        from do_math.submission import payload_issues
        engine, action, _, _ = self.fixture()
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'operational_review')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = engine._context(action, root, execution_id='EX-review')
            fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
                role='operational_review', profile=profile, snapshot=engine.head, workspace=root,
                activity_id='AY-review', install_submission_tools=True)
            fixed = fitted['validation_context']
            output = {'summary': 'Review', 'used_sources': ['EX-work'], 'questions': [],
                'disposition': {'kind': 'continue', 'basis_refs': ['EX-work'], 'next_owner': 'engine',
                                'reason': 'The preserved checkpoint is available.', 'next_review': None}}
            schema = contracts.schema_for('operational_review')
            self.assertEqual(payload_issues(output, schema, fixed, {}, root), [])
            output['disposition']['basis_refs'].append('input/catalog/observation.json')
            issues = payload_issues(output, schema, fixed, {}, root)
            self.assertTrue(any('invalid_basis_refs' in row['message'] for row in issues), issues)

    def test_changed_checkpoint_file_bytes_are_rejected_before_review(self):
        engine, action, _, _ = self.fixture()
        engine.store.read.return_value = b'changed bytes'
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(ValueError, 'checkpoint hash'):
            engine._context(action, Path(directory), execution_id='EX-review')


class CompletionBasisTests(unittest.TestCase):
    def fixture(self):
        fixture = task_fixtures.AssessmentApplicationTests()
        instance, runtime, assessment = fixture.fixture()
        assessment['decision'] = 'completed'
        assessment['item_dispositions'] = [
            {'obligation_id': row['id'], 'kind': 'fulfilled', 'evidence_refs': ['KN-proof', *row['evidence_required']]}
            for row in runtime['tasks']['TK-1']['completion_obligations']]
        instance['knowledge'] = {'KN-proof': {'id': 'KN-proof', 'revision': 1, 'lifecycle': 'active',
            'kind': 'theorem', 'formal_result_id': 'FR-proof', 'exposition_id': 'XP-proof',
            'dependencies': [], 'source_basis': []}}
        instance['formal_results'] = {'FR-proof': {'id': 'FR-proof', 'lean_code': 'exact source',
            'declaration_names': ['proof'], 'publication_state': 'candidate', 'formal_use': 'suspended'}}
        instance['expositions'] = {'XP-proof': {'id': 'XP-proof', 'items': [{'id': 'summary', 'text': 'exact argument'}]}}
        instance['identity_assessments'] = {}
        instance['assessment_uses'] = {}
        instance, runtime = fixture.apply(instance, runtime, assessment)
        return instance, runtime

    def test_submission_completion_survives_later_formal_verification_and_review_id(self):
        instance, runtime = self.fixture()
        task = runtime['tasks']['TK-1']
        self.assertTrue(task_scope.assessment_current(task, instance, runtime))
        instance['formal_results']['FR-proof'].update(publication_state='accepted', formal_use='active',
                                                    verification={'status': 'verified'})
        instance['knowledge']['KN-proof']['review_cycle_id'] = 'RC-new'
        self.assertTrue(task_scope.assessment_current(task, instance, runtime),
                        'Post-submission bookkeeping must not invalidate unchanged submitted evidence')

    def test_actual_submitted_source_change_still_invalidates_completion(self):
        instance, runtime = self.fixture()
        instance['formal_results']['FR-proof']['lean_code'] = 'different source'
        self.assertFalse(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_relation_endpoint_contents_remain_part_of_completion_evidence(self):
        instance, runtime = self.fixture()
        task = runtime['tasks']['TK-1']
        instance['knowledge']['KN-proof']['relation_claim'] = {'source': 'KN-source', 'target': 'KN-target'}
        for name in ('source', 'target'):
            instance['knowledge']['KN-' + name] = {'id': 'KN-' + name, 'lifecycle': 'active',
                'exposition_id': 'XP-' + name, 'formal_result_id': None, 'dependencies': []}
            instance['expositions']['XP-' + name] = {'id': 'XP-' + name, 'items': [{'text': name}]}
        task['assessment']['basis'] = task_scope.assessment_basis(task, task['assessment'], instance, runtime)
        instance['expositions']['XP-source']['items'][0]['text'] = 'different endpoint'
        self.assertFalse(task_scope.assessment_current(task, instance, runtime))

    def test_new_identity_assessment_does_not_change_submission_content_basis(self):
        instance, runtime = self.fixture()
        instance['identity_assessments']['IA-later'] = {'id': 'IA-later', 'formal_result_id': 'FR-proof',
            'exposition_id': 'XP-proof', 'decision': 'match'}
        self.assertTrue(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))

    def test_specialist_support_still_requires_its_current_trust_and_use(self):
        from test_walkthrough_contract_repairs import WalkthroughRepairs
        for judge in ('formal_check', 'identity_review'):
            with self.subTest(judge=judge):
                instance, runtime, assessment, _, _ = WalkthroughRepairs().specialist_fixture(judge)
                instance, runtime = task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)
                task = runtime['tasks']['TK-1']
                self.assertTrue(task_scope.assessment_current(task, instance, runtime))
                if judge == 'formal_check':
                    instance['active_trust_environment'] = 'TE-other'
                else:
                    for use in instance['assessment_uses'].values():
                        use['status'] = 'suspended'
                self.assertFalse(task_scope.assessment_current(task, instance, runtime))

    def test_specialist_dependency_use_is_not_reduced_to_submission_content(self):
        from test_walkthrough_contract_repairs import WalkthroughRepairs
        instance, runtime, assessment, kid, _ = WalkthroughRepairs().specialist_fixture('formal_check')
        formal = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]
        formal['dependencies'] = ['KN-dependency']
        instance['knowledge']['KN-dependency'] = {'id': 'KN-dependency', 'lifecycle': 'active',
            'formal_result_id': 'FR-dependency', 'dependencies': []}
        instance['formal_results']['FR-dependency'] = {'id': 'FR-dependency', 'lean_code': 'dependency',
            'declaration_names': ['dependency'], 'formal_use': 'active', 'dependencies': []}
        instance, runtime = task_fixtures.AssessmentApplicationTests().apply(instance, runtime, assessment)
        instance['formal_results']['FR-dependency']['formal_use'] = 'suspended'
        self.assertFalse(task_scope.assessment_current(runtime['tasks']['TK-1'], instance, runtime))


class SchedulingResponsibilityTests(unittest.TestCase):
    def test_terminal_stale_assessment_gets_one_followup_without_reopening(self):
        from test_six_connections import PlanningConnections
        with tempfile.TemporaryDirectory() as directory:
            engine = PlanningConnections().assessment_engine(directory)
            task = engine.runtime['tasks']['TK-1']
            task['status'] = 'closed'
            task['assessment'].update(current=False, invalidated_reason='source corrected')
            engine._refresh_readiness(); engine._refresh_readiness()
            self.assertEqual(task['status'], 'closed')
            events = [e for e in engine.runtime['events'] if e['kind'] == 'task_assessment_invalidated']
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]['target'], 'TK-1')
            self.assertTrue(any(events[0]['id'] in a.get('event_refs', []) for a in engine.runtime['queue']))

    def test_initial_preparation_owns_initial_events_until_accepted(self):
        from test_lifecycle_engine import FakeEngine
        from research_fixtures import FixtureAdapter
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(directory); engine.activate()
            engine.instance['lifecycle']['state'] = 'initializing'
            engine.runtime['status'] = 'initializing'
            engine._lifecycle_event('trust_environment_activated')
            engine._activate_initialization()
            first = next(a for a in engine.runtime['queue'] if a['role'] == 'research_preparation')
            self.assertEqual(set(first.get('event_refs', [])), set(engine.runtime['pending_events']))
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            self.assertTrue(engine.runtime['pending_events'], 'Assignment is not consumption')

    def test_normal_dispatch_occupancy_does_not_request_a_new_plan(self):
        from test_lifecycle_engine import FakeEngine
        from research_fixtures import FixtureAdapter
        with tempfile.TemporaryDirectory() as directory, patch('do_math.initialization.adapter_for', return_value=FixtureAdapter()):
            engine = FakeEngine(directory); engine.activate(); task = engine.task()
            engine._refresh_readiness()
            engine.runtime['queue'] = [{'id': 'AC-work', 'role': 'research_work', 'target': task['id']}]
            engine.runtime['pending_events'] = []
            engine._refresh_readiness()
            self.assertFalse(any(a['role'] == 'research_plan' for a in engine.runtime['queue']))
            self.assertTrue(engine._task_readiness[task['id']].get('dispatch_occupied'))
            engine.instance['grants']['GR-research']['status'] = 'revoked'
            engine._refresh_readiness()
            self.assertTrue(any(a['role'] == 'research_plan' for a in engine.runtime['queue']),
                            'Actual authority loss during occupancy still needs planning')


@test_group('resource')
class NativeBatchTests(unittest.TestCase):
    def test_real_job_completion_is_observed_before_delayed_batch_application(self):
        import os
        import time
        from unittest.mock import create_autospec
        from do_math.codex_adapter import CodexExecAdapter, CodexExecution
        from do_math.windows_job import WindowsJob
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        from test_redesign_ENGINE import routing_engine
        class LocalStream(CodexExecAdapter):
            def start(self, request_path, *, cwd, env, **kwargs):
                request = json.loads(request_path.read_bytes())
                prompt = Path(request['prompt_path'])
                schema_bytes = Path(request['output_schema_path']).read_bytes()
                (cwd / 'schema.json').write_bytes(schema_bytes)
                schema_hash = hashlib.sha256(schema_bytes).hexdigest()
                status = {'state': 'exited', 'cli_exit_code': 0,
                    'request_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
                    'stdin_sha256': hashlib.sha256(prompt.read_bytes()).hexdigest(), 'schema_sha256': schema_hash}
                events = [{'type': 'thread.started', 'thread_id': 'local-test'}, {'type': 'turn.started'},
                    {'type': 'item.completed', 'item': {'id': 'final', 'type': 'agent_message', 'text': '{"ok":true}'}},
                    {'type': 'turn.completed', 'usage': {}}]
                payload = {request['stdout_path']: ''.join(json.dumps(e) + '\n' for e in events),
                    request['stderr_path']: '', request['final_path']: '{"ok":true}',
                    request['status_path']: json.dumps(status)}
                script = 'import json,sys; from pathlib import Path; [(Path(p).write_bytes(v.encode())) for p,v in json.loads(sys.argv[1]).items()]'
                argv = (sys.executable, '-B', '-c', script, json.dumps(payload))
                job = WindowsJob(argv, cwd=cwd, env=os.environ)
                return CodexExecution(request_path, prompt, status['request_sha256'], status['stdin_sha256'], argv,
                    Path(request['stdout_path']), Path(request['stderr_path']), Path(request['final_path']),
                    Path(request['status_path']), job, cwd, schema_hash, request_path.read_bytes(), prompt.read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'; workspace.mkdir()
            engine = routing_engine()
            engine._controls = create_autospec(engine._controls)
            engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
            engine._save = create_autospec(engine._save)
            engine.runtime['executions']['EX-real'] = {'id': 'EX-real', 'status': 'running',
                'role': 'research_work', 'action': {'role': 'research_work'}}
            tracker = ObservationTracker('EX-real', workspace, {'observation_mode': 'periodic',
                'observation_interval_seconds': 1})
            tracker.last_review -= 600
            def delayed(batch):
                deadline = time.monotonic() + 10
                while not batch.is_terminated() and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertTrue(batch.is_terminated())
                engine._observe_running('EX-real', tracker, batch)
            runner = CodexModelRunner('local-fixture'); runner._adapter = LocalStream('local-fixture')
            result = runner.run(prompt='Local stream fixture, no model.', output_schema={'type': 'object'},
                workspace=workspace, evidence_dir=root / 'evidence', model='fixture', effort='low',
                timeout_seconds=15, on_observation=delayed)
            self.assertEqual(result['status'], 'completed', result.get('error'))
            self.assertEqual(result['output'], {'ok': True})
            self.assertTrue(result['execution']['collect']['termination_barrier']['confirmed'])
            self.assertFalse(any(a['role'] == 'operational_review' for a in engine.runtime['queue']))
            self.assertEqual(len(engine.runtime['observation_facts']), 4)
            for fact in engine.runtime['observation_facts'].values():
                Draft202012Validator(RECORDS['observation_facts']).validate(fact)


if __name__ == '__main__':
    unittest.main()
