# -*- coding: utf-8 -*-
"""vr.py 병합검산 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_병합검산.py`).

검사 대상은 여덟 가지로 한정한다:
① 통과 — 병합 산출 둘을 지급 키와 대조해 _병합.json을 만들고, `대체: 원래대로`를
   지급의 원래 축자로 해소한다
② 지급 키 누락 — exit 1
③ 지급 밖 키 추가 — exit 1
④ 원래 블록의 옮겨 적기 — exit 1 (금지 위반)
⑤ 병합 산출 파일 부재 — exit 1
⑥ 틈 조각의 `대체: 원래대로` — 빈 대체로 해소된다
⑦ 병합자검산 통과 — 묶음 하나를 검사하고 _병합.json을 만들지 않는다
⑧ 병합자검산 지급 키 누락 — exit 1이고 _병합.json을 만들지 않는다
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
from _파이프라인재료 import 런구축, 병합_M2, run_vr  # noqa: E402


def 실행():
    return run_vr("병합검산", "--런", "런", "--라운드", "1")


def 단건검산():
    return run_vr("병합자검산", "--런", "런", "--라운드", "1",
                  "--지급", "런/라운드1/병합지급_R1-M2.md",
                  "--병합", "런/라운드1/병합_R1-M2.md")


class MergeCheckTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        런구축(self.tmp, 병합산출=True)

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_통과와_원래대로_해소(self):
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        self.assertIn("병합 2건", out)
        data = json.loads(vrlib.read_text("런/라운드1/_병합.json"))
        rows = {r["id"]: r for r in data["묶음"]}
        m2 = rows["R1-M2"]["조각"]
        self.assertEqual(m2[0]["대체"], "둘째 문단이다.")   # 원래대로 → 지급 축자
        self.assertEqual(m2[1]["대체"], "병합 삽입 문단이다.")
        self.assertEqual(rows["R1-M1"]["조각"][0]["대체"], "병합된 첫 문단이다.")
        self.assertEqual(rows["R1-M2"]["근거"],
                         "삽입만으로 충분해 둘째 문단은 원래대로 두었다.")

    def test_병합자검산은_단건을_검사하고_공용산출을_쓰지_않는다(self):
        code, out, err = 단건검산()
        self.assertEqual(code, 0, err)
        self.assertIn("병합 R1-M2", out)
        self.assertIn("조각 2건", out)
        self.assertFalse(Path("런/라운드1/_병합.json").exists())

    def test_병합자검산_지급키_누락은_exit1_공용산출없음(self):
        bad = 병합_M2.replace(
            "### 조각 1 — 제품.md 5~5행\n대체: 원래대로\n\n", "").replace(
            "조각: 2", "조각: 1")
        Path("런/라운드1/병합_R1-M2.md").write_text(bad, encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("제품.md 5~5행", err)
        self.assertFalse(Path("런/라운드1/_병합.json").exists())

    def test_틈_원래대로는_빈_대체(self):
        bad = 병합_M2.replace(
            "### 조각 2 — 제품.md 행 6 뒤\n대체:\n```\n병합 삽입 문단이다.\n```",
            "### 조각 2 — 제품.md 행 6 뒤\n대체: 원래대로")
        Path("런/라운드1/병합_R1-M2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_병합.json"))
        rows = {r["id"]: r for r in data["묶음"]}
        self.assertEqual(rows["R1-M2"]["조각"][1]["대체"], "")

    def test_지급_키_누락은_exit1(self):
        bad = 병합_M2.replace(
            "### 조각 1 — 제품.md 5~5행\n대체: 원래대로\n\n", "").replace(
            "조각: 2", "조각: 1")
        Path("런/라운드1/병합_R1-M2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("제품.md 5~5행", err)

    def test_지급_밖_키는_exit1(self):
        bad = 병합_M2.replace(
            "### 조각 2 — 제품.md 행 6 뒤",
            "### 조각 2 — 제품.md 7~7행\n대체:\n```\n엉뚱\n```\n\n"
            "### 조각 3 — 제품.md 행 6 뒤").replace("조각: 2", "조각: 3")
        Path("런/라운드1/병합_R1-M2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("지급 밖", err)

    def test_원래_옮겨적기는_exit1(self):
        bad = 병합_M2.replace(
            "### 조각 1 — 제품.md 5~5행\n대체: 원래대로",
            "### 조각 1 — 제품.md 5~5행\n원래:\n```\n둘째 문단이다.\n```\n"
            "대체: 원래대로")
        Path("런/라운드1/병합_R1-M2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("옮겨 적기", err)

    def test_산출_부재는_exit1(self):
        Path("런/라운드1/병합_R1-M1.md").unlink()
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("병합_R1-M1.md", err)


if __name__ == "__main__":
    unittest.main()
