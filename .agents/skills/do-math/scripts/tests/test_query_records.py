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

from do_math.engine import CONTRACT, initialize, query_records, read_record, _repository  # noqa: E402
from do_math.repository import RepositoryCursorError, ResearchRepository, canonical_json
from do_math.knowledge_io import (import_candidate, import_relation, register_kind_definition,
    check_kind_definition, activate_kind_definition, relation_templates)  # noqa: E402


INSTANCE_ID = "RI-00000000000000000000000000"


class QueryRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git = self.root / "git"
        self.git.mkdir()
        subprocess.run(["git", "-C", str(self.git), "init", "-q"], check=True)
        self.workspace = self.root / "workspace"
        initialized = initialize(self.git, goal="A goal", workspace=self.workspace, instance_id=INSTANCE_ID,
                                 config={"operator_enabled": False, "scholarly_enabled": False})
        self.repository = _repository(self.git, INSTANCE_ID)
        self.initial_head = initialized["snapshot"]
        head, instance, runtime = self.repository.load(self.initial_head)
        self.assertEqual(head, self.initial_head)
        self.kids = []
        for title, kind, summary in (("One", "definition", "alpha"), ("Two", "theorem", "beta")):
            instance, runtime, kid = import_candidate(instance, runtime,
                {"kind": kind, "title": title, "statement": summary, "summary": summary,
                 "explanation": "Explicit query fixture: " + summary, "lean_code": "",
                 "declaration_names": [], "dependencies": []}, source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID)
            self.kids.append(kid)
        definition = next(row for row in relation_templates() if row['token'] == 'supports')
        instance, _ = register_kind_definition(instance, definition, source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID)
        check_ref = 'runtime/artifacts/query-kind/check.json'
        approval_ref = 'runtime/artifacts/query-kind/approval.json'
        instance = check_kind_definition(instance, 'relation', 'supports', check_ref=check_ref, actor_ref=INSTANCE_ID)
        instance = activate_kind_definition(instance, 'relation', 'supports', approval_ref=approval_ref, actor_ref=INSTANCE_ID)
        instance, self.relation_id = import_relation(instance,
            {"kind": "supports", "source": self.kids[0], "target": self.kids[1], "evidence": "alpha"},
            source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID)
        self.old_head = self.repository.save_with_state(self.initial_head, instance, runtime, artifacts={
            check_ref: canonical_json({'definition': definition, 'verdict': 'checked',
                'scope': 'Explicit CORE_TESTS kind-check fixture'}),
            approval_ref: canonical_json({'definition': definition, 'decision': 'activate',
                'scope': 'Explicit CORE_TESTS fixture; not actual user approval'}),
        })[0]
        self.file_head = self.repository.save_with_state(self.old_head, instance, runtime, artifacts={
            "runtime/artifacts/query-fixture/a.txt": b"needle alpha",
            "runtime/artifacts/query-fixture/b.txt": b"needle beta",
        })[0]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_record_cursor_reuses_its_old_snapshot_after_head_advances(self) -> None:
        first = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, limit=1)
        self.assertEqual(first["snapshot"], self.old_head)
        self.assertTrue(first["truncated"])

        _, instance, runtime = self.repository.load(self.file_head)
        instance, runtime, third = import_candidate(instance, runtime,
            {"kind": "question", "title": "Three", "statement": "new", "summary": "new",
             "explanation": "A later query record", "lean_code": "", "declaration_names": [], "dependencies": []},
            source_ref=INSTANCE_ID, actor_ref=INSTANCE_ID)
        self.repository.save_with_state(self.file_head, instance, runtime)[0]

        resumed = query_records(self.git, INSTANCE_ID, cursor=first["next_cursor"], limit=10)
        self.assertEqual(resumed["snapshot"], self.old_head)
        self.assertNotIn(third, {item["record"]["id"] for item in resumed["items"]})

    def test_relations_direction_hash_and_absent_record(self) -> None:
        outgoing = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[0], direction="outgoing", limit=10)
        self.assertEqual({item["record"]["id"] for item in outgoing["items"]}, {self.kids[1], self.relation_id})
        incoming = query_records(self.git, INSTANCE_ID, snapshot=self.old_head, related_to=self.kids[1], direction="incoming", limit=10)
        self.assertEqual({item["record"]["id"] for item in incoming["items"]}, {self.kids[0], self.relation_id})
        record = read_record(self.git, INSTANCE_ID, self.kids[0], snapshot=self.old_head)
        self.assertEqual(record["sha256"], hashlib.sha256(self.repository.read(record["path"], self.old_head)).hexdigest())
        self.assertNotIn("summary", record["record"])
        exposition = read_record(self.git, INSTANCE_ID, record["record"]["exposition_id"], snapshot=self.old_head)
        self.assertTrue(any(item["text"] == "alpha" for item in exposition["record"]["items"]))
        with self.assertRaises(KeyError):
            read_record(self.git, INSTANCE_ID, "K-absent", snapshot=self.old_head)

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
