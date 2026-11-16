# O10: 10장의 수치 주장(부동소수점 표본 검산)
import math
from math import log, exp, sqrt, pi, lgamma

def g(x): return (x-1)*log(1+1/x)
def gp(x): return log(1+1/x) - (x-1)/(x*(x+1))
def gpp(x): return -(3*x+1)/(x*x*(x+1)**2)

# 1. -g'' <= 3/x^3, g' bounds (2-26)
bad = [x for x in [i/7 for i in range(7, 70000)] if not (-gpp(x) <= 3/x**3 + 1e-15)]
print("1. -g''<=3/x^3 violations:", len(bad))
bad2 = [x for x in [1+i/10 for i in range(0, 100000)] if not ((3*x+1)/((2*x+1)*x*(x+1)) <= gp(x) + 1e-16 <= 3/(2*x*x) + 2e-16)]
print("   g' two-sided bound violations:", len(bad2))
bad3 = [x for x in [1+i/10 for i in range(0, 100000)] if (3*x+1)/((2*x+1)*x*(x+1)) < 3/(2*(x+1)**2) - 1e-16]
print("   lower bound >= 3/(2(x+1)^2) violations:", len(bad3))

# 2. M-natural step 1: inc^- - inc^+ <= (3/2)[1/((k-1+q)(k+q)) - 1/((k-1+d)(k+d))] and <= 3j/((k-1+q)^2 (k-1+d)); kappa bound
k = 6667
worst1 = worst2 = worst3 = -1
import random
random.seed(1)
pairs = [(q, d) for d in range(2, 60) for q in range(1, d)] + [(random.randint(1, 6667), random.randint(2, 6668)) for _ in range(20000)]
pairs = [(q, d) for (q, d) in pairs if q < d]
for q, d in pairs:
    j = d - q
    incm = g(k-1+d) - g(k-1+q); incp = g(k+d) - g(k+q)
    diff = incm - incp
    b1 = 1.5*(1/((k-1+q)*(k+q)) - 1/((k-1+d)*(k+d)))
    b2 = 3*j/((k-1+q)**2*(k-1+d))
    kap = exp(incm) + exp(-incp) - 2
    b3 = b2*(1 + 0.7501*j/(k-1+d))
    worst1 = max(worst1, diff/b1); worst2 = max(worst2, diff/b2); worst3 = max(worst3, kap/b3)
print("2. max ratios: (inc- - inc+)/text-intermediate =", worst1, "; /final =", worst2, "; kappa/bound =", worst3)
# tilt bound
def Bor(m): return exp(-m + (m-1)*log(m) - lgamma(m+1))
w = -1
for q, d in pairs[:3000]:
    t = Bor(k+q)/Bor(k+d); w = max(w, t/((k-1+d)/(k-1+q))**1.5)
print("   tilt/bound max:", w)

# 3. old-8-25 step 7 constants
def coefE(u, q): return 2/sqrt(2*pi)*(0.25*(1-1/(2*q))**-1.5 + (1+u+u*u)*(1-u)**-0.5*(1+u)**-1.5)
print("3. E coef max u<=0.9, q=113:", max(coefE(u, 113) for u in [i/10000 for i in range(1, 9001)]))
print("   E coef max u in (0.9,0.99], q=113:", max(coefE(u, 113) for u in [0.9+i/100000 for i in range(1, 9001)]))
print("   E coef max u in (0.99,0.9999], q=113:", max(coefE(u, 113) for u in [0.99+i/1000000 for i in range(1, 9901)]))
def F(u): return 2/sqrt(2*pi)*(1+2*u*u)*sqrt(1-u*u)
print("   F max:", max(F(u) for u in [i/100000 for i in range(1, 100000)]), " 2/sqrt(pi)=", 2/sqrt(pi))
print("   F on (0.9,0.99]:", max(F(u) for u in [0.9+i/100000 for i in range(1, 9001)]), "F on (0.99,0.9999]:", max(F(u) for u in [0.99+i/1000000 for i in range(1, 9901)]))
print("   (1.15*6666)^(2/3)=", (1.15*6666)**(2/3), " (1.2*1000)^(2/3)=", (1.2*1000)**(2/3))
print("   1.1284+2.82/389=", 1.1284+2.82/389, " 1.1284+2.82/113=", 1.1284+2.82/113, " 1.044+9.3/113=", 1.044+9.3/113, " 0.34+85/113=", 0.34+85/113)
# theta_1 root of (1-t)^{5/2} - 1 + 2t
f = lambda t: (1-t)**2.5 - 1 + 2*t
lo, hi = 0.1, 0.5
for _ in range(100):
    mid = (lo+hi)/2
    if f(mid) < 0: lo = mid
    else: hi = mid
print("   theta_1 =", lo)
# v(theta) <= 1.6 theta for theta <= 0.02
print("   max v/theta on (0,0.02]:", max(((1-t)**-1.5-1)/t for t in [i/100000 for i in range(1, 2001)]))

