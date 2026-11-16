# H13 검산: 부록 D 7A 항목의 수치
from fractions import Fraction as Fr
from math import ceil, log, exp, factorial, floor
import mpmath as mp
mp.mp.dps = 60

# (a) D.column-certification-k500 비교 수
def counts(ks):
    dd = rr = 0
    for k in ks:
        B = -(-k*k//4)
        dd += 2*B - (2*k+1) + 1
        rr += 2*B - B + 1
    return dd, rr
print("직접 차분/비 비교 수 121-160:", counts(range(121,161)))
print("직접 차분/비 비교 수 161-500:", counts(range(161,501)))
# (b) 정수 부등식
L = 10**21*400**10; R = 17**21*123**10
print("정수 부등식:", L > R, "%.6e %.6e" % (L, R), "17^21=%.4e 123^10=%.4e" % (17**21, 123**10))
# (d) n_X
for k in (501, 2002, 2001):
    v = mp.mpf(k)**(mp.mpf(4)/3)
    print("n_X(%d) = ceil(%s) = %d" % (k, mp.nstr(v, 20), int(mp.ceil(v))))
# (e) polar-PD numbers
print("2e^{-5.3146*0.6996} =", mp.nstr(2*mp.e**(-5.3146*0.6996), 8), " 0.0821 e^{-3/25233} =", mp.nstr(mp.mpf('0.0821')*mp.e**(-mp.mpf(3)/25233), 8), " 0.3^1.5/2 =", mp.nstr(mp.mpf('0.3')**1.5/2, 8))
print("0.7*2001/2002 =", mp.nstr(mp.mpf(0.7)*2001/2002, 8))
# (c) 자기일관 상수
def a0(m):  # a°_m = (m+1)^{m-1}/m!
    return Fr(m+1)**(m-1)/factorial(m)
def jstar(L):
    m = 0
    while a0(m+1)/a0(m) < L:
        m += 1
    return m-1 if not (a0(m+1)/a0(m) < L) else m
def kR(L, js):
    c2 = L**(js+2)/a0(js+1)
    return max(2*js+2, ceil(c2))
E = mp.e
def consts(L, J, k0):
    js = jstar(L); kr = kR(L, js)
    # E_J lower with mpmath interval for e^{-i}
    EJ = mp.mpf(0)
    for i in range(1, k0-js+1):
        EJ += mp.mpf(a0(J+i).numerator)/mp.mpf(a0(J+i).denominator)/ (mp.mpf(a0(J).numerator)/mp.mpf(a0(J).denominator)) * mp.e**(-i)
    Le = mp.mpf(L.numerator)/L.denominator/mp.e
    Einf = Le*(1-Le**k0)/(1-Le)
    RJ = max(1/(1+EJ), 1/(1+Einf))
    RJr = Fr(str(mp.nstr(RJ, 30)))  # 유리수로
    RJr = RJr + Fr(1, 10**28)  # 위로
    fall = [a0(x)*L**(-(x+1)) for x in range(J)]
    q = []
    for x in range(J):
        s = sum(a0(j)*L**(-(j+1)) for j in range(x))
        q.append(max(Fr(0), 1-s))
    Xi = sum(max(Fr(0), fall[x]-RJr*q[x]) for x in range(J))
    xk = Fr(k0**(k0-1), (k0+1)**(k0-1))
    Xik = sum(max(Fr(0), a0(x)*xk*L**(-x)-RJr*q[x]) for x in range(J))
    A0 = xk + Xik/(L*(1-Xi)); B0 = RJr*(1+Xik/(1-Xi))
    return js, kr, RJ, float(Xi), float(Xik), float(A0), float(B0), A0, B0
def corval(y, k0, A0, B0):
    xi = Fr(1, k0)
    return (y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y), (3*xi+xi*xi)/2+(1+xi)**2*B0/2
for (L, J, k0, y) in ((Fr(267,100),25,501,Fr(13,100)), (Fr(27,10),70,1855,Fr(2,25)), (Fr(271,100),100,6098,Fr(11,200))):
    js, kr, RJ, Xi, Xik, A0, B0, A0r, B0r = consts(L, J, k0)
    v, vert = corval(y, k0, A0r, B0r)
    print("L=%s J=%d k0=%d: j*=%d k_R=%d R_J=%s Xi=%.6f Xi(k0)=%.6f A0=%.5f B0=%.6f  따름값=%.4e 꼭짓점=%.5f<=%.4f" % (L, J, k0, js, kr, mp.nstr(RJ, 10), Xi, Xik, A0, B0, float(v), float(vert), float(y)))
# 표 올림값으로 세 값
for (k0, y, A0, B0) in ((501, Fr(13,100), Fr(14708,10000), Fr(98505,10**6)), (1855, Fr(2,25), Fr(25335,10000), Fr(60259,10**6)), (6098, Fr(11,200), Fr(27354,10000), Fr(422,10000))):
    v, vert = corval(y, k0, A0, B0)
    print("표 올림값 k0=%d: 값=%.5e 꼭짓점=%.6f" % (k0, float(v), float(vert)))
