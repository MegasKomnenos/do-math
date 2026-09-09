import importlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PQDTContract(unittest.TestCase):
    def test_document_id_is_not_the_dissertation_publication_number(self):
        self.assertTrue((ROOT / "pqdt.py").exists(), "PQDT adapter is absent")
        mod = importlib.import_module("pqdt")
        rows, total = mod.pqdt_records((ROOT / "tests/fixtures/pqdt-result.html").read_text("utf-8"), "https://www.proquest.com/")
        self.assertEqual(total, 1)
        self.assertEqual(rows[0]["id"], "2618193239")
        self.assertIn("Resource Bounded Measure", rows[0]["title"])


if __name__ == "__main__":
    unittest.main()
