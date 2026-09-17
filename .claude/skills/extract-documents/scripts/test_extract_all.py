# -*- coding: utf-8 -*-
"""extract_all.py의 실패 신호 검사. 직접 실행: python test_extract_all.py"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "extract_all.py"
sys.path.insert(0, str(HERE))
import extract_all  # noqa: E402


def run(*files):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, files)],
                          capture_output=True, text=True, encoding="utf-8")


class ExitCodeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_nonempty_text_succeeds(self):
        f = self.tmp / "ok.txt"
        f.write_text("본문", encoding="utf-8")
        self.assertEqual(run(f).returncode, 0)

    def test_missing_file_fails(self):
        self.assertNotEqual(run(self.tmp / "none.txt").returncode, 0)

    def test_empty_text_fails(self):
        f = self.tmp / "empty.txt"
        f.write_text("", encoding="utf-8")
        r = run(f)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("[오류]", r.stderr)

    def test_one_failure_among_many_still_outputs_others(self):
        ok = self.tmp / "ok.txt"
        ok.write_text("남는 본문", encoding="utf-8")
        r = run(ok, self.tmp / "none.txt")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("남는 본문", r.stdout)


class HwpTest(unittest.TestCase):
    def test_no_conversion_output_is_error(self):
        done = subprocess.CompletedProcess([], 1, "", "boom")
        with mock.patch.object(extract_all.subprocess, "run", return_value=done):
            with self.assertRaises(RuntimeError):
                extract_all.extract_hwp(Path("x.hwp"))


if __name__ == "__main__":
    unittest.main()
