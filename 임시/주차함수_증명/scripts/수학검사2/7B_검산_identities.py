# -*- coding: utf-8 -*-
"""수학 검사 2 (7B): 7.4–7.7절의 정확 유리수 항등식·부등식을 작은 k에서 전수 대조한다.
실행: python -I scripts/수학검사2/7B_검산_identities.py
대상: (7.2)(7.3)(7.4) 모멘트 재귀와 전분산 공식, src^M_k=-k x_k, (7.11), (7.14) 한 걸음 항등식,
      명제 fold-A·fold-R, 보조정리 fold-T, 보조정리 root-symmetry, (7.23)(7.24), (7.25)(7.26),
      보조정리 hazard-floor (가)(나), 보조정리 explicit-bounds (바), 보조정리 threshold-unit-ratio의 망원 등식,
      (7.28)(7.29)(7.30), 뿌리 자리 법칙의 두 표현, 명제 old-6-15의 Abel 합.
모든 양은 Fraction. e가 끼는 곳은 e^{-m}을 공통 인자로 떼어 e 없이 비교한다(동차성 확인 포함)."""
from fractions import Fraction as Q
from math import comb, factorial
from itertools import permutations
import sys

def binom(n, k):
    return comb(n, k) if 0 <= k <= n else 0

def p(n):  # p_n = (n+1)^{n-1}
    return (n + 1) ** (n - 1) if n >= 1 else 1

# ---- A_{n,l}: 마지막 차 재귀 (정리 2.6) ----
_A = {}
def A(n, l):
    if l < 0:
        return 0
    key = (n, l)
    if key in _A:
        return _A[key]
    if n == 0:
        v = 1
    else:
        v = sum(binom(n - 1, j) * min(j + 1, l + 1) * A(j, l) * A(n - 1 - j, l) for j in range(n))
    _A[key] = v
    return v

def b(n, k):   # 최대 변위가 정확히 k인 주차함수 수
    return A(n, k) - A(n, k - 1)

def d(n, k):
    return b(n, k) - b(n, k - 1)

def s(m, y):   # s_m(y) = A_{m,y-1}/p_m
    return Q(A(m, y - 1), p(m))

def c(m, y):   # c_m(y) = b_{m,y}/p_m
    return Q(b(m, y), p(m))

def cl_plus(m, k):
    return Q(b(m, k), A(m, k - 1))

def cl_minus(m, k):
    return Q(b(m, k - 1), A(m, k - 1))

def mu(m, k):
    return cl_plus(m, k) - cl_minus(m, k)

def Pk(m, j, k):  # 뿌리 자리 법칙 P^{(k)}_m(j)
    return Q(min(j, k) * binom(m - 1, j - 1) * A(j - 1, k - 1) * A(m - j, k - 1), A(m, k - 1))

def P(m, j):      # 균등 마지막 차 자리 법칙 P_m(j)
    return Q(j * binom(m - 1, j - 1) * p(j - 1) * p(m - j), p(m))

def eg(x):        # e^{g(x)} = (1+1/x)^{x-1}, 정수 x>=1
    return (Q(x + 1, x)) ** (x - 1)

fails = 0
def check(name, ok, info=""):
    global fails
    print(("OK   " if ok else "FAIL ") + name + ("" if not info else "  " + str(info)))
    if not ok:
        fails += 1

# ---- 1. 결과 순열 전수(n<=7): A_{n,k-1}=sum prod min(h_i,k), 모멘트 재귀 (7.3), 전분산 (7.4) ----
def capacities(sig):
    n = len(sig)
    h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)  # j=-1이면 i+1 (자리 번호 i+1)
    return h

def brute_moments(n, k):
    tot = 0; zf = 0; zh = 0; zz = 0
    for sig in permutations(range(n)):
        h = capacities(sig)
        w = 1
        for hi in h:
            w *= min(hi, k)
        Z = sum(1 for hi in h if hi > k)
        H = sum(1 for hi in h if hi == k)
        tot += w; zf += w * Z; zh += w * H; zz += w * Z * (Z - 1)
    return tot, Q(zf, tot), Q(zh, tot), Q(zz, tot)

