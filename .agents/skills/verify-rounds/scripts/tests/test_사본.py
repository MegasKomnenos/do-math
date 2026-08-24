# -*- coding: utf-8 -*-
"""vr.py 사본 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_사본.py`).

검사 대상은 넷으로 한정한다:
① 파일 하나 — `라운드N/`이 없으면 만들고 `라운드N/사본.<확장자>`로 뜨며 stdout에 수치 요약이 난다
② 파일 여럿 — `라운드N/사본/` 아래 저장소 상대 경로 구조로 뜬다
③ 재실행은 사본을 새 원본으로 덮는다(SKILL.md §4.4 라운드 재시작 경로)
④ 원본 파일 부재는 exit 2

그 밖의 검사는 두지 않는다. 시험은 임시 디렉토리를 루트 삼아 chdir하고 상대 경로를 준다.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import vr  # noqa: E402


def run_vr(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = vr.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 2
    return code, out.getvalue(), err.getvalue()


def 동결쓰기(경로: str, 산출물목록):
    """동결문의 최소 형태를 쓴다 — `## 산출물` 절의 `- <경로>` 줄이 산출물 목록의 정본이다."""
    lines = ["# 동결문", "", "## 산출물", ""] + [f"- {p}" for p in 산출물목록]
    Path(경로).parent.mkdir(parents=True, exist_ok=True)
    Path(경로).write_text("\n".join(lines) + "\n", encoding="utf-8")


class CopyTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        Path("산출물.md").write_text("본문 하나\n", encoding="utf-8")
        Path("하위").mkdir()
        Path("하위/둘째.md").write_text("본문 둘\n", encoding="utf-8")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def 사본실행(self, 라운드, 산출물목록):
        동결쓰기("런/동결.md", 산출물목록)
        return run_vr("사본", "--런", "런", "--라운드", str(라운드),
                      "--동결", "런/동결.md")

    def test_파일_하나는_라운드_디렉토리를_만들고_뜬다(self):
        code, out, err = self.사본실행(2, ["산출물.md"])
        self.assertEqual(code, 0, err)
        dst = Path("런/라운드2/사본.md")
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_bytes(), Path("산출물.md").read_bytes())
        self.assertIn("1건", out)

    def test_파일_여럿은_사본_디렉토리_구조로_뜬다(self):
        code, out, err = self.사본실행(1, ["산출물.md", "하위/둘째.md"])
        self.assertEqual(code, 0, err)
        self.assertTrue(Path("런/라운드1/사본/산출물.md").exists())
        self.assertTrue(Path("런/라운드1/사본/하위/둘째.md").exists())
        self.assertIn("2건", out)

    def test_재실행은_새_원본으로_덮는다(self):
        self.사본실행(1, ["산출물.md"])
        Path("산출물.md").write_text("고친 본문\n", encoding="utf-8")
        code, out, err = self.사본실행(1, ["산출물.md"])
        self.assertEqual(code, 0, err)
        self.assertEqual(Path("런/라운드1/사본.md").read_text(encoding="utf-8"), "고친 본문\n")

    def test_원본_부재는_exit2(self):
        code, out, err = self.사본실행(1, ["없는파일.md"])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
