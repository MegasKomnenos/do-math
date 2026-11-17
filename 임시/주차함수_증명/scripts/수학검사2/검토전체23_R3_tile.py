# R3 검산: 5.2.2절 — 타일 재귀, 동질 좌표 계수, 기울인 생일 평균 항등식 (ii), 하계 (iii), Pc(k), m(n).
from fractions import Fraction as Fr
from math import comb, factorial, sqrt, pi, log, isqrt
def p(n): return (n+1)**(n-1) if n >= 1 else 1
def tw(j): return Fr(1) if j == 1 else Fr((j-1)**(j-1), factorial(j))
def Gam_val(d, n, y):
    g = [Fr(1)]
    for dd in range(1, d+1):
        g.append(comb(n, dd)*p(dd) + y*sum(comb(n-dd+j, j)*p(j)*g[dd-1-j] for j in range(dd)))
    return g
def V(cos):  # tile sum with coordinates list
    v = [Fr(1)]
    for d in range(1, len(cos)+1):
        v.append((1+cos[d-1])*v[d-1] + sum(tw(j)*v[d-j] for j in range(2, d+1)))
    return v
ok = True
for n in (6, 9, 13):
    for yv in (Fr(2), Fr(7, 3), Fr(-1, 2)):
        g = Gam_val(n-1, n, yv)
        v = V([yv/Fr(n-i+1) for i in range(1, n)])
        for d in range(0, n):
            ff = Fr(factorial(n), factorial(n-d))
            if g[d] != ff*v[d]: ok = False; print("tile FAIL", n, yv, d)
# homogeneous coefficients
import sympy as sp
rho = sp.symbols('rho')
def hb(d):
    v = [sp.Integer(1)]
    for dd in range(1, d+1):
        v.append(sp.expand((1+rho)*v[dd-1] + sum(sp.Rational(tw(j).numerator, tw(j).denominator)*v[dd-j] for j in range(2, dd+1))))
    return v
H = hb(9)
for d in range(1, 10):
    for j in range(0, d+1):
        if H[d].coeff(rho, j) != sp.Rational((j+1)*(d+1)**(d-j-1) if d-j-1 >= 0 else 1, 1)/sp.factorial(d-j)*(1 if d-j-1 >= 0 else 1):
            if not (j == d and H[d].coeff(rho, j) == 1): ok = False; print("hb coeff FAIL", d, j)
    assert H[d].subs(rho, 1) == sp.Rational((d+1)**d, factorial(d))
print("tile/hb identities ok:", ok)
# tilted birthday law for r, k
def tilted(r, k):
    n = k + r; rh = Fr(k, n)
    bt = [Fr(1)]
    for j in range(1, r): bt.append(bt[-1]*(1-Fr(j, r)))
    w = [(j+1)*rh**j*bt[j] for j in range(0, r)]
    Z = sum(w)
    mu = sum(j*w[j] for j in range(r))/Z
    m2 = sum(j*j*w[j] for j in range(r))/Z
    return mu, m2
for (r, k) in ((5, 9), (12, 40), (30, 31)):
    mu, m2 = tilted(r, k)
    assert m2 + (3+Fr(r*r, k))*mu + 2 == 2*r, (r, k)
    assert m2 - mu <= Fr(3, 2)*mu*mu
print("(i),(ii) ok on samples")
for r in (64, 65, 100, 170, 400):
    k = int(r**1.5 + 8*r) + 1
    mu, _ = tilted(r, k)
    print("r=%d k=%d  tm=%.4f  (6/7)sqrt r=%.4f  ratio tm/sqrt r=%.4f" % (r, k, float(mu), 6/7*sqrt(r), float(mu)/sqrt(r)))
    eb = 6/7*sqrt(r)
    Pc = k*(1/(2*r)-1/(3*r*r)) - 2.5 + 2*eb*(1-1/k) - k/(k-1)*(1+sqrt(3*pi*(r-1)/2))
    print("    Pc(k) with eb=(6/7)sqrt r:", round(Pc, 4))
r, k = 170, 19831
print("branch (na): Pc =", k*(1/(2*r)-1/(3*r*r)) - 2.5 - k/(k-1)*(1+sqrt(3*pi*(r-1)/2)))
def m_of(n):
    m = 170; t = 171
    while t**3 <= (n-9*t)**2 and n-9*t >= 0:
        m = t; t += 1
    return m
print("m(20001)=", m_of(20001), " m(50001)=", m_of(50001), " 171^{3/2}+9*171=", 171**1.5+9*171)
for n in (20001, 50001, 10**6, 10**8):
    m = m_of(n); print(n, m, n**(2/3)-6*n**(1/3)-1 <= m <= n**(2/3)-6*n**(1/3)+37, round(m-(n**(2/3)-6*n**(1/3)), 3))
# cover-edge numbers
print("1/(1+9/sqrt598)=", 1/(1+9/sqrt(598)), " 832^1.5, 833^1.5, 1.2*20001:", 832**1.5, 833**1.5, 1.2*20001, " 965^1.5,966^1.5:", 965**1.5, 966**1.5)
