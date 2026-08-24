# -*- coding: utf-8 -*-
r"""vr.py 장부머리·장부갱신·종료집계 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_장부.py`).

검사 대상은 여덟으로 한정한다:
① 장부머리 — 재료 절을 라운드 머리 절로 치환 기재, 닫힌 절 이름 밖은 exit 1
② 장부갱신 제기 — _항목.json으로 본표(여섯 열)를 세운다: 위치·요지·상태 「제기」
③ 장부갱신 묶음 — 묶음 구성표와 구성 항목 상태 「병합」
④ 장부갱신 심사 — 심사 칸·처분·상태, 묶음 전파, 기각 사유 절
⑤ 장부갱신 적용 — 상태 「적용」과 묶음 전파
⑥ 종료집계 — 본표 적용 계수와 판정 순서(하한·연속영·상한), 결산 절 기재와
   다음 라운드의 결산 회수(연속영 발동 포함)
⑦ 본표 행 부재 — exit 1, 장부 무변경
⑧ 요지 칸의 파이프 문자 — 제기가 이스케이프한 `\|`를 묶음·심사·적용 모드와
   종료집계가 칸 경계로 읽지 않고, 요지 축자가 그대로 선다
그 밖의 검사는 두지 않는다. 파이프라인 재료로 실물 JSON을 만들어 쓴다.
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
from _파이프라인재료 import 런구축, 심사산출, run_vr  # noqa: E402


def 갱신(모드, 입력):
    return run_vr("장부갱신", "--장부", "런/장부.md", "--라운드", "1",
                  "--모드", 모드, "--입력", 입력)


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        런구축(self.tmp, 병합산출=True)
        assert run_vr("병합검산", "--런", "런", "--라운드", "1")[0] == 0
        assert run_vr("심사지급", "--런", "런", "--라운드", "1")[0] == 0
        기본 = {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"}
        for n in (1, 2, 3):
            Path(f"런/라운드1/심사_{n}.md").write_text(
                심사산출(n, 기본), encoding="utf-8")
        assert run_vr("심사집계", "--런", "런", "--라운드", "1",
                      "--대상", "런/라운드1/심사대상.md",
                      "--심사", "런/라운드1/심사_1.md",
                      "--심사", "런/라운드1/심사_2.md",
                      "--심사", "런/라운드1/심사_3.md",
                      "--정족", "3", "--기수", "3")[0] == 0
        Path("런/장부.md").write_text("# 장부\n", encoding="utf-8")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def 본표행(self):
        text = vrlib.read_text("런/장부.md")
        secs = {s.title: s for s in vrlib.split_sections(text)}
        mm: list = []
        rows = vrlib.parse_ledger_table(secs["라운드 1 — 본표"], "런/장부.md", mm)
        self.assertEqual(mm, [])
        return {r["ID"]: r for r in rows}

    def test_장부머리(self):
        Path("재료.md").write_text(
            "## 파라미터 전건\n표준 체급.\n\n## 상한 측정값 대조\n분할 없음.\n\n"
            "## 영역 검산 결과\n통과 — 영역 2개.\n", encoding="utf-8")
        code, out, err = run_vr("장부머리", "--장부", "런/장부.md",
                                "--라운드", "1", "--재료", "재료.md")
        self.assertEqual(code, 0, err)
        text = vrlib.read_text("런/장부.md")
        self.assertIn("## 라운드 1 — 라운드 머리", text)
        self.assertIn("- 영역 검산 결과: 통과 — 영역 2개.", text)
        Path("재료.md").write_text("## 낯선 절\n내용.\n", encoding="utf-8")
        code, out, err = run_vr("장부머리", "--장부", "런/장부.md",
                                "--라운드", "1", "--재료", "재료.md")
        self.assertEqual(code, 1)

    def test_제기_묶음_심사_적용의_흐름(self):
        code, out, err = 갱신("제기", "런/라운드1/_항목.json")
        self.assertEqual(code, 0, err)
        rows = self.본표행()
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows["R1-01"]["상태"], "제기")
        self.assertEqual(rows["R1-01"]["위치"], "제품.md 3~3행")
        self.assertEqual(rows["R1-05"]["위치"], "상신 제안")
        self.assertEqual(rows["R1-01"]["요지"], "첫 문단 결함")

        code, out, err = 갱신("묶음", "런/라운드1/_묶음.json")
        self.assertEqual(code, 0, err)
        rows = self.본표행()
        self.assertEqual(rows["R1-01"]["상태"], "병합")
        self.assertEqual(rows["R1-05"]["상태"], "제기")
        self.assertIn("## 라운드 1 — 묶음 구성표", vrlib.read_text("런/장부.md"))

        code, out, err = 갱신("심사", "런/라운드1/_심사집계.json")
        self.assertEqual(code, 0, err)
        rows = self.본표행()
        self.assertEqual(rows["R1-01"]["상태"], "수리확정")  # M1 전파
        self.assertEqual(rows["R1-04"]["상태"], "수리확정")
        self.assertEqual(rows["R1-05"]["상태"], "상신")
        self.assertEqual(rows["R1-01"]["심사"], "3/3")

        assert run_vr("적용", "--런", "런", "--라운드", "1")[0] == 0
        code, out, err = 갱신("적용", "런/라운드1/_적용.json")
        self.assertEqual(code, 0, err)
        rows = self.본표행()
        for iid in ("R1-01", "R1-02", "R1-03", "R1-04"):
            self.assertEqual(rows[iid]["상태"], "적용")
        self.assertEqual(rows["R1-05"]["상태"], "상신")

    def test_심사의_기각사유_기재(self):
        갱신("제기", "런/라운드1/_항목.json")
        갱신("묶음", "런/라운드1/_묶음.json")
        집계 = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        row = next(r for r in 집계["항목"] if r["id"] == "R1-M1")
        row["확정"] = "기각"
        row["처분"] = None
        row["승인수"] = 1
        row["기각사유"] = {"2": "관문 4 불성립."}
        Path("런/라운드1/_심사집계.json").write_text(
            json.dumps(집계, ensure_ascii=False), encoding="utf-8")
        code, out, err = 갱신("심사", "런/라운드1/_심사집계.json")
        self.assertEqual(code, 0, err)
        text = vrlib.read_text("런/장부.md")
        self.assertIn("## 라운드 1 — 사유 절", text)
        self.assertIn("관문 4 불성립.", text)
        self.assertEqual(self.본표행()["R1-01"]["상태"], "기각")

    def test_행_부재는_exit1_무변경(self):
        갱신("제기", "런/라운드1/_항목.json")
        전 = vrlib.read_text("런/장부.md")
        Path("가짜적용.json").write_text(
            json.dumps({"적용": ["R1-77"]}, ensure_ascii=False), encoding="utf-8")
        code, out, err = 갱신("적용", "가짜적용.json")
        self.assertEqual(code, 1)
        self.assertEqual(vrlib.read_text("런/장부.md"), 전)

    def test_요지의_파이프는_칸_경계가_아니다(self):
        제목 = "`|---|` 구분 행을 세지 않는다"
        항목 = json.loads(vrlib.read_text("런/라운드1/_항목.json"))
        next(r for r in 항목["항목"] if r["id"] == "R1-01")["제목"] = 제목
        Path("런/라운드1/_항목.json").write_text(
            json.dumps(항목, ensure_ascii=False), encoding="utf-8")

        code, out, err = 갱신("제기", "런/라운드1/_항목.json")
        self.assertEqual(code, 0, err)
        self.assertIn(r"`\|---\|`", vrlib.read_text("런/장부.md"))
        self.assertEqual(self.본표행()["R1-01"]["요지"], 제목.replace("|", "\\|"))

        for 모드, 입력 in (("묶음", "런/라운드1/_묶음.json"),
                        ("심사", "런/라운드1/_심사집계.json")):
            code, out, err = 갱신(모드, 입력)
            self.assertEqual(code, 0, err)
        assert run_vr("적용", "--런", "런", "--라운드", "1")[0] == 0
        code, out, err = 갱신("적용", "런/라운드1/_적용.json")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.본표행()["R1-01"]["상태"], "적용")

        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "1",
                                "--하한", "2", "--상한", "6", "--연속영", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("적용 4건", out)

    def test_종료집계(self):
        갱신("제기", "런/라운드1/_항목.json")
        갱신("묶음", "런/라운드1/_묶음.json")
        갱신("심사", "런/라운드1/_심사집계.json")
        assert run_vr("적용", "--런", "런", "--라운드", "1")[0] == 0
        갱신("적용", "런/라운드1/_적용.json")
        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "1",
                                "--하한", "2", "--상한", "6", "--연속영", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("판정: 다음 라운드 — 판정 순서 1항", out)
        self.assertIn("적용 4건", out)
        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "1",
                                "--하한", "1", "--상한", "1", "--연속영", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("판정: 종료 — 판정 순서 3항", out)

        text = vrlib.read_text("런/장부.md").replace(
            " | 수리한다 | 적용 |", " | 수리한다 | 대기 |", 1)
        Path("런/장부.md").write_text(text, encoding="utf-8")
        before = vrlib.read_text("런/장부.md")
        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "1",
                                "--하한", "1", "--상한", "1", "--연속영", "1")
        self.assertEqual(code, 1)
        self.assertIn("장부 상태 여덟", err)
        self.assertEqual(vrlib.read_text("런/장부.md"), before)


    def test_종료집계가_결산을_기재하고_다음_라운드가_회수한다(self):
        갱신("제기", "런/라운드1/_항목.json")
        갱신("묶음", "런/라운드1/_묶음.json")
        갱신("심사", "런/라운드1/_심사집계.json")
        assert run_vr("적용", "--런", "런", "--라운드", "1")[0] == 0
        갱신("적용", "런/라운드1/_적용.json")
        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "1",
                                "--하한", "2", "--상한", "6", "--연속영", "1")
        self.assertEqual(code, 0, err)
        text = vrlib.read_text("런/장부.md")
        self.assertIn("## 라운드 1 — 결산", text)
        secs = {s.title: s for s in vrlib.split_sections(text)}
        결산 = secs["라운드 1 — 결산"].body
        self.assertIn("적용 4", 결산)
        # 라운드 2: 적용 0의 본표를 세우면 결산 회수로 연속영(2항) 종료가 선다
        text += ("\n## 라운드 2 — 본표\n\n"
                 "| ID | 위치 | 요지 | 심사 | 처분 | 상태 |\n"
                 "|---|---|---|---|---|---|\n"
                 "| R2-01 | 제품.md 1~1행 | 남은 결함 | 3/3 | — | 기각 |\n")
        Path("런/장부.md").write_text(text, encoding="utf-8")
        code, out, err = run_vr("종료집계", "--장부", "런/장부.md", "--라운드", "2",
                                "--하한", "1", "--상한", "6", "--연속영", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("판정: 종료 — 판정 순서 2항", out)
        self.assertIn("## 라운드 2 — 결산", vrlib.read_text("런/장부.md"))


if __name__ == "__main__":
    unittest.main()
