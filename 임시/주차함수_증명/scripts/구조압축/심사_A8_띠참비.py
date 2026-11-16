# 심사 A8 — S13 검산: 가중 재귀(G1)를 로그 정규화 binary64로 풀어 z_n(l)=A_{n,l}/p_n=s_n(l+1)을 셋째 층 전까지 얻고,
# 둘째 층 띠에서 참 비 BV_n/Theta_n (8.1)을 센다(8.29의 1.009 대 참값; D:band-boxes의 '>=2.17'과 F5의 2.39·2.29 대조).
# 실행: python -I 심사_A8_띠참비.py [k ...]   (기본 2000 6668)
import math, sys, numpy as np
def logp(j): j=np.asarray(j,dtype=float); return (j-1)*np.log(j+1)
def z_table(l, nmax):
    """z_n = sum_j C(n-1,j) p_j p_{n-1-j}/p_n * w_{j+1} z_j z_{n-1-j}, w_t=min(t,l+1)."""
    z=np.ones(nmax+1); lg=np.array([math.lgamma(i+1) for i in range(nmax+2)]); lp=logp(np.arange(nmax+1))
    w=np.minimum(np.arange(1,nmax+2),l+1).astype(float)
    for n in range(l+2,nmax+1):  # n<=l+1: z_n=1
        j=np.arange(n); lc=lg[n-1]-lg[j]-lg[n-1-j]+lp[j]+lp[n-1-j]-lp[n]
        z[n]=np.sum(np.exp(lc)*w[j]*z[j]*z[n-1-j])
    return z
def logBor(m): m=np.asarray(m,dtype=float); return (m-1)*np.log(m)-m-np.array([math.lgamma(x+1) for x in np.atleast_1d(m)]).reshape(m.shape)
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
ks=[int(a) for a in sys.argv[1:]] or [2000,6668]
for k in ks:
    nmax=3*k
    zk=z_table(k,nmax); zk1=z_table(k-1,nmax); zk2=z_table(k-2,nmax)
    lB=np.zeros(nmax+2); lB[1:]=logBor(np.arange(1,nmax+2))
    # sanity vs chain recursion for s_n(k)=z_n(k-1), n<=2k+1
    s=np.ones(2*k+2)
    for n in range(k+1,2*k+2):
        m=np.arange(k+1,n+1); pi=np.exp(lB[m]+lB[n+1-m]-lB[n+1]); s[n]=(1-pi.sum())+np.sum(pi*(k/m)*s[m-1])
    P(f"k={k}: max |z_n(k-1)-s_n(k)| over n<=2k+1 = {np.max(np.abs(zk1[:2*k+2]-s)):.2e} (sanity)")
    cK=zk-zk1; cK1=zk1-zk2   # c_m(k), c_m(k-1)
    P("nu | n | BV/Theta | Theta/p_n | BV/p_n")
    worst=(1e9,0)
    for nu in range(3,k):
        n=2*k+nu; N=n-k
        theta=math.exp(lB[k]+lB[n+1-k]-lB[n+1])*zk1[N]/k
        m=np.arange(2*k+1,n); pim1=np.exp(lB[m+1]+lB[n-m]-lB[n+1])
        bv=np.sum(pim1/(m+1)*(cK[m]+cK1[m]))
        r=bv/theta
        if nu in (3,50,103,int(0.1*k),int(0.25*k),int(0.48*k),int(0.6*k),int(0.8*k),k-1): P(f"{nu:6d} | {n:6d} | {r:7.3f} | {theta:.3e} | {bv:.3e}")
        if 103<=nu<=0.48*k and r<worst[0]: worst=(r,nu)
    P(f"k={k}: min BV/Theta over band 103<=nu<=0.48k = {worst[0]:.4f} at nu={worst[1]}  (8.29 증명값 1.009)")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