def rec_moments(N, k):
    Zf = {0: Q(0)}; ZH = {0: Q(0)}; ZZ = {0: Q(0)}
    for n in range(1, N + 1):
        Zf[n] = sum(Pk(n, q, k) * ((1 if q > k else 0) + Zf[q - 1] + Zf[n - q]) for q in range(1, n + 1))
        ZH[n] = sum(Pk(n, q, k) * ((1 if q == k else 0) + ZH[q - 1] + ZH[n - q]) for q in range(1, n + 1))
        ZZ[n] = sum(Pk(n, q, k) * (ZZ[q - 1] + ZZ[n - q] + 2 * Zf[q - 1] * Zf[n - q]
                                    + 2 * (1 if q > k else 0) * (Zf[q - 1] + Zf[n - q])) for q in range(1, n + 1))
    return Zf, ZH, ZZ

print("== 1. 전수 대조 (n<=7): 섬유 크기 합 = A_{n,k-1}, (7.3) 모멘트 재귀")
ok_all = True
for k in (2, 3, 4):
    Zf, ZH, ZZ = rec_moments(7, k)
    for n in range(1, 8):
        tot, bzf, bzh, bzz = brute_moments(n, k)
        ok_all &= (tot == A(n, k - 1)) and (bzf == Zf[n]) and (bzh == ZH[n]) and (bzz == ZZ[n])
        # 시작값 주장: j<=k에서 Z^flat=0, j<k에서 Z^H=0, j<=k+1에서 Z=0
        if n <= k: ok_all &= Zf[n] == 0
        if n < k: ok_all &= ZH[n] == 0
        if n <= k + 1: ok_all &= ZZ[n] == 0
check("A_{n,k-1}=sum_sigma prod min(h_i,k); (7.3) 세 재귀 = 전수 모멘트; 시작값 (k=2,3,4, n<=7)", ok_all)

print("== 1b. (7.2) n a_n = sum min(p,k) a_{p-1} a_{n-p}; 뿌리 자리 법칙 두 표현; (7.4) 전분산; src^M_k = -k x_k")
ok = True
for k in (2, 3, 5):
    a = {n: Q(A(n, k - 1), factorial(n)) for n in range(0, 16)}
    for n in range(1, 16):
        ok &= n * a[n] == sum(min(q, k) * a[q - 1] * a[n - q] for q in range(1, n + 1))
        for j in range(1, n + 1):
            ok &= Pk(n, j, k) == Q(min(j, k), j) * P(n, j) * s(j - 1, k) * s(n - j, k) / s(n, k)
            ok &= Pk(n, j, k) == min(j, k) * a[j - 1] * a[n - j] / (n * a[n])
    # cnt_n(m), 전분산 공식 (7.4), 원천 분해
    N = 3 * k + 2
    Zf, ZH, ZZ = rec_moments(N, k)
    cnt = {}
    for n in range(0, N + 1):
        for m in range(1, N + 1):
            if m > n: cnt[(n, m)] = Q(0)
            elif m == n: cnt[(n, m)] = Q(1)
            else: cnt[(n, m)] = sum(Pk(n, q, k) * (cnt[(q - 1, m)] + cnt[(n - q, m)]) for q in range(1, n + 1))
    def g(m, q): return (1 if q > k else 0) + Zf[q - 1] + Zf[m - q]
    yv = {m: sum(Pk(m, q, k) * g(m, q) ** 2 for q in range(1, m + 1)) - Zf[m] ** 2 for m in range(1, N + 1)}
    for n in range(1, N + 1):
        var = ZZ[n] + Zf[n] - Zf[n] ** 2
        ok &= var == sum(cnt[(n, m)] * yv[m] for m in range(1, n + 1))
        ok &= k * ZH[n] == sum(cnt[(n, m)] * k * Pk(m, k, k) for m in range(k, n + 1))
        ok &= ZZ[n] - k * ZH[n] == Zf[n] * (Zf[n] - 1) + sum(cnt[(n, m)] * (yv[m] - k * Pk(m, k, k)) for m in range(k, n + 1))
        srcM = {m: 2 * sum(Pk(m, q, k) * Zf[q - 1] * Zf[m - q] for q in range(1, m + 1))
                   + 2 * sum(Pk(m, q, k) * (Zf[q - 1] + Zf[m - q]) for q in range(k + 1, m + 1)) - k * Pk(m, k, k)
                for m in range(k, n + 1)}
        ok &= ZZ[n] - k * ZH[n] == sum(cnt[(n, m)] * srcM[m] for m in range(k, n + 1))
    xk = Q(k, k + 1) ** (k - 1)
    ok &= Pk(k, k, k) == xk == Q(k * k ** (k - 2), (k + 1) ** (k - 1))
