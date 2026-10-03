"""Public CLI init publication and persistence; no external Git process."""
from pathlib import Path
import tempfile
import unittest

from support.git_init_cli import git_init_sim
from support.storage_files import audit_events


class GitInitCliTests(unittest.TestCase):
    def test_git_init_missing_and_empty_publish_and_restart_in_same_world(self):
        for empty, object_format in ((False, 'sha1'), (True, 'sha256')):
            with tempfile.TemporaryDirectory() as directory, audit_events('subprocess.Popen') as started:
                root = Path(directory)
                sim = git_init_sim(root, root, empty=empty, object_format=object_format)
                backend = sim.ports.git_backend
                head = sim.engine.head
                self.assertTrue(backend.repository_exists(sim.repository))
                self.assertEqual(backend.describe(sim.repository)[1], object_format)
                self.assertEqual(sim.instance['lifecycle']['state'], 'initializing')
                sim.restart()
                self.assertIs(sim.ports.git_backend, backend)
                self.assertEqual(sim.engine.head, head)
                self.assertEqual(len(head), 64 if object_format == 'sha256' else 40)
                self.assertEqual(started, [])
