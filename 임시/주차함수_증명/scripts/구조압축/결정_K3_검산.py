# -*- coding: utf-8 -*-
"""결정 K3 검산 — 2장 새 진술의 항등식을 정확 산술로 확인한다(python -I; fractions·sympy·mpmath).
(1) 정리 G(가)(나)(다)(라): 가중 분배함수 — 순열 합 = 숲 합(국소 역전 수 세분 포함), 재귀, 지수 공식, 상수 꼬리 닫힌 꼴.
(2) 따름 G2: 두 변수 얼린 다항식의 닫힌 꼴과 특수화, 유한 교대 항등식, deg<=floor(n/k).
(3) (B) 지정 사슬 공식 — D/A 고리별 Bor/Ren 인자, (ㄴ) 서로소 뿌리 나무, P_m(j)=(j/m)pi_m(j).
(4) (A) 표시 나무 전개 — 전 차수 항등식, 나머지 계수 비음성, n<=3k-1에서 O_n=PAIR_n, 3k 행 보정, 양의 꼴.
(5) (C) 용량 곱 한 걸음 비 — 다중집합 항등식 둘.
(6) Borel 산술 — rb_m 감소·Robbins 구간, Bor 비 상하계, Psi 하계 세 꼴의 순서.
(7) h-변환 항등식 — 자유 Borel 보행 기준, h=Bor(y+.): s-s0 = -sum (q/y) M0(q)(h(q)/h(d)-1).
(8) 상위해 원리 — T[1] = 10.11의 s^W(좌표 q<->q+1), T[1]<=1.
(9) nf 로그 계수 2d^i/i <= lc_i <= 5d^i/(2i); 합성 법칙.
(10) 가중 수준 방문 보존 — Abel 등식 판과 ς>=0.
표본 범위는 작다(숲 전수 n<=5, 순열 n<=6).
"""
from fractions import Fraction as Fr
from itertools import permutations, product
from math import comb, factorial
import random

OUT = []
def say(*a):
    s = ' '.join(str(x) for x in a); OUT.append(s); print(s)

random.seed(20261117)

# ---------- 기본 도구 ----------
def capacities(sigma):
    n = len(sigma); h = []
    for i in range(n):
        z = 0
        for j in range(i - 1, -1, -1):
            if sigma[j] > sigma[i]:
                z = j + 1; break
        h.append(i + 1 - z)
    return h

def rooted_forests(n):
    if n == 0:
        yield (); return
    for par in product(range(0, n + 1), repeat=n):
        ok = True
        for v in range(1, n + 1):
            seen = set(); u = v
            while u != 0:
                if u in seen:
                    ok = False; break
                seen.add(u); u = par[u - 1]
            if not ok: break
        if ok: yield par

def subtree_sizes(par, n):
    ch = {v: [] for v in range(0, n + 1)}
    for v in range(1, n + 1): ch[par[v - 1]].append(v)
    t = {}
    def dfs(v):
        s = 1
        for c in ch[v]: s += dfs(c)
        t[v] = s; return s
    for r in ch[0]: dfs(r)
    return t, ch

def local_inversions(n, ch):
    I = {}
    def desc(v):
        out = []
        for c in ch[v]:
            out.append(c); out += desc(c)
        return out
    for v in range(1, n + 1):
        I[v] = sum(1 for u in desc(v) if u < v)
    return I

FORESTS = {n: list(rooted_forests(n)) for n in range(0, 6)}
for n in range(1, 6):
    assert len(FORESTS[n]) == (n + 1) ** (n - 1)

def p(n): return (n + 1) ** (n - 1) if n >= 1 else 1
def Borq(m): return Fr(m ** (m - 1), factorial(m))      # Bor(m) = e^{-m} Borq(m)
def Renq(j): return Fr(j ** j, factorial(j)) if j >= 1 else Fr(1)  # Ren(j) = e^{-j} Renq(j)

def prodw(h, wg):
    r = Fr(1)
    for x in h: r *= wg[x]
    return r

def series_mul(A, B, M):
    C = [Fr(0)] * (M + 1)
    for i, x in enumerate(A):
        if x == 0: continue
        for j, y in enumerate(B):
            if i + j > M: break
            C[i + j] += x * y
    return C
