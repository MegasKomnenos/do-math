"""The installed skill must work without its author's repository documents."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import formal


class StandaloneTests(unittest.TestCase):
    def test_shallow_installation_without_lean_reports_unavailable(self):
        shallow = Path(Path.cwd().anchor) / "do-math/scripts/do_math/formal.py"
        with patch.object(formal, "__file__", str(shallow)), patch.object(formal.shutil, "which", return_value=None):
            self.assertIsNone(formal.discover_lean())


if __name__ == "__main__":
    unittest.main()
