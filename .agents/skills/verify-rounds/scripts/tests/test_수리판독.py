# -*- coding: utf-8 -*-
"""vr.py 수리판독 하위명령 시험. 직접 실행이 정본(`python .agents/skills/verify-rounds/scripts/tests/test_수리판독.py`).

검사 대상은 열넷으로 한정한다:
① 통과 — 두 수리 산출(영역 1기·관점 1기)에서 항목 5건에 파견 순서 ID를 붙이고,
   결합 고지의 절 제목을 같은 기의 ID로 풀며, 항목.md와 _항목.json을 조립한다
② 원래 축자가 사본 실측과 다름 — exit 1, 산출 파일 없음
③ 조각과 상신의 혼용 — exit 1
④ 결합 지목 제목이 같은 기의 항목과 일치하지 않음 — exit 1
⑤ frontmatter `항목:`과 실측 절 수의 어긋남 — exit 1
⑥ 조각 경로가 산출물 목록 밖(사본 경로를 적은 경우 포함) — exit 1
⑦ 동결문 산출물 목록의 파일에 대응 사본이 없음 — exit 2(파생 단계에서 잡힌다)
⑧ 항목 안 조각 쌍의 교차·같은 틈 중복 — exit 1
⑨ 틈 좌표가 사본 행 수를 넘음 — exit 1
⑩ 결합 고지가 상신 제안 항목을 지목 — exit 1
⑪ 조각 칸도 상신 칸도 없는 항목 — exit 1
⑫ 수리검산 통과 — 수리 산출 하나를 판독하고 공용 산출 파일을 만들지 않는다
⑬ 수리검산 축자 불일치 — exit 1이고 공용 산출 파일을 만들지 않는다
⑭ 수행 기록 아래 제목 — 어느 제목 층위든 허용하고 항목으로 세지 않는다
그 밖의 검사는 두지 않는다. 항목 서식의 정본은 계약/수리.md·계약/조각.md이고
재료는 _파이프라인재료.py가 정본이다.
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
from _파이프라인재료 import 산출물, 수리1, 수리2, run_vr  # noqa: E402


def 실행(*extra):
    return run_vr("수리판독", "--런", "런", "--라운드", "1",
                  "--동결", "런/동결.md",
                  "--수리", "런/라운드1/수리_1.md",
                  "--수리", "런/라운드1/수리_2.md", *extra)


def 단건검산(*extra):
    return run_vr("수리검산", "--런", "런", "--라운드", "1",
                  "--동결", "런/동결.md",
                  "--수리", "런/라운드1/수리_1.md", *extra)


class RepairParseTest(unittest.TestCase):
    def setUp(self):
        self.prev_cwd = os.getcwd()
        self.tmp = Path(tempfile.mkdtemp())
        os.chdir(self.tmp)
        Path("런/라운드1").mkdir(parents=True)
        Path("제품.md").write_text(산출물, encoding="utf-8")
        # 산출물 목록의 정본은 동결문이고, 사본 경로는 그 목록에서 파생한다.
        Path("런/동결.md").write_text(
            "# 동결문\n\n## 산출물\n\n- 제품.md\n", encoding="utf-8")
        Path("런/라운드1/사본.md").write_text(산출물, encoding="utf-8")
        Path("런/라운드1/수리_1.md").write_text(수리1, encoding="utf-8")
        Path("런/라운드1/수리_2.md").write_text(수리2, encoding="utf-8")

    def tearDown(self):
        os.chdir(self.prev_cwd)
        shutil.rmtree(self.tmp)

    def test_통과_ID와_결합_해소(self):
        code, out, err = 실행()
        self.assertEqual(code, 0, err)
        self.assertIn("항목 5건", out)
        self.assertIn("상신 제안 1건", out)
        self.assertIn("결합 간선 1건", out)
        data = json.loads(vrlib.read_text("런/라운드1/_항목.json"))
        rows = {r["id"]: r for r in data["항목"]}
        self.assertEqual(sorted(rows), ["R1-01", "R1-02", "R1-03", "R1-04", "R1-05"])
        self.assertEqual(rows["R1-02"]["결합"], ["R1-03"])
        self.assertEqual(rows["R1-03"]["결합"], ["R1-02"])
        self.assertTrue(rows["R1-05"]["상신"])
        self.assertEqual(rows["R1-03"]["조각"][0]["시작2"], 13)  # 행 6 뒤
        self.assertIsNone(rows["R1-03"]["조각"][0]["원래"])
        항목md = vrlib.read_text("런/라운드1/항목.md")
        fm, _ = vrlib.parse_frontmatter(항목md)
        self.assertEqual(fm.get("항목"), "5")
        titles = [s.title for s in vrlib.split_sections(항목md)]
        self.assertEqual(titles, ["R1-01", "R1-02", "R1-03", "R1-04", "R1-05"])
        self.assertIn("제목: 첫 문단 결함", 항목md)
        self.assertNotIn("기:", 항목md)  # 기 번호는 심사 지급에 새지 않는다

    def test_수리검산은_단건을_검사하고_공용산출을_쓰지_않는다(self):
        code, out, err = 단건검산()
        self.assertEqual(code, 0, err)
        self.assertIn("수리 1기", out)
        self.assertIn("항목 3건", out)
        self.assertFalse(Path("런/라운드1/항목.md").exists())
        self.assertFalse(Path("런/라운드1/_항목.json").exists())

    def test_수리검산_축자_불일치는_exit1_공용산출없음(self):
        bad = 수리1.replace("첫 문단이다.\n```\n대체", "다른 문단이다.\n```\n대체")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 1)
        self.assertIn("불일치", err)
        self.assertFalse(Path("런/라운드1/항목.md").exists())
        self.assertFalse(Path("런/라운드1/_항목.json").exists())

    def test_record_section_accepts_heading_at_any_level(self):
        changed = 수리1.replace(
            "# 수행 기록\n\n- 읽은 범위",
            "# 수행 기록\n\n## 범위 기록\n\n- 읽은 범위")
        Path("런/라운드1/수리_1.md").write_text(changed, encoding="utf-8")
        code, out, err = 단건검산()
        self.assertEqual(code, 0, err)
        self.assertIn("항목 3건", out)

    def test_축자_불일치는_exit1_산출없음(self):
        bad = 수리1.replace("첫 문단이다.\n```\n대체", "다른 문단이다.\n```\n대체")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("불일치", err)
        self.assertFalse(Path("런/라운드1/항목.md").exists())

    def test_조각_상신_혼용은_exit1(self):
        bad = 수리2.replace(
            "### 상신",
            "### 조각 1 — 제품.md 7~7행\n원래:\n```\n셋째 문단이다.\n```\n"
            "대체:\n```\n셋째 문단을 고쳤다.\n```\n\n### 상신")
        Path("런/라운드1/수리_2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("혼용", err)

    def test_결합_지목_미해소는_exit1(self):
        bad = 수리1.replace("- 셋째 삽입", "- 없는 제목")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("없는 제목", err)

    def test_frontmatter_불일치는_exit1(self):
        bad = 수리2.replace("항목: 2", "항목: 3")
        Path("런/라운드1/수리_2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)

    def test_사본_경로_조각은_exit1(self):
        # 조각 경로에 사본 경로를 적으면 산출물 목록 밖이라 어긋남이다 —
        # 통과시키면 적용이 사본을 편집한다.
        bad = 수리1.replace("제품.md 3~3행", "런/라운드1/사본.md 3~3행")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("런/라운드1/사본.md", err)
        self.assertFalse(Path("런/라운드1/항목.md").exists())

    def test_사본_부재는_exit2(self):
        # 사본 경로를 동결문 산출물 목록에서 파생하므로, 목록에 있고 사본이 없는
        # 파일은 판독 전에 잡힌다 — 좌표 결손이 판독까지 내려오지 못한다.
        Path("런/동결.md").write_text(
            "# 동결문\n\n## 산출물\n\n- 제품.md\n- 기타.md\n", encoding="utf-8")
        Path("기타.md").write_text("x\n", encoding="utf-8")
        Path("런/라운드1/사본").mkdir()
        Path("런/라운드1/사본/제품.md").write_text(산출물, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 2)
        self.assertIn("기타.md", err)

    def test_항목_안_조각_교차는_exit1(self):
        # 첫 항목의 조각을 3~4행으로 넓히고, 같은 항목에 4~5행 조각을 더한다
        # (행 4 공유 — 항목 안 교차).
        bad = 수리1.replace(
            "### 조각 1 — 제품.md 3~3행\n원래:\n```\n첫 문단이다.\n```\n대체:\n```\n첫 문단을 고쳤다.\n```",
            "### 조각 1 — 제품.md 3~4행\n원래:\n```\n첫 문단이다.\n\n```\n대체:\n```\n첫 문단을 고쳤다.\n```\n\n"
            "### 조각 2 — 제품.md 4~5행\n원래:\n```\n\n둘째 문단이다.\n```\n대체:\n```\n\n둘째 문단 다시.\n```",
            1)
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("서로소", err)

    def test_같은_틈_중복_조각은_exit1(self):
        bad = 수리1.replace(
            "### 조각 1 — 제품.md 행 6 뒤\n대체:\n```\n삽입 문단이다.\n```",
            "### 조각 1 — 제품.md 행 6 뒤\n대체:\n```\n삽입 문단이다.\n```\n\n"
            "### 조각 2 — 제품.md 행 6 뒤\n대체:\n```\n둘째 삽입이다.\n```")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("서로소", err)

    def test_틈_좌표_행수_초과는_exit1(self):
        bad = 수리1.replace("### 조각 1 — 제품.md 행 6 뒤",
                        "### 조각 1 — 제품.md 행 99 뒤")
        Path("런/라운드1/수리_1.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("99", err)

    def test_결합이_상신_항목_지목은_exit1(self):
        bad = 수리2.replace(
            "### 영향\n용어가 어긋난다.",
            "### 영향\n용어가 어긋난다.\n\n### 결합\n- 논지 선택 필요")
        Path("런/라운드1/수리_2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("상신", err)

    def test_조각도_상신도_없으면_exit1(self):
        # 계약/수리.md 「항목의 요건」은 항목마다 조각 하나 이상 또는 상신 칸
        # 하나를 요구한다. 둘 다 없는 항목은 적용할 문면도 올릴 선택지도 없다.
        bad = 수리2.replace(
            "### 상신\n- 선택지 가: 강경 논지\n- 선택지 나: 보수 논지\n", "")
        Path("런/라운드1/수리_2.md").write_text(bad, encoding="utf-8")
        code, out, err = 실행()
        self.assertEqual(code, 1)
        self.assertIn("조각 칸 하나 이상 또는 상신 칸", err)


if __name__ == "__main__":
    unittest.main()
