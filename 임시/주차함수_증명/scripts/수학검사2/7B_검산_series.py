# -*- coding: utf-8 -*-
"""수학 검사 2 (7B): 명제 block-exponential (7.7)(7.8), 보조정리 green-atom, 보조정리 pair-terms (7.10)의
형식적 멱급수 항등식을 k=2 (차수 x^{3k+2}=x^8까지, 결과 순열 전수 n<=8)와 k=3 (n<=8, (7.7)만)에서 대조한다.
실행: python -I scripts/수학검사2/7B_검산_series.py
방법: 얼린 용량 다항식 K_{n,k}(z)와 경계 다항식 J_n(z)를 정의대로 전수 계산해 급수 D(z;x), J-급수를 만들고,
      T(x), Gr(x), Q_k, S^G, G_*, X, bd, Neu 전개를 sympy로 만들어 계수를 비교한다."""
import sys
from itertools import permutations
from math import factorial, comb
import sympy as sp

x, z = sp.symbols('x z')

def capacities(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)
    return h

def K_and_J(n, k):
    """K_{n,k}(z) = sum prod_{h<=k} h * z^{Z}, J_n(z) = sum H k^{H-1} z^Z prod_{h<k} h"""
    K = sp.Integer(0); J = sp.Integer(0)
    for sig in permutations(range(n)):
        h = capacities(sig)
        w = 1; w2 = 1; Z = 0; H = 0
        for hi in h:
            if hi <= k: w *= hi
            if hi < k: w2 *= hi
            if hi > k: Z += 1
            if hi == k: H += 1
        K += w * z ** Z
        if H >= 1:
            J += H * k ** (H - 1) * z ** Z * w2
    return sp.expand(K), sp.expand(J)

def trunc(expr, N):
    """x^N 미만 차수만 남긴다 (x, z 다항식)."""
    e = sp.expand(expr)
    return sum(e.coeff(x, i) * x ** i for i in range(N))

def series_T(N):
    # T(x) = sum t^{t-1} x^t/t!
    return sum(sp.Rational(t ** (t - 1), factorial(t)) * x ** t for t in range(1, N))

def series_exp(f, N):
    """exp(f) with f(0)=0, 차수 N 미만"""
    out = sp.Integer(1); term = sp.Integer(1)
    for j in range(1, N):
        term = trunc(term * f / j, N)
        out = out + term
    return trunc(out, N)

def integ(f, N):
    e = sp.expand(f)
    return sum(e.coeff(x, i) * x ** (i + 1) / (i + 1) for i in range(N - 1))

fails = 0
def check(name, ok, info=""):
    global fails
    print(("OK   " if ok else "FAIL ") + name + ("" if info == "" else "  " + str(info)))
    if not ok: fails += 1