def series_exp(A, M):
    E = [Fr(0)] * (M + 1); E[0] = Fr(1)
    for n in range(1, M + 1):
        E[n] = sum(t * A[t] * E[n - t] for t in range(1, n + 1)) / n
    return E
def series_int(A, M):
    I = [Fr(0)] * (M + 1)
    for i in range(M): I[i + 1] = A[i] / (i + 1)
    return I
def series_inv(A, M):
    B = [Fr(0)] * (M + 1); B[0] = Fr(1)
    for n in range(1, M + 1):
        B[n] = -sum(A[i] * B[n - i] for i in range(1, n + 1))
    return B
def series_log(A, M):
    L = [Fr(0)] * (M + 1)
    for n in range(1, M + 1):
        L[n] = (n * A[n] - sum(t * L[t] * A[n - t] for t in range(1, n))) / n
    return L

# ---------- (1) 정리 G ----------
say("== (1) 정리 G: 가중 분배함수 ==")
def Z_perm(n, wg):
    if n == 0: return Fr(1)
    return sum(prodw(capacities(s), wg) for s in permutations(range(1, n + 1)))
def Z_forest(n, a):
    tot = Fr(0)
    for par in FORESTS[n]:
        t, ch = subtree_sizes(par, n); I = local_inversions(n, ch)
        r = Fr(1)
        for v in range(1, n + 1): r *= a[(t[v], I[v])]
        tot += r
    return tot
N = 5
a = {}; wg = {}
for t in range(1, N + 2):
    for d in range(t): a[(t, d)] = Fr(random.randint(1, 9), random.randint(1, 5))
    wg[t] = sum(a[(t, d)] for d in range(t))
ok1 = True
Zs = {0: Fr(1)}
for n in range(1, N + 1):
    zp = Z_perm(n, wg); zf = Z_forest(n, a)
    rec = sum(comb(n - 1, j) * wg[j + 1] * Zs[j] * Zs[n - 1 - j] for j in range(n))
    Zs[n] = zp
    ok1 &= (zp == zf == rec)
    say(f"  n={n}: 순열합={zp} 숲합(세분)={zf} 재귀={rec} 일치={zp == zf == rec}")
say("  G(가)(나) 성립:", ok1)
ok1c = True
for n in range(1, N + 1):
    lhs = Fr(n) * Zs[n] / factorial(n)
    rhs = sum(wg[t] * Zs[t - 1] / factorial(t - 1) * Zs[n - t] / factorial(n - t) for t in range(1, n + 1))
    ok1c &= (lhs == rhs)
say("  G(다) 로그 미분 꼴 Z'=(sum wg_t Z_{t-1} x^{t-1}/(t-1)!) Z:", ok1c)
K = 2; c = Fr(3, 2); wgc = {t: (wg[t] if t <= K else c) for t in range(1, N + 2)}
Zc = {0: Fr(1)}
for n in range(1, N + 1):
    Zc[n] = sum(comb(n - 1, j) * wgc[j + 1] * Zc[j] * Zc[n - 1 - j] for j in range(n))
M = N
R = [Fr(0)] * (M + 1)
for t in range(1, K + 1): R[t] = (wgc[t] - c) * Zc[t - 1] / factorial(t)
eR = series_exp(R, M); I = series_int(eR, M)
den = [Fr(1)] + [-c * I[i] for i in range(1, M + 1)]
Zcl = series_mul(eR, series_inv(den, M), M)
ok1d = all(Zcl[n] == Zc[n] / factorial(n) for n in range(M + 1))
say("  G(라) 상수 꼬리 닫힌 꼴 e^R/(1-c∫e^R) (K=2, c=3/2, n<=5):", ok1d)

# ---------- (2) 따름 G2 ----------
say("== (2) 따름 G2: 두 변수 얼린 다항식 ==")
def K2var(n, k, eta, y):
    if n == 0: return Fr(1)
    tot = Fr(0)
    for s in permutations(range(1, n + 1)):
        r = Fr(1)
        for x in capacities(s):
            r *= (Fr(x) if x < k else (eta if x == k else y))
        tot += r
    return tot
def A_nl(n, l):
    if n == 0: return Fr(1)
    return sum(prodw(capacities(s), {x: Fr(min(x, l + 1)) for x in range(1, n + 1)}) for s in permutations(range(1, n + 1)))
