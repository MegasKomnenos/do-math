# N12 검산: D.tilt-sum-small-k 정확 유리수 합과 B_2(k), D.prop-W-thirteen의 L(d)·R(d), D.theorem-U-constant 산술
from fractions import Fraction as Fr
from math import factorial
from mpmath import mp, mpf, e, sqrt, pi, exp
mp.dps=40
def S(k):
    return sum(Fr(n**(n-1),factorial(n))*Fr(k,k+1)**((k-1)*n) for n in range(2,k+2))
vals={k:S(k) for k in range(2,61)}
print("all <1 for 2<=k<=60:",all(v<1 for v in vals.values()), " max at k=",max(vals,key=vals.get), vals[2], float(vals[2]))
for k in (3,10,20,42,43): print(" k=%d sum=%.6f"%(k,float(vals[k])))
def B2(k): k=mpf(k); return (1-1/e)+(exp(mpf(1.5)+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B_2(42)=",B2(42)," B_2(43)=",B2(43)," B_2(2000)=",B2(2000))
# prop W thirteen
def eRen(m): return mpf(m)**(m-1)/(e**(m-1)*factorial(m-1))   # e*Ren(r+1) with m=r+1: (r+1)^r/(e^r r!)
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-mpf(60)*(d+1)/(k+d)); R=2*(1+sum(eRen(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print(" d=%2d L=%9.2f R=%6.2f L>R:%s"%(d,L,R,L>R))
# theorem U arithmetic
c=1/sqrt(2*pi); G=mpf('2.7323'); m=mpf('0.8051')
print("3c(8.133+10.301c)=",3*c*(mpf('8.133')+mpf('10.301')*c)," 1.5*G*m*c*(17.951+23.462c)=",mpf('1.5')*G*m*c*(mpf('17.951')+mpf('23.462')*c))
print("with recalc bounds:",3*c*(mpf('8.13091')+mpf('10.29939')*c), mpf('1.5')*G*m*c*(mpf('17.94855')+mpf('23.46002')*c))
print("0.0342^3=",mpf('0.0342')**3, ">=1/25000:",mpf('0.0342')**3>=mpf(1)/25000)
