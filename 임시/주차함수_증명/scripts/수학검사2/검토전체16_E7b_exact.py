# E7b: 7.6-7.7절의 항등식·부등식을 작은 k에서 정확 유리수로 재검산
# (7.22),(7.23), 정리 top-roots, (7.24),(7.25),(7.26), threshold-unit-ratio 첫 등식, root-symmetry, explicit-bounds (나)
from fractions import Fraction as Fr
from math import comb, log, exp, factorial
from functools import lru_cache

@lru_cache(None)
def A(m, l):
    if l < 0: return 0
    if m == 0: return 1
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))
def p(m): return 1 if m == 0 else (m+1)**(m-1)
def s(m, y): return Fr(A(m, y-1), p(m))
def c(m, Y): return Fr(A(m, Y)-A(m, Y-1), p(m))
def P(n, j): return Fr(j*comb(n-1, j-1)*p(j-1)*p(n-j), p(n))
def Pk(n, j, k): return Fr(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), A(n, k-1))
def clp(m, k): return Fr(A(m, k)-A(m, k-1), A(m, k-1))
def clm(m, k): return Fr(A(m, k-1)-A(m, k-2), A(m, k-1))
def mu(m, k): return clp(m, k)-clm(m, k)
def chi(m, j, k):
    lin = Fr(0)
    if j == k: lin -= Fr(1, k)*(1-clm(m-k, k))
    if j > k: lin += Fr(1, k)*(clp(j-1, k)+clm(j-1, k)+clp(m-j, k)+clm(m-j, k))
    ind = 1 if j > k else 0
    return lin + (1+Fr(ind, k))*clp(j-1, k)*clp(m-j, k) + (1-Fr(ind, k))*clm(j-1, k)*clm(m-j, k)
def src(n, k): return sum(Pk(n, j, k)*chi(n, j, k) for j in range(1, n+1))
def inh(n, k): return sum(Pk(n, j, k)*(mu(j-1, k)*(k <= j-1 <= 2*k) + mu(n-j, k)*(k <= n-j <= 2*k)) for j in range(1, n+1))
def inhlin(n, k): return Fr(1, k)*sum(Pk(n, j, k)*((clp(j-1, k)+clm(j-1, k))*(k <= j-1 <= 2*k) + (clp(n-j, k)+clm(n-j, k))*(k <= n-j <= 2*k)) for j in range(1, n+1))
def rw(n, k, q): return Fr(k, k+1+q)*P(n, k+1+q)/P(n, k)
def hz(N, k): return 1 - s(N+1, k)/s(N, k)

ok = True
def chk(cond, msg):
    global ok
    if not cond:
        ok = False; print("FAIL:", msg)

