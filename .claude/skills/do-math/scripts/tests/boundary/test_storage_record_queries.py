"""Record queries over one published instance (``query_records``, ``read_record``), over the real Git process.

Both functions open the repository themselves with the product's default
backend, the real Git process, and take no Ports; that places these tests with
the boundary tests, as ``test_lifecycle_engine_record_query`` is placed. The
instance comes from the public ``initialize``, then knowledge records and a
relation are published through the repository (``engine_fixtures.start_query_repository``,
which patches nothing and checks that the initial head loads as itself).
"""
import hashlib
import unittest

from do_math.engine import query_records, read_record
from do_math.knowledge_io import import_candidate
from engine_fixtures import QUERY_INSTANCE_ID, start_query_repository


class QueryRecordTests(unittest.TestCase):
    def setUp(self):
        start_query_repository(self)

    def test_record_cursor_reuses_its_old_snapshot_after_head_advances(self):
        first = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, limit=1)
        self.assertEqual(first["snapshot"], self.old_head)
        self.assertTrue(first["truncated"])

        _, instance, runtime = self.repository.load(self.file_head)
        instance, runtime, third = import_candidate(instance, runtime,
            {"kind": "question", "title": "Three", "statement": "new", "summary": "new",
             "explanation": "A later query record", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref=QUERY_INSTANCE_ID, actor_ref=QUERY_INSTANCE_ID)
        later = self.repository.save_with_state(self.file_head, instance, runtime)[0]
        self.assertNotEqual(later, self.file_head)  # the head advanced past the snapshots already published

        resumed = query_records(self.git, QUERY_INSTANCE_ID, cursor=first["next_cursor"], limit=10)
        self.assertEqual(resumed["snapshot"], self.old_head)
        self.assertNotIn(third, {item["record"]["id"] for item in resumed["items"]})

    def test_relations_direction_hash_and_absent_record(self):
        outgoing = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[0],
                                 direction="outgoing", limit=10)
        self.assertEqual({item["record"]["id"] for item in outgoing["items"]}, {self.kids[1], self.relation_id})
        incoming = query_records(self.git, QUERY_INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[1],
                                 direction="incoming", limit=10)
        self.assertEqual({item["record"]["id"] for item in incoming["items"]}, {self.kids[0], self.relation_id})
        record = read_record(self.git, QUERY_INSTANCE_ID, self.kids[0], snapshot=self.old_head)
        self.assertEqual(record["sha256"],
                         hashlib.sha256(self.repository.read(record["path"], self.old_head)).hexdigest())
        self.assertNotIn("summary", record["record"])
        exposition = read_record(self.git, QUERY_INSTANCE_ID, record["record"]["exposition_id"], snapshot=self.old_head)
        self.assertTrue(any(item["text"] == "alpha" for item in exposition["record"]["items"]))
        with self.assertRaises(KeyError) as absent:
            read_record(self.git, QUERY_INSTANCE_ID, "K-absent", snapshot=self.old_head)
        self.assertEqual(absent.exception.args, ("record not found: K-absent",))


if __name__ == "__main__":
    unittest.main()
