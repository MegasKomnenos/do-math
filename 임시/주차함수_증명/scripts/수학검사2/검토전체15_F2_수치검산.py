# F2 검산: (1) M4/M0 식(He_{n-5} 포함), (2) 따름정리 gauss-coeff-numeric (나)(다), (3) borel-tail-arc 둘째 조각 상수 -2/3와 유한합 나머지 범위, (4) 정리 4.5의 n<=15 부호와 P_C
import sympy as sp
from fractions import Fraction as F
from math import comb
import mpmath as mp
# (1)
n,y,N,vt,k=sp.symbols('n y N vartheta k')
He_n,He_n1=sp.symbols('He_n He_n1')
He_n2=(N*He_n1-He_n)/((n-1)*y); He_n3=(N*He_n2-He_n1)/((n-2)*y)
He_n4=(N*He_n3-He_n2)/((n-3)*y); He_n5=(N*He_n4-He_n3)/((n-4)*y)
ff=lambda m: sp.prod([n-i for i in range(m)])
num4=sum(sp.binomial(5,i)*(-1)**i*ff(i)*h for i,h in enumerate([He_n,He_n1,He_n2,He_n3,He_n4,He_n5]))
den=He_n-n*He_n1
for nv in (0,-1):
    r4=sp.simplify((num4/den).subs(He_n,(n+vt)*He_n1).subs(N,n+y+1).subs({y:k,n:2*k+nv}))
    tgt = 1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/vt if nv==0 else 1+12/k-6/k**2-(4+26/k-14/k**2)/vt
    print("M4/M0 nu=%d 차:"%nv, sp.simplify(r4-tgt))
# (2)
w=F(699,100); v=w-F(7,2)-(4*w+F(1,2))*F(3,2)/31-F(13,2)*w/961-12*w/30000
print("(나)", v, v==F(495594511,240250000), float(v))
mp.mp.dps=30
a0=mp.cbrt(3)**-2*mp.gamma(mp.mpf(1)/3); a1=mp.cbrt(3)**-1*mp.gamma(mp.mpf(2)/3)
print("a0,a1 =",a0,a1)
w=mp.mpf('6.98'); K=mp.mpf(10000)
val=w-3.5-(4*w+0.5)*mp.mpf('1.2879')*K**(-mp.mpf(1)/3)-mp.mpf(13)/2*w*mp.mpf('0.939')*K**(-mp.mpf(2)/3)-12*w/K
print("(다) 하계 값:",val)
# (3)
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
c=1/mp.sqrt(2*mp.pi)
tot=mp.nsum(lambda j: j*Bor(int(j))-c/mp.sqrt(j),[1,mp.inf]) if False else None
# direct partial sums with tail estimate
S=0; worst=-1; viol=[]
for j in range(1,20001):
    S+=j*Bor(j)
    if j in (1,2,3,5,10,50,100,1000,10000,20000) or j<=60:
        val=S-2*c*mp.sqrt(j)+mp.mpf(2)/3
        bound=mp.mpf(2)/3*c/mp.sqrt(j)
        if j in (1,2,3,5,10,50,100,1000,10000,20000): print("k=%d: S-2c sqrt k+2/3 = %s ; 2/3 c k^-1/2 = %s ; ratio=%s"%(j,mp.nstr(val,8),mp.nstr(bound,8),mp.nstr(val/bound,6)))
        if val<0 or val>bound: viol.append(j)
print("위반 k(<=60 및 표본):",viol)
# constant check: zeta(1/2)
print("c*zeta(1/2) =", c*mp.zeta(0.5), " ; -2/3 - c*zeta(1/2) =", -mp.mpf(2)/3-c*mp.zeta(0.5))
# (4)
Nn=80
A=[[0]*(Nn+1) for _ in range(Nn+1)]
for l in range(Nn+1):
    A[0][l]=1
    for m in range(1,Nn+1):
        A[m][l]=sum(comb(m-1,j)*min(j+1,l+1)*A[j][l]*A[m-1-j][l] for j in range(m))
def row(m): return [A[m][0]]+[A[m][l]-A[m][l-1] for l in range(1,m)]
import math
bad=[]
for m in range(2,Nn+1):
    b=row(m); kn=math.ceil(m/2); d=b[kn]-b[kn-1]
    if m<=15:
        pc=all(b[j]>=b[j+1] for j in range(kn,m-1))
        if not (d<0 and pc): bad.append((m,d,pc))
    else:
        if not d>0: bad.append((m,d))
print("정리 4.5 작은 n 검사 위반:",bad)
