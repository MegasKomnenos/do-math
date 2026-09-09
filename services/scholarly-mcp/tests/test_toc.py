import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TOCContract(unittest.TestCase):
    def test_native_category_listing_and_additional_document_formats(self):
        self.assertTrue((ROOT / "toc.py").exists(), "Theory of Computing adapter is absent")
        mod = importlib.import_module("toc")
        rows = mod.catalog_records((ROOT / "tests/fixtures/toc-category.html").read_text("utf-8"), "https://theoryofcomputing.org/")
        self.assertEqual(rows[0]["id"], "gs010")
        self.assertEqual(rows[0]["year"], "2025")
        self.assertEqual(len(rows[0]["authors"]), 2)
        formats = mod.document_formats((ROOT / "tests/fixtures/toc-article.html").read_text("utf-8"), "https://theoryofcomputing.org/articles/gs010/")
        self.assertTrue({"pdf", "postscript", "source_zip", "bibtex", "abstract_text", "references_html"}.issubset(formats))


if __name__ == "__main__":
    unittest.main()