for k in range(2, 7):
    for nu in range(1, 8):
        n = 2*k+nu
        L = k*s(n, k)*src(n, k)
        R22 = sum(Fr(k, j)*P(n, j)*((c(j-1, k-1)+c(j-1, k))*s(n-j, k) + s(j-1, k)*(c(n-j, k-1)+c(n-j, k))) for j in range(k+1, n+1)) - P(n, k)*s(n-k, k-1)
        chk(L >= R22, f"(7.22) k={k} nu={nu}")
        B1 = sum(rw(n, k, q)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1)
        B2 = c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
        chk(R22 >= P(n, k)*B1 and B1 >= B2, f"(7.23) k={k} nu={nu}")
        # apex equality: k s_n apex = P_n(k) * B1
        apex = Fr(1, k)*(sum(Pk(n, j, k)*(clp(j-1, k)+clm(j-1, k)) for j in range(n-k+1, n+1)) - Pk(n, k, k)*(1-clm(n-k, k)))
        chk(k*s(n, k)*apex == P(n, k)*B1, f"apex identity k={k} nu={nu}")
        # root-symmetry
        chk(rw(n, k, nu) == 1, f"rw(nu)=1 k={k} nu={nu}")
        for q in range(0, k+nu-1):
            lhs = rw(n, k, q+1)/rw(n, k, q)
            rhs = Fr((k+2+q)**(k+q), (k+1+q)**(k+q)) * Fr((k+nu-1-q)**(k+nu-2-q), (k+nu-q)**(k+nu-2-q))
            chk(lhs == rhs, f"rw ratio k={k} nu={nu} q={q}")
        # top-roots
        for U0 in range(0, k):
            T2 = B2 + sum((rw(n, k, k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1))
            T3 = s(n, k)*(sum((rw(n, k, k+nu-1-U)-1)*hz(n-1-U, k) for U in range(0, U0+1)) - 1)
            chk(B1 >= T2 >= T3, f"top-roots k={k} nu={nu} U0={U0}")
        # (7.25) for 2k+1<=n<=3k
        if n <= 3*k:
            KDp = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*(A(m, k)-2*A(m, k-1)+A(m, k-2)) for m in range(2*k+1, n))
            d = A(n, k)-2*A(n, k-1)+A(n, k-2)
            chk(A(n, k-1)*(src(n, k)+inh(n, k)) == d - KDp, f"(7.25) k={k} n={n}")
        # (7.24) for n>=3k+1
        if n >= 3*k+1:
            w = lambda m: Fr(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
            pm = lambda m: Fr((k+1)*(A(m, k)-A(m, k-1)) - (k-1)*(A(m, k-1)-A(m, k-2)), p(m))
            Left = sum(w(m)*pm(m) for m in range(k, 2*k+1))
            chk(inhlin(n, k)+inh(n, k) == 2*Left, f"(7.24) k={k} n={n}")
            # w nondecreasing
            chk(all(w(m+1) >= w(m) for m in range(k, 2*k)), f"w nondecreasing k={k} n={n}")
    # (7.26) and threshold-unit-ratio at n=3k
    n = 3*k
    w = lambda m: Fr(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
    pm = lambda m: Fr((k+1)*(A(m, k)-A(m, k-1)) - (k-1)*(A(m, k-1)-A(m, k-2)), p(m))
    Left = sum(w(m)*pm(m) for m in range(k, 2*k+1))
    u = w(2*k)*s(2*k, k+1)
    Quad = sum(Pk(n, j, k)*((1+Fr(1, k))*clp(j-1, k)*clp(n-j, k) + (1-Fr(1, k))*clm(j-1, k)*clm(n-j, k)) for j in range(k+1, n+1))
    Stem = Fr(1, k)*sum(Pk(n, j, k)*((clp(j-1, k)+clm(j-1, k))*(j-1 > 2*k) + (clp(n-j, k)+clm(n-j, k))*(n-j > 2*k)) for j in range(k+1, n+1))
    chk(src(n, k)+inh(n, k) == 2*Left - u + Quad + Stem, f"(7.26) k={k}")
    # threshold-unit-ratio first equality: u/w_k = e^{g(2k)-g(k)} * s_{2k}(k+1)/s_{2k-1}(k)
    eg = Fr((2*k+1)**(2*k-1), (2*k)**(2*k-1)) / Fr((k+1)**(k-1), k**(k-1))
    chk(u/w(k) == eg*s(2*k, k+1)/s(2*k-1, k), f"threshold-unit-ratio equality k={k}")
    chk(w(2*k)/w(k) == eg/s(2*k-1, k), f"w_2k/w_k k={k}")
    # P^(k)_{3k}(k) = k w_{2k} A_{2k,k-1}/p_{2k}
    chk(Pk(n, k, k) == k*w(2*k)*Fr(A(2*k, k-1), p(2*k)), f"P^(k)_3k(k) identity k={k}")
    # lower bound s_{2k-1}(k) >= binom(2k-1,k) k^{k-1}(k-1)^{k-2}/(2k)^{2k-2}
    chk(s(2*k-1, k) >= Fr(comb(2*k-1, k)*k**(k-1)*(k-1)**(k-2), (2*k)**(2*k-2)), f"two-tree lower bound k={k}")

# explicit-bounds (나) numeric
def Bor(d): return exp(-d)*d**(d-1)/factorial(d)
def Ren(j): return j**j*exp(-j)/factorial(j)
for m in range(1, 80):
    sg = m*log(m/(m+1))+1
    assert 0 <= sg <= 1/(2*(m+1)) + 1/(6*m*(m+1)) + 1e-15, m
    for U in range(0, m):
        chk(float(P(m, m-U)) <= Bor(U+1)*exp(sg)*(m+1)/(m-U)*(1+1e-12), f"explicit (나)1 m={m} U={U}")
    for j in range(1, m+1):
        chk(float(P(m, j)) <= Ren(j)*exp(sg)*(m+1)/(m+1-j)**2*(1+1e-12), f"explicit (나)2 m={m} j={j}")
    chk(Bor(m) <= (2*3.141592653589793)**-0.5*m**-1.5, f"Bor ub m={m}")
print("ALL OK" if ok else "SOME FAIL")
