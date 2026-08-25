# -*- coding: utf-8 -*-
"""verify-rounds의 수리·심사 범위 문면 회귀 시험."""

from __future__ import annotations

import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[2]


class ContractTextTest(unittest.TestCase):
    def test_수리자는_검사대상_산출물의_문제에서_시작한다(self):
        body = (SKILL / "계약" / "수리.md").read_text(encoding="utf-8")
        self.assertIn("산출물에 구현된 내용이나 동작의 문제", body)
        self.assertIn("원자료가 요구하지만 산출물에 구현되어 있지 않은 내용", body)
        self.assertIn("산출물에서 문제를 지목하지 못하면", body)
        self.assertNotIn("결함이 동결문 산출물 밖에 있으면 발견 항목으로 쓴다", body)

    def test_심사자는_발견의_산출물_문제와_밖의_원인을_같이_본다(self):
        body = (SKILL / "계약" / "심사.md").read_text(encoding="utf-8")
        flat = " ".join(body.split())
        self.assertIn("산출물 안의 문제", body)
        self.assertIn("산출물 밖의 근본 원인", body)
        self.assertIn("산출물 파일만 고쳐서 기준을 충족할 수", flat)


if __name__ == "__main__":
    unittest.main()
