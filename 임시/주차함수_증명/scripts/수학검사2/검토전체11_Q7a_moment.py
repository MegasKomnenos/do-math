# 검토전체11 Q7a: (7.2)·(7.3) 재귀로 E^sigma_{n,k}[T_k] = Z_n - k Z^H_n 의 부호를 n=2k+1부터 확인 (binary64, 참고용)
import numpy as np, math, sys
def run(k, nmax):
    # Boltzmann-normalized a~_m = e^{-m} A_{m,k-1}/m!
    at = np.zeros(nmax+1); at[0]=1.0
    w = np.minimum(np.arange(1,nmax+1), k).astype(float)  # min(p,k), p=1..nmax
    Zf = np.zeros(nmax+1); ZH = np.zeros(nmax+1); Z2 = np.zeros(nmax+1)
    out = {}
    for n in range(1, nmax+1):
        p = np.arange(1,n+1)
        prod = w[:n]*at[p-1]*at[n-p]
        at[n] = prod.sum()/(math.e*n)
        P = prod/(math.e*n*at[n])          # root-position law
        heavy = (p>k).astype(float); thr = (p==k).astype(float)
        Zf[n] = (P*(heavy + Zf[p-1] + Zf[n-p])).sum()
        ZH[n] = (P*(thr + ZH[p-1] + ZH[n-p])).sum()
        Z2[n] = (P*(Z2[p-1]+Z2[n-p] + 2*Zf[p-1]*Zf[n-p] + 2*heavy*(Zf[p-1]+Zf[n-p]))).sum()
        if n in (2*k+1, 2*k+2, 2*k+50, 3*k, 4*k, 5*k, 6*k, 8*k, 10*k, 10001) or n==nmax:
            out[n] = (Zf[n], ZH[n], Z2[n], Z2[n]-k*ZH[n])
    return out, Zf, ZH, Z2
for k, nmax in [(501, 4000), (840, 4000)]:
    out, Zf, ZH, Z2 = run(k, nmax)
    print("k=",k)
    for n,(a,b,c,T) in sorted(out.items()):
        print(f"  n={n:6d}  E[Z]={a:9.4f}  E[H]={b:9.5f}  E[Z(Z-1)]={c:10.4f}  E[T]={T:12.4f}  k*E[H]={k*b:10.4f}  P_k(n)={k*b/n:.5f}")
    T = Z2 - k*ZH
    neg = [n for n in range(2*k+1, nmax+1) if T[n] <= 0]
    print("  n in [2k+1,nmax] with E[T]<=0:", (neg[0], neg[-1], len(neg)) if neg else None)
