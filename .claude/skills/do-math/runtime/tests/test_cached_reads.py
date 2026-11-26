"""Files the runner reads on every pass (runtime_support.read_json_cached).

The runner draws the board and checks every active session on each pass, and for that it reads each
session's declaration, end check and process receipt. Most of them have not changed since the pass
before, so a file is opened and parsed again only when it has changed. These tests fix that a change
is always seen, that a path which is no file reads as None, and that callers cannot disturb one
another through what they are given.
"""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import coordination
import runtime_support
from runtime_support import read_json_cached, write_json


class CachedReads(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "declaration.json"
        runtime_support._JSON_SEEN.clear()
        self.reads = 0
        real = runtime_support.read_json

        def counted(path):
            self.reads += 1
            return real(path)

        patcher = patch.object(runtime_support, "read_json", counted)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_an_unchanged_file_is_opened_once(self):
        write_json(self.path, {"sections": [1, 2]})
        for _ in range(5):
            self.assertEqual(read_json_cached(self.path), {"sections": [1, 2]})
        self.assertEqual(self.reads, 1)

    def test_a_replaced_file_is_read_again(self):
        write_json(self.path, {"sections": [1]})
        self.assertEqual(read_json_cached(self.path), {"sections": [1]})
        seen = os.stat(self.path)
        write_json(self.path, {"sections": [2]})  # another file of the same size under the same name
        # A replacement can carry the timestamp of the version before it (runtime_support.file_stamp); here it does.
        os.utime(self.path, ns=(seen.st_atime_ns, seen.st_mtime_ns))
        self.assertEqual(read_json_cached(self.path), {"sections": [2]})
        self.assertEqual(self.reads, 2)

    def test_a_file_rewritten_in_place_with_another_size_is_read_again(self):
        self.path.write_text('{"a": 1}', encoding="utf-8")
        self.assertEqual(read_json_cached(self.path), {"a": 1})
        self.path.write_text('{"a": 1, "b": 2}', encoding="utf-8")
        self.assertEqual(read_json_cached(self.path), {"a": 1, "b": 2})

    def test_no_file_reads_as_none_and_a_later_file_is_seen(self):
        self.assertIsNone(read_json_cached(self.path))
        self.assertIsNone(read_json_cached(self.folder))  # a folder is no file
        self.assertIsNone(read_json_cached(self.folder / "missing" / "declaration.json"))
        write_json(self.path, {"sections": []})
        self.assertEqual(read_json_cached(self.path), {"sections": []})
        os.remove(self.path)
        self.assertIsNone(read_json_cached(self.path))
        write_json(self.path, {"sections": [3]})
        self.assertEqual(read_json_cached(self.path), {"sections": [3]})

    def test_what_one_caller_changes_another_does_not_see(self):
        write_json(self.path, {"sections": [{"element": "E"}]})
        first = read_json_cached(self.path)
        first["sections"][0]["element"] = "changed"
        first["extra"] = True
        self.assertEqual(read_json_cached(self.path), {"sections": [{"element": "E"}]})

    def test_a_file_that_does_not_parse_raises_as_read_json_does(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_json_cached(self.path)

    def test_the_board_reads_a_declaration_through_it(self):
        instance = self.folder / "instance"
        session = instance / "sessions" / "s1"
        session.mkdir(parents=True)
        model = {"elements": {"E": {}, "F": {}}, "questions": {"q0": {}}, "question_aliases": {}}
        self.assertEqual(coordination.section_entries(instance, "s1", model), [])
        self.assertIsNone(coordination.question_entry(instance, "s1", model))
        self.assertEqual(coordination.section_entries(instance, "", model), [])
        write_json(session / "declaration.json", {"sections": [{"element": "E", "at": 1}, {"element": "gone", "at": 2}],
                                                 "question": {"id": "q0"}})
        for _ in range(3):
            self.assertEqual(coordination.section_entries(instance, "s1", model),
                             [{"element": "E", "at": 1, "session": "s1"}])
            self.assertEqual(coordination.question_entry(instance, "s1", model), {"id": "q0", "session": "s1"})
        self.assertEqual(self.reads, 1)
        write_json(session / "declaration.json", {"sections": [{"element": "E", "at": 1}, {"element": "F", "at": 3}]})
        self.assertEqual([row["element"] for row in coordination.section_entries(instance, "s1", model)], ["E", "F"])
        self.assertIsNone(coordination.question_entry(instance, "s1", model))


if __name__ == "__main__":
    unittest.main()
