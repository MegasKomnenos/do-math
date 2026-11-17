# R11 검산: D.exact-n20000 (ㄱ)(ㄴ)(ㄹ)의 재귀와 D.c50의 Y, Z 재귀를 작은 n에서 정확 유리수로 대조
from fractions import Fraction as F
from math import comb, factorial
N = 40
def p(n): return (n+1)**(n-1) if n >= 1 else 1
# exact A_{n,l}
A = {}
for l in range(-1, N+2):
    col = [1]
    for n in range(1, N+1):
        col.append(0 if l < 0 else sum(comb(n-1, j)*min(j+1, l+1)*col[j]*col[n-1-j] for j in range(n)))
    for n in range(N+1): A[n, l] = col[n] if (l >= 0 or n == 0) else 0
b = lambda n, l: A[n, l]-A[n, l-1]
# (ㄹ) exceedance recursion
ok = True
for k in range(1, 20):
    Ac = lambda n: p(n)-A[n, k-1]
    for n in range(k+1, min(2*k+1, N)+1):
        rhs = sum(comb(n-1, i)*(n-k-i)*p(i)*p(n-1-i) for i in range(0, n-k)) + sum(comb(n-1, i)*(k+i+1)*p(i)*Ac(n-1-i) for i in range(0, n-k-1))
        if rhs != Ac(n): ok = False; print("exceed mismatch", k, n)
print("(ㄹ) 넘는 수 재귀 k<=19, k+1<=n<=2k+1:", ok)
# (ㄴ) n a_n = sum_{j=1}^n min(j,k) a_{j-1} a_{n-j}
ok = True
for k in range(1, 12):
    a = [F(A[n, k-1], factorial(n)) for n in range(N+1)]
    for n in range(1, N+1):
        if n*a[n] != sum(min(j, k)*a[j-1]*a[n-j] for j in range(1, n+1)): ok = False
print("(ㄴ) 재귀:", ok)
# (ㄱ) three series: T<=k, G=exp, Q, H' = k Q H + k (G-Q), E = G/(1-H)
ok = True
for k in range(1, 10):
    t = [F(0)]+[F(j**(j-1), factorial(j)) if j <= k else F(0) for j in range(1, N+1)]
    g = [F(1)]
    for n in range(1, N+1): g.append(sum(j*t[j]*g[n-j] for j in range(1, n+1))/n)
    q = [F(p(j), factorial(j)) if j < k else F(0) for j in range(N+1)]
    h = [F(0)]
    for n in range(1, N+1):
        h.append((k*sum(q[i]*h[n-1-i] for i in range(n))+k*(g[n-1]-q[n-1]))/n)
    e = [F(1)]
    for n in range(1, N+1): e.append(g[n]+sum(h[j]*e[n-j] for j in range(1, n+1)))
    if any(e[n] != F(A[n, k-1], factorial(n)) for n in range(N+1)): ok = False; print("col mismatch", k)
    if any(g[n]-q[n] < 0 for n in range(N+1)) or any(x < 0 for x in h): ok = False; print("negativity", k)
print("(ㄱ) E=G/(1-H) = sum a_n x^n, 항 비음:", ok)
# c50: s_n(y), c_n(y) recursions and hB-normalised forms (exact rationals, e-free: use weights without e)
# pi_n(s) = C(n,s) s^{s-1} p_{n-s}/p_n
def pi(n, s): return F(comb(n, s)*s**(s-1)*p(n-s), p(n))
ok = True
for y in range(1, 14):
    s_ = lambda m, yy: F(A[m, yy-1], p(m))
    c_ = lambda m, yy: F(b(m, yy), p(m))
    for n in range(y, min(2*y+1, N)+1):
        pi0 = 1-sum(pi(n, t) for t in range(y+1, n+1))
        if s_(n, y) != pi0+sum(pi(n, t)*F(y, t)*s_(t-1, y) for t in range(y+1, n+1)): ok = False; print("s mismatch", y, n)
        if c_(n, y) != sum(pi(n, t)/t*(s_(t-1, y+1)+y*c_(t-1, y)) for t in range(y+1, n+1)): ok = False; print("c mismatch", y, n)
print("c50 두 재귀 (y<=13, n<=2y+1):", ok)
