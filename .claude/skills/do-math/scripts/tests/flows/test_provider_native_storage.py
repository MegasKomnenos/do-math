"""native bytes가 실제 worker/runner/owner를 거쳐 review 원문으로 저장되는지 확인한다.

외부 CLI와 Jobs만 대역이다. callback은 실제 _observe_running에 전달하며
엔진·runner·collector·Repository를 교체하지 않는다. 각 stream은 32행 미만이다.
"""
from copy import deepcopy
import base64
import hashlib
import json
import unittest

from do_math.claude_adapter import ADAPTERS
from do_math.observations import ObservationTracker
from do_math.canonical import canonical_json
from do_math.repository import exact_content_hash
from do_math.payloads import json_safe
from support.provider_live import batch, running_execution
from support.provider_probes import ObservedCalls
from support.provider_native_inputs import EXTERNAL_JSON_VALUES, NATIVE_ROWS
from support.provider_runs import ProviderJobs, ScriptedCLI, model_runner, CLAUDE_INIT, claude_result
from support.review_sim import opened_sim, cycle_of


def setUpModule():
    opened_sim()


class NativeStorageTests(unittest.TestCase):
    def scene(self):
        sim = opened_sim()
        action = deepcopy(next(a for a in sim.runtime['queue'] if a['role'] == 'identity_review'))
        workspace = running_execution(sim, 'EX-native-close', 'identity_review', action=action)
        tracker = ObservationTracker('EX-native-close', workspace,
            {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
        return sim, action, workspace, tracker

    def test_public_branch_population_preserves_blocks_and_ignores_private_or_empty_content(self):
        """정본 _record_review_observation의 공개 분기와 정상 비공개·빈 행을 전건 대조한다."""
        sim, action, workspace, tracker = self.scene()
        command = {'type': 'command_execution', 'id': 'CMD', 'command': 'echo 정상',
                   'aggregated_output': '정상', 'exit_code': 0}
        tool_use = {'type': 'tool_use', 'id': 'TOOL', 'name': 'read', 'input': {'path': 'proof.lean'}}
        tool_result = {'type': 'tool_result', 'tool_use_id': 'TOOL', 'content': '정상'}
        events = [{'type': 'item.completed', 'item': command},
            {'type': 'assistant', 'message': {'content': [tool_use]}},
            {'type': 'user', 'message': {'content': [tool_result]}},
            {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': '첫째'},
                {'type': 'thinking', 'thinking': '비공개'}, {'type': 'text', 'text': '둘째'}]}},
            {'type': 'item.completed', 'item': {'type': 'reasoning', 'text': '비공개'}},
            {'type': 'assistant', 'message': {'content': []}},
            {'type': 'user', 'message': {'content': [None]}},
            {'type': 'assistant', 'message': {}},
            {'type': 'public_message', 'message': {'role': 'assistant', 'content': '후속'}}]
        expected = [('tool', {key: command[key] for key in ('command', 'aggregated_output', 'exit_code')}, 0, 0),
            ('assistant', tool_use, 1, 0), ('tool', tool_result, 2, 0),
            ('assistant', '첫째', 3, 0), ('assistant', '둘째', 3, 1), ('assistant', '후속', 8, 0)]
        stream = workspace / 'stdout.jsonl'
        incoming = batch(sim, events, stream, terminated=True)
        stream.write_bytes(b''.join(incoming.rows))
        sim.engine._observe_running('EX-native-close', tracker, incoming)
        messages = cycle_of(sim)['turns'][action['slot']]
        self.assertEqual([(row['role'], row['content'], row['source']['event_index'],
            int(row['message_id'].rsplit(':', 1)[1])) for row in messages], expected)
        self.assertEqual(messages[0]['call'], 'CMD')
        for message in messages:
            index = message['source']['event_index']
            self.assertEqual(sim.engine.store.read(message['source']['artifact_ref'], sim.engine.head), incoming.rows[index])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_native_numbers_and_public_blocks_survive_actual_runner_and_repository(self):
        for provider in ADAPTERS:
            with self.subTest(provider=provider):
                sim, action, workspace, tracker = self.scene()
                values = [deepcopy(value) for _, value, _ in EXTERNAL_JSON_VALUES]
                if provider == 'codex':
                    final = b'{"output_json":"{}"}'
                    public = [{'type': 'item.completed', 'item': {'id': 'tool-' + str(i),
                        'type': 'mcp_tool_call', 'server': 'numeric', 'tool': 'calculate',
                        'arguments': {'value': value}, 'result': {'value': value}}} for i, value in enumerate(values)]
                    public += [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': final.decode('utf-8')}}]
                    events = [{'type': 'thread.started', 'thread_id': 'native'}, {'type': 'turn.started'},
                              *public, {'type': 'turn.completed', 'usage': {'input_tokens': 1, 'output_tokens': 1,
                                  'reported_values': values}}]
                    first_public = 2
                    expected_roles = ['tool'] * len(values) + ['assistant']
                else:
                    final = b'{}'
                    public = [{'type': 'assistant', 'message': {'content': [{'type': 'tool_use',
                        'id': 'tool-' + str(i), 'name': 'calculate', 'input': {'value': value}}]}}
                        for i, value in enumerate(values)]
                    public += [{'type': 'user', 'message': {'content': [None, {'type': 'text', 'text': '정상 후속'}]}}]
                    events = [CLAUDE_INIT, *public, claude_result(b'{}', usage={
                        'input_tokens': 7, 'output_tokens': 3, 'reported_values': values})]
                    first_public = 1
                    expected_roles = ['assistant'] * len(values) + ['user']
                rows = [json.dumps(event, ensure_ascii=False).encode('utf-8') + b'\r\n' for event in events]
                if provider == 'codex':
                    # Codex's collector accepts the unterminated terminal row;
                    # Claude's strict JSONL collector requires its delimiter.
                    rows[-1] = rows[-1].rstrip(b'\r\n')
                raw = b'\n' + b''.join(rows)
                cli = ScriptedCLI(stdout=raw, final=final)
                jobs = ProviderJobs(cli, clock=sim.clock)
                deliveries = []
                tick_coordinates = []

                def deliver(incoming):
                    self.assertLess(len(deliveries), 32, '고정 길이 stream의 callback 상한')
                    self.assertLessEqual(len(incoming.events), 4, 'owner 적용은 read 전체와 독립된 유한 단위')
                    self.assertEqual(incoming.first_row, sum(len(part.rows) for part in deliveries))
                    self.assertEqual(incoming.caught_up(), incoming.end_offset == len(raw))
                    deliveries.append(incoming)
                    with ObservedCalls(observe=ObservationTracker.observe, capture={'observe': lambda arguments:
                            arguments['source'] if arguments['event'].get('type') == 'tick' else None}) as calls:
                        sim.engine._observe_running('EX-native-close', tracker, incoming)
                    tick_coordinates.extend(row for row in calls.captured('observe') if row is not None)

                result = model_runner(workspace.parent, jobs, sim.clock).run(prompt='시험용 합성 입력',
                    output_schema={'type': 'object'}, workspace=workspace, evidence_dir=workspace.parent / 'evidence',
                    model='claude:claude-sonnet-5' if provider == 'claude' else 'test-model',
                    effort='high', timeout_seconds=10, on_observation=deliver)
                self.assertEqual(result['status'], 'completed', result)
                self.assertEqual(result['output'], {})
                self.assertEqual(len(cli.calls), 1)
                self.assertEqual(cli.calls[0]['stdin'], '시험용 합성 입력'.encode('utf-8'))
                self.assertEqual([row for incoming in deliveries for row in incoming.rows], rows)
                self.assertEqual([event for incoming in deliveries for event in incoming.events], events)
                self.assertGreater(len([part for part in deliveries if part.events]), 1)
                coordinates = [coordinate for part in deliveries for coordinate in part.offsets]
                self.assertEqual([raw[start:end] for start, end in coordinates], rows)
                self.assertEqual(tick_coordinates, [part.source(part.end_offset, start_offset=part.end_offset)
                    for part in deliveries if part.caught_up()])
                self.assertEqual(sim.runtime['executions']['EX-native-close']['observation_receipts'], {
                    exact_content_hash({'execution_id': 'EX-native-close', 'event_index': index,
                        'offsets': list(coordinate), 'sha256': hashlib.sha256(row).hexdigest()}): index
                    for index, (coordinate, row) in enumerate(zip(coordinates, rows))})
                state, head = deepcopy(sim.runtime), sim.engine.head
                fresh = ObservationTracker('EX-native-close', workspace,
                    {'observation_mode': 'deadline_only', 'research_self_checks': False}, time_port=sim.clock)
                for incoming in deliveries:
                    sim.engine._observe_running('EX-native-close', fresh, incoming)
                self.assertEqual((sim.runtime, sim.engine.head), (state, head))
                messages = [row for row in cycle_of(sim)['turns'][action['slot']]
                            if row['kind'] == 'observed_public_message']
                self.assertEqual([row['role'] for row in messages], expected_roles)
                self.assertEqual([row['source']['event_index'] for row in messages], list(range(first_public, first_public + len(public))))
                for index, (message, event) in enumerate(zip(messages, public)):
                    self.assertEqual(message['message_id'], f'EX-native-close:public:{first_public + index}:0')
                    expected_event = json.dumps(event, ensure_ascii=False, sort_keys=True,
                                                separators=(',', ':'), allow_nan=False).encode('utf-8')
                    self.assertEqual(message['source']['event_sha256'], hashlib.sha256(expected_event).hexdigest())
                    self.assertEqual(sim.engine.store.read(message['source']['artifact_ref'], sim.engine.head), rows[first_public + index])
                for index, (message, (label, value, wire)) in enumerate(zip(messages, EXTERNAL_JSON_VALUES)):
                    content = message['content']
                    if label in {'decimal', 'unsafe-bound', 'unsafe-over'}:
                        expected_content = (b'{"arguments":{"value":' + wire +
                            b'},"result":{"value":' + wire + b'},"server":"numeric","tool":"calculate"}'
                            if provider == 'codex' else
                            b'{"id":"tool-' + str(index).encode() +
                            b'","input":{"value":' + wire + b'},"name":"calculate","type":"tool_use"}')
                        self.assertEqual(content.encode('utf-8'), expected_content)
                        content = json.loads(content)
                    self.assertEqual(content['arguments' if provider == 'codex' else 'input']['value'], value)
                    if provider == 'codex':
                        self.assertEqual(content['result']['value'], value)
                self.assertEqual(messages[-1]['content'], final.decode('utf-8') if provider == 'codex' else '정상 후속')
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
                self.assertEqual(sim.runtime['executions']['EX-native-close']['observation_stream']['end_offset'], len(raw))
                # The actual collector owns raw bytes; the owner stores a safe receipt projection.
                collected = result['execution']['collect']
                self.assertEqual(collected['stdout'], {'present': True, 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest(), 'raw': raw})
                final_raw = collected['final']['raw']
                self.assertEqual(collected['final']['sha256'], hashlib.sha256(final_raw).hexdigest())
                self.assertEqual(result['execution_id'], None)
                self.assertEqual(result['profile_ref'], None)
                self.assertEqual(result['error'], None)
                self.assertNotIn('error_kind', result)
                receipt = canonical_json(json_safe(result))
                reference = 'runtime/artifacts/BA-value-receipt/result.json'
                head, _, _ = sim.engine.store.save_with_state(sim.engine.head, sim.instance, sim.runtime,
                    artifacts={reference: receipt})
                saved = json.loads(sim.engine.store.read(reference, head))
                self.assertEqual(saved['execution']['collect']['stdout']['raw'], {
                    'sha256': hashlib.sha256(raw).hexdigest(), 'text': raw.decode('utf-8'),
                    'base64': base64.b64encode(raw).decode('ascii')})
                self.assertEqual(saved['output'], {})
                self.assertEqual(saved['execution_id'], None)
                self.assertEqual(saved['profile_ref'], None)
                self.assertEqual(saved['error'], None)
                self.assertNotIn('error_kind', saved)
                safe_values = [{'reported_decimal': '0.25'}, 2 ** 53 - 1,
                    '9007199254740992', '9007199254740993', *values[4:]]
                parsed = saved['execution']['collect']['jsonl']
                usage = parsed['usage'][-1] if provider == 'codex' else parsed['usage_segments'][0]['usage']
                self.assertEqual(usage['reported_values'], safe_values)
                self.assertTrue(all(job.closed for job in jobs.launched))

    def test_normalized_public_numeric_arguments_use_trusted_source_and_idle_is_noop(self):
        sim, action, workspace, tracker = self.scene()
        events = [deepcopy(seed) for _, seed, _, _ in NATIVE_ROWS]
        events += [{'type': 'public_message', 'source': {'event_index': 999},
            'message': {'role': 'tool', 'content': '숫자', 'arguments': {'value': value}}}
            for value in (0.25, 2 ** 53, 2 ** 53 + 1)]
        stream = workspace / 'stdout.jsonl'
        incoming = batch(sim, events, stream, terminated=True)
        stream.write_bytes(b''.join(incoming.rows))
        sim.engine._observe_running('EX-native-close', tracker, incoming)
        messages = cycle_of(sim)['turns'][action['slot']]
        self.assertEqual(len(messages), len(events))
        for index, message in enumerate(messages):
            self.assertEqual(message['source']['event_index'], index)
            if index < len(NATIVE_ROWS):
                self.assertEqual(message['content'], '정상')
            else:
                self.assertEqual(json.loads(message['arguments']), events[index]['message']['arguments'])
            self.assertEqual(sim.engine.store.read(message['source']['artifact_ref'], sim.engine.head), incoming.rows[index])
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
        head, runtime = sim.engine.head, deepcopy(sim.runtime)
        sim.advance(1)
        sim.engine._observe_running('EX-native-close', tracker, batch(sim, [], stream,
            start=incoming.end_offset, first_row=len(events), terminated=True))
        self.assertEqual(sim.engine.head, head)
        self.assertEqual(sim.runtime, runtime)

    def test_invalid_normalized_role_is_consumed_once_then_valid_row_is_published(self):
        """검토 원문은 불변이고 반려·원 바이트는 한 번 게시한 뒤 정상 행을 받는다."""
        sim, action, workspace, tracker = self.scene()
        event = {'type': 'public_message', 'message': {'role': 'outside', 'content': '잘못된 역할'}}
        stream = workspace / 'stdout.jsonl'
        incoming = batch(sim, [event], stream, terminated=True)
        stream.write_bytes(b''.join(incoming.rows))
        head = sim.engine.head
        cycle = deepcopy(cycle_of(sim))
        before = set(sim.runtime['observation_facts'])
        sim.engine._observe_running('EX-native-close', tracker, incoming)
        self.assertEqual(cycle_of(sim), cycle)
        added = [json.loads(row['event_json']) for key, row in sim.runtime['observation_facts'].items() if key not in before]
        rejected = [row for row in added if row.get('kind') == 'observation_input_rejected']
        self.assertEqual(len(rejected), 1)
        reference = rejected[0]['artifact_ref']
        self.assertEqual(rejected, [{'kind': 'observation_input_rejected', 'execution_id': 'EX-native-close',
            'reason': 'invalid normalized public message', 'next_owner': 'adapter',
            'observed_at': sim.clock.now(), 'artifact_ref': reference, 'event_index': 0}])
        self.assertEqual(sim.engine.store.read(reference, sim.engine.head), incoming.rows[0])
        self.assertNotEqual(sim.engine.head, head)
        self.assertEqual(tracker.fact_sequence, 2)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
        head, runtime = sim.engine.head, deepcopy(sim.runtime)
        sim.engine._observe_running('EX-native-close', tracker, incoming)
        self.assertEqual(sim.engine.head, head)
        self.assertEqual(sim.runtime, runtime)
        self.assertEqual(tracker.fact_sequence, 2)
        good = {'type': 'public_message', 'message': {'role': 'assistant', 'content': '정상'}}
        following = batch(sim, [good], stream, start=incoming.end_offset, first_row=1, terminated=True)
        stream.write_bytes(b''.join(incoming.rows + following.rows))
        sim.engine._observe_running('EX-native-close', tracker, following)
        messages = cycle_of(sim)['turns'][action['slot']]
        self.assertEqual([row['content'] for row in messages], ['정상'])
        self.assertEqual(messages[0]['source']['event_index'], 1)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
