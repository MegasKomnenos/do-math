# 수리 전체24 ZL — 묶음 6: 1.2·부록 A의 D^src_q 행의 묶인 지표를 본문 (8.6)의 j로(R13 3절 8·5절 4 — 8장에는 크기 변수 m이 있다; 0절 R1).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from 수리전체24_ZL_apply import apply
BASE = os.path.dirname(os.path.dirname(HERE))
J = os.path.join(BASE, '장부_v2.md')
A = os.path.join(BASE, '장v2', '부록A.md')
old = r'''$\frac q{k+q}\Psi(q)+\frac k{k+q}\sum_{m=1}^q\mathrm{Bor}(m)(1-s^{\mathrm{low}}_{q-m})$'''
new = r'''$\frac q{k+q}\Psi(q)+\frac k{k+q}\sum_{j=1}^q\mathrm{Bor}(j)(1-s^{\mathrm{low}}_{q-j})$'''
for dry in (True, False):
    apply(J, [(old + ' | 8.1 | 8 |', new + '(묶인 지표는 본문 (8.6)대로 $j$ — 8장에는 크기 변수 $m$이 있다, 2026-11-18 24차 R13 5절 4·ZL) | 8.1 | 8 |')], dry)
    apply(A, [(old, new)], dry)
