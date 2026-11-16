# T1: 2.9-2.12 표현 수치 검산 (정확 유리수): 2-13, 2-31, 2-34, 2-36/37, 2-38, 2-39, b-top, 2-40, 2-41, chain-expansion(가), moving-tail
from fractions import Fraction as Fr
from math import comb, factorial, exp, cosh, sqrt, e as E, pi as PI
import itertools
A = {}
def Ac(n, l):
    if l < 0: return 0
    if n == 0: return 1
    if (n, l) in A: return A[(n, l)]
    s = sum(comb(n-1, j)*min(j+1, l+1)*Ac(j, l)*Ac(n-1-j, l) for j in range(n)); A[(n, l)] = s; return s
def p(n): return (n+1)**(n-1) if n > 0 else 1
def b(n, l): return Ac(n, l)-Ac(n, l-1)
def d(n, k): return b(n, k)-b(n, k-1)
def s(m, y): return Fr(Ac(m, y-1), p(m)) if y >= 1 else Fr(0)
def c(m, Y): return Fr(b(m, Y), p(m))
def N(l, t): return min(t, l+1)*Ac(t-1, l)
def pi0(n, y):
    F = [1]+[0]*n
    for m in range(1, n+1):
        F[m] = sum(comb(m-1, t-1)*t**(t-1)*F[m-t] for t in range(1, min(y, m)+1))
    return Fr(F[n], p(n))
ok = True
for l in range(0, 5):
    for n in range(1, 2*l+4):
        y = l+1
        rhs = p(n)*pi0(n, y)+sum(comb(n, m)*(l+1)*Ac(m-1, l)*p(n-m) for m in range(l+2, n+1))
        if rhs != Ac(n, l): ok = False; print("2-13 fail", n, l)
print("2-13 ok", ok)
ok = True
for m in range(0, 12):
    for y in range(1, 14):
        if not (s(m+1, y) <= s(m, y) and s(m, y) <= s(m+1, y+1)): ok = False; print("2-31 fail", m, y)
print("2-31 ok", ok)
ok = True
for Y in range(1, 8):
    for K in range(Y+1, 14):
        if sum(c(m, Y) for m in range(Y+1, K+1)) < 1-s(K, Y): ok = False
        for m in range(Y+1, K+1):
            if c(m, Y) < s(m-1, Y)-s(m, Y): ok = False
print("2-34 ok", ok)
print("b-top ok", all(b(k, k-1) == k**(k-2) for k in range(2, 12)))
def trees(t):
    for root in range(t):
        others = [v for v in range(t) if v != root]
        for par in itertools.product(range(t), repeat=t-1):
            P = {v: par[i] for i, v in enumerate(others)}
            okk = True
            for v in others:
                seen = set(); u = v
                while u != root:
                    if u in seen: okk = False; break
                    seen.add(u); u = P[u]
                if not okk: break
            if okk: yield root, P
def subtree_sizes(t, root, P):
    ch = {v: [] for v in range(t)}
    for v, pa in P.items(): ch[pa].append(v)
    sz = {}
    def rec(v):
        sz[v] = 1+sum(rec(w) for w in ch[v]); return sz[v]
    rec(root); return sz
for t in range(1, 6):
    cnt = 0; H = {k: 0 for k in range(1, t+1)}
    for root, P in trees(t):
        cnt += 1; sz = subtree_sizes(t, root, P)
        for k in range(1, t+1): H[k] += sum(1 for v in sz if sz[v] == k)
    assert cnt == t**(t-1)
    ok = all(Fr(H[k], cnt) == (Fr(comb(t, k)*k**(k-1)*(t-k)**(t-k), t**(t-1)) if t > k else Fr(1)) for k in range(1, t+1))
    print("2-36 t=", t, "ok", ok)
from math import lgamma, log
def Ren(j): return exp(j*log(j)-j-lgamma(j+1)) if j > 0 else 1.0
def Borf(m): return exp(-m+(m-1)*log(m)-lgamma(m+1))
def Psi(q): return sum(Ren(j) for j in range(1, q+1))
ok = all(abs(sum(Borf(m)*Psi(q-m) for m in range(1, q+1)) - (Psi(q)-sum(Borf(m) for m in range(1, q+1)))) < 1e-12 for q in range(1, 30))
print("2-37(다) ok", ok)
def theta(t, k): return comb(t, k)*k**(k-1)*(t-k)**(t-k)/t**(t-1) if t > k else 1.0
ok = all(abs(theta(t, k)-Ren(t-k)*Borf(k)/Borf(t)) < 1e-9*theta(t, k) for k in range(1, 15) for t in range(k, 40))
print("2-37(마) ok", ok)
print("2-37(라) ok", all(Ren(j) <= (2*PI*j)**-0.5 for j in range(1, 200)) and all(Psi(q) <= 0.7979*sqrt(q) for q in range(1, 200)))
def xt(t, k): return Fr(N(k, t)-2*N(k-1, t)+N(k-2, t), t**(t-1))
ok2 = ok3 = ok4 = True
for k in range(2, 10):
    for t in range(k, 3*k+1):
        th = Fr(comb(t, k)*k**(k-1)*(t-k)**(t-k), t**(t-1)) if t > k else Fr(1)
        if k*xt(t, k) < -th: ok2 = False; print("(ii) fail", t, k)
        if t <= 2*k:
            q = t-k
            if float(k*xt(t, k)) > float(-th)+(2*q*q+q)*cosh(q/k)/k+1e-12: ok3 = False; print("(iii) fail", t, k)
            if not (Ren(q)-1e-12 <= float(th) <= Ren(q)*(1+q/k)**1.5+1e-12): ok4 = False; print("(iv) fail", t, k)
    for q in range(0, 2*k+1):
        Pq = sum(xt(tt, k) for tt in range(k, k+q+1))
        if float(k*Pq) < -(1+q/k)**1.5*(1+Psi(q))-1e-12: print("2-39(d) fail", k, q)
