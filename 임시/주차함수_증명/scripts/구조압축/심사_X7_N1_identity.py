# -*- coding: utf-8 -*-
# 심사 X7 — N1 검산: regen_n - A_{n,k-1}(star)(n) = sum_m L_{n,m} d_{m,k}, L>=0  (정확 유리수)
# 아울러 9장·10장이 같은 양을 다른 이름으로 세운 자리의 항등식을 함께 확인한다.
#   (a) w-weight: frak w_n(m+1) = n A_{n,k-1} w_m       (S9)
#   (b) Theta_n / A_{n,k-1} = (n/k) w_N s_N(k)
#   (c) FL_n / A_{n,k-1} = sum_{m=k}^{2k} (n/(m+1)) w_m p_m   (p_m = (k+1)c_m(k)-(k-1)c_m(k-1))
#   (d) (7.25) A(star) = d - KD'  via src+inh from the root-position law (independent computation)
#   (e) regen_n = FL - Theta + BV + PAIR  and  Pcor-free comparison of FL vs sum w_m f_m
from fractions import Fraction as Fr
from math import comb
import sys

NMAX = 34

def parking_counts(NMAX):
    # p_m = (m+1)^{m-1};  A[m][l] = # parking functions of size m with max displacement <= l
    # last-car recursion (2:old-2-6): A_{m,l} = sum_j C(m-1,j-1) min(j,l+1) A_{j-1,l} A_{m-j,l}
    A = [[0]*(NMAX+2) for _ in range(NMAX+1)]
    for l in range(NMAX+2):
        A[0][l] = 1
    for m in range(1, NMAX+1):
        for l in range(NMAX+2):
            s = 0
            for j in range(1, m+1):
                s += comb(m-1, j-1)*min(j, l+1)*A[j-1][l]*A[m-j][l]
            A[m][l] = s
    return A

A = parking_counts(NMAX)
def p(m): return (m+1)**(m-1) if m >= 1 else 1
# sanity: A[m][m-1] = p_m
for m in range(1, NMAX+1):
    assert A[m][m-1] == p(m), m

def b(m, l):  # exactly displacement l
    if l < 0: return 0
    return A[m][l] - (A[m][l-1] if l >= 1 else 0)