check("(7.2), 뿌리 자리 법칙 두 표현, (7.4) 세 식, 원천 분해, P^(k)_k(k)=x_k (k=2,3,5)", ok)

# ---- 2. (7.11) 꼬리 확률의 재귀 ----
print("== 2. (7.11) 1-s_q(k) = sum_{j=k+1}^{k+q-1} pi_m(j)[(j-k)/j + (k/j)(1-s_{j-k}(k))], m=k+q-1")
ok = True
def pi_m(m, j):
    return Q(binom(m, j) * j ** (j - 1) * p(m - j), p(m))
for k in (2, 3, 4, 6):
    for q in range(2, k + 3):
        m = k + q - 1
        lhs = 1 - s(k + q - 1, k)
        rhs = sum(pi_m(m, j) * (Q(j - k, j) + Q(k, j) * (1 - s(j - 1, k))) for j in range(k + 1, m + 1))
        ok &= lhs == rhs
        # (라) 1 - s_q <= pi^sharp_q
        ok &= lhs <= Q(q * (q - 1), 2 * (k + 1))
        # heavy-block (나): ex_t = t/s_{t-1}(k) - k = q + (k+q)(1-s)/s
        t = k + q
        ex = Q(t) / s(t - 1, k) - k
        ok &= ex == q + (k + q) * (1 - s(t - 1, k)) / s(t - 1, k) and ex >= q
    ok &= s(k, k) == 1
check("(7.11) 등식, (라) 상계, heavy-block (나) (k=2,3,4,6; 2<=q<=k+2)", ok)

# ---- 3. (7.14) 한 걸음 항등식, 명제 fold-A, fold-R, 보조정리 fold-T ----
print("== 3. (7.14), fold-A, fold-R, fold-T")
def chi(m, j, k):
    cp = lambda t: cl_plus(t, k); cm = lambda t: cl_minus(t, k)
    v = Q(0)
    if j == k: v += -Q(1, k) * (1 - cm(m - k))
    if j > k: v += Q(1, k) * (cp(j - 1) + cm(j - 1) + cp(m - j) + cm(m - j))
    v += (1 + Q(1 if j > k else 0, k)) * cp(j - 1) * cp(m - j)
    v += (1 - Q(1 if j > k else 0, k)) * cm(j - 1) * cm(m - j)
    return v
def src(m, k):
    return sum(Pk(m, j, k) * chi(m, j, k) for j in range(1, m + 1))
ok = True
for k in (2, 3, 4, 5):
    for m in range(1, 3 * k + 4):
        ok &= mu(m, k) == src(m, k) + sum(Pk(m, j, k) * (mu(j - 1, k) + mu(m - j, k)) for j in range(1, m + 1))
        if m <= k - 1: ok &= mu(m, k) == 0 and src(m, k) == 0
check("(7.14) mu_m = src + sum P[mu_L+mu_R], m<=k-1에서 0 (k=2..5, m<=3k+3)", ok)

# 볼츠만 열 without e: ah^{(y)}_m := A_{m,y-1}/m! (e^{-m} 공통 인자 제거)
def ah(m, y): return Q(A(m, y - 1), factorial(m))
def borh(m):  # e*Bor(m) without e^{-(m-1)}: e^{1-m} m^{m-1}/m! -> m^{m-1}/m!  (= p_{m-1}/(m-1)! )
    return Q(m ** (m - 1), factorial(m))
ok = True
for k in (2, 3, 4, 5):
    for n in range(k, 3 * k + 3):
        # fold-A: n ah_n src = thr + heavy + quad (모두 e^{-(n-1)} 동차)
        thr = -borh(k) * ah(n - k, k - 1)
        heavy = sum(ah(n - 1 - m, k) * (ah(m, k + 1) - ah(m, k - 1)) * (1 + (1 if n - 1 - m >= k else 0)) for m in range(k, n))
        quad = sum(min(j, k + 1) * (ah(j - 1, k + 1) - ah(j - 1, k)) * (ah(n - j, k + 1) - ah(n - j, k))
                   + min(j, k - 1) * (ah(j - 1, k) - ah(j - 1, k - 1)) * (ah(n - j, k) - ah(n - j, k - 1)) for j in range(1, n + 1))
        ok &= n * ah(n, k) * src(n, k) == thr + heavy + quad
        ok &= quad >= 0 and heavy >= 0
        # ah_m = Bor(m+1)e * s_m(k): m<=k에서 자유
        if n <= k: ok &= ah(n, k) == borh(n + 1)
    # 지표 확인: ah_{k-1}(k) = e Bor(k) (e 제거꼴)
    ok &= ah(k - 1, k) == borh(k)
