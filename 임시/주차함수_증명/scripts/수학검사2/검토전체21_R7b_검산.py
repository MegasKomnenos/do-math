# 검토전체21 R7b: 7.6-7.8절 수치·항등식 검산 (정확 유리수)
from fractions import Fraction as Fr
from math import comb, log, exp, sqrt, pi, factorial, lgamma
from functools import lru_cache

@lru_cache(None)
def A(m, l):
    # 최대 변위 <= l 인 길이 m 주차함수 수 (마지막 차 재귀, 정리 2.11)
    if l < 0: return 0
    if m == 0: return 1
    return sum(comb(m-1, j-1) * min(j, l+1) * A(j-1, l) * A(m-j, l) for j in range(1, m+1))

def p(m): return 1 if m == 0 else (m+1)**(m-1)
def s(m, y): return Fr(A(m, y-1), p(m))          # 생존 확률
def c(m, Y): return Fr(A(m, Y) - A(m, Y-1), p(m)) # 수준 질량
def b(m, l): return A(m, l) - A(m, l-1)
def d(m, k): return b(m, k) - b(m, k-1)
def P(m, j): return Fr(j * comb(m-1, j-1) * p(j-1) * p(m-j), p(m))  # 마지막 차 자리 법칙
def Pk(m, j, k): return Fr(min(j, k) * comb(m-1, j-1) * A(j-1, k-1) * A(m-j, k-1), A(m, k-1))
def clp(m, k): return Fr(b(m, k), A(m, k-1)) if m >= 1 else Fr(0)
def clm(m, k): return Fr(b(m, k-1), A(m, k-1)) if m >= 1 else Fr(0)
def mu(m, k): return Fr(d(m, k), A(m, k-1)) if m >= 1 else Fr(0)
def Bor(m): return exp(-m + (m-1)*log(m) - lgamma(m+1))
def Ren(j): return exp(j*log(j) - j - lgamma(j+1))
def g(x): return (x-1) * log(1 + 1/x)

def chi(m, j, k):
    L = clp(j-1, k) + clm(j-1, k); R = clp(m-j, k) + clm(m-j, k)
    lin = Fr(1, k) * (-(1 if j == k else 0) * (1 - clm(m-k, k)) + (1 if j > k else 0) * (L + R))
    e = Fr(1 if j > k else 0, k)
    return lin + (1 + e) * clp(j-1, k) * clp(m-j, k) + (1 - e) * clm(j-1, k) * clm(m-j, k)
def src(m, k): return sum(Pk(m, j, k) * chi(m, j, k) for j in range(1, m+1))
def inh(m, k): return sum(Pk(m, j, k) * (mu(j-1, k) * (1 if k <= j-1 <= 2*k else 0) + mu(m-j, k) * (1 if k <= m-j <= 2*k else 0)) for j in range(1, m+1))
def inhlin(m, k): return Fr(1, k) * sum(Pk(m, j, k) * ((clp(j-1, k) + clm(j-1, k)) * (1 if k <= j-1 <= 2*k else 0) + (clp(m-j, k) + clm(m-j, k)) * (1 if k <= m-j <= 2*k else 0)) for j in range(1, m+1))
def apex(n, k): return Fr(1, k) * (sum(Pk(n, j, k) * (clp(j-1, k) + clm(j-1, k)) for j in range(n-k+1, n+1)) - Pk(n, k, k) * (1 - clm(n-k, k)))
def rw(n, k, q): return Fr(k, k+1+q) * P(n, k+1+q) / P(n, k)
def hz(N, k): return 1 - s(N+1, k) / s(N, k)
def w(n, m, k): return Fr(comb(n-1, m) * p(m) * A(n-1-m, k-1), A(n, k-1))
def frakp(m, k): return (k+1) * c(m, k) - (k-1) * c(m, k-1)
def V(k, m): return sum(frakp(mm, k) for mm in range(m, 2*k+1))

ok = True
def check(name, cond):
    global ok
    print(('OK  ' if cond else 'FAIL'), name)
    ok = ok and cond

# 1. 보조정리 root-symmetry
for k in range(2, 7):
    for nu in range(1, k+1):
        n = 2*k + nu
        check(f'rw(nu)=1 k={k} nu={nu}', rw(n, k, nu) == 1)
        for q in range(0, k+nu-1):
            lhs = float(rw(n, k, q+1) / rw(n, k, q)); rhs = exp(g(k+1+q) - g(k+nu-1-q))
            check(f'rw ratio k={k} nu={nu} q={q}', abs(lhs - rhs) < 1e-12 * max(1, lhs))
        check(f'rw>=1 for q>=nu k={k} nu={nu}', all(rw(n, k, q) >= 1 for q in range(nu, k+nu)))

