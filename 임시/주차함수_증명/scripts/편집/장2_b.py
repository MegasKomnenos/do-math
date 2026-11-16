# -*- coding: utf-8 -*-
"""장2 편집 2묶음: 2.12 도입의 「~므로 … ~므로」 겹침."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""$n\ge2r+1$이면 그 크기는 $n/2$를 넘으므로 그런 꼭짓점들의 부분나무는 한 숲 안에서 서로 포개지므로 그 꼭짓점들은 한 사슬을 이룬다.""",
 r"""$n\ge2r+1$이면 그 크기는 $n/2$를 넘으므로 그런 꼭짓점들의 부분나무는 한 숲 안에서 서로 포개지고, 따라서 그 꼭짓점들은 한 사슬을 이룬다."""),
]

if __name__ == "__main__":
    apply("장2.md", PAIRS, dry="--dry" in sys.argv)