ok2a = True
for k in (2, 3):
    for n in range(0, 6):
        ok2a &= (K2var(n, k, Fr(k), Fr(k)) == A_nl(n, k - 1))
        ok2a &= (K2var(n, k, Fr(k), Fr(k + 1)) == A_nl(n, k))
        ok2a &= (K2var(n, k, Fr(k - 1), Fr(k - 1)) == A_nl(n, k - 2))
say("  G2(ㄱ) K(k,k)=A_{k-1}, K(k,k+1)=A_k, K(k-1,k-1)=A_{k-2} (k=2,3; n<=5):", ok2a)
ok2b = True
for k in (2, 3):
    eta = Fr(7, 3); y = Fr(5, 2); M = 5
    R = [Fr(0)] * (M + 1)
    for t in range(1, k): R[t] = (t - y) * Fr(p(t - 1)) / factorial(t)
    R[k] = (eta - y) * Fr(p(k - 1)) / factorial(k)
    eR = series_exp(R, M); I = series_int(eR, M)
    den = [Fr(1)] + [-y * I[i] for i in range(1, M + 1)]
    Zcl = series_mul(eR, series_inv(den, M), M)
    for n in range(M + 1):
        ok2b &= (Zcl[n] * factorial(n) == K2var(n, k, eta, y))
