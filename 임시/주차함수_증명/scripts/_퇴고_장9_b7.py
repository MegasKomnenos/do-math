# -*- coding: utf-8 -*-
"""장9 산문 퇴고 7묶음: 둘째 독해의 지적 D2·D3 반영."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""9.4절의 첫 층 하계와 9.3절의 행 비교는 첫 층 머리 합의 부호라는 같은 입력에 기대므로, 9.1절이 그것을 먼저 세운다.""",
 r"""9.1절은 먼저 9.4절의 첫 층 하계가 기대는 입력인 첫 층 머리 합의 부호를 세우고, 9.3절의 행 비교에도 쓰이는 무게중심 보조정리를 함께 둔다."""),
(r"""정량판 $\mathsf H^\ast_+$는 같은 범위에서 머리 합이 $-6/5$ 아래에 있다는 진술이다.""",
 r"""정량판 $\mathsf H^\ast_+$는 같은 범위에서 열의 용량을 곱한 머리 합이 $-6/5$ 아래에 있다는 진술이다."""),
]

if __name__ == "__main__":
    apply("장v2/장9.md", PAIRS, dry="--dry" in sys.argv)
