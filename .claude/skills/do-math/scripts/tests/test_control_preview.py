from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.control_transport import ControlTransport


class ControlPreviewTests(unittest.TestCase):
    def test_preview_is_replayable_but_never_a_publication_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            ControlTransport.worker_submit(binding, request_id="preview-1", kind="submission_preview",
                                           payload={"output_sha256": "a" * 64})
            calls = []
            def inspect(request):
                calls.append(request)
                return {"state": "previewed", "result": {"valid": True, "snapshot": "checked-snapshot"}}
            receipt = transport.pump(inspect)[0]
            self.assertEqual(receipt["state"], "previewed")
            self.assertTrue(receipt["result"]["valid"])
            self.assertNotIn("publication_id", receipt)
            self.assertNotIn("snapshot", receipt)
            self.assertEqual(ControlTransport.wait_receipt(binding, "preview-1", 0), receipt)
            self.assertEqual(ControlTransport(directory).pump(lambda _: self.fail("duplicate preview"))[0], receipt)
            self.assertEqual(len(calls), 1)

    def test_preview_cannot_be_misreported_as_accepted_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            request = {**binding, "request_id": "preview-1", "kind": "submission_preview", "payload": {}}
            with self.assertRaisesRegex(ValueError, "without publication"):
                transport.receive(request, publish=lambda _: {"state": "accepted", "published": True, "snapshot": "head"})
            self.assertIsNone(transport.receipt("preview-1"))

    def test_real_mcp_child_delivers_preview_and_returns_its_structured_result(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = ControlTransport(directory)
            binding = transport.issue("EX-preview", "GR-preview")
            server = transport.mcp_server_config(binding)
            child = subprocess.Popen([server["command"], *server["args"]], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            def rpc(number, method, params):
                child.stdin.write(json.dumps({"jsonrpc": "2.0", "id": number, "method": method, "params": params}) + "\n")
                child.stdin.flush()
                return json.loads(child.stdout.readline())
            try:
                rpc(1, "initialize", {"protocolVersion": "2024-11-05"})
                tools = rpc(2, "tools/list", {})["result"]["tools"]
                submit_schema = next(tool for tool in tools if tool["name"] == "control_submit")["inputSchema"]
                self.assertIn("submission_preview", submit_schema["properties"]["kind"]["enum"])
                submitted = rpc(3, "tools/call", {"name": "control_submit", "arguments": {
                    "request_id": "preview-mcp", "kind": "submission_preview", "payload": {"draft": "fixture"}}})
                self.assertNotIn("error", submitted)
                transport.pump(lambda _: {"state": "previewed", "result": {"valid": False, "issues": ["stale input"]}})
                reply = rpc(4, "tools/call", {"name": "control_receipt", "arguments": {"request_id": "preview-mcp", "wait_seconds": 0}})
                receipt = json.loads(reply["result"]["content"][0]["text"])
                self.assertEqual(receipt["state"], "previewed")
                self.assertEqual(receipt["result"]["issues"], ["stale input"])
            finally:
                child.stdin.close()
                child.wait(timeout=10)
                child.stdout.close()
                child.stderr.close()
