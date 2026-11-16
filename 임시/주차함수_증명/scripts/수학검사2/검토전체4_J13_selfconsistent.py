# 정리 self-consistent-S (다)의 표와 따름정리 S' 세 값을 본문 정의대로 다시 계산한다.
from fractions import Fraction as F
from math import factorial
import mpmath as mp
mp.mp.dps = 60
def ac(m):  # a°_m = (m+1)^{m-1}/m!
    return F((m+1)**(m-1), factorial(m)) if m >= 1 else F(1)
def jstar(L):
    m = 0
    while ac(m+1)/ac(m) < L: m += 1
    return m-1 if m>0 else -1
def ceil_frac(x): return -((-x.numerator)//x.denominator)
def xk(k): return F(k, k+1)**(k-1)
def tier(L, J, k0, yy):
    js = jstar(L)
    kR = max(2*js+2, ceil_frac(L**(js+2)/ac(js+1)))
    # E_J lower bound with interval e^{-i}
    Elow = mp.mpf(0)
    for i in range(1, k0-js+1):
        Elow += (lambda f: mp.mpf(f.numerator)/mp.mpf(f.denominator))(ac(J+i)/ac(J)) * mp.iv.exp(-mp.iv.mpf(i)).a
    Linf_low = mp.iv.mpf(L.numerator)/mp.iv.mpf(L.denominator)/mp.iv.e
    q = Linf_low
    Einf_low = (q*(1-q**k0)/(1-q)).a
    R_upper = max(1/(1+Elow), 1/(1+Einf_low))
    # rational above
    R = F(str(mp.nstr(R_upper, 7, min_fixed=-1, max_fixed=1)))  # 7 sig digits
    if R <= F(str(mp.nstr(R_upper, 30))): R = R + F(1, 10**8)
    xbar = [ac(v)*L**(-(v+1)) for v in range(J)]
    qlow = [max(F(0), 1 - sum(ac(j)*L**(-(j+1)) for j in range(v))) for v in range(J)]
    Xi = sum(max(F(0), xbar[v] - R*qlow[v]) for v in range(J))
    x0 = xk(k0)
    Xik = sum(max(F(0), ac(v)*x0*L**(-v) - R*qlow[v]) for v in range(J))
    A0 = x0 + Xik/(L*(1-Xi)); B0 = R*(1+Xik/(1-Xi))
    xi = F(1, k0)
    g = (yy-xi)*(yy-2*xi-xi**2) - (1+xi)**2*(A0*xi+B0*yy)
    vertex = (3*xi+xi**2)/2 + (1+xi)**2*B0/2
    return js, kR, R, Xi, Xik, A0, B0, g, vertex
tiers = [(F(267,100),25,501,F(13,100),F(14708,10000),F(98505,10**6)),
         (F(27,10),70,1855,F(2,25),F(25335,10000),F(60259,10**6)),
         (F(271,100),100,6098,F(11,200),F(27354,10000),F(422,10**4))]
for L,J,k0,yy,A0t,B0t in tiers:
    js,kR,R,Xi,Xik,A0,B0,g,vx = tier(L,J,k0,yy)
    xi = F(1,k0)
    gt = (yy-xi)*(yy-2*xi-xi**2) - (1+xi)**2*(A0t*xi+B0t*yy)
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R<={float(R):.7f} Xi={float(Xi):.6f} Xi^k0={float(Xik):.6f} A0={float(A0):.6f} B0={float(B0):.7f} g={float(g):.4e} g(table)={float(gt):.4e} vertex={float(vx):.5f} Xi<1:{Xi<1}")