# 4. old-8-34 constants
print("4. 2(2pi)^{-1/2}(1-1/206)^{-1/2}=", 2/sqrt(2*pi)*(1-1/206)**-0.5)

# 5. old-8-32 (iii) constants
cR = sqrt(2*pi)/2*exp(1/12)
print("5. c_R=", cR, " beta0 min=", cR*1.04**1.5/sqrt(2), " g^e(1.0216)=", exp(-1.0216)*(1+1.5*1.0216), " iota q0 max=", cR*2**(2/3)/6669**(1/3))
print("   beta2 range:", cR*1.04**1.5, cR*2, " sqrt(1/2+1/562)=", sqrt(0.5+1/562))
ge_p = lambda t: exp(-t)*(0.5-1.5*t)
print("   min |ge'| on [1.02,2.73]:", min(abs(ge_p(1.02+i*0.00001)) for i in range(0, 171001)))

# 6. family table constants
for kk, name in [(9705, "1a"), (9551, "1b"), (8065, "2")]:
    print("6.", name, kk, "20001-2k=", 20001-2*kk, " 1.3k^(2/3)=", 1.3*kk**(2/3), " 2k^(2/3)=", 2*kk**(2/3), " 0.48k=", 0.48*kk)
for kk in [6668, 8065, 9551, 9705]:
    print("   eps0(", kk, ")=", math.floor(2**(2/3)*(kk+1)**(2/3)))
print("   theta_0=", (2*exp(-0.48)-1)*exp(-0.48))
# bulk u(k), Bd^T etc at 8065 for family 2 o_F
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5/sqrt(k)
def BdT(k, nu): return (k+nu)*u(k)*(1/(k-1)+1/k) + 3*(k+1)*(k-1)**-1.5
def sup(d, y, m=1.15): return min(1, m*(y+d)/d**1.5)
k=8065; print("   fam2: 3 s^up=", 3*sup(2*k**(2/3)+1, k+1), " BdT(k,.48k)=", BdT(k, 0.48*k))
k=9551; xi2 = 2*k**(2/3)/(k-1); print("   fam1b: 3 s^up=", 3*sup(1.3*k**(2/3)+1, k+1), " theta part=", (2*exp(-xi2)-1)*exp(-xi2), " BdT=", BdT(k, 2*k**(2/3)))
k=9705; nup=1.3*k**(2/3); ec = 3*nup**2/((k-1)*k) + 4.8*sqrt(nup)/k + nup**2/(2*(k-1)**2); print("   fam1a: e^c=", ec, " BdT=", BdT(k, nup))
k=6668; mh = math.ceil(sqrt(5*k*log(k))); xip = (sqrt(5*k*log(k))+2)/k
ebar = exp(1.5/k)*(exp(sqrt(5*log(k)/k)+1/k) + 2.40918*k**(1.5-2.5/(1+xip)))
print("   bulk: ebar=", ebar, " m_hit=", mh, " 0.09k=", 0.09*k, " abar=", 3*1.15*(1.48*k+2)/(0.48*k+1)**1.5, " bbar=", 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**-1.5, " dbar=", 72.217/sqrt(k))
print("   pi_two const: ", 1/sqrt(2*pi)/math.e*2**1.5*exp(-1/(12*6667)-1/(12*3200)))
print("   bracket at nu/k=0.48:", 0.48**-0.5 - 1 + (1-sqrt(0.48))/3, " *132.32=", 132.32*(0.48**-0.5 - 1 + (1-sqrt(0.48))/3))
# 7. 10.3 table thresholds
print("7. k=8064: 20001-2k=", 20001-2*8064, " 0.48k=", 0.48*8064, "; k=8065:", 20001-2*8065, 0.48*8065, "; k=9948:", 20001-2*9948, "; k=9949:", 20001-2*9949)
# 8. reduction-ga (i): 0.99+0.59963(2k+1)^{2/3}+1.24847(2k+1)^{1/3} < (2k)^{2/3} at 2k=13334
x = 13335; print("8.", 0.99+0.59963*x**(2/3)+1.24847*x**(1/3), "<", 13334**(2/3))
# 9. M-natural: bracket >= 3.246 ; rho_0, iota_0
k=6667; print("9. 1.5log2 + 2.528571 - log(1.3751) =", 1.5*log(2)+2.528571-log(1.3751), "; rho0=", math.floor(2*k**(2/3))/k, "; q(rho0)=", 1+0.7501*0.10635/1.10635)
d_nat = 2*k**(2/3); print("   iota0 check:", 2.528571 - log(1.0722) + 1.5*log(math.floor(d_nat)) - log(k), " exp(-iota0/1.5)=", exp(-3.4964/1.5))
print("   first term coefficient 2^(7/2)=", 2**3.5, " 1.6/3.5=", 1.6/3.5, " 3sqrt2*0.16696=", 3*sqrt(2)*0.16696, " 2.5-log2-log0.485917=", 2.5-log(2)-log(0.485917), " sqrt(sqrt2*0.16696)=", sqrt(sqrt(2)*0.16696))
print("   j1+j2(0.5 log 6667 -1)=", 0.7998716+2.7171998*(0.5*log(6667)-1))
# 10. row-3k numbers
print("10. 2*0.7654=", 2*0.7654, ">=1.3502")
# 11. 10.4 (5): k>=6667: 0.48k vs 1.5(2k+3)^{2/3}
print("11. 0.48*6667=", 0.48*6667, " 1.5(2k+3)^(2/3)=", 1.5*(2*6667+3)**(2/3), "; 0.6*6666-1=", 0.6*6666-1, " 1.5(2*6666+3)^(2/3)=", 1.5*(2*6666+3)**(2/3))
# 12. old-8-33 (ii) constants
cAb = lambda r: 2*sqrt(r)/(1-r) + 2*log((1+sqrt(r))/(1-sqrt(r)))
print("12. 2cAb(0.6)-4/sqrt(0.6)=", 2*cAb(0.6)-4/sqrt(0.6))
_N=2000000; _a=sqrt(0.6); _h=_a/_N; _tot=sum(2*(1+((i+0.5)*_h)**2)/(1-((i+0.5)*_h)**2)**2 for i in range(_N))*_h
print("   Sub max int_0^0.6 (1+r)r^-1/2(1-r)^-2 =", _tot, "(r=s^2 치환, 중점 합)")
# 13. mathfrak a_y < 2y^{2/3}
y=6666; print("13. (2y^(2/3))^(3/2)=2^1.5 y=", 2**1.5*y, " vs 1.15(y+2y^(2/3))=", 1.15*(y+2*y**(2/3)))
# 14. 10.5 after old-8-18 : inc^+ bound
print("14. e^{inc-} at k=6667 max:", exp(1.5/6667), " (1+e)/2 =", (1+exp(1.5/6667))/2, " 2.25*that=", 2.25*(1+exp(1.5/6667))/2)

