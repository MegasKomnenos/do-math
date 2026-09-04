import importlib.util
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "build_b002_catalog.py"
SPEC = importlib.util.spec_from_file_location("build_b002_catalog", MODULE_PATH)
build_b002_catalog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_b002_catalog)


NESTED_BIB = r'''@book {MR1,
    AUTHOR = {G{\"o}del, Kurt and {de la Vall{\'e}e Poussin}, Charles},
     TITLE = {A {T}itle with {Nested {Groups}} and {$\alpha$}},
      NOTE = {A comma, and {a nested, comma}},
      YEAR = {2001},
   MRCLASS = {03-01 (03-02)},
  MRNUMBER = {1},
       DOI = {https://doi.org/10.1000/ABC},
}
'''


def make_entry(mr_number, *, title="Foundations", year=2000, doi=None,
               edition=None, entry_type="book"):
    fields = [
        ("author", "Example, Ada"),
        ("title", title),
        ("year", str(year)),
        ("mrclass", "00-01"),
        ("mrnumber", str(mr_number)),
    ]
    if doi is not None:
        fields.append(("doi", doi))
    if edition is not None:
        fields.append(("edition", edition))
    return build_b002_catalog.BibEntry(
        entry_type=entry_type,
        key=f"MR{mr_number}",
        field_items=tuple(fields),
        raw_text=f"fixture-MR{mr_number}",
    )


def make_occurrence(entry, field_code, rank):
    return build_b002_catalog.Occurrence(
        entry=entry,
        provenance={
            "source_id": "mathscinet",
            "batch_id": "B002",
            "field_code": field_code,
            "field_name": f"Field {field_code}",
            "query": f"pcsc:({field_code}-01)",
            "rank": rank,
            "path": f"intake/B002/mathscinet/{field_code}/fixture.bib",
            "artifact_sha256": "a" * 64,
            "collection_method": "fixture",
            "retrieved_at": None,
        },
    )


class BibTeXParserTests(unittest.TestCase):
    def test_nested_braces_multiline_fields_and_trailing_comma_parse(self):
        entries = build_b002_catalog.parse_bibtex(
            NESTED_BIB, source_name="nested.bib"
        )

        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.entry_type, "book")
        self.assertEqual(entry.key, "MR1")
        self.assertEqual(entry.field_values("note"),
                         ("A comma, and {a nested, comma}",))
        self.assertEqual(entry.field_values("mrnumber"), ("1",))
        self.assertEqual(entry.field_items[0][0], "author")

    def test_parser_rejects_unbalanced_values_but_preserves_duplicate_fields(self):
        with self.assertRaises(build_b002_catalog.BibTeXError):
            build_b002_catalog.parse_bibtex(
                "@book {MR1, title={Unclosed}\n", source_name="broken.bib"
            )

        duplicate = """@book {MR1,
          title={One}, edition={Second}, edition={Russian}, year={2000},
          mrclass={00-01}, mrnumber={1}}
        """
        entry = build_b002_catalog.parse_bibtex(
            duplicate, source_name="duplicate.bib"
        )[0]
        self.assertEqual(entry.field_values("edition"), ("Second", "Russian"))
        build_b002_catalog.validate_entry(entry, source_name="duplicate.bib")
        candidate = build_b002_catalog.aggregate_candidates(
            [make_occurrence(entry, "00", 1)]
        )[0]
        self.assertEqual(candidate["duplicate_fields"], {"edition": 2})

        duplicate_required = duplicate.replace(
            "title={One}", "title={One}, title={Two}"
        )
        required_entry = build_b002_catalog.parse_bibtex(
            duplicate_required, source_name="duplicate-required.bib"
        )[0]
        with self.assertRaises(build_b002_catalog.CorpusError):
            build_b002_catalog.validate_entry(
                required_entry, source_name="duplicate-required.bib"
            )

    def test_mathscinet_extra_title_brace_is_preserved_as_a_recovery(self):
        recovered = r'''@book {MR603624,
          title={{\cyr Chast\cprime {}}}},
          year={1980}, mrclass={40-01}, mrnumber={603624}}
        '''
        entry = build_b002_catalog.parse_bibtex(
            recovered, source_name="mathscinet-recovery.bib"
        )[0]

        self.assertEqual(entry.field_values("title"),
                         (r"{\cyr Chast\cprime {}}}",))
        self.assertIn("extra_closing_brace:title", entry.parse_warnings)
        candidate = build_b002_catalog.aggregate_candidates(
            [make_occurrence(entry, "40", 1)]
        )[0]
        self.assertEqual(candidate["parse_warnings"],
                         ["extra_closing_brace:title"])

    def test_decorated_mathscinet_year_is_derived_without_losing_raw_value(self):
        decorated = make_entry(4539628)
        decorated = build_b002_catalog.BibEntry(
            decorated.entry_type,
            decorated.key,
            tuple(
                (name, r"[2023] \copyright 2023" if name == "year" else value)
                for name, value in decorated.field_items
            ),
            decorated.raw_text,
        )
        build_b002_catalog.validate_entry(decorated, source_name="decorated.bib")
        normalized = build_b002_catalog.normalize_entry(decorated)

        self.assertEqual(normalized["year"], 2023)
        self.assertIn("noncanonical_year", normalized["normalization_warnings"])

    def test_missing_year_is_preserved_as_a_missing_link_signal(self):
        missing = make_entry(1351209)
        missing = build_b002_catalog.BibEntry(
            missing.entry_type,
            missing.key,
            tuple(
                (name, "" if name == "year" else value)
                for name, value in missing.field_items
            ),
            missing.raw_text,
        )
        build_b002_catalog.validate_entry(missing, source_name="missing-year.bib")
        normalized = build_b002_catalog.normalize_entry(missing)

        self.assertIsNone(normalized["year"])
        self.assertIn("missing_year", normalized["normalization_warnings"])

    def test_required_fields_and_mr_key_are_validated(self):
        entry = make_entry(2)
        build_b002_catalog.validate_entry(entry, source_name="valid.bib")

        wrong_number = build_b002_catalog.BibEntry(
            entry.entry_type,
            entry.key,
            tuple(
                (name, "3" if name == "mrnumber" else value)
                for name, value in entry.field_items
            ),
            entry.raw_text,
        )
        with self.assertRaises(build_b002_catalog.CorpusError):
            build_b002_catalog.validate_entry(wrong_number, source_name="wrong.bib")


