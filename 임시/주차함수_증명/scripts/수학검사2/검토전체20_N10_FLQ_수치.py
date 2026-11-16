# 사슬 재귀(보조정리 2:old-2-45 / 6.22)로 s_d(y)를 배정밀도로 계산해 10장의 주장(FLQ (가)(나), 머묾 상계, 생존 상·하계, 대각선 손실)을 첫 열들에서 수치로 확인
import numpy as np, math, sys
from math import lgamma, log, exp, sqrt

def logBor(m):
    m = np.asarray(m, dtype=float)
    return -m + (m-1)*np.log(m) - np.vectorize(lgamma)(m+1)

def chain_s(y, dmax):
    # s[d] = frak s_d(y) for d=1..dmax (dmax<=y+3; d=y+3 gets the two-tree correction t(y)/(y+1)^2 of (6.22))
    s = np.zeros(dmax+1); s[1]=1.0
    lb_small = logBor(np.arange(1, dmax+1))          # log Bor(j), j=1..dmax
    lb_big = logBor(np.arange(y+1, y+dmax+1))        # log Bor(y+q), q=1..dmax
    for d in range(2, dmax+1):
        q = np.arange(1, d)
        lp = lb_small[d-q-1] + lb_big[q-1] - lb_big[d-1]   # log Pr^y(d->q)
        pr = np.exp(lp)
        pi0 = 1.0 - pr.sum()
        s[d] = pi0 + np.sum(pr * (y/(y+q)) * s[1:d])
        if d==y+3:
            lt = -1 + 2*float(logBor(y+1)) - float(logBor(2*y+3)) - log(2)
            s[d] += exp(lt)/(y+1)**2
    return s

def exact_check():
    # 작은 y에서 정확 재귀(2:old-2-6)와 비교
    from fractions import Fraction as F
    from math import comb
    y=6; nmax=2*y+2
    A=[[F(0)]*(nmax+2) for _ in range(nmax+1)]
    for l in range(nmax+2): A[0][l]=F(1)
    for m in range(1,nmax+1):
        for l in range(nmax+2):
            A[m][l]=sum(comb(m-1,j-1)*min(j,l+1)*A[j-1][l]*A[m-j][l] for j in range(1,m+1))
    p=lambda m: F((m+1)**(m-1))
    s=chain_s(y, y+2)
    s=chain_s(y, y+3)
    for d in range(1,y+4):
        ex=float(A[y+d-1][y-1]/p(y+d-1))
        assert abs(s[d]-ex)<1e-12, (d,s[d],ex)
    print("chain recursion matches exact values at y=6")

exact_check()

def g(x): return (x-1)*log(1+1/x)