check("fold-A: n a_n src = thr+heavy+quad, heavy,quad>=0 (k=2..5, k<=n<=3k+2)", ok)

ok = True
for k in (3, 4, 5):
    for n in range(2 * k + 1, 3 * k + 3):
        nu = n - 2 * k
        sib = lambda q: borh(n - k - q)          # e Bor(n-k-q), 형제 크기 n-1-k-q <= k
        for l in range(0, k - 1):
            B = n - 1 - k - l
            if not (nu + 1 <= B <= n - 1 - k): continue
            lhs = sum(sib(q) * (ah(k + q, k + 1) - ah(k + q, k - 1)) for q in range(nu - 1, B + 1))
            ed1 = borh(k + 1) * ah(n - 1 - k, k + 1)
            ed2 = borh(k) * ah(n - k, k + 1)
            up = borh(l + 2) * ah(n - 2 - l, k - 1) + borh(l + 1) * ah(n - 1 - l, k - 1)
            inn = sum(sib(q + 1) * ah(k + q + 1, k + 1) - sib(q - 1) * ah(k + q - 1, k - 1) for q in range(nu, B))
            ok &= lhs == ed1 + ed2 + inn - up
            # 형제 크기 조건: sib_q 는 n-1-k-q <= k 이어야 자유
            ok &= all(n - 1 - k - q <= k for q in range(nu - 1, B + 1))
            # 내부 계수 >= 0 (fold-T 귀결)
            ok &= all(sib(q + 1) * ah(k + q + 1, k + 1) - sib(q - 1) * ah(k + q - 1, k - 1) >= 0 for q in range(nu, B))
            # (7.16)
            ok &= n * ah(n, k) * src(n, k) >= ed1 + borh(k) * (ah(n - k, k + 1) - ah(n - k, k - 1)) - up
check("fold-R (7.15) 등식, 내부 계수>=0, (7.16) (k=3,4,5; 2k+1<=n<=3k+2; 0<=l<=k-2)", ok)

ok = True
for k in (2, 3, 4, 5):
    for n in range(3, 3 * k + 4):
        for q in range(1, n - 1):
            if 2 * q >= n - 1:
                ok &= ah(n - 2 - q, k) * ah(q + 1, k + 1) >= ah(n - q, k) * ah(q - 1, k - 1)
check("fold-T: a_{n-2-q} a^+_{q+1} >= a_{n-q} a^-_{q-1} (2q>=n-1; k=2..5, n<=3k+3)", ok)

# ---- 4. root-symmetry, (7.23)(7.24) ----
print("== 4. 뿌리 법칙의 대칭, (7.23)(7.24)")
ok = True
def V(n, k, q):
    return Q(k, k + 1 + q) * P(n, k + 1 + q) / P(n, k)
for k in (2, 3, 5, 8):
    for nu in range(1, 6):
        n = 2 * k + nu
        ok &= V(n, k, nu) == 1
        for q in range(0, k + nu - 1):
            ok &= V(n, k, q + 1) / V(n, k, q) == eg(k + 1 + q) / eg(k + nu - 1 - q)
        ok &= all(V(n, k, q) >= 1 for q in range(nu, k + nu))
check("root-symmetry (가)(나), q>=nu에서 V>=1 (k=2,3,5,8; nu<=5)", ok)

ok = True
for k in (2, 3, 4, 5):
    for nu in range(1, k + 3):
        n = 2 * k + nu
        # (7.23): 이차 몫을 버린 선형 원천의 정확한 변환
        lin = sum(Pk(n, j, k) * Q(1, k) * (cl_plus(j - 1, k) + cl_minus(j - 1, k) + cl_plus(n - j, k) + cl_minus(n - j, k))
                  for j in range(k + 1, n + 1)) - Pk(n, k, k) * Q(1, k) * (1 - cl_minus(n - k, k))
        rhs = sum(Q(k, j) * P(n, j) * ((c(j - 1, k - 1) + c(j - 1, k)) * s(n - j, k) + s(j - 1, k) * (c(n - j, k - 1) + c(n - j, k)))
                  for j in range(k + 1, n + 1)) - P(n, k) * s(n - k, k - 1)
        ok &= k * s(n, k) * lin == rhs
        ok &= k * s(n, k) * src(n, k) >= rhs
        # (7.24)
        mid = P(n, k) * (sum(V(n, k, q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1))
        last = P(n, k) * (c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1))
        ok &= rhs >= mid >= last
