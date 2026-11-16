# 검토전체18 L2: a0,a1 상수, 따름정리 gauss-coeff-numeric 수치, Borel 합의 전개 상수(-2/3)와 오차 상계
from mpmath import mp, mpf, gamma, quad, exp, sqrt, pi, log, factorial, e
from fractions import Fraction
import sys
mp.dps=30
out=[]
a0=mpf(3)**(mpf(-2)/3)*gamma(mpf(1)/3); a1=mpf(3)**(mpf(-1)/3)*gamma(mpf(2)/3)
out.append(f"a0={a0} a1={a1}; in (1.287899,1.2879): {1.287899<a0<1.2879}; a1 in (0.938892,0.939): {0.938892<a1<0.939}")
# (나)
F=Fraction
val=F(699,100)-F(7,2)-F(6*699,100*31)-F(75,100*31)-F(13*699,2*100*961)-F(12*699,100*30000)
out.append(f"(나) exact = {val} == 495594511/240250000 ? {val==F(495594511,240250000)}; >2: {val>2}")
# (다)
k13=mpf(10000)**(mpf(-1)/3)
v=mpf('6.98')-mpf('3.5')-(4*mpf('6.98')+mpf('0.5'))*mpf('1.2879')*k13-(13*mpf('6.98')/2)*mpf('0.939')*k13**2-12*mpf('6.98')/10000
out.append(f"(다) lower bound with stated constants = {v}  >=1.6809: {v>=mpf('1.6809')}")
# Borel pieces
def Bor(j): return exp(-j)*mpf(j)**(j-1)/factorial(j)
c=1/sqrt(2*pi)
for k in (1000,10000,30000):
    eps=1/sqrt(mpf(k))
    tail1=1-sum(Bor(j) for j in range(1,k+1))
    d1=2*c*eps-tail1
    s2=sum(j*Bor(j) for j in range(1,k+1))
    d2=s2-(2*c*sqrt(mpf(k))-mpf(2)/3)
    out.append(f"k={k}: first piece 2c*eps-tail={d1}  bound (5/9)c eps^3={5*c*eps**3/9}  ok={0<=d1<=5*c*eps**3/9}; second piece diff={d2} bound (2/3)c eps={2*c*eps/3} ok={0<=d2<=2*c*eps/3}")
open(sys.argv[1],'w',encoding='utf-8').write("\n".join(out))
