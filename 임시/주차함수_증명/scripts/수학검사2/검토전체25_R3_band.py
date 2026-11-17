# R3 검산(표본; 인증 아님): 정리 old-5-12·old-5-13·보조정리 cover-edge가 증가를 말하는 몇 위치에서
# 한 칸 차분 d_{n,k}/p_n 을 열 재귀의 배정밀도 계산으로 본다.
import sys, numpy as np, math
def column(k,N):
    a=np.zeros(N+1,dtype=np.longdouble); a[0]=1.0
    w=np.minimum(np.arange(1,N+1),k).astype(np.longdouble)
    einv=np.exp(np.longdouble(-1.0))
    for n in range(1,N+1):
        a[n]=einv*np.dot(w[:n]*a[:n],a[n-1::-1][:n])/n
    return a
def dn(n,k):
    c=[column(kk,n)[n] for kk in (k-1,k,k+1)]   # A_{n,k-2},A_{n,k-1},A_{n,k} (scaled)
    pn=math.exp((n-1)*math.log(n+1)-n-math.lgamma(n+1))
    return float(c[2]-2*c[1]+c[0])/pn, float(c[1]-c[0])/pn
for (n,r) in [(20032,598),(20001,597),(20001,598),(20001,1090),(20001,1100),(12187,598),(16020,833)]:
    k=n-r
    d,b=dn(n,k)
    x32=r**1.5/n; xh=(r+1)/k**(2/3)
    print("n=%d r=%d k=%d x^{3/2}=%.4f xhat=%.4f : d_{n,k}/p_n=%.3e  1/(100r^2)=%.3e  ratio=%.1f"%(n,r,k,x32,xh,d,1/(100*r*r),d*100*r*r))
