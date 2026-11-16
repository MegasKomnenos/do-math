from mpmath import mp, mpf, e, factorial, nstr
from fractions import Fraction as F
from math import floor
mp.dps=40
# prop-W-thirteen
def eRen(r1): return mpf(r1)**(r1-1)/(e**(r1-1)*factorial(r1-1))
for d in range(1,15):
    L=3130*(eRen(d+1)-mpf(60)*(d+1)/(3131+d)); R=2*(1+sum(eRen(r+1)+mpf(60)*(r+1)/(3131+d) for r in range(1,d)))
    print("d",d,nstr(L,6),nstr(R,5), "L>R", L>R, "diff", nstr(L-R,4))
# tilt-sum
def S(k):
    q=F(k,k+1)**(k-1); return sum(F(n**(n-1),factorial(n))*q**n for n in range(2,k+2))
mx=max((S(k),k) for k in range(2,61)); print("tilt max", mx[1], float(mx[0]), "all<1:", all(S(k)<1 for k in range(2,61)))
for k in (3,10,20,42,43): print("k",k, "%.6f"%float(S(k)))
# theorem-D pairs
print("pairs m<=700:", sum(floor(mp.cbrt(m*m)/2) for m in range(4,701)), " check 8d^3<=m^2:", sum(1 for m in range(4,701) for d in range(1,60) if 8*d**3<=m*m))
print("pairs m<=30, 2d<=m+1:", sum((m+1)//2 for m in range(1,31)))