check("(7.23) 선형 몫의 등식과 부등식, (7.24) 두 부등식 (k=2..5, 1<=nu<=k+2)", ok)

# ---- 5. (7.25)(7.26) 결합과 위험률 항등식, hazard-floor ----
print("== 5. 결합 (7.25), 위험률 항등식 (7.26), hazard-floor (가)(나), explicit-bounds (바)")
def F(m, x): return sum(P(m, j) for j in range(1, min(x, m) + 1))
def hz(N, k): return 1 - s(N + 1, k) / s(N, k)
ok = True
for k in (2, 3, 4, 6):
    for N in range(1, 3 * k + 3):
        # 결합 확률: Pr(j=j, j'=j+1) = F_N(j) - F_{N+1}(j) >= 0, 그리고 j'=j 확률 = P_N(j) - (F_N(j)-F_{N+1}(j))
        pr_move = {j: F(N, j) - F(N + 1, j) for j in range(1, N + 1)}
        ok &= all(v >= 0 for v in pr_move.values())
        ok &= all(pr_move[j] <= P(N, j) for j in range(1, N + 1))
        # (7.25) 기댓값
        def term(j, y):
            return Q(min(j, k), j) * s(j - 1, k) * s(y - j, k)
        lhs = s(N, k) - s(N + 1, k)
        rhs = sum((P(N, j) - pr_move[j]) * (term(j, N) - term(j, N + 1)) + pr_move[j] * (term(j, N) - term(j + 1, N + 1))
                  for j in range(1, N + 1))
        ok &= lhs == rhs
        # 점별 음이 아님
        ok &= all(term(j, N) - term(j, N + 1) >= 0 and term(j, N) - term(j + 1, N + 1) >= 0 for j in range(1, N + 1))
        # (7.26)
        f = {j: pr_move[j] / P(N, j) for j in range(1, N + 1)}
        def sh(j):
            return hz(j - 1, k) * Q(j, j + 1) + Q(1, j + 1) if j >= k else Q(0)
        rhs26 = sum(Pk(N, j, k) * (f[j] * sh(j) + (1 - f[j]) * hz(N - j, k)) for j in range(1, N + 1))
        ok &= hz(N, k) == rhs26
        # hazard-floor (가)
        if N >= k:
            ok &= lhs >= P(N + 1, N + 1) * k * s(N, k) / (N * (N + 1))
            ok &= P(N + 1, N + 1) == Q(N + 1, N + 2) ** N
            # (나) 첫 부등식 (U_1 범위)
            for U1 in range(0, min(k - 1, N - k) + 1):
                br = sum(P(N, N - U) for U in range(U1 + 1)) - (U1 + 1) * (Q(1, 2 * (N - U1)) + Q(4, N * N))
                ok &= lhs >= k * s(N, k) / (N * (N + 1)) * br
check("(7.25) 등식·점별 비음, (7.26) 등식, hazard-floor (가)(나) 첫 부등식 (k=2,3,4,6; N<=3k+2)", ok)

# (바)는 Bor 질량(e 포함)이라 아래 numeric 스크립트에서 다룬다.

