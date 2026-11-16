# -*- coding: utf-8 -*-
"""장9 산문 퇴고 17묶음: 독해 12의 D4(두 수준 질량의 뜻을 첫 자리에서 말로)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _퇴고_장9_공통 import apply

PAIRS = [
(r"""$\mathrm{land}_m$을 착지 비라 부른다. 이 이름은 사건의 뜻에서 왔다.""",
 r"""두 수준 질량은 두 수준 개수를 같은 크기의 숲의 수로 나눈 확률이다. $\mathrm{land}_m$을 착지 비라 부른다. 이 이름은 사건의 뜻에서 왔다."""),
]

if __name__ == "__main__":
    apply("장v2/장9.md", PAIRS, dry="--dry" in sys.argv)
