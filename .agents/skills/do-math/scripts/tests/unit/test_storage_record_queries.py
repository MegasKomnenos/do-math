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
from support.doc_code import documents, field_schemas, scoped_field_issues, unowned_field_references
from support.state_builders import current_state
from support.storage_records import record_store

PREFIX = "runtime/artifacts/query-fixture/"


class QueryFamilyNameTests(unittest.TestCase):
    def test_query_family_names_are_the_condition_grammar_names(self):
        skill = Path(__file__).resolve().parents[3]
        texts = [(document.relative_to(skill).as_posix(), document.read_text(encoding='utf-8'))
                 for document in documents(skill)]
        schemas = field_schemas()

        def field_issues(text, record):
            actual = {**schemas, 'query_record': {
                'type': 'object', 'properties': {key: {} for key in record},
                'additionalProperties': False}}
            return scoped_field_issues(text, actual, defer_status=True,
                                       defer_operation_progress=True, defer_query_result=True,
                                       defer_continuations=('result_source', 'rejected_response', 'previous_output_files'),
                                       defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),
                                       defer_operational_inputs=('operational_evidence', 'recovery_materials'),
                                       defer_role_inputs=('input_manifest', 'prompt', 'documents', 'profile_selection'),
                                       defer_cli_results=('init_result', 'scheduling_result', 'selection_result'), defer_tool_inputs=('execution_window', 'scholarly', 'formal_verifier', 'preview', 'record_map.read_tool', 'submission_contract'))

        alias = '`record.family` <!-- do-math fields: record=query_record -->'
        for name, (_, stored) in RECORD_FAMILIES.items():
            if stored is not None:
                with self.subTest(stored=stored):
                    # A kind definition's own "family" field moves to definition_family.
                    row = {"family": stored, "record": {"id": "X", "family": "relation"}}
                    record = _query_record(row)
                    self.assertEqual(record["family"], name)
                    self.assertEqual([(path, *issue) for path, text in texts
                                      for issue in field_issues(text, record)], [])
                    self.assertEqual(field_issues('`query_record.family`', record), [])
                    self.assertEqual(field_issues(alias, record), [])
                    omitted = dict(record)
                    del omitted['family']
                    self.assertEqual(field_issues(alias, omitted), [('scoped field', 'record.family')])
                    self.assertIn(('references/CLI-실행-계약.md', 'scoped field', 'record.family'),
                        [(path, *issue) for path, text in texts for issue in field_issues(text, omitted)])
        self.assertEqual(unowned_field_references(alias + '\n`record.family`', schemas), ['record.family'])
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
