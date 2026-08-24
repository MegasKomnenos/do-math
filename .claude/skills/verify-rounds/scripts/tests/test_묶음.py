# -*- coding: utf-8 -*-
"""vr.py 묶음 하위명령 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_묶음.py`).

검사 대상은 여섯으로 한정한다:
① 통과 — 교차 간선(같은 구간의 두 항목)과 결합 간선(수리자 고지)이 각각 묶음을
   세우고, 상신 제안 항목은 간선 없이 단독으로 남는다
② 정규화 — 묶음 조각이 구성 조각의 병합이고, 정수 구간의 원래 축자를 사본에서
   다시 뜨며, 틈 조각은 원래 없이 선다
③ 병합지급 파일 — frontmatter(묶음·구성·조각 수), `# 구성 항목` 절 제목과 그
   아래 구성 항목 절 전문, `# 조각 목록` 절 제목과 그 아래 조각 칸들
④ 묶음 0건 — 간선이 없으면 묶음 0·전건 단독, 병합지급 파일 없음
⑤ 부분 겹침 정규화 — 2~3행과 3~4행이 2~4행 하나로 병합되고 원래 축자를 새로 뜬다
⑥ 항목.md frontmatter 계수 어긋남 — exit 1(§5.5 검산 내장)
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
from _파이프라인재료 import 런구축, 런구축2, run_vr  # noqa: E402


class BundleTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_교차와_결합이_묶음을_세운다(self):
        results = 런구축(self.tmp)
        for code, out, err in results:
            self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_묶음.json"))
        묶음 = {m["id"]: m for m in data["묶음"]}
        self.assertEqual(sorted(묶음), ["R1-M1", "R1-M2"])
        self.assertEqual(묶음["R1-M1"]["구성"], ["R1-01", "R1-04"])  # 교차
        self.assertEqual(묶음["R1-M2"]["구성"], ["R1-02", "R1-03"])  # 결합
        self.assertEqual(data["단독"], ["R1-05"])  # 상신 제안은 간선 없음

    def test_정규화와_원래_축자(self):
        런구축(self.tmp)
        data = json.loads(vrlib.read_text("런/라운드1/_묶음.json"))
        묶음 = {m["id"]: m for m in data["묶음"]}
        m1 = 묶음["R1-M1"]["조각"]
        self.assertEqual(len(m1), 1)  # 같은 구간 둘이 하나로 병합
        self.assertEqual(m1[0]["표기"], "제품.md 3~3행")
        self.assertEqual(m1[0]["원래"], "첫 문단이다.")
        m2 = 묶음["R1-M2"]["조각"]
        self.assertEqual([p["표기"] for p in m2],
                         ["제품.md 5~5행", "제품.md 행 6 뒤"])
        self.assertIsNone(m2[1]["원래"])

    def test_병합지급_파일(self):
        런구축(self.tmp)
        text = vrlib.read_text("런/라운드1/병합지급_R1-M2.md")
        fm, _ = vrlib.parse_frontmatter(text)
        self.assertEqual(fm.get("묶음"), "R1-M2")
        self.assertEqual(fm.get("조각"), "2")
        self.assertIn("R1-02 · R1-03", fm.get("구성", ""))
        self.assertIn("\n# 구성 항목\n", text)   # 계약/병합.md 32행이 가리키는 절
        self.assertIn("\n# 조각 목록\n", text)   # 계약/병합.md 34행이 가리키는 절
        self.assertIn("## R1-02", text)   # 구성 항목 절 전문
        self.assertIn("## R1-03", text)
        self.assertIn("### 조각 1 — 제품.md 5~5행", text)
        self.assertIn("### 조각 2 — 제품.md 행 6 뒤", text)

    def test_간선없으면_전건_단독(self):
        런구축(self.tmp)
        # 결합·교차를 없앤 항목 등록부로 다시 실행한다
        data = json.loads(vrlib.read_text("런/라운드1/_항목.json"))
        for r in data["항목"]:
            r["결합"] = []
        data["항목"][3]["조각"][0]["시작2"] = 14   # R1-04를 7~7행으로 옮겨 교차 해소
        data["항목"][3]["조각"][0]["끝2"] = 14
        data["항목"][3]["조각"][0]["표기"] = "제품.md 7~7행"
        Path("런/라운드1/_항목.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
        for f in Path("런/라운드1").glob("병합지급_*.md"):
            f.unlink()
        code, out, err = run_vr("묶음", "--런", "런", "--라운드", "1",
                                "--동결", "런/동결.md")
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_묶음.json"))
        self.assertEqual(data["묶음"], [])
        self.assertEqual(len(data["단독"]), 5)
        self.assertEqual(list(Path("런/라운드1").glob("병합지급_*.md")), [])

    def test_부분_겹침_정규화(self):
        results = 런구축2(self.tmp)
        for code, out, err in results:
            self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런2/라운드1/_묶음.json"))
        묶음 = {m["id"]: m for m in data["묶음"]}
        self.assertEqual(sorted(묶음), ["R1-M1"])
        self.assertEqual(묶음["R1-M1"]["구성"], ["R1-01", "R1-02"])
        조각들 = 묶음["R1-M1"]["조각"]
        self.assertEqual(len(조각들), 1)
        self.assertEqual(조각들[0]["표기"], "제품2.md 2~4행")
        self.assertEqual(조각들[0]["원래"], "나\n다\n라")
        self.assertEqual(sorted(data["단독"]), ["R1-03", "R1-04"])

    def test_항목md_계수_어긋남은_exit1(self):
        런구축(self.tmp)
        text = vrlib.read_text("런/라운드1/항목.md")
        Path("런/라운드1/항목.md").write_text(
            text.replace("항목: 5", "항목: 6", 1), encoding="utf-8")
        code, out, err = run_vr("묶음", "--런", "런", "--라운드", "1",
                                "--동결", "런/동결.md")
        self.assertEqual(code, 1)
        self.assertIn("기대=6", err)


if __name__ == "__main__":
    unittest.main()
