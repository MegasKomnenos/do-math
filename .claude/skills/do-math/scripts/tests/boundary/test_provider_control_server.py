"""The execution-control MCP server a worker registers, started as the child process its command names.

``control_server.mcp_server_config(binding)`` is the command both workers
register with their CLI. Started from that command, the server speaks JSON-RPC
on its standard streams: it forwards submissions and self-check answers only
for the bound execution, answers receipts, refuses a malformed answer as a tool
error, and reports a closed binding. The transport side runs in this process.
``sim.test_provider_pinned_runner`` checks the binding's way into the workers.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from do_math.control_protocol import REQUEST_KINDS, SELF_CHECK_RESPONSE_SCHEMA
from do_math.control_server import mcp_server_config
from do_math.control_transport import ControlTransport
from test_categories import test_group


@test_group('resource')
class ControlServerTests(unittest.TestCase):
    def test_execution_control_is_registered_and_round_trips_in_child(self):
        from support.entry import entry
        _entry = entry()
        from do_math.wiring import real_ports
        _entry.ports = real_ports(environment=_entry.environment)
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(Path(directory) / "transport", clock=_entry.ports.clock)
            binding = transport.issue("EX-bound", "GR-bound", self_check=True)  # a research work execution
            config = mcp_server_config(binding)
            process = subprocess.Popen([config["command"], *config["args"]], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            sequence = 0

            def exchange(method, params):
                nonlocal sequence
                sequence += 1
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": sequence, "method": method,
                                                "params": params}) + "\n")
                process.stdin.flush()
                response = json.loads(process.stdout.readline())
                self.assertEqual(response["id"], sequence)
                return response

            def rpc(method, params):
                response = exchange(method, params)
                self.assertNotIn("error", response)
                return response["result"]

            def call(name, arguments):
                return json.loads(rpc("tools/call", {"name": name, "arguments": arguments})["content"][0]["text"])
            try:
                self.assertEqual(rpc("initialize", {"protocolVersion": "2024-11-05"})["serverInfo"]["version"], "5")
                listed = {t["name"]: t for t in rpc("tools/list", {})["tools"]}
                tools = {name: tool["inputSchema"] for name, tool in listed.items()}
                self.assertEqual(set(tools), {"control_submit", "control_receipt", "control_self_check", "submit_draft"})
                # The worker sees the kinds the transport accepts and the answer schema it will be checked against.
                # The answer schema travels in the description; the input node keeps the plain object shape
                # that preserved provider runs accepted.
                self.assertEqual(set(tools["control_submit"]["properties"]["kind"]["enum"]), REQUEST_KINDS)
                self.assertEqual(tools["control_self_check"]["properties"]["response"], {"type": "object"})
                self.assertIn(json.dumps(SELF_CHECK_RESPONSE_SCHEMA, sort_keys=True),
                              listed["control_self_check"]["description"])
                submitted = call("control_submit", {"request_id": "REQ-one", "kind": "submit_intent",
                    "execution_id": "EX-cannot-override-bound-execution", "payload": {"draft_path": "draft.json"}})
                self.assertEqual(submitted["state"], "submitted")
                self.assertIsNone(call("control_receipt", {"request_id": "REQ-one"}))
                publications = []

                def publish(request):
                    self.assertEqual((request["execution_id"], request["grant_id"]), ("EX-bound", "GR-bound"))
                    publications.append(request)
                    return {"state": "accepted", "published": True, "snapshot": "test-published-head"}
                transport.pump(publish)
                receipt = call("control_receipt", {"request_id": "REQ-one"})
                self.assertEqual(receipt["state"], "accepted")
                self.assertEqual(receipt["execution_id"], "EX-bound")
                self.assertEqual(receipt["snapshot"], "test-published-head")
                other = transport.issue("EX-other", "GR-other")
                self.assertIsNone(ControlTransport.worker_receipt(other, "REQ-one"))
                transport.pump(publish)
                self.assertEqual(len(publications), 1)
                transport.request_self_check(binding, request={"self_check_id": "SC-one", "execution_id": "EX-bound",
                                                               "payload": {"obligations": ["answer"]}})
                self.assertEqual(call("control_self_check", {"self_check_id": "SC-one"})["execution_id"], "EX-bound")
                # A malformed answer is a tool error the worker can correct; nothing is delivered.
                refused = exchange("tools/call", {"name": "control_self_check",
                                                  "arguments": {"self_check_id": "SC-one", "response": {"answered": True}}})
                self.assertEqual(refused["error"]["code"], -32602)
                self.assertIsNone(ControlTransport.worker_receipt(binding, "self-check-SC-one"))
                self.assertFalse((Path(binding["endpoint"]) / "inbox" / "self-check-SC-one.json").exists())
                answer = {"obligation_id": "SC-one", "execution_id": "EX-bound", "rule_revision": 0,
                          "rule_results": [{"rule_id": "R-1", "status": "normal", "evidence_refs": ["EV-1"],
                                            "missing_evidence_refs": [], "reason": "checked"}],
                          "progress": "progress", "attempts": ["checked"], "next_method": "continue"}
                call("control_self_check", {"self_check_id": "SC-one", "response": answer})
                transport.pump(publish)
                self.assertEqual(call("control_receipt", {"request_id": "self-check-SC-one"})["state"], "accepted")
                transport.close(binding, reason="execution ended")
                self.assertEqual(call("control_submit", {"request_id": "REQ-after", "kind": "submit_intent",
                    "payload": {"manifest": []}})["state"], "closed")
            finally:
                process.stdin.close()
                process.wait(timeout=10)
                self.assertEqual(process.returncode, 0, process.stderr.read())
                process.stdout.close()
                process.stderr.close()


if __name__ == "__main__":
    unittest.main()
