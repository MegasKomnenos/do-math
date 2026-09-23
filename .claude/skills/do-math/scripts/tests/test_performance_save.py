"""Repository save-with-state contract on fresh, real Git repositories."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.git_store import GitStateStoreConflict  # noqa: E402
from do_math.repository import ResearchRepository  # noqa: E402


INSTANCE_ID = "RI-00000000000000000000000000"


class SaveWithStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository_path = self.root / "repository"
        self.repository_path.mkdir()
        subprocess.run(["git", "-C", str(self.repository_path), "init", "-q"], check=True)
        self.repository = ResearchRepository(self.repository_path, INSTANCE_ID)
        self.initial_head = self.repository.initialize(
            {"feature_version": 5, "title": "instance"},
            {"feature_version": 5, "status": "initializing"},
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_unchanged_state_is_noop_and_returns_normalized_reload_views(self) -> None:
        head, instance, runtime = self.repository.load()
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, runtime)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        self.assertEqual(saved_head, head)
        self.assertEqual((saved_head, saved_instance, saved_runtime),
                         (reloaded_head, reloaded_instance, reloaded_runtime))

    def test_changed_state_writes_the_same_canonical_files_and_returns_reload_views(self) -> None:
        head, instance, runtime = self.repository.load()
        changed_runtime = {**runtime, "status": "active"}
        expected = self.repository.validate_candidate(instance, changed_runtime, head)
        saved_head, saved_instance, saved_runtime = self.repository.save_with_state(head, instance, changed_runtime)
        stored = self.repository._store.read_many(saved_head, sorted(expected["files"]))
        self.assertNotEqual(saved_head, head)
        self.assertEqual(stored, expected["files"])
        self.assertEqual((saved_head, saved_instance, saved_runtime), self.repository.load(saved_head))

    def test_regular_save_still_rejects_invalid_input(self) -> None:
        head, instance, runtime = self.repository.load()
        invalid_runtime = {**runtime, "status": float("nan")}
        with self.assertRaises(ValueError):
            self.repository.save(head, instance, invalid_runtime)
        self.assertEqual(self.repository.load()[0], head)

    def test_save_reads_parent_family_bytes_once_and_preserves_reload_equivalence(self) -> None:
        head, instance, runtime = self.repository.load()
        with patch.object(self.repository._store, 'read_many', wraps=self.repository._store.read_many) as reads:
            saved = self.repository.save_with_state(head, instance, {**runtime, 'status': 'active'})
        self.assertEqual(len([call for call in reads.call_args_list if call.args[0] == head]), 1)
        self.assertEqual(saved, self.repository.load(saved[0]))

    def test_reused_parent_bytes_still_reject_a_damaged_previous_snapshot(self) -> None:
        head, instance, runtime = self.repository.load()
        damaged = self.repository._store.publish(head, {'runtime/_state/metadata.json': b'{}\n'}).head
        with patch.object(self.repository._store, 'publish', wraps=self.repository._store.publish) as publish:
            with self.assertRaises(ValueError):
                self.repository.save_with_state(damaged, instance, runtime)
        publish.assert_not_called()
        self.assertEqual(self.repository._store.read_snapshot().head, damaged)

    def test_stale_parent_loser_does_not_publish(self) -> None:
        head, instance, runtime = self.repository.load()
        other = ResearchRepository(self.repository_path, INSTANCE_ID)
        winner, _, _ = self.repository.save_with_state(head, instance, {**runtime, "status": "winner"})
        with self.assertRaises(GitStateStoreConflict):
            other.save_with_state(head, instance, {**runtime, "status": "loser"})
        self.assertEqual(self.repository.load()[0], winner)
        self.assertEqual(self.repository.load(winner)[2]["status"], "winner")

    def test_stale_head_is_rejected_before_artifact_shape(self) -> None:
        head, instance, runtime = self.repository.load()
        self.repository.save_with_state(head, instance, {**runtime, "status": "winner"})
        with self.assertRaises(GitStateStoreConflict):
            self.repository.save_with_state(
                head, instance, runtime, artifacts={"outside-artifacts.txt": b"not allowed"}
            )

    def test_artifact_bytes_and_namespace_are_checked_by_the_same_save_call(self) -> None:
        head, instance, runtime = self.repository.load()
        artifact_path = "runtime/artifacts/AB-01/output.txt"
        artifact_bytes = b"sealed artifact bytes"
        saved_head, _, _ = self.repository.save_with_state(
            head, instance, runtime, artifacts={artifact_path: artifact_bytes}
        )
        self.assertEqual(self.repository.read(artifact_path, saved_head), artifact_bytes)
        reloaded_head, reloaded_instance, reloaded_runtime = self.repository.load(saved_head)
        with self.assertRaises(ValueError):
            self.repository.save_with_state(
                reloaded_head,
                deepcopy(reloaded_instance),
                deepcopy(reloaded_runtime),
                artifacts={"outside-artifacts.txt": b"not allowed"},
            )
        self.assertEqual(self.repository.load()[0], saved_head)


if __name__ == "__main__":
    unittest.main(verbosity=2)