# ---- 6. 7.7절: 분할 무게, (7.28)(7.29)(7.30), 문턱 단위 비의 망원 등식 ----
print("== 6. 7.7절")
ok = True
for k in (3, 4, 5, 6):
    for n in range(2 * k + 1, 3 * k + 4):
        w = {m: Q(binom(n - 1, m) * p(m) * A(n - 1 - m, k - 1), A(n, k - 1)) for m in range(k, 2 * k + 1)}
        w[k - 1] = Q(0)
        # w_m = w_n(m+1)/(n A_{n,k-1}), w_n(t)=C(n,t) t^{t-1} A_{n-t,k-1}
        ok &= all(w[m] == Q(binom(n, m + 1) * (m + 1) ** m * A(n - 1 - m, k - 1), n * A(n, k - 1)) for m in range(k, 2 * k + 1))
        # 비감소 (정리 6.old-7-21, k>=43 가정이라 여기서는 확인만 출력)
        pm = {m: Q((k + 1) * b(m, k) - (k - 1) * b(m, k - 1), p(m)) for m in range(k, 2 * k + 1)}
        Left = sum(w[m] * pm[m] for m in range(k, 2 * k + 1))
        inh = sum(Pk(n, j, k) * (mu(j - 1, k) * (1 if k <= j - 1 <= 2 * k else 0) + mu(n - j, k) * (1 if k <= n - j <= 2 * k else 0))
                  for j in range(1, n + 1))
        inhlin = Q(1, k) * sum(Pk(n, j, k) * ((cl_plus(j - 1, k) + cl_minus(j - 1, k)) * (1 if k <= j - 1 <= 2 * k else 0)
                                              + (cl_plus(n - j, k) + cl_minus(n - j, k)) * (1 if k <= n - j <= 2 * k else 0))
                               for j in range(1, n + 1))
        if n >= 3 * k + 1:
            ok &= inhlin + inh == 2 * Left                                  # (7.28)
        if n <= 3 * k:
            KD = sum((k + n - m) * binom(n - 1, m) * p(n - 1 - m) * d(m, k) for m in range(2 * k + 1, n))
            ok &= A(n, k - 1) * (src(n, k) + inh) == d(n, k) - KD           # (7.29)
        if n == 3 * k:
            u = w[2 * k] * s(2 * k, k + 1)
            Quad = sum(Pk(n, j, k) * ((1 + Q(1, k)) * cl_plus(j - 1, k) * cl_plus(n - j, k) + (1 - Q(1, k)) * cl_minus(j - 1, k) * cl_minus(n - j, k))
                       for j in range(k + 1, n + 1))
            Stem = Q(1, k) * sum(Pk(n, j, k) * ((cl_plus(j - 1, k) + cl_minus(j - 1, k)) * (1 if j - 1 > 2 * k else 0)
                                               + (cl_plus(n - j, k) + cl_minus(n - j, k)) * (1 if n - j > 2 * k else 0))
                                 for j in range(k + 1, n + 1))
            ok &= src(n, k) + inh == 2 * Left - u + Quad + Stem               # (7.30)
            # 문턱 뿌리 항 (833행)
            ok &= Pk(n, k, k) == k * w[2 * k] * A(2 * k, k - 1) / p(2 * k)
            ok &= Pk(n, k, k) * (mu(2 * k, k) - Q(1, k) * (1 - cl_minus(2 * k, k))) == w[2 * k] * pm[2 * k] - u
            # 망원 등식: u_{3k}/w_k = e^{g(2k)-g(k)} s_{2k}(k+1)/s_{2k-1}(k)
            ok &= u / w[k] == eg(2 * k) / eg(k) * s(2 * k, k + 1) / s(2 * k - 1, k)
            # w_{m+1}/w_m 식 (808행)
            for m in range(k, 2 * k):
                N = n - 2 - m
                ok &= w[m + 1] / w[m] == eg(m + 1) * s(N, k) / (eg(N + 1) * s(N + 1, k))
        # Abel 합 (명제 old-6-20 증명)
        Vk = {m: sum(pm[mm] for mm in range(m, 2 * k + 1)) for m in range(k, 2 * k + 2)}
        ok &= Left == w[k] * Vk[k] + sum((w[m] - w[m - 1]) * Vk[m] for m in range(k + 1, 2 * k + 1))
check("w_m 표현, (7.28), (7.29), (7.30), 문턱 뿌리 항, 망원 등식, w 비 식, Abel 합 (k=3..6)", ok)

# ---- 7. 보조정리 error-induction (가): e^(1) 볼록 => 열가법 ----
print("== 7. error-induction (가)")
ok = True
from math import ceil
u = Q(1, 2 ** 53)
e0 = lambda n: (256 + ceil(n / 256)) * u
e1 = {0: Q(0)}
for n in range(1, 1200):
    e1[n] = e1[n - 1] + e0(n) + 5 * u
for n in range(1, 1200, 37):
    ok &= all(e1[p - 1] + e1[n - p] <= e1[n - 1] for p in range(1, n + 1))
check("e^(1)_{p-1}+e^(1)_{n-p} <= e^(1)_{n-1} (n<1200 표본)", ok)

print("\n실패 수:", fails)
sys.exit(1 if fails else 0)