# 15. 2항의 배정밀도 결과는 g(x)=(x-1)log(1+1/x)의 상쇄 오차 때문에 믿을 수 없다(차 자체가 ~3/(k+q)^3 ~ 1e-12). mpmath 50자리로 다시 잰다.
from mpmath import mp, mpf, log as mlog, exp as mexp, loggamma
mp.dps = 50
def gm(x):
    x = mpf(x); return (x-1)*mlog(1+1/x)
k = 6667
import random
random.seed(1)
pairs = [(q, d) for d in range(2, 60) for q in range(1, d)] + [(random.randint(1, 6667), random.randint(2, 6668)) for _ in range(20000)]
pairs = [(q, d) for (q, d) in pairs if q < d] + [(6667, 6668), (1, 6668), (1, 2)]
w1 = w2 = w3 = (mpf(-1), None)
for q, d in pairs:
    j = d - q
    incm = gm(k-1+d) - gm(k-1+q); incp = gm(k+d) - gm(k+q)
    diff = incm - incp
    b1 = mpf(3)/2*(mpf(1)/((k-1+q)*(k+q)) - mpf(1)/((k-1+d)*(k+d)))
    b2 = mpf(3)*j/((k-1+q)**2*(k-1+d))
    kap = mexp(incm) + mexp(-incp) - 2
    b3 = b2*(1 + mpf('0.7501')*j/(k-1+d))
    if diff/b1 > w1[0]: w1 = (diff/b1, (q, d))
    if diff/b2 > w2[0]: w2 = (diff/b2, (q, d))
    if kap/b3 > w3[0]: w3 = (kap/b3, (q, d))
print("15. mpmath 50자리: (inc- - inc+)/본문 중간식 최대", mp.nstr(w1[0], 8), w1[1], "; /마지막 꼴 최대", mp.nstr(w2[0], 8), w2[1], "; kappa/상계 최대", mp.nstr(w3[0], 8), w3[1])
def Borm(m):
    m = mpf(m); return mexp(-m + (m-1)*mlog(m) - loggamma(m+1))
wt = mpf(0); wa = mpf(0)
for q, d in pairs[:6000]:
    t_ = Borm(k+q)/Borm(k+d); wt = max(wt, t_/((mpf(k-1+d))/(k-1+q))**mpf(1.5))
    incm = gm(k-1+d) - gm(k-1+q); incp = gm(k+d) - gm(k+q)
    kap = mexp(incm) + mexp(-incp) - 2
    Acrit = (k-1)*kap/(2*(1-mexp(-incp)))
    qd = 1 + mpf('0.7501')*(d-1)/(k-1+d)
    wa = max(wa, Acrit/(mpf('1.00057')*qd))
print("    tilt/상계 최대", mp.nstr(wt, 10), "; Acrit/(1.00057 q_d) 최대", mp.nstr(wa, 8))
