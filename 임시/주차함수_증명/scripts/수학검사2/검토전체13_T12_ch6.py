# T12: chapter-6 appendix items, direct recomputation
from fractions import Fraction as F
from math import comb, factorial, exp, e, sqrt, pi
import mpmath as mp
mp.mp.dps=40
# D.prop-W-thirteen: L(d), R(d) at k=3131
def eRen(m): return mp.mpf(m)**(m-1)/(mp.e**(m-1)*mp.factorial(m-1))  # e*Ren(m) = m^{m-1}/(e^{m-1}(m-1)!)
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-mp.mpf(60)*(d+1)/(k+d))
    R=2*(1+sum(eRen(r+1)+mp.mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print(f"d={d}: L={mp.nstr(L,6)} R={mp.nstr(R,6)} L>R={L>R}")
# D.tilt-sum-small-k: exact rational sums
def tilt(k):
    q=F(k,k+1)**(k-1)
    return sum(F(n**(n-1),factorial(n))*q**n for n in range(2,k+2))
for k in (2,3,10,20,42,43):
    s=tilt(k); print(f"k={k}: sum={float(s):.6f} <1: {s<1}")
mx=max(range(2,61),key=lambda k: tilt(k)); print("max over 2..60 at k=",mx, float(tilt(mx)))
# D.theorem-D-base: q(4,1) and q(689,39) via complement recursion
def p(m): return (m+1)**(m-1) if m>=1 else 1
def Ac_col(l,nmax):
    Ac=[0]*(nmax+1)
    for n in range(l+2,nmax+1):
        s=sum(comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        s+=sum(Ac[i]*comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        Ac[n]=s
    return Ac
def Psi(d): return sum(mp.mpf(j)**j*mp.e**(-j)/mp.factorial(j) for j in range(1,d+1))
def q(m,d):
    l=m-d
    A1=Ac_col(l-1,m)[m]; A2=Ac_col(l,m)[m]
    b=A1-A2
    return mp.mpf(m)*b/(mp.mpf(p(m))*Psi(d))
print("q(4,1)=",mp.nstr(q(4,1),12)," q(689,39)=",mp.nstr(q(689,39),12), " q(3,1)=",mp.nstr(q(3,1),10))
