"""The control transport against real processes and the Windows file system (``control_transport``, ``control_server``).

The worker side of a transport runs in another process: the provider CLI starts
``control_server.py mcp`` as its MCP server, and a worker reads and writes
transport files as a separate program. These tests start those real Python
children and speak their JSON-RPC over pipes, and they drive real threads
against real files, so Windows file sharing itself is under test. The fake
clock port draws the transport tokens.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from do_math import control_transport as transport_module
from do_math.control_server import mcp_server_config
from do_math.control_transport import ControlTransport
from do_math.worker_request import validate_control_binding
from support.fakes.clock import FakeClock
from test_categories import test_group

SCRIPTS = Path(__file__).resolve().parents[2]


def _produce(binding, prefix, start, stopping, errors):
    """Submit forty requests after the start barrier; every failure goes to ``errors``, which the test asserts empty."""
    try:
        start.wait(timeout=10)
        for index in range(40):
            if stopping.is_set():
                return
            ControlTransport.worker_submit(binding, request_id=f'{prefix}-{index}', kind='submit_intent',
                                           payload={'manifest': [f'{prefix}-{index}.json']})
    except Exception as error:  # reported, not swallowed: the test fails on any entry
        errors.append(error)


class McpServer:
    """The worker's MCP server as the provider CLI starts it: a child process speaking JSON-RPC lines."""

    def __init__(self, binding):
        server = mcp_server_config(binding)
        self.child = subprocess.Popen([server['command'], *server['args']], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                      creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def rpc(self, number, method, params):
        self.child.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': number, 'method': method, 'params': params}) + '\n')
        self.child.stdin.flush()
        return json.loads(self.child.stdout.readline())

    def close(self):
        self.child.stdin.close()
        self.child.wait(timeout=10)
        self.child.stdout.close()
        self.child.stderr.close()


@test_group('resource')
class ChildProcessTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_real_mcp_child_delivers_preview_and_returns_its_structured_result(self):
        transport = ControlTransport(self.root, clock=FakeClock())
        binding = transport.issue('EX-preview', 'GR-preview')
        server = McpServer(binding)
        try:
            server.rpc(1, 'initialize', {'protocolVersion': '2024-11-05'})
            tools = server.rpc(2, 'tools/list', {})['result']['tools']
            submit_schema = next(tool for tool in tools if tool['name'] == 'control_submit')['inputSchema']
            self.assertIn('submission_preview', submit_schema['properties']['kind']['enum'])
            submitted = server.rpc(3, 'tools/call', {'name': 'control_submit', 'arguments': {
                'request_id': 'preview-mcp', 'kind': 'submission_preview', 'payload': {'draft': 'fixture'}}})
            self.assertNotIn('error', submitted)
            transport.pump(lambda _: {'state': 'previewed', 'result': {'valid': False, 'issues': ['stale input']}})
            reply = server.rpc(4, 'tools/call', {'name': 'control_receipt',
                                                 'arguments': {'request_id': 'preview-mcp', 'wait_seconds': 0}})
            receipt = json.loads(reply['result']['content'][0]['text'])
            self.assertEqual(receipt['state'], 'previewed')
            self.assertEqual(receipt['result']['issues'], ['stale input'])
        finally:
            server.close()

    def test_mcp_child_offers_the_self_check_tool_only_to_self_checking_executions(self):
        # Only research work answers self checks (observations.tracker_config).
        listed = {}
        transport = ControlTransport(self.root, clock=FakeClock())
        for self_check in (True, False):
            binding = transport.issue('EX-' + str(self_check), 'GR-1', self_check=self_check)
            validate_control_binding(binding, execution_id=binding['execution_id'])
            server = McpServer(binding)
            try:
                listed[self_check] = {tool['name'] for tool in server.rpc(1, 'tools/list', {})['result']['tools']}
            finally:
                server.close()
        self.assertEqual(listed[True] - listed[False], {transport_module.SELF_CHECK_TOOL})

    def test_child_process_round_trips_submit_receipt_self_check_and_close(self):
        def child(statement, binding):
            environment = {**os.environ, 'PYTHONPATH': str(SCRIPTS) + os.pathsep + os.environ.get('PYTHONPATH', '')}
            result = subprocess.run([sys.executable, '-c', statement, json.dumps(binding)], capture_output=True,
                                    text=True, check=True, env=environment)
            return json.loads(result.stdout)
        clock = FakeClock()
        transport = ControlTransport(self.root, clock=clock)
        binding = transport.issue('EX-1', 'GR-1')
        submit = ("import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); "
                  "print(json.dumps(ControlTransport.worker_submit(b, request_id='CT-1', kind='submit_intent', "
                  "payload={'manifest':['result.json']})))")
        self.assertEqual(child(submit, binding)['state'], 'submitted')
        published = []
        receipts = transport.pump(lambda request: (published.append(request) or {
            'state': 'accepted', 'published': True, 'snapshot': 'SN-1', 'publication_id': 'PR-1'}))
        self.assertEqual([row['state'] for row in receipts], ['accepted'])
        query = ("import json,sys; from do_math.control_server import wait_receipt; b=json.loads(sys.argv[1]); "
                 "print(json.dumps(wait_receipt(b, 'CT-1', 0)))")
        self.assertEqual(child(query, binding)['snapshot'], 'SN-1')
        recovered = ControlTransport(self.root, clock=clock)
        self.assertEqual(recovered.pump(lambda _: self.fail('published request must not republish'))[0]['publication_id'],
                         'PR-1')
        transport.request_self_check(binding, request={'self_check_id': 'SC-1', 'execution_id': 'EX-1',
                                                       'payload': {'obligation': 'report scope'}})
        poll = ("import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); "
                "print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1')))")
        self.assertEqual(child(poll, binding)['payload']['obligation'], 'report scope')
        answer = {'obligation_id': 'SC-1', 'execution_id': 'EX-1', 'rule_revision': 0,
                  'rule_results': [{'rule_id': 'R-1', 'status': 'normal', 'evidence_refs': ['EV-1'],
                                    'missing_evidence_refs': [], 'reason': 'checked'}],
                  'progress': 'progress', 'attempts': ['checked'], 'next_method': 'continue'}
        reply = ("import json,sys; from do_math.control_transport import ControlTransport; b=json.loads(sys.argv[1]); "
                 "print(json.dumps(ControlTransport.worker_self_check(b, self_check_id='SC-1', response="
                 + repr(answer) + ")))")
        self.assertEqual(child(reply, binding)['state'], 'submitted')
        self.assertEqual(transport.pump(lambda _: {'state': 'accepted', 'published': True, 'snapshot': 'SN-2'})[-1]['kind'],
                         'self_check_response')
        transport.close(binding, reason='execution ended')
        self.assertEqual(ControlTransport.worker_submit(binding, request_id='CT-2', kind='submit_intent',
                                                        payload={'manifest': []})['state'], 'closed')


class ConcurrentFileTests(unittest.TestCase):
    def test_concurrent_real_files_do_not_reproduce_old_permission_error(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        transport = ControlTransport(Path(temporary.name) / 'transport', clock=FakeClock())
        binding = transport.issue('EX-transport', 'GR-transport')
        errors, start, stopping = [], threading.Barrier(3), threading.Event()
        # A broken I/O implementation must not keep the test process alive.
        threads = [threading.Thread(target=_produce, args=(binding, prefix, start, stopping, errors), daemon=True)
                   for prefix in ('left', 'right')]
        for thread in threads:
            thread.start()
        start.wait(timeout=10)
        deadline = time.monotonic() + 15
        refuse = lambda _: {'state': 'rejected', 'reason': 'stress observation'}
        while any(thread.is_alive() for thread in threads):
            if time.monotonic() >= deadline:
                errors.append(TimeoutError('request producers did not finish; inbox=' + repr(
                    sorted(p.name for p in (Path(binding['endpoint']) / 'inbox').glob('*.json')))))
                break
            try:
                transport.pump(refuse)
            except (OSError, ValueError, RuntimeError) as error:
                errors.append(error)
                break
            # Pump again once a producer has progressed a little: bounded by the thread, not a fixed sleep.
            for thread in threads:
                if thread.is_alive():
                    thread.join(0.01)
                    break
        stopping.set()
        for thread in threads:
            thread.join(timeout=1)
        self.assertFalse(any(thread.is_alive() for thread in threads), errors)
        transport.pump(refuse)
        self.assertFalse(any(isinstance(error, PermissionError) for error in errors), errors)
        self.assertEqual([], errors)


if __name__ == '__main__':
    unittest.main()
