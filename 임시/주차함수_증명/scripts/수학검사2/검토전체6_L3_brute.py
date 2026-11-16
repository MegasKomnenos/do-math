# 검토전체6 L3: 5A의 식들을 작은 n에서 전수 대조한다.
# 결과 순열·용량 h_i를 주차함수 전수에서 구해 K_{n,k}(y), B, E, b, A를 만들고
# green-connection (다)(라), source-rep (가)(나)(다), 2-28, fixed-size-response (다),
# inverse-renewal 재귀, hb_d 계수, Cayley 비 값, 개수들을 확인한다.
from fractions import Fraction as Fr
from itertools import product
from math import comb, factorial, exp, log, sqrt, pi

def park(pref):
    n = len(pref); spots = [0]*n
    out = []
    for car, a in enumerate(pref, 1):
        i = a
        while i <= n and spots[i-1]: i += 1
        if i > n: return None
        spots[i-1] = car; out.append((car, i))
    return spots  # spots[i-1] = car number

def caps(sigma):
    n = len(sigma); h = []
    for i in range(1, n+1):
        j = i-1
        while j >= 1 and sigma[j-1] < sigma[i-1]: j -= 1
        h.append(i - j)  # j=0 -> h=i
    return h

def pdat(n):
    """returns list of (h tuple, disp tuple) per PF"""
    data = []
    for pref in product(range(1, n+1), repeat=n):
        sp = park(pref)
        if sp is None: continue
        h = caps(sp)
        disp = [0]*n
        for pos, car in enumerate(sp, 1):
            disp[pos-1] = pos - pref[car-1]
        data.append((tuple(h), tuple(disp)))
    return data

def p(n): return (n+1)**(n-1) if n >= 1 else 1

def Gamma(d, y, n):
    G = [Fr(1)]
    for dd in range(1, d+1):
        s = Fr(comb(n, dd)*p(dd))
        s += y*sum(Fr(comb(n-dd+j, j)*p(j))*G[dd-1-j] for j in range(dd))
        G.append(s)
    return G[d]

def phi_list(k, N):
    # EGF exp(sum_{t<=k} t^{t-1} x^t/t!) coefficients * m!
    tree = [Fr(0)]*(N+1)
    for t in range(1, min(k, N)+1): tree[t] = Fr(t**(t-1), factorial(t))
    F = [Fr(0)]*(N+1); F[0] = Fr(1)
    # F' = tree' F
    for m in range(1, N+1):
        F[m] = sum(Fr(j)*tree[j]*F[m-j] for j in range(1, m+1))/m
    return [F[m]*factorial(m) for m in range(N+1)]

ok = True
def chk(cond, msg):
    global ok
    if not cond:
        ok = False; print("FAIL:", msg)

NMAX = 7
cache = {}
for n in range(1, NMAX+1):
    cache[n] = pdat(n)
    chk(len(cache[n]) == p(n), f"p({n})")

def A(n, l):
    if n == 0: return 1
    if l < 0: return 0
    return sum(1 for h, d in cache[n] if max(d) <= l)
