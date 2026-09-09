import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class IEEEContract(unittest.TestCase):
    def test_source_document_range_and_abstract_are_preserved(self):
        self.assertTrue((ROOT / "ieee.py").exists(), "IEEE adapter is absent")
        mod = importlib.import_module("ieee")
        raw = json.loads((ROOT / "tests/fixtures/ieee-search.json").read_text("utf-8"))
        rows, total, offset = mod.ieee_records(raw)
        self.assertEqual((len(rows), total, offset), (1, 1, 0))
        self.assertEqual(rows[0]["articleNumber"], "10488889")
        self.assertIn("zero knowledge", rows[0]["abstract"])


if __name__ == "__main__":
    unittest.main()
