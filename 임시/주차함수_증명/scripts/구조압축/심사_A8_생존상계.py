# 심사 A8 — S3·S7·S13 검산: 첫 층 생존 s_N(k)의 참값(2.13 사슬 재귀, binary64)과
# 네 상계(6.1, 8.10(가), 8.10(나) 닫힌 꼴, 10.21)·세 하계(8.7 Jensen, 10.26, 8.8 탈출)의 비교.
# 실행: python -I 심사_A8_생존상계.py  (출력 심사_A8_생존상계_out.txt)
import math, sys, numpy as np
Z12=-1.4603545088095868; Zm12=-0.2078862249773545; Z32=2.6123753486854883
C2=(2*math.pi)**-0.5
def logBor(m):  # m>=1 (array ok)
    m=np.asarray(m,dtype=float); return (m-1)*np.log(m)-m-np.array([math.lgamma(x+1) for x in np.atleast_1d(m)]).reshape(m.shape)
def survival(y, Nmax):
    """s_n(y) for n=0..Nmax (Nmax<=2y+1) via 2.13: s_n = pi0 + sum_{m=y+1}^n pi_n(m)(y/m)s_{m-1}."""
    s=np.ones(Nmax+1)
    lB=np.zeros(Nmax+2); lB[1:]=logBor(np.arange(1,Nmax+2))
    for n in range(y+1,Nmax+1):
        m=np.arange(y+1,n+1)
        pi=np.exp(lB[m]+lB[n+1-m]-lB[n+1])
        pi0=1-pi.sum()
        s[n]=pi0+np.sum(pi*(y/m)*s[m-1])
    return s
