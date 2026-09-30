"""Fixed-snapshot record and file queries (``core_engine._query_record``, ``ResearchRepository.query``), layer 2.

The file query runs the real ``ResearchRepository`` on the Git port's
in-process fake (설계 4.3). The record query over a whole instance
(``query_records``, ``read_record``) opens the real Git backend itself and is in
``boundary/test_storage_record_queries.py``.
"""
from pathlib import Path
import tempfile
import unittest

from do_math.core_engine import _query_record
from do_math.planning import RECORD_FAMILIES
from do_math.repository import RepositoryCursorError
from research_fixtures import current_state
from support.storage_records import record_store

PREFIX = "runtime/artifacts/query-fixture/"


class QueryFamilyNameTests(unittest.TestCase):
    def test_query_family_names_are_the_condition_grammar_names(self):
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
    def test_file_cursor_reuses_old_snapshot_and_malformed_cursor_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = record_store(Path(directory))
            instance, runtime = current_state({"title": "query fixture"})
            head = repository.initialize(instance, runtime)
            file_head = repository.save_with_state(head, instance, runtime, artifacts={
                PREFIX + "a.txt": b"needle alpha", PREFIX + "b.txt": b"needle beta"})[0]
            first = repository.query(snapshot=file_head, prefix=PREFIX, text="needle", limit=1)
            # The head advances, so a cursor that followed the current head would be told apart.
            _, instance, runtime = repository.load(file_head)
            instance["title"] = "later query fixture"
            later = repository.save_with_state(file_head, instance, runtime)[0]
            self.assertNotEqual(later, file_head)
            resumed = repository.query(prefix=PREFIX, text="needle", limit=10, cursor=first["next_cursor"])
            self.assertEqual(resumed["snapshot"], file_head)
            self.assertEqual([item["path"] for item in resumed["items"]], [PREFIX + "b.txt"])
            with self.assertRaisesRegex(RepositoryCursorError, "^cursor is malformed$"):
                repository.query(prefix=PREFIX, cursor="%%%")
            empty = repository.query(snapshot=file_head, prefix=PREFIX, text="missing", limit=1)
            self.assertEqual(empty["total"], 0)
            self.assertEqual(empty["items"], [])
            self.assertFalse(empty["truncated"])


if __name__ == "__main__":
    unittest.main()
