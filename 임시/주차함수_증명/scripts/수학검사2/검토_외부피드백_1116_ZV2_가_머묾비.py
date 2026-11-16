# -*- coding: utf-8 -*-
"""외부 피드백 1116 (가) 검산 — 6.3절 머묾 법칙 (6.21) (y+1)ς_{y+d-1}(y) ≤ (d-1)c_{y+d}(y)의 실제 비.

묻는 것: 「(6.21)의 우변에 곱한 비례상수를 1보다 작게 할 수 없다」가 부등식 자체의 성질(최적 상수 1)인지,
계수별 전파 증명의 성질(θ<1이면 Cs^θ(d-1)<0)인지.

방법: 보조정리 chain-recursion (6.22)로 𝔰_d(y)=s_{y+d-1}(y)를 정확한 유리수로 계산한다. 핵
π_{y+d-1}(y+q)=Bor(d-q)Bor(y+q)/Bor(y+d)는 e의 지수가 지워져 유리수다(Bor(n)=n^{n-1}e^{-n}/n!).
d=y+3에서는 𝔱(y)/(y+1)^2를 더한다. 작은 y에서는 주차함수 전수 열거로 재귀의 구현을 맞춘다.
그 다음 비 R(y,d) := (y+1)ς_{y+d-1}(y) / ((d-1)c_{y+d}(y))를 2≤d≤y+2에서 구한다. (6.21)의 최적 비례상수는 sup R이다.
"""
from fractions import Fraction as Fr
from math import comb, factorial
from itertools import product
import sys

def Bor(n):  # e^{-n}을 뺀 Borel 질량 n^{n-1}/n!
    return Fr(n ** (n - 1), factorial(n))

def pi_kernel(y, d, q):  # π_{y+d-1}(y+q) = Bor(d-q)Bor(y+q)/Bor(y+d)
    return Bor(d - q) * Bor(y + q) / Bor(y + d)

def t_frak(y):  # 𝔱(y) = C(2y+2,y+1)(y+1)^{2y}/(2 p_{2y+2}),  p_n=(n+1)^{n-1}
    n = 2 * y + 2
    return Fr(comb(n, y + 1) * (y + 1) ** (2 * y), 2 * (n + 1) ** (n - 1))

def s_frak_all(y, dmax):
    """𝔰_d(y), d=1..dmax (dmax ≤ y+3), (6.22)로."""
    s = {1: Fr(1)}
    for d in range(2, dmax + 1):
        tot = Fr(0)
        for q in range(1, d):
            p = pi_kernel(y, d, q)
            tot += p * (1 - Fr(y, y + q) * s[q])
        val = 1 - tot
        if d == y + 3:
            val += t_frak(y) / (y + 1) ** 2
        s[d] = val
    return s

def brute_A(n):
    """A_{n,ℓ} (ℓ=-1..n-1): 최대 변위가 ℓ 이하인 길이 n 주차함수의 수. 전수 열거."""
    cnt = [0] * (n + 1)  # cnt[M] = 최대 변위가 정확히 M인 수
    for f in product(range(1, n + 1), repeat=n):
        occ = [False] * (n + 2)
        M = 0; ok = True
        for a in f:
            s = a
            while s <= n and occ[s]: s += 1
            if s > n: ok = False; break
            occ[s] = True
            if s - a > M: M = s - a
        if ok: cnt[M] += 1
    A = {-1: 0}
    run = 0
    for l in range(0, n):
        run += cnt[l]; A[l] = run
    assert run == (n + 1) ** (n - 1), (n, run)
    return A

def main():
    out = []
    # 1. 작은 y에서 재귀 구현을 전수 열거와 맞춘다 (m = y+d-1 ≤ 7).
    Acache = {}
    for y in (1, 2, 3):
        dmax = min(y + 3, 8 - y)
        s = s_frak_all(y, dmax)
        for d in range(1, dmax + 1):
            m = y + d - 1
            if m == 0:
                continue
            if m not in Acache: Acache[m] = brute_A(m)
            A = Acache[m]
            sm = Fr(A[y - 1], (m + 1) ** (m - 1))
            ok = (sm == s[d])
            out.append(f"y={y} d={d} (m={m}): 재귀 𝔰_d(y)={s[d]}  전수 s_m(y)={sm}  {'일치' if ok else '불일치!'}")
            assert ok
    # 2. 비 R(y,d)의 최댓값.
    for y in (50, 51, 60, 75, 100):
        sy = s_frak_all(y, y + 3)
        sy1 = s_frak_all(y + 1, y + 3)
        best = (Fr(0), None)
        rows = []
        for d in range(2, y + 3):
            stay = sy1[d] - sy[d]           # ς_{y+d-1}(y) = 𝔰_d(y+1) - 𝔰_d(y)
            lvl = sy1[d] - sy[d + 1]        # c_{y+d}(y) = 𝔰_d(y+1) - 𝔰_{d+1}(y)
            assert stay >= 0 and lvl > 0
            R = (y + 1) * stay / ((d - 1) * lvl)
            assert R <= 1, (y, d, float(R))  # (6.21)
            if R > best[0]: best = (R, d)
            if d in (2, 3, 4, 5, 10, 20, y // 2, y, y + 1, y + 2): rows.append((d, float(R)))
        out.append(f"y={y}: max_d R(y,d) = {float(best[0]):.6f} at d={best[1]};  "
                   + "  ".join(f"R({d})={r:.4f}" for d, r in rows))
    # 3. 상수 θ를 곱했을 때 계수 Cs^θ(q) = θ(d-1) - (y+1)q/(y+q)의 q=d-1 값.
    for th in (Fr(1), Fr(9, 10), Fr(99, 100)):
        y = 50
        vals = [(d, float(th * (d - 1) - Fr((y + 1) * (d - 1), y + d - 1))) for d in (2, 3, 4)]
        out.append(f"θ={th}: Cs^θ(d-1) at d=2,3,4 = " + ", ".join(f"{v:+.4f}" for _, v in vals))
    txt = "\n".join(out)
    print(txt)

def trend_mp(ys):
    """큰 y에서의 추세 — mpmath 60자리(유리수 대신). Bor(n)=exp((n-1)log n - n - lgamma(n+1))."""
    from mpmath import mp, mpf, log, loggamma, exp, binomial
    mp.dps = 60
    def Bor(n): n = mpf(n); return exp((n - 1) * log(n) - n - loggamma(n + 1))
    def s_all(y, dmax):
        s = {1: mpf(1)}
        for d in range(2, dmax + 1):
            tot = mpf(0)
            for q in range(1, d):
                tot += Bor(d - q) * Bor(y + q) / Bor(y + d) * (1 - mpf(y) / (y + q) * s[q])
            v = 1 - tot
            if d == y + 3:
                n = 2 * y + 2
                v += binomial(n, y + 1) * mpf(y + 1) ** (2 * y) / (2 * mpf(n + 1) ** (n - 1)) / (y + 1) ** 2
            s[d] = v
        return s
    res = []
    for y in ys:
        sy = s_all(y, y + 3); sy1 = s_all(y + 1, y + 3)
        best = (mpf(0), None)
        for d in range(2, y + 3):
            R = (y + 1) * (sy1[d] - sy[d]) / ((d - 1) * (sy1[d] - sy[d + 1]))
            if R > best[0]: best = (R, d)
        res.append(f"y={y}: max_d R = {float(best[0]):.6f} at d={best[1]} (mpmath 60자리)")
    return res

if __name__ == "__main__":
    main()
    print(chr(10).join(trend_mp((100, 200, 400, 800))))
