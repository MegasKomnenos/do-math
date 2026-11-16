# I12: 4장 검산 (경량판) — 네 재귀 전수 대조, 작은 행, 넘는 수 재귀, F0/F1 적분(erfi 기반 Dawson)
import itertools, time, sys
from math import comb
from fractions import Fraction
import mpmath as mp
p=lambda m:(m+1)**(m-1) if m>0 else 1
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        js=[j for j in range(1,i) if sig[j-1]>sig[i-1]]
        h.append(i-(max(js) if js else 0))
    return h
def brute(n,k):
    A=Kp=Kpp=J=0
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); A_=1;small=1;sm_lt=1;Z=0;H=0
        for hi in h:
            A_*=min(hi,k)
            if hi<=k: small*=hi
            if hi<k: sm_lt*=hi
            if hi>k: Z+=1
            if hi==k: H+=1
        A+=A_; Kp+=small*(Z*k**(Z-1) if Z>=1 else 0); Kpp+=small*(Z*(Z-1)*k**(Z-2) if Z>=2 else 0)
        J+=sm_lt*(H*k**(H-1) if H>=1 else 0)*(k-1)**Z
    return A,Kp,Kpp,J
def recur(k,N):
    A={i:p(i) for i in range(0,k+1)}; d={i:0 for i in range(0,k+1)}; z={i:0 for i in range(0,k+1)}
    J={i:0 for i in range(0,k)}; J[k]=p(k-1)
    for n in range(k+1,N+1):
        r=n-k
        A[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*A[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*min(i+1,k)*p(i)*p(n-1-i) for i in range(r-1,k+1))
        d[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*d[n-1-i] for i in range(0,r-1))+sum(comb(n-1,i)*p(i)*A[n-1-i] for i in range(0,r))
        z[n]=sum(comb(n-1,i)*(k+i+1)*p(i)*z[n-1-i] for i in range(0,r-1))+2*sum(comb(n-1,i)*p(i)*d[n-1-i] for i in range(0,r-1))
        J[n]=sum(comb(n-1,i)*(k+i)*p(i)*J[n-1-i] for i in range(0,r))+comb(n-1,k-1)*p(k-1)*p(n-k)
    return A,d,z,J
print("== 네 재귀 대 전수 대조 ==", flush=True)
for k in (2,3,4):
    A,d,z,J=recur(k,2*k)
    for n in range(k+1,2*k+1):
        b=brute(n,k); print(k,n,"A",A[n]==b[0],"K'",d[n]==b[1],"e_n",z[n]==b[2],"J",J[n]==b[3],flush=True)
def rows(N):
    cols=[]
    for l in range(0,N):
        a=[0]*(N+1); a[0]=1
        for n in range(1,N+1):
            if l>=n-1: a[n]=p(n); continue
            a[n]=sum(comb(n-1,j)*min(j+1,l+1)*a[j]*a[n-1-j] for j in range(n))
        cols.append(a)
    return {n:[cols[0][n]]+[cols[l][n]-cols[l-1][n] for l in range(1,n)] for n in range(1,N+1)}
t=time.time(); N=120; B=rows(N); print("rows N=%d time %.1f"%(N,time.time()-t),flush=True)
kn=lambda n:(n+1)//2
print("d_{n,k_n}<0 for n in", [n for n in range(2,61) if B[n][kn(n)]-B[n][kn(n)-1]<0])
print("right half nonincreasing 2..15:", all(all(B[n][j]>=B[n][j+1] for j in range(kn(n),n-1)) for n in range(2,16)))
print("b_{n,0}<...<b_{n,k_n-1} fails for n in", [n for n in range(1,N+1) if not all(B[n][i]<B[n][i+1] for i in range(0,kn(n)-1))])
fails=[]; best=None
for n in range(16,61):
    k=kn(n); A,d,z,J=recur(k,n)
    if not z[n]>J[n]: fails.append(n)
    rt=Fraction(z[n],J[n]); best=(n,rt) if best is None or rt<best[1] else best
print("e_n>J_n(k-1) fails 16..60:",fails,"min ratio n=%d %.7f"%(best[0],float(best[1])))
cr=[n for n in range(5,N+1) if B[n][kn(n)]<B[n][kn(n)+1]]
print("crossing 20..N all:", all(n in cr for n in range(20,N+1)), "fails 5..19:", [n for n in range(5,20) if n not in cr])
def Ac_rec(l,N):
    Ac={}
    for n in range(0,N+1):
        if n<=l+1: Ac[n]=0; continue
        Ac[n]=sum(comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))+sum(Ac[i]*comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
    return Ac
bad=0
for l in range(0,40):
    M=min(2*l+4,N); Ac=Ac_rec(l,M)
    for n in range(1,M+1):
        exact=p(n)-sum(B[n][:l+1]) if l<n else 0
        if Ac[n]!=exact: bad+=1
print("넘는 수 재귀 불일치 (l<40,n<=2l+4):",bad)
QL=lambda n: all(not(B[n][l]>B[n][l+1]) or B[n][l+1]**2>=B[n][l]*B[n][l+2] for l in range(0,n-2) if 2*l<=n-2)
print("Q_L(n) 3..15:", all(QL(n) for n in range(3,16)))
def su(z):
    i=0
    while i+1<len(z) and z[i]<z[i+1]: i+=1
    while i+1<len(z) and z[i]>z[i+1]: i+=1
    return i==len(z)-1
print("strict unimodal & no ties n<=N:", all(su(B[n]) for n in range(1,N+1)), all(B[n][l]!=B[n][l+1] for n in range(1,N+1) for l in range(n-1)))
mp.mp.dps=15
ninf=2/mp.sqrt(mp.pi)
def BorR(b): return 2*mp.e**(b*b/2)-2*b*mp.sqrt(mp.pi/2)*mp.erfi(b/mp.sqrt(2))
def F0(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r:(r*r*mp.e**((1-r*r)*z*z/2)*((1-r*r)*z*z+(1-r*r)**2*z**4/4)*BorR(r*z)/mp.sqrt(2*mp.pi)),[0,1])
def F1(z): return -ninf*z**4*mp.e**(-z*z)*mp.quad(lambda r:(r*r*mp.e**((1-r*r)*z*z/2)*((1-r*r)*z*z+(1-r*r)**2*z**4/4)*(mp.mpf(4)/3*r*r*z*z-mp.mpf(2)/3*r*z**4)),[0,1])
print("int F0 =",mp.nstr(mp.quad(F0,[-7,0,7]),6)," int F1 =",mp.nstr(mp.quad(F1,[-7,0,7]),8)," 46sqrt2-12 =",mp.nstr(46*mp.sqrt(2)-12,8),flush=True)