def check(n, k):
    Ak = lambda t: A[t][k-1]          # A_{t,k-1}
    d = lambda m: A[m][k] - 2*A[m][k-1] + A[m][k-2]   # d_{m,k}
    # --- regen_n with component kernel Kr(n,m) = k C(n,m+1) A_{n-m-1,k-1}
    KD = sum(k*comb(n, m+1)*Ak(n-m-1)*d(m) for m in range(2*k+1, n))
    regen = d(n) - KD
    # --- (star)(n) from the root-position law (7:old-6-14 / 7:old-6-15), as Fractions
    An = Ak(n)
    def P(j):  # root-position law
        return Fr(min(j, k)*comb(n-1, j-1)*Ak(j-1)*Ak(n-j), An)
    def clp(t): return Fr(b(t, k), Ak(t)) if t >= 1 else Fr(0)
    def clm(t): return Fr(b(t, k-1), Ak(t)) if t >= 1 else Fr(0)
    def mu(t): return Fr(d(t), Ak(t)) if t >= 1 else Fr(0)
    src = Fr(0); inh = Fr(0)
    for j in range(1, n+1):
        L, R = j-1, n-j
        chi = Fr(0)
        if j == k:
            chi += Fr(-1, k)*(1 - clm(R))
        if j > k:
            chi += Fr(1, k)*(clp(L)+clm(L)+clp(R)+clm(R))
        chi += (1 + Fr(1 if j > k else 0, k))*clp(L)*clp(R) + (1 - Fr(1 if j > k else 0, k))*clm(L)*clm(R)
        src += P(j)*chi
        inh += P(j)*((mu(L) if k <= L <= 2*k else 0) + (mu(R) if k <= R <= 2*k else 0))
    star = src + inh
    # --- KD'_n = sum_{m>2k} (k+n-m) C(n-1,m) p_{n-1-m} d_m   (7:old-6-21)
    KDp = sum((k+n-m)*comb(n-1, m)*p(n-1-m)*d(m) for m in range(2*k+1, n))
    ok725 = (An*star == d(n) - KDp)
    # --- F3's L_{n,m}
    Lsum = sum((1 + (n-m-1)*(1 - Fr(k, m+1)))*comb(n-1, m)*Ak(n-m-1)*d(m) for m in range(2*k+1, n))
    Lpos = all((1 + (n-m-1)*(1 - Fr(k, m+1))) > 0 for m in range(2*k+1, n))
    okN1 = (Fr(regen) - An*star == Lsum)
    # --- (a) weights
    w = {m: Fr(comb(n-1, m)*p(m)*Ak(n-1-m), An) for m in range(k, n)}
    frakw = {t: comb(n, t)*t**(t-1)*Ak(n-t) for t in range(k, n+1)}
    oka = all(frakw[m+1] == n*An*w[m] for m in range(k, n))
    # --- (b) Theta
    N = n-k
    Theta = comb(n, k)*k**(k-2)*Ak(N)
    sN = Fr(Ak(N), p(N))
    okb = (Fr(Theta, An) == Fr(n, k)*w[N]*sN)
    # --- (c) FL
    def c(m, l): return Fr(b(m, l), p(m))
    pp = {m: (k+1)*c(m, k) - (k-1)*c(m, k-1) for m in range(k, 2*k+1)}
    delta = {t: b_T(t, k) - b_T(t, k-1) for t in range(k+1, 2*k+2)}
    FL = sum(comb(n, t)*delta[t]*Ak(n-t) for t in range(k+1, 2*k+2))
    okc = (Fr(FL, An) == sum(Fr(n, m+1)*w[m]*pp[m] for m in range(k, 2*k+1)))
    # --- (e) ledger first sum vs FL/A
    f = {}
    for m in range(k, 2*k+1):
        if m <= N: f[m] = 2*pp[m]
        else:      f[m] = (k+n-m+1)*c(m, k) - (k+n-m-1)*c(m, k-1)
    ledger1 = sum(w[m]*f[m] for m in range(k, 2*k+1))
    # Theta vs u_n
    u = w[N]*Fr(A[N][k], p(N))
    return dict(ok725=ok725, okN1=okN1, Lpos=Lpos, oka=oka, okb=okb, okc=okc,
                FL_over_A=float(Fr(FL, An)), ledger1=float(ledger1),
                Theta_over_A=float(Fr(Theta, An)), u=float(u), star=float(star),
                regen_over_A=float(Fr(regen, An)), Lsum_over_A=float(Lsum/An))

def b_T(t, l):
    # tree-level count b^T_{t,l} = min(t,l+1) A_{t-1,l} - min(t,l) A_{t-1,l-1}  (2.10절)
    return min(t, l+1)*A[t-1][l] - min(t, l)*(A[t-1][l-1] if l >= 1 else 0)

out = []
allok = True
for k in range(3, 12):
    for n in range(2*k+1, min(3*k-1, NMAX)+1):
        r = check(n, k)
        flags = [r['ok725'], r['okN1'], r['Lpos'], r['oka'], r['okb'], r['okc']]
        allok &= all(flags)
        out.append((k, n, flags, r))
with open(sys.argv[1] if len(sys.argv) > 1 else 'scripts/구조압축/심사_X7_N1_identity_out.txt', 'w', encoding='utf-8') as fh:
    fh.write('# k n | (7.25) N1-identity L>=0 (a)w (b)Theta (c)FL | FL/A  sum w f | Theta/A  u_n | star  regen/A  (Lsum)/A\n')
    for k, n, flags, r in out:
        fh.write(f"{k:2d} {n:2d} | {' '.join('T' if x else 'F' for x in flags)} | "
                 f"{r['FL_over_A']:.6f} {r['ledger1']:.6f} | {r['Theta_over_A']:.6f} {r['u']:.6f} | "
                 f"{r['star']:.6f} {r['regen_over_A']:.6f} ({r['Lsum_over_A']:.6f})\n")
    fh.write(f"\nALL OK: {allok}; cases: {len(out)} (k=3..11, 2k+1<=n<=min(3k-1,{NMAX}))\n")
print('ALL OK:', allok, 'cases:', len(out))
