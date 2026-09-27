"""Fixed-snapshot record and file query checks without model execution."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from do_math.engine import _query_record, query_records, read_record  # noqa: E402
from do_math.planning import RECORD_FAMILIES
from do_math.repository import RepositoryCursorError
from do_math.knowledge_io import import_candidate
from engine_fixtures import QUERY_INSTANCE_ID, start_query_repository


class QueryFamilyNameTests(unittest.TestCase):
    def test_query_family_names_are_the_condition_grammar_names(self) -> None:
        for name, (_, stored) in RECORD_FAMILIES.items():
            if stored is not None:
                with self.subTest(stored=stored):
                    # A kind definition's own "family" field moves to definition_family.
                    row = {"family": stored, "record": {"id": "X", "family": "relation"}}
                    self.assertEqual(_query_record(row)["family"], name)
        self.assertEqual(_query_record({"family": "question_links", "record": {"id": "Q"}})["family"], "question")
        # A stored family the grammar does not name keeps its stored name.
        self.assertEqual(_query_record({"family": "capability_evidence", "record": {"id": "C"}})["family"],
                         "capability_evidence")


class QueryRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        start_query_repository(self)

    def test_record_cursor_reuses_its_old_snapshot_after_head_advances(self) -> None:
        first = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, limit=1)
        self.assertEqual(first["snapshot"], self.old_head)
        self.assertTrue(first["truncated"])

        _, instance, runtime = self.repository.load(self.file_head)
        instance, runtime, third = import_candidate(instance, runtime,
            {"kind": "question", "title": "Three", "statement": "new", "summary": "new",
             "explanation": "A later query record", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID)
        self.repository.save_with_state(self.file_head, instance, runtime)[0]

        resumed = query_records(self.git, QUERY_INSTANCE_ID, cursor=first["next_cursor"], limit=10)
        self.assertEqual(resumed["snapshot"], self.old_head)
        self.assertNotIn(third, {item["record"]["id"] for item in resumed["items"]})

    def test_relations_direction_hash_and_absent_record(self) -> None:
        outgoing = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[0], direction="outgoing", limit=10)
        self.assertEqual({item["record"]["id"] for item in outgoing["items"]}, {self.kids[1], self.relation_id})
        incoming = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[1], direction="incoming", limit=10)
        self.assertEqual({item["record"]["id"] for item in incoming["items"]}, {self.kids[0], self.relation_id})
        record = read_record(self.git, QUERY_INSTANCE_ID, self.kids[0], snapshot=self.old_head)
        self.assertEqual(record["sha256"], hashlib.sha256(self.repository.read(record["path"], self.old_head)).hexdigest())
        self.assertNotIn("summary", record["record"])
        exposition = read_record(self.git, QUERY_INSTANCE_ID, record["record"]["exposition_id"], snapshot=self.old_head)
        self.assertTrue(any(item["text"] == "alpha" for item in exposition["record"]["items"]))
        with self.assertRaises(KeyError):
            read_record(self.git, QUERY_INSTANCE_ID, "K-absent", snapshot=self.old_head)

    def test_file_cursor_reuses_old_snapshot_and_malformed_cursor_is_error(self) -> None:
        first = self.repository.query(snapshot=self.file_head, prefix="runtime/artifacts/query-fixture/", text="needle", limit=1)
        _, instance, runtime = self.repository.load(self.file_head)
        self.repository.save_with_state(self.file_head, instance, runtime)[0]
        resumed = self.repository.query(prefix="runtime/artifacts/query-fixture/", text="needle", limit=10, cursor=first["next_cursor"])
        self.assertEqual(resumed["snapshot"], self.file_head)
        self.assertEqual([item["path"] for item in resumed["items"]], ["runtime/artifacts/query-fixture/b.txt"])
        with self.assertRaises(RepositoryCursorError):
            self.repository.query(prefix="runtime/artifacts/query-fixture/", cursor="%%%");
        empty = self.repository.query(snapshot=self.file_head, prefix="runtime/artifacts/query-fixture/", text="missing", limit=1)
        self.assertEqual(empty["total"], 0)
        self.assertEqual(empty["items"], [])
        self.assertFalse(empty["truncated"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
