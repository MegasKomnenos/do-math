# -*- coding: utf-8 -*-
# 수리 V6 — 뒤늦게 받은 인계(X4 (a), X1-9)의 작은 손 편집: 장부 1.2 $\mathfrak c_0(N)$ 뜻, 3절·부록 C 「깊은 낙하」(8장 본문 0), 부록 C 「원천 쪽」 행.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
LEDGER = os.path.join(HERE, '..', '..', '장부_v2.md')
C = os.path.join(HERE, '..', '..', '장v2', '부록C.md')

ops12 = [
    ('sub', r'| $\mathfrak c_0(N)$ |', r'보조정리 `{{8:old-6-30}}` (가)(다)의 큰 쪽', r'보조정리 `{{2:capacity-shift-ratio}}`의 하계와 보조정리 `{{8:old-6-30}}`(나)의 하계 가운데 큰 쪽'),
]
ops3 = [('del_row', '| 깊은 낙하 |')]
opsC = [
    ('del_row', '| 깊은 낙하 |'),
    ('set_row', '| 원천 쪽 |', '| 원천 쪽 | 원천 쪽(기록의 명제 이름 SRC⁺) | 7.5 |'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(LEDGER, ops12, dry=dry, region=('### 1.2', '### 1.3'))
    apply(LEDGER, ops3, dry=dry, region=('## 3. ', '## 4. '))
    apply(C, opsC, dry=dry)
