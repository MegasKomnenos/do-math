# -*- coding: utf-8 -*-
"""장9 산문 퇴고 1묶음 보정: 새로 들어간 인라인 수식 둘을 말로 되돌린다."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""도 용량 $w$의 합과 같은 열 집합에 걸친 합이다.""",
 r"""도 앞의 합과 같은 열 집합에 걸친 합이다."""),
(r"""그러므로 위 정리가 덮은 범위와 $\mathsf H^\ast$가 묻는 범위를 잇는 것은 증가 시작점의 상계이고,""",
 r"""그러므로 위 정리가 덮은 범위와 이 조건이 묻는 범위를 잇는 것은 증가 시작점의 상계이고,"""),
]

if __name__ == "__main__":
    apply("장v2/장9.md", PAIRS, dry="--dry" in sys.argv)
