# -*- coding: utf-8 -*-
"""심사 X4 — C6(전달행렬), C7(5.28(다) 반례), C9(8.24(가) 범위)의 검산.

C6: nf(n,a+b)=nf(n,a)nf(n-a,b) (정확), K_{j,γ}(ε)의 0·1·2차 계수가 b_j, a_j, c_j (5.17·5.28의 계수)와 같은지,
    lc_i(d)의 하계 2d^i/i 확인(정수 d 표본), M_{j,sr}>=0 (표본).
C7: 𝒴_1[C+a]-𝒴_1[C] = -(5a/2) z ; 또 marked-recursion의 ((j+3/2)zC'-C) 연산자가 상수항 있는 급수에서 단조성을 잃는 것.
C9: A_{N,r-1}/A_{N,s-1} >= Π_{i<=N} min(i,r)/min(i,s) 를 2:old-2-6 재귀로 N<=60 전수(1<=r<=s<=N+1), 특히 N>2k-1.
"""
import sympy as sp
from fractions import Fraction as Fr
from math import comb, factorial

out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

# ---------- C6 ----------
P("== C6")
n, a_, b_ = sp.symbols('n a b', positive=True)
def nf(n, d):
    return sp.exp(d) * sp.gamma(n + 1) / sp.gamma(n - d + 1) * (n - d)**(n - d - 2) / n**(n - 2)
# 정수 표본에서 정확 비교
okc = True
for (nn, aa, bb) in [(20, 3, 5), (50, 7, 11), (31, 1, 1), (100, 40, 20)]:
    lhs = Fr(factorial(nn), factorial(nn - aa - bb)) * Fr((nn - aa - bb)**(nn - aa - bb - 2), nn**(nn - 2))
    rhs = Fr(factorial(nn), factorial(nn - aa)) * Fr((nn - aa)**(nn - aa - 2), nn**(nn - 2)) * Fr(factorial(nn - aa), factorial(nn - aa - bb)) * Fr((nn - aa - bb)**(nn - aa - bb - 2), (nn - aa)**(nn - aa - 2))
    okc = okc and (lhs == rhs)   # e^{a+b} = e^a e^b 는 자명
P("합성 항등식 nf(n,a+b)=nf(n,a)nf(n-a,b) 정수 표본 정확 일치:", okc)

eps, g, j = sp.symbols('epsilon gamma j')
d = g
lc1 = sp.Rational(5, 2) * d
lc2 = sp.Rational(5, 4) * d**2 - d / 12
K = sp.exp(lc1 * eps + lc2 * eps**2) * (1 - (g - 1) * eps)**(-1) * (1 - g * eps)**(-(j - 2))
ser = sp.series(K, eps, 0, 3).removeO()
k0 = sp.simplify(ser.coeff(eps, 0)); k1 = sp.expand(ser.coeff(eps, 1)); k2 = sp.expand(ser.coeff(eps, 2))
bj = (j + sp.Rational(3, 2)) * g - 1
cj = sp.Rational(1, 2) * (j + sp.Rational(3, 2)) * (j + sp.Rational(5, 2)) * g**2 - (j + sp.Rational(31, 12)) * g + 1
P("K의 0차:", k0, "; 1차 - b_j =", sp.simplify(k1 - bj), "; 2차 - c_j =", sp.simplify(k2 - cj))
# M_{j,21} = [ε^1] K (1-γε)^{-1} = b_j + γ = a_j
K1 = sp.series(K * (1 - g * eps)**(-1), eps, 0, 2).removeO().coeff(eps, 1)
aj = (j + sp.Rational(5, 2)) * g - 1
P("M_{j,21} - a_j =", sp.simplify(sp.expand(K1) - aj))
# lc_i 하계 2 d^i / i (정수 d, i<=6)
okl = True
for dd in range(0, 60):
    for i in range(1, 7):
        lc = Fr(1, i) * (Fr(dd**(i + 1), i + 1) + 2 * dd**i - sum(Fr(rho**i) for rho in range(dd)))
        if not (Fr(2 * dd**i, i) <= lc <= Fr(5 * dd**i, 2 * i)):
            okl = False
P("2d^i/i <= lc_i(d) <= 5d^i/(2i) (d<60, i<=6):", okl)
# M_{j,sr} >= 0 표본: j=3, γ=1..5, s<=6 (lc_i 전체 식 사용)
def lc_i(i, dd):
    return Fr(1, i) * (Fr(dd**(i + 1), i + 1) + 2 * dd**i - sum(Fr(rho**i) for rho in range(dd)))
