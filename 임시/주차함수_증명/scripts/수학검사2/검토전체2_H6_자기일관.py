# H6 검산: 정리 self-consistent-S (다)의 표와 따름정리 cor-S-prime의 세 값을 독립 재계산
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
import math
getcontext().prec=80
E=Decimal(1).exp()

def a0(m):  # a°_m=(m+1)^{m-1}/m!
    return Fr((m+1)**(m-1), math.factorial(m)) if m>=1 else Fr(1)
def free_ratio(m): # e^{g(m+1)} = a°_{m+1}/a°_m
    return a0(m+1)/a0(m)

layers=[(Fr(267,100),25,501,Fr(13,100)),(Fr(27,10),70,1855,Fr(2,25)),(Fr(271,100),100,6098,Fr(11,200))]
for vs,J,k0,y in layers:
    # j*
    m=0
    while free_ratio(m+1)<vs: m+=1
    # j* = max{m: free_ratio(m)<vs}
    jstar=m if free_ratio(m)<vs else m-1
    # recompute robustly
    jstar=max(mm for mm in range(0,2000) if free_ratio(mm)<vs)
    kR=max(2*jstar+2, math.ceil(vs**(jstar+2)/a0(jstar+1)))
    # E_lower (Decimal upper-bound approach: compute as Decimal, then R as rational slightly above)
    Elow=sum(Decimal((a0(J+i)/a0(J)).numerator)/Decimal((a0(J+i)/a0(J)).denominator)*(-Decimal(i)).exp() for i in range(1,k0-jstar+1))
    r=Decimal(vs.numerator)/Decimal(vs.denominator)/E
    Einf=r*(1-r**k0)/(1-r)
    Rdec=max(1/(1+Elow),1/(1+Einf))
    # table R value as rational upper bound
    Rtab={501:Fr(24992,10**6),1855:Fr(8802,10**6),6098:Fr(5691,10**6)}[k0]
    xk0=Fr(k0,k0+1)**(k0-1)
    def qlow(kap): return max(Fr(0),1-sum(a0(j)*vs**(-(j+1)) for j in range(kap)))
    Xi=sum(max(Fr(0),a0(kap)*vs**(-(kap+1))-Rtab*qlow(kap)) for kap in range(J))
    Xik=sum(max(Fr(0),a0(kap)*xk0*vs**(-kap)-Rtab*qlow(kap)) for kap in range(J))
    A0=xk0+Xik/(vs*(1-Xi)); B0=Rtab*(1+Xik/(1-Xi))
    xi=Fr(1,k0)
    val=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"층 vs={vs} J={J} k0={k0}: j*={jstar} kR={kR} R(참)={Rdec:.6f} R(표)={float(Rtab)} Xi={float(Xi):.6f} Xi(k0)={float(Xik):.6f} A0={float(A0):.5f} B0={float(B0):.6f} | g_S/k^4={float(val):.4e} 꼭짓점/k^2={float(vert):.4f}<=y={float(y)} ; k0>=kR {k0>=kR}, J<=j* {J<=jstar}, Xi<1 {Xi<1}, x_k0={float(xk0):.4f}")
