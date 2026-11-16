from mpmath import mp, mpf, e, sqrt, pi, log, factorial, quad, exp, nsum, inf
mp.dps = 40
def Bor(m): return e**(-m)*mpf(m)**(m-1)/factorial(m)
c = 1/sqrt(2*pi)
# Robbins-derived: 0 <= c j^{-3/2} - Bor(j) <= c j^{-5/2}/12
worst=0
for j in range(1,3001):
    d = c*mpf(j)**(-1.5) - Bor(j)
    assert d>=0, j
    r = d/(c*mpf(j)**(-2.5)/12)
    worst=max(worst,r)
print("robbins ratio max (<=1 needed):", worst)
for k in (50,200,1000,5000,30000):
    tail1 = 1 - sum(Bor(j) for j in range(1,k+1))
    eps = mpf(k)**(-0.5)
    d1 = 2*c*eps - tail1
    print(k,"piece1:", d1>=0, d1 <= mpf(5)/9*c*eps**3, float(d1/(c*eps**3)))
    s2 = sum(j*Bor(j) for j in range(1,k+1)) - (2*c*sqrt(k) - mpf(2)/3)
    print(k,"piece2:", s2>=0, s2 <= mpf(2)/3*c*eps, float(s2/(c*eps)))
# check (4.11) at a few phi with Re phi<=0, |phi|<=2|Re phi|
def Borsum(k,phi): return sum(Bor(j)*exp(-phi*j/k) for j in range(1,k+1))
def Borld(phi): return 2 + quad(lambda i: i**(-1.5)*(1-exp(-phi*i)), [0,1])
for k in (1000,30000):
    for phi in (mpf(-1), mpf(-3), mpc(-2,1) if False else mp.mpc(-2,1), mp.mpc(-0.5,0.8)):
        lhs = abs(Borsum(k,phi) - 1 + c*mpf(k)**(-0.5)*Borld(phi) - mpf(2)/3*phi/k)
        rhs = c*mpf(k)**(-1.5)*exp(-phi.real)*(mpf(5)/9 + mpf(2)/3*abs(phi) + mpf(13)/12*abs(phi)**2)
        print(k, phi, "4.11 holds:", lhs<=rhs, float(lhs/rhs))
print("e^2.079 =", float(exp(mpf('2.079'))))
