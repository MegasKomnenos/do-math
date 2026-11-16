# -*- coding: utf-8 -*-
"""심사 A7 — 항등식·소규모 정확 검산 묶음.
 1. (추가 발견) 가장 큰 나무 핵의 정확한 Borel 꼴: pi_m(j) = Bor(j) Bor(m+1-j) / Bor(m+1),
    마지막 차 자리 법칙 P_m(j) = (j/m) pi_m(j).  -> 7:kernel-bound·7:explicit-bounds(나)·2:old-2-32(ㄱ)·7:root-symmetry(나)가 한 항등식의 귀결.
    정확 유리수로 m<=40 전수.
 2. (G4) X = B(z∫X + e^δ - 1 - δ) 를 k=2,3 에서 x^{3k+2}차까지 정확 유리수(z 기호)로 확인하고 (7.7)과 대조.
 3. (P8) Q_k(2k+1) < 0, 볼록 => Q'(n_M) > 0 자동.  nM.json 과 저장 인증값으로 1160열 확인(정확 유리수).
 4. (S12 보조) 작은 k에서 V_k(k) >= ((k-1)/(R+1))[1-s_R(k-1)] - (k-1)c_{2k}(k-1), R=floor(3(k-1)/2) 를 정확 유리수로 검사(k<=40).
 5. (S12/S13 참고) k=2001, 3130, 3131 에서 V_k(k)의 참값과 F3 하계식의 값(배정밀도, 양수항 재귀).
"""
import os, json
from fractions import Fraction as Fr
from math import comb

ROOT = r"C:\math\임시\주차함수_증명"
out = []

# ---------- 1. Borel identity ----------
def Bor_frac_pair(w):
    # Bor(w) = e^{-w} w^{w-1}/w!  -> store as (rational part, power of e) : (w^{w-1}/w!, -w)
    return Fr(w ** (w - 1), __import__('math').factorial(w)), -w
