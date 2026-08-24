# -*- coding: utf-8 -*-
"""vr.py 앵커 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_앵커.py`).

검사 대상은 다섯으로 한정한다:
① 파일 하나 — `<런>/앵커.<확장자>`로 뜨고 바이트가 원본과 같으며 stdout에 수치 요약이 난다
② 파일 여럿 — `<런>/앵커/` 아래 저장소 상대 경로 구조로 뜬다
③ 앵커가 이미 있으면 exit 1과 stderr 좌표(앵커는 읽기 전용 — SKILL.md §7 0단계)
④ 원본 파일 부재는 exit 2
⑤ 절대 경로 산출물은 exit 2(저장소 상대 경로 계약 — 구조 미러가 깨진다)

그 밖의 검사는 두지 않는다. 산출물 경로는 저장소 상대 경로이고 실행 좌표는 저장소 루트이므로,
시험은 임시 디렉토리를 루트 삼아 chdir하고 상대 경로를 준다.
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


class AnchorTest(unittest.TestCase):
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

    def 앵커실행(self, 산출물목록):
        동결쓰기("런/동결.md", 산출물목록)
        return run_vr("앵커", "--런", "런", "--동결", "런/동결.md")

    def test_파일_하나는_앵커_확장자로_뜬다(self):
        code, out, err = self.앵커실행(["산출물.md"])
        self.assertEqual(code, 0, err)
        dst = Path("런/앵커.md")
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_bytes(), Path("산출물.md").read_bytes())
        self.assertIn("1건", out)

    def test_파일_여럿은_앵커_디렉토리_구조로_뜬다(self):
        code, out, err = self.앵커실행(["산출물.md", "하위/둘째.md"])
        self.assertEqual(code, 0, err)
        self.assertTrue(Path("런/앵커/산출물.md").exists())
        self.assertTrue(Path("런/앵커/하위/둘째.md").exists())
        self.assertEqual(Path("런/앵커/하위/둘째.md").read_bytes(),
                         Path("하위/둘째.md").read_bytes())
        self.assertIn("2건", out)

    def test_앵커가_이미_있으면_exit1(self):
        code, _, _ = self.앵커실행(["산출물.md"])
        self.assertEqual(code, 0)
        code, out, err = self.앵커실행(["산출물.md"])
        self.assertEqual(code, 1)
        self.assertIn("앵커", err)

    def test_원본_부재는_exit2(self):
        code, out, err = self.앵커실행(["없는파일.md"])
        self.assertEqual(code, 2)

    def test_절대_경로는_exit2(self):
        code, out, err = self.앵커실행([str(self.tmp / "산출물.md")])
        self.assertEqual(code, 2)
        앵커들 = list(Path("런").glob("앵커*")) if Path("런").is_dir() else []
        self.assertEqual(앵커들, [])


if __name__ == "__main__":
    unittest.main()
