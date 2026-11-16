# -*- coding: utf-8 -*-
"""장2 편집 3묶음: 2.11 도입에서 「보행」이 정의(확률보행) 앞에 나오던 자리."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""뒤에서는 이 두 사실로 사슬의 법칙을 Borel 보행의 법칙으로 바꾸어 다룬다.""",
 r"""뒤에서는 이 두 사실로 사슬의 법칙을 그 부분합들의 법칙으로 바꾸어 다룬다."""),
]

if __name__ == "__main__":
    apply("장2.md", PAIRS, dry="--dry" in sys.argv)