class NormalizationTests(unittest.TestCase):
    def test_tex_title_people_doi_and_year_have_stable_derived_values(self):
        entry = build_b002_catalog.parse_bibtex(
            NESTED_BIB, source_name="nested.bib"
        )[0]
        normalized = build_b002_catalog.normalize_entry(entry)

        self.assertEqual(
            normalized["title"], "a title with nested groups and alpha"
        )
        self.assertEqual(normalized["creator_role"], "author")
        self.assertEqual(
            normalized["creators"],
            ["gödel kurt", "de la vallée poussin charles"],
        )
        self.assertEqual(normalized["year"], 2001)
        self.assertEqual(normalized["dois"], ["10.1000/abc"])

    def test_long_tex_commands_are_not_misread_as_one_letter_accents(self):
        normalized, unknown = build_b002_catalog.normalize_text(
            r"{\cyr Chast\cprime}"
        )

        self.assertEqual(normalized, "cyr chast cprime")
        self.assertEqual(unknown, {"cyr", "cprime"})

    def test_legacy_doi_semicolon_is_part_of_the_identifier(self):
        value = "10.1002/(SICI)1521-4001(199807)78:7<441::AID-ZAMM441>3.0.CO;2-V"

        self.assertEqual(
            build_b002_catalog.normalize_doi(value),
            [value.casefold()],
        )

    def test_bibtex_escaped_underscore_is_unescaped_in_doi(self):
        value = r"10.1007/978-3-642-58175-5\_1"

        self.assertEqual(
            build_b002_catalog.normalize_doi(value),
            ["10.1007/978-3-642-58175-5_1"],
        )


class AggregationAndRelationTests(unittest.TestCase):
    def test_same_mr_is_one_candidate_with_every_occurrence(self):
        entry = make_entry(10)
        candidates = build_b002_catalog.aggregate_candidates(
            [
                make_occurrence(entry, "00", 1),
                make_occurrence(entry, "68", 7),
            ]
        )

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["candidate_id"], "MR10")
        self.assertEqual(
            [(p["field_code"], p["rank"]) for p in candidates[0]["provenance"]],
            [("00", 1), ("68", 7)],
        )

    def test_conflicting_payload_for_same_mr_is_rejected(self):
        with self.assertRaises(build_b002_catalog.CorpusError):
            build_b002_catalog.aggregate_candidates(
                [
                    make_occurrence(make_entry(10, title="First"), "00", 1),
                    make_occurrence(make_entry(10, title="Second"), "68", 7),
                ]
            )

    def test_distinct_mr_records_remain_and_relation_groups_are_candidates(self):
        occurrences = [
            make_occurrence(
                make_entry(20, doi="10.1000/SAME", entry_type="book"), "00", 1
            ),
            make_occurrence(
                make_entry(21, doi="https://doi.org/10.1000/same",
                           entry_type="article"),
                "03", 2,
            ),
            make_occurrence(
                make_entry(22, year=2001, edition="Second"), "05", 3
            ),
        ]
        candidates = build_b002_catalog.aggregate_candidates(occurrences)
        relations = build_b002_catalog.build_relation_groups(candidates)

        self.assertEqual([item["candidate_id"] for item in candidates],
                         ["MR20", "MR21", "MR22"])
        by_type = {item["relation_type"]: item for item in relations}
        self.assertEqual(by_type["same_doi_candidate"]["members"],
                         ["MR20", "MR21"])
        self.assertEqual(
            by_type["same_bibliographic_fingerprint_candidate"]["members"],
            ["MR20", "MR21"],
        )
        self.assertEqual(by_type["edition_or_version_candidate"]["members"],
                         ["MR20", "MR21", "MR22"])


class RealCorpusTests(unittest.TestCase):
    def test_all_b002_occurrences_parse_and_keep_contiguous_field_ranks(self):
        manifest = BASELINE_ROOT / "manifests" / "B002.json"
        intake = BASELINE_ROOT / "intake" / "B002" / "mathscinet"
        if not manifest.exists() or not intake.exists():
            self.skipTest("gitignored B002 intake is not present")

        corpus = build_b002_catalog.load_corpus(BASELINE_ROOT, manifest)
        candidates = build_b002_catalog.aggregate_candidates(corpus.occurrences)

        self.assertEqual(len(corpus.occurrences), 6233)
        self.assertEqual(len(candidates), 5472)
        by_field = {}
        for occurrence in corpus.occurrences:
            code = occurrence.provenance["field_code"]
            by_field.setdefault(code, []).append(occurrence.provenance["rank"])
        for ranks in by_field.values():
            self.assertEqual(ranks, list(range(1, len(ranks) + 1)))


if __name__ == "__main__":
    unittest.main()