say("  G2 닫힌 꼴 e^R/(1-y∫e^R), R=sum_{t<k}(t-y)p_{t-1}x^t/t!+(eta-y)p_{k-1}x^k/k! (k=2,3; n<=5):", ok2b)
from sympy import symbols, Poly, diff, factorial as sfact, sympify
ETA = symbols('eta')
ok2c = True
for k in (2, 3):
    for n in range(1, 6):
        expr = 0
        for s in permutations(range(1, n + 1)):
            term = 1
            for x in capacities(s):
                term *= (x if x < k else (ETA if x == k else (k - 1)))
            expr += term
        expr = sympify(expr)
        poly = Poly(expr, ETA)
        B = expr.subs(ETA, k) - expr.subs(ETA, k - 1)
        rhs = 0
        for r in range(1, max(poly.degree(), 1) + 1):
            rhs += (-1) ** (r - 1) * diff(expr, ETA, r).subs(ETA, k) / sfact(r)
        ok2c &= ((B - rhs).expand() == 0)
        ok2c &= (poly.degree() <= n // k)
say("  G2(ㄷ) B=K(k,k-1)-K(k-1,k-1)=sum_{r>=1}(-1)^{r-1}∂^r K(k,k-1)/r!, deg_eta<=floor(n/k) (k=2,3; n<=5):", ok2c)

# ---------- (3) (B) 지정 사슬 공식 ----------
say("== (3) (B) 지정 사슬 공식: D/A 고리 ==")
def count_chains(n, sizes, links):
    cnt = 0
    for par in FORESTS[n]:
        t, ch = subtree_sizes(par, n)
        def anc(v):
            out = []; u = par[v - 1]
            while u != 0:
                out.append(u); u = par[u - 1]
            return out
        cand = [[v for v in range(1, n + 1) if t[v] == s] for s in sizes]
        for tup in product(*cand):
            ok = True
            if links[0] == 'D' and par[tup[0] - 1] != 0: ok = False
            for i in range(1, len(tup)):
                if links[i] == 'D':
                    if par[tup[i] - 1] != tup[i - 1]: ok = False
                else:
                    if tup[i - 1] not in anc(tup[i]): ok = False
            if ok: cnt += 1
    return cnt
def formula(n, sizes, links):
    gam = [n + 1 - sizes[0]] + [sizes[i - 1] - sizes[i] for i in range(1, len(sizes))]
    val = Borq(sizes[-1]) / Borq(n + 1)
    for g, l in zip(gam, links):
        val *= (Borq(g) if l == 'D' else Renq(g))
    return val
ok3 = True
tests = [(5, (3,), 'D'), (5, (3,), 'A'), (5, (4, 2), 'AA'), (5, (4, 2), 'DD'), (5, (4, 2), 'DA'), (5, (4, 2), 'AD'),
         (5, (5, 3, 1), 'AAA'), (5, (5, 3, 1), 'DDD'), (5, (3, 1), 'DA'), (4, (2, 1), 'AD')]
for n, sizes, links in tests:
    ex = Fr(count_chains(n, sizes, links), p(n)); fm = formula(n, sizes, links)
    ok3 &= (ex == fm)
    say(f"  n={n} sizes={sizes} links={links}: 전수 기대수={ex} 공식={fm} 일치={ex == fm}")
say("  (B) D/A 공식 성립:", ok3)
def count_components(n, sizes):
    cnt = 0
    for par in FORESTS[n]:
        t, ch = subtree_sizes(par, n)
        for tup in product(ch[0], repeat=len(sizes)):
            if len(set(tup)) < len(tup): continue
            if all(t[v] == s for v, s in zip(tup, sizes)): cnt += 1
    return cnt
ok3b = True
for n, sizes in [(5, (2,)), (5, (3,)), (5, (2, 2)), (5, (3, 1)), (4, (1, 2)), (5, (1, 1, 2))]:
    ex = Fr(count_components(n, sizes), p(n)); fm = Fr(1)
    for s in sizes: fm *= Borq(s)
    fm *= Borq(n + 1 - sum(sizes)) / Borq(n + 1)
    ok3b &= (ex == fm)
say("  (B)(ㄴ) 서로소 뿌리 나무 순서쌍 공식 성립:", ok3b)
ok3c = True
for m in range(1, 21):
    for j in range(1, m + 1):
        P = Fr(j * comb(m - 1, j - 1) * p(j - 1) * p(m - j), p(m)); piv = Fr(comb(m, j) * j ** (j - 1) * p(m - j), p(m))
        ok3c &= (P == Fr(j, m) * piv)
say("  P_m(j)=(j/m)pi_m(j) (m<=20):", ok3c)

# ---------- (4) (A) 표시 나무 전개 ----------
say("== (4) (A) 표시 나무 전개 ==")
def A_series(l, M):
    A = [Fr(1)]
    for n in range(1, M + 1):
        A.append(sum(comb(n - 1, j) * min(j + 1, l + 1) * A[j] * A[n - 1 - j] for j in range(n)))
    return [A[n] / factorial(n) for n in range(M + 1)]
ok4 = True
for k in (2, 3):
    M = 3 * k + 3
    Ak = A_series(k, M); Ak1 = A_series(k - 1, M); Ak2 = A_series(k - 2, M)
    Tk = series_log(Ak, M); Tk1 = series_log(Ak1, M); Tk2 = series_log(Ak2, M)
    U = [Tk[i] - Tk1[i] for i in range(M + 1)]; V = [Tk1[i] - Tk2[i] for i in range(M + 1)]
    F = Ak1; G = Ak2
    D = [Ak[i] - 2 * Ak1[i] + Ak2[i] for i in range(M + 1)]
    def powsum(S, coef):
        tot = [Fr(0)] * (M + 1); P = [Fr(1)] + [Fr(0)] * M
        for j in range(1, M + 2):
            P = series_mul(P, S, M)
            if j >= 2:
                cj = coef(j)
                for i in range(M + 1): tot[i] += cj * P[i]
        return tot
    rem = [x + y for x, y in zip(series_mul(F, powsum(U, lambda j: Fr(1, factorial(j))), M),
                                  series_mul(G, powsum(V, lambda j: Fr(j - 1, factorial(j))), M))]
    main = series_mul(F, [U[i] - V[i] for i in range(M + 1)], M)
    ok4 &= all(D[i] == main[i] + rem[i] for i in range(M + 1))
    ok4 &= all(rem[i] >= 0 for i in range(M + 1))
    U2 = series_mul(U, U, M); V2 = series_mul(V, V, M)
    PAIR = series_mul(F, [Fr(1, 2) * (U2[i] + V2[i]) for i in range(M + 1)], M)
    eq = [rem[i] == PAIR[i] for i in range(M + 1)]
    ok4 &= all(eq[:3 * k]) and (not eq[3 * k])
    corr = Fr(factorial(3 * k) * k ** (3 * (k - 2)), 6 * factorial(k) ** 3)
    ok4 &= (rem[3 * k] * factorial(3 * k) == PAIR[3 * k] * factorial(3 * k) - corr)
    eV = series_exp(V, M)
    lhs = [Ak1[i] - Ak2[i] for i in range(M + 1)]
    rhs = series_mul(G, [eV[i] - (1 if i == 0 else 0) for i in range(M + 1)], M)
    ok4 &= (lhs == rhs)
    say(f"  k={k}: 항등식·비음성·O=PAIR(n<=3k-1)·3k 보정·양의 꼴 A_{{k-1}}-A_{{k-2}}=G(e^V-1) — {ok4}")
say("  (A) 성립:", ok4)

# ---------- (5) (C) 용량 곱 비 ----------
say("== (5) (C) 용량 곱 한 걸음 비 ==")
ok5 = True
for _ in range(300):
    ts = [random.randint(1, 9) for _ in range(random.randint(1, 7))]
    def P(yy):
        r = Fr(1)
        for t in ts: r *= Fr(min(t, yy), t)
        return r
    for y in range(1, 10):
        Z = sum(1 for t in ts if t > y); H = sum(1 for t in ts if t == y)
        ok5 &= (P(y + 1) / P(y) == (1 + Fr(1, y)) ** Z)
        if y >= 2: ok5 &= (P(y - 1) / P(y) == (1 - Fr(1, y)) ** (Z + H))
say("  (C) P(y+1)/P(y)=(1+1/y)^Z, P(y-1)/P(y)=(1-1/y)^{Z+H} (무작위 300 다중집합):", ok5)

# ---------- (6) Borel 산술 ----------
say("== (6) Borel 산술 ==")
from mpmath import mp, mpf, log as mlog, factorial as mfact, sqrt as msqrt, pi as mpi, exp as mexp, zeta
mp.dps = 30
def rb(m): return mlog(mfact(m)) - (m + mpf(1) / 2) * mlog(m) + m - mlog(2 * mpi) / 2
ok6a = all(rb(m) > rb(m + 1) for m in range(1, 3000)) and all(mpf(1) / (12 * m + 1) < rb(m) < mpf(1) / (12 * m) for m in range(1, 3000))
say("  rb_m 감소·Robbins 구간 (m<3000):", ok6a)
def BorR(m): return mexp(-m) * mpf(m) ** (m - 1) / mfact(m)
ok6b = True
for a0 in (3, 10, 50, 200):
    for b0 in range(a0 + 1, a0 + 60):
        r = BorR(a0) / BorR(b0); ok6b &= (1 <= r <= (mpf(b0) / a0) ** 1.5)
say("  1 <= Bor(a)/Bor(b) <= (b/a)^{3/2} (a<b):", ok6b)
def RenR(j): return mpf(j) ** j * mexp(-j) / mfact(j)
cPsi = -zeta(mpf(1) / 2) + zeta(mpf(3) / 2) / 12
ok6c = True; Psi = mpf(0)
for d in range(1, 3001):
    Psi += RenR(d)
    low86 = (2 * msqrt(d) - cPsi + 1 / (2 * msqrt(d)) - mpf(d) ** (-1.5) / 24) / msqrt(2 * mpi)
    low98 = mpf('0.7978') * msqrt(d) - mpf('0.8848')
    low943 = mpf('0.3989') * (2 * msqrt(d) - mpf('1.678'))
    up = 2 * msqrt(d) / msqrt(2 * mpi)
    ok6c &= (low98 <= low943 <= low86 <= Psi <= up)
say("  Psi: 9.8꼴 <= 9.43꼴 <= 8.6(라)꼴 <= Psi <= 2(2π)^{-1/2}√d (d<=3000):", ok6c, " c_Psi =", mp.nstr(cPsi, 8))

# ---------- (7) h-변환 항등식 ----------
say("== (7) h-변환 항등식 (자유 Borel 보행 기준, h=Bor(y+.)) ==")
def check_h(y, d):
    def K0(q, qp): return BorR(q - qp)
    def h(q): return BorR(y + q)
    def K(q, qp): return K0(q, qp) * h(qp) / h(q)
    def stop(kern, q): return 1 - sum(kern(q, qp) for qp in range(1, q))
    acc = {'s': mpf(0), 's0': mpf(0)}
    M0 = {q: mpf(0) for q in range(1, d + 1)}
    def rec(q, prob, prob0, Pi):
        M0[q] += prob0 * Pi
        acc['s'] += prob * stop(K, q) * Pi; acc['s0'] += prob0 * stop(K0, q) * Pi
        for qp in range(1, q):
            rec(qp, prob * K(q, qp), prob0 * K0(q, qp), Pi * mpf(y) / (y + qp))
    rec(d, mpf(1), mpf(1), mpf(1))
    rhs = -sum(mpf(q) / y * M0[q] * (h(q) / h(d) - 1) for q in range(1, d))
    return acc['s'] - acc['s0'], rhs
ok7 = True
for y, d in [(5, 4), (5, 7), (8, 10), (20, 8)]:
    a1, b1 = check_h(y, d); ok7 &= (abs(a1 - b1) < mpf(10) ** -20)
    say(f"  y={y}, d={d}: s-s0={mp.nstr(a1, 12)} 우변={mp.nstr(b1, 12)}")
say("  h-변환 항등식 성립:", ok7)

# ---------- (8) 상위해 원리 ----------
say("== (8) 상위해 원리: T[1] = 10.11의 s^W ==")
def PrBorGe(q): return 1 - sum(BorR(j) for j in range(1, q))
def T1(y, q): return PrBorGe(q) + sum(BorR(j) * mpf(y) / (y + q - j) for j in range(1, q))
def sW(m, y):
    q = m - y; return 1 - sum(BorR(r + 1) * mpf(q - r) / (m - r) for r in range(0, q))
ok8 = True
for y in (5, 20):
    for q in range(2, 12):
        ok8 &= (abs(T1(y, q) - sW(y + q - 1, y)) < mpf(10) ** -25)
say("  T_y[1](q) = s^W_{q-1}(y+q-1, y) (10.11; 초과 좌표 q <-> q-1):", ok8)
ok8b = all(T1(y, q) <= 1 for y in (5, 20) for q in range(2, 12))
say("  T[1] <= 1 (따라서 T[1]은 상위해):", ok8b)

# ---------- (9) nf 로그 계수 ----------
say("== (9) nf 로그 계수 상하계·합성 법칙 ==")
def lc(i, d): return Fr(1, i) * (Fr(d ** (i + 1), i + 1) + 2 * d ** i - sum(r ** i for r in range(d)))
ok9 = all(Fr(2 * d ** i, i) <= lc(i, d) <= Fr(5 * d ** i, 2 * i) for i in range(1, 8) for d in range(1, 60))
say("  2d^i/i <= lc_i(d) <= 5d^i/(2i) (i<=7, d<60):", ok9)
def nfq(n, d):  # nf(n,d)/e^d
    return Fr(factorial(n), factorial(n - d)) * Fr((n - d) ** (n - d - 2)) / Fr(n ** (n - 2))
ok9b = True
for n in range(4, 16):
    for a0 in range(0, n - 1):
        for b0 in range(0, n - a0 - 1):
            if n - a0 - b0 < 1: continue
            ok9b &= (nfq(n, a0 + b0) == nfq(n, a0) * nfq(n - a0, b0))
say("  nf(n,a+b) = nf(n,a) nf(n-a,b) (n<16):", ok9b)

# ---------- (10) 가중 수준 방문 보존의 등식 판 ----------
say("== (10) 가중 수준 방문 보존 (등식 판) ==")
def s_my(m, y):
    return A_series(y - 1, m)[m] * factorial(m) / p(m)
ok10 = True
for Y in (2, 3, 4):
    for Kk in range(Y + 1, Y + 7):
        om = {m: Fr(Y, m + 1) for m in range(Y + 1, Kk + 1)}  # 비증가 무게
        lhs = sum(om[m] * (s_my(m, Y + 1) - s_my(m, Y)) for m in range(Y + 1, Kk + 1))
        sK = s_my(Kk, Y)
        abel = om[Kk] * (1 - sK) + sum((om[m] - om[m + 1]) * (1 - s_my(m, Y)) for m in range(Y + 1, Kk))
        stay = sum(om[m] * (s_my(m, Y + 1) - s_my(m - 1, Y)) for m in range(Y + 1, Kk + 1))
        ok10 &= (lhs == abel + stay) and (stay >= 0) and (lhs >= abel)
say("  sum ω c = ω(K)(1-s_K) + sum(ω(m)-ω(m+1))(1-s_m) + sum ω ς, ς>=0 (등식):", ok10)

ALL = all([ok1, ok1c, ok1d, ok2a, ok2b, ok2c, ok3, ok3b, ok3c, ok4, ok5, ok6a, ok6b, ok6c, ok7, ok8, ok8b, ok9, ok9b, ok10])
say("== 총괄 ==", ALL)
open(__file__.replace('.py', '_out.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
