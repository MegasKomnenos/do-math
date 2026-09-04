import csv
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


BASELINE_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = BASELINE_ROOT / "scripts" / "build_b001_catalog.py"
SPEC = importlib.util.spec_from_file_location("build_b001_catalog", MODULE_PATH)
build_b001 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_b001)


class BibTeXParsingTests(unittest.TestCase):
    def test_tolerates_unbalanced_brace_inside_ignored_abstract(self):
        text = """@inproceedings{10.1/example,
author = {Example, Ada},
title = {A Useful Result},
year = {2025},
abstract = {A malformed formula {x}}} remains here.},
doi = {10.1/example},
booktitle = {Proceedings}
}
"""

        records = build_b001.parse_bibtex_tolerant(text, source_name="sample.bib")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["key"], "10.1/example")
        self.assertEqual(records[0]["fields"]["title"], ["A Useful Result"])
        self.assertEqual(records[0]["fields"]["doi"], ["10.1/example"])

    def test_splits_adjacent_ieee_entries_without_blank_line(self):
        text = """@ARTICLE{1,
 title={First},
 year={2001},}@INPROCEEDINGS{2,
 title={Second},
 year={2002},}
"""

        records = build_b001.parse_bibtex_tolerant(text, source_name="ieee.bib")

        self.assertEqual([record["key"] for record in records], ["1", "2"])
        self.assertEqual(records[1]["fields"]["title"], ["Second"])


class RisParsingTests(unittest.TestCase):
    def test_repeated_tags_and_continuation_lines_are_preserved(self):
        text = """TY  - JOUR
AU  - Example, Ada
AU  - Sample, Bob
TI  - A title
AB  - first line
continuation
PY  - 2020
DO  - 10.1/example
ER  - 
"""

        records = build_b001.parse_ris(text, source_name="sample.ris")

        self.assertEqual(records[0]["fields"]["au"], ["Example, Ada", "Sample, Bob"])
        self.assertEqual(records[0]["fields"]["ab"], ["first line\ncontinuation"])
        self.assertEqual(records[0]["fields"]["ti"], ["A title"])

    def test_ris_serial_and_book_numbers_are_not_duplicated(self):
        record = {
            "fields": {
                "ty": ["JOUR"],
                "ti": ["A title"],
                "au": ["Example, Ada"],
                "py": ["2020"],
                "ut": ["WOS:1"],
                "sn": ["0022-0000", "978-1-2345-6789-0"],
            },
            "parsed_record_sha256": "a" * 64,
        }

        occurrence = build_b001._ris_occurrence(record, "wos")

        self.assertEqual(occurrence["bibliographic"]["issn"], ["0022-0000"])
        self.assertEqual(occurrence["bibliographic"]["isbn"], ["978-1-2345-6789-0"])


class ScopusParsingTests(unittest.TestCase):
    def test_csv_record_keeps_identifier_but_only_flags_abstract_and_references(self):
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "EID",
                "Title",
                "Authors",
                "Author full names",
                "Year",
                "DOI",
                "Abstract",
                "References",
                "Document Type",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "EID": "2-s2.0-1",
                "Title": "A result",
                "Authors": "Example A.; Sample B.",
                "Author full names": "Example, Ada (123); Sample, Bob (456)",
                "Year": "2020",
                "DOI": "10.1/example",
                "Abstract": "Licensed abstract text",
                "References": "Long reference list",
                "Document Type": "Article",
            }
        )
        stream.seek(0)

        records = list(build_b001.parse_scopus_csv(stream, source_name="sample.csv"))

        record = records[0]
        self.assertEqual(record["source_record_id"], "2-s2.0-1")
        self.assertEqual(record["bibliographic"]["authors"], ["Example, Ada", "Sample, Bob"])
        self.assertTrue(record["abstract_present"])
        self.assertTrue(record["references_present"])
        serialized = json.dumps(record)
        self.assertNotIn("Licensed abstract text", serialized)
        self.assertNotIn("Long reference list", serialized)


