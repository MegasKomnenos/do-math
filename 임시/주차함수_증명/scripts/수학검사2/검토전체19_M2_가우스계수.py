# 보조정리 gauss-coeff (가)(나)(다)의 수치 확인: Hermite 수의 비 재귀로 M_0, M_2/M_0, M_4/M_0 을 고정밀로 계산.
from decimal import Decimal as D, getcontext
getcontext().prec = 60
def He_ratios(n, y):
    N = n + y + 1
    x = y / (N*N)
    ups = [None, D(1)]
    for j in range(2, n+1):
        ups.append(D(1) - (j-1)*x/ups[j-1])
    return N, ups
def M_i(n, y, k, i):
    # M_i = e^{-y/2}/p_n * sum_{m=0}^{i+1} C(i+1,m)(-1)^m n!/(n-m)! He_{n-m}
    # express relative to He_{n-1}: He_{n-m}/He_{n-1} = prod of 1/(N ups_j) for j = n-m+1..n-1 (m>=2), He_n/He_{n-1} = N ups_n
    N, ups = He_ratios(n, y)
    from math import comb
    rel = {}
    rel[0] = N*ups[n]  # He_n/He_{n-1}
    rel[1] = D(1)
    for m in range(2, i+2):
        r = D(1)
        for j in range(n-m+1, n):
            r /= (N*ups[j])
        rel[m] = r
    s = D(0)
    for m in range(0, i+2):
        ff = D(1)
        for t in range(m): ff *= (n-t)
        s += comb(i+1, m) * (-1)**m * ff * rel[m]
    # log scale: log He_{n-1} = (n-1) log N + sum log ups_j (j<=n-1); log p_n = (n-1) log(n+1)
    logHe = (n-1)*N.ln() + sum(u.ln() for u in ups[1:n])
    logp = (n-1)*D(n+1).ln()
    return s * (logHe - logp - y/2).exp()
for k in (10000, 30000):
    for n in (2*k-1, 2*k):
        y = D(k)
        M0 = M_i(n, y, k, 0); M2 = M_i(n, y, k, 2); M4 = M_i(n, y, k, 4)
        print(f"k={k} n={n}: M0={M0:.6f} 4sqrt2(1-26/k)={4*D(2).sqrt()*(1-D(26)/k):.6f}  k*M2/M0={k*M2/M0:.5f}  k^2*M4/M0={k*k*M4/M0:.4f}")
        M0b = M_i(n, y-1, k, 0)
        print(f"     M0^(k-1,n)={M0b:.6f} (<= M0 ? {M0b<=M0})")

# M4/M0 closed form check (y=k)
def theta_val(n,y):
    N, ups = He_ratios(n,y); return N*ups[n]-n
for k in (30000,):
    for n,nu in ((2*k,0),(2*k-1,-1)):
        y=D(k); th=theta_val(n,y); kk=D(k)
        M0 = M_i(n,y,k,0); M4=M_i(n,y,k,4)
        if nu==0:
            form = 1+16/kk+18/kk**2+2/kk**3-(4+38/kk+22/kk**2+2/kk**3)/th
        else:
            form = 1+12/kk-6/kk**2-(4+26/kk-14/kk**2)/th
        print(f"nu={nu}: theta={th:.10f} center={4-(26+4*nu)/kk+(506+97*nu+5*nu*nu)/kk**2:.10f}  M4/M0 actual={M4/M0:.6e} formula={form:.6e}")