okm = True
e = sp.symbols('e')
for jj in [2, 3, 5]:
    for gg in [1, 2, 3, 5]:
        logK = sum(sp.Rational(lc_i(i, gg).numerator, lc_i(i, gg).denominator) * e**i for i in range(1, 8))
        Kg = sp.exp(logK) * (1 - (gg - 1) * e)**(-1) * (1 - gg * e)**(-(jj - 2))
        for r in range(0, 4):
            s_ = sp.series(Kg * (1 - gg * e)**(-r), e, 0, 7).removeO()
            for s in range(r, 7):
                if s_.coeff(e, s - r) < 0:
                    okm = False
P("M_{j,sr}(γ) >= 0 표본(j∈{2,3,5}, γ<=5, s<=6):", okm)

# ---------- C7 ----------
P("== C7")
z, aa = sp.symbols('z a')
C = sp.Function('C')(z)
Y1 = lambda F: sp.Rational(5, 2) * z * (z * sp.diff(F, z) - F)
P("𝒴_1[C+a]-𝒴_1[C] =", sp.simplify(Y1(C + aa) - Y1(C)))
m = sp.symbols('m', integer=True, nonnegative=True)
P("((j+3/2)zC'-C)의 m차 계수 배율 (j+3/2)m-1: m=0에서", ((j + sp.Rational(3, 2)) * 0 - 1), "(음수) → 상수항이 있으면 ≼ 보존 실패")
# 실제 C_-, C_+, (K1) 상수항: w^{-1} at z=0 = 1, w=1
for name, expr in [("C_- = o(w^{-1}-1)", 1 - 1), ("C_+ = o(w^{-1}-11/12-w/12)", 1 - sp.Rational(11, 12) - sp.Rational(1, 12)), ("(K1) = o(w^{-1}-24/25-w/25)", 1 - sp.Rational(24, 25) - sp.Rational(1, 25)), ("kernel-crude (3/4)w^{-1}", sp.Rational(3, 4))]:
    P(f"  {name} 상수항 = {expr}")

# ---------- C9 ----------
P("== C9")
# p_n = (n+1)^{n-1}; A_{n,k-1} via 2:old-2-6: A_{n,k-1} = Σ_{j=1}^n C(n-1,j-1) min(j,k) A_{j-1,k-1} A_{n-j,k-1}, A_{0,·}=1
NMAX = 60
A = {}
def Acol(k):
    if k in A:
        return A[k]
    col = [1] * (NMAX + 1)
    for nn in range(1, NMAX + 1):
        col[nn] = sum(comb(nn - 1, jj - 1) * min(jj, k) * col[jj - 1] * col[nn - jj] for jj in range(1, nn + 1))
    A[k] = col
    return col
# 검산: A_{n,n-1} = p_n = (n+1)^{n-1}
P("A_{n,n-1}=(n+1)^{n-1} 확인 n<=12:", all(Acol(nn)[nn] == (nn + 1)**(nn - 1) for nn in range(1, 13)))
bad = []
cnt = 0
for N in range(1, NMAX + 1):
    for r in range(1, N + 2):
        for s in range(r, N + 2):
            lhs = Fr(Acol(r)[N], Acol(s)[N])
            prod = Fr(1)
            for i in range(1, N + 1):
                prod *= Fr(min(i, r), min(i, s))
            cnt += 1
            if lhs < prod:
                bad.append((N, r, s))
P(f"A_{{N,r-1}}/A_{{N,s-1}} >= Π min(i,r)/min(i,s): N<=60 전수 {cnt}건, 위반 {len(bad)}건", bad[:5])
# 특히 s=k, r=k-1, N>2k-1 포함
bad2 = []
for k in range(2, 20):
    for N in range(1, NMAX + 1):
        lhs = Fr(Acol(k - 1)[N], Acol(k)[N])
        rhs = Fr(k - 1, k)**max(N - k + 1, 0)
        if lhs < rhs:
            bad2.append((k, N))
P("s_N(k-1)/s_N(k) >= (1-1/k)^{max(N-k+1,0)} (k<20, N<=60, N>2k-1 포함) 위반:", bad2[:5], len(bad2))

open(__file__.replace('.py', '_out.txt'), 'w', encoding='utf-8').write("\n".join(out) + "\n")
