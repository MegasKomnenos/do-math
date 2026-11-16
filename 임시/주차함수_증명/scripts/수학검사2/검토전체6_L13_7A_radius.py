# L13: 기록 rc9aee43 estimate_radius 재구현(순수 파이썬) -> c = (x e - 1) k
import math
def estimate_c(k, factor=16):
    nmax=factor*k; r=math.exp(-1)
    t=[0.0]*(k+1); a=[1.0]*(k+1)
    for s in range(1,k+1):
        t[s]=math.exp((s-1)*math.log(s)-math.lgamma(s+1)-s)
        a[s]=math.exp((s-1)*math.log(s+1)-math.lgamma(s+1)-s)
    g=[0.0]*(nmax+1); h=[0.0]*(nmax+1); e=[0.0]*(nmax+1); g[0]=e[0]=1.0
    for n in range(1,nmax+1):
        m=min(k,n)
        if n<=k: g[n]=a[n]
        else:
            g[n]=sum((j)*t[j]*g[n-j] for j in range(1,m+1))/n
            h[n]=k*r*(sum(a[j]*h[n-1-j] for j in range(0,m))+g[n-1])/n
        e[n]=g[n]+sum(h[j]*e[n-j] for j in range(1,n+1))
    guess=r*e[-2]/e[-1]
    x=round(guess*(1<<40))/(1<<40)
    return (x*math.e-1)*k
for k in (121,125,160,161,165,495,500):
    print(k, round(estimate_c(k),4))
