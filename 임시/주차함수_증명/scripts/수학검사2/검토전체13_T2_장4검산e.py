import mpmath as mp, sympy as sp
mp.mp.dps=40
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
c=1/mp.sqrt(2*mp.pi)
for k in [10,100,1000,10000]:
    S=mp.fsum(j*Bor(j) for j in range(1,k+1))
    dev=S-(2*c*mp.sqrt(k)-mp.mpf(2)/3)
    print("k",k,"sum jBor - main:",mp.nstr(dev,8),"allowed [0,",mp.nstr(mp.mpf(2)/3*c/mp.sqrt(k),8),"]")
    tail=1-mp.fsum(Bor(j) for j in range(1,k+1))
    dev2=2*c/mp.sqrt(k)-tail
    print("   2c eps - tail:",mp.nstr(dev2,8),"allowed [0,",mp.nstr(mp.mpf(5)/9*c*k**(-1.5),8),"]")
# constant identity -2/3 = c*zeta(1/2) + sum_j (jBor(j)-c j^{-1/2})
s=mp.nsum(lambda j: j*Bor(j)-c/mp.sqrt(j),[1,mp.inf])
print("c*zeta(1/2)+sum:",c*mp.zeta(0.5)+s)
# T(e^{-1-U}) expansion
for U in [mp.mpf('1e-4'),mp.mpf('1e-6')]:
    T=-mp.lambertw(-mp.e**(-1-U))
    print("U",U,"T-(1-sqrt(2U)+2U/3):",mp.nstr(T-(1-mp.sqrt(2*U)+2*U/3),6),"U^1.5",mp.nstr(U**1.5,6))
# x^4 coefficient of residual at gamma=1/3
g,x=sp.symbols('gamma x',positive=True)
def hat(gg):
    u=(1+gg)/2
    c1=(1-u)/gg**2; c2=-(1-u)*(2+u)/gg**5; c3=sp.Rational(5)*(1-u)*(6+gg-gg**2)/(2*gg**8)
    return u+x*c1+x**2*c2+x**3*c3
R=(hat(g)-1)*hat(sp.sqrt(g**2+4*x))+(1-g**2)/4
ser=sp.series(R,x,0,5).removeO()
c4=sp.simplify(ser.coeff(x,4))
print("x^4 coeff at gamma=1/3:",c4.subs(g,sp.Rational(1,3)))
