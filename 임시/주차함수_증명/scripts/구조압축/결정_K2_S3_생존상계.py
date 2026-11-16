# -*- coding: utf-8 -*-
# 결정 K2 — S3: 10.21의 7단계 계수·네 경우를 y>=3130(q>=235), y>=4000(q>=277), y>=2000(q>=174)에서 다시 센다(mpmath 40자리).
# 따름 (상수 3 꼴): 1.15(k+q+1)/(q+1)^{3/2} <= 3k q^{-3/2}  (1<=q<=k, k>=2).
import sys
from mpmath import mp, mpf, sqrt, pi, floor, log
sys.stdout.reconfigure(encoding='utf-8')
mp.dps = 40
c = 2/sqrt(2*pi)
def Ecoef(q, u):
    return c*(mpf(1)/4*(1-mpf(1)/(2*q))**(-mpf(3)/2) + (1+u+u*u)*(1-u)**(-mpf(1)/2)*(1+u)**(-mpf(3)/2))
def Fval(u):
    return c*(1+2*u*u)*sqrt(1-u*u)
for y in (2000, 3130, 4000, 6666):
    aprime = int(floor((mpf('1.15')*y)**(mpf(2)/3)))
    q = aprime + 1
    bands = [(mpf(0), mpf('0.9')), (mpf('0.9'), mpf('0.99')), (mpf('0.99'), mpf('0.9999'))]
    out = []
    for (lo, hi) in bands:
        # E 계수는 u 에 증가 → 오른끝; F 의 최댓값: 첫 띠는 u=1/√2 에서 √2 c=1.12838, 둘째·셋째 띠는 u=lo 에서(감소 구간)
        E = Ecoef(q, hi)
        if lo == 0:
            Fm = c*sqrt(2)
        else:
            Fm = Fval(lo)
        out.append((float(E), float(Fm), float(Fm + E/q)))
    tail = 0.182 + 7.3*0.0003
    print(f"y>={y}: a'={aprime}, q>={q}; 띠별 (E계수, F최대, F+E/q) = " + "; ".join(f"({e:.4f},{f:.5f},{t:.5f})" for e,f,t in out) + f"; 넷째 경우 {tail:.5f}; 모두<1.15: {all(t<1.15 for _,_,t in out) and tail<1.15}; 조건 q/50-1/2>=0.77q/50 ⇔ q>=108.7: {q>=109}")
# 따름: 상수 3 꼴
worst = None
for k in (2, 3, 10, 100, 3130, 4000, 10**6):
    for q in range(1, min(k, 3000)+1):
        r = mpf('1.15')*(k+q+1)/(q+1)**mpf(1.5) / (3*k/mpf(q)**mpf(1.5))
        if worst is None or r > worst[0]:
            worst = (r, k, q)
print(f"따름(상수 3): max_{{k,q}} [1.15(k+q+1)/(q+1)^1.5] / [3k q^-1.5] = {float(worst[0]):.5f} at k={worst[1]}, q={worst[2]} (<1 이면 성립)")
# 1.15(k+q+1) <= 3k ⇔ q <= (1.85k-1.15)/1.15 ; q<=k 에서 1.15(2k+1)<3k ⇔ k>1.643
print("1.15(2k+1)<3k ⇔ k>1.643 → k>=2 성립")
