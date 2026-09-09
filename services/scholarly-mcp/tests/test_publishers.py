import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PublisherContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "publishers.py").exists():
            raise AssertionError("Publisher document adapters are absent")
        cls.mod = importlib.import_module("publishers")

    def test_citation_metadata_keeps_repeated_authors_and_separate_dates(self):
        raw = '<meta name="citation_title" content="A theorem"><meta name="citation_author" content="One"><meta name="citation_author" content="Two"><meta name="citation_publication_date" content="2020"><meta name="citation_online_date" content="2019"><meta name="citation_doi" content="10.1007/example">'
        metadata = self.mod.publication_metadata(raw)
        self.assertEqual(metadata["citation_author"], ["One", "Two"])
        self.assertEqual(metadata["citation_publication_date"], ["2020"])
        self.assertEqual(metadata["citation_online_date"], ["2019"])

    def test_pdf_selection_uses_document_metadata_not_related_paper_links(self):
        raw = '<meta name="citation_pdf_url" content="/article/current.pdf"><a href="/references/other.pdf">PDF</a>'
        links = self.mod.primary_pdf_links(raw, "https://link.springer.com/article/current")
        self.assertEqual(links, ["https://link.springer.com/article/current.pdf"])


if __name__ == "__main__":
    unittest.main()
