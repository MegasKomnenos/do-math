# -*- coding: utf-8 -*-
# 수리 V6 — 전수 검색이 남긴 잔여: 소멸 기록 rc391829의 글자 참조(장부 1.2·부록 A tail 행), 1.3 묶음의 옛 전역 $P_t(k)$ 언급 둘, 3절 「꼬리」 행의 「평평한 꼬리」(본문 0).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
ROOT = os.path.join(HERE, '..', '..')
LEDGER = os.path.join(ROOT, '장부_v2.md')
A = os.path.join(ROOT, '장v2', '부록A.md')

ops12 = [('sub', r'| $\mathrm{tail}_s(y)$ |', r'; $\mathcal T_S$ ([rc391829]; 인수 $y=k$ 고정)', '')]
ops13 = [
    ('sub', r'| $\mathrm{cp}(y)=\prod\min(\cdot,y)$(양의 정수 다중집합의 ', r'1.2 $P_t(k)$·8장 전역', r'1.2 $P_n(y)$·8장 전역'),
    ('sub', '| 정리 `{{7:old-6-6}}`·따름정리 `{{7:flat-threshold}}`의 ', r'7장 전역 $P_t(k)$ 회피', r'1.2 전역 $P_n(y)$ 회피'),
]
ops3 = [('sub', '| 꼬리 |', '꼬리합, 평평한 꼬리, Borel 꼬리, 꼬리 항) | 1.5 | 꼬리(여섯 쓰임; 뜻은 하나) |', '꼬리합, Borel 꼬리, 꼬리 항) | 1.5 | 꼬리(다섯 쓰임; 뜻은 하나) |')]
opsA = [('sub', r'| $\mathrm{tail}_s(y)$ |', r'; $\mathcal T_S$ ([rc391829]; 인수 $y=k$ 고정)', '')]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(LEDGER, ops12, dry=dry, region=('### 1.2', '### 1.3'))
    apply(LEDGER, ops13, dry=dry, region=('### 1.3', '## 2. '))
    apply(LEDGER, ops3, dry=dry, region=('## 3. ', '## 4. '))
    apply(A, opsA, dry=dry)
