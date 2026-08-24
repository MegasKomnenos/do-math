# -*- coding: utf-8 -*-
"""vr.py 적용 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_적용.py`).

검사 대상은 열하나로 한정한다:
① 통과 — 확정 「수리한다」 항목(병합 둘)의 조각을 역순 반영한다: 구간 치환,
   「원래대로」의 무변경 치환, 틈 삽입. _적용.json과 수치 stdout
② --추가·--제외 — 반영 집합의 가감(--추가 성공 경로 포함)
③ 서로소 위반 — exit 1, 산출물 무변경
④ 축자 대조 위반(런 밖 편집) — exit 1, 산출물 무변경
⑤ 반영 항목의 조각 정본 부재 — exit 1
⑥ 상신 제안 항목(조각 0)이 반영 집합에 듦 — exit 1
⑦ 행 수를 바꾸는 치환 뒤 조각과 중간 틈 삽입의 역순 반영(경계 재료)
⑧ CRLF 산출물의 개행 보존
⑨ _적용.json 실재 시 재실행 거부(exit 2), --강제로만 우회
⑩ 쓰기 실패(OS 오류) — exit 2와 stderr 좌표
⑪ 개행 종료 파일의 유령 마지막 행이 좌표 대상이 아니다(행 수 초과 어긋남)
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
from _파이프라인재료 import 산출물, 산출물2, 런구축, 런구축2, 심사산출, run_vr  # noqa: E402

기대_결과 = ("# 제목\n\n병합된 첫 문단이다.\n\n둘째 문단이다.\n\n"
         "병합 삽입 문단이다.\n셋째 문단이다.\n")


class ApplyCmdTest(unittest.TestCase):
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
        code, out, err = run_vr(
            "심사집계", "--런", "런", "--라운드", "1",
            "--대상", "런/라운드1/심사대상.md",
            "--심사", "런/라운드1/심사_1.md", "--심사", "런/라운드1/심사_2.md",
            "--심사", "런/라운드1/심사_3.md", "--정족", "3", "--기수", "3")
        assert code == 0, err

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_통과_역순_반영(self):
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 0, err)
        self.assertEqual(vrlib.read_text("제품.md"), 기대_결과)
        self.assertIn("적용 2건", out)
        data = json.loads(vrlib.read_text("런/라운드1/_적용.json"))
        self.assertEqual(data["적용"], ["R1-M1", "R1-M2"])
        self.assertEqual(data["파일"], ["제품.md"])

    def test_제외와_추가(self):
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1",
                                "--제외", "R1-M2")
        self.assertEqual(code, 0, err)
        text = vrlib.read_text("제품.md")
        self.assertIn("병합된 첫 문단이다.", text)
        self.assertNotIn("병합 삽입 문단이다.", text)
        data = json.loads(vrlib.read_text("런/라운드1/_적용.json"))
        self.assertEqual(data["적용"], ["R1-M1"])

    def test_서로소_위반은_무변경(self):
        # 단독 항목 R1-01을 --추가하면 R1-M1과 같은 구간이라 서로소가 깨진다
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1",
                                "--추가", "R1-01")
        self.assertEqual(code, 1)
        self.assertIn("서로소", err)
        self.assertEqual(vrlib.read_text("제품.md"), 산출물)

    def test_축자_대조_위반은_무변경(self):
        Path("제품.md").write_text(
            산출물.replace("첫 문단이다.", "런 밖에서 고친 문단이다."),
            encoding="utf-8")
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 1)
        self.assertIn("신호 6", err)
        self.assertIn("런 밖에서 고친 문단이다.", vrlib.read_text("제품.md"))

    def test_조각_정본_부재는_exit1(self):
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1",
                                "--추가", "R1-99")
        self.assertEqual(code, 1)
        self.assertIn("R1-99", err)

    def test_상신_제안_항목의_반영은_exit1(self):
        # R1-05는 조각 0의 상신 제안 항목이다 — 어떤 경로로도 적용 목록에 오르지 못한다.
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1",
                                "--추가", "R1-05")
        self.assertEqual(code, 1)
        self.assertIn("R1-05", err)
        self.assertEqual(vrlib.read_text("제품.md"), 산출물)

    def test_추가_성공_경로(self):
        # M2를 상신으로 집계한 뒤 --추가로 반영 집합에 넣는다(§8 승계 전환 경로).
        갈림 = {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
              "R1-M2": "사용자에게 올린다"}
        for n in (1, 2, 3):
            Path(f"런/라운드1/심사_{n}.md").write_text(
                심사산출(n, 갈림), encoding="utf-8")
        assert run_vr("심사집계", "--런", "런", "--라운드", "1",
                      "--대상", "런/라운드1/심사대상.md",
                      "--심사", "런/라운드1/심사_1.md",
                      "--심사", "런/라운드1/심사_2.md",
                      "--심사", "런/라운드1/심사_3.md",
                      "--정족", "3", "--기수", "3")[0] == 0
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1",
                                "--추가", "R1-M2")
        self.assertEqual(code, 0, err)
        self.assertEqual(vrlib.read_text("제품.md"), 기대_결과)
        data = json.loads(vrlib.read_text("런/라운드1/_적용.json"))
        self.assertEqual(sorted(data["적용"]), ["R1-M1", "R1-M2"])

    def test_재실행은_강제_없이_exit2(self):
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 0, err)
        적용후 = vrlib.read_text("제품.md")
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1")
        self.assertEqual(code, 2)
        self.assertIn("_적용.json", err)
        self.assertEqual(vrlib.read_text("제품.md"), 적용후)
        # --강제는 가드를 우회한다 — 이미 반영된 산출물이라 축자 대조(exit 1)까지 간다
        code, out, err = run_vr("적용", "--런", "런", "--라운드", "1", "--강제")
        self.assertEqual(code, 1)

    def test_쓰기_실패는_exit2와_좌표(self):
        원래_write = vrlib.write_text

        def 실패(path, text):
            raise OSError("디스크 오류 모의")

        vrlib.write_text = 실패
        try:
            code, out, err = run_vr("적용", "--런", "런", "--라운드", "1")
        finally:
            vrlib.write_text = 원래_write
        self.assertEqual(code, 2)
        self.assertIn("제품.md", err)


class ApplyBoundaryTest(unittest.TestCase):
    """경계 재료(행 수를 바꾸는 치환·중간 틈 삽입·CRLF·유령 행)의 적용 시험."""

    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        results = 런구축2(self.tmp)
        for code, _out, err in results:
            assert code == 0, err
        # R1-01(2~3행 축약)·R1-03(6~6행)·R1-04(행 4 뒤)를 반영 집합으로 둔다.
        Path("런2/라운드1/_심사집계.json").write_text(
            json.dumps({"수리": ["R1-01", "R1-03", "R1-04"]}, ensure_ascii=False),
            encoding="utf-8")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_행수_변경과_중간_삽입의_역순_반영(self):
        code, out, err = run_vr("적용", "--런", "런2", "--라운드", "1")
        self.assertEqual(code, 0, err)
        self.assertEqual(vrlib.read_text("제품2.md"),
                         "가\n나다\n라\n삽입줄\n마\n바꿈\n")

    def test_CRLF_보존(self):
        crlf = 산출물2.replace("\n", "\r\n").encode("utf-8")
        Path("제품2.md").write_bytes(crlf)
        code, out, err = run_vr("적용", "--런", "런2", "--라운드", "1")
        self.assertEqual(code, 0, err)
        self.assertEqual(Path("제품2.md").read_bytes(),
                         "가\n나다\n라\n삽입줄\n마\n바꿈\n".replace(
                             "\n", "\r\n").encode("utf-8"))

    def test_유령_마지막_행은_좌표_대상이_아니다(self):
        # 제품2.md는 6행 + 끝 개행이다. 7~7행 조각은 행 수 초과로 어긋나야 한다.
        data = json.loads(vrlib.read_text("런2/라운드1/_항목.json"))
        row = next(r for r in data["항목"] if r["id"] == "R1-03")
        row["조각"][0].update({"시작2": 14, "끝2": 14, "표기": "제품2.md 7~7행",
                            "원래": ""})
        Path("런2/라운드1/_항목.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out, err = run_vr("적용", "--런", "런2", "--라운드", "1")
        self.assertEqual(code, 1)
        self.assertIn("범위", err)


if __name__ == "__main__":
    unittest.main()
