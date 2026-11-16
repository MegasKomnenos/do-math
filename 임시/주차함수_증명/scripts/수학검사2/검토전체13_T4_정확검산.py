# T4 검산: 5.5절의 항등식·부등식을 작은 n에서 정확 유리수(또는 고정밀)로 다시 센다.
from fractions import Fraction as Fr
from math import comb, floor
import itertools
from mpmath import mp, mpf, sqrt, exp, log, pi, loggamma, findroot
mp.dps = 30

def pf(n): return 1 if n == 0 else ((n+1)**(n-1) if n > 0 else 0)

def brute_A(n):
    # A[l] = 최대 변위가 l 이하인 길이 n 주차함수의 수 (전수)
    cnt = [0]*n
    for a in itertools.product(range(1, n+1), repeat=n):
        spots = [False]*(n+2); M = 0; ok = True
        for pref in a:
            s_ = pref
            while s_ <= n and spots[s_]: s_ += 1
            if s_ > n: ok = False; break
            spots[s_] = True; M = max(M, s_-pref)
        if ok: cnt[M] += 1
    A = []; acc = 0
    for l in range(n): acc += cnt[l]; A.append(acc)
    return A

def pi_n(n, t): return Fr(comb(n, t)*t**(t-1)*pf(n-t), pf(n))

A = {}
def Aval(n, l):
    if l < 0: return 0
    if n <= l+1: return pf(n)
    key = (n, l)
    if key in A: return A[key]
    assert n <= 2*l+3, (n, l)
    pi0 = 1 - sum(pi_n(n, m) for m in range(l+2, n+1))
    val = pf(n)*pi0 + sum(comb(n, m)*(l+1)*Aval(m-1, l)*pf(n-m) for m in range(l+2, n+1))
    assert val.denominator == 1
    A[key] = int(val); return A[key]

for n in range(1, 8):
    B = brute_A(n)
    for l in range(n):
        if n <= 2*l+3: assert B[l] == Aval(n, l), (n, l, B[l], Aval(n, l))
print("2-13 재귀 vs 전수: n<=7 일치")

def s(m, y): return Fr(Aval(m, y-1), pf(m)) if y >= 1 else Fr(0)
def c(m, Y): return s(m, Y+1) - s(m, Y)
def sT(t, Y): return Fr(1) if t <= Y else Fr(Y*Aval(t-1, Y-1), t**(t-1))
def x(t, y): return sT(t, y+1) - 2*sT(t, y) + sT(t, y-1)
def tofl(q): return mpf(q.numerator)/q.denominator

