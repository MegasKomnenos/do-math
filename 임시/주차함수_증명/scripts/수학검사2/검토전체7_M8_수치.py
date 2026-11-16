# 8장 수치 상수 재계산 (검토전체7 M8). python -I 로 실행.
import math
try:
    import mpmath as mp
    mp.mp.dps = 30
    F = mp.mpf
except Exception:
    mp = None
    F = float
def f(x): return F(x)
c = 1/mp.sqrt(2*mp.pi) if mp else 1/math.sqrt(2*math.pi)
sqrt = mp.sqrt if mp else math.sqrt
exp = mp.exp if mp else math.exp
log = mp.log if mp else math.log
z12 = f('-1.4603545088095868'); zm12 = f('-0.2078862249773545'); z32 = f('2.6123753486854883')
cpsi = -z12 + z32/12
print("c_Psi", cpsi)
k0 = f(6600)
eps0 = k0**(-f(1)/3)
print("eps0", eps0, "k^-2/3", k0**(-f(2)/3))
qmin = f('0.2')*k0**(f(2)/3); pmin = qmin-1
print("qmin", qmin, "pmin", pmin, "sqrt pmin", sqrt(pmin), "mu", 1/qmin, "xi eps max", f('6.001')*eps0)
mu = 1/qmin
print("(1-mu)^-1/2", (1-mu)**(-f(1)/2), "(1-mu)^-3/2", (1-mu)**(-f(3)/2))
# 9i >= 5(n+1) with i>=k+2, n+1 <= k+6k^{2/3}+1
for k in range(400, 430):
    kk=f(k)
    ok = 9*(kk+2) >= 5*(kk+6*kk**(f(2)/3)+1)
    if ok:
        print("9i>=5(n+1) holds from k =", k); break
# pieces-k-monotone R2
print("R2: (1+1/(4pmin))/(1-mu)", (1+1/(4*pmin))/(1-mu), " 3.5*k/(k+1)", f(3.5)*k0/(k0+1))
print("R2 sum", 2.5 + (1+1/(4*pmin))/(1-mu) - f(3.5)*k0/(k0+1) - f(2)/3)
# D3
print("D3: 1-cpsi/(2 sqrt pmin)", 1-cpsi/(2*sqrt(pmin)), "c_Psi<=", 1.46036+2.61238/12)
print("D3 sum", f('0.319921')/3 + 1/(3*(1-mu)*(1-cpsi/(2*sqrt(pmin)))) - f(2)/3)
# E
print("E: eps(1+xi eps) at xi=6.001", eps0*(1+f('6.001')*eps0), " 6xi^2 at 0.2", 6*f('0.04'))
# escape-y-monotone (나)
xi=f('0.2')
print("D1-D3 min", xi - k0**(-f(2)/3) - 3*c*sqrt(xi)*eps0)
# (라)
t1 = (f(1.5)*sqrt(xi) - f(0.5)/sqrt(xi)*k0**(-f(2)/3))/(2*c)
t2 = f(0.75)*eps0*(1+(1-1/(xi*k0**(f(2)/3)))**(-f(1)/2))
t3 = (k0+1)/(2*k0)*(1-1/(xi*k0**(f(2)/3)))**(-f(3)/2)/(xi**2*k0**(f(2)/3))
print("U' terms", t1, t2, t3, "sum", t1-t2-t3)
# (마)
a = (1+xi*eps0)/(12*xi**2*k0**(f(1)/3)); b = 3/(8*sqrt(xi)*k0**(f(1)/3))
print("V' terms", a, b, a+b, -0.5+a+b)
# jensen-H-ii
print("Lambda'(1)", 2.75+z12, " bracket p=1", -f(1)/6 - f(2)/3*z12 + zm12)
# table-lower-bound (가)
def s_fun(q): return f(4)/15*q**f(2.5) + f('0.385')*q**f(1.5)
def Cr(q,k): return f(1.5)*c*(k+q)**f(1.5)/(k+1)**f(3.5)*s_fun(q)
def Lam(q):
    p=q-1
    return q*(2*sqrt(p)+z12+1/(2*sqrt(p))) - (f(2)/3*p**f(1.5)+f(0.5)*sqrt(p)+zm12)
