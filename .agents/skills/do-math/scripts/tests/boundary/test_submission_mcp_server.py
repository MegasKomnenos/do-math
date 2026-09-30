"""The worker's own processes around a submission: the MCP control server and the installed launcher (tier T4).

A provider CLI starts the product's MCP control server (``mcp_server_config``)
as a child process, and the producer runs the installed launcher
(``input/tools/check_submission.py``) in its own interpreter. These tests run
those real child processes against the scene of
``support.submission_protocol.ProtocolScene`` (the tools, the file transport and
a publisher over the Git port fake), and the launcher's check on a producer
workspace without the engine code.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
import zipfile

from do_math import submission, submission_tool
from purpose_fixtures import common
from support.fakes.clock import FakeClock
from support.submission_protocol import ProtocolScene, check_output, producer_workspace


class HyphenTokens(FakeClock):
    """A clock port whose random bytes begin with 0xf8, which the transport's URL-safe tokens encode as a leading "-"."""

    def random_hex(self, nbytes):
        return 'f8' + '00' * (nbytes - 1)


class LocalControlProtocolTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.scene = ProtocolScene(directory.name)

    def mcp(self, name, arguments):
        return self.scene.mcp(self, name, arguments)

    def test_real_mcp_intent_and_receipt_share_preserved_git_evidence(self):
        scene = self.scene
        check = submission.producer_check(scene.workspace, scene.draft)
        request = {"request_id": "CT-local", "kind": "submit_intent",
                   "payload": {"draft_path": check["raw_output_path"]}}
        self.assertEqual("submitted", self.mcp("control_submit", request)["state"])
        receipts = scene.transport.pump(scene.publish_intent)
        self.assertTrue(receipts and all(row["state"] == "accepted" for row in receipts), receipts)
        receipt = self.mcp("control_receipt", {"request_id": "CT-local", "wait_seconds": 0})
        self.assertEqual("accepted", receipt["state"])
        self.assertEqual(scene.head, receipt["snapshot"])
        self.assertEqual(scene.draft.read_bytes(), scene.store.read_bytes(scene.head, "runtime/artifacts/CT-local/output.json"))
        previous_head = scene.head
        scene.transport.pump(lambda _: self.fail("A replay must not publish twice"))
        self.assertEqual(previous_head, scene.head)

    def test_mcp_configuration_preserves_leading_hyphen_tokens(self):
        from do_math.control_transport import ControlTransport
        scene = self.scene
        # The legacy test swapped the transport's clock; this transport is made with the hyphen clock.
        transport = ControlTransport(scene.root / "delivery", clock=HyphenTokens())
        scene.binding = transport.issue("EX-worker", "GR-worker")
        self.assertTrue(scene.binding["transport_id"].startswith("-") and scene.binding["capability"].startswith("-"))
        result = self.mcp("control_receipt", {"request_id": "CT-not-submitted", "wait_seconds": 0})
        self.assertIsNone(result)

    def test_submit_draft_mcp_derives_internal_evidence_from_one_path(self):
        scene = self.scene
        result = self.mcp("submit_draft", {"draft_path": ".scratch/draft.json", "wait_seconds": 0})
        inbox = list((scene.root / "delivery" / scene.binding["transport_id"] / "inbox").glob("*.json"))
        self.assertEqual(len(inbox), 1)
        self.assertEqual({"draft_path": ".scratch/draft.json"}, json.loads(inbox[0].read_text())["payload"])
        self.assertEqual("submitted", result["delivery"]["state"])
        receipt = scene.transport.pump(scene.publish_intent)[0]
        self.assertEqual("accepted", receipt["state"])

    def test_installed_submit_command_waits_for_real_central_receipt(self):
        scene = self.scene
        command = [*scene.context["submission_contract"]["command"], "--output", str(scene.draft), "--submit",
                   "--wait-seconds", "20"]
        process = subprocess.Popen(command, cwd=scene.workspace, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            until = time.monotonic() + 25
            while process.poll() is None and time.monotonic() < until:
                scene.transport.pump(scene.publish_intent)
                try:
                    process.wait(timeout=0.02)
                except subprocess.TimeoutExpired:
                    continue
            stdout, stderr = process.communicate(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
        self.assertEqual(0, process.returncode, stderr.decode("utf-8", "replace") + stdout.decode("utf-8", "replace"))
        result = json.loads(stdout)
        self.assertEqual("accepted", result["delivery"]["state"])
        self.assertEqual(scene.head, result["delivery"]["snapshot"])

    def test_accepted_submission_is_unchanged_when_original_draft_changes_later(self):
        from do_math.canonical import canonical_json
        scene = self.scene
        check = submission.producer_check(scene.workspace, scene.draft)
        original = scene.draft.read_bytes()
        self.mcp("control_submit", {"request_id": "CT-changed", "kind": "submit_intent",
                                    "payload": {"draft_path": check["raw_output_path"]}})
        scene.transport.pump(scene.publish_intent)
        receipt = self.mcp("control_receipt", {"request_id": "CT-changed", "wait_seconds": 0})
        self.assertEqual("accepted", receipt["state"])
        scene.draft.write_bytes(canonical_json({"changed": True}))
        self.assertEqual(original, scene.store.read_bytes(scene.head, "runtime/artifacts/CT-changed/output.json"))

    def test_preview_is_an_explicit_nonpublication_control_request(self):
        scene = self.scene
        delivery = submission_tool.request_control(scene.workspace, ".scratch/draft.json", kind="submission_preview",
                                                   wait_seconds=0, clock=scene.clock)
        self.assertEqual("submitted", delivery["state"])
        # This tests transport semantics only; the engine's preview is tested with the receiver.
        result = {"contract_id": submission.PREVIEW_CONTRACT_ID, "passed": False, "authoritative": False,
                  "issues": [{"rule_id": "integration.candidate", "message": "Visible candidate issue"}]}
        scene.transport.pump(lambda request: {"state": "previewed", "result": result})
        receipt = self.mcp("control_receipt", {"request_id": delivery["request_id"], "wait_seconds": 0})
        self.assertEqual("previewed", receipt["state"])
        self.assertEqual(result, receipt["result"])
        self.assertIsNone(scene.head)


class InstalledToolTests(unittest.TestCase):
    def test_supplied_checker_is_standalone_and_does_not_mutate_fixed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, context = producer_workspace(directory)
            with zipfile.ZipFile(workspace / "input/tools/submission-support.zip") as archive:
                self.assertNotIn("do_math/engine.py", archive.namelist())
                self.assertFalse(any(name.endswith("_engine.py") for name in archive.namelist()))
                self.assertIn("do_math/record_schemas/__init__.py", archive.namelist())
            before = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (workspace / "input").rglob("*") if p.is_file()}
            # The installed command in its own interpreter, which imports only the shipped archive.
            self.assertTrue(check_output(self, workspace, context, {**common("No proposal."), "candidates": []},
                                         process=True)["passed"])
            after = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (workspace / "input").rglob("*") if p.is_file()}
            self.assertEqual(after, before)
            scripts = [part for part in context["submission_contract"]["command"][1:] if part.endswith(".py")]
            self.assertTrue(scripts)
            for part in scripts:
                self.assertTrue((Path(workspace) / part).resolve().is_relative_to(Path(workspace).resolve()))


if __name__ == "__main__":
    unittest.main()
