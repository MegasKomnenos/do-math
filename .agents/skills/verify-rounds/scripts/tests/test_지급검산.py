# -*- coding: utf-8 -*-
"""vr.py 지급검산 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_지급검산.py`).

검사 대상은 일곱으로 한정한다:
① 통과 — 실물 발췌(수리지적_발췌.md, `항목: 2` = `##` 절 2)에 exit 0과 stdout 수치
② frontmatter 수와 실측 절 수의 어긋남 — exit 1과 stderr 좌표(기대·실측)
③ `항목:` 키 없는 실물(승인문면_키이탈_발췌.md, `승인: 22`) — 닫힌 서식 위반으로 exit 1
④ `--기대` 불일치 — exit 1
⑤ `--기대` 일치 — 통과
⑥ 울타리 안 `## ` 줄은 절로 세지 않는다
⑦ 파일 부재 — exit 2
그 밖의 검사는 두지 않는다.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import vr  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


def run_vr(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = vr.main(list(argv))
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 2
    return code, out.getvalue(), err.getvalue()


class PayoutCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_실물_발췌_통과(self):
        code, out, err = run_vr("지급검산", "--파일", str(FIX / "수리지적_발췌.md"))
        self.assertEqual(code, 0, err)
        self.assertIn("2", out)

    def test_frontmatter_불일치는_exit1(self):
        text = (FIX / "수리지적_발췌.md").read_text(encoding="utf-8")
        bad = self.tmp / "수리지적_불일치.md"
        bad.write_text(text.replace("항목: 2", "항목: 3", 1), encoding="utf-8")
        code, out, err = run_vr("지급검산", "--파일", str(bad))
        self.assertEqual(code, 1)
        self.assertIn("기대=3", err)
        self.assertIn("실측=2", err)

    def test_항목_키_없는_실물은_exit1(self):
        code, out, err = run_vr("지급검산", "--파일", str(FIX / "승인문면_키이탈_발췌.md"))
        self.assertEqual(code, 1)
        self.assertIn("항목", err)

    def test_기대_불일치는_exit1(self):
        code, out, err = run_vr(
            "지급검산", "--파일", str(FIX / "수리지적_발췌.md"), "--기대", "5")
        self.assertEqual(code, 1)
        self.assertIn("기대=5", err)

    def test_기대_일치는_통과(self):
        code, out, err = run_vr(
            "지급검산", "--파일", str(FIX / "수리지적_발췌.md"), "--기대", "2")
        self.assertEqual(code, 0, err)

    def test_울타리_안_절제목은_세지_않는다(self):
        f = self.tmp / "울타리.md"
        f.write_text(
            "---\n항목: 1\n---\n\n## R1-01\n\n```\n## 울타리 안 가짜 절\n```\n",
            encoding="utf-8")
        code, out, err = run_vr("지급검산", "--파일", str(f))
        self.assertEqual(code, 0, err)
        self.assertIn("1", out)

    def test_파일_부재는_exit2(self):
        code, out, err = run_vr("지급검산", "--파일", str(self.tmp / "없음.md"))
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
