# J6 검산: 7.1 t_k, 열 인증 (가)의 정수 부등식, 정리 self-consistent-S의 표, 따름정리 cor-S-prime의 값
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
import math
getcontext().prec = 60

def t_k(k):
    j = 0
    while not ((k+1)**j * k**(j+1) + (k-1)**(2*j+1) >= 2*k**(2*j+1)):
        j += 1
    return j
print("t_k:", {k: t_k(k) for k in (2,3,5,10,41,100,501,2000)})
print("n_sharp_501 =", 501 + 502*t_k(501))

# 열 인증 (가): 10^21*400^10 > 17^21*123^10
L = 10**21 * 400**10; R = 17**21 * 123**10
print("column (가) integer check:", L > R, L, R)
print("phi_sharp(1.7) lower bound - 2 :", 1.7 + (40/41)*(10/17)**2.1 - 2)

# 정리 S 표
def a_circ(m):  # p_m/m! = (m+1)^(m-1)/m!
    return Fr(1) if m == 0 else Fr((m+1)**(m-1), math.factorial(m))
def g_exp(m):   # e^{g(m+1)} = (1+1/(m+1))^m as Fraction
    return Fr(m+2, m+1)**m
def jstar(Lf):
    m = 0
    while g_exp(m+1) < Lf: m += 1
    # m is max with g_exp(m) < Lf? recheck: want max m with e^{g(m+1)} < L
    m = 0
    while g_exp(m) < Lf: m += 1
    return m-1
def kR(Lf, js):
    val = Lf**(js+2) / a_circ(js+1)
    return max(2*js+2, math.ceil(val))

E = Decimal(1).exp()
def layer(Lf, J, k0, xk_k0=None):
    js = jstar(Lf); kr = kR(Lf, js)
    # E_under
    Eu = sum(Decimal(a_circ(J+i).numerator)/Decimal(a_circ(J+i).denominator)/ (Decimal(a_circ(J).numerator)/Decimal(a_circ(J).denominator)) * (-Decimal(i)).exp() for i in range(1, k0-js+1))
    Ld = Decimal(Lf.numerator)/Decimal(Lf.denominator)
    r = Ld/E
    Einf = r*(1-r**k0)/(1-r)
    RJ = max(1/(1+Eu), 1/(1+Einf))
    xbar = [a_circ(v)*Lf**(-(v+1)) for v in range(J)]
    qun = [max(Fr(0), 1 - sum(a_circ(j)*Lf**(-(j+1)) for j in range(v))) for v in range(J)]
    RJf = Fr(RJ)  # exact of decimal (upper-ish)
    Xi = sum(max(Fr(0), xbar[v] - RJf*qun[v]) for v in range(J))
    xk0 = Fr(k0, k0+1)**(k0-1)
    Xik = sum(max(Fr(0), a_circ(v)*xk0*Lf**(-v) - RJf*qun[v]) for v in range(J))
    A0 = xk0 + Xik/(Lf*(1-Xi))
    B0 = RJf*(1+Xik/(1-Xi))
    return dict(jstar=js, kR=kr, RJ=float(RJ), Xi=float(Xi), Xik=float(Xik), A0=float(A0), B0=float(B0), A0f=A0, B0f=B0, xk0=xk0)

layers = [(Fr(267,100),25,501,Fr(13,100)),(Fr(27,10),70,1855,Fr(2,25)),(Fr(271,100),100,6098,Fr(11,200))]
for Lf,J,k0,y in layers:
    d = layer(Lf,J,k0)
    print(f"L={Lf} J={J} k0={k0}: j*={d['jstar']} kR={d['kR']} RJ={d['RJ']:.6f} Xi={d['Xi']:.6f} Xi(k0)={d['Xik']:.6f} A0={d['A0']:.5f} B0={d['B0']:.6f}")
    xi = Fr(1,k0); A0=d['A0f']; B0=d['B0f']
    nv = ((3*xi+xi**2)/2 + (1+xi)**2*B0/2)
    gval = (y-xi)*(y-2*xi-xi**2) - (1+xi)**2*(A0*xi+B0*y)
    print(f"   n_v/k^2={float(nv):.5f} (<= y={float(y)}), g_S(yk^2)/k^4={float(gval):.4e}")
    # with table rounded values
    tab = {501:(Fr(14708,10000),Fr(98505,1000000)),1855:(Fr(25335,10000),Fr(60259,1000000)),6098:(Fr(27354,10000),Fr(422,10000))}[k0]
    gval2 = (y-xi)*(y-2*xi-xi**2) - (1+xi)**2*(tab[0]*xi+tab[1]*y)
    print(f"   with table A0,B0: {float(gval2):.4e}")
