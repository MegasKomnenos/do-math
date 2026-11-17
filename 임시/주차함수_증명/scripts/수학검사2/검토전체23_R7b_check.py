# 검토전체23 R7b: 7.6-7.8 항등식·부등식의 정확 유리수 검산 (작은 k) 과 수치 상수 검산
from fractions import Fraction as F
from math import comb, log, sqrt, pi, exp, factorial
from functools import lru_cache
import sys

@lru_cache(None)
def A(m, l):
    if m == 0: return 1
    if l < 0: return 0
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def b(m, l): return A(m, l) - A(m, l-1)
def s(m, y): return F(A(m, y-1), p(m))
def c(m, Y): return F(b(m, Y), p(m))
def Pk(n, j, k): return F(min(j, k)*comb(n-1, j-1)*A(j-1, k-1)*A(n-j, k-1), A(n, k-1))
def P(n, j): return F(j*comb(n-1, j-1)*p(j-1)*p(n-j), p(n))
def clp(m, k): return F(b(m, k), A(m, k-1))
def clm(m, k): return F(b(m, k-1), A(m, k-1))
def mu(m, k): return clp(m, k) - clm(m, k)
def chi(n, j, k):
    L, R = j-1, n-j
    v = F(0)
    if j == k: v -= F(1, k)*(1 - clm(n-k, k))
    if j > k: v += F(1, k)*(clp(L, k)+clm(L, k)+clp(R, k)+clm(R, k))
    h = 1 if j > k else 0
    v += (1+F(h, k))*clp(L, k)*clp(R, k) + (1-F(h, k))*clm(L, k)*clm(R, k)
    return v
def src(n, k): return sum(Pk(n, j, k)*chi(n, j, k) for j in range(1, n+1))
def inh(n, k):
    t = F(0)
    for j in range(1, n+1):
        L, R = j-1, n-j
        if k <= L <= 2*k: t += Pk(n, j, k)*mu(L, k)
        if k <= R <= 2*k: t += Pk(n, j, k)*mu(R, k)
    return t
def inhlin(n, k):
    t = F(0)
    for j in range(1, n+1):
        L, R = j-1, n-j
        if k <= L <= 2*k: t += Pk(n, j, k)*(clp(L, k)+clm(L, k))
        if k <= R <= 2*k: t += Pk(n, j, k)*(clp(R, k)+clm(R, k))
    return t/k
def apex(n, k):
    t = sum(Pk(n, j, k)*(clp(j-1, k)+clm(j-1, k)) for j in range(n-k+1, n+1))
    return (t - Pk(n, k, k)*(1-clm(n-k, k)))/k
def rw(q, n, k): return F(k, k+1+q)*P(n, k+1+q)/P(n, k)
def w(m, n, k): return F(comb(n-1, m)*p(m)*A(n-1-m, k-1), A(n, k-1))
def delta(m1, k):  # delta_{m+1}
    m = m1-1
    return (k+1)*b(m, k) - (k-1)*b(m, k-1)
def pm(m, k): return F(delta(m+1, k), p(m))
def hz(N, k): return 1 - s(N+1, k)/s(N, k)
def g(x): return (x-1)*log(1+1/x)

ok = True
def chk(cond, msg):
    global ok
    if not cond:
        ok = False; print("FAIL", msg)

