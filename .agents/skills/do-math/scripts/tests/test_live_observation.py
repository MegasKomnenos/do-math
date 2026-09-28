"""Live observation of running executions: collected events, self-check obligations and observation rules.

Provider streams and model answers are fixtures. The observation tracker,
its transport, the owner that applies observations and their publication are
the product's.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec, Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import execution_profiles, observations
from do_math.configuration import DEFAULT_CONFIG
from do_math.observation_transport import ObservationBatch
from do_math.observations import ObservationTracker
from engine_fixtures import routing_engine
from provider_fixtures import Adapter, runner_with
from research_fixtures import acknowledge, Clock, observation_batch, observe, write_checkpoint
from test_categories import test_group


class RuleBindingTests(unittest.TestCase):
    def test_producer_reports_missing_initial_rules_before_contract_review(self):
        from research_fixtures import candidate
        from record_fixtures import contract_check, preparation_context, preparation_issues
        with tempfile.TemporaryDirectory() as directory, \
                patch('research_fixtures.supply_observation_rules', lambda *args: None):
            issues = preparation_issues([contract_check()], candidates=[candidate('one')],
                                        context=preparation_context(), workspace=Path(directory))
        self.assertIn('initial_observation_rules', issues)

    def test_foreign_execution_is_not_silently_rebound(self):
        rules = [{'id':'checkpoints', 'operator':'checkpoint_count_gte',
            'subject':{'kind':'checkpoint','id':'EX-foreign'}, 'basis':{'source':'checkpoint','unit':'count'},
            'threshold':1, 'required_evidence':['input/contract.json']}]
        with self.assertRaises(ValueError): observations.bind_task_rules(rules, 'EX-new')
        with self.assertRaises(ValueError): observations.task_rules_from_execution(rules, 'EX-new')

    def test_one_task_rule_can_start_two_distinct_executions(self):
        profile = next(p for p in execution_profiles.build_profiles({**deepcopy(DEFAULT_CONFIG),
            'tool_review_window_seconds':60, 'self_check_response_window_seconds':5})['execution_profiles'].values()
                       if p['role'] == 'research_work')
        rules = [{'id':'checkpoints', 'operator':'checkpoint_count_gte',
            'subject': {'kind':'checkpoint', 'id':'$execution'},
            'basis': {'source':'checkpoint', 'unit':'count'}, 'threshold':2, 'required_evidence':['contract']}]
        binder = getattr(observations, 'bind_task_rules', None)
        self.assertTrue(callable(binder), 'task rules need an execution binding before tracker admission')
        with tempfile.TemporaryDirectory() as directory:
            for eid in ('EX-first', 'EX-second'):
                bound = binder(rules, eid)
                config = observations.tracker_config(profile, initial_self_check_rules=bound)
                tracker = observations.ObservationTracker(eid, Path(directory), config)
                self.assertEqual(tracker.rules[0]['subject']['id'], eid)
        self.assertEqual(rules[0]['subject']['id'], '$execution')


    def test_checkpoint_iterations_bind_and_round_trip_for_each_execution(self):
        template = [{'id': 'iteration-review', 'operator': 'iteration_gte',
            'subject': {'kind': 'iteration', 'id': '$execution'},
            'basis': {'source': 'checkpoint', 'unit': 'count'},
            'threshold': 10, 'repeat_interval': 10, 'required_evidence': ['contract']}]
        for eid in ('EX-first', 'EX-retry'):
            bound = observations.bind_task_rules(template, eid)
            observations.validate_execution_rules(bound,
                bindings=observations.observation_rule_contract(), execution_id=eid)
            self.assertEqual(bound[0]['subject']['id'], eid)
            snapshot = {'iterations': {eid: 10}}
            due = observations.evaluate_rules(bound, snapshot)
            self.assertEqual([row['rule_id'] for row in due], ['iteration-review'])
            self.assertEqual(observations.task_rules_from_execution(bound, eid), template)
            foreign = deepcopy(bound)
            foreign[0]['subject']['id'] = 'EX-foreign'
            with self.assertRaises(ValueError):
                observations.bind_task_rules(foreign, eid)
            with self.assertRaises(ValueError):
                observations.task_rules_from_execution(foreign, eid)
            with self.assertRaises(ValueError):
                observations.validate_execution_rules(foreign,
                    bindings=observations.observation_rule_contract(), execution_id=eid)
        self.assertEqual(template[0]['subject']['id'], '$execution')

    def test_iterations_have_only_the_checkpoint_source(self):
        # Provider events carry no iterations, so an event-sourced iteration rule is not admitted.
        rules = [{'id': 'search', 'operator': 'iteration_gte',
            'subject': {'kind': 'iteration', 'id': '$execution'},
            'basis': {'source': 'execution_events', 'unit': 'count'},
            'threshold': 2, 'required_evidence': ['contract']}]
        with self.assertRaisesRegex(ValueError, 'basis'):
            observations.bind_task_rules(rules, 'EX-new')


class ObservationCollectionTests(unittest.TestCase):
    def test_owner_distinguishes_preview_and_boundary_from_self_check(self):
        from unittest.mock import create_autospec
        from engine_fixtures import routing_engine
        from research_fixtures import observation_rule
        for provider in ('codex', 'claude'):
            for kind in ('submission_preview', 'safety_boundary', 'self_check'):
                with self.subTest(provider=provider, kind=kind), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    tracker = ObservationTracker('EX-one', root, {'observation_rules': [observation_rule()],
                        'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=Clock())
                    write_checkpoint(root, counters={'attempts': 2})
                    obligation = next(row for row in observe(tracker, {'type': 'tick'})
                                      if row['kind'] == 'self_check_due')
                    # The worker has received and polled the request, so a research action now misses it.
                    acknowledge(tracker, obligation['id'])
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
                    engine._observe_running('EX-one', tracker, observation_batch([event],
                        received_monotonic=tracker.clock(), stream_path=root / 'stdout.jsonl',
                        start=tracker.observation_source['end_offset']))
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
        from research_fixtures import observation_rule
        for variant in ('ok', 'started', 'failed', 'wrong_payload', 'error_result', 'claude'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [observation_rule()],
                    'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=Clock())
                write_checkpoint(directory, counters={'attempts': 2})
                obligation = next(r for r in observe(tracker, {'type': 'tick'})
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
        from research_fixtures import observation_rule
        with tempfile.TemporaryDirectory() as directory:
            clock = Clock()
            tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [observation_rule()],
                'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(directory, counters={'attempts': 2})
            obligation = next(r for r in observe(tracker, {'type': 'tick'})
                              if r['kind'] == 'self_check_due')
            tracker.issue_self_check(obligation['id'])
            tracker.record_delivery(obligation['id'], source_offset=100)
            source = {'stream': 'stdout.jsonl', 'start_offset': 200, 'end_offset': 300,
                      'received_at': '2026-09-25T00:00:00Z', 'received_monotonic': 1}
            rows = tracker.observe({'type': 'item.started', 'item': {'type': 'command_execution', 'id': 'late'}},
                                   source=source, evaluate=False)
            self.assertFalse(any(r['kind'] == 'self_check_missed' for r in rows),
                             'Publication after delivery does not establish receipt of this self-check')
            # The running command held the deadline from 1s to 2s, so it passes after 6s.
            clock.value = 2
            observe(tracker, {'type': 'item.completed', 'item': {'type': 'command_execution', 'id': 'late'}})
            clock.value = 7
            rows = observe(tracker, {'type': 'tick'})
            self.assertTrue(any(r.get('reason') == 'response_deadline_passed' for r in rows))

    def test_checkpoint_capture_preserves_its_evidence_before_live_file_changes(self):
        from engine_fixtures import routing_engine
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
            batch = ObservationBatch([], [], [], 0, '2026-09-25T00:00:00Z', 1.25, 0,
                                     root / 'stdout.jsonl', lambda: False)
            engine._observe_running('EX-one', tracker, batch)
            record = engine.runtime['checkpoints']['EX-one']
            self.assertEqual(len(record.get('evidence_files', [])), 1)
            (root / 'proof.lean').write_bytes(b'changed later')
            artifacts = engine._save.call_args.args[0]
            self.assertEqual(artifacts[record['evidence_files'][0]['artifact_ref']], proof)

    def test_rejected_input_of_a_deadline_only_execution_is_recorded_without_a_review(self):
        # A deadline_only execution opens no recursive review, so its rejected input carries no followup.
        engine = routing_engine()
        engine._controls = create_autospec(engine._controls)
        engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._save = create_autospec(engine._save)
        engine.runtime['executions']['EX-one'] = {'id': 'EX-one', 'status': 'running',
            'role': 'maintenance', 'action': {'role': 'maintenance'}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracker = ObservationTracker('EX-one', root, {'observation_mode': 'deadline_only'}, clock=Clock())
            engine._observe_running('EX-one', tracker, observation_batch(
                [{'type': 'turn.started', 'execution_id': 'EX-other'}],
                received_monotonic=tracker.clock(), stream_path=root / 'stdout.jsonl'))
        rejected = [json.loads(fact['event_json']) for fact in engine.runtime['observation_facts'].values()
                    if json.loads(fact['event_json']).get('kind') == 'observation_input_rejected']
        self.assertEqual(len(rejected), 1)
        self.assertNotIn('followup', rejected[0])
        self.assertFalse(any(a['role'] == 'operational_review' for a in engine.runtime['queue']))

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
        from research_fixtures import observation_rule
        with tempfile.TemporaryDirectory() as directory:
            clock = Clock()
            tracker = ObservationTracker('EX-one', Path(directory), {'observation_rules': [observation_rule()],
                'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5}, clock=clock)
            write_checkpoint(directory, counters={'attempts': 2})
            obligation = next(r for r in observe(tracker, {'type': 'tick'})
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
        from engine_fixtures import routing_engine
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
                                     301.25, 100, root / 'stdout.jsonl', lambda: True)
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
            runner = runner_with(Burst({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}}))
            delivered = []
            result = runner.run(prompt='fixture', output_schema={}, workspace=root,
                evidence_dir=root / 'evidence', model='fixture', effort='low',
                timeout_seconds=None, on_observation=delivered.append)
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(len(delivered), 1, 'One buffered stream chunk must not require 20 state transactions')
            self.assertEqual(delivered[0].events, events)


@test_group('resource')
class NativeBatchTests(unittest.TestCase):
    def test_real_job_completion_is_observed_before_delayed_batch_application(self):
        import os
        import time
        from unittest.mock import create_autospec
        from do_math.codex_adapter import CLIExecution, CodexExecAdapter
        from do_math.windows_job import WindowsJob
        from do_math.record_schemas import RECORDS
        from jsonschema import Draft202012Validator
        from engine_fixtures import routing_engine
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
                return CLIExecution(status['request_sha256'], status['stdin_sha256'], argv,
                    Path(request['stdout_path']), Path(request['stderr_path']), Path(request['final_path']),
                    Path(request['status_path']), job, schema_hash, request_path.read_bytes(), prompt.read_bytes())
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
            runner = runner_with(LocalStream('local-fixture'))
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


class ObservationTransactions(unittest.TestCase):
    def test_failed_observation_publication_does_not_advance_the_tracker(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule
        engine = routing_engine(); engine._controls = create_autospec(engine._controls); engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "role": "research_work", "action": {"role": "research_work"}}
        engine._transport = Mock(); engine._transport_bindings = {"EX-one": {}}
        with tempfile.TemporaryDirectory() as temporary:
            tracker = ObservationTracker("EX-one", Path(temporary), {"observation_rules": [observation_rule()], "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            before = deepcopy((engine.instance, engine.runtime))
            engine._save = create_autospec(engine._save, side_effect=ValueError("CAS failure"))
            write_checkpoint(temporary, counters={"attempts": 2})
            tick = lambda: observation_batch(received_monotonic=tracker.clock(), stream_path=Path(temporary) / "stdout.jsonl")
            with self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-one", tracker, tick())
            self.assertEqual(tracker.counters, {})
            self.assertEqual((engine.instance, engine.runtime), before)
            engine._transport.request_self_check.assert_not_called()
            engine._save.side_effect = None
            engine._observe_running("EX-one", tracker, tick())
            self.assertEqual(tracker.counters, {"attempts": 2})
            self.assertTrue(engine.runtime["self_check_obligations"])
            engine._transport.request_self_check.assert_called_once()

    def test_failed_observation_rolls_back_to_the_published_state_without_copying_it_first(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule

        class PublishedStore:
            git_dir = None
            def __init__(self, instance, runtime):
                self.state = deepcopy(instance), deepcopy(runtime)
            def published_state(self, head):
                return self.state
            def load(self, snapshot=None):
                return snapshot, deepcopy(self.state[0]), deepcopy(self.state[1])

        engine = routing_engine()
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "role": "research_work", "status": "running",
                                                  "action": {"role": "research_work"}}
        engine.store = PublishedStore(engine.instance, engine.runtime)
        with tempfile.TemporaryDirectory() as temporary:
            tracker = ObservationTracker("EX-one", Path(temporary), {"observation_rules": [observation_rule()], "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            before = deepcopy(engine.runtime)
            engine._save = create_autospec(engine._save, side_effect=ValueError("CAS failure"))
            with patch("do_math.engine.deepcopy", wraps=deepcopy) as copied,                     self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-one", tracker, observation_batch(
                    received_monotonic=tracker.clock(), stream_path=Path(temporary) / "stdout.jsonl"))
            self.assertFalse(any(call.args[0] is before or call.args[0] == before for call in copied.call_args_list))
            self.assertEqual(engine.runtime, before)
            self.assertEqual(tracker.counters, {})

    def test_idle_observation_tick_neither_copies_nor_publishes_the_runtime(self):
        from do_math.observations import ObservationTracker
        from research_fixtures import Clock, observation_rule
        engine = routing_engine()
        engine.runtime["executions"]["EX-one"] = {"id": "EX-one", "role": "research_work", "status": "running",
                                                  "action": {"role": "research_work"}}
        with tempfile.TemporaryDirectory() as temporary:
            tracker = ObservationTracker("EX-one", Path(temporary), {"observation_rules": [observation_rule()], "tool_review_window_seconds": 60, "self_check_response_window_seconds": 5}, clock=Clock())
            engine._save = create_autospec(engine._save)
            tick = lambda: observation_batch(received_monotonic=tracker.clock(), stream_path=Path(temporary) / "stdout.jsonl")
            # The first tick reports the unmeasured rule signal; the next one has nothing new.
            engine._observe_running("EX-one", tracker, tick())
            engine._save.assert_called_once()
            engine._save.reset_mock()
            before = deepcopy(engine.runtime)
            with patch("do_math.engine.deepcopy", wraps=deepcopy) as copied:
                engine._observe_running("EX-one", tracker, tick())
            engine._save.assert_not_called()
            self.assertFalse(any(call.args[0] is engine.runtime for call in copied.call_args_list))
            self.assertEqual(engine.runtime, before)


class ReviewDialogueObservationTests(unittest.TestCase):
    def test_review_public_dialogue_keeps_raw_row_order_and_retries_after_failed_cas(self):
        from do_math.observations import ObservationTracker
        from do_math.observation_transport import ObservationBatch
        engine = routing_engine()
        engine._controls = create_autospec(engine._controls); engine._check_conversations = create_autospec(engine._check_conversations, return_value=False)
        engine._record_review_observation = create_autospec(engine._record_review_observation)
        engine.runtime["executions"]["EX-review"] = {"id": "EX-review", "action": {"role": "identity_review", "review_cycle_id": "RC-one"}}
        with tempfile.TemporaryDirectory() as temporary:
            engine.instance["workspace"] = temporary
            path = Path(temporary) / "runs/EX-review/evidence/stdout.jsonl"
            path.parent.mkdir(parents=True)
            event = {"type": "item.completed", "item": {"type": "agent_message", "text": "Visible independent judgment"}}
            row = json.dumps(event).encode() + b"\n"
            tail = {"type": "item.completed", "item": {"type": "agent_message", "text": "Final unterminated public message"}}
            tail_row = json.dumps(tail).encode()
            path.write_bytes(b"\n" + row + tail_row)

            def batch(event, start, raw, first_row):
                # The runner's batch carries the exact row bytes and their stream row number.
                return ObservationBatch([event], [(start, start + len(raw))], [raw], first_row,
                    "2026-09-25T00:00:00Z", 1.0, start + len(raw), path, lambda: False)
            tracker = ObservationTracker("EX-review", Path(temporary), {"observation_mode": "deadline_only", "research_self_checks": False})
            engine._save = create_autospec(engine._save, side_effect=ValueError("CAS failed"))
            with self.assertRaisesRegex(ValueError, "CAS"):
                engine._observe_running("EX-review", tracker, batch(event, 1, row, 0))
            engine._save.side_effect = None
            engine._observe_running("EX-review", tracker, batch(event, 1, row, 0))
            call = engine._record_review_observation.call_args
            self.assertEqual(call.args, ("EX-review", event))
            self.assertEqual(call.kwargs["event_index"], 0)
            self.assertEqual(engine._save.call_args.args[0][call.kwargs["artifact_ref"]], row)
            # After the Job ends the runner delivers the unterminated last row with the next number.
            engine._observe_running("EX-review", tracker, batch(tail, 1 + len(row), tail_row, 1))
            call = engine._record_review_observation.call_args
            self.assertEqual(call.args, ("EX-review", tail))
            self.assertEqual(call.kwargs["event_index"], 1)
            self.assertEqual(engine._save.call_args.args[0][call.kwargs["artifact_ref"]], tail_row)


class TaskObservationRoleTests(unittest.TestCase):
    def test_task_rules_follow_the_selected_roles_observation_contract(self):
        from do_math.observations import tracker_config, ObservationTracker

        class BeforeInput(Exception):
            pass

        settings = {**deepcopy(DEFAULT_CONFIG), "tool_review_window_seconds": 60,
                    "self_check_response_window_seconds": 5}
        profiles = execution_profiles.build_profiles(settings)["execution_profiles"]
        rule = {"id": "checkpoints", "operator": "checkpoint_count_gte",
                "subject": {"kind": "checkpoint", "id": "$execution"},
                "basis": {"source": "checkpoint", "unit": "count"},
                "threshold": 2, "required_evidence": ["contract"]}
        for role in ("research_work", "supplemental_research"):
            with self.subTest(role=role):
                engine = routing_engine()
                engine.head = "snapshot-one"
                engine.instance["config"] = deepcopy(settings)
                engine.runtime["tasks"]["TK-one"] = {"initial_observation_rules": [deepcopy(rule)]}
                profile = next(p for p in profiles.values() if p["role"] == role)
                engine._check_installation = create_autospec(engine._check_installation, return_value=True)
                engine._clock_guard = create_autospec(engine._clock_guard, return_value={"usable": True})
                engine._evaluation_context = create_autospec(engine._evaluation_context, return_value={})
                engine._action_lifecycle_gate = create_autospec(engine._action_lifecycle_gate)
                engine._revision_dispatch_waits = create_autospec(engine._revision_dispatch_waits, return_value=[])
                engine._selected_action_current = create_autospec(engine._selected_action_current, return_value=True)
                engine._obsolete_action_reason = create_autospec(engine._obsolete_action_reason, return_value=None)
                engine._execution_profile = create_autospec(engine._execution_profile, return_value=profile)
                engine._activity_for_action = create_autospec(engine._activity_for_action, return_value={"id": "AY-one"})
                engine._register_execution = create_autospec(engine._register_execution, side_effect=BeforeInput)
                action = {"id": "AC-one", "role": role, "target": "TK-one"}
                with patch("do_math.engine.tracker_config", wraps=tracker_config) as configured, \
                     patch("do_math.engine.governance.authorize", return_value={"allowed": True, "grant_id": "GR-one"}), \
                     patch("do_math.engine.planning.task_ready", return_value={"state": "ready"}):
                    with self.assertRaises(BeforeInput):
                        next(engine._call_steps(action))
                eid = engine._register_execution.call_args.args[1]["id"]
                config = tracker_config(profile, initial_self_check_rules=
                    configured.call_args.kwargs["initial_self_check_rules"])
                tracker = ObservationTracker(eid, Path("."), config)
                self.assertEqual(tracker.research_self_checks, role == "research_work")
                self.assertEqual(bool(tracker.rules), role == "research_work")
                if tracker.rules:
                    self.assertEqual(tracker.rules[0]["subject"]["id"], eid)
                self.assertEqual(engine.runtime["tasks"]["TK-one"]["initial_observation_rules"], [rule])


if __name__ == "__main__":
    unittest.main()
