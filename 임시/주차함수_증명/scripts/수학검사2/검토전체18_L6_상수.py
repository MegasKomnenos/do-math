# L6 검산: 7.2절 자기일관 상계 표의 상수, 열 인증의 정수 부등식, hf(17/10), t_k 등
from fractions import Fraction as Fr
from math import log, exp, e, factorial, ceil
import mpmath as mp
mp.mp.dps = 40

def a0(m):  # 자유 계수 (m+1)^{m-1}/m!
    return Fr((m+1)**(m-1), factorial(m)) if m>=1 else Fr(1)

def jstar(L):
    m=0
    while True:
        r = a0(m+1)/a0(m)   # e^{g(m+1)}
        if r >= L: return m-1
        m+=1

def kR(L):
    j=jstar(L)
    return max(2*j+2, ceil(L**(j+2)/a0(j+1)))

def xk(k): return Fr(k, k+1)**(k-1)

out=[]
for (L,J,k0,yv) in [(Fr(267,100),25,501,Fr(13,100)),(Fr(27,10),70,1855,Fr(2,25)),(Fr(271,100),100,6098,Fr(11,200))]:
    j=jstar(L); kr=kR(L)
    Lm=mp.mpf(L.numerator)/L.denominator
    Eund = sum(mp.mpf((a0(J+i)/a0(J)).numerator)/ (a0(J+i)/a0(J)).denominator * mp.e**(-i) for i in range(1,k0-j+1))
    Einf = (Lm/mp.e)*(1-(Lm/mp.e)**k0)/(1-Lm/mp.e)
    R = max(1/(1+Eund), 1/(1+Einf))
    Rf = Fr(str(mp.nstr(R,12)))  # 근사 유리수(표 대조용)
    fall=[a0(x)*L**(-(x+1)) for x in range(J)]
    qund=[max(Fr(0), 1-sum(a0(jj)*L**(-(jj+1)) for jj in range(x))) for x in range(J)]
    Xi=sum(max(Fr(0), fall[x]-Rf*qund[x]) for x in range(J))
    Xik=sum(max(Fr(0), a0(x)*xk(k0)*L**(-x)-Rf*qund[x]) for x in range(J))
    A0=xk(k0)+Xik/(L*(1-Xi)); B0=Rf*(1+Xik/(1-Xi))
    xi=Fr(1,k0)
    val=(yv-xi)*(yv-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*yv)
    vert=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    out.append((float(L),j,kr,float(R),float(Xi),float(Xik),float(A0),float(B0),float(val),float(vert), float(yv*k0*k0-2*k0-1)))
for o in out: print(o)
# 정수 부등식
print(10**21*400**10 > 17**21*123**10, 10**21*400**10, 17**21*123**10)
# hf(17/10) at k=41
k=41; ok=-2*log(1-1/k)/log(1+1/k); print("o_41",ok, 1.7+(1-1/k)*1.7**(-ok)-2, (40/41)*(10/17)**2.1)
# t_k for some k, n^sharp_k, n^flat_k
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in [2,3,5,10,100,501,1000]:
    t=tk(k); print(k,t,k+(k+1)*t)
