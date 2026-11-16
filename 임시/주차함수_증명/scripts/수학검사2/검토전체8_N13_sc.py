# D.self-consistent-constants: 세 층 상수와 따름정리의 세 값을 정의에서 다시 계산한다(정확 유리수 + Decimal e^{-i}).
import sys, io
from fractions import Fraction as F
from decimal import Decimal, getcontext
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
getcontext().prec = 60
from math import factorial
def ao(m): return F(1) if m==0 else F((m+1)**(m-1), factorial(m))
def jstar(L):
    m=0
    while ao(m+1)/ao(m) < L: m+=1
    return m-1 if m>0 else None  # max m with ratio(m)<L : loop breaks at first m failing, so answer m-1... careful
def jstar2(L):
    best=None; m=0
    while True:
        if ao(m+1)/ao(m) < L: best=m
        else: break
        m+=1
    return best
E = Decimal(1).exp()
def Dec(fr): return Decimal(fr.numerator)/Decimal(fr.denominator)
layers=[(F(267,100),25,501,F(13,100)),(F(27,10),70,1855,F(2,25)),(F(271,100),100,6098,F(11,200))]
for (L,J,k0,y) in layers:
    js = jstar2(L)
    kR = max(2*js+2, -(-(L**(js+2)/ao(js+1)).numerator // (L**(js+2)/ao(js+1)).denominator))
    # E_J lower = sum_{i=1}^{k0-js} a°_{J+i}/a°_J e^{-i}
    EJ = Decimal(0); aJ = ao(J)
    for i in range(1, k0-js+1):
        EJ += Dec(ao(J+i)/aJ) * (-Decimal(i)).exp()
    Le = Dec(L)/E
    Einf = Le*(1-Le**k0)/(1-Le)
    RJ = max(1/(1+EJ), 1/(1+Einf))
    # Xi, Xi^(k0): use RJ rounded up to rational slightly above
    RJr = F(str(RJ.quantize(Decimal('1e-30'))))+F(1,10**30)
    xk0 = F(k0, k0+1)**(k0-1)  # x_k = (k/(k+1))^{k-1}
    Xi = F(0); Xik = F(0)
    for kap in range(0,J):
        xbar = ao(kap)*L**(-(kap+1))
        qlo = max(F(0), 1-sum(ao(j)*L**(-(j+1)) for j in range(kap)))
        Xi += max(F(0), xbar - RJr*qlo)
        Xik += max(F(0), ao(kap)*xk0*L**(-kap) - RJr*qlo)
    A0 = xk0 + Xik/(L*(1-Xi)); B0 = RJr*(1+Xik/(1-Xi))
    xi = F(1,k0)
    val = (y-xi)*(y-2*xi-xi**2) - (1+xi)**2*(A0*xi+B0*y)
    vert = (3*xi+xi**2)/2 + (1+xi)**2*B0/2
    print("L=%s J=%d k0=%d: j*=%d kR=%d RJ=%.6f Xi=%.6f Xi(k0)=%.6f A0=%.5f B0=%.6f val=%.4e vertex=%.4f<=%s" % (L,J,k0,js,kR,float(RJ),float(Xi),float(Xik),float(A0),float(B0),float(val),float(vert),y))
