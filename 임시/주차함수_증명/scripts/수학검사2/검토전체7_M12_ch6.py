# 6장 D 항목 재계산: theorem-D-base(q(m,d)), prop-W-thirteen, tilt-sum, 범위 셈
import math
from math import comb
from fractions import Fraction
import mpmath as mp
mp.mp.dps=40
M=700
p=[1]+[(n+1)**(n-1) for n in range(1,M+2)]
def Ac_column(l, nmax):
    top=min(nmax,2*l+4)
    Ac=[0]*(top+1)
    for n in range(l+2, top+1):
        s=0
        for j in range(l+1, n):
            s+=comb(n-1,j)*(j-l)*p[j]*p[n-1-j]
        for i in range(l+2, n):
            s+=Ac[i]*comb(n-1,i)*p[n-1-i]*((l+1)+min(n-i,l+1))
        Ac[n]=s
    return Ac
# need b_{m,m-d} for 4<=m<=700, 1<=d<=41 -> levels l=m-d, need Ac at l and l-1, n=m<=2l+4 requires d<=l+4 ok when m>= ~ 2d-4
cols={}
def Ac(n,l):
    if l<0: return p[n]
    if n<=l+1: return 0
    if l not in cols: cols[l]=Ac_column(l,M)
    return cols[l][n]
def b(n,l): return Ac(n,l-1)-Ac(n,l)
# full recurrence for small m (<=90) to be safe
def A_full(l,nmax):
    A=[1]
    for n in range(1,nmax+1):
        if l>=n-1: A.append(p[n]); continue
        A.append(sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
Afull=[A_full(l,90) for l in range(90)]
def b_small(n,l): return Afull[l][n]-(Afull[l-1][n] if l>=1 else 0)
# cross-check
for n in range(4,91):
    for d in range(1,min(41,(n+1)//2)+1):
        if n<=2*(n-d)+4:
            assert b(n,n-d)==b_small(n,n-d),(n,d)
print("Ac vs full ok for m<=90")
Psi=[None]+[sum(mp.mpf(j)**j*mp.e**(-j)/mp.factorial(j) for j in range(1,d+1)) for d in range(1,42)]
qmin=(10,None); qmax=(0,None); cnt=0
for m in range(4,M+1):
    for d in range(1,42):
        if 8*d**3>m*m: break
        cnt+=1
        q=mp.mpf(m)*b(m,m-d)/(mp.mpf(p[m])*Psi[d])
        if q<qmin[0]: qmin=(q,(m,d))
        if q>qmax[0]: qmax=(q,(m,d))
print("pairs",cnt,"min q",mp.nstr(qmin[0],14),qmin[1],"max q",mp.nstr(qmax[0],14),qmax[1])
print("q(3,1)=",mp.nstr(mp.mpf(3)*b_small(3,2)/(mp.mpf(p[3])*Psi[1]),12))
# prop-W-thirteen
def eRen(j): return mp.mpf(j)**(j-1)/(mp.e**(j-1)*mp.factorial(j-1))  # e*Ren(j) with j=r+1
for d in range(1,15):
    L=3130*(eRen(d+1)-mp.mpf(60)*(d+1)/(3131+d))
    R=2*(1+sum(eRen(r+1)+mp.mpf(60)*(r+1)/(3131+d) for r in range(1,d)))
    print("d",d,mp.nstr(L,6),mp.nstr(R,4),"L>R",L>R, "diff",mp.nstr(L-R,5))
# tilt-sum
def tilt(k):
    return sum(Fraction(n**(n-1),math.factorial(n))*Fraction(k,k+1)**((k-1)*n) for n in range(2,k+2))
mx=max((tilt(k),k) for k in range(2,61))
print("tilt max",mx[1],float(mx[0]), "all<1:",all(tilt(k)<1 for k in range(2,61)))
for k in (2,3,10,20,42,43): print(" k",k,float(tilt(k)))
# counts: (ㄹ) positions 5..20000; c50 positions 20001..50000
def pos(n): return n-2-math.ceil((n-1)/2)
print("positions 5..20000:",sum(pos(n) for n in range(5,20001)), " 20001..50000:",sum(pos(n) for n in range(20001,50001)))
print("pairs 5..20000:",sum(n-2-math.ceil((n-1)/2)+1 for n in range(5,20001)))
# column cert counts 161..500 and 121..160
def B(k): return -(-k*k//4)
d1=sum(2*B(k)-2*k for k in range(161,501)); r1=sum(B(k)+1 for k in range(161,501))
d2=sum(2*B(k)-2*k for k in range(121,161)); r2=sum(B(k)+1 for k in range(121,161))
print("col 161-500 direct",d1,"ratio",r1,"; 121-160 direct",d2,"ratio",r2)
# newton coefficient count r=2..40
print("newton coeffs 2..40:",sum(r+d+4 for r in range(2,41) for d in range(1,r)), " polys:",sum(r-1 for r in range(2,41)), sum(r-1 for r in range(2,171)))
# a0,a1
print("a0=",mp.nstr(3**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3),12)," a1=",mp.nstr(3**(-mp.mpf(1)/3)*mp.gamma(mp.mpf(2)/3),12))
# tail-T1 (B) constants
M0=mp.quad(lambda y: mp.e**(-y-y*y/2),[0,mp.inf]); Ms=[M0,1-M0]
for q in range(1,5): Ms.append(q*Ms[q-1]-Ms[q])
print("M0..M5:",[mp.nstr(x,6) for x in Ms])
s=mp.mpf(100); L4=mp.mpf('0.845204')
lhs=s*(mp.mpf(1)/2+2*L4-mp.sqrt(3*mp.pi/2))+mp.mpf(1)/2-(1/(3*s)+8/(3*s*s)+mp.mpf('2.507')/s**2+(1+mp.mpf('2.1709')*s)/s**3)
print("tailB s=100 lhs-rhs:",mp.nstr(lhs-(mp.mpf('0.0196')*s+mp.mpf('0.496')),6), "sqrt(3pi/2)=",mp.nstr(mp.sqrt(3*mp.pi/2),8))
# S=floor(e*2^30)
print("e*2^30=",mp.nstr(mp.e*2**30,15))