def pi_arr(n,m,lB): return np.exp(lB[m]+lB[n+1-m]-lB[n+1])
out=[]
P=lambda *a: out.append(' '.join(str(x) for x in a))
for k in [50,500,4000,6668]:
    Nmax=2*k+1
    s_k=survival(k,Nmax); s_k1=survival(k+1,Nmax)
    lB=np.zeros(Nmax+3); lB[1:]=logBor(np.arange(1,Nmax+3))
    P(f"\n===== k={k} =====")
    # (8.10) identity check and B_N
    worst_id=0; rows=[]
    qs=sorted(set([1,2,3,5,10,20,50]+[int(x*k**(2/3)) for x in (0.5,1,2,4,6)]+[k//4,k//2,int(0.75*k),k]))
    qs=[q for q in qs if 1<=q<=k]
    maxratio61=0.0
    for q in range(1,k+1):
        N=k+q; m=np.arange(k+1,N+1); th=(N+1-m)*pi_arr(N,m,lB)
        maxratio61=max(maxratio61, s_k[N]*q**1.5/k)
    P(f"max_q s_{{k+q}}(k) q^{{3/2}}/k over 1<=q<=k = {maxratio61:.4f}   (6.1의 상수 3 대 참값; F5/F6 S13)")
    P("q | xi | s(true) | 6.1 | 8.10(ga) | 8.10(na) | 10.21 | ratios: 6.1/s 8.10ga/s 8.10na/s 10.21/s | 8.7/s 10.26/s 8.8a/s 8.8b/s | (8.10)id err")
    for q in qs:
        N=k+q; xi=q/k**(2/3); st=s_k[N]
        m=np.arange(k+1,N+1); pi=pi_arr(N,m,lB); th=(N+1-m)*pi
        B=np.sum(th*(m-k)/m)
        iderr=abs((1-st)-np.sum(th*(m-k)/m*s_k[m-1]))
        nu=q; S12=2*math.sqrt(nu)+Z12+0.5/math.sqrt(nu)-nu**-1.5/24; Sm12=2/3*nu**1.5+0.5*math.sqrt(nu)+Zm12+1/(24*math.sqrt(nu))
        Blow=C2/(k+nu)*((nu+1)*S12-Sm12-((nu+1)*Z32-S12)/12)
        b61=min(1,3*k*q**-1.5); b810a=1/(1+B); b810b=1/(1+max(Blow,0)); b1021=min(1,1.15*(k+q+1)/(q+1)**1.5)
        # lower bounds for s_N(k): 8.7 Jensen (y=k), 10.26 (d=N-y+1=q+1), 8.8 escape
        EA=np.sum((m-k)*th); j87=math.exp(-EA/k)
        d=q+1; f1=4/3*C2; j1026=math.exp(-f1*((k+d-1)/k)**1.5*d**1.5/k)
        pi0=1-pi.sum(); km=np.sum(pi*k/m); e88a=pi0/(1-km); e88b=pi0/(1-k/N+(k/N)*pi0)
        P(f"{q:6d} | {xi:6.3f} | {st:.5e} | {b61:.4e} | {b810a:.4e} | {b810b:.4e} | {b1021:.4e} | {b61/st:7.3f} {b810a/st:7.3f} {b810b/st:7.3f} {b1021/st:7.3f} | {j87/st:6.3f} {j1026/st:6.3f} {e88a/st:6.3f} {e88b/st:6.3f} | {iderr:.1e}")
    # domination tests over all q
    dom_a=True; worst=(0,0)
    for q in range(1,k+1):
        N=k+q; m=np.arange(k+1,N+1); B=np.sum((N+1-m)*pi_arr(N,m,lB)*(m-k)/m)
        r=(1/(1+B))/min(1,3*k*q**-1.5)
        if r>worst[0]: worst=(r,q)
        if r>1+1e-15: dom_a=False
    P(f"max_q [8.10(ga)]/[6.1] = {worst[0]:.5f} at q={worst[1]}")
    P(f"8.10(ga) <= 6.1 for all 1<=q<=k ? {dom_a}")
    # 8.10(na) closed form vs 6.1
    fails=[]
    for q in range(1,k+1):
        nu=q; S12=2*math.sqrt(nu)+Z12+0.5/math.sqrt(nu)-nu**-1.5/24; Sm12=2/3*nu**1.5+0.5*math.sqrt(nu)+Zm12+1/(24*math.sqrt(nu))
        Blow=C2/(k+nu)*((nu+1)*S12-Sm12-((nu+1)*Z32-S12)/12)
        if 1/(1+max(Blow,0))>min(1,3*k*q**-1.5)+1e-15: fails.append(q)
    P(f"8.10(na) closed form 1/(1+B^low) <= 6.1 fails at {len(fails)} q-values; first/last: {fails[:3]} ... {fails[-3:]}" if fails else "8.10(na) closed form <= 6.1 for all q")
    # B_N main-term coefficient check (F6: B >= 0.376 q^{3/2}/k)
    coef=(9,0)
    for q in range(1,k+1):
        N=k+q; m=np.arange(k+1,N+1); B=np.sum((N+1-m)*pi_arr(N,m,lB)*(m-k)/m)
        if B*k/q**1.5<coef[0]: coef=(B*k/q**1.5,q)
    P(f"argmin q = {coef[1]}")
    coef=coef[0]
    P(f"min_q B_N k/q^(3/2) = {coef:.4f} (F6 claims >=0.376)")
    coefl=min((C2/(k+nu)*((nu+1)*(2*math.sqrt(nu)+Z12+0.5/math.sqrt(nu)-nu**-1.5/24)-(2/3*nu**1.5+0.5*math.sqrt(nu)+Zm12+1/(24*math.sqrt(nu)))-((nu+1)*Z32-(2*math.sqrt(nu)+Z12+0.5/math.sqrt(nu)-nu**-1.5/24))/12))*k/nu**1.5 for nu in range(1,k+1))
    P(f"min_q B^low k/q^(3/2) = {coefl:.4f}")
    # 8.7 vs 10.26 always?
    P("8.7 >= 10.26 for all q:", all(math.exp(-np.sum((m-k)*(N+1-m)*pi_arr(N,m,lB))/k) >= math.exp(-4/3*C2*((k+q)/k)**1.5*(q+1)**1.5/k)-1e-15 for q in range(1,k+1) for N in [k+q] for m in [np.arange(k+1,N+1)]))
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