bad = 0
for n in range(3, 36):
    for y in range((n+2)//2, n):
        lhs = c(n, y) - c(n, y-1); rhs = sum(pi_n(n, t)*x(t, y) for t in range(y, n+1))
        if lhs != rhs: bad += 1; print("5-19 불일치", n, y)
        P = sum(x(t, y) for t in range(y, n+1))
        P2 = -Fr(1, y) + sum(((y+1)*c(m, y) - (y-1)*c(m, y-1))/Fr(m+1) for m in range(y, n))
        if P != P2: bad += 1; print("5-27 불일치", n, y)
        if y >= 2 and y+1 <= n <= 2*y+1:
            if y*P < -1 - Fr(y*(y-1))*c(n-1, y-1)/n: bad += 1; print("cor-L 위반", n, y)
print("5-19·5-27·cor-L: n<=35 검사, 위반", bad)
assert all(x(y, y) == Fr(-1, y) for y in range(2, 20))
assert all(x(t, y) == 0 for y in range(2, 12) for t in range(1, y))
print("x_y(y)=-1/y, x_t(y)=0 (t<y) 확인")

bad = 0
for m in range(2, 40):
    for d in range(1, m//2+1):
        w = m - d
        z = exp(mpf(d-1)/w)/(w+1) + mpf(3*d)/(2*(w+1)*(m+1))
        if tofl(c(m+1, w+1)) < (1-z)*tofl(c(m, w)) - mpf(10)**-25: bad += 1; print("5-28 위반", m, d)
print("5-28: m<=39 검사, 위반", bad)

def t0(y):
    t = y + 2
    while not (y <= (t-1) - floor(0.75*(t-1)**(2/3))): t += 1
    return t
bad = 0; checked = 0
for n in range(20, 46):
    for y in range((n+2)//2, n):
        T0 = t0(y)
        if T0 > n: continue
        if not all(c(m, y) >= c(m, y-1) for m in range(T0-1, n)): continue
        checked += 1
        P = sum(x(t, y) for t in range(y, n+1))
        WIN = sum((pi_n(n, t) - pi_n(n, y))*max(-x(t, y), 0) for t in range(y+1, T0))
        POS = sum((pi_n(n, m+1) - pi_n(n, T0-1))*(c(m, y) + c(m, y-1))/Fr(m+1) for m in range(T0-1, n))
        if c(n, y) - c(n, y-1) < pi_n(n, y)*P - WIN + POS: bad += 1; print("5-22 위반", n, y)
print(f"5-22: {checked}개 위치 검사, 위반 {bad}")

def trees(t):
    if t == 1: yield {0: None}; return
    if t == 2:
        for root in (0, 1): yield {root: None, 1-root: root}
        return
    for seq in itertools.product(range(t), repeat=t-2):
        deg = [1]*t
        for v in seq: deg[v] += 1
        edges = []
        for v in seq:
            for u in range(t):
                if deg[u] == 1:
                    edges.append((u, v)); deg[u] -= 1; deg[v] -= 1; break
        u, v = [i for i in range(t) if deg[i] == 1]; edges.append((u, v))
        adj = {i: [] for i in range(t)}
        for a_, b_ in edges: adj[a_].append(b_); adj[b_].append(a_)
        for root in range(t):
            par = {root: None}; st = [root]
            while st:
                a_ = st.pop()
                for b_ in adj[a_]:
                    if b_ not in par: par[b_] = a_; st.append(b_)
            yield par

bad = 0
for t in range(2, 8):
    cnt = {}; total = 0
    for par in trees(t):
        total += 1
        ch = {i: [] for i in par}
        for v, p in par.items():
            if p is not None: ch[p].append(v)
        size = {}
        def sz(v):
            size[v] = 1 + sum(sz(u) for u in ch[v]); return size[v]
        root = [v for v, p in par.items() if p is None][0]; sz(root)
        v = root; chain = [size[v]]
        while ch[v]:
            v = max(ch[v], key=lambda u: size[u]); chain.append(size[v])
        for sv in set(chain): cnt[sv] = cnt.get(sv, 0) + 1
    assert total == t**(t-1)
    for sv in range(t//2+1, t):
        exact = Fr(cnt.get(sv, 0), total)
        formula = Fr(comb(t, sv)*sv**(sv-1)*(t-sv)**(t-sv), t**(t-1))
        if exact != formula: bad += 1; print("5-24 불일치", t, sv, exact, formula)
print("5-24 방문 확률: t<=7 전수, 위반", bad)

def Bor(m): return exp(-m + (m-1)*log(m) - loggamma(m+1))
def Ren(j): return j*Bor(j)
bad = 0
for t in range(3, 40):
    for y in range(t//2+1, t):
        neg = tofl(max(-x(t, y), Fr(0)))
        if neg > Ren(t-y)*Bor(y)/(y*Bor(t)) + mpf(10)**-25: bad += 1; print("5-25 위반", t, y)
print("5-25: t<=39 검사, 위반", bad)

def BT(z, D): return mpf(z)/D*exp(-D + (D-z)*log(D) - loggamma(D-z+1)) if D >= z else mpf(0)
def pi0(n, y): return 1 - sum(tofl(pi_n(n, m)) for m in range(y+1, n+1))
bad = 0
for Y in range(1, 16):
    for q in range(1, Y+2):
        Lc = mpf(0)
        for z in range(1, q+1):
            for D in range(z, q+1):
                Lc += z*BT(z, D)*Bor(Y+q+1-D)/Bor(Y+q+1)*pi0(Y+q-D, Y)*exp(-(z*(q+1) - mpf(D*(z+1))/2)/Y)
        Lc /= Y
        if tofl(c(Y+q, Y)) < Lc - mpf(10)**-25: bad += 1; print("5-31 위반", Y, q)
print("5-31: Y<=15 검사, 위반", bad)

bad = 0
for z in range(1, 12):
    for D in range(z+1, 80):
        W = D - z
        if BT(z, D) > z/sqrt(2*pi)/D/sqrt(W)*exp(-mpf(z*z)/(2*W) + mpf(z**3)/(3*W*W)) + mpf(10)**-25: bad += 1
print("bt-tail(가): 위반", bad)

bad = 0
for chi in range(2, 60):
    for z in range(1, 40):
        P_le = sum(BT(z, D) for D in range(z, chi))
        b1 = max(1 - 2/sqrt(pi)*mpf(z)**1.5/sqrt(chi-1), 0)
        if P_le < b1 - mpf(10)**-20: bad += 1; print("hover-tail 첫째 위반", chi, z)
        if chi >= 4:
            hv = mpf(chi)**-0.5*(2/sqrt(pi)*(1 + mpf(1)/chi) + 1/sqrt(pi))
            if 1 - P_le > z*hv + mpf(10)**-20: bad += 1; print("hover-tail 둘째 위반", chi, z)
print("hover-tail: 위반", bad)

bad = 0
for k in range(1, 400):
    s_ = mpf(k)/1000
    u = findroot(lambda u: -u - log(1-u) - s_, mpf(0.5))
    if not (sqrt(2*s_) - mpf(2)/3*s_ - mpf(10)**-20 <= u <= sqrt(2*s_) + mpf(10)**-20): bad += 1; print("borel-gf(다) 위반", s_, u)
print("borel-gf(다): 위반", bad)

Y = 25000
bad = 0
for j in [1, 2, 5, 10, 50, 100, 500, 1000, 2000, 4000, 6250]:
    Uj = Y + j + 1
    p0 = 1 - sum(Bor(i)*Bor(Uj-i)/Bor(Uj) for i in range(1, j+1))
    Pb = 1 - sum(Bor(i) for i in range(1, j+1))
    if p0 > Pb + mpf(10)**-20 or p0 < Pb - mpf('1.6')*sqrt(j)/Y - mpf(10)**-20: bad += 1; print("stop-lower 위반", j, p0, Pb)
print("stop-lower (Y=25000, 표본 j): 위반", bad)
