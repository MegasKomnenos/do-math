"""The workspace submission tool's control requests (``submission_tool``, layer 3), without an engine.

``request_control`` sends a draft locator through the control transport and
``main`` is what the installed launcher runs; both are called in this process
(``support.submission_protocol.ProtocolScene``: the tools, the transport and a
publisher over the Git port fake). The requests through the MCP server and the
installed launcher's own process are boundary tests
(``boundary.test_submission_mcp_server``).
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from do_math import submission_tool
from do_math.control_transport import ControlTransport
from support.submission_protocol import ProtocolScene


class LocalControlProtocolTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.scene = ProtocolScene(directory.name)

    def request(self, **options):
        scene = self.scene
        return submission_tool.request_control(scene.workspace, '.scratch/draft.json', clock=scene.clock, **options)

    def test_a_corrected_draft_at_the_same_path_gets_a_new_submission_attempt(self):
        scene = self.scene
        original = scene.draft.read_bytes()
        scene.draft.write_bytes(b'{invalid json')
        first = self.request(kind='submit_intent', wait_seconds=0)
        scene.transport.pump(scene.publish_intent)
        self.assertEqual(ControlTransport.worker_receipt(scene.binding, first['request_id'])['state'], 'rejected')
        scene.draft.write_bytes(original)
        second = self.request(kind='submit_intent', wait_seconds=0)
        self.assertNotEqual(first['request_id'], second['request_id'])
        scene.transport.pump(scene.publish_intent)
        self.assertEqual(ControlTransport.worker_receipt(scene.binding, second['request_id'])['state'], 'accepted')

    def test_supplied_tool_generates_fresh_sibling_ids_without_publishing(self):
        """The launcher's ``main`` runs in this process with the workspace as its working directory."""
        scene = self.scene
        identifiers = []
        before = sorted(str(path.relative_to(scene.workspace)) for path in scene.workspace.rglob('*'))
        for _ in range(2):
            printed = io.StringIO()
            with contextlib.chdir(scene.workspace), contextlib.redirect_stdout(printed):
                code = submission_tool.main(['--new-knowledge-id'])
            self.assertEqual(code, 0, printed.getvalue())
            identifier = json.loads(printed.getvalue())['replacement_id']
            self.assertRegex(identifier, r'^KN-[0-7][0-9A-HJKMNP-TV-Z]{25}$')
            identifiers.append(identifier)
        self.assertNotEqual(*identifiers)
        self.assertIsNone(scene.head)
        self.assertEqual(before, sorted(str(path.relative_to(scene.workspace)) for path in scene.workspace.rglob('*')))

    def test_invalid_wait_budget_does_not_queue_a_request(self):
        for budget in (-1, float('nan'), float('inf'), True):
            with self.subTest(budget=budget), \
                    self.assertRaisesRegex(ValueError, 'wait_seconds must be a finite nonnegative caller budget'):
                self.request(kind='submit_intent', wait_seconds=budget)
        self.scene.transport.pump(lambda _: self.fail('Invalid budget queued a request'))
        self.assertEqual(list((Path(self.scene.root) / 'delivery').rglob('inbox/*.json')), [])


if __name__ == '__main__':
    unittest.main()