class NormalizationAndAggregationTests(unittest.TestCase):
    def test_search_signals_record_locations_without_copying_text(self):
        signals = build_b001.detect_search_signals(
            title="A survey",
            abstract="We study whether P = NP using proof complexity.",
            keywords=["circuit complexity"],
        )

        self.assertEqual(signals["direct_p_vs_np"], ["abstract"])
        self.assertEqual(signals["proof_complexity"], ["abstract"])
        self.assertEqual(signals["circuit_complexity"], ["keywords"])
        self.assertNotIn("We study", json.dumps(signals))

    def test_doi_extraction_handles_url_escape_and_multiple_values(self):
        value = "https://doi.org/10.1007/test\\_1; DOI 10.1145/123.456."
        self.assertEqual(
            build_b001.extract_dois(value),
            ["10.1007/test_1", "10.1145/123.456"],
        )

    def test_doi_extraction_preserves_legacy_sici_semicolon_suffix(self):
        value = "10.1002/(SICI)1521-4001(199807)78:7<441::AID-ZAMM441>3.0.CO;2-V"
        self.assertEqual(
            build_b001.extract_dois(value),
            ["10.1002/(sici)1521-4001(199807)78:7<441::aid-zamm441>3.0.co;2-v"],
        )

    def test_same_source_identifier_aggregates_occurrences_without_losing_provenance(self):
        occurrences = [
            {
                "source_id": "scopus",
                "source_record_id": "2-s2.0-1",
                "entry_type": "article",
                "bibliographic": {
                    "title": "A result",
                    "authors": ["Example, Ada"],
                    "year": "2020",
                    "doi": ["10.1/example"],
                },
                "abstract_present": True,
                "references_present": True,
                "search_signals": {"direct_p_vs_np": ["title"]},
                "parsed_record_sha256": "a" * 64,
                "provenance": {"query_id": "S01", "rank": 1},
            },
            {
                "source_id": "scopus",
                "source_record_id": "2-s2.0-1",
                "entry_type": "article",
                "bibliographic": {
                    "title": "A result",
                    "authors": ["Example, Ada"],
                    "year": "2020",
                    "doi": ["10.1/example"],
                },
                "abstract_present": True,
                "references_present": True,
                "search_signals": {"proof_complexity": ["abstract"]},
                "parsed_record_sha256": "b" * 64,
                "provenance": {"query_id": "S02", "rank": 4},
            },
        ]

        candidates = build_b001.aggregate_candidates(occurrences)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["occurrence_count"], 2)
        self.assertEqual([p["query_id"] for p in candidates[0]["provenance"]], ["S01", "S02"])
        self.assertEqual(len(candidates[0]["parsed_record_sha256s"]), 2)
        self.assertEqual(candidates[0]["review_routing"], "direct_p_vs_np_signal")
        self.assertEqual(
            candidates[0]["search_signals"],
            {"direct_p_vs_np": ["title"], "proof_complexity": ["abstract"]},
        )

    def test_output_candidate_does_not_copy_abstract_or_reference_text(self):
        occurrence = {
            "source_id": "wos",
            "source_record_id": "WOS:1",
            "entry_type": "article",
            "bibliographic": {
                "title": "A result",
                "authors": ["Example, Ada"],
                "year": "2020",
                "doi": ["10.1/example"],
            },
            "abstract_present": True,
            "references_present": True,
            "search_signals": {},
            "parsed_record_sha256": "a" * 64,
            "provenance": {"query_id": "W01", "rank": 1},
        }

        candidate = build_b001.aggregate_candidates([occurrence])[0]
        text = json.dumps(candidate)

        self.assertTrue(candidate["content_flags"]["abstract_present"])
        self.assertTrue(candidate["content_flags"]["references_present"])
        self.assertNotIn("abstract_text", text)
        self.assertNotIn("references_text", text)

    def test_direct_title_queue_clusters_sources_by_doi_and_excludes_abstract_only(self):
        def item(candidate_id, doi, locations):
            return {
                "candidate_id": candidate_id,
                "source_id": candidate_id.split("-")[1],
                "source_record_id": candidate_id,
                "entry_type": "article",
                "bibliographic": {"title": "P versus NP", "venue": "Venue"},
                "normalized": {
                    "title": "p versus np",
                    "year": 2020,
                    "creators": ["example ada"],
                    "dois": [doi] if doi else [],
                },
                "search_signals": {"direct_p_vs_np": locations},
                "review_routing": "direct_p_vs_np_signal",
                "provenance": [{"query_id": "A01", "rank": 1}],
            }

        queue = build_b001.build_direct_title_queue(
            [
                item("B001-ACM-1", "10.1/same", ["title"]),
                item("B001-WOS-2", "10.1/same", ["title", "abstract"]),
                item("B001-SCOPUS-3", "", ["abstract"]),
            ]
        )

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["signal"], {"doi": "10.1/same"})
        self.assertEqual(queue[0]["member_count"], 2)
        self.assertEqual(
            [member["candidate_id"] for member in queue[0]["members"]],
            ["B001-ACM-1", "B001-WOS-2"],
        )

    def test_direct_axis_queue_requires_abstract_direct_signal_and_named_axis(self):
        base = {
            "source_id": "scopus",
            "source_record_id": "id",
            "entry_type": "article",
            "bibliographic": {"title": "A lower bound", "venue": "Venue"},
            "normalized": {
                "title": "a lower bound",
                "year": 2020,
                "creators": ["example ada"],
                "dois": ["10.1/axis"],
            },
            "review_routing": "direct_p_vs_np_signal",
            "provenance": [{"query_id": "S01", "rank": 1}],
        }
        accepted = dict(
            base,
            candidate_id="B001-SCOPUS-1",
            search_signals={
                "direct_p_vs_np": ["abstract"],
                "proof_complexity": ["title", "abstract"],
            },
        )
        no_axis = dict(
            base,
            candidate_id="B001-SCOPUS-2",
            source_record_id="id2",
            search_signals={"direct_p_vs_np": ["abstract"]},
        )
        title_direct = dict(
            base,
            candidate_id="B001-SCOPUS-3",
            source_record_id="id3",
            search_signals={
                "direct_p_vs_np": ["title", "abstract"],
                "proof_complexity": ["abstract"],
            },
        )

        queue = build_b001.build_direct_axis_queue([accepted, no_axis, title_direct])

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["member_count"], 1)
        self.assertEqual(queue[0]["members"][0]["named_axes"], ["proof_complexity"])

    def test_barrier_title_queue_selects_priority_axis_titles_without_direct_signal(self):
        base = {
            "source_id": "scopus",
            "source_record_id": "id",
            "entry_type": "article",
            "bibliographic": {"title": "Natural proofs", "venue": "JCSS"},
            "normalized": {
                "title": "natural proofs",
                "year": 1997,
                "creators": ["example ada"],
                "dois": ["10.1/natural"],
            },
            "review_routing": "named_complexity_axis_signal",
            "provenance": [{"query_id": "S02", "rank": 1}],
        }
        selected = dict(
            base,
            candidate_id="B001-SCOPUS-1",
            search_signals={"natural_proofs": ["title", "abstract"]},
        )
        abstract_only = dict(
            base,
            candidate_id="B001-SCOPUS-2",
            source_record_id="id2",
            search_signals={"natural_proofs": ["abstract"]},
        )

        queue = build_b001.build_barrier_title_queue([selected, abstract_only])

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["member_count"], 1)
        self.assertEqual(queue[0]["members"][0]["title_axes"], ["natural_proofs"])


