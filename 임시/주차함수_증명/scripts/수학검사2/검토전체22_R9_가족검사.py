# 검토 22차 R9: 9.6절 명제 check-na 표와 주변 수치의 독립 재계산 (mpmath, 50자리)
from mpmath import mp, mpf, sqrt, log, exp, pi, quad, floor, ceil, e
mp.dps = 40
mS = mpf('1.15')

def u(k):
    k = mpf(k)
    return mpf(3)/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**mpf('-1.5')*k**mpf('-0.5')
def DDLn(k):
    k = mpf(k)
    return 14*(log(3*k)-1)/(5*sqrt(pi*k)) + mpf('37.6')/(5*sqrt(pi)*k)
def BdT(k, nu):
    k = mpf(k)
    return (k+nu)*u(k)*(1/(k-1)+1/k) + 3*(k+1)*(k-1)**mpf('-1.5')
def sup(d, y):
    return min(mpf(1), mS*(y+d)/mpf(d)**mpf('1.5'))
def ec(k, nup):
    k = mpf(k)
    return 3*nup**2/((k-1)*k) + mpf('4.8')*sqrt(nup)/k + nup**2/(2*(k-1)**2)
def ebar(k):
    k = mpf(k)
    xi = (sqrt(5*k*log(k))+2)/k
    return exp(3/(2*k))*(exp(sqrt(5*log(k)/k)+1/k) + mpf('2.40918')*k**(mpf('1.5')-mpf('2.5')/(1+xi)))
def abar(k):
    k = mpf(k)
    return 3*mS*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**mpf('1.5')
def bbar(k):
    k = mpf(k)
    return 2*u(k)*(2*k-1)/(k-1) + 3*(k+1)*(k-1)**mpf('-1.5')
def dbar(k):
    return mpf('72.217')/sqrt(mpf(k))

def cAb(r):
    return 2*sqrt(r)/(1-r) + 2*log((1+sqrt(r))/(1-sqrt(r)))
def Sub(k, nub):
    k = mpf(k)
    xs = (nub+4)/(k-1)
    if xs >= mpf('0.6'):
        return mpf(0)
    return (k-1)/k*quad(lambda r: (r-xs)*(1+r)*r**mpf('-1.5')*(1-r)**-2, [xs, mpf('0.6')])
def Top(k, nub):
    k = mpf(k)
    lo = mpf('0.6')-mpf('2.6')/k
    kink = (nub+1)/k
    f = lambda r: min(mpf(2), 2+(nub+1)/k-r)*(1+r/3)*r**mpf('-1.5')
    pts = [lo, 1] if kink <= lo or kink >= 1 else [lo, kink, 1]
    return quad(f, pts)
def Flat(y):
    y = mpf(y)
    a = (mS*(y+2*y**(mpf(2)/3)))**(mpf(2)/3)
    return 2*(a-1)/(y+2-a)
def Ab(y, k, nub):
    y = mpf(y)
    z = mpf('0.6')+1/y
    return mS*(1+1/y)*(4*((mS*y)**(mpf(2)/3)-1)**mpf('-0.5') + y**mpf('-0.5')*(2*cAb(z)-4*z**mpf('-0.5')-Sub(k, nub)))
def StaysUp(k, nub):
    return sum(Flat(y)+Ab(y, k, nub) for y in (k-1, k)) + 2*mpf('16.54')*mpf(k)**mpf('-0.5')*Top(k, nub)

def show(name, v): print(f"{name:40s} {mp.nstr(v, 12)}")

print("== 벌크 k0=6668 ==")
k = 6668
show("ebar", ebar(k)); show("4-ebar", 4-ebar(k))
show("abar", abar(k)); show("bbar", bbar(k)); show("DDL", DDLn(k)); show("dbar", dbar(k))
tot = abar(k)+bbar(k)+DDLn(k)+dbar(k)
show("sum", tot); show("margin", 4-ebar(k)-tot); show("sum+ebar", tot+ebar(k))

print("== 가족 2 k0=8065 ==")
k = 8065; kk = mpf(k); c = kk**(mpf(2)/3)
t1 = 3*sup(2*c+1, kk+1); th0 = (2*exp(mpf('-0.48'))-1)*exp(mpf('-0.48'))
show("3 s_up", t1); show("theta0", th0); show("BdT(k,0.48k)", BdT(k, mpf('0.48')*kk)); show("DDL", DDLn(k))
oF = 4-t1+th0-BdT(k, mpf('0.48')*kk)-DDLn(k); show("o_F", oF)
su = StaysUp(k, mpf('0.48')*kk); show("StaysUp", su); show("margin", oF-su)

print("== 가족 1b k0=9551 ==")
k = 9551; kk = mpf(k); c = kk**(mpf(2)/3)
t1 = 3*sup(mpf('1.3')*c+1, kk+1); xi2 = 2*c/(kk-1); th = (2*exp(-xi2)-1)*exp(-xi2)
show("3 s_up", t1); show("theta piece", th); show("BdT(k,2k^2/3)", BdT(k, 2*c)); show("DDL", DDLn(k))
oF = 4-t1+th-BdT(k, 2*c)-DDLn(k); show("o_F", oF)
su = StaysUp(k, 2*c); show("StaysUp", su); show("margin", oF-su)

print("== 가족 1a k0=9705 ==")
k = 9705; kk = mpf(k); c = kk**(mpf(2)/3)
show("ec", ec(k, mpf('1.3')*c)); show("BdT(k,1.3k^2/3)", BdT(k, mpf('1.3')*c)); show("DDL", DDLn(k))
oF = 2-ec(k, mpf('1.3')*c)-BdT(k, mpf('1.3')*c)-DDLn(k); show("o_F", oF)
su = StaysUp(k, mpf('1.3')*c); show("StaysUp", su); show("margin", oF-su)

print("== 가족 첫 열 ==")
for name, kk0, f in [("1a", 9705, lambda k: mpf('1.3')*mpf(k)**(mpf(2)/3)), ("1b", 9551, lambda k: 2*mpf(k)**(mpf(2)/3)), ("2", 8065, lambda k: mpf('0.48')*k)]:
    for k in (kk0-1, kk0):
        print(name, k, 20001-2*k, mp.nstr(f(k), 8), 20001-2*k <= f(k))
print("== DDL 값 ==")
for k in (2001, 6668, 8065, 9551, 9705): show(f"DDL({k})", DDLn(k))
print("u(2001)", mp.nstr(u(2001), 8))
