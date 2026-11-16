# -*- coding: utf-8 -*-
"""장5A 편집 1묶음: 장 머리의 문서 주어 문장, 5.4 임계 창 인증의 격자 「칸」→「셀」(사전 3절)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""이 장이 앞 장들에서 가져와 쓰는 것은""",
 r"""이 장에서 앞 장들로부터 가져와 쓰는 것은"""),

(r"""주부는 $\hat{\mathrm{ag}}$의 격자 $480$칸에서 사다리꼴 공식과 도함수의 둘러싸기로 평가하고""",
 r"""주부는 $\hat{\mathrm{ag}}$의 범위를 $480$개 셀로 나눈 격자에서 사다리꼴 공식과 도함수의 둘러싸기로 평가하고"""),

(r"""$|\hat\varphi|\le10$은 $300$칸의 중점법,""",
 r"""$|\hat\varphi|\le10$은 $300$개 셀의 중점법,"""),

(r"""$v=\mathrm{ku} s$로 바꾼 적분을 $s$의 격자 $6400$칸의 단조 상·하합으로,""",
 r"""$v=\mathrm{ku} s$로 바꾼 적분을 $s$의 범위를 $6400$개 셀로 나눈 격자의 단조 상·하합으로,"""),
]

if __name__ == "__main__":
    apply("장5A.md", PAIRS, dry="--dry" in sys.argv)
