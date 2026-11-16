from fractions import Fraction as F
from math import factorial, floor
from mpmath import mp, mpf, e, sqrt, pi, exp
mp.dps=30
def S(k):
    q=F(k,k+1)**(k-1); return sum(F(n**(n-1),factorial(n))*q**n for n in range(2,k+2))
vals={k:S(k) for k in range(2,61)}
mk=max(vals,key=vals.get); print("tilt max at k=",mk, float(vals[mk]), "all<1:", all(v<1 for v in vals.values()))
for k in (3,10,20,42,43): print("k",k,"%.6f"%float(vals[k]))
B2=lambda k: (1-1/e)+(exp(mpf(3)/2+mpf(1)/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(42)=",B2(42)," B2(43)=",B2(43), " B2(2000)=",B2(2000))
print("pairs m<=700 (8d^3<=m^2):", sum(1 for m in range(4,701) for d in range(1,60) if 8*d**3<=m*m), " pairs m<=30,2d<=m+1:", sum((m+1)//2 for m in range(1,31)))
