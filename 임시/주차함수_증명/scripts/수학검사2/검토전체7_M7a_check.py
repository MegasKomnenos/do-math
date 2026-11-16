# -*- coding: utf-8 -*-
"""M7a 검산: 장7B.md 7.4–7.5절의 수치·식 확인."""
from fractions import Fraction as Fr
import math
import sympy as sp

print("=== (a) pair-check-10000: 경우 수와 최솟값 ===")
k = 10000
def pis(q): return Fr(q*(q-1), 2*(k+1))
def exbar(q):
    p = pis(q); return q + (k+q)*p/(1-p)
cnt = 0; best = None
for q in range(1, 49):
    for qp in range(q, 50):
        if q+qp > 50: break
        for j in range(0, 51-q-qp):
            cnt += 1
            v = 1 - Fr(j,k)*(exbar(q)+exbar(qp)) - (exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or v < best[0]: best = (v, q, qp, j)
print("count(q<=q')=", cnt, " min=", float(best[0]), best[1:])
cnt2 = sum(1 for q in range(1,50) for qp in range(1,50) for j in range(0,51) if q+qp+j<=50)
print("ordered count=", cnt2)

print("=== (b) C*M^{3/2} ===")
for K1,M,C in [(10**4,120,0.54),(2*10**4,250,0.593),(10**5,300,0.522),(10**5,450,0.548),(10**6,700,0.519)]:
    print(K1,M,C, round(C*M**1.5,1), C*M**1.5 < K1)

print("=== (c) nu_P(K1) (float, sanity) ===")
def nuP(K1,M,C):
    def nhat(q): return 0.0 if q==1 else C*q**1.5/K1
    def exh(q): n=nhat(q); return q+(K1+q)*n/(1-n)
    ex=[0]+[exh(q) for q in range(1,M+1)]
    nu=1
    while True:
        ok=True; worst=None
        for q in range(1,nu):
            qp_max=nu-q
            for qp in range(1,qp_max+1):
                if q>M or qp>M: ok=False; break
                j=nu-q-qp
                lb=1-(j/K1)*(ex[q]+ex[qp])-(ex[q]*(qp-1)+ex[qp]*(q-1))/(2*K1)
                if worst is None or lb<worst[0]: worst=(lb,q,qp,j)
                if lb<=0: ok=False
            if not ok: break
        if not ok: return nu-1, worst
        nu+=1
for K1,M,C in [(12000,120,0.54),(13000,120,0.54),(14000,120,0.54),(15000,120,0.54),(20000,120,0.54),(30000,250,0.593),(50000,250,0.593),(10**5,300,0.522)]:
    r,w=nuP(K1,M,C); print(K1, "nu_P=",r, "fail at", r+1, "worst", w)

print("=== (d) n_X(2002) ===")
import mpmath as mp
mp.mp.dps=40
v=mp.mpf(2002)**(mp.mpf(4)/3); print(v, math.ceil(v))
print("n_X(3130)=", mp.ceil(mp.mpf(3130)**(mp.mpf(4)/3)), " 3k+1=", 3*3130+1)

print("=== (e) n_M ratios ===")
print(20507/841**1.5, 73032/2000**1.5)

print("=== (f) Hermite U_r, V_r via backward recurrence (sympy) ===")
n,d,nu,kk,y,th = sp.symbols('n d nu k y theta')
# He_{j-1} = (N He_j - He_{j+1})/(y j);  He_n/He_{n-1} = n + d
N = n + y + 1
He_n = sp.Symbol('He_n'); He_nm1 = He_n/(n+d)
He = {n: He_n, n-1: He_nm1}
def Hem(i):  # He_{n-i}
    if i==0: return He[n]
    if i==1: return He[n-1]
    # He_{n-i} = (N He_{n-i+1} - He_{n-i+2})/(y (n-i+1))
    return sp.simplify((N*Hem(i-1) - Hem(i-2))/(y*(n-i+1)))
def Mr(r):  # n! [Y^n] (1-Y)^{r+1} B(Y) = sum_i C(r+1,i)(-1)^i n!/(n-i)! He_{n-i}
    s=0
    for i in range(r+2):
        s += sp.binomial(r+1,i)*(-1)**i*sp.ff(n,i)*Hem(i)
    return sp.simplify(s)
M0=Mr(0); M2=Mr(2); M4=Mr(4)
ratio2=sp.simplify(M2/M0); ratio4=sp.simplify(M4/M0)
# general y formula check: 1 - 2n/y + n(n+1)/y^2 - n(n+1)/(y^2 d)
print("M2/M0 general check:", sp.simplify(ratio2 - (1-2*n/y+n*(n+1)/y**2-n*(n+1)/(y**2*d))))
r2k = sp.simplify(ratio2.subs({y:kk, n:2*kk+nu}))
U2 = 1+(2*nu+2)/kk+nu*(nu+1)/kk**2; V2 = 4+(4*nu+2)/kk+nu*(nu+1)/kk**2
print("U2-V2/d check:", sp.simplify(r2k-(U2-V2/d)))
r4k = sp.simplify(ratio4.subs({y:kk, n:2*kk+nu}))
U4 = 1+(4*nu+16)/kk+(6*nu**2+30*nu+18)/kk**2+(4*nu**3+17*nu**2+15*nu+2)/kk**3+nu*(nu+1)**3/kk**4
V4 = 4+(12*nu+38)/kk+(13*nu**2+49*nu+22)/kk**2+(6*nu**3+21*nu**2+17*nu+2)/kk**3+nu*(nu+1)**3/kk**4
print("U4-V4/d check:", sp.simplify(r4k-(U4-V4/d)))

print("=== (g) H_0,H_1,H_2 via series ===")
w = sp.symbols('w')  # w = 1/k
Nk = 3+(nu+1-th)*w
xfr = w*(1-th*w)/Nk**2
xn = (2+(nu-1)*w)*(1-th*w)/Nk**2
gam = sp.sqrt(1-4*xn)
ups = (1+gam)/2
C1 = (1-ups)/gam**2; C2 = -(1-ups)*(2+ups)/gam**5; C3 = 5*(1-ups)*(6+gam-gam**2)/(2*gam**8)
uhat = ups + xfr*C1 + xfr**2*C2 + xfr**3*C3
Hexpr = (Nk*uhat - 2 - nu*w)/w
ser = sp.series(Hexpr, w, 0, 3).removeO()
ser = sp.expand(ser)
for j in range(3):
    print("H_%d ="%j, sp.factor(sp.expand(ser.coeff(w,j))))
nm = sp.expand(sp.simplify((1-4*xn)*Nk**2))
print("nm =", sp.collect(nm, w))
print("=== (h) (마) k-coefficient 20 ===")
dy = 4 + (-(26+4*nu)-8*th)*w  # d_y to first order
expr = (2*kk+nu)*(2*kk+nu+1) - dy.subs(w,1/kk)*((kk+nu+th)**2 + 2*kk+nu)
print(sp.Poly(sp.expand(expr*kk), kk).coeff_monomial(kk**2))  # coefficient of k after multiplying by k? simpler:
e2 = sp.expand(expr)
print("coeff k^2:", e2.coeff(kk,2), " coeff k:", sp.simplify(e2.coeff(kk,1)))

print("=== (i) ke algebra ===")
s,m = sp.symbols('s m', positive=True)
wv = s+1; J = wv/(m+1)
lhs = wv + (m+1)*(-J+J**2/2+J**3/6+J**4/(12*(1-J))) + (J+J**2/(2*(1-J))) - s*(s+1)/(2*(m+1)) - s*(s+1)*(2*s+1)/(12*(m+1)**2)
ke = 3*(s+1)/(2*(m+1)) + (s+1)*(3*s+2)/(12*(m+1)**2) + (s+1)**2/(2*(m+1)*(m-s)) + (s+1)**4/(12*(m+1)**2*(m-s))
print("ke check:", sp.simplify(lhs-ke))

print("=== (j) counts 44380, 200170 ===")
c1=sum(max(0,2*k_+40-max(20001,2*k_+1)+1) for k_ in range(9981,11100)); print(c1)
c2=sum(max(0,2*k_+102-max(2*k_+41,20001)+1) for k_ in range(9950,12000)); c3=44*1000+23*1000+7*1000; print(c2,c3,c2+c3)

print("=== (k) polar-PD numbers ===")
print(2*math.exp(-5.3146*0.6996), 0.3**1.5/2, 0.0821*math.exp(-3/25233), 0.7*2001/2002)
x=sp.symbols('x'); print("varsigma needed:", sp.nsolve(2*sp.exp(-x*0.6996)-0.0820, x, 4.5))

print("=== (l) misc ===")
print("9400 const:", 2e7*3.07/9**4, " 1.50005^1.5=", 1.50005**1.5, " *2/sqrt(pi)=", 1.84*2/math.sqrt(math.pi), " Bn:", 2.08/math.sqrt(2*math.pi))
print("3+601/1e4=",3+601/1e4)
# (7.12) check for (1e4,120,0.54) at q=120 in floats
K1,M,C=10**4,120,0.54
keb=3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
def Bor(j): return math.exp(-j+ (j-1)*math.log(j) - math.lgamma(j+1))
def F(q): return C*q**1.5 - math.exp(keb)*sum(Bor(s+1)*((q-1-s)+C*(q-1-s)**1.5) for s in range(0,q-1))
print("kebar=",keb, " min F/(Cq^1.5) over q=2..M:", min(F(q)/(C*q**1.5) for q in range(2,M+1)))
# g_k approx monotonic check: g_k = 2 - k*(U2 - V2/d) with d from series H0+H1/k+H2/k^2 (theta=0)
for nu_ in [1,19,40,102,600]:
    for k_ in [1e4,2e4,1e5,1e6]:
        H1=-(26+4*nu_); H2=506+97*nu_+5*nu_**2
        d_=4+H1/k_+H2/k_**2
        U2_=1+(2*nu_+2)/k_+nu_*(nu_+1)/k_**2; V2_=4+(4*nu_+2)/k_+nu_*(nu_+1)/k_**2
        g=2-k_*(U2_-V2_/d_)
        print("nu",nu_,"k",k_,"g_k~",round(g,5), end=" | ")
    print()

print("=== (m) H_3 and lower bound d >= 4-(26+4nu)/k at theta=0 ===")
ser4 = sp.expand(sp.series(Hexpr.subs(th,0), w, 0, 4).removeO())
H3 = sp.expand(ser4.coeff(w,3)); print("H_3(theta=0) =", sp.factor(H3))
for nu_ in [1,102,600]:
    for k_ in [1e4,1.5e4]:
        H1=-(26+4*nu_); H2=float(sp.expand(ser4.coeff(w,2)).subs(nu,nu_)); H3v=float(H3.subs(nu,nu_))
        low = 4 + H1/k_ + (H2-20)/k_**2 + H3v/k_**3
        print("nu",nu_,"k",k_," d_low-(4+H1/k) =", (H2-20)/k_**2 + H3v/k_**3, " H2=",H2," H3=",H3v)
