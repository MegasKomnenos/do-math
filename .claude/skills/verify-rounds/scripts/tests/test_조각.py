# -*- coding: utf-8 -*-
"""조각.py 단위 시험. 직접 실행이 정본(`python .claude/skills/verify-rounds/scripts/tests/test_조각.py`).

검사 대상은 여섯으로 한정한다:
① 좌표 표기의 해석·재생 — 구간·틈·머리, 표기 위반(a>b, a=0)의 거부, 왕복 동일성
② 교차 공식 — 공유 행, 틈과 가로지르는 구간, 접촉 비교차(계약/조각.md 4절의 네 예)
③ 정규화 — 교차 병합, 잇닿음 비병합, 틈 점의 독립
④ 칸 분해 — `### 조각 <k> — <좌표>` 동적 이름과 닫힌 이름의 공존, 울타리 안 `###` 무시
⑤ 조각 칸 판독 — 원래·대체 블록, `대체: 원래대로`, 라벨 중복·블록 없는 라벨의 오류
⑥ 적용 엔진 — 서로소 조각의 역순 반영(치환·삭제·틈 삽입)
그 밖의 검사는 두지 않는다.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import 조각  # noqa: E402


class CoordTest(unittest.TestCase):
    def test_구간_해석(self):
        self.assertEqual(조각.parse_좌표("제품.md 3~5행"), ("제품.md", 6, 10))
        self.assertEqual(조각.parse_좌표("제품.md 3~3행"), ("제품.md", 6, 6))

    def test_틈_해석(self):
        self.assertEqual(조각.parse_좌표("제품.md 행 6 뒤"), ("제품.md", 13, 13))
        self.assertEqual(조각.parse_좌표("제품.md 행 0 뒤"), ("제품.md", 1, 1))

    def test_표기_위반은_None(self):
        self.assertIsNone(조각.parse_좌표("제품.md 5~3행"))
        self.assertIsNone(조각.parse_좌표("제품.md 0~3행"))
        self.assertIsNone(조각.parse_좌표("제품.md 3행"))

    def test_왕복_동일(self):
        for s in ("제품.md 3~5행", "제품.md 행 6 뒤", "제품.md 행 0 뒤"):
            p, a, b = 조각.parse_좌표(s)
            self.assertEqual(조각.format_좌표(p, a, b), s)


class IntersectTest(unittest.TestCase):
    def s(self, a, b):
        return 2 * a, 2 * b

    def test_공유행은_교차(self):
        self.assertTrue(조각.intersects(*self.s(3, 5), *self.s(5, 7)))

    def test_틈을_가로지르는_구간은_교차(self):
        # [3, 4]는 틈 3.5(=7)를 덮는다
        self.assertTrue(조각.intersects(*self.s(3, 4), 7, 7))

    def test_접촉은_비교차(self):
        self.assertFalse(조각.intersects(*self.s(1, 3), 7, 7))  # [1,3]과 행 3 뒤
        self.assertFalse(조각.intersects(*self.s(4, 6), 7, 7))  # [4,6]과 행 3 뒤

    def test_같은_틈끼리는_교차(self):
        self.assertTrue(조각.intersects(7, 7, 7, 7))


class NormalizeTest(unittest.TestCase):
    def test_교차_병합(self):
        self.assertEqual(조각.normalize([(6, 10), (10, 14)]), [(6, 14)])

    def test_잇닿음은_비병합(self):
        self.assertEqual(조각.normalize([(2, 6), (8, 10)]), [(2, 6), (8, 10)])

    def test_틈점은_덮는_구간에_흡수(self):
        self.assertEqual(조각.normalize([(6, 8), (7, 7)]), [(6, 8)])
        self.assertEqual(조각.normalize([(2, 6), (7, 7)]), [(2, 6), (7, 7)])


class SplitCellsTest(unittest.TestCase):
    def test_동적_이름과_울타리(self):
        body = ("머리 줄.\n### 위치\n어디.\n### 조각 1 — 제품.md 3~3행\n"
                "원래:\n```\n### 울타리 안 가짜 칸\n```\n대체:\n```\n새 문면\n```\n")
        head, cells = 조각.split_cells(body)
        self.assertEqual(head, ["머리 줄."])
        self.assertEqual([c.name for c in cells],
                         ["위치", "조각 1 — 제품.md 3~3행"])
        self.assertEqual(조각.조각칸_이름(cells[1].name),
                         (1, "제품.md 3~3행"))
        self.assertIsNone(조각.조각칸_이름("위치"))


class ParseCellTest(unittest.TestCase):
    def test_원래_대체_판독(self):
        body = "원래:\n```\n옛 문면\n```\n대체:\n```\n새 문면\n```"
        values, errors = 조각.parse_조각_cell(body)
        self.assertEqual(errors, [])
        self.assertEqual(values, {"원래": "옛 문면", "대체": "새 문면"})

    def test_원래대로(self):
        values, errors = 조각.parse_조각_cell("대체: 원래대로")
        self.assertEqual(errors, [])
        self.assertEqual(values, {"대체": "원래대로"})

    def test_빈_대체는_삭제(self):
        values, errors = 조각.parse_조각_cell("대체:\n```\n```")
        self.assertEqual(errors, [])
        self.assertEqual(values["대체"], "")

    def test_오류_라벨중복과_블록없는_라벨(self):
        _v, errors = 조각.parse_조각_cell(
            "원래:\n```\nx\n```\n원래:\n```\ny\n```\n대체:")
        self.assertTrue(any("중복" in e for e in errors))
        self.assertTrue(any("블록 없는 라벨" in e for e in errors))


class ApplyTest(unittest.TestCase):
    def test_치환_삭제_삽입_역순(self):
        lines = ["하나", "둘", "셋", "넷"]
        pieces = [
            {"시작2": 2, "끝2": 2, "대체": "하나 고침", "id": "R1-01"},   # 1행 치환
            {"시작2": 4, "끝2": 6, "대체": "", "id": "R1-02"},           # 2~3행 삭제
            {"시작2": 7, "끝2": 7, "대체": "삽입", "id": "R1-03"},       # 행 3 뒤 삽입
        ]
        out = 조각.apply_pieces(lines, pieces)
        self.assertEqual(out, ["하나 고침", "삽입", "넷"])

    def test_여러_줄_대체(self):
        lines = ["하나", "둘"]
        pieces = [{"시작2": 4, "끝2": 4, "대체": "둘-1\n둘-2", "id": "R1-01"}]
        out = 조각.apply_pieces(lines, pieces)
        self.assertEqual(out, ["하나", "둘-1", "둘-2"])


if __name__ == "__main__":
    unittest.main()
