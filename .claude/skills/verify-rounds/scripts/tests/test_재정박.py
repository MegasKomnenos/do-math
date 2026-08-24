# -*- coding: utf-8 -*-
"""vr.py 재정박 하위명령 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_재정박.py`).

검사 대상은 여섯으로 한정한다:
① 통과 — 시작·끝 축자가 라운드 사본에서 각 1회 나오면 exit 0, stdout에 구간별 「a-b → a2-b2」 수치, `라운드N/_재정박.json`에 바뀐 행 번호
② 축자 없음 — exit 1과 stderr 좌표
③ 축자 2회 이상 — exit 1과 stderr 좌표
④ 명세 결손(행 범위 구간에 시작·끝 축자 줄이 없음) — exit 1과 stderr 좌표
⑤ frontmatter `영역: <N>`과 실측 영역 절 수의 어긋남 — exit 1
⑥ 행 범위 구간 0건 — exit 0과 「재정박 0구간」 수치
그 밖의 검사는 두지 않는다. 확장 명세 서식의 정본은 vr.py 재정박 docstring이다.
시험은 임시 디렉토리를 루트 삼아 chdir하고 상대 경로를 준다.
"""

from __future__ import annotations

import contextlib
import io
import json
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


def write(path: str, text: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


COPY = "머리말\n1절 첫 행\n본문 하나\n1절 끝 행\n2절 첫 행\n본문 둘\n2절 끝 행\n꼬리\n"


class ReanchorTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        write("산출물.md", COPY)
        write("런/라운드2/사본.md", COPY)
        # 산출물 하나면 사본 경로 파생값이 `라운드N/사본.<확장자>`다.
        write("런/동결.md", "# 동결문\n\n## 산출물\n\n- 산출물.md\n")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def check(self, spec: str):
        write("명세.md", spec)
        return run_vr("재정박", "--런", "런", "--라운드", "2",
                      "--동결", "런/동결.md", "--명세", "명세.md")

    def test_통과가_행_번호를_바꾸고_json을_쓴다(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md 행 10-13\n"
            "  시작 축자: 1절 첫 행\n  끝 축자: 1절 끝 행\n"
            "\n## 영역 2\n\n- 산출물.md 행 14-16\n"
            "  시작 축자: 2절 첫 행\n  끝 축자: 2절 끝 행\n")
        self.assertEqual(code, 0, err)
        self.assertIn("10-13 → 2-4", out)
        self.assertIn("14-16 → 5-7", out)
        self.assertIn("재정박 2구간", out)
        data = json.loads(Path("런/라운드2/_재정박.json").read_text(encoding="utf-8"))
        spans = [sp for area in data["영역"] for sp in area["구간"]]
        self.assertEqual([sp["라운드행"] for sp in spans], [[2, 4], [5, 7]])

    def test_축자_없음은_exit1(self):
        code, out, err = self.check(
            "---\n영역: 1\n---\n\n## 영역 1\n\n- 산출물.md 행 10-13\n"
            "  시작 축자: 없는 행\n  끝 축자: 1절 끝 행\n")
        self.assertEqual(code, 1)
        self.assertIn("없는 행", err)

    def test_축자_2회_이상은_exit1(self):
        write("런/라운드2/사본.md", COPY + "1절 첫 행\n")
        code, out, err = self.check(
            "---\n영역: 1\n---\n\n## 영역 1\n\n- 산출물.md 행 10-13\n"
            "  시작 축자: 1절 첫 행\n  끝 축자: 1절 끝 행\n")
        self.assertEqual(code, 1)
        self.assertIn("1절 첫 행", err)
        self.assertIn("2회", err)

    def test_행_범위_구간에_축자_줄이_없으면_exit1(self):
        code, out, err = self.check(
            "---\n영역: 1\n---\n\n## 영역 1\n\n- 산출물.md 행 10-13\n"
            "  시작 축자: 1절 첫 행\n")
        self.assertEqual(code, 1)
        self.assertIn("명세.md", err)
        self.assertIn("끝 축자", err)

    def test_frontmatter_영역_수_불일치는_exit1(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md 행 10-13\n"
            "  시작 축자: 1절 첫 행\n  끝 축자: 1절 끝 행\n")
        self.assertEqual(code, 1)
        self.assertIn("기대=2", err)
        self.assertIn("실측=1", err)

    def test_행_범위_0건은_0구간_수치로_통과(self):
        code, out, err = self.check(
            "---\n영역: 1\n---\n\n## 영역 1\n\n- 산출물.md\n")
        self.assertEqual(code, 0, err)
        self.assertIn("재정박 0구간", out)


if __name__ == "__main__":
    unittest.main()
