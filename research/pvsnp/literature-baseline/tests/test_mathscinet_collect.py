import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "mathscinet_collect.py"
)
SPEC = importlib.util.spec_from_file_location("mathscinet_collect", MODULE_PATH)
mathscinet_collect = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mathscinet_collect)


VALID_BIB = """@book {MR1,
    author = {Example, Ada},
    title = {An example},
    year = {2024},
    mrclass = {00-01 (00-02)}
}
"""


class QueryPlanTests(unittest.TestCase):
    def test_load_queries_preserves_leading_zero_and_builds_fielded_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            table = Path(tmp) / "queries.tsv"
            table.write_text(
                "field_code\tfield_name\tquery\n"
                "00\tGeneral\t00-01 OR 00-02\n"
                "01\tHistory\t01-00 OR 01-01 OR 01-02\n",
                encoding="utf-8",
            )
            queries = mathscinet_collect.load_queries(table)

        self.assertEqual([item.field_code for item in queries], ["00", "01"])
        self.assertEqual(queries[0].mathscinet_query, "pcsc:(00-01 OR 00-02)")

    def test_pending_queries_skip_valid_existing_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            table = tmp_path / "queries.tsv"
            table.write_text(
                "field_code\tfield_name\tquery\n"
                "00\tGeneral\t00-01 OR 00-02\n"
                "01\tHistory\t01-00 OR 01-01 OR 01-02\n",
                encoding="utf-8",
            )
            output = tmp_path / "out"
            (output / "00").mkdir(parents=True)
            (output / "00" / "export").write_text(VALID_BIB, encoding="utf-8")
            (output / "01").mkdir(parents=True)

            pending, skipped = mathscinet_collect.plan_queries(
                mathscinet_collect.load_queries(table), output
            )

        self.assertEqual([item.field_code for item in pending], ["01"])
        self.assertEqual(skipped, ["00"])

    def test_invalid_existing_export_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            table = tmp_path / "queries.tsv"
            table.write_text(
                "field_code\tfield_name\tquery\n"
                "00\tGeneral\t00-01 OR 00-02\n",
                encoding="utf-8",
            )
            output = tmp_path / "out"
            (output / "00").mkdir(parents=True)
            (output / "00" / "export").write_text("broken", encoding="utf-8")

            with self.assertRaises(mathscinet_collect.ExistingOutputError):
                mathscinet_collect.plan_queries(
                    mathscinet_collect.load_queries(table), output
                )


class CredentialTests(unittest.TestCase):
    def test_credentials_are_parsed_but_never_exposed_by_repr(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kudos.md"
            path.write_text(
                "# KUDOS\n- 로그인 페이지: https://example.test\n"
                "- ID: student123\n- PW: secret456\n",
                encoding="utf-8",
            )
            credentials = mathscinet_collect.load_credentials(path)

        self.assertEqual(credentials.user_id, "student123")
        self.assertEqual(credentials.password, "secret456")
        self.assertNotIn("student123", repr(credentials))
        self.assertNotIn("secret456", repr(credentials))


class OutputTests(unittest.TestCase):
    def test_validate_bibtex_checks_record_count_and_requested_msc(self):
        result = mathscinet_collect.validate_bibtex(
            VALID_BIB, expected_codes=("00-01", "00-02"), expected_count=1
        )
        self.assertEqual(result.record_count, 1)
        self.assertEqual(result.matched_count, 1)

        with self.assertRaises(mathscinet_collect.OutputValidationError):
            mathscinet_collect.validate_bibtex(
                VALID_BIB, expected_codes=("03-01",), expected_count=1
            )

    def test_atomic_store_writes_validated_text_without_partial_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "05" / "mathscinet.bib"
            mathscinet_collect.atomic_store(target, VALID_BIB)
            self.assertEqual(target.read_text(encoding="utf-8"), VALID_BIB)
            self.assertFalse(target.with_suffix(".bib.tmp").exists())


class BrowserContractTests(unittest.TestCase):
    def test_search_url_fixes_query_page_size_sort_and_order(self):
        query = mathscinet_collect.Query(
            field_code="05",
            field_name="Combinatorics",
            raw_query="05-00 OR 05-01 OR 05-02",
        )
        url = mathscinet_collect.build_search_url(query)
        self.assertIn(
            "query=pcsc%3A%2805-00+OR+05-01+OR+05-02%29", url
        )
        self.assertIn("page=1", url)
        self.assertIn("size=100", url)
        self.assertIn("sort=citations", url)
        self.assertIn("order=desc", url)

    def test_extract_mathscinet_target_from_kudos_database_block(self):
        html = """
        <div class="db-tit">
          <b class="subject">MathSciNet</b>
          <a href="javascript:popup_gourl('https://mathscinet.ams.org/mathscinet')">바로가기</a>
        </div>
        """
        self.assertEqual(
            mathscinet_collect.extract_mathscinet_target(html),
            "https://mathscinet.ams.org/mathscinet",
        )


if __name__ == "__main__":
    unittest.main()
