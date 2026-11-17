# R9: independent double-precision recomputation of the 9.6 family tables (check-na, check-ga)
import math
from math import log, exp, sqrt, pi, lgamma, floor, ceil
mS = 1.15
f1 = 4/(3*sqrt(2*pi)); cR = sqrt(2*pi)/2*exp(1/12)
print("f1", f1, "cR", cR)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def BdT(k, nu): return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
def DDLn(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k))+37.6/(5*sqrt(pi)*k)
def sup(d, y): return min(1.0, mS*(y+d)/d**1.5)
def ec(k, nu): return 3*nu*nu/((k-1)*k)+4.8*sqrt(nu)/k+nu*nu/(2*(k-1)**2)
def cAb(r): return 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
def quad(f, a, b, n=200000):
    # composite Simpson
    h = (b-a)/n; s = f(a)+f(b)
    for i in range(1, n):
        s += f(a+i*h)*(4 if i % 2 else 2)
    return s*h/3
def Sub(k, nub):
    xi = (nub+4)/(k-1)
    if xi >= 0.6: return 0.0
    return (k-1)/k*quad(lambda r: (r-xi)*(1+r)*r**-1.5*(1-r)**-2, xi, 0.6, 20000)
def Top(k, nub):
    return quad(lambda r: min(2, 2+(nub+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1.0, 20000)
def Flat(y):
    a = (mS*(y+2*y**(2/3)))**(2/3)
    return 2*(a-1)/(y+2-a)
def Ab(y, k, nub):
    z = 0.6+1/y
    return mS*(1+1/y)*(4*((mS*y)**(2/3)-1)**-0.5+y**-0.5*(2*cAb(z)-4*z**-0.5-Sub(k, nub)))
def StaysUp(k, nub, parts=False):
    fl = [Flat(y) for y in (k-1, k)]; ab = [Ab(y, k, nub) for y in (k-1, k)]; tp = 2*16.54*k**-0.5*Top(k, nub)
    if parts: print("   Flat", fl, "Ab", ab, "Top-part", tp)
    return sum(fl)+sum(ab)+tp
def ebar(k):
    xi = (sqrt(5*k*log(k))+2)/k
    return exp(3/(2*k))*(exp(sqrt(5*log(k)/k)+1/k)+2.40918*k**(1.5-2.5/(1+xi)))
abar = lambda k: 3*1.15*(1.48*k+2)/(0.48*k+1)**1.5
bbar = lambda k: 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**-1.5
dbar = lambda k: 72.217/sqrt(k)
th0 = (2*exp(-0.48)-1)*exp(-0.48)
print("theta0", th0, " 2/sqrt(2pi)/e*2^1.5 =", (2*pi)**-0.5/math.e*2**1.5, 1/0.41508)
print("132.32*bracket(0.48) =", 132.32*(0.48**-0.5-1+(1-sqrt(0.48))/3), 0.48**-0.5-1+(1-sqrt(0.48))/3)
# first columns
def first_col(cap, lo=6668):
    k = lo
    while not (max(103, 20001-2*k) <= cap(k)): k += 1
    return k
print("first cols", first_col(lambda k: 1.3*k**(2/3)), first_col(lambda k: 2*k**(2/3)), first_col(lambda k: 0.48*k), first_col(lambda k: k-1))
for k in (9705, 9704, 9551, 9550, 8065, 8064):
    print(k, 20001-2*k, 1.3*k**(2/3), 2*k**(2/3), 0.48*k)
res = {}
# bulk
k = 6668
print("bulk", 4-ebar(k), ebar(k), abar(k), bbar(k), DDLn(k), dbar(k), abar(k)+bbar(k)+DDLn(k)+dbar(k), "sum+ebar", abar(k)+bbar(k)+DDLn(k)+dbar(k)+ebar(k))
res['bulk'] = (k, abar(k)+bbar(k)+DDLn(k)+dbar(k), None)
k = 8065; t = k**(2/3)
print("fam2", 3*sup(2*t+1, k+1), th0, BdT(k, 0.48*k), DDLn(k), "o=", 4-3*sup(2*t+1, k+1)+th0-BdT(k, 0.48*k)-DDLn(k), "Stays", StaysUp(k, 0.48*k))
res['2'] = (k, 3*sup(2*t+1, k+1)+BdT(k, 0.48*k)+DDLn(k)+StaysUp(k, 0.48*k), None)
k = 9551; t = k**(2/3); xi2 = 2*t/(k-1)
print("fam1b", 3*sup(1.3*t+1, k+1), (2*exp(-xi2)-1)*exp(-xi2), BdT(k, 2*t), DDLn(k), "o=", 4-3*sup(1.3*t+1, k+1)+(2*exp(-xi2)-1)*exp(-xi2)-BdT(k, 2*t)-DDLn(k), "Stays", StaysUp(k, 2*t))
res['1b'] = (k, 3*sup(1.3*t+1, k+1)+BdT(k, 2*t)+DDLn(k)+StaysUp(k, 2*t), BdT(k, 2*t)+DDLn(k)+StaysUp(k, 2*t))
k = 9705; t = k**(2/3)
print("fam1a", ec(k, 1.3*t), BdT(k, 1.3*t), DDLn(k), "o=", 2-ec(k, 1.3*t)-BdT(k, 1.3*t)-DDLn(k), "Stays", StaysUp(k, 1.3*t, True))
res['1a'] = (k, 3+BdT(k, 1.3*t)+DDLn(k)+StaysUp(k, 1.3*t), BdT(k, 1.3*t)+DDLn(k)+StaysUp(k, 1.3*t))
# (ga): chain recursion
def lBor(m): return -m+(m-1)*log(m)-lgamma(m+1)
def surv(y, qmax):
    # s[q] = frak s_q(y), q=1..qmax
    lb = [0.0]+[lBor(j) for j in range(1, qmax+1)]
    lby = [lBor(y+q) for q in range(0, qmax+1)]
    s = [0.0, 1.0]
    for q in range(2, qmax+1):
        tot = 0.0; acc = 0.0
        for qp in range(1, q):
            pr = exp(lb[q-qp]+lby[qp]-lby[q])
            tot += pr; acc += pr*y/(y+qp)*s[qp]
        s.append(1-tot+acc)
    return s
def slow(d, y): return exp(-f1*((y+d-1)/y)**1.5*d**1.5/y)
def Q(y, xi):
    k = y-1; q0 = xi*y**(2/3)
    pre = k/(k+1)*(1-q0/(2*k))*2*(2*pi)**-0.5*exp(-1/12)*y/(cR*q0)
    return pre*(exp(-q0/y)*slow(q0, y)*(exp(-cR*q0/y)-exp(-cR*q0*sqrt(q0/2)/y))+exp(-q0/(2*y))*slow(q0/2, y)*(exp(-cR*q0*sqrt(q0/2+1)/y)-exp(-cR*q0**1.5/y)))
Bor = lambda j: exp(lBor(j))
for fam in ('bulk', '2', '1b', '1a'):
    k0, R, Rp = res[fam]; y = k0+1
    e0 = floor(2**(2/3)*(k0+1)**(2/3))
    sy = surv(y, e0+1); sk = surv(k0, e0+2)
    cumB = [0.0]
    for j in range(1, e0+2): cumB.append(cumB[-1]+Bor(j))
    best = (1e9, None); bestp = (1e9, None)
    for q0 in range(2, e0+1):
        z = 0.0
        for q in range(1, q0):
            l = q0-q
            Aup = sqrt(2*pi)/4*exp(1/(12*l))*(q0+q)*sqrt(l)
            z += (2*pi)**-0.5*l**-0.5*exp(-1/(12*l))*exp(-(q+Aup)/y)*sy[q]
        eR = k0/(k0+1)*(1-q0/(2*k0))*(max(z, sy[q0]-(1-cumB[q0-1]))+Bor(q0))
        el = 4*sk[q0+1]+2*eR
        if el-R < best[0]: best = (el-R, q0)
        if Rp is not None and q0 >= 104 and eR+sk[q0+1]-Rp < bestp[0]: bestp = (eR+sk[q0+1]-Rp, q0)
    xc = 1.3 if fam == '1a' else 2**(2/3)
    edge = 4*slow(xc*y**(2/3)+1, k0)+2*Q(y, xc)-R
    line = [fam, k0, "eps0", e0, "R#", round(R, 6), "(a)min", round(best[0], 6), "at", best[1], "(b)", round(edge, 6)]
    if Rp is not None:
        xc2 = 2**(2/3)
        line += ["R#'", round(Rp, 6), "(a')", round(bestp[0], 6), "at", bestp[1], "(b')", round(Q(y, xc2)+slow(xc2*y**(2/3)+1, k0)-Rp, 6)]
    print(*line)
