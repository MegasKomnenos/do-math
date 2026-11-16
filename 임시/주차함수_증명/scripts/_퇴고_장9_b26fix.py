# -*- coding: utf-8 -*-
"""장9 산문 퇴고 26묶음 보정: 증가 시작점 문장에서 빠진 인라인 기호 $k$를 되살린다."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""이 값을 증가 시작점이라 부른다.""",
 r"""이 값을 열 $k$의 증가 시작점이라 부른다."""),
]

if __name__ == "__main__":
    apply("장v2/장9.md", PAIRS, dry="--dry" in sys.argv)
