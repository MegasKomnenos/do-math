"""MCP 공개 봉투와 가상 영수증 대기. 실제 수송의 파일을 읽고 쓴다."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math import control_server
from do_math.control_protocol import BINDING_FIELDS, RECEIPT_TOOL, SAFETY_BOUNDARY, SELF_CHECK_TOOL, SUBMIT_TOOL
from do_math.control_transport import ControlTransport
from support.entry import entry
from support.fakes.clock import FakeClock


class ReceiptClock(FakeClock):
    """첫 가상 대기에 실제 수송 종결을 주입하며 4회 초과 대기는 실패시킨다."""
    def __init__(self):
        super().__init__(monotonic=0)
        self.sleeps = []
        self.on_sleep = None

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        if len(self.sleeps) > 4:
            raise AssertionError('영수증 대기가 유한 차례를 초과함')
        super().sleep(seconds)
        if self.on_sleep is not None:
            self.on_sleep()


class ControlServerWireTests(unittest.TestCase):
    def test_timeout_validation_and_pending_receipt_use_virtual_time(self):
        clock = ReceiptClock()
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory, clock=clock)
            binding = transport.issue('EX-wire', 'GR-wire')
            for duration in (True, -1, '1'):
                with self.subTest(duration=duration):
                    with self.assertRaisesRegex(ValueError, '^timeout_seconds must be nonnegative or null$'):
                        control_server.wait_receipt(binding, 'RQ-absent', duration, clock=clock)
            start = clock.monotonic()
            self.assertIsNone(control_server.wait_receipt(binding, 'RQ-absent', 0.1, clock=clock))
            self.assertAlmostEqual(clock.monotonic() - start, 0.1)
            self.assertEqual(clock.sleeps, [0.05, 0.05])

    def test_unlimited_wait_returns_after_actual_transport_closes(self):
        clock = ReceiptClock()
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory, clock=clock)
            binding = transport.issue('EX-wire', 'GR-wire')
            ControlTransport.worker_submit(binding, request_id='RQ-close', kind=SAFETY_BOUNDARY,
                                           payload={'inflight_calls': False})
            clock.on_sleep = lambda: transport.close(binding, reason='소유 실행 종결')
            receipt = control_server.wait_receipt(binding, 'RQ-close', None, clock=clock)
            self.assertEqual((receipt['request_id'], receipt['state'], receipt['reason']),
                             ('RQ-close', 'closed', '소유 실행 종결'))
            self.assertEqual(clock.sleeps, [0.05])
            self.assertEqual(receipt, ControlTransport.worker_receipt(binding, 'RQ-close'))

    def test_protocol_negotiation_tools_errors_and_following_valid_request(self):
        values = entry()
        for enabled in (False, True):
            with self.subTest(self_check=enabled), tempfile.TemporaryDirectory() as directory:
                transport = ControlTransport(directory, clock=values.ports.clock)
                binding = transport.issue('EX-wire', 'GR-wire', self_check=enabled)
                messages = [
                    {'method': 'notifications/initialized'},
                    {'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-03-26'}},
                    {'id': 2, 'method': 'tools/list'},
                    {'id': 3, 'method': 'not-supported'},
                    {'id': 4, 'method': 'tools/call', 'params': {'name': 'not-a-tool'}},
                    {'id': 5, 'method': 'tools/call', 'params': {'name': 'submit_draft', 'arguments': {'draft_path': 'output.json'}}},
                    {'id': 6, 'method': 'tools/call', 'params': {'name': SUBMIT_TOOL, 'arguments': {
                        'request_id': 'RQ-wire', 'kind': SAFETY_BOUNDARY, 'payload': {'inflight_calls': False}, 'wait_seconds': 0}}},
                    {'id': 7, 'method': 'tools/call', 'params': {'name': RECEIPT_TOOL, 'arguments': {'request_id': 'RQ-wire'}}},
                    {'method': 'tools/list'},
                ]
                output = StringIO()
                argv = ['mcp', *('--' + key.replace('_', '-') + '=' + binding[key] for key in BINDING_FIELDS)]
                if enabled:
                    argv.append('--self-check')
                # 표준 입출력만 메모리 스트림에 연결한다. 제품 함수·수송 객체는 바꾸지 않는다.
                with patch('sys.stdin', StringIO('\n'.join(json.dumps(row) for row in messages))), redirect_stdout(output):
                    code = control_server.main(argv, ports=values.ports, environment=values.environment)
                replies = [json.loads(line) for line in output.getvalue().splitlines()]
                self.assertEqual((code, [row['id'] for row in replies]), (0, list(range(1, 8))))
                self.assertEqual(replies[0]['result'], {'protocolVersion': '2025-03-26', 'capabilities': {'tools': {}},
                    'serverInfo': {'name': 'do-math-control-transport', 'version': '5'}})
                self.assertEqual([tool['name'] for tool in replies[1]['result']['tools']],
                                 ['submit_draft', SUBMIT_TOOL, RECEIPT_TOOL] + ([SELF_CHECK_TOOL] if enabled else []))
                self.assertEqual([row['error'] for row in replies[2:5]], [
                    {'code': -32602, 'message': message} for message in
                    ('unsupported MCP method', 'unknown control tool', 'submission binding has no workspace')])
                delivery = json.loads(replies[5]['result']['content'][0]['text'])
                self.assertIsNone(delivery['receipt'])
                self.assertIsNone(json.loads(replies[6]['result']['content'][0]['text']))
                files = list((Path(binding['endpoint']) / 'inbox').glob('*.json'))
                self.assertEqual([path.name for path in files], ['RQ-wire.json'])
                request = json.loads(files[0].read_bytes())
                self.assertEqual((request['execution_id'], request['grant_id'], request['payload']),
                                 ('EX-wire', 'GR-wire', {'inflight_calls': False}))
                self.assertEqual(transport.pump()[0]['state'], 'received')


class PublishedReceiptWireTests(unittest.TestCase):
    def test_closed_worker_transport_keeps_the_accepted_receipt_and_refuses_new_drafts(self):
        """One real worker return; acceptance, file closure and confirmed termination are separate assertions."""
        from copy import deepcopy
        from do_math.control_protocol import SUBMIT_INTENT
        from support.scheduling_parallel import ready_work_sim
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        sim.step()
        execution_id, = set(sim.runtime['executions']) - before
        execution = sim.runtime['executions'][execution_id]
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        binding = json.loads((Path(execution['control_transport']['endpoint']) / 'binding.json').read_bytes())
        self.assertTrue(binding['self_check'])
        published, = [row for row in sim.runtime['control_receipts'].values()
                      if row['execution_id'] == execution_id and row['kind'] == SUBMIT_INTENT]
        receipt = ControlTransport.worker_receipt(binding, published['request_id'])
        self.assertEqual(receipt['state'], 'accepted')
        endpoint = Path(binding['endpoint'])
        state = json.loads((endpoint / 'state.json').read_bytes())
        self.assertEqual(state['state'], 'closed')
        snapshot = deepcopy((sim.engine.head, sim.instance, sim.runtime))
        requests_before = {path.name: path.read_bytes() for path in (endpoint / 'inbox').glob('*.json')}
        messages = [
            {'method': 'invalid-notification'},
            {'id': 1, 'method': 'tools/call', 'params': {'name': RECEIPT_TOOL,
                'arguments': {'request_id': published['request_id']}}},
            {'id': 2, 'method': 'tools/call', 'params': {'name': 'submit_draft',
                'arguments': {'draft_path': 'output.json', 'wait_seconds': 0}}},
            {'id': 3, 'method': 'tools/call', 'params': {'name': SELF_CHECK_TOOL,
                'arguments': {'self_check_id': 'SC-never-issued'}}},
            {'id': 4, 'method': 'tools/call', 'params': {'name': SUBMIT_TOOL,
                'arguments': {'request_id': 'RQ-after-ended', 'kind': SUBMIT_INTENT,
                              'payload': {'draft_path': 'output.json'}}}},
        ]
        output = StringIO()
        config = control_server.mcp_server_config(binding)
        with patch('sys.stdin', StringIO('\n'.join(json.dumps(row) for row in messages))), redirect_stdout(output):
            code = control_server.main(config['args'][1:], ports=sim.ports, environment=sim.environment)
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual((code, [row['id'] for row in replies]), (0, [1, 2, 3, 4]))
        self.assertTrue(all('error' not in row for row in replies), replies)
        values = [json.loads(row['result']['content'][0]['text']) for row in replies]
        self.assertEqual(values[0], receipt)
        self.assertEqual((values[1]['delivery']['state'], values[1]['delivery']['reason']), ('closed', state['reason']))
        self.assertIsNone(values[2])
        self.assertEqual(values[3], {'request_id': 'RQ-after-ended', 'state': 'closed', 'reason': state['reason']})
        self.assertEqual(ControlTransport.worker_receipt(binding, published['request_id']), receipt)
        self.assertEqual({path.name: path.read_bytes() for path in (endpoint / 'inbox').glob('*.json')}, requests_before)
        self.assertEqual((sim.engine.head, sim.instance, sim.runtime), snapshot)
        self.assertEqual(sim.engine.store.load()[2]['control_receipts'][published['id']], published)
