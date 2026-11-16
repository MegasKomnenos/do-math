# -*- coding: utf-8 -*-
"""장4 편집 2묶음: 4.1의 「자리」, 4.2의 장 주어 문장."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""이 명제는 「감소 뒤에 증가가 오는 자리가 없다」는 말로 바꾸어 적을 수 있고, 그렇게 적으면 그 자리가 행의 어느 쪽에 놓이는가에 따라 명제를 넷으로 나눌 수 있다.""",
 r"""이 명제는 「감소 뒤에 증가가 오는 일이 없다」는 말로 바꾸어 적을 수 있고, 그렇게 적으면 그 감소와 증가가 행의 어느 쪽에 놓이는가에 따라 명제를 넷으로 나눌 수 있다."""),

(r"""다음 장은 오른쪽 절반의 위치 $(n,k)$, $k+2\le n\le2k-1$에서 $\mathsf Q_R$을 다룬다. 그 장에서는""",
 r"""다음 장에서는 오른쪽 절반의 위치 $(n,k)$, $k+2\le n\le2k-1$에서 $\mathsf Q_R$을 다룬다. 거기서는"""),
]

if __name__ == "__main__":
    apply("장4.md", PAIRS, dry="--dry" in sys.argv)
