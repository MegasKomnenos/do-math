"""Integration tests for immutable Git object state storage in fresh repositories."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import create_autospec


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.git_store import GitStateStore, GitStateStoreError  # noqa: E402
from research_fixtures import git_init  # noqa: E402


def git_result(returncode, stdout=b'', stderr=b''):
    return subprocess.CompletedProcess(['git'], returncode, stdout, stderr)


class SnapshotMetadataTests(unittest.TestCase):
    INSTANCE = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'
    REF = 'refs/heads/do-math/' + INSTANCE

    def setUp(self):
        self.repository = git_init(Path(self.enterContext(tempfile.TemporaryDirectory())))

    def store(self, *, length=40, root_type='commit', rows=None, returncode=0, resolved=None):
        """A store over an empty repository whose later Git runs answer with the given metadata.

        Git output is parsed by the real Git backend (do_math.git_process), so the
        fake output replaces that backend's process runs. Rows carry the object size.
        """
        store = GitStateStore(self.repository, self.INSTANCE)
        store.object_format = 'sha1' if length == 40 else 'sha256'
        head, research, runtime = ('a' * length, 'b' * length, 'c' * length)
        values = rows if rows is not None else [head + ' ' + root_type + ' 180', research + ' tree 70',
                                                runtime + ' tree 70']
        if resolved is None:
            resolved = git_result(0, (head + '\n').encode())
        # One batch query; rev-parse (``resolved``) runs only when the ref line is missing.
        store._backend._run = create_autospec(store._backend._run, side_effect=[
            git_result(returncode, ('\n'.join(values) + '\n').encode()), resolved])
        return store, head

    def test_wrong_or_incomplete_metadata_never_returns_a_snapshot(self):
        head, tree, ref = 'a' * 40, 'b' * 40, self.REF
        missing = [ref + suffix + ' missing' for suffix in ('', ':research', ':runtime')]
        # Row shape (field count, size) is refused by the Git backend; kinds and
        # subtrees by the store.
        cases = [([head + ' blob 5', ref + ':research missing', ref + ':runtime missing'], 'commit'),
                 (missing, 'unreadable'),
                 ([head + ' commit extra', tree + ' tree 70', tree + ' tree 70'], 'invalid batch object check row'),
                 ([head + ' commit 180', ref + ':research missing', tree + ' tree 70'], 'research'),
                 ([head + ' commit 180', tree + ' blob 5', tree + ' tree 70'], 'tree'),
                 ([head + ' commit 180', tree + ' tree 70'], 'response count differs'),
                 ([head + ' commit 180', tree + ' tree 70', tree + ' tree 70', tree + ' tree 70'],
                  'response count differs')]
        for rows, message in cases:
            with self.subTest(rows=rows):
                store, _ = self.store(rows=rows)
                with self.assertRaisesRegex(GitStateStoreError, message):
                    store.read_snapshot()
        store, _ = self.store(returncode=1)
        with self.assertRaises(GitStateStoreError):
            store.read_snapshot()


if __name__ == "__main__":
    unittest.main(verbosity=2)
