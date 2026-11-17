# R2 검산: 보조정리 4:e-integral (4.1), 명제 4:old-4-6 좌변 = J_n(k-1)/p_n (n<=2k) 를 작은 k에서 전수 열거와 대조
import itertools, sympy as sp
from math import factorial
def park(pref):
    n = len(pref); occ = [0]*(n+2); disp = []; pos = []
    for a in pref:
        p = a
        while p <= n and occ[p]: p += 1
        if p > n: return None
        occ[p] = 1; disp.append(p-a); pos.append(p)
    return disp, pos
def brute(n, k):
    # e_n = 2*E2_{n,k};  J_n(k-1) from permutations; d_{n,k}; B_{n,k-1}
    E2 = 0; b = [0]*(n+1)
    perms = {}
    for pref in itertools.product(range(1, n+1), repeat=n):
        r = park(pref)
        if r is None: continue
        disp, pos = r
        M = max(disp); b[M] += 1
        if M == k and disp.count(M) == 2: E2 += 1
        sigma = [0]*(n+1)
        for car, p in enumerate(pos, 1): sigma[p] = car
        perms[tuple(sigma[1:])] = 1
    J = 0
    for s in perms:
        h = []
        for i in range(1, n+1):
            js = [j for j in range(1, i) if s[j-1] > s[i-1]]
            h.append(i - (max(js) if js else 0))
        H = sum(1 for x in h if x == k); Z = sum(1 for x in h if x > k)
        prod = 1
        for x in h:
            if x < k: prod *= x
        if H: J += H*k**(H-1)*(k-1)**Z*prod
    d = (b[k] if k <= n else 0) - b[k-1]
    return 2*E2, J, d
Y, t = sp.symbols('Y t')
def series_check(k, nmax):
    V = lambda u: (1-u)**2/2
    Z = t*Y
    tail = 1 - sum(sp.exp(-j*Z)*(j*Z)**(j-1)/sp.factorial(j) for j in range(1, k+1))
    Jf = V(Z) - V(Y)
    integrand = (1-Z)**2*tail*sp.exp(k*Jf)*(2*Jf + k*Jf**2)*Y   # dZ = Y dt
    ser = sp.series(integrand, Y, 0, nmax+1).removeO()
    inner = sp.integrate(sp.expand(ser), (t, 0, 1))
    res = {}
    # J side: Bor(k) e^Y e^{-(k-1)V(Y)} int_0^Y (1-Z) Z^{k-1} e^{k(1-Z)+(k-1)V(Z)} dZ
    Bor = sp.exp(-k)*sp.Integer(k)**(k-1)/sp.factorial(k)
    integ2 = (1-Z)*Z**(k-1)*sp.exp(k*(1-Z)+(k-1)*V(Z))*Y
    ser2 = sp.series(integ2, Y, 0, nmax+1).removeO()
    inner2 = sp.integrate(sp.expand(ser2), (t, 0, 1))
    for n in range(1, nmax+1):
        f = sp.series(sp.exp(Y)*inner*(1-Y)*sp.exp(n*Y), Y, 0, n+1).removeO()
        en = sp.nsimplify(sp.simplify(sp.factorial(n)*f.coeff(Y, n)))
        f2 = sp.series(Bor*sp.exp(Y)*sp.exp(-(k-1)*V(Y))*inner2*(1-Y)*sp.exp(n*Y), Y, 0, n+1).removeO()
        jn = sp.simplify(sp.factorial(n)*f2.coeff(Y, n))
        res[n] = (en, jn)
    return res
for k, nmax in ((2, 6), (3, 7)):
    res = series_check(k, nmax)
    for n in range(k, nmax+1):
        e, J, d = brute(n, k)
        print('k=%d n=%d  e_n brute=%d  series=%s | J_n(k-1) brute=%d  series=%s | d_{n,k}=%d  e-J=%d' % (k, n, e, sp.nsimplify(res[n][0]), J, sp.nsimplify(sp.N(res[n][1], 30), rational=False, tolerance=1e-20), d, e-J))
