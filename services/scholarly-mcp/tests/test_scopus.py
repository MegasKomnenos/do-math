import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ScopusContract(unittest.TestCase):
    def test_primary_documents_are_not_confused_with_preprint_counts(self):
        self.assertTrue((ROOT / "scopus.py").exists(), "Scopus adapter is absent")
        mod = importlib.import_module("scopus")
        payload = json.loads((ROOT / "tests/fixtures/scopus-primary.json").read_text("utf-8"))
        records, total, offset = mod.scopus_records(payload)
        self.assertEqual(total, 21)
        self.assertEqual(offset, 0)
        self.assertEqual(len(records), 10)
        self.assertEqual(records[-1]["title"], "P versus NP and geometry")
        self.assertTrue(mod.primary_request({"query": 'TITLE("P versus NP")', "documentClassification": "primary"}, 'TITLE("P versus NP")'))
        self.assertFalse(mod.primary_request({"query": 'TITLE("P versus NP")', "documentClassification": "preprint"}, 'TITLE("P versus NP")'))

    def test_page_capacity_can_exceed_last_page_record_count(self):
        mod = importlib.import_module("scopus")
        payload = json.loads((ROOT / "tests/fixtures/scopus-single.json").read_text("utf-8"))
        rows, total, offset = mod.scopus_records(payload)
        self.assertEqual((len(rows), total, offset), (1, 1, 0))


if __name__ == "__main__":
    unittest.main()
