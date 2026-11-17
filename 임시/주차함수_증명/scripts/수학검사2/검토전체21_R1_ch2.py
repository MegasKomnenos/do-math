# R1: 2장 항등식·부등식의 수치 검산 (전수 조사 n<=7, 재귀, 급수)
from math import comb
from fractions import Fraction as Fr
from itertools import product, permutations
from functools import lru_cache
from collections import Counter
import mpmath as mp
mp.mp.dps = 40

def p(n): return (n+1)**(n-1) if n >= 1 else 1
@lru_cache(None)
def A(n, l):
    if n == 0: return 1
    if l < 0: return 0
    return sum(comb(n-1, j)*min(j+1, l+1)*A(j, l)*A(n-1-j, l) for j in range(n))
def b(n, l): return A(n, l)-A(n, l-1)
def d(n, k): return b(n, k)-b(n, k-1)
def prod(xs):
    r = 1
    for x in xs: r *= x
    return r

def park(a):
    n = len(a); slots = [0]*(n+2); pos = [0]*n
    for i, ai in enumerate(a):
        q = ai
        while q <= n and slots[q]: q += 1
        if q > n: return None
        slots[q] = i+1; pos[i] = q
    return pos
def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        z = max([j for j in range(1, i) if sigma[j-1] > sigma[i-1]]+[0]); h.append(i-z)
    return h

for n in range(1, 8):
    pfs = []
    for a in product(range(1, n+1), repeat=n):
        pos = park(a)
        if pos is None: continue
        disp = [pos[i]-a[i] for i in range(n)]
        sigma = [0]*n
        for i in range(n): sigma[pos[i]-1] = i+1
        pfs.append((a, disp, tuple(sigma), pos))
    assert len(pfs) == p(n)
    fib = Counter(s for _, _, s, _ in pfs)
    for s_, cnt in fib.items():
        assert cnt == prod(caps(s_))
    perms = list(permutations(range(1, n+1)))
    capl = {s_: caps(s_) for s_ in perms}
    for l in range(0, n):
        assert A(n, l) == sum(prod(min(x, l+1) for x in capl[s_]) for s_ in perms)
    for k in range(1, n+1):
        E_even = sum(1 for _, disp, _, _ in pfs if max(disp) == k and disp.count(k) % 2 == 0 and disp.count(k) > 0)
        E2 = sum(1 for _, disp, _, _ in pfs if max(disp) == k and disp.count(k) == 2)
        def blocked(disp, s_, pos):
            h = capl[s_]; m = max(disp)
            return all(h[pos[i]-1] == m+1 for i in range(n) if disp[i] == m)
        B = sum(1 for _, disp, s_, pos in pfs if max(disp) == k-1 and blocked(disp, s_, pos))
        assert d(n, k) == 2*E_even-B, (n, k)
        assert 2*E2-B <= d(n, k)
        J = 0; en = 0
        for s_ in perms:
            h = capl[s_]; H = h.count(k); Z = sum(1 for x in h if x > k)
            pr_lt = prod(x for x in h if x < k); pr_le = prod(x for x in h if x <= k)
            if H > 0: J += H*k**(H-1)*(k-1)**Z*pr_lt
            if Z >= 2: en += pr_le*Z*(Z-1)*k**(Z-2)
        assert B <= J, (n, k, B, J)
        if n <= 2*k-1: assert B == J, (n, k, B, J)
        if n == 2*k: assert J-B == comb(2*k-1, k-1)*p(k-1)**2, (n, k)
        assert en == 2*E2, (n, k, en, E2)
print("brute force n<=7: 정리2.3/2.4/2.28/2.29/2.33(ㄹ)(ㅁ) OK")