def Bp(q,k): return c*Lam(q)/(k+1)
def jinf(xi): return f(4)/3*c*xi**f(1.5)
print("jinf(0.2)", jinf(f('0.2')), "Cr(qmin,6600)", Cr(qmin,k0), "exp(-0.0477345)", exp(-f('0.0477345')))
E0 = 2*c/sqrt(xi)
num = 2*c/sqrt(xi)*(1+xi*eps0)
den = f('0.168623') + E0
print("q bound at 0.2:", num, den, num/den)
# envelope-code-monotone (나)
print("8.92e-6:", 2*c*sqrt(f('0.0005'))*f('0.0005'))
Ks = (2/f('0.0055'))**f(1.5)
print("Ks(0.0055)", Ks, "s(2)", s_fun(f(2)), "Cr(2,Ks)", Cr(f(2),Ks), "Cr(2e4,6.6e9)", Cr(f(2e4), f(6.6e9)))
# closed-form (가)
print("phi min", exp(-1/(12*qmin)), "rho1 max", f(1.5)*f('6.001')*eps0)
xi6=f('6.001')
rho2 = f(5)/8*(1+3/(4*pmin))*(1+xi6*eps0)**f(2.5)*xi6**2*k0**(-f(2)/3)
print("rho2 max", rho2, "V min", exp(-1/(12*qmin)) - f(1.5)*xi6*eps0 - rho2)
print("U max", xi6**f(1.5)/(2*c), (k0+1)/k0*(1-mu)**(-f(1)/2), xi6**f(1.5)/(2*c)+(k0+1)/k0*(1-mu)**(-f(1)/2))
print("quotient", f('0.3895139')/f('19.43183'))
# closed-form (나)
def brack(xi,k): return (f('0.4')*xi**f(1.5)+f('0.5775')*sqrt(xi)*k**(-f(2)/3))*(1+xi*k**(-f(1)/3))**f(1.5)
print("xi<=0.1:", brack(f('0.1'),k0), 1.46035-0.103945-0.041667-float(brack(f('0.1'),k0)))
q21 = f('2.1')*k0**(f(2)/3); print("q at 0.1:", f('0.1')*k0**(f(2)/3), (q21*0+f('0.1')*k0**(f(2)/3)-1)**(-f(1.5))/(12*f('0.1')*k0**(f(2)/3)))
print("xi=2.1 bracket:", brack(f('2.1'),k0), "zm/q", f('0.20789')/(f('0.1')*k0**(f(2)/3)))
print("margin 0.1-2.1:", 1.46035-0.005909-0.000012-float(brack(f('2.1'),k0)))
# (다)
q2 = 2*k0**(f(2)/3); p2=q2-1; mu2=1/q2
print("q>=", q2)
br = sqrt(1-mu2) - (1+p2**(-f(0.5)))*eps0/sqrt(f(2))
print("rho1' bracket/2", br/2, "dV/dk coeff", br/2-f(1)/3)
print("dtheta1", eps0/sqrt(f(2))/(3*c), "dtheta3", f(0.5)*(1+1/(4*p2)), "sum", eps0/sqrt(f(2))/(3*c)+f(0.5)*(1+1/(4*p2)))
print("V<1 bracket", f(0.5)-f(1.5)*mu2-f(0.75)*eps0/sqrt(f(2)))
xi2=f(2)
print("U>", 1+(xi2**f(1.5)-sqrt(xi2)*k0**(-f(2)/3))/(2*c) - f(1.5)*xi2*eps0)
print("log q' coeff", f('0.146751') - f('0.5316752')/f('4.37993'))
# (라) q_{6600,6600}(2), (2.1); full six pieces
def Psilow(r):
    if r<1: return f(0)
    return c*(2*sqrt(r)-cpsi+1/(2*sqrt(r))-r**(-f(1.5))/24)
def pieces(xi,k):
    q=xi*k**(f(2)/3); p=q-1; n=k+q; kk=k+1; e=k**(-f(1)/3)
    E=2*c*exp(-1/(12*q))/sqrt(xi)*(1+xi*e)
    R1=f(1.5)*c*(2*sqrt(p)-1)*k**(-f(2)/3)
    H=f(2)/3*p**f(1.5)+f(0.5)*sqrt(p)+zm12+1/(24*sqrt(p))
    R2=f(15)/8*c*n**f(2.5)*H/(kk**f(3.5)*k**(f(2)/3))
    D1=p/k**(f(2)/3)
    D2=kk*sqrt(2/mp.pi if mp else 2/math.pi)/sqrt(p)/k**(f(2)/3)
    D3=f(1.5)*kk*Psilow(p)/((n+1)*k**(f(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(xi,k); return (E-R1-R2)/(D1+D2-D3)
print("q6600(2)", qkk(f(2),k0), "exp(-jinf(2))", exp(-jinf(f(2))))
print("q6600(2.1)", qkk(f('2.1'),k0), "exp(-jinf(2.1))", exp(-jinf(f('2.1'))))
print("q6600(0.2)", qkk(f('0.2'),k0), " q6600(6.001)", qkk(f('6.001'),k0))
# table-tolerance
print("rG", f('0.38951')*f('0.7202')/f('19.4319')**2)
print("Lambda'(1)-0.85 sqrt2", 2.75+z12-f('0.85')*sqrt(f(2)))
print("0.339049:", f('0.85')*c*k0/(k0+1))
print("1.51e-3:", f('0.020044')*f('0.169524')*sqrt(f('0.2')), "3.61e-3:", f('0.953386')*f('0.169524')*sqrt(f('0.000499')))
print("rG*0.0004999", f('7.429e-4')*f('0.0004999'))
# hazard-H1
k7=f(6667)
print("1.1935:", 1.5-0.307*(1-1.5/6667), "z low", f(3)/32-f(0.75)*k7**(-f(1)/3)+f('0.53125')/k7)
def G(z): return f(1.5)*(1-z)-f('1.1935')*log(2/(1+z))-1/(1+z)+f(0.5)
print("G(0.0537)", G(f('0.0537')), "G(0.571)", G(f('0.571')), "3.2/k", f('3.2')/k7)
# old-6-29 k=6668
k8=6668; qmax=math.floor(6*k8**(2/3)); print("qmax(6668)", qmax, "k-2399>=qmax+300:", k8-2399>=qmax+300, "3k/4>=2398+qmax:", 0.75*k8>=2398+qmax)
qfb=math.floor((3*(k8-1)/4-qmax-3)/8); print("qfb(6668)", qfb, "(qfb+2)/k", (qfb+2)/k8, "6k^2/3<=k+3 at 6600:", 6*6600**(2/3)<=6603)
# explicit-bounds numerics
print("max B3/6:", (f(1)/(12*sqrt(f(3))))/6, "sqrt3/216", sqrt(f(3))/216)
print("c_Psi>=37/24", f(37)/24, "Psi_low(1)", Psilow(f(1)))
