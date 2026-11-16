# H6 검산: 정리 self-consistent-S (다)의 표와 따름정리 cor-S-prime의 세 값, t_k / n#_k / n♭_k
from fractions import Fraction as F
from math import factorial, exp, log, ceil
import mpmath as mp
mp.mp.dps = 60

def a0(m):  # 자유 계수 (m+1)^{m-1}/m!
    return F((m+1)**(m-1), factorial(m)) if m>=1 else F(1)

def free_ratio(m):  # e^{g(m+1)} = a0(m+1)/a0(m)
    return a0(m+1)/a0(m)

def jstar(L):
    m=0
    while free_ratio(m) < L: m+=1
    return m-1

def xk(k): return F(k,k+1)**(k-1)

ranges=[(F(267,100),25,501,F(13,100)),(F(27,10),70,1855,F(2,25)),(F(271,100),100,6098,F(11,200))]
E=mp.e
for L,J,k0,y in ranges:
    js=jstar(L)
    kR=max(2*js+2, ceil(L**(js+2)/a0(js+1)))
    # E_J lower, E_inf (with mp, upper for R)
    EJ=mp.mpf(0)
    for i in range(1,k0-js+1):
        EJ+= mp.mpf((a0(J+i)/a0(J)).numerator)/mp.mpf((a0(J+i)/a0(J)).denominator)*mp.e**(-i)
    Le=mp.mpf(L.numerator)/L.denominator/E
    Einf=Le*(1-Le**k0)/(1-Le)
    R=max(1/(1+EJ),1/(1+Einf))
    Rq=F(str(mp.nstr(R,12)))  # 유리수 올림 근사
    if Rq < F(str(mp.nstr(R,30))): Rq=F(str(mp.nstr(R,30)))+F(1,10**12)
    fall=[a0(kp)*L**(-(kp+1)) for kp in range(J)]
    q=[max(F(0),1-sum(a0(j)*L**(-(j+1)) for j in range(kp))) for kp in range(J)]
    Xi=sum(max(F(0),fall[kp]-Rq*q[kp]) for kp in range(J))
    Xik=sum(max(F(0),a0(kp)*xk(k0)*L**(-kp)-Rq*q[kp]) for kp in range(J))
    A0=xk(k0)+Xik/(L*(1-Xi)); B0=Rq*(1+Xik/(1-Xi))
    xi=F(1,k0)
    val=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R={mp.nstr(R,10)} Xi={float(Xi):.6f} Xi(k0)={float(Xik):.6f} A0={float(A0):.5f} B0={float(B0):.6f} val={float(val):.4e} vertex/k^2={float(vert):.5f} <= y={float(y)}")

def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
def nsharp(k): return k+(k+1)*tk(k)
def phi(k,n):
    ms=F(n-k,k+1); x=float(xk(k))
    return (1+1/k)**float(ms)+(1-1/k)**(float(ms)+x*n/k)-2
def nflat(k):
    n=2*k+1
    while phi(k,n)<0: n+=1
    return n
for k in [2,3,10,41,120,500,501,840,841,1000,2000,2001]:
    print(k, "t_k=",tk(k), "n#=",nsharp(k), "n♭=",nflat(k), "2k^1.5=",2*k**1.5, "0.13k^2=",0.13*k*k)
