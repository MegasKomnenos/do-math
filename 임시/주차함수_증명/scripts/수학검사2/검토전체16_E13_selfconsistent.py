# E13: 부록 D.self-consistent-constants 표와 따름정리 cor-S-prime 세 값의 재계산
from fractions import Fraction as F
from math import factorial
import mpmath as mp
mp.mp.dps = 60

def ac(m):  # 𝔞°_m = (m+1)^{m-1}/m!
    return F((m+1)**(m-1), factorial(m)) if m >= 1 else F(1)

def jstar(L):
    m = 0
    while ac(m+1)/ac(m) < L:
        m += 1
    return m-1 if m > 0 else 0  # max m with ratio(m+1)/ratio(m) < L

def kR(L, j):
    v = L**(j+2)/ac(j+1)
    import math
    return max(2*j+2, math.ceil(v))

def xk(k):
    return F(k, k+1)**(k-1)

for (L, J, k0, y) in [(F(267,100),25,501,F(13,100)), (F(27,10),70,1855,F(2,25)), (F(271,100),100,6098,F(11,200))]:
    j = jstar(L)
    # check definition directly: e^{g(j+1)}<L and e^{g(j+2)}>=L
    assert ac(j+1)/ac(j) < L <= ac(j+2)/ac(j+1)
    kr = kR(L, j)
    # E_J lower, E_inf with intervals
    ei = mp.iv.mpf(1)/mp.iv.exp(1)
    EJ = mp.iv.mpf(0)
    for i in range(1, k0-j+1):
        EJ += (lambda f: mp.iv.mpf(f.numerator)/mp.iv.mpf(f.denominator))(ac(J+i)/ac(J)) * ei**i
    Le = (mp.iv.mpf(L.numerator)/mp.iv.mpf(L.denominator))*ei
    Einf = Le*(1-Le**k0)/(1-Le)
    RJ_iv = mp.iv.mpf(1)/(1+EJ)
    RJ2 = mp.iv.mpf(1)/(1+Einf)
    RJ_up = max(mp.mpf(RJ_iv.b), mp.mpf(RJ2.b))
    # rational above
    RJ = F(str(mp.nstr(RJ_up, 40, strip_zeros=False))) + F(1, 10**30)
    assert RJ > F(str(mp.nstr(RJ_up, 60, strip_zeros=False)))
    fall = [ac(x)*L**(-(x+1)) for x in range(J)]
    q = [max(F(0), 1-sum(ac(jj)*L**(-(jj+1)) for jj in range(x))) for x in range(J)]
    Xi = sum(max(F(0), fall[x]-RJ*q[x]) for x in range(J))
    Xk = sum(max(F(0), ac(x)*xk(k0)*L**(-x)-RJ*q[x]) for x in range(J))
    A0 = xk(k0)+Xk/(L*(1-Xi))
    B0 = RJ*(1+Xk/(1-Xi))
    xi = F(1, k0)
    val = (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    vert = (3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={L} J={J} k0={k0}: j*={j} kR={kr} RJ={float(RJ):.10f} Xi={float(Xi):.8f} Xi(k0)={float(Xk):.8f} A0={float(A0):.6f} B0={float(B0):.8f}")
    print(f"   cor value={float(val):.6e}  vertex={float(vert):.6f} <= y={float(y)}: {vert<=y}")
    # with table ceilings
    tabA = {501:F(14708,10000),1855:F(25335,10000),6098:F(27354,10000)}[k0]
    tabB = {501:F(98505,10**6),1855:F(60259,10**6),6098:F(422,10**4)}[k0]
    val2 = (y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(tabA*xi+tabB*y)
    print(f"   with table ceilings: {float(val2):.6e}")