def analyze(k, out):
    y_list = {k-1: None, k: None, k+1: None}
    for y in y_list: y_list[y] = chain_s(y, k+3 if y==k-1 else k+2)
    sm1, s0, s1 = y_list[k-1], y_list[k], y_list[k+1]
    # s_m(l): s_m(k+1)=frak s_{m-k}(k+1); s_m(k)=frak s_{m-k+1}(k); s_m(k-1)=frak s_{m-k+2}(k-1)
    def S(m, l):
        if l==k+1: return s1[m-k] if m-k>=1 else 1.0
        if l==k:   return s0[m-k+1]
        if l==k-1: return sm1[m-k+2]
    ms = np.arange(k, 2*k+2)
    c_k  = {m: S(m,k+1)-S(m,k) for m in range(k,2*k+2)}
    c_k1 = {m: S(m,k)-S(m,k-1) for m in range(k,2*k+2)}
    vs_k  = {m: S(m+1,k+1)-S(m,k) for m in range(k,2*k+1)}
    vs_k1 = {m: S(m+1,k)-S(m,k-1) for m in range(k,2*k+1)}
    assert all(v>=-1e-13 for v in vs_k.values()) and all(v>=-1e-13 for v in vs_k1.values())
    frak_p = {m: (k+1)*c_k[m]-(k-1)*c_k1[m] for m in range(k,2*k+1)}
    V = np.cumsum([frak_p[m] for m in range(2*k,k-1,-1)])[::-1]  # V_k(m), m=k..2k
    out.write(f"k={k}: V_k(k)={V[0]:.5f} (v(k) lower bound in 6:old-6-19), min V={V.min():.4e}\n")
    # 생존 상·하계 (정리 old-8-25, 보조정리 old-8-30) at y=k+1 and k-1,k
    mS=1.15; f1=4/(3*sqrt(2*math.pi))
    for y,s in ((k-1,sm1),(k,s0),(k+1,s1)):
        dm=min(len(s)-1,y+2); d=np.arange(1,dm+1); sup=np.minimum(1, mS*(y+d)/d**1.5)
        low=np.exp(-f1*((y+d-1)/y)**1.5*d**1.5/y)
        viol_up=(s[1:dm+1]-sup).max(); viol_low=(low[1:]-s[2:dm+1]).max()
        out.write(f"  y={y}: max(s-s_up)={viol_up:.2e}  max(s_low-s) over d>=2 ={viol_low:.2e}\n")
    # 머묾 법칙 check: (y+1)vs_{y+d-1}(y) <= (d-1)c_{y+d}(y)
    viol=max((k+1)*vs_k[m]-(m-k)*c_k[m+1] for m in range(k+1,2*k+1))
    out.write(f"  stay-law violation y=k: {viol:.2e}\n")
    # DD_m and its negative part
    DD={m:(k+1)*S(m+1,k+1)-2*k*S(m,k)+(k-1)*S(m-1,k-1) for m in range(k+1,2*k+1)}
    negsum=sum(min(0,v) for v in DD.values())
    out.write(f"  sum of negative DD_m = {negsum:.5f} (vs -DDL(k)={-2*50.62/sqrt(k-1):.5f})\n")
    # FLQ for all nu
    worst_ga=float('inf'); worst_na=float('inf'); worst_na_pos=None
    nus = range(max(103,20001-2*k), k+1)
    for nu in nus:
        n=2*k+nu; N=k+nu
        f = {m:(2*frak_p[m] if m<=N else (k+n-m+1)*c_k[m]-(k+n-m-1)*c_k1[m]) for m in range(k,2*k+1)}
        T=0.0; Tm={}
        for m in range(2*k,k-1,-1):
            T+=f[m]; Tm[m]=T
        mga=min(Tm[m] for m in range(k+2,2*k+1)); worst_ga=min(worst_ga,mga)
        if nu>0.48*k: theta=-1.0
        else: theta=2*(1+1/k)*S(N,k)/S(N,k+1)-1
        u_over_wk = exp(g(N)-g(k))*S(N,k+1)/S(N-1,k)
        wk1_over_wk = exp(g(k+1)-g(N-1))*S(N-2,k)/S(N-1,k)
        val = wk1_over_wk*Tm[k] + theta*u_over_wk      # (w_{k+1}T_k + theta u_n)/w_k
        if val<worst_na: worst_na=val; worst_na_pos=nu
        # Stays and Stays^up sanity for band
    out.write(f"  FLQ(ga): min_{{nu,m>=k+2}} T_m = {worst_ga:.5f};  FLQ(na): min_nu (w_{{k+1}}T_k+theta u)/w_k = {worst_na:.5f} at nu={worst_na_pos}\n")
    # Stays at a few nu vs Stays^up(k; nubar)
    def Stays(nu):
        N=k+nu
        return 2*vs_k[N+1]+sum((2-(m-N)/k)*(vs_k[m]+vs_k1[m-1]) for m in range(N+2,2*k+1))
    for nu in sorted(set([max(103,20001-2*k), int(1.3*k**(2/3)), int(2*k**(2/3)), int(0.48*k), int(0.6*k), k-1])):
        if nu<1 or nu>k-1: continue
        out.write(f"  Stays(k,{nu})={Stays(nu):.5f}\n")
    return

with open(sys.argv[1] if len(sys.argv)>1 else "scripts/수학검사2/_N10_FLQ_out.txt","w",encoding="utf-8") as out:
    for k in (6668, 8065, 9551, 9705):
        analyze(k,out); out.flush()
print("done")
