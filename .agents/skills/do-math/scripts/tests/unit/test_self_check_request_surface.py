"""Where a worker finds a self-check request (``control_transport``, layer 2): a known path in its own workspace.

The transport is the real ``ControlTransport`` over a temporary folder; the
worker's poll is the product's ``worker_self_check``.
"""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.control_transport import ControlTransport
from support.fakes.clock import FakeClock


class SelfCheckSurfaceTests(unittest.TestCase):
    def test_self_check_is_discoverable_inside_the_assigned_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / 'workspace'
            workspace.mkdir()
            transport = ControlTransport(root / 'transport', clock=FakeClock())
            binding = transport.issue('EX-one', 'GR-one', workspace=workspace)
            request = transport.request_self_check(binding, request={'self_check_id': 'SC-one',
                'execution_id': 'EX-one', 'payload': {'claim': 'check'}})
            surface = workspace / '.control/self-checks/SC-one.json'
            self.assertTrue(surface.is_file(), 'An ID-required poll needs a discoverable request in the allowed workspace')
            self.assertEqual(json.loads(surface.read_bytes()), request)
            self.assertEqual(transport.worker_self_check(binding, self_check_id='SC-one'), request)


if __name__ == '__main__':
    unittest.main()
