# P8: 8장 조합 항등식·부등식을 작은 k에서 정확 정수로 검사
from fractions import Fraction as Fr
from math import comb
import sys
K=int(sys.argv[1]) if len(sys.argv)>1 else 12
NMAX=3*K+3
p=[ (n+1)**(n-1) if n>0 else 1 for n in range(NMAX+2)]
# A[l][n]
def Atable(l):
    A=[1]+[0]*NMAX
    Ncal=[0]*(NMAX+1)
    for n in range(1,NMAX+1):
        Ncal[n]=min(n,l+1)*A[n-1]
        A[n]=sum(comb(n-1,t-1)*Ncal[t]*A[n-t] for t in range(1,n+1))
    return A
A={l:Atable(l) for l in range(K-3,K+3)}
def s(m,y): return Fr(A[y-1][m],p[m]) if y-1>=K-3 else None   # s_m(y)=A_{m,y-1}/p_m
def c(m,Y): return Fr(A[Y][m]-A[Y-1][m],p[m])
def pi(n,m): return Fr(comb(n,m)*m**(m-1)*p[n-m],p[n])
def pi0(n,y):
    # forests with all trees <= y : exp formula with unrestricted trees of size<=y
    F=[1]+[0]*n
    for nn in range(1,n+1):
        F[nn]=sum(comb(nn-1,t-1)*t**(t-1)*F[nn-t] for t in range(1,min(nn,y)+1))
    return Fr(F[n],p[n])
k=K
# (8.2) one-tree recursion
bad=[]
for m in range(k+1,3*k):
    rhs=sum(pi(m,t)/t*(s(t-1,k+1)+k*c(t-1,k))*(s(m-t,k) if m-t>=0 else 0) for t in range(k+1,m+1))
    if m<=2*k+1 and rhs!=c(m,k): bad.append(('eq',m))
    if m>=2*k+2 and not rhs<=c(m,k): bad.append(('lb',m))
    rhs2=sum(pi(m,t)/t*(s(t-1,k)+(k-1)*c(t-1,k-1))*(s(m-t,k-1)) for t in range(k,m+1))
    if m<=2*k-1 and rhs2!=c(m,k-1): bad.append(('eq2',m))
    if m>=2*k and not rhs2<=c(m,k-1): bad.append(('lb2',m))
print("8.2:",bad)
# lowest violation (8.10) and escape (8.9), prop-U (가)
def theta(t,m): return Fr(comb(t,m)*m**(m-1)*(t-m)**(t-m),t**(t-1)) if t>m else Fr(1)
bad=[]
for y in range(k-2,k+2):
    for N in range(y+1,2*y+2):
        lhs=1-s(N,y); rhs=sum(theta(N+1,m)*Fr(m-y,m)*s(m-1,y) for m in range(y+1,N+1))
        if lhs!=rhs: bad.append(('V',y,N))
        km=sum(pi(N,m)*Fr(y,m) for m in range(y+1,N+1)); p0=pi0(N,y)
        if not (s(N,y)>=p0/(1-km)>=p0/(1-Fr(y,N)+Fr(y,N)*p0)): bad.append(('G',y,N))
        B=sum(theta(N+1,m)*Fr(m-y,m) for m in range(y+1,N+1))
        if not s(N,y)<=1/(1+B): bad.append(('U',y,N))
        # Jensen (8.8) E[A]
        EA=sum(j*theta(N+1,y+j) for j in range(1,N-y+1))
        import math
        if not float(s(N,y))>=math.exp(-float(EA)/y)-1e-12: bad.append(('W',y,N))
print("V,G,U,W:",bad)
# old-6-30
bad=[]
for N in range(k,2*k):
    r=s(N,k-1)/s(N,k)
    if not r>=Fr(k-1,k)**(N-k+1): bad.append(('a',N))
    if not r>=1-max(1/(k*pi0(Np,k-1)) for Np in range(k,N+1)): bad.append(('b',N))
    if N<=2*k-2:
        import math
        if not float(r)>=1-math.exp(7/6)*N**1.5/(4*(2*math.pi)**-0.5*k*(2*k-1-N)): bad.append(('c',N))
        # pi0 lower bound in (다)
        if not float(pi0(N,k-1))>=4*(2*math.pi)**-0.5*math.exp(-7/6)*(2*k-1-N)*N**-1.5: bad.append(('c0',N))
print("6-30:",bad)
# old-6-31 (마), old-6-32
bad=[]
for N in range(k,2*k+1):
    for j in range(N//2+1,N+1):
        if not pi0(N,j)-pi0(N+1,j)<=pi(N,j): bad.append(('ma',N,j))
def sT(t,y): return min(Fr(1),Fr(y,t))*s(t-1,y)
for t in range(k+1,2*k+2):
    ecap=sT(t,k+1)-sT(t,k); esz=sT(t,k)-sT(t+1,k)
    if not ecap>=esz/2: bad.append(('K',t))
    if ecap!=Fr(1,t)*(s(t-1,k+1)+k*c(t-1,k)): bad.append(('ecap',t))
print("6-31(마),6-32:",bad)
# (8.4) window recursion
bad=[]
for q in range(1,k+2):
    R=k*c(k+q,k)
    rhs=sum(pi(k+q,k+j)*Fr(k,k+j)*(s(k+j-1,k+1)+(k*c(k+j-1,k) if j>=2 else 0)) for j in range(1,q+1))
    if R!=rhs: bad.append(q)
print("8.4:",bad)
