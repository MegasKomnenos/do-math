# -*- coding: utf-8 -*-
"""장9 산문 퇴고 2묶음 보정: 새로 들어간 인라인 수식 하나를 말로 되돌린다."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""$q$의 범위를 세 구간으로 나눈다. $j_\ast:=\lceil(3k)^{2/3}\rceil$로 둔다.""",
 r"""초과의 범위를 세 구간으로 나눈다. $j_\ast:=\lceil(3k)^{2/3}\rceil$로 둔다."""),
]

if __name__ == "__main__":
    apply("장v2/장9.md", PAIRS, dry="--dry" in sys.argv)