print("2-38 ok", ok2, ok3, ok4)
for k in range(2, 8):
    assert xt(k, k) == Fr(-1, k)
    for t in range(k, 3*k):
        bT_k = N(k, t)-N(k-1, t); bT_km1 = N(k-1, t)-N(k-2, t)
        assert bT_k-bT_km1 == xt(t, k)*t**(t-1)
        if t >= k+1: assert bT_k-bT_km1 == (k+1)*b(t-1, k)-(k-1)*b(t-1, k-1) == k*d(t-1, k)+b(t-1, k)+b(t-1, k-1)
print("delta_t ok")
def egf_coeffs(l, nmax): return [0]+[N(l, t)-N(l-1, t) for t in range(1, nmax+1)]
ok = True
for k in range(2, 7):
    for n in range(2*k+1, 3*k):
        Theta = comb(n, k)*k**(k-2)*Ac(n-k, k-1)
        FL = sum(comb(n, t)*(N(k, t)-2*N(k-1, t)+N(k-2, t))*Ac(n-t, k-1) for t in range(k+1, 2*k+2))
        BV = sum(comb(n, m+1)*p(n-1-m)*(b(m, k)+b(m, k-1)) for m in range(2*k+1, n))
        KD = sum(comb(n, m+1)*p(n-1-m)*k*d(m, k) for m in range(2*k+1, n))
        bk = egf_coeffs(k, n); bk1 = egf_coeffs(k-1, n)
        PAIR = Fr(0)
        for t1 in range(1, n+1):
            for t2 in range(1, n+1-t1):
                PAIR += Fr(factorial(n), factorial(t1)*factorial(t2)*factorial(n-t1-t2))*(bk[t1]*bk[t2]+bk1[t1]*bk1[t2])*p(n-t1-t2)
        PAIR /= 2
        if d(n, k) != -Theta+FL+BV+KD+PAIR: ok = False; print("2-40 fail", n, k, d(n, k), -Theta+FL+BV+KD+PAIR)
        Acoef = [Fr(Ac(m, k-1), factorial(m)) for m in range(n+1)]
        def sq(bs):
            r = [Fr(0)]*(n+1)
            for i in range(n+1):
                for j in range(n+1-i): r[i+j] += Fr(bs[i], factorial(i))*Fr(bs[j], factorial(j))
            return r
        S = sq(bk); S1 = sq(bk1)
        PAIRdef = Fr(factorial(n), 2)*sum(Acoef[m]*(S[n-m]+S1[n-m]) for m in range(n+1))
        if PAIRdef != PAIR: ok = False; print("2-41 fail", n, k)
print("2-40/2-41 ok", ok)
for n in range(1, 6):
    tot = {t: 0 for t in range(1, n+1)}; cnt = 0
    for root, P in trees(n+1):
        if root != 0: continue
        cnt += 1; sz = subtree_sizes(n+1, 0, P)
        for t in range(1, n+1): tot[t] += sum(1 for v in sz if v != 0 and sz[v] == t)
    assert cnt == p(n)
    print("chain-exp(가) n=", n, all(Fr(tot[t], cnt) == Fr(comb(n, t)*t**(t-1)*(n+1-t)**(n-t), p(n)) for t in range(1, n+1)))
def Q1(n, r): return comb(n, r)*(n-r)**(n-r-2)*(r+1)**r
def W2(n, g1, g2):
    t1 = n+1-g1; t2 = t1-g2
    return Fr(factorial(n)*t2**(t2-1)*g1**(g1-1)*g2**g2, factorial(g1-1)*factorial(g2)*factorial(t2))
def Q2(n, r):
    tot = Fr(0)
    for g1 in range(1, r+1):
        for g2 in range(1, r+2-g1):
            t1 = n+1-g1; t2 = t1-g2
            if g1+g2 <= r: tot += 2*W2(n, g1, g2)/(t1*t2)
            else: tot += (g2+1)*W2(n, g1, g2)/(t1*t2)
    return tot
def nf(n, dd): return exp(dd)*factorial(n)/factorial(n-dd)*(n-dd)**(n-dd-2)/n**(n-2)
ok = True
for n in range(3, 26):
    for r in range(1, (n-1)//2+1):
        lhs = b(n, n-r-1)-b(n, n-r)
        if not (Q1(n, r)-Q2(n, r) <= lhs <= Q1(n, r)): ok = False; print("(가) fail", n, r)
        val = nf(n, r)*E*Ren(r+1)+d(n, n-r)/n**(n-2)
        if not (-1e-9 <= val <= E*(5*r-1)/(4*n*(1-r/n)**4)+1e-9): ok = False; print("(마) fail", n, r, val)
        if abs(-d(n, n-r)/n**(n-2)-E*Ren(r+1)) > 60*(r+1)/n: ok = False; print("(사) fail", n, r)
        if not ((n/(n-r))**2-1e-9 <= nf(n, r) <= (n/(n-r))**3+1e-9): ok = False; print("(다) fail")
        if abs(Q1(n, r)/n**(n-2)-nf(n, r)*E*Ren(r+1)) > 1e-9*Q1(n, r)/n**(n-2): ok = False; print("(라) fail", n, r)
print("moving-tail (가)(다)(라)(마)(사) ok", ok)
for D in (2, 3):
    nmin = int(20*D**1.5)+1
    print("(아) D=", D, "n_min", nmin, all(all(b(n, n-r-1) > b(n, n-r) for r in range(1, D)) for n in range(nmin, nmin+3)))
