# M1: 정리 2-40 다섯 몫 분해, 명제 2-41, 보조정리 b-top, 정리 2-38(ii)(iii), 따름 2-39(d), 보조정리 2-37(다)(라)(마) 수치 대조
from math import comb, factorial, cosh, exp, sqrt, pi
from fractions import Fraction as Fr
from functools import lru_cache
import sympy as sp

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j)*min(j+1, l+1)*A(j, l)*A(n-1-j, l) for j in range(n))
def b(n, l): return A(n, l)-A(n, l-1)
def p(n): return (n+1)**(n-1) if n >= 1 else 1
def N(l, t): return min(t, l+1)*A(t-1, l) if t >= 1 else 0
def bT(t, l): return N(l, t)-N(l-1, t)
ok = True
# b-top
for k in range(2, 12):
    if b(k, k-1) != k**(k-2): ok = False; print("b-top FAIL", k)
# five-part decomposition
x = sp.symbols('x')
for k in range(2, 8):
    for n in range(2*k+1, 3*k):
        Theta = comb(n, k)*k**(k-2)*A(n-k, k-1)
        FL = sum(comb(n, t)*(bT(t, k)-bT(t, k-1))*A(n-t, k-1) for t in range(k+1, 2*k+2))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*(b(m, k)-b(m, k-1)) for m in range(2*k+1, n))
        # PAIR via series
        Ak1 = sum(sp.Integer(A(m, k-1))*x**m/sp.factorial(m) for m in range(0, n+1))
        Bk = sum(sp.Integer(bT(t, k))*x**t/sp.factorial(t) for t in range(1, n+1))
        Bk1 = sum(sp.Integer(bT(t, k-1))*x**t/sp.factorial(t) for t in range(1, n+1))
        PAIR = sp.Rational(1, 2)*sp.factorial(n)*sp.expand(Ak1*(Bk**2+Bk1**2)).coeff(x, n)
        PAIR2 = Fr(1, 2)*sum(Fr(factorial(n), factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bT(t1, k)*bT(t2, k)+bT(t1, k-1)*bT(t2, k-1))*p(n-t1-t2) for t1 in range(1, n) for t2 in range(1, n-t1+1))
        d = b(n, k)-b(n, k-1)
        if d != -Theta+FL+BV+KD+PAIR: ok = False; print("2-40 FAIL", k, n, d, -Theta+FL+BV+KD+PAIR)
        if PAIR != PAIR2: ok = False; print("2-41 FAIL", k, n)
print("2-40/2-41/b-top ok =", ok)

# 2-38 (ii)(iii), 2-39(d), 2-37
def Ren(j): return 1.0 if j == 0 else j**j*exp(-j)/factorial(j)
def Bor(m): return exp(-m)*m**(m-1)/factorial(m)
def theta(t, k): return comb(t, k)*k**(k-1)*(t-k)**(t-k)/t**(t-1) if t > k else 1.0
def xt(t, k):
    return (N(k, t)-2*N(k-1, t)+N(k-2, t))/t**(t-1)
for k in range(2, 15):
    P = 0.0
    for t in range(k, 2*k+1):
        q = t-k
        v = k*xt(t, k); th = theta(t, k)
        if not (v >= -th-1e-12): ok = False; print("2-38(ii) FAIL", k, t)
        if not (v <= -th+(2*q*q+q)*cosh(q/k)/k+1e-12): ok = False; print("2-38(iii) FAIL", k, t)
        if not (Ren(q)-1e-12 <= th <= Ren(q)*(1+q/k)**1.5+1e-12): ok = False; print("2-38(iv) FAIL", k, t)
        P += xt(t, k)
        Psi = sum(Ren(j) for j in range(1, q+1))
        if not (k*P >= -(1+q/k)**1.5*(1+Psi)-1e-12): ok = False; print("2-39(d) FAIL", k, t)
        if not (abs(th-Ren(t-k)*Bor(k)/Bor(t)) < 1e-9): ok = False; print("2-37(마) FAIL", k, t)
    if abs(k*xt(k+1, k) + (k-1)*k**(k-1)/(k+1)**k) > 1e-12: ok = False; print("q=1 closed form FAIL", k)
for q in range(1, 60):
    Psi = sum(Ren(j) for j in range(1, q+1))
    lhs = sum(Bor(m)*sum(Ren(j) for j in range(1, q-m+1)) for m in range(1, q+1))
    if abs(lhs-(Psi-sum(Bor(m) for m in range(1, q+1)))) > 1e-10: ok = False; print("2-37(다) FAIL", q)
    if not (Psi <= 0.7979*sqrt(q)): ok = False; print("2-37(라) FAIL", q)
    if not (Ren(q) <= (2*pi*q)**-0.5): ok = False; print("2-37(라) Ren FAIL", q)
print("2-37/2-38/2-39 ok =", ok)
print("zeta:", sp.N(sp.zeta(sp.Rational(1, 2)), 12), sp.N(sp.zeta(-sp.Rational(1, 2)), 12), sp.N(sp.zeta(sp.Rational(3, 2)), 12))