def p(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1
ok1 = True; ok2 = True
for m in range(1, 41):
    for j in range(1, m + 1):
        pi = Fr(comb(m, j) * j ** (j - 1) * p(m - j), p(m))
        a, ea = Bor_frac_pair(j); b, eb = Bor_frac_pair(m + 1 - j); c, ec = Bor_frac_pair(m + 1)
        assert ea + eb - ec == 0  # e-powers cancel
        rhs = a * b / c
        if pi != rhs:
            ok1 = False
        Pm = Fr(j * comb(m - 1, j - 1) * p(j - 1) * p(m - j), p(m))
        if Pm != Fr(j, m) * pi:
            ok2 = False
out.append(f"1. pi_m(j) = Bor(j)Bor(m+1-j)/Bor(m+1) for all 1<=j<=m<=40 (exact): {ok1};  P_m(j) = (j/m) pi_m(j): {ok2}")
out.append("   따라서 pi_m(m-s) = Bor(s+1) * Bor(m-s)/Bor(m+1) = Bor(s+1) * exp(sum_{i=m-s}^{m} (1-g(i)))  (2:old-2-26(나)); kernel-bound·explicit-bounds(나)는 g의 상계 한 줄.")
# compare ke(s,m) with exact log ratio for a few (s,m)
from mpmath import mp, mpf, log, exp
mp.dps = 30
def g(x):
    x = mpf(x); return (x - 1) * log(1 + 1 / x)
def ke(s, m):
    s = mpf(s); m = mpf(m)
    return 3 * (s + 1) / (2 * (m + 1)) + (s + 1) * (3 * s + 2) / (12 * (m + 1) ** 2) + (s + 1) ** 2 / (2 * (m + 1) * (m - s)) + (s + 1) ** 4 / (12 * (m + 1) ** 2 * (m - s))
for (s, m) in [(118, 10119), (10, 10010), (699, 10**6 + 699), (50, 2050)]:
    exact = sum(1 - g(i) for i in range(m - s, m + 1))
    gb = sum(mpf(3) / (2 * i) - mpf(1) / (2 * i * i) for i in range(m - s, m + 1))  # from g(i) >= 1-3/(2i)+1/(2i^2)
    out.append(f"   (s,m)=({s},{m}): exact log[pi/Bor(s+1)] = {mp.nstr(exact,8)};  g-bound sum(3/(2i)-1/(2i^2)) = {mp.nstr(gb,8)};  manuscript ke(s,m) = {mp.nstr(ke(s,m),8)}")

# ---------- 2. G4 identity (exact rational truncated power series, z fixed rational) ----------
from math import factorial
def ser_mul(a, b, N):
    c = [Fr(0)] * (N + 1)
    for i, ai in enumerate(a):
        if ai == 0: continue
        for j in range(0, N + 1 - i):
            c[i + j] += ai * b[j]
    return c
def ser_exp(g, N):  # g[0]=0
    f = [Fr(0)] * (N + 1); f[0] = Fr(1)
    for n in range(1, N + 1):
        f[n] = sum(Fr(i) * g[i] * f[n - i] for i in range(1, n + 1)) / n
    return f
def ser_int(a, N):
    c = [Fr(0)] * (N + 1)
    for i in range(0, N):
        c[i + 1] = a[i] / (i + 1)
    return c
def ser_add(a, b, N, cb=1):
    return [a[i] + cb * b[i] for i in range(N + 1)]
def series_check(k, zval):
    N = 3 * k + 2
    T = [Fr(0)] + [Fr(t ** (t - 1), factorial(t)) for t in range(1, N + 1)]
    Tle = [Fr(0)] + [Fr(t ** (t - 1), factorial(t)) if t <= k else Fr(0) for t in range(1, N + 1)]
    Tgt = ser_add(T, Tle, N, -1)
    E = [Fr(p(m), factorial(m)) if m < k else Fr(0) for m in range(0, N + 1)]
    B = ser_exp(T, N)
    D = [Fr(1)] + [Fr(0)] * N
    for it in range(N + 2):
        D = ser_exp(ser_add(Tle, [zval * c for c in ser_int(ser_add(D, E, N, -1), N)], N), N)
    G = [Fr(1)] + [Fr(0)] * N
    for it in range(N + 2):
        inner = ser_add(ser_add([Fr(1)] + [Fr(0)] * N, Tgt, N, -1), [zval * c for c in ser_int(ser_add(G, E, N, -1), N)], N)
        G = ser_mul(B, inner, N)
    delta = ser_add([zval * c for c in ser_int(ser_add(D, E, N, -1), N)], Tgt, N, -1)
    X = ser_add(D, G, N, -1)
    ed = ser_exp(delta, N)
    rhs = ser_mul(B, ser_add(ser_add([zval * c for c in ser_int(X, N)], ed, N), ser_add([Fr(1)] + [Fr(0)] * N, delta, N), N, -1), N)
    eTle = ser_exp(Tle, N)
    rhs77 = ser_mul(eTle, ser_add([zval * c for c in ser_int(X, N)], [c / 2 for c in ser_mul(delta, delta, N)], N), N)
    lowest = min([d for d in range(N + 1) if X[d] != 0] or [None])
    return all(X[i] == rhs[i] for i in range(N + 1)), all(X[i] == rhs77[i] for i in range(N + 1)), lowest, (X[2*k+2] == ser_mul(eTle, [c/2 for c in ser_mul(delta,delta,N)], N)[2*k+2])
for k in [2, 3, 4, 5]:
    for zval in [Fr(k), Fr(2*k+1, 2)]:
        a, b, lo, c = series_check(k, zval)
        out.append(f"2. k={k}, z={zval}: exact identity X=B(z∫X+e^δ-1-δ) mod x^{3*k+3}: {a}; (7.7) mod x^{3*k+3}: {b}; lowest degree of X = {lo} (=2k+2: {lo==2*k+2}); X_{{2k+2}} = e^{{T_le}}δ²/2 coefficient: {c}")

# ---------- 3. P8 ----------
MC = os.path.join(ROOT, "원고_자료", "세션_재계산", "moment_cert_iv")
nM = {int(k): v for k, v in json.load(open(os.path.join(MC, "nM.json"), encoding="utf-8")).items()}
CC = os.path.join(ROOT, "원고_자료", "세션_재계산", "column_cert_iv")
rows = {}
for fn in ["res_p0.jsonl", "res_p1.jsonl"]:
    for line in open(os.path.join(CC, fn), encoding="utf-8"):
        if line.strip():
            r = json.loads(line); rows[r["k"]] = r
bad = []
for k in range(841, 2001):
    r = rows[k]
    V = Fr(r["rec_Gamma"]) * Fr(str(r["rec_PU"])) * (1 + Fr(2, 10 ** 5)) if "rec_PU" in r else None
    if V is None:
        # fall back: use V_hi (upper end) as the certified value
        V = Fr(repr(r["V_hi"]))
    n = nM[k]
    def Qk(nn):
        mu = Fr(nn - k, k + 1); return mu * (mu - 1) - nn * V
    c1 = Qk(2 * k + 1) < 0
    c2 = Qk(n) > 0
    # Q'(n) = d/dn [ ((n-k)/(k+1))^2 - (n-k)/(k+1) - nV ] = 2(n-k)/(k+1)^2 - 1/(k+1) - V
    Qp = Fr(2 * (n - k), (k + 1) ** 2) - Fr(1, k + 1) - V
    c3 = Qp > 0
    c4 = Qp >= (Qk(n) - Qk(2 * k + 1)) / (n - 2 * k - 1)  # convexity slope bound
    if not (c1 and c2 and c3 and c4):
        bad.append(k)
out.append(f"3. P8: Q_k(2k+1)<0, Q_k(n_M)>0, Q_k'(n_M)>0 and Q' >= secant slope, 841..2000: violations {bad} (count {len(bad)})  [note: keys used: {'rec_PU' if 'rec_PU' in rows[841] else 'V_hi'}]")

# ---------- 4. S12 small-k exact ----------
def A_col(ell, M):
    # A_{m,ell}, m=0..M via last-car recursion: A_m = sum_j C(m-1,j-1) min(j,ell+1) A_{j-1} A_{m-j}
    A = [1]
    for m in range(1, M + 1):
        A.append(sum(comb(m - 1, j - 1) * min(j, ell + 1) * A[j - 1] * A[m - j] for j in range(1, m + 1)))
    return A
res4 = []
for k in range(3, 41):
    M = 2 * k
    Am2 = A_col(k - 2, M); Am1 = A_col(k - 1, M); A0 = A_col(k, M)
    def s(m, y):  # s_m(y) = A_{m,y-1}/p_m
        col = {k - 1: Am2, k: Am1, k + 1: A0}[y]
        return Fr(col[m], p(m))
    V = sum((k + 1) * (s(m, k + 1) - s(m, k)) - (k - 1) * (s(m, k) - s(m, k - 1)) for m in range(k, 2 * k + 1))
    R = (3 * (k - 1)) // 2
    rhs = Fr(k - 1, R + 1) * (1 - s(R, k - 1)) - (k - 1) * (s(2 * k, k) - s(2 * k, k - 1))
    res4.append((k, V >= rhs, float(V), float(rhs)))
viol4 = [r for r in res4 if not r[1]]
out.append(f"4. S12 inequality V_k(k) >= ((k-1)/(R+1))[1-s_R(k-1)] - (k-1)c_2k(k-1), exact, k=3..40: violations {len(viol4)} {[(r[0], r[2], r[3]) for r in viol4][:5]}")
out.append("   samples (k, V, rhs): " + ", ".join(f"({r[0]},{r[2]:.4f},{r[3]:.4f})" for r in res4 if r[0] in (3, 5, 10, 20, 30, 40)))

# ---------- 5. V_k(k) true value at k=2001, 3130, 3131 (double, scaled positive recursion) ----------
import numpy as np
def scaled_col(ell, M, beta):
    a = np.zeros(M + 1); a[0] = 1.0
    w = np.minimum(np.arange(1, M + 2), ell + 1).astype(float)  # min(j, ell+1), j=1..M+1
    for m in range(1, M + 1):
        j = np.arange(1, m + 1)
        a[m] = beta * np.dot(w[:m], a[j - 1] * a[m - j]) / m
    return a
for k in [2001, 3130, 3131]:
    M = 2 * k
    beta = 1 / np.e
    cols = {y: scaled_col(y - 1, M, beta) for y in (k - 1, k, k + 1)}
    # s_m(y) = A_{m,y-1}/p_m = a_m m! / (beta^m p_m);  log p_m = (m-1) log(m+1)
    from math import lgamma
    def s(m, y):
        return cols[y][m] * np.exp(lgamma(m + 1) - m * np.log(beta) - (m - 1) * np.log(m + 1))
    V = sum((k + 1) * (s(m, k + 1) - s(m, k)) - (k - 1) * (s(m, k) - s(m, k - 1)) for m in range(k, 2 * k + 1))
    R = (3 * (k - 1)) // 2
    rhs = (k - 1) / (R + 1) * (1 - s(R, k - 1)) - (k - 1) * (s(2 * k, k) - s(2 * k, k - 1))
    out.append(f"5. k={k}: V_k(k) (double) = {V:.5f};  F3 lower-bound expression = {rhs:.5f};  s_R(k-1)={s(R,k-1):.5f} (R={R}), (k-1)c_2k(k-1)={(k-1)*(s(2*k,k)-s(2*k,k-1)):.5f}")

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "scripts", "구조압축", "심사_A7_identities_out.txt"), "w", encoding="utf-8") as f:
    f.write(txt + "\n")
