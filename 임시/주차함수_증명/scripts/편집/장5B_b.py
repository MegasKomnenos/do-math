# -*- coding: utf-8 -*-
"""장5B 편집 2묶음: 5.7의 「서로 다른 결과로」가 불변식의 구별 문장 꼴에 걸리던 자리."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 공통 import apply

PAIRS = [
(r"""행의 크기와 꼬리 좌표의 범위에 따라 서로 다른 결과로 덮이며, 그 분담은 다음 표와 같다.""",
 r"""행의 크기와 꼬리 좌표의 범위에 따라 덮는 결과가 달라지며, 그 분담은 다음 표와 같다."""),
]

if __name__ == "__main__":
    apply("장5B.md", PAIRS, dry="--dry" in sys.argv)