for k in range(2, 7):
    for nu in range(1, 3*k+5):
        n = 2*k+nu
        # (가) rw(nu)=1; q>=nu -> rw>=1
        chk(rw(nu, n, k) == 1, ("rw(nu)", k, n))
        for q in range(nu, k+nu): chk(rw(q, n, k) >= 1, ("rw>=1", k, n, q))
        # src >= apex
        S = src(n, k); Ap = apex(n, k)
        chk(S >= Ap, ("src>=apex", k, n))
        # (7.10)
        chk(mu(n, k) == S + sum(Pk(n, j, k)*(mu(j-1, k)+mu(n-j, k)) for j in range(1, n+1)), ("7.10", k, n))
        # (7.11) equality
        lhs = k*s(n, k)*Ap
        mid0 = P(n, k)*(sum(rw(q, n, k)*(c(k+q, k-1)+c(k+q, k)) for q in range(nu, k+nu)) - s(k+nu, k-1))
        chk(lhs == mid0, ("7.11 eq", k, n))
        for U0 in range(0, k):
            mid = P(n, k)*(c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
                           + sum((rw(k+nu-1-U, n, k)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1)))
            last = P(n, k)*s(n, k)*(sum((rw(k+nu-1-U, n, k)-1)*hz(n-1-U, k) for U in range(0, U0+1)) - 1)
            chk(mid0 >= mid >= last, ("7.11 ineq", k, n, U0))
        if n >= 3*k+1:
            chk(S >= inhlin(n, k) + Ap, ("src>=inhlin+apex", k, n))
            Left = sum(w(m, n, k)*pm(m, k) for m in range(k, 2*k+1))
            chk(inhlin(n, k) + inh(n, k) == 2*Left, ("7.13", k, n))
        if 2*k+1 <= n <= 3*k:
            KD = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
            chk(A(n, k-1)*(S+inh(n, k)) == (b(n, k)-b(n, k-1)) - KD, ("7.14", k, n))
        # P^{(k)}_n(m+1)=k s_m(k) w_m
        for m in range(k, 2*k+1):
            if m+1 <= n: chk(Pk(n, m+1, k) == k*s(m, k)*w(m, n, k), ("Pk=k s w", k, n, m))
    # (7.15) at n=3k and threshold unit ratio
    n = 3*k
    Left = sum(w(m, n, k)*pm(m, k) for m in range(k, 2*k+1))
    u = w(2*k, n, k)*s(2*k, k+1)
    Quad = sum(Pk(n, j, k)*((1+F(1, k))*clp(j-1, k)*clp(n-j, k)+(1-F(1, k))*clm(j-1, k)*clm(n-j, k)) for j in range(k+1, n+1))
    Stem = sum(Pk(n, j, k)*((clp(j-1, k)+clm(j-1, k))*(1 if j-1 > 2*k else 0)+(clp(n-j, k)+clm(n-j, k))*(1 if n-j > 2*k else 0)) for j in range(k+1, n+1))/k
    chk(src(n, k)+inh(n, k) == 2*Left - u + Quad + Stem, ("7.15", k))
    ratio = u/w(k, n, k)
    surv = s(2*k, k+1)/s(2*k-1, k)
    chk(abs(float(ratio) - exp(g(2*k)-g(k))*float(surv)) < 1e-12, ("thr ratio eq", k, float(ratio), exp(g(2*k)-g(k))*float(surv)))
    chk(float(surv) <= exp(g(k))+1e-15 and float(ratio) < exp(1), ("thr ratio bd", k))
    # light-root form for n<3k
    for n in range(2*k+1, 3*k):
        for j in range(max(1, n-2*k), k):
            m = n-j
            chk(Pk(n, j, k)*mu(m, k) == (n-m)*w(m, n, k)*F(b(m, k)-b(m, k-1), p(m)), ("light", k, n, j))
    print("k", k, "done", ok)

# explicit bounds
def Bor(m): return exp(-m + (m-1)*log(m) - sum(log(i) for i in range(1, m+1)))
def Ren(j): return j*Bor(j)
for m in range(1, 60):
    sg = m*log(m/(m+1))+1
    chk(-1e-15 <= sg <= 1/(2*(m+1))+1/(6*m*(m+1))+1e-15, ("sg", m))
    for U in range(0, m):
        chk(float(P(m, m-U)) <= Bor(U+1)*exp(sg)*(m+1)/(m-U)*(1+1e-12), ("Pb1", m, U))
        chk(float(P(m, m-U)) >= Bor(U+1)*(1-1e-12), ("2-32", m, U))
    for j in range(1, m+1):
        chk(float(P(m, j)) <= Ren(j)*exp(sg)*(m+1)/(m+1-j)**2*(1+1e-12), ("Pb2", m, j))
print("explicit bounds ok", ok)

# constants in 7:apex-positive
print("1-sqrt(2/pi)/sqrt(301) =", 1-sqrt(2/pi)/sqrt(301))
print("sum Bor(1..301) =", sum(Bor(d) for d in range(1, 302)))
print("(2pi)^-1/2 =", (2*pi)**-0.5)
print("0.9538/0.398943 =", 0.9538/0.398943)
n = 904
print("sg bound at 904 =", 1/(2*(n+1))+1/(6*n*(n+1)), " e^-0.0006=", exp(-0.0006))
print("2.38*0.9994*4/9/2 =", 2.38*0.9994*4/9/2)
print("0.528*sqrt(301)-151/301-1 =", 0.528*sqrt(301)-151/301-1)
print("(1-k/n)^2 at n=3k+1,k=301:", (1-301/904)**2, " 4/9=", 4/9)
print("2*1.549-e =", 2*1.549-exp(1))
print("3k-300>=k iff k>=150; 3k+1-300>=2k iff k>=299")
print("ALL OK" if ok else "SOME FAIL")