def Borf(m): return mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m)
def Ren(j): return mp.mpf(1) if j == 0 else j*Borf(j)
def pi_n(n, m): return Fr(comb(n, m)*m**(m-1)*p(n-m), p(n))
def s(m, y): return Fr(A(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(m, Y), p(m))
for y in range(1, 13):
    for n in range(1, 2*y+2):
        pi0 = 1-sum(pi_n(n, m) for m in range(y+1, n+1))
        assert pi0+sum(pi_n(n, m)*Fr(y, m)*s(m-1, y) for m in range(y+1, n+1)) == s(n, y), (y, n)
        assert sum(pi_n(n, m)/m*(s(m-1, y+1)+y*c(m-1, y)) for m in range(y+1, n+1)) == c(n, y), (y, n)
print("정리 2.13(나)·한 나무 재귀 OK (y<=12)")
for m in range(0, 40):
    for y in range(1, 45):
        assert s(m+1, y) <= s(m, y) and s(m, y) <= s(m+1, y+1), (m, y)
for Y in range(1, 20):
    for K in range(Y+1, 45):
        assert sum(c(m, Y) for m in range(Y+1, K+1)) >= 1-s(K, Y)
print("정리 2.31·보조정리 2.34 OK")
def P(m, j): return Fr(j*comb(m-1, j-1)*p(j-1)*p(m-j), p(m))
for rho in range(0, 15):
    for m in range(rho+1, 60):
        assert P(m+1, m+1-rho) <= P(m, m-rho)
        assert float(P(m, m-rho)) >= float(Borf(rho+1))-1e-15
for j in range(1, 30):
    for m in range(j, 60):
        assert (m+1)*P(m+1, j) <= m*P(m, j)
print("보조정리 2.32 OK")
for t in range(1, 30):
    for k in range(1, t+1):
        lhs = Fr(comb(t, k)*k**(k-1)*((t-k)**(t-k) if t > k else 1), t**(t-1))
        rhs = Ren(t-k)*Borf(k)/Borf(t)
        assert abs(float(lhs)-float(rhs)) < 1e-12*float(lhs)
print("theta_t(k) OK")
def N(l, t): return min(t, l+1)*A(t-1, l)
for k in range(2, 9):
    for t in range(1, 3*k):
        bTk = N(k, t)-N(k-1, t); bTk1 = N(k-1, t)-N(k-2, t)
        if t >= k+1: assert bTk == A(t-1, k)+k*b(t-1, k)
        else: assert bTk == 0
        if t >= k: assert bTk1 == A(t-1, k-1)+(k-1)*b(t-1, k-1)
        else: assert bTk1 == 0
        if t >= k+1: assert bTk-bTk1 == k*d(t-1, k)+b(t-1, k)+b(t-1, k-1)
    assert N(k-1, k)-N(k-2, k) == k**(k-2) == b(k, k-1)
    for n in range(1, 2*k+2):
        assert b(n, k) == sum(comb(n, t)*(N(k, t)-N(k-1, t))*A(n-t, k-1) for t in range(1, n+1))
    for n in range(1, 2*k):
        assert b(n, k-1) == sum(comb(n, t)*(N(k-1, t)-N(k-2, t))*A(n-t, k-1) for t in range(1, n+1))
    # 정의 old-2-40: Theta_n, BV_n 와 첫 항의 t>=2k+2 몫
    for n in range(2*k+1, 3*k+1):
        Theta = comb(n, k)*k**(k-2)*A(n-k, k-1)
        assert Theta == -comb(n, k)*(N(k, k)-N(k-1, k)-(N(k-1, k)-N(k-2, k)))*A(n-k, k-1)
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        big = sum(comb(n, t)*(N(k, t)-N(k-1, t)-N(k-1, t)+N(k-2, t))*A(n-t, k-1) for t in range(2*k+2, n+1))
        assert big == BV+sum(comb(n, t)*k*d(t-1, k)*p(n-t) for t in range(2*k+2, n+1))
print("b-top·tree-expansion(다)·정의 old-2-40 OK")
for n in range(3, 120):
    for r in range(1, (n-1)//2+1):
        Q1 = comb(n, r)*(n-r)**(n-r-2)*(r+1)**r
        assert b(n, n-r-1)-b(n, n-r) <= Q1
        nf = mp.e**r*mp.factorial(n)/mp.factorial(n-r)*mp.mpf(n-r)**(n-r-2)/mp.mpf(n)**(n-2)
        assert (mp.mpf(n)/(n-r))**2-1e-30 <= nf <= (mp.mpf(n)/(n-r))**2.5+1e-30
        err = nf*mp.e*Ren(r+1)+mp.mpf(d(n, n-r))/mp.mpf(n)**(n-2)
        assert -1e-25 <= err <= mp.e*(5*r-1)/(4*n*(1-mp.mpf(r)/n)**4)+1e-25, (n, r)
        assert abs(mp.mpf(-d(n, n-r))/mp.mpf(n)**(n-2)-mp.e*Ren(r+1)) <= 60*(r+1)/mp.mpf(n)
for D in range(2, 7):
    n = int(mp.ceil(20*mp.mpf(D)**1.5))
    assert all(b(n, n-r-1) > b(n, n-r) for r in range(1, D)), (D, n)
print("moving-tail (가)(다)(마)(사)(아) OK")
for j in range(2, 200):
    S = sum(Ren(g)*Ren(j-g) for g in range(1, j)); S2 = sum(g*Ren(j-g)*Ren(g) for g in range(1, j))
    assert S <= 0.5 and S2 <= j/4
for r in range(0, 200):
    v = mp.e*Ren(r+1); assert v <= 1
    if r >= 1: assert v >= mp.e**(-0.5)*r**-0.5 > 1/(2*mp.sqrt(r+1))
print("moving-tail (라)(바) OK")
z12 = mp.zeta(0.5); zm12 = mp.zeta(-0.5); z32 = mp.zeta(1.5)
print("zeta:", z12, zm12, z32)
cPsi = -z12+z32/12; print("c_Psi=", cPsi, "(1.5,1.6781)?", 1.5 < cPsi < 1.6781)
def Psi(q): return sum(Ren(j) for j in range(1, q+1))
for q in range(1, 400):
    assert Psi(q) <= (2*mp.pi)**-0.5*(2*mp.sqrt(q)-1) <= 0.7979*mp.sqrt(q)
    low = (2*mp.pi)**-0.5*(2*mp.sqrt(q)-cPsi+1/(2*mp.sqrt(q))-mp.mpf(q)**-1.5/24)
    assert Psi(q) >= low >= 0.3989*(2*mp.sqrt(q)-1.678) >= 0.7978*mp.sqrt(q)-0.8848
    S = sum(mp.mpf(j)**-0.5 for j in range(1, q+1))
    assert 2*mp.sqrt(q)+z12+0.5/mp.sqrt(q)-mp.mpf(q)**-1.5/24 <= S <= 2*mp.sqrt(q)+z12+0.5/mp.sqrt(q)
    S2 = sum(mp.sqrt(j) for j in range(1, q+1))
    assert mp.mpf(2)/3*mp.mpf(q)**1.5+0.5*mp.sqrt(q)+zm12 <= S2 <= mp.mpf(2)/3*mp.mpf(q)**1.5+0.5*mp.sqrt(q)+zm12+mp.mpf(q)**-0.5/24
    tail = 1-sum(Borf(m) for m in range(1, q+1))
    assert 2*(2*mp.pi)**-0.5*mp.e**(-1/(12*(q+1)))*(q+1)**-0.5 <= tail <= 2*(2*mp.pi)**-0.5*(q+0.5)**-0.5 <= mp.sqrt(2/mp.pi)*q**-0.5
print("power-sum·borel-arithmetic OK (q<400)")
for y in range(1, 25):
    for n in range(y+1, 2*y+30):
        q = n-y
        lhs = 1-s(n, y); rhs = (mp.mpf(n+1)/(y+1))**1.5/(y+1)*sum(Psi(i) for i in range(1, q+1))
        rhs2 = (2*mp.pi)**-0.5*(mp.mpf(n+1)/(y+1))**1.5/(y+1)*(mp.mpf(4)/3*mp.mpf(q)**1.5+mp.sqrt(q)-q-mp.mpf(1)/3)
        assert float(lhs) <= rhs+1e-20 <= rhs2+1e-20, (y, n)
print("union-bound-closed OK")
for y in range(2, 30):
    for q in range(1, y+3):
        phi1 = 1-sum(Borf(j)*mp.mpf(q-j)/(y+q-j) for j in range(1, q))
        assert float(s(y+q-1, y)) <= phi1+1e-25
print("supersolution OK")
h = [1, 2, 3, 4, 1, 6, 7]
Al = [prod(min(x, l+1) for x in h) for l in range(7)]
print("2.5:", Al, [Al[0]]+[Al[l]-Al[l-1] for l in range(1, 7)])
print("e(20/19)^4=", mp.e*(mp.mpf(20)/19)**4, " 2(2pi)^-1/2=", 2*(2*mp.pi)**-0.5, " 0.3989*1.678=", 0.3989*1.678)
