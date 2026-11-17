# R11 검산: D.central-gap-rational-audit (ㄷ) — H_j(theta)의 theta-차수.
# audit_K1.py의 g_series(멱급수 계산)만 떼어 읽어 theta=0..12의 값으로 유한 차분을 본다.
import io, re
from fractions import Fraction as Q
from math import comb, factorial, prod
src = io.open('원고_자료/rce3dc75/audit_K1.py', encoding='utf-8').read()
start = src.index('N = 9'); end = src.index('def newton_poly')
ns = {'Q': Q, 'comb': comb, 'factorial': factorial, 'prod': prod}
exec(src[start:end], ns)
g_series = ns['g_series']
for nu in (-1, 0):
    vals = [g_series(nu, Q(th)) for th in range(13)]
    degs = []
    for j in range(9):
        col = [v[j] for v in vals]; d = 0; cur = col
        while any(x != 0 for x in cur):
            cur = [cur[i+1]-cur[i] for i in range(len(cur)-1)]; d += 1
            if len(cur) == 0: d = None; break
        degs.append(None if d is None else d-1)
    print("nu =", nu, " theta-degree of H_0..H_8 (13 points):", degs)
