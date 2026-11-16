# K13: 부록 D 7A 항목의 수치 검산
from fractions import Fraction as Fr
from math import ceil, log, factorial
import mpmath as mp
mp.mp.dps = 60

print("== 정수 부등식 10^21*400^10 > 17^21*123^10")
L = 10**21 * 400**10; R = 17**21 * 123**10
print(L, R, L > R, "%.6e %.6e" % (L, R))

print("== n_X(2002), n_X(501)")
for k in (501, 2002, 5000):
    v = mp.mpf(k)**(mp.mpf(4)/3)
    print(k, v, int(mp.ceil(v)))

print("== 열 인증 비교 수")
def counts(ks):
    dd = 0; bb = 0
    for k in ks:
        B = -(-k*k//4)
        dd += 2*B - (2*k+1) + 1
        bb += 2*B - B + 1
    return dd, bb
print("121-160", counts(range(121,161)))
print("161-500", counts(range(161,501)))

print("== 자기일관 상수")
def ao(m):  # a°_m = (m+1)^{m-1}/m!
    return Fr(m+1)**(m-1)/factorial(m)
def jstar(Lf):
    m = 0
    while True:
        r = ao(m+1)/ao(m)
        if not (r < Lf): return m-1
        m += 1
tiers = [(Fr(267,100),25,501),(Fr(27,10),70,1855),(Fr(271,100),100,6098)]
ys = [Fr(13,100),Fr(2,25),Fr(11,200)]
for (Lf,J,k0),y in zip(tiers,ys):
    j = jstar(Lf)
    kR = max(2*j+2, ceil(Lf**(j+2)/ao(j+1)))
    # E_J lower
    e_inv = mp.e**-1
    EJ = mp.mpf(0)
    for i in range(1, k0-j+1):
        fr=ao(J+i)/ao(J); EJ += mp.mpf(fr.numerator)/mp.mpf(fr.denominator) * e_inv**i
    Le = mp.mpf(Lf.numerator)/mp.mpf(Lf.denominator)/mp.e
    Einf = Le*(1-Le**k0)/(1-Le)
    RJ = max(1/(1+EJ), 1/(1+Einf))
    RJr = Fr(str(mp.nstr(RJ, 30)))  # rational >= RJ approx (close)
    # use slightly larger rational
    RJr = RJr + Fr(1,10**25)
    xb = [ao(v)*Lf**(-(v+1)) for v in range(J)]
    q = []
    for v in range(J):
        s = sum(ao(jj)*Lf**(-(jj+1)) for jj in range(v))
        q.append(max(Fr(0), 1-s))
    Xi = sum(max(Fr(0), xb[v]-RJr*q[v]) for v in range(J))
    xk = Fr(k0, k0+1)**(k0-1)
    Xik = sum(max(Fr(0), ao(v)*xk*Lf**(-v)-RJr*q[v]) for v in range(J))
    A0 = xk + Xik/(Lf*(1-Xi))
    B0 = RJr*(1+Xik/(1-Xi))
    print("tier L=%s J=%d k0=%d: j*=%d kR=%d RJ=%s Xi=%.6f Xik=%.6f A0=%.5f B0=%.6f" % (Lf,J,k0,j,kR,mp.nstr(RJ,8),float(Xi),float(Xik),float(A0),float(B0)))
    xi = Fr(1,k0)
    val = (y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    vert = (3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print("   S' value=%.4e vertex=%.5f <= y=%.4f : %s" % (float(val), float(vert), float(y), vert<=y))
    print("   y k0^2 - 2k0 - 1 =", float(y*k0*k0-2*k0-1))
