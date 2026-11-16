# T6 검산: 7.1절 t_k, 7.2절 열 인증 (가)의 수치, 정리 self-consistent-S 표의 상수, 따름정리 S'의 값
from fractions import Fraction as Fr
from math import factorial, exp, log, e
import math

def tk(k):
    j=0
    while True:
        if (k+1)**j * k**(j+1) + (k-1)**(2*j+1) >= 2*k**(2*j+1): return j
        j+=1
print("t_k:", {k:tk(k) for k in [2,3,5,10,100,501,2000,2001,3130]})
# 열 인증 (가)
print("hf check 10^21*400^10 > 17^21*123^10:", 10**21*400**10 > 17**21*123**10, 10**21*400**10, 17**21*123**10)
print("17^21=",17**21, " 123^10=",123**10)
print("(40/41)(10/17)^2.1 =", (40/41)*(10/17)**2.1)

def a0(m): # 자유 계수 (m+1)^{m-1}/m!
    return Fr((m+1)**(m-1), factorial(m)) if m>=1 else Fr(1)
def freeratio(m): # e^{g(m+1)} = a0(m+1)/a0(m)
    return a0(m+1)/a0(m)
def jstar(L):
    m=0
    while freeratio(m) < L: m+=1
    return m-1
def kR(L):
    j=jstar(L)
    return max(2*j+2, math.ceil(L**(j+2)/a0(j+1)))
for L,J,k0,yy in [(Fr(267,100),25,501,Fr(13,100)),(Fr(27,10),70,1855,Fr(2,25)),(Fr(271,100),100,6098,Fr(11,200))]:
    j=jstar(L); kr=kR(L)
    Lf=float(L)
    def lga0(m):
        return (m-1)*math.log(m+1)-math.lgamma(m+1) if m>=1 else 0.0
    Elow=sum(exp(lga0(J+i)-lga0(J)-i) for i in range(1,k0-j+1))
    Einf=(Lf/e)*(1-(Lf/e)**k0)/(1-Lf/e)
    R=max(1/(1+Elow),1/(1+Einf))
    fall=[float(a0(x))*Lf**(-(x+1)) for x in range(J)]
    qlow=[max(0.0,1-sum(float(a0(jj))*Lf**(-(jj+1)) for jj in range(x))) for x in range(J)]
    Xi=sum(max(0.0,fall[x]-R*qlow[x]) for x in range(J))
    xk=(k0/(k0+1))**(k0-1)
    Xik=sum(max(0.0,float(a0(x))*xk*Lf**(-x)-R*qlow[x]) for x in range(J))
    A0=xk+Xik/(Lf*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    xi=1/k0; y=float(yy)
    g=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    nv=((3/k0+1/k0**2)/2+(1+xi)**2*B0/2)
    print(f"L={L} J={J} k0={k0}: j*={j} kR={kr} R={R:.8f} Xi={Xi:.6f} Xik0={Xik:.6f} A0={A0:.5f} B0={B0:.6f} g_S/k^4={g:.4e} nv/k^2={nv:.4f} y k0^2-2k0-1={y*k0*k0-2*k0-1:.1f}")
