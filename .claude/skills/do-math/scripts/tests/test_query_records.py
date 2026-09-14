"""Fixed-snapshot record and file query checks without model execution."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.engine import CONTRACT, initialize, query_records, read_record  # noqa: E402
from do_math.repository import RepositoryCursorError, ResearchRepository, canonical_json  # noqa: E402


INSTANCE_ID = "RI-00000000000000000000000000"


class QueryRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git = self.root / "git"
        self.git.mkdir()
        subprocess.run(["git", "-C", str(self.git), "init", "-q"], check=True)
        self.workspace = self.root / "workspace"
        initialized = initialize(self.git, goal="A goal", workspace=self.workspace, instance_id=INSTANCE_ID)
        self.repository = ResearchRepository(self.git, INSTANCE_ID)
        self.initial_head = initialized["snapshot"]
        head, instance, runtime = self.repository.load(self.initial_head)
        self.assertEqual(head, self.initial_head)
        instance["knowledge"] = {
            "K-01": {"id": "K-01", "kind": "definition", "title": "One", "summary": "alpha", "status": "verified"},
            "K-02": {"id": "K-02", "kind": "theorem", "title": "Two", "summary": "beta", "status": "candidate"},
        }
        instance["relations"] = [{"id": "RL-01", "kind": "supports", "source": "K-01", "target": "K-02", "evidence": "alpha"}]
        runtime["tasks"] = {"T-01": {"id": "T-01", "title": "Task", "status": "planned"}}
        self.old_head = self.repository.save(self.initial_head, instance, runtime)
        self.repository._store.publish(self.old_head, {
            "research/a.txt": b"needle alpha",
            "research/b.txt": b"needle beta",
        })
        self.file_head = self.repository._store.read_snapshot().head

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_record_cursor_reuses_its_old_snapshot_after_head_advances(self) -> None:
        first = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, limit=1)
        self.assertEqual(first["snapshot"], self.old_head)
        self.assertTrue(first["truncated"])

        _, instance, runtime = self.repository.load(self.file_head)
        instance["knowledge"]["K-03"] = {"id": "K-03", "kind": "question", "title": "Three", "summary": "new", "status": "candidate"}
        self.repository.save(self.file_head, instance, runtime)

        resumed = query_records(self.git, INSTANCE_ID, cursor=first["next_cursor"], limit=10)
        self.assertEqual(resumed["snapshot"], self.old_head)
        self.assertNotIn("K-03", {item["record"]["id"] for item in resumed["items"]})

    def test_relations_direction_hash_and_absent_record(self) -> None:
        outgoing = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, related_to="K-01", direction="outgoing", limit=10)
        self.assertEqual({item["record"]["id"] for item in outgoing["items"]}, {"K-02", "RL-01"})
        incoming = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, related_to="K-02", direction="incoming", limit=10)
        self.assertEqual({item["record"]["id"] for item in incoming["items"]}, {"K-01", "RL-01"})
        record = read_record(self.git, INSTANCE_ID, "K-01", snapshot=self.old_head)
        self.assertEqual(record["sha256"], hashlib.sha256(canonical_json(record["record"])).hexdigest())
        with self.assertRaises(KeyError):
            read_record(self.git, INSTANCE_ID, "K-absent", snapshot=self.old_head)

    def test_file_cursor_reuses_old_snapshot_and_malformed_cursor_is_error(self) -> None:
        first = self.repository.query(snapshot=self.file_head, prefix="research/", text="needle", limit=1)
        _, instance, runtime = self.repository.load(self.file_head)
        self.repository.save(self.file_head, instance, runtime)
        resumed = self.repository.query(prefix="research/", text="needle", limit=10, cursor=first["next_cursor"])
        self.assertEqual(resumed["snapshot"], self.file_head)
        self.assertEqual([item["path"] for item in resumed["items"]], ["research/b.txt"])
        with self.assertRaises(RepositoryCursorError):
            self.repository.query(prefix="research/", cursor="%%%");
        empty = self.repository.query(snapshot=self.file_head, prefix="research/", text="missing", limit=1)
        self.assertEqual(empty["total"], 0)
        self.assertEqual(empty["items"], [])
        self.assertFalse(empty["truncated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
