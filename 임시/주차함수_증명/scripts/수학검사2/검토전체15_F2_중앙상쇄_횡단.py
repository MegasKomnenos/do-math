# F2 검산: (1) 중앙 상쇄 항등식 int F0 = 0, int F1 = 46 sqrt2 - 12 ; (2) 20<=n<=300 에서 b_{n,k_n} < b_{n,k_n+1}
import mpmath as mp
mp.mp.dps=20
ninf=2/mp.sqrt(mp.pi); c=1/mp.sqrt(2*mp.pi)
def Daw(b): return mp.exp(-b*b/2)*mp.quad(lambda v: mp.exp(v*v/2),[0,b])
def BldR(b): return mp.exp(b*b/2)*(2-2*b*Daw(b))
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z):
    inner=mp.quad(lambda r: r*r*mp.exp((1-r*r)*z*z/2)*Pq(z,r)*c*BldR(r*z),[0,1])
    return -ninf*z**4*mp.exp(-z*z)*inner
def F1(z):
    inner=mp.quad(lambda r: r*r*mp.exp((1-r*r)*z*z/2)*Pq(z,r)*(mp.mpf(4)/3*r*r*z*z-mp.mpf(2)/3*r*z**4),[0,1])
    return -ninf*z**4*mp.exp(-z*z)*inner
I0=2*mp.quad(F0,[0,2,4,8]); I1=2*mp.quad(F1,[0,2,4,8])
print("int F0 =",I0," int F1 =",I1," 46sqrt2-12 =",46*mp.sqrt(2)-12)
from math import comb, ceil
Nn=300
A=[[0]*(Nn+1) for _ in range(Nn+1)]
for l in range(Nn+1):
    A[0][l]=1
    for m in range(1,Nn+1):
        A[m][l]=sum(comb(m-1,j)*min(j+1,l+1)*A[j][l]*A[m-1-j][l] for j in range(m))
bad=[]
for m in range(20,Nn+1):
    b=[A[m][0]]+[A[m][l]-A[m][l-1] for l in range(1,m)]
    kn=ceil(m/2)
    if not (b[kn]<b[kn+1] and kn+1<=m-2): bad.append(m)
print("20<=n<=300에서 b_{n,k_n}<b_{n,k_n+1} 위반:",bad)
