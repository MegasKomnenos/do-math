# -*- coding: utf-8 -*-
"""장3 편집 1묶음: 장 머리의 모호한 지시 「뒤의 두 장」."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""주 정리는 행이 모든 길이에서 단봉이라는 주장이고, 뒤의 두 장에는 서로 독립인 완결된 증명이 하나씩 있다.""",
 r"""주 정리는 행이 모든 길이에서 단봉이라는 주장이고, 9장과 10장에 서로 독립인 완결된 증명이 하나씩 있다."""),
]

if __name__ == "__main__":
    apply("장3.md", PAIRS, dry="--dry" in sys.argv)
