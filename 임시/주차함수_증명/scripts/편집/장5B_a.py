# -*- coding: utf-8 -*-
"""장5B 편집 1묶음: 5.7 조립의 문서 주어 문장."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""이 장이 범위별로 무엇을 증명했는지 한자리에 모아 둔다.""",
 r"""이 장에서 범위별로 무엇을 증명했는지를 한자리에 모아 둔다."""),
]

if __name__ == "__main__":
    apply("장5B.md", PAIRS, dry="--dry" in sys.argv)
