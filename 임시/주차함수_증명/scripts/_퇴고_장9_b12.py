# -*- coding: utf-8 -*-
"""장9 산문 퇴고 12묶음: 여섯째 독해의 지적 D8(부록 D의 표시 Q의 뜻) 반영."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS_D = [
(r"""의 구간 하한 이하이면 표시 I(증가 인증), 그렇지 않으면 표시 Q를 남긴다.""",
 r"""의 구간 하한 이하이면 표시 I(증가 인증)를, 그렇지 않으면, 곧 구간 비교만으로는 증가를 인증하지 못하면 표시 Q를 남긴다."""),
]

if __name__ == "__main__":
    apply("장v2/부록D_장9.md", PAIRS_D, dry="--dry" in sys.argv)
