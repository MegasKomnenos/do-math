"""CLI init then existing public Sim activation, plus template external-world persistence.

Full activation belongs in flows; engine's separately owned 35 CLI journey tests
remain untouched and must later connect to this init builder in integration.
"""
from pathlib import Path
import platform
import tempfile
import unittest

from support.git_init_cli import git_init_sim
from support.git_init_contract import isolated_nonrepository_parent
from support.sim import built
from support.storage_files import audit_events


def setUpModule():
    # Adapter identity samples the host once; audit the Git/activation path after that setup.
    platform.version()


class GitInitActivationTests(unittest.TestCase):
    def test_git_init_public_creation_reaches_activation_without_processes(self):
        with tempfile.TemporaryDirectory() as directory, audit_events('subprocess.Popen') as started:
            root = Path(directory)
            sim = git_init_sim(root, root)
            sim.activate()
            self.assertEqual(sim.instance['lifecycle']['state'], 'active')
            sim.restart()
            self.assertEqual(sim.instance['lifecycle']['state'], 'active')
            self.assertTrue(sim.ports.git_backend.repository_exists(sim.repository))
            self.assertEqual(started, [])

    def test_git_init_template_restores_repository_and_default_format(self):
        with audit_events('subprocess.Popen') as started:
            first = built('git-init-cli', git_init_sim, object_format='sha256')
            head = first.engine.head
            isolated_nonrepository_parent(first.root)
            (first.repository / '.git/HEAD').unlink()
            self.assertFalse(first.ports.git_backend.repository_exists(first.repository))
            second = built('git-init-cli', git_init_sim, object_format='sha256')
            self.assertTrue(second.ports.git_backend.repository_exists(second.repository))
            self.assertEqual(second.ports.git_backend.init_object_format, 'sha256')
            self.assertEqual(second.ports.git_backend.describe(second.repository)[1], 'sha256')
            self.assertEqual(second.engine.head, head)
            self.assertEqual(started, [])