class RealCorpusTests(unittest.TestCase):
    def test_actual_b001_manifest_and_all_records_load(self):
        manifest = BASELINE_ROOT / "manifests" / "B001.json"
        if not manifest.exists():
            self.skipTest("B001 manifest is absent")

        corpus = build_b001.load_corpus(BASELINE_ROOT, manifest)

        self.assertEqual(len(corpus["occurrences"]), 20746)
        self.assertEqual(
            corpus["source_counts"],
            {
                "acm-dl": 2175,
                "ieee-xplore": 64,
                "mathscinet": 500,
                "pqdt": 218,
                "scopus": 15659,
                "wos": 2130,
            },
        )
        self.assertEqual(corpus["artifact_mismatches"], 0)

    def test_review_material_is_recovered_from_provenance_rank(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "intake" / "sample.csv"
            path.parent.mkdir(parents=True)
            path.write_text(
                "EID,Title,Abstract,Author Keywords,Index Keywords,Document Type\n"
                'first,First,"not this one",,,Article\n'
                'second,Second,"P versus NP context",proof complexity,,Article\n',
                encoding="utf-8",
            )
            candidate_record = {
                "candidate_id": "B001-SCOPUS-test",
                "source_id": "scopus",
                "source_record_id": "second",
                "provenance": [
                    {"path": "intake/sample.csv", "rank": 2, "query_id": "S01"}
                ],
            }

            material = build_b001.load_review_material(root, candidate_record)

        self.assertEqual(material["title"], "Second")
        self.assertEqual(material["abstract"], "P versus NP context")
        self.assertEqual(material["keywords"], ["proof complexity"])


if __name__ == "__main__":
    unittest.main()
