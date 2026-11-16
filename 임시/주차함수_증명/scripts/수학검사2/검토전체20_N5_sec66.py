# 6.6절 수치 재계산: u(k), d(k), Obar, Low, Psi(14), Fr 인자, (6.49), (6.50)
from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, ceil
mp.dps = 30
def u(k): k=mpf(k); return (3/mpf('0.35'))*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def ups(k): k=mpf(k); return mpf(1)/2+5/(2*k)+1/(4*k*k)
gW = 2*exp(mpf('0.0031'))/e
def dd(k): return gW*ups(k)+u(k)/(e*2**mpf(1.5))
print("u(3131)", u(3131), "2u", 2*u(3131))
print("gW", gW, "gW*ups(3131)", gW*ups(3131), "u/(e 2^1.5) @3131", u(3131)/(e*2**mpf(1.5)))
print("d(3131)", dd(3131), "d(10001)", dd(10001))
def Obar(k,dp1_over_k): k=mpf(k); return dd(k)*exp(1+1/(12*k))*(1+dp1_over_k)**mpf(1.5)
print("Obar far-window @10001", Obar(10001, mpf('1.4')*mpf(10001)**(-mpf(1)/3)+1/mpf(10001)))
print("Obar small-k (나) @3131", Obar(3131, mpf('0.75')*mpf(3131)**(-mpf(1)/3)+1/mpf(3131)))
c=1/sqrt(2*pi)
def Low(k,rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3)
    br=2*sqrt(rho)-mpf('2.218')*eps
    return c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf(1.5)*exp(1/(4*(k+1)))/(c*br))
print("Low(10001,1.4)", Low(10001,'1.4'), "Low(3131,0.75)", Low(3131,'0.75'))
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
Psi14=sum(n*Bor(n) for n in range(1,15))
print("Psi(14)", Psi14, "Psi/(2e)", Psi14/(2*e))
k=mpf(3131)
f1=sqrt(2*pi)*(k+15)**mpf(1.5)*Bor(k+15); f2=(k/(k+15))**mpf(1.5); f3=(k+1)/(k+14)
print("Fr factors", f1,f2,f3, f1*f2*f3, f1*f2*f3*Psi14/(2*e))
print("E3 const u(3131)/(e 2^1.5)", u(3131)/(e*2**mpf(1.5)), "0.0648*e*2^1.5", mpf('0.0648')*e*2**mpf(1.5))
# (6.49)
uu=k**(mpf(1)/3); print("k^(1/3)", uu)
print("quad at u", mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'))
def wp(m): m=mpf(m); return mpf('1.99')+mpf('0.59963')*(m+1)**(mpf(2)/3)+mpf('1.24847')*(m+1)**(mpf(1)/3)
d0=mpf('0.75')*k**(mpf(2)/3)
print("(6.49) lhs-rhs", d0-(wp(k+d0)-1))
# (6.50)
def Ren(n): return n*Bor(n)
for d in range(1,14):
    m=k+d
    lhs=(k-1)*(e*Ren(d+1)-60*(d+1)/m)
    rhs=2*(1+sum(e*Ren(r+1)+60*(r+1)/m for r in range(1,d)))
    print(d, mp.nstr(lhs,6), mp.nstr(rhs,5))