def run(k, NMAX, full):
    N = NMAX + 1                       # x^NMAX까지
    KJ = {n: K_and_J(n, k) for n in range(0, NMAX + 1)}
    Kpoly = {n: KJ[n][0] for n in KJ}; Jpoly = {n: KJ[n][1] for n in KJ}
    Kpoly[0] = sp.Integer(1)
    D = sum(Kpoly[n] * x ** n / factorial(n) for n in range(0, N))
    Dlt = sum(sp.Integer((m + 1) ** (m - 1) if m >= 1 else 1) * x ** m / factorial(m) for m in range(0, k))
    Dge = trunc(D - Dlt, N)
    Tle = sum(sp.Rational(t ** (t - 1), factorial(t)) * x ** t for t in range(1, k + 1))
    T = series_T(N)
    Tgt = trunc(T - Tle, N)
    # (7.7)
    rhs = series_exp(Tle + z * integ(Dge, N), N)
    check(f"(7.7) D = exp(T<=k + z int D>=k)  (k={k}, x^{NMAX})", sp.expand(trunc(D, N) - rhs) == 0)
    # m<k에서 K_{m,k}(z)=p_m
    check(f"m<k: K_m(z)=p_m (k={k})", all(sp.expand(Kpoly[m] - (m + 1) ** (m - 1)) == 0 for m in range(1, k)))
    if not full:
        return
    eT = series_exp(T, N)
    # Q_k, S^G (ODE 풀이: 계수별), G_*
    Qk = trunc((1 - T) * (eT - Dlt), N)
    # S' = Qk + z e^T S, S(0)=0: 차수별로 푼다
    S = sp.Integer(0)
    for deg in range(1, N):
        # x^{deg} 계수: deg*S_deg = [x^{deg-1}](Qk + z e^T S)
        rhs_c = sp.expand(Qk + z * trunc(eT * S, N)).coeff(x, deg - 1)
        S = S + rhs_c / deg * x ** deg
    S = sp.expand(S)
    Gs = trunc(Dlt + Qk + z * eT * S, N)
    # 연쇄 해 방정식 G_* = e^T (1 - T>k + z int (G_* - Dlt))
    check(f"G_* = e^T(1 - T>k + z int(G_*-D<k)) (k={k})", sp.expand(Gs - trunc(eT * (1 - Tgt + z * integ(trunc(Gs - Dlt, N), N)), N)) == 0)
    # 적분 표현의 동치: D<k + Q_k = e^T(1-T>k)
    check(f"D<k + Q_k = e^T(1 - T>k) (k={k})", sp.expand(trunc(Dlt + Qk - eT * (1 - Tgt), N)) == 0)
    # X = D - G_*: 최저 차수 2k+2, (7.8) mod x^{3k+3}
    X = sp.expand(trunc(D - Gs, N))
    lowdeg = min([i for i in range(N) if X.coeff(x, i) != 0] or [N])
    check(f"X의 최저 차수 = 2k+2 (k={k})", lowdeg == 2 * k + 2, lowdeg)
    bd = trunc(z * integ(Dge, N) - Tgt, N)
    # bd_t(z) = z K_{t-1}(z) - t^{t-1}
    bd_coef_ok = all(sp.expand(bd.coeff(x, t) * factorial(t) - (z * Kpoly[t - 1] - t ** (t - 1))) == 0 for t in range(k + 1, N))
    check(f"bd_t(z) = z K_{{t-1,k}}(z) - t^(t-1) (k={k})", bd_coef_ok)
    eTle = series_exp(Tle, N)
    M = 3 * k + 3
    rhs78 = trunc(eTle * (z * integ(X, N) + bd ** 2 / 2), N)
    check(f"(7.8) X = e^{{T<=k}}[z int X + bd^2/2] mod x^{{3k+3}} (k={k}, 비교 차수 < {min(M, N)})",
          sp.expand(trunc(X - rhs78, min(M, N))) == 0)
    # K''_{n,k}(k) = POS^G_n + X''_n(k), POS^G_n := n![x^n] d_z^2 G_*|_{z=k}
    ok = True
    for n in range(1, N):
        Kpp = sp.diff(Kpoly[n], z, 2).subs(z, k)
        POS = factorial(n) * sp.diff(Gs.coeff(x, n), z, 2).subs(z, k)
        Xpp = factorial(n) * sp.diff(X.coeff(x, n), z, 2).subs(z, k)
        ok &= sp.simplify(Kpp - POS - Xpp) == 0
        if n <= 2 * k + 1: ok &= sp.simplify(Kpp - POS) == 0
    check(f"K''_n(k) = POS^G_n + X''_n(k), n<=2k+1에서 X''=0 (k={k})", ok)
    # pair-terms: X = sum_j z^j Neu^j [e^{T<=k} bd^2/2] mod x^{3k+3}
    Neu = lambda f: trunc(eTle * integ(f, N), N)
    Y = trunc(eTle * bd ** 2 / 2, N); acc = sp.Integer(0); cur = Y
    for j in range(0, N):
        acc += z ** j * cur
        cur = Neu(cur)
        if sp.expand(cur) == 0: break
    check(f"Neumann 전개 X = sum z^j Neu^j[e^{{T<=k}} bd^2/2] mod x^{{3k+3}} (k={k})", sp.expand(trunc(X - acc, min(M, N))) == 0)
    # X''(k) = sum_j k^j Neu^j[e^{T<=k} Q_j], Q_j = j(j-1)/(2k^2) bd^2 + (2j/k) bd bd' + bd'^2 + bd bd''  (z=k)
    bdk = sp.expand(bd.subs(z, k)); bd1 = sp.expand(sp.diff(bd, z).subs(z, k)); bd2 = sp.expand(sp.diff(bd, z, 2).subs(z, k))
    acc2 = sp.Integer(0)
    for j in range(0, N):
        Qj = sp.Rational(j * (j - 1), 2 * k * k) * bdk ** 2 + sp.Rational(2 * j, k) * bdk * bd1 + bd1 ** 2 + bdk * bd2
        f = trunc(eTle * Qj, N)
        for _ in range(j): f = Neu(f)
        acc2 += k ** j * f
    Xpp_series = sp.diff(X, z, 2).subs(z, k)
    check(f"X''(k) = sum k^j Neu^j[e^{{T<=k}} Q_j] mod x^{{3k+3}} (k={k})", sp.expand(trunc(Xpp_series - acc2, min(M, N))) == 0)
    # (7.10) 값: bd_t(k) = -A ex_t, bd'_t(k) = A(1+Zf), bd''_t(k) = (A/k)(2Zf+Z)
    ok = True
    for t in range(k + 1, N):
        Akk = Kpoly[t - 1].subs(z, k)            # A_{t-1,k-1}
        Zf = sp.diff(Kpoly[t - 1], z).subs(z, k) * k / Akk
        ZZ = sp.diff(Kpoly[t - 1], z, 2).subs(z, k) * k * k / Akk
        ex = sp.Rational(t * (t) ** (t - 2), 1) / Akk - k   # t p_{t-1}/A - k
        ok &= sp.simplify(bdk.coeff(x, t) * factorial(t) + Akk * ex) == 0
        ok &= sp.simplify(bd1.coeff(x, t) * factorial(t) - Akk * (1 + Zf)) == 0
        ok &= sp.simplify(bd2.coeff(x, t) * factorial(t) - Akk / k * (2 * Zf + ZZ)) == 0
        # (7.10) q_j(t,t') 공식 vs 직접 곱 전개의 계수
        for tp in range(k + 1, N):
            if t + tp >= N: continue
            for j in range(0, 3):
                exp_ = sp.Rational(t + tp, 1)
                Akp = Kpoly[tp - 1].subs(z, k)
                Zfp = sp.diff(Kpoly[tp - 1], z).subs(z, k) * k / Akp
                ZZp = sp.diff(Kpoly[tp - 1], z, 2).subs(z, k) * k * k / Akp
                exp2 = sp.Rational(tp * tp ** (tp - 2), 1) / Akp - k
                q_direct = (sp.Rational(j * (j - 1), 2 * k * k) * (-Akk * ex) * (-Akp * exp2)
                            + sp.Rational(j, k) * ((-Akk * ex) * Akp * (1 + Zfp) + Akk * (1 + Zf) * (-Akp * exp2))
                            + Akk * (1 + Zf) * Akp * (1 + Zfp)
                            + sp.Rational(1, 2) * ((-Akk * ex) * Akp / k * (2 * Zfp + ZZp) + Akk / k * (2 * Zf + ZZ) * (-Akp * exp2)))
                q_formula = Akk * Akp * ((1 + Zf) * (1 + Zfp) + sp.Rational(j * (j - 1), 2 * k * k) * ex * exp2
                                         - sp.Rational(j, k) * (ex * (1 + Zfp) + exp2 * (1 + Zf))
                                         - sp.Rational(1, 2 * k) * (ex * (2 * Zfp + ZZp) + exp2 * (2 * Zf + ZZ)))
                ok &= sp.simplify(q_direct - q_formula) == 0
    check(f"bd_t(k), bd'_t(k), bd''_t(k)의 값과 (7.10) (k={k})", ok)
    # Q_j의 x^m/m! 계수 = sum_{t+t'=m} C(m,t) q_j(t,t')  (대칭화 포함)
    ok = True
    for j in range(0, 3):
        Qj = sp.Rational(j * (j - 1), 2 * k * k) * bdk ** 2 + sp.Rational(2 * j, k) * bdk * bd1 + bd1 ** 2 + bdk * bd2
        Qj = sp.expand(Qj)
        for m in range(2 * k + 2, N):
            lhs = Qj.coeff(x, m) * factorial(m)
            rhs = 0
            for t in range(k + 1, m - k):
                tp = m - t
                bt = bdk.coeff(x, t) * factorial(t); btp = bdk.coeff(x, tp) * factorial(tp)
                b1t = bd1.coeff(x, t) * factorial(t); b1tp = bd1.coeff(x, tp) * factorial(tp)
                b2t = bd2.coeff(x, t) * factorial(t); b2tp = bd2.coeff(x, tp) * factorial(tp)
                qj = (sp.Rational(j * (j - 1), 2 * k * k) * bt * btp + sp.Rational(j, k) * (bt * b1tp + b1t * btp)
                      + b1t * b1tp + sp.Rational(1, 2) * (bt * b2tp + b2t * btp))
                rhs += comb(m, t) * qj
            ok &= sp.simplify(lhs - rhs) == 0
    check(f"Q_j의 x^m/m! 계수 = sum C(m,t) q_j(t,t') (k={k})", ok)
    # Green 원자: J^G_n(z) = n![x^n] e^T ghat, ghat' = a°_{k-1} x^{k-1} + z e^T ghat;  J_n(z) <= J^G_n(z) (0<=z<=k+1), n<=2k 등호
    a0 = sp.Rational((k) ** (k - 2) if k >= 2 else 1, factorial(k - 1))   # p_{k-1}/(k-1)!
    gh = sp.Integer(0)
    for deg in range(1, N):
        rhs_c = sp.expand(a0 * x ** (k - 1) + z * trunc(eT * gh, N)).coeff(x, deg - 1)
        gh = gh + rhs_c / deg * x ** deg
    JG = trunc(eT * gh, N)
    ok = True; ok_eq = True
    for n in range(0, N):
        JGn = sp.expand(JG.coeff(x, n) * factorial(n))
        diff = sp.Poly(sp.expand(JGn - Jpoly[n]), z)
        if n <= 2 * k:
            ok_eq &= sp.expand(JGn - Jpoly[n]) == 0
        else:
            for zz in [sp.Rational(i, 4) for i in range(0, 4 * (k + 1) + 1)]:
                ok &= diff.eval(zz) >= 0
    check(f"Green 원자: n<=2k 등호 (k={k})", ok_eq)
    check(f"Green 원자: J_n(z) <= J^G_n(z), 0<=z<=k+1 표본, 2k<n<={NMAX} (k={k})", ok)
    # 두 꼴의 일치: e^T ghat = p_{k-1} e^T e^{z Gr} int e^{-z Gr} s^{k-1}/(k-1)!
    Gr = trunc(T - T ** 2 / 2, N)
    inner = integ(trunc(series_exp(-z * Gr, N) * x ** (k - 1) / factorial(k - 1), N), N)
    alt = trunc(k ** (k - 2) * eT * series_exp(z * Gr, N) * inner, N) if k >= 2 else None
    check(f"Green 원자 두 꼴 일치 (k={k})", sp.expand(trunc(JG - alt, N)) == 0)
    # (Gr)' = e^T
    check(f"(Gr)' = e^T (k={k})", sp.expand(trunc(sp.diff(Gr, x) - eT, N - 1)) == 0)

run(2, 8, True)
run(3, 8, False)
print("\n실패 수:", fails)
sys.exit(1 if fails else 0)
