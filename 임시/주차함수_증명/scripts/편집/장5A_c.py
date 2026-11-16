# -*- coding: utf-8 -*-
"""장5A 편집 3묶음: 5.1의 느슨한 「자리」."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""그러므로 두 재귀 안에서 뺄셈이 일어나는 자리는 쪼개짐 확률""",
 r"""그러므로 두 재귀 안에서 뺄셈이 일어나는 곳은 쪼개짐 확률"""),
]

if __name__ == "__main__":
    apply("장5A.md", PAIRS, dry="--dry" in sys.argv)
