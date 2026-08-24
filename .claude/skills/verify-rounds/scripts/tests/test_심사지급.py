# -*- coding: utf-8 -*-
"""vr.py 심사지급 하위명령 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_심사지급.py`).

검사 대상은 다섯으로 한정한다:
① 통과 — 단독 항목(항목.md 절 전문)과 병합 항목(구성 줄·병합 칸·조각의 원래+대체)을
   심사대상.md 하나로 모으고 frontmatter `항목:`이 합과 같다
② 병합 항목의 조각 — 원래는 지급 정본에서, 대체는 해소 값에서 오고 「원래대로」가
   남지 않는다
③ _병합.json에 묶음이 빠짐 — exit 2
④ --결번 묶음 제외 — 병합검산·심사지급이 결번 묶음과 그 구성 항목을 빼고 수치로 보고
⑤ 항목.md frontmatter 계수 어긋남 — exit 1(§5.5 검산 내장)
그 밖의 검사는 두지 않는다. 재료는 _파이프라인재료.py가 정본이다.
시험은 임시 디렉토리를 루트 삼아 chdir하고 상대 경로를 준다.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import vrlib  # noqa: E402
from _파이프라인재료 import 런구축, run_vr  # noqa: E402


class ReviewPayloadTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        런구축(self.tmp, 병합산출=True)
        code, out, err = run_vr("병합검산", "--런", "런", "--라운드", "1")
        assert code == 0, err

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_통과_구성과_계수(self):
        code, out, err = run_vr("심사지급", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("단독 1, 병합 2", out)
        text = vrlib.read_text("런/라운드1/심사대상.md")
        fm, _ = vrlib.parse_frontmatter(text)
        self.assertEqual(fm.get("항목"), "3")
        titles = [s.title for s in vrlib.split_sections(text)]
        self.assertEqual(titles, ["R1-05", "R1-M1", "R1-M2"])
        self.assertIn("구성: R1-01 · R1-04", text)
        self.assertIn("### 상신", text)   # 단독 상신 제안 절 전문

    def test_병합_조각의_원래와_대체(self):
        run_vr("심사지급", "--런", "런", "--라운드", "1")
        text = vrlib.read_text("런/라운드1/심사대상.md")
        self.assertIn("첫 문단이다.", text)          # M1 원래 (지급 정본)
        self.assertIn("병합된 첫 문단이다.", text)     # M1 대체
        # M2 조각 1: 원래 블록과 「원래대로」 해소 대체 블록의 두 자리에 선다
        self.assertEqual(text.count("둘째 문단이다."), 2)
        self.assertNotIn("대체: 원래대로", text)  # 라벨은 해소되어 남지 않는다

    def test_병합_누락은_exit2(self):
        data = json.loads(vrlib.read_text("런/라운드1/_병합.json"))
        data["묶음"] = [r for r in data["묶음"] if r["id"] != "R1-M2"]
        Path("런/라운드1/_병합.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out, err = run_vr("심사지급", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 2)
        self.assertIn("R1-M2", err)

    def test_결번_묶음_제외(self):
        # 병합 결번 경로(§5.3): M2 산출이 없어도 --결번이 그 묶음과 구성 항목을 뺀다.
        Path("런/라운드1/병합_R1-M2.md").unlink()
        code, out, err = run_vr("병합검산", "--런", "런", "--라운드", "1",
                                "--결번", "R1-M2")
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_병합.json"))
        self.assertEqual([r["id"] for r in data["묶음"]], ["R1-M1"])
        code, out, err = run_vr("심사지급", "--런", "런", "--라운드", "1",
                                "--결번", "R1-M2")
        self.assertEqual(code, 0, err)
        self.assertIn("결번", out)
        text = vrlib.read_text("런/라운드1/심사대상.md")
        titles = [s.title for s in vrlib.split_sections(text)]
        self.assertEqual(titles, ["R1-05", "R1-M1"])
        fm, _ = vrlib.parse_frontmatter(text)
        self.assertEqual(fm.get("항목"), "2")

    def test_항목md_계수_어긋남은_exit1(self):
        text = vrlib.read_text("런/라운드1/항목.md")
        Path("런/라운드1/항목.md").write_text(
            text.replace("항목: 5", "항목: 6", 1), encoding="utf-8")
        code, out, err = run_vr("심사지급", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 1)
        self.assertIn("기대=6", err)


if __name__ == "__main__":
    unittest.main()
