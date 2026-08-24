# -*- coding: utf-8 -*-
"""vr.py 분할 하위명령 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_분할.py`).

검사 대상은 셋으로 한정한다:
① 통과 — 항목 5를 배치 2로 균등에 가깝게 가르고(3+2), 배치 파일 frontmatter `항목:`을 실측으로 새로 쓰며, 울타리 안 `## ` 줄을 항목 경계로 세지 않고, stdout에 배치별 항목 수·바이트
② frontmatter `항목:`과 실측 절 수의 어긋남 — exit 1
③ 배치수가 세울 수 있는 배치 수를 넘음(빈 배치 발생) — exit 1
그 밖의 검사는 두지 않는다. 새 절차의 분할은 병합 뒤의 심사 입력만 다루므로 묶음 인자가 없다.
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
import vrlib  # noqa: E402

입력 = (
    "---\n항목: 5\n---\n\n# 심사 대상 (라운드 1)\n\n머리글.\n\n"
    "## R1-01\n\n본문 하나. 울타리 실물:\n\n```\n## 울타리 안 가짜 절\n```\n\n"
    "## R1-02\n\n본문 둘.\n\n"
    "## R1-03\n\n본문 셋.\n\n"
    "## R1-04\n\n본문 넷.\n\n"
    "## R1-05\n\n본문 다섯.\n"
)


def run_vr(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = vr.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 2
    return code, out.getvalue(), err.getvalue()


class SplitTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        Path("심사대상.md").write_text(입력, encoding="utf-8")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_배치2_균등_분할과_frontmatter_갱신(self):
        code, out, err = run_vr("분할", "--파일", "심사대상.md", "--배치수", "2")
        self.assertEqual(code, 0, err)
        b1 = vrlib.read_text("심사대상_배치1.md")
        b2 = vrlib.read_text("심사대상_배치2.md")
        fm1, _ = vrlib.parse_frontmatter(b1)
        fm2, _ = vrlib.parse_frontmatter(b2)
        self.assertEqual(fm1.get("항목"), "3")
        self.assertEqual(fm2.get("항목"), "2")
        self.assertEqual([s.title for s in vrlib.split_sections(b1)],
                         ["R1-01", "R1-02", "R1-03"])
        self.assertEqual([s.title for s in vrlib.split_sections(b2)],
                         ["R1-04", "R1-05"])
        self.assertIn("## 울타리 안 가짜 절", b1)  # 울타리 축자 보존
        self.assertIn("배치1: 항목 3", out)
        self.assertIn("배치2: 항목 2", out)
        self.assertIn("바이트", out)

    def test_frontmatter_항목_불일치는_exit1(self):
        Path("심사대상.md").write_text(입력.replace("항목: 5", "항목: 6"),
                                   encoding="utf-8")
        code, out, err = run_vr("분할", "--파일", "심사대상.md", "--배치수", "2")
        self.assertEqual(code, 1)
        self.assertIn("기대=6", err)
        self.assertIn("실측=5", err)

    def test_배치수_초과는_exit1(self):
        code, out, err = run_vr("분할", "--파일", "심사대상.md", "--배치수", "6")
        self.assertEqual(code, 1)
        self.assertIn("심사대상.md", err)


if __name__ == "__main__":
    unittest.main()
