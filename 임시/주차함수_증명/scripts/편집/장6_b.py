# -*- coding: utf-8 -*-
"""장6 편집 2묶음: 느슨한 「자리」."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""반대쪽 끝항, 곧 망원 합이 용량 $k$의 자리에서 남기는 작은 경계항""",
 r"""반대쪽 끝항, 곧 망원 합이 크기 $k$에서 남기는 작은 경계항"""),

(r"""이 둘은 결손이 크기의 절반에 이르거나 넘는 자리의 점확률이다. 전형적인 결손은 크기의 삼분의 이 제곱 눈금이므로 그 자리는 큰 편차 쪽이고,""",
 r"""이 둘은 결손이 크기의 절반에 이르거나 넘는 수준의 점확률이다. 전형적인 결손은 크기의 삼분의 이 제곱 눈금이므로 그 수준은 큰 편차 쪽이고,"""),

(r"""이중합을 상태 $\mathfrak N$와 그 자리의 초과 $q=d-\mathfrak N$로 다시 묶는다.""",
 r"""이중합을 상태 $\mathfrak N$와 그 상태에서의 초과 $q=d-\mathfrak N$로 다시 묶는다."""),
]

if __name__ == "__main__":
    apply("장6.md", PAIRS, dry="--dry" in sys.argv)
