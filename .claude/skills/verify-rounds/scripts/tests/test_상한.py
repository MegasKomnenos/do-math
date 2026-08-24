# -*- coding: utf-8 -*-
"""vr.py 상한 하위명령 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_상한.py`).

검사 대상은 일곱으로 한정한다:
① 두 상한 0(무제한) — 분할이 발동하지 않아 배치 수 1, 바이트 실측이 stdout 수치로 난다(§4.2-5)
② 항목상한이 요구하는 분할 수 — ceil(항목수 / 항목상한)
③ 입력상한이 요구하는 분할 수 — 고정 지급은 배치마다 실리므로 ceil(가변 / (상한 - 고정)),
   배치 수는 두 분할 수 중 큰 쪽(§7 심사 분할 규칙)
④ 고정 지급 단독 초과 — §8 신호 5 해당을 수치로 내고 입력상한 분할은 산정 불가(SKILL.md §4.2-7).
   경계값(고정 합 = 입력상한)도 같은 처분이다
⑤ 지급 파일 부재는 exit 2
⑥ 측정·산정만 하고 파일을 산출하지 않는다
⑦ 고정 지급 목록은 공통 계약 둘·산출 계약·GLOSSARY·`<런>/동결.md`
   다섯을 세고(§4.2-7), 동결문이 없으면 exit 2다
그 밖의 검사는 두지 않는다. 바이트는 실물 파일의 디스크 크기 실측이다.
"""

from __future__ import annotations

import contextlib
import io
import math
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import vr  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
지급1 = FIX / "기안_평문_발췌.md"
지급2 = FIX / "기안_볼드_발췌.md"
SKILL = SCRIPTS.parent
def 고정상수() -> list[Path]:
    return [SKILL / "계약" / "심사.md", SKILL / "계약" / "조각.md",
            SKILL / "계약" / "산출.md", SKILL / "GLOSSARY.md"]


def run_vr(*argv):
    args = list(argv)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = vr.main(args)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 2
    return code, out.getvalue(), err.getvalue()


def 런구축(tmp: Path, 동결본문: str = "# 동결문\n\n## 산출물\n\n- 제품.md\n") -> Path:
    """`<런>/동결.md`만 있는 런 디렉토리를 세운다. 동결문은 고정 지급의 다섯째다."""
    run = tmp / "런"
    run.mkdir(parents=True, exist_ok=True)
    (run / "동결.md").write_text(동결본문, encoding="utf-8")
    return run


def 고정합(run: Path) -> int:
    return sum(p.stat().st_size for p in 고정상수()) + (run / "동결.md").stat().st_size


class CapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.run = 런구축(self.tmp)
        self.fixed = 고정합(self.run)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_무제한이면_배치_하나와_바이트_실측(self):
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "7", "--지급", str(지급1),
            "--항목상한", "0", "--입력상한", "0")
        self.assertEqual(code, 0, err)
        self.assertIn("배치 수: 1", out)
        var = 지급1.stat().st_size
        self.assertIn(str(var), out)
        self.assertIn(str(self.fixed), out)
        self.assertIn(str(var + self.fixed), out)

    def test_고정지급은_파생한_다섯이다(self):
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "7", "--지급", str(지급1),
            "--항목상한", "0", "--입력상한", "0")
        self.assertEqual(code, 0, err)
        self.assertIn(f"고정지급: 5파일 {self.fixed}바이트", out)

    def test_동결문_부재는_exit2(self):
        (self.run / "동결.md").unlink()
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "7", "--지급", str(지급1),
            "--항목상한", "0", "--입력상한", "0")
        self.assertEqual(code, 2)
        self.assertIn("고정 지급 파일 부재", err)

    def test_항목상한_분할_수(self):
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "100", "--지급", str(지급1),
            "--항목상한", "48", "--입력상한", "0")
        self.assertEqual(code, 0, err)
        self.assertIn("항목상한 요구 분할: 3", out)
        self.assertIn("배치 수: 3", out)

    def test_입력상한_분할_수와_큰_쪽_채택(self):
        var = 지급1.stat().st_size + 지급2.stat().st_size
        cap = self.fixed + var // 2  # 가변을 두 배치로 갈라야 하는 상한
        k_bytes = math.ceil(var / (cap - self.fixed))
        self.assertGreaterEqual(k_bytes, 2)
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "10",
            "--지급", str(지급1), "--지급", str(지급2),
            "--항목상한", "48", "--입력상한", str(cap))
        self.assertEqual(code, 0, err)
        self.assertIn(f"입력상한 요구 분할: {k_bytes}", out)
        self.assertIn(f"배치 수: {k_bytes}", out)

    def test_고정지급_단독_초과는_신호5(self):
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "10", "--지급", str(지급1),
            "--항목상한", "0", "--입력상한", str(self.fixed - 1))
        self.assertEqual(code, 0, err)
        self.assertIn("고정지급 단독 초과: 예", out)
        self.assertIn("신호 5", out)
        self.assertIn("산정 불가", out)

    def test_고정지급_경계값도_신호5(self):
        # 고정 합 = 입력상한이면 가변을 실을 자리가 0이라 초과와 같은 처분이다.
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "10", "--지급", str(지급1),
            "--항목상한", "0", "--입력상한", str(self.fixed))
        self.assertEqual(code, 0, err)
        self.assertIn("고정지급 단독 초과: 예", out)
        self.assertIn("산정 불가", out)

    def test_지급_파일_부재는_exit2(self):
        code, out, err = run_vr(
            "상한", "--런", str(self.run), "--항목수", "10",
            "--지급", str(self.tmp / "없음.md"),
            "--항목상한", "0", "--입력상한", "0")
        self.assertEqual(code, 2)

    def test_파일을_산출하지_않는다(self):
        빈칸 = self.tmp / "빈칸"
        빈칸.mkdir()
        prev = Path.cwd()
        os.chdir(빈칸)
        try:
            code, out, err = run_vr(
                "상한", "--런", str(self.run), "--항목수", "7", "--지급", str(지급1),
                "--항목상한", "48", "--입력상한", "0")
            self.assertEqual(code, 0, err)
            self.assertEqual(list(Path(".").iterdir()), [])
        finally:
            os.chdir(prev)


if __name__ == "__main__":
    unittest.main()
