"""wait_outputs 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_wait_outputs.py`).

검사 대상은 다섯으로 한정한다:
① 인자 경로 전건이 비어 있지 않은 파일로 섬 — exit 0
② 인자 경로 하나 이상이 부재 — exit 3
③ 크기 0인 파일 — exit 3
④ 디렉토리 인자 — 항목 유무와 관계없이 exit 3
⑤ 인자 없음 — exit 2
그 밖의 검사는 두지 않는다.
"""

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import wait_outputs


class TestWaitOutputs(unittest.TestCase):
    def setUp(self):
        self._interval = wait_outputs.INTERVAL
        wait_outputs.INTERVAL = 0
        self.addCleanup(setattr, wait_outputs, "INTERVAL", self._interval)
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root = pathlib.Path(d.name)

    def test_전건_실재면_0(self):
        p = self.root / "a.md"
        p.write_text("x", encoding="utf-8")
        self.assertEqual(wait_outputs.main([str(p)]), 0)

    def test_하나라도_없으면_3(self):
        p = self.root / "a.md"
        p.write_text("x", encoding="utf-8")
        self.assertEqual(
            wait_outputs.main([str(p), str(self.root / "없다.md")]), 3)

    def test_빈_파일은_3(self):
        p = self.root / "비었다.md"
        p.touch()
        self.assertEqual(wait_outputs.main([str(p)]), 3)

    def test_빈_디렉토리는_3(self):
        d = self.root / "빈디렉토리"
        d.mkdir()
        self.assertEqual(wait_outputs.main([str(d)]), 3)

    def test_항목을_담은_디렉토리도_3(self):
        d = self.root / "찬디렉토리"
        d.mkdir()
        (d / "a.md").write_text("x", encoding="utf-8")
        self.assertEqual(wait_outputs.main([str(d)]), 3)

    def test_인자_없으면_2(self):
        self.assertEqual(wait_outputs.main([]), 2)


if __name__ == "__main__":
    unittest.main()