# 2. 정리 top-roots: 등식과 두 부등식 (7.11)
for k in range(2, 7):
    for nu in range(1, k+1):
        n = 2*k + nu
        lhs = k * s(n, k) * apex(n, k)
        mid = P(n, k) * (sum(rw(n, k, q) * (c(k+q, k-1) + c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1))
        check(f'top-roots equality k={k} nu={nu}', lhs == mid)
        for U0 in range(0, k):
            b1 = P(n, k) * (c(k+nu, k-1) + s(k+nu, k+1) - s(n, k) - s(n, k+1) + sum((rw(n, k, k+nu-1-U) - 1) * (s(n-1-U, k) - s(n-U, k)) for U in range(0, U0+1)))
            b2 = P(n, k) * s(n, k) * (sum((rw(n, k, k+nu-1-U) - 1) * hz(n-1-U, k) for U in range(0, U0+1)) - 1)
            check(f'top-roots ineq1 k={k} nu={nu} U0={U0}', mid >= b1)
            check(f'top-roots ineq2 k={k} nu={nu} U0={U0}', b1 >= b2)

# 3. src >= apex, src >= inhlin + apex (n>=3k+1)
for k in range(2, 6):
    for n in range(2*k+1, 3*k+5):
        check(f'src>=apex k={k} n={n}', src(n, k) >= apex(n, k))
        if n >= 3*k+1:
            check(f'src>=inhlin+apex k={k} n={n}', src(n, k) >= inhlin(n, k) + apex(n, k))
            Left = sum(w(n, m, k) * frakp(m, k) for m in range(k, 2*k+1))
            check(f'(7.13) inhlin+inh=2Left k={k} n={n}', inhlin(n, k) + inh(n, k) == 2 * Left)

# 4. 보조정리 explicit-bounds
for m in range(1, 80):
    sg = m * log(m/(m+1)) + 1
    check(f'sg bounds m={m}', -1e-15 <= sg <= 1/(2*(m+1)) + 1/(6*m*(m+1)) + 1e-15)
    for U in range(0, m):
        check(f'P_m(m-U)<=Bor e^sg (m+1)/(m-U) m={m} U={U}', float(P(m, m-U)) <= Bor(U+1) * exp(sg) * (m+1)/(m-U) * (1 + 1e-12))
    for j in range(1, m+1):
        check(f'P_m(j)<=Ren e^sg (m+1)/(m+1-j)^2 m={m} j={j}', float(P(m, j)) <= Ren(j) * exp(sg) * (m+1)/(m+1-j)**2 * (1 + 1e-12))

# 5. (7.14) 항등식, (7.15), 보조정리 threshold-unit-ratio
for k in range(2, 7):
    for n in range(2*k+1, 3*k+1):
        KD = sum((k+n-m) * comb(n-1, m) * p(n-1-m) * d(m, k) for m in range(2*k+1, n))
        check(f'(7.14) k={k} n={n}', A(n, k-1) * (src(n, k) + inh(n, k)) == d(n, k) - KD)
    n = 3*k
    Left = sum(w(n, m, k) * frakp(m, k) for m in range(k, 2*k+1))
    u = w(n, 2*k, k) * s(2*k, k+1)
    Quad = sum(Pk(n, j, k) * ((1 + Fr(1, k)) * clp(j-1, k) * clp(n-j, k) + (1 - Fr(1, k)) * clm(j-1, k) * clm(n-j, k)) for j in range(k+1, n+1))
    Stem = Fr(1, k) * sum(Pk(n, j, k) * ((clp(j-1, k) + clm(j-1, k)) * (1 if j-1 > 2*k else 0) + (clp(n-j, k) + clm(n-j, k)) * (1 if n-j > 2*k else 0)) for j in range(k+1, n+1))
    check(f'(7.15) k={k}', src(n, k) + inh(n, k) == 2 * Left - u + Quad + Stem)
    # 문턱 뿌리 항
    thr = Pk(n, k, k) * (mu(2*k, k) - Fr(1, k) * (1 - clm(2*k, k)))
    check(f'threshold-root term k={k}', thr == w(n, 2*k, k) * frakp(2*k, k) - u)
    # threshold-unit-ratio
    r_thr = s(2*k, k+1) / s(2*k-1, k)
    check(f'u/w_k = e^(g2k-gk) r_thr k={k}', abs(float(u / w(n, k, k)) - exp(g(2*k) - g(k)) * float(r_thr)) < 1e-12)
    check(f'r_thr<=e^g(k) k={k}', float(r_thr) <= exp(g(k)) * (1 + 1e-12))
    check(f'u/w_k<e k={k}', float(u / w(n, k, k)) < exp(1))
    # w 비감소 (정리 6.9: k>=43이지만 작은 k에서도 관찰)
    print('   w_m (n=3k) nondecreasing?', all(w(n, m, k) <= w(n, m+1, k) for m in range(k, 2*k)), ' k=', k)

# 6. 정리 apex-positive 상수
print('sum Bor(1..301) >=', 1 - sqrt(2/pi)/sqrt(301), ' exact sum =', sum(Bor(d) for d in range(1, 302)))
print('0.9538/0.398943 =', 0.9538/0.398943, ' (2pi)^-1/2 =', (2*pi)**-0.5)
print('sg_904 <=', 1/(2*905) + 1/(6*904*905), ' e^-0.0006 =', exp(-0.0006))
print('2.38*0.9994*(4/9)/2 =', 2.38*0.9994*(4/9)/2)
print('k=301 bracket =', 0.528*sqrt(301) - 151/301 - 1)
print('2*1.549 - e =', 2*1.549 - exp(1))
print('hz floor check: 1/k(3/4-11/(6k)) >= 1/(2k) for k>=8 ->', all((0.75 - 11/(6*k)) >= 0.5 for k in range(8, 1000)))
print('ALL OK' if ok else 'SOME FAIL')