def b(n, l): return A(n, l) - A(n, l-1)
hcount = {}
def Kpoly(n, k, y):
    if n not in hcount:
        cnt = {}
        for h, d in cache[n]: cnt[h] = cnt.get(h, 0) + 1
        hcount[n] = cnt
    s = Fr(0)
    for h, c in hcount[n].items():
        fib = 1
        for hi in h: fib *= hi
        assert c % fib == 0
        pr = Fr(1)
        for hi in h: pr *= hi if hi <= k else y
        s += (c//fib)*pr   # 결과 순열마다 한 번씩(섬유 크기 prod h_i로 나눔)
    return s
def Kperm(n, k, y):
    seen = {}
    for h, d in cache[n]: seen[h] = seen.get(h, 0) + 1
    s = Fr(0)
    for h, cnt in seen.items():
        fib = 1
        for hi in h: fib *= hi
        pr = Fr(1)
        for hi in h: pr *= hi if hi <= k else y
        s += Fr(cnt, fib)*pr
    return s
def Bcount(n, k):  # B_{n,k-1}
    c = 0
    for h, d in cache[n]:
        if max(d) != k-1: continue
        if all(h[i] == k for i in range(n) if d[i] == k-1): c += 1
    return c
def Ecount(n, k):
    c = 0
    for h, d in cache[n]:
        if max(d) != k: continue
        m = sum(1 for x in d if x == k)
        if m % 2 == 0: c += 1
    return c
def E2count(n, k):
    return sum(1 for h, d in cache[n] if max(d) == k and sum(1 for x in d if x == k) == 2)

import sys
for n in range(1, NMAX+1):
    print("n =", n, flush=True)
    for k in range(1, n+1):
        # 2-28, 2-29
        d = A(n,k)-2*A(n,k-1)+A(n,k-2)
        chk(d == 2*Ecount(n,k)-Bcount(n,k), f"2-28 n={n} k={k}")
        chk(2*E2count(n,k)-Bcount(n,k) <= d, f"2-29 n={n} k={k}")
        # 2-4: K(k+1)=A_{n,k}, K(k)=A_{n,k-1}
        chk(Kpoly(n,k,k+1) == A(n,k) and Kpoly(n,k,k) == A(n,k-1), f"2-4 n={n} k={k}")
        chk(Kpoly(n,k,k-1) == A(n,k-2)+Bcount(n,k), f"K(k-1)=A+B n={n} k={k}")
        # green (다)
        if k+1 <= n <= 2*k+1:
            for y in [Fr(0), Fr(1), Fr(3,2), Fr(k+2), Fr(7)]:
                lhs = Kpoly(n,k,y)-Kpoly(n,k+1,y)
                chk(lhs == (y-k-1)*p(k)*Gamma(n-k-1, y, n), f"green(다) n={n} k={k} y={y}")
        if k <= n <= 2*k-1:
            chk(Bcount(n,k) == p(k-1)*Gamma(n-k, Fr(k-1), n), f"Gamma^-=B n={n} k={k}")
        # green (라)
        l = k
        if l+1 <= n <= 2*l+1:
            s = sum(A(m,l)*Gamma(n-m-1, Fr(l), n) for m in range(l, n))
            chk(s == b(n,l), f"green(라) n={n} l={l}")
        # source-rep (가)(나)
        if n <= 2*k+1:
            phi = phi_list(k, n)
            for y in [Fr(0), Fr(2), Fr(k), Fr(k+1), Fr(k-1), Fr(k+2)]:
                rhs = phi[n] + y*sum(phi[m]*Gamma(n-m-1, y, n) for m in range(k, n))
                chk(Kpoly(n,k,y) == rhs, f"source-rep(가) n={n} k={k} y={y}")
            hg = lambda dd, y: y*Gamma(dd, y, n)
            sd = lambda dd, y: hg(dd,y+1)-2*hg(dd,y)+hg(dd,y-1)
            chk(2*Ecount(n,k) == sum(phi[m]*sd(n-m-1, Fr(k)) for m in range(k, n)), f"source-rep(나)1 n={n} k={k}")
            c3 = Kpoly(n,k,k+2)-3*Kpoly(n,k,k+1)+3*Kpoly(n,k,k)-Kpoly(n,k,k-1)
            chk(2*Ecount(n,k)+c3 == sum(phi[m]*sd(n-m-1, Fr(k+1)) for m in range(k, n)), f"source-rep(나)2 n={n} k={k}")
            chk(c3 >= 0, f"c>=0 n={n} k={k}")
        # source-rep (다) S formula
        if k+2 <= n <= 2*k-1:
            r = n-k
            Gp = p(k)*Gamma(r-1, Fr(k+2), n); Gm = p(k-1)*Gamma(r, Fr(k-1), n)
            dk = A(n,k)-2*A(n,k-1)+A(n,k-2); dk1 = A(n,k+1)-2*A(n,k)+A(n,k-1)
            S = Gp*dk - Gm*dk1
            phi = phi_list(k, n)
            hg = lambda dd, y: y*Gamma(dd, y, n)
            sd = lambda dd, y: hg(dd,y+1)-2*hg(dd,y)+hg(dd,y-1)
            S2 = sum(phi[n-dd-1]*(Gp*sd(dd,Fr(k))-Gm*sd(dd,Fr(k+1))) for dd in range(1, r))
            chk(S == S2, f"source-rep(다) n={n} k={k}")
            chk(Gp == Kpoly(n,k,k+2)-A(n,k+1), f"Gamma^+ n={n} k={k}")
        # fixed-size-response (다): (n)_m fs_m = Gamma_m(k;n), k<=n<=2k
        if k <= n <= 2*k:
            a = [Fr(A(j,k-1), factorial(j)) for j in range(n+1)]
            fs = [Fr(1)]
            for m in range(1, n-k+1):
                fs.append(a[m] + k*sum(a[m-1-i]*fs[i]/(n-i) for i in range(m)))
            for m in range(n-k+1):
                chk(Fr(factorial(n), factorial(n-m))*fs[m] == Gamma(m, Fr(k), n), f"fixed-size(다) n={n} k={k} m={m}")

# inverse-renewal recurrence and hb_d coefficients
def tw(j): return Fr(1) if j == 1 else Fr((j-1)**(j-1), factorial(j))
for n in range(2, 9):
    for y in [Fr(1), Fr(5,2)]:
        fs = [Gamma(d, y, n)/Fr(factorial(n), factorial(n-d)) for d in range(n)]
        for d in range(1, n):
            rhs = (1+y/(n-d+1))*fs[d-1] + sum(tw(j)*fs[d-j] for j in range(2, d+1))
            chk(fs[d] == rhs, f"inverse-renewal n={n} y={y} d={d}")
# hb_d via recurrence with rho symbolic -> evaluate polynomial coefficients
def hb_coeffs(d):
    # returns list of coefficient lists in rho
    polys = [[Fr(1)]]
    for dd in range(1, d+1):
        new = [Fr(0)]*(dd+1)
        prev = polys[dd-1]
        for i, c in enumerate(prev):
            new[i] += c; new[i+1] += c
        for j in range(2, dd+1):
            for i, c in enumerate(polys[dd-j]): new[i] += tw(j)*c
        polys.append(new)
    return polys[d]
for d in range(1, 9):
    co = hb_coeffs(d)
    for j in range(d+1):
        chk(co[j] == Fr((j+1)*(d+1)**(d-j-1), factorial(d-j)) if j < d else co[j] == 1, f"hb coeff d={d} j={j}")
    chk(sum(co) == Fr((d+1)**d, factorial(d)), f"hb_d(1) d={d}")
    # bd tail
    for j in range(d+1):
        tail = sum((Fr((i+1)*(d+1)**(d-i-1), factorial(d-i)) if i < d else Fr(1))/Fr((d+1)**d, factorial(d)) for i in range(j, d+1))
        prodf = Fr(1)
        for i in range(1, j+1): prodf *= Fr(d+1-i, d+1)
        chk(tail == prodf, f"bd tail d={d} j={j}")

# Cayley ratio values k=1..9
vals = []
for k in range(1, 10):
    cr = Fr(k+1, k)**(k-2)
    v = cr*(1+Fr(5, 2*k)+Fr(2, k*k))
    vals.append(float(v)); chk(v > Fr(87, 32), f"cr k={k}")
    chk(Fr(p(k), p(k-1)) == (k+1)*cr, f"p ratio k={k}")
print("cr values:", [round(v, 4) for v in vals])

# counts
c1 = sum((-(-n//2)) - 1 for n in range(10001, 20001)); print("74,995,000 ?", c1)
c2 = sum(n-3 - (-(-(n-1)//2)) + 1 for n in range(5, 20001)); print("99,970,002 ?", c2)
c3 = sum(n-3 - (-(-(n-1)//2)) + 1 for n in range(20001, 50001)); print("524,955,000 ?", c3)
c4 = sum(n-1 - (-(-(n-1)//2)) for n in range(20001, 50001)); print("pairs 524,985,000 ?", c4)
print("14365 ?", sum(r-1 for r in range(2, 171)))

def mfrak(n):
    m = 170
    mm = 171
    while mm**1.5 + 9*mm <= n: m = mm; mm += 1
    return m
print("m(20001)=", mfrak(20001), " m(50001)=", mfrak(50001), " m(20001) check 597/598:", 597**1.5+9*597, 598**1.5+9*598)
for r0 in [832, 833, 965, 966, 2163, 2164]:
    print(r0, r0**1.5)
print("r0 checks:", 20001**(2/3), int(0.75*20001**(2/3)), 27.14**3, (149/200)**3, (16/25)**2, 0.75**3, (13/20)**2)
print("1/(1+9/sqrt(598))=", 1/(1+9/sqrt(598)), " (9/5)^(2/3)=", 1.8**(2/3), " 10/2^(2/3)=", 10/2**(2/3))
print("2*181*32/(128*87)=", 2*181*32/(128*87), "2sqrt2/e=", 2*sqrt(2)/exp(1), " e vs 65/24+1/100:", exp(1), 65/24+0.01, 87/32)
print("log et(1/2) approx:", 0.5*0.25+ (1/36)*0.25**2 + (1/405)*0.25**3)
print("sqrt(3pi/2)=", sqrt(3*pi/2), " sqrt(pi/2)=", sqrt(pi/2), " 1/2+1.690408-sqrt(3pi/2)=", 0.5+1.690408-sqrt(3*pi/2))
print("bracket at s=100:", 1/300+8/30000+2.507/1e4+(1+217.09)/1e6)
print("(1-cos1)=", 1-__import__('math').cos(1))
print("rq_* at S=23:", 0.65*(1+3/529)/23, " 1/12=", 1/12)
print("rq values:", 1.2/sqrt(598), 1.5/sqrt(833), 1.8/sqrt(966), 2.1/sqrt(2164), 2.4/100, 1/16)
print("(12/11)^1.5*(1+1/598)=", (12/11)**1.5*(1+1/598), " 12/(110e)=", 12/(110*exp(1)), 1/24)
print("log10(1.15*598^3)=", log(1.15*598**3, 10), " 598*log10(24)=", 598*log(24, 10))
print("r0 lower: 0.75*736.58=", 0.75*736.58, " n^{-2/3} at 20001:", 20001**(-2/3), 0.75-20001**(-2/3), 149/200)
print("(27/4)/27.14=", 6.75/27.14, " 0.75^1.5=", 0.75**1.5)
print("1.2*20001=", 1.2*20001, " 1.5*20001=", 1.5*20001)
print("5/12*sqrt(598)=", 5/12*sqrt(598))
print("ALL OK" if ok else "SOME FAIL")
