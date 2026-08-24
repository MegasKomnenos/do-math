# -*- coding: utf-8 -*-
"""vr.py 영역검산 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_영역검산.py`).

검사 대상은 열로 한정한다:
① 통과 — 영역들의 합집합 = 산출물 전건, 비중첩이면 exit 0과 영역별 수치 stdout
② 빠진 구간 — exit 1과 stderr 좌표(파일·행 구간)
③ 겹친 구간 — exit 1과 stderr 좌표
④ frontmatter `영역: <N>`과 실측 영역 절 수의 어긋남 — exit 1
⑤ 명세의 닫힌 서식 위반(구간 줄도 축자 줄도 아닌 줄) — exit 1
⑥ 명세가 사본에 대응하지 않는 경로를 지목 — exit 1
⑦ 0행 파일의 전체 파일 구간 — 유효한 빈 구간으로 통과
⑧ 재정박 확장 명세(시작·끝 축자 줄)의 수용 — 축자 줄은 구간 부속으로 무시된다
⑨ 원본 경로와 사본 경로의 대응 — 사본이 `사본/` 아래 디렉토리 구조여도 원본 경로로 검산한다
⑩ 동결문 산출물 목록의 파일에 대응 사본이 없음 — exit 2
그 밖의 검사는 두지 않는다. 명세 서식의 정본은 vr.py 영역검산 docstring이다.
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


def write(path: str, text: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def 동결쓰기(경로: str, 산출물목록):
    """동결문의 최소 형태를 쓴다 — `## 산출물` 절의 `- <경로>` 줄이 산출물 목록의 정본이다."""
    lines = ["# 동결문", "", "## 산출물", ""] + [f"- {p}" for p in 산출물목록]
    write(경로, "\n".join(lines) + "\n")


class AreaCheckTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        write("산출물.md", "1행\n2행\n3행\n4행\n")            # 4행
        write("하위/둘째.md", "a\nb\nc\nd\ne\nf\n")           # 6행

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def check(self, spec: str, 산출물목록=("산출물.md", "하위/둘째.md")):
        # 사본 경로는 인자가 아니라 런·라운드·동결문 산출물 목록에서 파생한다.
        write("명세.md", spec)
        동결쓰기("런/동결.md", 산출물목록)
        for p in 산출물목록:
            write(f"런/라운드1/사본/{p}", Path(p).read_text(encoding="utf-8"))
        return run_vr("영역검산", "--런", "런", "--라운드", "1",
                      "--동결", "런/동결.md", "--명세", "명세.md")

    def test_합집합이_전건이고_비중첩이면_통과(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n- 하위/둘째.md 행 1-3\n"
            "\n## 영역 2\n\n- 하위/둘째.md 행 4-6\n")
        self.assertEqual(code, 0, err)
        self.assertIn("영역 2", out)
        self.assertIn("2파일", out)
        self.assertIn("10행", out)

    def test_빠진_구간은_exit1(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n"
            "\n## 영역 2\n\n- 하위/둘째.md 행 1-3\n")
        self.assertEqual(code, 1)
        self.assertIn("하위/둘째.md", err)
        self.assertIn("4-6", err)

    def test_겹친_구간은_exit1(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n- 하위/둘째.md 행 1-4\n"
            "\n## 영역 2\n\n- 하위/둘째.md 행 3-6\n")
        self.assertEqual(code, 1)
        self.assertIn("하위/둘째.md", err)
        self.assertIn("3-4", err)

    def test_frontmatter_영역_수_불일치는_exit1(self):
        code, out, err = self.check(
            "---\n영역: 3\n---\n\n## 영역 1\n\n- 산출물.md\n"
            "\n## 영역 2\n\n- 하위/둘째.md\n")
        self.assertEqual(code, 1)
        self.assertIn("기대=3", err)
        self.assertIn("실측=2", err)

    def test_서식_위반_줄은_exit1(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n산출물.md\n"
            "\n## 영역 2\n\n- 하위/둘째.md\n")
        self.assertEqual(code, 1)
        self.assertIn("명세.md", err)

    def test_0행_파일의_전체_구간은_통과(self):
        write("빈파일.gitkeep", "")
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n- 빈파일.gitkeep\n"
            "\n## 영역 2\n\n- 하위/둘째.md\n",
            ("산출물.md", "하위/둘째.md", "빈파일.gitkeep"))
        self.assertEqual(code, 0, err)
        self.assertIn("3파일", out)
        self.assertIn("10행", out)

    def test_사본_밖_경로_지목은_exit1(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n- 셋째.md\n"
            "\n## 영역 2\n\n- 하위/둘째.md\n")
        self.assertEqual(code, 1)
        self.assertIn("셋째.md", err)

    def test_재정박_확장_명세를_수용한다(self):
        code, out, err = self.check(
            "---\n영역: 2\n---\n\n## 영역 1\n\n- 산출물.md\n- 하위/둘째.md 행 1-3\n"
            "  시작 축자: a\n  끝 축자: c\n"
            "\n## 영역 2\n\n- 하위/둘째.md 행 4-6\n"
            "  시작 축자: d\n  끝 축자: f\n")
        self.assertEqual(code, 0, err)
        self.assertIn("10행", out)

    def test_사본_부재는_exit2(self):
        # 사본 경로를 파생하므로 `사본` 하위명령을 먼저 돌리지 않으면 쓸 사본이 없다.
        write("명세.md",
              "---\n영역: 1\n---\n\n## 영역 1\n\n- 산출물.md\n")
        동결쓰기("런/동결.md", ["산출물.md", "하위/둘째.md"])
        code, out, err = run_vr("영역검산", "--런", "런", "--라운드", "1",
                                "--동결", "런/동결.md", "--명세", "명세.md")
        self.assertEqual(code, 2)
        self.assertIn("사본", err)


if __name__ == "__main__":
    unittest.main()
