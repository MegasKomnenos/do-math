# -*- coding: utf-8 -*-
"""vr.py 심사집계 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_심사집계.py`).

검사 대상은 열다섯으로 한정한다:
① 통과 — 3기 정족 3에서 항목마다 승인 수를 세어 확정하고, 수리·무처분·상신·기각
   목록과 _심사집계.json을 낸다
② 처분 보수 병합 — 갈린 처분에서 보수 순서 최상위가 선다
③ 정족 미달 — 기각 확정과 `### 사유` 칸 수집
④ 상신 제안 항목의 「수리한다」 처분 — 어휘 위반으로 exit 1
⑤ 덮개 미달 — 한 기가 항목을 빠뜨리면 exit 1이고, 어긋남이 남은 항목 ID를 내며
   (§5.6 재개의 입력), _심사집계.json을 쓰지 않는다
⑥ 어휘 밖 처분 값 — exit 1 (죽지 않는다)
⑦ 배치 분할 — 기마다 배치 산출 여럿을 합쳐 덮개를 잰다
⑧ 재개 산출 — 덮개 미달인 기의 재개 산출을 더하면 덮개가 차고 집계가 선다
⑨ 심사검산 통과 — 산출 하나의 기 번호·서식·대상 덮개를 검사하고 집계 파일을 만들지 않는다
⑩ 심사검산 대상 누락 — exit 1이고 집계 파일을 만들지 않는다
⑪ 심사검산 재개 — `--항목`으로 준 남은 항목만 대조한다
⑫ 「사용자에게 올린다」의 상신안 칸 누락 — exit 1
⑬ 「호출자에게 전달」의 검토전개 실익 칸 누락 — exit 1
⑭ 발견 항목의 「승인하되 고치지 않는다」에도 검토전개 실익 칸을 요구한다
⑮ 기각·무처분 항목의 원문·판정·근거를 기각 보관 파일에 남긴다
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
from _파이프라인재료 import 런구축, 심사산출, run_vr  # noqa: E402


def 심사쓰기(번호: int, 처분표: dict[str, str]):
    Path(f"런/라운드1/심사_{번호}.md").write_text(심사산출(번호, 처분표),
                                            encoding="utf-8")


def 실행(기수=3, 정족=3, 심사들=("심사_1.md", "심사_2.md", "심사_3.md"), 보관=False):
    argv = ["심사집계", "--런", "런", "--라운드", "1",
            "--대상", "런/라운드1/심사대상.md",
            "--정족", str(정족), "--기수", str(기수)]
    for f in 심사들:
        argv += ["--심사", f"런/라운드1/{f}"]
    if 보관:
        argv += ["--기각보관", "보관", "--보관출처", "2.3"]
    return run_vr(*argv)


def 단건검산():
    return run_vr("심사검산", "--심사", "런/라운드1/심사_1.md",
                  "--대상", "런/라운드1/심사대상.md", "--기", "1")


class ReviewTallyTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        런구축(self.tmp, 병합산출=True)
        assert run_vr("병합검산", "--런", "런", "--라운드", "1")[0] == 0
        assert run_vr("심사지급", "--런", "런", "--라운드", "1")[0] == 0

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_통과와_목록(self):
        기본 = {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"}
        for n in (1, 2, 3):
            심사쓰기(n, 기본)
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        self.assertEqual(data["수리"], ["R1-M1", "R1-M2"])
        self.assertEqual(data["상신"], ["R1-05"])
        self.assertEqual(data["기각"], [])
        self.assertIn("수리 2", out)

    def test_심사검산은_단건을_검사하고_집계산출을_쓰지_않는다(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        code, out, err = 단건검산()
        self.assertEqual(code, 0, err)
        self.assertIn("심사 1기", out)
        self.assertIn("판정 3건", out)
        self.assertFalse(Path("런/라운드1/_심사집계.json").exists())

        path = Path("런/라운드1/심사_1.md")
        path.write_text(vrlib.read_text(path).replace("읽은 범위: 전건\n", ""),
                        encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("읽은 범위", err)
        self.assertFalse(Path("런/라운드1/_심사집계.json").exists())


    def test_심사검산_대상누락은_exit1_집계산출없음(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다"})
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("남은 항목: R1-M2", err)
        self.assertFalse(Path("런/라운드1/_심사집계.json").exists())

    def test_사용자에게_올린다의_상신안_누락은_exit1(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        path = Path("런/라운드1/심사_1.md")
        text = vrlib.read_text(path)
        text = text.replace("\n### 상신안\n선택지와 추천을 최종 상태로 대조했다.\n", "")
        path.write_text(text, encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("상신안", err)

    def test_호출자에게_전달의_검토전개_실익_누락은_exit1(self):
        심사쓰기(1, {"R1-05": "호출자에게 전달", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        path = Path("런/라운드1/심사_1.md")
        text = vrlib.read_text(path)
        text = text.replace("\n### 검토전개 실익\n방치 손상이 후속 작업 비용보다 크다.\n", "")
        path.write_text(text, encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("검토전개 실익", err)

    def test_발견_무처분도_검토전개_실익을_요구한다(self):
        data = json.loads(vrlib.read_text("런/라운드1/_항목.json"))
        row = next(r for r in data["항목"] if r["id"] == "R1-05")
        row["상신"] = False
        row["발견"] = True
        Path("런/라운드1/_항목.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
        target = Path("런/라운드1/심사대상.md")
        target.write_text(vrlib.read_text(target).replace("### 상신", "### 발견", 1),
                          encoding="utf-8")
        심사쓰기(1, {"R1-05": "승인하되 고치지 않는다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        path = Path("런/라운드1/심사_1.md")
        path.write_text(vrlib.read_text(path).replace(
            "\n### 검토전개 실익\n방치 손상이 후속 작업 비용보다 크다.\n", ""),
            encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("검토전개 실익", err)

    def test_기각과_무처분을_보관한다(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "승인하되 고치지 않는다",
                 "R1-M2": "기각"})
        심사쓰기(2, {"R1-05": "사용자에게 올린다", "R1-M1": "승인하되 고치지 않는다",
                 "R1-M2": "기각"})
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "승인하되 고치지 않는다",
                 "R1-M2": "기각"})
        code, out, err = 실행(보관=True)
        self.assertEqual(code, 0, err)
        path = Path("보관/2.3-라운드1.md")
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("## R1-M1", text)
        self.assertIn("## R1-M2", text)
        self.assertIn("최종 처분: 승인하되 고치지 않는다", text)
        self.assertIn("최종 판정: 기각", text)
        self.assertIn("관문 3 불성립.", text)

    def test_심사검산_재개는_항목목록과_대조한다(self):
        Path("런/라운드1/심사_1_재개1.md").write_text(
            심사산출(1, {"R1-M2": "수리한다"}), encoding="utf-8")
        code, out, err = run_vr(
            "심사검산", "--심사", "런/라운드1/심사_1_재개1.md",
            "--항목", "R1-M2", "--기", "1")
        self.assertEqual(code, 0, err)
        self.assertIn("판정 1건", out)

    def test_처분_보수_병합(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        심사쓰기(2, {"R1-05": "사용자에게 올린다", "R1-M1": "승인하되 고치지 않는다",
                 "R1-M2": "수리한다"})
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        self.assertEqual(data["무처분"], ["R1-M1"])   # 보수 순서가 수리한다를 덮는다
        self.assertEqual(data["수리"], ["R1-M2"])

    def test_정족_미달은_기각과_사유(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "기각", "R1-M2": "수리한다"})
        심사쓰기(2, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"})
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"})
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        self.assertEqual(data["기각"], ["R1-M1"])
        row = next(r for r in data["항목"] if r["id"] == "R1-M1")
        self.assertEqual(row["기각사유"], {"1": "관문 3 불성립."})

    def test_상신제안의_수리한다는_exit1(self):
        기본 = {"R1-05": "수리한다", "R1-M1": "수리한다", "R1-M2": "수리한다"}
        for n in (1, 2, 3):
            심사쓰기(n, 기본)
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("상신 제안", err)

    def test_덮개_미달은_남은_항목을_내고_exit1(self):
        # 남은 항목 목록이 §5.6 재개의 입력이다 — 세션이 그 목록을 읽어
        # 재개 지시문의 슬롯을 채운다.
        기본 = {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"}
        심사쓰기(1, 기본)
        심사쓰기(2, 기본)
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다"})  # R1-M2 미판정
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("기 3의 덮개", err)
        self.assertIn("남은 항목: R1-M2", err)
        # 어긋난 집계를 남기면 적용이 그대로 읽는다 — 산출 없이 반환한다
        self.assertFalse(Path("런/라운드1/_심사집계.json").exists())

    def test_어휘_밖_처분은_exit1(self):
        심사쓰기(1, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        심사쓰기(2, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다",
                 "R1-M2": "수리한다"})
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "엉뚱한 처분",
                 "R1-M2": "수리한다"})
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("엉뚱한 처분", err)

    def test_배치_산출_여럿이_한_기의_덮개를_이룬다(self):
        # 배치 경계는 모든 기가 같이 쓴다(SKILL.md §7 심사 단계). 기마다
        # 배치1 = {R1-05} · 배치2 = {R1-M1, R1-M2} 두 산출이 오고, 집계는
        # frontmatter 심사자 번호로 그 둘을 합쳐 덮개를 잰다.
        for n in (1, 2, 3):
            Path(f"런/라운드1/심사_{n}_배치1.md").write_text(
                심사산출(n, {"R1-05": "사용자에게 올린다"}), encoding="utf-8")
            Path(f"런/라운드1/심사_{n}_배치2.md").write_text(
                심사산출(n, {"R1-M1": "수리한다", "R1-M2": "수리한다"}),
                encoding="utf-8")
        code, out, err = 실행(심사들=(
            "심사_1_배치1.md", "심사_1_배치2.md",
            "심사_2_배치1.md", "심사_2_배치2.md",
            "심사_3_배치1.md", "심사_3_배치2.md"))
        self.assertEqual(code, 0, err)
        data = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        self.assertEqual(data["수리"], ["R1-M1", "R1-M2"])
        self.assertEqual(data["상신"], ["R1-05"])
        row = next(r for r in data["항목"] if r["id"] == "R1-M1")
        self.assertEqual(row["승인기"], [1, 2, 3])
        self.assertIn("기 3: 덮개 3건", out)

    def test_재개_산출이_덮개를_채운다(self):
        # 기 3의 산출이 R1-M2를 빠뜨렸고, §5.6 재개가 그 항목만 판정해 낸다.
        # 재개 산출을 --심사에 더하면 덮개가 차고 집계가 선다.
        기본 = {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다", "R1-M2": "수리한다"}
        심사쓰기(1, 기본)
        심사쓰기(2, 기본)
        심사쓰기(3, {"R1-05": "사용자에게 올린다", "R1-M1": "수리한다"})
        Path("런/라운드1/심사_3_재개1.md").write_text(
            심사산출(3, {"R1-M2": "수리한다"}), encoding="utf-8")
        code, out, err = 실행(심사들=(
            "심사_1.md", "심사_2.md", "심사_3.md", "심사_3_재개1.md"))
        self.assertEqual(code, 0, err)
        self.assertIn("기 3: 덮개 3건", out)
        data = json.loads(vrlib.read_text("런/라운드1/_심사집계.json"))
        self.assertEqual(data["수리"], ["R1-M1", "R1-M2"])
        row = next(r for r in data["항목"] if r["id"] == "R1-M2")
        self.assertEqual(row["승인기"], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
