"""The workspace submission tool's entry points (``submission_tool``, layer 3), called without an engine.

``main`` is what the installed launcher runs in the producer's process and
``request_control`` is what it and the MCP control server call to send a draft
locator. Both only wire the layer-2 checks to the control transport, so these
tests call them directly in this process (the child-process runs are the
boundary tests of ``boundary.test_submission_installed_tool``).
"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math import contracts, submission, submission_tool
from do_math.control_transport import ControlTransport
from record_fixtures import research_work_context
from support.fakes.clock import FakeClock
from support.provider_probes import ObservedCalls


class RequestControlTests(unittest.TestCase):
    def test_submit_transport_contains_only_the_draft_locator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            clock = FakeClock()
            transport = ControlTransport(root / "delivery", clock=clock)
            binding = transport.issue("EX-flow", "GR-flow", workspace=workspace)
            context = {"action": {"role": "maintenance", "id": "AC-flow"}, "execution_id": "EX-flow",
                       "control_binding": binding, "snapshot": "fixed", "tasks": [], "knowledge_catalog": [],
                       "sources": [], "kind_definitions": {}}
            submission.install_tools(workspace, context, contracts.schema_for("maintenance"), None, clock=clock)
            (workspace / ".scratch").mkdir()
            (workspace / ".scratch" / "draft.json").write_bytes(b'{}')
            # The legacy test replaced worker_submit; the real one runs and its arguments are captured as it starts.
            with ObservedCalls(submit=ControlTransport.worker_submit) as calls:
                submission_tool.request_control(workspace, ".scratch/draft.json", kind="submit_intent",
                                                wait_seconds=0, binding=binding, clock=clock)
            (arguments,) = calls.captured("submit")
            self.assertEqual({"draft_path": ".scratch/draft.json"}, arguments["payload"])
            # The one request the transport delivers to the owner carries exactly that payload.
            delivered = []
            transport.pump(lambda request: delivered.append(request) or {"state": "rejected", "reason": "read only"})
            self.assertEqual([(arguments["request_id"], {"draft_path": ".scratch/draft.json"})],
                             [(row["request_id"], row["payload"]) for row in delivered])


class ToolMainTests(unittest.TestCase):
    def test_preview_records_are_written_even_when_schema_is_invalid(self):
        """The name says preview records; the legacy test and this one run the check mode without ``--preview``."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            submission.install_tools(workspace, research_work_context(), contracts.schema_for("research_work"), None,
                                     clock=FakeClock())
            draft = workspace / "response.json"
            draft.write_text('{}', encoding="utf-8")
            # The launcher runs main in the workspace; the working directory is the process's, not a product name.
            with patch.object(Path, "cwd", return_value=workspace), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, submission_tool.main(["--output", str(draft)]))
            records = list((workspace / "checks").glob("*.json"))
            self.assertEqual(1, len(records))
            check = json.loads(records[0].read_bytes())
            self.assertIn("payload_semantics", check["not_checked"])


if __name__ == "__main__":
    unittest.main()
